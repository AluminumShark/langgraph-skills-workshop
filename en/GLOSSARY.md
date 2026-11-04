# English edition: translation glossary and conventions

This file is the single source of truth for the English edition under `en/`.
Every translated file must use the names and strings below **exactly**, because they cross file
boundaries (review-bot modules ↔ notebook cells ↔ tests ↔ fake model ↔ slides ↔ docs).

## 1. Layout

`en/` mirrors the repo root. Paths inside `en/` are the same as the originals, with one rename:

| Original | English edition |
| --- | --- |
| `README.md`, `CLAUDE.md` | `en/README.md`, `en/CLAUDE.md` |
| `docs/*` | `en/docs/*` (same file names) |
| `slides/session1.html`, `slides/session2.html` | `en/slides/session1.html`, `en/slides/session2.html` |
| `scripts/*.py`, `scripts/nbspec/nb_*.py` | `en/scripts/*.py`, `en/scripts/nbspec/nb_*.py` (same file names) |
| `notebooks/*.ipynb` | `en/notebooks/*.ipynb` (**generated** by `uv run python en/scripts/build_notebooks.py`, never hand-written) |
| `review-bot/**` | `en/review-bot/**` |
| `review-bot/我的作業.py` | `en/review-bot/my_homework.py` |
| `tests/**` | `en/tests/**` |
| `reference/old-workshop/**` | `en/reference/old-workshop/**` |

- `en/scripts/*.py` resolve the repo root as `Path(__file__).resolve().parents[1]`, which is `en/`, so they read `en/review-bot`, write `en/notebooks`, and so on.
- `pyproject.toml` and `uv.lock` are shared; run everything from the repo root with `uv run python en/...`.
- Colab links point to `https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/en/notebooks/<name>.ipynb`. Any GitHub or raw URL that points into this repo's `notebooks/`, `review-bot/`, `slides/`, or `docs/` must point to the `en/` path.
- The Colab runtime path stays `/content/review-bot` (not `/content/en/review-bot`).
- Runtime files: `寄件匣.txt` → `outbox.txt`, `作業.py` → `homework.py`. Unchanged: `history.jsonl`, `checkpoints.sqlite`, `.llm.json`, `2B_results.json`, `mcp_server.log`, `.port`, `.mcp_port`.
- **No CJK characters may remain in `en/`** except in this glossary. If you think one must stay, report it.

## 2. Writing style

- The audience is beginners who have just learned Python. Use plain, short sentences, and say "you".
- Keep the structure intact: headings, tables, lists, emoji, `<details>`, HTML classes and ids, `#@title`, `#@param`, `#@markdown`, code-cell order, and comment density.
- Translate the meaning, not word by word. Keep the original teaching distinctions exactly (see CLAUDE.md "教學規範").
- Use Colab's English UI labels: "Runtime", "Secrets" (🔑 key icon in the left sidebar), "File → Save a copy in Drive", "Disconnect and delete runtime".
- Numbers, times, slide numbers, and notebook names (1-0, 1-A, … 2-E) stay the same.
- Chinese full-width punctuation becomes ASCII punctuation. Chinese quotation marks 「」 become "double quotes" in prose; in code strings, pick whichever quoting keeps the code valid.

## 3. Terms

