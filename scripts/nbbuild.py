"""產生 Colab notebook 的小工具：每本 notebook 的格子定義在 scripts/nbspec/*.py。

- md()        ：文字格
- code()      ：程式格（預設收合成表單，第一行必須是 #@title）
- writefile() ：%%writefile 格，內容直接讀 review-bot/ 裡的講師版原始碼，保證兩邊一模一樣
- setup()     ：每本第一格「0. 環境設定」：裝套件（uv）、選模型來源、寫出共用檔案
- ending()    ：每本最後三格：存雲端硬碟、下載 zip、印出整份 State 歷程
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

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

# 每一段 run cell 的開頭：重新連上模型（斷線、跑錯都能從這裡重來）
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
    return new_code_cell(f"%%writefile {COLAB_RB}/{dest or rel}\n{content.rstrip()}\n")


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
    src = f'''#@title 0. 環境設定（第一次打開、或斷線後，先執行這一格）
#@markdown **模型來源**：`colab` ＝ Colab 內建模型（免費、不用 API key）；`gemini` ＝ 講師提供的 Gemini API key（備案）
模型來源 = "colab"  #@param ["colab", "gemini"]
#@markdown 選 `gemini` 時：建議在左邊 🔑「密鑰」新增 `GOOGLE_API_KEY`；也可以把 key 貼在下面（⚠️ 貼了就不要把 notebook 分享出去）
講師_API_KEY = ""  #@param {{type:"string"}}
#@markdown 進階（通常不用改）：指定模型名稱，留空用預設
colab_模型名稱 = ""  #@param {{type:"string"}}
gemini_模型名稱 = "gemini-flash-latest"  #@param {{type:"string"}}

import os, shutil, subprocess, sys
from pathlib import Path

# 1. 用 uv 安裝套件（版本釘死，大約 10–30 秒）
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
        - 📸 **最後一格**：印出這本 notebook 跑過的所有 State，截圖就能交作業。

        Colab 斷線後 `/content/` 裡的檔案會消失，想留下來就先存。notebook 本身請用上方選單「檔案 → 在雲端硬碟中儲存副本」。
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
        #@title 📸 印出整份 State 歷程（截圖交作業）
        {PREAMBLE}
        印出歷程()
        """),
    ]


def build(name: str, cells: list) -> Path:
    nb = new_notebook(cells=cells)
    nb.metadata = {
        "colab": {"provenance": [], "toc_visible": True, "name": f"{name}.ipynb"},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    }
    out = REPO / "notebooks" / f"{name}.ipynb"
    nbformat.validate(nb)
    nbformat.write(nb, out)
    return out
