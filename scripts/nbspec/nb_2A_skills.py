from nbbuild import RB, badge, code, ending, md, my_homework, project_intro, setup, writefile

NAME = "2-A_skills"
作業選項 = '["變數打錯字", "正確的程式", "縮排亂掉", "命名不一致", "我的作業"]'
需求選項 = '["幫第一次交作業的初學者看看", "期中考正式評分，請嚴格審查"] {allow-input: true}'
兩本手冊 = '["friendly-feedback", "strict-review"]'


def _feedback_cell(title: str, mode: str):
    需求表單 = f'批改需求 = "幫第一次交作業的初學者看看"  #@param {需求選項}' if mode == "選手冊" else '#@markdown 本實驗固定使用「幫第一次交作業的初學者看看」，不用改需求。'
    return code(f"""
    #@title ▶ 實驗 {title}
    {需求表單}
    {{PREAMBLE}}
    from langchain_core.messages import HumanMessage, SystemMessage
    import skill_loader
    實驗模式 = {mode!r}
    if 實驗模式 != "選手冊":
        批改需求 = "幫第一次交作業的初學者看看"
    名片們 = skill_loader.列出名片({兩本手冊})
    if len(名片們) != 2:
        raise SystemExit("請先執行本實驗前的兩本手冊文字格，或本段的恢復預設。")
    print("本次需求：", 批改需求)
    print("固定作業：變數打錯字")
    for c in 名片們:
        print(f"名片 {{c['name']}}：{{c['description']}}")
    if 實驗模式 == "固定手冊":
        選中 = next(c for c in 名片們 if c["name"] == "friendly-feedback")
        print("本實驗由程式固定手冊，沒有讓模型重新挑選。")
    else:
        選中 = skill_loader.挑手冊(model, 批改需求, 名片們)
    手冊內文 = skill_loader.讀內文(選中)
    print("選中的手冊：", 選中["name"])
    print("本次讀到的規則：\\n" + 手冊內文)
    回饋 = model.invoke([SystemMessage(手冊內文), HumanMessage(
        f"請批改這份作業：\\n```python\\n{{取得作業('變數打錯字')}}\\n```"
    )]).text
    print("回饋：\\n" + 回饋)
    if 實驗模式 == "固定手冊":
        print("回饋是否以指定句結尾：", 回饋.strip().rstrip("。.!！").endswith("下一步：請再測試一次"))
    記下(f"2-A 實驗 {{實驗模式}}", {{"需求": 批改需求, "選中": 選中["name"], "內文": 手冊內文, "回饋": 回饋}})
    """)


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

        在上一個範例中，這段話寫在程式裡。幹部說「期中要嚴格一點」，你得找到那段文字修改；多種風格也會變得不好維護。
        有沒有辦法**程式不動、只換一張紙**？

        答案是 **Skill**：一個資料夾，裡面一份 `SKILL.md` 文字檔，寫著做某件事的方法，就像給新同事的**工作手冊**。
        程式把手冊提供給 AI，讓它依據其中的規則產生回饋，Python 一行都不用改。

        這本先掌握兩個名詞：**Skill（手冊）** 和 **名片（description）**。

        | 段落 | 你會做什麼 | 對應投影片 |
        | --- | --- | --- |
        | 第 1 段 | 寫出兩本手冊「溫和鼓勵」「嚴格審查」，看書架上的名片 | 6–8 |
        | 第 2 段 | 三個控制條件的實驗：選手冊、改規則、換名片 | 9–11 |
        | 第 3 段（課後選讀） | 下載一份 Anthropic 官方的 Skill 來拆解：名片、內文、附錄 | 12 |

        ## 怎麼用

        1. 先執行 **「0. 環境設定」**。
        2. 這本要改的是**SKILL.md 文字格**（每個實驗有自己的格子）和表單欄位。改完手冊那格，**記得再執行一次那一格**才會存檔。
        3. 每一段：**🤔 先寫預測 → ▶ 執行 → 👀 對照**；重跑時先確認環境仍在，再依各實驗的準備步驟操作。
        4. 小提醒：重跑「0. 環境設定」不會動到你的手冊；但執行階段被刪除或重建後，`/content/` 裡的檔案會遺失，要再執行一次手冊那兩格。
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

        預測題會用到兩個詞：**token** 是 AI 讀字的單位（字與 token 並非固定比例，依模型與內容不同）；
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
          全部攤開會增加 context 的用量，只放名片就輕鬆很多。這叫**漸進式揭露**：名片 → 內文 → 附錄，需要才翻。
        - 你剛才沒有改任何一行 Python，只寫了兩個文字檔，就多了兩種「回饋風格」可以選。
        """),
        md("""
        ---
        ## 第 2 段（必做）：三個實驗，一次只改一件事

        > 📍 **對應簡報**：投影片 9–11（手冊選擇與動手實驗）

        | 實驗 | 固定的條件 | 唯一改變 | 看哪裡 |
        | --- | --- | --- | --- |
        | A：選手冊 | 同一份作業、兩本預設手冊 | 批改需求 | 選中的手冊名稱 |
        | B：改做法 | 同一份作業、初學者需求、固定用溫和手冊 | 手冊的一條規則 | 回饋有沒有指定結尾句 |
        | C：改選擇條件 | 同一份作業、初學者需求、原本內文 | 兩本 description | 選中了哪本、讀到什麼規則 |

        每次執行只觀察一個差別。**A 先跑兩種需求，再做 B；C 是時間足夠時的進一步實驗。**
        下方的「恢復預設」只重設 Colab 裡的兩份手冊檔案，不會改 notebook 文字格；需要保留修改時先下載。
        """),
        code(f"""
        #@title ↺ 恢復兩本手冊的預設內容（重新開始實驗時執行）
        {{PREAMBLE}}
        預設手冊 = { {name: (RB / "skills" / name / "SKILL.md").read_text(encoding="utf-8") for name in ["friendly-feedback", "strict-review"]}!r}
        for name, text in 預設手冊.items():
            (BASE / "skills" / name / "SKILL.md").write_text(text, encoding="utf-8")
        print("✅ 已恢復兩本手冊。實驗 A 可直接執行；實驗 B 請修改下面專用的文字格。")
        """),
        md("""
        ### 實驗 A：只改需求，觀察選擇（必做）

        先用「初學者」執行，再只把需求改成「期中考」執行。兩本手冊都保持預設。
        **先猜：哪一本更符合需求？** 執行後先找「選中的手冊」，再讀回饋。
        """),
        _feedback_cell("A：只改需求，讓模型選手冊", "選手冊"),
        md("""
        ### 👀 你看到了什麼

        記下兩次選中的手冊。模型依據名片選擇，結果不保證每次相同；若和預測不同，先比對它看到的兩張名片。
        **工具說明與 Skill 名片的共同作用，是交代用途與使用時機。**

        ### 實驗 B：只改規則，觀察回饋（必做）

        下面是本實驗專用的溫和手冊。先原樣執行，再執行回饋格，保留一次基準。
        接著只把規則第 3 條改成：**回饋最後加上「下一步：請再測試一次」。**
        執行手冊那格存檔，再執行回饋格。其他規則不動。

        **先猜：手冊選擇不變時，回饋會多出什麼？**
        本實驗固定「初學者」需求，並由程式指定溫和手冊，暫時排除選錯手冊的影響。
        """),
        writefile("skills/friendly-feedback/SKILL.md"),
        _feedback_cell("B：固定溫和手冊，比較修改前後", "固定手冊"),
        md("""
        ### 👀 你看到了什麼

        先確認印出的手冊內文真的包含新規則，再檢查回饋。若檔案沒變，請先執行剛修改的文字格。
        若內文有新規則、回饋卻沒有指定句子，請記錄「這次未遵守」，不用重跑到符合為止。
        完成標準：指出改了哪一條規則，並用修改前後的輸出說明結果。

        ### 實驗 C：恢復內文，只交換名片（進一步實驗）

        下面兩格是獨立的預設手冊，不會沿用 B 的結尾句。先原樣執行兩格和回饋格，取得基準。
        再**只交換兩格的 description 值**，name 和內文都不改；重新執行兩格存檔，再執行回饋格。
        需求固定為「初學者」。**先猜：這次選中哪一本？選中的名片與內文是否相符？**
        """),
        writefile("skills/friendly-feedback/SKILL.md"),
        writefile("skills/strict-review/SKILL.md"),
        _feedback_cell("C：固定初學者需求，只比較名片", "比較名片"),
        md("""
        ### 👀 你看到了什麼

        對照「需求、兩張名片、選中名稱、讀到的內文、回饋」五項證據。
        交換名片後，模型可能選到內文較嚴格的手冊；若沒有改選，也如實記錄，討論名稱與說明的線索。
        這裡用程式實作「先選名片，再讀內文」，並非所有 agent 都會自動讀取任意資料夾。
        做完可執行本段最前面的「恢復預設」。下一本 notebook 會準備自己的講師預設檔案，不會自動匯入本次修改。
        """),
        md("""
        ---
        ## 第 3 段（課後選讀）：拆解一份官方的 Skill

        > 📍 **對應簡報**：投影片 12「手冊的附件：腳本與參考資料」

        前兩段的手冊都只有一個 `SKILL.md`。真實世界的手冊還可以附別的檔案：

        ```
        某本手冊/
        ├── SKILL.md          ← 手冊本體（名片 ＋ 內文）
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
        #@title ▶ 執行：下載官方 Skill，拆成名片、內文、附錄
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
        print("① 名片（挑選時提供給模型）")
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

        - **名片**：官方手冊的 description 很長，而且明確寫了「什麼時候該用這本手冊」（狀態報告、公司電子報、FAQ……）。
          寫得越清楚，AI 越知道什麼時候該翻開它。
        - **內文**：步驟寫得像給新同事的 SOP：先判斷是哪一種公告 → 打開對應的範例檔 → 照範例的格式寫。
        - **附錄**：`examples/` 裡有四份範例，內文裡寫著「哪種情況打開哪一份」。AI 只有在真的要寫那種公告時才打開，平常不佔桌子。
          這就是三層的**漸進式揭露**：名片約 100 token 一直在桌上，內文建議 5,000 token 以內，附錄需要才讀。
        - Skill 是開放標準：不同支援工具可共用這種手冊結構；放置位置、發現與執行方式仍依工具而異。
        - 下一本 **2-B** 會用到手冊附的 `scripts/`：把「每次都要一模一樣」的檢查寫成小程式，叫 AI 執行它。
        """),
        *ending(),
    ]
