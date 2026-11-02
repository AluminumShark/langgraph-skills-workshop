"""2-E 練習 2：把第 2 堂的整張分工圖在 Colab 跑一次（多 agent ＋ MCP）。

START → 抓作業 ─Send×N→ 批一份 → 寄信前確認 → 寄信 → END
         (MCP)             │                  (interrupt)  (MCP)
                           └ 程式檢查語法 → 批改子 agent（手冊＋腳本＋run_code）→ 驗證 agent

對照分工圖的五個抽屜：
- 程式：外層流程的順序、語法檢查、「驗證不過就重寫一次」
- Tool：check_naming（手冊附的腳本）、run_code
- MCP ：作業倉庫的 list_homework / get_homework / send_email（工具住在另一個程式裡）
- Skill：friendly-feedback 手冊，當批改子 agent 的 system prompt
- 子 agent：每份作業一個批改子 agent（一張乾淨的桌子）＋ 一個人設不同的驗證 agent
"""

import json
import operator
import re
import sys
from pathlib import Path
from typing import Annotated, TypedDict

from langchain.agents import create_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send, interrupt

from graph import check_syntax
from skill_loader import 列出名片, 讀內文
from tools.check_naming import check_naming
from tools.run_code import run_code

MCP_SERVER = Path(__file__).resolve().with_name("homework_mcp.py")
存檔位置 = Path(__file__).resolve().with_name("multi_agent.sqlite")
寄信選項 = ["全部寄出", "只寄驗證通過的", "都不要寄"]


# ---------- MCP：作業倉庫的插座 ----------

def 作業倉庫設定(網址: str | None = None) -> dict:
    """給網址就連遠端（Streamable HTTP），沒給就在本機開一個（stdio）。"""
    if 網址:
        return {"作業倉庫": {"url": 網址, "transport": "streamable_http"}}
    return {"作業倉庫": {"command": sys.executable, "args": [str(MCP_SERVER)], "transport": "stdio"}}


async def 取得MCP工具(設定: dict) -> dict:
    return {t.name: t for t in await MultiServerMCPClient(設定).get_tools()}


def 結果文字(結果) -> str:
    """MCP 工具回傳的是一串內容區塊，取出裡面的文字。"""
    if isinstance(結果, str):
        return 結果
    if isinstance(結果, list):
        return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in 結果)
    return str(結果)


# ---------- State ----------

class 總State(TypedDict, total=False):
    名單: list[dict]                             # [{"學生", "email", "code"}]
    結果們: Annotated[list[dict], operator.add]   # 每個「批一份」交回來的結果，往下接著寫
    決定: str
    寄件紀錄: list[str]


class 一份State(TypedDict):
    學生: str
    email: str
    code: str


# ---------- 驗證 agent：另一個人設，只檢查、不寫回饋 ----------

稽核員人設 = (
    "你是嚴格的稽核員，只負責檢查別人寫的作業回饋，自己不寫回饋。\n"
    "檢查三件事：1. 回饋說的問題在作業裡真的存在嗎 2. 有沒有亂講行號 3. 有沒有用「錯誤」「很差」這類字眼。\n"
    '只回一行 JSON，不要其他文字：{"通過": true 或 false, "原因": "一句話"}'
)


def 驗證(model, code: str, feedback: str) -> dict:
    # 程式能判斷的，先用程式檢查（不花 token）
    問題 = []
    if "優點" not in feedback or "改進" not in feedback:
        問題.append("少了「優點」或「改進」段落")
    行數 = len(code.splitlines())
    for n in re.findall(r"第\s*(\d+)\s*行", feedback):
        if not 1 <= int(n) <= 行數:
            問題.append(f"提到第 {n} 行，但作業只有 {行數} 行")
    # 程式判斷不了的，交給稽核員
    帶行號 = "\n".join(f"{i:>2} | {line}" for i, line in enumerate(code.splitlines(), 1))
    回答 = model.invoke([SystemMessage(稽核員人設), HumanMessage(f"作業：\n{帶行號}\n\n回饋：\n{feedback}")]).text
    m = re.search(r"\{.*\}", 回答, re.S)
    try:
        判斷 = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        判斷 = {}
    稽核通過 = bool(判斷.get("通過", "不通過" not in 回答))
    if not 稽核通過:
        問題.append("稽核員：" + str(判斷.get("原因", 回答.strip()[:60])))
    return {"通過": not 問題, "原因": "；".join(問題) or "OK"}


# ---------- 把零件接起來 ----------

