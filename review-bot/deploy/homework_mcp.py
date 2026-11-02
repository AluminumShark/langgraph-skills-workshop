"""作業倉庫 MCP server：工具住在「另一個程式」裡，透過 MCP 插座接進來。

它就是一個普通的 Python 檔，只是函式上面加了 @mcp.tool()。
真實世界裡，這個角色是 GitHub 的 MCP server（抓作業）和信箱的 MCP server（寄信）；
這裡用假資料代替，寄信也只會寫進 寄件匣.txt。

兩種接法：
    python homework_mcp.py              # stdio：本機插座，由 agent 那邊把它開起來
    python homework_mcp.py --http 8765  # Streamable HTTP：變成一個網址，像遠端 MCP
"""

import argparse
import datetime as _dt
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

寄件匣 = Path(__file__).resolve().parent.parent / "寄件匣.txt"

# 假的作業倉庫：學生、信箱、交的作業
作業們 = {
    "小明": ("xiaoming@example.com", "print('hi'\n"),
    "小華": ("xiaohua@example.com", "def add(a, b):\n    return a + b\n\nprint(add(2, 3))\n"),
    "小美": ("xiaomei@example.com", "def add(a, b):\n    total = a + b\n    return summ\n\nprint(add(2, 3))\n"),
    "阿傑": ("ajie@example.com", "def CalcAverage(scoreList):\n    Total = 0\n    for s in scoreList:\n        Total += s\n"
                                 "    return Total / len(scoreList)\n\nmyScores = [90, 85, 77]\nprint(CalcAverage(myScores))\n"),
    "小芳": ("xiaofang@example.com", "def average(scores):\n  total = 0\n  for s in scores:\n        total += s\n"
                                     "  return total / len(scores)\n\nprint(average([90, 85, 77]))\n"),
}

mcp = FastMCP("作業倉庫", log_level="WARNING")


@mcp.tool()
def list_homework() -> str:
    """列出已經交作業的學生（名字和 email），回傳 JSON 字串。要批改作業時先呼叫這個。"""
    return json.dumps([{"學生": name, "email": email} for name, (email, _) in 作業們.items()], ensure_ascii=False)


@mcp.tool()
def get_homework(student: str) -> str:
    """取得某位學生交的作業程式碼。參數 student：學生名字（從 list_homework 拿）。"""
    if student not in 作業們:
        return f"找不到「{student}」的作業"
    return 作業們[student][1]


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """寄信給學生（不可逆：寄出去就收不回來）。參數：收件人 email、主旨、內文。"""
    with 寄件匣.open("a", encoding="utf-8") as f:
        f.write(f"[{_dt.datetime.now():%H:%M:%S}] 寄給 {to}｜{subject}\n{body}\n\n")
    return f"（模擬）已寄給 {to}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", type=int, help="用 Streamable HTTP 開在這個 port（不給就用 stdio）")
    args = parser.parse_args()
    if args.http:
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = args.http
        mcp.run(transport="streamable-http")   # 網址：http://127.0.0.1:<port>/mcp
    else:
        mcp.run()
