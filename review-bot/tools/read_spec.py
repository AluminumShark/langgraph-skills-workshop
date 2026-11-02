"""read_spec：讀這一題的作業要求。

題目要求存在 review-bot/spec.md，notebook 的表單改了題目就會重寫這個檔案。
"""

from pathlib import Path

from langchain.tools import tool

題目檔 = Path(__file__).resolve().parent.parent / "spec.md"


def 讀題目() -> str:
    if not 題目檔.exists():
        return "（這一題沒有提供作業要求）"
    return 題目檔.read_text(encoding="utf-8").strip() or "（這一題沒有提供作業要求）"


@tool
def read_spec() -> str:
    """讀取這一題的作業要求（題目寫了什麼、要交什麼）。

    什麼時候用：要判斷作業有沒有做到題目要求之前，例如函式名稱、輸出格式對不對。
    不需要參數。
    回傳：題目要求的全文。
    """
    return 讀題目()
