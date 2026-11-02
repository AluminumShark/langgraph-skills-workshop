"""產生 Colab notebook 的小工具：每本 notebook 的格子定義在 scripts/nbspec/*.py。

- md()        ：文字格
- code()      ：程式格（預設收合成表單，第一行必須是 #@title）
- writefile() ：%%writefile 格，內容直接讀 review-bot/ 裡的講師版原始碼，保證兩邊一模一樣
- setup()     ：每本第一格「0. 環境設定」：裝套件（uv）、選模型來源、寫出共用檔案
- ending()    ：每本最後三格：存雲端硬碟、下載 zip、印出已記錄的實驗結果
"""

from __future__ import annotations

import copy
import hashlib
import json
import textwrap
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
from nbformat.v4.rwbase import split_lines

REPO = Path(__file__).resolve().parents[1]
RB = REPO / "review-bot"
COLAB_RB = "/content/review-bot"
GITHUB = "AluminumShark/langgraph-skills-workshop"
PACKAGES = [
    "langgraph>=1.1,<2",
    "langchain>=1.2,<2",
    "langchain-google-genai>=4,<5",
    "langgraph-checkpoint-sqlite>=3,<4",
]

# 每一段 run cell 的開頭：重新連上模型；檔案準備及前置結果仍須依該段說明完成。
PREAMBLE = f'''import sys, importlib; sys.path.insert(0, "{COLAB_RB}"); importlib.invalidate_caches()
try:
    from workshop import *   # 準備、記下…（「0. 環境設定」寫好的小工具）
except ImportError:
    raise SystemExit("⚠️ 找不到環境：請先執行最上面的「0. 環境設定」那一格")
model = 準備()'''


def _clean(text: str) -> str:
    return textwrap.dedent(text).strip("\n")


def md(text: str):
    return new_markdown_cell(_clean(text))


def code(src: str, form: bool = True):
    src = _clean(src).replace("{PREAMBLE}", PREAMBLE)
    cell = new_code_cell(src)
    if form:
        assert src.startswith("#@title"), f"表單格的第一行要是 #@title：{src[:40]!r}"
        cell.metadata["cellView"] = "form"
    return cell


def writefile(rel: str, dest: str | None = None):
    content = (RB / rel).read_text(encoding="utf-8")
    cell = new_code_cell(f"%%writefile {COLAB_RB}/{dest or rel}\n{content.rstrip()}\n")
    # 手冊與學生作業要直接編輯；長篇基礎設施預設收合，避免把實驗入口推離畫面。
    if not (Path(rel).name.startswith("SKILL") or rel == "我的作業.py"):
        cell.metadata["cellView"] = "form"
        cell.metadata["jupyter"] = {"source_hidden": True}
    return cell


def colab_url(name: str) -> str:
    return f"https://colab.research.google.com/github/{GITHUB}/blob/main/notebooks/{name}.ipynb"


def badge(name: str) -> str:
    return f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({colab_url(name)})"


def _embed(rel: str) -> str:
    content = (RB / rel).read_text(encoding="utf-8")
    assert "'''" not in content and not content.endswith("\\"), rel
    return f"    {rel!r}: r'''{content}''',"


# 每本都需要的目錄（%%writefile 不會自己建資料夾）
DIRS = ["tools", "deploy", "skills/friendly-feedback", "skills/strict-review", "skills/naming-check/scripts",
        "skills/detailed-feedback/scripts"]


def setup(name: str, support: list[str] = (), extra: str = "", packages: list[str] = ()):
    """「0. 環境設定」：表單選模型來源 → uv 裝套件 → 寫出共用檔案 → 測試連線。"""
    files = ["llm.py", "workshop.py", *support]
    embedded = "\n".join(_embed(f) for f in files)
    pkgs = " ".join(f'"{p}"' for p in [*PACKAGES, *packages])
    src = f'''#@title 0. 環境設定（第一次打開、或執行階段重設後執行）
#@markdown **模型來源**：`colab` ＝ Colab 內建模型（不另填 API key；可用性與額度依帳號）；`gemini` ＝ 講師提供的 Gemini API key（備案）
模型來源 = "colab"  #@param ["colab", "gemini"]
#@markdown 選 `gemini` 時：建議在左邊 🔑「密鑰」新增 `GOOGLE_API_KEY`；也可以把 key 貼在下面（⚠️ 貼了就不要把 notebook 分享出去）
講師_API_KEY = ""  #@param {{type:"string"}}
#@markdown 進階（通常不用改）：指定模型名稱，留空用預設
colab_模型名稱 = ""  #@param {{type:"string"}}
gemini_模型名稱 = "gemini-flash-latest"  #@param {{type:"string"}}

import os, shutil, subprocess, sys
from pathlib import Path

# 1. 用 uv 安裝套件（限制相容版本範圍；時間依網路而異）
if not os.environ.get("WORKSHOP_SKIP_INSTALL"):
    print("⏳ 用 uv 安裝 LangGraph / LangChain ...")
    if shutil.which("uv") is None:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "uv"], check=True)
    subprocess.run(f'uv pip install --python "{{sys.executable}}" -q {pkgs}', shell=True, check=True)

# 2. 寫出這本 notebook 用到的共用檔案
RB = Path("{COLAB_RB}")
for d in {DIRS!r}:
    (RB / d).mkdir(parents=True, exist_ok=True)
_檔案 = {{
{embedded}
}}
for rel, content in _檔案.items():
    (RB / rel).write_text(content, encoding="utf-8")
sys.path.insert(0, str(RB))
# 剛寫好的檔案要讓 Python 重新找一次（如果之前先跑過別的格子，Python 會記得「這個資料夾不存在」）
import importlib
importlib.invalidate_caches()

# 3. 記住模型來源（不會存 API key），測試連線
import llm
llm.存設定(模型來源, colab_模型名稱.strip(), gemini_模型名稱.strip())
if 講師_API_KEY.strip():
    os.environ["GOOGLE_API_KEY"] = 講師_API_KEY.strip()
from workshop import *
model = 準備()
{_clean(extra)}
回覆 = model.invoke("用一句話跟剛學 Python 的同學打招呼").text
print(f"✅ 環境設定完成，模型來源：{{模型來源}}")
print(f"🤖 模型說：{{回覆.strip()}}")'''
    cell = new_code_cell(src)
    cell.metadata["cellView"] = "form"
    return cell


