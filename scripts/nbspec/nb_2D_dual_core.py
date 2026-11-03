from nbbuild import badge, code, ending, md, project_intro, setup, writefile

NAME = "2-D_dual_core"
作業選項 = '["命名不一致", "變數打錯字", "正確的程式", "少了右括號"]'
需求選項 = '["幫第一次交作業的初學者看看", "期中考正式評分，請嚴格審查"]'
SUPPORT = [
    "tools/__init__.py", "tools/run_code.py", "tools/check_naming.py",
    "graph.py", "skill_loader.py",
    "skills/friendly-feedback/SKILL.md", "skills/strict-review/SKILL.md",
    "skills/naming-check/SKILL.md", "skills/naming-check/scripts/check_naming.py",
]


def cells():
    return [
        md(f"""
        # 2-D：流程與 Agent 整合

        {badge(NAME)}

        > 📍 **對應簡報**：第 2 堂「第三站：資安與整合」，投影片 **25–28**；選做 **43–44**（課堂時間 1:08–1:23）
        """),
        project_intro("把小助教的流程、agent、手冊和腳本接在一起，做成結合固定流程與 Agent 的小助教，並讓它中斷之後還能接著跑。"),
        md("""
        ## 這本 notebook 在做什麼

        小助教可以用兩種方式做：

        - **流程（workflow）**：路線用程式畫好（LangGraph）。先檢查語法；語法通過才寫回饋、檢查格式。不合格可退回重寫，達次數上限就停止。
          分支與順序明確；遇到未處理的情況，仍需補上流程規則。（第 1 堂 1-A）
        - **agent**：只給 AI 目標和一個工具箱，讓它自己決定用哪些工具、用幾次。很有彈性，但每次走的路可能不同。（第 1 堂 1-B）

        這本把固定流程與 agent 接在一起，就是課名裡「**雙拼**」的做法：

        - **外面**是流程（分支與順序由程式控制）：先檢查語法；通過才進 agent；回饋必須檢查格式，達生成上限會停止，可能仍不合格。
        - **裡面**的 `give_feedback`（寫回饋）這一站，是一個小 agent（由 AI 判斷）：
          手冊用 2-A 的「溫和鼓勵」或「嚴格審查」，工具箱裡有 2-B 的命名檢查腳本 `check_naming`、`run_code`（執行作業）、`read_spec`（讀題目要求）。
          要不要檢查命名、要不要讀題目，由它自己決定。
        - 題目與作業在新執行時配對，題目存入 State 的 `spec`。`read_spec` 只讀這份 State 的題目，不讀共用 `spec.md`；續跑仍使用原存檔的題目。
        - 新零件 `skill_loader`：流程裡的一站，看所有手冊的**名片**（`SKILL.md` 開頭的 name 和 description），挑一本，把內文交給下一站。
        - 最後用 **checkpointer**（自動存檔）和 **thread_id**（存檔的編號）把每一步的 **State**（在各站之間傳遞的那張「訂單紙」，一個 dict）存起來：
          中斷了也能接著跑。

        | 段落 | 你會看到什麼 | 對應投影片 |
        | --- | --- | --- |
        | 第 1 段 | 寫出 `dual_core.py`，畫出整合後的流程圖 | 25–26 |
        | 第 2 段 | 完整跑一次：外層一站一站走，裡面的 agent 自己選工具 | 25–26 |
        | 第 3 段 | 中斷：跑到一半先停，State 存進存檔 | 27 |
        | 第 4 段 | ⭐ 接著跑：同一個 thread_id 接著跑、換一個 thread_id 從空白開始 | 27–28 |
        | 第 5 段 | 一個 thread 的 State 歷程（每一步的存檔） | 28 |
        | 第 6 段 | 選做：評測（eval），純 agent 的提示詞比較；記錄實際通過率 | 43–44 |

        ## 怎麼用

        1. 先執行 **「0. 環境設定」**（這一格會準備**全新預設副本**；不會匯入你在前一本 notebook 修改的手冊、腳本或工具）。
        2. 這本要改的只有 **thread_id**（第 3、4 段的表單）。其他表單想改也可以。
           選做：想套用自己在 2-A 改過的手冊，先完成第 1–4 段，再用左側「檔案」面板打開 `/content/review-bot/skills/friendly-feedback/SKILL.md`，
           貼上你備份的內容並存檔（之後不要重跑「0. 環境設定」，否則會被覆寫），再用全新的 thread_id 從第 2 段重跑。
        3. 環境設定與準備格會覆寫其中的手冊、腳本與程式，請先保留自行修改的內容；它們不會刪除既有的 SQLite 存檔。
        4. 每一段：**🤔 先寫預測 → ▶ 執行 → 👀 對照**；第 3、4 段先看存檔狀態再動作；想重新實驗請換一個從未使用的 thread_id。課堂約 15 分鐘，先完成第 1–4 段，第 5 段快速看歷程，第 6 段留課後。
        """),
        setup(NAME, support=SUPPORT),
        md("""
        ---
        ## 第 1 段：流程與 Agent 如何配合

        > 📍 **對應簡報**：投影片 25「流程與 Agent 整合：串接手冊與工具」、投影片 26「流程與 Agent 的接點：載入手冊、提供工具」

        先看整合後的流程圖。下一格寫出 `dual_core.py`（不用改，直接執行）。
        檔名 `dual_core`（雙核）是舊名，指的就是投影片 25 的「流程與 Agent 整合」，也就是課名裡的「雙拼」。想看程式的話，重點在三個地方：

        - `建立整合小助教`：外層的節點（每一站）和箭頭，跟 1-A 的流程幾乎一樣，只多了 `skill_loader` 這一站
        - `建立_skill_loader`：把所有手冊的**名片**給模型看，挑一本，把內文放進 State 的 `skill`
        - `建立_give_feedback`：裡面用 `create_agent`（一行做出 agent 的寫法）做一個小 agent，
          手冊當它的 system prompt（每次都放在最前面、告訴 AI 要遵守什麼的那段話），工具箱有 `check_naming`、`run_code`、`read_spec`

        ### 🤔 預測題
        1. 外層流程圖上，`skill_loader` 會放在哪兩站中間？
        2. 流程圖上看得到裡面那個 agent 會叫哪些工具嗎？
        """),
        writefile("dual_core.py"),
        code("""
        #@title ▶ 執行：畫出整合版小助教的外層流程圖
        {PREAMBLE}
        import dual_core

        小助教 = dual_core.建立整合小助教(model)
        顯示流程圖(小助教)
        """),
        md("""
        ### 👀 你看到了什麼

        - `skill_loader` 在 `check_syntax`（語法 OK）和 `give_feedback` 中間：語法通過後才挑手冊、給回饋、檢查格式；語法錯誤直接解釋後結束。**這條分支的順序由流程控制。**
        - 流程圖上看不到 agent 會叫哪些工具，因為那是 `give_feedback` 這一站**裡面**的事，由 AI 當下決定。
          外面保證執行必要檢查，裡面保留判斷空間：這就是雙拼。
        """),
        md(f"""
        ---
        ## 第 2 段：完整跑一次

        > 📍 **對應簡報**：投影片 25「流程與 Agent 整合：串接手冊與工具」

        上一段只畫了圖，這一段真的跑一次。輸出會一站一站印出來：`▶` 後面是站名，底下縮排的是這一站寫進 State 的欄位。

        本課有三種結果，請先分清楚「結束」與「成功」：

        | 路徑 | 輸出與狀態 |
        | --- | --- |
        | 語法錯誤 | 程式產生「語法：／改進：」，不進 agent，也不跑格式檢查 |
        | 語法通過、回饋格式合格 | 回饋採「優點：／改進：」，format_ok=True |
        | 生成到上限仍不合格 | 保留最後一版供檢查，format_ok=False，不把它當成功結果 |

        ### 🤔 預測題
        1. 作業選「命名不一致」、需求選「初學者」，`skill_loader` 會挑哪一本手冊？換成「期中考」呢？
        2. 裡面的 agent 會用 `check_naming` 嗎？會不會也用 `run_code`？如果用了 `check_naming`，回饋會把腳本找到的 6 項都寫進去嗎？
        3. 如果它寫的回饋太長，誰會把它退回去？
        """),
        code(f"""
        #@title ▶ 執行：整合版小助教，一站一站跑
        作業 = "命名不一致"  #@param {作業選項}
        批改需求 = "幫第一次交作業的初學者看看"  #@param {需求選項} {{allow-input: true}}
        回饋字數上限 = 250  #@param {{"type":"integer"}}
        #@markdown **最多生成次數（含第一次）**
        最多生成次數 = 3  #@param {{"type":"integer"}}
        {{PREAMBLE}}
        import time
        import dual_core

        小助教 = dual_core.建立整合小助教(model, checkpointer=dual_core.開存檔(),
                                         最多重試次數=最多生成次數, 回饋字數上限=回饋字數上限)
        config = {{"configurable": {{"thread_id": f"完整示範-{{time.time_ns()}}"}}}}
        state = dual_core.逐站執行(小助教, dual_core.作業輸入(作業, 取得作業(作業), 批改需求), config)

        print("\\n========== 結果 ==========")
        print("本次作業：", 作業)
        print("本次題目要求：", state.get("spec"))
        print("挑中的手冊：", state.get("skill_name"))
        print("裡面的 agent 用了哪些工具：", state.get("tools_used") or "（沒有用工具）")
        print(f"已生成回饋 {{state.get('retries', 0)}} 次；format_ok = {{state.get('format_ok')}}")
        print("停止原因：", "語法未通過" if not state.get("syntax_ok") else
              "格式通過" if state.get("format_ok") else "已達生成上限，格式仍不合格")
        print("\\n回饋：")
        print(state.get("feedback"))
        記下(f"2-D 第 2 段：完整跑一次（{{作業}}／{{批改需求}}）", {{k: v for k, v in state.items() if k != "skill"}})
        """),
        md("""
        ### 👀 你看到了什麼

        - 語法通過：`check_syntax → skill_loader → give_feedback → check_format`；格式不合格且還沒到生成上限才回到 `give_feedback`。
        - 語法未通過：`check_syntax → explain_error → 結束`，不選手冊、不呼叫模型，也不經過 check_format。只把作業改成「少了右括號」觀察這條分支；之後先改回「命名不一致」。
        - 手冊選擇、工具使用與回饋內容仍由模型決定。必要檢查有執行，不代表結果一定合格。
        - 這裡只印出用了哪些工具，看不到工具回傳什麼。腳本對「命名不一致」會列出 6 項（2-B 第 1 段看過），請和回饋對照：回饋可能全部列出，也可能只挑幾項，字數上限也會影響它挑多少。**用了工具，不代表回饋完整轉述工具結果。**
        - 選做上限對照：作業先恢復「命名不一致」，需求固定初學者，最多生成次數設為 **1**、字數上限 **250**，執行一次作為基準。第二輪**只把字數上限改為 1**。兩段格式無法塞進一字，應看到「達上限，格式仍不合格」。做完恢復 **250／3**。
        - `retries` 是內部欄位名稱，這份實作每寫一次回饋就加一，**包括第一稿**；課堂把它讀成「已生成次數」。
        """),
        md("""
        ---
        ## 第 3 段：中斷，跑到一半先停

        > 📍 **對應簡報**：投影片 27「先暫停一次，再用同一個 ID 接續」

        第 2 段一口氣跑完了。可是真實世界會斷線、會當機，所以這一段故意跑到一半停下來，看 State 有沒有被存起來。

        **checkpointer** 會在每一站跑完時把整張訂單紙（State）存起來；**thread_id** 是這份存檔的編號，像置物櫃的號碼。
        這裡的存檔放在 `/content/review-bot/checkpoints.sqlite` 這個檔案裡，只要這個檔案還在，重跑 cell 就能讀回。Colab 刪除或更換執行階段可能移除本機檔案；檔案不在時就沒有舊存檔。

        本段先固定使用語法正確的「命名不一致」與初學者需求，並保存對應的平均值題目。使用全新 thread_id 時，下面這格會在 `give_feedback` **前面**暫停。這是可預期的教學中斷，不是實際模擬斷線後的所有恢復情況；語法錯誤會走另一條分支，無法停在這裡。

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

        小助教 = dual_core.建立整合小助教(model, checkpointer=dual_core.開存檔(), interrupt_before=["give_feedback"])
        config = {{"configurable": {{"thread_id": thread_id}}}}
        舊存檔 = 小助教.get_state(config)
        if 舊存檔.values and not 舊存檔.values.get("spec"):
            raise SystemExit("這是未保存題目的舊版存檔。請在第 3、4 段換成同一個全新 thread_id，再做暫停與接續；原存檔保留。")
        if 舊存檔.values:
            print(f"此編號已有存檔：{{'尚未完成' if 舊存檔.next else '已完成'}}。本格保留原內容，不重新送入作業。")
            print("要接著跑請去第 4 段；要重設實驗，請在第 3、4 段填同一個全新編號，例如「小明的作業-2」。")
        else:
            dual_core.逐站執行(小助教, dual_core.作業輸入(作業, 取得作業(作業), 批改需求), config)
        存檔 = 小助教.get_state(config)
        print(f"\\n📂 thread_id「{{thread_id}}」的存檔：")
        印出狀態({{k: v for k, v in 存檔.values.items() if k not in ("skill", "code")}})
        print("下一站（還沒跑）：", 存檔.next)
        記下(f"2-D 第 3 段：中斷（thread_id={{thread_id}}）", {{"next": list(存檔.next), **{{k: v for k, v in 存檔.values.items() if k != "skill"}}}})
        """),
        md("""
        ### 👀 你看到了什麼

        - 使用全新編號和預設作業時，停在 `give_feedback` 前面：`syntax_ok`、`skill_name` 已經填好，`feedback` 還是空的。
        - 題目也已存入 `spec`：這份平均值作業不會讀到前一本留下的加法題。續跑使用存檔，不採當前表單的新題目。舊版沒有 `spec` 的存檔請換全新編號，不刪原檔。
        - 「下一站」是 `('give_feedback',)`：存檔不只記得 State，也記得**流程走到哪裡**。
        """),
        md(f"""
        ---
        ## 第 4 段 ⭐：接著跑，還是從空白開始？

        > 📍 **對應簡報**：投影片 27–28；最低完成標準：區分未完成續跑、完成取回、新 ID 從頭執行

        上一段停在一半，存檔裡留下一份「還沒跑完」的 State。這一段用 thread_id 去存檔裡找：
        找到停在一半的存檔就**接著跑**；已完成就**只讀既有結果**；全新編號才**從空白開始**。

        | 編號狀態 | 會做什麼 | 是否重讀本格作業欄位 |
        | --- | --- | --- |
        | 舊編號，尚未完成 | 接續待執行節點 | 否，使用存檔中的作業 |
        | 舊編號，已完成 | 顯示完成結果 | 否，不重新批改 |
        | 從未用過的新編號 | 從 check_syntax 開始 | 是 |

        ### 🤔 預測題（三輪，答案寫在紙上）

        配合簡報分兩次操作：第 27 頁先做第一輪；確認接續成功後，翻到第 28 頁才做第二、三輪。
        1. thread_id 保持 **小明的作業**（跟第 3 段一樣），執行。它會從哪一站開始？`skill_name` 需要重挑嗎？
        2. 保持同一個編號再執行一次：已完成的結果會重新批改嗎？
        3. 把 thread_id 改成**從未用過**的「小華的作業」，再執行一次。這次從哪站開始？
        """),
        code(f"""
        #@title ▶ 執行：用 thread_id 找存檔，接著跑或從空白開始
        thread_id = "小明的作業"  #@param {{type:"string"}}
        作業 = "命名不一致"  #@param {作業選項}
        批改需求 = "幫第一次交作業的初學者看看"  #@param {需求選項} {{allow-input: true}}
        {{PREAMBLE}}
        import dual_core

        小助教 = dual_core.建立整合小助教(model, checkpointer=dual_core.開存檔())
        config = {{"configurable": {{"thread_id": thread_id}}}}
        存檔 = 小助教.get_state(config)

        if 存檔.values and not 存檔.values.get("spec"):
            raise SystemExit("這是未保存題目的舊版存檔。請回第 3 段，用全新 thread_id 建立暫停狀態，再填相同 ID 接續。")
        if not 存檔.values:
            print(f"🆕 thread_id「{{thread_id}}」沒有任何存檔：State 是空白的，從頭開始跑\\n")
            state = dual_core.逐站執行(小助教, dual_core.作業輸入(作業, 取得作業(作業), 批改需求), config)
            狀況 = "沒有存檔，從空白開始"
        elif 存檔.next:
            print(f"📂 找到 thread_id「{{thread_id}}」的存檔：停在 {{存檔.next}} 前面，接著跑")
            print("   存檔裡已經有：", {{k: v for k, v in 存檔.values.items() if k in ("syntax_ok", "skill_name", "retries")}}, "\\n")
            state = dual_core.逐站執行(小助教, None, config)      # 輸入 None ＝ 從存檔接著跑
            狀況 = "找到存檔，接著跑"
        else:
            print(f"📂 thread_id「{{thread_id}}」已經跑完了，存檔內容如下（想重來就換一個 thread_id）\\n")
            state = 存檔.values
            狀況 = "已經跑完"

        print("\\n========== 現在的 State ==========")
        print("存檔中的題目：", state.get("spec"))
        印出狀態({{k: v for k, v in state.items() if k not in ("skill", "code")}})
        print("最新存檔的下一站：", 小助教.get_state(config).next or "（流程已結束）")
        print("結果判讀：", "語法未通過，未進行回饋格式檢查" if state.get("syntax_ok") is False else
              "回饋格式通過；內容仍需檢視" if state.get("format_ok") else "回饋格式未通過，流程結束不代表成功")
        記下(f"2-D 第 4 段：{{狀況}}（thread_id={{thread_id}}）", {{k: v for k, v in state.items() if k != "skill"}})
        """),
        md("""
        ### 👀 你看到了什麼

        - **同一個尚未完成的 thread_id**：從 `give_feedback` 接著跑，`check_syntax` 和 `skill_loader` 沒有重跑，`skill_name` 是存檔裡原本那一本。**State 沒有丟失。**
        - **換一個從未使用的 thread_id**：存檔裡什麼都沒有，State 從空白開始，整條流程從 `check_syntax` 重新跑。
        - 這裡「已完成」只表示流程沒有下一站，不表示作業或回饋合格。相同 thread_id 跑完之後再執行一次，會看到「已經跑完」：這次只顯示原結果。換編號只是查另一份存檔，並不刪除原本那份。
        - **完成檢查**：指出輸出中的存檔編號、下一站與 skill_name，說明三輪是否重新挑選手冊。要從空白重設，兩格一起換全新編號。
        """),
        md("""
        ---
        ## 第 5 段：一個 thread 的 State 歷程

        > 📍 **對應簡報**：投影片 28（完成後再查看 State 歷史）

        第 4 段看的是「最新的」那份存檔。其實 checkpointer **每一站跑完都存一份**，下面把同一個 thread_id 的每一份存檔列出來。

        ### 🤔 預測題
        找出哪份存檔第一次出現 skill_name、哪份第一次出現 feedback。重寫次數會影響存檔數量。
        """),
        code("""
        #@title ▶ 執行：列出一個 thread_id 的每一份存檔
        thread_id = "小明的作業"  #@param {type:"string"}
        {PREAMBLE}
        import dual_core

        小助教 = dual_core.建立整合小助教(model, checkpointer=dual_core.開存檔())
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

        - 每跑完一站就多一份存檔，所以看得到訂單紙一格一格被填滿的過程。這和 1-A 一步一步印出整張訂單紙很像，只是這次**存在檔案裡**。
        - 這格是**查看歷史**，不會重新執行任何節點。Replay（從特定 checkpoint 重新執行）是另一種操作，這本沒有示範。
        """),
        md("""
        ---
        ## 第 6 段（選做）：評測（eval）怎麼做？把「應該怎麼做」寫成程式能判斷的規則

        > 📍 **對應簡報**：選做投影片 43「選做：用程式檢查純 agent 的表現」、44「選做：固定考題，比較修改前後」

        這個附錄換了一個系統：**純 agent**，不是前面第 1–5 段的整合版小助教；它把 check_syntax 也放進可選工具箱。若沒有外層流程，怎麼知道它有沒有照規矩做？答案是**考它**。

        把「agent 應該怎麼做」寫成程式能自動批改的考題，叫做 **eval**（評測）。這裡有五個考題（eval case），
        每題各自綁定對應的題目要求，避免平均值題讀到加法規格。每題檢查兩件事：**第一個該叫哪個工具**、**最後的回覆要有哪些字**。考卷是程式在改，不是人在看。我們比較兩個版本的 system prompt：

        - **baseline**（原本的版本，拿來當比較的基準）：沒有特別交代順序
        - **v2**：多一句「一定要先呼叫 check_syntax 再回饋」（這裡的 `check_syntax` 是把小助教的語法檢查包成一把工具）

        這裡的「評測」是給 agent 出考題，和第 2 堂投影片 35 檢查每份回饋的「驗證 agent」是兩件事。表單「要跑驗證嗎」指的就是要不要跑這組評測。

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
        import dual_core
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

        def evaluate_one(system_prompt, case):
            read_spec = dual_core.建立_read_spec(dual_core.範例題目[case["作業"]])
            考生 = create_agent(model, tools=[check_syntax, run_code, read_spec], system_prompt=system_prompt)
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
                print(f"===== {版本} =====")
                結果們 = [evaluate_one(system_prompt, case) for case in EVAL_CASES]
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

        - 先記下 baseline 與 v2 各過幾題、失敗原因。baseline 也可能全部通過，請照實記錄。
        - v2 可能提升、相同或降低；五題的一次結果只代表這次測試。關鍵字命中也不代表回饋正確，還需人工抽查內容。
        - 再往前一步：把「第一個一定要 check_syntax」直接寫成**外層流程的順序**、把「一定要有優點和改進」寫成 `check_format` 節點，
          能讓流程按分支執行必要檢查：語法錯誤不進回饋與格式檢查；語法通過後的回饋才檢查格式。檢查本身由程式判定。整合版仍要測分支、上限、存檔接續與回饋品質，並非不需要 eval。
        """),
        *ending(),
    ]
