from nbbuild import badge, code, ending, md, my_homework, project_intro, setup, writefile

NAME = "1-A_workflow"
HOMEWORK_OPTIONS = '["Missing parenthesis", "Correct program", "Empty", "Variable typo", "My homework"]'


def cells():
    return [
        md(f"""
        # 1-A: Workflow, where the program decides the route

        {badge(NAME)}

        > 📍 **Matching slides**: Session 1, "Stop 2: Workflow 1-A", slides **16–28** (class time 0:35–1:00)

        ## What this notebook does

        This notebook builds the first version of the Homework Helper, and its **route is decided by the program** (this approach is called a workflow):
        it checks the syntax first. If the syntax is wrong, it explains the error and ends, **skipping the format check**. Only when the syntax passes does it generate feedback and then check the format; if the format fails and the limit has not been reached, it generates again.
        What each step does and where the next step goes were all written in code beforehand. The AI only handles one of the steps.

        We write it with **LangGraph**, a Python package for **connecting a few functions with arrows so that one piece of data flows through them in order**.
        This session introduces three core components and compares them with the Python you already know. Think of a bubble-tea shop:

        | Python you know | LangGraph name | Bubble-tea shop | In the helper |
        | --- | --- | --- | --- |
        | dict | **State** | The order slip that travels with the drink | One slip records the homework, whether the syntax is right, the feedback, and how many times it has been generated |
        | function | **Node** | One workstation | `check_syntax`, `give_feedback`... each does just one thing |
        | calling in order | **Edge** | The arrows between workstations | After the feedback is written, check the format |
        | if / else | **Conditional edge** | A hot drink skips the ice station | If the syntax is wrong, go to "explain the error" instead |
        | while loop | An edge that points back | The sweetness is wrong, so send it back to be remade | The format fails and the limit is not reached, so generate again |

        | Part | What you will do | Matching slides |
        | --- | --- | --- |
        | Part 1 | Write out `graph.py`, draw the flow diagram, and find every Node and Edge | 17–23 |
        | Part 2 | No AI yet: switch between three homework samples and watch the order slip fill in cell by cell | 24–25 |
        | Part 3 | Put the AI into one node; adjust "Maximum generations" and "Feedback character limit" | 26–28 |
        | Optional after class | The message-merging rule | 46 |

        ## How to use it

        1. First run **"0. Environment setup"**.
        2. Every part: **🤔 write your prediction first → ▶ run → 👀 compare**. The only things you change in this notebook are form fields: **homework, maximum generations, feedback character limit**.
        3. **In class (required)**: Parts 1–3. **Optional after class**: the message-merging rule.
        4. When you see a long program with `%%writefile`, just run it to write the file; in this session read the output first, and you don't need to understand every line.
        5. The parts need the `graph.py` written in Part 1. If the module can't be found, run the environment setup and the Part 1 file-writing cell first, then come back to the current part.
        """),
        project_intro("Use LangGraph to connect the helper's four workstations (check syntax, explain error, write feedback, check format) into one fixed flow. "
                      "First see how the data flows without any AI, then put the AI into the \"write feedback\" station."),
        setup(NAME),
        *my_homework(),
        md("""
        ---
        ## Part 1: LangGraph just connects functions with arrows

        > 📍 **Matching slides**: slide 17 "LangGraph: connecting functions with arrows", 18 "The Homework Helper's flow: four workstations", 20 "Component 1: State, the order slip that travels along", 21 "Component 2: Node, one workstation", 22 "Component 3: Edge, the arrows between workstations", 23 "One table for the three components"

        First, look at the whole flow diagram: what the helper's four workstations look like in code, and how they are connected.

        The next cell saves the helper's program as `/content/review-bot/graph.py` (no changes needed, just run it).
        If you want to read the program, there are only three kinds of things to look for:

        - **State**: the `class State(TypedDict)` part, which is which cells the order slip has (see the table below).
        - **Node**: functions like `def check_syntax(state)`. It receives the whole order slip and **returns only the cells it is responsible for**; LangGraph writes them back onto the slip for you.
        - **Edge**: `add_edge` at the bottom (after A, always go to B) and `add_conditional_edges` (decide the next station depending on the situation, which is an if).

        | Cell on the order slip | What it records |
        | --- | --- |
        | `code` | The homework the student turned in |
        | `syntax_ok`, `error` | Whether the syntax is right, and which line is wrong (before checking, `syntax_ok` is `None` and `error` is an empty string) |
        | `feedback` | The feedback for the student |
        | `format_ok`, `format_problem` | Whether the feedback format passes, and the reason if it doesn't |
        | `retries` | How many times the feedback has been written |

        > What is "syntax"? It is Python's grammar rules, like parentheses must come in pairs and the `def` line must end with a colon.
        > `check_syntax` only checks grammar and **does not run** the program. `print(unknown_name)` has correct syntax, but it fails when run because the name is not defined.
        > Valid syntax, running successfully and meeting the assignment are three different checks. The helper in 1-A only checks syntax; `run_code`, which actually runs the program (you tried it in 1-0 Part 4), is not handed to the helper until 1-B.

        ### 🤔 Prediction questions
        1. How many Nodes (workstations) will the flow diagram have?
        2. Which arrows are "conditional edges" (the ones that fork)?
        3. Is there an arrow that points backward? Which Python syntax does it resemble?
        """),
        writefile("graph.py"),
        code("""
        #@title ▶ Run: draw the Homework Helper's flow diagram
        {PREAMBLE}
        import graph

        helper = graph.build_helper()        # No model yet: give_feedback uses fixed text
        show_graph(helper)

        g = helper.get_graph()
        print("Nodes (workstations):", [n for n in g.nodes if n not in ("__start__", "__end__")])
        print("Edges (arrows):")
        for e in g.edges:
            print(f"  {e.source} -> {e.target}{'   <- conditional edge (if)' if e.conditional else ''}")
        """),
        md("""
        ### 👀 What did you see?

        - 4 workstations: `check_syntax`, `explain_error`, `give_feedback`, `check_format` (`__start__` and `__end__` are the start and end points).
        - There are two places with conditional edges: after `check_syntax` it splits into "syntax OK -> give_feedback" and "syntax wrong -> explain_error"; after `check_format` it splits into "OK or limit reached -> end" and "fails and limit not reached -> send back to give_feedback".
        - The arrow from `check_format -> give_feedback` that **points backward** is just like a `while` loop: the sweetness is wrong, so send it back to be remade.
        - 🏅 Bonus question: in the `graph.py` cell above, find which lines these two conditional edges are written on (hint: look for `add_conditional_edges`).
        """),
        md(f"""
        ---
        ## Part 2: No AI yet, guess then run three homework samples

        > 📍 **Matching slides**: slide 24 "No AI yet: three homework samples, guess then run", slide 25 "Data flow: watch the order slip fill in"

        The last part showed the "shape" of the flow diagram. This part feeds in real homework and shows how the data flows from station to station.

        The nodes in this part are ordinary Python with no AI yet, and `give_feedback` returns a fixed piece of text.
        The form below has a "homework" dropdown. **Pick "Missing parenthesis", "Correct program" and "Empty" in turn and run once for each.**

        The program runs with `stream_mode="values"`, which means **after every station finishes, the whole order slip is printed once**,
        and it marks which cells were newly written in that step, so you can watch the order slip fill in cell by cell.

        ### 🤔 Worksheet (write on paper first, then run and compare)
        1. If the input is `print('hi'` (missing the closing parenthesis), which nodes does it pass through? What is `syntax_ok` at the end?
        2. For the correct program, after which step does `feedback` first have content?
        3. This system says "empty counts as not turned in". Does it take the write-feedback branch or the explain-error branch?
        """),
        code(f"""
        #@title ▶ Run: watch the order slip fill in cell by cell (no AI yet)
        homework = "Missing parenthesis"  #@param {HOMEWORK_OPTIONS}
        {{PREAMBLE}}
        import graph

        helper = graph.build_helper()        # No model: give_feedback uses fixed text
        code = load_homework(homework)
        print(f"Homework: {{code!r}}\\n")

        steps, prev_state = [], None
        for step_no, state in enumerate(helper.stream(graph.blank_order_slip(code), stream_mode="values"), start=1):
            print_order_slip(step_no, state, prev_state)
            steps.append(state)
            prev_state = state

        print("\\nFinal feedback:")
        print(state["feedback"])
        record(f"1-A Part 2: {{homework}} (no AI)", steps)
        """),
        md("""
        ### 👀 What did you see?

        1. **Missing parenthesis**: `check_syntax` writes `syntax_ok: False` and which line is wrong -> the conditional edge goes to `explain_error` -> it writes `feedback` -> end. It never passes through `give_feedback`.
        2. **Correct program**: `syntax_ok: True` -> `give_feedback` writes `feedback` and `retries: 1` (step 3, the `give_feedback` step, is when the feedback first appears) -> `check_format` writes `format_ok: True` -> end.
        3. **Empty**: empty is actually "legal" Python, but we added an extra `if` in `check_syntax`: empty counts as not turned in. This is "if something can be written as an if, write it in code". The output reuses the error branch's format with the title "Syntax", which does not mean empty is a syntax error.
        - Only one or two cells change at each step: **each node writes only the cells it is responsible for**, and all other cells are passed along untouched.
        - Whenever you read any LangGraph program from now on, ask two things first: which cells does State have? Which cell does each node write?
        """),
        md("""
        ---
        ## Part 3: Put the AI into one node

        > 📍 **Matching slides**: slide 26 "Putting AI into one node", 27 "The flow ended. Did the feedback pass?", slide 28 "Back to the helper's flow: all three design patterns"

        In the first two parts, `give_feedback` only returned fixed text. In this part we swap it for a real AI and leave everything else alone.

        Now `give_feedback` calls the model to write the feedback (the code is `make_give_feedback` in `graph.py`).
        The AI is just one line of code living inside one node: **the flow diagram is unchanged, State is unchanged, and the arrows are unchanged**.

        `check_format` is a plain-Python **checkpoint**: it checks the order of the "Strengths:" and "Improvements:" labels, that both sections are non-empty, and the character count; it does not judge whether the content is correct.
        If the check fails and the limit has not been reached, it sends the work back to `give_feedback` to generate again. `retries` records how many times the feedback has been written; when it reaches "Maximum generations", it no longer sends it back and simply ends.

        The form has two numbers you can adjust:

        - **Maximum generations**: the most times the feedback is generated, counting the first one (set it to 3 and it generates at most 3 times).
          In the code this value is passed to `max_retries`, and the State field is called `retries`. Both are legacy names; what they actually count is "generations, including the first".
        - **Feedback character limit**: the most characters the whole feedback may have (counting "Strengths:", "Improvements:", spaces, newlines and letters), and anything longer fails.

        ### 🤔 Prediction questions (write them down, then change the form and run)
        First run once with the defaults (homework "Variable typo", maximum generations 3, feedback character limit 450) as a baseline, then change the form and compare:
        1. Change "Maximum generations" to **1** and "Feedback character limit" to **90**: what will `format_ok` and the reason for stopping be?
        2. The program ended, but `format_ok=False`. Has the format requirement been met?
        3. (If you have time) Change generations back to 3 and keep the character limit at 90: will `retries` go up? If you run the same settings twice, are the feedback and `format_ok` the same? Record it honestly.
        """),
        code(f"""
        #@title ▶ Run: AI writes the feedback + the program checks the format (regenerate if it fails)
        homework = "Variable typo"  #@param {HOMEWORK_OPTIONS}
        max_generations = 3  #@param {{type:"slider", min:1, max:5, step:1}}
        feedback_char_limit = 450  #@param {{type:"slider", min:60, max:900, step:30}}
        {{PREAMBLE}}
        import graph

        helper = graph.build_helper(model, max_retries=max_generations, feedback_char_limit=feedback_char_limit)
        code = load_homework(homework)

        steps, prev_state = [], None
        for step_no, state in enumerate(helper.stream(graph.blank_order_slip(code), stream_mode="values"), start=1):
            print_order_slip(step_no, state, prev_state)
            steps.append(state)
            prev_state = state

        print(f"\\nIn the end: the feedback was generated {{state['retries']}} time(s), format_ok = {{state['format_ok']}}")
        if not state["syntax_ok"]:
            print("Reason for stopping: the homework did not pass the syntax/empty check, and the reason was explained.")
        elif state["format_ok"]:
            print("Reason for stopping: the feedback passed the format check.")
        else:
            print("Reason for stopping: reached the generation limit and the feedback still failed the format check, so a person needs to handle it. (Not passed.)")
        if state.get("format_problem"):
            print(f"Reason the last attempt failed: {{state['format_problem']}}")
        print("\\nFinal feedback:")
        print(state["feedback"])
        record(f"1-A Part 3: {{homework}} (AI, generation limit {{max_generations}}, character limit {{feedback_char_limit}})", steps)
        """),
        md("""
        ### 👀 What did you see?

        - With a smaller character limit, the feedback may be sent back more often. Watch `retries`; it is not guaranteed to go up every time. When it reaches "Maximum generations" it stops, and `format_ok` may still be `False` then.
          **With no limit, it might loop forever**: how many times the feedback may be generated has to be limited by the program.
        - Running the same homework twice, the feedback text may be the same or different. The feedback produced by `give_feedback` goes into the format check; the explanation for a syntax error takes a different branch. The flow **does not guarantee that the model will fix it until it passes**.
        - Only `format_ok=True` means it passed the format check here. Hitting the generation limit also ends the flow, but the feedback may still fail. **The flow ending and the task being met are two different things.**
        - Look back at the whole flow diagram: it happens to contain three common "flow layouts" (design patterns, from Anthropic's article "Building effective agents"):
          - **Prompt chaining**: `check_syntax -> give_feedback -> check_format`, small steps in a fixed order
          - **Routing**: the fork after `check_syntax`, which decides the type first and then hands off to a specialized step
          - **Evaluator-optimizer**: the loop where `check_format` sends work back to `give_feedback`; produce, check, and redo if it fails
        - Counting characters: the limit counts every character of the feedback, including "Strengths:", "Improvements:", spaces and newlines. The count is by `len()`, so a long English sentence uses up the limit quickly.
        """),
        md("""
        ---
        ## Optional after class: without "keep writing after the existing messages", the messages get overwritten

        > 📍 **Matching slides**: slide 46 "Optional appendix: how messages in State are merged" (optional after class)

        Every cell on the order slip so far held a single value (for example, after the check `syntax_ok` is True or False), so a new value can simply overwrite the old one.
        But what if a cell needs to hold "a whole conversation"?

        The model needs the program to supply the relevant conversation (1-0 Part 1). In LangGraph, the conversation goes in the `messages` cell of State.
        If you don't tell LangGraph "this cell should keep appending" (using `add_messages`), by default it **overwrites the whole cell**, and the earlier conversation is gone.

        ### 🤔 Prediction questions
        You send one message, "My name is Alex", through a node that calls the model. How many messages will `messages` contain afterwards? How many for each of the two ways of writing it?
        """),
        code("""
        #@title ▶ Run: BadState (overwrite) vs. with add_messages (keep appending)
        {PREAMBLE}
        from typing import Annotated, TypedDict
        from langgraph.graph import END, START, StateGraph
        from langgraph.graph.message import add_messages

        class BadState(TypedDict):
            messages: list                               # <- the default behavior is "overwrite"

        class GoodState(TypedDict):
            messages: Annotated[list, add_messages]      # <- tells LangGraph: keep appending to this cell

        def chatbot(state) -> dict:
            response = model.invoke(state["messages"])
            return {"messages": [response]}

        for name, StateClass in [("BadState (no add_messages)", BadState), ("GoodState (with add_messages)", GoodState)]:
            builder = StateGraph(StateClass)
            builder.add_node("chatbot", chatbot)
            builder.add_edge(START, "chatbot")
            builder.add_edge("chatbot", END)
            result = builder.compile().invoke({"messages": [{"role": "user", "content": "My name is Alex"}]})
            print(f"{name}: messages has {len(result['messages'])} message(s)")
            for m in result["messages"]:
                print(f"   [{m.type if hasattr(m, 'type') else m['role']}] {(m.text if hasattr(m, 'text') else m['content'])[:60]}")
            record(f"1-A bonus: {name}", result)
        """),
        md("""
        ### 👀 What did you see?

        - `BadState` has only **1 message** left: the user's "My name is Alex" was overwritten by the model's reply.
        - With `Annotated[list, add_messages]` there are **2 messages**: both the user's words and the model's reply are there.
        - How to read that line: `messages` is a list, but when LangGraph handles it, it should merge rather than overwrite, using `add_messages`. A rule of thumb: **the first item in `Annotated` is the data type, and the rest is extra information for the framework.**
        - The `MessagesState` in the optional after-class part of 1-B is exactly this line inside.
        """),
        *ending(),
    ]