| 中文 | English |
| --- | --- |
| 作業小助教 / 小助教 | the Homework Helper / the helper |
| 手冊 (a Skill) | handbook (in "Skill handbook"; the folder and file are still `skills/<name>/SKILL.md`) |
| 名片 (SKILL.md name + description) | card |
| 內文 (SKILL.md body) | body |
| 附件 / 附錄 | attachment / appendix |
| 訂單紙 (State metaphor) | order slip |
| 手搖飲店 | bubble-tea shop |
| 工作站 / 站 | workstation / station |
| 零件 | component |
| 插座 (MCP metaphor) | socket |
| 出貨單 (langgraph.json) | packing slip |
| 便利貼 | sticky note |
| 學習單 | worksheet |
| 分工圖 | division-of-labor diagram |
| 回饋 | feedback |
| 批改 | review (verb and noun); 批改需求 → review request |
| 批改員 / 稽核員 | reviewer / auditor |
| 題目 / 題目要求 | assignment / assignment requirements (`spec`) |
| 流程 / 流程控制 / AI 判斷 | workflow (or "flow") / flow control / AI judgment |
| 流程與 Agent 整合 (雙核) | combining workflow and agent (dual-core) |
| 放法 A／B／C | placement A / B / C |
| 實驗 | experiment |
| 預測 / 對照 / 觀察 | predict / compare / observe |
| 前置條件 | prerequisites |
| 準備格 | setup cell |
| 第 1 段 (notebook part) | Part 1 |
| 第 1 堂 / 第 2 堂 | Session 1 / Session 2 |
| 第一站…第四站 (slides) | Stop 1 … Stop 4 |
| 投影片 17 | slide 17 |
| 課堂必做 / 課後選做 / 選讀 / 補充 | in class (required) / optional after class / optional reading / supplementary |
| 中場休息 | break |
| 語法正確 ≠ 執行成功 ≠ 答案正確 | valid syntax ≠ runs successfully ≠ meets the assignment |
| 最多生成次數（含第一次） | maximum generations (including the first) |
| 最多重試次數 (legacy API field) | `max_retries` (legacy name; it actually counts generations including the first) |
| 回饋字數上限 | feedback character limit |
| 達到上限、未通過 | reached the limit, not passed |
| 執行階段 | runtime |
| 雲端硬碟 | Google Drive |
| 金鑰 / 假金鑰 | key / fake key |
| 歷程 | history (the recorded results) |
| 工具原始結果 / AI 最終回覆 / 解析器擷取值 | raw tool result / AI's final reply / parser-extracted value |

Slide chapter tracks (`data-track`): 開場 → Opening; 模型與工具 → Models & Tools; Workflow → Workflow; Agent → Agent;
流程與判斷 → Flow & Judgment; 附錄選讀 → Optional Appendix; Skill 工作手冊 → Skill Handbooks;
程式・文字・腳本 → Code · Text · Scripts; 資安與整合 → Security & Integration; 系統設計 → System Design; 補充 → Supplementary.
Defaults in `sync_slide_navigation.py`: 觀念與實驗 → Concepts & Experiments, 流程與實作 → Flow & Practice,
整合與實作 → Integration & Practice, 系統設計 → System Design, 開場 → Opening, 補充 → Supplementary.
Navigation labels: `第 N 頁：T` → `Slide N: T`; `跳到第 N 頁：T` → `Go to slide N: T`; `投影片 N` → `Slide N`.

## 4. Slide titles (`data-title`) — use verbatim in slides, outlines, notebooks, and docs

Session 1:

| id | English title |
| --- | --- |
| s1-001 | From LangGraph to Skills |
| s1-004 | Same AI, two outcomes |
| s1-005 | What we'll build: the Homework Helper |
| s1-002 | Today's route |
| s1-006 | Stop 1: How AI gets things done |
| s1-007 | An LLM is a "continuation machine" |
| s1-008 | LLMs have no memory: your program supplies the conversation |
| s1-009 | Tokens and the context window |
| s1-011 | Prompts and system prompts |
| s1-012 | Models can't act, so how does an agent "do" things? |
| s1-013 | Tool calling: the model only "says" which tool it wants |
| s1-014 | Predict first: will the model ask to use a tool? |
| s1-new-tool-result | Read the tool request, then call the model again |
| s1-015 | Agent = model + tools + loop |
| s1-016 | Workflow vs. agent: who decides the next step |
| s1-017 | Stop 2: Workflow 1-A |
| s1-018 | LangGraph: connecting functions with arrows |
| s1-019 | The Homework Helper's flow: four workstations |
| s1-003 | Tell them apart: valid syntax, runs, correct answer |
| s1-020 | Component 1: State, the order slip that travels along |
| s1-021 | Component 2: Node, one workstation |
| s1-023 | Component 3: Edge, the arrows between workstations |
| s1-024 | One table for the three components |
| s1-025 | No AI yet: three homework samples, guess then run |
| s1-026 | Data flow: watch the order slip fill in |
| s1-027 | Putting AI into one node |
| s1-new-format-stop | The flow ended. Did the feedback pass? |
| s1-028 | Back to the helper's flow: all three design patterns |
| s1-029 | 10-minute break |
| s1-030 | Stop 3: Agent 1-B |
| s1-031 | A different approach: no flow diagram, just a toolbox |
| s1-032 | Try the tools first, then hand them to the agent |
| s1-034 | What a tool interface tells the model |
| s1-033 | An agent in one line: create_agent |
| s1-037 | Reading an agent's execution trace |
| s1-038 | Same homework, three runs: same order? |
| s1-039 | If a tool keeps failing, will the agent stop? |
| s1-new-recursion-limit | Set a limit, then work out why it stopped |
| s1-035 | Where tools come from: your own functions vs. MCP sockets |
| s1-040 | Stop 4: Flow control and AI judgment |
| s1-041 | The math of ten checkpoints |
| s1-042 | Combining workflow and agent: an agent inside a node |
| s1-043 | Worksheet: flow control or AI judgment? |
| s1-044 | Three takeaways and homework |
| s1-010 | Optional appendix: usage fields in the returned object |
| s1-022 | Optional appendix: how messages in State are merged |
| s1-036 | Optional appendix: the core model-and-tool loop |
| s1-045 | References |

