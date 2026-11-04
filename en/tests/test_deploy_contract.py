"""After-class API exercise: reading the pending emails and confirming are separate, and re-running must not append to an existing batch."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "review-bot"))
from deploy import multi_agent, server


class VerificationContractTest(unittest.TestCase):
    def test_unparseable_or_nonboolean_verdict_does_not_pass(self):
        for reply in ['cannot tell', '{}', '{"passed": "false"}', '{"passed": null}', '{broken}']:
            model = SimpleNamespace(invoke=lambda _, text=reply: SimpleNamespace(text=text))
            result = multi_agent.verify(model, "print(1)", "Strengths: Clear.\nImprovements: Add tests.")
            self.assertFalse(result["passed"], reply)

    def test_explicit_verdict_is_still_subject_to_code_checks(self):
        model = SimpleNamespace(invoke=lambda _: SimpleNamespace(text='{"passed": true, "reason": "OK"}'))
        self.assertTrue(multi_agent.verify(model, "print(1)", "Strengths: Clear.\nImprovements: Add tests.")["passed"])
        self.assertFalse(multi_agent.verify(model, "print(1)", "Strengths: Clear.\nImprovements: Line 99 needs a change.")["passed"])


class SendDecisionTest(unittest.IsolatedAsyncioTestCase):
    async def test_cancel_ends_at_confirmation_without_sending(self):
        from langgraph.checkpoint.memory import InMemorySaver
        from langgraph.types import Command

        def fake_tool(result):
            return SimpleNamespace(ainvoke=AsyncMock(return_value=result))
        tools = {"list_homework": fake_tool('[{"student": "Alex", "email": "alex@example.com"}]'),
                 "get_homework": fake_tool("print('hi'"),   # Syntax error: the code replies directly, no model call
                 "send_email": fake_tool("sent")}
        with patch.object(multi_agent, "get_mcp_tools", AsyncMock(return_value=tools)):
            graph = multi_agent.build_multi_agent_helper(SimpleNamespace(), mcp_config={}, checkpointer=InMemorySaver())
            config = {"configurable": {"thread_id": "cancel"}}
            await graph.ainvoke({"results": []}, config)
            stations_visited = [station async for event in graph.astream(Command(resume="Send none"), config, stream_mode="updates")
                                for station in event]
            snapshot = await graph.aget_state(config)
        self.assertEqual(stations_visited, ["confirm_before_send"])
        self.assertEqual(snapshot.next, ())
        self.assertEqual(snapshot.values["sent_log"], ["No emails were sent (decision: Send none)"])
        tools["send_email"].ainvoke.assert_not_awaited()


class ApiContractTest(unittest.IsolatedAsyncioTestCase):
    async def test_existing_thread_does_not_restart(self):
        graph = SimpleNamespace(aget_state=AsyncMock(return_value=SimpleNamespace(values={"results": [1]})),
                                ainvoke=AsyncMock())
        with patch.object(server, "helper", AsyncMock(return_value=graph)):
            result = await server.start_batch(server.BatchRequest(thread_id="used"))
        self.assertIn("error", result)
        graph.ainvoke.assert_not_awaited()

    async def test_new_thread_returns_pending_content_without_resuming(self):
        pending = {"emails_to_send": [{"student": "Chloe", "feedback": "full content"}]}
        graph = SimpleNamespace(aget_state=AsyncMock(return_value=SimpleNamespace(values={})),
                                ainvoke=AsyncMock(return_value={"__interrupt__": [SimpleNamespace(value=pending)]}))
        with patch.object(server, "helper", AsyncMock(return_value=graph)):
            result = await server.start_batch(server.BatchRequest(thread_id="fresh"))
        self.assertEqual(result["pending_confirmation"], pending)
        graph.ainvoke.assert_awaited_once()
        self.assertIsInstance(graph.ainvoke.call_args.args[0], dict)

    async def test_only_pending_confirmation_accepts_a_valid_decision(self):
        graph = SimpleNamespace(aget_state=AsyncMock(return_value=SimpleNamespace(next=("review_one",))),
                                ainvoke=AsyncMock(return_value={"sent_log": ["simulated send"]}))
        with patch.object(server, "helper", AsyncMock(return_value=graph)):
            result = await server.confirm_send("id", server.DecisionRequest(decision="Send all"))
            self.assertIn("error", result)
            graph.ainvoke.assert_not_awaited()
            graph.aget_state.return_value = SimpleNamespace(next=("confirm_before_send",))
            result = await server.confirm_send("id", server.DecisionRequest(decision="invalid"))
            self.assertIn("error", result)
            graph.ainvoke.assert_not_awaited()
            result = await server.confirm_send("id", server.DecisionRequest(decision="Send all"))
            self.assertEqual(result["sent_log"], ["simulated send"])
            self.assertEqual(graph.ainvoke.call_args.args[0].resume, "Send all")


if __name__ == "__main__":
    unittest.main()
