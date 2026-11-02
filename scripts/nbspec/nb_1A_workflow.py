from nbbuild import badge, code, ending, md, my_homework, setup, writefile

NAME = "1-A_workflow"
作業選項 = '["少了右括號", "正確的程式", "空白", "變數打錯字", "我的作業"]'


def cells():
    return [
        md(f"""
        # 1-A：Workflow，路線由程式決定

        {badge(NAME)}

        > 📍 **對應簡報**：第 1 堂「第二站：Workflow 1-A」，投影片 **16–26**（課堂時間 0:28–0:52）

        ## 這本 notebook 在做什麼

        我們要做一個「作業小助教」：輸入一段 Python 作業，輸出一份固定格式的回饋。
        這一版的**路線是你用程式畫好的**：一定先檢查語法，語法錯就解釋錯誤，語法對才給回饋，
        給完回饋還要檢查格式，不合格就退回重寫。

        LangGraph 只有三個零件，全部都是你已經會的 Python：

        | 你會的 Python | LangGraph | 手搖飲店 |
        | --- | --- | --- |
        | dict | **State** | 訂單紙 |
        | 函式 | **Node** | 工作站 |
        | 依序呼叫 | **Edge** | 箭頭 |
        | if / else | 條件邊 | 熱飲不加冰 |
        | while 迴圈 | 指回前面的邊 | 甜度不對，退回重做 |

        | 段落 | 你會做什麼 | 對應投影片 |
        | --- | --- | --- |
        | 第 1 段 | 寫出 `graph.py`、畫出流程圖，找出每個 Node 和 Edge | 17–22 |
        | 第 2 段 | 先不接 AI：換三段作業，看訂單紙一格一格被填滿 | 23–24 |
        | 第 3 段 | 把 AI 放進一個節點；調「最多重試次數」和「回饋字數上限」 | 25–26 |
        | 加碼 | 反例：沒說「往下接著寫」，訊息就被蓋掉 | 20 |

        ## 怎麼用

        1. 先執行 **「0. 環境設定」**。
        2. 每一段：**🤔 先寫預測 → ▶ 執行 → 👀 對照**。這本要改的只有表單欄位：**作業、最多重試次數、回饋字數上限**。
        3. 跑錯或斷線：從那一段的第一格重跑就好。
        """),
        setup(NAME),
        *my_homework(),
        md("""
        ---
        ## 第 1 段：LangGraph 就是把函式用箭頭接起來

        > 📍 **對應簡報**：投影片 17「把函式用箭頭接起來」、18「State」、19「Node」、21「Edge」、22「一張表記住三個零件」

        下一格會把作業小助教的程式存成 `/content/review-bot/graph.py`（不用改，直接執行）。
        想看程式的話，重點只有三種東西：

        - **State**：`class State(TypedDict)` 那一段，就是訂單紙有哪幾格（`code`、`syntax_ok`、`feedback`、`retries`…）
        - **Node**：`def check_syntax(state)` 這種函式，收訂單紙、**只回傳自己改的那幾格**
        - **Edge**：最下面 `add_edge`（做完 A 一定接 B）和 `add_conditional_edges`（看情況走哪條路，就是 if）

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
        - 條件邊有兩處：`check_syntax` 之後分成「語法 OK → give_feedback」和「語法錯 → explain_error」；`check_format` 之後分成「OK → 結束」和「不合格 → 退回 give_feedback」。
        - `check_format → give_feedback` 那條**往回指**的箭頭，就像 `while` 迴圈：甜度不對，退回重做。
        - 🏅 加分題：展開上面 `graph.py` 那一格，找出這兩條條件邊分別寫在哪一行（提示：搜尋 `add_conditional_edges`）。
        """),
        md(f"""
        ---
        ## 第 2 段：先不接 AI，三段作業先猜再跑

        > 📍 **對應簡報**：投影片 23「先不接 AI：三段作業，先猜再跑」、投影片 24「資料流：看訂單紙一格一格被填滿」

        這一段的節點都是普通 Python，沒有 AI。下面的表單有一個「作業」下拉選單，
        **請依序選「少了右括號」「正確的程式」「空白」各執行一次**。
        程式用 `stream_mode="values"` 印出每一步的**整張訂單紙**，並標出這一步新寫了哪幾格。

        ### 🤔 學習單（先寫在紙上，再執行比對）
        1. 輸入 `print("hi"`（少了右括號），會經過哪些節點？`syntax_ok` 最後是什麼？
        2. 輸入正確的程式，`feedback` 在哪一步之後才有內容？
        3. 輸入空白，會發生什麼事？
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

        > 📍 **對應簡報**：投影片 25「把 AI 放進一個節點」、投影片 26「三種設計模式，這張流程圖全都有」

        現在把 `give_feedback` 換成呼叫模型的版本（在 `graph.py` 的 `建立_give_feedback`）。
        AI 只是住在某個節點裡的一行程式：**流程圖沒變、State 沒變、箭頭沒變**。

        `check_format` 是一個純 Python 的**檢查站**：回饋一定要有「優點」和「改進」兩段、不能超過字數上限，
        不合格就退回 `give_feedback` 重寫，重寫到「最多重試次數」就停。

        ### 🤔 預測題（先寫下來，再改表單、執行）
        1. 「回饋字數上限」從 150 改成 **30**，`retries` 會變多還是變少？`format_ok` 最後會是什麼？
        2. 「最多重試次數」改成 **1**，字數上限 30 時會發生什麼事？
        3. 同一段作業跑兩次，回饋的文字會一樣嗎？格式呢？
        """),
        code(f"""
        #@title ▶ 執行：AI 寫回饋 ＋ 程式檢查格式（不合格退回重寫）
        作業 = "變數打錯字"  #@param {作業選項}
        最多重試次數 = 3  #@param {{type:"slider", min:1, max:5, step:1}}
        回饋字數上限 = 150  #@param {{type:"slider", min:20, max:300, step:10}}
        {{PREAMBLE}}
        import graph

        小助教 = graph.建立小助教(model, 最多重試次數=最多重試次數, 回饋字數上限=回饋字數上限)
        code = 取得作業(作業)

        步驟們, 上一步 = [], None
        for 第幾步, state in enumerate(小助教.stream(graph.空白訂單紙(code), stream_mode="values"), start=1):
            印出訂單紙(第幾步, state, 上一步)
            步驟們.append(state)
            上一步 = state

        print(f"\\n最後：retries = {{state['retries']}}，format_ok = {{state['format_ok']}}")
        if state.get("format_problem"):
            print(f"最後一次不合格的原因：{{state['format_problem']}}")
        print("\\n最後的回饋：")
        print(state["feedback"])
        記下(f"1-A 第 3 段：{{作業}}（AI，重試上限 {{最多重試次數}}、字數上限 {{回饋字數上限}}）", 步驟們)
        """),
        md("""
        ### 👀 你看到了什麼

        - 字數上限越小，AI 越容易寫太長被退回，`retries` 就越多；到了「最多重試次數」就停，這時 `format_ok` 可能還是 `False`。
          **不設上限的話，它可能永遠轉下去**：重寫最多幾次，是一定要鎖死在程式裡的事。
        - 同一段作業跑兩次，回饋的**文字**會不同（AI 每次都重新想），但**格式**一定有兩段、一定不超過上限，因為檢查是程式做的。
        - 這張流程圖剛好有 Anthropic〈Building effective agents〉的三種設計模式：
          - **串接（prompt chaining）**：`check_syntax → give_feedback → check_format` 固定順序的小步驟
          - **分流（routing）**：`check_syntax` 之後的分叉，先判斷類型再交給專門處理的步驟
          - **評估與修正（evaluator-optimizer）**：`check_format` 退回 `give_feedback` 的圈，產出、檢查、不合格就重做
        """),
        md("""
        ---
        ## 加碼：沒說「這一格要往下接著寫」，訊息就被蓋掉

        > 📍 **對應簡報**：投影片 20「反例：訊息被蓋掉」（必踩的雷 2）

        還記得 1-0 第 1 段嗎？模型沒有記憶，對話要整段貼回去。在 LangGraph 裡，對話放在 State 的 `messages` 那一格。
        如果沒有告訴 LangGraph「這一格要往下接著寫（`add_messages`）」，它預設會**整格覆蓋**。

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
        - 怎麼讀這行：`messages` 是一個 list，但 LangGraph 處理時不要覆蓋，要用 `add_messages` 合併。口訣：**`Annotated` 第一格是真型別，第二格是給框架看的提示。**
        - 1-B 會用到的 `MessagesState`，裡面就是這一行。
        """),
        *ending(),
    ]
