"""1-B: the Homework Helper as an agent. The route is decided by the AI.

Agent = model + tools + loop.
- make_agent()          : the standard LangChain 1.0 way, create_agent, which builds an agent in one line
- make_expanded_agent() : the same agent assembled by hand with LangGraph, so you can see the loop underneath
- pretty_trace()        : prints every step so you can see which tool it picked
"""

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from tools.check_indent import check_indent
from tools.read_spec import read_spec
from tools.run_code import run_code

base_system_prompt = (
    "You are a Python homework helper. The students are beginners who just learned Python, so give feedback in English with a gentle tone. "
    "You have a few tools. You decide whether to use one, which one, and how many times. "
    'Write the feedback in two paragraphs: the first starts with "Strengths:" and the second starts with "Improvements:".'
)
helper_tools = [run_code, check_indent, read_spec]


def make_agent(model, system_prompt: str = base_system_prompt, tools=None):
    return create_agent(model, tools=tools or helper_tools, system_prompt=system_prompt)


def make_expanded_agent(model, system_prompt: str = base_system_prompt, tools=None):
    """The core loop for teaching: it expands how the model and the tools interact. It is not the full implementation of create_agent."""
    tools = tools or helper_tools
    model_with_tools = model.bind_tools(tools)

    def ask_model(state: MessagesState) -> dict:
        messages = [SystemMessage(system_prompt)] + state["messages"]
        return {"messages": [model_with_tools.invoke(messages)]}

    builder = StateGraph(MessagesState)
    builder.add_node("ask_model", ask_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "ask_model")
    # tools_condition: if the last message has tool_calls go to tools, otherwise go to END
    builder.add_conditional_edges("ask_model", tools_condition)
    builder.add_edge("tools", "ask_model")  # after tools run, loop back to ask_model
    return builder.compile()


def homework_message(homework: str) -> str:
    return f"Please look at this homework:\n```python\n{homework}\n```"


def pretty_trace(graph, user_message: str, config: dict | None = None) -> list[dict]:
    events = []
    print(f"USER: {user_message}\n")
    inputs = {"messages": [{"role": "user", "content": user_message}]}
    stream = graph.stream(inputs, config=config or {}, stream_mode="updates")
    for step, event in enumerate(stream, start=1):
        events.append(event)
        for node_name, node_state in event.items():
            print(f"--- Step {step} | node: {node_name} ---")
            for msg in (node_state or {}).get("messages", []):
                role = type(msg).__name__
                tool_calls = getattr(msg, "tool_calls", None)
                if tool_calls:
                    for call in tool_calls:
                        print(f"  The model decided to call -> {call['name']}({call['args']})")
                else:
                    text = msg.text if hasattr(msg, "text") else str(msg.content)
                    if len(text) > 400:
                        text = text[:400] + "..."
                    print(f"  [{role}] {text}")
            print()
    return events


def tool_sequence(messages_or_events) -> list[str]:
    """Pull the order of tool calls out of messages (or out of the events from pretty_trace)."""
    messages = []
    for item in messages_or_events:
        if isinstance(item, dict):
            for node_state in item.values():
                messages += (node_state or {}).get("messages", [])
        else:
            messages.append(item)
    return [c["name"] for m in messages for c in (getattr(m, "tool_calls", None) or [])]


def final_reply(messages_or_events) -> str:
    messages = []
    for item in messages_or_events:
        if isinstance(item, dict):
            for node_state in item.values():
                messages += (node_state or {}).get("messages", [])
        else:
            messages.append(item)
    for m in reversed(messages):
        if m.type == "ai" and not getattr(m, "tool_calls", None):
            return m.text
    return ""
