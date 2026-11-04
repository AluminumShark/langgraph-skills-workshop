# langgraph-harness-workshop

> Companion code for the LangGraph workshop: write your first Data Analyst Agent

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-harness-workshop/blob/main/notebooks/workshop.ipynb)

Click the badge above to open the notebook directly in Colab. No local install needed.

## What this is

Companion code for students in the LangGraph workshop. In a 90-minute workshop you build a ReAct agent that analyzes a CSV from scratch, see the agent's stochastic nature for yourself, and learn to manage it as an engineering system with trace + eval.

Workshop focus:

- Run the notebook live along with the instructor, and **watch the instructor open up the returned objects**. This matters more than the slides.
- Let students experience, on purpose, the reality that "same question, same program, the agent gives three different answers"
- Teach trace and eval, the two key disciplines that turn an agent into a system you can engineer

## Using Colab (students)

1. Click the **Open In Colab** badge above
2. In the top right, click **"Copy to Drive"** to save a copy to your own Drive
3. Go to https://aistudio.google.com/apikey and get a free Gemini API key
4. Paste the key into the string in the §1 cell (we only do this to save time in the workshop; in a real project, use a Colab secret or an environment variable)
5. Run the first cell to check the connection works
6. Follow along with the instructor

## Local development (advanced)

If you want to fork and modify it, or run it locally instead of on Colab:

```bash
# 1. Install uv (if you haven't yet)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. clone
git clone https://github.com/AluminumShark/langgraph-harness-workshop.git
cd langgraph-harness-workshop

# 3. Install dependencies
uv sync

# 4. Set the API key
export GOOGLE_API_KEY="your key"

# 5. Run the notebook
uv run jupyter notebook notebooks/workshop.ipynb

# Or run the tests
uv run pytest

# Lint / format
uv run ruff check .
uv run ruff format .

# Type check (ty is still in preview)
uv run ty check src/
```

## Directory layout

```
pandas-pilot/
├── README.md
├── pyproject.toml
├── .gitignore
├── .python-version
├── notebooks/
│   └── workshop.ipynb       # the main file students work in (§0-§14)
├── data/
│   └── sales.csv            # demo data (100 rows, with a few NaN)
├── scripts/
│   └── generate_sales_csv.py  # script that regenerates sales.csv
├── src/
│   └── pandas_pilot/
│       ├── __init__.py
│       ├── tools.py         # @tool definitions (inspect_data, run_pandas)
│       ├── graph.py         # build_graph()
│       ├── trace.py         # pretty_trace()
│       └── eval.py          # EVAL_CASES, evaluate_one, run_eval_suite
└── tests/
    └── test_smoke.py        # smoke test
```

## What the workshop covers

- §0 Opening
- §1 Environment first aid (API key, package install)
- §2 LangGraph mental model (Node / Edge / State)
- §3 Quick Python refresher (type hint / TypedDict / Annotated / `@tool`)
- §4 Your first graph: echo bot
- §5 Two nodes + an edge
- §6 Taking apart the LLM object
- §7 MessagesState
- §8 Tool Calling (the core of the first half)
- §9 First-half recap
- §10 Opening the second half (the harness idea)
- §11 Trace
- §12 Eval (baseline → rerun with a system prompt)
- §13 The Harness Loop idea
- §14 Wrap-up + after-class exercise ideas

## Security warning

`run_pandas` uses `eval()` to run code the LLM generates. In production, this is a serious vulnerability. In practice, use a sandbox / RestrictedPython / e2b. This project is for teaching, and is simplified on purpose to make it easier to explain.

## License

MIT
