"""read_spec: reads the assignment requirements for this question.

The requirements are stored in review-bot/spec.md. When the notebook form changes the assignment, this file is rewritten.
"""

from pathlib import Path

from langchain.tools import tool

SPEC_FILE = Path(__file__).resolve().parent.parent / "spec.md"


def read_spec_text() -> str:
    if not SPEC_FILE.exists():
        return "(No assignment requirements were provided for this question)"
    return SPEC_FILE.read_text(encoding="utf-8").strip() or "(No assignment requirements were provided for this question)"


@tool
def read_spec() -> str:
    """Read the assignment requirements for this question (what the assignment says and what to hand in).

    When to use it: before judging whether the homework meets the assignment, for example whether the function name or the output format is right.
    It takes no parameters.
    Returns: the full text of the assignment requirements.
    """
    return read_spec_text()
