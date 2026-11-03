from nbbuild import badge, code, ending, md, project_intro, setup, writefile

NAME = "2-B_code_text_script"

# 每個 run cell 帶共用觀察函式；仍需先完成環境設定與該段檔案準備
HELPERS = '''import json, re

def 讀手冊內文(path):
    text = path.read_text(encoding="utf-8")
    return text.split("---", 2)[2].strip() if text.startswith("---") else text

def 抓出名稱(text):
    """從回覆裡抓出「第 N 行：名稱」，回傳排序過的 [(行號, 名稱), ...]。"""
    return sorted({(int(行), 名稱) for 行, 名稱 in re.findall(r"第\\s*(\\d+)\\s*行[：:]\\s*([A-Za-z_]\\w*)", text)})

def 解析狀態(text):
    lines = [line for line in text.splitlines() if line.strip()]
    unmatched = [line for line in lines if "行" in line and not 抓出名稱(line)]
    if unmatched:
        return "部分行無法解析，請對照原文"
    if not 抓出名稱(text) and not text.strip().startswith("OK："):
        return "無法從格式確認問題數，請對照原文"
    return "可解析"

def 存結果(版本, 資料):
    path = BASE / "2B_results.json"
    全部 = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    全部[版本] = 資料
    path.write_text(json.dumps(全部, ensure_ascii=False, indent=2), encoding="utf-8")'''


def _run(src: str) -> str:
    """把 HELPERS 插在 {PREAMBLE} 後面（縮排 8 格，和 code(\"\"\"...\"\"\") 裡其他行一致）。"""
    helpers = "\n".join(("        " + line) if line else "" for line in HELPERS.splitlines())
    return src.replace("        {HELPERS}", helpers)


