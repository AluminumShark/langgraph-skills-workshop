# 歷史素材說明

> 本檔保留舊教案可參考的素材與當時規劃，不代表目前頁碼、段落順序或驗收標準。實作以 [目前課綱](syllabus.md)、兩堂逐頁大綱及 `scripts/nbspec/` 為準。

# REUSE.md：舊教案可直接貼用的素材

來源：`AluminumShark/langgraph-harness-workshop`（clone 在 `scratchpad/oldrepo/`，Gemini 2.5 Flash、langgraph 1.1.10 / langchain 1.2.18 手組 ReAct 迴圈，單堂 90 分鐘「Data Analyst Agent + trace/eval」課）。
投影片編號依協調者給的新版大綱編號（第 1 堂 S1-N、第 2 堂 S2-N）；括號內附舊 repo 的 notebook cell id 或 `slides/workshop.pdf` 頁標題，方便查原文。

**改寫規則（每段程式碼下方都有標註）**
- 模型物件：舊版 `ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)` → 新版 `model`（由 `google.colab.ai` 或講師 key 建立，簡報上就寫 `model`，不要寫供應商）。
- pandas 語境 → review-bot 語境：`inspect_data` → `check_syntax`、`run_pandas` → `run_code`、`get_weather` → `run_code`、`question`（分析 CSV）→ `作業`、`chatbot` 節點 → `ask_model`、`data/sales.csv` → 一段 Python 作業字串。
- `.text()` 一律改 `.text`（langchain-core 1.x 是 property；舊投影片寫成 method，notebook 已改成 property）。
- 程式碼都是從 `notebooks/workshop.ipynb` 逐字抄，只有「改」字樣標註的行動過。

---

## 1. `bind_tools` 印出 tool_calls JSON

- (a) **S1-8**（1-0_tool_calling 的核心格）。舊 cell `3d2b10c8` + 說明 cell `eea28461`；投影片「進 LangGraph 之前先看 LLM 回什麼」「LLM 的回應拆解」。
- (b) 程式碼：

```python
from langchain_core.tools import tool

@tool
def run_code(code: str) -> str:            # 改：原 get_weather(city)
    """執行一段 Python 作業，回傳輸出或錯誤訊息。"""   # 改：原「查詢城市的天氣。」
    return "（這裡先不真的執行，只看模型想不想叫它）"

model_with_tools = model.bind_tools([run_code])   # 改：原 llm.bind_tools([get_weather])
resp = model_with_tools.invoke("這段作業跑得起來嗎？print('hi'")   # 改：原「台北今天天氣怎樣?」
print("content:", repr(resp.content))
print("tool_calls:", resp.tool_calls)
```

舊版實際輸出（原封照抄，換成 run_code 後長相相同）：

```
content: ''
tool_calls: [{'name': 'get_weather', 'args': {'city': '台北'}, 'id': '032ae5d1-...', 'type': 'tool_call'}]
```

舊投影片原文（「LLM 的回應拆解」頁，可直接貼）：
> content: '' ← 注意是空字串!LLM 不打算用文字回答
> tool_calls 四個 key: name（叫什麼）、args（參數）、id（配對結果）、type（固定）
> LLM 沒有真的執行 get_weather —— 只是建議
> 我們要拿這個 dict 自己呼叫對應的 function,然後把結果包回 ToolMessage 給 LLM

- (c) 給初學者：模型不能跑程式，它只會回一張「請幫我執行 run_code，參數是這段」的紙條；真的去跑的是你的 Python。

---

## 2. 有歷史 vs 沒歷史的對照（LLM 沒記憶）

- (a) **S1-4**（觀念 1「LLM 只會接下一段字、不記得上一次對話」）。舊 cell `bca48125`、`aac07fe8`；投影片「§6.3 多輪對話:messages 是 list」。
- (b) 程式碼：

```python
from langchain_core.messages import AIMessage, HumanMessage

# LLM 自己沒記憶,你必須把整段對話歷史塞給它
history = [
    HumanMessage(content="我叫 Alice"),
    AIMessage(content="你好 Alice!"),
    HumanMessage(content="我叫什麼?"),
]
print(model.invoke(history).text)      # 改：原 llm.invoke(history).text

# 反例:不傳 history,只傳最後一句
print(model.invoke("我叫什麼?").text)   # 改：原 llm
```

舊版實際輸出（照抄）：

