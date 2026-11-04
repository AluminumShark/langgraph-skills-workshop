from nbbuild import badge, code, ending, md, project_intro, setup, writefile

NAME = "2-D_dual_core"
HOMEWORK_OPTIONS = '["Inconsistent naming", "Variable typo", "Correct program", "Missing parenthesis"]'
REQUEST_OPTIONS = '["Take a look for a beginner handing in homework for the first time", "Midterm exam, official grading: please review strictly"]'
SUPPORT = [
    "tools/__init__.py", "tools/run_code.py", "tools/check_naming.py",
    "graph.py", "skill_loader.py",
    "skills/friendly-feedback/SKILL.md", "skills/strict-review/SKILL.md",
    "skills/naming-check/SKILL.md", "skills/naming-check/scripts/check_naming.py",
]


def cells():
    return [
        md(f"""
        # 2-D: Combining Workflow and Agent

        {badge(NAME)}

        > 📍 **Matching slides**: Session 2, "Stop 3: Security and integration", slides **25-28**; optional **43-44** (class time 1:08-1:23)
        """),
        project_intro("Connect the helper's workflow, agent, handbooks and scripts into one helper that combines a fixed workflow with an agent, and that can resume after an interruption."),
        md("""
        ## What this notebook does

        You can build the helper in two ways:

        - **Workflow**: the route is drawn in code (LangGraph). It checks syntax first; only if the syntax passes does it write feedback and check the format. Feedback that fails can be sent back to be rewritten, and the flow stops when it reaches the maximum number of generations.
          The branches and the order are clear; for any case you haven't handled, you still have to add a flow rule. (Session 1, 1-A)
        - **Agent**: you give the AI only a goal and a toolbox, and it decides which tools to use and how many times. It is very flexible, but the path can differ from run to run. (Session 1, 1-B)

        This notebook connects a fixed workflow with an agent. That is the **dual-core** approach from the course title:

        - **Outside** is the workflow (the program controls branches and order): check syntax first; only a pass goes on to the agent; the feedback must pass the format check, and the flow stops at the generation limit, possibly still not passed.
        - **Inside**, the `give_feedback` station (which writes the feedback) is a small agent (AI judgment):
          the handbook is 2-A's "friendly feedback" or "strict review", and its toolbox has 2-B's naming-check script `check_naming`, `run_code` (runs the homework), and `read_spec` (reads the assignment requirements).
          It decides on its own whether to check naming and whether to read the assignment.
        - The assignment and the homework are paired when a run starts, and the assignment is saved in the State as `spec`. `read_spec` reads only the assignment in that State, not the shared `spec.md`; a resumed run still uses the assignment in the original checkpoint.
        - A new component, `skill_loader`: one station in the workflow that looks at the **cards** of all handbooks (the name and description at the top of `SKILL.md`), picks one, and hands its body to the next station.
        - Finally, a **checkpointer** (automatic saving) and a **thread_id** (the number of a save) store the **State** after every step (the "order slip" passed between stations, a dict):
          if a run is interrupted, it can continue.

        | Part | What you'll see | Matching slides |
        | --- | --- | --- |
        | Part 1 | Write `dual_core.py` and draw the combined flow chart | 25-26 |
        | Part 2 | Run the whole thing once: the outer flow goes station by station, and the agent inside picks its own tools | 25-26 |
        | Part 3 | Interrupt: stop halfway and save the State to the checkpoint | 27 |
        | Part 4 ⭐ | Resume: with the same thread_id, or start from blank with a different thread_id | 27-28 |
        | Part 5 | The State history of one thread (one save per step) | 28 |
        | Part 6 | Optional: eval, compare prompt versions of a pure agent; record the actual pass rate | 43-44 |

        ## How to use it

        1. Run **"0. Setup"** first (this cell prepares a **fresh set of default copies**; it does not import the handbooks, scripts or tools you changed in earlier notebooks). This notebook uses the default handbooks.
        2. The only thing you need to change in this notebook is the **thread_id** (the forms in Parts 3 and 4). You can change the other forms too.
           Optional: to use the handbook you changed in 2-A, finish Parts 1-4 first, then open `/content/review-bot/skills/friendly-feedback/SKILL.md` in the left "Files" panel,
           paste in the content you backed up and save it (don't re-run "0. Setup" afterward, or it will be overwritten), and then re-run from Part 2 with a brand-new thread_id.
        3. The setup and prepare cells overwrite the handbooks, scripts and code in them, so keep any changes you made yourself; they do not delete an existing SQLite checkpoint.
        4. Each part: **🤔 write your prediction → ▶ run → 👀 compare**; in Parts 3 and 4, look at the checkpoint state before you act; to run an experiment again, use a thread_id you have never used. Class takes about 15 minutes: finish Parts 1-4 first, take a quick look at the history in Part 5, and leave Part 6 for after class.
        """),
        setup(NAME, support=SUPPORT),
        md("""
        ---
        ## Part 1: How the workflow and the agent fit together

        > 📍 **Matching slides**: slide 25 "Combining workflow and agent: wiring handbooks and tools", slide 26 "Where workflow meets agent: load the handbook, provide the tools"

        First look at the combined flow chart. The next cell writes `dual_core.py` (no changes needed; just run it).
        The file name `dual_core` is an old name. It means slide 25's "combining workflow and agent", the "dual-core" in the course title. If you want to read the code, look at three places:

        - `build_integrated_helper`: the outer nodes (the stations) and arrows, almost the same as the 1-A workflow, with one extra station, `skill_loader`
        - `make_skill_loader`: shows the model the **cards** of all handbooks, picks one, and puts its body into the State's `skill`
        - `make_give_feedback`: inside it, `create_agent` (the one-line way to make an agent) builds a small agent,
          with the handbook as its system prompt (the text that always goes first and tells the AI what to follow), and a toolbox of `check_naming`, `run_code` and `read_spec`

        ### 🤔 Prediction questions
        1. In the outer flow chart, between which two stations will `skill_loader` sit?
        2. Can you see in the flow chart which tools the inner agent will call?
        """),
        writefile("dual_core.py"),
        code("""
        #@title ▶ Run: draw the outer flow chart of the combined helper
        {PREAMBLE}
        import dual_core

        helper = dual_core.build_integrated_helper(model)
        show_graph(helper)
        """),
        md("""
        ### 👀 What did you see?

        - `skill_loader` sits between `check_syntax` (syntax OK) and `give_feedback`: only after the syntax passes does it pick a handbook, give feedback and check the format; a syntax error is explained and the run ends. **The workflow controls the order of this branch.**
        - The flow chart does not show which tools the agent will call, because that happens **inside** the `give_feedback` station, and the AI decides it at that moment.
          The outside guarantees the required checks run; the inside keeps room for judgment. That is dual-core.
        """),
        md(f"""
        ---
        ## Part 2: Run the whole thing once

        > 📍 **Matching slides**: slide 25 "Combining workflow and agent: wiring handbooks and tools"

        The last part only drew the chart. In this part we really run it once. The output prints station by station: the name after `▶` is the station, and the indented lines below it are the fields that station wrote into the State.

        There are three kinds of outcome in this course. Please keep "ended" and "succeeded" apart:

        | Path | Output and state |
        | --- | --- |
        | Syntax error | The code produces "Syntax: / Improvements:", does not enter the agent, and does not run the format check |
        | Syntax passes, feedback format passes | The feedback uses "Strengths: / Improvements:", format_ok=True |
        | Still not passed at the generation limit | The last version is kept for inspection, format_ok=False; it is not treated as a success |

        ### 🤔 Prediction questions
        1. With the homework "Inconsistent naming" and the request for a beginner, which handbook will `skill_loader` pick? What about the midterm request?
        2. Will the inner agent use `check_naming`? Will it also use `run_code`? If it uses `check_naming`, will the feedback include all 6 items the script found?
        3. If the feedback it writes is too long, who sends it back?
        """),
        code(f"""
        #@title ▶ Run: the integrated helper, station by station
        homework = "Inconsistent naming"  #@param {HOMEWORK_OPTIONS}
        review_request = "Take a look for a beginner handing in homework for the first time"  #@param {REQUEST_OPTIONS} {{allow-input: true}}
        feedback_char_limit = 750  #@param {{"type":"integer"}}
        #@markdown **Maximum generations (including the first)**
        max_generations = 3  #@param {{"type":"integer"}}
        {{PREAMBLE}}
        import time
        import dual_core

        helper = dual_core.build_integrated_helper(model, checkpointer=dual_core.open_checkpointer(),
                                                   max_retries=max_generations, feedback_char_limit=feedback_char_limit)
        config = {{"configurable": {{"thread_id": f"full-demo-{{time.time_ns()}}"}}}}
        state = dual_core.run_station_by_station(helper, dual_core.homework_input(homework, load_homework(homework), review_request), config)

        print("\\n========== Result ==========")
        print("This homework:", homework)
        print("This assignment:", state.get("spec"))
        print("Handbook picked:", state.get("skill_name"))
        print("Tools the inner agent used:", state.get("tools_used") or "(no tools used)")
        print(f"Feedback generated {{state.get('retries', 0)}} time(s); format_ok = {{state.get('format_ok')}}")
        print("Why it stopped:", "syntax did not pass" if not state.get("syntax_ok") else
              "format passed" if state.get("format_ok") else "reached the generation limit, format still not passed")
        print("\\nFeedback:")
        print(state.get("feedback"))
        record(f"2-D Part 2: one full run ({{homework}} / {{review_request}})", {{k: v for k, v in state.items() if k != "skill"}})
        """),
        md("""
        ### 👀 What did you see?

        - Syntax passes: `check_syntax → skill_loader → give_feedback → check_format`; it goes back to `give_feedback` only if the format fails and the generation limit has not been reached.
        - Syntax fails: `check_syntax → explain_error → end`. No handbook is picked, the model is not called, and `check_format` is skipped. To watch this branch, change only the homework to "Missing parenthesis"; afterward set it back to "Inconsistent naming".
        - Handbook choice, tool use and the feedback content are still up to the model. The required checks ran, but that does not mean the result passes.
        - This cell prints only which tools were used, not what they returned. For "Inconsistent naming" the script lists 6 items (you saw them in 2-B Part 1). Compare that with the feedback: it may list all of them or pick only a few, and the character limit also affects how many it picks. **Using a tool does not mean the feedback relays the tool's result in full.**
        - Optional limit comparison: set the homework back to "Inconsistent naming", keep the request for a beginner, set maximum generations to **1** and the character limit to **750**, and run once as the baseline. In the second round **change only the character limit to 1**. The two-part format can't fit in one character, so you should see "reached the limit, format still not passed". Afterward restore **750 / 3**.
        - `retries` is an internal field name. In this implementation it goes up by one every time feedback is written, **including the first draft**; in class, read it as "generations so far".
        """),
        md("""
        ---
        ## Part 3: Interrupt, stop halfway

        > 📍 **Matching slides**: slide 27 "Pause once, then resume with the same ID"

        Part 2 ran all the way through. But in the real world connections drop and programs crash, so this part stops halfway on purpose, to see whether the State was saved.

        A **checkpointer** saves the whole order slip (the State) each time a station finishes; a **thread_id** is the number of that save, like a locker number.
        The saves live in the file `/content/review-bot/checkpoints.sqlite`. As long as that file exists, re-running a cell can read them back. Colab may delete or replace the runtime and remove local files; if the file is gone, there is no old checkpoint.

        This part fixes the homework to "Inconsistent naming" (valid syntax) with the beginner request, and saves the matching average assignment. With a brand-new thread_id, the cell below pauses **before** `give_feedback`. This is a planned teaching interruption, not a simulation of every way a real disconnect can be recovered; a syntax error takes a different branch and cannot stop here.

        ### 🤔 Prediction question
        When it stops, which fields of the State in the checkpoint are already filled in? Does `feedback` have content?
        """),
        code(f"""
        #@title ▶ Run: stop just before give_feedback
        thread_id = "Alex's homework"  #@param {{type:"string"}}
        homework = "Inconsistent naming"  #@param {HOMEWORK_OPTIONS}
        review_request = "Take a look for a beginner handing in homework for the first time"  #@param {REQUEST_OPTIONS} {{allow-input: true}}
        {{PREAMBLE}}
        import dual_core

        helper = dual_core.build_integrated_helper(model, checkpointer=dual_core.open_checkpointer(), interrupt_before=["give_feedback"])
        config = {{"configurable": {{"thread_id": thread_id}}}}
        old_checkpointer = helper.get_state(config)
        if old_checkpointer.values and not old_checkpointer.values.get("spec"):
            raise SystemExit("This is an old checkpoint that did not save the assignment. In Parts 3 and 4, switch to the same brand-new thread_id, then pause and resume; the original checkpoint is kept.")
        if old_checkpointer.values:
            print(f"This ID already has a checkpoint: {{'not finished' if old_checkpointer.next else 'finished'}}. This cell keeps the original content and does not submit the homework again.")
            print("To resume, go to Part 4; to reset the experiment, fill the same brand-new ID in Parts 3 and 4, for example \\"Alex's homework-2\\".")
        else:
            dual_core.run_station_by_station(helper, dual_core.homework_input(homework, load_homework(homework), review_request), config)
        checkpointer = helper.get_state(config)
        print(f"\\n📂 Checkpoint for thread_id \\"{{thread_id}}\\":")
        print_state({{k: v for k, v in checkpointer.values.items() if k not in ("skill", "code")}})
        print("Next station (not run yet):", checkpointer.next)
        record(f"2-D Part 3: interrupt (thread_id={{thread_id}})", {{"next": list(checkpointer.next), **{{k: v for k, v in checkpointer.values.items() if k != "skill"}}}})
        """),
        md("""
        ### 👀 What did you see?

        - With a brand-new ID and the default homework, it stops before `give_feedback`: `syntax_ok` and `skill_name` are filled in, and `feedback` is still empty.
        - The assignment is also saved in `spec`: this average assignment will not pick up the addition assignment left over from the previous notebook. A resumed run uses the checkpoint, not the new assignment in the current form. For an old checkpoint with no `spec`, use a brand-new ID; the original is not deleted.
        - The "next station" is `('give_feedback',)`: the checkpoint remembers not only the State but also **where the flow had got to**.
        """),
        md(f"""
        ---
        ## Part 4 ⭐: Resume, or start from blank?

        > 📍 **Matching slides**: slides 27-28; minimum to complete: tell apart resuming an unfinished thread, retrieving a finished result, and a fresh run on a new ID

        The last part stopped halfway and left an "unfinished" State in the checkpoint. This part uses the thread_id to look for a checkpoint:
        if it finds one stopped halfway, it **resumes**; if it is already finished, it **only reads the existing result**; only a brand-new ID **starts from blank**.

        | ID status | What it does | Re-reads this cell's homework fields? |
        | --- | --- | --- |
        | Old ID, not finished | Continues with the pending node | No, uses the homework in the checkpoint |
        | Old ID, finished | Shows the finished result | No, does not review again |
        | A new ID never used | Starts from check_syntax | Yes |

        ### 🤔 Prediction questions (three rounds; write the answers on paper)

        Follow the slides in two steps: do the first round on slide 27; once resuming works, go to slide 28 for the second and third rounds.
        1. Keep the thread_id as **Alex's homework** (same as in Part 3) and run. Which station does it start from? Does `skill_name` need to be picked again?
        2. Run again with the same ID: will the finished result be reviewed again?
        3. Change the thread_id to a **never-used** "Ben's homework" and run again. Which station does it start from this time?
        """),
        code(f"""
        #@title ▶ Run: look up the checkpoint by thread_id, then resume or start from blank
        thread_id = "Alex's homework"  #@param {{type:"string"}}
        homework = "Inconsistent naming"  #@param {HOMEWORK_OPTIONS}
        review_request = "Take a look for a beginner handing in homework for the first time"  #@param {REQUEST_OPTIONS} {{allow-input: true}}
        {{PREAMBLE}}
        import dual_core

        helper = dual_core.build_integrated_helper(model, checkpointer=dual_core.open_checkpointer())
        config = {{"configurable": {{"thread_id": thread_id}}}}
        checkpointer = helper.get_state(config)

        if checkpointer.values and not checkpointer.values.get("spec"):
            raise SystemExit("This is an old checkpoint that did not save the assignment. Go back to Part 3, build a paused state with a brand-new thread_id, then fill in the same ID to resume.")
        if not checkpointer.values:
            print(f"🆕 thread_id \\"{{thread_id}}\\" has no checkpoint: the State is blank, so the run starts from the beginning\\n")
            state = dual_core.run_station_by_station(helper, dual_core.homework_input(homework, load_homework(homework), review_request), config)
            situation = "no checkpoint, started from blank"
        elif checkpointer.next:
            print(f"📂 Found a checkpoint for thread_id \\"{{thread_id}}\\": stopped before {{checkpointer.next}}, resuming")
            print("   Already in the checkpoint:", {{k: v for k, v in checkpointer.values.items() if k in ("syntax_ok", "skill_name", "retries")}}, "\\n")
            state = dual_core.run_station_by_station(helper, None, config)      # input None = continue from the checkpoint
            situation = "found a checkpoint, resumed"
        else:
            print(f"📂 thread_id \\"{{thread_id}}\\" has already finished; the checkpoint content is below (to start over, use a different thread_id)\\n")
            state = checkpointer.values
            situation = "already finished"

        print("\\n========== Current State ==========")
        print("Assignment in the checkpoint:", state.get("spec"))
        print_state({{k: v for k, v in state.items() if k not in ("skill", "code")}})
        print("Next station in the latest checkpoint:", helper.get_state(config).next or "(the flow has ended)")
        print("Reading the result:", "syntax did not pass; the feedback format was not checked" if state.get("syntax_ok") is False else
              "feedback format passed; the content still needs a look" if state.get("format_ok") else "feedback format did not pass; the flow ending does not mean success")
        record(f"2-D Part 4: {{situation}} (thread_id={{thread_id}})", {{k: v for k, v in state.items() if k != "skill"}})
        """),
        md("""
        ### 👀 What did you see?

        - **The same unfinished thread_id**: it continues from `give_feedback`; `check_syntax` and `skill_loader` are not re-run, and `skill_name` is the one that was in the checkpoint. **The State was not lost.**
        - **A thread_id never used**: the checkpoint is empty, the State starts from blank, and the whole flow runs again from `check_syntax`.
        - Here "finished" only means the flow has no next station; it does not mean the homework or the feedback passes. If you run the same thread_id again after it finishes, you will see "already finished": this time it only shows the original result. Switching IDs just looks up a different checkpoint; it does not delete the original one.
        - **Completion check**: point out the checkpoint ID, the next station and the skill_name in the output, and say whether the three rounds picked a handbook again. To reset from blank, change both cells to a brand-new ID.
        """),
        md("""
        ---
        ## Part 5: The State history of one thread

        > 📍 **Matching slides**: slide 28 (look at the State history after the run finishes)

        Part 4 looked at the "latest" checkpoint. In fact the checkpointer **saves one checkpoint every time a station finishes**, and the cell below lists every checkpoint of the same thread_id.

        ### 🤔 Prediction question
        Find which checkpoint first has skill_name and which first has feedback. The number of rewrites affects the number of checkpoints.
        """),
        code("""
        #@title ▶ Run: list every checkpoint of one thread_id
        thread_id = "Alex's homework"  #@param {type:"string"}
        {PREAMBLE}
        import dual_core

        helper = dual_core.build_integrated_helper(model, checkpointer=dual_core.open_checkpointer())
        config = {"configurable": {"thread_id": thread_id}}
        history = list(helper.get_state_history(config))
        if not history:
            print(f"thread_id \\"{thread_id}\\" has no checkpoint. Run Parts 3 and 4 first.")
        for snap in reversed(history):
            v = snap.values
            step_no = snap.metadata.get("step")
            print(f"{'input received' if step_no == -1 else f'step {step_no}'} | next station: {snap.next or '(end)'} | "
                  f"syntax_ok={v.get('syntax_ok')}  skill={v.get('skill_name')}  "
                  f"retries={v.get('retries')}  format_ok={v.get('format_ok')}  has feedback={'yes' if v.get('feedback') else 'no'}")
        record(f"2-D Part 5: State history (thread_id={thread_id})",
              [{"step": s.metadata.get("step"), "next": list(s.next),
                **{k: val for k, val in s.values.items() if k not in ("skill", "code")}} for s in reversed(history)])
        """),
        md("""
        ### 👀 What did you see?

        - Every time a station finishes, one more checkpoint appears, so you can watch the order slip fill in field by field. It is much like 1-A printing the whole order slip step by step, except this time it is **stored in a file**.
        - This cell is **viewing history**; it does not re-run any node. Replay (re-running from a specific checkpoint) is a different operation that this notebook does not demonstrate.
        """),
        md("""
        ---
        ## Part 6 (optional): Evals: how do you write "what it should do" as rules that code can check?

        > 📍 **Matching slides**: optional slide 43 "Optional: checking a pure agent with code", 44 "Optional: a fixed test set, before vs. after a change"

        This appendix switches to a different system: a **pure agent**, not the integrated helper from Parts 1-5; it puts check_syntax into its optional toolbox too. Without an outer flow, how do you know whether it follows the rules? The answer is **test it**.

        Writing "what the agent should do" as a test that code can grade automatically is called an **eval**. Here are five test cases (eval cases),
        each tied to its own assignment requirements, so the average assignment never reads the addition spec. Each case checks two things: **which tool is called first** and **which words the final reply must contain**. Code grades the test, not a person. We compare two versions of the system prompt:

        - **baseline** (the original version, used as the reference point): says nothing special about order
        - **v2**: adds one sentence, "always call check_syntax before giving feedback" (here `check_syntax` is the helper's syntax check wrapped as a tool)

        The "eval" here sets test cases for an agent, and it is a different thing from the "verifying agent" on Session 2 slide 35 that checks each piece of feedback. The form field "run_verification" means whether to run this eval.

        ⚠️ This part calls the model about 20-30 times. If your free quota is small, **run it after class**: tick "run_verification" in the form and run the cell.

        ### 🤔 Prediction questions
        How many of the five will baseline pass? What about after adding the sentence? Will it hit exactly 100%?
        """),
        code("""
        #@title ▶ Run (optional): five test cases, compare the pass rate of baseline and v2
        run_verification = False  #@param {type:"boolean"}
        {PREAMBLE}
        from langchain.agents import create_agent
        from langchain.tools import tool
        import graph
        import dual_core
        from tools.run_code import run_code

        @tool
        def check_syntax(code: str) -> str:
            \"\"\"Check whether a Python homework's syntax is correct. Returns "Syntax OK" or the line where the error is.\"\"\"
            result = graph.check_syntax({"code": code})
            return "Syntax OK" if result["syntax_ok"] else f"Syntax error: {result['error']}"

        # Five test cases: who must be called first, and what the final reply must contain
        EVAL_CASES = [
            {"id": "001_must_check_syntax_first", "homework": "Correct program", "must_call_first": "check_syntax", "must_contain_in_final": ["Strengths", "Improvements"]},
            {"id": "002_handle_syntax_error", "homework": "Missing parenthesis", "must_call_first": "check_syntax", "must_contain_in_final": ["Syntax"]},
            {"id": "003_wrong_variable", "homework": "Variable typo", "must_call_first": "check_syntax", "must_contain_in_final": ["Improvements"]},
            {"id": "004_messy_indent", "homework": "Messy indentation", "must_call_first": "check_syntax", "must_contain_in_final": ["Improvements"]},
            {"id": "005_naming", "homework": "Inconsistent naming", "must_call_first": "check_syntax", "must_contain_in_final": ["Strengths", "Improvements"]},
        ]

        def evaluate_one(system_prompt, case):
            read_spec = dual_core.make_read_spec(dual_core.sample_specs[case["homework"]])
            candidate = create_agent(model, tools=[check_syntax, run_code, read_spec], system_prompt=system_prompt)
            inputs = {"messages": [{"role": "user", "content": f"Please review this homework:\\n```python\\n{load_homework(case['homework'])}\\n```"}]}
            events = list(candidate.stream(inputs, stream_mode="updates"))
            msgs = [m for e in events for u in e.values() for m in (u or {}).get("messages", [])]
            tc = [c["name"] for m in msgs for c in (getattr(m, "tool_calls", None) or [])]   # order of tool calls
            final = next((m.text for m in reversed(msgs) if m.type == "ai" and not m.tool_calls), "")
            reasons = []
            if not tc:
                reasons.append(f"called no tool (expected {case['must_call_first']})")
            elif tc[0] != case["must_call_first"]:
                reasons.append(f"first tool was {tc[0]}, expected {case['must_call_first']}")
            for kw in case["must_contain_in_final"]:
                if kw not in final:
                    reasons.append(f"final reply is missing the keyword {kw!r}")
            return {"id": case["id"], "passed": not reasons, "reasons": reasons, "tool_calls": tc}

        base = "You are a Python homework helper. Give beginners feedback in English. The feedback has two parts: the first starts with \\"Strengths:\\" and the second starts with \\"Improvements:\\"."
        versions = {
            "baseline (no order given)": base,
            "v2 (adds \\"call check_syntax before giving feedback\\")": base + " Always call check_syntax to check the syntax before giving feedback.",
        }

        if not run_verification:
            print("This part is optional: tick \\"run_verification\\" in the form above, then run it again.")
        else:
            grade = {}
            for version, system_prompt in versions.items():
                print(f"===== {version} =====")
                results = [evaluate_one(system_prompt, case) for case in EVAL_CASES]
                for r in results:
                    print(f"[{'PASS' if r['passed'] else 'FAIL'}] {r['id']}  tool_calls={r['tool_calls']}")
                    for why in r["reasons"]:
                        print(f"        - {why}")
                passed = sum(r["passed"] for r in results)
                print(f"Passed {passed}/{len(results)} ({passed / len(results):.0%})\\n")
                grade[version] = f"{passed}/{len(results)}"
            record("2-D Part 6: eval pass rate", grade)
        """),
        md("""
        ### 👀 What did you see?

        - First write down how many cases baseline and v2 each passed, and why the others failed. Baseline may pass all of them; record what you actually saw.
        - v2 may improve, stay the same or get worse; one run of five cases only describes this test. Matching a keyword does not mean the feedback is correct, so you still need to spot-check the content by hand.
        - One step further: write "the first call must be check_syntax" directly as the **order of the outer flow**, and "there must be strengths and improvements" as a `check_format` node,
          so the flow runs the required checks along its branches: a syntax error does not enter feedback or the format check; feedback is format-checked only after the syntax passes. The checks themselves are decided by code. The integrated helper still needs testing of its branches, its limit, checkpoint resuming and the quality of its feedback; it is not exempt from evals.
        """),
        *ending(),
    ]
