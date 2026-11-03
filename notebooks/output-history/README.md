# 原始輸出快照

這裡保留原始 notebook 的**程式、表單值、真實輸出與執行次數**。它們是歷史執行證據，不代表最新版程式已跑過；課堂使用上一層的最新版 notebook。

## 從 Git 歷史找回的三本

下列快照完整取自提交 `8d4b4b3edcd7287337a8cd768ce4e2fac368267c`，檔案位元組與該提交完全相同。檔名是內容的 SHA-256，便於核對及避免重複備份。

| 歷史 notebook | 有輸出的程式格 | 實際保存內容 |
| --- | --- | --- |
| [1-0 Tool calling](1-0_tool_calling/cc74105eceacfb30cede5b4ed9c80c6dc16a3c8f01e5a32e2b39f3667d1497f6.ipynb) | 9／9 | 帶歷史回覆、單次工具交接、遇到 NameError 後模型停止 |
| [1-B Agent](1-B_agent/927ba99b10f8d0b0c5fa4d19791c1f6b2fa5655e3255c8f22be1ea94a4c9abee.ipynb) | 18／18 | 本地工具、三次直接回覆、always_fail 自行停止、MCP 工具執行 |
| [2-A Skills](2-A_skills/cd09b61d511c81b2cbcb7be65137d7be612434a3105e28f21c0e7b9083eea761.ipynb) | 11／11 | 一次初學者需求載入 friendly 手冊；名片與內文 token 估算 |

這三本在教材修改、重建後沒有保留部分不再完全相同的程式格輸出。這是產生器的來源比對規則造成的，不能據此推論使用者沒跑過或沒存檔。

## 本輪修正前的最新真實輸出

以下快照由重建保護機制保存，保留當時工作檔的原始位元組；JSON 內容已核對與提交 `2979fd3` 的對應 notebook 相同。修改後的格子不繼承這些舊結果。

| Notebook | 保存的輸出 | 快照 |
| --- | --- | --- |
| 1-B | 18／18 格，含 13 次工具要求／12 次回傳的原始紀錄 | [修正前完整檔](1-B_agent/c3171820bb697d65ef337f9be0775c779571b8ff05716d7c3c9cb5f46936b8ff.ipynb) |
| 2-A | 16／16 格，包含未改結尾規則的基準結果 | [修正前完整檔](2-A_skills/8690e4ebeeebff6acdfe7a5839c35849a0745a317d9e7ccf9816b2bfe95ec082.ipynb) |
| 2-C | 12／12 格，定位題行號仍為 0 | [修正前完整檔](2-C_security/3e6c5d6d8e6056351377579d2b257f912af343997dfded925eeab2ef0c43ccb3.ipynb) |
| 2-D | 11／11 格，含舊題目配對與已啟用的 eval 成績 | [修正前完整檔](2-D_dual_core/8db0acac917a6d0b6b8162e356f3a30fcd962bf35936bf736edec757f3bf22da.ipynb) |

## 之後重建時的保護

`scripts/nbbuild.py` 只把來源完全相同的輸出沿用到新版。若修改或刪除程式格會使舊輸出無法沿用，產生器會先將整本舊檔保存到本目錄，顯示位置，再寫新版；備份失敗時停止覆寫。

- 自動快照位置：`output-history/<notebook 名稱>/<內容 SHA-256>.ipynb`。
- 相同內容只保存一份。只改 Markdown、且所有輸出都能沿用時，不新增快照。
- 重建後檢查 `git status`，需要保存的快照須一起提交。
- 不把舊輸出直接接到變更後的程式碼，也不以假模型結果補成真實 Colab 輸出。

詳細觀察與新版差異見 [輸出檢查報告](../../docs/notebook-output-review.md)。
