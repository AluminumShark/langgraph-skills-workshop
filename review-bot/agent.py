"""1-B：作業小助教的 agent 版，路線由 AI 決定。

Agent = 模型 + 工具 + 迴圈。
- 建立_agent()      ：LangChain 1.0 的標準寫法 create_agent，一行做出 agent
- 建立_展開版_agent()：同一個 agent 自己用 LangGraph 組出來，看清楚底下的迴圈
- pretty_trace()    ：把每一步攤開印出來，看它選了哪個工具
"""

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from tools.check_indent import check_indent
from tools.read_spec import read_spec
from tools.run_code import run_code

基本_system_prompt = (
    "你是 Python 作業小助教。學生是剛學會 Python 的初學者，請用繁體中文、溫和的語氣給回饋。"
    "你有幾個工具可以用：要不要用、用哪一個、用幾次，由你自己決定。"
    "回饋分兩段：第一段以「優點：」開頭，第二段以「改進：」開頭。"
)
小助教的工具 = [run_code, check_indent, read_spec]


def 建立_agent(model, system_prompt: str = 基本_system_prompt, tools=None):
    return create_agent(model, tools=tools or 小助教的工具, system_prompt=system_prompt)


def 建立_展開版_agent(model, system_prompt: str = 基本_system_prompt, tools=None):
    """教學用的核心迴圈：展開模型與工具如何互動，不是 create_agent 的完整實作。"""
    tools = tools or 小助教的工具
    model_with_tools = model.bind_tools(tools)

    def ask_model(state: MessagesState) -> dict:
        messages = [SystemMessage(system_prompt)] + state["messages"]
        return {"messages": [model_with_tools.invoke(messages)]}

    builder = StateGraph(MessagesState)
    builder.add_node("ask_model", ask_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "ask_model")
    # tools_condition：上一則訊息有 tool_calls 就走 tools，否則走 END
    builder.add_conditional_edges("ask_model", tools_condition)
    builder.add_edge("tools", "ask_model")  # tools 跑完繞回 ask_model
    return builder.compile()


def 作業訊息(作業: str) -> str:
    return f"幫我看這段作業：\n```python\n{作業}\n```"


def pretty_trace(graph, user_message: str, config: dict | None = None) -> list[dict]:
    events = []
    print(f"USER: {user_message}\n")
    inputs = {"messages": [{"role": "user", "content": user_message}]}
    stream = graph.stream(inputs, config=config or {}, stream_mode="updates")
    for step, event in enumerate(stream, start=1):
        events.append(event)
        for node_name, node_state in event.items():
            print(f"--- 第 {step} 步 | 節點: {node_name} ---")
            for msg in (node_state or {}).get("messages", []):
                role = type(msg).__name__
                tool_calls = getattr(msg, "tool_calls", None)
                if tool_calls:
                    for call in tool_calls:
                        print(f"  模型決定呼叫 -> {call['name']}({call['args']})")
                else:
                    text = msg.text if hasattr(msg, "text") else str(msg.content)
                    if len(text) > 400:
                        text = text[:400] + "..."
                    print(f"  [{role}] {text}")
            print()
    return events


def 工具順序(messages_or_events) -> list[str]:
    """從 messages（或 pretty_trace 的 events）抽出工具呼叫的順序。"""
    messages = []
    for item in messages_or_events:
        if isinstance(item, dict):
            for node_state in item.values():
                messages += (node_state or {}).get("messages", [])
        else:
            messages.append(item)
    return [c["name"] for m in messages for c in (getattr(m, "tool_calls", None) or [])]


def 最後回覆(messages_or_events) -> str:
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
