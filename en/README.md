> This is the English edition. The original is in Traditional Chinese: [中文版](../README.md).

# From LangGraph to Skills: A Two-in-One Guide to Structured and Unstructured Agents

> Agents in 2026: Mastering LangGraph & SKILL.md

These are the materials for an **NTU AI Club** technical workshop. The speakers are Levi Lee ([@AluminumShark](https://github.com/AluminumShark)) and Yu-Chi Ko.
The course is for **beginners who have just learned Python**: if you can read a dict, a function, an `if` and a `while`, you can follow along.
You don't write code yourself. You run notebooks the instructors prepared, all in Google Colab,
and you mainly do three things: **predict first, press run, compare with the result**. When something needs changing, you only change a form or the text of a specific handbook.

Together we build the "**Homework Helper**". The workflow version first checks the syntax of a Python homework: if there is an error, it reports it; if the syntax passes, it asks the AI for "Strengths / Improvements" feedback and checks its format.
Passing the syntax check does not mean the code runs successfully, and it does not mean the code meets the assignment. Stopping because the helper reached its generation limit does not mean the feedback passed either.
Session 1 explains what an AI agent is, and uses LangGraph to show the difference between "the program decides the route" and "the AI decides the route" with your own eyes.
Session 2 teaches Agent Skills (handbooks for the AI). At the end we connect the two and build a Homework Helper that combines a fixed workflow with an agent.

| Session | Date | Length | Topic |
| --- | --- | --- | --- |
| Session 1 | 2026-11-09 (Mon) | 120 minutes | What is an agent? Build one with LangGraph |
| Session 2 | 2026-11-16 (Mon) | 120 minutes | Agent Skills: what to write as a handbook, what to write as a script, and finally what goes where |

## Notebooks at a glance

Click **Open in Colab** in the table to open a notebook right in your browser. You don't need to install anything on your computer.

| Session / start time | Notebook | What you will learn | What you change | Slides |
| --- | --- | --- | --- | --- |
| Session 1 0:10 | **1-0 Tool calling**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/en/notebooks/1-0_tool_calling.ipynb) | The model only "says" which tool it wants; your program does the real work | Read the model's reply, the tool request, and how the result is handed back | Session 1, 5–15; optional reading 45 |
| Session 1 0:35 | **1-A Workflow**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/en/notebooks/1-A_workflow.ipynb) | Follow the branches with State, Node and Edge, and tell why the flow stopped | Homework, maximum generations, feedback character limit | Session 1, 16–28; optional reading 46 |
| Session 1 1:10 | **1-B Agent**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/en/notebooks/1-B_agent.ipynb) | Try the tools first, then build the agent; the instructor demonstrates MCP | Homework, one sentence in the system prompt | Session 1, 30–39; optional reading 47 |
| Session 2 0:08 | **2-A Skills**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/en/notebooks/2-A_skills.ipynb) | Observe separately: changing the request to pick a handbook, editing the body, editing the card | A specific SKILL.md rule and its description | Session 2, 5–12; C: optional reading 42 |
| Session 2 0:28 | **2-B Code · Text · Scripts**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/en/notebooks/2-B_code_text_script.ipynb) | Compare one rule as text, as a script the agent chooses, and as a check the workflow runs directly | No code changes; predict first, then compare with the actual results | Session 2, 13–19 |
| Session 2 0:58 | **2-C Security**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/en/notebooks/2-C_security.ipynb) | Compare the same handbook with and without a tool permission; find the malicious lines | No code changes; record what the tools and the fake data produce | Session 2, 21–24 |
| Session 2 1:08 | **2-D Combining workflow and agent**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/en/notebooks/2-D_dual_core.ipynb) | Connect the workflow with the handbooks; tell apart three checkpoint states | thread_id; compare resuming, retrieving a finished result, and a new run | Session 2, 25–28; optional reading 43–44 |
| Optional after class | **2-E Getting ready for the cloud**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/en/notebooks/2-E_deploy.ipynb) | Run one submission first, then batching, division of labor, an API, and pre-deployment checks | Follow the prerequisites of each part | Session 2, 47–55 (supplementary) |

> If time runs short, students can watch the instructor demo 2-B and then answer from its records. Still keep the tool-permission comparison in 2-C and the three checkpoint states in 2-D. 2-E, repeated evals, RAG and deployment are optional after class.

## First time using Colab? Follow these steps

