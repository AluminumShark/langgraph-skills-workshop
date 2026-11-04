from nbbuild import badge, code, ending, md, project_intro, setup, writefile

NAME = "2-E_deploy"
MCP_PACKAGES = ["mcp>=1.20,<2", "langchain-mcp-adapters>=0.3,<0.4"]
SUPPORT = [
    "tools/__init__.py", "tools/run_code.py", "tools/check_naming.py",
    "graph.py", "skill_loader.py", "spec.md", "deploy/__init__.py",
    "deploy/homework_mcp.py", "deploy/multi_agent.py",
    "skills/friendly-feedback/SKILL.md", "skills/strict-review/SKILL.md",
    "skills/naming-check/SKILL.md", "skills/naming-check/scripts/check_naming.py",
]
SEND_OPTIONS = '["Send only verified", "Send all", "Send none"]'


def cells():
    return [
        md(f"""
        # 2-E (optional after class): Run the whole division-of-labor diagram in Colab, then see how it goes to the cloud

        {badge(NAME)}

        > 📍 **Matching slides**: Session 2, Stop 4, slide **37** "The Homework Helper's full division of labor", slide **48** "The division of labor in the cloud: where each box lives", and "Supplementary: moving to the cloud", slides **47-55** (self-study after class)
        """),
        project_intro("Run a simplified version of Session 2's division-of-labor diagram once (MCP, workflow, reviewer agent, verifying agent, human confirmation; this version has no assignment attachment and no read_spec), then see where each piece lives once it goes to the cloud."),
        md("""
        ## What this notebook does

        At the end of Session 2, we imagined upgrading the Homework Helper: fetch 200 homework submissions from GitHub, review them all at once, and send the emails automatically.
        We split that into a **division-of-labor diagram**, sorted from two angles: "who decides when it runs" and "how the ability is provided". One feature can use several kinds of components at the same time:

        | Role | Plain meaning | Example in this notebook |
        | --- | --- | --- |
        | Code (workflow) | Order and checks controlled by the workflow | Always check syntax first; always stop and wait for a person before sending email |
        | Tool | A Python function the AI can call | `check_naming` (checks naming), `run_code` (runs the homework) |
        | MCP | A standard socket for plugging in "tools that live in another program or service" | The homework repo: fetch homework, send email |
        | Handbook (Skill) | A work handbook for the AI to read | `friendly-feedback` (friendly feedback) |
        | Reviewer agent and verifying agent | The reviewer agent is one configuration run once per submission with that submission's own input (batching, not opening more roles), each on a clean "desk" (its own conversation history); the verifying agent is a second role whose job is separate: it only checks and never writes | The reviewer agent (= the feedback agent on slide 37) uses `friendly-feedback`; the verifying agent is called the "auditor" in the code |

        In class we only drew the diagram. This notebook **actually runs it once**, entirely inside free Colab:

        | Exercise | What you'll do | Matching slides |
        | --- | --- | --- |
        | Exercise 1 | Start a **real MCP server**, the "homework repo": connect to it through a local socket first, then turn it into a URL (remote MCP) | 48, 52 |
        | Exercise 2 | ⭐ **Review one first, then run the whole batch**: MCP fetches the homework → Send dispatches each submission → each one gets a syntax check first, and only those that pass go on to the review and the verification agent → stop and wait for a person to confirm before sending → MCP sends the emails | 31, 34-37, 48, 53-54 |
        | Exercise 3 | Wrap it as an **API service**: start a review by URL, confirm the sending by URL; the thread_id is kept across requests | 48, 49, 51, 54 |
        | Exercise 4 | **Pre-launch checks**, and generate the deployment files (`Dockerfile`, `langgraph.json`) | 49-50, 55 |

        **This notebook does not deploy anything to the cloud** (that needs a cloud account and a credit card). The MCP server and the API service run on this one Colab machine,
        and the emails are fake; they are only written to `/content/review-bot/outbox.txt`.

        ## Deployment map: where each thing lives once it goes to the cloud

        | Thing | In this notebook | Where it lives in the cloud | Exercise |
        | --- | --- | --- | --- |
        | Outer workflow, reviewer agent, verifying agent, local tools (`check_naming`, `run_code`) | Python in Colab | **Your container** (Cloud Run or LangSmith Deployment): a self-built container uses the `server.py` API (`POST /batch`); a managed platform uses its built-in threads / runs API instead | 2, 3 |
        | `skills/`, `scripts/` | `/content/review-bot/` | **Shipped with the container**: changing a handbook = releasing a new version | 4 |
        | Homework repo, sending email (MCP) | Another program on the same machine | **Someone else's service**: a remote MCP connects through a URL, with authorization set up by that service | 1 |
        | Each thread_id's State, and emails waiting for confirmation | A SQLite file | **A database** (Postgres), which survives when the machine is replaced | 2, 3 |
        | Model API key | Colab 🔑 Secrets (or none needed) | **A vault** (Secret Manager), exposed as an environment variable | 4 |
        | How many to review at once, Trace / Eval | `max_concurrency`, the printed usage | A **task queue**, a **monitoring dashboard** | 2, 4 |

        In one sentence: **code, handbooks and scripts travel with the container; data that changes goes into a database; keys go into a vault; other people's abilities are connected over the network.**

        The terms in the table: **container** = put a program and everything it needs into one box that runs on any machine; **Cloud Run, LangSmith Deployment** = services that run your program in the cloud;
        **Postgres** = a kind of database; **Secret Manager** = a password vault in the cloud; **task queue** = lets jobs wait in line when there is too much work;
        **Trace / Eval** = a record of what each step did / automatic tests that give a score.

        **When reading the results:** "verified" means the feedback passed the check; it does not mean the student's homework is correct. A homework with a syntax error gets an error notice produced directly by code, which can also be listed as feedback that is ready to send.
        2-E always uses the default friendly handbook and verifies the feedback after reviewing; only 2-D demonstrates picking a handbook and a full format redo.

        ## How to use it

        1. Run **"0. Setup"** first (it installs MCP and FastAPI as well, and prepares the tools and handbooks from the earlier notebooks).
        2. We suggest doing Exercise 1's stdio first, then Exercise 2 with one submission and the human confirmation; choose the whole batch only after you can explain the result and the confirmation step. Leave HTTP, the API and the deployment files for a second pass.
        3. The number of model calls changes with the number of submissions, tool use and rewrites; watch the usage with one submission first. Setup uses fresh default handbooks and does not carry over changes from earlier notebooks.
        4. Re-running setup and the `%%writefile` prepare cells overwrites the default files in them, so keep your changes first; the SQLite checkpoint and the fake outbox are not cleared by that. After the environment is rebuilt, prepare the files and services again.
        5. This notebook uses `await`: a Colab cell can use `await` directly. Don't worry about it; just press ▶ as usual.
        """),
        setup(NAME, support=SUPPORT, packages=["fastapi>=0.115", "uvicorn>=0.30", *MCP_PACKAGES]),
        md("""
        ---
        ## Exercise 1: Start a real MCP server

        > 📍 **Matching slides**: slide 48 (deployment map), 52 (remote MCP); Session 1 slide 39 (MCP sockets)

        First build the "someone else's service" box from the diagram. An MCP tool lives in **another program**. The next cell writes `deploy/homework_mcp.py`: it is an ordinary Python file,
        and the `@mcp.tool()` on top of three functions turns them into tools that can be plugged in through the socket:

        This exercise's data source is a Python dictionary in `homework_mcp.py`, with fake mailboxes and homework code for **5 students** already filled in; it does not read any student repo on GitHub yet.
        The MCP server and the connection are real, but the data source and the email sending are simulated.

        | Tool | What this exercise does | When connecting a real service |
        | --- | --- | --- |
        | `list_homework`, `get_homework` | Take the roster and code from the default dictionary | Connect to the GitHub API, or adapt a compatible MCP tool |
        | `send_email` | Only writes into a simulated outbox | Connect a real email service |

        These are tool names defined for this course; you can't just swap the URL for any GitHub MCP server and expect it to work. The tool names, parameters and return format must match too.

        Two ways to connect: **stdio** is a local socket (the agent side starts the server as a child process); **Streamable HTTP** is a URL.
        That is how a remote MCP works, except that a real service may use **OAuth** sign-in or another kind of authorization (the standard way of signing in with an account and exchanging it for a pass).

        ### 🤔 Prediction questions
        1. Once connected, how does an MCP tool look different from the `@tool` you wrote yourself in 1-B?
        2. When you connect by URL instead, will the tool names and usage change?
        """),
        writefile("deploy/homework_mcp.py"),
        code("""
        #@title ▶ Run: connect to the homework repo through a local socket (stdio)
        {PREAMBLE}
        import json
        from langchain_core.utils.function_calling import convert_to_openai_tool
        from deploy import multi_agent

        config = multi_agent.homework_repo_config()          # stdio: this side starts homework_mcp.py as another program
        mcp_tools = await multi_agent.get_mcp_tools(config)
        for t in mcp_tools.values():
            print(f"🔌 {t.name} (parameters: {list(t.args) or 'none'}): {t.description.splitlines()[0]}")

        roster = json.loads(multi_agent.result_text(await mcp_tools["list_homework"].ainvoke({})))
        print("\\nlist_homework →", ", ".join(a["student"] for a in roster))
        print("\\nget_homework(student='Chloe') →")
        print(multi_agent.result_text(await mcp_tools["get_homework"].ainvoke({"student": "Chloe"})))

        tool_spec_tokens = estimate_tokens(json.dumps([convert_to_openai_tool(t) for t in mcp_tools.values()], ensure_ascii=False))
        print(f"The tool descriptions of these {len(mcp_tools)} MCP tools add up to about {tool_spec_tokens} tokens (estimate)")
        record("2-E Exercise 1: connected to the homework repo over stdio", {"tools": list(mcp_tools), "students": [a["student"] for a in roster], "tool_spec_tokens": tool_spec_tokens})
        """),
        code("""
        #@title ▶ Optional: turn the same server into a URL (Streamable HTTP, like a remote MCP)
        {PREAMBLE}
        import asyncio, socket, subprocess
        from deploy import multi_agent

        old_process = getattr(sys, "_homework_repo_process", None)       # on a re-run, shut down the one started last time
        if old_process:
            old_process.terminate()
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        log_file = open(BASE / "deploy" / "homework_mcp.log", "w")
        sys._homework_repo_process = subprocess.Popen([sys.executable, str(multi_agent.MCP_SERVER), "--http", str(port)],
                                                      stdout=log_file, stderr=log_file)
        url = f"http://127.0.0.1:{port}/mcp"
        for _ in range(60):
            try:
                mcp_tools = await multi_agent.get_mcp_tools(multi_agent.homework_repo_config(url))
                break
            except Exception:
                await asyncio.sleep(0.5)
        else:
            raise SystemExit("⚠️ The MCP server did not start. Check /content/review-bot/deploy/homework_mcp.log")

        (BASE / "deploy" / ".mcp_port").write_text(str(port))
        print(f"🌐 The homework repo MCP is now a URL: {url}")
        print("Tools connected by URL:", ", ".join(mcp_tools))
        print("\\nget_homework(student='Jay') →")
        print(multi_agent.result_text(await mcp_tools["get_homework"].ainvoke({"student": "Jay"})))
        record("2-E Exercise 1: connected to the homework repo by URL", {"url": url, "tools": list(mcp_tools)})
        """),
        md("""
        ### 👀 What did you see?

        - An MCP tool also has a name, a description and parameters. **Once connected as a tool, the model still proposes calls from the name, description and parameters**; at run time there is also a connection to another program and error handling to think about.
          (This Python adapter example waits for the tool's return with `await ...ainvoke()`; that is not how every MCP client is written.)
        - Connected by URL, the tools are exactly the same. In the cloud, the homework repo is just a URL on someone else's service: your program doesn't need to know how it was written or in what language.
        - MCP provides a list of tools; the application decides which tools to offer the model. A Skill can describe how to use them, but it does not shrink the tool definitions or revoke permissions automatically. In this flow the code calls MCP directly, and the reviewer agent gets only the naming-check and run-code tools.
        - **Completion check**: find the tool names and Chloe's homework in the stdio output. Once you can explain "another program provides the tools", try the URL connection as an option; you don't need to understand network deployment first.
        """),
        md("""
        ---
        ## Exercise 2 ⭐: Run the whole division-of-labor diagram once

        > 📍 **Matching slides**: slide 31 "Feature 1: fetching homework from GitHub", 34 "Reviewing 200 submissions: independent first, then parallel", 35 "Verifying feedback: rules first, then independent judgment", 36 "Before sending email, make the flow wait for confirmation", 37 "The Homework Helper's full division of labor", 48 "The division of labor in the cloud: where each box lives", 53 "Reviewing 200 at once: Send", 54 "Waiting for confirmation before sending: interrupt"

        Exercise 1 started the homework repo, and this exercise uses it to run a simplified version of the diagram once. The next cell writes `deploy/multi_agent.py`; this version has no assignment attachment and no `read_spec`:

        | Box in the diagram | Role | In the code |
        | --- | --- | --- |
        | Fetch homework from the homework repo | MCP (called by the **code**, no judgment needed) | The `fetch_homework` node calls `list_homework` and `get_homework` |
        | Always check syntax first | Code | On a syntax error it replies directly and **does not call the AI** |
        | Review each submission once | The same reviewer agent (= the feedback agent on slide 37) + Skill + script: batching, not opening more roles | `Send` dispatches each submission to `review_one`; the handbook is `friendly-feedback`, and the tools are `check_naming` and `run_code` |
        | Check the feedback for made-up claims | The verifying agent (a separate checking job, called the "auditor" in the code) + code | Code checks the line numbers first, then the auditor reads the content; a failure is sent back for at most one rewrite; if it still fails, the failed state is kept. The auditor gets only the original homework and the feedback, with **no assignment requirements**, so it cannot judge whether the assignment was misunderstood (slide 35's full design needs the assignment + homework + draft) |
        | Send the email | MCP + human confirmation | `interrupt()` stops, and only after a person decides is `send_email` called; choosing "Send none" ends the run right there |

        Two new pieces of syntax in the table:
        - `Send`: sends each item of a list to the `review_one` node, so they can be handled at the same time. The node checks syntax first and creates a reviewer agent only if it passes.
        - `interrupt()`: when the flow gets here it stops, saves the State, and waits for a person to answer before it continues.

        The flow chart has only four stations (fetch_homework → review_one → confirm_before_send → send_emails); the syntax check, the review and the verification are all written inside the `review_one` node, run once per submission (slide 37 draws them as separate boxes). When you choose "Send none", the flow ends straight from `confirm_before_send` without entering `send_emails`.

        Note "don't pass the work along three people": one submission, from review to fix, is handled by the **same reviewer**; the semantic judgment goes to a separate agent whose only job is to check; independent checking can still miss errors.

        ### 🤔 Prediction questions
        1. First round, Chloe only: predict which node will stop and how you can tell that nothing has been sent yet. Second round, all five: Alex has a syntax error, so how many submissions need the model to review them?
        2. If you change "max_concurrency" from 1 to 3, will it be faster? Will it use fewer tokens?
        3. When Step 1 finishes, has the email been sent?
        """),
        writefile("deploy/multi_agent.py"),
        code("""
        #@title ▶ Run (Step 1): run the whole diagram once, stopping before the email is sent
        thread_id = "midterm-batch-1"  #@param {type:"string"}
        batch_scope = "Just Chloe"  #@param ["Just Chloe", "All five"]
        max_concurrency = 1  #@param {type:"slider", min:1, max:5, step:1}
        homework_repo_transport = "Local socket (stdio)"  #@param ["Local socket (stdio)", "URL (Streamable HTTP; run Exercise 1's second cell first)"]
        {PREAMBLE}
        import time
        from deploy import multi_agent

        url = None
        if homework_repo_transport.startswith("URL"):
            port_file = BASE / "deploy" / ".mcp_port"
            if not port_file.exists():
                raise SystemExit("⚠️ The MCP server was not started by URL yet: run Exercise 1's second cell first, or choose \\"Local socket (stdio)\\"")
            url = f"http://127.0.0.1:{port_file.read_text()}/mcp"

        checkpointer = await multi_agent.open_checkpointer()
        helper = multi_agent.build_multi_agent_helper(model, mcp_config=multi_agent.homework_repo_config(url), checkpointer=checkpointer,
                                                      only_students="Chloe" if batch_scope == "Just Chloe" else None)
        config = {"configurable": {"thread_id": thread_id}, "max_concurrency": max_concurrency}
        if (await helper.aget_state(config)).values:
            await checkpointer.conn.close()
            raise SystemExit(f"⚠️ thread_id \\"{thread_id}\\" has already been used: pick a new one (for example \\"midterm-batch-2\\"), or go straight to Step 2")
        show_graph(helper)

        meter = multi_agent.usage_meter()
        t0 = time.time()
        result = await helper.ainvoke({"results": []}, {**config, "callbacks": [meter]})
        seconds = time.time() - t0
        for r in result["results"]:
            verdict = "✅ passed" if r["verify"]["passed"] else "❌ " + r["verify"]["reason"]
            print(f"[{r['student']}] tools: {', '.join(r['used_tools']) or '(no tool requested; that does not mean the AI was not called)'} | verification: {verdict} | rewritten {r['rewrite_count']} time(s)")
            print("Full feedback:\\n" + r["feedback"])
            print("Verification reason:", r["verify"]["reason"])
        print(f"\\n⏱️ {seconds:.0f} s (up to {max_concurrency} at a time); {meter.count} model call(s), about {meter.input_tokens + meter.output_tokens:,} tokens (estimate)")

        if "__interrupt__" in result:
            print("\\n⏸️  Stopped before sending, waiting for a person to confirm. Emails ready to send:")
            for mail in result["__interrupt__"][0].value["emails_to_send"]:
                print(f"    → {mail['student']} <{mail['email']}> (verification {'passed' if mail['verified'] else 'not passed'})")
                print(mail["feedback"])
        print("Next station in the checkpoint:", (await helper.aget_state(config)).next)
        await checkpointer.conn.close()
        record(f"2-E Exercise 2: the whole diagram (thread_id={thread_id})",
               {"results": [{k: r[k] for k in ("student", "used_tools", "verify", "rewrite_count")} for r in result["results"]],
                "model_calls": meter.count, "tokens": meter.input_tokens + meter.output_tokens, "seconds": round(seconds)})
        """),
        code(f"""
        #@title ▶ Run (Step 2): a person has read it and decides whether to send
        thread_id = "midterm-batch-1"  #@param {{type:"string"}}
        decision = "Send only verified"  #@param {SEND_OPTIONS}
        {{PREAMBLE}}
        from langgraph.types import Command
        from deploy import multi_agent

        checkpointer = await multi_agent.open_checkpointer()
        helper = multi_agent.build_multi_agent_helper(model, checkpointer=checkpointer)
        config = {{"configurable": {{"thread_id": thread_id}}}}
        if (await helper.aget_state(config)).next != ("confirm_before_send",):
            print(f"thread_id \\"{{thread_id}}\\" has no email waiting for confirmation: run Step 1 first, or check whether the thread_id has a typo.")
        else:
            result = await helper.ainvoke(Command(resume=decision), config)   # the resume value is what interrupt() returns
            for entry in result["sent_log"]:
                print("📮", entry)
            outbox = BASE / "outbox.txt"
            if outbox.exists():
                print("\\nLast lines of outbox.txt:")
                print("\\n".join(outbox.read_text(encoding="utf-8").splitlines()[-6:]))
            record(f"2-E Exercise 2: decision \\"{{decision}}\\" (thread_id={{thread_id}})", {{"sent_log": result["sent_log"]}})
        await checkpointer.conn.close()
        """),
        md("""
        ### 👀 What did you see?

        - **First round, done when**: you see Chloe's one piece of feedback, the verification result, the email waiting for confirmation, and the next station. Step 1 only prepares the emails; after you decide in Step 2 with the same thread_id, they are written to the fake outbox.
        - Second round: change the scope to "All five", use the new ID "midterm-batch-2" in both steps, and set max_concurrency to 1. Alex has a syntax error, so the code replies directly; the other four each go through review and verification, and a rewrite is verified again.
        - Third round (optional): use another new ID, keep "All five", change max_concurrency to 3, and record the seconds, model calls and tokens to compare with the second round. **Parallel is not guaranteed to be faster, and the tokens are not guaranteed to be the same**; the model's answers, the number of rewrites, rate limits and system load all affect the result.
        - Each reviewer picks its own tools; the value of the verifying agent is its separate checking job and input, not just a different persona. Passing verification still does not mean the content is absolutely correct; feedback that still fails after a rewrite is still listed, and the default "Send only verified" leaves it out. Alex's syntax reply is produced directly by code and is not handed to the verifying agent; the output says why.
        - To start over, use a new thread_id; an ID that has been used is never cleared. Get to where you can explain "waiting for confirmation → a person decides → sent_log" before you move to the API exercise.
        """),
        md("""
        ---
        ## Exercise 3 (advanced, optional): Wrap it as an API service

        > 📍 **Matching slides**: slide 48 (the API box), 49 "Leaving Colab: three things to replace", 51 "Optional reading: choose a deployment by operational needs", 54 "Waiting for confirmation before sending: interrupt"

        In Exercise 2 you pressed ▶ in a notebook. In the cloud, nobody presses a notebook's ▶: a staff member presses "Start review" and "Confirm sending" on a back-office web page,
        and that page calls your service over **HTTP** (the same set of rules a browser uses to open a web page). This kind of interface, which lets another program ask you to do things through a URL, is called an **API**.

        The next cell writes `deploy/server.py`, which uses FastAPI (a Python package for writing APIs) to open four URLs:

        | URL | What it does |
        | --- | --- |
        | `GET /health` | The cloud platform pings it regularly to check the service is still alive |
        | `POST /batch` | Start a batch: fetch homework, review, verify, stop before sending, and return the emails waiting for confirmation |
        | `POST /batch/{thread_id}/decision` | After a person confirms: send or don't send |
        | `GET /threads/{thread_id}` | Check the progress of a batch |

        ### 🤔 Prediction question
        "Start review" and "Confirm sending" are two different requests, and three days may pass between them. How does the second request know which emails to send?
        """),
        writefile("deploy/server.py"),
        code("""
        #@title ▶ Run: open the helper as an API service inside Colab
        {PREAMBLE}
        import socket, threading, time
        import requests, uvicorn
        from deploy import server

        old_server = getattr(sys, "_helper_server", None)       # when this cell is re-run, shut down the one started last time
        if old_server:
            old_server.should_exit = True
            time.sleep(1)
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        helper_server = uvicorn.Server(uvicorn.Config(server.app, host="127.0.0.1", port=port, log_level="warning"))
        threading.Thread(target=helper_server.run, daemon=True).start()
        sys._helper_server = helper_server
        for _ in range(50):
            try:
                if requests.get(f"http://127.0.0.1:{port}/health", timeout=1).ok:
                    break
            except requests.ConnectionError:
                time.sleep(0.2)
        else:
            raise SystemExit("⚠️ The API did not pass the health check. Read the error above and restart the service.")
        (BASE / "deploy" / ".port").write_text(str(port))
        print(f"✅ The helper API is up: http://127.0.0.1:{port}")
        for url in ["GET  /health", "POST /batch", "POST /batch/{thread_id}/decision", "GET  /threads/{thread_id}"]:
            print("   ", url)
        """),
        code(f"""
        #@title ▶ API Step 1: start a batch, read what is waiting to be sent, and check progress
        thread_id = "API-batch-1"  #@param {{type:"string"}}
        {{PREAMBLE}}
        import json, requests

        port_file = BASE / "deploy" / ".port"
        if not port_file.exists():
            raise SystemExit("⚠️ The service is not running yet: run the previous cell first")
        url = f"http://127.0.0.1:{{port_file.read_text()}}"
        try:
            started = requests.post(f"{{url}}/batch", json={{"thread_id": thread_id, "max_concurrency": 2}}, timeout=900).json()
        except requests.ConnectionError:
            raise SystemExit("⚠️ The service is not running (the runtime may have been restarted): run the previous cell first")

        if started.get("error"):
            raise SystemExit(started["error"] + " To confirm the existing emails, use the same ID in the next cell.")
        to_send = (started.get("pending_confirmation") or {{}}).get("emails_to_send", [])
        print(f"POST /batch → stopped before sending, {{len(to_send)}} email(s) waiting for confirmation:")
        for mail in to_send:
            print(f"    {{mail['student']}} <{{mail['email']}}> verification {{'passed' if mail['verified'] else 'not passed'}}")
            print(mail["feedback"])
        print(f"\\nGET /threads/{{thread_id}} →", json.dumps(requests.get(f"{{url}}/threads/{{thread_id}}", timeout=30).json(), ensure_ascii=False))

        print("Read what is waiting to be sent first, then choose a sending decision in the next cell; nothing has been sent in this cell.")
        record(f"2-E Exercise 3: API start (thread_id={{thread_id}})", started)
        """),
        md("""
        **Pause here**: the last cell only started the review and listed what is waiting to be sent. After you have read it, fill in the same thread_id in the next cell and choose a decision.
        This example still writes only to the fake outbox; it is split into two cells to leave room for a person to actually read and decide.
        """),
        code(f"""
        #@title ▶ API Step 2: after a person has read it, confirm the sending and check progress
        thread_id = "API-batch-1"  #@param {{type:"string"}}
        decision = "Send only verified"  #@param {SEND_OPTIONS}
        {{PREAMBLE}}
        import json, requests

        port_file = BASE / "deploy" / ".port"
        if not port_file.exists():
            raise SystemExit("Start the API service and finish API Step 1 first.")
        url = f"http://127.0.0.1:{{port_file.read_text()}}"
        confirmation = requests.post(f"{{url}}/batch/{{thread_id}}/decision", json={{"decision": decision}}, timeout=300).json()
        print(f"\\nPOST /batch/{{thread_id}}/decision ({{decision}}) →")
        for entry in confirmation.get("sent_log") or [confirmation.get("error")]:
            print("    📮", entry)
        print(f"\\nGET /threads/{{thread_id}} →", json.dumps(requests.get(f"{{url}}/threads/{{thread_id}}", timeout=30).json(), ensure_ascii=False))
        print("GET /threads/not-started-batch →", json.dumps(requests.get(f"{{url}}/threads/not-started-batch", timeout=30).json(), ensure_ascii=False))
        record(f"2-E Exercise 3: API service (thread_id={{thread_id}})", {{"confirmation": confirmation}})
        """),
        md("""
        ### 👀 What did you see?

        - The two requests are tied together by the **thread_id**: the first request runs up to `interrupt()`, saves the State into the checkpoint and answers "pending confirmation", and nothing has been sent yet;
          the second request carries the same thread_id and sends or doesn't send according to the decision. A batch that has not started has no checkpoint to find; an ID that has been used cannot start a review again, so results don't get mixed together.
        - Cloud machines can be replaced at any time, so when you go live the checkpoint must live in a database (Postgres), not in a SQLite file on this machine.
        - In a real launch, `POST /batch` over 200 submissions takes a long time, so it usually becomes "put it in a task queue and answer right away"; platforms like LangSmith Deployment have this built in.
        - `server.py` is the API that really runs on the "own container" path (the `Dockerfile` starts `uvicorn deploy.server:app`). A managed platform instead reads `deploy/app_graph.py:graph`, which `langgraph.json` points to, and uses the platform's built-in threads / runs API; there is no `POST /batch`.
        """),
        md("""
        ---
        ## Exercise 4 (advanced, optional): Pre-launch checks, and generating the deployment files

        > 📍 **Matching slides**: slide 49 (keys go in Secret Manager), 50 (langgraph.json is the packing slip), 55 "After launch: observable and containable"

        The last step: before really going to the cloud, check everything with code, then prepare the files to ship.
        The cells below write the files needed for the cloud (**they only generate files; nothing is packaged or deployed**):

        | File | What it is |
        | --- | --- |
        | `langgraph.json` | The packing slip: tells LangSmith Deployment / `langgraph dev` "the graph is in which variable of which file" |
        | `deploy/app_graph.py` | The entry point the packing slip points to: the model key and the remote MCP URL are read from environment variables |
        | `requirements.txt` | Which packages to install (limited to compatible version ranges; `mcp` and `langchain-mcp-adapters` must be pinned together) |
        | `Dockerfile` | The recipe for putting the code, `skills/` and `scripts/` into one container |
        | `.dockerignore` | What must not go into the container: `.env`, checkpoints, logs |
        | `deploy/preflight.py` | Pre-launch checks: every item is checked by code, not by feel |

        `langgraph.json` reads `.env` (used only on your own computer and kept out of git). This notebook does not generate `.env`; create it yourself when you want to use `langgraph dev`. The template is `review-bot/.env.example` in the repo.

        ### 🤔 Prediction question
        There are 10 pre-launch checks. Which do you guess will be ⚠️ (still to handle before going to the cloud)?
        """),
        writefile("langgraph.json"),
        writefile("deploy/app_graph.py"),
        writefile("requirements.txt"),
        writefile("Dockerfile"),
        writefile(".dockerignore"),
        writefile("deploy/preflight.py"),
        code("""
        #@title ▶ Run: pre-launch checks
        {PREAMBLE}
        from deploy import preflight

        passed = preflight.print_check_results()
        record("2-E Exercise 4: pre-launch checks", [{"result": a, "item": b, "note": c} for a, b, c in preflight.run_checks()])
        """),
        md("""
        ### 👀 What did you see?

        - ✅ only means it passed this example's check: for example, no listed key pattern was matched, a simple scan found none of the listed suspicious words, `run_code` has the execution limits from the class example, the agent has a `recursion_limit`,
          there is an `interrupt` before sending email, there is a separate verifying agent, and the deployment files are all there.
        - ⚠️ marks what still needs handling before the cloud:
          - **Key**: this Gemini deployment example needs a valid API key, kept in Secret Manager (Colab's 🔑 "Secrets" on the left is a small version of it).
          - **checkpointer**: SQLite exists only on this one machine; when going live, switch to PostgresSaver.
          - **MCP**: right now the server is started on the same machine over stdio; across machines you can switch to a remote MCP URL (`HOMEWORK_MCP_URL`), authorized the way that service sets up; OAuth is one such way.
        - To try 2-C again: put the problem handbook `detailed-feedback` into `skills/`, run the check again, and see whether "third-party Skill scan" turns into ❌.

        ### When you really deploy (reference for after class; it costs money, and the commands follow each platform's official documentation)

        ```bash
        # Inside the review-bot/ folder
        # 0. Copy .env.example to .env and fill in your own GOOGLE_API_KEY (.env stays out of git)
        # 1. Get it working locally first (needs pip install "langgraph-cli[inmem]")
        langgraph dev

        # 2a. Your own container: build an image and put it on a service like Cloud Run; inject the key with Secret Manager
        docker build -t review-bot .
        gcloud run deploy review-bot --source . --set-secrets=GOOGLE_API_KEY=review-bot-key:latest

        # 2b. Managed: push this folder to GitHub, and in LangSmith Deployment pick this repo to deploy (it reads langgraph.json)
        ```

        A real deployment also needs the runtime to be managed: **every step visible (trace, eval, cost), and permissions properly limited (least privilege, sandbox, review of Skills, keys, human confirmation).**
        """),
        *ending(),
    ]
