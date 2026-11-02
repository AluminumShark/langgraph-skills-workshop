# 從 LangGraph 到 Skills：結構化與非結構化 Agent 的雙拼指南

NTU AI Club 技術工作坊，兩堂各 120 分鐘。講者：李維（Levi, @AluminumShark）、柯宥圻。

## 這個 repo 的狀態

- `slides/session1.html`、`slides/session2.html`：兩堂課的簡報，**已完成**，單一 HTML，只依賴 Google Fonts。← → 換頁、N 看講者備註、F 全螢幕。
- `docs/syllabus.md`：完整課綱（時間表、24 個觀念、七本 notebook 規格、最低完成標準）。**任何實作都以它為準。**
- `docs/slides-session{1,2}-outline.md`：投影片逐張大綱，含每張的「互動／停一下」，notebook 的段落要對得上。
- `docs/reuse-from-old-workshop.md`：從舊教案 `reference/old-workshop/` 抄出來、已改成 review-bot 語境的程式碼，每段標了該放哪本 notebook。
- `docs/original-proposal.txt`：最初的提案，只供對照。
- `notebooks/`：**待實作**，七本 Colab notebook，見下方。
- `review-bot/`：**待實作**，notebook 執行後會在 Colab 的 `/content/review-bot/` 產生的檔案；這裡放講師版的範例 Skill 與工具原始碼，notebook 用 `%%writefile` 把它們寫出去。

## 要做的事：七本 Colab notebook

| 檔名 | 對應段落 | 學生會改的地方 |
| --- | --- | --- |
| `notebooks/1-0_tool_calling.ipynb` | 第 1 堂 0:10 | 不用改，只看模型回傳的工具呼叫 JSON |
| `notebooks/1-A_workflow.ipynb` | 第 1 堂 0:28 | 作業程式、最多重試次數、回饋字數上限 |
| `notebooks/1-B_agent.ipynb` | 第 1 堂 1:02 | 作業程式、system prompt 裡的一句話 |
| `notebooks/2-A_skills.ipynb` | 第 2 堂 0:08 | 兩份 SKILL.md 的規則與 description |
| `notebooks/2-B_code_text_script.ipynb` | 第 2 堂 0:28 | 不用改，執行三個版本並比對 |
| `notebooks/2-C_security.ipynb` | 第 2 堂 0:58 | 不用改，找出藏指令的行 |
| `notebooks/2-D_dual_core.ipynb` | 第 2 堂 1:06 | thread_id |

每本的細節、每段的預測題、三個版本要比什麼，全部在 `docs/syllabus.md` 的「第 1 堂」「第 2 堂」「講師準備的 Colab notebook」三節，以及對應投影片大綱的「互動／停一下」。

## 硬性規範（學生是剛學會 Python 的初學者，只執行、不寫程式）

1. **LLM 呼叫**：優先用 Colab 內建 `from google.colab import ai`（免費帳號不需 API key）。每本第一格做可切換的 provider：`ai.generate_text` 為預設，講師 API key（Gemini 經 `langchain_google_genai`）為備案；兩者都包成同一個 `model` 物件給後面的 cell 用。1-0 的 tool calling 示範若 `google.colab.ai` 不支援 `bind_tools`，就用備案。
2. **學生要改的值一律做成表單欄位** `#@param`，不讓學生碰程式碼。
3. **程式碼格預設收合**（cell metadata `"cellView": "form"` 或在 `#@title` 下），只露出標題和輸出。
4. **每段前一格 markdown 寫預測題，執行後一格寫「你看到了什麼」**；題目照投影片大綱的「停一下」。
5. **每段都能從該段第一格獨立重跑**（斷線、跑錯都能回到起點），不依賴上一段的變數。
6. **SKILL.md 和 scripts 用 `%%writefile /content/review-bot/...` 寫進檔案**，學生改完那一格再執行即可。
7. **`run_code` 工具必須受限執行**學生作業：禁止 `import os / sys / subprocess / shutil`、設 timeout、捕捉 stdout 與例外，回傳短字串。不可照抄舊教案的 `eval()`。
8. **2-C 的金鑰一律用假的**（例如 `FAKE_KEY_do_not_use_1234`），藏指令那本 Skill 的壞行要明顯但不要太容易一眼看到。
9. 套件版本釘死：`langgraph>=1.1,<2`、`langchain>=1.2,<2`、`langchain-google-genai>=4,<5`。用 `create_agent`（`from langchain.agents import create_agent`），不用已棄用的 `create_react_agent`；1-B 的「展開」用手組 `StateGraph(MessagesState) + ToolNode + tools_condition`（程式在 `docs/reuse-from-old-workshop.md`）。
10. 1-A 用 `stream_mode="values"` 印每一步的完整 State；1-B 用 `docs/reuse-from-old-workshop.md` 的 `pretty_trace`，輸出改中文。
11. 變數名用中文語境（`作業`、`小助教`、`ask_model`），不用 pandas 舊名。
12. 每本最後一格印出整份 State 歷程，方便學生截圖交作業；並提供「掛載 Google Drive 保存」與「下載 zip」兩格。

## 範例專案 review-bot 的檔案（notebook 跑完後在 `/content/review-bot/`）

```
review-bot/
├── graph.py                     # 1-A：workflow（check_syntax → give_feedback → check_format，分叉 explain_error，退回最多 3 次）
├── agent.py                     # 1-B：create_agent 版
├── tools/
│   ├── run_code.py              # 受限執行
│   ├── check_indent.py          # 縮排與行長（故意不碰命名，留給 2-B）
│   └── read_spec.py
├── skills/
│   ├── friendly-feedback/SKILL.md
│   ├── strict-review/SKILL.md
│   ├── detailed-feedback/        # 2-C 用：SKILL.md 藏指令 + scripts/setup.sh 有 curl | bash
│   └── naming-check/
│       ├── SKILL.md
│       └── scripts/check_naming.py
└── dual_core.py                 # 2-D：外層 workflow，give_feedback 節點裡包 agent + skill_loader
```

這些檔案的講師版原始碼放在本 repo 的 `review-bot/`，notebook 用 `%%writefile` 寫出同樣內容。

## 驗收

- 每本 notebook 在乾淨的 Colab 免費帳號上能從頭跑到尾（用 `jupyter nbconvert --execute` 在本機先驗一次，需要時 mock `google.colab`）。
- 學生的最低完成標準（見 `docs/syllabus.md`「講師準備的 Colab notebook」末尾）每一條都有對應的 cell 能做到。
- 2-B 的三個版本各跑三次，版本 A 結果真的會飄、B 和 C 三次一致。
- 2-D 用同一個 `thread_id` 中斷再跑，State 保留；換 `thread_id` 從空白開始。

## 工作方式

先讀 `docs/syllabus.md` 全文，再讀對應投影片大綱，再讀 `docs/reuse-from-old-workshop.md`，然後一本一本做，每做完一本就跑一次驗收。不要一次產生七本再驗。
