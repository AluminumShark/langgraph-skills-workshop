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

        > 📍 **對應簡報**：第 2 堂投影片 **48**「分工圖搬上雲端」，以及「補充：上雲端」投影片 **47–55**（課後自學）
        """),
        project_intro("把第 2 堂畫的整張分工圖（MCP、流程、子 agent、驗證 agent、人工確認）真的跑一次，再看上雲端時每一塊住在哪裡。"),
        md("""
        ## 這本 notebook 在做什麼

        第 2 堂最後，我們假設作業小助教要升級：從 GitHub 抓 200 份作業、一次批完、批完自動寄信。
        我們把它拆成一張**分工圖**，從「由誰決定執行」和「能力如何提供」兩個角度分類；同一項功能可以同時用到幾種零件：

        | 角色 | 白話說是什麼 | 這本裡的例子 |
        | --- | --- | --- |
        | 程式（流程） | 由流程控制的順序和檢查 | 一定先檢查語法；寄信前一定停下來等人確認 |
        | 工具（tool） | AI 可以呼叫的 Python 函式 | `check_naming`（檢查命名）、`run_code`（執行作業） |
        | MCP | 把「住在別的程式或服務裡的工具」接進來的標準插座 | 作業倉庫：抓作業、寄信 |
        | 手冊（Skill） | 給 AI 看的工作手冊 | `friendly-feedback`（溫和鼓勵） |
        | 子 agent | 另一個有自己一張「桌子」（自己的對話紀錄）的 AI 同事 | 每份作業一個批改員；外加一個專門檢查回饋的**驗證 agent** |

        課堂上只畫了圖，這本把它**真的跑一次**，而且全部在免費 Colab 裡：

        | 練習 | 你會做什麼 | 對應投影片 |
        | --- | --- | --- |
        | 練習 1 | 開一個**真的 MCP server**「作業倉庫」：先用本機插座接，再把它變成一個網址（遠端 MCP） | 48、52 |
        | 練習 2 | ⭐ **先批一份，再整批執行**：MCP 抓作業 → Send 分派各份 → 每份先查語法，通過才進批改與驗證 agent → 寄信前停下來等人確認 → MCP 寄信 | 33–35、48、53–54 |
        | 練習 3 | 把它包成 **API 服務**：用網址開始批改、用網址確認寄信，thread_id 跨請求保留 | 49–51 |
        | 練習 4 | **上線前檢查**，並產生部署檔（`Dockerfile`、`langgraph.json`） | 49–50、55 |

        **這本不會真的部署到雲端**（那需要雲端帳號和信用卡）。MCP server、API 服務都開在 Colab 這台機器裡，
        信也是假的，只會寫進 `/content/review-bot/寄件匣.txt`。

        ## 部署地圖：上雲端之後，每個東西住在哪裡

        | 東西 | 在這本 notebook 裡 | 上雲端之後住在哪裡 | 練習 |
        | --- | --- | --- | --- |
        | 外層流程、批改子 agent、驗證 agent、本地 tool（`check_naming`、`run_code`） | Colab 裡的 Python | **你的容器**（Cloud Run 或 LangSmith Deployment），外面包一層 API | 2、3 |
        | `skills/`、`scripts/` | `/content/review-bot/` | **跟著容器一起出貨**：改手冊 ＝ 發新版本 | 4 |
        | 作業倉庫、寄信（MCP） | 同一台機器上的另一個程式 | **別人的服務**：遠端 MCP 透過網址連線，依服務設定授權 | 1 |
        | 每個 thread_id 的 State、等人確認的信 | SQLite 檔 | **資料庫**（Postgres），機器換掉也還在 | 2、3 |
        | 模型 API key | Colab 🔑 密鑰（或不需要） | **保管箱**（Secret Manager），變成環境變數 | 4 |
        | 同時批幾份、Trace／Eval | `max_concurrency`、印出來的用量 | **任務佇列**、**監控儀表板** | 2、4 |

        一句話：**程式、手冊、腳本跟著容器走；會變的資料進資料庫；鑰匙進保管箱；別人的能力透過網路接進來。**

        表裡的名詞：**容器**＝把程式和它需要的一切裝進同一個箱子，搬到哪台機器都能跑；**Cloud Run、LangSmith Deployment**＝幫你在雲端跑程式的服務；
        **Postgres**＝一種資料庫；**Secret Manager**＝雲端的密碼保管箱；**任務佇列**＝工作太多時讓它們排隊；
        **Trace／Eval**＝記錄每一步做了什麼／自動考試打分數。

        ## 怎麼用

        1. 先執行 **「0. 環境設定」**（會多裝 MCP、FastAPI；並準備好前面幾本的工具和手冊）。
        2. 建議先做練習 1 的 stdio，再做練習 2 的一份作業與人工確認；能說明結果與確認步驟後才選整批。HTTP、API、部署檔留第二輪。
        3. 模型呼叫數隨份數、工具使用與退回重寫改變；先用一份觀察用量。環境設定使用全新預設手冊，不會延續前面 notebook 的修改。
        4. 重跑環境設定與 `%%writefile` 準備格會覆寫其中的預設檔案，請先保留修改；SQLite 存檔與假的寄件匣不會因此清空。環境重建後要重新準備檔案與服務。
        5. 這本用到 `await`：Colab 的格子可以直接寫 `await`，不用管它，照樣按 ▶ 就好。
        """),
        setup(NAME, support=SUPPORT, packages=["fastapi>=0.115", "uvicorn>=0.30", *MCP_PACKAGES]),
        md("""
        ---
        ## 練習 1：開一個真的 MCP server

        > 📍 **對應簡報**：投影片 48（部署地圖）、52（遠端 MCP）；第 1 堂投影片 39（MCP 插座）

        先把分工圖上「別人的服務」那一格做出來。MCP 的工具住在**另一個程式**裡。下一格寫出 `deploy/homework_mcp.py`：它就是一個普通的 Python 檔，
        三個函式上面加了 `@mcp.tool()`，就變成可以從插座接出去的工具：

        本練習的資料源是 `homework_mcp.py` 中的 Python 字典，預先放好 **5 位學生的假信箱與作業程式碼**，尚未讀取 GitHub 上的學生 repo。
        MCP server 與連線是真的，資料來源與寄信則使用模擬內容。

        | 工具 | 本練習實作 | 真正接服務時 |
        | --- | --- | --- |
        | `list_homework`、`get_homework` | 從預設字典取名單與程式碼 | 需接 GitHub API，或轉接相容的 MCP 工具 |
        | `send_email` | 只寫進模擬寄件匣 | 需串接真正的寄信服務 |

        這些是本課自訂的工具名稱；不能只把網址換成任意 GitHub MCP server 就直接相容，還要對應工具名稱、參數與回傳格式。

        兩種接法：**stdio** 是本機插座（agent 這邊把 server 開成一個子程式）；**Streamable HTTP** 是一個網址，
        遠端 MCP 就是這樣，只是實際服務可能使用 **OAuth** 登入或其他授權方式（用帳號登入、換一張通行證的標準做法）。

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
        print(f"這 {len(工具們)} 個 MCP 工具的說明書合計：約 {說明書} token（估算）")
        記下("2-E 練習 1：stdio 接上作業倉庫", {"工具": list(工具們), "學生": [a["學生"] for a in 名單], "說明書token": 說明書})
        """),
        code("""
        #@title ▶ 選做：同一個 server 換成一個網址（Streamable HTTP，像遠端 MCP）
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

        - MCP 工具一樣有名字、說明、參數，**接成工具後，模型同樣依名字、說明與參數提出呼叫要求**；執行時還涉及另一個程式的連線與錯誤處理。
          （這份 Python adapter 範例使用 `await ...ainvoke()` 等待工具回傳；這不是所有 MCP 客戶端的固定寫法。）
        - 換成網址接，工具一模一樣。上雲端時，作業倉庫就是別人服務上的一個網址：你的程式不用知道它怎麼寫、用什麼語言寫。
        - MCP 提供工具清單；由應用程式決定把哪些工具提供給模型。Skill 可以描述使用方式，但不會自動縮減工具定義或撤銷權限。這份流程由程式直接呼叫 MCP，批改 agent 只拿到命名檢查與執行工具。
        - **完成檢查**：先在 stdio 輸出找到工具名稱與小美的作業。能說明「另一個程式提供工具」後，再選做網址接法；不必先懂網路部署。
        """),
        md("""
        ---
        ## 練習 2 ⭐：把整張分工圖跑一次

        > 📍 **對應簡報**：投影片 33–35（批次、子 agent 與驗證）、48「分工圖搬上雲端：每一格住在哪裡」、53「200 份同時批：Send」、54「寄信前等待確認：interrupt」

        練習 1 把作業倉庫開起來了，這一個練習用它把整張分工圖跑一次。下一格寫出 `deploy/multi_agent.py`，就是那張分工圖：

        | 分工圖上的格子 | 角色 | 在程式裡 |
        | --- | --- | --- |
        | 從作業倉庫抓作業 | MCP（由**程式**呼叫，不需要判斷） | `抓作業` 節點呼叫 `list_homework`、`get_homework` |
        | 一定先檢查語法 | 程式 | 語法錯就直接回，**不叫 AI** |
        | 每份作業一個批改員 | 子 agent ＋ Skill ＋ 腳本 | `Send` 一份開一個；手冊 `friendly-feedback`，工具 `check_naming`、`run_code` |
        | 檢查回饋有沒有亂講 | 驗證 agent（獨立檢查職責）＋ 程式 | 程式先查行號，稽核員再看內容；不通過最多退回重寫一次；仍不通過會保留失敗狀態 |
        | 寄信 | MCP ＋ 人工確認 | `interrupt()` 停下來，人決定後才呼叫 `send_email` |

        表裡的兩個新寫法：
        - `Send`：把清單中的每份資料送進「批一份」節點，可以同時處理。節點先查語法，通過才建立批改 agent。
        - `interrupt()`：流程跑到這裡先停住、把 State 存起來，等人回覆之後再接著跑。

        注意「不要三人接力」：一份作業從批改到修正都是**同一個批改員**；語意判斷交給另一個只負責檢查的 agent；獨立檢查仍可能漏錯。

        ### 🤔 預測題
        1. 第一輪只選小美：預測哪個節點會停下來、怎樣確認還沒有寄信。第二輪整批有 5 份，其中小明語法錯，會有幾份需要模型批改？
        2. 「同時批幾份」從 1 調到 3，會比較快嗎？token 會變少嗎？
        3. 第 1 步跑完時，信寄出去了嗎？
        """),
        writefile("deploy/multi_agent.py"),
        code("""
        #@title ▶ 執行（第 1 步）：整張分工圖跑一次，停在寄信前面
        thread_id = "期中-第一批"  #@param {type:"string"}
        批改範圍 = "先批小美一份"  #@param ["先批小美一份", "整批五份"]
        同時批幾份 = 1  #@param {type:"slider", min:1, max:5, step:1}
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
        小助教 = multi_agent.建立多agent小助教(model, mcp設定=multi_agent.作業倉庫設定(網址), checkpointer=存檔,
                                            只批學生="小美" if 批改範圍 == "先批小美一份" else None)
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
            print(f"【{r['學生']}】工具：{'、'.join(r['用到的工具']) or '（沒有要求工具；不等於沒叫 AI）'}｜驗證：{驗證}｜退回重寫 {r['重寫次數']} 次")
            print("回饋全文：\\n" + r["feedback"])
            print("驗證原因：", r["驗證"]["原因"])
        print(f"\\n⏱️ {秒數:.0f} 秒（同時最多 {同時批幾份} 份）；模型呼叫 {用量.次數} 次，約 {用量.input_tokens + 用量.output_tokens:,} token（估算）")

        if "__interrupt__" in 結果:
            print("\\n⏸️  停在寄信前面，等人確認。準備寄出的信：")
            for 信 in 結果["__interrupt__"][0].value["要寄出的信"]:
                print(f"    → {信['學生']} <{信['email']}>（驗證{'通過' if 信['驗證通過'] else '沒過'}）")
                print(信["回饋"])
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
        if (await 小助教.aget_state(config)).next != ("寄信前確認",):
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

        - **第一輪完成檢查**：應看到小美的一份回饋、驗證結果、待確認的信與下一站。第 1 步只準備信；第 2 步用相同 thread_id 決定後，才寫入假的寄件匣。
        - 第二輪：把範圍改成「整批五份」、兩步都換成新編號「期中-第二批」、同時批幾份設為 1。小明語法錯由程式直接回覆；其餘四份各自進入批改與驗證，退回重寫時會再驗證。
        - 第三輪選做：再換新編號，保持整批五份、同時批幾份改成 3，記錄秒數、模型呼叫數與 token，和第二輪比較。**並行不保證更快，也不保證 token 相同**；模型回答、重寫次數、限流和系統負載都會影響結果。
        - 每個批改員自行選工具；驗證 agent 的價值是獨立檢查職責與輸入，不只是換個人設。驗證通過仍不代表內容絕對正確；重寫後未通過的回饋仍會列出，預設「只寄驗證通過的」會排除它們。小明的語法回覆由程式直接產生，沒有交給驗證 agent，輸出會註明原因。
        - 想從頭再做請用新 thread_id；已用過的編號不會清空。先能說明「待確認 → 人決定 → 寄件紀錄」，再進入 API 練習。
        """),
        md("""
        ---
        ## 練習 3（進階選做）：包成 API 服務

        > 📍 **對應簡報**：投影片 49「離開 Colab：三樣東西要換掉」、50「打包：langgraph.json 是出貨單」、51「選讀：部署方式，依維運需求選擇」

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
        else:
            raise SystemExit("⚠️ API 未通過健康檢查，請查看上方錯誤並重新啟動服務。")
        (BASE / "deploy" / ".port").write_text(str(port))
        print(f"✅ 小助教 API 開好了：http://127.0.0.1:{port}")
        for 網址 in ["GET  /health", "POST /batch", "POST /batch/{thread_id}/decision", "GET  /threads/{thread_id}"]:
            print("   ", 網址)
        """),
        code(f"""
        #@title ▶ API 第 1 步：開始一批、閱讀待寄內容與進度
        thread_id = "API-第一批"  #@param {{type:"string"}}
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

        if 開始.get("錯誤"):
            raise SystemExit(開始["錯誤"] + " 若要確認既有信件，請到下一格使用相同編號。")
        待寄 = (開始.get("待確認") or {{}}).get("要寄出的信", [])
        print(f"POST /batch → 停在寄信前面，待確認 {{len(待寄)}} 封：")
        for 信 in 待寄:
            print(f"    {{信['學生']}} <{{信['email']}}> 驗證{{'通過' if 信['驗證通過'] else '沒過'}}")
            print(信["回饋"])
        print(f"\\nGET /threads/{{thread_id}} →", json.dumps(requests.get(f"{{網址}}/threads/{{thread_id}}", timeout=30).json(), ensure_ascii=False))

        print("請先閱讀待寄內容，再到下一格選擇寄信決定；本格尚未寄信。")
        記下(f"2-E 練習 3：API 開始（thread_id={{thread_id}}）", 開始)
        """),
        md("""
        **停一下**：上一格只是開始批改與列出待寄內容。讀完後，再在下一格填入同一個 thread_id 並選擇決定。
        本範例仍只寫假的寄件匣；分成兩格是為了保留人實際閱讀與決定的時間。
        """),
        code(f"""
        #@title ▶ API 第 2 步：人讀完後，確認寄信並查進度
        thread_id = "API-第一批"  #@param {{type:"string"}}
        決定 = "只寄驗證通過的"  #@param {寄信選項}
        {{PREAMBLE}}
        import json, requests

        port檔 = BASE / "deploy" / ".port"
        if not port檔.exists():
            raise SystemExit("請先啟動 API 服務並完成 API 第 1 步。")
        網址 = f"http://127.0.0.1:{{port檔.read_text()}}"
        確認 = requests.post(f"{{網址}}/batch/{{thread_id}}/decision", json={{"決定": 決定}}, timeout=300).json()
        print(f"\\nPOST /batch/{{thread_id}}/decision（{{決定}}）→")
        for 紀錄 in 確認.get("寄件紀錄") or [確認.get("錯誤")]:
            print("    📮", 紀錄)
        print(f"\\nGET /threads/{{thread_id}} →", json.dumps(requests.get(f"{{網址}}/threads/{{thread_id}}", timeout=30).json(), ensure_ascii=False))
        print("GET /threads/還沒開始的那批 →", json.dumps(requests.get(f"{{網址}}/threads/還沒開始的那批", timeout=30).json(), ensure_ascii=False))
        記下(f"2-E 練習 3：API 服務（thread_id={{thread_id}}）", {{"確認": 確認}})
        """),
        md("""
        ### 👀 你看到了什麼

        - 兩個請求之間靠 **thread_id** 接起來：第一個請求跑到 `interrupt()` 就把 State 存進存檔、回應「待確認」，此時尚未寄信；
          第二個請求帶同一個 thread_id，依決定寄或不寄。還沒開始的那批查不到任何存檔；已用過的編號不能再次開始批改，以免把結果混在一起。
        - 雲端機器隨時會被換掉，所以上線時存檔要放在資料庫（Postgres），不能放在這台機器的 SQLite 檔。
        - 真的上線時，`POST /batch` 跑 200 份會很久，通常改成「丟進任務佇列、馬上回應」，LangSmith Deployment 這類平台內建這件事。
        - 投影片 51 的三種上雲端做法，真正在跑的都是這一層。
        """),
        md("""
        ---
        ## 練習 4（進階選做）：上線前檢查，順便產生部署檔

        > 📍 **對應簡報**：投影片 49（金鑰放 Secret Manager）、50（langgraph.json 是出貨單）、55「上線之後：看得見、關得住」

        最後一步：真的要上雲端之前，先用程式檢查一遍，再把出貨要用的檔案準備好。
        下面幾格會寫出上雲端要用的檔案（**只產生檔案，不會真的打包或部署**）：

        | 檔案 | 是什麼 |
        | --- | --- |
        | `langgraph.json` | 出貨單：告訴 LangSmith Deployment / `langgraph dev`「graph 在哪個檔案的哪個變數」 |
        | `deploy/app_graph.py` | 出貨單指向的進入點：模型金鑰、遠端 MCP 網址都從環境變數讀 |
        | `requirements.txt` | 要裝哪些套件（限制相容版本範圍；`mcp` 和 `langchain-mcp-adapters` 一定要一起釘） |
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

        - ✅ 只代表通過這份範例的檢查，例如未命中列出的金鑰樣式、簡易掃描未發現所列可疑詞、`run_code` 有課堂範例的執行限制、agent 有 `recursion_limit`、
          寄信前有 `interrupt`、有獨立的驗證 agent、部署檔都在。
        - ⚠️ 的是上雲端前還要處理的：
          - **金鑰**：這個 Gemini 部署範例需要有效的 API key，放進 Secret Manager（Colab 左邊 🔑「密鑰」就是它的縮小版）。
          - **checkpointer**：SQLite 只存在這一台機器，上線要換成 PostgresSaver。
          - **MCP**：現在是同一台機器用 stdio 開 server；跨機器使用時可改成遠端 MCP 的網址（`HOMEWORK_MCP_URL`），依服務設定授權；OAuth 是其中一種方式。
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

        正式部署還需補上執行環境的管理：**每一步看得見（trace、eval、成本），權限受到適當限制（最小權限、沙箱、審 Skill、金鑰、人工確認）。**
        """),
        *ending(),
    ]
