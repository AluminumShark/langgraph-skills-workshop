# 從 LangGraph 到 Skills：結構化與非結構化 Agent 的雙拼指南

> Agents in 2026: Mastering LangGraph & SKILL.md

這是 **NTU AI Club** 的技術工作坊教材，講者是 李維（Levi, [@AluminumShark](https://github.com/AluminumShark)）和柯宥圻。
課程對象是**剛學會 Python 的初學者**：只要看得懂 dict、函式、if、while 就跟得上。
你不用自己寫程式，全程都在 Google Colab 上執行講師準備好的 notebook，
只要做三件事：**按執行、改表單裡的文字或數字、先預測再對答案**。

我們會一起做一個「**作業小助教**」：輸入一段 Python 作業，輸出一份固定格式的回饋。
第 1 堂先弄懂 AI agent 是什麼，用 LangGraph 親眼看「路線由程式決定」和「路線由 AI 決定」的差別；
第 2 堂學 Agent Skills（給 AI 的工作手冊），最後把兩者接在一起，變成「雙核」的小助教。

| 堂次 | 日期 | 長度 | 主題 |
| --- | --- | --- | --- |
| 第 1 堂 | 2026-11-09（一） | 120 分鐘 | 什麼是 agent，用 LangGraph 做一個 |
| 第 2 堂 | 2026-11-16（一） | 120 分鐘 | Agent Skills：什麼該寫成手冊、什麼該寫成腳本，最後決定什麼放哪裡 |

## Notebook 一覽

點表格裡的 **Open in Colab** 就能直接在瀏覽器打開，不需要在電腦上安裝任何東西。

| 堂／段落時間 | Notebook | 你會學到什麼 | 你要改什麼 | 對應投影片 |
| --- | --- | --- | --- | --- |
| 第 1 堂 0:10 | **1-0 Tool calling**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/1-0_tool_calling.ipynb) | 模型只會「說」它想用哪個工具，真正做事的是你的程式 | 不用改，看模型回的工具呼叫紙條 | 第 1 堂 5–15 |
| 第 1 堂 0:28 | **1-A Workflow**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/1-A_workflow.ipynb) | 用 State、Node、Edge 畫出路線固定的流程 | 作業、最多重試次數、回饋字數上限 | 第 1 堂 16–26 |
| 第 1 堂 1:02 | **1-B Agent**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/1-B_agent.ipynb) | 給 AI 一個工具箱，看它自己決定先用哪個工具 | 作業、system prompt 裡的一句話 | 第 1 堂 28–37 |
| 第 2 堂 0:08 | **2-A Skills**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-A_skills.ipynb) | 程式不動、只換一本手冊（SKILL.md），AI 的行為就變了 | 兩份 SKILL.md 的規則與 description | 第 2 堂 5–12 |
| 第 2 堂 0:28 | **2-B 程式・文字・腳本**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-B_code_text_script.ipynb) | 同一個檢查放進手冊文字、腳本、流程節點，各跑三次比比看 | 不用改，執行三個版本並比對 | 第 2 堂 13–19 |
| 第 2 堂 0:58 | **2-C 資安**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-C_security.ipynb) | 別人寫的手冊可能藏著壞指令（prompt injection） | 不用改，找出藏指令的那一行 | 第 2 堂 21–23 |
| 第 2 堂 1:06 | **2-D 雙核**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-D_dual_core.ipynb) | 外面用流程鎖住順序，裡面讓 agent 帶著手冊判斷；State 存檔後能接著跑 | thread_id | 第 2 堂 24–27 |
| 課後選做 | **2-E 上雲端前的準備**<br>[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-E_deploy.ipynb) | 把小助教包成服務、平行批改、寄信前人工確認、上線前檢查 | 依各段說明 | 第 2 堂 47–54（補充）；部署地圖在 41 |

> 時間不夠時，必做的是 1-A、1-B、2-A；2-B 可以改成看講師示範；2-E 是課後自己玩的。

## 第一次用 Colab？照這幾步