def 建立多agent小助教(model, mcp設定: dict | None = None, checkpointer=None):
    mcp設定 = mcp設定 or 作業倉庫設定()
    手冊 = 讀內文(列出名片(["friendly-feedback"])[0])
    批改員人設 = (
        f"{手冊}\n\n"
        "# 你的工具\n"
        "- check_naming：檢查變數命名（手冊附的腳本），要談命名時用它\n"
        "- run_code：執行作業看輸出\n"
        "要不要用、用哪一個，你自己決定。回饋不超過 250 字。"
    )

    async def 抓作業(state: 總State) -> dict:
        # 抓作業不需要判斷，所以是「程式」呼叫 MCP 工具，不是 agent
        tools = await 取得MCP工具(mcp設定)
        名單 = json.loads(結果文字(await tools["list_homework"].ainvoke({})))
        for a in 名單:
            a["code"] = 結果文字(await tools["get_homework"].ainvoke({"student": a["學生"]}))
        return {"名單": 名單}

    def 分派(state: 總State) -> list[Send]:
        # 每份作業開一個「批一份」：各自一張乾淨的桌子
        return [Send("批一份", a) for a in state["名單"]]

    def 批一份(state: 一份State) -> dict:
        code = state["code"]
        語法 = check_syntax({"code": code})
        if not 語法["syntax_ok"]:   # 能寫成 if 的事：程式直接回，不叫 AI
            feedback = f"語法：{語法['error']}\n改進：先把這一行修好，再執行一次看看。"
            return {"結果們": [{**state, "feedback": feedback, "用到的工具": [], "重寫次數": 0,
                              "驗證": {"通過": True, "原因": "語法錯誤由程式直接回覆，沒有經過 AI"}}]}
        批改員 = create_agent(model, tools=[check_naming, run_code], system_prompt=批改員人設)
        messages = [{"role": "user", "content": f"請批改這份作業：\n```python\n{code}\n```"}]
        用到的工具, 重寫次數 = [], 0
        while True:
            result = 批改員.invoke({"messages": messages}, config={"recursion_limit": 25})
            用到的工具 += [c["name"] for m in result["messages"] for c in (getattr(m, "tool_calls", None) or [])]
            feedback = result["messages"][-1].text.strip()
            結論 = 驗證(model, code, feedback)
            if 結論["通過"] or 重寫次數 >= 1:      # 驗證不過最多退回重寫一次
                break
            重寫次數 += 1
            messages = result["messages"] + [{"role": "user", "content": f"稽核員退回：{結論['原因']}。請修正後重寫回饋。"}]
        return {"結果們": [{**state, "feedback": feedback, "用到的工具": 用到的工具,
                          "重寫次數": 重寫次數, "驗證": 結論}]}

    def 寄信前確認(state: 總State) -> dict:
        # 寄信不可逆：停下來，把要寄的內容交給人看
        清單 = [{"學生": r["學生"], "email": r["email"], "驗證通過": r["驗證"]["通過"],
                "回饋": r["feedback"]} for r in state["結果們"]]
        決定 = interrupt({"要寄出的信": 清單, "選項": 寄信選項})
        return {"決定": 決定}

    async def 寄信(state: 總State) -> dict:
        要寄 = [r for r in state["結果們"]
              if state.get("決定") == "全部寄出" or (state.get("決定") == "只寄驗證通過的" and r["驗證"]["通過"])]
        if not 要寄:
            return {"寄件紀錄": [f"沒有寄出任何信（決定：{state.get('決定')}）"]}
        tools = await 取得MCP工具(mcp設定)
        紀錄 = []
        for r in 要寄:
            結果 = await tools["send_email"].ainvoke({"to": r["email"], "subject": "作業回饋", "body": r["feedback"]})
            紀錄.append(結果文字(結果))
        return {"寄件紀錄": 紀錄}

    builder = StateGraph(總State)
    builder.add_node("抓作業", 抓作業)
    builder.add_node("批一份", 批一份)
    builder.add_node("寄信前確認", 寄信前確認)
    builder.add_node("寄信", 寄信)
    builder.add_edge(START, "抓作業")
    builder.add_conditional_edges("抓作業", 分派, ["批一份"])
    builder.add_edge("批一份", "寄信前確認")
    builder.add_edge("寄信前確認", "寄信")
    builder.add_edge("寄信", END)
    return builder.compile(checkpointer=checkpointer)


async def 開存檔(path: Path = 存檔位置):
    """interrupt 要等人確認，所以 State 一定要存起來；這裡存成 SQLite 檔（雲端改用 Postgres）。"""
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    return AsyncSqliteSaver(await aiosqlite.connect(str(path)))


class 用量計(BaseCallbackHandler):
    """數模型被呼叫幾次、加總 token（Colab 內建模型的 token 是估算值）。"""

    def __init__(self):
        self.次數 = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def on_llm_end(self, response, **kwargs):
        self.次數 += 1
        for generations in response.generations:
            for g in generations:
                usage = getattr(getattr(g, "message", None), "usage_metadata", None) or {}
                self.input_tokens += usage.get("input_tokens", 0)
                self.output_tokens += usage.get("output_tokens", 0)
