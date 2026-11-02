# 從 LangGraph 到 Skills：結構化與非結構化 Agent 的雙拼指南｜工作坊課綱

Oct 30, 2026 · @Levi

## 總覽

兩堂課各 120 分鐘（含中場 10 分鐘），對象是剛學會 Python 的初學者，學生只執行講師準備好的 Colab。兩堂都是「零件 + 怎麼擺」：第 1 堂教 agent、LangGraph、tool 與 MCP；第 2 堂教 Skill，再收束成系統設計：什麼該放 agent、什麼該寫成 Skill、什麼該做成 tool 或 MCP、什麼時候才需要第二個 agent。第 1 堂把「什麼是 agent」講清楚，並用 LangGraph 親眼看到 workflow 和 agent 各是怎麼跑的；第 2 堂講 Agent Skills：什麼該寫成 SKILL.md、什麼該放進 scripts/、什麼該留在程式裡，最後把 Skill 接回第 1 堂的流程，完成「雙核」。

- **中文名稱**：從 LangGraph 到 Skills：結構化與非結構化 Agent 的雙拼指南
- **英文名稱**：Agents in 2026: Mastering LangGraph & SKILL.md
- **上課日期**：第 1 堂 2026-11-09（週一）、第 2 堂 2026-11-16（週一），各 120 分鐘
- **課程資料**：[github.com/AluminumShark/langgraph-skills-workshop](https://github.com/AluminumShark/langgraph-skills-workshop)（notebook 都有 Open in Colab 連結）
- **一句話介紹**：先弄懂 AI agent 到底是什麼，再親手看它在 LangGraph 的流程裡怎麼跑、在 Skill 的說明書下怎麼變聰明，最後學會判斷哪些事該用程式鎖死、哪些事該交給 AI 判斷。
- **範例專案**：作業小助教 review-bot。輸入一段 Python 作業，輸出一份固定格式的回饋。選它是因為流程順序重要、輸出能用程式檢查、又需要領域知識，三種零件都用得到。
- **實作環境**：Google Colab。LLM 呼叫優先用內建的 `google.colab.ai`（免費帳號不需要 API key，但有用量上限），不足時改用講師的 API key。學生只做三件事：按執行、改表單欄位裡的文字或數字、先預測再比對輸出。

| 項目 | 原提案 | 新版 |
| --- | --- | --- |
| 對象 | 有 Python 與 LLM 經驗 | 剛學會 Python 的初學者 |
| 堂數 | 3 堂（第 3 堂選修） | 2 堂。原第 3 堂的整合併進第 2 堂；系統設計（五個抽屜、六問、何時要第二個 agent）佔第 2 堂最後 35 分鐘 |
| 學生動手方式 | 自己寫程式、建 repo | 執行講師的 Colab，改參數與 SKILL.md 文字 |
| 第 1 堂重點 | LangGraph：State、Node、條件邊 | 同上，前面多 20 分鐘講清楚 LLM、tool calling、agent 是什麼，後面多做一個「真正會自己選工具的 agent」 |
| 第 2 堂重點 | SKILL.md 與漸進式揭露、資安 | 同上，多一段「什麼該寫成 Skill、什麼該放 scripts/」的判斷，最後把 Skill 接回 graph |
| 原提案的核心學習成果 | 設計並部署 LangGraph 流程；撰寫合規 SKILL.md；判斷何時限制、何時放手 | 三項全部保留，改成「看懂、能改、能判斷」而非「從零寫出」 |

## 原提案每個知識點在新版的位置

原提案的內容全部保留，只是講法改成初學者看得懂，並補上 2026 年的新資訊。

| 原提案知識點 | 新版位置 | 怎麼教 |
| --- | --- | --- |
| 介紹 2026 年企業端為何仍依賴 Graph 架構 | 第 1 堂 1:30 | 用 0.99^10 的數學和 OpenAI 案例，改成「為什麼要把 AI 的步驟固定下來」 |
| State 定義、Nodes 建立、Conditional Edges | 第 1 堂 0:30 | 對照 dict、函式、if；notebook 1-A |
| 沒有框架 AI 會怎麼把事情搞砸 | 第 1 堂 0:00、1:05 | 開場 demo；1-B 讓 agent 自己選工具，親眼看它繞圈 |
| 建立「必須先完成 A 才能做 B」的審查 agent | 第 1 堂 0:30 | 作業小助教的 check\_syntax → give\_feedback → check\_format |
| SKILL.md 三階段漸進式揭露 | 第 2 堂 0:10 | 圖書館比喻：書背、內文、附錄 |
| 為何缺乏審查會有資安風險與幻覺 | 第 2 堂 1:05 | 藏指令的 Skill 實驗 + 兩份 2026 研究數據 |
| 下載一個 SKILL.md、拆解它 | 第 2 堂 0:10 | notebook 2-A 內建 Anthropic 官方 skills repo 的一份 Skill |
| 寫一個自定義 Skill 並測試觸發條件 | 第 2 堂 0:10、0:35 | 改現成 Skill 的規則與 description，看觸發與回饋怎麼變 |
| 將 Skills 嵌入 LangGraph 節點 | 第 2 堂 1:25 | notebook 2-D：skill\_loader 節點 + 2-B 的 scripts 當 tool |
| 評估何時限制 AI、何時釋放自治 | 第 1 堂 1:30、第 2 堂 0:35 | 兩張判斷表：「程式 / 文字 / 腳本」與 harness 四格 |
| 最低完成標準：受控節點正確觸發 Skill 且 state 未丟失 | 第 2 堂 1:25 | 用 checkpointer + thread\_id 重跑，印出 state 證明沒丟 |
| 分組 Demo 與 Code Review | 第 2 堂 1:45 | 改成兩人一組互相說明自己改了什麼、結果為何不同 |

## 要教的觀念清單（依教學順序）

每個觀念都附上給初學者的講法。這是講師備課的完整清單；依 cold review 後的密度控制，課堂上只點名其中約 20 個，其餘（如 checkpointer、腳本四原則、收回子 agent 的趨勢）放講義。標「先備」的是沒講學生會聽不懂的，標「新」的是 2025–2026 年才出現、原提案沒有的。

### 第 1 堂要講的

| # | 觀念 | 類型 | 給初學者的講法 |
| --- | --- | --- | --- |
| 1 | LLM 只會「接下一段字」 | 先備 | 它是一個超強的接話機器：你給一段文字，它猜最合理的下一段。它不會記得上一次對話，除非你把對話再貼給它。 |
| 2 | Token 與 context window | 先備 | Token 是模型讀字的最小單位，中文大約一到兩個字一個 token。Context window 是它一次能看的字數上限，像一張桌子，東西放太多就擺不下。 |
| 3 | Prompt 與 system prompt | 先備 | 你跟它說的話叫 prompt；放在最前面、每次都在的那段「你是誰、要遵守什麼」叫 system prompt。 |
| 4 | Tool calling（工具呼叫） | 先備 | 模型本身不能執行程式、不能上網。它只能回一段「我想呼叫 run\_code 這個函式，參數是……」的文字，由你的 Python 真的去執行，再把結果貼回去給它。這是 agent 能「做事」的唯一管道。 |
| 5 | Agent 是什麼 | 先備 | Agent = 模型 + 一組工具 + 一個迴圈。迴圈很簡單：問模型 → 它要用工具就執行、把結果貼回去 → 再問 → 直到它說不用工具了。Anthropic 和 LangChain 都是這樣定義的。 |
| 6 | Workflow 與 agent 的差別 | 先備 | Workflow：路線是你用程式畫好的，AI 只負責每一站的工作。Agent：下一步走哪由 AI 自己決定。前者穩、後者彈性大。 |
| 7 | LangGraph 的 State、Node、Edge | 原提案 | 對照 dict、函式、箭頭；條件邊就是 if。用手搖飲店的訂單紙與工作站比喻。 |
| 8 | 每個節點只寫自己的欄位 | 原提案 | 看 `stream_mode="values"` 的逐步輸出，訂單紙一格一格被填滿。 |
| 9 | 三個設計模式 | 新 | Prompt chaining（串接）、routing（分流）、evaluator-optimizer（產出 + 檢查 + 退回重做），出自 Anthropic〈Building effective agents〉。 |
| 10 | LangChain 1.0 的 `create_agent` | 新 | 2025 年 10 月起，LangChain 的標準 agent 寫法是 `create_agent(model, tools)`，它底下自動幫你畫好「模型節點 ↔ 工具節點」的迴圈，回傳的就是一個 LangGraph。所以 LangGraph 和 LangChain 不是對手，是上下層。 |
| 11 | Recursion limit 與 checkpointer | 新 | Agent 可能繞圈不停，所以要設 `recursion_limit`（notebook 1-B 設 25 步就停）。注意：LangGraph 1.0 預設是 25；從 1.1 起預設放寬到 10007，不設就會繞很久。Checkpointer 加 `thread_id` 可以把 State 存起來，下次接著跑，這就是原提案說的「state 未丟失」。 |
| 12 | 0.99 的 10 次方 | 新 | 每步 99% 成功的 10 步流程，整體只剩約 90%；每步 95% 只剩約 60%。所以要在中間放檢查站。 |
| 13 | Harness：Agent = Model + Harness | 新 | 模型是馬，harness 是韁繩和馬鞍。流程圖、檢查節點、說明書都是 harness。2026 年業界的共識是 harness 常常比模型更決定成敗。 |

| # | 觀念 | 類型 | 給初學者的講法 |
| --- | --- | --- | --- |
| 25 | Tool 的兩種來源：本地函式與 MCP | 先備（社課教過） | 自己寫的 `@tool` 函式是本地工具；MCP 是工具的標準插座，工具住在別的程式或服務裡、透過協定接進來、自帶認證。MCP 不是另一種 agent，是「工具」這一格的延伸。代價：連上後所有 tool 定義一次進桌子。 |

### 第 2 堂要講的

| # | 觀念 | 類型 | 給初學者的講法 |
| --- | --- | --- | --- |
| 14 | Agent Skill 是什麼 | 原提案 | 一個資料夾加一份 SKILL.md，是給 AI 的「工作手冊」。程式不動，換手冊就能換行為。 |
| 15 | SKILL.md 的格式 | 原提案 | 開頭兩條虛線之間是名片（name、description），下面是手冊內容。name 只能小寫英文、數字、連字號，最多 64 字元。 |
| 16 | 漸進式揭露三層 | 原提案 | 書背（name + description，約 100 token）→ 內文（整份 SKILL.md，建議 5,000 token 以內）→ 附錄（references/、scripts/，需要才開）。 |
| 17 | description 決定會不會被用 | 原提案 | AI 只靠 description 決定要不要翻開這本手冊，所以要寫「做什麼、什麼時候用」。 |
| 18 | 什麼該寫成程式、文字、腳本 | 新 | 一定要每次發生的順序和檢查 → 寫進 LangGraph 程式。需要判斷、風格、領域知識、步驟說明 → 寫進 SKILL.md 文字。重複、脆弱、必須一模一樣的操作 → 寫成 scripts/ 裡的小程式，叫 AI 執行而不是叫它自己寫。 |
| 19 | scripts/ 的設計原則 | 新 | 一個腳本只做一件事、像小型命令列工具、輸出要讓 AI 看得懂（簡短的成功或失敗訊息，不要整段 traceback）、不放帳號密碼。 |
| 20 | 開放標準與跨工具 | 新 | Skill 格式由 Anthropic 發起、已開放成共同標準，Claude Code、Codex、Cursor、Gemini CLI 等都能讀，放在 `.claude/skills/` 或 `.agents/skills/`。 |
| 21 | Prompt injection 與供應鏈風險 | 原提案 | Skill 拿到的權限和 AI 一樣；2026 年兩份研究：26%–37% 的公開 Skill 至少有一個安全問題，約 5% 疑似惡意，附腳本的 Skill 風險是純文字的 2.12 倍。 |
| 22 | 把 Skill 接進 graph | 原提案 | 一個 skill\_loader 節點讀所有 Skill 的名片，讓模型挑一份，把內文放進 State 給下一個節點用；腳本則註冊成 agent 的工具。 |
| 23 | Guides 與 sensors | 新 | Harness 分兩類：行動前引導（流程圖、SKILL.md）和行動後檢查（測試、格式檢查）。Fowler 的觀察：檢查比引導更有價值，但多數人只投資引導。 |
| 24 | 業界工具一瞥 | 新 | Claude Code 的 AGENTS.md（給 AI 的專案說明）、hooks（每次都會執行的小程式，能擋下危險指令）。講師示範 5 分鐘即可。 |

| # | 觀念 | 類型 | 給初學者的講法 |
| --- | --- | --- | --- |
| 26 | 五個抽屜 | 新 | 程式、tool、MCP、Skill、子 agent。每個功能只能放一格。一句話：tool 是做事的函式，MCP 是插座，Skill 是手冊。 |
| 27 | 六問決策 | 新 | 做還是知道怎麼做？要連外部活系統嗎？能寫成 if 且不能漏嗎？AI 會一直重寫嗎？需要第二個 agent 嗎？要拆的話照什麼拆？ |
| 28 | 何時要第二個 agent | 新 | Anthropic 2026 年 1 月：只有 context 污染、可平行、專門化三種情況划算，代價 3–10 倍 token；照 context 拆不照工作類型拆；驗證子 agent 最穩，但要防「早早宣布成功」；2026 年 10 月趨勢是把子 agent 收回主 agent。 |

## 第 1 堂：什麼是 agent，用 LangGraph 做一個

目標：學生能說出 agent 的三個組成（模型、工具、迴圈），能看著流程圖預測資料怎麼走，並親眼看到「路線由程式決定」和「路線由 AI 決定」兩種 agent 的差別。

| 時間 | 段落 | 內容 | 學生做什麼 |
| --- | --- | --- | --- |
| 0:00–0:10 | 開場：同一個 AI，兩種結局 | 同一段有 bug 的作業，直接問 AI 兩次、交給作業小助教兩次，比較穩定度。結論：AI 是同一個，差別在外面那一層。 | 看 |
| 0:10–0:28 | 先備知識：AI 到底怎麼「做事」 | 觀念 1–6。重點在 tool calling：讓學生看模型回傳的那段「我想呼叫 run\_code」的 JSON，再看 Python 真的去執行、把結果貼回去。畫出 agent 迴圈。Workflow 與 agent 的差別。 | notebook 1-0：執行一格，看到模型回傳的工具呼叫 JSON |
| 0:28–0:52 | Notebook 1-A：Workflow，路線由程式決定 | 觀念 7–9。先不接 AI，三個純 Python 節點：State 是 dict、Node 是函式、Edge 是箭頭、條件邊是 if；`stream_mode="values"` 看訂單紙逐步填滿。再把 give\_feedback 換成呼叫模型，加 check\_format 退回重寫，講三個設計模式。 | 換三段作業先預測再執行；調「最多重試次數」看 retries 變化 |
| 0:52–1:02 | 中場休息 |  |  |
| 1:02–1:30 | Notebook 1-B：Agent，路線由 AI 決定；tool 與 MCP | 觀念 10–11、25。給模型三個工具：`run_code`、`check_indent（縮排與行長，故意不碰命名，留給第 2 堂 2-B）`、`read_spec`。用 `create_agent(model, tools)` 做出 agent，印出每一步選的工具；展開底下的兩節點 LangGraph；同一段作業跑兩次看順序不同；故意繞圈被 recursion limit 停下。最後 5 分鐘講 tool 的兩種來源：自己寫的本地函式 vs 透過 MCP 插上的外部工具（之前社課教過的 MCP 在這裡定位：它是 tool 的標準插座，不是另一種 agent）。 | 先預測它會先用哪個工具，再執行比對；改 system prompt 加一句看順序有沒有變；看 MCP 接上後 tool 定義占掉多少 token |
| 1:30–1:50 | 何時鎖死、何時放手 | 觀念 12–13。0.99^10 的數學；workflow 穩但只處理想到的情況，agent 彈性大但會繞路；「雙拼」第一次出現：把 agent 放進 workflow 的某一個節點。Harness 的比喻。預告：今天學的程式、tool、MCP 是五個抽屜的前三格，下週補上 Skill 和子 agent。 | 填「該鎖死還是放手」學習單 |
| 1:50–2:00 | 收尾 | 今天三件事；課後作業；預告第 2 堂。 |  |

&#91;embedded content: 作業小助教的 LangGraph 流程（notebook 1-A）\]

從 START 到 END 是 prompt chaining；check\_syntax 之後的分叉是 routing；check\_format 退回 give\_feedback 的迴圈是 evaluator-optimizer。

**Notebook 1-B 的 agent 長這樣（講師展開給學生看的版本）：**

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def run_code(code: str) -> str:
    """安全地執行一段 Python 作業，回傳輸出或錯誤訊息。"""
    ...

@tool
def check_style(code: str) -> str:
    """檢查變數命名與縮排，回傳問題清單。"""
    ...

agent = create_agent(model, tools=[run_code, check_style, read_spec],
                     system_prompt="你是 Python 作業小助教……")

for step in agent.stream({"messages": [("user", 作業)]}, stream_mode="values"):
    印出這一步模型說了什麼、選了哪個工具
```

**「該鎖死還是放手」學習單（1:30 段落用）：**

| 步驟 | 鎖死（寫進流程） | 放手（讓 AI 決定） | 為什麼 |
| --- | --- | --- | --- |
| 一定要先檢查語法 | ✓ |  | 順序錯了後面全錯 |
| 回饋用什麼語氣 |  | ✓ | 需要判斷 |
| 回饋一定要有「優點」和「改進」兩段 | ✓ |  | 能用程式檢查 |
| 要不要執行作業看輸出 |  | ✓ | 看情況 |

**課後作業**：把自己寫過的一段 Python 作業分別丟進 1-A 和 1-B，截圖兩邊的執行過程，寫一句話說哪邊的結果你比較信任、為什麼。

## 第 2 堂：Agent Skills，什麼該寫成說明書、什麼該寫成腳本

目標：學生能解釋 Skill 是什麼、看得懂 SKILL.md、能判斷一件事該寫進程式、寫進 SKILL.md 文字還是 scripts/ 的小程式，知道為什麼不能隨便裝別人的 Skill，並看到 Skill 接回 LangGraph 後 state 沒有丟失。

**密度控制（依 cold review 修正）**：本堂新名詞控制在 8 個：Skill、名片、腳本、prompt injection、子 agent、驗證 agent，加上複習的 MCP 與雙拼。每張投影片只帶一個新名詞，先看例子再給名字，表格最多三列。砂掉的內容（Tool vs Skill 八列對照、MCP vs Skill 表、腳本四原則、token 數字、checkpointer、收回子 agent 的趨勢、兩份研究的細部數字）全部放進講義，見第 2 堂投影片分頁末。六問改為「先拆再總結」，不先給公式。

| 時間 | 段落 | 內容 | 學生做什麼 |
| --- | --- | --- | --- |
| 0:00–0:08 | 回顧 + 便利貼 | 上週三件事擺回桌上。發一個真實需求（30 題、抓 GitHub、200 份、寄信），學生在便利貼上寫「會分幾個 agent」貼白板，最後 35 分鐘回來重貼。 | 寫便利貼 |
| 0:08–0:28 | 2-A：Skill 是給 AI 的工作手冊 | 新名詞只有 Skill 和名片。從「個性寫死在 system prompt」的麻煩開始，引出手冊；手冊長相；為什麼要有名片（AI 選書只看書背）；動手改手冊看 AI 變臉；手冊可以附東西。 | 改規則與 description，先寫預測再執行 |
| 0:28–0:48 | 2-B：同一件事的三種放法 | 新名詞只有腳本。「檢查變數命名」分別放進手冊文字、腳本、LangGraph 節點，各跑三次並排看。本堂口訣在這裡出現。停一下：五件事各放哪。 | 先猜哪個版本三次一樣，再執行；紙上填五件事 |
| 0:48–0:58 | 中場休息 |  |  |
| 0:58–1:06 | 2-C：別人的手冊能直接用嗎 | 新名詞只有 prompt injection。藏指令的手冊實驗（假金鑰）；一個數字（每 3–4 份有 1 份有問題）、三個習慣。細部數據放講義。 | 執行，找出藏指令的那一行 |
| 1:06–1:15 | 2-D：雙核 demo | 不教新名詞。講師跑給大家看：外層 1-A 流程鎖順序，give\_feedback 裡面是小 agent，用 2-A 的手冊和 2-B 的腳本。skill\_loader 和腳本包成工具各一句話帶過。checkpointer 只提一句，放講義。 | 看 |
| 1:15–1:50 | 系統設計：邊拆邊教 | 新名詞：子 agent、驗證 agent（MCP 為上週複習）。回到便利貼，一個功能一張投影片放進格子：抓作業→MCP；先檢語法→程式；語氣與 30 題→手冊；命名檢查→腳本；200 份→子 agent（用「桌子堆滿 149 份」的災難故事引出）；驗證→驗證 agent（溫和與嚴格不該是同一人）；不要三人接力；寄信→MCP + 人工確認。分工圖最後才長完整，六問最後才總結。新增兩張、約多 4 分鐘：「RAG 用哪一格」（tool／MCP／Skill）接在 30 題 references/ 之後；「分工圖搬上雲端」部署地圖接在分工圖之後，時間不夠可跳過（課後補充會再講）。 | 跟著填設計單；兩次停一下在紙上作答 |
| 1:50–2:00 | 工作坊 + 收束 | 兩人一組抽需求卡用六問填設計單；講師抽一組只問「這裡為什麼需要 agent」。收束三句話；講師 2 分鐘示範 Claude Code 的 skills 資料夾與 hook。 | 設計、說明；填回饋 |

**三格判斷表（0:35 段落用，這是本課程最重要的一張表）：**

| 這件事的特性 | 該放哪裡 | 作業小助教的例子 | 為什麼 |
| --- | --- | --- | --- |
| 順序不能錯、每次都必須發生、能用程式判斷對錯 | **LangGraph 程式**（節點與邊） | 先檢查語法再給回饋；回饋一定要有兩段 | 寫在文字裡 AI 可能忘記，寫成程式一定執行 |
| 需要判斷、有風格、是領域知識、是一套步驟說明 | **SKILL.md 文字** | 回饋的語氣；什麼算「好的變數名稱」的說明；「先找優點再找問題」的步驟 | 這些沒有標準答案，交給 AI 判斷比寫死好 |
| 重複、脆弱、必須每次一模一樣、AI 自己寫容易寫錯 | **scripts/ 裡的小程式**，叫 AI 執行它 | `check_naming.py`、`run_tests.sh` | 讓 AI 自己重寫一次檢查邏輯，每次都不同；給它一個現成工具，每次都一樣 |

判斷口訣：**能寫成 if 的寫進程式，要靠經驗判斷的寫進文字，重複又怕出錯的寫成腳本。**

**scripts/ 的四個原則（觀念 19）：**

1. 一個腳本只做一件事，像小型命令列工具，能用參數呼叫
2. 輸出要讓 AI 看得懂：短短一行「OK」或「第 3 行 myVar 不符合規則」，不要整段 traceback
3. 不放帳號、密碼、金鑰
4. 不要因為有 scripts/ 資料夾就硬塞程式進去；只有當你看到 AI 一直重寫同一段邏輯時才加

**2-B 的三個版本並排（講師投影用）：**

| 版本 | 怎麼做 | 跑三次的結果 |
| --- | --- | --- |
| A：寫在 SKILL.md 文字裡 | 「請檢查變數名稱是否為小寫加底線」 | 三次抓到的問題數量不同，有一次漏了 |
| B：寫成 scripts/check\_naming.py | SKILL.md 寫「執行 check\_naming.py 並引用它的輸出」 | 三次完全相同 |
| C：寫成 LangGraph 節點 | 不經過 AI，直接跑 Python | 三次完全相同，而且不用花 token |

講師收尾：B 和 C 結果一樣，差別在 B 是 AI 「決定」要用這個工具，C 是程式「強迫」一定執行。要不要讓 AI 決定，就看這件事能不能漏掉。

**課後作業**：替作業小助教想一個新功能，寫下它該放程式、文字還是腳本，以及為什麼。選做：用任何 AI 工具搭配下面的四段式範本把它做出來。

```
目標：我要加一個檢查「有沒有寫註解」的功能。
背景：程式用 LangGraph，State 有 code、syntax_ok、feedback 三格；Skill 放在 skills/ 資料夾。
限制：只新增一個檔案，不要改現有節點。
完成條件：輸入一段沒有註解的程式時，回饋裡要提到「建議加註解」。
```

## 系統設計：什麼該放 agent、Skill、tool、MCP（第 2 堂 1:27–2:00）

目標：學生拿到一個多 agent 的需求，能用「五個抽屜」和「六問決策」把每個功能拆進程式、tool、MCP、Skill、子 agent，並說出為什麼。這是兩堂課零件的收束，也是業界最少人系統化教的部分。MCP 在第 1 堂 1-B 隨 tool 一起教（tool 的標準插座），這裡只做定位。

### 教學框架：五個抽屜

用「一間公司」比喻。每件事只能放進一個抽屜，放錯不會壞，但會不穩、變貴或難維護。

| 抽屜 | 公司裡的對應 | 它是什麼 | 放什麼進去 | 第幾堂學過 |
| --- | --- | --- | --- | --- |
| 1. 程式（graph） | SOP、作業流程 | 用 Python 寫死的順序與檢查 | 順序不能錯、每次都要發生、能用 if 判斷的事 | 第 1 堂 |
| 2. Tool（工具） | 員工手邊的計算機、印表機 | 一個函式，agent 可以呼叫，做一件事、回一個結果 | 要「做」的動作：執行程式、查資料、寄信、算東西 | 第 1 堂 1-B |
| 3. MCP | 外部供應商的標準插座 | Tool 的標準化外接方式：工具住在另一個程式或服務裡，透過一個協定接進來，自帶認證 | 需要連到活的外部系統（資料庫、GitHub、行事曆）的 tool，或要給多個 agent 共用的 tool | 之前社課教過，本堂重新定位 |
| 4. Skill | 工作手冊、SOP 說明書 | 一份 SKILL.md，教 AI「怎麼用工具做好一件事」 | 要「知道怎麼做」的事：步驟、風格、判斷標準、領域知識、哪個情況用哪個工具 | 第 2 堂 |
| 5. 子 agent | 另一位同事 | 另一個有自己 context window 的 AI | 只有三種情況才開：context 會被污染、可以平行做、需要完全不同的工具組或人設 | 本堂 |

**Hook 與檢查節點**不是抽屜，是稽核：每個抽屜外面都可以加。

**一句話記住 tool、MCP、Skill 的關係**：tool 是做事的函式，MCP 是把 tool 接進來的插座，Skill 是教 AI 怎麼用這些 tool 的手冊。Anthropic 的原話：MCP 把 AI 連到資料，Skills 教 AI 拿到資料後該做什麼。

### Tool 與 Skill 的差異（最容易搞混的一組）

|  | Tool | Skill |
| --- | --- | --- |
| 本質 | 一個可以被呼叫的函式 | 一份給 AI 讀的說明書 |
| 誰執行 | 你的程式執行，AI 只負責「決定呼叫」和「拿結果」 | AI 讀完後自己執行（判斷、寫作、或再去呼叫 tool） |
| 輸入輸出 | 固定：參數進、結果出 | 沒有固定格式，是行為的改變 |
| 載入時機 | 定義一開始就在桌上 | 名片在桌上，內文需要才翻 |
| 能不能保證 | 呼叫了就一定照程式跑 | 是建議，AI 可能部分遵守 |
| 改一次要動什麼 | 程式碼 | 文字檔 |
| 擅長 | 做一件明確的事：執行、查、算、寄 | 教一套做法：步驟、風格、判斷標準、什麼時候用哪個 tool |

口訣：**Tool 回答「能做什麼」，Skill 回答「該怎麼做」。** 兩個常見混淆：把評分標準寫成 tool（判斷不是動作，規則寫不完 → Skill）；把執行程式寫成 Skill（AI 讀了說明書也不能執行，需要真的能跑的函式 → Tool）。一個功能常常兩個都要：tool 提供能力，Skill 教 AI 什麼時候用、怎麼組合。

### 六問決策流程

拿到一件事，依序問：

1. **它是「做」還是「知道怎麼做」？** 做 → tool（問 2）；知道怎麼做 → Skill 文字或程式（問 3）
2. **這個 tool 要連到外部活系統、需要認證、或要給多個 agent 共用嗎？** 是 → MCP；否 → 本地函式就好
3. **這件事能寫成 if、而且不能漏掉嗎？** 是 → 程式（graph 節點或 hook）；否 → Skill 文字
4. **AI 會不會一直重寫同一段邏輯？** 會 → 放進 Skill 的 scripts/
5. **需要第二個 agent 嗎？只在三種情況說是**：這一步會產生大量和後面無關的內容（context 污染）；幾件事彼此獨立可以同時做（平行）；需要的工具組或人設和主 agent 衝突（專門化）。都不是 → 留在同一個 agent
6. **真的要拆 agent 時，照什麼拆？** 照「需要哪些 context」拆，不要照「工作類型」拆。同一個功能的規劃、實作、測試留在一起；可以獨立驗證的（跑測試、對規格）才拆出去

### MCP 與 Skills：不是對手，是上下層

|  | MCP | Skill |
| --- | --- | --- |
| 回答的問題 | AI 能碰到什麼 | AI 該怎麼做 |
| 形式 | 一個常駐的 server，透過協定提供 tools | 一個資料夾裡的文字檔 |
| 載入方式 | 連上後所有 tool 定義都放進桌子 | 先看書背，需要才翻 |
| 認證 | 自帶（OAuth 等） | 沒有 |
| 適合 | 活的資料、外部系統、多人共用 | 流程、風格、領域知識、怎麼用 MCP |
| 來源 | Anthropic 2024 年底發起，2025 年 12 月捐給 Linux 基金會 | Anthropic 2025 年 10 月發起，同年 12 月開放標準 |

2026 年的主流做法是兩者一起用：MCP 負責連線，Skill 負責教 AI 怎麼用那些連線。甚至出現「用 Skill 包 MCP」的模式：一個 MCP server 有 80 個 tool 會把桌子塞爆，改寫成一份 Skill，描述「要查作業時用哪三個 tool、順序是什麼」，桌子只放一張書背。

### RAG 用哪一格呈現（第 2 堂投影片 34）

RAG（Retrieval-Augmented Generation，先查再答）：先從一大堆資料裡搜尋出最相關的幾段，放上桌給 AI 參考，再讓它回答。它不是新的抽屜，而是拆進現有的三格：

| 抽屜 | RAG 的哪一部分 | 作業小助教的例子 |
| --- | --- | --- |
| Tool | 「查資料」這個動作本身；資料不多、只有自己用 → 本地 `@tool` 就夠 | `search_past_mistakes(query)` 回傳最像的幾筆歷屆作業錯誤 |
| MCP | 知識庫、向量資料庫是別人的服務、要認證，或要給多個 agent 共用 → 同一個查詢工具改從 MCP 插座接（agent 用起來和本地 tool 一樣） | 全系共用的歷屆作業資料庫 |
| Skill | 不負責查；教 AI 什麼時候該查、用什麼關鍵字、查到之後怎麼引用。資料少到能整份讀時直接放 `references/`，根本不需要 RAG | 「先查這題的常見錯誤，只引用最相關的兩筆」；30 題的題目要求放 references/ |

每一份都一定要先查 → 寫成流程裡固定的 retrieve 節點（程式），這叫固定的 RAG；把搜尋做成 tool、讓 agent 自己決定要不要查，叫 agentic RAG。上雲端時向量資料放在資料庫裡（例如和 checkpointer 同一個 Postgres 加 pgvector），見下面的部署地圖。

一句話：**RAG 不是新的抽屜：查 ＝ tool，插座 ＝ MCP，怎麼查 ＝ Skill。**

### 何時需要第二個 agent

Anthropic 2026 年 1 月的指引（出處見參考資料）：

- **先用單一 agent。** 很多團隊花幾個月建多 agent 架構，最後發現把單一 agent 的 prompt 寫好就有一樣的效果。
- **多 agent 的代價是 3–10 倍的 token**，因為 context 要複製、agent 之間要傳話、結果要摘要。
- **只有三種情況划算**：context 污染、可平行、需要專門化（工具超過 15–20 個、人設互相衝突、領域知識太多）。
- **照 context 拆，不要照工作類型拆。** 「規劃 agent、實作 agent、測試 agent」這種拆法會變成傳話遊戲，每次交接都掉資訊。
- **驗證子 agent 是最穩的模式**：它只需要產出物和合格標準，不需要知道東西是怎麼做的，所以不會有傳話問題。要防「早早宣布成功」：明確要求它跑完整測試。
- **2026 年 10 月的新趨勢**：模型變強後，很多子 agent 可以收回主 agent，改用漸進式揭露的 context 和 tool search。所以今天教的是「什麼時候不要拆」，比「怎麼拆」更重要。

### 完整範例：升級版作業小助教的分工

開場的需求拆完應該長這樣。這張圖就是「設計一個多 agent 系統時，什麼功能放哪裡」的樣板，工作坊的設計單照著它填。

&#91;embedded content: 升級版作業小助教：每個功能放在哪個抽屜（第 3 堂的標準答案）\]

| 需求裡的功能 | 放哪個抽屜 | 六問裡的哪一問 | 為什麼不放別的抽屜 |
| --- | --- | --- | --- |
| 從 GitHub 抓 200 份作業 | 3 MCP | 問 2：外部活系統、要認證 | 寫成本地函式要自己處理 token 和分頁；Skill 不能連線 |
| 一定先檢查語法 | 1 程式 | 問 3：能寫成 if、不能漏 | 寫在 Skill 裡 AI 可能跳過 |
| 200 份同時批 | 5 子 agent（平行） | 問 5：彼此獨立 | 單一 agent 批 200 份，第 150 份時桌子已經塞滿前面的內容 |
| 回饋的語氣與步驟、評分標準 | 4 Skill | 問 1：知道怎麼做 | 寫在程式裡要改十次；寫在 system prompt 不能換 |
| 30 個題目各自的要求 | 4 Skill 的 references/ | 問 1 + 漸進式揭露 | 30 份題目全塞 system prompt 會占掉桌子 |
| 執行作業看輸出 | 2 Tool | 問 1：做 | 是動作不是知識 |
| 檢查變數命名 | 4 Skill 的 scripts/ | 問 4：AI 會一直重寫 | 第 2 堂 2-B 已證明文字版會飄 |
| 先讀題目還是先執行 | 交給回饋 agent 決定 | 問 3 反面：不是不能漏的順序 | 鎖死反而浪費：有些作業不用執行 |
| 驗證回饋沒有亂講行號 | 5 子 agent（驗證） | 問 6：可獨立驗證 | 讓寫回饋的 agent 自己驗，容易自己放過自己 |
| 寄信給學生 | 3 MCP + hook | 問 2 + 稽核 | 寄信不可逆，hook 強制人工確認 |
| 回饋一定要有兩段 | 1 程式（驗證節點） | 問 3 | 格式能用程式檢查，不必花 token 讓 AI 判斷 |
| 從上千筆歷屆作業找相似錯誤（RAG） | 2 Tool（查詢）；資料庫在外面或要共用 → 3 MCP；怎麼查寫進 4 Skill | 問 1 ＋ 問 2 | 太多了不能整份放 references/；Skill 自己不能查，只能教怎麼查 |

**三個常見的錯放：**

- 把「規劃、寫回饋、檢查」拆成三個 agent：這是照工作類型拆，會變傳話遊戲。寫回饋和檢查自己的格式應該在同一個 agent；只有黑箱驗證才拆出去。
- 把 30 個題目的要求全寫進 system prompt：桌子塞爆，每一份作業都要付 30 份題目的 token。放進 Skill 的 references/，需要哪題才翻哪題。
- 為了「以後可能用到」先接 MCP：一個 MCP server 動輒幾十個 tool 定義全進桌子。只有真的要連外部活系統才用，而且用一份 Skill 告訴 AI 只用其中幾個。

### 設計單（工作坊用）

| 需求裡的每件事 | 抽屜 | 為什麼（引用六問的哪一問） |
| --- | --- | --- |
| 例：一定先檢查語法 | 1 程式 | 問 3：能寫成 if 且不能漏 |
| 例：從 GitHub 抓作業 | 3 MCP | 問 2：外部活系統、要認證 |
| 例：回饋的語氣與步驟 | 4 Skill | 問 1：知道怎麼做 |
| 例：檢查變數命名 | 4 Skill 的 scripts/ | 問 4：AI 會一直重寫 |
| 例：一次批 200 份 | 5 子 agent（平行） | 問 5：彼此獨立 |
| 例：驗證回饋沒有亂講 | 5 子 agent（驗證） | 問 6：可獨立驗證 |

### 補充：多 agent 系統怎麼部署到雲端（課後自學）

第 2 堂簡報第 47–54 張（參考來源在第 55–56 張），課堂上不講，給想把作業小助教真的放上線的同學。內容依序是：離開 Colab 要換掉的三樣東西（模型金鑰改放 Secret Manager、檔案改裝進容器、checkpointer 改用 Postgres）；用 `langgraph.json` 打包、`langgraph dev` 本機跑通；三種上雲做法（LangSmith Deployment、自己的容器如 Cloud Run、Google Agent Runtime 或 AWS Bedrock AgentCore）；五個抽屜搬上雲後各變成什麼（含遠端 MCP）；用 `Send` 平行批 200 份並設並行上限、先算成本；寄信前用 `interrupt()` 人工確認；上線後的 trace、eval 進 CI 與權限清單。對應的課後選做 notebook 是 [`2-E_deploy.ipynb`](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-E_deploy.ipynb)，四個練習都在免費 Colab 跑，不需要真的部署：練習 1 在 Colab 開一個真的 MCP server「作業倉庫」（stdio 本機插座、Streamable HTTP 網址）；練習 2 把整張分工圖跑一次（MCP 抓作業 → 程式檢查語法 → `Send` 開批改子 agent → 驗證 agent → `interrupt()` 等人確認 → MCP 寄信，並數模型呼叫次數與 token）；練習 3 把它包成 API 服務；練習 4 上線前檢查並產生部署檔。

**部署地圖（課堂上放在第 2 堂投影片 41，約 2 分鐘，時間不夠可跳過）**：把分工圖搬上雲端，每一格住在不同的地方。

| 住在哪裡 | 放什麼 |
| --- | --- |
| 你的容器（Cloud Run 或 LangSmith Deployment） | API、外層流程（程式）、回饋 agent、本地 tool、`skills/` 與 `scripts/`（跟映像一起出貨） |
| 資料庫（Postgres） | checkpointer（每個 `thread_id` 的 State、等人按確認的信）、RAG 的向量資料 |
| 保管箱（Secret Manager） | 模型 API key、OAuth token（部署時才變成環境變數） |
| 別人的服務（透過網路呼叫） | 模型 API、遠端 MCP server（抓 GitHub 作業、寄信）、沙箱（`run_code` 跑學生程式） |
| 旁邊 | 任務佇列（200 份排隊）、Trace／Eval 儀表板 |

一句話：程式、手冊、腳本跟著容器走；會變的資料進資料庫；鑰匙進保管箱；別人的能力透過網路接進來。

## 講師準備的 Colab notebook

學生只執行、不寫程式，notebook 本身就是教材。每一段照「預測 → 執行 → 比對」設計。

| Notebook | 對應段落 | 學生會改的地方 |
| --- | --- | --- |
| `1-0_tool_calling.ipynb` | 第 1 堂 0:10 | 不用改，只看模型回傳的工具呼叫 JSON |
| `1-A_workflow.ipynb` | 第 1 堂 0:30 | 作業程式、最多重試次數、回饋字數上限 |
| `1-B_agent.ipynb` | 第 1 堂 1:05 | 作業程式、system prompt 裡的一句話 |
| `2-A_skills.ipynb` | 第 2 堂 0:10 | 兩份 SKILL.md 的規則與 description |
| `2-B_code_text_script.ipynb` | 第 2 堂 0:35 | 不用改，執行三個版本並比對 |
| `2-C_security.ipynb` | 第 2 堂 1:05 | 不用改，找出藏指令的行 |
| `2-D_dual_core.ipynb` | 第 2 堂 1:25 | thread\_id |
| `2-E_deploy.ipynb`（課後選做） | 第 2 堂補充：上雲端（投影片 47–54） | 選做四個練習：真的 MCP server、整張分工圖跑一次（子 agent、驗證 agent、寄信前確認）、API 服務、上線前檢查 |

Notebook 執行後在 `/content/review-bot/` 產生的檔案：

```
review-bot/
├── graph.py                     # 1-A：workflow
├── agent.py                     # 1-B：create_agent 版 agent
├── tools/
│   ├── run_code.py
│   ├── check_indent.py
│   └── read_spec.py
├── skills/
│   ├── friendly-feedback/SKILL.md
│   ├── strict-review/SKILL.md
│   └── naming-check/
│       ├── SKILL.md
│       └── scripts/check_naming.py   # 2-B 的腳本
└── dual_core.py                 # 2-D：workflow 節點裡包 agent + skill_loader
```

**設計原則：**

- 學生要改的值一律做成表單欄位（`#@param`）
- 程式碼格預設收合，只露出標題和輸出；想看的人自己展開
- 每段前一格文字格寫預測題，執行後一格寫「你看到了什麼」
- 每段都能從第一格獨立重跑
- SKILL.md 和 scripts 用 `%%writefile` 寫進檔案，學生改完那一格再執行
- 1-B 的 `run_code` 工具要在受限環境執行學生程式（禁 import os、subprocess，設 timeout）
- 2-C 的金鑰一律用假的

**最低完成標準（學生）：**

- 第 1 堂：能說出 agent 的三個組成；1-A 學習單三題作答；1-B 看到 agent 兩次選工具順序不同並說出原因
- 第 2 堂：改過一次 SKILL.md 並看到回饋改變；三格判斷表填對至少兩格；2-C 找出藏指令的行；2-D 換 thread\_id 重跑並說明 State 有沒有保留

## 背景：2026 年的 harness engineering 與 AI-native development

*這一節是講師備課用的背景。對初學者，課堂上只用到最後的 0.99^10 數字和下方的四格圖。*

Harness engineering 在 2026 年 2 月由 OpenAI 帶紅，4 月 Thoughtworks 的 Birgitta Böckeler 在 Martin Fowler 網站給出「guides / sensors」這套通用詞彙，現在已是討論 agent 可靠性的主流框架。核心公式是 **Agent = Model + Harness**：harness 是模型以外的一切，包括指令、工具、權限、流程控制、記憶和驗證。

&#91;embedded content: 課程工具在 guides / sensors 四格中的位置\]

這張四格圖是整個課程的地圖：每個實作都在補其中一格。分類依 Böckeler 的框架，各工具歸到哪一格是本課程的教學整理。

**課堂上要講的幾個關鍵案例：**

1. **OpenAI 的零手寫程式碼實驗**（2026-02-11，Ryan Lopopolo）：團隊從 2025 年 8 月的空 repo 開始，全部由 Codex 產生，幾週內出貨約百萬行程式碼。工程師的工作變成設計環境、寫清楚意圖、建立回饋迴圈。初期進展慢不是因為模型不行，而是環境描述不足。另一個教訓：context 是稀缺資源，一個巨大的指令檔會擠掉任務本身。
2. **Böckeler 的 guides / sensors 分類**（2026 年 4 月）：guides 是行動前的前饋控制，sensors 是行動後的回饋控制；兩者又各分 computational（確定性的程式）與 inferential（交給 LLM 判斷）。Fowler 在 7 月的筆記補了一句：conformance tests（sensor）比規格書（guide）更有價值。
3. **Anthropic 的長時間任務 harness**（2025-11-26）：第一個 session 由 initializer agent 建立 `init.sh`、進度紀錄檔、feature list 和初始 git commit，後續每個 session 讀進度、只做一個功能、留下乾淨狀態。2026 年 3 月的續篇再加入 planner / generator / evaluator 三角色。
4. **把錯誤當成永久訊號**（Addy Osmani，2026 年 4 月）：agent 每犯一次錯，就該變成 harness 裡一條新規則、新測試或新工具，而不是重跑一次了事。所以合適的 harness 是從你自己的失敗史長出來的，無法直接下載。
5. **LangChain Deep Agents**：它不是 LangGraph 的替代品，`create_deep_agent()` 回傳的就是一個編譯好的 LangGraph graph，並內建規劃、檔案系統、subagent 與 skills 支援。這正好回答原提案「把 Skills 嵌入 LangGraph」的問題。
6. **AI-native development**：Gartner 把 AI-native development platforms 列為 2026 年策略科技趨勢之首。常見的分法是：AI-assisted 是人寫、AI 補；AI-native 是 AI 產出整個功能，人負責審查與核准。GitHub 的 Spec Kit 把流程拆成 specify → plan → tasks → implement，已支援 30 種以上的 coding agent。

**一個開場就能用的數字**：每一步成功率 99% 的 10 步流程，整體成功率只有 0.99^10 ≈ 90%；每步 95% 的話只剩約 60%。這就是為什麼需要 sensors 在每一步攔截錯誤。

## 課前準備、風險與原提案要修正的地方

學生課前只要 10 分鐘，不需要任何 LLM 或 agent 經驗：用 Google 帳號打開講師分享的 notebook、按「複製到雲端硬碟」、執行第一格看到模型回應即可。不需要買任何訂閱，若 `google.colab.ai` 的免費額度夠用，也不需要 API key。

**先備知識改為**：會 Python 基本語法，看得懂 dict、函式、if、while。LLM、tool calling、agent 的觀念課堂上從零講起（觀念 1–6）。原提案的 vibe coding 經驗、LangChain、git、VS Code、terminal 全部拿掉。報名表的「是否已完成環境安裝」改成「是否已打開並跑通測試 notebook」。

| 風險 | 預防或備案 |
| --- | --- |
| `google.colab.ai` 免費額度在課堂上用完 | 課前用免費帳號實測一次完整流程的用量；備好講師 API key 的版本，或兩人共用一本 notebook |
| 免費帳號沒有 Colab 內建 Gemini 對話功能 | 課前用免費帳號確認；不行就改用 ChatGPT、Claude 或 Gemini 網頁版做 vibe coding 練習 |
| Colab 斷線或跑錯格 | 每段都能從第一格重跑 |
| 學生只按執行、沒有思考 | 每段都有預測題，先寫答案再執行 |
| 進度落後 | 必做：1-A、1-B、2-A；可略：2-B 改為講師示範 |
| 有人程度較好、很快做完 | 給「展開程式碼，找出條件邊寫在哪一行」等加分題 |

**原提案建議修正的三處：**

- **「超過三成的開源 Skills 存在 Prompt Injection 風險」不準確。** Snyk 2026 年 2 月掃描 3,984 個 skills，36.82% 至少有一個安全問題，13.4% 有嚴重問題；arXiv 2601.10338 分析 31,132 個 skills，26.1% 至少有一個漏洞，5.2% 疑似惡意。Prompt injection 只是其中一類。建議改寫為：「2026 年兩份大規模研究發現，約 26%–37% 的公開 Skills 至少有一個安全問題，約 5% 疑似惡意。」
- **「大型科技公司內部依然堅持 LangGraph」沒有引用來源**，建議刪除，或改成有出處的說法（例如 LangChain 的 Deep Agents 本身就建在 LangGraph 上）。
- **定位改成「互補」而不是「對決」。** 標題的「雙拼」正好符合：LangGraph 管流程，Skills 管知識，兩者都是 harness 的一部分。

**尚待決定：**

- 社團能否提供 API 額度作為 `google.colab.ai` 的備案
- 第 2 堂 1:35 的業界示範用 Claude Code 還是 Codex（兩者都支援 Agent Skills）
- 原本預計 25 人上限，初學者每 8–10 人配 1 位助教較合適

## 參考資料

建議講師課前必讀前三篇，其餘可放進課程講義。

1. [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — OpenAI，2026-02-11
2. [Harness Engineering](https://martinfowler.com/articles/harness-engineering.html) — Birgitta Böckeler，martinfowler.com，2026 年 4 月
3. [Effective harnesses for long-running agents](https://anthropic.com/engineering/effective-harnesses-for-long-running-agents) — Anthropic，2025-11-26
4. [Fragments: July 13](https://martinfowler.com/fragments/2026-07-13.html) — Martin Fowler，2026-07-13
5. [Agent Harness Engineering](https://addyosmani.com/blog/agent-harness-engineering/) — Addy Osmani，2026-04-19
6. [Agent Skills 官方網站](https://agentskills.io/) 與 [規格](https://agentskills.io/specification)
7. [What Are LangGraph Deep Agents? The Harness Explained](https://www.truefoundry.com/blog/what-are-langgraph-deep-agents-the-harness-explained) — TrueFoundry，2026-09-21
8. [ToxicSkills: Malicious AI Agent Skills](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub) — Snyk，2026-02-05
9. [Agent Skills in the Wild (arXiv 2601.10338)](https://www.arxiv.org/abs/2601.10338) — Liu 等，2026-01-15
10. [GitHub Spec Kit](https://github.com/github/spec-kit)
11. [How to Block Dangerous Commands with Claude Code Hooks](https://dev.to/tyson_cung/how-to-block-dangerous-commands-with-claude-code-hooks-g5o) — PreToolUse 與 exit code 2 的範例
12. [AI-Native Software Development](https://lucaberton.com/blog/ai-native-software-development-2026/) — Gartner 2026 趨勢的整理

**初學者版補充：**

- [Building effective agents](https://www.anthropic.com/research/building-effective-agents) — Anthropic，2024 年 12 月，三個設計模式的出處
- [All Colab users now get access to Gemini and Gemma models](https://medium.com/@spkshumway) — Google Colab 團隊，2025-11-12，`google.colab.ai` 開放免費帳號
- [LangGraph streaming 說明](https://www.krishnaik.in/coding-labs/langgraph/watching-it-work) — `stream_mode="values"` 與 `"updates"` 的差別

**重新規劃版補充：**

- [LangChain 1.0 release notes](https://docs.langchain.com/oss/python/releases/langchain-v1) — `create_agent` 是 LangChain 1.0 的標準 agent 寫法，底下是 LangGraph 的模型 ↔ 工具迴圈
- [LangChain vs LangGraph (2026)](https://www.testmuai.com/blog/langchain-vs-langgraph/) — 2025-10-22 的 1.0 版後，`create_agent` 取代 `create_react_agent`；同一個 agent 兩種寫法的對照
- [agentskills.io skill.md](https://agentskills.io/skill.md) — scripts/、references/、assets/ 的用途；何時用內嵌指令、何時打包腳本
- [Gemini CLI：Agent Skill best practices](https://geminicli.com/docs/cli/skills-best-practices/) — 腳本用於確定性任務、輸出要對 LLM 友善、低自由度 vs 高自由度的指令
- [Decide when a script beats prose](https://flaviocopes.com/courses/ai-agent-skills/decide-when-a-script-beats-prose/) — 只有當 AI 一直重建同一個步驟時才加腳本；判斷留在文字裡
- [skills-best-practices](https://github.com/mgechev/skills-best-practices/wiki) — 腳本做成小型 CLI、不放函式庫程式碼
- [Anthropic 官方 skills repo](https://github.com/anthropics/skills) — 2-A 拆解用的範例來源

**第 3 堂補充：**

- [Building multi-agent systems: When and how to use them](https://claude.com/resources/articles/building-multi-agent-systems-when-and-how-to-use-them) — Anthropic，2026-01-23。三種划算情況、3–10 倍 token、照 context 拆、驗證子 agent、早早宣布成功
- [Building agents: When to fold subagents into your main agent loop](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop) — Anthropic，2026-10-22。收回子 agent 的趨勢
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — Anthropic，2025 年 6 月。平行子 agent 的來源案例
- [Agent Skills vs MCP](https://atlan.com/know/ai-agent/ai-agent-skills/agent-skills-vs-mcp/) — Atlan，2026-07-16。兩者的時間線、認證差異、「一起用」的共識
- [MCP vs Skills: When to Use Which](https://dev.to/baboon/mcp-vs-skills-when-to-use-which-for-ai-agents-nhe) — MCP 把所有 tool 定義塞進 context vs Skill 漸進式載入；用 Skill 包 MCP
- [Claude Code Skills vs Subagents vs Hooks vs CLAUDE.md](https://chudi.dev/blog/claude-code-skills-vs-subagents-vs-hooks) — 2026-09-29。各機制何時載入、用誰的 context、是否保證觸發
- [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents) — Cognition，2025 年。單一 context 派的論點，課堂上當反方
