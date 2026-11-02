"""langgraph.json 指向的進入點：LangSmith Deployment / `langgraph dev` 會 import 這個檔案裡的 graph。

部署平台會自己提供 checkpointer（例如 Postgres），所以這裡不用 開存檔()。
模型來源用環境變數：WORKSHOP_PROVIDER=gemini，金鑰 GOOGLE_API_KEY 由平台的 Secret 注入。
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("WORKSHOP_PROVIDER", "gemini")

from dual_core import 建立雙核小助教  # noqa: E402
from llm import get_model  # noqa: E402

graph = 建立雙核小助教(get_model())
