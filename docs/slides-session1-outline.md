# 第 1 堂投影片大綱：什麼是 agent，用 LangGraph 做一個

共 30 張，每張列出「畫面上放什麼」和「講者怎麼說」。方括號數字對應文末參考來源。

實際的 HTML 簡報（`slides/session1.html`）共 45 張：多了各站的分隔頁，以及「今天的路線」、「這兩堂要做的東西：作業小助教」、「作業小助教的流程：四個工作站」、「LLM 沒有記憶」、「打開回傳物件」、「實際看一次 tool_calls」、「反例：訊息被蓋掉」、「run_code 的圍欄」、「docstring」、「展開 create_agent」、「參考來源」這幾張。每張標題後面括號裡是 HTML 頁碼，notebook 裡的「📍 對應簡報」用的也是 HTML 頁碼。

**標籤**：簡報上只放學生看得懂的提示，講師的帶法寫在講者備註（N 鍵）。「**Colab**」＝學生在 notebook 的哪一段自己跑；「**紙上**」＝寫在學習單上。

## 開場（0:00–0:10）

### 投影片 1｜封面（HTML 第 1 張）

- **畫面**：從 LangGraph 到 Skills：結構化與非結構化 Agent 的雙拼指南｜第 1 堂：什麼是 agent，用 LangGraph 做一個；講者李維、柯宥圻；NTU AI Club；日期 2026-11-09（週一）；右側「課程資料」QR code 指向 https://github.com/AluminumShark/langgraph-skills-workshop
- **講者**：自我介紹 30 秒，請大家先打開 notebook 連結並「複製到雲端硬碟」

### 投影片 2｜今天你會學到三件事（HTML 第 3 張）

- **畫面**：
  1. AI agent 到底是什麼：模型 + 工具 + 迴圈
  2. 兩種 agent：路線由程式決定（workflow）vs 路線由 AI 決定（agent）
  3. 什麼時候該把 AI 鎖在流程裡，什麼時候該放手
- **畫面下方一行字**：今天不用寫程式，你只要「先猜、再跑、再對答案」
- **講者**：只要會 dict、函式、if、while 就跟得上，其他今天從零講

### 投影片 3｜同一個 AI，兩種結局（HTML 第 4 張）

- **畫面**：左右兩欄對照同一段有 bug 的作業
  - 左：直接問 AI「幫我看這段作業」，跑兩次 → 兩次長短不同、格式不同，有一次沒發現語法錯誤
  - 右：交給「作業小助教」，跑兩次 → 一定先檢查語法、回饋格式一樣、寫不好會自己重寫
- **講者**：現場各跑兩次。結論一句話：AI 是同一個，差別在外面包了什麼。今天就是在學外面那一層。

### 投影片 3a｜這兩堂要做的東西：作業小助教（HTML 第 5 張）

- **畫面左**：你交給它一段 Python 作業（`def add(a, b): total = a + b; return summ`）→ 它回你一份固定格式的回饋：「優點：…」「改進：…」兩段；作業有語法錯時，改成告訴你錯在第幾行
- **畫面右**：為什麼拿它當練習？三種東西都用得到
  1. 順序不能錯 → 用程式畫好的流程：一定要先確認程式的「文法」沒錯，才給回饋（今天 1-A，LangGraph）
  2. 需要判斷 → 交給 AI：回饋怎麼寫、要不要執行程式看看（今天 1-B，agent）
  3. 做法和規矩 → 寫成給 AI 看的手冊：語氣溫和還是嚴格、好的變數名稱長什麼樣（下週，Skill）
- **畫面下方一行字**：今天做兩個版本：1-A 路線由程式決定、1-B 路線由 AI 決定；下週加上手冊，接成一個
- **講者**：用一分鐘把小專案講清楚，之後每一段都可以回到這張：「現在做的是小助教的哪一塊？」

## 先備知識：AI 到底怎麼做事（0:10–0:28）

### 投影片 4｜LLM 是一台「接話機器」（HTML 第 7 張）

- **畫面**：一個輸入框「今天天氣真」，右邊模型吐出「好」；再一格「好，適合」→「出門」
  - 它只做一件事：看前面的字，猜最合理的下一段
  - 它不會記得上一次對話，除非你把對話再貼給它
  - 它算數不可靠、不會上網、不會執行程式（真的不會）
- **講者**：這一張很重要，後面所有東西都建立在「它只會接話」這件事上。
- **Colab**：1-0 第 1 段（HTML 第 8 張「LLM 沒有記憶」）：有歷史 vs 沒歷史

