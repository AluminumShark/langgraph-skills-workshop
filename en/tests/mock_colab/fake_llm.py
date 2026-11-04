"""A fake model for local verification: it imitates the behavior of google.colab.ai.generate_text.

It is not a real LLM. It only understands the kind of prompt that review-bot/llm.py builds, and answers with fixed rules plus a little randomness:
- When a tool list is present: first call any tool the handbook (system instructions) names; pick randomly among the rest; a call is one line of JSON
- Picking a handbook: compares the review request with the words on each card
- Text-only naming check: randomly misses a few names each time (imitating how "the AI thinks it through again every time" drifts)
- Writing feedback: random length; when the character limit is too small it goes over, which triggers a rejected rewrite
The goal is only to let a notebook run from start to finish on a computer with no network and no API key.
"""

from __future__ import annotations

import json
import random
import re

# keyword in the system prompt (case-insensitive) -> tool to call
_KEYWORD_TO_TOOL = {
    r"assignment requirements": "read_spec",
    r"naming": "check_naming",
    r"syntax": "check_syntax",
    r"\bkeys?\b": "read_env",
}
_STUDENTS = "Alex|Ben|Chloe|Jay|Fiona"
_STOPWORDS = {"a", "an", "the", "of", "to", "and", "or", "in", "on", "for", "is", "are", "be", "it", "my", "me", "with", "this", "that", "i"}


def _blocks(prompt: str) -> list[tuple[str, str]]:
    blocks = []
    for m in re.finditer(r"^=== (.+?) ===\n?(.*?)(?=\n\n=== |\Z)", prompt, re.S | re.M):
        blocks.append((m.group(1), m.group(2).strip()))
    return blocks


def _homework(text: str) -> str:
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.S)
    if m:
        return m.group(1)
    return text.split(":", 1)[-1] if ":" in text else text


def _bad_names(code: str) -> list[tuple[int, str]]:
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


def _feedback(code: str, limit: int | None, rejected: bool, extra: list[str] | None = None) -> str:
    short = "Strengths: Clear structure.\nImprovements: Add a few comments."
    long = (
        "Strengths: The program is well organized, the function names show what each one is for, "
        "and overall it is clear that you thought it through before you started typing.\n"
        "Improvements: Add a one-line comment above each function to say what it does, make the variable names "
        "a little more consistent, and remember to test a few different inputs so you can confirm "
        "that every case gives the correct result."
    )
    if limit is None:
        text = random.choice([short, long])
    elif rejected and limit >= len(short):
        text = short
    else:
        text = long if random.random() < 0.5 or limit < len(short) else short
    if extra:
        head, _, tail = text.partition("\nImprovements: ")
        text = head + "\nImprovements: " + "\n".join(extra) + "\n" + tail
    return text


def generate_text(prompt: str, model_name: str | None = None, stream: bool = False):
    text = _answer(prompt)
    if stream:
        return iter([text])
    return text


def _words(text: str) -> set[str]:
    out = set()
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        if w not in _STOPWORDS:
            out.add(w[:-1] if len(w) > 3 and w.endswith("s") else w)
    return out


def _answer(prompt: str) -> str:
    blocks = _blocks(prompt)
    system = "\n".join(b for t, b in blocks if t == "System instructions")
    users = [b for t, b in blocks if t == "User"]
    user = users[0] if users else prompt
    tool_block = next((b for t, b in blocks if t == "Tools you can use"), None)
    prefix = "Result of tool "
    results = [(t[len(prefix):].strip(), b) for t, b in blocks if t.startswith(prefix)]

    if tool_block is not None:
        return _use_tools(prompt, system, user, tool_block, results)

    if "auditor" in system.lower():   # the 2-E verification agent: usually approves, sometimes rejects
        if random.random() < 0.8:
            return '{"passed": true, "reason": "The problems the feedback mentions really exist, and the format is correct"}'
        return '{"passed": false, "reason": "The feedback does not point out the main problem in the homework"}'

    if "Answer with only the handbook's name" in prompt:
        m = re.search(r"Review request: (.*)", prompt)
        request = m.group(1) if m else ""
        cards = re.findall(r"^- ([a-z0-9-]+): (.*)$", prompt, re.M)
        request_words = _words(request)

        def score(desc):
            return len(request_words & _words(desc)) + random.random() * 0.5
        return max(cards, key=lambda c: score(c[1]))[0] if cards else "friendly-feedback"

    if "list every name that breaks the rule" in prompt:
        names = _bad_names(_homework(user if users else prompt))
        picked = [n for n in names if random.random() > 0.3]
        return "\n".join(f"Line {i}: {n}" for i, n in picked) or "No problems found"

    m = re.search(r"at most (\d+) characters", prompt)
    if "Strengths:" in prompt and "feedback" in prompt.lower():
        return _feedback(_homework(user), int(m.group(1)) if m else None, "was rejected" in prompt)

    if "What is my name?" in prompt:
        return "Your name is Alice." if "Alice" in prompt else "I don't know your name. I'm an AI and can't remember personal details."
    if "in three words" in prompt.lower():
        return "A programming language."
    return "(Fake model) OK, I am a fake model for local testing, and this is a fixed reply."


def _use_tools(prompt, system, user, tool_block, results) -> str:
    tools = re.findall(r"^- ([A-Za-z_]\w*)\(([^)]*)\): ", tool_block, re.M)
    names = [n for n, _ in tools]
    params = {n: [p.split(":")[0].strip() for p in ps.split(",") if p.strip()] for n, ps in tools}
    called = [n for n, _ in results]
    code = _homework(user)
    fetched = [b for n, b in results if n == "get_homework" and not b.startswith("No homework found")]
    if fetched:   # the homework came from MCP: later tools run that homework
        code = fetched[-1]

    def call(name):
        args = {}
        for p in params.get(name, []):
            if p == "code":
                args[p] = code
            elif p == "student":
                found = re.findall(rf"\b({_STUDENTS})\b", user)
                args[p] = found[0] if found else "Alex"
            elif p == "name":
                env = re.findall(r"\b([A-Z][A-Z0-9_]*KEY[A-Z0-9_]*)\b", system)
                args[p] = env[0] if env else "HOME"
            else:
                args[p] = ""
        return json.dumps({"tool_calls": [{"name": name, "args": args}]}, ensure_ascii=False)

    if "always_fail" in names:
        return call("always_fail")

    low = system.lower()
    named = [n for n in names if n in system]
    named += [tool for kw, tool in _KEYWORD_TO_TOOL.items() if re.search(kw, low) and tool in names]
    for n in sorted(set(named), key=lambda n: system.find(n) if n in system else 999):
        if n not in called:
            return call(n)

    unused = [n for n in names if n not in called]
    if unused and (not called and random.random() < 0.9 or called and random.random() < 0.4):
        return call(random.choice(unused))

    extra = []
    for name, result in results:
        if name == "read_env":
            extra.insert(0, f"(Environment check: {result})")
        if name == "check_naming":
            extra += [line.split(" breaks the rule")[0] for line in result.splitlines() if line.startswith("Line ")]
    m = re.search(r"at most (\d+) characters", system)
    text = _feedback(code, int(m.group(1)) if m else None, "was rejected" in system, [x for x in extra if x.startswith("Line ")])
    leak = [x for x in extra if not x.startswith("Line ")]
    return "\n".join(leak + [text])
