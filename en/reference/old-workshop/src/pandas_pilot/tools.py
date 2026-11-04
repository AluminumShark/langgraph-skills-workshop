"""The two tools used by the data analyst agent."""

from __future__ import annotations

import io

import pandas as pd
from langchain_core.tools import tool


@tool
def inspect_data(path: str) -> str:
    """Check the quality of CSV data. You **must** call this tool before running
    any groupby/filter/agg, to learn the data's shape, columns, and missing values.

    Args:
        path: path to the CSV file
    Returns:
        A string with the shape, columns, missing values, and the first five rows
    """
    df = pd.read_csv(path)

    buf = io.StringIO()
    buf.write(f"shape: {df.shape}\n")
    buf.write(f"columns: {list(df.columns)}\n")
    buf.write("\ndtypes:\n")
    buf.write(df.dtypes.to_string())
    buf.write("\n\nmissing values per column:\n")
    buf.write(df.isna().sum().to_string())
    buf.write("\n\nhead(5):\n")
    buf.write(df.head(5).to_string())
    return buf.getvalue()


@tool
def run_pandas(path: str, code: str) -> str:
    """Run pandas analysis code on a CSV, such as groupby, filter, agg, or sort.
    The loaded DataFrame is available as the `df` variable, so you can use it directly in code.

    Args:
        path: path to the CSV file
        code: a pandas expression (for example "df.groupby('region')['revenue'].mean()")
    Returns:
        The result as a string (truncated if longer than 2000 characters)
    """
    # ⚠️ Warning: eval() is a serious security problem in production
    # It is used here only to keep the workshop explanation simple; in practice use a sandbox / RestrictedPython / e2b
    df = pd.read_csv(path)
    try:
        result = eval(code, {"df": df, "pd": pd})
    except Exception as exc:
        return f"Execution error: {type(exc).__name__}: {exc}"

    text = str(result)
    if len(text) > 2000:
        text = text[:2000] + "\n... (output truncated)"
    return text
