# review-bot：作業小助教（講師版原始碼）

這個資料夾是範例專案「作業小助教」的原始碼。在 Colab 上執行 notebook 時，程式會把這些檔案寫到 `/content/review-bot/`，
**內容和這裡一模一樣**：`%%writefile` 格的內容就是直接從這裡讀出來產生的（見 `scripts/build_notebooks.py`）。

## 每個檔案是什麼、哪一本 notebook 會寫出它

| 檔案 | 是什麼 | 由哪本 notebook 寫出 |
| --- | --- | --- |
| `graph.py` | 1-A 的 workflow：`check_syntax → give_feedback → check_format`，語法錯分叉到 `explain_error`，格式不合格最多退回重寫 | 1-A（`%%writefile`）；2-D 也會用到 |
| `agent.py` | 1-B 的 agent：`create_agent` 一行版、手組 `StateGraph(MessagesState) + ToolNode + tools_condition` 的展開版、`pretty_trace` | 1-B（`%%writefile`） |
| `tools/run_code.py` | 在籠子裡執行作業：禁 `import os/sys/subprocess/shutil`、子程序加 timeout、錯誤縮成一行 | 1-B（`%%writefile`）；1-0 等也會寫出 |
| `tools/check_indent.py` | 檢查縮排與每行長度（故意不碰命名，留給 2-B） | 1-B（`%%writefile`） |
| `tools/read_spec.py` | 讀題目要求（`spec.md`） | 1-B（`%%writefile`） |
| `tools/check_naming.py` | 把 Skill 的腳本 `check_naming.py` 包成 agent 的工具 | 2-B；2-D 也會用到 |
| `spec.md` | 題目要求；1-B 的表單改題目時會重寫它 | 1-B 等 |
| `我的作業.py` | 讓學生貼自己的作業；表單選「我的作業」時讀它 | 1-A、1-B（`%%writefile`，選用） |
| `skill_loader.py` | 只讀 SKILL.md 的「名片」（name、description），讓模型挑一本，再讀內文 | 2-A（`%%writefile`）；2-D 也會用到 |
| `skills/friendly-feedback/SKILL.md` | 手冊：溫和鼓勵 | 2-A（`%%writefile`） |
| `skills/strict-review/SKILL.md` | 手冊：嚴格審查 | 2-A（`%%writefile`） |
| `skills/naming-check/SKILL.md` | 手冊：命名檢查（放法 B：叫 AI 執行腳本） | 2-B（`%%writefile`） |
| `skills/naming-check/SKILL.version-a.md` | 命名檢查的放法 A（規則寫在手冊文字裡）；2-B 會把它寫成 `SKILL.md` 來比較 | 2-B（`%%writefile`） |
| `skills/naming-check/scripts/check_naming.py` | 腳本：檢查變數與函式名稱是否為小寫加底線，每次結果一樣 | 2-B（`%%writefile`） |
| `skills/detailed-feedback/SKILL.md` | 2-C 的實驗用手冊：中間藏了一行壞指令（金鑰一律用假的） | 2-C（`%%writefile`） |
| `skills/detailed-feedback/scripts/setup.sh` | 2-C 的實驗用腳本：含 `curl … \| bash` 與看不懂的編碼字串，**只給你讀、notebook 不會執行它** | 2-C（`%%writefile`） |
| `dual_core.py` | 2-D 的雙核：外層 workflow 鎖順序，`give_feedback` 裡是帶著手冊與工具的小 agent；用 SQLite checkpointer 依 `thread_id` 存 State | 2-D（`%%writefile`） |

### 2-E（課後選做）：上雲端前的準備

| 檔案 | 是什麼 |
| --- | --- |
| `deploy/server.py` | 練習 1：用 FastAPI 把雙核小助教包成 API 服務（`/health`、`POST /review`、`/threads/{thread_id}`） |
| `deploy/batch.py` | 練習 2：用 `Send` 平行批改（map-reduce），並和「一張桌子批全部」比 token |
| `deploy/email_flow.py` | 練習 3：寄信前用 `interrupt()` 停下來等人確認，`Command(resume=...)` 接著跑；寄信是假的，只寫進 `寄件匣.txt` |
| `deploy/preflight.py` | 練習 4：上線前檢查（寫死的金鑰、第三方 Skill 掃描、run_code 圍欄、recursion_limit、checkpointer、interrupt、部署檔） |
| `deploy/app_graph.py` | `langgraph.json` 指向的進入點：模型來源與金鑰都從環境變數讀 |
| `langgraph.json` | 出貨單：給 `langgraph dev` / LangSmith Deployment 看的「graph 在哪裡」 |
| `requirements.txt`、`Dockerfile`、`.dockerignore` | 把程式、`skills/`、`scripts/` 裝進同一個容器；金鑰不進映像，由雲端的 Secret Manager 注入 |
| `.env.example` | 本機用的環境變數範本（複製成 `.env`，`.env` 不進 git） |

全部由 2-E 用 `%%writefile` 寫出；2-E 只產生檔案、在 Colab 裡練習，不會真的部署。

## 工作坊的基礎設施（學生不用看）

| 檔案 | 是什麼 |
| --- | --- |
| `llm.py` | 模型轉接頭：把 Colab 內建模型 `google.colab.ai`（預設，免 API key）或講師的 Gemini key 包成同一個 `model`。內建模型沒有原生 tool calling，所以它把工具說明寫進 prompt、請模型回 JSON，再轉成一樣格式的 `tool_calls` |
| `workshop.py` | notebook 共用的小工具：每段起點的 `準備()`、範例作業、記錄 State 歷程、畫流程圖、存到雲端硬碟、下載 zip |

這兩個檔案由每本 notebook 的第一格「0. 環境設定」寫出。

## 執行時才會出現的檔案（不在 repo 裡）

- `history.jsonl`：每次執行的 State 紀錄，最後一格「📸 印出整份 State 歷程」讀它
- `checkpoints.sqlite`：2-D 的存檔（同一個 `thread_id` 可以接著跑）
- `.llm.json`：記住選了哪個模型來源（不存 API key）
- `寄件匣.txt`、`deploy/email_checkpoints.sqlite`、`deploy/.port`：2-E 練習時產生