```
你叫 Alice。
---
我不知道你的名字。
我是一個AI，無法獲取或記住使用者的個人資訊。所以，我不知道你叫什麼名字。
```

舊投影片原文：
> LLM 沒有記憶。每次 invoke 要把整段歷史傳進去 — 它才知道剛才聊過什麼。所以 LangGraph 把 messages 包成 list、要 append 不要覆蓋。

- (c) 給初學者：它不是記得你，是你每次把整本對話紀錄再貼給它一次。

---

## 3. 打開回傳物件：type / content / tool_calls / usage_metadata

- (a) **S1-5**（講 token 與 context window「桌子」時，用 `usage_metadata` 看這次用了幾個 token）。舊 cell `4001ebb0`、`28cc4f06`；投影片「把 AIMessage 整個打開看」「物件的每個 attribute」。
- (b) 程式碼：

```python
resp = model.invoke("用三個字回答:Python 是什麼?")   # 改：原 llm

print("type:", type(resp).__name__)
print("content:", repr(resp.content))
print("tool_calls:", resp.tool_calls)
print("usage_metadata:", resp.usage_metadata)
print("response_metadata keys:", list(resp.response_metadata.keys()))
```

舊版實際輸出（照抄，注意 reasoning token 占了 501 個）：

```
type: AIMessage
content: '程式語'
tool_calls: []
usage_metadata: {'input_tokens': 10, 'output_tokens': 503, 'total_tokens': 513,
                 'input_token_details': {'cache_read': 0}, 'output_token_details': {'reasoning': 501}}
response_metadata keys: ['finish_reason', 'model_name', 'safety_ratings', 'model_provider']
```

舊投影片原文（「物件的每個 attribute」頁）：
> .text 訊息文字 — 今天最常用；用 tool 時可能是空字串
> .tool_calls LLM 建議呼叫的工具 — 空 list = 沒呼叫工具，有東西 = 要呼叫
> .usage_metadata 這次呼叫花多少 token — production 算錢 {input_tokens, output_tokens, total_tokens}
> .response_metadata.finish_reason STOP = 正常 / MAX_TOKENS = 被截斷
> 經驗法則：展示給人看用 .text，做訊息序列化或要看完整結構用 .content。

- (c) 給初學者：`input_tokens` 是你放到桌上的字、`output_tokens` 是它寫回來的字；桌子（context window）就這麼大，等一下接 MCP 時再看這個數字會跳多少。

---

## 4. 手組 ToolNode + tools_condition 迴圈（`create_agent` 的展開版）

- (a) **S1-18 前後、1-B「展開底下的兩節點 LangGraph」那張**。舊 cell `56950db5`（同 `src/pandas_pilot/graph.py`）；投影片「完整 Data Analyst Agent — 組裝」「逐行解剖」「ReAct 循環」。
- (b) 程式碼：

```python
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

tools = [run_code, check_indent, read_spec]          # 改：原 [inspect_data, run_pandas]
model_with_tools = model.bind_tools(tools)           # 改：原 llm_with_tools = llm.bind_tools(tools)

def ask_model(state: MessagesState) -> dict:         # 改：原節點名 chatbot
    return {"messages": [model_with_tools.invoke(state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("ask_model", ask_model)             # 改：原 "chatbot"
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "ask_model")
# tools_condition: 如果上一則訊息有 tool_calls,走 tools 節點;否則走 END
builder.add_conditional_edges("ask_model", tools_condition)
builder.add_edge("tools", "ask_model")  # tools 跑完繞回 ask_model

agent = builder.compile()
```

舊投影片「逐行解剖」表（照抄，可直接做 `.tbl`）：

| 元件 | 做什麼 |
| --- | --- |
| `@tool` | function → LLM 看得到的工具 |
| `bind_tools(tools)` | 工具說明書附在 LLM 呼叫 |
| `chatbot` 節點（新版 `ask_model`） | 呼叫 LLM，可能回文字或 tool_calls |
| `ToolNode(tools)` | 讀 tool_calls、執行、包結果 |
| `tools_condition` | 內建路由 function：有 tool_calls → tools / 沒 → END |
| `add_conditional_edges` | 條件邊：依 fn 回傳值動態決定下一站 |
| `add_edge("tools", "chatbot")` | 工具跑完回去 LLM，形成循環 |

