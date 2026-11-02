"""練習 1：把雙核小助教包成一個網路服務（API）。

上雲端之後，雲端機器上真正在跑的就是這種程式：
別人（網頁、LINE bot、排程）用 HTTP 把作業送進來，它把回饋送回去。
每個學生、每份作業用一個 thread_id 記住進度，下次用同一個 thread_id 就接得回來。

本機或容器裡啟動：uvicorn deploy.server:app --port 8080
"""

from fastapi import FastAPI
from pydantic import BaseModel

import dual_core
from llm import get_model

app = FastAPI(title="作業小助教 API")
_小助教 = None


def 小助教():
    """第一次有人呼叫時才建立（模型、存檔都只建一次）。"""
    global _小助教
    if _小助教 is None:
        _小助教 = dual_core.建立雙核小助教(get_model(), checkpointer=dual_core.開存檔())
    return _小助教


class 批改請求(BaseModel):
    thread_id: str
    code: str
    request: str = "幫第一次交作業的初學者看看"


@app.get("/health")
def health() -> dict:
    """雲端平台會定時敲這個網址，確認服務還活著。"""
    return {"ok": True}


@app.post("/review")
def review(req: 批改請求) -> dict:
    config = {"configurable": {"thread_id": req.thread_id}}
    state = 小助教().invoke({"code": req.code, "request": req.request, "retries": 0}, config)
    return {
        "thread_id": req.thread_id,
        "skill": state.get("skill_name"),
        "feedback": state.get("feedback"),
        "format_ok": state.get("format_ok"),
        "retries": state.get("retries"),
    }


@app.get("/threads/{thread_id}")
def get_thread(thread_id: str) -> dict:
    """查某個 thread_id 的存檔：State 有沒有保留下來。"""
    snap = 小助教().get_state({"configurable": {"thread_id": thread_id}})
    return {
        "thread_id": thread_id,
        "有存檔": bool(snap.values),
        "下一站": list(snap.next),
        "State": {k: v for k, v in snap.values.items() if k not in ("skill", "code")},
    }
