"""在步數上限落在工具要求之後時，要求數與回傳數不可混為一談。"""
import contextlib
import ast
import io
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.errors import GraphRecursionError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from nbbuild import PREAMBLE
from nbspec.nb_1B_agent import cells


class ToolCountTest(unittest.TestCase):
    def test_last_request_without_execution_is_not_counted_as_a_return(self):
        def stream(*args, **kwargs):
            for i in range(13):
                call = {"name": "always_fail", "args": {}, "id": f"call-{i}"}
                yield {"model": {"messages": [AIMessage(content="", tool_calls=[call])]}}
                if i < 12:
                    yield {"tools": {"messages": [ToolMessage(
                        content="執行失敗", name="always_fail", tool_call_id=call["id"]
                    )]}}
            raise GraphRecursionError("limit reached")

        cell = next(c for c in cells() if c.cell_type == "code"
                    and c.source.startswith("#@title ▶ 執行：一個永遠失敗的工具"))
        log = Mock()
        output = io.StringIO()
        with patch("langchain.agents.create_agent", return_value=SimpleNamespace(stream=stream)), \
                contextlib.redirect_stdout(output):
            exec(cell.source.replace(PREAMBLE, ""), {"model": object(), "記下": log})
        self.assertEqual(log.call_args.args[1], {"工具要求次數": 13, "工具回傳次數": 12})
        self.assertIn("13 次工具要求，收到 12 次工具回傳", output.getvalue())


class McpToolVisibilityTest(unittest.IsolatedAsyncioTestCase):
    async def test_printed_agent_tools_match_granted_tools(self):
        async def events(*args, **kwargs):
            if False:
                yield {}

        server_tools = [SimpleNamespace(name=n, description="demo", args={})
                        for n in ["list_homework", "get_homework", "send_email"]]
        local_tools = [SimpleNamespace(name=n, description="demo", args={})
                       for n in ["run_code", "check_indent", "read_spec"]]
        agent_module = SimpleNamespace(小助教的工具=local_tools, 基本_system_prompt="demo")
        client = SimpleNamespace(get_tools=AsyncMock(return_value=server_tools))
        factory = Mock(return_value=SimpleNamespace(astream=events))
        cell = next(c for c in cells() if c.cell_type == "code"
                    and c.source.startswith("#@title ▶ 執行：接上 MCP 插座"))
        log = Mock()
        output = io.StringIO()
        with patch.dict(sys.modules, {"agent": agent_module}), \
                patch("langchain.agents.create_agent", factory), \
                patch("langchain_mcp_adapters.client.MultiServerMCPClient", return_value=client), \
                contextlib.redirect_stdout(output):
            compiled = compile(cell.source.replace(PREAMBLE, ""), "mcp-cell", "exec",
                               flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
            await eval(compiled, {"model": object(), "記下": log, "BASE": Path("/demo"), "sys": sys})
        granted = [t.name for t in factory.call_args.kwargs["tools"]]
        self.assertNotIn("send_email", granted)
        recorded = log.call_args.args[1]
        self.assertEqual(recorded["實際交給 agent 的工具"], granted)
        self.assertIn("send_email", recorded["server 可提供的 MCP 工具"])
        shown = output.getvalue().split("實際交給 agent 的工具", 1)[1]
        self.assertNotIn("send_email", shown)
        for name in granted:
            self.assertIn(name, shown)


if __name__ == "__main__":
    unittest.main()