> 本質上 LangGraph 是把「拿 tool_calls → 自己呼叫 → 包 ToolMessage 回去」這串 boilerplate 自動化。
> LLM 決策 → ToolNode 執行 → 結果回 LLM → 再決策，直到 LLM 認為夠了，不再回 tool_calls，走 END。

- (c) 給初學者：`create_agent(model, tools)` 一行底下就是這 12 行：一個問模型的節點、一個跑工具的節點、一條「有沒有要用工具」的 if，繞成一個圈。

---

## 5. `pretty_trace`

- (a) **S1-23**（1-B「印出每一步選的工具」；2-B、2-D 也共用）。舊 cell `e23ef69e`（同 `src/pandas_pilot/trace.py`）；投影片「把 trace 包成漂亮的 print」「trace 輸出長相」。
- (b) 程式碼：

```python
def pretty_trace(graph, user_message: str) -> list[dict]:
    events = []
    print(f"USER: {user_message}\n")
    inputs = {"messages": [{"role": "user", "content": user_message}]}
    for step, event in enumerate(graph.stream(inputs, stream_mode="updates"), start=1):
        events.append(event)
        for node_name, node_state in event.items():
            print(f"--- 第 {step} 步 | 節點: {node_name} ---")        # 改：原 "--- step {step} | node: ..."
            for msg in node_state.get("messages", []):
                role = type(msg).__name__
                tool_calls = getattr(msg, "tool_calls", None)
                if tool_calls:
                    for call in tool_calls:
                        print(f"  模型決定呼叫 -> {call['name']}({call['args']})")   # 改：原 "[{role}] tool_call ->"
                else:
                    text = msg.text if hasattr(msg, "text") else str(msg.content)
                    if len(text) > 400:
                        text = text[:400] + "..."
                    print(f"  [{role}] {text}")
            print()
    return events

events = pretty_trace(agent, 作業)        # 改：原 pretty_trace(agent, question)
```

舊版實際輸出（照抄，換工具名即可）：

```
--- step 1 | node: chatbot ---
  [AIMessage] tool_call -> inspect_data({'path': 'data/sales.csv'})
--- step 2 | node: tools ---
  [ToolMessage] shape: (100, 5) ...
--- step 3 | node: chatbot ---
  [AIMessage] tool_call -> run_pandas({'path': 'data/sales.csv', 'code': "..."})
--- step 4 | node: tools ---
  [ToolMessage] South ...
--- step 5 | node: chatbot ---
  [AIMessage] 平均 revenue 最低的 region 是 South,數值為 382.347727。
```

舊投影片原文：
> invoke 只給你終點；stream 把過程攤開。
> stream_mode='updates' — 每個節點跑完後吐出「return 了什麼」；還有 'values'（整個 state 快照）。
> 每個節點的順序、呼叫了什麼工具、看到什麼結果 — 全部看得見。

- (c) 給初學者：`invoke` 只給你最後一句話；`stream` 讓你站在旁邊看它每一步選了哪個工具。

---

## 6. 跑三次看 stochastic，預期三種結局

- (a) **S1-24**（1-B「同一段作業跑兩次看順序不同」→ 改成跑三次）。舊 cell `85165e63`、說明 cell `faef113e`；投影片「試跑這個 agent 三次」「LLM agent 的本質特性」。
- (b) 程式碼：

```python
for i in range(3):
    print(f"========== 第 {i + 1} 次 ==========")
    result = agent.invoke({"messages": [{"role": "user", "content": 作業}]})   # 改：原 question
    print(result["messages"][-1].text)
    print()
```

舊投影片「試跑這個 agent 三次」原文（三欄，review-bot 版建議對應：先 run_code / 先 check_indent / 根本沒跑就直接評語）：
> 預期看到三次不一致
> 第一次：可能 East 是最差　｜　第二次：可能 West 是最差　｜　第三次：可能跳過 inspect_data，結果可能錯
> 先別急著找原因——這個現象本身就是後半場的主題

舊投影片「LLM agent 的本質特性」原文：
> 正確走完工具流程 ｜ 流程相同但結果不同 ｜ 流程錯，結果可能錯
> 這不是 bug、不是寫錯。同一程式、同一資料，每次跑可能走不同路徑、做不同決定。業界所有人都在處理這件事。

舊 notebook 說明 cell 原文：
> **這就是 stochastic 的本性**。三次答案不一致很正常,有時候它甚至不 inspect 就直接 run。

