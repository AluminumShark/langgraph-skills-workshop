"""練習 4：上線前檢查。每一項都是用程式檢查（sensor），不是靠感覺。

用法：python -m deploy.preflight（在 review-bot/ 資料夾裡）
"""

import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

金鑰樣式 = [
    (r"AIza[0-9A-Za-z\-_]{35}", "Google API key"),
    (r"sk-[A-Za-z0-9_\-]{20,}", "OpenAI / Anthropic 類型的 key"),
    (r"(?i)(api[_-]?key|token|password)\s*=\s*['\"][^'\"\s]{8,}['\"]", "寫死在程式裡的密碼"),
]
可疑樣式 = [
    (r"curl[^\n|]*\|\s*(ba)?sh|wget[^\n|]*\|\s*(ba)?sh", "下載後直接執行（curl … | bash）"),
    (r"base64\s+(-d|--decode)", "解碼一段看不懂的內容"),
    (r"(?i)ignore (all |the )?previous|忽略(之前|以上|前面)", "要 AI 忽略之前的指示"),
    (r"(?i)環境變數|read_env|WORKSHOP_API_KEY|\$[A-Z_]*KEY", "要 AI 去讀金鑰或環境變數"),
]
文字檔 = {".py", ".md", ".sh", ".json", ".txt", ".toml", ".yaml", ".yml", ""}
略過 = {"__pycache__", ".llm.json", "history.jsonl", ".env.example"}


def _檔案們(root: Path):
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix in 文字檔 and not (set(p.parts) & 略過) and p.name not in 略過:
            yield p


def _掃(root: Path, 樣式) -> list[str]:
    找到 = []
    for p in _檔案們(root):
        if p.resolve() == Path(__file__).resolve():
            continue  # 不掃自己（這個檔案裡本來就寫著這些樣式）
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for pattern, 說明 in 樣式:
                if re.search(pattern, line):
                    找到.append(f"{p.relative_to(BASE)} 第 {i} 行：{說明}")
    return 找到


def 檢查() -> list[tuple[str, str, str]]:
    """回傳 [(結果, 項目, 說明)]，結果是 ✅ / ⚠️ / ❌。"""
    結果 = []

    外洩 = _掃(BASE, 金鑰樣式)
    結果.append(("❌" if 外洩 else "✅", "程式和手冊裡沒有寫死的金鑰",
               "；".join(外洩) if 外洩 else "金鑰應該放在 Secrets / Secret Manager，從環境變數讀"))

    來源 = os.environ.get("WORKSHOP_PROVIDER") or "（看 0. 環境設定 的選擇）"
    有key = bool(os.environ.get("GOOGLE_API_KEY"))
    結果.append(("✅" if 有key else "⚠️", "模型金鑰從環境變數來",
               f"WORKSHOP_PROVIDER={來源}；GOOGLE_API_KEY {'已設定' if 有key else '沒設定（Colab 內建模型不需要，上雲端一定要）'}"))

    可疑 = _掃(BASE / "skills", 可疑樣式)
    結果.append(("❌" if 可疑 else "✅", "第三方 Skill 掃描（2-C 的三個習慣）",
               "；".join(可疑) if 可疑 else "skills/ 裡沒有可疑的指令"))

    sys.path.insert(0, str(BASE))
    from tools.run_code import 執行作業

    擋下 = 執行作業("import os\nos.listdir('.')").startswith("⛔")
    結果.append(("✅" if 擋下 else "❌", "run_code 有圍欄", "import os 會被擋下" if 擋下 else "import os 沒有被擋下！"))

    多agent = BASE / "deploy" / "multi_agent.py"
    內容 = 多agent.read_text(encoding="utf-8") if 多agent.exists() else ""
    結果.append(("✅" if "recursion_limit" in 內容 else "❌", "agent 有 recursion_limit", "每個批改子 agent 最多跑 25 步"))
    結果.append(("⚠️" if "SqliteSaver" in 內容 else "✅", "checkpointer 是持久的",
               "SQLite 只存在這一台機器；雲端機器會被換掉，上線要改用 PostgresSaver"))
    有確認 = "interrupt(" in 內容
    結果.append(("✅" if 有確認 else "❌", "不可逆的動作（寄信）前面有 interrupt", "寄信前會停下來等人確認" if 有確認 else "找不到 interrupt"))
    有驗證 = "稽核員人設" in 內容
    結果.append(("✅" if 有驗證 else "❌", "有獨立的驗證 agent", "批改和稽核是兩個不同人設，不會自己放過自己" if 有驗證 else "找不到驗證 agent"))

    網址 = os.environ.get("HOMEWORK_MCP_URL")
    結果.append(("✅" if 網址 else "⚠️", "作業倉庫 MCP 從網址連（遠端 MCP）",
               f"HOMEWORK_MCP_URL={網址}" if 網址 else "現在是在同一台機器用 stdio 開 MCP server；上雲端要改成遠端 MCP 的網址（加上 OAuth 登入）"))

    缺 = [f for f in ("langgraph.json", "requirements.txt", "Dockerfile", ".dockerignore") if not (BASE / f).exists()]
    結果.append(("❌" if 缺 else "✅", "部署檔都在", f"缺少：{'、'.join(缺)}" if 缺 else "langgraph.json、requirements.txt、Dockerfile、.dockerignore"))
    return 結果


def 印出檢查結果() -> bool:
    結果 = 檢查()
    for 符號, 項目, 說明 in 結果:
        print(f"{符號} {項目}\n     {說明}")
    失敗 = sum(1 for r in 結果 if r[0] == "❌")
    print(f"\n{'🚫 有 ' + str(失敗) + ' 項沒過，先修好再上線' if 失敗 else '🎉 沒有 ❌，⚠️ 的項目上線前記得處理'}")
    return 失敗 == 0


if __name__ == "__main__":
    sys.exit(0 if 印出檢查結果() else 1)
