"""check_indent: checks indentation and line length.

It deliberately checks ONLY indentation and line length, and never touches variable naming. The naming check is left to Session 2's 2-B,
where it is used to compare "written in the handbook text" with "written as a script".
"""

from langchain.tools import tool

MAX_LINE_LENGTH = 79


def check_indentation(code: str, limit: int = MAX_LINE_LENGTH) -> str:
    problems = []
    for i, line in enumerate(code.splitlines(), start=1):
        if not line.strip():
            continue
        leading_spaces = line[: len(line) - len(line.lstrip())]
        if "\t" in leading_spaces:
            problems.append(f"Line {i}: indented with a Tab; use 4 spaces instead")
        elif len(leading_spaces) % 4 != 0:
            problems.append(f"Line {i}: indented {len(leading_spaces)} spaces; use a multiple of 4")
        if len(line) > limit:
            problems.append(f"Line {i}: {len(line)} characters, over the limit of {limit}")
    return "\n".join(problems) if problems else "OK: indentation and line length look fine"


@tool
def check_indent(code: str) -> str:
    """Check the indentation of a Python homework (is it a multiple of 4, are Tabs mixed in) and the length of each line (limit 79 characters).

    When to use it: when you want to confirm the homework's layout is tidy. It does not check variable naming and does not run the code.
    Parameter code: the complete Python code (a string).
    Returns: one line per problem, for example "Line 2: indented 2 spaces; use a multiple of 4". If everything is fine it returns "OK: ...".
    """
    return check_indentation(code)