- (c) 給初學者：同一段作業、同一個程式，跑三次走三條路。這不是壞掉，是 agent 的天性，所以下一堂才要學怎麼把該固定的步驟固定下來。

---

## 7. 「docstring 決定 tool 會不會被用」

- (a) **S1-22**（tool 的說明書）；**S2-7** 和 Skill 的 `description` 並排（tool 看 docstring 選工具 ↔ AI 看 description 選手冊）。舊 cell `d81b6a38`、`abbfe9cd`；投影片「§8.3 docstring 是 LLM 唯一的『使用說明書』」「你的 agent 行為好不好 80% 取決於 tool docstring」。
- (b) 程式碼：

```python
# LLM 看不到你的程式碼,只看到 tool 的 name、docstring、參數
print(run_code.name)           # 改：原 get_weather
print(run_code.description)    # 這就是 docstring
print(run_code.args)
```

舊版輸出（照抄）：

```
get_weather
查詢城市的天氣。
{'city': {'title': 'City', 'type': 'string'}}
```

舊投影片原文（整頁可貼）：
> @tool 把 function 名稱、參數、docstring 包成 JSON schema 餵給 LLM
> LLM 完全靠 docstring 決定要不要呼叫這個 tool。docstring 寫不好 = LLM 永遠不呼叫
> 好的 docstring 要寫：做什麼 / 何時該呼叫 / 參數是什麼意義 / 回傳什麼
> 常見錯誤：只寫一句「查詢天氣」/ 沒講何時該呼叫 / 參數沒解釋格式 / 用中英混雜的怪用語
> 你的 agent 行為好不好，80% 取決於 tool docstring 寫得好不好
> Gemini 對短 docstring 比 Claude 更敏感——詳細寫，LLM 才會穩定呼叫

舊 notebook 原文：
> **docstring 寫得爛 → tool 沒人用**。

S2-7 並排建議：左欄貼上面「好的 docstring 要寫：做什麼 / 何時該呼叫」，右欄貼新課綱觀念 17「description 要寫做什麼、什麼時候用」，標題「同一件事：AI 只看說明書的第一行決定要不要拿起來」。

- (c) 給初學者：模型看不到你的程式碼，只看得到那一行說明；說明沒寫「什麼時候用我」，它就永遠不會用。

---

## 8. 「LangGraph 必踩的 6 個雷」cheatsheet 全文

- (a) **S1-13、S1-14** 用第 1、2、5 條（State 紀律、條件邊只讀 state）；**第 2 堂講義**放全部六條。舊投影片「§14 Cheatsheet：LangGraph 必踩的 6 個雷」。
- (b) 全文照抄：

| # | 雷 | 解法 |
| --- | --- | --- |
| 1 | `state["messages"].append(...)` | → `return {"messages": [new_msg]}` |
| 2 | 自訂 State 沒寫 reducer，訊息列表被覆蓋 | → `Annotated[list, add_messages]` |
| 3 | 沒 `compile()` 就 invoke | → `graph = builder.compile()` 後 |
| 4 | `@tool` docstring 沒寫「使用時機」 | → LLM 不知何時呼叫 |
| 5 | 路由函數裡呼叫 LLM | → 路由只讀 state 純值 |
| 6 | Tool 裡用 `eval()` 跑 LLM 給的 code | → Production 改 sandbox / RestrictedPython |

> 1-3 是 state 紀律 / 4-5 是 graph 設計 / 6 是安全
> 把這頁拍下來，寫 code 卡住時翻一下省 30 分鐘 debug。

配套「State 的紀律」頁原文（S1-13 可用）：

```python
# 錯誤寫法
def bad_node(state):
    state["messages"].append(new_msg)
    return state          # 直接改 state 物件 → 繞過 reducer → 行為難預測

# 正確寫法
def good_node(state):
    return {"messages": [new_msg]}   # 回新 dict → reducer 處理合併 → 行為可預測
```
> 永遠不要直接 mutate state。把新東西包成 dict return 出去，讓 reducer 幫你 merge。

- (c) 給初學者：節點只交「我改了哪一格」的小紙條回去，不要整張訂單紙拿去塗；要走哪條路（條件邊）只看訂單紙上的字，不要再問 AI。

---

## 9. 沒有 `add_messages` 訊息被蓋掉的反例

