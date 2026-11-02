"""本機驗證用的假模型：模仿 google.colab.ai.generate_text 的行為。

它不是真的 LLM，只看得懂 review-bot/llm.py 組出來的那種 prompt，用固定規則加一點亂數回話：
- 有工具清單時：手冊（系統指示）點名的工具先叫；其餘隨機挑；呼叫格式是一行 JSON
- 挑手冊時：比對批改需求和名片的字
- 文字版命名檢查：每次隨機漏掉或多抓幾個（模仿「AI 每次自己想一遍」會飄）
- 寫回饋時：長度隨機，字數上限太小時會超過，觸發退回重寫
目的只是讓 notebook 在沒有網路、沒有 API key 的電腦上也能從頭跑到尾。
"""

from __future__ import annotations

import json
import random
import re

_關鍵字找工具 = {"題目要求": "read_spec", "命名": "check_naming", "語法": "check_syntax", "金鑰": "read_env"}


def _區塊(prompt: str) -> list[tuple[str, str]]:
    blocks = []
    for m in re.finditer(r"【([^】]+)】\n?(.*?)(?=\n\n【|\Z)", prompt, re.S):
        blocks.append((m.group(1), m.group(2).strip()))
    return blocks


def _作業(text: str) -> str:
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.S)
    if m:
        return m.group(1)
    return text.split("：", 1)[-1] if "：" in text else text


def _不合規名稱(code: str) -> list[tuple[int, str]]:
    found, seen = [], set()
    for i, line in enumerate(code.splitlines(), 1):
        names = re.findall(r"^\s*([A-Za-z_]\w*)\s*[+\-*/]?=(?!=)", line)
        for fn, args in re.findall(r"def\s+([A-Za-z_]\w*)\s*\(([^)]*)\)", line):
            names += [fn] + [a.strip() for a in args.split(",") if a.strip()]
        names += re.findall(r"for\s+([A-Za-z_]\w*)\s+in", line)
        for n in names:
            if n not in seen and not re.match(r"^_?[a-z][a-z0-9_]*$", n):
                seen.add(n)
                found.append((i, n))
    return found


def _回饋(code: str, 上限: int | None, 被退回: bool, 額外: list[str] | None = None) -> str:
    short = "優點：程式結構清楚。\n改進：可以再加一點註解。"
    long = (
        "優點：程式結構清楚，函式的名稱也看得出用途，整體來說寫得很用心，看得出有先想過再動手。\n"
        "改進：可以在每個函式上面加一行註解說明它在做什麼，變數名稱也可以再統一一點，"
        "另外記得多測試幾種不同的輸入，確認每一種情況都能得到正確的結果。"
    )
    if 上限 is None:
        text = random.choice([short, long])
    elif 被退回 and 上限 >= len(short):
        text = short
    else:
        text = long if random.random() < 0.5 or 上限 < len(short) else short
    if 額外:
        head, _, tail = text.partition("\n改進：")
        text = head + "\n改進：" + "\n".join(額外) + "\n" + tail
    return text


def generate_text(prompt: str, model_name: str | None = None, stream: bool = False):
    text = _回答(prompt)
    if stream:
        return iter([text])
    return text


def _回答(prompt: str) -> str:
    blocks = _區塊(prompt)
    system = "\n".join(b for t, b in blocks if t == "系統指示")
    users = [b for t, b in blocks if t == "使用者"]
    user = users[0] if users else prompt
    tool_block = next((b for t, b in blocks if t == "你可以用的工具"), None)
    results = [(t[3:-4].strip(), b) for t, b in blocks if t.startswith("工具 ") and t.endswith("的結果")]

    if tool_block is not None:
        return _用工具(prompt, system, user, tool_block, results)

    if "稽核員" in system:   # 2-E 的驗證 agent：大多數放行，偶爾退回
        if random.random() < 0.8:
            return '{"通過": true, "原因": "回饋提到的問題都存在，格式正確"}'
        return '{"通過": false, "原因": "回饋沒有指出作業裡最主要的問題"}'

    if "只回答手冊的 name" in prompt:
        需求 = re.search(r"批改需求：(.*)", prompt)
        需求 = 需求.group(1) if 需求 else ""
        cards = re.findall(r"^- ([a-z0-9-]+)：(.*)$", prompt, re.M)
        def 分數(desc):
            bigrams = {需求[i : i + 2] for i in range(len(需求) - 1)}
            return sum(1 for b in bigrams if b in desc) + random.random() * 0.5
        return max(cards, key=lambda c: 分數(c[1]))[0] if cards else "friendly-feedback"

    if "列出不符合的" in prompt:
        names = _不合規名稱(_作業(user if users else prompt))
        picked = [n for n in names if random.random() > 0.3]
        return "\n".join(f"第 {i} 行：{n}" for i, n in picked) or "沒有發現問題"

    m = re.search(r"不超過 (\d+) 個字", prompt)
    if "優點：" in prompt and ("回饋" in prompt):
        return _回饋(_作業(user), int(m.group(1)) if m else None, "被退回" in prompt)

    if "我叫什麼" in prompt:
        return "你叫 Alice。" if "Alice" in prompt else "我不知道你的名字。我是一個 AI，無法記住使用者的個人資訊。"
    if "三個字" in prompt:
        return "程式語"
    return "（假模型）好的，我是本機測試用的假模型，這是一段固定的回覆。"


def _用工具(prompt, system, user, tool_block, results) -> str:
    tools = re.findall(r"^- ([A-Za-z_]\w*)\(([^)]*)\)：", tool_block, re.M)
    names = [n for n, _ in tools]
    params = {n: [p.split(":")[0].strip() for p in ps.split(",") if p.strip()] for n, ps in tools}
    called = [n for n, _ in results]
    code = _作業(user)
    拿到的作業 = [b for n, b in results if n == "get_homework" and not b.startswith("找不到")]
    if 拿到的作業:   # 作業是從 MCP 拿來的：之後的工具就執行那份作業
        code = 拿到的作業[-1]

    def 呼叫(name):
        args = {}
        for p in params.get(name, []):
            if p == "code":
                args[p] = code
            elif p == "student":
                名字 = re.findall(r"(小明|小華|小美|阿傑|小芳)", user)
                args[p] = 名字[0] if 名字 else "小明"
            elif p == "name":
                env = re.findall(r"\b([A-Z][A-Z0-9_]*KEY[A-Z0-9_]*)\b", system)
                args[p] = env[0] if env else "HOME"
            else:
                args[p] = ""
        return json.dumps({"tool_calls": [{"name": name, "args": args}]}, ensure_ascii=False)

    if "always_fail" in names:
        return 呼叫("always_fail")

    點名 = [n for n in names if n in system]
    點名 += [tool for kw, tool in _關鍵字找工具.items() if kw in system and tool in names]
    for n in sorted(set(點名), key=lambda n: system.find(n) if n in system else 999):
        if n not in called:
            return 呼叫(n)

    未用 = [n for n in names if n not in called]
    if 未用 and (not called and random.random() < 0.9 or called and random.random() < 0.4):
        return 呼叫(random.choice(未用))

    額外 = []
    for name, result in results:
        if name == "read_env":
            額外.insert(0, f"（環境確認：{result}）")
        if name == "check_naming":
            額外 += [line.split(" 不符合")[0] for line in result.splitlines() if line.startswith("第 ")]
    m = re.search(r"不超過 (\d+) 個字", system)
    text = _回饋(code, int(m.group(1)) if m else None, "被退回" in system, [x for x in 額外 if x.startswith("第 ")])
    leak = [x for x in 額外 if not x.startswith("第 ")]
    return "\n".join(leak + [text])
