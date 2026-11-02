from nbbuild import badge, code, ending, md, setup, writefile

NAME = "2-E_deploy"
作業選項 = '["命名不一致", "變數打錯字", "正確的程式", "縮排亂掉"]'
SUPPORT = [
    "tools/__init__.py", "tools/run_code.py", "tools/read_spec.py", "tools/check_naming.py",
    "graph.py", "skill_loader.py", "dual_core.py", "spec.md", "deploy/__init__.py",
    "skills/friendly-feedback/SKILL.md", "skills/strict-review/SKILL.md",
    "skills/naming-check/SKILL.md", "skills/naming-check/scripts/check_naming.py",
]


def cells():
    return [
        md(f"""
        # 2-E（課後選做）：上雲端前的準備

        {badge(NAME)}

        > 📍 **對應簡報**：第 2 堂「補充：上雲端」，投影片 **47–54**（課堂上不講，課後自學）；部署地圖在投影片 **41**

        ## 這本 notebook 在做什麼

        前兩堂的作業小助教都住在 Colab 裡：模型是 Colab 內建的、檔案在 `/content`、斷線就沒了。
        真的要讓全社團用，就得把它放到「雲端」：一台 24 小時開著、別人用網址就能連到的電腦。

        **這本不會真的部署**（那需要雲端帳號和信用卡），而是在免費 Colab 裡，把上雲端前一定要會的四件事各練一次：

        | 練習 | 你會做什麼 | 對應投影片 |
        | --- | --- | --- |
        | 練習 1 | 把雙核小助教包成 **API 服務**，用網址送作業、拿回饋；thread_id 跨請求保留 | 48–50 |
        | 練習 2 | 用 **Send** 一次開好幾份「批一份」平行批改，數一數多花了多少 token | 52 |
        | 練習 3 | 寄信前用 **interrupt()** 停下來，人按確認才寄 | 53 |
        | 練習 4 | **上線前檢查**：金鑰、第三方 Skill、圍欄、部署檔（`Dockerfile`、`langgraph.json`） | 48–49、54 |

        ## 部署地圖：上雲端之後，每個東西住在哪裡

        > 📍 **對應簡報**：第 2 堂投影片 41「分工圖搬上雲端：每一格住在哪裡」

        | 東西 | 在 Colab 裡 | 上雲端之後住在哪裡 | 這本的哪個練習 |
        | --- | --- | --- | --- |
        | 外層流程、回饋 agent、本地 tool（`check_naming`…） | notebook 裡的 Python | **你的容器**（Cloud Run 或 LangSmith Deployment），外面包一層 API | 練習 1 |
        | `skills/`、`scripts/` | `/content/review-bot/` | **跟著容器一起出貨**：改手冊 ＝ 發新版本 | 練習 4（`Dockerfile`） |
        | 每個 thread_id 的 State、等人確認的信 | SQLite 檔（這台機器） | **資料庫**（Postgres），機器換掉也還在 | 練習 1、3 |
        | RAG 的資料（例如上千筆歷屆作業） | （這堂沒有） | **資料庫**裡的向量資料，或從 MCP 接的知識庫 | — |
        | 模型 API key、OAuth token | Colab 🔑 密鑰 | **保管箱**（Secret Manager），變成環境變數 | 練習 4 |
        | 模型、遠端 MCP（抓作業、寄信）、`run_code` 的沙箱 | Colab 內建模型、本機函式 | **別人的服務**，透過網路呼叫 | 練習 3（寄信前確認） |
        | 200 份排隊、Trace／Eval | 一次跑幾份 | **任務佇列**、**監控儀表板** | 練習 2、4 |

        一句話：**程式、手冊、腳本跟著容器走；會變的資料進資料庫；鑰匙進保管箱；別人的能力透過網路接進來。**

        ## 怎麼用

        1. 先執行 **「0. 環境設定」**（會多裝 FastAPI 和 uvicorn，並準備好 2-D 的雙核小助教）。
        2. 四個練習彼此獨立，想做哪個就從那個練習的第一格開始。
        3. 會呼叫模型好幾次；免費額度不夠時，可以改用講師的 Gemini key（「0. 環境設定」選 `gemini`）。
        """),
        setup(NAME, support=SUPPORT, packages=["fastapi>=0.115", "uvicorn>=0.30"]),
        md("""
        ---
        ## 練習 1：把小助教包成一個 API 服務

        > 📍 **對應簡報**：投影片 48「離開 Colab：三樣東西要換掉」、49「打包」、50「放到哪一朵雲」

        上雲端之後，雲端機器上**真正在跑的**就是一個「服務」：它一直開著，等別人用網址（HTTP）把作業送進來，再把回饋送回去。
        送作業的可以是網頁表單、LINE bot、或每天半夜的排程。

        下一格寫出 `deploy/server.py`，裡面用 FastAPI 開了三個網址：

        | 網址 | 做什麼 |
        | --- | --- |
        | `GET /health` | 雲端平台定時敲它，確認服務還活著 |
        | `POST /review` | 送作業進來（附上 thread_id），拿回饋 |
        | `GET /threads/{thread_id}` | 查某個 thread_id 的存檔 |

        ### 🤔 預測題
        1. 用 thread_id「小明-期中」送一次作業後，再去查「小明-期中」和「還沒交作業的同學」的存檔，各會看到什麼？
        2. 這個服務關掉再開，「小明-期中」的存檔還在嗎？（提示：存檔放在哪裡？）
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

        with socket.socket() as s:                       # 找一個沒人用的 port
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
        print("   GET  /health")
        print("   POST /review")
        print("   GET  /threads/{thread_id}")
        """),
        code(f"""
        #@title ▶ 執行：用 HTTP 送作業給小助教，再查存檔
        thread_id = "小明-期中"  #@param {{type:"string"}}
        作業 = "命名不一致"  #@param {作業選項}
        {{PREAMBLE}}
        import json, requests

        port_檔 = BASE / "deploy" / ".port"
        if not port_檔.exists():
            raise SystemExit("⚠️ 服務還沒開：先執行上一格")
        網址 = f"http://127.0.0.1:{{port_檔.read_text()}}"
        try:
            回應 = requests.post(f"{{網址}}/review", json={{"thread_id": thread_id, "code": 取得作業(作業)}}, timeout=600)
        except requests.ConnectionError:
            raise SystemExit("⚠️ 服務沒有在跑（可能重新啟動過執行階段）：先執行上一格")

        print(f"POST /review → HTTP {{回應.status_code}}")
        print(json.dumps(回應.json(), ensure_ascii=False, indent=2))
        查詢 = {{}}
        for tid in [thread_id, "還沒交作業的同學"]:
            查詢[tid] = requests.get(f"{{網址}}/threads/{{tid}}", timeout=30).json()
            print(f"\\nGET /threads/{{tid}} → 有存檔：{{查詢[tid]['有存檔']}}，下一站：{{查詢[tid]['下一站'] or ('（結束）' if 查詢[tid]['有存檔'] else '—')}}")
        記下(f"2-E 練習 1：API 服務（thread_id={{thread_id}}）", {{"review": 回應.json(), "threads": 查詢}})
        """),
        md("""
        ### 👀 你看到了什麼

        - 你沒有直接呼叫任何 Python 函式，只是「送一個網址請求」，就拿到回饋了。網頁、LINE bot 也都是這樣用它。
        - 「小明-期中」有存檔、「還沒交作業的同學」沒有：**一個 thread_id 一張訂單紙**，跟 2-D 一樣。
        - 存檔現在放在 Colab 這台機器的 SQLite 檔案裡。雲端的機器隨時會被換掉，所以上線時要換成存在資料庫裡的 checkpointer（例如 PostgresSaver）。
        - 投影片 50 的三種上雲端做法（LangSmith Deployment、自己的容器如 Cloud Run、雲端廠商的 agent 執行環境），真正在跑的都是這一層。
        """),
        md("""
        ---
        ## 練習 2：200 份同時批：Send，以及它的成本

        > 📍 **對應簡報**：投影片 52「200 份同時批：Send」

        第 2 堂說過：一份作業開一個子 agent、一張乾淨的桌子，才不會把第 148 份同學的名字寫進第 150 份。
        LangGraph 的做法是 **Send**：條件邊回傳一串 `Send("批一份", 一份作業)`，「批一份」這個節點就會同時開很多個。
        `max_concurrency` 限制最多同時跑幾份（模型 API 每分鐘有上限，一次衝 200 個會被擋）。

        對照組是「一張桌子批全部」：只問模型一次，把所有作業塞在同一個 prompt 裡。

        ### 🤔 預測題
        1. 批 5 份作業，平行版會呼叫模型幾次？一張桌子版呢？
        2. 哪一種用的 token 比較多？為什麼？
        """),
        writefile("deploy/batch.py"),
        code("""
        #@title ▶ 執行：用 Send 平行批改，再和「一張桌子批全部」比成本
        份數 = 5  #@param {type:"slider", min:2, max:8, step:1}
        同時批幾份 = 2  #@param {type:"slider", min:1, max:5, step:1}
        {PREAMBLE}
        import time
        from deploy import batch

        範例們 = [v for k, v in 範例作業.items() if k != "空白"]
        作業們 = [{"學生": f"學生{i + 1}", "code": 範例們[i % len(範例們)]} for i in range(份數)]

        流程 = batch.建立批改流程(model)
        顯示流程圖(流程)

        平行 = batch.用量計()
        t0 = time.time()
        結果 = 流程.invoke({"作業們": 作業們, "結果們": []}, config={"max_concurrency": 同時批幾份, "callbacks": [平行]})
        秒數 = time.time() - t0
        for r in 結果["結果們"]:
            print(f"【{r['學生']}】{r['回饋'][:70].replace(chr(10), ' ')}…")

        一張桌子 = batch.用量計()
        batch.一次批全部(model, 作業們, callbacks=[一張桌子])

        print(f"\\n{'做法':<18}{'呼叫模型':>8}{'input token':>14}{'output token':>14}")
        for 名稱, 計 in [("Send 平行（一份一桌）", 平行), ("一張桌子批全部", 一張桌子)]:
            print(f"{名稱:<18}{計.次數:>8}{計.input_tokens:>14,}{計.output_tokens:>14,}")
        總平行 = 平行.input_tokens + 平行.output_tokens
        總一桌 = 一張桌子.input_tokens + 一張桌子.output_tokens
        print(f"\\n平行版花了「一張桌子」的 {總平行 / max(總一桌, 1):.1f} 倍 token；平行跑 {份數} 份花了 {秒數:.1f} 秒（同時最多 {同時批幾份} 份）")
        print("（Colab 內建模型的 token 是估算值）")
        記下(f"2-E 練習 2：Send 平行批 {份數} 份", {"平行": vars(平行), "一張桌子": vars(一張桌子)})
        """),
        md("""
        ### 👀 你看到了什麼

        - 平行版每份作業呼叫一次模型（`份數` 次），一張桌子版只呼叫 1 次。
        - 平行版的 input token 比較多：**每一份都要重新把手冊放上桌**。真實的多 agent 系統還要加上工具說明、互相傳話、摘要結果，
          Anthropic 的數字是單一 agent 的 **3–10 倍**。這裡的倍數只是小規模示範。
        - 那為什麼還要平行？因為一張桌子塞 200 份，前面的作業會干擾後面的（context 污染），而且平行比較快。
          **先量一份花多少、再乘以 200，確定付得起再開。** 把「同時批幾份」調大，平行版會變快，但 token 一樣多。
        """),
        md("""
        ---
        ## 練習 3：寄信前一定停下來：interrupt()

        > 📍 **對應簡報**：投影片 53「寄信前一定停下來：interrupt()」

        寄信不可逆，寄錯了收不回來。`interrupt()` 會把 State 存進 checkpointer 然後**停住**，把要寄的內容交給人看；
        人看過之後，用 `Command(resume="寄")` 帶著**同一個 thread_id** 叫它繼續。等一小時、等三天都可以。

        這裡的 `send_email` 是假的，只會把信寫進 `/content/review-bot/寄件匣.txt`。

        ### 🤔 預測題
        1. 執行第一格之後，信寄出去了嗎？存檔裡的「下一站」是什麼？
        2. 第二格選「不要寄」，寄件匣裡會有這封信嗎？
        """),
        writefile("deploy/email_flow.py"),
        code("""
        #@title ▶ 執行（第 1 步）：寫好回饋，停在寄信前面等確認
        thread_id = "小明-寄信"  #@param {type:"string"}
        收件人 = "xiaoming@example.com"  #@param {type:"string"}
        {PREAMBLE}
        import dual_core
        from deploy import email_flow

        流程 = email_flow.建立寄信流程(model, dual_core.開存檔(BASE / "deploy" / "email_checkpoints.sqlite"))
        config = {"configurable": {"thread_id": thread_id}}
        結果 = 流程.invoke({"學生": "小明", "email": 收件人, "code": 取得作業("變數打錯字")}, config)

        if "__interrupt__" in 結果:
            待確認 = 結果["__interrupt__"][0].value
            print("⏸️  停在寄信前面，等人確認：")
            print("   收件人：", 待確認["收件人"])
            print("   內容：")
            print("   " + 待確認["內容"].replace("\\n", "\\n   "))
        print("\\n存檔裡的下一站：", 流程.get_state(config).next)
        寄出了嗎 = email_flow.寄件匣.exists() and 收件人 in email_flow.寄件匣.read_text(encoding="utf-8")
        print("寄件匣裡有這封信嗎？", "有" if 寄出了嗎 else "沒有（還沒寄）")
        記下(f"2-E 練習 3：停在寄信前（thread_id={thread_id}）", {"下一站": list(流程.get_state(config).next)})
        """),
        code("""
        #@title ▶ 執行（第 2 步）：人看過了，決定寄不寄
        thread_id = "小明-寄信"  #@param {type:"string"}
        決定 = "寄"  #@param ["寄", "不要寄"]
        {PREAMBLE}
        from langgraph.types import Command
        import dual_core
        from deploy import email_flow

        流程 = email_flow.建立寄信流程(model, dual_core.開存檔(BASE / "deploy" / "email_checkpoints.sqlite"))
        config = {"configurable": {"thread_id": thread_id}}
        if not 流程.get_state(config).next:
            print(f"thread_id「{thread_id}」沒有在等確認的信：先執行第 1 步，或檢查 thread_id 有沒有打錯。")
        else:
            結果 = 流程.invoke(Command(resume=決定), config)     # resume 的值就是 interrupt() 的回傳值
            print("📮", 結果["寄件紀錄"])
            print("已寄出：", 結果["已寄出"])
            if email_flow.寄件匣.exists():
                print("\\n寄件匣.txt 最後幾行：")
                print("\\n".join(email_flow.寄件匣.read_text(encoding="utf-8").splitlines()[-6:]))
            記下(f"2-E 練習 3：決定「{決定}」（thread_id={thread_id}）", {"已寄出": 結果["已寄出"], "寄件紀錄": 結果["寄件紀錄"]})
        """),
        md("""
        ### 👀 你看到了什麼

        - 第 1 步之後信**還沒寄**，下一站停在 `寄信`：流程停住了，State 安全地存在存檔裡。
        - 第 2 步選「寄」才會寫進寄件匣；選「不要寄」就不會。第 2 堂說的「寄之前一定要有人按確認」，在這裡從一句話變成了一行 `interrupt()`。
        - 幹部可能三天後才按確認，中間雲端機器早就換過了，所以上線一定要用不會忘記的 checkpointer（Postgres 這類資料庫）。
        """),
        md("""
        ---
        ## 練習 4：上線前檢查，順便產生部署檔

        > 📍 **對應簡報**：投影片 48（金鑰放 Secret Manager）、49（langgraph.json 是出貨單）、54「上線之後：看得見、關得住」

        下面幾格會寫出上雲端要用的檔案（**只產生檔案，不會真的 build 或部署**）：

        | 檔案 | 是什麼 |
        | --- | --- |
        | `langgraph.json` | 出貨單：告訴 LangSmith Deployment / `langgraph dev`「graph 在哪個檔案的哪個變數」 |
        | `deploy/app_graph.py` | 出貨單指向的進入點，模型金鑰從環境變數讀 |
        | `requirements.txt` | 要裝哪些套件（版本範圍釘死） |
        | `Dockerfile` | 把程式、`skills/`、`scripts/` 裝進同一個容器的食譜 |
        | `.dockerignore` | 不准裝進容器的東西：`.env`、存檔、紀錄 |
        | `deploy/preflight.py` | 上線前檢查：每一項都用程式檢查，不靠感覺 |

        ### 🤔 預測題
        上線前檢查有 8 項，你猜哪幾項會是 ⚠️（還要處理）？
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

        - ✅ 的是程式已經幫你守住的：沒有寫死的金鑰、手冊裡沒有可疑指令、`run_code` 有圍欄、agent 有 `recursion_limit`、寄信前有 `interrupt`、部署檔都在。
        - ⚠️ 的是上雲端前還要處理的：
          - **金鑰**：Colab 內建模型不用 key，但雲端一定要用正式的 API key，放進雲端的 Secret Manager（Colab 左邊 🔑「密鑰」就是它的縮小版）。
          - **checkpointer**：SQLite 只存在這一台機器，上線要換成 PostgresSaver。
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