- (a) **S1-13**（State 是 dict、每個節點只寫自己的欄位、list 要合併不是覆蓋）。舊投影片「反例:沒有 add_messages 會怎樣」「MessagesState 內部」；notebook 只有文字 cell `9fb74552`。
- (b) 程式碼（投影片版，`bad_graph` 的組裝比照第 4 項骨架）：

```python
class BadState(TypedDict):
    messages: list   # ← 預設行為是「覆蓋」

def bad_chatbot(state: BadState) -> dict:
    response = model.invoke(state["messages"])      # 改：原 llm
    return {"messages": [response]}   # 覆蓋整個 list

# 跑一次
r1 = bad_graph.invoke({
    "messages": [{"role": "user", "content": "我叫小明"}]
})
print(len(r1["messages"]))
# 1   ← 怪!user 訊息消失了
```

修法（「MessagesState 內部」頁原文）：

```python
class MessagesState(TypedDict):
    messages: Annotated[list, add_messages]
```
> 怎麼讀這行？messages 是個 list，但 LangGraph 處理時不要覆蓋，要用 add_messages 合併（append）。
> 記憶口訣：Annotated 第一格是真型別，第二格是給框架看的提示。
> Bug 原因：`return {"messages": [response]}` 預設覆蓋整個 list；原本「我叫小明」直接消失 → 加上 `Annotated[list, add_messages]` 就 fix。

- (c) 給初學者：訂單紙上的「對話」那一格如果每次都整格擦掉重寫，前面講的話就不見了；`add_messages` 是告訴它「這一格要往下接著寫」。

---

## 10. Eval suite：五個 case、`evaluate_one`、40% → 100%

- (a) **S2-19、S2-20**（「驗證節點 = computational sensor」：行動後用程式檢查，不花 token）。舊 cell `63e33cf1`、`a65b2edd`、`07702f0c`、`696d8a94`、`5e8c7823`（同 `src/pandas_pilot/eval.py`）；投影片「Eval case 範例」「Eval runner」「量化看到變好」。
- (b) 五個 case 的結構（照抄前兩個，review-bot 版把 `must_call_first` 換成 `"check_syntax"`、`must_contain_in_final` 換成 `["優點", "改進"]`）：

```python
EVAL_CASES = [
    {
        "id": "001_must_inspect_first",
        "user_message": f"幫我看一下 {CSV_PATH} 這份資料的概況。",
        "must_call_first": "inspect_data",
        "must_contain_in_final": [],
    },
    {
        "id": "002_handle_empty_result",
        "user_message": f"在 {CSV_PATH} 裡找出 region 是 'Mars' 的紀錄總數。",
        "must_call_first": "inspect_data",
        "must_contain_in_final": ["0"],
    },
    # 003_inspect_before_summary / 004_top_region / 005_count_rows 結構相同
]
```

`evaluate_one` 邏輯（照抄）：

```python
def evaluate_one(graph, case):
    inputs = {"messages": [{"role": "user", "content": case["user_message"]}]}
    events = list(graph.stream(inputs, stream_mode="updates"))
    tc = extract_tool_calls(events)        # 從 events 抽出 tool 呼叫順序 (by name)
    final = extract_final_text(events)     # 最後一則沒有 tool_calls 的模型訊息

    reasons = []
    if case["must_call_first"]:
        if not tc:
            reasons.append(f"沒呼叫任何 tool(預期 {case['must_call_first']})")
        elif tc[0] != case["must_call_first"]:
            reasons.append(f"第一個 tool 是 {tc[0]},預期 {case['must_call_first']}")
    for kw in case.get("must_contain_in_final", []):
        if kw not in final:
            reasons.append(f"最終回覆缺關鍵字 {kw!r}")

    return {"id": case["id"], "passed": not reasons, "reasons": reasons,
            "tool_calls": tc, "final_text": final}
```

舊版實際跑出的數字（照抄，可直接做兩欄對照）：

```
baseline（沒 system prompt）                 v2（加「先呼叫 inspect_data 再分析」）
[PASS] 001  tool_calls=['inspect_data']       [PASS] 001  ['inspect_data']
[FAIL] 002  tool_calls=['run_pandas']         [PASS] 002  ['inspect_data', 'run_pandas']
        - 第一個 tool 是 run_pandas,預期 inspect_data
[FAIL] 003  tool_calls=['run_pandas']         [PASS] 003  ['inspect_data', 'run_pandas']
[FAIL] 004  tool_calls=['run_pandas']         [PASS] 004  ['inspect_data', 'run_pandas', 'run_pandas']
[PASS] 005  tool_calls=['inspect_data']       [PASS] 005  ['inspect_data']
通過 2/5 (40%)                                通過 5/5 (100%)
```

