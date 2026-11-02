"""模型轉接頭：把「Colab 內建模型」或「講師的 Gemini API key」包成同一個 model 物件。

學生不用看這個檔案。後面所有 cell 都只寫 model.invoke(...)、model.bind_tools(...)，
不管背後是哪一家模型，用法都一樣。

- colab ：google.colab.ai.generate_text（免費帳號可用，不需要 API key）
- gemini：langchain_google_genai.ChatGoogleGenerativeAI（需要 GOOGLE_API_KEY）

generate_text 只吃一段文字、只回一段文字，不支援原生的 tool calling。
所以 ColabAIChat 做了一個小轉接：
1. 把多則訊息接成一段文字（系統指示、使用者、AI、工具結果各標一個標題）
2. 有綁工具時，在文字最後附上工具清單，請模型「需要工具就只回一行 JSON」
3. 把模型回的 JSON 解析成 tool_calls，格式和原生 tool calling 一模一樣
這剛好讓你看到：模型從頭到尾只是在「說」它想用哪個工具。
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

設定檔 = Path(__file__).with_name(".llm.json")
預設_gemini_模型 = "gemini-flash-latest"


def 估算_token(text: str) -> int:
    """粗估 token 數：中日韓文字約 1 字 1 token，其他字元約 4 個 1 token。"""
    cjk = len(re.findall(r"[⺀-鿿豈-﫿＀-￯]", text))
    return max(1, round(cjk + (len(text) - cjk) / 4))


# ---------- 把訊息接成一段文字 ----------

def _工具說明(tools: list[dict]) -> str:
    lines = []
    for t in tools:
        fn = t.get("function", t)
        props = fn.get("parameters", {}).get("properties", {})
        params = ", ".join(f"{k}: {v.get('type', 'string')}" for k, v in props.items())
        desc = " ".join((fn.get("description") or "").split())
        lines.append(f"- {fn['name']}({params})：{desc}")
    return "\n".join(lines)


def _訊息轉文字(messages: list[BaseMessage], tools: list[dict] | None, tool_choice: Any) -> str:
    parts = []
    for m in messages:
        if m.type == "system":
            parts.append(f"【系統指示】\n{m.text}")
        elif m.type == "human":
            parts.append(f"【使用者】\n{m.text}")
        elif m.type == "ai":
            if m.tool_calls:
                calls = [{"name": c["name"], "args": c["args"]} for c in m.tool_calls]
                parts.append("【AI】\n" + json.dumps({"tool_calls": calls}, ensure_ascii=False))
            else:
                parts.append(f"【AI】\n{m.text}")
        elif m.type == "tool":
            name = getattr(m, "name", None) or "工具"
            parts.append(f"【工具 {name} 的結果】\n{m.text}")
    if tools:
        must = ""
        if tool_choice in ("any", "required"):
            must = "這一次你一定要呼叫至少一個工具。\n"
        elif isinstance(tool_choice, str) and tool_choice not in ("auto", "none"):
            must = f"這一次你一定要呼叫 {tool_choice}。\n"
        parts.append(
            "【你可以用的工具】\n"
            f"{_工具說明(tools)}\n\n"
            "【回覆規則】\n"
            f"{must}"
            "如果你需要使用工具，只回一行 JSON，不要加任何其他文字、也不要加 ``` 符號：\n"
            '{"tool_calls": [{"name": "工具名稱", "args": {"參數名稱": "參數值"}}]}\n'
            "如果不需要工具（例如已經有足夠的資訊），就直接用一般文字回答，不要輸出 JSON。"
        )
    parts.append("【AI】")
    return "\n\n".join(parts)


def _解析回覆(text: str, tools: list[dict] | None) -> AIMessage:
    """模型回的是 JSON 紙條就轉成 tool_calls，否則當成一般文字。"""
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
    """把 google.colab.ai.generate_text 包成 LangChain 的聊天模型。"""

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
        prompt = _訊息轉文字(messages, tools, kwargs.get("tool_choice"))
        extra = {"model_name": self.model_name} if self.model_name else {}
        for attempt in range(self.max_retries):
            try:
                text = ai.generate_text(prompt, **extra) or ""
                break
            except Exception:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 * (attempt + 1))
        message = _解析回覆(text, tools)
        message.usage_metadata = {
            "input_tokens": 估算_token(prompt),
            "output_tokens": 估算_token(text),
            "total_tokens": 估算_token(prompt) + 估算_token(text),
        }
        message.response_metadata["token_count"] = "估算值（Colab 內建模型不回報用量）"
        return ChatResult(generations=[ChatGeneration(message=message)])


# ---------- 對外：設定與取得 model ----------

def 讀設定() -> dict:
    try:
        return json.loads(設定檔.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def 存設定(provider: str, colab_model: str = "", gemini_model: str = "") -> None:
    """記住選了哪個模型來源（不存 API key）。"""
    設定檔.write_text(
        json.dumps(
            {"provider": provider, "colab_model": colab_model, "gemini_model": gemini_model or 預設_gemini_模型},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _找_api_key() -> str | None:
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
    cfg = 讀設定()
    # 上雲端時沒有設定檔：用環境變數 WORKSHOP_PROVIDER=gemini（金鑰從 GOOGLE_API_KEY 讀）
    provider = os.environ.get("WORKSHOP_PROVIDER") or cfg.get("provider", "colab")
    if provider == "gemini":
        key = _找_api_key()
        if not key:
            raise RuntimeError(
                "選了 gemini 但找不到 API key：請在左邊 🔑「密鑰」新增 GOOGLE_API_KEY，"
                "或在「0. 環境設定」的表單貼上講師提供的 key，再重跑那一格。"
            )
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=cfg.get("gemini_model") or 預設_gemini_模型, google_api_key=key, max_retries=3
        )
    try:
        from google.colab import ai  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("google.colab.ai 只能在 Google Colab 上使用；不在 Colab 的話請改選 gemini。") from exc
    return ColabAIChat(model_name=cfg.get("colab_model") or None)
