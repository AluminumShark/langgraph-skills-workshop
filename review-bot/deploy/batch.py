"""練習 2：用 Send 平行批改（map-reduce），並算一算成本。

START ─分派→ 批一份 × N（同時跑，每份一張乾淨的桌子）→ 彙整 → END

- Send：在條件邊裡說「批一份這個節點，照這份清單一份開一個」
- 結果們用 Annotated[list, operator.add]：每個「批一份」交回來的結果往下接著寫
- config={"max_concurrency": 2}：最多同時跑幾份，其餘排隊（模型 API 每分鐘有上限）
"""

import operator
from typing import Annotated, TypedDict

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from skill_loader import 列出名片, 讀內文


class 批次State(TypedDict):
    作業們: list[dict]                            # [{"學生": "學生1", "code": "..."}, ...]
    結果們: Annotated[list[dict], operator.add]   # 往下接著寫，不會互相覆蓋


class 一份State(TypedDict):
    學生: str
    code: str


def _手冊() -> str:
    return 讀內文(列出名片(["friendly-feedback"])[0])


def 建立批改流程(model):
    手冊 = _手冊()

    def 分派(state: 批次State) -> list[Send]:
        # 每份作業開一個「批一份」：各自一張乾淨的桌子，不會把別人的作業看進來
        return [Send("批一份", {"學生": a["學生"], "code": a["code"]}) for a in state["作業們"]]

    def 批一份(state: 一份State) -> dict:
        回饋 = model.invoke([
            SystemMessage(手冊),
            HumanMessage(f"請批改這份作業：\n```python\n{state['code']}\n```"),
        ]).text
        return {"結果們": [{"學生": state["學生"], "回饋": 回饋.strip()}]}

    def 彙整(state: 批次State) -> dict:
        return {}

    builder = StateGraph(批次State)
    builder.add_node("批一份", 批一份)
    builder.add_node("彙整", 彙整)
    builder.add_conditional_edges(START, 分派, ["批一份"])
    builder.add_edge("批一份", "彙整")
    builder.add_edge("彙整", END)
    return builder.compile()


def 一次批全部(model, 作業們: list[dict], callbacks=None) -> str:
    """對照組：一張桌子批全部（便宜，但第 150 份時桌上堆滿前面 149 份）。"""
    全部 = "\n\n".join(f"### {a['學生']}\n```python\n{a['code']}\n```" for a in 作業們)
    return model.invoke(
        [SystemMessage(_手冊()), HumanMessage(f"請逐一批改下面每一位學生的作業：\n\n{全部}")],
        config={"callbacks": callbacks or []},
    ).text


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
