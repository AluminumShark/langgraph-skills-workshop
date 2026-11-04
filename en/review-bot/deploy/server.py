"""2-E Exercise 3: wrap the multi-agent Homework Helper as a network service (an API).

Once it is in the cloud, a program like this is what actually runs on the cloud machine:
a staff member's admin web page calls it over HTTP to "start a batch review", and it lists the emails waiting to be sent. When the staff member confirms, the page calls it again over HTTP to "send".
Each batch uses one thread_id to remember its progress: starting and confirming are two different requests, and in between the State is kept in the checkpoint.

To start it on your machine or in a container: uvicorn deploy.server:app --port 8080
Homework repo MCP: if the environment variable HOMEWORK_MCP_URL is set, it connects to that URL; if not, it starts one locally (stdio).
"""

import os

from fastapi import FastAPI
from langgraph.types import Command
from pydantic import BaseModel

from deploy import multi_agent
from llm import get_model

app = FastAPI(title="Homework Helper API")
_helper = None


async def helper():
    """Built the first time someone calls it (the model, the MCP config and the checkpoint are each created only once)."""
    global _helper
    if _helper is None:
        _helper = multi_agent.build_multi_agent_helper(
            get_model(),
            mcp_config=multi_agent.homework_repo_config(os.environ.get("HOMEWORK_MCP_URL")),
            checkpointer=await multi_agent.open_checkpointer(),
        )
    return _helper


class BatchRequest(BaseModel):
    thread_id: str
    max_concurrency: int = 2


class DecisionRequest(BaseModel):
    decision: str   # Send all / Send only verified / Send none


@app.get("/health")
def health() -> dict:
    """The cloud platform hits this URL on a schedule to check that the service is still alive."""
    return {"ok": True}


@app.post("/batch")
async def start_batch(req: BatchRequest) -> dict:
    """Fetch homework from the homework repo, review it in parallel, verify it, then stop before sending and wait for a person to confirm."""
    config = {"configurable": {"thread_id": req.thread_id}, "max_concurrency": req.max_concurrency}
    graph = await helper()
    if (await graph.aget_state(config)).values:
        return {"thread_id": req.thread_id, "error": "This ID already has a checkpoint. Check its progress or start with a new ID; it will not re-review or add results."}
    result = await graph.ainvoke({"results": []}, config)
    pending_confirmation = result["__interrupt__"][0].value if "__interrupt__" in result else None
    return {"thread_id": req.thread_id, "pending_confirmation": pending_confirmation}


@app.post("/batch/{thread_id}/decision")
async def confirm_send(thread_id: str, req: DecisionRequest) -> dict:
    """The decision after a person has looked: continue running with the same thread_id."""
    config = {"configurable": {"thread_id": thread_id}}
    graph = await helper()
    if req.decision not in multi_agent.SEND_OPTIONS:
        return {"thread_id": thread_id, "error": "Please choose a valid send decision"}
    if (await graph.aget_state(config)).next != ("confirm_before_send",):
        return {"thread_id": thread_id, "error": "This thread_id has no emails waiting for confirmation. Check its progress first"}
    result = await graph.ainvoke(Command(resume=req.decision), config)
    return {"thread_id": thread_id, "sent_log": result.get("sent_log", [])}


@app.get("/threads/{thread_id}")
async def get_progress(thread_id: str) -> dict:
    """Look up the checkpoint of a thread_id: whether the State was kept and which station it is stopped at."""
    snap = await (await helper()).aget_state({"configurable": {"thread_id": thread_id}})
    v = snap.values
    return {
        "thread_id": thread_id,
        "has_checkpoint": bool(v),
        "next_station": list(snap.next),
        "reviewed_count": len(v.get("results", [])),
        "decision": v.get("decision"),
        "sent_log": v.get("sent_log"),
    }
