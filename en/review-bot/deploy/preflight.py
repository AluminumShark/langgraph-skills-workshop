"""Exercise 4: pre-launch checks. Every item is checked with code (a sensor), not by gut feeling.

Usage: python -m deploy.preflight (inside the review-bot/ folder)
"""

import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

KEY_PATTERNS = [
    (r"AIza[0-9A-Za-z\-_]{35}", "Google API key"),
    (r"sk-[A-Za-z0-9_\-]{20,}", "OpenAI / Anthropic style key"),
    (r"(?i)(api[_-]?key|token|password)\s*=\s*['\"][^'\"\s]{8,}['\"]", "password hard-coded in the code"),
]
SUSPICIOUS_PATTERNS = [
    (r"curl[^\n|]*\|\s*(ba)?sh|wget[^\n|]*\|\s*(ba)?sh", "download and run right away (curl ... | bash)"),
    (r"base64\s+(-d|--decode)", "decodes content you can't read"),
    (r"(?i)ignore (all |the )?previous", "tells the AI to ignore earlier instructions"),
    (r"(?i)environment variable|read_env|WORKSHOP_API_KEY|\$[A-Z_]*KEY", "tells the AI to read a key or an environment variable"),
]
text_files = {".py", ".md", ".sh", ".json", ".txt", ".toml", ".yaml", ".yml", ""}
skip = {"__pycache__", ".llm.json", "history.jsonl", ".env.example"}


def _files(root: Path):
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix in text_files and not (set(p.parts) & skip) and p.name not in skip:
            yield p


def _scan(root: Path, patterns) -> list[str]:
    found = []
    for p in _files(root):
        if p.resolve() == Path(__file__).resolve():
            continue  # don't scan itself (these patterns are written in this file on purpose)
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for pattern, note in patterns:
                if re.search(pattern, line):
                    found.append(f"{p.relative_to(BASE)} line {i}: {note}")
    return found


def run_checks() -> list[tuple[str, str, str]]:
    """Return [(symbol, item, note)]; the symbol is ✅ / ⚠️ / ❌."""
    results = []

    leaks = _scan(BASE, KEY_PATTERNS)
    results.append(("❌" if leaks else "✅", "No hard-coded keys in the code or handbooks",
               "; ".join(leaks) if leaks else "Keys belong in Secrets / Secret Manager and should be read from environment variables"))

    source = os.environ.get("WORKSHOP_PROVIDER") or "(depends on your choice in 0. Environment setup)"
    has_key = bool(os.environ.get("GOOGLE_API_KEY"))
    results.append(("✅" if has_key else "⚠️", "The model key comes from an environment variable",
               f"WORKSHOP_PROVIDER={source}; GOOGLE_API_KEY {'is set' if has_key else 'is not set (Colab built-in model does not need it; in the cloud you must set it)'}"))

    suspicious = _scan(BASE / "skills", SUSPICIOUS_PATTERNS)
    results.append(("❌" if suspicious else "✅", "Third-party Skill scan (the three habits from 2-C)",
               "; ".join(suspicious) if suspicious else "The simple rules found nothing; that does not mean everything in skills/ is safe"))

    sys.path.insert(0, str(BASE))
    from tools.run_code import run_homework

    blocked = run_homework("import os\nos.listdir('.')").startswith("⛔")
    results.append(("✅" if blocked else "❌", "run_code has a fence", "import os is blocked" if blocked else "import os was NOT blocked!"))

    multi_agent = BASE / "deploy" / "multi_agent.py"
    content = multi_agent.read_text(encoding="utf-8") if multi_agent.exists() else ""
    results.append(("✅" if "recursion_limit" in content else "❌", "The agent has a recursion_limit", "Each review sub-agent runs at most 25 steps"))
    results.append(("⚠️" if "SqliteSaver" in content else "✅", "The checkpointer is durable",
               "SQLite lives only on this one machine; cloud machines get replaced, so switch to PostgresSaver when you launch"))
    has_confirm = "interrupt(" in content
    results.append(("✅" if has_confirm else "❌", "An interrupt comes before the irreversible action (sending email)", "The flow stops and waits for a person before sending" if has_confirm else "No interrupt found"))
    has_verifier = "AUDITOR_PERSONA" in content
    results.append(("✅" if has_verifier else "❌", "There is an independent verification agent", "Review and audit have separate duties and inputs; an independent auditor can still miss errors" if has_verifier else "No verification agent found"))

    url = os.environ.get("HOMEWORK_MCP_URL")
    results.append(("✅" if url else "⚠️", "The homework repo MCP is reached by URL (remote MCP)",
               f"HOMEWORK_MCP_URL={url}" if url else "Right now the MCP server is started on the same machine over stdio; to use it across machines, set a remote MCP URL and configure authorization for your service"))

    missing = [f for f in ("langgraph.json", "requirements.txt", "Dockerfile", ".dockerignore") if not (BASE / f).exists()]
    results.append(("❌" if missing else "✅", "Deployment files are all there", f"Missing: {', '.join(missing)}" if missing else "langgraph.json, requirements.txt, Dockerfile, .dockerignore"))
    return results


def print_check_results() -> bool:
    results = run_checks()
    for symbol, item, note in results:
        print(f"{symbol} {item}\n     {note}")
    failed = sum(1 for r in results if r[0] == "❌")
    print(f"\n{'🚫 ' + str(failed) + ' item(s) failed. Fix them before launch' if failed else '🎉 No ❌. Handle the ⚠️ items before launch'}")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if print_check_results() else 1)
