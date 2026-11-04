"""2-E Exercise 2: run Session 2's whole division-of-labor diagram once in Colab (multi-agent + MCP).

START → fetch_homework ─Send×N→ review_one → confirm_before_send ─send→ send_emails → END
          (MCP)                     │            (interrupt)      └Send none→ END       (MCP)
                                    └ code checks syntax → reviewer agent (handbook + script + run_code) → verification agent

How this maps to the five roles you can combine in the diagram (this is a simplified version: no assignment attachment and no read_spec):
- Code: the order of the outer flow, the syntax check, "if verification fails, rewrite once", and ending right away on "Send none"
- Tool: check_naming (the script that comes with the handbook), run_code
- MCP: the homework repo's list_homework / get_homework / send_email (the tools live in another program)
- Skill: the friendly-feedback handbook, used as the reviewer agent's system prompt
- Agent: the same reviewer agent handles each submission (dispatched with Send, each on its own clean desk) + a verification agent with its own separate job
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
from skill_loader import list_cards, read_body
from tools.check_naming import check_naming
from tools.run_code import run_code

MCP_SERVER = Path(__file__).resolve().with_name("homework_mcp.py")
CHECKPOINT_PATH = Path(__file__).resolve().with_name("multi_agent.sqlite")
SEND_OPTIONS = ["Send all", "Send only verified", "Send none"]


# ---------- MCP: the homework repo's socket ----------

def homework_repo_config(url: str | None = None) -> dict:
    """Given a URL, connect to the remote server (Streamable HTTP); without one, start a server locally (stdio)."""
    if url:
        return {"homework_repo": {"url": url, "transport": "streamable_http"}}
    return {"homework_repo": {"command": sys.executable, "args": [str(MCP_SERVER)], "transport": "stdio"}}


async def get_mcp_tools(config: dict) -> dict:
    return {t.name: t for t in await MultiServerMCPClient(config).get_tools()}


def result_text(result) -> str:
    """An MCP tool returns a list of content blocks; pull out the text inside them."""
    if isinstance(result, str):
        return result
    if isinstance(result, list):
        return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in result)
    return str(result)


# ---------- State ----------

class BatchState(TypedDict, total=False):
    roster: list[dict]                            # [{"student", "email", "code"}]
    results: Annotated[list[dict], operator.add]  # the result each "review_one" hands back, appended in order
    decision: str
    sent_log: list[str]


class SubmissionState(TypedDict):
    student: str
    email: str
    code: str


# ---------- Verification agent: checks the homework and the feedback independently; it does not write feedback ----------

AUDITOR_PERSONA = (
    "You are a strict auditor. Your only job is to check homework feedback that someone else wrote; you never write feedback yourself.\n"
    "Check three things: 1. Do the problems the feedback mentions really exist in the homework? "
    "2. Does it cite any line numbers that are wrong? 3. Does it use harsh words such as \"wrong\" or \"terrible\"?\n"
    'Reply with exactly one line of JSON and nothing else: {"passed": true or false, "reason": "one sentence"}'
)


def verify(model, code: str, feedback: str) -> dict:
    # What code can decide, check with code first (these checks cost no tokens); the auditor still calls the model once per submission
    problems = []
    if "Strengths" not in feedback or "Improvements" not in feedback:
        problems.append('Missing the "Strengths" or "Improvements" section')
    line_count = len(code.splitlines())
    for n in re.findall(r"(?i)\bline\s*(\d+)", feedback):
        if not 1 <= int(n) <= line_count:
            problems.append(f"Mentions line {n}, but the homework has only {line_count} lines")
    # What code can't decide goes to the auditor
    with_line_numbers = "\n".join(f"{i:>2} | {line}" for i, line in enumerate(code.splitlines(), 1))
    answer = model.invoke([SystemMessage(AUDITOR_PERSONA),
                           HumanMessage(f"Homework:\n{with_line_numbers}\n\nFeedback:\n{feedback}")]).text
    m = re.search(r"\{.*\}", answer, re.S)
    try:
        judgement = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        judgement = {}
    if not isinstance(judgement, dict) or not isinstance(judgement.get("passed"), bool):
        problems.append("Could not parse the auditor's reply into a true/false passed value; check it by hand")
    elif not judgement["passed"]:
        problems.append("Auditor: " + str(judgement.get("reason", answer.strip()[:60])))
    return {"passed": not problems, "reason": "; ".join(problems) or "OK"}


# ---------- Wiring the components together ----------

def build_multi_agent_helper(model, mcp_config: dict | None = None, checkpointer=None, only_students: str | None = None):
    mcp_config = mcp_config or homework_repo_config()
    handbook = read_body(list_cards(["friendly-feedback"])[0])
    REVIEWER_PERSONA = (
        f"{handbook}\n\n"
        "# Your tools\n"
        "- check_naming: checks variable naming (the script that comes with the handbook); use it when you discuss naming\n"
        "- run_code: runs the homework so you can see its output\n"
        "You decide whether to use them and which one. Keep the feedback to at most 750 characters."
    )

    async def fetch_homework(state: BatchState) -> dict:
        # Fetching homework needs no judgment, so "code" calls the MCP tools, not an agent
        tools = await get_mcp_tools(mcp_config)
        roster = json.loads(result_text(await tools["list_homework"].ainvoke({})))
        if only_students is not None:
            roster = [a for a in roster if a["student"] == only_students]
            if not roster:
                raise ValueError(f"The homework repo has no student named: {only_students}")
        for a in roster:
            a["code"] = result_text(await tools["get_homework"].ainvoke({"student": a["student"]}))
        return {"roster": roster}

    def dispatch(state: BatchState) -> list[Send]:
        # Start one "review_one" per submission: each gets its own clean desk
        return [Send("review_one", a) for a in state["roster"]]

    def review_one(state: SubmissionState) -> dict:
        code = state["code"]
        syntax = check_syntax({"code": code})
        if not syntax["syntax_ok"]:   # Anything you can write as an if: the code replies directly, no AI call
            feedback = f"Syntax: {syntax['error']}\nImprovements: Fix this line first, then run the program again."
            return {"results": [{**state, "feedback": feedback, "used_tools": [], "rewrite_count": 0,
                                 "verify": {"passed": True, "reason": "The code replied to the syntax error directly; no AI was involved"}}]}
        reviewer = create_agent(model, tools=[check_naming, run_code], system_prompt=REVIEWER_PERSONA)
        messages = [{"role": "user", "content": f"Please review this homework:\n```python\n{code}\n```"}]
        used_tools, rewrite_count = [], 0
        while True:
            result = reviewer.invoke({"messages": messages}, config={"recursion_limit": 25})
            # result includes the full record of the previous round; take only this round's new messages so old tool requests aren't counted twice.
            used_tools += [c["name"] for m in result["messages"][len(messages):] for c in (getattr(m, "tool_calls", None) or [])]
            feedback = result["messages"][-1].text.strip()
            verdict = verify(model, code, feedback)
            if verdict["passed"] or rewrite_count >= 1:      # If verification fails, send it back for at most one rewrite
                break
            rewrite_count += 1
            messages = result["messages"] + [{"role": "user", "content": f"The auditor sent it back: {verdict['reason']}. Fix it and rewrite the feedback."}]
        return {"results": [{**state, "feedback": feedback, "used_tools": used_tools,
                             "rewrite_count": rewrite_count, "verify": verdict}]}

    def confirm_before_send(state: BatchState) -> dict:
        # Sending email is irreversible: stop and hand what would be sent to a person to read
        emails = [{"student": r["student"], "email": r["email"], "verified": r["verify"]["passed"],
                   "feedback": r["feedback"]} for r in state["results"]]
        decision = interrupt({"emails_to_send": emails, "options": SEND_OPTIONS})
        if decision == "Send none":
            return {"decision": decision, "sent_log": ["No emails were sent (decision: Send none)"]}
        return {"decision": decision}

    def should_send(state: BatchState) -> str:
        # Choosing "Send none" ends right away, without entering the send_emails node
        return END if state.get("decision") == "Send none" else "send_emails"

    async def send_emails(state: BatchState) -> dict:
        to_send = [r for r in state["results"]
                   if state.get("decision") == "Send all" or (state.get("decision") == "Send only verified" and r["verify"]["passed"])]
        if not to_send:
            return {"sent_log": [f"No emails were sent (decision: {state.get('decision')})"]}
        tools = await get_mcp_tools(mcp_config)
        log = []
        for r in to_send:
            result = await tools["send_email"].ainvoke({"to": r["email"], "subject": "Homework feedback", "body": r["feedback"]})
            log.append(result_text(result))
        return {"sent_log": log}

    builder = StateGraph(BatchState)
    builder.add_node("fetch_homework", fetch_homework)
    builder.add_node("review_one", review_one)
    builder.add_node("confirm_before_send", confirm_before_send)
    builder.add_node("send_emails", send_emails)
    builder.add_edge(START, "fetch_homework")
    builder.add_conditional_edges("fetch_homework", dispatch, ["review_one"])
    builder.add_edge("review_one", "confirm_before_send")
    builder.add_conditional_edges("confirm_before_send", should_send, ["send_emails", END])
    builder.add_edge("send_emails", END)
    return builder.compile(checkpointer=checkpointer)


async def open_checkpointer(path: Path = CHECKPOINT_PATH):
    """interrupt waits for a person to confirm, so the State must be saved; here it goes into a SQLite file (in the cloud, use Postgres)."""
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    return AsyncSqliteSaver(await aiosqlite.connect(str(path)))


class usage_meter(BaseCallbackHandler):
    """Counts how many times the model is called and adds up the tokens (for Colab's built-in model, the tokens are estimates)."""

    def __init__(self):
        self.count = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def on_llm_end(self, response, **kwargs):
        self.count += 1
        for generations in response.generations:
            for g in generations:
                usage = getattr(getattr(g, "message", None), "usage_metadata", None) or {}
                self.input_tokens += usage.get("input_tokens", 0)
                self.output_tokens += usage.get("output_tokens", 0)
