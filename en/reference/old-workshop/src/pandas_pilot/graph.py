"""Assemble the graph for the Data Analyst Agent."""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .tools import inspect_data, run_pandas

DEFAULT_SYSTEM_PROMPT = """You are a careful data analysis assistant.

Ground rules for the workflow:
1. For any question, first call inspect_data to see the data's shape, columns, and missing values.
2. Only call run_pandas for analysis after you have looked at inspect_data.
3. Handle all missing values before you report results.
4. Reply in English. Give the conclusion first, then the key numbers.
"""


def build_graph(system_prompt: str | None = None):
    """Build the ReAct agent graph.

    Args:
        system_prompt: Optional system prompt. Pass None to run the baseline version (no system prompt).
    Returns:
        compiled graph
    """
    tools = [inspect_data, run_pandas]
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
    llm_with_tools = llm.bind_tools(tools)

    def chatbot(state: MessagesState) -> dict:
        messages = state["messages"]
        # If none is given, run the baseline; if one is given, make sure the system prompt always comes first in messages
        if system_prompt is not None and (
            not messages or not isinstance(messages[0], SystemMessage)
        ):
            messages = [SystemMessage(content=system_prompt), *messages]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("chatbot", chatbot)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")

    return builder.compile()
