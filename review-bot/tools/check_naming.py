"""check_naming：把 Skill 的腳本 scripts/check_naming.py 包成 agent 的工具。

腳本外面包一層 @tool，就進了 agent 的工具箱：
AI 只負責「決定要不要跑」和「把結果抄進回饋」，檢查本身是 Python，每次都一樣。
"""

import subprocess
import sys
from pathlib import Path

from langchain.tools import tool

腳本 = Path(__file__).resolve().parent.parent / "skills" / "naming-check" / "scripts" / "check_naming.py"


def 執行命名腳本(code: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(腳本)], input=code.encode("utf-8"), capture_output=True, timeout=10
    )
    out = proc.stdout.decode("utf-8").strip()
    return out or "腳本執行失敗：" + proc.stderr.decode("utf-8", "replace").strip()[-200:]


@tool
def check_naming(code: str) -> str:
    """檢查變數與函式名稱是否為小寫加底線（snake_case），回傳不合規則的行。

    什麼時候用：批改作業、需要列出命名問題時（這是 naming-check 手冊附的腳本）。
    參數 code：完整的 Python 程式碼（字串）。
    回傳：每個問題一行，例如「第 3 行：myVar 不符合規則（建議 my_var）」；全部合格時回傳「OK：…」。
    """
    return 執行命名腳本(code)
