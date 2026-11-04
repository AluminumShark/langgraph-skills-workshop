from nbbuild import badge, code, ending, md, project_intro, setup, writefile

NAME = "2-B_code_text_script"

# Every run cell carries these shared helper functions; you still need to finish the environment setup and that part's file preparation first
HELPERS = '''import json, re

def read_handbook_body(path):
    text = path.read_text(encoding="utf-8")
    return text.split("---", 2)[2].strip() if text.startswith("---") else text

def extract_names(text):
    """Pull "Line N: name" out of a reply and return a sorted [(line_no, name), ...]."""
    return sorted({(int(line_no), name) for line_no, name in re.findall(r"Line\\s*(\\d+)\\s*:\\s*([A-Za-z_]\\w*)", text)})

def parse_status(text):
    lines = [line for line in text.splitlines() if line.strip()]
    unmatched = [line for line in lines if re.search(r"\\bLine\\s*\\d", line) and not extract_names(line)]
    if unmatched:
        return "Some lines could not be parsed; check the original text"
    if not extract_names(text) and not text.strip().startswith("OK:"):
        return "Cannot confirm the number of problems from the format; check the original text"
    return "Parsable"

def save_result(version, data):
    path = BASE / "2B_results.json"
    all_results = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    all_results[version] = data
    path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")'''


def _run(src: str) -> str:
    """Insert HELPERS after {PREAMBLE} (indented 8 spaces, matching the other lines inside code(\"\"\"...\"\"\"))."""
    helpers = "\n".join(("        " + line) if line else "" for line in HELPERS.splitlines())
    return src.replace("        {HELPERS}", helpers)