舊投影片原文：
> 把「agent 應該怎麼做」寫成程式可以檢查的規則。改 prompt → 跑 eval → 看 pass rate 變化。Software engineering 的單元測試思維，搬到 LLM 行為上。
> 這些都是「程式可以判斷的規則」——不需要人類來看每個答案。
> 改一行 prompt，量化看到變好。沒有 eval 你只能靠「感覺好像比較好」改 prompt。
> 重點不是滿分：v2 也不一定 100%——LLM 偶爾還是會不聽話。有客觀基準可以比較，才知道 v1 vs v2 是不是真的進步。
> eval set 是「長出來」的，不是「計畫出來」的：先寫 1 個 → 跑 → 改 prompt → 發現新 bug → 寫第 2 個 case。

新課綱接法：這段就是「guides 改了（system prompt），用 sensor 量（eval）」；再往前一步，把 `must_call_first` 直接寫成 graph 的順序、`must_contain_in_final` 寫成 `check_format` 節點，就不用事後測、也不用花 token——這是 2-B 版本 C 的論點。

- (c) 給初學者：用五題小考考 AI，改一句話前 2 題對、改完 5 題對，數字會說話；而且考卷是程式在改，不是人在看。

---

## 11. Harness loop 四件事 + Harness 自檢清單五條

- (a) **S2-34** 收束，或「講義裡還有」。舊投影片「完整 harness 包含四件事」「§13 Harness Loop」「Harness 自檢清單」「今天最重要的一句話」。
- (b) 全文照抄：

**完整 harness 包含四件事**
> 業界 LLMOps 公司（LangSmith、Langfuse、Braintrust）賣的就是這四件事的工具。今天不靠平台，用 LangGraph + 100 行 code 把核心做完。
> Trace 「這次 agent 為什麼這樣決策？」
> Replay 「失敗時能不能從中間試？」
> Eval 「我改了 prompt，整體變好還是變壞？」
> Loop 「怎麼把上面接成持續改進的迴圈？」

**Harness loop（notebook §13 原文）**
```
1. 改 agent(prompt / tool / graph)
2. run_eval_suite(agent)
3. 看哪個 case 跌了 → pretty_trace(agent, that_case) → 看出問題
4. 回 1
```
> **這個 loop 才是 agent 工程化的核心**——不是 LangGraph、不是 Gemini。任何框架、任何 LLM，只要能跑這個 loop，就能維護。

**Harness 自檢清單**
> 寫 production agent 之前自問——這 5 點任一個沒打勾，代表你還在 demo 階段，不是 production。
> ☐ 能 trace 嗎？看得到每個節點的決策嗎？
> ☐ State 顯式嗎？節點之間傳的資料都在 schema 裡？
> ☐ 有 eval set 嗎？至少 5 個 case 涵蓋已知失敗？
> ☐ 改了東西能量化嗎？一行 command 跑 eval 出 pass rate？
> ☐ 改 graph 有紀錄嗎？每次改有對應的 eval report？
> 沒打勾不算寫完 agent，只算寫了個 demo。

**收尾句**
> 有 trace + 有 eval = 你的 agent 從「demo 程式」變成「可工程化迭代的系統」。
> LangGraph 會被取代、Gemini 會出新版、API syntax 會改——但 State + Node + Tool 的 mental model，和 Trace + Eval 的工程紀律，會跟著你十年。

新課綱對應：Trace / Eval 是 sensors（行動後檢查）；Replay 對應 checkpointer + thread_id（2-D）；Loop 就是 Osmani「把錯誤變成 harness 裡一條新規則」。

- (c) 給初學者：馬鞍（harness）不只是韁繩，還要有後視鏡（trace）、計分板（eval）、可以倒帶（replay），和「每次摔了就加一條規則」的習慣（loop）。

---

## 12. `eval()` 的安全告誡 → 為什麼 `run_code` 要有圍欄

- (a) **S1-21**（1-B 的 `run_code` 工具：禁 import os / subprocess、設 timeout）。舊 cell `44d94687` 中 `run_pandas`、README「安全告誡」；投影片「eval() 的安全告誡」。
- (b) 舊程式碼（照抄，標出要改的地方）：

