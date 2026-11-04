"""Small helpers shared by the workshop notebooks (students don't need to read this).

- prepare()                     : the first cell of every part calls it to reconnect the model and reload edited files
- sample_homework               : the sample homework in the form dropdown
- record() / print_history()    : save the results that experiment cells name, then list them by title in the last cell
- show_graph()                  : draw a LangGraph as a diagram
- save_to_drive() / download_zip()
"""

from __future__ import annotations

import datetime as _dt
import importlib
import json
import shutil
import sys
from pathlib import Path

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage

from llm import get_model, estimate_tokens  # noqa: F401  (so notebooks can write: from workshop import estimate_tokens)

__all__ = [
    "BASE", "prepare", "sample_homework", "load_homework", "record", "print_state", "print_order_slip", "print_history", "clear_history",
    "ModelCallCounter", "show_graph", "save_to_drive", "download_zip", "estimate_tokens",
]

BASE = Path(__file__).resolve().parent
HISTORY_FILE = BASE / "history.jsonl"

sample_homework = {
    "Missing parenthesis": "print('hi'\n",
    "Correct program": "def add(a, b):\n    return a + b\n\nprint(add(2, 3))\n",
    "Empty": "",
    "Variable typo": "def add(a, b):\n    total = a + b\n    return summ\n\nprint(add(2, 3))\n",
    "Messy indentation": "def average(scores):\n  total = 0\n  for s in scores:\n        total += s\n  return total / len(scores)\n\nprint(average([90, 85, 77]))\n",
    "Inconsistent naming": (
        "def CalcAverage(scoreList):\n"
        "    Total = 0\n"
        "    for s in scoreList:\n"
        "        Total += s\n"
        "    avgScore = Total / len(scoreList)\n"
        "    return avgScore\n"
        "\n"
        "myScores = [90, 85, 77]\n"
        "MAX = 100\n"
        "result_2 = CalcAverage(myScores)\n"
        "print(result_2, '/', MAX)\n"
    ),
}


def load_homework(name: str) -> str:
    """When the form says "My homework", read /content/review-bot/my_homework.py. Otherwise take it from the samples."""
    if name.startswith("My homework"):
        path = BASE / "my_homework.py"
        if not path.exists():
            raise FileNotFoundError('There is no "My homework" yet. Run the cell above that has %%writefile ... my_homework.py first.')
        return path.read_text(encoding="utf-8")
    return sample_homework[name]


def prepare():
    """The start of every part: put review-bot on the import path, reload edited files, and return the model."""
    if str(BASE) not in sys.path:
        sys.path.insert(0, str(BASE))
    importlib.invalidate_caches()
    for name, mod in list(sys.modules.items()):
        path = getattr(mod, "__file__", None) or ""
        if path and Path(path).resolve().is_relative_to(BASE) and name not in ("workshop", "llm"):
            try:
                importlib.reload(mod)
            except Exception:
                sys.modules.pop(name, None)
    _make_mcp_stdio_work_in_notebook()
    return get_model()


def _make_mcp_stdio_work_in_notebook() -> None:
    """mcp's stdio_client connects the MCP server's error output to sys.stderr.
    On Colab (Linux), sys.stderr has a real file descriptor, so this works. Jupyter on Windows has none, so we redirect to a log file."""
    try:
        sys.stderr.fileno()
        return
    except Exception:
        pass
    try:
        import mcp.client.stdio as mcp_stdio
    except ImportError:
        return
    (BASE / "deploy").mkdir(exist_ok=True)
    log = open(BASE / "deploy" / "mcp_server.log", "a", encoding="utf-8")
    mcp_stdio.stdio_client.__wrapped__.__defaults__ = (log,)


# ---------- State history ----------

