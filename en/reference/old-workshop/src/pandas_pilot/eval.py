"""A simple eval suite that checks whether the agent behaves as expected."""

from __future__ import annotations

from typing import Any

# Default demo CSV path (students can change it in the notebook)
DEFAULT_CSV = "data/sales.csv"

EVAL_CASES: list[dict[str, Any]] = [
    {
        "id": "001_must_inspect_first",
        "user_message": f"Give me an overview of the data in {DEFAULT_CSV}.",
        "must_call_first": "inspect_data",
        "must_contain_in_final": [],
    },
    {
        "id": "002_handle_empty_result",
        "user_message": f"In {DEFAULT_CSV}, count the records where region is 'Mars'.",
        "must_call_first": "inspect_data",
        "must_contain_in_final": ["0"],
    },
    {
        "id": "003_inspect_before_summary",
        "user_message": f"Calculate the average revenue in {DEFAULT_CSV} for me.",
        "must_call_first": "inspect_data",
        "must_contain_in_final": [],
    },
    {
        "id": "004_top_region",
        "user_message": f"Analyze {DEFAULT_CSV}: which region has the lowest average revenue?",
        "must_call_first": "inspect_data",
        "must_contain_in_final": [],
    },
    {
        "id": "005_count_rows",
        "user_message": f"How many rows are there in {DEFAULT_CSV}?",
        "must_call_first": "inspect_data",
        "must_contain_in_final": [],
    },
]


def extract_tool_calls(events: list[dict]) -> list[str]:
    """Pull the order of tool calls (by name) out of the graph.stream events."""
    names: list[str] = []
    for event in events:
        for _node, state in event.items():
            for msg in state.get("messages", []) or []:
                tool_calls = getattr(msg, "tool_calls", None) or []
                for call in tool_calls:
                    name = (
                        call.get("name") if isinstance(call, dict) else getattr(call, "name", None)
                    )
                    if name:
                        names.append(name)
    return names


def extract_final_text(events: list[dict]) -> str:
    """Get the text of the last message produced by the chatbot node that has no tool_calls."""
    final = ""
    for event in events:
        for node, state in event.items():
            if node != "chatbot":
                continue
            for msg in state.get("messages", []) or []:
                tool_calls = getattr(msg, "tool_calls", None)
                if not tool_calls:
                    # Use .text to handle the list-of-dict content from gemini-2.5+ the same way
                    final = msg.text if hasattr(msg, "text") else str(getattr(msg, "content", "") or "")
    return final


def evaluate_one(graph, case: dict[str, Any]) -> dict[str, Any]:
    """Run one eval case and return pass / fail with details."""
    inputs = {"messages": [{"role": "user", "content": case["user_message"]}]}
    events = list(graph.stream(inputs, stream_mode="updates"))

    tool_calls = extract_tool_calls(events)
    final_text = extract_final_text(events)

    reasons: list[str] = []
    must_call_first = case.get("must_call_first")
    if must_call_first:
        if not tool_calls:
            reasons.append(f"no tool called (expected {must_call_first} first)")
        elif tool_calls[0] != must_call_first:
            reasons.append(f"first tool was {tool_calls[0]}, expected {must_call_first}")

    for keyword in case.get("must_contain_in_final", []):
        if keyword not in final_text:
            reasons.append(f"final reply is missing keyword: {keyword!r}")

    passed = len(reasons) == 0
    return {
        "id": case["id"],
        "passed": passed,
        "reasons": reasons,
        "tool_calls": tool_calls,
        "final_text": final_text,
    }


def run_eval_suite(graph, cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Run the whole eval suite, print a summary, and return the results."""
    cases = cases if cases is not None else EVAL_CASES
    results = []
    for case in cases:
        result = evaluate_one(graph, case)
        mark = "PASS" if result["passed"] else "FAIL"
        print(f"[{mark}] {result['id']}  tool_calls={result['tool_calls']}")
        for reason in result["reasons"]:
            print(f"        - {reason}")
        results.append(result)

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"\nPassed {passed}/{total} ({passed / total:.0%})")
    return {"results": results, "passed": passed, "total": total}