1. **打開 notebook**：點上面表格的 **Open in Colab**。需要登入 Google 帳號（免費帳號就可以）。
2. **存一份自己的**：點左上角選單「**檔案 → 在雲端硬碟中儲存副本**」。之後都在你自己的副本上操作，改壞了也不怕，原本那份永遠在。
3. **執行「0. 環境設定」**：每本 notebook 的第一個程式格叫「0. 環境設定」，把滑鼠移過去，點左邊的 ▶ 執行。
   第一次會用 [uv](https://docs.astral.sh/uv/)（一個安裝 Python 套件很快的工具）安裝 LangGraph 等套件，大約半分鐘。
   看到「✅ 環境設定完成」和模型打的招呼，就代表成功了。
4. **每一段都照這個節奏**：
   - 🤔 **預測**：先讀程式格上面的預測題，把答案寫在紙上
   - ▶ **執行**：按下那一段的程式格
   - 👀 **對照**：讀下面的「你看到了什麼」，和你的預測比一比
5. **改表單欄位**：有些程式格右邊會出現表單，例如：

   ```
   作業：        [ 少了右括號   ▼ ]
   最多重試次數： ──●──────── 3
   ```

   你只要選下拉選單、拉滑桿或改文字，再按 ▶ 重新執行那一格就好，**不用碰程式碼**。
6. **程式碼是收起來的**：大部分格子只露出標題和輸出。想看程式的話點格子上的「顯示程式碼」，看不懂也沒關係，這堂課只要看輸出。
   有些格子會寫 `%%writefile`，那是「把這格的內容存成檔案」，例如手冊 SKILL.md，要你改的時候直接改文字、再執行那一格。
7. **最後三格：存檔與交作業**
   - 💾 存到 Google 雲端硬碟：把你改過的檔案和執行紀錄存一份
   - ⬇️ 下載 zip：直接下載到電腦
   - 📸 印出整份 State 歷程：把這本 notebook 跑過的每一步印出來，**截圖就能交作業**

## 模型從哪裡來？

- **預設：Colab 內建模型（`google.colab.ai`）**。免費帳號就能用，**不需要 API key**，但有用量上限。
- **備案：講師提供的 Gemini API key**。如果內建模型的額度用完，或課堂上講師說要換：
  1. 點 Colab 左邊的 🔑「**密鑰**」，新增一個名稱為 `GOOGLE_API_KEY` 的密鑰，值貼上講師給的 key，並打開「notebook 存取權」
  2. 在「0. 環境設定」的表單把 **模型來源** 改成 `gemini`，重新執行那一格

> ⚠️ 表單裡也有一個可以直接貼 key 的欄位，但**貼了 key 的 notebook 千萬不要分享給別人**（key 會跟著 notebook 一起被看到）。能用 🔑 密鑰就用密鑰。

## 常見問題

**Colab 斷線了、或某一格跑出錯誤怎麼辦？**
從那一段的**第一格**重新執行就好，每一段都能自己重來，不用從頭跑整本。
如果出現「⚠️ 找不到環境：請先執行最上面的「0. 環境設定」那一格」，代表 Colab 把環境清掉了，先重跑「0. 環境設定」，再回到那一段。

**出現額度用完、或模型一直沒有回應？**
Colab 內建模型有免費用量上限。可以等一下再試、兩個人共用一本 notebook，或照上面「模型從哪裡來」改用講師的 Gemini key。

**同一格跑兩次，結果不一樣，是我弄壞了嗎？**
沒有，這是正常的。AI 每次都會重新想一遍，回饋的文字、用工具的順序都可能不同，這正是 agent 的天性，也是這堂課要討論的重點：哪些事該用程式鎖住、哪些事可以放手讓 AI 判斷。

**為什麼 `run_code` 會擋下 `import os`？**
`run_code` 是真的會執行作業的工具，而作業裡什麼都可能有（刪檔、無限迴圈）。所以它有圍欄：不准 `import os` 這類危險模組、超過 3 秒就強制停止、錯誤只回一行。這是故意的，1-B 和 2-C 會講為什麼。

**我改了 SKILL.md，可是 AI 的回饋沒有變？**
改完記得**執行那一格**（`%%writefile` 那格），檔案才會真的存進去；然後再執行下面使用它的那一格。

**我看不到表單，只看到一堆程式碼？**
可能是用 GitHub 或 Jupyter 直接打開的。請用表格裡的 **Open in Colab** 打開，表單和收合只有在 Colab 裡才會出現。

## 簡報

| 檔案 | 內容 |
| --- | --- |
| [`slides/session1.html`](slides/session1.html) | 第 1 堂：什麼是 agent，用 LangGraph 做一個 |
| [`slides/session2.html`](slides/session2.html) | 第 2 堂：Agent Skills，什麼該寫成說明書、什麼該寫成腳本（最後附「上雲端」補充） |

下載後用瀏覽器打開即可（單一 HTML 檔，不用安裝）：**← →** 換頁、**N** 看講者備註、**F** 全螢幕、**Ctrl／⌘＋P** 匯出 PDF。
每本 notebook 的每一段都會標出「📍 對應簡報：投影片 N」，上課時可以對照。

## 專案結構

```
langgraph-skills-workshop/
├── notebooks/                  # 八本 Colab notebook（由 scripts/ 產生）
├── slides/                     # 兩堂課的 HTML 簡報
├── docs/                       # 課綱、投影片逐張大綱、舊教案可沿用的素材、原始提案
├── review-bot/                 # 範例專案「作業小助教」的講師版原始碼
│   ├── graph.py                #   1-A：workflow（State、Node、Edge）
│   ├── agent.py                #   1-B：create_agent 版的 agent
│   ├── skill_loader.py         #   2-A：看手冊的名片、挑一本
│   ├── dual_core.py            #   2-D：外層 workflow ＋ 裡面的 agent ＋ Skill
│   ├── tools/                  #   工具：run_code、check_indent、read_spec、check_naming
│   ├── skills/                 #   手冊：friendly-feedback、strict-review、naming-check、detailed-feedback
│   ├── deploy/                 #   2-E：API 服務、平行批改、寄信前確認、上線前檢查
│   ├── langgraph.json、Dockerfile、requirements.txt  # 2-E：上雲端用的部署檔（只產生、不部署）
│   ├── llm.py                  #   工作坊用：把 Colab 內建模型或 Gemini 包成同一個 model
│   └── workshop.py             #   工作坊用：notebook 共用的小工具（存紀錄、畫流程圖、存檔）
├── scripts/
│   ├── nbspec/                 # 每本 notebook 的內容定義（要改 notebook 就改這裡）
│   ├── build_notebooks.py      # 從 nbspec/ ＋ review-bot/ 產生 notebooks/*.ipynb
│   └── verify_notebooks.py     # 在本機把每本 notebook 從頭跑到尾
├── tests/mock_colab/           # 本機驗證用的假 google.colab 和假模型
├── reference/old-workshop/     # 上一版教案，只供參考
├── pyproject.toml / uv.lock    # 本機環境（uv 管理）
└── CLAUDE.md                   # 給 AI 協作工具看的專案說明與實作規範
```

**`/content/review-bot/` 是什麼？** 在 Colab 上執行 notebook 時，程式會把作業小助教的檔案寫到 Colab 雲端電腦的 `/content/review-bot/` 資料夾（左邊 📁 檔案面板看得到）。
它的內容和這個 repo 的 `review-bot/` 一模一樣。Colab 斷線後這個資料夾會消失，想保留就用最後的「存到雲端硬碟」或「下載 zip」。

## 給講師／想改教材的人

本機環境用 [uv](https://docs.astral.sh/uv/) 管理（Python 3.12，和 Colab 相同）。先安裝相依套件：

```bash
uv sync
```

**notebook 是產生出來的，請不要直接改 `.ipynb`。** 內容來自兩個地方：每本的格子定義在 `scripts/nbspec/*.py`，`%%writefile` 格的內容直接讀 `review-bot/` 的原始碼（所以 notebook 寫出的檔案和 repo 裡的保證一樣）。改完重新產生：

```bash
uv run python scripts/build_notebooks.py
```

只想產生其中幾本，在後面加上名稱開頭（例如 `1-A 2-B`）。

在本機把每本 notebook 從頭跑到尾，確認每一格都跑得過：

```bash
uv run python scripts/verify_notebooks.py
```

這個驗證不需要 Colab，也不需要 API key：它用 `tests/mock_colab/` 裡的**假 `google.colab`** 和**假模型**（照固定規則加一點亂數回話），並把 `/content/` 換成暫存資料夾。
所以它檢查的是「流程和程式接得起來」，**不代表真實模型的回答品質**；要看真實效果，請在 Colab 上實際跑一次。
執行後的結果會存成 `notebooks/*.executed.ipynb`（不會進 git），可以打開看每一格的輸出。

## 參考資料

- 完整課綱（時間表、觀念清單、notebook 規格、最低完成標準）：[`docs/syllabus.md`](docs/syllabus.md)
- 投影片逐張大綱：[`docs/slides-session1-outline.md`](docs/slides-session1-outline.md)、[`docs/slides-session2-outline.md`](docs/slides-session2-outline.md)
- 引用的文章與研究：兩份簡報最後的「參考來源」頁
