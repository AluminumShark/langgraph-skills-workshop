from nbbuild import badge, code, ending, md, my_homework, project_intro, setup, writefile

NAME = "1-B_agent"
HOMEWORK_OPTIONS = '["Variable typo", "Correct program", "Messy indentation", "Missing parenthesis", "My homework"]'
DEFAULT_SPEC = "Write a function add(a, b) that returns the sum of two numbers, and use print(add(2, 3)) to print 5."

# Illustrative MCP tool list: scale modeled on the GitHub MCP server (names and descriptions are rewritten for teaching, not the official text)
MCP_TOOLS = [
    ("get_me", "Get details of the authenticated GitHub user.", {}),
    ("search_repositories", "Search GitHub repositories by keyword, language, stars or topic.", {"query": "string", "page": "integer", "per_page": "integer"}),
    ("get_repository", "Get metadata of a repository such as description, default branch and visibility.", {"owner": "string", "repo": "string"}),
    ("create_repository", "Create a new repository for the authenticated user or an organization.", {"name": "string", "description": "string", "private": "boolean"}),
    ("fork_repository", "Fork a repository to your account or an organization.", {"owner": "string", "repo": "string", "organization": "string"}),
    ("list_branches", "List branches in a repository with pagination.", {"owner": "string", "repo": "string", "page": "integer"}),
    ("create_branch", "Create a new branch from an existing branch or commit.", {"owner": "string", "repo": "string", "branch": "string", "from_branch": "string"}),
    ("list_commits", "List commits of a branch, optionally filtered by author or path.", {"owner": "string", "repo": "string", "sha": "string", "author": "string"}),
    ("get_commit", "Get a single commit including the diff and changed files.", {"owner": "string", "repo": "string", "sha": "string"}),
    ("get_file_contents", "Get the contents of a file or directory from a repository at a given ref.", {"owner": "string", "repo": "string", "path": "string", "ref": "string"}),
    ("create_or_update_file", "Create or update a single file in a repository with a commit message.", {"owner": "string", "repo": "string", "path": "string", "content": "string", "message": "string", "branch": "string", "sha": "string"}),
    ("delete_file", "Delete a file from a repository with a commit message.", {"owner": "string", "repo": "string", "path": "string", "message": "string", "branch": "string"}),
    ("push_files", "Push multiple files to a branch in a single commit.", {"owner": "string", "repo": "string", "branch": "string", "files": "array", "message": "string"}),
    ("search_code", "Search code across GitHub repositories using code search syntax.", {"query": "string", "page": "integer", "per_page": "integer"}),
    ("list_issues", "List issues in a repository filtered by state, labels, assignee or date.", {"owner": "string", "repo": "string", "state": "string", "labels": "array", "since": "string"}),
    ("get_issue", "Get the details of a specific issue including body and labels.", {"owner": "string", "repo": "string", "issue_number": "integer"}),
    ("create_issue", "Create a new issue with title, body, labels and assignees.", {"owner": "string", "repo": "string", "title": "string", "body": "string", "labels": "array", "assignees": "array"}),
    ("update_issue", "Update the title, body, state, labels or assignees of an issue.", {"owner": "string", "repo": "string", "issue_number": "integer", "title": "string", "body": "string", "state": "string"}),
    ("add_issue_comment", "Add a comment to an issue or pull request.", {"owner": "string", "repo": "string", "issue_number": "integer", "body": "string"}),
    ("list_issue_comments", "List comments on an issue with pagination.", {"owner": "string", "repo": "string", "issue_number": "integer", "page": "integer"}),
    ("search_issues", "Search issues and pull requests across repositories.", {"query": "string", "sort": "string", "order": "string"}),
    ("list_pull_requests", "List pull requests filtered by state, base or head branch.", {"owner": "string", "repo": "string", "state": "string", "base": "string", "head": "string"}),
    ("get_pull_request", "Get details of a pull request including mergeability and reviewers.", {"owner": "string", "repo": "string", "pull_number": "integer"}),
    ("create_pull_request", "Open a new pull request from a head branch into a base branch.", {"owner": "string", "repo": "string", "title": "string", "head": "string", "base": "string", "body": "string", "draft": "boolean"}),
    ("update_pull_request", "Update the title, body, base branch or state of a pull request.", {"owner": "string", "repo": "string", "pull_number": "integer", "title": "string", "body": "string"}),
    ("merge_pull_request", "Merge a pull request using merge, squash or rebase.", {"owner": "string", "repo": "string", "pull_number": "integer", "merge_method": "string"}),
    ("get_pull_request_files", "List files changed in a pull request with patch snippets.", {"owner": "string", "repo": "string", "pull_number": "integer"}),
    ("get_pull_request_diff", "Get the unified diff of a pull request.", {"owner": "string", "repo": "string", "pull_number": "integer"}),
    ("create_pull_request_review", "Create a review on a pull request with comments and a verdict.", {"owner": "string", "repo": "string", "pull_number": "integer", "body": "string", "event": "string", "comments": "array"}),
    ("request_reviewers", "Request reviewers for a pull request.", {"owner": "string", "repo": "string", "pull_number": "integer", "reviewers": "array"}),
    ("list_releases", "List releases of a repository.", {"owner": "string", "repo": "string", "page": "integer"}),
    ("get_latest_release", "Get the latest published release of a repository.", {"owner": "string", "repo": "string"}),
    ("list_tags", "List git tags of a repository.", {"owner": "string", "repo": "string"}),
    ("list_workflows", "List GitHub Actions workflows defined in a repository.", {"owner": "string", "repo": "string"}),
    ("run_workflow", "Trigger a workflow_dispatch run of a GitHub Actions workflow.", {"owner": "string", "repo": "string", "workflow_id": "string", "ref": "string", "inputs": "object"}),
    ("get_workflow_run", "Get the status and conclusion of a workflow run.", {"owner": "string", "repo": "string", "run_id": "integer"}),
    ("get_job_logs", "Download logs of jobs in a workflow run, optionally only failed jobs.", {"owner": "string", "repo": "string", "run_id": "integer", "failed_only": "boolean"}),
    ("list_notifications", "List notifications for the authenticated user.", {"all": "boolean", "participating": "boolean", "since": "string"}),
    ("list_code_scanning_alerts", "List code scanning alerts of a repository by state and severity.", {"owner": "string", "repo": "string", "state": "string", "severity": "string"}),
    ("list_secret_scanning_alerts", "List secret scanning alerts detected in a repository.", {"owner": "string", "repo": "string", "state": "string"}),
]


