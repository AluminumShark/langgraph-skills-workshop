"""Homework repo MCP server: the tools live in "another program" and plug in through the MCP socket.

It's just an ordinary Python file; the functions simply have @mcp.tool() on top.
In the real world this role is played by GitHub's MCP server (fetching homework) and a mailbox MCP server (sending email);
here we use fake data instead, and "sending email" only writes to outbox.txt.

Two ways to connect:
    python homework_mcp.py              # stdio: a local socket; the agent side starts it
    python homework_mcp.py --http 8765  # Streamable HTTP: it becomes a URL, like a remote MCP
"""

import argparse
import datetime as _dt
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

OUTBOX = Path(__file__).resolve().parent.parent / "outbox.txt"

# A fake homework repo: students, emails, submitted homework
SUBMISSIONS = {
    "Alex": ("alex@example.com", "print('hi'\n"),
    "Ben": ("ben@example.com", "def add(a, b):\n    return a + b\n\nprint(add(2, 3))\n"),
    "Chloe": ("chloe@example.com", "def add(a, b):\n    total = a + b\n    return summ\n\nprint(add(2, 3))\n"),
    "Jay": ("jay@example.com", "def CalcAverage(scoreList):\n    Total = 0\n    for s in scoreList:\n        Total += s\n"
                               "    return Total / len(scoreList)\n\nmyScores = [90, 85, 77]\nprint(CalcAverage(myScores))\n"),
    "Fiona": ("fiona@example.com", "def average(scores):\n  total = 0\n  for s in scores:\n        total += s\n"
                                   "  return total / len(scores)\n\nprint(average([90, 85, 77]))\n"),
}

mcp = FastMCP("homework_repo", log_level="WARNING")


@mcp.tool()
def list_homework() -> str:
    """List the students who have submitted homework (name and email) as a JSON string. Call this first when you need to review homework."""
    return json.dumps([{"student": name, "email": email} for name, (email, _) in SUBMISSIONS.items()], ensure_ascii=False)


@mcp.tool()
def get_homework(student: str) -> str:
    """Get the homework code one student submitted. Parameter student: the student's name (from list_homework)."""
    if student not in SUBMISSIONS:
        return f'No homework found for "{student}"'
    return SUBMISSIONS[student][1]


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a student (irreversible: once sent, it can't be taken back). Parameters: recipient email, subject, body."""
    with OUTBOX.open("a", encoding="utf-8") as f:
        f.write(f"[{_dt.datetime.now():%H:%M:%S}] To {to} | {subject}\n{body}\n\n")
    return f"(simulated) Sent to {to}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", type=int, help="Serve over Streamable HTTP on this port (omit it to use stdio)")
    args = parser.parse_args()
    if args.http:
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = args.http
        mcp.run(transport="streamable-http")   # URL: http://127.0.0.1:<port>/mcp
    else:
        mcp.run()