def _serializable(obj):
    if isinstance(obj, BaseMessage):
        d = {"type": obj.type, "content": obj.text}
        if getattr(obj, "tool_calls", None):
            d["tool_calls"] = [{"name": c["name"], "args": c["args"]} for c in obj.tool_calls]
        if obj.type == "tool":
            d["name"] = getattr(obj, "name", None)
        return d
    if isinstance(obj, dict):
        return {str(k): _serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serializable(v) for v in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def record(title: str, content) -> None:
    """Save this result (usually a State) into history.jsonl."""
    row = {"time": _dt.datetime.now().strftime("%H:%M:%S"), "title": title, "content": _serializable(content)}
    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _short(text, n=300):
    text = str(text)
    return text if len(text) <= n else text[:n] + f"... ({len(text) - n} more characters)"


def print_state(state: dict, indent: str = "  ") -> None:
    for k, v in state.items():
        if k == "messages":
            print(f"{indent}{k}: ({len(v)} messages)")
            for m in v:
                m = _serializable(m)
                if isinstance(m, dict) and m.get("tool_calls"):
                    print(f"{indent}  [{m['type']}] calls {m['tool_calls']}")
                elif isinstance(m, dict):
                    print(f"{indent}  [{m.get('type')}] {_short(m.get('content', ''), 200)}")
        else:
            print(f"{indent}{k}: {_short(repr(v) if not isinstance(v, str) else repr(v), 300)}")


def print_order_slip(step_no: int, state: dict, prev_state: dict | None = None, skip_keys: tuple = ("code",)) -> None:
    """stream_mode="values" gives the whole order slip at every step. This also marks which fields this step newly wrote."""
    if not prev_state:
        note = "start: blank order slip"
    else:
        changed_keys = [k for k in state if state.get(k) != prev_state.get(k)]
        note = "newly written: " + (", ".join(changed_keys) if changed_keys else "(nothing changed)")
    print(f"Step {step_no} ({note})")
    print("  ", {k: (_short(v, 120) if isinstance(v, str) else v) for k, v in state.items() if k not in skip_keys})


def print_history() -> None:
    if not HISTORY_FILE.exists():
        print("There are no records yet. Run a few parts above first, then come back to this cell.")
        return
    rows = [json.loads(line) for line in HISTORY_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"📸 {len(rows)} records (saved in {HISTORY_FILE})\n")
    for i, row in enumerate(rows, 1):
        print(f"===== {i}. [{row['time']}] {row['title']} =====")
        content = row["content"]
        if isinstance(content, dict):
            print_state(content)
        elif isinstance(content, list):
            for j, item in enumerate(content, 1):
                print(f"  --- step {j} ---")
                if isinstance(item, dict):
                    print_state(item, "    ")
                else:
                    print(f"    {_short(item)}")
        else:
            print(f"  {_short(content, 1000)}")
        print()


def clear_history() -> None:
    HISTORY_FILE.unlink(missing_ok=True)


# ---------- Count how many times the model was called ----------

class ModelCallCounter(BaseCallbackHandler):
    """Put it in config={"callbacks": [counter]}. It adds 1 every time the model is called."""

    def __init__(self):
        self.count = 0

    def on_chat_model_start(self, serialized, messages, **kwargs):
        self.count += 1

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.count += 1


# ---------- Draw the graph ----------

def show_graph(graph) -> None:
    g = graph.get_graph()
    try:
        from IPython.display import Image, display

        display(Image(g.draw_mermaid_png()))
    except Exception:
        print("(The drawing service is unreachable for now, so here is a text version. You can paste it into https://mermaid.live to see the diagram.)\n")
        print(g.draw_mermaid())


# ---------- Saving ----------

def save_to_drive() -> None:
    from google.colab import drive

    drive.mount("/content/drive")
    destination = Path("/content/drive/MyDrive/langgraph-skills-workshop") / _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copytree(BASE, destination, ignore=shutil.ignore_patterns("__pycache__", ".llm.json"))
    print(f"✅ Saved to Google Drive: {destination}")
    print('   (Save the notebook itself with the menu above: "File → Save a copy in Drive")')


def download_zip() -> None:
    from google.colab import files

    name = BASE.parent / ("review-bot-" + _dt.datetime.now().strftime("%Y%m%d-%H%M%S"))
    zip_path = shutil.make_archive(str(name), "zip", BASE.parent, BASE.name)
    print(f"✅ Packed: {zip_path}")
    files.download(zip_path)
