"""1-A：作業小助教的 workflow，路線由程式決定。

START → check_syntax ─語法 OK→ give_feedback → check_format ─格式 OK 或達上限→ END
                     └語法錯→ explain_error → END     └不合格、retries 還沒到上限→ 退回 give_feedback

三個零件：
- State：一張訂單紙（dict），從頭傳到尾
- Node ：一個工作站（函式），收 State、只回傳自己改的那幾格
- Edge ：工作站之間的箭頭；條件邊就是一個回傳「下一站名字」的 if
"""

import ast
import re
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict, total=False):
    code: str              # 學生交的作業
    syntax_ok: bool | None # 語法對不對（還沒檢查時是 None）
    error: str             # 語法錯在哪裡
    feedback: str          # 給學生的回饋
    format_ok: bool | None # 回饋格式合不合格
    format_problem: str    # 不合格的原因（退回重寫時會告訴 AI）
    retries: int           # 已產生回饋的次數，包含第一次


# ---------- Node 1：check_syntax 檢查語法（純 Python）：只看文法對不對，不執行程式 ----------

_錯誤翻譯 = [
    (r"'(.)' was never closed", lambda m: f"少了右括號 {dict(zip('([{', ')]}')).get(m.group(1), '')}"),
    (r"unterminated string literal", lambda m: "字串少了結尾的引號"),
    (r"expected ':'", lambda m: "少了冒號 :"),
    (r"unexpected indent", lambda m: "縮排多了"),
    (r"expected an indented block", lambda m: "這裡需要縮排"),
    (r"unindent does not match", lambda m: "縮排對不齊"),
    (r"unmatched '(.)'", lambda m: f"多了一個 {m.group(1)}"),
    (r"invalid character", lambda m: "有全形或看不懂的字元"),
    (r"Perhaps you forgot a comma", lambda m: "可能少了逗號"),
    (r"invalid syntax", lambda m: "語法不正確"),
]


def 翻譯語法錯誤(msg: str) -> str:
    for pattern, 說法 in _錯誤翻譯:
        m = re.search(pattern, msg)
        if m:
            return 說法(m)
    return msg


def check_syntax(state: State) -> dict:
    code = state.get("code", "")
    if not code.strip():
        return {"syntax_ok": False, "error": "作業是空白的，沒有任何程式"}
    try:
        ast.parse(code)
    except SyntaxError as e:
        return {"syntax_ok": False, "error": f"第 {e.lineno} 行{翻譯語法錯誤(e.msg)}"}
    return {"syntax_ok": True, "error": ""}


# ---------- 條件邊 1：語法對 → 寫回饋；語法錯 → 解釋錯誤（就是一個 if） ----------

def route_after_syntax(state: State) -> str:
    if state["syntax_ok"]:
        return "give_feedback"
    return "explain_error"


# ---------- Node 2：explain_error 解釋錯誤（純 Python）：一句話說錯在第幾行 ----------

def explain_error(state: State) -> dict:
    return {"feedback": f"語法：{state['error']}\n改進：先把這一行修好，再執行一次看看。"}


# ---------- Node 3：give_feedback 寫回饋（兩個版本：固定文字／交給 AI） ----------

def give_feedback_固定文字(state: State) -> dict:
    """先不接 AI 的版本：回固定的一段話。"""
    return {
        "feedback": "優點：這份作業通過語法檢查。\n改進：（這一版還沒接 AI，尚未檢查執行結果與邏輯）",
        "retries": state.get("retries", 0) + 1,
    }


def 建立_give_feedback(model, 回饋字數上限: int):
    """接上 AI 的版本：AI 只是住在這個節點裡的一行程式。"""

    def give_feedback(state: State) -> dict:
        prompt = (
            "你是 Python 作業小助教，請用繁體中文給下面這段作業回饋。\n"
            "格式規定（一定要遵守）：\n"
            "- 只寫兩段：第一段以「優點：」開頭，第二段以「改進：」開頭\n"
            f"- 整段回饋（含「優點：」「改進：」與換行）不超過 {回饋字數上限} 個字元\n\n"
            f"作業：\n```python\n{state['code']}\n```"
        )
        if state.get("format_problem"):
            prompt += f"\n\n你上一版的回饋被退回，原因：{state['format_problem']}。請修正後重寫。"
        text = model.invoke(prompt).text
        return {"feedback": text.strip(), "retries": state.get("retries", 0) + 1}

    return give_feedback


# ---------- Node 4：check_format 檢查格式（純 Python 的檢查站）：要有兩段、不能太長 ----------

def 建立_check_format(回饋字數上限: int):
    def check_format(state: State) -> dict:
        feedback = state.get("feedback", "")
        問題 = []
        # 檢查標籤順序與兩段非空內容；接受全形／半形冒號與換行。
        parts = re.fullmatch(r"\s*優點[：:]\s*(.+?)\s*改進[：:]\s*(.+?)\s*", feedback, re.DOTALL)
        if not parts or not all(part.strip() for part in parts.groups()):
            問題.append("需依序寫出「優點：內容」與「改進：內容」兩段")
        if len(feedback) > 回饋字數上限:
            問題.append(f"太長了：{len(feedback)} 字元（含標籤與換行），上限 {回饋字數上限} 字元")
        return {"format_ok": not 問題, "format_problem": "；".join(問題)}

    return check_format


# ---------- 條件邊 2：格式 OK 或回饋產生次數到上限 → 結束；否則退回重寫 ----------

def 建立_route_after_format(最多重試次數: int):
    def route_after_format(state: State) -> str:
        if state["format_ok"]:
            return END
        if state.get("retries", 0) >= 最多重試次數:
            return END  # 已達回饋產生上限；停止不代表格式通過
        return "give_feedback"

    return route_after_format


# ---------- 把零件接起來 ----------

def 建立小助教(model=None, 最多重試次數: int = 3, 回饋字數上限: int = 150):
    """model=None 時用固定文字。最多重試次數是歷史參數名，實際包含第一次產生。"""
    give_feedback = 建立_give_feedback(model, 回饋字數上限) if model else give_feedback_固定文字

    builder = StateGraph(State)
    builder.add_node("check_syntax", check_syntax)
    builder.add_node("explain_error", explain_error)
    builder.add_node("give_feedback", give_feedback)
    builder.add_node("check_format", 建立_check_format(回饋字數上限))

    builder.add_edge(START, "check_syntax")
    builder.add_conditional_edges("check_syntax", route_after_syntax, ["give_feedback", "explain_error"])
    builder.add_edge("explain_error", END)
    builder.add_edge("give_feedback", "check_format")
    builder.add_conditional_edges("check_format", 建立_route_after_format(最多重試次數), ["give_feedback", END])
    return builder.compile()


def 空白訂單紙(code: str) -> State:
    return {"code": code, "syntax_ok": None, "error": "", "feedback": "", "format_ok": None,
            "format_problem": "", "retries": 0}
