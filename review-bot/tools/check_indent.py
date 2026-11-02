"""check_indent：檢查縮排與每行長度。

故意「只」檢查縮排和行長、不碰變數命名：命名檢查留給第 2 堂 2-B，
用來比較「寫在手冊文字裡」和「寫成腳本」的差別。
"""

from langchain.tools import tool

行長上限 = 79


def 檢查縮排(code: str, 上限: int = 行長上限) -> str:
    問題 = []
    for i, line in enumerate(code.splitlines(), start=1):
        if not line.strip():
            continue
        開頭空白 = line[: len(line) - len(line.lstrip())]
        if "\t" in 開頭空白:
            問題.append(f"第 {i} 行：用了 Tab 縮排，建議改成 4 個空白")
        elif len(開頭空白) % 4 != 0:
            問題.append(f"第 {i} 行：縮排 {len(開頭空白)} 格，建議用 4 的倍數")
        if len(line) > 上限:
            問題.append(f"第 {i} 行：有 {len(line)} 個字元，超過 {上限}")
    return "\n".join(問題) if 問題 else "OK：縮排與行長都沒問題"


@tool
def check_indent(code: str) -> str:
    """檢查 Python 作業的縮排（是否為 4 的倍數、有沒有混用 Tab）與每行長度（上限 79 字元）。

    什麼時候用：想確認作業的排版整不整齊時。不會檢查變數命名，也不會執行程式。
    參數 code：完整的 Python 程式碼（字串）。
    回傳：每個問題一行，例如「第 2 行：縮排 2 格，建議用 4 的倍數」；全部沒問題時回傳「OK：…」。
    """
    return 檢查縮排(code)
