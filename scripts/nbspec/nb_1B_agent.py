from nbbuild import badge, code, ending, md, my_homework, project_intro, setup, writefile

NAME = "1-B_agent"
作業選項 = '["變數打錯字", "正確的程式", "縮排亂掉", "少了右括號", "我的作業"]'
預設題目 = "請寫一個函式 add(a, b)，回傳兩個數字相加的結果，並用 print(add(2, 3)) 印出 5。"

# 示意用的 MCP 工具清單：規模仿 GitHub MCP server（名稱與說明為教學改寫，不是官方原文）
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
    # 縮排 8 格，和 code(f"""...""") 裡的其他行一致，dedent 之後才會對齊
    mcp_literal = "[\n" + "\n".join(f"            {t!r}," for t in MCP_TOOLS) + "\n        ]"
    return [
        md(f"""
        # 1-B：Agent，路線由 AI 決定；tool 與 MCP

        {badge(NAME)}

        > 📍 **對應簡報**：第 1 堂「第三站：Agent 1-B」，投影片 **28–36**；核心迴圈選做在附錄 **44**（課堂時間 1:10–1:40）

        ## 這本 notebook 在做什麼

        1-A 的小助教，每一步的順序都是程式寫死的（workflow）。這本換個做法：**不畫流程圖，只給 AI 一個工具箱**，
        告訴它有哪些工具、目標是什麼，讓它自己決定先用哪個、用幾次。這種做法叫 **agent**：

        > **Agent ＝ 模型 ＋ 工具 ＋ 迴圈**：問模型 → 它說要用哪個工具，你的程式就去執行、把結果貼回去 → 再問模型 → 直到它說「不用工具了」。
        > 模型本身不會執行程式，它只會「說」想用哪個工具；真正做事的是你的程式（細節在 1-0）。

        工具箱裡有三把自己寫的工具（第 6 段還會從 MCP 插座多接幾把）：

        | 工具 | 做什麼 |
        | --- | --- |
        | `run_code` | 在教學限制下執行作業，回傳輸出或錯誤 |
        | `check_indent` | 檢查縮排和每行長度（故意不檢查命名，留給第 2 堂） |
        | `read_spec` | 讀這一題的作業要求 |

        | 段落 | 你會做什麼 | 對應投影片 |
        | --- | --- | --- |
        | 第 1 段 | 執行三個本地工具，觀察限制與錯誤訊息 | 29–30 |
        | 第 2 段 | 查看模型拿到的工具說明書 | 31 |
        | 第 3 段 | 建立本地 agent，觀察工具執行紀錄 | 32、33 |
        | 第 4 段 | 跑三次比較，再調整 system prompt | 34 |
        | 第 5 段 | 區分自行停止、達到步數上限與成功 | 35 |
        | 第 6 段（教師示範） | 接入 MCP 工具；工具說明長度比較選讀 | 36 |
        | 第 7 段（課後選做） | 用 LangGraph 重建核心迴圈 | 44 |

        ## 怎麼用

        1. 先執行 **「0. 環境設定」**。
        2. 要改的只有表單欄位：**作業**、**system prompt 加的一句話**（第 4 段）。
        3. 每一段：**🤔 先寫預測 → ▶ 執行 → 👀 對照**；核心依序完成第 1–5 段；第 6 段跟著教師看，第 7 段課後選做。
        4. 斷線後先重跑環境設定，以及工具與 `agent.py` 的寫檔格，再回到要做的段落。寫檔格只需執行，不必逐行讀。
        """),
        project_intro("讓 AI 自己決定怎麼批改的小助教（agent）：不畫流程圖，只給它一個工具箱"
                      "（執行作業、檢查縮排、讀題目，再加上從 MCP 插座接進來的「作業倉庫」），看它自己選工具，也看它會出什麼狀況。"),
        setup(NAME, support=["tools/__init__.py", "tools/run_code.py", "tools/check_indent.py", "tools/read_spec.py",
                           "agent.py", "spec.md"],
              packages=["mcp>=1.20,<2", "langchain-mcp-adapters>=0.3,<0.4"]),
        *my_homework(),
        md("""
        ---
        ## 第 1 段：工具箱，以及 run_code 的圍欄

        > 📍 **對應簡報**：投影片 29「換個做法：給它一個工具箱」、投影片 30「run_code 要有圍欄」

        先準備 agent 的工具箱。

        下面三格會寫出三把工具（不用改，直接執行）。每把工具都是一個普通的 Python 函式，
        上面加一行 `@tool`，再把它加入 agent 的工具清單，模型便能要求使用它。

        `run_code` 是**真的會執行程式**的工具，而學生作業裡什麼都可能有，所以先看兩個執行限制，以及一個方便閱讀的設計：
        1. 在執行前檢查允許的語法與模組，擋下這堂課測試的危險操作
        2. 設時間上限（timeout）：超過 3 秒就強制停止，無限迴圈也停得下來
        3. 把錯誤訊息縮成一行，方便人與模型讀取；這不是安全限制

        ### 🤔 預測題
        下面會丟四段作業給 `run_code`：正常的、打錯變數的、偷偷 `import os` 的、無限迴圈的。各會得到什麼結果？
        """),
        writefile("tools/run_code.py"),
        writefile("tools/check_indent.py"),
        writefile("tools/read_spec.py"),
        code("""
        #@title ▶ 執行：試試 run_code 的限制與錯誤訊息
        {PREAMBLE}
        from tools.run_code import run_code

        四段作業 = {
            "正常的作業": "print(sum([1, 2, 3]))",
            "打錯變數": "total = 1 + 2\\nprint(totla)",
            "偷偷 import os": "import os\\nos.remove('重要檔案.txt')",
            "無限迴圈": "while True:\\n    pass",
        }
        結果們 = {}
        for 名稱, 作業 in 四段作業.items():
            結果們[名稱] = run_code.invoke({"code": 作業})
            print(f"【{名稱}】\\n{作業}\\n→ {結果們[名稱]}\\n")
        記下("1-B 第 1 段：run_code 的圍欄", 結果們)
        """),
        md("""
        ### 👀 你看到了什麼

        - 正常的作業印出 `6`；打錯變數只回一行「第 2 行 NameError…」，不是一大段 traceback。
        - `import os` 在**執行前**就被擋下，檔案一個都沒動到；無限迴圈 3 秒後被強制停止。
        - 交給 AI 的東西要先關進籠子：模型可能被騙去叫 `run_code` 跑壞東西（第 2 堂 2-C 會回來講這件事）。
          這裡的圍欄是教學用的簡化版，正式產品要用真正的 sandbox（容器、e2b、Modal 等）。
        """),
        md("""
        ---
        ## 第 2 段：模型看不到你的程式碼，只看得到說明書

        > 📍 **對應簡報**：投影片 31「模型看不到你的程式碼，只看得到這幾行」

        上一段寫好了三把工具。可是模型看不到你的程式碼，它怎麼知道每把工具能做什麼？

        `@tool` 會把函式名稱、參數、還有函式開頭三引號裡的那段說明（叫 docstring）包成一份**說明書**交給模型。
        模型會參考這份說明書、任務與對話，決定是否要求使用工具。

        ### 🤔 預測題
        模型看得到 `run_code` 裡面「禁止 import os」那段程式嗎？它怎麼知道 `read_spec` 是拿來讀題目的？
        """),
        code("""
        #@title ▶ 執行：印出三個工具的說明書
        {PREAMBLE}
        from tools.check_indent import check_indent
        from tools.read_spec import read_spec
        from tools.run_code import run_code

        for t in [run_code, check_indent, read_spec]:
            print("name：", t.name)
            print("description：", t.description)
            print("args：", t.args)
            print("-" * 60)
        """),
        md("""
        ### 👀 你看到了什麼

        - 這裡的工具介面提供 `name`、`description`（docstring）和 `args`，不會自動把函式實作交給模型。
        - 好的 docstring 要寫四件事：**做什麼、什麼時候該呼叫、參數是什麼意思、回傳什麼**。
          只寫一句「執行程式」、沒寫什麼時候用，模型可能漏用或誤用它。
        - 第 2 堂的 Skill 也是同一件事：AI 只看手冊的「名片」決定要不要翻開。
        """),
        md(f"""
        ---
        ## 第 3 段：一行做出 agent，看它每一步選了什麼

        > 📍 **對應簡報**：投影片 32「一行做出 agent：create_agent」、投影片 33「看它每一步選了什麼：pretty_trace」

        前兩段準備好了工具箱與說明書。這一段把模型和工具箱組起來，正式做出 agent，看它批改一份作業時每一步選了什麼。

        下一格寫出 `agent.py`：裡面的 `建立_agent` 只有一行 `create_agent(model, tools=..., system_prompt=...)`，
        這堂課使用這個介面：

        - `tools`：工具箱（三把本地工具）
        - `system_prompt`：放在對話最前面、每次都會帶著的那段指示，例如「你是 Python 作業小助教，語氣要溫和」
        - `pretty_trace`：把 agent 的每一步攤開印出來，讓你看到模型提出的工具要求與工具結果；這不是模型內部的思考過程

        ### 🤔 預測題（寫在學習單上）
        作業選「變數打錯字」（`return summ`，但變數叫 `total`），題目要求是「寫一個 add(a, b)」。
        1. 它**第一個**會用哪個工具？
        2. 它總共會用幾次工具？三把工具都會用到嗎？
        """),
        writefile("agent.py"),
        code(f"""
        #@title ▶ 執行：create_agent 做出的 agent，看它每一步
        作業 = "變數打錯字"  #@param {作業選項}
        題目要求 = "{預設題目}"  #@param {{type:"string"}}
        {{PREAMBLE}}
        import agent

        (BASE / "spec.md").write_text(題目要求, encoding="utf-8")   # read_spec 會讀這個檔案
        小助教 = agent.建立_agent(model)
        events = agent.pretty_trace(小助教, agent.作業訊息(取得作業(作業)))
        print("這次用工具的順序：", " → ".join(agent.工具順序(events)) or "（沒有用任何工具）")
        記下(f"1-B 第 3 段：create_agent（{{作業}}）", events)
        """),
        md("""
        ### 👀 你看到了什麼

        - 每一個「節點: model」是一次模型回應；「節點: tools」是你的程式在執行它選的工具。一來一回就是 1-0 那個迴圈轉一圈。
        - 最後一步的 `AIMessage` 沒有再叫工具，迴圈就結束了。
        - 對照你的預測：它先用了哪一個？有沒有哪把工具根本沒用？下一段會看到這個順序每次可能不一樣。
        - `invoke` 只給你終點；`stream`（`pretty_trace` 用的）把過程攤開。
        """),
        md(f"""
        ---
        ## 第 4 段：同一段作業跑三次，順序會一樣嗎？

        > 📍 **對應簡報**：投影片 34「同一段作業跑三次，順序會一樣嗎？」

        上一段看了 agent 走一次的路線。同一段作業再跑三次，路線會一樣嗎？

        這是 agent 和 workflow 最大的差別：**路線不是你畫的，是它當下決定的**。
        這一段也可以改 **system prompt**（每次都放在最前面的那段指示）加一句話，看它會不會比較聽話。

        ### 🤔 預測題（兩輪）
        1. 先讓「system prompt 加一句」保持空白，執行。三次用工具的順序會一樣嗎？
        2. 再把它改成 **一定要先讀題目要求**，執行。這次順序有沒有變？三次都一樣了嗎？
        """),
        code(f"""
        #@title ▶ 執行：同一段作業跑三次，比較用工具的順序
        作業 = "變數打錯字"  #@param {作業選項}
        system_prompt_加一句 = ""  #@param ["", "一定要先讀題目要求", "一定要先執行作業看結果", "不要使用任何工具"] {{allow-input: true}}
        {{PREAMBLE}}
        import agent

        system_prompt = agent.基本_system_prompt + system_prompt_加一句
        print("system prompt：", system_prompt, "\\n")
        小助教 = agent.建立_agent(model, system_prompt=system_prompt)

        三次 = []
        for i in range(3):
            result = 小助教.invoke({{"messages": [{{"role": "user", "content": agent.作業訊息(取得作業(作業))}}]}})
            順序 = agent.工具順序(result["messages"])
            三次.append(順序)
            print(f"========== 第 {{i + 1}} 次 ==========")
            print("用工具的順序：", " → ".join(順序) or "（沒有用任何工具，直接評語）")
            print(result["messages"][-1].text[:300])
            print()

        print("三次順序都一樣嗎？", "是" if all(x == 三次[0] for x in 三次) else "不一樣")
        記下(f"1-B 第 4 段：跑三次（加一句：{{system_prompt_加一句 or '無'}}）", {{"三次的工具順序": 三次}})
        """),
        md("""
        ### 👀 你看到了什麼

        - 三次可能相同，也可能不同；先記錄實際工具順序與漏掉的檢查。結果相同不代表之後都一樣；若漏掉必要步驟，仍是系統需要處理的問題。
        - 加了「一定要先讀題目要求」之後，第一步大多會變成 `read_spec`，但**不保證每次都聽話**：
          prompt 可以影響選擇；必須執行的檢查，應由流程安排，並驗證它的結果。
        - 所以接下來要想清楚：哪些步驟該鎖死在流程裡、哪些可以放手讓 AI 決定（簡報的第四站）。
        """),
        md("""
        ---
        ## 第 5 段：它會繞圈：recursion limit

        > 📍 **對應簡報**：投影片 35「它會繞圈：recursion limit」

        上一段看到 agent 的路線由模型決定，可能改變。最糟的情況是：它一直繞圈，自己停不下來。

        下面這格給 agent 一個**故意永遠失敗**的工具 `always_fail`，再叫它「一定要成功才停」。
        我們在程式裡設 `recursion_limit=25`來限制圖的執行步數；這不是「最多呼叫 25 次工具」，模型節點也會占步數。模型也可能先自行停止。

        ### 🤔 預測題
        模型會自行停止，還是持續呼叫工具直到達上限？步數與工具呼叫次數會相同嗎？
        """),
        code("""
        #@title ▶ 執行：一個永遠失敗的工具，觀察自行停止或達到 recursion limit
        {PREAMBLE}
        from langchain.agents import create_agent
        from langchain.tools import tool
        from langgraph.errors import GraphRecursionError

        @tool
        def always_fail() -> str:
            \"\"\"做一件很重要的事。失敗的話請再試一次，直到成功為止。\"\"\"
            return "執行錯誤：RuntimeError: 還是不行，請再試一次"

        繞圈agent = create_agent(
            model, tools=[always_fail],
            system_prompt="你的任務是呼叫 always_fail 直到它成功為止。不管失敗幾次都要再試，不要放棄，也不要用文字回答。",
        )
        次數 = 0
        try:
            for step, event in enumerate(繞圈agent.stream({"messages": [{"role": "user", "content": "開始吧"}]},
                                                       config={"recursion_limit": 25}, stream_mode="updates"), start=1):
                for node, update in event.items():
                    for msg in (update or {}).get("messages", []):
                        if getattr(msg, "tool_calls", None):
                            次數 += len(msg.tool_calls)
                            print(f"--- 第 {step} 步 | 節點: {node} ---  模型決定呼叫 -> always_fail()")
                        elif msg.type == "tool":
                            print(f"--- 第 {step} 步 | 節點: {node} ---  [ToolMessage] {msg.text}")
                        else:
                            print(f"--- 第 {step} 步 | 節點: {node} ---  [AIMessage] {msg.text[:80]}")
            print("\\n（這次模型自行停止，沒有達到上限；工具仍未成功。請記錄這個結果。）")
        except GraphRecursionError as e:
            print(f"\\n🛑 GraphRecursionError：{str(e).splitlines()[0]}")
        print(f"模型總共呼叫了 always_fail {次數} 次")
        記下("1-B 第 5 段：recursion limit", {"呼叫次數": 次數})
        """),
        md("""
        ### 👀 你看到了什麼

        - 若模型持續叫 `always_fail`，每一圈都會增加模型呼叫成本；也可能自行停止。
        - 持續執行而達到步數上限時，會得到 `GraphRecursionError`。停止不等於任務成功。
        - 1-0 的「最多 5 圈」、1-A 的「回饋最多產生次數」、這裡的 `recursion_limit`，都是在程式中設停止上限；三者計算的單位不同。
        - 接著看 MCP 示範，再到簡報第四站討論：哪些事該這樣鎖死、哪些可以放手。
        """),
        md("""
        ---
        ## 第 6 段（教師示範）：Tool 從哪裡來：自己寫的函式 vs MCP 插座

        > 📍 **對應簡報**：投影片 36「Tool 從哪裡來：自己寫的函式 vs MCP 插座」

        上一段看到：模型只看得到工具的說明書。**說明書不一定是你寫的**：別人做好的工具，也能從插座接進來。

        - **本地函式**：你自己寫、住在同一個程式裡（我們的三把工具）。
        - **MCP**：工具住在**另一個程式或服務**裡（例如 GitHub），透過一個大家共用的「插座」規格接進來。
          **MCP 不是另一種 agent，它是「工具」的外接方式。**
        - 代價：交給模型的工具越多，工具說明書通常也越長。連上 MCP 不代表必須把所有工具都交給模型。
          （桌子＝context window，模型一次能讀的字數上限；說明書越多，留給作業和回饋的空間越少。）

        這一段真的接一個 MCP server。下一格寫出 `deploy/homework_mcp.py`：一個假的「作業倉庫」，
        有三個工具：`list_homework`（誰交了作業）、`get_homework`（拿某位同學的作業）、`send_email`（寄信，假的，只寫進 `寄件匣.txt`）。
        打開看就會發現：**它就是幾個普通的 Python 函式，上面加了 `@mcp.tool()`**，然後在自己的程式裡跑起來。

        接著用 `langchain-mcp-adapters` 這個套件把插座接上，拿到的工具和三把本地工具一起交給 agent。
        （`create_agent` 是「把模型和工具箱組成 agent」的函式，前面的本地 agent 已經用過它。
        程式裡的 `await` 意思是「等這件事做完再往下」：MCP 工具要透過插座和另一個程式溝通，所以要用 `await`，Colab 的格子可以直接寫。）

        ### 🤔 預測題
        1. 從插座接進來的工具，agent 用起來和自己寫的 `@tool` 有什麼不一樣？
        2. 請 agent「看小美交的作業、跑跑看有沒有錯」，它會先叫哪一個工具？會不會同時用到 MCP 的工具和本地的 `run_code`？
        """),
        writefile("deploy/homework_mcp.py"),
        code("""
        #@title ▶ 執行：接上 MCP 插座，讓 agent 同時用 MCP 工具和本地工具
        {PREAMBLE}
        from langchain.agents import create_agent
        from langchain_mcp_adapters.client import MultiServerMCPClient
        import agent

        # 插座設定：用 stdio 在旁邊開一個「作業倉庫」程式，工具住在那個程式裡
        插座 = MultiServerMCPClient({
            "作業倉庫": {"command": sys.executable, "args": [str(BASE / "deploy" / "homework_mcp.py")], "transport": "stdio"},
        })
        mcp工具 = await 插座.get_tools()          # Colab 可以直接寫 await
        mcp名稱 = {t.name for t in mcp工具}

        print("🧰 工具箱裡現在有：")
        for t in agent.小助教的工具 + mcp工具:
            來源 = "MCP 插座（住在另一個程式）" if t.name in mcp名稱 else "本地函式（住在這個程式）"
            print(f"  - {t.name:<14} ← {來源}")
            print(f"      說明：{' '.join(t.description.split())[:70]}")
            print(f"      參數：{list(t.args)}")

        # 最小權限：這個 agent 只需要「讀」作業，所以不把會寄信的 send_email 交給它
        讀作業的工具 = [t for t in mcp工具 if t.name != "send_email"]
        小助教 = create_agent(
            model, tools=agent.小助教的工具 + 讀作業的工具,
            system_prompt=agent.基本_system_prompt + "學生交的作業放在作業倉庫裡，要用 get_homework 拿到程式碼。",
        )
        問題 = "幫我看小美交的作業，跑跑看有沒有錯。"
        print(f"\\nUSER: {問題}\\n")
        順序, 步 = [], 0
        # MCP 的工具只能用 async 呼叫，所以這裡用 astream（不是 1-B 前面的 stream）
        async for event in 小助教.astream({"messages": [{"role": "user", "content": 問題}]}, stream_mode="updates"):
            for 節點, update in event.items():
                步 += 1
                for msg in (update or {}).get("messages", []):
                    if getattr(msg, "tool_calls", None):
                        for c in msg.tool_calls:
                            順序.append(c["name"])
                            來源 = "MCP 插座" if c["name"] in mcp名稱 else "本地函式"
                            print(f"--- 第 {步} 步 | 節點: {節點} ---  模型決定呼叫 -> {c['name']}({c['args']})  ← {來源}")
                    elif msg.type == "tool":
                        print(f"--- 第 {步} 步 | 節點: {節點} ---  [{msg.name} 的結果] {msg.text[:200]}")
                    else:
                        print(f"--- 第 {步} 步 | 節點: {節點} ---  [AIMessage] {msg.text[:300]}")
        print("\\n這次用工具的順序：", " → ".join(順序) or "（沒有用任何工具）")
        記下("1-B 第 6 段：接上 MCP 插座", {"MCP 工具": sorted(mcp名稱), "用工具的順序": 順序})
        """),
        md("""
        ### 👀 你看到了什麼

        - 取得的清單有三把 MCP 工具；實際只交給 agent 兩把讀取工具。它們和 `run_code` 都有相同的基本介面：都有名字、說明書、參數，**都是「我可以呼叫的工具」**。
        - 差別在**工具住在哪裡**：`get_homework` 真正執行的地方是旁邊那個「作業倉庫」程式，不是這個 notebook。
          其他 MCP server 可以在本機或遠端；認證方式依服務而定，MCP 不會自動替你取得權限。
        - 通常 agent 會先用 MCP 的 `get_homework` 拿到程式碼，再用本地的 `run_code` 執行它：**兩種來源的工具混在同一個迴圈裡用**。
        - 插座上有 `send_email`，但我們**故意不把它交給這個 agent**：看作業不需要寄信，寄信又收不回來。工具給越少越安全，這叫最小權限（第 2 堂 2-C 會再講）。
        - 這裡的插座是 stdio：作業倉庫就跑在這台 Colab 上。真正的「遠端 MCP」是一個網址，2-E 練習 1 會把同一個 server 變成網址再接一次。
        """),
        md("""
        ### 🤔 預測題（用量比較選讀）
        三把本地工具的說明書大約幾個 token？接上作業倉庫的 3 個 MCP 工具呢？如果接的是真的 GitHub MCP server（幾十個工具），token 會多幾倍？
        """),
        code(f"""
        #@title ▶ 執行：本地工具 vs MCP 插座，說明書佔掉多少 token
        {{PREAMBLE}}
        import json
        from langchain_core.utils.function_calling import convert_to_openai_tool
        from langchain_mcp_adapters.client import MultiServerMCPClient
        import agent

        插座 = MultiServerMCPClient({{
            "作業倉庫": {{"command": sys.executable, "args": [str(BASE / "deploy" / "homework_mcp.py")], "transport": "stdio"}},
        }})
        mcp工具 = await 插座.get_tools()

        # 示意用：規模仿 GitHub MCP server 的工具清單（名稱與說明是教學改寫，不是官方原文）
        GitHub規模的工具 = {mcp_literal}

        def 轉成說明書(name, desc, params):
            props = {{k: {{"type": v, "description": k}} for k, v in params.items()}}
            return {{"type": "function", "function": {{"name": name, "description": desc,
                    "parameters": {{"type": "object", "properties": props, "required": list(params)[:2]}}}}}}

        def 估算說明書(說明書們):
            return 估算_token(json.dumps(說明書們, ensure_ascii=False))

        三組 = [
            ("本地工具（自己寫的）", [convert_to_openai_tool(t) for t in agent.小助教的工具]),
            ("作業倉庫 MCP（真的接上）", [convert_to_openai_tool(t) for t in mcp工具]),
            ("GitHub 規模的 MCP（示意）", [轉成說明書(*t) for t in GitHub規模的工具]),
        ]
        結果 = {{}}
        for 名稱, 說明書們 in 三組:
            結果[名稱] = 估算說明書(說明書們)
            print(f"{{名稱:<18}} {{len(說明書們):>3}} 個工具：約 {{結果[名稱]:>5,}} token  " + "█" * max(1, 結果[名稱] // 100))
        本地 = 結果["本地工具（自己寫的）"]
        大的 = 結果["GitHub 規模的 MCP（示意）"]
        print(f"\\n若把這份 GitHub 規模清單全部交給模型，一次呼叫的工具說明約有 {{大的:,}} token 的說明書，是本地工具的 {{大的 / 本地:.1f}} 倍。")
        print("（token 數是用字數估算的，只看大小關係就好）")
        記下("1-B 第 6 段：MCP 說明書的 token", 結果)
        """),
        md("""
        ### 👀 你看到了什麼

        - 作業倉庫只有 3 個工具，說明書不多；這個示意清單有 40 個，說明書明顯較長。實際成本取決於選了哪些工具、模型格式與 tokenizer，這裡只看估算的大小關係。
        - 對 agent 來說，本地工具和 MCP 工具用起來一樣；差別在工具住哪、怎麼認證、說明書佔多少桌子。
        - 第 2 堂會用 **Skill** 按需載入任務指引。Skill 不會自動移除工具定義；要縮減工具清單，仍須由程式篩選或延後提供。
        """),
        md("""
        ---
        ## 第 7 段（課後選做）：用 LangGraph 看懂 agent 的核心迴圈

        > 📍 **對應簡報**：投影片 44「展開 create_agent」

        核心練習已用過 `create_agent`。這段另用 LangGraph 示範「模型 ↔ 工具」迴圈，不是 `create_agent` 的完整實作；可課後再讀。

        其實就是 LangGraph 的三個零件（1-A 用過：**Node** 是一個工作站、**Edge** 是工作站之間的箭頭、**條件邊**是 if）：
        一個問模型的節點 `ask_model`、一個跑工具的節點 `tools`、一條「有沒有要用工具」的 if（`tools_condition`），繞成一個圈。
        程式在 `agent.py` 的 `建立_展開版_agent`。

        | 元件 | 做什麼 |
        | --- | --- |
        | `@tool` | 函式 → 模型看得到的工具 |
        | `bind_tools` | 工具說明書附在每次呼叫上 |
        | `ask_model` | 問模型，回文字或 tool_calls |
        | `ToolNode` | 讀 tool_calls、執行、包結果 |
        | `tools_condition` | 內建路由：有 tool_calls → tools，沒有 → END |
        | `add_edge("tools", "ask_model")` | 工具跑完回去問模型，形成循環 |

        ### 🤔 預測題
        流程圖上會有幾個節點？哪一條是條件邊？
        """),
        code(f"""
        #@title ▶ 執行：自己用 LangGraph 組出核心迴圈
        作業 = "變數打錯字"  #@param {作業選項}
        {{PREAMBLE}}
        import agent

        展開版 = agent.建立_展開版_agent(model)
        顯示流程圖(展開版)
        events = agent.pretty_trace(展開版, agent.作業訊息(取得作業(作業)))
        記下(f"1-B 第 7 段：展開版 agent（{{作業}}）", events)
        """),
        md("""
        ### 👀 你看到了什麼

        - 只有兩個節點：`ask_model` 和 `tools`。從 `ask_model` 出來的是條件邊（虛線）：要用工具就去 `tools`，不用就結束。
        - `tools` 跑完一定回到 `ask_model`，這條往回指的箭頭就是迴圈。
        - LangGraph 和 LangChain 不是對手，是上下層：`create_agent` 回傳的就是一個 LangGraph。
        """),
        md("""
        ---
        ## 第 1 堂收尾

        - **Agent ＝ 模型 ＋ 工具 ＋ 迴圈**；模型只會「說」要用哪個工具，做事的是你的程式。
        - **流程安排不能省略的步驟，agent 處理需要彈性判斷的部分**；兩者可以套在一起（外面是固定流程、某一站裡面放一個 agent），就是課名的「雙拼」（簡報投影片 39，第 2 堂 2-D 會做出來）。
        - 📝 **課後作業**：把你自己寫過的一段作業放進「我的作業」，分別在 1-A 和 1-B 跑一次，
          截圖 1-A 的 State 歷程與 1-B 的工具執行紀錄，寫一句話說哪邊的結果你比較信任、為什麼。
        """),
        *ending(),
    ]
