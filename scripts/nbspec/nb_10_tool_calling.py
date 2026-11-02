from nbbuild import badge, code, ending, md, project_intro, setup

NAME = "1-0_tool_calling"


def cells():
    return [
        md(f"""
        # 1-0：AI 到底怎麼「做事」？看懂 tool calling 的那張紙條

        {badge(NAME)}

        > 📍 **對應簡報**：第 1 堂「第一站：AI 怎麼做事」，投影片 **5–14**；用量選讀在附錄 **42**（課堂時間 0:10–0:35）

        ## 這本 notebook 在做什麼

        這是第 1 堂的第一本，先打地基：**AI 到底是怎麼「做事」的？**

        **模型**（LLM，大型語言模型，就是 ChatGPT、Gemini 背後那個東西）先用文字生成來理解：**依輸入產生回應**。
        單次模型呼叫只看本次提供的內容；上網與執行程式等動作，需要程式提供工具。那為什麼 ChatGPT 可以幫你跑 Python？
        答案是 **tool calling（工具呼叫）**：模型只會回一張「請幫我執行 `run_code`，參數是這段」的**紙條**，
        真正去執行的是你的 Python。

        這本 notebook 讓你親眼看到這張紙條，再看你的 Python 照著紙條做事、把結果貼回去。
        把這件事一直重複，寫成一個迴圈，就是 **agent**。

        | 段落 | 你會看到什麼 | 對應投影片 |
        | --- | --- | --- |
        | 第 1 段 | 模型沒有記憶：不把對話貼回去，它就忘了你是誰 | 6–7 |
        | 第 2 段 | 模型回傳什麼：文字與工具要求；用量細節選讀 | 8；42（用量選讀） |
        | 第 3 段 | ⭐ 模型回的那張「紙條」：`tool_calls` | 11–12 |
        | 第 4 段 | 你的 Python 照紙條去執行、把結果貼回去；寫成迴圈就是 agent | 11、13 |
        | 第 5 段 | Workflow 和 agent 差在哪（接到 1-A、1-B） | 14 |

        ## 怎麼用（這本不用改任何東西）

        1. 先執行下面的 **「0. 環境設定」**（點格子左邊的 ▶）。第一次會花大約半分鐘安裝套件。
        2. 每一段都照這個順序：**🤔 先讀預測題、把答案寫在紙上 → ▶ 執行 → 👀 對照「你看到了什麼」**。
        3. **課堂必做**：各段的主要輸出。第 2 段用量細節由講師選擇示範，不要求記欄位。
        4. 收起來的格子是程式碼，想看可以點「顯示程式碼」；看不懂也沒關係，這堂課只要看輸出。
        5. 跑錯或 Colab 斷線：從那一段的第一格重新執行就好（如果出現「找不到環境」，就先重跑「0. 環境設定」）。
        """),
        project_intro("小助教要「做事」之前的地基。模型產生回應；它想用工具時，只會回一張「紙條」說要用哪個工具，"
                      "真正去做的是你的 Python。1-A、1-B 的小助教都建立在這件事上。"),
        setup(NAME, support=["tools/__init__.py", "tools/run_code.py"]),
        md("""
        ---
        ## 第 1 段：LLM 是一台「接話機器」，而且沒有記憶

        > 📍 **對應簡報**：投影片 6「LLM 是一台接話機器」、投影片 7「LLM 沒有記憶」

        先從最基本的開始：模型到底在做什麼？

        模型每次都只看「這一次你給它的文字」，然後猜最合理的下一段，像一台接話機器。
        它不會記得上一次的對話，**除非程式把相關歷史或摘要一起傳入**。
        下面這格會問兩次「我叫什麼？」：第一次把前面的對話一起傳進去，第二次只傳這一句。

        ### 🤔 預測題（先寫在紙上再執行）
        1. 第一次（有把「我叫 Alice」一起傳進去），它答得出你的名字嗎？
        2. 第二次（只傳「我叫什麼？」），它會怎麼回答？
        """),
        code("""
        #@title ▶ 執行：有歷史 vs 沒歷史
        {PREAMBLE}
        from langchain_core.messages import AIMessage, HumanMessage

        # LLM 自己沒記憶，這裡由程式把相關歷史一起傳入
        history = [
            HumanMessage(content="我叫 Alice"),
            AIMessage(content="你好 Alice!"),
            HumanMessage(content="我叫什麼?"),
        ]
        有歷史 = model.invoke(history).text
        print("【把相關歷史傳進去】")
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
        - 同一個模型、同一個問題，差別**只在你有沒有把前面的話一起貼回去**。它不是記得你，是程式這次提供了相關紀錄。
        - 延伸：如何保存與合併對話，放在 1-A 的課後選做。
        """),
        md("""
        ---
        ## 第 2 段：模型回傳的兩種內容

        > 📍 **對應簡報**：投影片 8「Token 與 context window」、投影片 42「打開回傳物件」

        上一段知道了：模型每次都要重新讀一遍你給它的所有文字。那它一次能讀多少？

        - **Token**：模型處理文字的單位；切分方式依模型而異，用量與計費常以 token 計算。
        - **Context window**：模型一次能看的 token 上限。把它想成一張**桌子**：對話、說明、資料都要攤在桌上，東西放太多就擺不下。

        模型回傳的不只是一段文字，而是一個物件，裡面還記著這次用了多少 token。

        ### 🤔 預測題
        1. 這次模型會回文字，還是要求使用工具？（提示：我們沒有提供工具）
        2. 先記住兩個欄位：`content` 是文字，`tool_calls` 是工具要求。你預測哪個會有內容？
        """),
        code("""
        #@title ▶ 執行：先看文字與工具要求（用量細節選讀）
        顯示用量細節 = False  #@param {type:"boolean"}
        {PREAMBLE}
        resp = model.invoke("用三個字回答:Python 是什麼?")

        print("content:", repr(resp.content))
        print("tool_calls:", resp.tool_calls)
        if 顯示用量細節:
            print("type:", type(resp).__name__)
            print("usage_metadata:", resp.usage_metadata)
            print("response_metadata keys:", list(resp.response_metadata.keys()))
            if "token_count" in resp.response_metadata:
                print("\\n（這個轉接頭的 token 數是估算值，不代表供應商回報的實際用量）")

        記下("1-0 第 2 段：回傳物件", {"content": resp.content, "tool_calls": resp.tool_calls,
                                  "usage_metadata": resp.usage_metadata})
        """),
        md("""
        ### 👀 你看到了什麼

        - 這次先看 `content` 和 `tool_calls`，不用背物件型別或其他欄位。
        - `.content` / `.text` 是它說的話；`.tool_calls` 是空的 list，代表這次**沒有**要用工具（下一段提供工具後，再觀察是否有要求）。
        - **選讀**：勾選用量細節後，`usage_metadata` 顯示輸入與輸出的 token 用量。模型來源不同，可能回報實際用量或教學估算；不要拿兩者直接比較。
          某些模型的用量含推理 token，不能只用看得到的答案字數推算。
        - 不必記住數字。1-B 的 MCP 用量選讀會比較工具說明的估計長度。
        """),
        md("""
        ---
        ## 第 3 段 ⭐：模型只會「說」它想用哪個工具

        > 📍 **對應簡報**：投影片 11「Tool calling：模型只會說它想用哪個工具」、投影片 12「實際看一次：紙條長什麼樣」

        前兩段的模型只會回文字。可是小助教需要「做事」，例如真的執行學生的程式。這要怎麼辦？
        答案是 **tool calling（工具呼叫）**，分成三格漫畫：

        1. 你的 Python 告訴模型：「你有一個工具叫 `run_code`，可以執行程式」← 這就是 `bind_tools`
        2. 模型回一段文字（JSON 格式）：「我想用 `run_code`，參數是這段」← 這就是 `tool_calls`
        3. 你的 Python 看到這張紙條，**真的去執行**，再把結果貼回去給模型 ← 下一段

        - **工具（tool）**：一個普通的 Python 函式，上面加一行 `@tool`，模型就看得到它的名字和說明。
        - **JSON**：一種用大括號 `{}` 寫的資料格式，程式很容易讀。

        這一格的 `run_code` 是假的，什麼都不會執行，我們只看模型想不想叫它。

        ### 🤔 預測題
        1. 模型這次的 `content`（文字回答）會是什麼？
        2. 如果它要求使用工具，你預測會選哪個工具、交給它哪段程式？欄位名稱等輸出後再讀。
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
            print("\\n這次模型直接回答，沒有工具要求。請記錄這個結果；下方仍可對照紙條示意，不必反覆重跑。")

        記下("1-0 第 3 段：tool_calls 紙條", {"content": resp.content, "tool_calls": resp.tool_calls})
        """),
        md("""
        ### 👀 你看到了什麼

        - **有工具要求時**：先讀 `name`（選哪個工具）和 `args`（交給工具的內容）。`content` 可能是空字串。
        - **沒有工具要求時**：模型選擇直接回答。這也是有效觀察，不是操作失敗。請把它與投影片的工具要求示意對照。
        - `tool_calls` 是一個 list。先會讀工具名稱和參數就夠了；`id` 用來配對結果、`type` 標記訊息種類，留作選讀。
        - 模型**沒有**執行 `print('hi'`，它只是「建議」你去執行。要不要執行、怎麼執行，是你的程式決定的。
        - 用 Colab 內建模型時，你還會看到「原始文字」：它真的就只回了一行 JSON 文字。
          Colab 內建模型沒有原生的 tool calling，我們的小轉接頭（`review-bot/llm.py`）把工具說明寫進 prompt、請它回 JSON，
          再轉成一模一樣的 `tool_calls`。選 `gemini` 的話用的是原生 tool calling，紙條長相相同。
          這正好證明：**模型提出工具要求，做事的是你的程式。**
        """),
        md("""
        ---
        ## 第 4 段：你的 Python 照紙條去執行，再把結果貼回去

        > 📍 **對應簡報**：投影片 11 漫畫第 3 格、投影片 13「Agent ＝ 模型 ＋ 工具 ＋ 迴圈」

        上一段，模型寫好紙條就停了，什麼事都沒發生。這一段我們照著紙條真的去做。

        這次換成**真的會執行程式**的 `run_code`。它有圍欄：不准 `import os`、超過 3 秒就強制停止（1-B 會細講）。
        流程分三步：

        ① 問模型 → ② 照紙條執行，把結果包成 `ToolMessage`（「工具的執行結果」這種訊息）貼回對話 → ③ 再問一次模型

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
            print("這次模型沒有叫工具，因此步驟②沒有執行。請記錄「直接回答」，再對照投影片示意。")

        記下("1-0 第 4 段：照紙條執行再貼回去", messages)
        """),
        md("""
        ### 👀 你看到了什麼

        - ② 那一行是**你的 Python** 在執行程式，不是模型。執行結果被包成 `ToolMessage`，用 `tool_call_id` 跟紙條配對。
        - ③ 模型這次「看得到」結果了，因為我們把結果貼進了對話裡（還記得第 1 段嗎？它沒有記憶，什麼都要貼回去給它）。
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

        else:
            print("已達最多 5 圈，停止執行；這不代表作業已完成。")

        記下("1-0 第 4 段：agent 迴圈", messages)
        """),
        md("""
        ### 👀 你看到了什麼

        - 可能第 1 圈呼叫 `run_code`，第 2 圈就給回饋；也可能直接回答或再使用工具。請記錄實際圈數與停止原因。
        - 這個迴圈就是 Anthropic 和 LangChain 對 agent 的定義：**Agent ＝ 模型 ＋ 工具 ＋ 迴圈**。
        - 「最多 5 圈」是用程式給 AI 設的限制：agent 可能一直繞圈出不來，每一圈都在花錢。1-B 會看到的 `recursion_limit`（最多跑幾步就強制停）也是同一件事。
        """),
        md("""
        ---
        ## 第 5 段：Workflow 與 Agent：誰決定下一步？

        > 📍 **對應簡報**：投影片 14「Workflow 與 Agent：誰決定下一步」

        上一段的迴圈裡，下一步要不要用工具，是**模型**自己決定的，所以它是 agent。
        另一種做法，是把每一步的順序都用程式寫死，這叫 **workflow（工作流程）**。兩種各有好處：

        |  | Workflow（工作流程） | Agent（自主代理） |
        | --- | --- | --- |
        | 誰決定下一步 | 你用程式畫好的流程圖 | AI 自己決定 |
        | 像什麼 | 手搖飲店的出餐流程 | 一個拿著工具箱的實習生 |
        | 優點 | 穩定、好預測、好除錯 | 彈性大，能處理沒想過的情況 |
        | 缺點 | 只能處理你想到的情況 | 比較不穩定、可能繞路 |
        | 今天在哪裡 | **1-A_workflow** | **1-B_agent** |

        接下來 1-A 先做一個「路線由程式決定」的 workflow 小助教，1-B 再做一個自己選工具的 agent 小助教。
        """),
        *ending(),
    ]