Session 2:

| id | English title |
| --- | --- |
| s2-001 | Title |
| s2-002 | Today's route |
| s2-003 | Three things you learned last week |
| s2-004 | Sticky note: a real request |
| s2-005 | Stop 1: Skill handbooks |
| s2-006 | Last week's leftover problem: feedback style hard-coded |
| s2-007 | What do you give a new colleague on day one? |
| s2-008 | What a handbook looks like |
| s2-009 | Pick a handbook by its card, then read the body |
| s2-new-skill-choice | Experiment A: change only the request, see which handbook is picked |
| s2-011 | Experiment B: keep the handbook, add one rule |
| s2-012 | Handbook attachments: scripts and reference material |
| s2-013 | Stop 2: Code · Text · Scripts |
| s2-014 | One naming check, three placements |
| s2-015 | Placement A: the model judges from the handbook text |
| s2-016 | Placement B: the model picks a tool, a script checks |
| s2-017 | Placement C: the workflow always runs the same check |
| s2-018 | Two questions, decided separately |
| s2-019 | Pause: five tasks, two questions each |
| s2-020 | 10-minute break |
| s2-021 | Stop 3: Security and integration |
| s2-022 | Can you use someone else's handbook as is? Observe first |
| s2-new-permissions | Same handbook, only the available tools change |
| s2-023 | Three habits before using an external Skill |
| s2-024 | Combining workflow and agent: wiring handbooks and tools |
| s2-025 | Where workflow meets agent: load the handbook, provide the tools |
| s2-new-checkpoint | Pause once, then resume with the same ID |
| s2-new-checkpoint-compare | Then compare: a finished ID vs. a new ID |
| s2-028 | Stop 4: What goes where |
| s2-030 | Back to the sticky note: does every step need an agent? |
| s2-031 | Feature 1: fetching homework from GitHub |
| s2-032 | Syntax, tone, and the assignment: separate responsibilities |
| s2-035 | Pause: which checks must run on every submission? |
| s2-036 | Reviewing 200 submissions: independent first, then parallel |
| s2-037 | Verifying feedback: rules first, then independent judgment |
| s2-039 | Before sending email, make the flow wait for confirmation |
| s2-040 | The Homework Helper's full division of labor |
| s2-042 | Six questions to ask, in order, when designing |
| s2-043 | 8 minutes: your turn to design |
| s2-044 | Wrapping up both sessions |
| s2-046 | After class: optional reading by need |
| s2-010 | Optional after class: swap the cards, see if the pick changes |
| s2-026 | Optional: checking a pure agent with code |
| s2-027 | Optional: a fixed test set, before vs. after a change |
| s2-034 | Optional reading: when data grows, retrieve before answering (RAG) |
| s2-045 | Optional reading: from demo to maintainable |
| s2-047 | Supplementary: moving to the cloud |
| s2-041 | The division of labor in the cloud: where each box lives |
| s2-048 | Leaving Colab: three things to replace |
| s2-049 | Packaging: langgraph.json is the packing slip |
| s2-050 | Optional reading: choose a deployment by operational needs |
| s2-051 | Moving each role to the cloud |
| s2-052 | Reviewing 200 at once: Send |
| s2-053 | Waiting for confirmation before sending: interrupt |
| s2-054 | After launch: observable and containable |
| s2-055 | References and further resources |
| s2-056 | References (cont.): supplementary and cloud |

## 5. Data values shared across files

Sample homework keys (`sample_homework` in `workshop.py`, form dropdowns in notebooks):