1. **Open a notebook**: click **Open in Colab** in the table above. You need to sign in with a Google account (a free account is fine).
2. **Save your own copy**: in the menu at the top left, click "**File → Save a copy in Drive**". From then on, work in your own copy. If you break something, don't worry: the original is always there.
3. **Run "0. Environment setup"**: the first code cell of every notebook is called "0. Environment setup". Move your mouse over it and click the ▶ on its left.
   The first time, it uses [uv](https://docs.astral.sh/uv/) to install LangGraph and other packages. How long it takes depends on your network and the runtime.
   When you see "✅ Environment setup complete" and a greeting from the model, it worked.
4. **Use the same rhythm for every part**:
   - 🤔 **Predict**: read the prediction question above the code cell first, and write your answer on paper
   - ▶ **Run**: run that part's code cell
   - 👀 **Compare**: read "What did you see?" below it, and compare it with your prediction
5. **Change form fields**: some code cells show a form on the right, for example:

   ```
   homework:          [ Missing parenthesis   ▼ ]
   max_generations:   ──●──────── 3 (including the first)
   ```

   Pick from a dropdown, drag a slider or edit the text, then press ▶ to run it again. When you compare experiments, change only one thing at a time.
6. **The code is collapsed**: most cells only show a title and the output. If you want to see the code, click "Show code" on the cell. It's fine if you don't understand it; in this course you only need to read the output.
   Some cells say `%%writefile`, which means "save this cell's content as a file", for example a SKILL.md handbook. When you are asked to change it, edit the text directly and then run that cell.
7. **The last three cells: saving and handing in**
   - 💾 Save to Google Drive: save a copy of the files you changed and your run records
   - ⬇️ Download zip: download straight to your computer
   - 📸 Print the recorded experiment results: pick the relevant records by their titles and take screenshots, then add the observations and reasons the homework asks for

## Where does the model come from?

- **Default: Colab's built-in model (`google.colab.ai`)**. This mode needs no separate API key. Availability and quota depend on your account, so run the environment setup first to check.
- **Backup: a Gemini API key from the instructor**. If the built-in model runs out of quota, or the instructor asks you to switch in class:
  1. Click the 🔑 "**Secrets**" icon on the left side of Colab. Add a secret named `GOOGLE_API_KEY`, paste the key the instructor gave you as its value, and turn on "Notebook access"
  2. In the form of "0. Environment setup", change **`model_source`** to `gemini`, and run that cell again

> ⚠️ The form also has a field where you can paste the key directly, but **never share a notebook with a pasted key** (anyone who sees the notebook sees the key). Use 🔑 Secrets whenever you can.

## FAQ

**Colab disconnected, or a cell raised an error. What now?**
First check whether the runtime still exists. A temporary browser disconnect does not necessarily clear your files; you only need to rebuild the environment when the runtime has been recycled or deleted.
Rerun the setup cells as described in that part's prerequisites. If the part depends on earlier results or a checkpoint, finish or restore those first.
If you see "⚠️ Environment not found", run "0. Environment setup" and that part's file setup cell first. A setup cell may overwrite the handbooks, so back up your own changes first.

**The quota ran out, or the model keeps not responding?**
Colab's built-in model has a free usage limit. You can wait a bit and try again, share one notebook between two people, or switch to the instructor's Gemini key as described in "Where does the model come from?" above.

**I ran the same cell twice and got different results. Did I break it?**
The feedback text and the tool order may differ, or they may be the same; both are valid observations. Record what actually happened; you don't need to rerun until you get a difference. What we discuss in class is which things the program guarantees and which choices are left to the AI.

**Why does `run_code` block `import os`?**
`run_code` runs the homework, so the example adds module restrictions and a 3-second timeout, and shortens the error output. These are limits for a classroom demo; they are not a complete security sandbox. Only use the course examples or homework you trust.

**I changed SKILL.md, but the AI's feedback didn't change?**
After editing, remember to **run that cell** (the `%%writefile` cell) so the file is actually saved; then run the experiment that uses it. 2-A observes three things separately: "changing only the request affects which handbook is picked", "keeping the handbook fixed and editing the body", and "keeping the request fixed and editing the description". Each experiment changes only one thing at a time.

**I can't see the forms, only a lot of code?**
You probably opened the notebook directly on GitHub or in Jupyter. Open it with **Open in Colab** from the table; forms and collapsed code only appear in Colab.

## Slides

| File | Content |
| --- | --- |
| [`slides/session1.html`](slides/session1.html) | Session 1: What is an agent? Build one with LangGraph |
| [`slides/session2.html`](slides/session2.html) | Session 2: Agent Skills, what to write as instructions and what to write as a script (with a supplementary "moving to the cloud" part at the end) |

Download a file and open it in your browser (one HTML file, nothing to install): **← →** to change slides, **N** for speaker notes, **F** for full screen, **Ctrl / ⌘ + P** to export a PDF.
Every part of every notebook is marked "📍 Slides: slide N", so you can follow along in class.

## Project structure

```
en/                             # English edition; mirrors the repo root
├── notebooks/                  # eight Colab notebooks (generated by scripts/)
├── slides/                     # HTML slides for both sessions
├── docs/                       # syllabus, slide-by-slide outlines, reusable material from the old workshop, original proposal
├── review-bot/                 # instructor source code for the sample project, the Homework Helper
│   ├── graph.py                #   1-A: workflow (State, Node, Edge)
│   ├── agent.py                #   1-B: the agent, built with create_agent
│   ├── skill_loader.py         #   2-A: read the handbooks' cards and pick one
│   ├── dual_core.py            #   2-D: outer workflow + inner agent + Skill
│   ├── tools/                  #   tools: run_code, check_indent, read_spec, check_naming
│   ├── skills/                 #   handbooks: friendly-feedback, strict-review, naming-check, detailed-feedback
│   ├── deploy/                 #   2-E: the "homework repo" MCP server, multi-agent flow, API service, pre-launch checks
│   ├── langgraph.json, Dockerfile, requirements.txt  # 2-E: deployment files for the cloud (generated only, not deployed)
│   ├── llm.py                  #   for the workshop: wraps Colab's built-in model or Gemini as one model
│   └── workshop.py             #   for the workshop: small shared helpers for the notebooks (records, flow diagrams, saving)
├── scripts/
│   ├── nbspec/                 # the content of each notebook (edit here to change a notebook)
│   ├── build_notebooks.py      # generates notebooks/*.ipynb from nbspec/ + review-bot/
│   └── verify_notebooks.py     # runs every notebook from start to finish on your machine
├── tests/mock_colab/           # fake google.colab and fake model for local verification
├── reference/old-workshop/     # the previous version of the workshop, for reference only
├── GLOSSARY.md                 # translation glossary: names and strings shared across files
└── CLAUDE.md                   # project notes and working rules for AI coding assistants
../pyproject.toml / ../uv.lock  # local environment (managed by uv), shared with the Chinese edition at the repo root
```

**What is `/content/review-bot/`?** When you run a notebook in Colab, the program writes the Homework Helper's files to the `/content/review-bot/` folder on Colab's cloud machine (you can see it in the 📁 Files panel on the left).
Its initial content comes from `en/review-bot/` in this repo; after you run experiments, it may contain your edited handbooks and records. When the runtime is deleted or recycled, this folder is not kept, so back it up with "Save to Google Drive" or "Download zip" at the end. Saving a copy of the notebook is not the same as backing up these files.

## For instructors / anyone who wants to change the materials

The local environment is managed with [uv](https://docs.astral.sh/uv/) (Python 3.12; on Colab, the runtime decides the versions). From the repo root, first install the dependencies:

```bash
uv sync
```

**The notebooks are generated. Don't edit the `.ipynb` files directly.** Their content comes from two places: each notebook's cells are defined in `en/scripts/nbspec/*.py`, and the `%%writefile` cells read the source code in `en/review-bot/` directly (so the files a notebook writes are guaranteed to match the ones in the repo). After editing, regenerate them:

```bash
uv run python en/scripts/build_notebooks.py
```

To generate only some notebooks, add the start of their names (for example `1-A 2-B`).

**Only cells whose code source is exactly the same keep their old outputs**; when cells are reordered, they are matched by content. When you change or delete a code cell, the generator first backs up the whole notebook, old outputs included, to `en/notebooks/output-history/`, shows where it saved it, and only then generates the new version. If the backup fails, it stops and does not overwrite anything.
Even when outputs are kept, that does not mean the new prerequisite files and model behavior have been verified; you still need a trial run in Colab before class, and then save the results.
If you edit text directly in Colab (for example a cell title), also make the same change in `en/scripts/nbspec/`, or the next generation will overwrite it.
Before regenerating, run `git pull` to get the latest version saved back from Colab.

To run every notebook from start to finish on your machine and confirm that every cell runs:

```bash
uv run python en/scripts/verify_notebooks.py
```

This verification needs neither Colab nor an API key: it uses the **fake `google.colab`** and the **fake model** in `en/tests/mock_colab/` (which reply by fixed rules plus a bit of randomness), and replaces `/content/` with a temporary folder.
So it checks that "the flow and the code fit together"; **it does not say anything about the quality of a real model's answers, or about compatibility with real Colab**. To see the real behavior, run the notebooks once in Colab.
The results are saved as `en/notebooks/*.executed.ipynb` (not tracked by git), so you can open them and see each cell's output.

After adding, removing or reordering slides, run `uv run python en/scripts/sync_slide_navigation.py` to rebuild the slide numbers and navigation, then update the slide references in the outlines and notebooks to match; `uv run python en/scripts/sync_slide_navigation.py --check` only checks. Run `uv run python -m unittest discover -s en/tests` to check regression cases such as how notebook outputs are matched.

## References

- Full syllabus (timetable, concept list, notebook specs, minimum completion standards): [`docs/syllabus.md`](docs/syllabus.md)
- Slide-by-slide outlines: [`docs/slides-session1-outline.md`](docs/slides-session1-outline.md), [`docs/slides-session2-outline.md`](docs/slides-session2-outline.md)
- Articles and research cited: the "References" slides at the end of both decks