```python
@tool
def run_code(code: str) -> str:                  # 改：原 run_pandas(path, code)
    """執行一段 Python 作業，回傳輸出或錯誤訊息。"""   # 改：原「對 CSV 執行 pandas 分析程式碼...」
    # ⚠️ 注意:eval() 在 production 是嚴重安全問題
    # 此處為了工作坊講解簡化,實務上請改 sandbox / RestrictedPython / e2b
    try:
        result = eval(code, {"df": df, "pd": pd})   # 改：新版要換成受限 exec（禁 os/subprocess、timeout、抓 stdout）
    except Exception as exc:
        return f"執行錯誤:{type(exc).__name__}: {exc}"
    text = str(result)
    if len(text) > 2000:
        text = text[:2000] + "\n... (output truncated)"
    return text
```

舊投影片原文（整頁可貼）：
> ⚠️ Production 絕對不能這樣寫
> run_pandas 用 eval() 是為了讓程式碼短到可以講解
> LLM 生出來的 code 直接 eval = 把程式控制權交給 LLM
> LLM 可能被 prompt injection 騙去寫 `__import__('os').system('rm -rf /')`，你的 server 就完了
> Production 必須用：Sandbox 子進程（用 subprocess 跑、限制檔案/網路存取）／ RestrictedPython（只允許白名單的 Python 操作）／ e2b / Modal（專門的 code 執行環境，業界主流）

README 原文：
> `run_pandas` 用 `eval()` 跑 LLM 生出的 code——這在 production 是嚴重漏洞。實務上請用 sandbox / RestrictedPython / e2b。本專案是教學用，故意簡化以便講解。

新課綱接法：`run_code` 跑的是「學生的作業」，而學生作業裡什麼都可能有（`import os` 刪檔、無限迴圈）；所以工具本身要有圍欄：禁掉 `os`/`subprocess`、設 timeout、把 traceback 縮成一行給模型看（這也是 2-B「腳本輸出要讓 AI 看得懂」的原則）。這條在第 2 堂 2-C 可以回頭接 prompt injection：藏在 Skill 裡的指令一樣能騙模型去叫 `run_code` 跑壞東西。

- (c) 給初學者：`run_code` 是真的會在你電腦上跑程式的工具；交給 AI 的東西要先關進籠子，不然它被騙一次就把你的檔案刪光。

---

## 補充：還有兩段可選用

**A. echo bot / clean→respond 兩節點（S1-11、S1-12，1-A 純 Python 節點的骨架）**。舊 cell `6b39d86f`、`98f8c04e`：

```python
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    code: str            # 改：原 text
    feedback: str        # 改：新增

def check_syntax(state: State) -> dict:          # 改：原 clean
    return {"feedback": "語法 OK"}                 # 改：原 {"text": state["text"].strip().lower()}

def give_feedback(state: State) -> dict:         # 改：原 respond
    return {"feedback": f"{state['feedback']}；寫得不錯"}   # 改

b = StateGraph(State)
b.add_node("check_syntax", check_syntax)
b.add_node("give_feedback", give_feedback)
b.add_edge(START, "check_syntax")
b.add_edge("check_syntax", "give_feedback")
b.add_edge("give_feedback", END)
g2 = b.compile()
print(g2.invoke({"code": "print('hi')", "feedback": ""}))
```
舊投影片「水管比喻」原文：「兩節點之間完全不直接互相呼叫，state 是節點之間唯一的水管。好處：節點之間解耦。」「你只 return 要更新的欄位就好——不用每次把整個 state 抄一遍。」
講法：訂單紙（State）在工作站（Node）間傳，每站只填自己那一格。

**B. 「動腦不動手」題型**（舊投影片三處：猜輸出 / 第六個 eval case / production 回報算錯怎麼 debug）。格式就是新課綱的「預測 → 執行 → 比對」，直接改題：
> 動腦不動手：猜輸出 —— `return {"response": state["user_input"].upper()}`，輸入 "hello world"，猜 print(result) 印出什麼？
> 動腦不動手：假設你是 agent 開發者，production 上有人回報「agent 偶爾算錯數字」，你會用 trace 怎麼 debug？沒有 trace：你只看得到一個錯答案。有 trace：你看得到錯在哪一步。