| 中文 | English (exact string) |
| --- | --- |
| 少了右括號 | `Missing parenthesis` |
| 正確的程式 | `Correct program` |
| 空白 | `Empty` |
| 變數打錯字 | `Variable typo` |
| 縮排亂掉 | `Messy indentation` |
| 命名不一致 | `Inconsistent naming` |
| 我的作業 | `My homework` (`load_homework` checks `name.startswith("My homework")` and reads `my_homework.py`) |

`sample_specs` in `dual_core.py` uses the same English keys.

Review requests (2-A, 2-D dropdowns; slides quote them verbatim): 幫第一次交作業的初學者看看 → `Take a look for a beginner handing in homework for the first time`; 期中考正式評分，請嚴格審查 → `Midterm exam, official grading: please review strictly`.

Student names (`homework_mcp.py`, fake model, notebooks, slides): 小明 → Alex, 小華 → Ben, 小美 → Chloe, 阿傑 → Jay, 小芳 → Fiona.

History rows written by `record()`: keys 時間/標題/內容 → `time`/`title`/`content`.

Auditor JSON (2-E): `{"通過": …, "原因": …}` → `{"passed": true|false, "reason": "one sentence"}`.

**Character limits are tripled** in the English edition because English needs about three times as many characters as Chinese for the same feedback.
`len()` still counts characters. Examples: graph default 150 → 450; 1-A slider `150, min 20, max 300, step 10` → `450, min 60, max 900, step 30`; "try 30" → "try 90"; dual_core and 2-D default 250 → 750; multi_agent "at most 250 characters" → 750; tests scale the same way.
A limit of `1` (the "can never fit" demo) stays `1`. Code-line limits (`max_line_length`) and `run_code` output limits stay the same.

1-0 memory demo strings: "我叫 Alice" → `My name is Alice`; "你好 Alice!" → `Hi Alice!`; "我叫什麼?" → `What is my name?`; "用三個字回答:Python 是什麼?" → `Answer in three words: what is Python?`.
`setup()` greeting prompt: `Say hello in one sentence to a classmate who just learned Python`.

## 6. Protocol strings (matched by code in other files)

| Where produced → where matched | 中文 | English (exact) |
| --- | --- | --- |
| `llm.py` prompt blocks → fake model | `【系統指示】` `【使用者】` `【AI】` `【工具 X 的結果】` `【你可以用的工具】` `【回覆規則】` | `=== System instructions ===` `=== User ===` `=== AI ===` `=== Result of tool X ===` `=== Tools you can use ===` `=== Reply rules ===` (each header alone on its own line) |
| `llm.py` tool list line → fake model | `- name(params)：說明` | `- name(params): description` |
| feedback markers (graph, dual_core, agent, skills, fake, tests) | `優點：` / `改進：` | `Strengths:` / `Improvements:` (check_format also accepts them without a following space; `優點：無` → `Strengths: none`) |
| syntax-error feedback | `語法：{error}` | `Syntax: {error}` |
| length rule in feedback prompts → fake model | `不超過 N 個字元` / `不超過 N 字` | `at most N characters` |
| retry hint → fake model | `被退回` | `was rejected` (e.g. `Your previous feedback was rejected because: …. Fix it and rewrite.`) |
| `skill_loader.py` pick prompt → fake model | `只回答手冊的 name` / `批改需求：` / card line `- name：description` | `Answer with only the handbook's name` / `Review request: ` / `- name: description` |
| `SKILL.version-a.md` text-only naming prompt → fake model | `列出不符合的` | `list every name that breaks the rule` |
| naming script / `check_naming` tool output | `第 3 行：myVar 不符合規則（建議 my_var）` / `OK：所有變數與函式名稱都是小寫加底線` | `Line 3: myVar breaks the rule (suggest my_var)` / `OK: all variable and function names are lowercase with underscores` |
| text-only naming OK answer (version A) | `OK：所有名稱符合本課規則` | `OK: all names follow this course's rules` |
| `check_indent` output | `第 2 行：縮排 2 格，建議用 4 的倍數` / `OK：縮排與行長都沒問題` | `Line 2: indented 2 spaces; use a multiple of 4` / `OK: indentation and line length look fine` |
| `get_homework` not found → fake model | `找不到「{student}」的作業` | `No homework found for "{student}"` (fake checks `startswith("No homework found")`) |
| auditor detection → fake model | system prompt contains `稽核員` | system prompt contains `auditor` |
| fake model keyword → tool | 題目要求 / 命名 / 語法 / 金鑰 | `assignment requirements` / `naming` / `syntax` / `key` (match on the system prompt, case-insensitive) |

