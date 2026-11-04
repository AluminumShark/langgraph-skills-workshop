"""Run each notebook from top to bottom on your own machine to confirm every cell runs (no Colab, no API key needed).

How it works:
- Uses the fake google.colab in tests/mock_colab/ (the fake model fake_llm imitates google.colab.ai.generate_text)
- Replaces /content/ in the notebook with a temporary folder
- Skips package installation (the local environment is prepared by uv sync)
- Can swap values of form fields (for example, turn on an "optional" switch)

Usage:
    uv run python en/scripts/verify_notebooks.py            # everything
    uv run python en/scripts/verify_notebooks.py 1-0 2-D    # only the notebooks whose name starts with one of these
The executed notebook is saved as notebooks/<name>.executed.ipynb (ignored by .gitignore) so you can open it and look at the output.
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

# Swap form field values: {notebook name prefix: {field name: new value (Python source)}}
PARAM_OVERRIDES: dict[str, dict[str, str]] = {
    "2-D": {"run_verification": "True"},
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
    # Simulate a student who pressed a later cell before running "0. Setup": Python first remembers "this folder does not exist"
    # (we stuff in both spellings: on Windows str(Path(...)) uses backslashes, which is a different key from the / in the notebook text)
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
