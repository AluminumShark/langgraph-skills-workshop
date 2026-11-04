"""When the step limit lands right after a tool request, the request count and the result count must not be mixed up."""
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
                        content="Execution failed", name="always_fail", tool_call_id=call["id"]
                    )]}}
            raise GraphRecursionError("limit reached")

        cell = next(c for c in cells() if c.cell_type == "code"
                    and c.source.startswith("#@title") and "always_fail" in c.source and "create_agent" in c.source)
        log = Mock()
        output = io.StringIO()
        with patch("langchain.agents.create_agent", return_value=SimpleNamespace(stream=stream)), \
                contextlib.redirect_stdout(output):
            exec(cell.source.replace(PREAMBLE, ""), {"model": object(), "record": log})
        self.assertEqual(log.call_args.args[1], {"tool_call_requests": 13, "tool_result_count": 12})
        self.assertIn("the model made 13 tool request(s) and received 12 tool result(s)", output.getvalue())


class McpToolVisibilityTest(unittest.IsolatedAsyncioTestCase):
    async def test_printed_agent_tools_match_granted_tools(self):
        async def events(*args, **kwargs):
            if False:
                yield {}

        server_tools = [SimpleNamespace(name=n, description="demo", args={})
                        for n in ["list_homework", "get_homework", "send_email"]]
        local_tools = [SimpleNamespace(name=n, description="demo", args={})
                       for n in ["run_code", "check_indent", "read_spec"]]
        agent_module = SimpleNamespace(helper_tools=local_tools, base_system_prompt="demo")
        client = SimpleNamespace(get_tools=AsyncMock(return_value=server_tools))
        factory = Mock(return_value=SimpleNamespace(astream=events))
        cell = next(c for c in cells() if c.cell_type == "code"
                    and c.source.startswith("#@title") and "MultiServerMCPClient" in c.source)
        log = Mock()
        output = io.StringIO()
        with patch.dict(sys.modules, {"agent": agent_module}), \
                patch("langchain.agents.create_agent", factory), \
                patch("langchain_mcp_adapters.client.MultiServerMCPClient", return_value=client), \
                contextlib.redirect_stdout(output):
            compiled = compile(cell.source.replace(PREAMBLE, ""), "mcp-cell", "exec",
                               flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
            await eval(compiled, {"model": object(), "record": log, "BASE": Path("/demo"), "sys": sys})
        granted = [t.name for t in factory.call_args.kwargs["tools"]]
        self.assertNotIn("send_email", granted)
        recorded = log.call_args.args[1]
        self.assertEqual(recorded["tools handed to the agent"], granted)
        self.assertIn("send_email", recorded["MCP tools the server provides"])
        shown = output.getvalue().split("Tools actually handed to the agent", 1)[1]
        self.assertNotIn("send_email", shown)
        for name in granted:
            self.assertIn(name, shown)


if __name__ == "__main__":
    unittest.main()