def cells():
    return [
        md(f"""
        # 2-B: One job, three placements: code, text, script

        {badge(NAME)}

        > 📍 **Matching slides**: Session 2 "Stop 2: Code · Text · Scripts", slides **13-19** (class time 0:28-0:48)
        """),
        project_intro("Put the same \"check variable naming\" job in three places (handbook text, a script, and a workflow), run each three times, and compare \"who does the check\" with \"who decides to run it\"."),
        md("""
        ## What this notebook does

        The Homework Helper wants to do one more thing: **check that variable names are "lowercase letters plus underscores"** (for example `my_score` passes; `myScore` and `MyScore` do not).
        The same rule can live in three places:

        | Placement | Where it lives | Who does the check |
        | --- | --- | --- |
        | **A** | Written into the handbook text (`skills/naming-check/SKILL.version-a.md`) | The AI works out how to check it again every time |
        | **B** | Written as a small program next to the handbook, `scripts/check_naming.py`, and the handbook tells the AI to run it | The AI decides whether to run it; the check itself is Python |
        | **C** | Written as one station in the flow (LangGraph) | The flow always runs the check when it reaches that station; the AI never touches it |

        All three can do the job, so what is the difference? **Run each three times, and record whether the results are the same, whether a tool was called, and how many AI calls were made. When the results are the same, the difference is who checks and who decides to run it.**
        This notebook has one new term: **script** (a small program that sits in the handbook's `scripts/` folder and really runs).

        | Part | What you do | Matching slides |
        | --- | --- | --- |
        | Part 1 | Look at the homework and the script; run `check_naming.py` once from the command line | 14, 16 |
        | Part 2 | Placement A: written in the handbook text, run three times | 15 |
        | Part 3 | Placement B: written as a script, the handbook tells the AI to run it, run three times | 16 |
        | Part 4 | Placement C: written as a LangGraph node, run three times | 17 |
        | Part 5 | The three versions side by side; this session's rule of thumb | 17-18 |
        | Part 6 | Pause: where does each of five jobs go? | 19 |

        ## How to use it (you do not need to edit anything in this notebook)

        1. Run **"0. Environment setup"** first.
        2. Every part: **🤔 guess whether the three runs match and how many AI calls → ▶ run → 👀 compare**.
        3. Parts 2-4 write this version's latest three-run result to `2B_results.json`; rerunning replaces that version's old record. Part 5 uses the last record of each of A, B, and C, so finish them in order with the same rule and homework.
        4. The environment setup and file preparation cells in this notebook overwrite the handbooks and scripts they contain. Keep any edits first, then prepare again; other notebooks do not pick up your edited versions automatically.
        5. How many AI calls each run makes: A makes 1 per round; B varies with tool choice and the loop, so read the measured count; C makes 0 for the naming check.
        """),
        setup(NAME, support=[
            "tools/__init__.py",
            "tools/check_naming.py",
            "skills/naming-check/scripts/check_naming.py",
            "skills/naming-check/SKILL.md",
            "skills/naming-check/SKILL.version-a.md",
        ]),
        md("""
        ---
        ## Part 1: One job, three places it can live

        > 📍 **Matching slides**: slide 14 "One naming check, three placements", slide 16 "Placement B: the model picks a tool, a script checks"

        Before comparing, prepare two things:
        1. This notebook uses the **same homework** from start to finish (printed below, with line numbers on the left).
        2. The naming-check **script** `check_naming.py`: the first setup cell after you look at the homework writes it into the handbook's `scripts/` folder.
           It does just one thing and prints a few short lines, like a small command-line tool.
           The next setup cell is `tools/check_naming.py`: it wraps the script in `@tool`, turning it into a **tool** the AI can call,
           so it can go into the toolbox of an **agent** (an AI that decides for itself whether to use tools). Part 3 uses it.

        ### 🤔 Predictions
        All three versions use the same rule:
        - Check assigned variables, function names, and function parameters; for a repeated name, list only the place where it is first defined; do not check class names; skip `self` and `cls`.
        - A name may have one leading underscore, then a lowercase letter, then lowercase letters, digits, or underscores.
        - This exercise has no exception for constants, so `MAX` fails and `result_2` passes. This is this course's rule; it does not claim every Python project works this way.

        The next cell only shows the homework. **Circle the names that break the rule and count them first, then check below.**
        """),
        code("""
        #@title 👀 Look at the homework and answer on paper first (this cell does not show the answer)
        {PREAMBLE}
        for i, line in enumerate(sample_homework["Inconsistent naming"].splitlines(), 1):
            print(f"{i:>3} | {line}")
        print("Circle the names that break the rule first, then run the script below to check.")
        """),
        writefile("skills/naming-check/scripts/check_naming.py"),
        writefile("tools/check_naming.py"),
        code("""
        #@title ▶ Run: look at the homework, then run check_naming.py once from the command line
        {PREAMBLE}
        import subprocess

        homework = sample_homework["Inconsistent naming"]
        (BASE / "homework.py").write_text(homework, encoding="utf-8")
        print("This homework (line numbers on the left):")
        for i, line in enumerate(homework.splitlines(), start=1):
            print(f"{i:>3} | {line}")

        script = BASE / "skills" / "naming-check" / "scripts" / "check_naming.py"
        print("\\n$ python check_naming.py homework.py")
        result = subprocess.run([sys.executable, str(script), str(BASE / "homework.py")],
                                capture_output=True, text=True, encoding="utf-8")
        print(result.stdout.strip() or result.stderr.strip())
        record("2-B Part 1: output of check_naming.py", result.stdout.strip())
        """),
        md("""
        ### 👀 What did you see

        - The script caught **6**: `CalcAverage`, `scoreList`, `Total`, `avgScore`, `myScores`, `MAX`. `s` and `result_2` pass.
        - Does `MAX` count? By Python convention constants may be all caps, but our rule says "lowercase plus underscores", so **the script follows the rule**.
          Whether to allow an exception is a human decision; the same script on the same input gives the same result.
        - The output is a few lines, one problem per line: the AI can read it and so can a person. This is the script principle: one script does one thing, and its output is short.
        """),
        md("""
        ---
        ## Part 2: Placement A: written into the handbook text

        > 📍 **Matching slides**: slide 15 "Placement A: the model judges from the handbook text"

        The script just listed 6 problems under this course's rule. This part tries the most intuitive placement: write the rule into the handbook text and let the AI check it itself.

        The next cell writes the handbook `skills/naming-check/SKILL.version-a.md` as the "text version": the same scope of names, format, and exception rules as the script.
        The cell after it has the AI read this handbook and check the same homework, **three times in a row**.

        ### 🤔 Predictions
        Will the three runs catch the same number? Will they match the 6 the script caught in Part 1?
        """),
        writefile("skills/naming-check/SKILL.version-a.md"),
        code(_run("""
        #@title ▶ Run: Placement A, same homework three times (the AI checks by itself)
        {PREAMBLE}
        {HELPERS}
        from langchain_core.messages import HumanMessage, SystemMessage

        handbook = read_handbook_body(BASE / "skills" / "naming-check" / "SKILL.version-a.md")
        print("Handbook body the AI read:\\n" + handbook + "\\n")
        homework = sample_homework["Inconsistent naming"]

        counter = ModelCallCounter()
        three_runs, evidence = [], []
        for i in range(1, 4):
            answer = model.invoke(
                [SystemMessage(handbook), HumanMessage(f"Please check this homework:\\n```python\\n{homework}```")],
                config={"callbacks": [counter]},
            ).text
            print(f"Run {i} raw answer:\\n{answer}")
            print("Parse status:", parse_status(answer))
            evidence.append({"raw_answer": answer, "parse_status": parse_status(answer)})
            result = extract_names(answer)
            three_runs.append(result)
            print(f"Run {i}: caught {len(result)} -> " + (", ".join(f"Line {n}: {name}" for n, name in result) or "(no parsable items; read the raw answer)"))

        same = all(x == three_runs[0] for x in three_runs)
        print(f"\\nAre the three runs the same? {'✅ Same' if same else '❌ Different'}; the AI was called {counter.count} times in total")
        save_result("A", {"three_runs": three_runs, "ai_calls": counter.count, "evidence": evidence})
        record("2-B Part 2: Placement A (written in the handbook text)", {"three_runs": three_runs, "same": same, "ai_calls": counter.count, "evidence": evidence})
        """)),
        md("""
        ### 👀 What did you see

        - Check whether the three results are the same, then compare them with the script's result. You may see missed items, extra items, different line numbers, or perfect agreement.
          The model judges from the text rule afresh each time, so the three runs may agree or may not.
        - Three identical runs is also a valid observation; record it honestly and do not rerun until it goes wrong. Three identical runs is no guarantee for every input; also check that the names and line numbers fit the shared rule.
        - And it may not match the script's 6. First separate the cases: the model judged wrongly, the reply format could not be parsed, or this run was judged correctly.
        """),
        md("""
        ---
        ## Part 3: Placement B: a small program, and the handbook tells the AI to run it

        > 📍 **Matching slides**: slide 16 "Placement B: the model picks a tool, a script checks"

        In Placement A the AI re-judges from the text rule every time. This part gives the check to a script, and the AI only decides whether to run it.

        The next cell writes a separate "script version" handbook `SKILL.md` (A uses a different file, so rerunning does not mix them): "Run `scripts/check_naming.py` (tool name `check_naming`) and write its output into the feedback."
        The cell after it uses `create_agent` (the one-line way to make an agent) to build an agent: the handbook is its **system prompt**
        (the text always placed first that tells the AI what to obey), and its toolbox holds just one tool, `check_naming` (the script wrapped in Part 1), again **run three times**.

        ### 🤔 Predictions
        1. Will the three runs catch the same this time? Will they match the script's output from Part 1?
        2. What two things does the AI do this time? Does it still need to think up "how to check"?
        """),
        writefile("skills/naming-check/SKILL.md"),
        code(_run("""
        #@title ▶ Run: Placement B, same homework three times (the AI decides whether to run the script)
        {PREAMBLE}
        {HELPERS}
        from langchain.agents import create_agent
        from tools.check_naming import check_naming

        handbook = read_handbook_body(BASE / "skills" / "naming-check" / "SKILL.md")
        print("Handbook body the AI read:\\n" + handbook + "\\n")
        homework = sample_homework["Inconsistent naming"]
        helper = create_agent(model, tools=[check_naming], system_prompt=handbook)

        counter = ModelCallCounter()
        three_runs, evidence = [], []
        for i in range(1, 4):
            result = helper.invoke(
                {"messages": [{"role": "user", "content": f"Please check this homework:\\n```python\\n{homework}```"}]},
                config={"callbacks": [counter]},
            )
            msgs = result["messages"]
            used = [c["name"] for m in msgs for c in (getattr(m, "tool_calls", None) or [])]
            tool_results = [m for m in msgs if m.type == "tool" and getattr(m, "name", "") == "check_naming"]
            script_output = [m.text for m in tool_results]
            final_reply = msgs[-1].text
            names_found = extract_names(final_reply)
            script_items = sorted({pair for t in script_output for pair in extract_names(t)})
            ran = any(getattr(m, "status", "success") != "error" for m in tool_results)
            kept = ran and names_found == script_items and parse_status(final_reply) == "Parsable"
            evidence.append({"tools_requested": used, "tool_returned_ok": ran, "raw_script_output": script_output, "script_items": script_items,
                             "final_reply": final_reply, "parse_status": parse_status(final_reply), "kept_all_items": kept})
            three_runs.append(names_found)
            print(f"========== Run {i} ==========")
            print("Tools the AI requested:", ", ".join(used) or "(no tool used; it judged by itself)")
            print("Tool returned successfully:", ran)
            if script_output:
                print("Script output this run:\\n" + "\\n---\\n".join(script_output))
            print("The AI's final reply, verbatim:\\n" + final_reply)
            print("Parse status:", parse_status(final_reply), "| Kept every script item:", kept)
            print(f"The AI's final reply yielded {len(names_found)} -> " + (", ".join(f"Line {n}: {name}" for n, name in names_found) or "(no parsable items; read the raw answer)"))
            print()

        same = all(x == three_runs[0] for x in three_runs)
        print(f"Are the three runs the same? {'✅ Same' if same else '❌ Different'}; the AI was called {counter.count} times in total")
        save_result("B", {"three_runs": three_runs, "ai_calls": counter.count, "evidence": evidence})
        record("2-B Part 3: Placement B (written as a script)", {"three_runs": three_runs, "same": same, "ai_calls": counter.count, "evidence": evidence})
        """)),
        md("""
        ### 👀 What did you see

        - First confirm that the tool was really called in all three runs; when it was, compare the script's result with the final reply. A fixed script result does not mean the model calls it or relays it in full every time.
        - The AI no longer works out how to check. Here we want it to do two things: **decide whether to run the tool** and **put the result into the reply**. Use the output to confirm what it actually did. With the same input and rules the script result is fixed, but the relaying still needs checking.
        - But "whether to run it" is still the AI's decision: if in some run it did not call the tool and judged by itself, then even if the answer happens to match there is no evidence the script ran. Placement C in the next part does not have this problem.
        - If the tool is called just once, there are usually two model responses: first it requests the tool, then it writes the final reply. With no tool use or several calls the count differs; go by the counter.
        """),
        md("""
        ---
        ## Part 4: Placement C: a LangGraph node, and the AI never touches it

        > 📍 **Matching slides**: slide 17 "Placement C: the workflow always runs the same check"

        In Placement B the AI still decides whether to run the script. This part keeps the AI out of it altogether.

        This version has no handbook and no agent, only a **flow** drawn with LangGraph. Each station in the flow is a **node** (just a function) and always runs when the flow reaches it;
        the dict passed between stations is the **State**. This flow has only one station, `check_naming`: it calls the same script directly and writes the result into the State's `naming_problems`.
        Like the helper's `check_syntax`: when the flow reaches this station, the check always happens.

        ### 🤔 Predictions
        Will the three runs be the same? How many AI calls will this version make in total?
        """),
        code(_run("""
        #@title ▶ Run: Placement C, the flow always runs the check, three times
        {PREAMBLE}
        {HELPERS}
        from typing import TypedDict
        from langgraph.graph import END, START, StateGraph
        from tools.check_naming import run_naming_script

        class NamingState(TypedDict):
            code: str
            naming_problems: str

        def check_naming(state: NamingState) -> dict:
            return {"naming_problems": run_naming_script(state["code"])}

        builder = StateGraph(NamingState)
        builder.add_node("check_naming", check_naming)
        builder.add_edge(START, "check_naming")
        builder.add_edge("check_naming", END)
        flow = builder.compile()

        homework = sample_homework["Inconsistent naming"]
        counter = ModelCallCounter()
        three_runs = []
        for i in range(1, 4):
            state = flow.invoke({"code": homework, "naming_problems": ""}, config={"callbacks": [counter]})
            result = extract_names(state["naming_problems"])
            three_runs.append(result)
            print(f"Run {i}: caught {len(result)} -> " + ", ".join(f"Line {n}: {name}" for n, name in result))

        same = all(x == three_runs[0] for x in three_runs)
        print(f"\\nAre the three runs the same? {'✅ Same' if same else '❌ Different'}; the AI was called {counter.count} times in total")
        save_result("C", {"three_runs": three_runs, "ai_calls": counter.count})
        record("2-B Part 4: Placement C (written as a flow node)", {"three_runs": three_runs, "same": same, "ai_calls": counter.count})
        """)),
        md("""
        ### 👀 What did you see

        - With the same input and script, these three runs should give the same result; the naming check itself makes **0 AI calls**. The model connection test in the environment setup is counted separately.
        - B and C use the same script; keep the difference clear: **in B the AI decides whether to run it; in C the flow always calls it.**
          Whether this job may ever be skipped decides whether you choose B or C.
        """),
        md("""
        ---
        ## Part 5: The three versions side by side

        > 📍 **Matching slides**: slide 17 (the difference between B and C), slide 18 "Two questions, decided separately"

        Below, we call Placements A, B, and C "the three versions". All three have run, and their results are saved to a file. This cell puts the results of Parts 2-4 side by side; a version you have not run yet will tell you to go back and run it.

        ### 🤔 Predictions
        If all three versions give the same result, where is the difference? Which uses the least AI? If every homework must have its naming checked, would you pick B or C?
        """),
        code("""
        #@title ▶ Run: compare the three versions side by side
        {PREAMBLE}
        import json
        from IPython.display import Markdown, display

        path = BASE / "2B_results.json"
        all_results = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        descriptions = {
            "A": ("A: written in the handbook text", "Part 2"),
            "B": ("B: written as a script, the AI decides to run it", "Part 3"),
            "C": ("C: written as a flow node, always runs", "Part 4"),
        }
        rows = ["| Version | Parsable items in the three runs | Same in all three | AI calls | Parse / tool evidence |", "| --- | --- | --- | --- | --- |"]
        for version, (name, part) in descriptions.items():
            if version not in all_results:
                rows.append(f"| {name} | (not run yet: run {part} first) | | | |")
                continue
            three_runs = all_results[version]["three_runs"]
            counts = ", ".join(str(len(x)) for x in three_runs)
            same = "✅ Same" if all(x == three_runs[0] for x in three_runs) else "❌ Different"
            evidence = all_results[version].get("evidence", [])
            summary = "; ".join(e["parse_status"] + (f" / tool returned={e['tool_returned_ok']}, kept all={e['kept_all_items']}" if version == "B" else "") for e in evidence) or "The flow got the script result directly"
            rows.append(f"| {name} | {counts} | {same} | {all_results[version]['ai_calls']} | {summary} |")
        display(Markdown("\\n".join(rows)))
        record("2-B Part 5: the three versions side by side", all_results)
        """),
        md("""
        ### 👀 What did you see

        - **A** is judged by the model, so record its consistency from the actual results; for **B**, look separately at whether the tool ran, the script output, and the model's relaying; **C** runs the script directly in the flow.
        - **C**'s check makes no model call and is always run by the flow; **B** lets the model choose the tool as it sees fit. Three identical runs is an observation; how it runs is decided by the program's structure.

        ### 📌 Ask two questions separately

        > **How is it done?** Fixed rules go in code or a script; criteria that need judgment go in the handbook.
        > **Who decides to run it?** A must-do on every run is called by the flow every time; when it depends on the situation, leave it to the agent to pick a tool.

        The same script can be called by the flow, and it can also be wrapped as a tool. These two questions are not three mutually exclusive drawers.
        """),
        md("""
        ---
        ## Part 6: Pause: where does each of five jobs go?

        > 📍 **Matching slides**: slide 19 "Pause: five tasks, two questions each"

        Finally, answer in order: **What does the job use? Who decides whether it runs?** When the conditions are not enough, write down your assumption; answers can combine, and you need not pick just one.

        | The job | How it is done / who decides to run it? |
        | --- | --- |
        | 1. What tone the feedback uses | ____ |
        | 2. Run the homework and read the output | ____ |
        | 3. At most three generations (including the first) | ____ |
        | 4. Check whether comments were written | ____ |
        | 5. Judge whether the logic is well written | ____ |

        <details>
        <summary>Open the reference answers after you write yours</summary>

        | The job | How it is done | Who runs it, and why |
        | --- | --- | --- |
        | 1. What tone the feedback uses | **Handbook** | Write the tone guidance into a Skill and give it to the model when it writes feedback |
        | 2. Run the homework and read the output | **Script / tool** | Run it with a tool; this example lets the agent use it as it sees fit, and if every submission must be tested, have the flow arrange it instead |
        | 3. At most three generations (including the first) | **Code** | In this course `retries` counts the first draft, and `retries >= 3` stops; it can be written as an if and must not be missed, or it would loop forever |
        | 4. Check whether comments were written | **Script** (make it a **flow node** if it must never be missed) | Use code to recognize real comments; if every submission must be checked, the flow arranges it, and an optional check can be wrapped as a tool. A # inside a string is not a comment |
        | 5. Judge whether the logic is well written | **Handbook** | Put the quality criteria into a Skill; correctness tests that can run still go to code, and the model adds interpretation |

        </details>
        """),
        *ending(),
    ]
