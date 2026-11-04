"""Each homework's assignment must stay correctly paired across threads and checkpoints."""
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
        average = dual_core.homework_input("Inconsistent naming", "average code", "beginner")
        addition = dual_core.homework_input("Variable typo", "addition code", "beginner")
        self.assertIn("average", average["spec"].lower())
        self.assertNotIn("add(a, b)", average["spec"])
        self.assertIn("add(a, b)", addition["spec"])
        self.assertEqual(average["code"], "average code")
        with self.assertRaisesRegex(ValueError, "set up"):
            dual_core.homework_input("Unknown homework", "print(1)", "beginner")

    def test_tools_are_isolated_and_missing_spec_never_uses_global_file(self):
        average = dual_core.make_read_spec(dual_core.sample_specs["Inconsistent naming"])
        addition = dual_core.make_read_spec(dual_core.sample_specs["Correct program"])
        self.assertEqual(average.name, "read_spec")
        self.assertIn("average", average.invoke({}).lower())
        self.assertIn("add(a, b)", addition.invoke({}))
        self.assertIn("average", average.invoke({}).lower())
        for value in (None, "", "   "):
            with self.assertRaisesRegex(ValueError, "no assignment"):
                dual_core.make_read_spec(value)

    def test_interleaved_paused_threads_resume_their_saved_spec(self):
        observed = []

        def factory(model, tools, system_prompt):
            read_spec = next(t for t in tools if t.name == "read_spec")

            def invoke(inputs, config):
                observed.append(read_spec.invoke({}))
                return {"messages": [AIMessage(content="Strengths: Clear structure.\nImprovements: Add tests.")]}

            return SimpleNamespace(invoke=invoke)

        model = SimpleNamespace(invoke=lambda _: SimpleNamespace(text="friendly-feedback"))
        graph = dual_core.build_integrated_helper(
            model, checkpointer=InMemorySaver(), interrupt_before=["give_feedback"]
        )
        average_id = {"configurable": {"thread_id": "average"}}
        addition_id = {"configurable": {"thread_id": "addition"}}
        with patch.object(dual_core, "create_agent", side_effect=factory):
            graph.invoke(dual_core.homework_input("Inconsistent naming", "print(84)", "beginner"), average_id)
            graph.invoke(dual_core.homework_input("Correct program", "print(5)", "beginner"), addition_id)
            self.assertEqual(observed, [])
            self.assertEqual(graph.get_state(average_id).next, ("give_feedback",))
            average = graph.invoke(None, average_id)
            addition = graph.invoke(None, addition_id)
            self.assertIn("average", observed[0].lower())
            self.assertIn("add(a, b)", observed[1])
            self.assertEqual(average["spec"], dual_core.sample_specs["Inconsistent naming"])
            self.assertEqual(addition["spec"], dual_core.sample_specs["Correct program"])
            self.assertTrue(average["format_ok"])
            self.assertFalse(graph.get_state(average_id).next)
            graph.invoke(None, average_id)
            self.assertEqual(len(observed), 2, "Retrieving a finished result must not call the model again")


if __name__ == "__main__":
    unittest.main()