def cells():
    # Indent 8 spaces, matching the other lines inside code(f"""..."""), so it lines up after dedent
    mcp_literal = "[\n" + "\n".join(f"            {t!r}," for t in MCP_TOOLS) + "\n        ]"
    return [
        md(f"""
        # 1-B: Agent, where the AI decides the route; tools and MCP

        {badge(NAME)}

        > 📍 **Matching slides**: Session 1, "Stop 3: Agent 1-B", slides **30–39**; the core-loop exercise is appendix slide **47** (class time 1:10–1:40)

        ## What this notebook does

        In the helper from 1-A, the steps, branches and stopping conditions were all arranged by the program (a workflow). This notebook takes a different approach: **no flow diagram, just a toolbox for the AI**.
        You tell it which tools exist and what the goal is, and let it decide which to use first and how many times. This approach is called an **agent**:

        > **Agent = model + tools + loop**: ask the model -> it says which tool it wants, and your program runs it and pastes the result back -> ask the model again -> until it says "no more tools".
        > The model itself does not run code; it only "says" which tool it wants, and your program does the real work (details in 1-0).

        The toolbox has three tools we wrote ourselves (Part 6 also connects two read-only tools from an MCP server):

        | Tool | What it does |
        | --- | --- |
        | `run_code` | Runs the homework under teaching limits and returns the output or the error |
        | `check_indent` | Checks indentation and the length of each line (deliberately does not check naming, which is left for Session 2) |
        | `read_spec` | Reads the assignment requirements for this problem |

        | Part | What you will do | Matching slides |
        | --- | --- | --- |
        | Part 1 | Prepare the three tools, and test run_code's limits and error messages | 31–32 |
        | Part 2 | Look at the tool descriptions the model receives | 33 |
        | Part 3 | Build a local agent and watch its tool-call record | 34, 35 |
        | Part 4 | Run three times and compare, then adjust the system prompt | 36 |
        | Part 5 | Tell apart stopping by itself, hitting the step limit, and success | 37–38 |
        | Part 6 (instructor demo) | Connect MCP tools; the tool-description length comparison is optional reading | 39 |
        | Part 7 (optional after class) | Rebuild the core loop with LangGraph | 47 |

        ## How to use it

        1. First run **"0. Environment setup"**.
        2. The only things you change are form fields: **homework**, **spec** (the assignment requirements, in Part 3), and **system prompt extra** (the sentence added to the system prompt, in Part 4).
        3. Every part: **🤔 write your prediction first → ▶ run → 👀 compare**. For the core, do Parts 1–5 in order; follow the instructor for Part 6, and Part 7 is optional after class.
        4. If the runtime has been reset (not just a browser disconnect), rerun "0. Environment setup" first. It also writes the tools and `agent.py` back; then return to the part you want. The file-writing cells only need to be run, not read line by line.
        """),
        project_intro("A helper (agent) that lets the AI decide how to review: no flow diagram, just a toolbox "
                      "(run the homework, check indentation, read the assignment, plus a \"homework repo\" connected through an MCP socket), so you can watch it pick tools and see what can go wrong."),
        setup(NAME, support=["tools/__init__.py", "tools/run_code.py", "tools/check_indent.py", "tools/read_spec.py",
                           "agent.py", "spec.md"],
              packages=["mcp>=1.20,<2", "langchain-mcp-adapters>=0.3,<0.4"]),
        *my_homework(),
        md("""
        ---
        ## Part 1: The toolbox, and run_code's guardrails

        > 📍 **Matching slides**: slide 31 "A different approach: no flow diagram, just a toolbox", slide 32 "Try the tools first, then hand them to the agent"

        First, prepare the agent's toolbox.

        The next three cells write out three tools (no changes needed, just run them). Each tool is an ordinary Python function
        with one `@tool` line on top, and once you add it to the agent's tool list, the model can ask to use it.

        `run_code` is a tool that **really runs code**, and anything can be in a student's homework, so first look at two execution limits and one design that makes things easier to read:
        1. Before running, it checks the allowed syntax and modules, and blocks the dangerous operations tested in this session
        2. A time limit (timeout): it is force-stopped after 3 seconds, so even an infinite loop stops
        3. It shrinks an error message to a single line so people and the model can read it easily; this is not a safety limit

        ### 🤔 Prediction questions
        Below, four homeworks are passed to `run_code`: a normal one, one with a mistyped variable, one that sneaks in `import os`, and one with an infinite loop. What result will each get?
        """),
        writefile("tools/run_code.py"),
        writefile("tools/check_indent.py"),
        writefile("tools/read_spec.py"),
        code("""
        #@title ▶ Run: try run_code's limits and error messages
        {PREAMBLE}
        from tools.run_code import run_code

        four_homeworks = {
            "Normal homework": "print(sum([1, 2, 3]))",
            "Mistyped variable": "total = 1 + 2\\nprint(totla)",
            "Sneaky import os": "import os\\nos.remove('important_file.txt')",
            "Infinite loop": "while True:\\n    pass",
        }
        results = {}
        for name, homework in four_homeworks.items():
            results[name] = run_code.invoke({"code": homework})
            print(f"[{name}]\\n{homework}\\n-> {results[name]}\\n")
        record("1-B Part 1: run_code guardrails", results)
        """),
        md("""
        ### 👀 What did you see?

        - The normal homework prints `6`; the mistyped variable returns just one line like "Line 2 NameError...", not a long traceback.
        - `import os` is blocked **before** running, and not a single file was touched; the infinite loop is force-stopped after 3 seconds.
        - Running outside code needs isolation and permission limits: the model can be influenced by its input and may ask `run_code` to do something inappropriate (Session 2's 2-C comes back to this).
          The guardrails here are a simplified teaching version and not a complete sandbox. A real product needs a real sandbox (containers, e2b, Modal, and so on).
        """),
        md("""
        ---
        ## Part 2: What tool information does the model get?

        > 📍 **Matching slides**: slide 33 "What a tool interface tells the model"

        The last part wrote three tools. A tool interface doesn't automatically send the function's implementation; so how does the model know what each tool can do?

        `@tool` wraps the function name, the parameters, and the explanation in triple quotes at the top of the function (called the docstring) into a **description** and hands it to the model.
        The model consults that description, the task and the conversation to decide whether to ask for a tool.

        ### 🤔 Prediction questions
        Can the model see the code inside `run_code` that forbids `import os`? How does it know `read_spec` is for reading the assignment?
        """),
        code("""
        #@title ▶ Run: print the descriptions of the three tools
        {PREAMBLE}
        from tools.check_indent import check_indent
        from tools.read_spec import read_spec
        from tools.run_code import run_code

        for t in [run_code, check_indent, read_spec]:
            print("name:", t.name)
            print("description:", t.description)
            print("args:", t.args)
            print("-" * 60)
        """),
        md("""
        ### 👀 What did you see?

        - The tool interface here provides `name`, `description` (the docstring) and `args`; it does not automatically hand the function's implementation to the model.
        - A good docstring says four things: **what it does, when to call it, what the parameters mean, and what it returns**.
          If it only says "run code" and not when to use it, the model may skip it or misuse it.
        - The model cannot see the code that blocks `import os`, but it can see the line in the docstring saying "Limits: only a few standard modules such as math, random and re can be imported...".
        - Skills in Session 2 also have a name and a description, which help the model decide whether to read the full guidance.
        """),
        md(f"""
        ---
        ## Part 3: Build an agent in one line, and see what it picks at each step

        > 📍 **Matching slides**: slide 34 "An agent in one line: create_agent", slide 35 "Reading an agent's execution trace"

        The first two parts prepared the toolbox and its descriptions. This part puts the model and the toolbox together to make an agent, and shows what it picks at each step while reviewing a homework.

        The next cell writes out `agent.py`: its `make_agent` is just the one line `create_agent(model, tools=..., system_prompt=...)`,
        and this session uses that interface:

        - `tools`: the toolbox (three local tools)
        - `system_prompt`: the instruction placed at the very start of the conversation and carried along every time, for example "You are a Python homework helper, and your tone should be gentle"
        - `pretty_trace`: prints out each step of the agent so you can see the tool requests the model proposes and the tool results; it is not the model's internal thinking

        ### 🤔 Prediction questions (write on your worksheet)
        Pick the homework "Variable typo" (`return summ`, but the variable is called `total`), and the assignment is "write an add(a, b)".
        1. Will it use a tool? If so, which one **first**?
        2. How many times in total? Will it use all three? (It may also use none and just reply.)
        """),
        writefile("agent.py"),
        code(f"""
        #@title ▶ Run: the agent made by create_agent, and each of its steps
        homework = "Variable typo"  #@param {HOMEWORK_OPTIONS}
        spec = "{DEFAULT_SPEC}"  #@param {{type:"string"}}
        {{PREAMBLE}}
        import agent

        (BASE / "spec.md").write_text(spec, encoding="utf-8")   # read_spec reads this file
        helper = agent.make_agent(model)
        events = agent.pretty_trace(helper, agent.homework_message(load_homework(homework)))
        print("Order in which tools were used this time:", " -> ".join(agent.tool_sequence(events)) or "(no tools used)")
        record(f"1-B Part 3: create_agent ({{homework}})", events)
        """),
        md("""
        ### 👀 What did you see?

        - Each "node: model" is one model response; "node: tools" is your program running the tool it picked. One back-and-forth is one turn of the loop from 1-0.
        - The `AIMessage` at the last step did not call a tool again, so the loop ended.
        - If there is only one "node: model" and the output ends with "(no tools used)", the model replied without requesting any tool, which is also a valid observation. In that case, any error mentioned in the feedback was the model's guess from reading the code, not something `run_code` actually ran.
        - Compare with your prediction: which did it use first? Was there a tool it never used at all? The next part will show that this order can differ every time.
        - `invoke` gives you only the end result; `stream` (which `pretty_trace` uses) lays out the process.
        """),
        md(f"""
        ---
        ## Part 4: Same homework three times, will the order be the same?

        > 📍 **Matching slides**: slide 36 "Same homework, three runs: same order?"

        The last part watched the agent's route once. If you run the same homework three more times, will the route be the same?

        This is the biggest difference between an agent and a workflow: **the route isn't one you drew, it's one it decides in the moment**.
        This part also lets you change the **system prompt** (the instruction placed at the very start every time) by adding a sentence, and watch how the new instruction affects the order of tools.

        ### 🤔 Prediction questions (two rounds)
        1. First leave "system prompt extra" blank and run. Will the order of tool use be the same across the three runs?
        2. Then change it to **Always read the assignment requirements first** and run. Did the order change this time? Are all three the same now?
        """),
        code(f"""
        #@title ▶ Run: run the same homework three times and compare the order of tool use
        homework = "Variable typo"  #@param {HOMEWORK_OPTIONS}
        system_prompt_extra = ""  #@param ["", "Always read the assignment requirements first", "Always run the homework and look at the result first", "Do not use any tools"] {{allow-input: true}}
        {{PREAMBLE}}
        import agent

        system_prompt = agent.base_system_prompt + system_prompt_extra
        print("system prompt:", system_prompt, "\\n")
        helper = agent.make_agent(model, system_prompt=system_prompt)

        three_runs = []
        for i in range(3):
            result = helper.invoke({{"messages": [{{"role": "user", "content": agent.homework_message(load_homework(homework))}}]}})
            sequence = agent.tool_sequence(result["messages"])
            three_runs.append(sequence)
            print(f"========== Run {{i + 1}} ==========")
            print("Order of tool use:", " -> ".join(sequence) or "(no tools used, went straight to feedback)")
            print(result["messages"][-1].text[:300])
            print()

        print("Same order in all three runs?", "Yes" if all(x == three_runs[0] for x in three_runs) else "No, they differ")
        record(f"1-B Part 4: three runs (extra sentence: {{system_prompt_extra or 'none'}})", {{"tool order in the three runs": three_runs}})
        """),
        md("""
        ### 👀 What did you see?

        - The three runs may be the same or different. First record the actual tool order and any checks that were skipped. The same result now does not mean it will be the same later; if a necessary step is skipped, that is still a problem for the system to handle.
        - After adding "Always read the assignment requirements first", see whether the first step becomes `read_spec`. **Do not treat an instruction as a guarantee of execution**:
          a prompt can influence the choice, but a check that must run should be arranged by the flow, and its result should be verified.
        - So the next thing to work out is: which steps does the flow control, and which are left to AI judgment (Stop 4 on the slides).
        """),
        md("""
        ---
        ## Part 5: It can go in circles: recursion limit

        > 📍 **Matching slides**: slide 37 "If a tool keeps failing, will the agent stop?", slide 38 "Set a limit, then work out why it stopped"

        The last part showed that the agent's route is decided by the model and may change. The worst case is that it keeps going in circles and can't stop by itself.

        The cell below gives the agent a tool `always_fail` that **deliberately always fails**, then tells it "don't stop until it succeeds".
        In the code we set `recursion_limit=25` to limit the number of graph steps. This is not "call tools at most 25 times"; model nodes also use up steps. The model may also stop by itself first.

        ### 🤔 Prediction questions
        Will the model stop by itself, or keep requesting the tool until the limit is reached? Will the number of graph steps, the number of tool requests and the number of tool results be the same?
        """),
        code("""
        #@title ▶ Run: a tool that always fails; watch for stopping by itself or hitting the recursion limit
        {PREAMBLE}
        from langchain.agents import create_agent
        from langchain.tools import tool
        from langgraph.errors import GraphRecursionError

        @tool
        def always_fail() -> str:
            \"\"\"Do something very important. If it fails, try again until it succeeds.\"\"\"
            return "Execution error: RuntimeError: still not working, please try again"

        looping_agent = create_agent(
            model, tools=[always_fail],
            system_prompt="Your task is to call always_fail until it succeeds. No matter how many times it fails, try again. Do not give up, and do not answer in text.",
        )
        tool_call_requests, tool_result_count = 0, 0
        try:
            for step, event in enumerate(looping_agent.stream({"messages": [{"role": "user", "content": "Let's begin."}]},
                                                       config={"recursion_limit": 25}, stream_mode="updates"), start=1):
                for node, update in event.items():
                    for msg in (update or {}).get("messages", []):
                        if getattr(msg, "tool_calls", None):
                            for call in msg.tool_calls:
                                if call["name"] == "always_fail":
                                    tool_call_requests += 1
                                print(f"--- Step {step} | node: {node} ---  model requests -> {call['name']}({call['args']})")
                        elif msg.type == "tool":
                            if getattr(msg, "name", None) == "always_fail":
                                tool_result_count += 1
                            print(f"--- Step {step} | node: {node} ---  [ToolMessage] {msg.text}")
                        else:
                            print(f"--- Step {step} | node: {node} ---  [AIMessage] {msg.text[:80]}")
            print("\\n(This time the model stopped by itself without reaching the limit; the tool still has not succeeded. Record this result.)")
        except GraphRecursionError as e:
            print(f"\\n🛑 GraphRecursionError: {str(e).splitlines()[0]}")
        print(f"always_fail: the model made {tool_call_requests} tool request(s) and received {tool_result_count} tool result(s)")
        record("1-B Part 5: recursion limit", {"tool_call_requests": tool_call_requests, "tool_result_count": tool_result_count})
        """),
        md("""
        ### 👀 What did you see?

        - If the model keeps calling `always_fail`, every round adds to the model-call cost; it may also stop by itself.
        - If it keeps running until the step limit, you get a `GraphRecursionError`. Stopping is not success.
        - Read the **number of tool requests** and the **number of tool results** separately; both count only `always_fail`. After the model proposes its last request, the step limit may be hit before a tool result comes back, so you can't treat the request count as the number of times the tool actually ran.
        - The "at most 5 rounds" in 1-0, the "Maximum generations" in 1-A, and the `recursion_limit` here are all stop limits set in code; the three count different units.
        - Next, see the MCP demo, then go to Stop 4 on the slides to discuss which steps the flow controls and which are left to AI judgment.
        """),
        md("""
        ---
        ## Part 6 (instructor demo): Where tools come from: your own functions vs. MCP sockets

        > 📍 **Matching slides**: slide 39 "Where tools come from: your own functions vs. MCP sockets"

        So far we built the agent from local tools and watched its run and its stopping conditions. Now we widen where tools can come from. **The tool description doesn't have to be written by you**: tools someone else built can also be plugged in through a socket.

        - **Local function**: you write it yourself and it lives in the same program (our three tools).
        - **MCP**: the tools live in **another program or service** (such as GitHub) and are connected through a shared "socket" standard.
          ("Socket" refers to the shared MCP standard; the program that provides the tools is called an MCP server, like the "homework repo" in this part.)
          **MCP is not another kind of agent; it is a way to plug in "tools".**
        - The cost: the more tools you give the model, the longer the tool descriptions usually get. Connecting to MCP does not mean you have to hand every tool to the model.
          (The desk = the context window, the maximum number of tokens the model can handle at once; the more descriptions there are, the less room is left for the homework and the feedback.)

        This part connects to an MCP server that actually runs. The next cell writes out `deploy/homework_mcp.py`: a "homework repo" (the homework and the email in it are all fake data)
        with three tools: `list_homework` (who turned in homework), `get_homework` (fetch one student's homework), and `send_email` (sends mail, but fake: it only writes to `outbox.txt`).
        Open it and you will see that **it's just a few ordinary Python functions with `@mcp.tool()` on top**, running in its own program.

        Then the `langchain-mcp-adapters` package plugs in the socket, we first filter out two read-only tools, and hand them to the agent together with the three local tools.
        (`create_agent` is the function that "puts a model and a toolbox together into an agent", which the local agent above already used.
        The `await` in the code means "wait for this to finish before moving on": MCP tools talk to another program through the socket, so they need `await`, which a Colab cell can use directly.)

        ### 🤔 Prediction questions
        1. How does an agent use a tool that comes in through the socket, compared with your own `@tool`?
        2. If you ask the agent to "look at the homework Chloe turned in and run it to see if there are errors", which tool does it call first? Will it use both an MCP tool and the local `run_code`?
        """),
        writefile("deploy/homework_mcp.py"),
        code("""
        #@title ▶ Run: connect the MCP socket so the agent uses MCP tools and local tools together
        {PREAMBLE}
        from langchain.agents import create_agent
        from langchain_mcp_adapters.client import MultiServerMCPClient
        import agent

        # Socket config: use stdio to start a "homework repo" program next door; the tools live in that program
        mcp_client = MultiServerMCPClient({
            "homework_repo": {"command": sys.executable, "args": [str(BASE / "deploy" / "homework_mcp.py")], "transport": "stdio"},
        })
        mcp_tools = await mcp_client.get_tools()          # In Colab you can write await directly
        mcp_names = {t.name for t in mcp_tools}

        print("Tools the MCP server can provide:", ", ".join(sorted(mcp_names)))

        # Least privilege: this agent only needs to "read" homework, so give it just the two read tools
        read_tools = [t for t in mcp_tools if t.name in {"list_homework", "get_homework"}]
        available_tools = agent.helper_tools + read_tools
        print(f"\\n🧰 Tools actually handed to the agent ({len(available_tools)} in total):")
        for t in available_tools:
            source = "MCP socket (lives in another program)" if t.name in mcp_names else "local function (lives in this program)"
            print(f"  - {t.name:<14} <- {source}")
            print(f"      description: {' '.join(t.description.split())[:70]}")
            print(f"      parameters: {list(t.args)}")

        helper = create_agent(
            model, tools=available_tools,
            system_prompt=agent.base_system_prompt + " The homework students turned in is in the homework repo; use get_homework to get the code.",
        )
        question = "Look at the homework Chloe turned in and run it to see if there are errors."
        print(f"\\nUSER: {question}\\n")
        sequence, step = [], 0
        # MCP tools can only be called asynchronously, so this uses astream (not the stream used earlier in 1-B)
        async for event in helper.astream({"messages": [{"role": "user", "content": question}]}, stream_mode="updates"):
            for node, update in event.items():
                step += 1
                for msg in (update or {}).get("messages", []):
                    if getattr(msg, "tool_calls", None):
                        for c in msg.tool_calls:
                            sequence.append(c["name"])
                            source = "MCP socket" if c["name"] in mcp_names else "local function"
                            print(f"--- Step {step} | node: {node} ---  model decided to call -> {c['name']}({c['args']})  <- {source}")
                    elif msg.type == "tool":
                        print(f"--- Step {step} | node: {node} ---  [result of {msg.name}] {msg.text[:200]}")
                    else:
                        print(f"--- Step {step} | node: {node} ---  [AIMessage] {msg.text[:300]}")
        print("\\nOrder of tool use this time:", " -> ".join(sequence) or "(no tools used)")
        record("1-B Part 6: connect the MCP socket", {"MCP tools the server provides": sorted(mcp_names),
                                            "tools handed to the agent": [t.name for t in available_tools], "order of tool use": sequence})
        """),
        md("""
        ### 👀 What did you see?

        - The output first lists the **three MCP tools the server can provide**, then the **five tools actually handed to the agent**: the three local tools plus two MCP read-only tools. The basic interface of the tools is the same: each has a name, a description and parameters.
        - The difference is **where the tool lives**: the place where `get_homework` really runs is the "homework repo" program next door, not this notebook.
          Other MCP servers can be local or remote; how you authenticate depends on the service, and MCP does not get permissions for you automatically.
        - Check the actual record: did it first use the MCP `get_homework` to get the homework, and then the local `run_code` to run it? This example lets you observe **tools from two sources mixed in the same loop**.
        - The homework-repo MCP server has `send_email`, but we **deliberately did not hand it to this agent**: reading homework doesn't need sending email, and sent email can't be taken back. Giving only the tools and permissions needed to finish the task is called least privilege (2-C in Session 2 covers it again).
        - Here we connect over stdio: the homework repo runs on this same Colab machine. A remote MCP can connect through a network endpoint, and Exercise 1 in 2-E turns the same server into a URL and connects it again.
        """),
        md("""
        ### 🤔 Prediction questions (usage comparison, optional reading)
        About how many tokens do the descriptions of the three local tools take? And the 2 MCP read-only tools actually handed to the agent? If we swap in the teaching list below, which imitates GitHub's tool scale, how much would the estimated length differ?
        """),
        code(f"""
        #@title ▶ Run: local tools vs. MCP socket, how many tokens the descriptions take
        {{PREAMBLE}}
        import json
        from langchain_core.utils.function_calling import convert_to_openai_tool
        from langchain_mcp_adapters.client import MultiServerMCPClient
        import agent

        mcp_client = MultiServerMCPClient({{
            "homework_repo": {{"command": sys.executable, "args": [str(BASE / "deploy" / "homework_mcp.py")], "transport": "stdio"}},
        }})
        mcp_tools = await mcp_client.get_tools()
        # Count only the two read-only tools really handed to the agent; send_email was not handed over, so it takes no input
        read_tools = [t for t in mcp_tools if t.name in {{"list_homework", "get_homework"}}]

        # Illustration only: a tool list at the scale of the GitHub MCP server (names and descriptions are rewritten for teaching, not the official text)
        github_scale_tools = {mcp_literal}

        def to_tool_spec(name, desc, params):
            props = {{k: {{"type": v, "description": k}} for k, v in params.items()}}
            return {{"type": "function", "function": {{"name": name, "description": desc,
                    "parameters": {{"type": "object", "properties": props, "required": list(params)[:2]}}}}}}

        def estimate_tool_spec(specs):
            return estimate_tokens(json.dumps(specs, ensure_ascii=False))

        groups = [
            ("Local tools (our own)", [convert_to_openai_tool(t) for t in agent.helper_tools]),
            ("Homework repo MCP (handed to agent)", [convert_to_openai_tool(t) for t in read_tools]),
            ("GitHub-scale MCP (illustration)", [to_tool_spec(*t) for t in github_scale_tools]),
        ]
        results = {{}}
        for name, specs in groups:
            results[name] = estimate_tool_spec(specs)
            print(f"{{name:<38}} {{len(specs):>3}} tools: about {{results[name]:>5,}} tokens  " + "█" * max(1, results[name] // 100))
        local = results["Local tools (our own)"]
        large = results["GitHub-scale MCP (illustration)"]
        print(f"\\nIf you handed this whole GitHub-scale list to the model, one call would carry about {{large:,}} tokens of tool descriptions, {{large / local:.1f}} times the local tools.")
        print("(The token counts are estimated from text length; only the relative sizes matter.)")
        record("1-B Part 6: tokens of MCP tool descriptions", results)
        """),
        md("""
        ### 👀 What did you see?

        - The homework-repo server has 3 tools, but only 2 were handed to the agent, so only those 2 descriptions are counted; this illustration list has 40, and its descriptions are clearly longer. The real cost depends on which tools you choose, the model's format and its tokenizer, so here we only look at the relative sizes of the estimates.
        - To an agent, local tools and MCP tools are used the same way; the differences are where the tool lives, how it is authenticated, and how much of the desk its descriptions take up.
        - Session 2 uses **Skills** to load task guidance on demand. A Skill does not automatically remove tool definitions; to shorten the tool list, your program still has to filter it or provide tools later.
        """),
        md("""
        ---
        ## Part 7 (optional after class): Read the agent's core loop with LangGraph

        > 📍 **Matching slides**: slide 47 "Optional appendix: the core model-and-tool loop"

        The core exercises already used `create_agent`. This part instead uses LangGraph to demonstrate the "model <-> tool" loop; it is not a full implementation of `create_agent`, and you can read it after class.

        It reuses the three components from 1-A: **State** holds the messages, **Node** does the work, **Edge** connects to the next step; a conditional edge picks the route based on tool requests:
        a node that asks the model, `ask_model`; a node that runs the tools, `tools`; and an if for "is a tool wanted?" (`tools_condition`), looped into a circle.
        The code is `make_expanded_agent` in `agent.py`.

        | Component | What it does |
        | --- | --- |
        | `@tool` | Turns a function into a tool the model can see |
        | `bind_tools` | Attaches the tool descriptions to every call |
        | `ask_model` | Asks the model; it returns text or tool_calls |
        | `ToolNode` | Reads tool_calls, runs them, and wraps the results |
        | `tools_condition` | Built-in routing: with tool_calls -> tools, without -> END |
        | `add_edge("tools", "ask_model")` | After the tool runs, go back and ask the model, forming the cycle |

        ### 🤔 Prediction questions
        How many nodes will the flow diagram have? Which edge is the conditional edge?
        """),
        code(f"""
        #@title ▶ Run: build the core loop yourself with LangGraph
        homework = "Variable typo"  #@param {HOMEWORK_OPTIONS}
        {{PREAMBLE}}
        import agent

        expanded = agent.make_expanded_agent(model)
        show_graph(expanded)
        events = agent.pretty_trace(expanded, agent.homework_message(load_homework(homework)))
        record(f"1-B Part 7: expanded agent ({{homework}})", events)
        """),
        md("""
        ### 👀 What did you see?

        - Not counting START/END, there are two working nodes: `ask_model` and `tools`. The edge out of `ask_model` is the conditional edge (dashed): if a tool is wanted, go to `tools`; if not, end.
        - After `tools` finishes it always returns to `ask_model`, and that backward-pointing arrow is the loop.
        - This session builds agents with LangChain's `create_agent`; what it runs on underneath is LangGraph.
        """),
        md("""
        ---
        ## Wrapping up Session 1

        - **Agent = model + tools + loop**; the model only "says" which tool it wants, and your program does the work.
        - **The flow arranges the steps that cannot be skipped, and the agent handles the parts that need flexible judgment**; the two can be nested (a fixed flow outside, with an agent inside one station). That is "Combining workflow and agent: an agent inside a node" on slide 42, and it is what "dual-core" in the course name means (you will build it in 2-D in Session 2).
        - 📝 **Homework after class**: put a homework you wrote yourself into "My homework", run it once in 1-A and once in 1-B,
          take a screenshot of the State history from 1-A and the tool-call record from 1-B, and write one sentence on which result you trust more and why.
          When you use "My homework", first change the "spec" in Part 3 to the assignment for your own homework; Parts 4 and 7 reuse the same spec, and rerunning "0. Environment setup" resets it to the default.
        """),
        *ending(),
    ]
