# Notes on Historical Material

> This file keeps material from the old lesson plan that may be worth reusing, and the planning at that time. It does not represent the current slide numbers, section order, or acceptance criteria. Implementation follows the [current syllabus](syllabus.md), the two slide-by-slide outlines, and `scripts/nbspec/`.

# REUSE.md: material from the old lesson plan that can be pasted in directly

Source: `AluminumShark/langgraph-harness-workshop` (cloned to `scratchpad/oldrepo/`; Gemini 2.5 Flash, langgraph 1.1.10 / langchain 1.2.18, a hand-built ReAct loop; a single 90-minute "Data Analyst Agent + trace/eval" session).
Slide numbers follow the new outline given by the coordinator (Session 1 is S1-N, Session 2 is S2-N). The parentheses give the old repo's notebook cell id or the `slides/workshop.pdf` page title, so you can look up the original text.

**Rewrite rules (every code block is annotated below)**
- Model object: the old `ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)` → the new `model` (built from `google.colab.ai` or the instructor's key; the slides just say `model`, with no vendor name).
- pandas context → review-bot context: `inspect_data` → `check_syntax`, `run_pandas` → `run_code`, `get_weather` → `run_code`, `question` (analyze a CSV) → `homework`, the `chatbot` node → `ask_model`, `data/sales.csv` → a string of Python homework.
- Always change `.text()` to `.text` (it is a property in langchain-core 1.x; the old slides wrote it as a method, and the notebook already uses the property).
- All code is copied verbatim from `notebooks/workshop.ipynb`. Only the lines marked "changed" were altered.

---

## 1. `bind_tools` prints the tool_calls JSON

- (a) **S1-8** (the core cell of 1-0_tool_calling). Old cell `3d2b10c8` plus explanation cell `eea28461`; slides "Look at what the LLM returns before entering LangGraph" and "Breaking down the LLM's response".
- (b) Code:

```python
from langchain_core.tools import tool

@tool
def run_code(code: str) -> str:            # changed: was get_weather(city)
    """Run a piece of Python homework and return the output or the error message."""   # changed: was "Look up the weather of a city."
    return "(We do not really run anything here; we only see whether the model wants to call it)"

model_with_tools = model.bind_tools([run_code])   # changed: was llm.bind_tools([get_weather])
resp = model_with_tools.invoke("Does this homework run? print('hi'")   # changed: was "What is the weather in Taipei today?"
print("content:", repr(resp.content))
print("tool_calls:", resp.tool_calls)
```

Actual output of the old version (copied as is; it looks the same after switching to run_code):

```
content: ''
tool_calls: [{'name': 'get_weather', 'args': {'city': 'Taipei'}, 'id': '032ae5d1-...', 'type': 'tool_call'}]
```

Original text of the old slide ("Breaking down the LLM's response" page, can be pasted directly):
> content: '' ← note that it is an empty string! The LLM does not plan to answer in text
> The four keys of tool_calls: name (what it is called), args (the arguments), id (to match the result), type (fixed)
> The LLM did not really run get_weather. It only made a suggestion
> We take this dict, call the matching function ourselves, and then wrap the result in a ToolMessage for the LLM

- (c) For beginners: a model cannot run programs. It only hands back a note saying "please run run_code with this argument". The one that really runs it is your Python.

---

## 2. With history vs. without history (an LLM has no memory)

- (a) **S1-4** (idea 1: "an LLM only continues text and does not remember the last conversation"). Old cells `bca48125` and `aac07fe8`; slide "§6.3 Multi-turn conversation: messages is a list".
- (b) Code:

```python
from langchain_core.messages import AIMessage, HumanMessage

# The LLM itself has no memory; you must stuff the whole conversation history into it
history = [
    HumanMessage(content="My name is Alice"),
    AIMessage(content="Hi Alice!"),
    HumanMessage(content="What is my name?"),
]
print(model.invoke(history).text)      # changed: was llm.invoke(history).text

# Counter-example: do not pass the history, only the last sentence
print(model.invoke("What is my name?").text)   # changed: was llm
```

Actual output of the old version (copied):

```
Your name is Alice.
---
I don't know your name.
I'm an AI and can't get or remember a user's personal information, so I don't know what your name is.
```

Original text of the old slide:
> An LLM has no memory. Every invoke must pass in the whole history. That is how it knows what was just discussed. So LangGraph wraps messages in a list, and you append instead of overwriting.

- (c) For beginners: it does not remember you. Every time, you paste the whole conversation record to it again.

---

## 3. Open up the returned object: type / content / tool_calls / usage_metadata

- (a) **S1-5** (when explaining tokens and the context window "desk", use `usage_metadata` to see how many tokens this call used). Old cells `4001ebb0` and `28cc4f06`; slides "Open the whole AIMessage" and "Every attribute of the object".
- (b) Code:

```python
resp = model.invoke("Answer in three words: what is Python?")   # changed: was llm

print("type:", type(resp).__name__)
print("content:", repr(resp.content))
print("tool_calls:", resp.tool_calls)
print("usage_metadata:", resp.usage_metadata)
print("response_metadata keys:", list(resp.response_metadata.keys()))
```

Actual output of the old version (copied; note that reasoning tokens took 501):

```
type: AIMessage
content: 'A programming language.'
tool_calls: []
usage_metadata: {'input_tokens': 10, 'output_tokens': 503, 'total_tokens': 513,
                 'input_token_details': {'cache_read': 0}, 'output_token_details': {'reasoning': 501}}
response_metadata keys: ['finish_reason', 'model_name', 'safety_ratings', 'model_provider']
```

Original text of the old slide ("Every attribute of the object" page):
> .text: the message text. The one used most today. When tools are used it may be an empty string
> .tool_calls: the tools the LLM suggests calling. An empty list = no tool call, anything in it = a call is wanted
> .usage_metadata: how many tokens this call cost. In production it is how you count the money {input_tokens, output_tokens, total_tokens}
> .response_metadata.finish_reason: STOP = normal / MAX_TOKENS = truncated
> Rule of thumb: use .text to show to people, and use .content for message serialization or to see the whole structure.

- (c) For beginners: `input_tokens` are the words you put on the desk, and `output_tokens` are the words it writes back. The desk (the context window) is only so big. When we connect MCP later, look at this number again to see how much it jumps.

---

## 4. Hand-built ToolNode + tools_condition loop (the expanded version of `create_agent`)

- (a) **Around S1-18, and the "expand the two-node LangGraph underneath" cell in 1-B**. Old cell `56950db5` (same as `src/pandas_pilot/graph.py`); slides "The full Data Analyst Agent: assembly", "Line-by-line dissection", and "The ReAct cycle".
- (b) Code:

```python
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

tools = [run_code, check_indent, read_spec]          # changed: was [inspect_data, run_pandas]
model_with_tools = model.bind_tools(tools)           # changed: was llm_with_tools = llm.bind_tools(tools)

def ask_model(state: MessagesState) -> dict:         # changed: the node was named chatbot
    return {"messages": [model_with_tools.invoke(state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("ask_model", ask_model)             # changed: was "chatbot"
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "ask_model")
# tools_condition: if the last message has tool_calls, go to the tools node; otherwise go to END
builder.add_conditional_edges("ask_model", tools_condition)
builder.add_edge("tools", "ask_model")  # after tools run, loop back to ask_model

agent = builder.compile()
```

The old slide's "line-by-line dissection" table (copied; can be turned into a `.tbl` directly):

| Component | What it does |
| --- | --- |
| `@tool` | Turns a function into a tool the LLM can see |
| `bind_tools(tools)` | Attaches the tool descriptions to the LLM call |
| `chatbot` node (`ask_model` in the new version) | Calls the LLM, which may reply with text or tool_calls |
| `ToolNode(tools)` | Reads tool_calls, runs them, and wraps the results |
| `tools_condition` | A built-in routing function: tool_calls present → tools / absent → END |
| `add_conditional_edges` | A conditional edge: decides the next station dynamically from the function's return value |
| `add_edge("tools", "chatbot")` | After the tool runs, go back to the LLM, which forms the loop |

> In essence, LangGraph automates the boilerplate of "take tool_calls → call them yourself → wrap in a ToolMessage and send back".
> The LLM decides → ToolNode runs → the result goes back to the LLM → it decides again, until the LLM thinks that is enough, returns no more tool_calls, and the flow goes to END.

- (c) For beginners: under the one line `create_agent(model, tools)` are these 12 lines: a node that asks the model, a node that runs tools, and an "are tools needed?" if, wired into a circle.

---

## 5. `pretty_trace`

- (a) **S1-23** (1-B "print the tool chosen at each step"; 2-B and 2-D share it too). Old cell `e23ef69e` (same as `src/pandas_pilot/trace.py`); slides "Wrap the trace in a nice print" and "What the trace output looks like".
- (b) Code:

```python
def pretty_trace(graph, user_message: str) -> list[dict]:
    events = []
    print(f"USER: {user_message}\n")
    inputs = {"messages": [{"role": "user", "content": user_message}]}
    for step, event in enumerate(graph.stream(inputs, stream_mode="updates"), start=1):
        events.append(event)
        for node_name, node_state in event.items():
            print(f"--- step {step} | node: {node_name} ---")
            for msg in node_state.get("messages", []):
                role = type(msg).__name__
                tool_calls = getattr(msg, "tool_calls", None)
                if tool_calls:
                    for call in tool_calls:
                        print(f"  Model decided to call -> {call['name']}({call['args']})")   # changed: was "[{role}] tool_call ->"
                else:
                    text = msg.text if hasattr(msg, "text") else str(msg.content)
                    if len(text) > 400:
                        text = text[:400] + "..."
                    print(f"  [{role}] {text}")
            print()
    return events

events = pretty_trace(agent, homework)        # changed: was pretty_trace(agent, question)
```

Actual output of the old version (copied; just swap the tool names):

```
--- step 1 | node: chatbot ---
  [AIMessage] tool_call -> inspect_data({'path': 'data/sales.csv'})
--- step 2 | node: tools ---
  [ToolMessage] shape: (100, 5) ...
--- step 3 | node: chatbot ---
  [AIMessage] tool_call -> run_pandas({'path': 'data/sales.csv', 'code': "..."})
--- step 4 | node: tools ---
  [ToolMessage] South ...
--- step 5 | node: chatbot ---
  [AIMessage] The region with the lowest average revenue is South, at 382.347727.
```

Original text of the old slide:
> invoke only gives you the end point. stream lays out the process.
> stream_mode='updates': after each node runs, it emits "what was returned". There is also 'values' (a snapshot of the whole state).
> The order of every node, which tool it called, and what result it saw: all visible.

- (c) For beginners: `invoke` gives you only the last sentence. `stream` lets you stand beside it and watch which tool it picks at each step.

---

## 6. Run three times to see the randomness, expect three different endings

- (a) **S1-24** (1-B "run the same homework twice and see the order differ" → changed to three runs). Old cell `85165e63` and explanation cell `faef113e`; slides "Try this agent three times" and "The essential nature of an LLM agent".
- (b) Code:

```python
for i in range(3):
    print(f"========== Run {i + 1} ==========")
    result = agent.invoke({"messages": [{"role": "user", "content": homework}]})   # changed: was question
    print(result["messages"][-1].text)
    print()
```

Original text of the old slide "Try this agent three times" (three columns; the suggested review-bot mapping is: runs run_code first / runs check_indent first / does not run anything and gives a comment directly):
> Expect to see three inconsistent runs
> First run: maybe East is the worst | Second run: maybe West is the worst | Third run: maybe it skips inspect_data and the result may be wrong
> Do not rush to find the cause. The phenomenon itself is the topic of the second half

Original text of the old slide "The essential nature of an LLM agent":
> Follows the tool flow correctly | Same flow but different result | Wrong flow, the result may be wrong
> This is not a bug and not a coding mistake. With the same program and the same data, each run may take a different path and make a different decision. Everyone in the industry is dealing with this.

Original text of the old notebook explanation cell:
> **This is the nature of being stochastic**. Three inconsistent answers are perfectly normal. Sometimes it even runs without inspecting first.

- (c) For beginners: the same homework and the same program take three different paths in three runs. This is not broken. It is how agents are. That is why the next session teaches how to fix the steps that must be fixed.

---

## 7. "The docstring decides whether a tool gets used"

- (a) **S1-22** (the tool's manual); **S2-7** side by side with a Skill's `description` (a tool picks by its docstring ↔ an AI picks a handbook by its description). Old cells `d81b6a38` and `abbfe9cd`; slides "§8.3 The docstring is the LLM's only 'user manual'" and "80% of your agent's behavior depends on the tool docstring".
- (b) Code:

```python
# The LLM cannot see your code. It only sees the tool's name, docstring, and arguments
print(run_code.name)           # changed: was get_weather
print(run_code.description)    # this is the docstring
print(run_code.args)
```

Output of the old version (copied):

```
get_weather
Look up the weather of a city.
{'city': {'title': 'City', 'type': 'string'}}
```

Original text of the old slide (the whole page can be pasted):
> @tool wraps a function's name, arguments, and docstring into a JSON schema and feeds it to the LLM
> The LLM relies entirely on the docstring to decide whether to call this tool. A badly written docstring = the LLM never calls it
> A good docstring says: what it does / when to call it / what the arguments mean / what it returns
> Common mistakes: writing only one line like "look up the weather" / not saying when to call it / not explaining the argument format / using odd mixed-language wording
> 80% of whether your agent behaves well depends on how well the tool docstring is written
> Gemini is more sensitive to short docstrings than Claude. Write in detail so the LLM calls it reliably

Original text of the old notebook:
> **A badly written docstring → nobody uses the tool**.

S2-7 side-by-side suggestion: on the left, paste "A good docstring says: what it does / when to call it" from above. On the right, paste idea 17 of the new syllabus, "a description says what it does and when to use it". Title: "The same thing: the AI decides whether to pick it up by reading only the first line of the manual".

- (c) For beginners: the model cannot see your code. It only sees that one line of description. If the description does not say "when to use me", it will never use me.

---

## 8. Full text of the "6 LangGraph traps" cheatsheet

- (a) **S1-13 and S1-14** use items 1, 2, and 5 (State discipline, conditional edges only read state). The **Session 2 handout** carries all six. Old slide "§14 Cheatsheet: 6 LangGraph traps you will step on".
- (b) Copied in full:

| # | Trap | Fix |
| --- | --- | --- |
| 1 | `state["messages"].append(...)` | → `return {"messages": [new_msg]}` |
| 2 | A custom State without a reducer, so the message list gets overwritten | → `Annotated[list, add_messages]` |
| 3 | Calling invoke without `compile()` | → after `graph = builder.compile()` |
| 4 | The `@tool` docstring does not say "when to use" | → the LLM does not know when to call it |
| 5 | Calling the LLM inside a routing function | → routing only reads plain values in state |
| 6 | Using `eval()` in a tool to run code from the LLM | → in production, use a sandbox / RestrictedPython |

> 1-3 are state discipline / 4-5 are graph design / 6 is security
> Take a picture of this page. When you get stuck writing code, flip to it and save 30 minutes of debugging.

The matching "State discipline" page (usable for S1-13):

```python
# Wrong way
def bad_node(state):
    state["messages"].append(new_msg)
    return state          # mutates the state object directly → bypasses the reducer → hard-to-predict behavior

# Right way
def good_node(state):
    return {"messages": [new_msg]}   # return a new dict → the reducer merges it → predictable behavior
```
> Never mutate state directly. Wrap the new thing in a dict and return it, and let the reducer merge it for you.

- (c) For beginners: a node hands back a small note saying "which box I changed". It does not take the whole order slip and scribble on it. Which way to go (a conditional edge) depends only on the words on the order slip. Do not ask the AI again.

---

## 9. Counter-example: messages get overwritten without `add_messages`

- (a) **S1-13** (State is a dict, each node writes only its own field, a list must be merged, not overwritten). Old slides "Counter-example: what happens without add_messages" and "Inside MessagesState"; the notebook has only the text cell `9fb74552`.
- (b) Code (slide version; assemble `bad_graph` using the skeleton from item 4):

```python
class BadState(TypedDict):
    messages: list   # ← the default behavior is "overwrite"

def bad_chatbot(state: BadState) -> dict:
    response = model.invoke(state["messages"])      # changed: was llm
    return {"messages": [response]}   # overwrites the whole list

# Run once
r1 = bad_graph.invoke({
    "messages": [{"role": "user", "content": "My name is Alex"}]
})
print(len(r1["messages"]))
# 1   ← weird! The user message disappeared
```

The fix (original text of the "Inside MessagesState" page):

```python
class MessagesState(TypedDict):
    messages: Annotated[list, add_messages]
```
> How do you read this line? messages is a list, but when LangGraph handles it, it should not overwrite. It should merge (append) with add_messages.
> Mnemonic: the first slot of Annotated is the real type, and the second slot is a hint for the framework.
> Cause of the bug: `return {"messages": [response]}` overwrites the whole list by default, so the original "My name is Alex" simply vanished → adding `Annotated[list, add_messages]` fixes it.

- (c) For beginners: if the "conversation" box on the order slip is wiped out and rewritten every time, what was said earlier is gone. `add_messages` tells it "keep writing below in this box".

---

## 10. Eval suite: five cases, `evaluate_one`, 40% → 100%

- (a) **S2-19, S2-20** ("verification node = computational sensor": check with code after the action, spending no tokens). Old cells `63e33cf1`, `a65b2edd`, `07702f0c`, `696d8a94`, `5e8c7823` (same as `src/pandas_pilot/eval.py`); slides "Eval case example", "Eval runner", and "See the improvement in numbers".
- (b) The structure of the five cases (the first two copied; the review-bot version replaces `must_call_first` with `"check_syntax"` and `must_contain_in_final` with `["Strengths", "Improvements"]`):

```python
EVAL_CASES = [
    {
        "id": "001_must_inspect_first",
        "user_message": f"Give me an overview of the data in {CSV_PATH}.",
        "must_call_first": "inspect_data",
        "must_contain_in_final": [],
    },
    {
        "id": "002_handle_empty_result",
        "user_message": f"In {CSV_PATH}, count the records where region is 'Mars'.",
        "must_call_first": "inspect_data",
        "must_contain_in_final": ["0"],
    },
    # 003_inspect_before_summary / 004_top_region / 005_count_rows have the same structure
]
```

The `evaluate_one` logic (copied):

```python
def evaluate_one(graph, case):
    inputs = {"messages": [{"role": "user", "content": case["user_message"]}]}
    events = list(graph.stream(inputs, stream_mode="updates"))
    tc = extract_tool_calls(events)        # pull out the order of tool calls (by name) from the events
    final = extract_final_text(events)     # the last model message without tool_calls

    reasons = []
    if case["must_call_first"]:
        if not tc:
            reasons.append(f"No tool was called (expected {case['must_call_first']})")
        elif tc[0] != case["must_call_first"]:
            reasons.append(f"The first tool was {tc[0]}, expected {case['must_call_first']}")
    for kw in case.get("must_contain_in_final", []):
        if kw not in final:
            reasons.append(f"The final reply is missing the keyword {kw!r}")

    return {"id": case["id"], "passed": not reasons, "reasons": reasons,
            "tool_calls": tc, "final_text": final}
```

The numbers actually produced by the old version (copied; can be made into a two-column comparison directly):

```
baseline (no system prompt)                   v2 (added "call inspect_data first, then analyze")
[PASS] 001  tool_calls=['inspect_data']       [PASS] 001  ['inspect_data']
[FAIL] 002  tool_calls=['run_pandas']         [PASS] 002  ['inspect_data', 'run_pandas']
        - The first tool was run_pandas, expected inspect_data
[FAIL] 003  tool_calls=['run_pandas']         [PASS] 003  ['inspect_data', 'run_pandas']
[FAIL] 004  tool_calls=['run_pandas']         [PASS] 004  ['inspect_data', 'run_pandas', 'run_pandas']
[PASS] 005  tool_calls=['inspect_data']       [PASS] 005  ['inspect_data']
Passed 2/5 (40%)                              Passed 5/5 (100%)
```

Original text of the old slide:
> Write "how the agent should behave" as rules that a program can check. Change the prompt → run the eval → watch the pass rate change. The unit-test mindset of software engineering, moved onto LLM behavior.
> These are all "rules a program can judge". No human needs to look at every answer.
> Change one line of the prompt and see the improvement in numbers. Without an eval you can only change the prompt on a feeling that "it seems better".
> The point is not a perfect score: v2 is not always 100% either, because the LLM sometimes still does not listen. Only with an objective baseline can you tell whether v1 vs. v2 is real progress.
> An eval set "grows", it is not "planned". Write 1 first → run → change the prompt → find a new bug → write the 2nd case.

How it connects to the new syllabus: this is "the guides changed (the system prompt), and we measure with a sensor (the eval)". Go one step further: write `must_call_first` directly as the graph's order and `must_contain_in_final` as a `check_format` node, and you no longer test after the fact or spend tokens. That is the argument of 2-B version C.

- (c) For beginners: quiz the AI with five questions. Before changing one sentence it gets 2 right, after the change it gets 5 right. The numbers speak, and the test paper is graded by a program, not by a person looking.

---

## 11. The four things of the harness loop + the five-point harness self-check

- (a) **S2-34** wrap-up, or "more in the handout". Old slides "A complete harness includes four things", "§13 Harness Loop", "Harness self-check list", and "The most important sentence today".
- (b) Copied in full:

**A complete harness includes four things**
> What LLMOps companies in the industry (LangSmith, Langfuse, Braintrust) sell is the tooling for these four things. Today we do not rely on a platform. We finish the core with LangGraph + 100 lines of code.
> Trace: "Why did the agent decide this way this time?"
> Replay: "When it fails, can we try again from the middle?"
> Eval: "I changed the prompt. Did things get better or worse overall?"
> Loop: "How do we connect the above into a continuous improvement loop?"

**Harness loop (original text of notebook §13)**
```
1. Change the agent (prompt / tool / graph)
2. run_eval_suite(agent)
3. See which case dropped → pretty_trace(agent, that_case) → find the problem
4. Go back to 1
```
> **This loop is the core of agent engineering.** Not LangGraph, and not Gemini. With any framework and any LLM, as long as you can run this loop, you can maintain it.

**Harness self-check list**
> Before writing a production agent, ask yourself these 5 points. If any one is unchecked, you are still at the demo stage, not production.
> ☐ Can you trace? Can you see the decision at each node?
> ☐ Is State explicit? Is all the data passed between nodes in the schema?
> ☐ Do you have an eval set? At least 5 cases covering known failures?
> ☐ Can you quantify a change? One command to run the eval and get a pass rate?
> ☐ Are graph changes recorded? Is there an eval report for each change?
> Without the checks, you have not finished writing an agent. You have only written a demo.

**Closing line**
> With trace + eval, your agent goes from a "demo program" to a "system you can iterate on with engineering".
> LangGraph will be replaced, Gemini will get new versions, API syntax will change. But the mental model of State + Node + Tool, and the engineering discipline of Trace + Eval, will stay with you for ten years.

How it maps to the new syllabus: Trace / Eval are sensors (checks after the action). Replay corresponds to checkpointer + thread_id (2-D). Loop is Osmani's "turn a mistake into a new rule in the harness".

- (c) For beginners: a harness is not only reins. It also needs a rear-view mirror (trace), a scoreboard (eval), rewinding (replay), and the habit of "add a rule every time you fall off".

---

## 12. The `eval()` safety warning → why `run_code` needs a fence

- (a) **S1-21** (the `run_code` tool in 1-B: block import os / subprocess, set a timeout). `run_pandas` in old cell `44d94687`, the README "safety warning"; slide "Safety warning about eval()".
- (b) Old code (copied, with the parts to change marked):

```python
@tool
def run_code(code: str) -> str:                  # changed: was run_pandas(path, code)
    """Run a piece of Python homework and return the output or the error message."""   # changed: was "Run pandas analysis code on a CSV..."
    # ⚠️ Note: eval() is a serious security problem in production
    # It is simplified here for the workshop. In practice, use a sandbox / RestrictedPython / e2b
    try:
        result = eval(code, {"df": df, "pd": pd})   # changed: the new version must switch to a restricted exec (block os/subprocess, timeout, capture stdout)
    except Exception as exc:
        return f"Execution error: {type(exc).__name__}: {exc}"
    text = str(result)
    if len(text) > 2000:
        text = text[:2000] + "\n... (output truncated)"
    return text
```

Original text of the old slide (the whole page can be pasted):
> ⚠️ Never write it like this in production
> run_pandas uses eval() to keep the code short enough to explain
> Running code generated by an LLM straight through eval = handing control of your program to the LLM
> The LLM might be tricked by prompt injection into writing `__import__('os').system('rm -rf /')`, and your server is gone
> Production must use: a sandboxed subprocess (run with subprocess, limit file/network access) / RestrictedPython (allow only a whitelist of Python operations) / e2b / Modal (dedicated code execution environments, the industry mainstream)

Original text of the README:
> `run_pandas` uses `eval()` to run code produced by the LLM. This is a serious vulnerability in production. In practice, use a sandbox / RestrictedPython / e2b. This project is for teaching and is deliberately simplified for explanation.

How it connects to the new syllabus: `run_code` runs "a student's homework", and a student's homework can contain anything (`import os` to delete files, an infinite loop). So the tool itself needs a fence: block `os` / `subprocess`, set a timeout, and shrink the traceback to one line for the model (this is also the principle in 2-B that "script output must be understandable to the AI"). In Session 2's 2-C this connects back to prompt injection: an instruction hidden in a Skill can also trick the model into calling `run_code` to run something harmful.

- (c) For beginners: `run_code` is a tool that really runs programs on your computer. Anything you hand to an AI has to be locked in a cage first. Otherwise, one trick and it deletes all your files.

---

## Extra: two more optional pieces

**A. The echo bot / clean→respond two-node graph (S1-11, S1-12, the skeleton of 1-A's plain Python nodes)**. Old cells `6b39d86f` and `98f8c04e`:

```python
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    code: str            # changed: was text
    feedback: str        # changed: added

def check_syntax(state: State) -> dict:          # changed: was clean
    return {"feedback": "Syntax OK"}                 # changed: was {"text": state["text"].strip().lower()}

def give_feedback(state: State) -> dict:         # changed: was respond
    return {"feedback": f"{state['feedback']}; nicely written"}   # changed

b = StateGraph(State)
b.add_node("check_syntax", check_syntax)
b.add_node("give_feedback", give_feedback)
b.add_edge(START, "check_syntax")
b.add_edge("check_syntax", "give_feedback")
b.add_edge("give_feedback", END)
g2 = b.compile()
print(g2.invoke({"code": "print('hi')", "feedback": ""}))
```
Original text of the old slide "the plumbing metaphor": "The two nodes never call each other directly. State is the only pipe between nodes. The benefit: nodes are decoupled." "You only return the fields you want to update. You do not copy the whole state every time."
How to say it: the order slip (State) is passed between workstations (Nodes), and each station fills in only its own box.

**B. The "think without typing" question type** (three places in the old slides: guess the output / the sixth eval case / how to debug when production reports a wrong calculation). The format is the new syllabus's "predict → run → compare". Just rewrite the questions:
> Think without typing: guess the output. `return {"response": state["user_input"].upper()}`, input "hello world". What does print(result) show?
> Think without typing: suppose you are the agent developer, and someone reports that "the agent sometimes gets a number wrong" in production. How would you debug it with the trace? Without a trace: you only see one wrong answer. With a trace: you can see which step went wrong.
