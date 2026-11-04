"""Helpers that generate the Colab notebooks. Each notebook's cells are defined in scripts/nbspec/*.py.

- md()        : text cell
- code()      : code cell (collapsed into a form by default; the first line must be #@title)
- writefile() : %%writefile cell; its content is read straight from the instructor source in review-bot/, so the two are always identical
- setup()     : the first cell of every notebook, "0. Setup": install packages (uv), pick the model source, write the shared files
- ending()    : the last three cells of every notebook: save to Google Drive, download a zip, print the recorded experiment results
"""

from __future__ import annotations

import copy
import hashlib
import json
import textwrap
from collections import Counter
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

# Start of every run cell: reconnect to the model. Files and earlier results still have to be prepared as that part describes.
PREAMBLE = f'''import sys, importlib; sys.path.insert(0, "{COLAB_RB}"); importlib.invalidate_caches()
try:
    from workshop import *   # prepare, record, ... (the helpers written by "0. Setup")
except ImportError:
    raise SystemExit("⚠️ Environment not found: run the 0. Setup cell at the very top first")
model = prepare()'''


def _clean(text: str) -> str:
    return textwrap.dedent(text).strip("\n")


def md(text: str):
    return new_markdown_cell(_clean(text))


def code(src: str, form: bool = True):
    src = _clean(src).replace("{PREAMBLE}", PREAMBLE)
    cell = new_code_cell(src)
    if form:
        assert src.startswith("#@title"), f"The first line of a form cell must be #@title: {src[:40]!r}"
        cell.metadata["cellView"] = "form"
    return cell


def writefile(rel: str, dest: str | None = None):
    content = (RB / rel).read_text(encoding="utf-8")
    cell = new_code_cell(f"%%writefile {COLAB_RB}/{dest or rel}\n{content.rstrip()}\n")
    # Handbooks and student homework are meant to be edited directly; long infrastructure code is collapsed by default so it does not push the experiment entry points off screen.
    if not (Path(rel).name.startswith("SKILL") or rel == "my_homework.py"):
        cell.metadata["cellView"] = "form"
        cell.metadata["jupyter"] = {"source_hidden": True}
    return cell


def colab_url(name: str) -> str:
    return f"https://colab.research.google.com/github/{GITHUB}/blob/main/en/notebooks/{name}.ipynb"


def badge(name: str) -> str:
    return f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({colab_url(name)})"


def _embed(rel: str) -> str:
    content = (RB / rel).read_text(encoding="utf-8")
    assert "'''" not in content and not content.endswith("\\"), rel
    return f"    {rel!r}: r'''{content}''',"


# Folders every notebook needs (%%writefile does not create folders by itself)
DIRS = ["tools", "deploy", "skills/friendly-feedback", "skills/strict-review", "skills/naming-check/scripts",
        "skills/detailed-feedback/scripts"]


def setup(name: str, support: list[str] = (), extra: str = "", packages: list[str] = ()):
    """"0. Setup": pick the model source in a form -> install packages with uv -> write the shared files -> test the connection."""
    files = ["llm.py", "workshop.py", *support]
    embedded = "\n".join(_embed(f) for f in files)
    pkgs = " ".join(f'"{p}"' for p in [*PACKAGES, *packages])
    src = f'''#@title 0. Setup (run it the first time you open this notebook, or after the runtime is reset)
#@markdown **Model source**: `colab` = the model built into Colab (no API key needed; availability and quota depend on your account); `gemini` = the instructor's Gemini API key (the backup option)
model_source = "colab"  #@param ["colab", "gemini"]
#@markdown If you pick `gemini`: we recommend adding `GOOGLE_API_KEY` under 🔑 "Secrets" in the left sidebar. You can also paste the key below (⚠️ if you paste it, do not share this notebook)
INSTRUCTOR_API_KEY = ""  #@param {{type:"string"}}
#@markdown Advanced (you usually don't need to change these): set a model name, or leave it empty to use the default
colab_model_name = ""  #@param {{type:"string"}}
gemini_model_name = "gemini-flash-latest"  #@param {{type:"string"}}

import os, shutil, subprocess, sys
from pathlib import Path

# 1. Install packages with uv (limited to compatible version ranges; time depends on your network)
if not os.environ.get("WORKSHOP_SKIP_INSTALL"):
    print("⏳ Installing LangGraph / LangChain with uv ...")
    if shutil.which("uv") is None:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "uv"], check=True)
    subprocess.run(f'uv pip install --python "{{sys.executable}}" -q {pkgs}', shell=True, check=True)

# 2. Write the shared files this notebook uses
RB = Path("{COLAB_RB}")
for d in {DIRS!r}:
    (RB / d).mkdir(parents=True, exist_ok=True)
_files = {{
{embedded}
}}
for rel, content in _files.items():
    (RB / rel).write_text(content, encoding="utf-8")
sys.path.insert(0, str(RB))
# Make Python look again for the files we just wrote (if another cell ran first, Python remembers "this folder does not exist")
import importlib
importlib.invalidate_caches()

# 3. Remember the model source (the API key is not saved) and test the connection
import llm
llm.save_settings(model_source, colab_model_name.strip(), gemini_model_name.strip())
if INSTRUCTOR_API_KEY.strip():
    os.environ["GOOGLE_API_KEY"] = INSTRUCTOR_API_KEY.strip()
from workshop import *
model = prepare()
{_clean(extra)}
reply = model.invoke("Say hello in one sentence to a classmate who just learned Python").text
print(f"✅ Setup complete. Model source: {{model_source}}")
print(f"🤖 The model says: {{reply.strip()}}")'''
    cell = new_code_cell(src)
    cell.metadata["cellView"] = "form"
    return cell


