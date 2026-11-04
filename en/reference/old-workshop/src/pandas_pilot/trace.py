"""Print the graph.stream event stream nicely, so the instructor can debug live."""

from __future__ import annotations

from typing import Any


def pretty_trace(graph, user_message: str, *, config: dict[str, Any] | None = None) -> list[dict]:
    """Run the graph and print each node's decisions as they happen.

    Args:
        graph: a compiled LangGraph
        user_message: the user's message
        config: config for graph.stream (optional)
    Returns:
        The raw event for each step (handy for further analysis)
    """
    events: list[dict] = []
    inputs = {"messages": [{"role": "user", "content": user_message}]}

    print(f"USER: {user_message}\n")

    for step, event in enumerate(
        graph.stream(inputs, config=config, stream_mode="updates"),
        start=1,
    ):
        events.append(event)
        for node_name, node_state in event.items():
            print(f"--- step {step} | node: {node_name} ---")
            messages = node_state.get("messages", [])
            for msg in messages:
                _print_message(msg)
            print()

    return events


def _print_message(msg) -> None:
    role = type(msg).__name__
    tool_calls = getattr(msg, "tool_calls", None)

    if tool_calls:
        for call in tool_calls:
            name = call.get("name") if isinstance(call, dict) else getattr(call, "name", "?")
            args = call.get("args") if isinstance(call, dict) else getattr(call, "args", {})
            print(f"  [{role}] tool_call -> {name}({args})")
    else:
        # Use .text to get a plain string from either str or list-of-dict content
        text = msg.text if hasattr(msg, "text") else str(getattr(msg, "content", ""))
        if len(text) > 400:
            text = text[:400] + "..."
        print(f"  [{role}] {text}")
