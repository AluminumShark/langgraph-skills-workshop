from nbbuild import badge, code, ending, md, setup, writefile

NAME = "2-B_code_text_script"

# 每個 run cell 都自己帶這三個小工具，讓每一段都能單獨重跑
HELPERS = '''import json, re

def 讀手冊內文(path):
    text = path.read_text(encoding="utf-8")
    return text.split("---", 2)[2].strip() if text.startswith("---") else text

def 抓出名稱(text):
    """從回覆裡抓出「第 N 行：名稱」，回傳排序過的 [(行號, 名稱), ...]。"""
    return sorted({(int(行), 名稱) for 行, 名稱 in re.findall(r"第\\s*(\\d+)\\s*行[：:]\\s*([A-Za-z_]\\w*)", text)})

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

        ## 這本 notebook 在做什麼

        同一句話：「**檢查變數名稱是不是小寫加底線**」，可以放在三個地方：

        | 放法 | 放在哪裡 | 誰來做檢查 |
        | --- | --- | --- |
        | **A** | 寫進手冊（SKILL.md）的文字裡 | AI 每次自己想一遍怎麼檢查 |
        | **B** | 寫成手冊旁邊的小程式 `scripts/check_naming.py`，手冊叫 AI 去執行 | AI 決定要不要跑，檢查本身是 Python |
        | **C** | 寫成 LangGraph 流程裡的一個節點 | 流程一定會跑，AI 根本不經手 |

        三個都做得到。那差在哪？**各跑三次，你自己看。**
        今天的新名詞只有一個：**腳本**（放在手冊 `scripts/` 資料夾裡、真的會執行的小程式）。

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
        2. 每一段：**🤔 先猜哪個版本三次會一樣 → ▶ 執行 → 👀 對照**。
        3. 第 2–4 段的結果會存成檔案，第 5 段把它們並排；跑錯或斷線就從那一段的第一格重跑。
        4. 會花多少 AI：A 每跑一次叫 1 次模型、B 大約 2 次、C 是 0 次。
        """),
        setup(NAME, support=[
            "tools/__init__.py",
            "tools/check_naming.py",
            "skills/naming-check/scripts/check_naming.py",
            "skills/naming-check/SKILL.md",
        ]),
        md("""
        ---
        ## 第 1 段：同一件事，三個地方都能放

        > 📍 **對應簡報**：投影片 14「同一件事，三個地方都能放」、投影片 16「腳本的輸出」

        這一段先看兩樣東西：
        1. 這本 notebook 從頭到尾都用**同一份作業**（下面會印出來，左邊是行號）。
        2. 命名檢查的**腳本** `check_naming.py`：下一格會把它寫進手冊的 `scripts/` 資料夾。
           它只做一件事，輸出短短幾行，像一個小型的命令列工具。
           再下一格是 `tools/check_naming.py`：在腳本外面包一層 `@tool`，它就進了 agent 的工具箱（第 3 段會用到）。

        ### 🤔 預測題
        看印出來的作業：哪幾個名稱不是「小寫英文加底線」？先數數看有幾個。`MAX` 算不算？函式名稱 `CalcAverage` 算不算？
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
          要不要開例外是人決定的；一旦寫進腳本，每次都一樣。
        - 輸出只有幾行、每行一個問題：AI 讀得懂，人也讀得懂。這就是腳本的原則：一個腳本只做一件事、輸出要短。
        """),
        md("""
        ---
        ## 第 2 段：放法 A：寫進手冊文字

        > 📍 **對應簡報**：投影片 15「放法 A：寫進手冊文字」

        下一格把手冊 `skills/naming-check/SKILL.md` 寫成「文字版」：只有一句「請檢查每個變數名稱是否為小寫英文加底線，列出不符合的。」
        再下一格讓 AI 讀這本手冊、檢查同一份作業，**連續跑三次**。

        ### 🤔 預測題
        三次抓到的數量會一樣嗎？會跟第 1 段腳本抓到的 6 個一樣嗎？
        """),
        writefile("skills/naming-check/SKILL.version-a.md", dest="skills/naming-check/SKILL.md"),
        code(_run("""
        #@title ▶ 執行：放法 A，同一份作業跑三次（AI 自己檢查）
        {PREAMBLE}
        {HELPERS}
        from langchain_core.messages import HumanMessage, SystemMessage

        手冊 = 讀手冊內文(BASE / "skills" / "naming-check" / "SKILL.md")
        print("AI 讀到的手冊內文：\\n" + 手冊 + "\\n")
        作業 = 範例作業["命名不一致"]

        計數器 = 模型呼叫計數器()
        三次 = []
        for i in range(1, 4):
            回答 = model.invoke(
                [SystemMessage(手冊), HumanMessage(f"請檢查這份作業：\\n```python\\n{作業}```")],
                config={"callbacks": [計數器]},
            ).text
            結果 = 抓出名稱(回答)
            三次.append(結果)
            print(f"第 {i} 次：抓到 {len(結果)} 個 → " + ("、".join(f"第{行}行 {名}" for 行, 名 in 結果) or "（沒抓到）"))

        一樣 = all(x == 三次[0] for x in 三次)
        print(f"\\n三次一樣嗎？{'✅ 一樣' if 一樣 else '❌ 不一樣'}；總共呼叫了 AI {計數器.次數} 次")
        存結果("A", {"三次": 三次, "AI呼叫": 計數器.次數})
        記下("2-B 第 2 段：放法 A（寫在手冊文字裡）", {"三次": 三次, "三次一樣": 一樣, "AI呼叫": 計數器.次數})
        """)),
        md("""
        ### 👀 你看到了什麼

        - 三次抓到的數量常常不一樣：有一次漏了 `MAX`、有一次把函式名稱 `CalcAverage` 當成不算變數、有一次多抓或寫錯行號。
          **AI 每次都自己想一遍怎麼檢查。想三次，結果三種。**
        - 如果你這次剛好三次都一樣，再執行一次這一格，或仔細比對行號和抓到的名稱；多跑幾次幾乎一定會飄。
        - 而且它跟腳本的 6 個不一定對得上：規則寫在文字裡，「什麼算變數」「常數算不算」都要 AI 自己判斷。
        """),
        md("""
        ---
        ## 第 3 段：放法 B：寫成小程式，手冊叫 AI 去執行

        > 📍 **對應簡報**：投影片 16「放法 B：寫成小程式，手冊叫 AI 去執行」

        下一格把同一本手冊改寫成「腳本版」：「執行 `scripts/check_naming.py`（工具名稱 `check_naming`），把它的輸出寫進回饋。」
        再下一格做一個 agent：手冊當 system prompt，工具箱裡只有 `check_naming` 這一把（就是第 1 段包好的腳本），一樣**跑三次**。

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
        三次 = []
        for i in range(1, 4):
            result = 小助教.invoke(
                {"messages": [{"role": "user", "content": f"請檢查這份作業：\\n```python\\n{作業}```"}]},
                config={"callbacks": [計數器]},
            )
            msgs = result["messages"]
            用了 = [c["name"] for m in msgs for c in (getattr(m, "tool_calls", None) or [])]
            腳本輸出 = [m.text for m in msgs if m.type == "tool"]
            結果 = 抓出名稱(msgs[-1].text)
            三次.append(結果)
            print(f"========== 第 {i} 次 ==========")
            print("AI 用的工具：", "、".join(用了) or "（沒有用工具，自己判斷）")
            if 腳本輸出:
                print("腳本回傳：\\n" + 腳本輸出[0])
            print(f"AI 最後的回覆抓到 {len(結果)} 個 → " + ("、".join(f"第{行}行 {名}" for 行, 名 in 結果) or "（沒抓到）"))
            print()

        一樣 = all(x == 三次[0] for x in 三次)
        print(f"三次一樣嗎？{'✅ 一樣' if 一樣 else '❌ 不一樣'}；總共呼叫了 AI {計數器.次數} 次")
        存結果("B", {"三次": 三次, "AI呼叫": 計數器.次數})
        記下("2-B 第 3 段：放法 B（寫成腳本）", {"三次": 三次, "三次一樣": 一樣, "AI呼叫": 計數器.次數})
        """)),
        md("""
        ### 👀 你看到了什麼

        - 三次抓到的都是同樣的 6 個，跟第 1 段腳本的輸出一模一樣。
        - AI 不再自己想怎麼檢查，它只做兩件事：**決定要跑這個工具**、**把結果抄進回覆**。檢查本身是 Python，每次一樣。
        - 但「要不要跑」還是 AI 決定的：如果某一次它沒叫工具、自己判斷，那一次就會跟其他次不一樣。下一段的放法 C 就沒有這個問題。
        - 每次大約要叫 2 次 AI（一次決定叫工具、一次寫回覆）。
        """),
        md("""
        ---
        ## 第 4 段：放法 C：寫成 LangGraph 節點，AI 根本不經手

        > 📍 **對應簡報**：投影片 17「放法 C：寫成 LangGraph 節點，AI 根本不經手」

        這一版沒有手冊、也沒有 agent：流程只有一個節點 `check_naming`，它直接呼叫同一支腳本，把結果寫進 State 的 `naming_problems`。
        就像第 1 堂 1-A 的 `check_syntax`：流程走到這裡，就一定會檢查。

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

        - 三次完全一樣，而且**呼叫 AI 0 次**：沒花到任何 token，也不用等模型。
        - B 和 C 的結果一樣，差在：**B 是 AI「決定」要跑，C 是流程「強迫」一定跑。**
          這件事能不能漏掉，決定你選 B 還是 C。
        """),
        md("""
        ---
        ## 第 5 段：三個版本並排

        > 📍 **對應簡報**：投影片 17（B 和 C 的差別）、投影片 18「本堂口訣」

        這一格把第 2–4 段存下來的結果並排。還沒跑過的版本會提醒你先回去跑。

        ### 🤔 預測題
        哪一個版本最穩？哪一個最省 AI？如果 B 和 C 結果一樣，你會選哪一個？
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
        列 = ["| 版本 | 三次各抓到幾個 | 三次一樣嗎 | 花了幾次 AI |", "| --- | --- | --- | --- |"]
        for 版本, (名稱, 段落) in 說明.items():
            if 版本 not in 全部:
                列.append(f"| {名稱} | （還沒跑：先跑{段落}） | | |")
                continue
            三次 = 全部[版本]["三次"]
            數量 = "、".join(str(len(x)) for x in 三次)
            一樣 = "✅ 一樣" if all(x == 三次[0] for x in 三次) else "❌ 不一樣"
            列.append(f"| {名稱} | {數量} | {一樣} | {全部[版本]['AI呼叫']} |")
        display(Markdown("\\n".join(列)))
        記下("2-B 第 5 段：三個版本並排", 全部)
        """),
        md("""
        ### 👀 你看到了什麼

        - **A** 最容易飄、而且每次都要花 AI；**B** 和 **C** 三次都一樣，因為檢查本身是程式。
        - **C** 完全不花 AI，而且一定會跑；**B** 要花 AI，但好處是 AI 可以視情況決定要不要用（例如作業根本沒有變數時）。

        ### 📌 本堂口訣

        > **能寫成 if 的，寫進程式。**
        > **要靠經驗判斷的，寫進手冊文字。**
        > **重複又怕出錯的，寫成腳本。**

        今天剩下所有東西，都是這三句的延伸。
        """),
        md("""
        ---
        ## 第 6 段：停一下：五件事各放哪？

        > 📍 **對應簡報**：投影片 19「停一下：五件事各放哪？」

        在紙上寫「**程式／手冊／腳本**」。對答案時只問一個問題：「這件事能不能寫成 if？」
        能，就是程式；不能，再問「每次做法會不會不一樣」。

        | 這件事 | 你的答案 |
        | --- | --- |
        | 1. 回饋用什麼語氣 | ＿＿＿＿ |
        | 2. 執行作業看輸出 | ＿＿＿＿ |
        | 3. 最多重寫三次 | ＿＿＿＿ |
        | 4. 檢查有沒有寫註解 | ＿＿＿＿ |
        | 5. 判斷邏輯寫得好不好 | ＿＿＿＿ |

        <details>
        <summary>寫完再點開看參考答案</summary>

        | 這件事 | 放哪裡 | 為什麼 |
        | --- | --- | --- |
        | 1. 回饋用什麼語氣 | **手冊** | 「溫和」沒有 if，需要判斷，交給 AI 讀手冊 |
        | 2. 執行作業看輸出 | **腳本／工具** | 執行本身是固定的程式（`run_code`），每次一樣；要不要執行可以交給 AI 決定 |
        | 3. 最多重寫三次 | **程式** | `retries >= 3` 就停，能寫成 if，而且不能漏，不然會無限轉圈 |
        | 4. 檢查有沒有寫註解 | **腳本**（一定不能漏就做成**流程節點**） | 有沒有 `#` 能用程式判斷，AI 自己檢查會飄；跟命名檢查是同一種事 |
        | 5. 判斷邏輯寫得好不好 | **手冊** | 沒有標準答案，要靠經驗判斷，把判斷標準寫成文字交給 AI |

        </details>
        """),
        *ending(),
    ]
