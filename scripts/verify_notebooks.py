"""在本機從頭到尾執行 notebook，確認每一格都跑得過（不需要 Colab、不需要 API key）。

做法：
- 用 tests/mock_colab/ 的假 google.colab（假模型 fake_llm 模仿 google.colab.ai.generate_text）
- 把 notebook 裡的 /content/ 換成暫存資料夾
- 跳過套件安裝（本機環境由 uv sync 準備好）
- 可以替表單欄位換值（例如把「選做」的開關打開）

用法：
    uv run python scripts/verify_notebooks.py            # 全部
    uv run python scripts/verify_notebooks.py 1-0 2-D    # 只跑名稱開頭符合的
執行後的 notebook 存成 notebooks/<name>.executed.ipynb（已被 .gitignore 忽略），方便打開看輸出。
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

REPO = Path(__file__).resolve().parents[1]
MOCK = REPO / "tests" / "mock_colab"

# 表單欄位換值：{notebook 名稱開頭: {欄位名稱: 新的值（Python 原始碼）}}
PARAM_OVERRIDES: dict[str, dict[str, str]] = {
    "2-D": {"要跑驗證嗎": "True"},
}


def _override(src: str, overrides: dict[str, str]) -> str:
    for name, value in overrides.items():
        src = re.sub(rf"^(\s*{re.escape(name)}\s*=\s*).*?(\s*#@param.*)$", rf"\g<1>{value}\g<2>", src, flags=re.M)
    return src


def run(path: Path) -> tuple[bool, str]:
    nb = nbformat.read(path, as_version=4)
    work = Path(tempfile.mkdtemp(prefix="nbverify-"))
    content = (work / "content").as_posix()
    overrides = next((v for k, v in PARAM_OVERRIDES.items() if path.stem.startswith(k)), {})
    for cell in nb.cells:
        if cell.cell_type == "code":
            src = re.sub(r"(?<![\w.])/content(?=[/\"'\s]|$)", content, cell.source)
            cell.source = _override(src, overrides)
    # 模擬學生先按了後面的格子才跑「0. 環境設定」：Python 會先記住「這個資料夾不存在」
    # （兩種寫法的路徑都塞：Windows 上 str(Path(...)) 是反斜線，和 notebook 字面上的 / 是不同的 key）
    nb.cells.insert(0, nbformat.v4.new_code_cell(
        "import sys\nfrom pathlib import Path\n"
        f'for p in ("{content}/review-bot", str(Path("{content}/review-bot"))):\n'
        "    sys.path.insert(0, p)\n"
        "try:\n    import workshop\nexcept ImportError:\n    pass"
    ))
    (work / "content").mkdir()
    env_backup = dict(os.environ)
    os.environ.update({
        "PYTHONPATH": os.pathsep.join([str(MOCK), os.environ.get("PYTHONPATH", "")]),
        "WORKSHOP_SKIP_INSTALL": "1",
        "PYTHONIOENCODING": "utf-8",
        "WORKSHOP_FAKE_KEY_CHECK": "1",
    })
    client = NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(work / "content")}})
    t0 = time.time()
    try:
        client.execute()
        ok, msg = True, f"{time.time() - t0:.0f}s"
    except CellExecutionError as e:
        ok, msg = False, str(e)[-3000:]
    finally:
        os.environ.clear()
        os.environ.update(env_backup)
        out = path.with_name(path.stem + ".executed.ipynb")
        nbformat.write(nb, out)
        shutil.rmtree(work, ignore_errors=True)
    return ok, msg


def main(prefixes: list[str]) -> int:
    paths = [p for p in sorted((REPO / "notebooks").glob("*.ipynb")) if not p.stem.endswith(".executed")]
    if prefixes:
        paths = [p for p in paths if any(p.stem.startswith(x) for x in prefixes)]
    failed = 0
    for p in paths:
        ok, msg = run(p)
        print(f"{'✅' if ok else '❌'} {p.name}  {msg if ok else ''}")
        if not ok:
            failed += 1
            print(msg)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
