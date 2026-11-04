"""The teaching workflow must tell apart syntax errors, format passes, and stopping at the limit."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "review-bot"))
import graph


class WorkflowContractTest(unittest.TestCase):
    def test_two_nonempty_sections_and_limit(self):
        check = graph.make_check_format(300)
        for text in ["Strengths: Clear structure.\nImprovements: Try a few more inputs.", "Strengths:clear Improvements:add tests"]:
            self.assertTrue(check({"feedback": text})["format_ok"])
        for text in ["Has strengths and improvements", "Strengths:\nImprovements: add tests", "Strengths: clear\nImprovements:", "Improvements: add tests\nStrengths: clear"]:
            self.assertFalse(check({"feedback": text})["format_ok"])
        self.assertFalse(graph.make_check_format(1)({"feedback": "Strengths: good\nImprovements: test"})["format_ok"])

    def test_syntax_error_skips_generation(self):
        result = graph.build_helper().invoke(graph.blank_order_slip("print("))
        self.assertFalse(result["syntax_ok"])
        self.assertEqual(result["retries"], 0)
        self.assertIn("Syntax:", result["feedback"])

    def test_runtime_error_can_pass_syntax(self):
        result = graph.build_helper().invoke(graph.blank_order_slip("print(undefined_name)"))
        self.assertTrue(result["syntax_ok"])
        self.assertNotIn("The program runs", result["feedback"])

    def test_limit_stops_without_passing(self):
        result = graph.build_helper(max_retries=2, feedback_char_limit=1).invoke(graph.blank_order_slip("print(1)"))
        self.assertEqual(result["retries"], 2)
        self.assertFalse(result["format_ok"])


if __name__ == "__main__":
    unittest.main()
