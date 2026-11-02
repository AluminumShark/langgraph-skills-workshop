"""從 scripts/nbspec/*.py 產生 notebooks/*.ipynb。

用法：
    uv run python scripts/build_notebooks.py            # 全部重新產生
    uv run python scripts/build_notebooks.py 1-A 2-B    # 只產生名稱開頭符合的
"""

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbbuild  # noqa: E402


def main(prefixes: list[str]) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    for spec_file in sorted((Path(__file__).parent / "nbspec").glob("nb_*.py")):
        spec = importlib.util.spec_from_file_location(spec_file.stem, spec_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if prefixes and not any(mod.NAME.startswith(p) for p in prefixes):
            continue
        out = nbbuild.build(mod.NAME, mod.cells())
        print(f"✅ {out.relative_to(nbbuild.REPO)}")


if __name__ == "__main__":
    main(sys.argv[1:])
