"""課後 API 練習：讀取待寄內容與確認分開，重跑不應追加既有批次。"""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "review-bot"))
from deploy import multi_agent, server


class VerificationContractTest(unittest.TestCase):
    def test_unparseable_or_nonboolean_verdict_does_not_pass(self):
        for reply in ['無法判斷', '{}', '{"通過": "false"}', '{"通過": null}', '{broken}']:
            model = SimpleNamespace(invoke=lambda _, text=reply: SimpleNamespace(text=text))
            result = multi_agent.驗證(model, "print(1)", "優點：清楚。\n改進：補測試。")
            self.assertFalse(result["通過"], reply)

    def test_explicit_verdict_is_still_subject_to_code_checks(self):
        model = SimpleNamespace(invoke=lambda _: SimpleNamespace(text='{"通過": true, "原因": "OK"}'))
        self.assertTrue(multi_agent.驗證(model, "print(1)", "優點：清楚。\n改進：補測試。")["通過"])
        self.assertFalse(multi_agent.驗證(model, "print(1)", "優點：清楚。\n改進：第 99 行需要修改。")["通過"])


class SendDecisionTest(unittest.IsolatedAsyncioTestCase):
    async def test_cancel_ends_at_confirmation_without_sending(self):
        from langgraph.checkpoint.memory import InMemorySaver
        from langgraph.types import Command

        def 假工具(回傳):
            return SimpleNamespace(ainvoke=AsyncMock(return_value=回傳))
        tools = {"list_homework": 假工具('[{"學生": "小明", "email": "ming@example.com"}]'),
                 "get_homework": 假工具("print('hi'"),   # 語法錯：程式直接回覆，不呼叫模型
                 "send_email": 假工具("寄出")}
        with patch.object(multi_agent, "取得MCP工具", AsyncMock(return_value=tools)):
            graph = multi_agent.建立多agent小助教(SimpleNamespace(), mcp設定={}, checkpointer=InMemorySaver())
            config = {"configurable": {"thread_id": "cancel"}}
            await graph.ainvoke({"結果們": []}, config)
            走過的站 = [站 async for event in graph.astream(Command(resume="都不要寄"), config, stream_mode="updates")
                     for 站 in event]
            snapshot = await graph.aget_state(config)
        self.assertEqual(走過的站, ["寄信前確認"])
        self.assertEqual(snapshot.next, ())
        self.assertEqual(snapshot.values["寄件紀錄"], ["沒有寄出任何信（決定：都不要寄）"])
        tools["send_email"].ainvoke.assert_not_awaited()


class ApiContractTest(unittest.IsolatedAsyncioTestCase):
    async def test_existing_thread_does_not_restart(self):
        graph = SimpleNamespace(aget_state=AsyncMock(return_value=SimpleNamespace(values={"結果們": [1]})),
                                ainvoke=AsyncMock())
        with patch.object(server, "小助教", AsyncMock(return_value=graph)):
            result = await server.開始批改(server.批改請求(thread_id="used"))
        self.assertIn("錯誤", result)
        graph.ainvoke.assert_not_awaited()

    async def test_new_thread_returns_pending_content_without_resuming(self):
        pending = {"要寄出的信": [{"學生": "小美", "回饋": "完整內容"}]}
        graph = SimpleNamespace(aget_state=AsyncMock(return_value=SimpleNamespace(values={})),
                                ainvoke=AsyncMock(return_value={"__interrupt__": [SimpleNamespace(value=pending)]}))
        with patch.object(server, "小助教", AsyncMock(return_value=graph)):
            result = await server.開始批改(server.批改請求(thread_id="fresh"))
        self.assertEqual(result["待確認"], pending)
        graph.ainvoke.assert_awaited_once()
        self.assertIsInstance(graph.ainvoke.call_args.args[0], dict)

    async def test_only_pending_confirmation_accepts_a_valid_decision(self):
        graph = SimpleNamespace(aget_state=AsyncMock(return_value=SimpleNamespace(next=("批一份",))),
                                ainvoke=AsyncMock(return_value={"寄件紀錄": ["模擬寄出"]}))
        with patch.object(server, "小助教", AsyncMock(return_value=graph)):
            result = await server.確認寄信("id", server.決定請求(決定="全部寄出"))
            self.assertIn("錯誤", result)
            graph.ainvoke.assert_not_awaited()
            graph.aget_state.return_value = SimpleNamespace(next=("寄信前確認",))
            result = await server.確認寄信("id", server.決定請求(決定="invalid"))
            self.assertIn("錯誤", result)
            graph.ainvoke.assert_not_awaited()
            result = await server.確認寄信("id", server.決定請求(決定="全部寄出"))
            self.assertEqual(result["寄件紀錄"], ["模擬寄出"])
            self.assertEqual(graph.ainvoke.call_args.args[0].resume, "全部寄出")


if __name__ == "__main__":
    unittest.main()
