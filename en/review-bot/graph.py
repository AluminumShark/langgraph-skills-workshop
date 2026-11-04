"""1-A: the Homework Helper as a workflow. The route is decided by code.

START → check_syntax ─syntax OK→ give_feedback → check_format ─format OK or limit reached→ END
                     └syntax error→ explain_error → END       └failed and retries below the limit→ send back to give_feedback

Three components:
- State: one order slip (a dict) that travels from start to finish
- Node : one workstation (a function). It takes the State and returns only the fields it changed
- Edge : the arrows between workstations. A conditional edge is just an if that returns the name of the next station
"""

import ast
import re
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict, total=False):
    code: str              # the homework the student submitted
    syntax_ok: bool | None # is the syntax valid? (None before it is checked)
    error: str             # where the syntax is wrong
    feedback: str          # the feedback for the student
    format_ok: bool | None # does the feedback pass the format check?
    format_problem: str    # why it failed (told to the AI when the feedback is sent back)
    retries: int           # how many times feedback has been generated, including the first


# ---------- Node 1: check_syntax (pure Python): only checks the grammar, never runs the code ----------

_ERROR_TRANSLATIONS = [
    (r"'(.)' was never closed", lambda m: f"missing a closing bracket {dict(zip('([{', ')]}')).get(m.group(1), '')}"),
    (r"unterminated string literal", lambda m: "the string is missing its closing quote"),
    (r"expected ':'", lambda m: "missing a colon :"),
    (r"unexpected indent", lambda m: "extra indentation"),
    (r"expected an indented block", lambda m: "this line needs to be indented"),
    (r"unindent does not match", lambda m: "the indentation doesn't line up"),
    (r"unmatched '(.)'", lambda m: f"an extra {m.group(1)}"),
    (r"invalid character", lambda m: "there is a full-width or unrecognized character"),
    (r"Perhaps you forgot a comma", lambda m: "maybe a comma is missing"),
    (r"invalid syntax", lambda m: "invalid syntax"),
]


def translate_syntax_error(msg: str) -> str:
    for pattern, wording in _ERROR_TRANSLATIONS:
        m = re.search(pattern, msg)
        if m:
            return wording(m)
    return msg


def check_syntax(state: State) -> dict:
    code = state.get("code", "")
    if not code.strip():
        return {"syntax_ok": False, "error": "the homework is empty, there is no code"}
    try:
        ast.parse(code)
    except SyntaxError as e:
        return {"syntax_ok": False, "error": f"line {e.lineno}: {translate_syntax_error(e.msg)}"}
    return {"syntax_ok": True, "error": ""}


# ---------- Conditional edge 1: syntax OK → write feedback; syntax error → explain the error (just an if) ----------

def route_after_syntax(state: State) -> str:
    if state["syntax_ok"]:
        return "give_feedback"
    return "explain_error"


# ---------- Node 2: explain_error (pure Python): one sentence saying which line is wrong ----------

def explain_error(state: State) -> dict:
    return {"feedback": f"Syntax: {state['error']}\nImprovements: fix this line first, then run it again."}


# ---------- Node 3: give_feedback (two versions: fixed text / handed to the AI) ----------

def give_feedback_fixed_text(state: State) -> dict:
    """The version with no AI yet: it returns a fixed piece of text."""
    return {
        "feedback": "Strengths: this homework passes the syntax check.\nImprovements: (this version has no AI yet, so the run result and the logic are not checked)",
        "retries": state.get("retries", 0) + 1,
    }


def make_give_feedback(model, feedback_char_limit: int):
    """The version with AI: the AI is just one line of code living inside this node."""

    def give_feedback(state: State) -> dict:
        prompt = (
            "You are a Python homework helper. Give feedback in English on the homework below.\n"
            "Format rules (you must follow them):\n"
            '- Write only two paragraphs: the first starts with "Strengths:", the second starts with "Improvements:"\n'
            f'- The whole feedback (including "Strengths:", "Improvements:", and line breaks) must be at most {feedback_char_limit} characters\n\n'
            f"Homework:\n```python\n{state['code']}\n```"
        )
        if state.get("format_problem"):
            prompt += f"\n\nYour previous feedback was rejected because: {state['format_problem']}. Fix it and rewrite."
        text = model.invoke(prompt).text
        return {"feedback": text.strip(), "retries": state.get("retries", 0) + 1}

    return give_feedback


# ---------- Node 4: check_format (a pure-Python checkpoint): needs two paragraphs and must not be too long ----------

def make_check_format(feedback_char_limit: int):
    def check_format(state: State) -> dict:
        feedback = state.get("feedback", "")
        problems = []
        # Check the label order and that both paragraphs are non-empty; line breaks are accepted.
        parts = re.fullmatch(r"\s*Strengths:\s*(.+?)\s*Improvements:\s*(.+?)\s*", feedback, re.DOTALL)
        if not parts or not all(part.strip() for part in parts.groups()):
            problems.append('it needs two paragraphs in order: "Strengths: ..." and "Improvements: ..."')
        if len(feedback) > feedback_char_limit:
            problems.append(f"too long: {len(feedback)} characters (including labels and line breaks), limit {feedback_char_limit} characters")
        return {"format_ok": not problems, "format_problem": "; ".join(problems)}

    return check_format


# ---------- Conditional edge 2: format OK or generation limit reached → end; otherwise send back to rewrite ----------

def make_route_after_format(max_retries: int):
    def route_after_format(state: State) -> str:
        if state["format_ok"]:
            return END
        if state.get("retries", 0) >= max_retries:
            return END  # reached the feedback generation limit; stopping does not mean the format passed
        return "give_feedback"

    return route_after_format


# ---------- Connect the components ----------

def build_helper(model=None, max_retries: int = 3, feedback_char_limit: int = 450):
    """With model=None it uses fixed text. max_retries is a legacy parameter name; it actually counts generations, including the first."""
    give_feedback = make_give_feedback(model, feedback_char_limit) if model else give_feedback_fixed_text

    builder = StateGraph(State)
    builder.add_node("check_syntax", check_syntax)
    builder.add_node("explain_error", explain_error)
    builder.add_node("give_feedback", give_feedback)
    builder.add_node("check_format", make_check_format(feedback_char_limit))

    builder.add_edge(START, "check_syntax")
    builder.add_conditional_edges("check_syntax", route_after_syntax, ["give_feedback", "explain_error"])
    builder.add_edge("explain_error", END)
    builder.add_edge("give_feedback", "check_format")
    builder.add_conditional_edges("check_format", make_route_after_format(max_retries), ["give_feedback", END])
    return builder.compile()


def blank_order_slip(code: str) -> State:
    return {"code": code, "syntax_ok": None, "error": "", "feedback": "", "format_ok": None,
            "format_problem": "", "retries": 0}
