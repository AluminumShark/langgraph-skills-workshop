from nbbuild import badge, code, ending, md, my_homework, project_intro, setup, writefile

NAME = "1-A_workflow"
作業選項 = '["少了右括號", "正確的程式", "空白", "變數打錯字", "我的作業"]'


def cells():
    return [
        md(f"""
        # 1-A：Workflow，路線由程式決定

        {badge(NAME)}

        > 📍 **對應簡報**：第 1 堂「第二站：Workflow 1-A」，投影片 **16–28**（課堂時間 0:35–1:00）

        ## 這本 notebook 在做什麼

        這本做出第一版的作業小助教，它的**路線由程式決定**（這種做法叫 workflow）：
        先檢查語法；語法錯就直接說明並結束，**不經格式檢查**。語法通過後才產生回饋，再檢查格式；不合格且尚未達上限時，才重新產生。
        每一步做什麼、下一步去哪，都是我們事先用程式寫好的，AI 只負責其中一步。

        我們用 **LangGraph** 來寫：它是一個 Python 套件，用來**把幾個函式用箭頭接起來，讓一份資料依序流過它們**。
        這堂課先認識三個核心零件，對照你學過的 Python。用手搖飲店來想：

        | 你會的 Python | LangGraph 的名字 | 手搖飲店 | 在小助教裡 |
        | --- | --- | --- | --- |
        | dict | **State**（狀態） | 跟著飲料走的訂單紙 | 一張紙記著作業、語法對不對、回饋、已產生次數 |
        | 函式 | **Node**（節點） | 一個工作站 | `check_syntax`、`give_feedback`… 每個只做一件事 |
        | 依序呼叫 | **Edge**（邊） | 工作站之間的箭頭 | 寫完回饋，接著檢查格式 |
        | if / else | **條件邊** | 熱飲就不經過加冰站 | 語法錯就改走「解釋錯誤」 |
        | while 迴圈 | 指回前面的邊 | 甜度不對，退回重做 | 格式不合格且未達上限，重新產生 |

        | 段落 | 你會做什麼 | 對應投影片 |
        | --- | --- | --- |
        | 第 1 段 | 寫出 `graph.py`、畫出流程圖，找出每個 Node 和 Edge | 17–23 |
        | 第 2 段 | 先不接 AI：換三段作業，看訂單紙一格一格被填滿 | 24–25 |
        | 第 3 段 | 把 AI 放進一個節點；調「最多生成次數」和「回饋字數上限」 | 26–28 |
        | 課後選做 | 訊息合併規則 | 46 |

        ## 怎麼用

        1. 先執行 **「0. 環境設定」**。
        2. 每一段：**🤔 先寫預測 → ▶ 執行 → 👀 對照**。這本要改的只有表單欄位：**作業、最多生成次數、回饋字數上限**。
        3. **課堂必做**：第 1–3 段。**課後選做**：訊息合併規則。
        4. 看到 `%%writefile` 的長程式，只需執行寫入檔案；這堂課先讀輸出，不需逐行理解。
        5. 段落需要第 1 段寫出的 `graph.py`。若找不到模組，先執行環境設定和第 1 段的寫檔格；回到目前段落再跑。
        """),
        project_intro("用 LangGraph 把小助教的四個工作站（檢查語法、解釋錯誤、寫回饋、檢查格式）接成一條固定的流程，"
                      "先不用 AI 看懂資料怎麼流，再把 AI 放進「寫回饋」這一站。"),
        setup(NAME),
        *my_homework(),
        md("""
        ---
        ## 第 1 段：LangGraph 就是把函式用箭頭接起來

        > 📍 **對應簡報**：投影片 17「LangGraph：把函式用箭頭接起來」、18「作業小助教的流程：四個工作站」、20「零件一：State，跟著走的訂單紙」、21「零件二：Node，一個工作站」、22「零件三：Edge，工作站之間的箭頭」、23「一張表記住三個零件」

        先看整張流程圖：小助教的四個工作站，在程式裡長什麼樣、怎麼接起來。

        下一格會把小助教的程式存成 `/content/review-bot/graph.py`（不用改，直接執行）。
        想看程式的話，重點只有三種東西：

        - **State**：`class State(TypedDict)` 那一段，就是訂單紙上有哪幾格（見下表）。
        - **Node**：像 `def check_syntax(state)` 這樣的函式。它拿到整張訂單紙，**只回傳自己負責的那幾格**，LangGraph 會幫你寫回訂單紙。
        - **Edge**：最下面的 `add_edge`（做完 A 一定接 B），以及 `add_conditional_edges`（看情況決定下一站，就是 if）。

        | 訂單紙上的格子 | 記什麼 |
        | --- | --- |
        | `code` | 學生交的作業 |
        | `syntax_ok`、`error` | 語法對不對、錯在哪一行（還沒檢查時是 `None`） |
        | `feedback` | 給學生的回饋 |
        | `format_ok`、`format_problem` | 回饋格式合不合格、不合格的原因 |
        | `retries` | 回饋已經寫了幾次 |

        > 「語法」是什麼？就是 Python 的文法規則，例如括號要成對、`def` 那一行最後要有冒號。
        > `check_syntax` 只檢查文法、**不執行**程式。`print(unknown_name)` 文法正確，但執行時會因為名稱未定義而出錯。
        > 語法正確、執行成功、符合題目要求，是三個不同的檢查。本段只做語法檢查；1-B 才加入執行工具。

        ### 🤔 預測題
        1. 流程圖上會有幾個 Node（工作站）？
        2. 哪幾條箭頭是「條件邊」（會分岔的）？
        3. 有沒有一條箭頭是往回指的？它像 Python 的哪個語法？
        """),
        writefile("graph.py"),
        code("""
        #@title ▶ 執行：畫出作業小助教的流程圖
        {PREAMBLE}
        import graph

        小助教 = graph.建立小助教()        # 先不給 model：give_feedback 用固定文字
        顯示流程圖(小助教)

        g = 小助教.get_graph()
        print("Node（工作站）：", [n for n in g.nodes if n not in ("__start__", "__end__")])
        print("Edge（箭頭）：")
        for e in g.edges:
            print(f"  {e.source} → {e.target}{'   ← 條件邊（if）' if e.conditional else ''}")
        """),
        md("""
        ### 👀 你看到了什麼

        - 4 個工作站：`check_syntax`、`explain_error`、`give_feedback`、`check_format`（`__start__`、`__end__` 是起點和終點）。
        - 條件邊有兩處：`check_syntax` 之後分成「語法 OK → give_feedback」和「語法錯 → explain_error」；`check_format` 之後分成「OK 或達上限 → 結束」和「不合格且未達上限 → 退回 give_feedback」。
        - `check_format → give_feedback` 那條**往回指**的箭頭，就像 `while` 迴圈：甜度不對，退回重做。
        - 🏅 加分題：在上面 `graph.py` 那一格裡，找出這兩條條件邊分別寫在哪一行（提示：找 `add_conditional_edges`）。
        """),
        md(f"""
        ---
        ## 第 2 段：先不接 AI，三段作業先猜再跑

        > 📍 **對應簡報**：投影片 24「先不接 AI：三段作業，先猜再跑」、投影片 25「資料流：看訂單紙一格一格被填滿」

        上一段看到了流程圖的「形狀」。這一段實際丟作業進去，看資料怎麼一站一站流過。

        這一段的節點都是普通 Python，還沒有 AI，`give_feedback` 先回一段固定的文字。
        下面的表單有一個「作業」下拉選單，**請依序選「少了右括號」「正確的程式」「空白」各執行一次**。

        程式用 `stream_mode="values"` 來跑：意思是**每走完一站，就把整張訂單紙印出來一次**，
        而且會標出這一步新寫了哪幾格，你就能看到訂單紙一格一格被填滿。

        ### 🤔 學習單（先寫在紙上，再執行比對）
        1. 輸入 `print("hi"`（少了右括號），會經過哪些節點？`syntax_ok` 最後是什麼？
        2. 輸入正確的程式，`feedback` 在哪一步之後才有內容？
        3. 本系統規定「空白視為未交作業」，會走寫回饋還是解釋錯誤的分支？
        """),
        code(f"""
        #@title ▶ 執行：看訂單紙一格一格被填滿（先不接 AI）
        作業 = "少了右括號"  #@param {作業選項}
        {{PREAMBLE}}
        import graph

        小助教 = graph.建立小助教()        # 不給 model：give_feedback 用固定文字
        code = 取得作業(作業)
        print(f"作業：{{code!r}}\\n")

        步驟們, 上一步 = [], None
        for 第幾步, state in enumerate(小助教.stream(graph.空白訂單紙(code), stream_mode="values"), start=1):
            印出訂單紙(第幾步, state, 上一步)
            步驟們.append(state)
            上一步 = state

        print("\\n最後的回饋：")
        print(state["feedback"])
        記下(f"1-A 第 2 段：{{作業}}（不接 AI）", 步驟們)
        """),
        md("""
        ### 👀 你看到了什麼

        1. **少了右括號**：`check_syntax` 寫入 `syntax_ok: False` 和錯在哪一行 → 條件邊走 `explain_error` → 寫入 `feedback` → 結束。完全沒經過 `give_feedback`。
        2. **正確的程式**：`syntax_ok: True` → `give_feedback` 寫入 `feedback` 和 `retries: 1`（第 3 步之後才有回饋）→ `check_format` 寫入 `format_ok: True` → 結束。
        3. **空白**：空白其實是「合法」的 Python，但我們在 `check_syntax` 裡多寫了一個 `if`：空白就當成沒交作業。這就是「能寫成 if 的事，寫進程式」。
        - 每一步只有一兩格改變：**每個節點只寫自己負責的那幾格**，其他格原封不動往下傳。
        - 以後看任何 LangGraph 程式，先問兩件事：State 有哪幾格？每個節點寫哪一格？
        """),
        md("""
        ---
        ## 第 3 段：把 AI 放進一個節點

        > 📍 **對應簡報**：投影片 26「把 AI 放進一個節點」、27「流程結束了，回饋合格了嗎？」、投影片 28「回頭看小助教的流程圖：三種設計模式全都有」

        前兩段的 `give_feedback` 都只回固定文字。這一段把它換成真的 AI，其他都不動。

        現在 `give_feedback` 會呼叫模型來寫回饋（程式在 `graph.py` 的 `建立_give_feedback`）。
        AI 只是住在某一個節點裡的一行程式：**流程圖沒變、State 沒變、箭頭也沒變**。

        `check_format` 是一個純 Python 的**檢查站**：檢查「優點：」「改進：」標籤順序、兩段非空內容及字數；不判定內容是否正確。
        不合格且未達上限時，就退回 `give_feedback` 重新產生。`retries` 記著回饋寫了幾次，寫到「最多生成次數」就不再退回，直接結束。

        表單有兩個數字可以調：

        - **最多生成次數**：包含第一次在內，回饋最多產生幾次（設 3 就是最多產生 3 次）
        - **回饋字數上限**：回饋最多幾個字，超過就不合格

        ### 🤔 預測題（先寫下來，再改表單、執行）
        1. 「回饋字數上限」從 150 改成 **30**，`retries` 會變多還是變少？`format_ok` 最後會是什麼？
        2. 「最多生成次數」改成 **1**，字數上限 30 時會發生什麼事？
        3. 同一段作業跑兩次，回饋的文字與 `format_ok` 是否一樣？請如實記錄。
        4. 程式結束了，但 `format_ok=False`，是否已達到格式要求？
        """),
        code(f"""
        #@title ▶ 執行：AI 寫回饋 ＋ 程式檢查格式（不合格退回重寫）
        作業 = "變數打錯字"  #@param {作業選項}
        最多生成次數 = 3  #@param {{type:"slider", min:1, max:5, step:1}}
        回饋字數上限 = 150  #@param {{type:"slider", min:20, max:300, step:10}}
        {{PREAMBLE}}
        import graph

        小助教 = graph.建立小助教(model, 最多重試次數=最多生成次數, 回饋字數上限=回饋字數上限)
        code = 取得作業(作業)

        步驟們, 上一步 = [], None
        for 第幾步, state in enumerate(小助教.stream(graph.空白訂單紙(code), stream_mode="values"), start=1):
            印出訂單紙(第幾步, state, 上一步)
            步驟們.append(state)
            上一步 = state

        print(f"\\n最後：已產生 {{state['retries']}} 次回饋，format_ok = {{state['format_ok']}}")
        if not state["syntax_ok"]:
            print("停止原因：作業未通過語法／空白檢查，已說明原因。")
        elif state["format_ok"]:
            print("停止原因：回饋通過格式檢查。")
        else:
            print("停止原因：已達產生次數上限，回饋仍未通過格式檢查，需要人工處理。")
        if state.get("format_problem"):
            print(f"最後一次不合格的原因：{{state['format_problem']}}")
        print("\\n最後的回饋：")
        print(state["feedback"])
        記下(f"1-A 第 3 段：{{作業}}（AI，產生上限 {{最多生成次數}}、字數上限 {{回饋字數上限}}）", 步驟們)
        """),
        md("""
        ### 👀 你看到了什麼

        - 字數上限較小時，回饋可能更常被退回；請觀察 `retries`，不保證每次都增加；到了「最多生成次數」就停，這時 `format_ok` 可能還是 `False`。
          **不設上限的話，它可能永遠轉下去**：回饋最多產生幾次，需要由程式限制。
        - 同一段作業跑兩次，回饋的文字可能相同，也可能不同。由 `give_feedback` 產生的回饋會進入格式檢查；語法錯誤的說明走另一個分支。流程**不保證模型一定改到合格**。
        - `format_ok=True` 才表示通過這裡的格式檢查；達到產生次數上限也會結束，但可能仍不合格。**流程結束和任務達標是兩件事。**
        - 回頭看整張流程圖：它剛好包含了三種常見的「流程擺法」（設計模式，出自 Anthropic 的文章〈Building effective agents〉）：
          - **串接（prompt chaining）**：`check_syntax → give_feedback → check_format` 固定順序的小步驟
          - **分流（routing）**：`check_syntax` 之後的分叉，先判斷類型再交給專門處理的步驟
          - **評估與修正（evaluator-optimizer）**：`check_format` 退回 `give_feedback` 的圈，產出、檢查、不合格就重做
        """),
        md("""
        ---
        ## 課後選做：沒說「這一格要往下接著寫」，訊息就被蓋掉

        > 📍 **對應簡報**：投影片 46「附錄選做：如何合併 State 裡的訊息」（課後選做）

        前面訂單紙上的每一格，都只放一個值（例如檢查後的 `syntax_ok` 是 True 或 False），新的值直接蓋掉舊的就好。
        但如果某一格要放「一整串對話」呢？

        模型需要程式提供相關對話（1-0 第 1 段）。在 LangGraph 裡，對話放在 State 的 `messages` 那一格。
        如果沒有告訴 LangGraph「這一格要往下接著寫」（用 `add_messages`），它預設會**整格蓋掉**，前面的對話就不見了。

        ### 🤔 預測題
        輸入一則訊息「我叫小明」，經過一個會呼叫模型的節點之後，`messages` 裡會有幾則訊息？兩種寫法各是幾則？
        """),
        code("""
        #@title ▶ 執行：BadState（覆蓋） vs 有 add_messages（接著寫）
        {PREAMBLE}
        from typing import Annotated, TypedDict
        from langgraph.graph import END, START, StateGraph
        from langgraph.graph.message import add_messages

        class BadState(TypedDict):
            messages: list                               # ← 預設行為是「覆蓋」

        class GoodState(TypedDict):
            messages: Annotated[list, add_messages]      # ← 告訴 LangGraph：這一格要往下接著寫

        def chatbot(state) -> dict:
            response = model.invoke(state["messages"])
            return {"messages": [response]}

        for 名稱, StateClass in [("BadState（沒寫 add_messages）", BadState), ("GoodState（有 add_messages）", GoodState)]:
            builder = StateGraph(StateClass)
            builder.add_node("chatbot", chatbot)
            builder.add_edge(START, "chatbot")
            builder.add_edge("chatbot", END)
            結果 = builder.compile().invoke({"messages": [{"role": "user", "content": "我叫小明"}]})
            print(f"{名稱}：messages 有 {len(結果['messages'])} 則")
            for m in 結果["messages"]:
                print(f"   [{m.type if hasattr(m, 'type') else m['role']}] {(m.text if hasattr(m, 'text') else m['content'])[:60]}")
            記下(f"1-A 加碼：{名稱}", 結果)
        """),
        md("""
        ### 👀 你看到了什麼

        - `BadState` 只剩 **1 則**：使用者說的「我叫小明」被模型的回覆蓋掉了。
        - 加上 `Annotated[list, add_messages]` 就有 **2 則**：使用者的話和模型的回覆都在。
        - 怎麼讀這行：`messages` 是一個 list，但 LangGraph 處理時不要覆蓋，要用 `add_messages` 合併。口訣：**`Annotated` 的第一項是資料型別，後面是給框架的額外資訊。**
        - 1-B 課後選做裡的 `MessagesState`，裡面就是這一行。
        """),
        *ending(),
    ]
