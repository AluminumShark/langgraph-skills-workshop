"""When a notebook is reordered or edited, old output must never be attached to a different experiment."""
import sys
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import nbformat

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from nbbuild import _keep_outputs, _stable_ids
import nbbuild


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


class ArchiveOutputsTest(unittest.TestCase):
    def make_old(self, root):
        out = root / "notebooks" / "example.ipynb"
        out.parent.mkdir()
        cell = nbformat.v4.new_code_cell("print('old')", execution_count=7)
        cell.outputs = [nbformat.v4.new_output("stream", name="stdout", text="real old result\n")]
        nbformat.write(nbformat.v4.new_notebook(cells=[cell]), out)
        return out

    def test_changed_code_archives_exact_original_before_clearing_output(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            out = self.make_old(root)
            raw = out.read_bytes()
            with patch.object(nbbuild, "REPO", root):
                nbbuild.build("example", [nbformat.v4.new_code_cell("print('new')")])
                nbbuild.build("example", [nbformat.v4.new_code_cell("print('new')")])
            snapshots = list((out.parent / "output-history" / "example").glob("*.ipynb"))
            self.assertEqual(len(snapshots), 1)
            self.assertEqual(snapshots[0].stem, hashlib.sha256(raw).hexdigest())
            self.assertEqual(snapshots[0].read_bytes(), raw)
            new = nbformat.read(out, as_version=4).cells[0]
            self.assertEqual(new.outputs, [])
            self.assertIsNone(new.execution_count)

    def test_markdown_edit_keeps_output_without_archive(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            out = self.make_old(root)
            with patch.object(nbbuild, "REPO", root):
                nbbuild.build("example", [nbformat.v4.new_markdown_cell("new explanation"),
                                         nbformat.v4.new_code_cell("print('old')")])
            self.assertFalse((out.parent / "output-history").exists())
            cell = nbformat.read(out, as_version=4).cells[1]
            self.assertEqual(cell.outputs[0].text, "real old result\n")
            self.assertEqual(cell.execution_count, 7)

    def test_removed_duplicate_with_distinct_result_is_archived(self):
        with tempfile.TemporaryDirectory() as work:
            out = self.make_old(Path(work))
            old = nbformat.read(out, as_version=4)
            second = nbformat.v4.new_code_cell("print('old')", execution_count=8)
            second.outputs = [nbformat.v4.new_output("stream", name="stdout", text="second result")]
            old.cells.append(second)
            nbformat.write(old, out)
            raw = out.read_bytes()
            archive = nbbuild._archive_replaced_outputs([old.cells[0]], out)
            self.assertEqual(archive.read_bytes(), raw)
            self.assertEqual(out.read_bytes(), raw)

    def test_archive_failure_leaves_original_notebook_untouched(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            out = self.make_old(root)
            raw = out.read_bytes()
            with patch.object(nbbuild, "REPO", root), patch.object(
                nbbuild, "_archive_replaced_outputs", side_effect=OSError("disk full")
            ):
                with self.assertRaises(OSError):
                    nbbuild.build("example", [nbformat.v4.new_code_cell("print('new')")])
            self.assertEqual(out.read_bytes(), raw)


if __name__ == "__main__":
    unittest.main()
