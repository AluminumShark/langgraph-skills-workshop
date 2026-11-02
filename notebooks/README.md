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
| `2-D_dual_core` | 第 2 堂：雙核，流程鎖順序、agent 帶手冊判斷 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-D_dual_core.ipynb) |
| `2-E_deploy` | 課後選做：上雲端前的準備 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AluminumShark/langgraph-skills-workshop/blob/main/notebooks/2-E_deploy.ipynb) |

> 這些檔案由 `scripts/build_notebooks.py` 產生，請改 `scripts/nbspec/`（以及 `review-bot/` 的原始碼），不要直接改 `.ipynb`。
> 本機驗證的輸出 `*.executed.ipynb` 不會進 git。
