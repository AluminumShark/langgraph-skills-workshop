"""run_code：在教學限制下執行學生的作業。

學生作業裡什麼都可能有（import os 刪檔、無限迴圈），所以這個工具有兩道執行限制，加上一個方便閱讀的設計：
1. 執行前先檢查：只准 import 少數標準模組（math、random、re…），os / sys / subprocess 這類一律擋下；
   也不准用 eval、exec、open、input 和底線開頭的屬性（常被拿來繞過限制）
2. 開一個獨立的子程序執行，超過時間就強制停止（無限迴圈也停得下來）
3. 只回一行結果（第幾行、什麼錯），方便人與模型閱讀；這不是安全限制

⚠️ 這是教學用的圍欄。正式產品請用真正的 sandbox（容器、RestrictedPython、e2b、Modal）。
"""

import ast
import json
import os
import subprocess
import sys
import tempfile

from langchain.tools import tool

禁止的模組 = {"os", "sys", "subprocess", "shutil", "socket", "pathlib", "ctypes", "importlib",
           "multiprocessing", "threading", "signal", "pickle", "builtins", "io", "inspect", "gc"}
允許的模組 = {"math", "random", "string", "re", "datetime", "collections", "itertools", "functools",
           "statistics", "time", "decimal", "fractions", "json", "copy", "heapq", "bisect"}
禁止的函式 = {"eval", "exec", "compile", "open", "input", "__import__", "globals", "locals", "vars",
           "getattr", "setattr", "delattr", "breakpoint", "help", "exit", "quit", "memoryview"}
禁止的屬性 = {"system", "popen", "modules", "builtins", "f_globals", "f_back", "gi_frame", "cr_frame"}
最長時間_秒 = 3
最長輸出_字 = 800

# 子程序裡真正執行作業的那段程式：用「縮小版的 builtins」執行，import 只放行白名單
_RUNNER = r"""
import builtins, contextlib, io, json, sys, traceback
code = sys.stdin.buffer.read().decode("utf-8")
allowed = set(json.loads(sys.argv[1]))
blocked = set(json.loads(sys.argv[2]))
real_import = builtins.__import__
def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] not in allowed:
        raise ImportError("這個工具不允許 import " + name)
    return real_import(name, globals, locals, fromlist, level)
safe = {k: v for k, v in vars(builtins).items() if k not in blocked}
safe["__import__"] = guarded_import
try:
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
except Exception:
    pass
out = io.StringIO()
result = {"ok": True}
try:
    compiled = compile(code, "作業.py", "exec")
    with contextlib.redirect_stdout(out):
        exec(compiled, {"__builtins__": safe, "__name__": "__main__"})
except SyntaxError as e:
    result = {"ok": False, "line": e.lineno, "error": "SyntaxError: " + str(e.msg)}
except BaseException as e:
    line = None
    for frame in traceback.extract_tb(e.__traceback__):
        if frame.filename == "作業.py":
            line = frame.lineno
    result = {"ok": False, "line": line, "error": type(e).__name__ + ": " + str(e)}
result["stdout"] = out.getvalue()
sys.__stdout__.write(json.dumps(result))
"""


def _先檢查(code: str) -> str | None:
    """執行前的靜態檢查；有問題就回一行說明，沒問題回 None。"""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"❌ 第 {e.lineno} 行 SyntaxError: {e.msg}"
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            for name in names:
                root = name.split(".")[0]
                if root in 禁止的模組 or root not in 允許的模組:
                    return f"⛔ 已擋下：第 {node.lineno} 行 import {name}（這個工具不允許使用 {root}）"
        elif isinstance(node, ast.Name) and node.id in 禁止的函式:
            return f"⛔ 已擋下：第 {node.lineno} 行用了 {node.id}（這個工具不允許）"
        elif isinstance(node, ast.Attribute) and (
            node.attr.startswith("_") or node.attr in 禁止的屬性 or node.attr in 禁止的模組
        ):
            return f"⛔ 已擋下：第 {node.lineno} 行存取了 .{node.attr}（這個工具不允許）"
    return None


def 執行作業(code: str, 最長時間: float = 最長時間_秒) -> str:
    """真正做事的函式：檢查 → 子程序執行 → 回傳一行結果。"""
    if not code.strip():
        return "❌ 作業是空白的，沒有東西可以執行"
    擋下 = _先檢查(code)
    if 擋下:
        return 擋下
    env = {"PYTHONIOENCODING": "utf-8", "PATH": os.environ.get("PATH", "")}
    if os.name == "nt":
        env["SYSTEMROOT"] = os.environ.get("SYSTEMROOT", "")
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", _RUNNER, json.dumps(sorted(允許的模組)), json.dumps(sorted(禁止的函式))],
            input=code, capture_output=True, text=True, encoding="utf-8",
            timeout=最長時間, cwd=tempfile.gettempdir(), env=env,
        )
    except subprocess.TimeoutExpired:
        return f"⏱️ 執行超過 {最長時間:g} 秒被強制停止（可能有無限迴圈）"
    try:
        result = json.loads(proc.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return "❌ 執行失敗（程式沒有正常結束，可能用了太多記憶體）"
    stdout = result.get("stdout", "")
    if len(stdout) > 最長輸出_字:
        stdout = stdout[:最長輸出_字] + "\n…（輸出太長，後面省略）"
    if result["ok"]:
        return f"✅ 執行成功，輸出：\n{stdout}" if stdout else "✅ 執行成功（沒有印出任何東西）"
    where = f"第 {result['line']} 行 " if result.get("line") else ""
    印出 = f"\n（出錯前印出：{stdout.strip()}）" if stdout.strip() else ""
    return f"❌ {where}{result['error']}{印出}"


@tool
def run_code(code: str) -> str:
    """在教學限制下執行一段 Python 作業，回傳輸出或錯誤訊息。

    什麼時候用：想知道作業「實際跑起來」會印出什麼、會不會出錯時。
    參數 code：完整的 Python 程式碼（字串）。
    回傳：一行結果，例如「✅ 執行成功，輸出：5」或「❌ 第 3 行 NameError: ...」。
    限制：只能 import math、random、re 等少數標準模組；不能用 input()、open()；超過 3 秒會被停止。
    """
    return 執行作業(code)
