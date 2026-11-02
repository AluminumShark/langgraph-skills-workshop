"""工作坊 notebook 共用的小工具（學生不用看）。

- 準備()          ：每一段的第一格都會呼叫，重新連上模型、重新載入改過的檔案
- 範例作業         ：表單下拉選單裡的幾段作業
- 記下() / 印出歷程()：保存實驗格指定的結果，最後一格按紀錄標題列出
- 顯示流程圖()      ：把 LangGraph 畫成圖
- 存到雲端硬碟() / 下載壓縮檔()
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

from llm import get_model, 估算_token  # noqa: F401  （讓 notebook 可以直接 from workshop import 估算_token）

__all__ = [
    "BASE", "準備", "範例作業", "取得作業", "記下", "印出狀態", "印出訂單紙", "印出歷程", "清除歷程",
    "模型呼叫計數器", "顯示流程圖", "存到雲端硬碟", "下載壓縮檔", "估算_token",
]

BASE = Path(__file__).resolve().parent
歷程檔 = BASE / "history.jsonl"

範例作業 = {
    "少了右括號": "print('hi'\n",
    "正確的程式": "def add(a, b):\n    return a + b\n\nprint(add(2, 3))\n",
    "空白": "",
    "變數打錯字": "def add(a, b):\n    total = a + b\n    return summ\n\nprint(add(2, 3))\n",
    "縮排亂掉": "def average(scores):\n  total = 0\n  for s in scores:\n        total += s\n  return total / len(scores)\n\nprint(average([90, 85, 77]))\n",
    "命名不一致": (
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


def 取得作業(名稱: str) -> str:
    """表單選「我的作業」時讀 /content/review-bot/我的作業.py，其他從範例裡拿。"""
    if 名稱.startswith("我的作業"):
        path = BASE / "我的作業.py"
        if not path.exists():
            raise FileNotFoundError("還沒有「我的作業」：請先執行上面寫著 %%writefile ... 我的作業.py 的那一格。")
        return path.read_text(encoding="utf-8")
    return 範例作業[名稱]


def 準備():
    """每一段的起點：把 review-bot 放進 import 路徑、重新載入改過的檔案、回傳 model。"""
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
    _讓_mcp_stdio_能在notebook用()
    return get_model()


def _讓_mcp_stdio_能在notebook用() -> None:
    """mcp 的 stdio_client 會把 MCP server 的錯誤輸出接到 sys.stderr。
    Colab（Linux）的 sys.stderr 有真的檔案代號，沒問題；Windows 的 Jupyter 沒有，就改接到 log 檔。"""
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


# ---------- State 歷程 ----------

def _可存的(obj):
    if isinstance(obj, BaseMessage):
        d = {"type": obj.type, "content": obj.text}
        if getattr(obj, "tool_calls", None):
            d["tool_calls"] = [{"name": c["name"], "args": c["args"]} for c in obj.tool_calls]
        if obj.type == "tool":
            d["name"] = getattr(obj, "name", None)
        return d
    if isinstance(obj, dict):
        return {str(k): _可存的(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_可存的(v) for v in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def 記下(標題: str, 內容) -> None:
    """把這一次的結果（通常是 State）存進 history.jsonl。"""
    row = {"時間": _dt.datetime.now().strftime("%H:%M:%S"), "標題": 標題, "內容": _可存的(內容)}
    with 歷程檔.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _短(text, n=300):
    text = str(text)
    return text if len(text) <= n else text[:n] + f"…（還有 {len(text) - n} 字）"


def 印出狀態(state: dict, 縮排: str = "  ") -> None:
    for k, v in state.items():
        if k == "messages":
            print(f"{縮排}{k}: （{len(v)} 則訊息）")
            for m in v:
                m = _可存的(m)
                if isinstance(m, dict) and m.get("tool_calls"):
                    print(f"{縮排}  [{m['type']}] 呼叫 {m['tool_calls']}")
                elif isinstance(m, dict):
                    print(f"{縮排}  [{m.get('type')}] {_短(m.get('content', ''), 200)}")
        else:
            print(f"{縮排}{k}: {_短(repr(v) if not isinstance(v, str) else repr(v), 300)}")


def 印出訂單紙(第幾步: int, state: dict, 上一步: dict | None = None, 不印: tuple = ("code",)) -> None:
    """stream_mode="values" 每一步都會給整張訂單紙；順便標出這一步新寫了哪幾格。"""
    if not 上一步:
        說明 = "起點：空白訂單紙"
    else:
        新寫入 = [k for k in state if state.get(k) != 上一步.get(k)]
        說明 = "新寫入：" + ("、".join(新寫入) if 新寫入 else "（沒有改變）")
    print(f"第 {第幾步} 步（{說明}）")
    print("  ", {k: (_短(v, 120) if isinstance(v, str) else v) for k, v in state.items() if k not in 不印})


def 印出歷程() -> None:
    if not 歷程檔.exists():
        print("還沒有任何紀錄：先跑上面幾段，再回來執行這一格。")
        return
    rows = [json.loads(line) for line in 歷程檔.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"📸 共 {len(rows)} 筆紀錄（存在 {歷程檔}）\n")
    for i, row in enumerate(rows, 1):
        print(f"===== {i}. [{row['時間']}] {row['標題']} =====")
        內容 = row["內容"]
        if isinstance(內容, dict):
            印出狀態(內容)
        elif isinstance(內容, list):
            for j, item in enumerate(內容, 1):
                print(f"  --- 第 {j} 步 ---")
                if isinstance(item, dict):
                    印出狀態(item, "    ")
                else:
                    print(f"    {_短(item)}")
        else:
            print(f"  {_短(內容, 1000)}")
        print()


def 清除歷程() -> None:
    歷程檔.unlink(missing_ok=True)


# ---------- 數模型被呼叫了幾次 ----------

class 模型呼叫計數器(BaseCallbackHandler):
    """放進 config={"callbacks": [計數器]}，每呼叫一次模型就 +1。"""

    def __init__(self):
        self.次數 = 0

    def on_chat_model_start(self, serialized, messages, **kwargs):
        self.次數 += 1

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.次數 += 1


# ---------- 畫流程圖 ----------

def 顯示流程圖(graph) -> None:
    g = graph.get_graph()
    try:
        from IPython.display import Image, display

        display(Image(g.draw_mermaid_png()))
    except Exception:
        print("（畫圖服務暫時連不上，改用文字版流程圖；可以貼到 https://mermaid.live 看圖）\n")
        print(g.draw_mermaid())


# ---------- 保存 ----------

def 存到雲端硬碟() -> None:
    from google.colab import drive

    drive.mount("/content/drive")
    目的地 = Path("/content/drive/MyDrive/langgraph-skills-workshop") / _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copytree(BASE, 目的地, ignore=shutil.ignore_patterns("__pycache__", ".llm.json"))
    print(f"✅ 已存到雲端硬碟：{目的地}")
    print("   （notebook 本身請用上方選單「檔案 → 在雲端硬碟中儲存副本」）")


def 下載壓縮檔() -> None:
    from google.colab import files

    名稱 = BASE.parent / ("review-bot-" + _dt.datetime.now().strftime("%Y%m%d-%H%M%S"))
    zip_path = shutil.make_archive(str(名稱), "zip", BASE.parent, BASE.name)
    print(f"✅ 已打包：{zip_path}")
    files.download(zip_path)