### 投影片 5｜Token 與 context window（HTML 第 9 張）

- **畫面**：一句中文被切成一塊一塊（「今天 / 天氣 / 真 / 好」），旁邊一張桌子，上面擺滿紙
  - Token：模型讀字的最小單位，中文大約一到兩個字一個 token
  - Context window：它一次能看的 token 上限，像一張桌子，東西放太多就擺不下
- **Colab**：1-0 第 2 段（HTML 第 10 張「打開回傳物件」）：這次桌上用了幾個 token
- **講者**：記住「桌子」這個比喻，等一下 1-B 講 MCP、第 2 堂講 AI 怎麼選手冊、為什麼要開第二個 agent，都會回到這張桌子。

### 投影片 6｜Prompt 與 system prompt（HTML 第 11 張）

- **畫面**：一段對話截圖，最上面灰底一段「你是 Python 作業小助教，回答要用繁體中文」，下面是使用者的話
  - 你跟它說的話叫 prompt
  - 放在最前面、每次都在的那段「你是誰、要遵守什麼」叫 system prompt
- **講者**：等一下 1-B 你會改 system prompt 裡的一句話，看 agent 行為怎麼變。

### 投影片 7｜模型不能做事，那 agent 怎麼「做事」？（HTML 第 12 張）

- **畫面**：一個問號：模型不能執行程式，為什麼 ChatGPT 可以幫我跑 Python？
- **講者**：賣個關子，下一張揭曉。這是今天最關鍵的觀念。

### 投影片 8｜Tool calling：模型只會「說」它想用哪個工具（HTML 第 13 張）

- **畫面**：三格漫畫
  1. 你的 Python 告訴模型：「你有一個工具叫 run\_code，可以執行程式」
  2. 模型回一段文字（JSON）：`{"tool": "run_code", "args": {"code": "print(1+1)"}}`
  3. 你的 Python 看到這段，真的去執行，把結果 `2` 貼回去給模型
- **講者**：模型從頭到尾只是「說」它想用什麼工具，真正做事的是你的程式。這叫 tool calling 或 function calling \[1\]。
- **Colab**：1-0 第 3 段（HTML 第 14 張）：自己跑一次，看模型回傳的那段 JSON 紙條；第 4 段（HTML 第 15 張）把三步寫成迴圈

### 投影片 9｜Agent = 模型 + 工具 + 迴圈（HTML 第 15 張）

- **畫面**：一個圓圈
  - 問模型 → 它說要用工具？執行、把結果貼回去 → 再問 → 它說不用了 → 結束
  - 公式：Agent = Model + Tools + Loop \[1\]\[2\]
- **講者**：Anthropic 和 LangChain 都是這樣定義的 \[1\]\[2\]。迴圈用 Python 寫出來不到 10 行，Colab 1-0 第 4 段就有；1-B 會看到 LangGraph 幫你寫好的版本。

### 投影片 10｜兩種 agent：誰決定下一步（HTML 第 16 張）

|  | Workflow（工作流程） | Agent（自主代理） |
| --- | --- | --- |
| 誰決定下一步 | 你用程式畫好的流程圖 | AI 自己決定 |
| 像什麼 | 手搖飲店的出餐流程 | 一個拿著工具箱的實習生 |
| 優點 | 穩定、好預測、好除錯 | 彈性大，能處理沒想過的情況 |
| 缺點 | 只能處理你想到的情況 | 比較不穩定、可能繞路 |
| 今天在哪裡 | Notebook 1-A | Notebook 1-B |

- **講者**：Anthropic 的分法 \[1\]。兩種都叫「agentic system」，今天先做穩的，再做自由的。

## Notebook 1-A：Workflow，路線由程式決定（0:28–0:52）

### 投影片 11｜LangGraph：把函式用箭頭接起來（HTML 第 18 張）

- **畫面**：手搖飲店出餐流程：點單 → 做飲料 → 檢查甜度 → 封膜 → 交給客人，旁邊一張訂單紙
- **畫面上的一句話**：LangGraph = 把幾個 Python 函式用箭頭接起來，讓一份資料依序流過它們 \[4\]
- **畫面下方一行字**：下一張：把這間店換成作業小助教
- **講者**：每個工作站只做一件事，訂單紙跟著飲料走，每站只在上面寫一點東西。三個零件（訂單紙＝State、工作站＝Node、箭頭＝Edge）都在這間店裡。

