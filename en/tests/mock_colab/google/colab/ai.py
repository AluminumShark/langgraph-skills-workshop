"""A fake google.colab.ai: forwards calls to fake_llm (used only for local verification)."""

import fake_llm

__all__ = ["generate_text", "list_models"]


def generate_text(prompt: str, model_name: str = "google/gemini-fake", stream: bool = False):
    if not prompt:
        raise ValueError("Prompt cannot be empty.")
    return fake_llm.generate_text(prompt, model_name=model_name, stream=stream)


def list_models() -> list[str]:
    return ["google/gemini-fake"]
