"""每份作業的題目必須跨 thread 與 checkpoint 保持正確配對。"""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "review-bot"))
import dual_core


class AssignmentSpecTest(unittest.TestCase):
    def test_each_assignment_has_an_explicit_matching_spec(self):
        average = dual_core.作業輸入("命名不一致", "average code", "初學者")
        addition = dual_core.作業輸入("變數打錯字", "addition code", "初學者")
        self.assertIn("平均值", average["spec"])
        self.assertNotIn("add(a, b)", average["spec"])
        self.assertIn("add(a, b)", addition["spec"])
        self.assertEqual(average["code"], "average code")
        with self.assertRaisesRegex(ValueError, "尚未設定"):
            dual_core.作業輸入("未知作業", "print(1)", "初學者")

    def test_tools_are_isolated_and_missing_spec_never_uses_global_file(self):
        average = dual_core.建立_read_spec(dual_core.範例題目["命名不一致"])
        addition = dual_core.建立_read_spec(dual_core.範例題目["正確的程式"])
        self.assertEqual(average.name, "read_spec")
        self.assertIn("平均值", average.invoke({}))
        self.assertIn("add(a, b)", addition.invoke({}))
        self.assertIn("平均值", average.invoke({}))
        for value in (None, "", "   "):
            with self.assertRaisesRegex(ValueError, "缺少題目"):
                dual_core.建立_read_spec(value)

    def test_interleaved_paused_threads_resume_their_saved_spec(self):
        observed = []

        def factory(model, tools, system_prompt):
            read_spec = next(t for t in tools if t.name == "read_spec")

            def invoke(inputs, config):
                observed.append(read_spec.invoke({}))
                return {"messages": [AIMessage(content="優點：結構清楚。\n改進：增加測試。") ]}

            return SimpleNamespace(invoke=invoke)

        model = SimpleNamespace(invoke=lambda _: SimpleNamespace(text="friendly-feedback"))
        graph = dual_core.建立整合小助教(
            model, checkpointer=InMemorySaver(), interrupt_before=["give_feedback"]
        )
        average_id = {"configurable": {"thread_id": "average"}}
        addition_id = {"configurable": {"thread_id": "addition"}}
        with patch.object(dual_core, "create_agent", side_effect=factory):
            graph.invoke(dual_core.作業輸入("命名不一致", "print(84)", "初學者"), average_id)
            graph.invoke(dual_core.作業輸入("正確的程式", "print(5)", "初學者"), addition_id)
            self.assertEqual(observed, [])
            self.assertEqual(graph.get_state(average_id).next, ("give_feedback",))
            average = graph.invoke(None, average_id)
            addition = graph.invoke(None, addition_id)
            self.assertIn("平均值", observed[0])
            self.assertIn("add(a, b)", observed[1])
            self.assertEqual(average["spec"], dual_core.範例題目["命名不一致"])
            self.assertEqual(addition["spec"], dual_core.範例題目["正確的程式"])
            self.assertTrue(average["format_ok"])
            self.assertFalse(graph.get_state(average_id).next)
            graph.invoke(None, average_id)
            self.assertEqual(len(observed), 2, "完成結果取回不應重新呼叫模型")


if __name__ == "__main__":
    unittest.main()
