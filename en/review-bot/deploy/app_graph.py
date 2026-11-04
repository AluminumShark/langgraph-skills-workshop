"""The entry point that langgraph.json points to: LangSmith Deployment / `langgraph dev` imports the graph in this file.

The deployment platform provides its own checkpointer (for example Postgres), so we don't call open_checkpointer() here.
- Model: WORKSHOP_PROVIDER=gemini; the key GOOGLE_API_KEY is injected by the platform's Secrets
- Homework repo MCP: HOMEWORK_MCP_URL points to the URL of a remote MCP server (if it isn't set, one is started on the same machine over stdio)
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("WORKSHOP_PROVIDER", "gemini")

from deploy.multi_agent import build_multi_agent_helper, homework_repo_config  # noqa: E402
from llm import get_model  # noqa: E402

graph = build_multi_agent_helper(get_model(), mcp_config=homework_repo_config(os.environ.get("HOMEWORK_MCP_URL")))