def project_intro(this_notebook: str):
    """The same "mini project" intro in every notebook, so someone who only reads the notebook (not the slides) still knows what we are building.
    this_notebook: one sentence saying which part of the Homework Helper this notebook covers."""
    return md(f"""
    ## 🎯 The mini project for these two sessions: the Homework Helper

    The **Homework Helper** is a small program that helps check Python homework. You give it a piece of homework, and it replies with the review result.
    In the workflow version (1-A, workflow), a syntax error gets an error reply first; only code with valid syntax goes on to the AI, which writes feedback containing **"Strengths:" and "Improvements:"**.
    If the format check keeps failing, the flow stops when it reaches the maximum number of generations and marks the result as not passed. "Stopped" must never be read as "passed".

    **Keep three things apart:** valid syntax (Python can read it) ≠ runs successfully (no error while running) ≠ meets the assignment (matches what the assignment asks for).

    We chose it because it happens to use all three kinds of things (and you can also combine them):

    | What the helper needs | Example | What we use |
    | --- | --- | --- |
    | Steps controlled by a flow | Check syntax first; report errors; only on a pass, write feedback and check its format | A **workflow** defined in code (LangGraph, Session 1) |
    | Things that need judgment | How to word the feedback, whether to actually run the code and see | Leave it to the **AI** (agent, Session 1) |
    | Ways of working and rules | Should the feedback be gentle or strict, what a good variable name looks like | A **handbook** written for the AI to read (Skill, Session 2). Rules that code can check (such as variable naming) can also come with a script or go into the workflow; 2-B compares them |

    👉 **This notebook covers:** {this_notebook}

    <details><summary>Open this when you need to look up a component name (no need to memorize it)</summary>

    | Component | What it does, in plain words |
    | --- | --- |
    | `check_syntax` (check syntax) | Only checks whether the code's "grammar" is right, for example whether brackets are closed or a colon is missing. It **does not run the code** |
    | `explain_error` (explain the error) | When the syntax is wrong, tells the student in one sentence which line is wrong |
    | `give_feedback` (write feedback) | Once a model is connected in 1-A, asks the AI to write "Strengths + Improvements" feedback; the next station checks whether it matches the format |
    | `check_format` (check format) | Checks the order of the two markers, that each part is non-empty, and the total character count. It does not verify that the feedback content is correct |
    | Tools: `run_code`, `check_indent`, `read_spec` (from 1-B on); `check_naming` (from 2-B on) | Run the homework under teaching limits, check indentation, read the assignment requirements, check variable names |
    | Handbooks: `friendly-feedback`, `strict-review`; `naming-check` (2-B), `detailed-feedback` (the 2-C security experiment) | Tell the AI whether feedback should be gentle and encouraging or strict; the naming-check handbook comes with a script; the last one hides a suspicious instruction so you can practice checking an outside handbook |

    </details>

    **Reminder:** run "0. Setup" first, then follow each part: setup cell → predict → run → compare.
    `%%writefile` means "save this cell's content as a file"; edits only take effect after you run the cell. Re-running a setup cell may overwrite the handbooks, so save your own edits first.
    """)