### 投影片 11a｜作業小助教的流程：四個工作站（HTML 第 19 張）

- **畫面**：小助教的流程圖，每一站都有白話說明，上方用灰字對照手搖飲店
  - `check_syntax` 檢查語法：只看程式的「文法」對不對，例如括號有沒有關好、冒號有沒有漏，**不會執行程式**（≈ 確認這單做得出來）
  - 語法錯 → `explain_error` 解釋錯誤：一句話說錯在第幾行，然後結束（≈ 做不出來，跟客人說明）
  - 語法對 → `give_feedback` 寫回饋：寫出「優點＋改進」，**這一步才用到 AI**（≈ 做飲料）
  - `check_format` 檢查格式：有沒有兩段、有沒有太長；不合格就退回 give\_feedback 重寫（≈ 檢查甜度）
  - 一張訂單紙（State）從頭傳到尾：作業、語法對不對、回饋、重寫幾次
- **畫面下方一行字**：接下來幾張，就是把這張圖拆開來看：訂單紙（State）、工作站（Node）、箭頭（Edge）
- **講者**：先讓大家看到整個小助教，再拆零件；投影片 19（設計模式）會回到這張圖。Colab 1-A 第 1 段會畫出同一張圖。

### 投影片 12｜零件一：State，跟著走的訂單紙（HTML 第 20 張）

```python
state = {
    "code": "print('hi'",   # 學生交的作業
    "syntax_ok": None,       # 語法對不對
    "feedback": "",          # 給學生的回饋
    "retries": 0,            # 重寫了幾次
}
```

- **講者**：State 就是一個 dict。整個流程只有這一張訂單紙，從頭傳到尾。

### 投影片 13｜零件二：Node，一個工作站（HTML 第 21 張）

```python
def check_syntax(state):
    ok = 語法檢查(state["code"])   # 只看文法，不執行
    return {"syntax_ok": ok}   # 只回傳自己改的那一格
```

- **右欄（必踩的雷 1：直接改 state）**：錯誤寫法 `state["syntax_ok"] = True; return state`（整張交回去，別站寫的格子也被重寫一次）；正確寫法 `return {"syntax_ok": True}`（只交回改了哪一格）

- **Colab**：1-A 加碼（HTML 第 22 張「反例：訊息被蓋掉」）：BadState vs add\_messages。這張開頭有一句橋接：「岔出去看一個常見的坑：如果訂單紙上有一格是『對話紀錄』呢？（1-B 的 agent 就會用到這一格）」
- **講者**：Node 就是一個函式：收 dict、回傳 dict。重點是它只回傳自己負責的那一格，LangGraph 幫你寫回訂單紙 \[4\]。封膜的店員只蓋「已封膜」的章，不會去改甜度。

### 投影片 14｜零件三：Edge，工作站之間的箭頭（HTML 第 23 張）

- **畫面**：兩種箭頭並排
  - 一般箭頭：`add_edge("check_syntax", "give_feedback")`，做完 A 一定接 B
  - 條件箭頭：一個回傳「下一站名字」的函式，就是 if / else \[3\]

```python
def route(state):
    if state["syntax_ok"]:
        return "give_feedback"
    return "explain_error"
```

- **講者**：客人點熱飲就不經過加冰站。條件箭頭就是把「看情況走哪條路」寫成一個 if。

### 投影片 15｜一張表記住三個零件（HTML 第 24 張）

| 你會的 Python | LangGraph | 手搖飲店 |
| --- | --- | --- |
| dict | State | 訂單紙 |
| 函式 | Node | 工作站 |
| 依序呼叫 | Edge | 箭頭 |
| if / else | 條件邊 | 熱飲不加冰 |
| while 迴圈 | 指回前面的邊 | 甜度不對，退回重做 |

- **Colab**：1-A 第 1 段：畫出作業小助教的流程圖，找找看每個 Node 和每條 Edge 在哪裡

### 投影片 16｜先不接 AI：三段作業，先猜再跑（HTML 第 25 張）

- **畫面**：學習單三題
  1. 輸入 `print("hi"`，會經過哪些節點？`syntax_ok` 最後是什麼？
  2. 輸入正確的程式，`feedback` 在哪一步之後才有內容？
  3. 輸入空白，會發生什麼事？
- **紙上 → Colab**：先在學習單寫下猜測，再到 1-A 第 2 段依序選三段作業執行比對
- **講者**：這一段的節點都是普通 Python，沒有 AI。先把流程看懂，再把 AI 放進來。

