"""check_naming: wraps the Skill's script scripts/check_naming.py as an agent tool.

Wrap the script in @tool and it joins the agent's toolbox.
In this example the AI decides whether to call the tool and tidies up the result. With the same version and the same input, the Python script returns the same check result,
but you still need to confirm whether the model actually called it and whether it kept the result intact.
"""

import subprocess
import sys
from pathlib import Path

from langchain.tools import tool

SCRIPT = Path(__file__).resolve().parent.parent / "skills" / "naming-check" / "scripts" / "check_naming.py"


def run_naming_script(code: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)], input=code.encode("utf-8"), capture_output=True, timeout=10
    )
    output = proc.stdout.decode("utf-8").strip()
    return output or "The script failed to run: " + proc.stderr.decode("utf-8", "replace").strip()[-200:]


@tool
def check_naming(code: str) -> str:
    """Check whether variable and function names are lowercase with underscores (snake_case), and return the lines that break the rule.

    When to use it: when reviewing a homework and you need to list the naming problems (this is the script that comes with the naming-check handbook).
    Parameter code: the complete Python code (a string).
    Returns: one line per problem, for example "Line 3: myVar breaks the rule (suggest my_var)". If everything passes it returns "OK: ...".
    """
    return run_naming_script(code)