## 7. Identifier map

Python allows Chinese identifiers; the English edition uses only ASCII identifiers. Rules:

1. Every identifier below must be translated exactly as listed, wherever it appears (module code, notebook cells, tests, slides, docs).
2. Identifiers that are not listed are local to one file: translate them to idiomatic `snake_case` (`PascalCase` for classes, `UPPER_CASE` for module constants).
3. If you create a new name that another file must also use, report it in your final summary.

### workshop.py (`__all__` and helpers)

`準備`→`prepare` · `範例作業`→`sample_homework` · `取得作業`→`load_homework` · `記下`→`record` · `印出狀態`→`print_state` · `印出訂單紙`→`print_order_slip` · `印出歷程`→`print_history` · `清除歷程`→`clear_history` · `模型呼叫計數器` (class)→`ModelCallCounter` · `顯示流程圖`→`show_graph` · `存到雲端硬碟`→`save_to_drive` · `下載壓縮檔`→`download_zip` · `估算_token`→`estimate_tokens` · `歷程檔`→`HISTORY_FILE` · `_可存的`→`_serializable` · `_短`→`_short` · `_讓_mcp_stdio_能在notebook用`→`_make_mcp_stdio_work_in_notebook` · params: `標題`→`title`, `內容`→`content`, `縮排`→`indent`, `第幾步`→`step_no`, `上一步`→`prev_state`, `不印`→`skip_keys`, `新寫入`→`changed_keys`, `說明`→`note`, `目的地`→`destination`, `名稱`→`name`, `次數`→`count`

### llm.py

`存設定`→`save_settings` · `讀設定`→`load_settings` · `設定檔`→`SETTINGS_FILE` · `預設_gemini_模型`→`DEFAULT_GEMINI_MODEL` · `_工具說明`→`_describe_tools` · `_訊息轉文字`→`_messages_to_text` · `_解析回覆`→`_parse_reply` · `_找_api_key`→`_find_api_key`
(`estimate_tokens` lives here too. Adapt its heuristic to English text, roughly 4 characters per token, and keep the docstring honest that it is an estimate.)

### graph.py

`建立小助教`→`build_helper` · `空白訂單紙`→`blank_order_slip` · `建立_check_format`→`make_check_format` · `建立_give_feedback`→`make_give_feedback` · `建立_route_after_format`→`make_route_after_format` · `最多重試次數`→`max_retries` · `回饋字數上限`→`feedback_char_limit` · `_錯誤翻譯`→`_ERROR_TRANSLATIONS` · `翻譯語法錯誤`→`translate_syntax_error` · `說法`→`wording` · `give_feedback_固定文字`→`give_feedback_fixed_text` · `問題`→`problems`
(State keys are already English: `code, syntax_ok, error, feedback, format_ok, format_problem, retries`; keep them.)

### agent.py

`建立_agent`→`make_agent` · `建立_展開版_agent`→`make_expanded_agent` · `基本_system_prompt`→`base_system_prompt` · `小助教的工具`→`helper_tools` · `作業訊息`→`homework_message` · `工具順序`→`tool_sequence` · `最後回覆`→`final_reply` · `作業`→`homework`

### skill_loader.py

`列出名片`→`list_cards` · `讀名片`→`read_card` · `讀內文`→`read_body` · `挑手冊`→`pick_handbook` · `需求`→`request` · `清單`→`card_list` · `選項`→`options` · `回答`→`answer` · `只要`→`only`

### dual_core.py

`存檔位置`→`CHECKPOINT_PATH` · `可選的手冊`→`AVAILABLE_HANDBOOKS` · `範例題目`→`sample_specs` · `整合State`→`IntegratedState` · `雙核State`→`DualCoreState` · `建立整合小助教`→`build_integrated_helper` · `建立雙核小助教`→`build_dual_core_helper` · `建立_read_spec`→`make_read_spec` · `建立_skill_loader`→`make_skill_loader` · `開存檔`→`open_checkpointer` · `逐站執行`→`run_station_by_station` · `作業輸入`→`homework_input` · `作業名稱`→`homework_name` · `題目要求`→`spec_text` · `批改需求`→`review_request` · `小agent`→`inner_agent` · `站`→`station` · `輸入`→`inputs` · `寫入`→`writes`
(State keys `code, spec, request, skill_name, skill, tools_used` are already English; keep them.)

