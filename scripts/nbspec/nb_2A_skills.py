from nbbuild import badge, code, ending, md, my_homework, project_intro, setup, writefile

NAME = "2-A_skills"
作業選項 = '["變數打錯字", "正確的程式", "縮排亂掉", "命名不一致", "我的作業"]'
需求選項 = '["幫第一次交作業的初學者看看", "期中考正式評分，請嚴格審查"] {allow-input: true}'
兩本手冊 = '["friendly-feedback", "strict-review"]'


def cells():
    return [
        md(f"""
        # 2-A：Skill 是給 AI 的工作手冊

        {badge(NAME)}

        > 📍 **對應簡報**：第 2 堂「第一站：Skill 工作手冊」，投影片 **5–12**（課堂時間 0:08–0:28）
        """),
        project_intro("把回饋的語氣和規則寫成一本給 AI 看的手冊（Skill）：程式一行不動，換一本手冊就能換風格。"),
        md("""
        ## 這本 notebook 在做什麼

        小助教「寫回饋」這一步是交給 AI 做的。要 AI 用什麼語氣、照什麼規矩寫，最直接的做法是寫在 **system prompt** 裡：
        system prompt 是每次問 AI 時都放在最前面的一段話，告訴它「你是誰、要遵守什麼」，例如「你是 Python 作業小助教，語氣要溫和」。

        麻煩的是，這段話寫死在程式裡。幹部說「期中要嚴格一點」，你就得改程式、重跑；想要十種風格就得改十次。
        有沒有辦法**程式不動、只換一張紙**？

        答案是 **Skill**：一個資料夾，裡面一份 `SKILL.md` 文字檔，寫著做某件事的方法，就像給新同事的**工作手冊**。
        AI 讀了手冊，行為就跟著變，Python 一行都不用改。

        這本的新名詞只有兩個：**Skill（手冊）** 和 **名片（description）**。

        | 段落 | 你會做什麼 | 對應投影片 |
        | --- | --- | --- |
        | 第 1 段 | 寫出兩本手冊「溫和鼓勵」「嚴格審查」，看書架上的名片 | 6–8 |
        | 第 2 段 | AI 看名片挑一本、照手冊給回饋；✏️ 改手冊，看 AI 變臉 | 9–11 |
        | 第 3 段 | 下載一份 Anthropic 官方的 Skill 來拆解：書背、內文、附錄 | 12 |

        ## 怎麼用

        1. 先執行 **「0. 環境設定」**。
        2. 這本要改的是**兩份 SKILL.md 的文字**（第 1 段那兩格）和表單欄位。改完手冊那格，**記得再執行一次那一格**才會存檔。
        3. 每一段：**🤔 先寫預測 → ▶ 執行 → 👀 對照**；跑錯或斷線就從那一段的第一格重跑。
        4. 小提醒：重跑「0. 環境設定」不會動到你的手冊；但 Colab 斷線後 `/content/` 會清空，要再執行一次手冊那兩格。
        """),
        setup(NAME, support=["skill_loader.py"]),
        *my_homework(),
        md("""
        ---
        ## 第 1 段：手冊長這樣，書架上只看得到名片

        > 📍 **對應簡報**：投影片 6「上週留下的麻煩」、投影片 7「新同事報到時，你會做什麼？」、投影片 8「手冊長這樣」

        開頭說了為什麼需要手冊，這一段先看手冊長什麼樣子。一份 `SKILL.md` 分兩部分：

        ```markdown
        ---
        name: friendly-feedback                      ← 名片：只有兩格
        description: 給 Python 初學者的作業回饋……   ←（做什麼、什麼時候用）
        ---

        # 溫和回饋規則                                ← 手冊內容：怎麼做這件事
        1. 先講一個做得好的地方
        ```

        - **名片**：兩條 `---` 之間。`name` 是手冊的名字（只能用小寫英文、數字、連字號，最多 64 字元）；`description` 說這本手冊**做什麼、什麼時候用**。
        - **手冊內容**：名片下面，寫給人看也看得懂的步驟。

        下面兩格是兩本手冊「溫和鼓勵」和「嚴格審查」。**第 2 段會請你改它們**，現在先直接執行。
        第三格寫出 `skill_loader.py`：負責讀名片、挑手冊（不用改）。

        預測題會用到兩個詞：**token** 是 AI 讀字的單位（中文大約一兩個字算一個 token）；
        AI 一次能讀的 token 有上限，我們把它想成一張**桌子**（正式名稱是 context window），東西放太多就擺不下。

        ### 🤔 預測題
        1. AI 要挑手冊的時候，看得到手冊的「內容」嗎？還是只看得到名片？
        2. 名片和內文，哪個比較佔桌子（token）？
        """),
        writefile("skills/friendly-feedback/SKILL.md"),
        writefile("skills/strict-review/SKILL.md"),
        writefile("skill_loader.py"),
        code(f"""
        #@title ▶ 執行：看看書架上有哪些名片
        {{PREAMBLE}}
        import skill_loader

        名片們 = skill_loader.列出名片({兩本手冊})
        名片_總 = 內文_總 = 0
        for c in 名片們:
            內文 = skill_loader.讀內文(c)
            名片_token = 估算_token(c["name"] + c["description"])
            內文_token = 估算_token(內文)
            名片_總 += 名片_token
            內文_總 += 內文_token
            print(f"📕 name：{{c['name']}}")
            print(f"   description：{{c['description']}}")
            print(f"   名片約 {{名片_token}} token；翻開內文約 {{內文_token}} token\\n")

        print(f"AI 挑書時，桌上只放 {{len(名片們)}} 張名片：約 {{名片_總}} token")
        print(f"如果把每本內文都攤在桌上：約 {{名片_總 + 內文_總}} token")
        print(f"手冊有 50 本的話：只放名片約 {{名片_總 * 25}} token，全部攤開約 {{(名片_總 + 內文_總) * 25}} token（估算）")
        記下("2-A 第 1 段：書架上的名片", {{c["name"]: c["description"] for c in 名片們}})
        """),
        md("""
        ### 👀 你看到了什麼

        - 每本手冊的名片只有短短一兩句；翻開才看得到完整的規則。
        - AI 挑書時**只看名片**，選中了才把內文放上桌。手冊只有兩本時差別不大，但有 50 本時，
          全部攤開會把桌子（context window）塞滿，只放名片就輕鬆很多。這叫**漸進式揭露**：書背 → 內文 → 附錄，需要才翻。
        - 你剛才沒有改任何一行 Python，只寫了兩個文字檔，就多了兩種「個性」可以選。
        """),
        md(f"""
        ---
        ## 第 2 段：AI 看名片挑一本，照手冊給回饋

        > 📍 **對應簡報**：投影片 9「為什麼要有名片：AI 選書只看書背」、投影片 10「AI 只看說明書的第一行」、投影片 11「動手：改手冊，看 AI 變臉」

        上一段看到：AI 挑書時只看得到名片。這一段讓它真的挑一本、照著寫回饋。下一格會做兩件事：
        1. **挑手冊**（`skill_loader.挑手冊`）：把兩張名片和你的「批改需求」交給 AI，請它挑一本。
        2. **照手冊給回饋**：把挑中那本的內文當成 system prompt，請 AI 批改作業。

        這和 AI 挑「工具」的方式一樣：工具（AI 可以呼叫的 Python 函式）靠它的說明文字（docstring）被選中，
        手冊靠名片（description）被翻開。AI 都只看那一兩行，就決定要不要拿起來。

        先用預設值執行一次，再換「期中考正式評分，請嚴格審查」執行一次，看 AI 挑的手冊和回饋語氣有沒有變。

        ### 🤔 停一下（寫在紙上，再改、再執行）
        1. 回到第 1 段，把「溫和鼓勵」手冊的**規則第 3 條**改成 **「每句話都用台語」**，執行那一格存檔，再回來執行下一格。回饋會怎麼變？
        2. 把兩本手冊的 **description 對調**（`friendly-feedback` 的 description 換成嚴格審查那句，反過來也一樣），兩格都執行存檔。
           這次批改需求選「幫第一次交作業的初學者看看」，AI 會挑中哪一本？回饋是溫和還是嚴格？
        """),
        code(f"""
        #@title ▶ 執行：AI 看名片挑一本，再照手冊給回饋
        批改需求 = "幫第一次交作業的初學者看看"  #@param {需求選項}
        作業 = "變數打錯字"  #@param {作業選項}
        {{PREAMBLE}}
        from langchain_core.messages import HumanMessage, SystemMessage
        import skill_loader

        名片們 = skill_loader.列出名片({兩本手冊})
        if len(名片們) < 2:
            raise SystemExit("⚠️ 書架上的手冊不夠兩本：請先執行第 1 段寫出兩份 SKILL.md 的那兩格")

        print("📚 AI 挑書時看到的名片（只有這些）：")
        for c in 名片們:
            print(f"   - {{c['name']}}：{{c['description']}}")

        選中 = skill_loader.挑手冊(model, 批改需求, 名片們)
        print(f"\\n👉 批改需求「{{批改需求}}」→ AI 挑了：{{選中['name']}}")

        手冊內文 = skill_loader.讀內文(選中)     # 選中了才翻開內文
        print("\\n📖 翻開的手冊內文：")
        print(手冊內文)

        code = 取得作業(作業)
        回饋 = model.invoke([
            SystemMessage(手冊內文),
            HumanMessage(f"請批改這份作業：\\n```python\\n{{code}}\\n```"),
        ]).text
        print("\\n📝 AI 照手冊寫的回饋：")
        print(回饋)
        記下(f"2-A 第 2 段：{{批改需求}} → {{選中['name']}}", {{"批改需求": 批改需求, "挑中的手冊": 選中["name"],
                                                       "手冊內文": 手冊內文, "回饋": 回饋}})
        """),
        md("""
        ### 👀 你看到了什麼

        - 批改需求說「初學者」，AI 挑溫和鼓勵；說「期中考、嚴格」，AI 挑嚴格審查。**它是看名片上的字決定的**，不是看內文。
        - **停一下 1（改規則第 3 條）**：回饋的語氣跟著變了（可能真的冒出台語）。你只改了文字檔，Python 一行都沒動。
          這就是開頭那個麻煩的答案：個性不用寫死在程式裡，換一本手冊就好。
        - **停一下 2（對調 description）**：AI 會挑到**名片寫著「初學者」的那本**，也就是現在掛著溫和名片的 `strict-review`，
          翻開後卻是嚴格的規則，所以回饋變得很兇。AI 選書只看書背；名片寫錯，對的手冊永遠不會被翻開。
        - 📝 最低完成標準：改過一次 SKILL.md，並看到回饋改變。做到了就截圖最後一格的 State 歷程。
        - 實驗完記得把 description 換回來（或重新開一份 notebook），不然後面會一直挑錯。
        """),
        md("""
        ---
        ## 第 3 段：拆解一份官方的 Skill

        > 📍 **對應簡報**：投影片 12「順便一提：手冊可以附東西」

        前兩段的手冊都只有一個 `SKILL.md`。真實世界的手冊還可以附別的檔案：

        ```
        某本手冊/
        ├── SKILL.md          ← 手冊本體（書背 ＋ 內文）
        ├── scripts/          ← 可以執行的小程式（下一本 2-B 會用到）
        └── references/ 或 examples/  ← 太長的參考資料，需要才翻
        ```

        下一格會從網路下載 Anthropic 官方 skills repo 裡的一份真實 Skill：`internal-comms`（寫公司內部公告用的手冊，Apache-2.0 授權），
        把它拆成三層給你看。連不上網路的話，會改拆解我們自己的 `friendly-feedback`。

        ### 🤔 預測題
        1. 官方手冊的 description 有沒有寫「**什麼時候用**」？
        2. 它附的 `examples/` 資料夾裡的檔案，AI 什麼時候才會打開？
        """),
        code("""
        #@title ▶ 執行：下載官方 Skill，拆成書背、內文、附錄
        {PREAMBLE}
        import json
        import urllib.request

        網址 = "https://raw.githubusercontent.com/anthropics/skills/main/skills/internal-comms/SKILL.md"
        附錄網址 = "https://api.github.com/repos/anthropics/skills/contents/skills/internal-comms/examples"
        備用附錄 = ["3p-updates.md", "company-newsletter.md", "faq-answers.md", "general-comms.md"]

        try:
            with urllib.request.urlopen(網址, timeout=10) as r:
                text = r.read().decode("utf-8")
            來源 = "Anthropic 官方 skills repo：skills/internal-comms（Apache-2.0）"
            try:
                with urllib.request.urlopen(附錄網址, timeout=10) as r:
                    附錄 = [f["name"] for f in json.load(r)]
            except Exception:
                附錄 = 備用附錄
        except Exception as e:
            print(f"⚠️ 連不上 GitHub（{type(e).__name__}），改拆解我們自己的 friendly-feedback\\n")
            text = (BASE / "skills" / "friendly-feedback" / "SKILL.md").read_text(encoding="utf-8")
            來源 = "review-bot/skills/friendly-feedback"
            附錄 = []

        _, 頭, 內文 = text.split("---", 2)
        名片 = {}
        for line in 頭.strip().splitlines():
            key, _, value = line.partition(":")
            名片[key.strip()] = value.strip()

        print(f"來源：{來源}\\n")
        print("① 書背（名片，一直放在桌上）")
        for key, value in 名片.items():
            print(f"   {key}: {value}")
        print(f"   → 約 {估算_token(頭)} token\\n")

        print("② 內文（被選中才翻開），前 12 行：")
        for line in 內文.strip().splitlines()[:12]:
            print(f"   {line}")
        print(f"   …（內文共 {len(內文.strip().splitlines())} 行，約 {估算_token(內文)} token）\\n")

        print("③ 附錄（內文叫它打開才打開）：")
        for name in 附錄:
            提到 = "（內文裡有提到）" if name in 內文 else ""
            print(f"   examples/{name} {提到}")
        if not 附錄:
            print("   （這本沒有附錄）")
        記下("2-A 第 3 段：拆解 Skill", {"來源": 來源, "名片": 名片, "內文行數": len(內文.strip().splitlines()), "附錄": 附錄})
        """),
        md("""
        ### 👀 你看到了什麼

        - **書背**：官方手冊的 description 很長，而且明確寫了「什麼時候該用這本手冊」（狀態報告、公司電子報、FAQ……）。
          寫得越清楚，AI 越知道什麼時候該翻開它。
        - **內文**：步驟寫得像給新同事的 SOP：先判斷是哪一種公告 → 打開對應的範例檔 → 照範例的格式寫。
        - **附錄**：`examples/` 裡有四份範例，內文裡寫著「哪種情況打開哪一份」。AI 只有在真的要寫那種公告時才打開，平常不佔桌子。
          這就是三層的**漸進式揭露**：書背約 100 token 一直在桌上，內文建議 5,000 token 以內，附錄需要才讀。
        - Skill 是開放標準：同一個資料夾放進 Claude Code、Codex、Cursor、Gemini CLI 的 skills 資料夾都讀得懂。
        - 下一本 **2-B** 會用到手冊附的 `scripts/`：把「每次都要一模一樣」的檢查寫成小程式，叫 AI 執行它。
        """),
        *ending(),
    ]
