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
寄信選項 = '["只寄驗證通過的", "全部寄出", "都不要寄"]'


def cells():
    return [
        md(f"""
        # 2-E（課後選做）：把整張分工圖在 Colab 跑起來，再看它怎麼上雲端

        {badge(NAME)}

        > 📍 **對應簡報**：第 2 堂投影片 **41**「分工圖搬上雲端」，以及「補充：上雲端」投影片 **47–54**（課後自學）
        """),
        project_intro("把第 2 堂畫的整張分工圖（MCP、流程、子 agent、驗證 agent、人工確認）真的跑一次，再看上雲端時每一塊住在哪裡。"),
        md("""
        ## 這本 notebook 在做什麼

        第 2 堂最後，我們假設作業小助教要升級：從 GitHub 抓 200 份作業、一次批完、批完自動寄信。
        我們把它拆成一張**分工圖**，每個功能都放進一個「抽屜」：

        | 抽屜 | 白話說是什麼 | 這本裡的例子 |
        | --- | --- | --- |
        | 程式（流程） | 用程式寫死的順序和檢查 | 一定先檢查語法；寄信前一定停下來等人確認 |
        | 工具（tool） | AI 可以呼叫的 Python 函式 | `check_naming`（檢查命名）、`run_code`（執行作業） |
        | MCP | 把「住在別的程式或服務裡的工具」接進來的標準插座 | 作業倉庫：抓作業、寄信 |
        | 手冊（Skill） | 給 AI 看的工作手冊 | `friendly-feedback`（溫和鼓勵） |
        | 子 agent | 另一個有自己一張「桌子」（自己的對話紀錄）的 AI 同事 | 每份作業一個批改員；外加一個專門檢查回饋的**驗證 agent** |

        課堂上只畫了圖，這本把它**真的跑一次**，而且全部在免費 Colab 裡：

        | 練習 | 你會做什麼 | 對應投影片 |
        | --- | --- | --- |
        | 練習 1 | 開一個**真的 MCP server**「作業倉庫」：先用本機插座接，再把它變成一個網址（遠端 MCP） | 41、51 |
        | 練習 2 | ⭐ **整張分工圖跑一次**：MCP 抓作業 → 程式檢查語法 → Send 開 N 個批改子 agent → 驗證 agent → 寄信前停下來等人確認 → MCP 寄信 | 35–37、41、52–53 |
        | 練習 3 | 把它包成 **API 服務**：用網址開始批改、用網址確認寄信，thread_id 跨請求保留 | 48–50 |
        | 練習 4 | **上線前檢查**，並產生部署檔（`Dockerfile`、`langgraph.json`） | 48–49、54 |

        **這本不會真的部署到雲端**（那需要雲端帳號和信用卡）。MCP server、API 服務都開在 Colab 這台機器裡，
        信也是假的，只會寫進 `/content/review-bot/寄件匣.txt`。

        ## 部署地圖：上雲端之後，每個東西住在哪裡

        | 東西 | 在這本 notebook 裡 | 上雲端之後住在哪裡 | 練習 |
        | --- | --- | --- | --- |
        | 外層流程、批改子 agent、驗證 agent、本地 tool（`check_naming`、`run_code`） | Colab 裡的 Python | **你的容器**（Cloud Run 或 LangSmith Deployment），外面包一層 API | 2、3 |
        | `skills/`、`scripts/` | `/content/review-bot/` | **跟著容器一起出貨**：改手冊 ＝ 發新版本 | 4 |
        | 作業倉庫、寄信（MCP） | 同一台機器上的另一個程式 | **別人的服務**：遠端 MCP 是一個網址，用 OAuth 登入 | 1 |
        | 每個 thread_id 的 State、等人確認的信 | SQLite 檔 | **資料庫**（Postgres），機器換掉也還在 | 2、3 |
        | 模型 API key | Colab 🔑 密鑰（或不需要） | **保管箱**（Secret Manager），變成環境變數 | 4 |
        | 同時批幾份、Trace／Eval | `max_concurrency`、印出來的用量 | **任務佇列**、**監控儀表板** | 2、4 |

        一句話：**程式、手冊、腳本跟著容器走；會變的資料進資料庫；鑰匙進保管箱；別人的能力透過網路接進來。**

        表裡的名詞：**容器**＝把程式和它需要的一切裝進同一個箱子，搬到哪台機器都能跑；**Cloud Run、LangSmith Deployment**＝幫你在雲端跑程式的服務；
        **Postgres**＝一種資料庫；**Secret Manager**＝雲端的密碼保管箱；**任務佇列**＝工作太多時讓它們排隊；
        **Trace／Eval**＝記錄每一步做了什麼／自動考試打分數。

        ## 怎麼用

        1. 先執行 **「0. 環境設定」**（會多裝 MCP、FastAPI；並準備好前面幾本的工具和手冊）。
        2. 四個練習彼此獨立，想做哪個就從那個練習的第一格開始；練習 2 是重點。
        3. 練習 2、3 會呼叫模型二十幾次。免費額度不夠時，「0. 環境設定」改選 `gemini` 用講師的 key。
        4. 這本用到 `await`：Colab 的格子可以直接寫 `await`，不用管它，照樣按 ▶ 就好。
        """),
        setup(NAME, support=SUPPORT, packages=["fastapi>=0.115", "uvicorn>=0.30", *MCP_PACKAGES]),
        md("""
        ---
        ## 練習 1：開一個真的 MCP server

        > 📍 **對應簡報**：投影片 41（別人的服務）、51「五個抽屜搬上雲」（遠端 MCP）；第 1 堂投影片 35（MCP 插座）

        先把分工圖上「別人的服務」那一格做出來。MCP 的工具住在**另一個程式**裡。下一格寫出 `deploy/homework_mcp.py`：它就是一個普通的 Python 檔，
        三個函式上面加了 `@mcp.tool()`，就變成可以從插座接出去的工具：

        | 工具 | 真實世界裡是誰 |
        | --- | --- |
        | `list_homework`、`get_homework` | GitHub 的 MCP server（從 repo 抓作業） |
        | `send_email` | 信箱的 MCP server（這裡是假的，只寫進寄件匣） |

        兩種接法：**stdio** 是本機插座（agent 這邊把 server 開成一個子程式）；**Streamable HTTP** 是一個網址，
        遠端 MCP 就是這樣，只是真的服務還要用 **OAuth** 登入（用帳號登入、換一張通行證的標準做法）。

        ### 🤔 預測題
        1. 接上之後，MCP 工具和你在 1-B 自己寫的 `@tool` 看起來有什麼不一樣？
        2. 換成網址接，工具的名字和用法會變嗎？
        """),
        writefile("deploy/homework_mcp.py"),
        code("""
        #@title ▶ 執行：用本機插座（stdio）接上作業倉庫
        {PREAMBLE}
        import json
        from langchain_core.utils.function_calling import convert_to_openai_tool
        from deploy import multi_agent

        設定 = multi_agent.作業倉庫設定()          # stdio：由這邊把 homework_mcp.py 開成另一個程式
        工具們 = await multi_agent.取得MCP工具(設定)
        for t in 工具們.values():
            print(f"🔌 {t.name}（參數：{list(t.args) or '無'}）：{t.description.splitlines()[0]}")

        名單 = json.loads(multi_agent.結果文字(await 工具們["list_homework"].ainvoke({})))
        print("\\nlist_homework →", "、".join(a["學生"] for a in 名單))
        print("\\nget_homework(student='小美') →")
        print(multi_agent.結果文字(await 工具們["get_homework"].ainvoke({"student": "小美"})))

        說明書 = 估算_token(json.dumps([convert_to_openai_tool(t) for t in 工具們.values()], ensure_ascii=False))
        print(f"這 {len(工具們)} 個 MCP 工具的說明書，每次問模型都會放上桌：約 {說明書} token（估算）")
        記下("2-E 練習 1：stdio 接上作業倉庫", {"工具": list(工具們), "學生": [a["學生"] for a in 名單], "說明書token": 說明書})
        """),
        code("""
        #@title ▶ 執行：同一個 server 換成一個網址（Streamable HTTP，像遠端 MCP）
        {PREAMBLE}
        import asyncio, socket, subprocess
        from deploy import multi_agent

        舊的 = getattr(sys, "_作業倉庫程序", None)       # 重跑時先把上一次開的關掉
        if 舊的:
            舊的.terminate()
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        紀錄檔 = open(BASE / "deploy" / "homework_mcp.log", "w")
        sys._作業倉庫程序 = subprocess.Popen([sys.executable, str(multi_agent.MCP_SERVER), "--http", str(port)],
                                         stdout=紀錄檔, stderr=紀錄檔)
        網址 = f"http://127.0.0.1:{port}/mcp"
        for _ in range(60):
            try:
                工具們 = await multi_agent.取得MCP工具(multi_agent.作業倉庫設定(網址))
                break
            except Exception:
                await asyncio.sleep(0.5)
        else:
            raise SystemExit("⚠️ MCP server 沒有開起來，可以看 /content/review-bot/deploy/homework_mcp.log")

        (BASE / "deploy" / ".mcp_port").write_text(str(port))
        print(f"🌐 作業倉庫 MCP 現在是一個網址：{網址}")
        print("用網址接上的工具：", "、".join(工具們))
        print("\\nget_homework(student='阿傑') →")
        print(multi_agent.結果文字(await 工具們["get_homework"].ainvoke({"student": "阿傑"})))
        記下("2-E 練習 1：網址接上作業倉庫", {"網址": 網址, "工具": list(工具們)})
        """),
        md("""
        ### 👀 你看到了什麼

        - MCP 工具一樣有名字、說明、參數，**對 agent 來說和自己寫的 `@tool` 用法完全一樣**；差別只在它住在另一個程式裡。
          （MCP 工具只能用 `await` 呼叫，因為它要透過插座和另一個程式溝通。）
        - 換成網址接，工具一模一樣。上雲端時，作業倉庫就是別人服務上的一個網址：你的程式不用知道它怎麼寫、用什麼語言寫。
        - 插座一接，**所有**工具的說明書都會放上桌。真的 GitHub MCP server 有幾十個工具，所以第 2 堂才說要用 Skill 告訴 AI「只用其中幾個」。
        """),
        md("""
        ---
        ## 練習 2 ⭐：把整張分工圖跑一次

        > 📍 **對應簡報**：投影片 35–37（子 agent、驗證 agent、不要三人接力）、41「部署地圖」、52「Send」、53「interrupt」

        練習 1 把作業倉庫開起來了，這一個練習用它把整張分工圖跑一次。下一格寫出 `deploy/multi_agent.py`，就是那張分工圖：

        | 分工圖上的格子 | 抽屜 | 在程式裡 |
        | --- | --- | --- |
        | 從作業倉庫抓作業 | MCP（由**程式**呼叫，不需要判斷） | `抓作業` 節點呼叫 `list_homework`、`get_homework` |
        | 一定先檢查語法 | 程式 | 語法錯就直接回，**不叫 AI** |
        | 每份作業一個批改員 | 子 agent ＋ Skill ＋ 腳本 | `Send` 一份開一個；手冊 `friendly-feedback`，工具 `check_naming`、`run_code` |
        | 檢查回饋有沒有亂講 | 驗證 agent（另一個人設）＋ 程式 | 程式先查行號，稽核員再看內容；不通過就退回重寫一次 |
        | 寄信 | MCP ＋ 人工確認 | `interrupt()` 停下來，人決定後才呼叫 `send_email` |

        表裡的兩個新寫法：
        - `Send`：LangGraph 的寫法，意思是「照這份清單，一份開一個批改員」，它們可以同時跑。
        - `interrupt()`：流程跑到這裡先停住、把 State 存起來，等人回覆之後再接著跑。

        注意「不要三人接力」：一份作業從批改到修正都是**同一個批改員**；只有黑箱的驗證交給另一個人。

        ### 🤔 預測題
        1. 作業倉庫裡有 5 份作業，其中小明的作業少了右括號。總共會開幾個批改子 agent？
        2. 「同時批幾份」從 1 調到 3，會比較快嗎？token 會變少嗎？
        3. 第 1 步跑完時，信寄出去了嗎？
        """),
        writefile("deploy/multi_agent.py"),
        code("""
        #@title ▶ 執行（第 1 步）：整張分工圖跑一次，停在寄信前面
        thread_id = "期中-第一批"  #@param {type:"string"}
        同時批幾份 = 2  #@param {type:"slider", min:1, max:5, step:1}
        作業倉庫接法 = "本機插座 stdio"  #@param ["本機插座 stdio", "網址 Streamable HTTP（要先跑練習 1 第二格）"]
        {PREAMBLE}
        import time
        from deploy import multi_agent

        網址 = None
        if 作業倉庫接法.startswith("網址"):
            port檔 = BASE / "deploy" / ".mcp_port"
            if not port檔.exists():
                raise SystemExit("⚠️ 還沒用網址開 MCP server：先執行練習 1 的第二格，或改選「本機插座 stdio」")
            網址 = f"http://127.0.0.1:{port檔.read_text()}/mcp"

        存檔 = await multi_agent.開存檔()
        小助教 = multi_agent.建立多agent小助教(model, mcp設定=multi_agent.作業倉庫設定(網址), checkpointer=存檔)
        config = {"configurable": {"thread_id": thread_id}, "max_concurrency": 同時批幾份}
        if (await 小助教.aget_state(config)).values:
            await 存檔.conn.close()
            raise SystemExit(f"⚠️ thread_id「{thread_id}」已經用過了：換一個新的（例如「期中-第二批」），或直接去跑第 2 步")
        顯示流程圖(小助教)

        用量 = multi_agent.用量計()
        t0 = time.time()
        結果 = await 小助教.ainvoke({"結果們": []}, {**config, "callbacks": [用量]})
        秒數 = time.time() - t0
        for r in 結果["結果們"]:
            驗證 = "✅ 通過" if r["驗證"]["通過"] else "❌ " + r["驗證"]["原因"]
            print(f"【{r['學生']}】工具：{'、'.join(r['用到的工具']) or '（沒有叫 AI）'}｜驗證：{驗證}｜退回重寫 {r['重寫次數']} 次")
            print("    " + r["feedback"][:90].replace("\\n", " ") + "…")
        print(f"\\n⏱️ {秒數:.0f} 秒（同時最多 {同時批幾份} 份）；模型呼叫 {用量.次數} 次，約 {用量.input_tokens + 用量.output_tokens:,} token（估算）")

        if "__interrupt__" in 結果:
            print("\\n⏸️  停在寄信前面，等人確認。準備寄出的信：")
            for 信 in 結果["__interrupt__"][0].value["要寄出的信"]:
                print(f"    → {信['學生']} <{信['email']}>（驗證{'通過' if 信['驗證通過'] else '沒過'}）")
        print("存檔裡的下一站：", (await 小助教.aget_state(config)).next)
        await 存檔.conn.close()
        記下(f"2-E 練習 2：整張分工圖（thread_id={thread_id}）",
             {"結果": [{k: r[k] for k in ("學生", "用到的工具", "驗證", "重寫次數")} for r in 結果["結果們"]],
              "模型呼叫次數": 用量.次數, "token": 用量.input_tokens + 用量.output_tokens, "秒數": round(秒數)})
        """),
        code(f"""
        #@title ▶ 執行（第 2 步）：人看過了，決定要不要寄
        thread_id = "期中-第一批"  #@param {{type:"string"}}
        決定 = "只寄驗證通過的"  #@param {寄信選項}
        {{PREAMBLE}}
        from langgraph.types import Command
        from deploy import multi_agent

        存檔 = await multi_agent.開存檔()
        小助教 = multi_agent.建立多agent小助教(model, checkpointer=存檔)
        config = {{"configurable": {{"thread_id": thread_id}}}}
        if not (await 小助教.aget_state(config)).next:
            print(f"thread_id「{{thread_id}}」沒有在等確認的信：先執行第 1 步，或檢查 thread_id 有沒有打錯。")
        else:
            結果 = await 小助教.ainvoke(Command(resume=決定), config)   # resume 的值就是 interrupt() 的回傳值
            for 紀錄 in 結果["寄件紀錄"]:
                print("📮", 紀錄)
            寄件匣 = BASE / "寄件匣.txt"
            if 寄件匣.exists():
                print("\\n寄件匣.txt 最後幾行：")
                print("\\n".join(寄件匣.read_text(encoding="utf-8").splitlines()[-6:]))
            記下(f"2-E 練習 2：決定「{{決定}}」（thread_id={{thread_id}}）", {{"寄件紀錄": 結果["寄件紀錄"]}})
        await 存檔.conn.close()
        """),
        md("""
        ### 👀 你看到了什麼

        - 小明的作業語法錯，**程式直接回覆、沒有叫 AI**；其他 4 份各開一個批改子 agent，所以是 4 個子 agent ＋ 4 次驗證。
        - 每個批改員自己決定要不要跑 `check_naming`、`run_code`；驗證 agent 換了一個「嚴格稽核員」的人設，只檢查不寫，偶爾會退回。
        - 「同時批幾份」調大會比較快，但 **token 一樣多**：每一份都要重新把手冊、工具說明放上桌。
          這就是多 agent 的代價（Anthropic 說約 3–10 倍），先量一份花多少，再乘以 200。
        - 第 1 步結束時信**還沒寄**，流程停在「寄信前確認」，State 存在存檔裡；第 2 步帶著同一個 thread_id 才接著寄。
          換一個 thread_id 去跑第 2 步，會發現它沒有在等確認的信。
        """),
        md("""
        ---
        ## 練習 3：包成 API 服務

        > 📍 **對應簡報**：投影片 48「離開 Colab：三樣東西要換掉」、49「打包」、50「放到哪一朵雲」

        練習 2 是你在 notebook 裡按 ▶ 跑的。上雲端之後，沒有人會按 notebook 的 ▶：幹部是在後台網頁按「開始批改」和「確認寄信」，
        網頁再用 **HTTP**（瀏覽器開網頁用的同一套規則）呼叫你的服務。這種「讓別的程式用網址叫你做事」的介面，叫做 **API**。
        下一格寫出 `deploy/server.py`，用 FastAPI（寫 API 的 Python 套件）開了四個網址：

        | 網址 | 做什麼 |
        | --- | --- |
        | `GET /health` | 雲端平台定時敲它，確認服務還活著 |
        | `POST /batch` | 開始一批：抓作業、批改、驗證，停在寄信前面，回傳待確認的信 |
        | `POST /batch/{thread_id}/decision` | 人確認之後：寄或不寄 |
        | `GET /threads/{thread_id}` | 查一批的進度 |

        ### 🤔 預測題
        「開始批改」和「確認寄信」是兩個不同的請求，中間可能隔三天。第二個請求怎麼知道要寄哪些信？
        """),
        writefile("deploy/server.py"),
        code("""
        #@title ▶ 執行：在 Colab 裡把小助教開成 API 服務
        {PREAMBLE}
        import socket, threading, time
        import requests, uvicorn
        from deploy import server

        舊的 = getattr(sys, "_小助教伺服器", None)       # 重跑這一格時，先把上一次開的關掉
        if 舊的:
            舊的.should_exit = True
            time.sleep(1)
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        伺服器 = uvicorn.Server(uvicorn.Config(server.app, host="127.0.0.1", port=port, log_level="warning"))
        threading.Thread(target=伺服器.run, daemon=True).start()
        sys._小助教伺服器 = 伺服器
        for _ in range(50):
            try:
                if requests.get(f"http://127.0.0.1:{port}/health", timeout=1).ok:
                    break
            except requests.ConnectionError:
                time.sleep(0.2)
        (BASE / "deploy" / ".port").write_text(str(port))
        print(f"✅ 小助教 API 開好了：http://127.0.0.1:{port}")
        for 網址 in ["GET  /health", "POST /batch", "POST /batch/{thread_id}/decision", "GET  /threads/{thread_id}"]:
            print("   ", 網址)
        """),
        code(f"""
        #@title ▶ 執行：用 HTTP 開始一批、確認寄信、查進度
        thread_id = "API-第一批"  #@param {{type:"string"}}
        決定 = "只寄驗證通過的"  #@param {寄信選項}
        {{PREAMBLE}}
        import json, requests

        port檔 = BASE / "deploy" / ".port"
        if not port檔.exists():
            raise SystemExit("⚠️ 服務還沒開：先執行上一格")
        網址 = f"http://127.0.0.1:{{port檔.read_text()}}"
        try:
            開始 = requests.post(f"{{網址}}/batch", json={{"thread_id": thread_id, "同時批幾份": 2}}, timeout=900).json()
        except requests.ConnectionError:
            raise SystemExit("⚠️ 服務沒有在跑（可能重新啟動過執行階段）：先執行上一格")

        待寄 = (開始.get("待確認") or {{}}).get("要寄出的信", [])
        print(f"POST /batch → 停在寄信前面，待確認 {{len(待寄)}} 封：")
        for 信 in 待寄:
            print(f"    {{信['學生']}} <{{信['email']}}> 驗證{{'通過' if 信['驗證通過'] else '沒過'}}")
        print(f"\\nGET /threads/{{thread_id}} →", json.dumps(requests.get(f"{{網址}}/threads/{{thread_id}}", timeout=30).json(), ensure_ascii=False))

        確認 = requests.post(f"{{網址}}/batch/{{thread_id}}/decision", json={{"決定": 決定}}, timeout=300).json()
        print(f"\\nPOST /batch/{{thread_id}}/decision（{{決定}}）→")
        for 紀錄 in 確認.get("寄件紀錄") or [確認.get("錯誤")]:
            print("    📮", 紀錄)
        print(f"\\nGET /threads/{{thread_id}} →", json.dumps(requests.get(f"{{網址}}/threads/{{thread_id}}", timeout=30).json(), ensure_ascii=False))
        print("GET /threads/還沒開始的那批 →", json.dumps(requests.get(f"{{網址}}/threads/還沒開始的那批", timeout=30).json(), ensure_ascii=False))
        記下(f"2-E 練習 3：API 服務（thread_id={{thread_id}}）", {{"開始": 開始, "確認": 確認}})
        """),
        md("""
        ### 👀 你看到了什麼

        - 兩個請求之間靠 **thread_id** 接起來：第一個請求跑到 `interrupt()` 就把 State 存進存檔、回應「待確認」；
          第二個請求帶同一個 thread_id，從存檔接著寄。還沒開始的那批查不到任何存檔。
        - 雲端機器隨時會被換掉，所以上線時存檔要放在資料庫（Postgres），不能放在這台機器的 SQLite 檔。
        - 真的上線時，`POST /batch` 跑 200 份會很久，通常改成「丟進任務佇列、馬上回應」，LangSmith Deployment 這類平台內建這件事。
        - 投影片 50 的三種上雲端做法，真正在跑的都是這一層。
        """),
        md("""
        ---
        ## 練習 4：上線前檢查，順便產生部署檔

        > 📍 **對應簡報**：投影片 48（金鑰放 Secret Manager）、49（langgraph.json 是出貨單）、54「上線之後：看得見、關得住」

        最後一步：真的要上雲端之前，先用程式檢查一遍，再把出貨要用的檔案準備好。
        下面幾格會寫出上雲端要用的檔案（**只產生檔案，不會真的打包或部署**）：

        | 檔案 | 是什麼 |
        | --- | --- |
        | `langgraph.json` | 出貨單：告訴 LangSmith Deployment / `langgraph dev`「graph 在哪個檔案的哪個變數」 |
        | `deploy/app_graph.py` | 出貨單指向的進入點：模型金鑰、遠端 MCP 網址都從環境變數讀 |
        | `requirements.txt` | 要裝哪些套件（版本範圍釘死；`mcp` 和 `langchain-mcp-adapters` 一定要一起釘） |
        | `Dockerfile` | 把程式、`skills/`、`scripts/` 裝進同一個容器的食譜 |
        | `.dockerignore` | 不准裝進容器的東西：`.env`、存檔、紀錄 |
        | `deploy/preflight.py` | 上線前檢查：每一項都用程式檢查，不靠感覺 |

        ### 🤔 預測題
        上線前檢查有 10 項，你猜哪幾項會是 ⚠️（上雲端前還要處理）？
        """),
        writefile("langgraph.json"),
        writefile("deploy/app_graph.py"),
        writefile("requirements.txt"),
        writefile("Dockerfile"),
        writefile(".dockerignore"),
        writefile("deploy/preflight.py"),
        code("""
        #@title ▶ 執行：上線前檢查
        {PREAMBLE}
        from deploy import preflight

        通過 = preflight.印出檢查結果()
        記下("2-E 練習 4：上線前檢查", [{"結果": a, "項目": b, "說明": c} for a, b, c in preflight.檢查()])
        """),
        md("""
        ### 👀 你看到了什麼

        - ✅ 的是程式已經幫你守住的：沒有寫死的金鑰、手冊裡沒有可疑指令、`run_code` 有圍欄、agent 有 `recursion_limit`、
          寄信前有 `interrupt`、有獨立的驗證 agent、部署檔都在。
        - ⚠️ 的是上雲端前還要處理的：
          - **金鑰**：雲端一定要用正式的 API key，放進 Secret Manager（Colab 左邊 🔑「密鑰」就是它的縮小版）。
          - **checkpointer**：SQLite 只存在這一台機器，上線要換成 PostgresSaver。
          - **MCP**：現在是同一台機器用 stdio 開 server；上雲端要改成遠端 MCP 的網址（`HOMEWORK_MCP_URL`），加上 OAuth 登入。
        - 想再試一次 2-C：把 `detailed-feedback` 那本有問題的手冊放進 `skills/`，再跑一次檢查，看「第三方 Skill 掃描」會不會變成 ❌。

        ### 真的要部署的時候（課後參考，會產生費用，指令以各平台官方文件為準）

        ```bash
        # 在 review-bot/ 資料夾裡
        # 1. 本機先跑通（需要 pip install "langgraph-cli[inmem]"）
        langgraph dev

        # 2a. 自己的容器：打包成映像，放到 Cloud Run 這類服務；金鑰用 Secret Manager 注入
        docker build -t review-bot .
        gcloud run deploy review-bot --source . --set-secrets=GOOGLE_API_KEY=review-bot-key:latest

        # 2b. 代管：把這個資料夾推上 GitHub，在 LangSmith Deployment 選這個 repo 部署（它會讀 langgraph.json）
        ```

        上雲端不是換個地方跑，是把 harness 補完整：**每一步看得見（trace、eval、成本），每一個權限關得住（最小權限、沙箱、審 Skill、金鑰、人工確認）。**
        """),
        *ending(),
    ]