### tools/

`允許的模組`→`ALLOWED_MODULES` · `禁止的模組`→`BLOCKED_MODULES` · `禁止的函式`→`BLOCKED_FUNCTIONS` · `禁止的屬性`→`BLOCKED_ATTRIBUTES` · `最長時間`→`TIME_LIMIT` · `最長時間_秒`→`time_limit_seconds` · `最長輸出_字`→`MAX_OUTPUT_CHARS` · `_先檢查`→`_precheck` · `擋下`→`blocked` · `執行作業`→`run_homework` · `開頭空白`→`leading_spaces` · `行長上限`→`MAX_LINE_LENGTH` · `檢查縮排`→`check_indentation` · `題目檔`→`SPEC_FILE` · `讀題目`→`read_spec_text` · `腳本`→`SCRIPT` · `執行命名腳本`→`run_naming_script` · `印出`→`output`
Tool names exposed to the model stay as they are: `run_code`, `check_indent`, `read_spec`, `check_naming`, `check_syntax`, `read_env`, `list_homework`, `get_homework`, `send_email`, `always_fail`.

### skills/naming-check/scripts/check_naming.py

`規則`→`RULE` · `建議名稱`→`suggest_name` · `找出所有名稱`→`find_all_names` · `檢查命名`→`check_names`

### deploy/

`建立多agent小助教`→`build_multi_agent_helper` · `總State`→`BatchState` · `一份State`→`SubmissionState` · `名單`→`roster` · `結果們`→`results` · `決定`→`decision` · `寄件紀錄`→`sent_log` · `學生`→`student` · `稽核員人設`→`AUDITOR_PERSONA` · `批改員人設`→`REVIEWER_PERSONA` · `批改員`→`reviewer` · `取得MCP工具`→`get_mcp_tools` · `mcp設定`→`mcp_config` · `作業倉庫設定`→`homework_repo_config` · `作業倉庫接法`→`homework_repo_transport` · `_作業倉庫程序`→`_homework_repo_process` · `批改請求`→`BatchRequest` · `決定請求`→`DecisionRequest` · `開始批改`→`start_batch` · `確認寄信`→`confirm_send` · `查進度`→`get_progress` · `寄件匣`→`OUTBOX` (file `outbox.txt`) · `寄信`→`send_emails` · `寄信前確認`→`confirm_before_send` · `要不要寄`→`should_send` · `要寄`→`to_send` · `待寄`→`pending_emails` · `待確認`→`pending_confirmation` · `抓作業`→`fetch_homework` · `分派`→`dispatch` · `批一份`→`review_one` · `驗證`→`verify` · `只批學生`→`only_students` · `同時批幾份`→`max_concurrency` · `用量計`→`usage_meter` · `結果文字`→`result_text` · `重寫次數`→`rewrite_count` · `結論`→`verdict` · `判斷`→`judgement` · `帶行號`→`with_line_numbers` · `用到的工具`→`used_tools` · `語法`→`syntax` · `行數`→`line_count` · `外洩`→`leaks` · `可疑`→`suspicious` · `可疑樣式`→`SUSPICIOUS_PATTERNS` · `金鑰樣式`→`KEY_PATTERNS` · `樣式`→`pattern` · `文字檔`→`text_files` · `_檔案們`→`_files` · `_掃`→`_scan` · `有key`→`has_key` · `有確認`→`has_confirm` · `有驗證`→`has_verifier` · `印出檢查結果`→`print_check_results` · `符號`→`symbol` · `項目`→`item` · `網址`→`url` · `小助教`→`helper` · `_小助教`→`_helper` · `_小助教伺服器`→`_helper_server` · `設定`→`config` · `紀錄`→`log` · `走過的站`→`stations_visited`

### Notebook cells and nbspec modules

Setup form (`nbbuild.setup`): `模型來源`→`model_source` · `講師_API_KEY`→`INSTRUCTOR_API_KEY` · `colab_模型名稱`→`colab_model_name` · `gemini_模型名稱`→`gemini_model_name` · `_檔案`→`_files` · `回覆`→`reply` · `這本` (param of `project_intro`)→`this_notebook`