### 投影片 17｜資料流：看訂單紙一格一格被填滿（HTML 第 26 張）

```
第 1 步  {"code": "print('hi'", "syntax_ok": None,  "feedback": ""}
第 2 步  {"code": "print('hi'", "syntax_ok": False, "feedback": ""}
第 3 步  {"code": "print('hi'", "syntax_ok": False, "feedback": "第 1 行少了右括號"}
```

- **Colab**：1-A 第 2 段：看訂單紙一格一格被填滿
- **講者**：這是 `stream_mode="values"` 印出來的，每一步都比上一步多填好一格 \[5\]。以後看任何 LangGraph 程式，先問兩件事：State 有哪幾格？每個節點寫哪一格？

### 投影片 18｜把 AI 放進一個節點（HTML 第 27 張）

```python
from google.colab import ai

def give_feedback(state):
    text = ai.generate_text(f"用「優點：」「改進：」兩段給這段作業回饋：{state['code']}")
    return {"feedback": text, "retries": state["retries"] + 1}
```

- **Colab**：1-A 第 3 段：give\_feedback 換成接上 AI 的版本，再跑一次作業
- **講者**：剛才「先不接 AI」時，give\_feedback 只回一段固定文字；現在把它換成請 AI 寫。AI 只是住在某個節點裡的一行程式，流程圖沒變。Colab 免費帳號可直接用 `google.colab.ai`，不用 API key \[6\]。

### 投影片 19｜回頭看小助教的流程圖：三種設計模式全都有（HTML 第 28 張）

- **畫面**：投影片 11a 那張作業小助教流程圖，換成設計模式的名字再看一次，三個地方各圈一個顏色
  - 直線 check\_syntax → give\_feedback → check\_format：**串接（prompt chaining）**，把大事拆成固定順序的小步驟 \[1\]
  - check\_syntax 後的分叉：**分流（routing）**，先判斷類型再交給專門處理的步驟 \[1\]
  - check\_format 退回 give\_feedback 的圈：**評估與修正（evaluator-optimizer）**，產出、檢查、不合格就重做，`retries` 到 3 就停 \[1\]
- **Colab**：1-A 第 3 段：調「最多重試次數」和「回饋字數上限」，先猜 retries 會變多還是變少

### 投影片 20｜中場休息 10 分鐘（HTML 第 29 張）

- **畫面**：休息倒數；下半場預告「讓 AI 自己決定要做什麼」
- **講者**：還沒跑完 1-A 的同學，從該段第一格重跑就能重來

## Notebook 1-B：Agent，路線由 AI 決定；tool 與 MCP（1:02–1:30）

### 投影片 21｜換個做法：不畫流程圖，給它一個工具箱（HTML 第 31 張）
- **畫面**：同一個作業小助教，換個做法。左邊 1-A 的流程圖；右邊「1-B：同一個小助教，改成給 AI 一個工具箱」，裡面三把工具
  - `run_code`：安全地執行作業，回傳輸出或錯誤
  - `check_indent`：檢查縮排和每行長度（縮排對不對、有沒有太長）
  - `read_spec`：讀這題的作業要求
- **講者**：這次不告訴它先做什麼再做什麼，只告訴它有哪些工具、目標是什麼，讓它自己決定。
- **Colab**：1-B 第 1 段（HTML 第 32 張）：試試 `run_code` 的三道圍欄（那張的程式碼上方標明「天真的寫法（不要這樣寫）」）

### 投影片 22｜一行做出 agent：`create_agent`（HTML 第 33 張）

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def run_code(code: str) -> str:
    """安全地執行一段 Python 作業，回傳輸出或錯誤訊息。"""
    ...

agent = create_agent(model, tools=[run_code, check_indent, read_spec],
                     system_prompt="你是 Python 作業小助教……")
