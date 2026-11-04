"""2-D: the integrated Homework Helper. The outside is the 1-A workflow (branches and order controlled by code), and the inside is the 1-B agent (decided by the AI).

START → check_syntax ─syntax OK→ skill_loader → give_feedback → check_format ─OK→ END
                     └syntax error→ explain_error → END            └failed and limit not reached→ send back to give_feedback

- skill_loader : looks at the cards of all handbooks, picks one, and puts its body into the State (the handbooks from 2-A)
- give_feedback: contains a small agent that uses the picked handbook as its system prompt,
                 and its toolbox has run_code, read_spec, check_naming (the 2-B script wrapped as a tool)
- checkpointer : saves the State of every step into a SQLite file, so the same thread_id can continue running
"""

import operator
import sqlite3
from pathlib import Path
from typing import Annotated, TypedDict

from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from graph import check_syntax, explain_error, route_after_syntax, make_check_format, make_route_after_format
from skill_loader import list_cards, pick_handbook, read_body
from tools.check_naming import check_naming
from tools.run_code import run_code

CHECKPOINT_PATH = Path(__file__).resolve().parent / "checkpoints.sqlite"
AVAILABLE_HANDBOOKS = ["friendly-feedback", "strict-review"]
sample_specs = {
    "Correct program": "Write a function add(a, b) that returns the sum of two numbers, and use print(add(2, 3)) to print 5.",
    "Variable typo": "Write a function add(a, b) that returns the sum of two numbers, and use print(add(2, 3)) to print 5.",
    "Missing parenthesis": "Use print to print hi.",
    "Inconsistent naming": "Write a function that computes the average of a list of scores. Test it with [90, 85, 77] and print the average along with the full mark 100 for comparison. Name variables, functions and parameters in lowercase with underscores.",
    "Messy indentation": "Write an average(scores) function that computes the average of the scores, and print the result of average([90, 85, 77]).",
}


class IntegratedState(TypedDict, total=False):
    code: str                 # the homework the student submitted
    spec: str                 # the assignment paired with this homework, saved along with the State
    request: str              # the review request (skill_loader uses it to pick a handbook)
    syntax_ok: bool | None
    error: str
    skill_name: str           # the handbook that was picked
    skill: str                # the handbook body
    feedback: str
    format_ok: bool | None
    format_problem: str
    retries: int
    tools_used: Annotated[list[str], operator.add]  # which tools the inner agent used (keeps appending)


def homework_input(homework_name: str, code: str, review_request: str) -> IntegratedState:
    """Pair the assignment when a new run starts. A resumed run uses the checkpoint and does not re-read the form or shared files."""
    if homework_name not in sample_specs:
        raise ValueError(f"No assignment is set up for this homework yet: {homework_name}")
    return {"code": code, "spec": sample_specs[homework_name], "request": review_request, "retries": 0}


def make_read_spec(spec_text: str):
    """The agent still chooses whether to use the tool, but what it reads is fixed to the assignment in that State."""
    if not isinstance(spec_text, str) or not spec_text.strip():
        raise ValueError("The State has no assignment (spec). Use homework_input to start a new run. For an old checkpoint, use a brand-new thread_id and don't fall back to the shared spec.md.")

    @tool
    def read_spec() -> str:
        """Read the assignment requirements paired with this homework. Use it before judging whether the homework meets the assignment. It takes no parameters."""
        return spec_text

    return read_spec


def make_skill_loader(model):
    def skill_loader(state: IntegratedState) -> dict:
        card = pick_handbook(model, state.get("request", ""), list_cards(AVAILABLE_HANDBOOKS))
        return {"skill_name": card["name"], "skill": read_body(card)}

    return skill_loader


def make_give_feedback(model, feedback_char_limit: int):
    def give_feedback(state: IntegratedState) -> dict:
        read_spec = make_read_spec(state.get("spec", ""))
        system_prompt = (
            f"{state['skill']}\n\n"
            "# Your tools\n"
            "- check_naming: checks variable naming (a script that comes with the handbook). Use it when naming comes up, and copy its result as is\n"
            "- run_code: runs the homework and shows the output\n"
            "- read_spec: reads the assignment requirements\n"
            "You decide whether to use a tool and which one.\n\n"
            "# Format (the outer workflow checks it with code and sends back anything that fails)\n"
            '- Write only two paragraphs: the first starts with "Strengths:", the second starts with "Improvements:"\n'
            f'- The whole feedback (including "Strengths:", "Improvements:", and line breaks) must be at most {feedback_char_limit} characters'
        )
        if state.get("format_problem"):
            system_prompt += f"\n\nThe previous version was rejected because: {state['format_problem']}. Please fix it."
        inner_agent = create_agent(model, tools=[check_naming, run_code, read_spec], system_prompt=system_prompt)
        result = inner_agent.invoke(
            {"messages": [{"role": "user", "content": f"Please review this homework:\n```python\n{state['code']}\n```"}]},
            config={"recursion_limit": 25},
        )
        messages = result["messages"]
        used = [c["name"] for m in messages for c in (getattr(m, "tool_calls", None) or [])]
        return {"feedback": messages[-1].text.strip(), "retries": state.get("retries", 0) + 1, "tools_used": used}

    return give_feedback


def run_station_by_station(helper, inputs, config: dict) -> dict:
    """Run one station at a time, print which fields each station wrote, and return the State in the checkpoint when it finishes (or is interrupted)."""
    for event in helper.stream(inputs, config=config, stream_mode="updates"):
        for station, writes in event.items():
            if station == "__interrupt__":
                print("⏸️  Interrupted: the flow stops here, and the State is already saved in the checkpoint")
                continue
            print(f"▶ {station}")
            for key, value in (writes or {}).items():
                text = value if isinstance(value, str) else repr(value)
                if key == "skill":
                    text = text.splitlines()[0] + " ... (handbook body)"
                print(f"    {key}: {text[:200]}")
    return helper.get_state(config).values


def open_checkpointer(path: Path = CHECKPOINT_PATH) -> SqliteSaver:
    """Save the State into a SQLite file. As long as the same file still exists, you can read it back by thread_id."""
    return SqliteSaver(sqlite3.connect(str(path), check_same_thread=False))


def build_integrated_helper(model, checkpointer=None, max_retries: int = 3, feedback_char_limit: int = 750,
                interrupt_before: list[str] | None = None):
    builder = StateGraph(IntegratedState)
    builder.add_node("check_syntax", check_syntax)
    builder.add_node("explain_error", explain_error)
    builder.add_node("skill_loader", make_skill_loader(model))
    builder.add_node("give_feedback", make_give_feedback(model, feedback_char_limit))
    builder.add_node("check_format", make_check_format(feedback_char_limit))

    builder.add_edge(START, "check_syntax")
    # If the syntax is OK, go pick a handbook first, then give feedback
    builder.add_conditional_edges(
        "check_syntax", route_after_syntax, {"give_feedback": "skill_loader", "explain_error": "explain_error"}
    )
    builder.add_edge("explain_error", END)
    builder.add_edge("skill_loader", "give_feedback")
    builder.add_edge("give_feedback", "check_format")
    builder.add_conditional_edges("check_format", make_route_after_format(max_retries), ["give_feedback", END])
    return builder.compile(checkpointer=checkpointer, interrupt_before=interrupt_before)


# Compatibility aliases for calls from an older version of the code; the new materials use the "integrated" names.
DualCoreState = IntegratedState
build_dual_core_helper = build_integrated_helper