nbspec module constants: `作業選項`→`HOMEWORK_OPTIONS` · `需求選項`→`REQUEST_OPTIONS` · `寄信選項`→`SEND_OPTIONS` · `需求表單`→`REQUEST_FORM` · `預設題目`→`DEFAULT_SPEC` · `兩本手冊`→`TWO_HANDBOOKS` · `假金鑰`→`FAKE_KEY`

Form fields and common cell variables: `作業`→`homework` · `結果`→`result` · `名稱`→`name` · `小助教`→`helper` · `最多生成次數`→`max_generations` · `回饋字數上限`→`feedback_char_limit` · `批改需求`→`review_request` · `要跑驗證嗎`→`run_verification` (also used by `en/scripts/verify_notebooks.py` PARAM_OVERRIDES) · `實驗模式`→`experiment_mode` · `存檔`→`checkpointer` · `舊存檔`→`old_checkpointer` · `三次`→`three_runs` · `結果們`→`results` · `步驟們`→`steps` · `名片們`→`cards` · `名片`→`card` · `手冊內文`→`handbook_body` · `讀手冊內文`→`read_handbook_body` · `回饋`→`feedback` · `版本`→`version` · `版本們`→`versions` · `計數器`→`counter` · `抓出名稱`→`extract_names` · `腳本輸出`→`script_output` · `執行命名腳本`→`run_naming_script` · `解析狀態`→`parse_status` · `證據`→`evidence` · `考生`→`candidate` · `預設手冊`→`default_handbook` · `附錄網址`→`appendix_url` · `備用附錄`→`fallback_appendix` · `已載入新規則`→`new_rule_loaded` · `mcp工具`→`mcp_tools` · `可用工具`→`available_tools` · `讀作業的工具`→`read_tools` · `四段作業`→`four_homeworks` · `繞圈agent`→`looping_agent` · `GitHub規模的工具`→`github_scale_tools` · `轉成說明書`→`to_tool_spec` · `估算說明書`→`estimate_tool_spec` · `顯示用量細節`→`show_usage_details` · `有歷史`→`with_history` · `沒歷史`→`without_history` · `第幾圈`→`loop_no` · `system_prompt_加一句`→`system_prompt_extra` · `工具要求次數`→`tool_call_requests` · `工具回傳次數`→`tool_result_count` · `命名State`→`NamingState` · `批改範圍`→`batch_scope` · `port檔`→`port_file` · `成績`→`grade` · `我找到的行號`→`my_line_numbers` · `可疑規則`→`suspicious_rules`

### Names added while translating (also cross-file; keep them stable)

- `deploy/preflight.py`: `run_checks()` (檢查) returns (result, item, note) tuples for `print_check_results()`.
- `deploy/server.py`: module-level async `helper()` (小助教; tests patch `server.helper`); JSON keys `error`, `pending_confirmation`, `emails_to_send`, `sent_log`, `has_checkpoint`, `next_station`, `reviewed_count`, `decision`; request fields `BatchRequest(thread_id, max_concurrency)`, `DecisionRequest(decision)`; waiting station `confirm_before_send`.
- `deploy/multi_agent.py`: interrupt payload key `emails_to_send` (entries `student`, `email`, `verified`, `feedback`); result keys `verify`, `used_tools`; `SEND_OPTIONS` values `Send all`, `Send only verified`, `Send none`; async `open_checkpointer()` (the dual_core one is sync).
- `workshop.ModelCallCounter` and `usage_meter()` expose `.count`.
- 1-B: form field `spec` (題目要求); MCP server key `homework_repo` (作業倉庫).
- 2-A: `experiment_mode` values `pick`, `fixed`, `compare_cards`; 2-B results file keys `three_runs`, `ai_calls`, `evidence`.

## 8. Fake model (`en/tests/mock_colab/fake_llm.py`)

It must understand the English prompts defined above, with the same behavior as the original:
the tool-use JSON line, picking a handbook by word overlap between the review request and card descriptions, a text-only naming check that randomly drops names,
feedback whose length can exceed small limits (so retries happen), the auditor JSON, the 1-0 memory demo (`What is my name?` → `Your name is Alice.` when `Alice` appears in the prompt, otherwise `I don't know your name. I'm an AI and can't remember personal details.`),
and the 1-0 three-word demo (`in three words` → `A programming language.`).