def cells():
    return [
        md(f"""
        # 2-B：同一件事的三種放法：程式、文字、腳本

        {badge(NAME)}

        > 📍 **對應簡報**：第 2 堂「第二站：程式・文字・腳本」，投影片 **13–19**（課堂時間 0:28–0:48）
        """),
        project_intro("同一個「檢查變數命名」，分別放進手冊文字、腳本、流程三個地方，各跑三次，比較「誰負責檢查」與「誰決定執行」。"),
        md("""
        ## 這本 notebook 在做什麼

        小助教想多做一件事：**檢查變數名稱是不是「小寫英文加底線」**（例如 `my_score` 合格，`myScore`、`MyScore` 不合格）。
        同一句規則，可以放在三個地方：

        | 放法 | 放在哪裡 | 誰來做檢查 |
        | --- | --- | --- |
        | **A** | 寫進手冊文字（`skills/naming-check/SKILL.version-a.md`） | AI 每次自己想一遍怎麼檢查 |
        | **B** | 寫成手冊旁邊的小程式 `scripts/check_naming.py`，手冊叫 AI 去執行 | AI 決定要不要執行，檢查本身是 Python |
        | **C** | 寫成流程（LangGraph）裡的一站 | 流程走到這裡一定會檢查，AI 根本不經手 |

        三個都做得到，那差在哪？**各跑三次，記錄結果是否相同、有沒有呼叫工具、花了幾次 AI；結果相同時，差別在誰檢查、誰決定執行。**
        這本的新名詞只有一個：**腳本**（放在手冊 `scripts/` 資料夾裡、真的會執行的小程式）。

        | 段落 | 你會做什麼 | 對應投影片 |
        | --- | --- | --- |
        | 第 1 段 | 看作業和腳本；用命令列跑一次 `check_naming.py` | 14、16 |
        | 第 2 段 | 放法 A：寫在手冊文字裡，跑三次 | 15 |
        | 第 3 段 | 放法 B：寫成腳本，手冊叫 AI 去執行，跑三次 | 16 |
        | 第 4 段 | 放法 C：寫成 LangGraph 節點，跑三次 | 17 |
        | 第 5 段 | 三個版本並排比較；本堂口訣 | 17–18 |
        | 第 6 段 | 停一下：五件事各放哪？ | 19 |

        ## 怎麼用（這本不用改任何東西）

        1. 先執行 **「0. 環境設定」**。
        2. 每一段：**🤔 先猜三次是否一樣、會呼叫幾次 AI → ▶ 執行 → 👀 對照**。
        3. 第 2–4 段會把本版本的最新三輪結果寫入 `2B_results.json`，重跑會取代該版本舊紀錄。第 5 段使用 A、B、C 各自最後一次紀錄，請在同一套規則與作業下依序完成。
        4. 這本的環境設定與檔案準備格會覆寫內含的手冊和腳本。先保留修改，再重新準備；不同 notebook 不會自動接續你改過的版本。
        5. 每跑一次會叫幾次 AI：A 每輪 1 次；B 依工具選擇與迴圈而變，請看實測計數；C 的命名檢查為 0 次。
        """),
        setup(NAME, support=[
            "tools/__init__.py",
            "tools/check_naming.py",
            "skills/naming-check/scripts/check_naming.py",
            "skills/naming-check/SKILL.md",
            "skills/naming-check/SKILL.version-a.md",
        ]),
        md("""
        ---
        ## 第 1 段：同一件事，三個地方都能放

        > 📍 **對應簡報**：投影片 14「同一個命名檢查，三種放法」、投影片 16「放法 B：模型選工具，腳本做檢查」

        比較之前，先準備兩樣東西：
        1. 這本 notebook 從頭到尾都用**同一份作業**（下面會印出來，左邊是行號）。
        2. 命名檢查的**腳本** `check_naming.py`：看完作業後的第一個準備格會把它寫進手冊的 `scripts/` 資料夾。
           它只做一件事，輸出短短幾行，像一個小型的命令列工具。
           下一個準備格是 `tools/check_naming.py`：在腳本外面包一層 `@tool`，把它變成 AI 可以呼叫的**工具**，
           就能放進 **agent**（會自己決定要不要用工具的 AI）的工具箱，第 3 段會用到。

        ### 🤔 預測題
        三個版本使用同一份規則：
        - 檢查賦值變數、函式名稱和函式參數；同名只列第一次定義的位置，不檢查類別名稱，略過 `self`、`cls`。
        - 名稱可有一個開頭底線，接小寫英文字母，後面可接小寫英文字母、數字或底線。
        - 本練習不設常數例外，因此 `MAX` 不合格，`result_2` 合格。這是本課的規則，不是在宣告所有 Python 專案都如此。

        執行下一格只會顯示作業。**先圈出不合規名稱並數一數，再往下核對。**
        """),
        code("""
        #@title 👀 先看作業並在紙上作答（這格不顯示答案）
        {PREAMBLE}
        for i, line in enumerate(範例作業["命名不一致"].splitlines(), 1):
            print(f"{i:>3} | {line}")
        print("先圈出不合規名稱，再執行下方腳本核對。")
        """),
        writefile("skills/naming-check/scripts/check_naming.py"),
        writefile("tools/check_naming.py"),
        code("""
        #@title ▶ 執行：看作業，再用命令列跑一次 check_naming.py
        {PREAMBLE}
        import subprocess

        作業 = 範例作業["命名不一致"]
        (BASE / "作業.py").write_text(作業, encoding="utf-8")
        print("這份作業（左邊是行號）：")
        for i, line in enumerate(作業.splitlines(), start=1):
            print(f"{i:>3} | {line}")

        腳本 = BASE / "skills" / "naming-check" / "scripts" / "check_naming.py"
        print("\\n$ python check_naming.py 作業.py")
        結果 = subprocess.run([sys.executable, str(腳本), str(BASE / "作業.py")],
                            capture_output=True, text=True, encoding="utf-8")
        print(結果.stdout.strip() or 結果.stderr.strip())
        記下("2-B 第 1 段：check_naming.py 的輸出", 結果.stdout.strip())
        """),
        md("""
        ### 👀 你看到了什麼

        - 腳本抓到 **6 個**：`CalcAverage`、`scoreList`、`Total`、`avgScore`、`myScores`、`MAX`。`s` 和 `result_2` 是合格的。
        - `MAX` 算不算？Python 習慣上常數可以全大寫，但我們的規則寫的是「小寫加底線」，**腳本就照規則做**。
          要不要開例外是人決定的；相同腳本處理相同輸入時，結果相同。
        - 輸出只有幾行、每行一個問題：AI 讀得懂，人也讀得懂。這就是腳本的原則：一個腳本只做一件事、輸出要短。
        """),
        md("""
        ---
        ## 第 2 段：放法 A：寫進手冊文字

        > 📍 **對應簡報**：投影片 15「放法 A：模型依手冊文字判斷」

        上一段腳本依本課規則列出 6 個問題。這一段先試最直覺的放法：把規則寫進手冊文字，讓 AI 自己檢查。

        下一格把手冊 `skills/naming-check/SKILL.version-a.md` 寫成「文字版」：使用與腳本相同的名稱範圍、格式與例外規則。
        再下一格讓 AI 讀這本手冊、檢查同一份作業，**連續跑三次**。

        ### 🤔 預測題
        三次抓到的數量會一樣嗎？會跟第 1 段腳本抓到的 6 個一樣嗎？
        """),
        writefile("skills/naming-check/SKILL.version-a.md"),
        code(_run("""
        #@title ▶ 執行：放法 A，同一份作業跑三次（AI 自己檢查）
        {PREAMBLE}
        {HELPERS}
        from langchain_core.messages import HumanMessage, SystemMessage

        手冊 = 讀手冊內文(BASE / "skills" / "naming-check" / "SKILL.version-a.md")
        print("AI 讀到的手冊內文：\\n" + 手冊 + "\\n")
        作業 = 範例作業["命名不一致"]

        計數器 = 模型呼叫計數器()
        三次, 證據 = [], []
        for i in range(1, 4):
            回答 = model.invoke(
                [SystemMessage(手冊), HumanMessage(f"請檢查這份作業：\\n```python\\n{作業}```")],
                config={"callbacks": [計數器]},
            ).text
            print(f"第 {i} 次原始回答：\\n{回答}")
            print("解析狀態：", 解析狀態(回答))
            證據.append({"原始回答": 回答, "解析狀態": 解析狀態(回答)})
            結果 = 抓出名稱(回答)
            三次.append(結果)
            print(f"第 {i} 次：抓到 {len(結果)} 個 → " + ("、".join(f"第{行}行 {名}" for 行, 名 in 結果) or "（沒有可解析的項目，請讀原始回答）"))

        一樣 = all(x == 三次[0] for x in 三次)
        print(f"\\n三次一樣嗎？{'✅ 一樣' if 一樣 else '❌ 不一樣'}；總共呼叫了 AI {計數器.次數} 次")
        存結果("A", {"三次": 三次, "AI呼叫": 計數器.次數, "證據": 證據})
        記下("2-B 第 2 段：放法 A（寫在手冊文字裡）", {"三次": 三次, "三次一樣": 一樣, "AI呼叫": 計數器.次數, "證據": 證據})
        """)),
        md("""
        ### 👀 你看到了什麼

        - 檢查三次結果是否相同，再和腳本結果對照。可能出現漏項、多項、行號不同，或完全一致。
          模型每次重新依文字規則判斷，這三次可能一致，也可能不同。
        - 三次一致也是有效觀察，請如實記錄，不用重跑到出錯。三次一致不代表對所有輸入都有保證；再檢查名稱與行號是否符合共同規則。
        - 而且它跟腳本的 6 個不一定對得上：先區分：模型判斷錯誤、回覆格式無法解析，還是本次判斷正確。
        """),
        md("""
        ---
        ## 第 3 段：放法 B：寫成小程式，手冊叫 AI 去執行

        > 📍 **對應簡報**：投影片 16「放法 B：模型選工具，腳本做檢查」

        放法 A 由 AI 每次依文字規則重新判斷。這一段把檢查交給腳本，AI 只負責決定要不要執行它。

        下一格寫出獨立的「腳本版」手冊 `SKILL.md`（A 使用另一個檔案，重跑不會混用）：「執行 `scripts/check_naming.py`（工具名稱 `check_naming`），把它的輸出寫進回饋。」
        再下一格用 `create_agent`（一行做出 agent 的寫法）做一個 agent：手冊當它的 **system prompt**
        （每次都放在最前面、告訴 AI 要遵守什麼的那段話），工具箱裡只有 `check_naming` 這一把（就是第 1 段包好的腳本），一樣**跑三次**。

        ### 🤔 預測題
        1. 這次三次抓到的會一樣嗎？會跟第 1 段腳本的輸出一樣嗎？
        2. AI 這次做了哪兩件事？它還需要自己想「怎麼檢查」嗎？
        """),
        writefile("skills/naming-check/SKILL.md"),
        code(_run("""
        #@title ▶ 執行：放法 B，同一份作業跑三次（AI 決定要不要跑腳本）
        {PREAMBLE}
        {HELPERS}
        from langchain.agents import create_agent
        from tools.check_naming import check_naming

        手冊 = 讀手冊內文(BASE / "skills" / "naming-check" / "SKILL.md")
        print("AI 讀到的手冊內文：\\n" + 手冊 + "\\n")
        作業 = 範例作業["命名不一致"]
        小助教 = create_agent(model, tools=[check_naming], system_prompt=手冊)

        計數器 = 模型呼叫計數器()
        三次, 證據 = [], []
        for i in range(1, 4):
            result = 小助教.invoke(
                {"messages": [{"role": "user", "content": f"請檢查這份作業：\\n```python\\n{作業}```"}]},
                config={"callbacks": [計數器]},
            )
            msgs = result["messages"]
            用了 = [c["name"] for m in msgs for c in (getattr(m, "tool_calls", None) or [])]
            工具結果 = [m for m in msgs if m.type == "tool" and getattr(m, "name", "") == "check_naming"]
            腳本輸出 = [m.text for m in 工具結果]
            最後回覆 = msgs[-1].text
            結果 = 抓出名稱(最後回覆)
            腳本項目 = sorted({pair for t in 腳本輸出 for pair in 抓出名稱(t)})
            有執行 = any(getattr(m, "status", "success") != "error" for m in 工具結果)
            保留 = 有執行 and 結果 == 腳本項目 and 解析狀態(最後回覆) == "可解析"
            證據.append({"模型要求工具": 用了, "工具有成功回傳": 有執行, "腳本原文": 腳本輸出, "腳本項目": 腳本項目,
                         "最後回覆": 最後回覆, "解析狀態": 解析狀態(最後回覆), "完整保留項目": 保留})
            三次.append(結果)
            print(f"========== 第 {i} 次 ==========")
            print("AI 要求的工具：", "、".join(用了) or "（沒有用工具，自己判斷）")
            print("工具有成功回傳：", 有執行)
            if 腳本輸出:
                print("各次腳本回傳：\\n" + "\\n---\\n".join(腳本輸出))
            print("AI 最後回覆原文：\\n" + 最後回覆)
            print("解析狀態：", 解析狀態(最後回覆), "｜是否保留腳本全部項目：", 保留)
            print(f"AI 最後的回覆抓到 {len(結果)} 個 → " + ("、".join(f"第{行}行 {名}" for 行, 名 in 結果) or "（沒有可解析的項目，請讀原始回答）"))
            print()

        一樣 = all(x == 三次[0] for x in 三次)
        print(f"三次一樣嗎？{'✅ 一樣' if 一樣 else '❌ 不一樣'}；總共呼叫了 AI {計數器.次數} 次")
        存結果("B", {"三次": 三次, "AI呼叫": 計數器.次數, "證據": 證據})
        記下("2-B 第 3 段：放法 B（寫成腳本）", {"三次": 三次, "三次一樣": 一樣, "AI呼叫": 計數器.次數, "證據": 證據})
        """)),
        md("""
        ### 👀 你看到了什麼

        - 先確認三次是否真的呼叫工具；有呼叫時，再對照腳本結果與最後回覆。腳本結果固定，不代表模型每次都會呼叫或完整轉述。
        - AI 不再自己想怎麼檢查，本例希望它負責兩件事：**決定是否跑工具**、**把結果整理進回覆**；請用輸出確認它實際怎麼做。相同輸入與規則下，腳本結果固定；轉述仍需要核對。
        - 但「要不要跑」還是 AI 決定的：如果某一次它沒叫工具、自己判斷，即使答案碰巧相同，也沒有執行腳本的證據。下一段的放法 C 就沒有這個問題。
        - 若只呼叫一次工具，通常有兩次模型回應：先提出工具要求，再寫最後回覆。未用工具或多次呼叫時，次數不同，以計數器為準。
        """),
        md("""
        ---
        ## 第 4 段：放法 C：寫成 LangGraph 節點，AI 根本不經手

        > 📍 **對應簡報**：投影片 17「放法 C：流程固定執行同一份檢查」

        放法 B 還是由 AI 決定要不要執行腳本。這一段乾脆不讓 AI 經手。

        這一版沒有手冊、也沒有 agent，只有一條用 LangGraph 畫的**流程**。流程裡的每一站叫**節點**（就是一個函式），走到就一定會執行；
        各站之間傳遞資料的那個 dict 叫 **State**。這條流程只有一站 `check_naming`：它直接呼叫同一支腳本，把結果寫進 State 的 `naming_problems`。
        就像小助教的 `check_syntax`：流程走到這裡，就一定會檢查。

        ### 🤔 預測題
        三次會一樣嗎？這一版總共會呼叫幾次 AI？
        """),
        code(_run("""
        #@title ▶ 執行：放法 C，流程一定會跑檢查，跑三次
        {PREAMBLE}
        {HELPERS}
        from typing import TypedDict
        from langgraph.graph import END, START, StateGraph
        from tools.check_naming import 執行命名腳本

        class 命名State(TypedDict):
            code: str
            naming_problems: str

        def check_naming(state: 命名State) -> dict:
            return {"naming_problems": 執行命名腳本(state["code"])}

        builder = StateGraph(命名State)
        builder.add_node("check_naming", check_naming)
        builder.add_edge(START, "check_naming")
        builder.add_edge("check_naming", END)
        流程 = builder.compile()

        作業 = 範例作業["命名不一致"]
        計數器 = 模型呼叫計數器()
        三次 = []
        for i in range(1, 4):
            state = 流程.invoke({"code": 作業, "naming_problems": ""}, config={"callbacks": [計數器]})
            結果 = 抓出名稱(state["naming_problems"])
            三次.append(結果)
            print(f"第 {i} 次：抓到 {len(結果)} 個 → " + "、".join(f"第{行}行 {名}" for 行, 名 in 結果))

        一樣 = all(x == 三次[0] for x in 三次)
        print(f"\\n三次一樣嗎？{'✅ 一樣' if 一樣 else '❌ 不一樣'}；總共呼叫了 AI {計數器.次數} 次")
        存結果("C", {"三次": 三次, "AI呼叫": 計數器.次數})
        記下("2-B 第 4 段：放法 C（寫成流程節點）", {"三次": 三次, "三次一樣": 一樣, "AI呼叫": 計數器.次數})
        """)),
        md("""
        ### 👀 你看到了什麼

        - 相同輸入與腳本下，這三次應得到相同結果；命名檢查本身**呼叫 AI 0 次**。環境設定的模型連線測試另計。
        - B 與 C 都使用同一支腳本；要區分：**B 由 AI 判斷是否執行，C 由流程固定呼叫。**
          這件事能不能漏掉，決定你選 B 還是 C。
        """),
        md("""
        ---
        ## 第 5 段：三個版本並排

        > 📍 **對應簡報**：投影片 17（B 和 C 的差別）、投影片 18「兩個問題，分開決定」

        以下把 A、B、C 三種放法簡稱「三個版本」。三個版本都跑完了，結果也都存成了檔案。這一格把第 2–4 段的結果並排，還沒跑過的版本會提醒你先回去跑。

        ### 🤔 預測題
        如果三個版本結果都一樣，差別在哪裡？哪一個最省 AI？如果每份作業都必須檢查命名，你會選 B 還是 C？
        """),
        code("""
        #@title ▶ 執行：三個版本並排比較
        {PREAMBLE}
        import json
        from IPython.display import Markdown, display

        path = BASE / "2B_results.json"
        全部 = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        說明 = {
            "A": ("A：寫在手冊文字裡", "第 2 段"),
            "B": ("B：寫成腳本，AI 決定要跑", "第 3 段"),
            "C": ("C：寫成流程節點，一定會跑", "第 4 段"),
        }
        列 = ["| 版本 | 三次可解析項目數 | 三次一樣嗎 | 花了幾次 AI | 解析／工具證據 |", "| --- | --- | --- | --- | --- |"]
        for 版本, (名稱, 段落) in 說明.items():
            if 版本 not in 全部:
                列.append(f"| {名稱} | （還沒跑：先跑{段落}） | | | |")
                continue
            三次 = 全部[版本]["三次"]
            數量 = "、".join(str(len(x)) for x in 三次)
            一樣 = "✅ 一樣" if all(x == 三次[0] for x in 三次) else "❌ 不一樣"
            證據 = 全部[版本].get("證據", [])
            摘要 = "；".join(e["解析狀態"] + (f"／工具回傳={e['工具有成功回傳']}、保留={e['完整保留項目']}" if 版本 == "B" else "") for e in 證據) or "流程直接取得腳本結果"
            列.append(f"| {名稱} | {數量} | {一樣} | {全部[版本]['AI呼叫']} | {摘要} |")
        display(Markdown("\\n".join(列)))
        記下("2-B 第 5 段：三個版本並排", 全部)
        """),
        md("""
        ### 👀 你看到了什麼

        - **A** 由模型判斷，請依實際結果記錄一致性；**B** 要分開看工具是否執行、腳本輸出與模型轉述；**C** 由流程直接執行腳本。
        - **C** 的這項檢查不呼叫模型，而且由流程固定執行；**B** 讓模型視情況選工具。三次一致是觀察結果，執行方式則由程式結構決定。

        ### 📌 分開問兩個問題

        > **怎麼做？** 固定規則用程式或腳本；需要判斷的準則寫進手冊。
        > **誰決定執行？** 每次必做由流程固定呼叫；需要視情況決定時，交給 agent 選工具。

        同一支腳本可以被流程呼叫，也可以包成工具。這兩個問題不是互斥的三個抽屜。
        """),
        md("""
        ---
        ## 第 6 段：停一下：五件事各放哪？

        > 📍 **對應簡報**：投影片 19「停一下：五件事，分別回答兩個問題」

        最後依序回答：**用什麼完成這件事？由誰決定是否執行？** 條件不足時可以寫出你的假設，答案可以組合，不限單選。

        | 這件事 | 怎麼做／誰決定執行？ |
        | --- | --- |
        | 1. 回饋用什麼語氣 | ＿＿＿＿ |
        | 2. 執行作業看輸出 | ＿＿＿＿ |
        | 3. 最多生成三次（含第一次） | ＿＿＿＿ |
        | 4. 檢查有沒有寫註解 | ＿＿＿＿ |
        | 5. 判斷邏輯寫得好不好 | ＿＿＿＿ |

        <details>
        <summary>寫完再點開看參考答案</summary>

        | 這件事 | 怎麼做 | 執行安排與理由 |
        | --- | --- | --- |
        | 1. 回饋用什麼語氣 | **手冊** | 把語氣準則寫進 Skill，寫回饋時提供給模型 |
        | 2. 執行作業看輸出 | **腳本／工具** | 用工具執行；本例讓 agent 視情況選用，若每份必測則改由流程安排 |
        | 3. 最多生成三次（含第一次） | **程式** | 本課 `retries` 計入第一稿，`retries >= 3` 就停，能寫成 if，而且不能漏，不然會無限轉圈 |
        | 4. 檢查有沒有寫註解 | **腳本**（一定不能漏就做成**流程節點**） | 用程式辨認真正的註解；每份必查由流程安排，選查可包成工具。字串裡的 # 不算註解 |
        | 5. 判斷邏輯寫得好不好 | **手冊** | 將品質準則寫進 Skill；可執行的正確性測試仍交給程式，模型負責補充判讀 |

        </details>
        """),
        *ending(),
    ]
