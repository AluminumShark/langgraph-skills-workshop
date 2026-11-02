# Notebooks

點 **Open in Colab** 直接在瀏覽器打開；打開後先「檔案 → 在雲端硬碟中儲存副本」，再執行第一格「0. 環境設定」。

| Notebook | 內容 | |
| --- | --- | --- |
| `1-0_tool_calling` | 第 1 堂：模型只會「說」它想用哪個工具 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/1-0_tool_calling.ipynb) |
| `1-A_workflow` | 第 1 堂：Workflow，路線由程式決定 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/1-A_workflow.ipynb) |
| `1-B_agent` | 第 1 堂：Agent，路線由 AI 決定；tool 與 MCP | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/1-B_agent.ipynb) |
| `2-A_skills` | 第 2 堂：Skill 是給 AI 的工作手冊 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-A_skills.ipynb) |
| `2-B_code_text_script` | 第 2 堂：同一件事的三種放法（文字、腳本、程式） | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-B_code_text_script.ipynb) |
| `2-C_security` | 第 2 堂：別人的手冊能直接用嗎（prompt injection） | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-C_security.ipynb) |
| `2-D_dual_core` | 第 2 堂：流程與 Agent 整合，流程控制順序、agent 依手冊判斷 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-D_dual_core.ipynb) |
| `2-E_deploy` | 課後選做：上雲端前的準備 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-E_deploy.ipynb) |

> 這些檔案由 `scripts/build_notebooks.py` 產生，請改 `scripts/nbspec/`（以及 `review-bot/` 的原始碼），不要直接改 `.ipynb`。
> 本機驗證的輸出 `*.executed.ipynb` 不會進 git。

課堂節奏是「準備 → 預測 → 執行 → 對照」。先完成 1-0／1-A／1-B，再做第二堂；每本的準備格會寫入該本所需的預設檔案，不會自動沿用另一個 runtime 的修改。

- 2-A：只改需求觀察選書、固定手冊改正文、固定需求改 description，一次只改一項。
- 2-B：先看作業找問題，再比較文字、agent 選用腳本、流程直接執行。同樣結果也算有效觀察。
- 2-C：先預測，再比較有／無工具權限，依工具紀錄與回覆找出惡意行；只使用假金鑰。
- 2-D：主線辨識未完成續跑、完成取回、新 thread；純 agent 與 eval 是選做。
- 2-E 與每本標示「補充／選做」的段落不計入課堂主線。

重跑前先看該段前置條件，準備格可能覆寫手冊。執行階段被回收時 `/content/` 的檔案不會保留；請分別保存 notebook 副本及手冊／程式／checkpoint 的備份。
