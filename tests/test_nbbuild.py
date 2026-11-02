"""Notebook 重排或修改時，不可把舊輸出接到另一個實驗。"""
import sys
import tempfile
import unittest
from pathlib import Path

import nbformat

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from nbbuild import _keep_outputs, _stable_ids


class PreserveOutputsTest(unittest.TestCase):
    def test_reorder_edit_and_duplicate_writefile(self):
        sources = ["#@title A\nprint(1)", "#@title B\nprint(2)",
                   "%%writefile /tmp/skill\nversion A", "%%writefile /tmp/skill\nversion B"]
        old = []
        for i, source in enumerate(sources):
            cell = nbformat.v4.new_code_cell(source, id=f"old-{i}")
            cell.metadata["id"] = cell.id
            cell.outputs = [nbformat.v4.new_output("stream", name="stdout", text=f"result-{i}")]
            cell.execution_count = i + 1
            old.append(cell)
        with tempfile.TemporaryDirectory() as work:
            path = Path(work) / "test.ipynb"
            nbformat.write(nbformat.v4.new_notebook(cells=old), path)
            new = [nbformat.v4.new_code_cell(s) for s in
                   [sources[3], sources[1].replace("print(2)", "print(20)"), sources[0], sources[2]]]
            self.assertEqual(_keep_outputs(new, path), 3)
            _stable_ids(new, path)
            self.assertEqual(new[0].outputs[0].text, "result-3")
            self.assertEqual(new[0].id, "old-3")
            self.assertEqual(new[1].outputs, [])
            self.assertIsNone(new[1].execution_count)
            self.assertEqual(new[2].outputs[0].text, "result-0")
            self.assertEqual(new[3].outputs[0].text, "result-2")
            self.assertEqual(len({c.id for c in new}), len(new))


if __name__ == "__main__":
    unittest.main()