def my_homework():
    """(Optional) Let students paste their own homework: the form reads this file when "My homework" is selected."""
    return [
        md("""
        ### ✏️ (Optional) Bring in your own homework

        The take-home assignment asks you to run **a piece of homework you wrote yourself**. Replace the code in the cell below with your homework and run it.
        After that, choose **My homework** in the form's "homework" field and the helper will use it. You can skip this cell in class.
        `run_code` does not allow `input()` or `open()`, and only a few standard modules can be imported. If your homework uses `input()`, change it to a fixed value first (for example `n = 5`).
        """),
        writefile("my_homework.py"),
    ]


def ending():
    return [
        md("""
        ## Wrap-up: save your work and hand it in

        - 💾 **Save to Google Drive**: save a copy of `/content/review-bot/` (your edited handbooks, code, and State records) to your own Google Drive.
        - ⬇️ **Download the zip**: download it straight to your computer.
        - 📸 **The last cell**: prints the results the experiment cells saved. Pick the relevant records for a screenshot, then add your observations and reasons as the assignment asks.

        These are the results the experiment cells saved through `record()`, not every intermediate state of every run.
        Records in the same runtime pile up, so they may include experiments from other notebooks; use the printed titles to tell them apart.

        A temporary browser disconnect does not necessarily wipe your files; files under `/content/` are lost only when the runtime is deleted or recycled.
        To keep your handbooks, code, and checkpoint, back them up first. The notebook itself is saved with the menu "File → Save a copy in Drive". The two kinds of saving do different jobs.
        When you come back, first check that the runtime is still there. If it was reset, re-run "0. Setup" and this part's setup cell, then restore the files you backed up as needed.
        """),
        code("""
        #@title 💾 Save to Google Drive (an authorization window will pop up)
        {PREAMBLE}
        save_to_drive()
        """),
        code("""
        #@title ⬇️ Download the zip
        {PREAMBLE}
        download_zip()
        """),
        code("""
        #@title 📸 Print the recorded experiment results (pick the relevant records to hand in)
        {PREAMBLE}
        print_history()
        """),
    ]


def _key(cell) -> str:
    """A code cell's "identity": its first line (the #@title or %%writefile line)."""
    return cell.source.splitlines()[0] if cell.source else ""


def _keep_outputs(new_cells: list, old_path: Path) -> int:
    """Reuse outputs only for cells whose source is exactly the same; reordering does not match by position, and edited code loses its output."""
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


def _archive_replaced_outputs(new_cells: list, old_path: Path) -> Path | None:
    """Edited code does not keep its old result; before overwriting, save a full snapshot of the original code and outputs."""
    if not old_path.exists():
        return None
    raw = old_path.read_bytes()
    old = nbformat.reads(raw.decode("utf-8"), as_version=4)
    remaining = Counter(c.source for c in new_cells if c.cell_type == "code")
    replaced = 0
    for cell in old.cells:
        if cell.cell_type != "code":
            continue
        if remaining[cell.source]:
            remaining[cell.source] -= 1
        elif cell.get("outputs"):
            replaced += 1
    if not replaced:
        return None
    digest = hashlib.sha256(raw).hexdigest()
    archive = old_path.parent / "output-history" / old_path.stem / f"{digest}.ipynb"
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        if archive.read_bytes() != raw:
            raise RuntimeError(f"Snapshot content does not match; stopping before overwrite: {archive}")
    else:
        archive.write_bytes(raw)
    print(f"⚠️ {old_path.name}: {replaced} cells have old outputs that no longer fit the new code; full snapshot saved to {archive}")
    return archive


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
    _archive_replaced_outputs(nb.cells, out)
    # Same format as a Colab save (2-space indent, an id in the metadata too), so diffs stay small when the two sides save back and forth
    out.write_text(_colab_json(nb), encoding="utf-8", newline="\n")
    return out


def _colab_json(nb) -> str:
    """Write JSON the way Colab saves it: 2-space indent, cell keys sorted alphabetically, metadata and outputs in their original order, no trailing newline.
    (nbformat.writes always indents by 1 space, so we write it ourselves.)"""
    nb = split_lines(copy.deepcopy(nb))
    cells = [{k: cell[k] for k in sorted(cell)} for cell in nb["cells"]]
    meta = {k: ({kk: v[kk] for kk in sorted(v)} if isinstance(v, dict) else v) for k, v in sorted(nb["metadata"].items())}
    data = {"cells": cells, "metadata": meta, "nbformat": nb["nbformat"], "nbformat_minor": nb["nbformat_minor"]}
    return json.dumps(data, indent=2, ensure_ascii=False)


def _stable_ids(cells: list, old_path: Path) -> None:
    """Markdown cells reuse the id of the old cell with the same content; new cells get a fixed id computed from their content (the same on every build)."""
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
