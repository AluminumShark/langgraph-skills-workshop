from nbbuild import badge, code, ending, md, setup

NAME = "1-0_tool_calling"


def cells():
    return [
        md(f"""
        # 1-0：AI 到底怎麼「做事」？看懂 tool calling 的那張紙條

        {badge(NAME)}

        > 📍 **對應簡報**：第 1 堂「第一站：AI 怎麼做事」，投影片 **5–15**（課堂時間 0:10–0:28）

        ## 這本 notebook 在做什麼

        模型（LLM）其實只會一件事：**接話**。它不會記得你、不會上網、也不會執行程式。
        那為什麼 ChatGPT 可以幫你跑 Python？答案就是 **tool calling（工具呼叫）**：
        模型只會回一張「請幫我執行 `run_code`，參數是這段」的**紙條**，真正去執行的是你的 Python。

        這本 notebook 讓你親眼看到這張紙條，再看你的 Python 照著紙條做事、把結果貼回去。
        把這件事寫成迴圈，就是 **agent**。

        | 段落 | 你會看到什麼 | 對應投影片 |
        | --- | --- | --- |
        | 第 1 段 | 模型沒有記憶：不把對話貼回去，它就忘了你是誰 | 6–7 |
        | 第 2 段 | 打開模型回傳的物件：這次用了幾個 token | 8–9 |
        | 第 3 段 | ⭐ 模型回的那張「紙條」：`tool_calls` | 12–13 |
        | 第 4 段 | 你的 Python 照紙條去執行、把結果貼回去；寫成迴圈就是 agent | 12、14 |
        | 第 5 段 | Workflow 和 agent 差在哪（接到 1-A、1-B） | 15 |

        ## 怎麼用（這本不用改任何東西）

        1. 先執行下面的 **「0. 環境設定」**（點格子左邊的 ▶）。第一次會花大約半分鐘安裝套件。
        2. 每一段都照這個順序：**🤔 先讀預測題、把答案寫在紙上 → ▶ 執行 → 👀 對照「你看到了什麼」**。
        3. 收起來的格子是程式碼，想看可以點「顯示程式碼」；看不懂也沒關係，這堂課只要看輸出。
        4. 跑錯或 Colab 斷線：從那一段的第一格重新執行就好（如果出現「找不到環境」，就先重跑「0. 環境設定」）。
        """),
        setup(NAME, support=["tools/__init__.py", "tools/run_code.py"]),
        md("""
        ---
        ## 第 1 段：LLM 是一台「接話機器」，而且沒有記憶

        > 📍 **對應簡報**：投影片 6「LLM 是一台接話機器」、投影片 7「LLM 沒有記憶」

        模型每次都只看「這一次你給它的文字」，猜最合理的下一段。它不會記得上一次對話，
        **除非你把整段對話再貼給它一次**。下面這格會問兩次「我叫什麼？」：
        第一次把前面的對話一起傳進去，第二次只傳這一句。

        ### 🤔 預測題（先寫在紙上再執行）
        1. 第一次（有把「我叫 Alice」一起傳進去），它答得出你的名字嗎？
        2. 第二次（只傳「我叫什麼？」），它會怎麼回答？
        """),
        code("""
        #@title ▶ 執行：有歷史 vs 沒歷史
        {PREAMBLE}
        from langchain_core.messages import AIMessage, HumanMessage

        # LLM 自己沒記憶，你必須把整段對話歷史塞給它
        history = [
            HumanMessage(content="我叫 Alice"),
            AIMessage(content="你好 Alice!"),
            HumanMessage(content="我叫什麼?"),
        ]
        有歷史 = model.invoke(history).text
        print("【把整段歷史傳進去】")
        print(有歷史)

        # 反例：不傳 history，只傳最後一句
        沒歷史 = model.invoke("我叫什麼?").text
        print("\\n【只傳最後一句】")
        print(沒歷史)

        記下("1-0 第 1 段：有歷史 vs 沒歷史", {"有歷史": 有歷史, "沒歷史": 沒歷史})
        """),
        md("""
        ### 👀 你看到了什麼

        - 有歷史的那次，它說得出「Alice」；只傳最後一句的那次，它不知道你是誰。
        - 同一個模型、同一個問題，差別**只在你有沒有把前面的話一起貼回去**。它不是記得你，是你每次把整本對話紀錄再貼給它一次。
        - 伏筆：等一下 1-A 會看到 LangGraph 把對話包成一個 list，而且要「往下接著寫」、不能整格覆蓋，原因就是這個。
        """),
        md("""
        ---
        ## 第 2 段：打開回傳物件，這次桌上用了幾個 token？

        > 📍 **對應簡報**：投影片 8「Token 與 context window」、投影片 9「打開回傳物件」

        **Token** 是模型讀字的最小單位（中文大約一到兩個字一個 token）。
        **Context window** 是它一次能看的 token 上限，像一張**桌子**，東西放太多就擺不下。
        模型回傳的不只是一段文字，而是一個物件，裡面記著這次花了多少 token。

        ### 🤔 預測題
        1. 我們只叫它「用三個字回答」，你猜 `output_tokens`（它寫回來的字）是多少？
        2. `tool_calls` 會是什麼？（提示：這次我們沒給它任何工具）
        """),
        code("""
        #@title ▶ 執行：把模型回傳的物件整個打開看
        {PREAMBLE}
        resp = model.invoke("用三個字回答:Python 是什麼?")

        print("type:", type(resp).__name__)
        print("content:", repr(resp.content))
        print("tool_calls:", resp.tool_calls)
        print("usage_metadata:", resp.usage_metadata)
        print("response_metadata keys:", list(resp.response_metadata.keys()))
        if "token_count" in resp.response_metadata:
            print("\\n（Colab 內建模型不會回報用量，上面的 token 數是用字數估算的）")

        記下("1-0 第 2 段：回傳物件", {"content": resp.content, "tool_calls": resp.tool_calls,
                                  "usage_metadata": resp.usage_metadata})
        """),
        md("""
        ### 👀 你看到了什麼

        - `type` 是 `AIMessage`：模型回的是一則「訊息」，不只是字串。
        - `.content` / `.text` 是它說的話；`.tool_calls` 是空的 list，代表這次**沒有**要用工具（下一段就會有東西了）。
        - `usage_metadata` 裡，`input_tokens` 是你放到桌上的字，`output_tokens` 是它寫回來的字。
          用講師的 Gemini key 時，常會看到 output 遠大於三個字：有些模型會先「自己想一想」（reasoning），想的過程也佔桌子。
        - 記住這個數字。1-B 最後接 MCP 時，會回來看工具說明一次佔掉多少桌面。
        """),
        md("""
        ---
        ## 第 3 段 ⭐：模型只會「說」它想用哪個工具

        > 📍 **對應簡報**：投影片 12「Tool calling：模型只會說它想用哪個工具」、投影片 13「實際看一次：紙條長什麼樣」

        三格漫畫：
        1. 你的 Python 告訴模型：「你有一個工具叫 `run_code`，可以執行程式」← 這就是 `bind_tools`
        2. 模型回一段文字（JSON）：「我想用 `run_code`，參數是這段」← 這就是 `tool_calls`
        3. 你的 Python 看到這張紙條，**真的去執行**，把結果貼回去給模型 ← 下一段

        這一格的 `run_code` 是假的，什麼都不會執行，我們只看模型想不想叫它。

        ### 🤔 預測題
        1. 模型這次的 `content`（文字回答）會是什麼？
        2. `tool_calls` 裡面會有哪幾個欄位？`args` 裡會放什麼？
        3. 模型有沒有真的執行 `print('hi'`？
        """),
        code("""
        #@title ▶ 執行：看模型回的那張「紙條」
        {PREAMBLE}
        from langchain_core.tools import tool

        @tool
        def run_code(code: str) -> str:
            \"\"\"執行一段 Python 作業，回傳輸出或錯誤訊息。\"\"\"
            return "（這裡先不真的執行，只看模型想不想叫它）"

        model_with_tools = model.bind_tools([run_code])     # 漫畫第 1 格：告訴模型你有工具
        resp = model_with_tools.invoke("這段作業跑得起來嗎？print('hi'")

        print("content:", repr(resp.content))
        print("tool_calls:", resp.tool_calls)              # 漫畫第 2 格：那張 JSON 紙條

        if "raw_text" in resp.response_metadata:
            print("\\n📝 模型實際回的原始文字：")
            print(resp.response_metadata["raw_text"])
        if not resp.tool_calls:
            print("\\n這次模型決定不用工具、直接回答。再執行一次這格看看（每次結果可能不同）。")

        記下("1-0 第 3 段：tool_calls 紙條", {"content": resp.content, "tool_calls": resp.tool_calls})
        """),
        md("""
        ### 👀 你看到了什麼

        - `content` 是**空字串**：模型不打算用文字回答。
        - `tool_calls` 是一個 list，每張紙條有四個欄位：`name`（叫哪個工具）、`args`（參數）、`id`（之後用來配對結果）、`type`（固定是 `tool_call`）。
        - 模型**沒有**執行 `print('hi'`，它只是「建議」你去執行。要不要執行、怎麼執行，是你的程式決定的。
        - 用 Colab 內建模型時，你還會看到「原始文字」：它真的就只回了一行 JSON 文字。
          Colab 內建模型沒有原生的 tool calling，我們的小轉接頭（`review-bot/llm.py`）把工具說明寫進 prompt、請它回 JSON，
          再轉成一模一樣的 `tool_calls`。選 `gemini` 的話用的是原生 tool calling，紙條長相相同。
          這正好證明：**模型從頭到尾只是在「說」它想用什麼工具，做事的是你的程式。**
        """),
        md("""
        ---
        ## 第 4 段：你的 Python 照紙條去執行，再把結果貼回去

        > 📍 **對應簡報**：投影片 12 漫畫第 3 格、投影片 14「Agent ＝ 模型 ＋ 工具 ＋ 迴圈」

        這次換成**真的會執行程式**的 `run_code`（它有圍欄：不准 `import os`、超過 3 秒就停，1-B 會細講）。
        流程分三步：① 問模型 → ② 照紙條執行、把結果包成 `ToolMessage` 貼回去 → ③ 再問一次模型。

        ### 🤔 預測題
        1. 第 ③ 步模型看得到 `print(1+1)` 的執行結果嗎？它會說什麼？
        2. 如果把 ①②③ 一直重複，什麼時候該停下來？
        """),
        code("""
        #@title ▶ 執行：① 問模型 → ② 真的去執行 → ③ 把結果貼回去再問
        {PREAMBLE}
        from langchain_core.messages import HumanMessage, ToolMessage
        from tools.run_code import run_code     # 真的會執行程式的版本（有圍欄）

        model_with_tools = model.bind_tools([run_code])
        messages = [HumanMessage("這段作業跑得起來嗎？請實際執行看看再告訴我結果。\\n```python\\nprint(1+1)\\n```")]

        # ① 問模型
        resp = model_with_tools.invoke(messages)
        messages.append(resp)
        print("① 模型的紙條：", resp.tool_calls or "（沒有紙條，直接回答了）")

        # ② 你的 Python 照紙條真的去執行，把結果包成 ToolMessage 貼回去
        for call in resp.tool_calls:
            result = run_code.invoke(call["args"])
            print(f"② 你的 Python 執行了 {call['name']}，結果：{result}")
            messages.append(ToolMessage(content=result, tool_call_id=call["id"], name=call["name"]))

        # ③ 再問一次模型：這次它看得到執行結果了
        if resp.tool_calls:
            final = model_with_tools.invoke(messages)
            messages.append(final)
            print("③ 模型看到結果後說：", final.text or final.tool_calls)
        else:
            print("這次模型沒有叫工具。再執行一次這格看看。")

        記下("1-0 第 4 段：照紙條執行再貼回去", messages)
        """),
        md("""
        ### 👀 你看到了什麼

        - ② 那一行是**你的 Python** 在執行程式，不是模型。執行結果被包成 `ToolMessage`，用 `tool_call_id` 跟紙條配對。
        - ③ 模型這次「看得到」結果了，因為我們把它貼進對話裡（還記得第 1 段嗎？它沒有記憶，什麼都要貼回去）。
        - 把 ①②③ 寫成迴圈，一直轉到模型說「不用工具了」為止，就是 **agent**。下面這格就是那個迴圈，不到 10 行。
        """),
        md("""
        ### 🤔 預測題
        下面的迴圈最多轉 5 圈。你猜它會轉幾圈就停？為什麼要設「最多 5 圈」？
        """),
        code("""
        #@title ▶ 執行：把三步寫成迴圈，就是 agent（模型 ＋ 工具 ＋ 迴圈）
        {PREAMBLE}
        from langchain_core.messages import HumanMessage, ToolMessage
        from tools.run_code import run_code

        model_with_tools = model.bind_tools([run_code])
        messages = [HumanMessage("幫我看這段作業能不能跑，有錯就告訴我錯在哪。\\n```python\\nx = 3\\nprint(x * y)\\n```")]

        for 第幾圈 in range(1, 6):                          # 最多轉 5 圈，避免停不下來
            resp = model_with_tools.invoke(messages)        # 問模型
            messages.append(resp)
            if not resp.tool_calls:                         # 它說不用工具了 → 結束
                print(f"第 {第幾圈} 圈：模型說不用工具了，最後回答：\\n{resp.text}")
                break
            for call in resp.tool_calls:                    # 它說要用工具 → 執行、把結果貼回去
                result = run_code.invoke(call["args"])
                print(f"第 {第幾圈} 圈：模型叫了 {call['name']} → {result}")
                messages.append(ToolMessage(content=result, tool_call_id=call["id"], name=call["name"]))

        記下("1-0 第 4 段：agent 迴圈", messages)
        """),
        md("""
        ### 👀 你看到了什麼

        - 通常轉 2 圈：第 1 圈它叫 `run_code`，看到 `NameError` 後，第 2 圈就直接給回饋、不再叫工具。
        - 這個迴圈就是 Anthropic 和 LangChain 對 agent 的定義：**Agent ＝ 模型 ＋ 工具 ＋ 迴圈**。
        - 「最多 5 圈」是用程式給 AI 設的限制：agent 可能一直繞圈出不來，每一圈都在花錢。1-B 會看到 LangGraph 的 `recursion_limit` 做的是同一件事。
        """),
        md("""
        ---
        ## 第 5 段：兩種 agent，誰決定下一步？

        > 📍 **對應簡報**：投影片 15「兩種 agent：誰決定下一步」

        |  | Workflow（工作流程） | Agent（自主代理） |
        | --- | --- | --- |
        | 誰決定下一步 | 你用程式畫好的流程圖 | AI 自己決定 |
        | 像什麼 | 手搖飲店的出餐流程 | 一個拿著工具箱的實習生 |
        | 優點 | 穩定、好預測、好除錯 | 彈性大，能處理沒想過的情況 |
        | 缺點 | 只能處理你想到的情況 | 比較不穩定、可能繞路 |
        | 今天在哪裡 | **1-A_workflow** | **1-B_agent** |

        剛才第 4 段的迴圈，下一步要不要用工具是**模型**決定的，所以它是 agent。
        接下來 1-A 先做一個「路線由程式決定」的 workflow，1-B 再回來做一個真正自己選工具的 agent。
        """),
        *ending(),
    ]
