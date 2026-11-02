"""2-D：雙核作業小助教。外面是 1-A 的 workflow（分支與順序由程式控制），裡面是 1-B 的 agent（放手判斷）。

START → check_syntax ─語法 OK→ skill_loader → give_feedback → check_format ─OK→ END
                     └語法錯→ explain_error → END            └不合格且未達上限→ 退回 give_feedback

- skill_loader ：看所有手冊的名片，挑一本，把內文放進 State（2-A 的手冊）
- give_feedback：裡面是一個小 agent，用挑中的手冊當 system prompt，
                 工具箱有 run_code、read_spec、check_naming（2-B 的腳本包成工具）
- checkpointer ：每一步的 State 都存進 SQLite 檔，同一個 thread_id 可以接著跑
"""

import operator
import sqlite3
from pathlib import Path
from typing import Annotated, TypedDict

from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from graph import check_syntax, explain_error, route_after_syntax, 建立_check_format, 建立_route_after_format
from skill_loader import 列出名片, 挑手冊, 讀內文
from tools.check_naming import check_naming
from tools.read_spec import read_spec
from tools.run_code import run_code

存檔位置 = Path(__file__).resolve().parent / "checkpoints.sqlite"
可選的手冊 = ["friendly-feedback", "strict-review"]


class 雙核State(TypedDict, total=False):
    code: str                 # 學生交的作業
    request: str              # 批改需求（skill_loader 用它挑手冊）
    syntax_ok: bool | None
    error: str
    skill_name: str           # 挑中的手冊
    skill: str                # 手冊內文
    feedback: str
    format_ok: bool | None
    format_problem: str
    retries: int
    tools_used: Annotated[list[str], operator.add]  # 裡面的 agent 用過哪些工具（往下接著寫）


def 建立_skill_loader(model):
    def skill_loader(state: 雙核State) -> dict:
        card = 挑手冊(model, state.get("request", ""), 列出名片(可選的手冊))
        return {"skill_name": card["name"], "skill": 讀內文(card)}

    return skill_loader


def 建立_give_feedback(model, 回饋字數上限: int):
    def give_feedback(state: 雙核State) -> dict:
        system_prompt = (
            f"{state['skill']}\n\n"
            "# 你的工具\n"
            "- check_naming：檢查變數命名（手冊附的腳本），要談命名時用它，照抄它的結果\n"
            "- run_code：執行作業看輸出\n"
            "- read_spec：讀題目要求\n"
            "要不要用、用哪一個，你自己決定。\n\n"
            "# 格式（外層流程會用程式檢查，不合格會退回）\n"
            "- 只寫兩段：第一段以「優點：」開頭，第二段以「改進：」開頭\n"
            f"- 兩段加起來不超過 {回饋字數上限} 個字"
        )
        if state.get("format_problem"):
            system_prompt += f"\n\n上一版被退回，原因：{state['format_problem']}。請修正。"
        小agent = create_agent(model, tools=[check_naming, run_code, read_spec], system_prompt=system_prompt)
        result = 小agent.invoke(
            {"messages": [{"role": "user", "content": f"請批改這份作業：\n```python\n{state['code']}\n```"}]},
            config={"recursion_limit": 25},
        )
        messages = result["messages"]
        used = [c["name"] for m in messages for c in (getattr(m, "tool_calls", None) or [])]
        return {"feedback": messages[-1].text.strip(), "retries": state.get("retries", 0) + 1, "tools_used": used}

    return give_feedback


def 逐站執行(小助教, 輸入, config: dict) -> dict:
    """一站一站跑，印出每一站寫了哪幾格；回傳跑完（或中斷）時存檔裡的 State。"""
    for event in 小助教.stream(輸入, config=config, stream_mode="updates"):
        for 站, 寫入 in event.items():
            if 站 == "__interrupt__":
                print("⏸️  中斷：流程停在這裡，State 已經存進存檔")
                continue
            print(f"▶ {站}")
            for key, value in (寫入 or {}).items():
                text = value if isinstance(value, str) else repr(value)
                if key == "skill":
                    text = text.splitlines()[0] + " …（手冊內文）"
                print(f"    {key}: {text[:200]}")
    return 小助教.get_state(config).values


def 開存檔(path: Path = 存檔位置) -> SqliteSaver:
    """把 State 存進 SQLite 檔；只要同一檔案仍存在，就能按 thread_id 讀回。"""
    return SqliteSaver(sqlite3.connect(str(path), check_same_thread=False))


def 建立雙核小助教(model, checkpointer=None, 最多重試次數: int = 3, 回饋字數上限: int = 250,
                interrupt_before: list[str] | None = None):
    builder = StateGraph(雙核State)
    builder.add_node("check_syntax", check_syntax)
    builder.add_node("explain_error", explain_error)
    builder.add_node("skill_loader", 建立_skill_loader(model))
    builder.add_node("give_feedback", 建立_give_feedback(model, 回饋字數上限))
    builder.add_node("check_format", 建立_check_format(回饋字數上限))

    builder.add_edge(START, "check_syntax")
    # 語法 OK 先去挑手冊，再給回饋
    builder.add_conditional_edges(
        "check_syntax", route_after_syntax, {"give_feedback": "skill_loader", "explain_error": "explain_error"}
    )
    builder.add_edge("explain_error", END)
    builder.add_edge("skill_loader", "give_feedback")
    builder.add_edge("give_feedback", "check_format")
    builder.add_conditional_edges("check_format", 建立_route_after_format(最多重試次數), ["give_feedback", END])
    return builder.compile(checkpointer=checkpointer, interrupt_before=interrupt_before)
