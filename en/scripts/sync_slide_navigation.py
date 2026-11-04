"""Rebuild slide numbers and the bottom navigation from the current order of the HTML sections; stable section ids are kept.

Usage: uv run python en/scripts/sync_slide_navigation.py
Add --check to only check without changing files. Chapters come from data-track; supplementary slides are marked data-optional="true".
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = re.compile(r'<section\b[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>.*?</section>', re.S)
COLORS = {"sec1": "var(--blue)", "sec2": "var(--green)", "sec3": "var(--orange)", "sec4": "var(--neutral)"}


def attr(section: str, name: str, default: str = "") -> str:
    found = re.search(rf'\b{re.escape(name)}="([^"]*)"', section.split(">", 1)[0])
    return html.unescape(found[1]) if found else default


def chapter(section: str) -> tuple[str, str]:
    if attr(section, "data-optional") == "true":
        return "Supplementary", "var(--ink2)"
    classes = attr(section, "class").split()
    kind = next((c for c in classes if c in COLORS), "")
    label = attr(section, "data-track") or {"sec1": "Concepts & Experiments", "sec2": "Flow & Practice", "sec3": "Integration & Practice", "sec4": "System Design"}.get(kind, "Opening")
    return label, COLORS.get(kind, "var(--ink2)")


def sync(source: str) -> str:
    sections = SECTIONS.findall(source)
    if not sections:
        raise ValueError("No slide sections found")
    total = len(sections)
    titles = [attr(s, "data-title", f"Slide {i + 1}") for i, s in enumerate(sections)]
    ids = [attr(s, "id") for s in sections]
    if not all(ids) or len(set(ids)) != total:
        raise ValueError("Every slide needs a unique stable id")
    positions = [120 + i * 1320 / max(total - 1, 1) for i in range(total)]
    groups = []
    for i, section in enumerate(sections):
        key = chapter(section)
        if groups and groups[-1][2] == key:
            groups[-1][1] = i
        else:
            groups.append([i, i, key])
    rails = []
    for first, last, (label, color) in groups:
        left = positions[first]
        right = positions[last]
        rails.append(f'<i class="rb" style="left:{left:.1f}px;width:{max(right-left, 2):.1f}px;background:{color}"></i>')
        # A narrow single-slide section keeps only its tick, so chapter names do not overlap.
        if right - left >= 160:
            width = min(260, right - left)
            rails.append(f'<i class="sl" style="left:{(left+right)/2:.1f}px;width:{width:.1f}px;margin-left:{-width/2:.1f}px;color:{color}">{html.escape(label)}</i>')
    for i, (section, title) in enumerate(zip(sections, titles)):
        x = positions[i]
        color = chapter(section)[1]
        label = html.escape(f"{i + 1}. {title}", quote=True)
        rails.append(f'<i class="tk" style="left:{x:.1f}px;background:{color}"></i>')
        rails.append(f'<a class="hit" href="#{i+1}" data-go="{i+1}" data-t="{label}" aria-label="Go to slide {i+1}: {html.escape(title, quote=True)}" style="left:{x:.1f}px"></a>')
    common = "".join(rails)
    replaced = iter(range(total))

    def replace(match):
        i = next(replaced)
        section = match[0]
        opening, body = section.split(">", 1)
        opening = re.sub(r'\saria-label="[^"]*"', "", opening)
        opening += f' aria-label="Slide {i+1}: {html.escape(titles[i], quote=True)}"'
        progress = f'<i class="rd" style="left:120px;width:{positions[i]-120:.1f}px;background:var(--ink2);opacity:.35"></i>'
        rail = f'<div class="rail">{progress}{common}<i class="cur" style="left:{positions[i]:.1f}px"></i><i class="cnt">{i+1} / {total}</i></div>'
        body, count = re.subn(r'<div class="rail"[^>]*>.*?</div>', lambda _: rail, body, flags=re.S)
        if count == 0 and "-new-" in ids[i]:
            body = body.replace("</section>", rail + "</section>")
        elif count != 1:
            raise ValueError(f"{ids[i]} should have exactly one rail, found {count}")
        return opening + ">" + body

    return SECTIONS.sub(replace, source)


def main():
    check = "--check" in sys.argv
    failed = False
    for path in sorted((ROOT / "slides").glob("session[12].html")):
        old = path.read_text(encoding="utf-8")
        new = sync(old)
        if check and old != new:
            print(f"Needs update: {path.name}")
            failed = True
        elif not check:
            path.write_text(new, encoding="utf-8", newline="\n")
        print(f"{path.name}: {len(SECTIONS.findall(new))} slides")
    return int(failed)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