def project_intro(這本: str):
    """每本都一樣的「小專案」說明，讓只看 notebook、沒看簡報的人也知道在做什麼。
    這本：一句話說明「這本 notebook 做的是小助教的哪一塊」。"""
    return md(f"""
    ## 🎯 這兩堂課的小專案：作業小助教

    **作業小助教**是一個協助檢查 Python 作業的小程式。你交給它一段作業，它回覆檢查結果。
    在 workflow 版本中，語法有錯會先回覆錯誤；語法通過才請 AI 產生含**「優點：」與「改進：」**的回饋。
    格式檢查若一直不通過，流程會在達到生成次數上限時停止，並標示未通過，不能把「停止」當成「合格」。

    **先分清三件事：**語法正確（Python 看得懂）≠ 執行成功（跑的時候沒出錯）≠ 答案正確（符合題目要求）。

    選它當練習，是因為它剛好三種東西都用得到：

    | 小助教需要的 | 例子 | 我們用什麼做 |
    | --- | --- | --- |
    | 由流程控制的步驟 | 先檢查語法；有錯就回報，通過才產生回饋並檢查格式 | 用程式定義**流程**（LangGraph，第 1 堂） |
    | 需要判斷的事 | 回饋怎麼寫、要不要真的執行程式看看 | 交給 **AI**（agent，第 1 堂） |
    | 做法和規矩 | 回饋的語氣要溫和還是嚴格、好的變數名稱長什麼樣 | 寫成給 AI 看的**手冊**（Skill，第 2 堂） |

    👉 **這本 notebook 做的是：**{這本}

    <details><summary>想查零件名稱時再展開（不用先背）</summary>

    | 零件 | 白話說它在做什麼 |
    | --- | --- |
    | `check_syntax`（檢查語法） | 只看程式的「文法」對不對，例如括號有沒有關好、冒號有沒有漏；**不會執行程式** |
    | `explain_error`（解釋錯誤） | 語法錯的時候，用一句話告訴學生錯在第幾行 |
    | `give_feedback`（寫回饋） | 在 1-A 接上模型後，請 AI 寫出「優點＋改進」回饋；是否符合格式由下一站檢查 |
    | `check_format`（檢查格式） | 檢查兩個標記的順序、內容是否非空與總字數；不驗證回饋內容是否正確 |
    | 工具：`run_code`、`check_indent`、`read_spec`、`check_naming` | 真的執行作業、檢查縮排、讀題目要求、檢查變數名稱 |
    | 手冊：`friendly-feedback`、`strict-review` | 告訴 AI 回饋要溫和鼓勵，還是嚴格審查 |

    </details>

    **操作提醒：**先執行「0. 環境設定」，再照本段的準備格 → 預測 → 執行 → 對照操作。
    `%%writefile` 表示「把這格內容存成檔案」；修改後要執行才會生效。重跑準備格可能覆寫手冊，先存好自己的修改。
    """)


def my_homework():
    """（選用）讓學生貼自己的作業：表單選「我的作業」時會讀這個檔案。"""
    return [
        md("""
        ### ✏️（選用）放進你自己的作業

        課後作業要把**你自己寫過的一段作業**丟進來跑。把下面那格的程式換成你的作業、執行它，
        之後在表單的「作業」選 **我的作業** 就會用它。課堂上可以先跳過這格。
        """),
        writefile("我的作業.py"),
    ]