```

- **講者**：2025 年 10 月 LangChain 1.0 之後，這是標準寫法 \[7\]。注意每個工具上面那段三引號的說明，那就是投影片 8 裡「告訴模型你有一個工具叫 run\_code」的那段話，模型靠它決定要不要用。
- **Colab**：1-B 第 2 段（HTML 第 34 張）：印出三個工具的說明書，模型只看得到這幾行

### 投影片 23｜Tool 從哪裡來：自己寫的函式 vs MCP 插座（HTML 第 35 張）

- **畫面上方一行字**：說明書不一定是你寫的：別人做好的工具，也能從插座接進來（接在 docstring 那張後面，所以不會突然冒出來）
- **畫面**：工具箱裡左邊兩把是你寫的 `@tool`（`run_code`、`check_indent`），右邊一把 `get_homework` 插在牆上的插座，插座外面接著 GitHub
  - 本地函式：你自己寫、住在同一個程式裡
  - MCP：工具住在別的程式或服務裡，透過一個共同的插座規格接進來，自帶帳號認證。之前社課教過的 MCP 就是這個 \[12\]
  - 兩者對 agent 來說一樣：都是「我可以呼叫的工具」
- **Colab**：1-B 第 3 段：接上一個真的 MCP server「作業倉庫」（加了 `@mcp.tool()` 的小程式，跑在同一台 Colab 上），agent 同時用 MCP 的 `get_homework` 和本地的 `run_code`；再比比看說明書佔掉多少桌子（估算：本地 3 個約 479 token、作業倉庫 3 個約 244、GitHub 規模約 40 個約 4,245）
- **講者**：MCP 不是另一種 agent，它是「工具」的外接方式。代價是接上後所有工具定義都進桌子，下週會講怎麼用 Skill 把它包起來。真的遠端 MCP 是一個網址加 OAuth 登入，2-E 練習 1 有網址版。

### 投影片 24｜看它每一步選了什麼（HTML 第 37 張）

- **畫面**：notebook 印出的執行過程

```
[模型] 我先讀題目要求 → 呼叫 read_spec
[工具] read_spec → "請寫一個函式回傳兩數之和"
[模型] 我來執行看看 → 呼叫 run_code
[工具] run_code → "NameError: name 'summ' is not defined"
[模型] 第 3 行變數名稱打錯了……（給出回饋，不再呼叫工具）
```

- **Colab**：1-B 第 4 段：先猜猜看它會先用哪個工具，再執行比對（展開版的兩節點 LangGraph 在 1-B 第 5 段，HTML 第 36 張）
- **講者**：每一行都是投影片 9 那個迴圈轉一圈。

### 投影片 25｜同一段作業跑三次，順序不一樣（HTML 第 38 張）

- **畫面**：「你可能會看到三次都不一樣」：三次執行並排，一次先 read\_spec，一次先 run\_code，一次沒跑程式就直接評語
- **講者**：這就是 agent 和 workflow 最大的差別：路線不是你畫的，是它當下決定的。大方向通常對，但每次不同。
- **Colab**：1-B 第 6 段：system prompt 加一句「一定要先讀題目要求」，再跑三次，順序有沒有變？

### 投影片 26｜它會繞圈：recursion limit（HTML 第 39 張）

- **畫面**：一個故意會一直失敗的工具，agent 一直呼叫它，跑到第 25 步被 LangGraph 停下來，印出 `GraphRecursionError`
- **Colab**：1-B 第 7 段：給它一個永遠失敗的工具，看它被停下來（學生自己跑；時間不夠就由講師投影示範，寫在講者備註）
- **講者**：Agent 可能一直轉圈出不來。所以我們在程式裡設 `recursion_limit=25`，跑到 25 步就強制停。注意：LangGraph 1.0 預設就是 25；從 1.1 版起預設放寬到 10007 步（環境變數 `LANGGRAPH_DEFAULT_RECURSION_LIMIT`），不設的話它會繞很久、一直燒 token。這是今天第一個「用程式限制 AI」的例子，下一站就來談：哪些事該這樣鎖死、哪些可以放手。

## 何時鎖死、何時放手、收尾（1:30–2:00）

### 投影片 27｜十道關卡的數學（HTML 第 41 張）

- **畫面**：一排 10 個關卡圖示，下方兩行大字
  - 每關 99% 會過 → 全部過關約 90%（0.99 的 10 次方）
  - 每關 95% 會過 → 全部過關只剩約 60%（0.95 的 10 次方）\[9\]
- **講者**：每一步看起來都很可靠，串起來卻常出錯。所以要在中間放檢查站，錯了馬上抓回來。1-A 的 check\_format 就是檢查站。

### 投影片 28｜雙拼：把 agent 放進 workflow 的一個節點（HTML 第 42 張）

- **畫面**：1-A 的流程圖，give\_feedback 那一格放大，裡面是 1-B 的小迴圈（model ↔ tools）
  - 外面：順序鎖死，一定先檢查語法、一定檢查格式
  - 裡面：給回饋這一站，讓 agent 自己決定要不要執行程式、要不要查題目
- **講者**：這就是課名裡的「雙拼」。不是二選一，是外面用圖鎖住不能錯的事，裡面放手讓 AI 處理需要判斷的事。第 2 堂會把它做出來。

### 投影片 29｜學習單：作業小助教的每一步，該鎖死還是放手？（HTML 第 43 張）

| 步驟 | 鎖死（寫進流程） | 放手（讓 AI 決定） | 為什麼 |
| --- | --- | --- | --- |
| 一定要先檢查語法 | ✓ |  | 順序錯了後面全錯 |
| 回饋用什麼語氣 |  | ✓ | 需要判斷 |
| 回饋一定要有「優點」和「改進」兩段 | ✓ |  | 能用程式檢查 |
| 要不要執行作業看輸出 |  | ✓ | 看情況 |
| 重寫最多幾次 | ✓ |  | 不鎖會無限轉圈 |

- **紙上**：先在學習單上勾勾看，再一起對答案（帶法寫在講者備註：先只放出左欄，再按 → 逐列公布）
- **講者**：本堂口訣：流程鎖住不能錯的事，agent 放手處理需要判斷的事。判斷方法：能寫成 if 的就是「不能錯的事」。下週這句會再長出第三段。

### 投影片 30｜新名詞 Harness、今天重點、課後作業（HTML 第 44 張）

- **畫面上半**：一匹馬加韁繩和馬鞍，公式 **Agent = Model + Harness**
  - 模型是馬，跑得快但不一定往你要的方向
  - Harness（馬具）是韁繩和馬鞍：今天的流程圖、檢查節點、recursion limit 都是 \[10\]
  - 2026 年業界的共識：決定 AI 好不好用的常常不是模型，是外面這一層 \[10\]\[11\]
- **畫面下半，今天三件事**：
  1. Agent = 模型 + 工具 + 迴圈；模型只會「說」要用哪個工具，做事的是你的程式
  2. 流程鎖住不能錯的事，agent 放手處理需要判斷的事；兩者可以套在一起，就是雙拼
  3. 工具有兩種來源：自己寫的函式，或從 MCP 插座接進來；說明書都會放上桌
- **課後作業（Colab）**：把自己寫過的一段作業放進 1-A、1-B 的「我的作業」，截圖兩邊的過程，寫一句話說哪邊你比較信任、為什麼
- **下週預告**：不改程式，只換一份說明書，就能改變 AI 的行為

## 參考來源

1. [Building effective agents](https://www.anthropic.com/research/building-effective-agents) — Anthropic，2024 年 12 月。Augmented LLM、tool calling、workflow 與 agent 的區分、三個設計模式
2. [LangChain 文件：Agents](https://docs.langchain.com/oss/python/releases/langchain-v1) — agent 的核心迴圈：呼叫模型、執行它選的工具、直到不再呼叫工具
3. [Introduction to LangGraph: A Beginner's Guide](https://medium.com/@cplog/introduction-to-langgraph-a-beginners-guide-14f9be027141) — 條件邊與路由函式的初學者範例
4. [LangChain 官方文件：StateGraph 與條件邊](https://docs.langchain.com/oss/python/2-add-tools) — State、Node、`add_conditional_edges`
5. [LangGraph：Watching it work（streaming）](https://www.krishnaik.in/coding-labs/langgraph/watching-it-work) — `stream_mode="values"` 與 `"updates"`
6. [All Colab users now get access to Gemini and Gemma models](https://medium.com/@spkshumway) — Google Colab 團隊，2025-11-12
7. [LangChain 1.0 release notes](https://docs.langchain.com/oss/python/releases/langchain-v1) — `create_agent` 是標準寫法，底下是 LangGraph
8. [LangChain vs LangGraph (2026)](https://www.testmuai.com/blog/langchain-vs-langgraph/) — 2025-10-22 的 1.0 版後 `create_agent` 取代 `create_react_agent`；同一個 agent 兩種寫法
9. [What Is an Agent Harness?](https://atlan.com/know/what-is-an-agent-harness/) — Atlan，2026 年 4 月。0.99^10 的複合失敗例子
10. [Harness Engineering](https://martinfowler.com/articles/harness-engineering.html) — Birgitta Böckeler，martinfowler.com，2026 年 4 月
11. [Agent Harness Engineering](https://addyosmani.com/blog/agent-harness-engineering/) — Addy Osmani，2026-04-19

12. [Agent Skills vs MCP](https://atlan.com/know/ai-agent/ai-agent-skills/agent-skills-vs-mcp/) — Atlan，2026-07-16。MCP 的架構、認證與治理；與 Skill 的關係
