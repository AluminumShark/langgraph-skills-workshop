"""練習 3：寄信前一定停下來，等人按確認（interrupt）。

START → 寫回饋 → 寄信（interrupt：停住，等人確認）→ END

interrupt() 會把 State 存進 checkpointer 然後停住；人看過內容之後，
用 Command(resume="寄") 帶著同一個 thread_id 叫它繼續，resume 的值就是 interrupt() 的回傳值。
"""

import datetime as _dt
from pathlib import Path
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from skill_loader import 列出名片, 讀內文

寄件匣 = Path(__file__).resolve().parent.parent / "寄件匣.txt"


class 寄信State(TypedDict, total=False):
    學生: str
    email: str
    code: str
    feedback: str
    已寄出: bool
    寄件紀錄: str


def send_email(to: str, body: str) -> str:
    """假的寄信工具：只寫進 寄件匣.txt。真實系統這裡會是 MCP 的寄信工具，寄出去就收不回來。"""
    with 寄件匣.open("a", encoding="utf-8") as f:
        f.write(f"[{_dt.datetime.now():%H:%M:%S}] 寄給 {to}\n{body}\n\n")
    return f"（模擬）已寄給 {to}"


def 建立寄信流程(model, checkpointer):
    手冊 = 讀內文(列出名片(["friendly-feedback"])[0])

    def 寫回饋(state: 寄信State) -> dict:
        回饋 = model.invoke([
            SystemMessage(手冊),
            HumanMessage(f"請批改這份作業：\n```python\n{state['code']}\n```"),
        ]).text
        return {"feedback": 回饋.strip()}

    def 寄信(state: 寄信State) -> dict:
        # 寄信不可逆：先停下來，把要寄的內容交給人看
        答案 = interrupt({"收件人": state["email"], "內容": state["feedback"]})
        if 答案 == "寄":
            return {"已寄出": True, "寄件紀錄": send_email(state["email"], state["feedback"])}
        return {"已寄出": False, "寄件紀錄": f"確認的人回答「{答案}」，這封信沒有寄出"}

    builder = StateGraph(寄信State)
    builder.add_node("寫回饋", 寫回饋)
    builder.add_node("寄信", 寄信)
    builder.add_edge(START, "寫回饋")
    builder.add_edge("寫回饋", "寄信")
    builder.add_edge("寄信", END)
    return builder.compile(checkpointer=checkpointer)
