# 從 LangGraph 到 Skills：教材協作規範

NTU AI Club 工作坊，對象是剛學會 Python 的初學者，兩堂各 120 分鐘。
第 1 堂：2026-11-09；第 2 堂：2026-11-16。
公開 repo：AluminumShark/langgraph-skills-workshop。

## 文件優先順序

1. docs/syllabus.md：目前課程主線、時間與驗收標準。
2. docs/slides-session1-outline.md、docs/slides-session2-outline.md：現行頁次與講者停頓點。
3. scripts/nbspec/：每本 notebook 的實際內容。
4. docs/reuse-from-old-workshop.md、docs/original-proposal.txt、reference/old-workshop/：歷史參考，不是目前規格。

## 來源與產物

- slides/session1.html、slides/session2.html 是單檔 HTML 簡報。保留原有設計、鍵盤操作與講者備註。每張 section 有穩定 id；重排後執行 scripts/sync_slide_navigation.py 重建每頁的靜態導覽和 aria 頁碼，並同步 notebook／文件引用。
- notebooks/ 有七本課程 notebook 與課後選做的 2-E。**不要直接修改 ipynb**。
- 格子定義在 scripts/nbspec/nb_*.py；共用環境、存檔與產生邏輯在 scripts/nbbuild.py。
- review-bot/ 是講師版原始碼；writefile() 從這裡產生相同程式內容。
- llm.py 包裝 Colab 或 Gemini provider；workshop.py 提供檔案、紀錄及顯示功能。
- pyproject.toml 與 uv.lock 管理本機環境。Colab 安裝使用相容版本範圍，不能稱為完全釘死版本。

## 教學規範

1. 主線只要求操作表單、改指定手冊、讀輸出；不要求現場寫框架程式。
2. 長篇基礎設施預設收合；學生要改的 SKILL.md 與作業保持可見。
3. 實驗前寫前置條件與預測題，後面寫觀察問題。輸出相同／不同、模型拒絕／接受都可以是有效觀察，不要求重跑到指定結果。
4. 控制實驗一次只改一項。2-A 分開換手冊、改正文、改 description；2-B 三版的命名規則、輸入、基準集合必須相同。
5. 區分工具原始結果、AI 最終回覆與解析器擷取值；腳本確定性不保證 agent 一定呼叫或完整轉述。
6. 表單使用「最多生成次數（含第一次）」；graph 的相容 API 欄位「最多重試次數」若保留，必須解釋其實際語意。達到上限要標成未通過，不把停止當成功。
7. 語法正確、執行成功、符合題目要求是不同判斷；格式檢查不能驗證內容正確。
8. 每段可否獨立重跑依前置條件而定。不宣稱所有格子都能獨立執行；說明準備格會否覆寫手冊。
9. 瀏覽器斷線不等於 runtime 已回收。重建 runtime 後要重新準備檔案，備份 notebook 與備份 /content/review-bot/ 是不同操作。
10. 主線收束後才放 token metadata、手組 agent、eval、RAG、部署、多 agent 完整系統等補充。
11. Skill、tool、MCP、workflow、agent 不是互斥分類。先決定規則如何表達，再決定誰控制執行時機。
12. 多份獨立作業先教批次，再談並行與子 agent；角色名字不同不等於驗證更可靠。可程式檢查的規則先用程式，重要外部動作加入人工確認。

## 程式規範

- 使用 create_agent（langchain.agents）；手組 StateGraph + ToolNode + tools_condition 為補充。
- 使用中文情境變數與 review-bot 範例，不沿用舊 pandas 情境。
- run_code 保留模組限制、timeout 與錯誤輸出限制；不可稱為完整安全沙箱，不引入 eval 執行任意學生文字。
- 2-C 只使用假金鑰資料，工具不得讀任意真實環境變數；遠端 shell 範例只閱讀，不能執行。
- 2-D 明示本 notebook 使用預設手冊。區分未完成 thread 續跑、完成 thread 取回結果、新 thread 全新執行。列出歷史紀錄不是 Replay。
- 每本提供存檔、zip 下載與歷程輸出。收尾的歷程只代表已執行的格子，不暗示完成全部實驗。

## 英文版（en/）

- en/ 鏡像整個 repo 的英文版；中文檔是主要來源，修改中文來源時同步更新 en/ 對應檔。
- 跨檔名稱、協定字串、投影片標題與用語以 en/GLOSSARY.md 為準；出現新的跨檔名稱時先補進 glossary。
- en/notebooks/*.ipynb 由 uv run python en/scripts/build_notebooks.py 產生；驗證改用 en/scripts/ 與 en/tests/ 下的對應指令（見 en/CLAUDE.md）。

## 修改與驗證

1. 修改前確認工作樹，必要時先 git pull 取得講師從 Colab 存回的版本；不要覆蓋未提交變更。
2. 修改 nbspec 與 review-bot，再執行 uv run python scripts/build_notebooks.py；可加 1-A 2-B 等名稱前綴。
3. 只有來源完全相同的 code cell 才沿用舊輸出，重排不依位置接輸出；修改過的程式不沿用舊結果。產生器在覆寫前會把有失效輸出的舊 notebook 完整保存到 notebooks/output-history/ 並提示位置；備份失敗就停止覆寫。檢查並提交需要保留的快照。沿用輸出不等於驗過新前置狀態，不能由空白輸出推論使用者未執行。
4. 執行 uv run python -m unittest discover -s tests，檢查語意與輸出保存的回歸案例。
5. 執行 uv run python scripts/verify_notebooks.py，把八本 notebook 從頭跑到尾。使用 tests/mock_colab/ 假模型，僅驗程式流程，不代表真實模型品質或正式 Colab 相容性。
6. 修改投影片後執行 scripts/sync_slide_navigation.py --check，檢查頁次、內文引用與大綱一致。
7. 課前另用真實 Colab 試跑主要操作，確認帳號可用功能、模型額度與實際授課耗時。
