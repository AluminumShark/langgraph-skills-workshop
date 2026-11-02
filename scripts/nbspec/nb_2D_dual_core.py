from nbbuild import badge, code, ending, md, setup, writefile

NAME = "2-D_dual_core"
作業選項 = '["命名不一致", "變數打錯字", "正確的程式", "少了右括號"]'
需求選項 = '["幫第一次交作業的初學者看看", "期中考正式評分，請嚴格審查"]'
SUPPORT = [
    "tools/__init__.py", "tools/run_code.py", "tools/read_spec.py", "tools/check_naming.py",
    "graph.py", "skill_loader.py", "spec.md",
    "skills/friendly-feedback/SKILL.md", "skills/strict-review/SKILL.md",
    "skills/naming-check/SKILL.md", "skills/naming-check/scripts/check_naming.py",
]


def cells():
    return [
        md(f"""
        # 2-D：雙核 demo，外面鎖住順序、裡面放手判斷

        {badge(NAME)}

        > 📍 **對應簡報**：第 2 堂「第三站：資安與雙核」，投影片 **24–27**（課堂時間 1:06–1:15，講師示範）

        ## 這本 notebook 在做什麼

        把上週和今天學的東西接起來，就是課名裡的「**雙拼**」：

        - **外面**是 1-A 的 workflow（順序鎖死）：一定先檢查語法、一定檢查格式，不合格退回重寫。
        - **裡面**的 `give_feedback` 是 1-B 的小 agent（放手判斷）：
          手冊用 2-A 的「溫和鼓勵」或「嚴格審查」，工具箱裡有 2-B 的命名檢查腳本、`run_code`、`read_spec`，
          要不要跑命名檢查、要不要讀題目，由它自己決定。
        - 兩個新零件一句話帶過：`skill_loader` 節點看所有手冊的**名片**挑一本；腳本外面包一層 `@tool` 就進了工具箱。
        - 最後用 **checkpointer ＋ thread_id** 把每一步的 State 存起來：中斷了也能接著跑。

        | 段落 | 你會看到什麼 | 對應投影片 |
        | --- | --- | --- |
        | 第 1 段 | 寫出 `dual_core.py`，畫出雙核的流程圖 | 24 |
        | 第 2 段 | 完整跑一次：外層一站一站走，裡面的 agent 自己選工具 | 24–25 |
        | 第 3 段 | 中斷：跑到一半先停，State 存進存檔 | 25 |
        | 第 4 段 | ⭐ 接著跑：同一個 thread_id 接著跑、換一個 thread_id 從空白開始 | 25 |
        | 第 5 段 | 一個 thread 的 State 歷程（每一步的存檔） | 25 |
        | 第 6 段 | 選做：驗證怎麼做，改一句話看通過率 40% → 100% | 26–27 |

        ## 怎麼用

        1. 先執行 **「0. 環境設定」**（這一格也會把 2-A 的手冊、2-B 的腳本、1-B 的工具準備好）。
        2. 這本要改的只有 **thread_id**（第 3、4 段的表單）。其他表單想改也可以。
        3. 每一段：**🤔 先寫預測 → ▶ 執行 → 👀 對照**；跑錯或斷線就從那一段的第一格重跑。
        """),
        setup(NAME, support=SUPPORT),
        md("""
        ---
        ## 第 1 段：雙核長什麼樣

        > 📍 **對應簡報**：投影片 24「雙核：把上週的流程和今天的手冊接起來」、投影片 25「兩個新零件」

        下一格寫出 `dual_core.py`（不用改，直接執行）。想看程式的話，重點在三個地方：

        - `建立雙核小助教`：外層的節點和箭頭，跟 1-A 幾乎一樣，只多了 `skill_loader` 這一站
        - `建立_skill_loader`：把所有手冊的**名片**給模型看，挑一本，內文放進 State 的 `skill`
        - `建立_give_feedback`：裡面用 `create_agent` 做一個小 agent，手冊當 system prompt，工具箱有 `check_naming`、`run_code`、`read_spec`

        ### 🤔 預測題
        1. 外層流程圖上，`skill_loader` 會放在哪兩站中間？
        2. 流程圖上看得到裡面那個 agent 會叫哪些工具嗎？
        """),
        writefile("dual_core.py"),
        code("""
        #@title ▶ 執行：畫出雙核的外層流程圖
        {PREAMBLE}
        import dual_core

        小助教 = dual_core.建立雙核小助教(model)
        顯示流程圖(小助教)
        """),
        md("""
        ### 👀 你看到了什麼

        - `skill_loader` 在 `check_syntax`（語法 OK）和 `give_feedback` 中間：先檢查語法、再挑手冊、再給回饋、再檢查格式。**這個順序是程式鎖死的。**
        - 流程圖上看不到 agent 會叫哪些工具，因為那是 `give_feedback` 這一站**裡面**的事，由 AI 當下決定。
          外面鎖住不能錯的事，裡面放手讓它判斷：這就是雙拼。
        """),
        md(f"""
        ---
        ## 第 2 段：完整跑一次

        > 📍 **對應簡報**：投影片 24「雙核」講師 demo

        ### 🤔 預測題
        1. 作業選「命名不一致」、需求選「初學者」，`skill_loader` 會挑哪一本手冊？換成「期中考」呢？
        2. 裡面的 agent 會用 `check_naming` 嗎？會不會也用 `run_code`？
        3. 如果它寫的回饋太長，誰會把它退回去？
        """),
        code(f"""
        #@title ▶ 執行：雙核小助教，一站一站跑
        作業 = "命名不一致"  #@param {作業選項}
        批改需求 = "幫第一次交作業的初學者看看"  #@param {需求選項} {{allow-input: true}}
        {{PREAMBLE}}
        import time
        import dual_core

        小助教 = dual_core.建立雙核小助教(model, checkpointer=dual_core.開存檔())
        config = {{"configurable": {{"thread_id": f"完整示範-{{time.strftime('%H%M%S')}}"}}}}
        state = dual_core.逐站執行(小助教, {{"code": 取得作業(作業), "request": 批改需求, "retries": 0}}, config)

        print("\\n========== 結果 ==========")
        print("挑中的手冊：", state.get("skill_name"))
        print("裡面的 agent 用了哪些工具：", state.get("tools_used") or "（沒有用工具）")
        print(f"retries = {{state.get('retries')}}，format_ok = {{state.get('format_ok')}}")
        print("\\n回饋：")
        print(state.get("feedback"))
        記下(f"2-D 第 2 段：完整跑一次（{{作業}}／{{批改需求}}）", {{k: v for k, v in state.items() if k != "skill"}})
        """),
        md("""
        ### 👀 你看到了什麼

        - 外層每次都照同樣的順序走：`check_syntax → skill_loader → give_feedback → check_format`。換作業、換需求都一樣。
        - `skill_loader` 只看名片挑手冊：需求寫「初學者」大多挑 `friendly-feedback`，寫「期中考、嚴格」大多挑 `strict-review`。
        - 裡面的 agent 用了哪些工具、用幾次，**每次可能不同**；但它最後交出的回饋一定會被 `check_format` 用程式檢查，不合格就退回重寫。
        - 試著把「少了右括號」丟進去：根本不會走到 agent，`check_syntax` 之後就直接去 `explain_error`，一個 token 都不花。
        """),
        md("""
        ---
        ## 第 3 段：中斷，跑到一半先停

        > 📍 **對應簡報**：投影片 25「還有一個叫 checkpointer 的東西能把 State 存起來、中斷後接著跑」

        **checkpointer** 會在每一站跑完時把整張訂單紙（State）存起來；**thread_id** 是這份存檔的編號，像置物櫃的號碼。
        這裡的存檔放在 `/content/review-bot/checkpoints.sqlite` 這個檔案裡，所以重跑 cell、甚至重新啟動執行階段，存檔都還在。

        下面這格會在 `give_feedback` **前面**故意停下來（模擬跑到一半斷線）。

        ### 🤔 預測題
        停下來的時候，存檔裡的 State 會有哪幾格已經填好？`feedback` 有內容嗎？
        """),
        code(f"""
        #@title ▶ 執行：跑到 give_feedback 前面就先停
        thread_id = "小明的作業"  #@param {{type:"string"}}
        作業 = "命名不一致"  #@param {作業選項}
        批改需求 = "幫第一次交作業的初學者看看"  #@param {需求選項} {{allow-input: true}}
        {{PREAMBLE}}
        import dual_core

        小助教 = dual_core.建立雙核小助教(model, checkpointer=dual_core.開存檔(), interrupt_before=["give_feedback"])
        config = {{"configurable": {{"thread_id": thread_id}}}}
        if 小助教.get_state(config).values:
            print(f"（提醒：thread_id「{{thread_id}}」本來就有存檔了，這次會在同一份存檔上再跑一次）\\n")

        state = dual_core.逐站執行(小助教, {{"code": 取得作業(作業), "request": 批改需求, "retries": 0}}, config)
        存檔 = 小助教.get_state(config)
        print(f"\\n📂 thread_id「{{thread_id}}」的存檔：")
        印出狀態({{k: v for k, v in 存檔.values.items() if k not in ("skill", "code")}})
        print("下一站（還沒跑）：", 存檔.next)
        記下(f"2-D 第 3 段：中斷（thread_id={{thread_id}}）", {{"next": list(存檔.next), **{{k: v for k, v in 存檔.values.items() if k != "skill"}}}})
        """),
        md("""
        ### 👀 你看到了什麼

        - 停在 `give_feedback` 前面：`syntax_ok`、`skill_name` 已經填好，`feedback` 還是空的。
        - 「下一站」是 `('give_feedback',)`：存檔不只記得 State，也記得**流程走到哪裡**。
        """),
        md(f"""
        ---
        ## 第 4 段 ⭐：接著跑，還是從空白開始？

        > 📍 **對應簡報**：投影片 25；第 2 堂最低完成標準「2-D 換 thread_id 重跑並說明 State 有沒有保留」

        下面這格會先用 thread_id 去存檔裡找：找到「停在一半」的存檔就**接著跑**；找不到就**從空白開始**。

        ### 🤔 預測題（兩輪，答案寫在紙上）
        1. thread_id 保持 **小明的作業**（跟第 3 段一樣），執行。它會從哪一站開始？`skill_name` 需要重挑嗎？
        2. 把 thread_id 改成 **小華的作業**，再執行一次。這次 State 裡有什麼？
        """),
        code(f"""
        #@title ▶ 執行：用 thread_id 找存檔，接著跑或從空白開始
        thread_id = "小明的作業"  #@param {{type:"string"}}
        作業 = "命名不一致"  #@param {作業選項}
        批改需求 = "幫第一次交作業的初學者看看"  #@param {需求選項} {{allow-input: true}}
        {{PREAMBLE}}
        import dual_core

        小助教 = dual_core.建立雙核小助教(model, checkpointer=dual_core.開存檔())
        config = {{"configurable": {{"thread_id": thread_id}}}}
        存檔 = 小助教.get_state(config)

        if not 存檔.values:
            print(f"🆕 thread_id「{{thread_id}}」沒有任何存檔：State 是空白的，從頭開始跑\\n")
            state = dual_core.逐站執行(小助教, {{"code": 取得作業(作業), "request": 批改需求, "retries": 0}}, config)
            狀況 = "沒有存檔，從空白開始"
        elif 存檔.next:
            print(f"📂 找到 thread_id「{{thread_id}}」的存檔：停在 {{存檔.next}} 前面，接著跑")
            print("   存檔裡已經有：", {{k: v for k, v in 存檔.values.items() if k in ("syntax_ok", "skill_name", "retries")}}, "\\n")
            state = dual_core.逐站執行(小助教, None, config)      # 輸入 None ＝ 從存檔接著跑
            狀況 = "找到存檔，接著跑"
        else:
            print(f"✅ thread_id「{{thread_id}}」已經跑完了，存檔內容如下（想重來就換一個 thread_id）\\n")
            state = 存檔.values
            狀況 = "已經跑完"

        print("\\n========== 現在的 State ==========")
        印出狀態({{k: v for k, v in state.items() if k not in ("skill", "code")}})
        記下(f"2-D 第 4 段：{{狀況}}（thread_id={{thread_id}}）", {{k: v for k, v in state.items() if k != "skill"}})
        """),
        md("""
        ### 👀 你看到了什麼

        - **同一個 thread_id**：直接從 `give_feedback` 接著跑，`check_syntax` 和 `skill_loader` 沒有重跑，`skill_name` 是存檔裡原本那一本。**State 沒有丟失。**
        - **換一個 thread_id**：存檔裡什麼都沒有，State 從空白開始，整條流程從 `check_syntax` 重新跑。
        - 同一個 thread_id 跑完之後再執行一次，會看到「已經跑完」：存檔一直都在，除非你換編號。
        - 這就是原提案說的「受控節點正確觸發 Skill，且 State 未丟失」。正式上線時通常把 SQLite 換成資料庫（例如 Postgres），做法一樣。
        """),
        md("""
        ---
        ## 第 5 段：一個 thread 的 State 歷程

        > 📍 **對應簡報**：投影片 25（checkpointer）

        checkpointer 不只存「最新的」State，而是**每一站跑完都存一份**。下面把同一個 thread_id 的每一份存檔列出來。

        ### 🤔 預測題
        「小明的作業」跑完整條流程，總共會有幾份存檔？
        """),
        code("""
        #@title ▶ 執行：列出一個 thread_id 的每一份存檔
        thread_id = "小明的作業"  #@param {type:"string"}
        {PREAMBLE}
        import dual_core

        小助教 = dual_core.建立雙核小助教(model, checkpointer=dual_core.開存檔())
        config = {"configurable": {"thread_id": thread_id}}
        歷史 = list(小助教.get_state_history(config))
        if not 歷史:
            print(f"thread_id「{thread_id}」沒有任何存檔。先跑第 3、4 段。")
        for snap in reversed(歷史):
            v = snap.values
            步 = snap.metadata.get("step")
            print(f"{'收到輸入' if 步 == -1 else f'第 {步} 步'}｜下一站：{snap.next or '（結束）'}｜"
                  f"syntax_ok={v.get('syntax_ok')}  skill={v.get('skill_name')}  "
                  f"retries={v.get('retries')}  format_ok={v.get('format_ok')}  有回饋={'是' if v.get('feedback') else '否'}")
        記下(f"2-D 第 5 段：State 歷程（thread_id={thread_id}）",
             [{"step": s.metadata.get("step"), "next": list(s.next),
               **{k: val for k, val in s.values.items() if k not in ("skill", "code")}} for s in reversed(歷史)])
        """),
        md("""
        ### 👀 你看到了什麼

        - 每跑完一站就多一份存檔，所以可以看到訂單紙一格一格被填滿的過程，跟 1-A 的 `stream_mode="values"` 很像，只是這次是**存在檔案裡**的。
        - 這就是 harness 裡的「Replay」：失敗的時候，可以回到中間某一步重新試，不用每次從頭跑。
        """),
        md("""
        ---
        ## 第 6 段（選做）：驗證怎麼做？把「應該怎麼做」寫成程式能判斷的規則

        > 📍 **對應簡報**：投影片 26「驗證怎麼做」、投影片 27「改一句話，量化看到變好：40% → 100%」

        把「agent 應該怎麼做」寫成五個考題（eval case）：**第一個該叫哪個工具**、**最後的回覆要有哪些字**。
        考卷是程式在改，不是人在看。我們比較兩個版本的 system prompt：

        - **baseline**：沒有特別交代順序
        - **v2**：多一句「一定要先呼叫 check_syntax 再回饋」

        ⚠️ 這一段會呼叫模型大約 20–30 次，免費額度不多的話**課後再跑**：把表單的「要跑驗證嗎」打勾再執行。

        ### 🤔 預測題
        baseline 五題會過幾題？加了一句之後呢？會不會剛好 100%？
        """),
        code("""
        #@title ▶ 執行（選做）：五個考題，比較 baseline 和 v2 的通過率
        要跑驗證嗎 = False  #@param {type:"boolean"}
        {PREAMBLE}
        from langchain.agents import create_agent
        from langchain.tools import tool
        import graph
        from tools.read_spec import read_spec
        from tools.run_code import run_code

        @tool
        def check_syntax(code: str) -> str:
            \"\"\"檢查 Python 作業的語法對不對。回傳「語法 OK」或錯在第幾行。\"\"\"
            結果 = graph.check_syntax({"code": code})
            return "語法 OK" if 結果["syntax_ok"] else f"語法錯誤：{結果['error']}"

        # 五個考題：第一個該叫誰、最後要有什麼
        EVAL_CASES = [
            {"id": "001_must_check_syntax_first", "作業": "正確的程式", "must_call_first": "check_syntax", "must_contain_in_final": ["優點", "改進"]},
            {"id": "002_handle_syntax_error", "作業": "少了右括號", "must_call_first": "check_syntax", "must_contain_in_final": ["語法"]},
            {"id": "003_wrong_variable", "作業": "變數打錯字", "must_call_first": "check_syntax", "must_contain_in_final": ["改進"]},
            {"id": "004_messy_indent", "作業": "縮排亂掉", "must_call_first": "check_syntax", "must_contain_in_final": ["改進"]},
            {"id": "005_naming", "作業": "命名不一致", "must_call_first": "check_syntax", "must_contain_in_final": ["優點", "改進"]},
        ]

        def evaluate_one(考生, case):
            inputs = {"messages": [{"role": "user", "content": f"幫我批改這份作業：\\n```python\\n{取得作業(case['作業'])}\\n```"}]}
            events = list(考生.stream(inputs, stream_mode="updates"))
            msgs = [m for e in events for u in e.values() for m in (u or {}).get("messages", [])]
            tc = [c["name"] for m in msgs for c in (getattr(m, "tool_calls", None) or [])]   # 工具呼叫順序
            final = next((m.text for m in reversed(msgs) if m.type == "ai" and not m.tool_calls), "")
            reasons = []
            if not tc:
                reasons.append(f"沒呼叫任何 tool（預期 {case['must_call_first']}）")
            elif tc[0] != case["must_call_first"]:
                reasons.append(f"第一個 tool 是 {tc[0]}，預期 {case['must_call_first']}")
            for kw in case["must_contain_in_final"]:
                if kw not in final:
                    reasons.append(f"最終回覆缺關鍵字 {kw!r}")
            return {"id": case["id"], "passed": not reasons, "reasons": reasons, "tool_calls": tc}

        基本 = "你是 Python 作業小助教，用繁體中文給初學者回饋。回饋分兩段：第一段以「優點：」開頭，第二段以「改進：」開頭。"
        版本們 = {
            "baseline（沒交代順序）": 基本,
            "v2（加一句「先呼叫 check_syntax 再回饋」）": 基本 + "一定要先呼叫 check_syntax 檢查語法，再回饋。",
        }

        if not 要跑驗證嗎:
            print("這一段是選做：把上面表單的「要跑驗證嗎」打勾，再執行一次。")
        else:
            成績 = {}
            for 版本, system_prompt in 版本們.items():
                考生 = create_agent(model, tools=[check_syntax, run_code, read_spec], system_prompt=system_prompt)
                print(f"===== {版本} =====")
                結果們 = [evaluate_one(考生, case) for case in EVAL_CASES]
                for r in 結果們:
                    print(f"[{'PASS' if r['passed'] else 'FAIL'}] {r['id']}  tool_calls={r['tool_calls']}")
                    for why in r["reasons"]:
                        print(f"        - {why}")
                通過 = sum(r["passed"] for r in 結果們)
                print(f"通過 {通過}/{len(結果們)} ({通過 / len(結果們):.0%})\\n")
                成績[版本] = f"{通過}/{len(結果們)}"
            記下("2-D 第 6 段：eval 通過率", 成績)
        """),
        md("""
        ### 👀 你看到了什麼

        - baseline 通常有幾題的第一個工具不是 `check_syntax`：沒交代，它就照自己的想法走。
        - 加一句之後通過率明顯上升，但**不一定永遠 100%**：模型偶爾還是會不聽話。有客觀的分數可以比，才知道改了是不是真的變好。
        - 再往前一步：把「第一個一定要 check_syntax」直接寫成**外層流程的順序**、把「一定要有優點和改進」寫成 `check_format` 節點，
          就不用事後考、也不用花 token。這正是第 1、2 段的雙核做的事（也是 2-B 放法 C 的論點）。
        """),
        *ending(),
    ]
