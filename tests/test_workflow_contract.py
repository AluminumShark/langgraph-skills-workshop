"""教學用 workflow 必須區分語法、格式通過與達上限停止。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "review-bot"))
import graph


class WorkflowContractTest(unittest.TestCase):
    def test_two_nonempty_sections_and_limit(self):
        check = graph.建立_check_format(100)
        for text in ["優點：結構清楚。\n改進：多測幾個輸入。", "優點:清楚 改進:加測試"]:
            self.assertTrue(check({"feedback": text})["format_ok"])
        for text in ["有優點也有改進", "優點：\n改進：加測試", "優點：清楚\n改進：", "改進：加測試\n優點：清楚"]:
            self.assertFalse(check({"feedback": text})["format_ok"])
        self.assertFalse(graph.建立_check_format(1)({"feedback": "優點：好\n改進：測試"})["format_ok"])

    def test_syntax_error_skips_generation(self):
        result = graph.建立小助教().invoke(graph.空白訂單紙("print("))
        self.assertFalse(result["syntax_ok"])
        self.assertEqual(result["retries"], 0)
        self.assertIn("語法：", result["feedback"])

    def test_runtime_error_can_pass_syntax(self):
        result = graph.建立小助教().invoke(graph.空白訂單紙("print(undefined_name)"))
        self.assertTrue(result["syntax_ok"])
        self.assertNotIn("程式可以執行", result["feedback"])

    def test_limit_stops_without_passing(self):
        result = graph.建立小助教(最多重試次數=2, 回饋字數上限=1).invoke(graph.空白訂單紙("print(1)"))
        self.assertEqual(result["retries"], 2)
        self.assertFalse(result["format_ok"])


if __name__ == "__main__":
    unittest.main()
