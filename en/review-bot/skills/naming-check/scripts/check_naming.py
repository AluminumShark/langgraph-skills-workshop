"""Check whether variable and function names are lowercase English with underscores (snake_case).

Usage:
    python check_naming.py homework.py        # check one file
    python check_naming.py < homework.py      # or read from standard input
Output:
    One line per problem, for example "Line 3: myVar breaks the rule (suggest my_var)"
    When everything passes it prints "OK: all variable and function names are lowercase with underscores"

A script does one thing and prints only a few short lines, so people and the AI can both check it. The same input and the same script give the same result.
"""

import ast
import re
import sys

RULE = re.compile(r"^_?[a-z][a-z0-9_]*$")


def suggest_name(name: str) -> str:
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    return re.sub(r"_+", "_", s).lower()


def find_all_names(tree: ast.AST) -> dict[str, int]:
    """name → line number of its first appearance (variables, functions, parameters; class names are not included)."""
    names = {}

    def note(name, line):
        if name not in names or line < names[name]:
            names[name] = line

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            note(node.id, node.lineno)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            note(node.name, node.lineno)
        elif isinstance(node, ast.arg) and node.arg not in ("self", "cls"):
            note(node.arg, node.lineno)
    return names


def check_names(code: str) -> str:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"Cannot check: line {e.lineno} has a syntax error"
    problems = [
        f"Line {line}: {name} breaks the rule (suggest {suggest_name(name)})"
        for name, line in sorted(find_all_names(tree).items(), key=lambda x: (x[1], x[0]))
        if not RULE.match(name)
    ]
    return "\n".join(problems) if problems else "OK: all variable and function names are lowercase with underscores"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            source = f.read()
    else:
        source = sys.stdin.buffer.read().decode("utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(check_names(source))
