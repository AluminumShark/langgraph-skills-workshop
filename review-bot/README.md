# review-bot：作業小助教（講師版原始碼）

這個資料夾是範例專案「作業小助教」的原始碼。在 Colab 上執行 notebook 時，程式會把這些檔案寫到 `/content/review-bot/`，
**內容和這裡一模一樣**：`%%writefile` 格的內容就是直接從這裡讀出來產生的（見 `scripts/build_notebooks.py`）。

## 每個檔案是什麼、哪一本 notebook 會寫出它

| 檔案 | 是什麼 | 由哪本 notebook 寫出 |
| --- | --- | --- |
| `graph.py` | 1-A 的 workflow：`check_syntax → give_feedback → check_format`，語法錯分叉到 `explain_error`，格式不合格最多退回重寫 | 1-A（`%%writefile`）；2-D 也會用到 |
| `agent.py` | 1-B 的 agent：`create_agent` 一行版、手組 `StateGraph(MessagesState) + ToolNode + tools_condition` 的展開版、`pretty_trace` | 1-B（`%%writefile`） |
| `tools/run_code.py` | 在教學用限制下執行作業（不是完整安全沙箱）：禁 `import os/sys/subprocess/shutil`、子程序加 timeout、錯誤縮成一行 | 1-B（`%%writefile`）；1-0 等也會寫出 |
| `tools/check_indent.py` | 檢查縮排與每行長度（故意不碰命名，留給 2-B） | 1-B（`%%writefile`） |
| `tools/read_spec.py` | 讀題目要求（`spec.md`） | 1-B（`%%writefile`） |
| `tools/check_naming.py` | 把 Skill 的腳本 `check_naming.py` 包成 agent 的工具 | 2-B；2-D 也會用到 |
| `spec.md` | 題目要求；1-B 的表單改題目時會重寫它 | 1-B 等 |
| `我的作業.py` | 讓學生貼自己的作業；表單選「我的作業」時讀它 | 1-A、1-B（`%%writefile`，選用） |
| `skill_loader.py` | 只讀 SKILL.md 的「名片」（name、description），讓模型挑一本，再讀內文 | 2-A（`%%writefile`）；2-D 也會用到 |
| `skills/friendly-feedback/SKILL.md` | 手冊：溫和鼓勵 | 2-A（`%%writefile`） |
| `skills/strict-review/SKILL.md` | 手冊：嚴格審查 | 2-A（`%%writefile`） |
| `skills/naming-check/SKILL.md` | 手冊：命名檢查（放法 B：叫 AI 執行腳本） | 2-B（`%%writefile`） |
| `skills/naming-check/SKILL.version-a.md` | 命名檢查的放法 A（規則寫在手冊文字裡）；2-B 與版本 B 使用不同檔名，避免互相覆寫 | 2-B（`%%writefile`） |
| `skills/naming-check/scripts/check_naming.py` | 腳本：檢查變數與函式名稱是否為小寫加底線，相同輸入與腳本版本會得到相同結果 | 2-B（`%%writefile`） |
| `skills/detailed-feedback/SKILL.md` | 2-C 的實驗用手冊：中間藏了一行壞指令（金鑰一律用假的） | 2-C（`%%writefile`） |
| `skills/detailed-feedback/scripts/setup.sh` | 2-C 的實驗用腳本：含 `curl … \| bash` 與看不懂的編碼字串，**只給你讀、notebook 不會執行它** | 2-C（`%%writefile`） |
| `dual_core.py` | 2-D 的流程與 Agent 整合：外層 workflow 控制分支與順序，`give_feedback` 裡是帶著手冊與工具的小 agent；每份作業的題目放在 State.spec，read_spec 只讀本份題目；用 SQLite checkpointer 依 `thread_id` 存 State | 2-D（`%%writefile`） |

### 2-E（課後選做）：上雲端前的準備

| 檔案 | 是什麼 |
| --- | --- |
| `deploy/homework_mcp.py` | 練習 1：「作業倉庫」MCP server（`list_homework`、`get_homework`、`send_email`）。工具住在另一個程式裡：stdio 是本機插座，`--http <port>` 變成一個網址（Streamable HTTP，像遠端 MCP）。寄信是假的，只寫進 `寄件匣.txt`。1-B 第 6 段也會用它，但只把讀取工具交給 agent |
| `deploy/multi_agent.py` | 練習 2：整張分工圖跑一次：MCP 抓作業 → 程式檢查語法 → `Send` 開批改子 agent（手冊 ＋ `check_naming` 腳本 ＋ `run_code`）→ 驗證 agent（稽核員 ＋ 程式檢查行號）→ `interrupt()` 等人確認 → MCP 寄信 |
| `deploy/server.py` | 練習 3：用 FastAPI 把多 agent 小助教包成 API 服務（`GET /health`、`POST /batch`、`POST /batch/{thread_id}/decision`、`GET /threads/{thread_id}`） |
| `deploy/preflight.py` | 練習 4：上線前檢查（寫死的金鑰、第三方 Skill 掃描、run_code 圍欄、recursion_limit、checkpointer、寄信前的 interrupt、部署檔） |
| `deploy/app_graph.py` | 練習 4：`langgraph.json` 指向的進入點；模型來源、金鑰和 MCP server 的網址都從環境變數讀 |
| `langgraph.json` | 出貨單：給 `langgraph dev` / LangSmith Deployment 看的「graph 在哪裡」 |
| `requirements.txt`、`Dockerfile`、`.dockerignore` | 把程式、`skills/`、`scripts/` 裝進同一個容器；金鑰不進映像，由雲端的 Secret Manager 注入 |
| `.env.example` | 本機用的環境變數範本（複製成 `.env`，`.env` 不進 git） |

全部由 2-E 用 `%%writefile` 寫出；2-E 只產生檔案、在 Colab 裡練習，不會真的部署。

## 工作坊的基礎設施（學生不用看）

| 檔案 | 是什麼 |
| --- | --- |
| `llm.py` | 模型轉接頭：把 Colab 內建模型 `google.colab.ai`（預設，免 API key）或講師的 Gemini key 包成同一個 `model`。本課的 Colab 轉接器把工具說明寫進 prompt、請模型回 JSON，再轉成一樣格式的 `tool_calls` |
| `workshop.py` | notebook 共用的小工具：每段起點的 `準備()`、範例作業、保存實驗格指定的結果、畫流程圖、存到雲端硬碟、下載 zip |

這兩個檔案由每本 notebook 的第一格「0. 環境設定」寫出。

## 執行時才會出現的檔案（不在 repo 裡）

- `history.jsonl`：實驗格指定保存的結果，最後一格「📸 印出已記錄的實驗結果」讀它；不等於所有中間狀態
- `checkpoints.sqlite`：2-D 的存檔（未完成的 thread 可以接續；已完成的取回結果；新 ID 開始新執行）
- `.llm.json`：記住選了哪個模型來源（不存 API key）
- `寄件匣.txt`、`deploy/multi_agent.sqlite`、`deploy/.port`、`deploy/.mcp_port`：2-E 練習時產生（1-B 第 6 段只使用作業讀取工具）
