from nbbuild import badge, code, ending, md, project_intro, setup

NAME = "1-0_tool_calling"


def cells():
    return [
        md(f"""
        # 1-0: How does AI actually "do" things? Reading the tool-calling note

        {badge(NAME)}

        > 📍 **Matching slides**: Session 1, "Stop 1: How AI gets things done", slides **5–15**; the usage-fields reading is appendix slide **45** (class time 0:10–0:35)

        ## What this notebook does

        This is the first notebook of Session 1. It lays the foundation: **how does AI actually "do" things?**

        A **model** (an LLM, a large language model, the thing behind ChatGPT and Gemini) first works by generating text: **it produces a reply from its input**.
        A single model call only sees what you give it this time. Actions like browsing the web or running code need tools that your program provides. So why can ChatGPT run Python for you?
        The answer is **tool calling**: the model only sends back a **note** saying "please run `run_code` with this code",
        and the thing that actually runs it is your Python.

        This notebook lets you see that note with your own eyes, then watch your Python follow the note and paste the result back.
        Repeat that in a loop and you have an **agent**.

        | Part | What you will see | Matching slides |
        | --- | --- | --- |
        | Part 1 | How relevant history changes the model's reply | 6–7 |
        | Part 2 | What the model returns: text and tool requests; usage details are optional reading | 8; 45 (usage reading) |
        | Part 3 | ⭐ The "note" the model sends back: `tool_calls` | 11–12 |
        | Part 4 | Your Python follows the note and pastes the result back; put it in a loop and it is an agent | 13–14 |
        | Part 5 | How a workflow differs from an agent (leads into 1-A and 1-B) | 15 |

        ## How to use it (you don't change anything in this notebook)

        1. First run **"0. Environment setup"** below (click the ▶ to the left of the cell). The first run installs packages, and how long that takes depends on your connection and environment.
        2. Every part follows the same order: **🤔 read the prediction questions and write your answers on paper → ▶ run → 👀 compare with "What did you see?"**.
        3. **In class (required)**: the main output of each part. The usage details in Part 2 are optional reading (appendix slide 45); the instructor may demo them, and you do not need to memorize the fields.
        4. Collapsed cells are code. Click "Show code" if you want to look; it's fine if you can't follow it, because in this session you only need to read the output.
        5. After a runtime reset, rerun "0. Environment setup" first. After that, every cell builds the messages and tools it needs, so you can rerun just the cell you want. For Part 4, run the first cell and then the loop cell.
        """),
        project_intro("The foundation before the helper can \"do\" things. The model generates a reply; when it wants a tool, it only sends back a \"note\" naming the tool, "
                      "and your Python is what actually does the work. The helpers in 1-A and 1-B are built on this."),
        setup(NAME, support=["tools/__init__.py", "tools/run_code.py"]),
        md("""
        ---
        ## Part 1: An LLM is a "continuation machine", and it has no memory

        > 📍 **Matching slides**: slide 6 "An LLM is a "continuation machine"", slide 7 "LLMs have no memory: your program supplies the conversation"

        Let's start with the basics: what does a model actually do?

        Each time, the model sees only "the text you give it this time" and guesses the most sensible continuation, like a machine that finishes your sentence.
        It does not remember the previous conversation, **unless your program passes the relevant history or a summary back in**.
        The cell below asks "What is my name?" twice. The first time it passes the earlier conversation along; the second time it sends only that one sentence.

        ### 🤔 Prediction questions (write on paper before running)
        1. The first time (with "My name is Alice" passed along), can it tell you your name?
        2. The second time (only "What is my name?"), how will it answer?
        """),
        code("""
        #@title ▶ Run: with history vs. without history
        {PREAMBLE}
        from langchain_core.messages import AIMessage, HumanMessage

        # The LLM has no memory of its own, so the program passes the relevant history in
        history = [
            HumanMessage(content="My name is Alice"),
            AIMessage(content="Hi Alice!"),
            HumanMessage(content="What is my name?"),
        ]
        with_history = model.invoke(history).text
        print("[Relevant history passed in]")
        print(with_history)

        # Counter-example: don't pass history, send only the last sentence
        without_history = model.invoke("What is my name?").text
        print("\\n[Only the last sentence passed in]")
        print(without_history)

        record("1-0 Part 1: with history vs. without history", {"with_history": with_history, "without_history": without_history})
        """),
        md("""
        ### 👀 What did you see?

        - With history, the model has a basis for answering "Alice"; with only the last sentence, it has no way to know the name. Compare the actual outputs; the wording does not have to match.
        - Same model, same question. The only difference is **whether you pasted the earlier lines back in**. It doesn't remember you; your program supplied the relevant record this time.
        - Going further: how a conversation is merged in LangGraph State is the optional after-class part of 1-A; saving a conversation across runs is 2-D in Session 2.
        """),
        md("""
        ---
        ## Part 2: Two kinds of content a model returns

        > 📍 **Matching slides**: slide 8 "Tokens and the context window", slide 45 "Optional appendix: usage fields in the returned object"

        The last part showed that the model rereads everything you give it every time. So how much can it read at once?

        - **Token**: the unit in which a model processes text. How text is split depends on the model, and usage and billing are often counted in tokens.
        - **Context window**: the maximum number of tokens a model can look at at once. Think of it as a **desk**: the conversation, instructions and data all have to be laid out on it, and if you put too much there, it won't fit.

        A model returns a message object. Besides the content and tool requests, it may also include token usage.

        ### 🤔 Prediction questions
        1. Will the model reply with text this time, or ask to use a tool? (Hint: we did not provide any tools.)
        2. Remember two fields first: `content` is text, and `tool_calls` is a tool request. Which one do you predict will have something in it?
        """),
        code("""
        #@title ▶ Run: look at the text and tool requests first (usage details are optional)
        show_usage_details = False  #@param {type:"boolean"}
        {PREAMBLE}
        resp = model.invoke("Answer in three words: what is Python?")

        print("content:", repr(resp.content))
        print("tool_calls:", resp.tool_calls)
        if show_usage_details:
            print("type:", type(resp).__name__)
            print("usage_metadata:", resp.usage_metadata)
            print("response_metadata keys:", list(resp.response_metadata.keys()))
            if "token_count" in resp.response_metadata:
                print("\\n(The token count from this adapter is an estimate. It is not the usage reported by the provider.)")

        record("1-0 Part 2: returned object", {"content": resp.content, "tool_calls": resp.tool_calls,
                                  "usage_metadata": resp.usage_metadata})
        """),
        md("""
        ### 👀 What did you see?

        - This time, just look at `content` and `tool_calls`. You don't need to memorize the object type or the other fields.
        - `.content` / `.text` is what it said; `.tool_calls` is an empty list, meaning it did **not** ask to use a tool this time (in the next part we provide a tool and then see whether it asks).
        - **Optional reading**: if you tick the usage details, `usage_metadata` shows input and output token usage. Depending on the model source, it may report actual usage or a teaching estimate, so don't compare the two directly.
          Some models count reasoning tokens in their usage, so you can't work it out from the length of the visible answer alone.
        - You don't need to remember the numbers. The optional MCP usage reading in 1-B compares the estimated length of tool descriptions.
        """),
        md("""
        ---
        ## Part 3 ⭐: The model only "says" which tool it wants

        > 📍 **Matching slides**: slide 11 "Tool calling: the model only "says" which tool it wants", slide 12 "Predict first: will the model ask to use a tool?"

        The first two parts had no tools, so we only looked at text replies. But the helper needs to "do" things, like actually run a student's program. What then?
        The answer is **tool calling**, which works like a three-panel comic:

        1. Your Python tells the model: "You have a tool called `run_code` that can run code." ← this is `bind_tools`
        2. The model returns a structured tool request (shown as JSON): "I want to use `run_code` with this code." ← this is `tool_calls`
        3. Your Python sees the note, **actually runs it**, and pastes the result back to the model ← the next part

        In this notebook we call the model's tool request the "note"; the "tool request" on the slides is the same thing.

        - **Tool**: an ordinary Python function with one `@tool` line on top. Once you provide it to the model through `bind_tools`, the model receives its name, description and parameters.
        - **JSON**: a data format written with curly braces `{}` that programs can read easily.

        The `run_code` in this cell is fake and runs nothing; we only watch whether the model wants to call it.

        ### 🤔 Prediction questions
        1. Will the model answer directly or ask to use a tool? If it answers directly, what will `content` (the text answer) say?
        2. If it asks to use a tool, which tool do you predict it picks, and which code does it hand over? Read the field names after the output appears.
        3. Did the model actually run `print('hi'`?
        """),
        code("""
        #@title ▶ Run: look at the "note" the model sends back
        {PREAMBLE}
        from langchain_core.tools import tool

        @tool
        def run_code(code: str) -> str:
            \"\"\"Run a Python homework and return its output or error message.\"\"\"
            return "(Not actually run here; we only check whether the model wants to call it)"

        model_with_tools = model.bind_tools([run_code])     # Comic panel 1: tell the model you have a tool
        resp = model_with_tools.invoke("Does this homework run? print('hi'")

        print("content:", repr(resp.content))
        print("tool_calls:", resp.tool_calls)              # Comic panel 2: the JSON note

        if "raw_text" in resp.response_metadata:
            print("\\n📝 The raw text the model actually returned:")
            print(resp.response_metadata["raw_text"])
        if not resp.tool_calls:
            print("\\nThis time the model answered directly, with no tool request. Record this result; you can still compare with the note shown on the slides, and you don't need to keep rerunning.")

        record("1-0 Part 3: the tool_calls note", {"content": resp.content, "tool_calls": resp.tool_calls})
        """),
        md("""
        ### 👀 What did you see?

        - **If there is a tool request**: first read `name` (which tool it picked) and `args` (what it handed to the tool). `content` may be an empty string.
        - **If there is no tool request**: the model chose to answer directly. That is also a valid observation, not a failed run. Compare it with the tool-request example on slide 13.
        - `tool_calls` is a list. Reading the tool name and arguments is enough for now; `id` is used to match results and `type` marks the kind of message, so treat both as optional reading.
        - The model did **not** run `print('hi'`; it only "suggested" that you run it. Whether to run it, and how, is up to your program.
        - With the built-in Colab model you will also see the "raw text": that is the response before the adapter parses it, and it may contain a tool request or a direct answer.
          On the Colab path, this course uses a teaching adapter (`review-bot/llm.py`) that writes the tool descriptions into the prompt and asks the model to reply in JSON,
          then turns that into an identical `tool_calls`. If you choose `gemini`, it uses native tool calling, and the note looks the same.
          This is exactly the point: **the model proposes a tool request, and your program does the work.**
        """),
        md("""
        ---
        ## Part 4: Your Python follows the note, then pastes the result back

        > 📍 **Matching slides**: slide 13 "Read the tool request, then call the model again", slide 14 "Agent = model + tools + loop"

        The last part only observed whether the model proposes a tool request; it did not run the tool. In this part, if we get a request, we actually run it and send back the result.

        This time we switch to a `run_code` that **really runs code**. It has guardrails: `import os` is not allowed, and it is stopped after 3 seconds (1-B explains this in detail).
        The flow has three steps:

        ① Ask the model → ② Follow the note and run it, wrap the result in a `ToolMessage` (the kind of message that means "the tool's result") and paste it into the conversation → ③ Ask the model again

        ### 🤔 Prediction questions
        1. In step ③, can the model see the result of `print(1+1)`? What will it say?
        2. If you repeat ①②③ over and over, when should it stop?
        """),
        code("""
        #@title ▶ Run: ① ask the model → ② actually run it → ③ paste the result back and ask again
        {PREAMBLE}
        from langchain_core.messages import HumanMessage, ToolMessage
        from tools.run_code import run_code     # The version that really runs code (with guardrails)

        model_with_tools = model.bind_tools([run_code])
        messages = [HumanMessage("Does this homework run? Please actually run it and tell me the result.\\n```python\\nprint(1+1)\\n```")]

        # ① Ask the model
        resp = model_with_tools.invoke(messages)
        messages.append(resp)
        print("① The model's note:", resp.tool_calls or "(no note, it answered directly)")

        # ② Your Python follows the note and really runs it, then wraps the result in a ToolMessage and pastes it back
        for call in resp.tool_calls:
            result = run_code.invoke(call["args"])
            print(f"② Your Python ran {call['name']}, result: {result}")
            messages.append(ToolMessage(content=result, tool_call_id=call["id"], name=call["name"]))

        # ③ Ask the model again: this time it can see the result
        if resp.tool_calls:
            final = model_with_tools.invoke(messages)
            messages.append(final)
            print("③ After seeing the result, the model said:", final.text or final.tool_calls)
        else:
            print("This time the model did not call a tool, so step ② did not run. Record \\"answered directly\\" and compare with the slide example.")

        record("1-0 Part 4: follow the note, run it, paste it back", messages)
        """),
        md("""
        ### 👀 What did you see?

        - When there is a tool request, in ② it is **your Python** that runs the code, not the model. The result is wrapped in a `ToolMessage` and matched to the note by `tool_call_id`.
        - After the tool runs, in ③ the model can read the result, because we pasted it into the conversation (remember Part 1? Relevant results have to be added to the conversation by the program).
        - Write ①②③ as a loop that keeps turning until the model says "no more tools", and that is an **agent**. Below is a loop with an upper limit that demonstrates this interaction.
        """),
        md("""
        ### 🤔 Prediction questions
        The loop below runs at most 5 rounds. How many rounds do you guess it will run before it stops? Why set "at most 5 rounds"?
        """),
        code("""
        #@title ▶ Run: write the three steps as a loop, and that is an agent (model + tools + loop)
        {PREAMBLE}
        from langchain_core.messages import HumanMessage, ToolMessage
        from tools.run_code import run_code

        model_with_tools = model.bind_tools([run_code])
        messages = [HumanMessage("Check whether this homework runs, and if there is an error, tell me what is wrong.\\n```python\\nx = 3\\nprint(x * y)\\n```")]

        for loop_no in range(1, 6):                         # At most 5 rounds, so it can't run forever
            resp = model_with_tools.invoke(messages)        # Ask the model
            messages.append(resp)
            if not resp.tool_calls:                         # It says no more tools -> done
                print(f"Round {loop_no}: the model said no more tools. Final answer:\\n{resp.text}")
                break
            for call in resp.tool_calls:                    # It wants a tool -> run it and paste the result back
                result = run_code.invoke(call["args"])
                print(f"Round {loop_no}: the model called {call['name']} -> {result}")
                messages.append(ToolMessage(content=result, tool_call_id=call["id"], name=call["name"]))

        else:
            print("Reached the maximum of 5 rounds and stopped; this does not mean the homework is finished.")

        record("1-0 Part 4: agent loop", messages)
        """),
        md("""
        ### 👀 What did you see?

        - Round 1 might call `run_code` and round 2 might give the feedback; or it might answer directly, or use a tool again. Record the actual number of rounds and why it stopped.
        - This loop shows the agent core model used in this course: **Agent = model + tools + loop**.
        - "At most 5 rounds" is a limit your program sets on the AI: an agent can keep going in circles, and every round costs money. The `recursion_limit` you will see in 1-B (force a stop after this many steps) is also a stop limit, but it counts graph steps, not the loop rounds here.
        """),
        md("""
        ---
        ## Part 5: Workflow vs. agent: who decides the next step?

        > 📍 **Matching slides**: slide 15 "Workflow vs. agent: who decides the next step"

        In the loop from the last part, **the model** decides on its own whether to use a tool next, which makes it an agent.
        The other approach is to have your program arrange the steps, branches and stopping conditions. That is a **workflow**. Each has its strengths:

        |  | Workflow | Agent |
        | --- | --- | --- |
        | Who decides the next step | The flow diagram you drew in code | The AI decides |
        | What it's like | The order-fulfilment line in a bubble-tea shop | An intern holding a toolbox |
        | Strength | Paths are easier to predict and debug | Can choose tools dynamically for the task |
        | Weakness | You must design branches and exception handling up front | Less stable, may take detours |
        | Where today | **1-A_workflow** | **1-B_agent** |

        Next, 1-A builds a workflow helper whose route is decided by the program, and 1-B builds an agent helper that picks its own tools.
        """),
        *ending(),
    ]