def ending():
    return [
        md("""
        ## 收尾：存檔與交作業

        - 💾 **存到雲端硬碟**：把 `/content/review-bot/`（你改過的手冊、程式、State 紀錄）存一份到自己的 Google 雲端硬碟。
        - ⬇️ **下載 zip**：直接下載到電腦。
        - 📸 **最後一格**：印出實驗格存下的結果。挑選相關紀錄截圖，再依作業要求補上觀察與理由。

        這些是實驗格透過 `記下()` 保存的結果，並非每次執行的所有中間狀態。
        同一執行環境的紀錄會累積，可能包含其他 notebook 的實驗；請按輸出標題辨認。

        瀏覽器暫時斷線不一定會清掉檔案；執行階段被刪除或回收時，`/content/` 的檔案才會失去。
        想保留手冊、程式和 checkpoint，請先備份。notebook 本身則用上方選單「檔案 → 在雲端硬碟中儲存副本」，兩種存檔用途不同。
        回來操作時先確認執行階段仍在；若已重設，重跑「0. 環境設定」及本段準備格，再依需要還原自己備份的檔案。
        """),
        code("""
        #@title 💾 存到 Google 雲端硬碟（會跳出授權視窗）
        {PREAMBLE}
        存到雲端硬碟()
        """),
        code("""
        #@title ⬇️ 下載 zip
        {PREAMBLE}
        下載壓縮檔()
        """),
        code("""
        #@title 📸 印出已記錄的實驗結果（選取相關紀錄交作業）
        {PREAMBLE}
        印出歷程()
        """),
    ]


def _key(cell) -> str:
    """程式格的「身分」：第一行（#@title 或 %%writefile 那一行）。"""
    return cell.source.splitlines()[0] if cell.source else ""


def _keep_outputs(new_cells: list, old_path: Path) -> int:
    """只沿用程式內容完全相同的輸出；重排不靠位置配對，改過的程式清空輸出。"""
    if not old_path.exists():
        return 0
    old_code = [c for c in nbformat.read(old_path, as_version=4).cells if c.cell_type == "code"]
    new_code = [c for c in new_cells if c.cell_type == "code"]
    by_source = {}
    for cell in old_code:
        by_source.setdefault(cell.source, []).append(cell)
    pairs = []
    for cell in new_code:
        matches = by_source.get(cell.source, [])
        if matches:
            pairs.append((cell, matches.pop(0)))
    kept = 0
    for new, old in pairs:
        new.id = old.get("id", new.id)
        if old.metadata.get("id"):
            new.metadata["id"] = old.metadata["id"]
        if old.get("outputs"):
            new.outputs = old.outputs
            new.execution_count = old.get("execution_count")
            for k in ("id", "outputId", "colab"):
                if k in old.metadata:
                    new.metadata[k] = old.metadata[k]
            kept += 1
    return kept


def build(name: str, cells: list) -> Path:
    out = REPO / "notebooks" / f"{name}.ipynb"
    nb = new_notebook(cells=cells)
    nb.metadata = {
        "colab": {"provenance": [], "toc_visible": True, "name": f"{name}.ipynb"},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    }
    _keep_outputs(nb.cells, out)
    _stable_ids(nb.cells, out)
    nbformat.validate(nb)
    # 和 Colab 存檔的格式一樣（縮排 2 格、metadata 裡也有 id），兩邊互相存檔時 diff 才會小
    out.write_text(_colab_json(nb), encoding="utf-8", newline="\n")
    return out


def _colab_json(nb) -> str:
    """照 Colab 存檔的樣子輸出：縮排 2 格、cell 欄位照字母排、metadata 和輸出保留原本順序、結尾不換行。
    （nbformat.writes 一定用縮排 1 格，所以自己輸出。）"""
    nb = split_lines(copy.deepcopy(nb))
    cells = [{k: cell[k] for k in sorted(cell)} for cell in nb["cells"]]
    meta = {k: ({kk: v[kk] for kk in sorted(v)} if isinstance(v, dict) else v) for k, v in sorted(nb["metadata"].items())}
    data = {"cells": cells, "metadata": meta, "nbformat": nb["nbformat"], "nbformat_minor": nb["nbformat_minor"]}
    return json.dumps(data, indent=2, ensure_ascii=False)


def _stable_ids(cells: list, old_path: Path) -> None:
    """文字格沿用舊檔裡同內容那一格的 id；新的格子用內容算出固定的 id（每次產生都一樣）。"""
    old_ids = {}
    if old_path.exists():
        for c in nbformat.read(old_path, as_version=4).cells:
            if c.cell_type == "markdown":
                old_ids.setdefault(c.source, c.get("id"))
    used = set()
    for i, c in enumerate(cells):
        if c.cell_type == "markdown" and old_ids.get(c.source) and old_ids[c.source] not in used:
            c.id = old_ids[c.source]
        elif c.cell_type == "markdown" or "outputId" not in c.metadata:
            if not (c.cell_type == "code" and c.metadata.get("id")):
                c.id = hashlib.sha1(f"{i}:{c.source}".encode("utf-8")).hexdigest()[:8]
        if c.id in used:
            c.id = hashlib.sha1(f"{i}:{c.id}".encode("utf-8")).hexdigest()[:8]
        used.add(c.id)
        c.metadata["id"] = c.id
