"""Model adapter: wraps either "Colab's built-in model" or "the instructor's Gemini API key" into one model object.

Students don't need to read this file. Every later cell only writes model.invoke(...) and model.bind_tools(...),
and it works the same no matter which provider is behind it.

- colab : google.colab.ai.generate_text (works with a free account, no API key needed)
- gemini: langchain_google_genai.ChatGoogleGenerativeAI (needs GOOGLE_API_KEY)

generate_text takes only one piece of text and returns only one piece of text. It has no native tool calling.
So ColabAIChat adds a small adapter:
1. It joins the messages into one text (system instructions, user, AI, and tool results each get a header)
2. When tools are bound, it appends the tool list and asks the model to "reply with a single line of JSON if you need a tool"
3. It parses the model's JSON into tool_calls, in exactly the same format as native tool calling
This lets you see that the model only ever "says" which tool it wants.
"""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool

SETTINGS_FILE = Path(__file__).with_name(".llm.json")
DEFAULT_GEMINI_MODEL = "gemini-flash-latest"


def estimate_tokens(text: str) -> int:
    """Rough token estimate: about 4 characters per token for English text.
    This is only a guess. A real tokenizer can count noticeably more or fewer."""
    return max(1, round(len(text) / 4))


# ---------- Join the messages into one text ----------

def _describe_tools(tools: list[dict]) -> str:
    lines = []
    for t in tools:
        fn = t.get("function", t)
        props = fn.get("parameters", {}).get("properties", {})
        params = ", ".join(f"{k}: {v.get('type', 'string')}" for k, v in props.items())
        desc = " ".join((fn.get("description") or "").split())
        lines.append(f"- {fn['name']}({params}): {desc}")
    return "\n".join(lines)


def _messages_to_text(messages: list[BaseMessage], tools: list[dict] | None, tool_choice: Any) -> str:
    parts = []
    for m in messages:
        if m.type == "system":
            parts.append(f"=== System instructions ===\n{m.text}")
        elif m.type == "human":
            parts.append(f"=== User ===\n{m.text}")
        elif m.type == "ai":
            if m.tool_calls:
                calls = [{"name": c["name"], "args": c["args"]} for c in m.tool_calls]
                parts.append("=== AI ===\n" + json.dumps({"tool_calls": calls}, ensure_ascii=False))
            else:
                parts.append(f"=== AI ===\n{m.text}")
        elif m.type == "tool":
            name = getattr(m, "name", None) or "tool"
            parts.append(f"=== Result of tool {name} ===\n{m.text}")
    if tools:
        must = ""
        if tool_choice in ("any", "required"):
            must = "This time you must call at least one tool.\n"
        elif isinstance(tool_choice, str) and tool_choice not in ("auto", "none"):
            must = f"This time you must call {tool_choice}.\n"
        parts.append(
            "=== Tools you can use ===\n"
            f"{_describe_tools(tools)}\n\n"
            "=== Reply rules ===\n"
            f"{must}"
            "If you need to use a tool, reply with a single line of JSON only. Add no other text and no ``` marks:\n"
            '{"tool_calls": [{"name": "tool name", "args": {"parameter name": "parameter value"}}]}\n'
            "If you don't need a tool (for example, you already have enough information), just answer in plain text and output no JSON."
        )
    parts.append("=== AI ===")
    return "\n\n".join(parts)


def _parse_reply(text: str, tools: list[dict] | None) -> AIMessage:
    """If the model replied with a JSON note, turn it into tool_calls. Otherwise treat it as plain text."""
    meta = {"raw_text": text, "model_provider": "colab"}
    if tools:
        s = text.strip()
        s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s)
        start, end = s.find("{"), s.rfind("}")
        if start != -1 and end > start and ("tool_calls" in s or s.startswith("{")):
            try:
                data = json.loads(s[start : end + 1])
            except json.JSONDecodeError:
                data = None
            calls = None
            if isinstance(data, dict):
                if isinstance(data.get("tool_calls"), list):
                    calls = data["tool_calls"]
                elif "name" in data or "tool" in data:
                    calls = [data]
            if calls:
                tool_calls = []
                for c in calls:
                    if not isinstance(c, dict):
                        continue
                    name = c.get("name") or c.get("tool")
                    args = c.get("args") or c.get("arguments") or {}
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except json.JSONDecodeError:
                            args = {}
                    if name:
                        tool_calls.append(
                            {"name": name, "args": args, "id": f"call_{uuid.uuid4().hex[:8]}", "type": "tool_call"}
                        )
                if tool_calls:
                    return AIMessage(content="", tool_calls=tool_calls, response_metadata=meta)
    return AIMessage(content=text, response_metadata=meta)


class ColabAIChat(BaseChatModel):
    """Wraps google.colab.ai.generate_text as a LangChain chat model."""

    model_name: str | None = None
    max_retries: int = 3

    @property
    def _llm_type(self) -> str:
        return "colab-ai"

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        formatted = [convert_to_openai_tool(t) for t in tools]
        return self.bind(tools=formatted, tool_choice=tool_choice)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        from google.colab import ai

        tools = kwargs.get("tools")
        prompt = _messages_to_text(messages, tools, kwargs.get("tool_choice"))
        extra = {"model_name": self.model_name} if self.model_name else {}
        for attempt in range(self.max_retries):
            try:
                text = ai.generate_text(prompt, **extra) or ""
                break
            except Exception:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 * (attempt + 1))
        message = _parse_reply(text, tools)
        message.usage_metadata = {
            "input_tokens": estimate_tokens(prompt),
            "output_tokens": estimate_tokens(text),
            "total_tokens": estimate_tokens(prompt) + estimate_tokens(text),
        }
        message.response_metadata["token_count"] = "estimate (Colab's built-in model does not report usage)"
        return ChatResult(generations=[ChatGeneration(message=message)])


# ---------- Public: settings and getting the model ----------

def load_settings() -> dict:
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_settings(provider: str, colab_model: str = "", gemini_model: str = "") -> None:
    """Remember which model provider was chosen (the API key is not saved)."""
    SETTINGS_FILE.write_text(
        json.dumps(
            {"provider": provider, "colab_model": colab_model, "gemini_model": gemini_model or DEFAULT_GEMINI_MODEL},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _find_api_key() -> str | None:
    if os.environ.get("GOOGLE_API_KEY"):
        return os.environ["GOOGLE_API_KEY"]
    try:
        from google.colab import userdata

        key = userdata.get("GOOGLE_API_KEY")
        if key:
            os.environ["GOOGLE_API_KEY"] = key
            return key
    except Exception:
        pass
    return None


def get_model() -> BaseChatModel:
    cfg = load_settings()
    # In the cloud there is no settings file: use the environment variable WORKSHOP_PROVIDER=gemini (the key is read from GOOGLE_API_KEY)
    provider = os.environ.get("WORKSHOP_PROVIDER") or cfg.get("provider", "colab")
    if provider == "gemini":
        key = _find_api_key()
        if not key:
            raise RuntimeError(
                "You chose gemini but no API key was found. Add GOOGLE_API_KEY under 🔑 Secrets on the left, "
                "or paste the key from the instructor into the form in \"0. Environment setup\", then rerun that cell."
            )
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=cfg.get("gemini_model") or DEFAULT_GEMINI_MODEL, google_api_key=key, max_retries=3
        )
    try:
        from google.colab import ai  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("google.colab.ai only works on Google Colab. If you are not on Colab, choose gemini instead.") from exc
    return ColabAIChat(model_name=cfg.get("colab_model") or None)
