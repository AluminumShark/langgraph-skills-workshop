"""檢查變數與函式名稱是不是小寫英文加底線（snake_case）。

用法：
    python check_naming.py 作業.py        # 檢查一個檔案
    python check_naming.py < 作業.py      # 或從標準輸入讀
輸出：
    每個問題一行，例如「第 3 行：myVar 不符合規則（建議 my_var）」
    全部合格時印「OK：所有變數與函式名稱都是小寫加底線」

一個腳本只做一件事、輸出短短幾行，AI 才看得懂；每次執行結果都一模一樣。
"""

import ast
import re
import sys

規則 = re.compile(r"^_?[a-z][a-z0-9_]*$")


def 建議名稱(name: str) -> str:
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    return re.sub(r"_+", "_", s).lower()


def 找出所有名稱(tree: ast.AST) -> dict[str, int]:
    """名稱 → 第一次出現的行號（變數、函式、參數，不含 class 名稱）。"""
    名稱 = {}

    def 記(name, line):
        if name not in 名稱 or line < 名稱[name]:
            名稱[name] = line

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            記(node.id, node.lineno)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            記(node.name, node.lineno)
        elif isinstance(node, ast.arg) and node.arg not in ("self", "cls"):
            記(node.arg, node.lineno)
    return 名稱


def 檢查命名(code: str) -> str:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"無法檢查：第 {e.lineno} 行有語法錯誤"
    問題 = [
        f"第 {line} 行：{name} 不符合規則（建議 {建議名稱(name)}）"
        for name, line in sorted(找出所有名稱(tree).items(), key=lambda x: (x[1], x[0]))
        if not 規則.match(name)
    ]
    return "\n".join(問題) if 問題 else "OK：所有變數與函式名稱都是小寫加底線"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            source = f.read()
    else:
        source = sys.stdin.buffer.read().decode("utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(檢查命名(source))
