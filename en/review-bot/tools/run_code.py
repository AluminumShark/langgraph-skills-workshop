"""run_code: runs a student's homework under teaching restrictions.

A student's homework could contain anything (import os to delete files, an infinite loop), so this tool has two execution limits plus one readability feature:
1. A check before running: only a few standard modules may be imported (math, random, re, ...). os / sys / subprocess and the like are always blocked.
   eval, exec, open, input and attributes that start with an underscore (often used to get around restrictions) are not allowed either
2. The code runs in a separate child process, and it is stopped by force when the time runs out (so an infinite loop can be stopped too)
3. It returns only one line of result (which line, what error), which is easier for people and models to read. This is not a security limit

⚠️ This is a teaching fence. For a real product, use a real sandbox (a container, RestrictedPython, e2b, Modal).
"""

import ast
import json
import os
import subprocess
import sys
import tempfile

from langchain.tools import tool

BLOCKED_MODULES = {"os", "sys", "subprocess", "shutil", "socket", "pathlib", "ctypes", "importlib",
           "multiprocessing", "threading", "signal", "pickle", "builtins", "io", "inspect", "gc"}
ALLOWED_MODULES = {"math", "random", "string", "re", "datetime", "collections", "itertools", "functools",
           "statistics", "time", "decimal", "fractions", "json", "copy", "heapq", "bisect"}
BLOCKED_FUNCTIONS = {"eval", "exec", "compile", "open", "input", "__import__", "globals", "locals", "vars",
           "getattr", "setattr", "delattr", "breakpoint", "help", "exit", "quit", "memoryview"}
BLOCKED_ATTRIBUTES = {"system", "popen", "modules", "builtins", "f_globals", "f_back", "gi_frame", "cr_frame"}
TIME_LIMIT = 3
MAX_OUTPUT_CHARS = 800

# The code in the child process that really runs the homework: it uses a "shrunken builtins", and import lets only the allowlist through
_RUNNER = r"""
import builtins, contextlib, io, json, sys, traceback
code = sys.stdin.buffer.read().decode("utf-8")
allowed = set(json.loads(sys.argv[1]))
blocked = set(json.loads(sys.argv[2]))
real_import = builtins.__import__
def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] not in allowed:
        raise ImportError("This tool does not allow import " + name)
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
    compiled = compile(code, "homework.py", "exec")
    with contextlib.redirect_stdout(out):
        exec(compiled, {"__builtins__": safe, "__name__": "__main__"})
except SyntaxError as e:
    result = {"ok": False, "line": e.lineno, "error": "SyntaxError: " + str(e.msg)}
except BaseException as e:
    line = None
    for frame in traceback.extract_tb(e.__traceback__):
        if frame.filename == "homework.py":
            line = frame.lineno
    result = {"ok": False, "line": line, "error": type(e).__name__ + ": " + str(e)}
result["stdout"] = out.getvalue()
sys.__stdout__.write(json.dumps(result))
"""


def _precheck(code: str) -> str | None:
    """A static check before running. If there is a problem, return a one-line explanation. Otherwise return None."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"❌ Line {e.lineno} SyntaxError: {e.msg}"
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            for name in names:
                root = name.split(".")[0]
                if root in BLOCKED_MODULES or root not in ALLOWED_MODULES:
                    return f"⛔ Blocked: line {node.lineno} import {name} (this tool does not allow {root})"
        elif isinstance(node, ast.Name) and node.id in BLOCKED_FUNCTIONS:
            return f"⛔ Blocked: line {node.lineno} uses {node.id} (this tool does not allow it)"
        elif isinstance(node, ast.Attribute) and (
            node.attr.startswith("_") or node.attr in BLOCKED_ATTRIBUTES or node.attr in BLOCKED_MODULES
        ):
            return f"⛔ Blocked: line {node.lineno} accesses .{node.attr} (this tool does not allow it)"
    return None


def run_homework(code: str, time_limit_seconds: float = TIME_LIMIT) -> str:
    """The function that does the real work: check → run in a child process → return one line of result."""
    if not code.strip():
        return "❌ The homework is empty, there is nothing to run"
    blocked = _precheck(code)
    if blocked:
        return blocked
    env = {"PYTHONIOENCODING": "utf-8", "PATH": os.environ.get("PATH", "")}
    if os.name == "nt":
        env["SYSTEMROOT"] = os.environ.get("SYSTEMROOT", "")
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", _RUNNER, json.dumps(sorted(ALLOWED_MODULES)), json.dumps(sorted(BLOCKED_FUNCTIONS))],
            input=code, capture_output=True, text=True, encoding="utf-8",
            timeout=time_limit_seconds, cwd=tempfile.gettempdir(), env=env,
        )
    except subprocess.TimeoutExpired:
        return f"⏱️ Ran longer than {time_limit_seconds:g} seconds and was stopped by force (there may be an infinite loop)"
    try:
        result = json.loads(proc.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return "❌ The run failed (the program did not end normally; it may have used too much memory)"
    stdout = result.get("stdout", "")
    if len(stdout) > MAX_OUTPUT_CHARS:
        stdout = stdout[:MAX_OUTPUT_CHARS] + "\n... (output too long, the rest is omitted)"
    if result["ok"]:
        return f"✅ Ran successfully, output:\n{stdout}" if stdout else "✅ Ran successfully (nothing was printed)"
    where = f"line {result['line']} " if result.get("line") else ""
    output = f"\n(printed before the error: {stdout.strip()})" if stdout.strip() else ""
    return f"❌ {where}{result['error']}{output}"


@tool
def run_code(code: str) -> str:
    """Run a piece of Python homework under teaching restrictions and return the output or the error message.

    When to use it: when you want to know what the homework actually prints when it runs, or whether it errors.
    Parameter code: the complete Python code (a string).
    Returns: one line of result, for example "✅ Ran successfully, output: 5" or "❌ line 3 NameError: ...".
    Limits: it can only import a few standard modules such as math, random and re; it cannot use input() or open(); it is stopped after 3 seconds.
    """
    return run_homework(code)
