"""2-E 練習 3：把多 agent 小助教包成一個網路服務（API）。

上雲端之後，雲端機器上真正在跑的就是這種程式：
幹部的後台網頁用 HTTP 叫它「開始批改」，它把待寄的信列出來；幹部按下確認，再用 HTTP 叫它「寄」。
每一批用一個 thread_id 記住進度：開始和確認是兩個不同的請求，中間 State 存在存檔裡。

本機或容器裡啟動：uvicorn deploy.server:app --port 8080
作業倉庫 MCP：有設環境變數 HOMEWORK_MCP_URL 就連那個網址，沒設就在本機開一個（stdio）。
"""

import os

from fastapi import FastAPI
from langgraph.types import Command
from pydantic import BaseModel

from deploy import multi_agent
from llm import get_model

app = FastAPI(title="作業小助教 API")
_小助教 = None


async def 小助教():
    """第一次有人呼叫時才建立（模型、MCP 設定、存檔都只建一次）。"""
    global _小助教
    if _小助教 is None:
        _小助教 = multi_agent.建立多agent小助教(
            get_model(),
            mcp設定=multi_agent.作業倉庫設定(os.environ.get("HOMEWORK_MCP_URL")),
            checkpointer=await multi_agent.開存檔(),
        )
    return _小助教


class 批改請求(BaseModel):
    thread_id: str
    同時批幾份: int = 2


class 決定請求(BaseModel):
    決定: str   # 全部寄出／只寄驗證通過的／都不要寄


@app.get("/health")
def health() -> dict:
    """雲端平台會定時敲這個網址，確認服務還活著。"""
    return {"ok": True}


@app.post("/batch")
async def 開始批改(req: 批改請求) -> dict:
    """從作業倉庫抓作業、平行批改、驗證，然後停在寄信前面等人確認。"""
    config = {"configurable": {"thread_id": req.thread_id}, "max_concurrency": req.同時批幾份}
    結果 = await (await 小助教()).ainvoke({"結果們": []}, config)
    待確認 = 結果["__interrupt__"][0].value if "__interrupt__" in 結果 else None
    return {"thread_id": req.thread_id, "待確認": 待確認}


@app.post("/batch/{thread_id}/decision")
async def 確認寄信(thread_id: str, req: 決定請求) -> dict:
    """人看過之後的決定：帶著同一個 thread_id 接著跑。"""
    config = {"configurable": {"thread_id": thread_id}}
    圖 = await 小助教()
    if not (await 圖.aget_state(config)).next:
        return {"thread_id": thread_id, "錯誤": "這個 thread_id 沒有在等確認的信"}
    結果 = await 圖.ainvoke(Command(resume=req.決定), config)
    return {"thread_id": thread_id, "寄件紀錄": 結果.get("寄件紀錄", [])}


@app.get("/threads/{thread_id}")
async def 查進度(thread_id: str) -> dict:
    """查某個 thread_id 的存檔：State 有沒有保留下來、停在哪一站。"""
    snap = await (await 小助教()).aget_state({"configurable": {"thread_id": thread_id}})
    v = snap.values
    return {
        "thread_id": thread_id,
        "有存檔": bool(v),
        "下一站": list(snap.next),
        "批好幾份": len(v.get("結果們", [])),
        "決定": v.get("決定"),
        "寄件紀錄": v.get("寄件紀錄"),
    }
