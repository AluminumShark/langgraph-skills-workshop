# Original output snapshots

This folder is for the English edition's own snapshots. The generator, `en/scripts/nbbuild.py`, saves them here automatically; nothing has been saved yet unless a snapshot file is listed below.

The Chinese edition keeps its history in the repo's top-level `notebooks/output-history/`. Those snapshots (the original notebooks' **code, form values, real outputs and execution counts**) belong to the Chinese notebooks. They are not copied here, and they are not evidence that the English notebooks have been run.

## Protection when you rebuild

`en/scripts/nbbuild.py` carries old outputs over to the new version only for code cells whose source is exactly the same. If changing or deleting a code cell would make old outputs unusable, the generator first saves the whole old file into this folder, prints where it went, and then writes the new version. If the backup fails, it stops and does not overwrite.

- Automatic snapshot location: `output-history/<notebook name>/<content SHA-256>.ipynb`.
- Identical content is saved only once. If only Markdown changed and every output can be carried over, no new snapshot is added.
- After a rebuild, check `git status`; snapshots you want to keep must be committed too.
- Old outputs are never attached directly to changed code, and fake-model results are never used to stand in for real Colab outputs.
- An empty output in the new notebook does not mean the user did not run it or did not save it.

For the detailed observations and the differences in the new version, see the [output review report](../../docs/notebook-output-review.md).
