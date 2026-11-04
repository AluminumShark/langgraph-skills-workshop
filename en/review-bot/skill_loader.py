"""skill_loader: the AI picks a handbook by looking only at its "card", and the body is opened only after it is picked.

Progressive disclosure has three layers:
1. Card: the name and description between the two --- lines at the top of SKILL.md. They are given to the model when it picks
2. Body: the whole SKILL.md, read only after it is picked
3. Appendix: files in scripts/ and references/, opened only when needed
"""

from pathlib import Path

SKILLS = Path(__file__).resolve().parent / "skills"


def read_card(path: Path) -> dict:
    """Read only the name and description between the two --- lines."""
    text = Path(path).read_text(encoding="utf-8")
    card = {"name": Path(path).parent.name, "description": "", "path": str(path)}
    if text.startswith("---"):
        head = text.split("---", 2)[1]
        for line in head.strip().splitlines():
            key, _, value = line.partition(":")
            if key.strip() in ("name", "description"):
                card[key.strip()] = value.strip()
    return card


def read_body(card: dict) -> str:
    """Opened only after the handbook is picked: the handbook content below the card."""
    text = Path(card["path"]).read_text(encoding="utf-8")
    return text.split("---", 2)[2].strip() if text.startswith("---") else text


def list_cards(only: list[str] | None = None) -> list[dict]:
    cards = [read_card(p) for p in sorted(SKILLS.glob("*/SKILL.md"))]
    if only:
        cards = [c for c in cards if Path(c["path"]).parent.name in only]
    return cards


def pick_handbook(model, request: str, cards: list[dict]) -> dict:
    """Show the model all the cards and let it pick one. Returns the card that was picked."""
    if not cards:
        raise ValueError("No handbook is available. Write a SKILL.md first, then list the cards.")
    card_list = "\n".join(f"- {c['name']}: {c['description']}" for c in cards)
    answer = model.invoke(
        "Pick the one handbook that best fits the review request below.\n"
        f"Review request: {request}\n\n"
        f"Handbook cards:\n{card_list}\n\n"
        "Answer with only the handbook's name, no other words."
    ).text.strip()
    name = answer.strip("`\"' \n")
    options = {c["name"]: c for c in cards}
    if name not in options:
        raise ValueError(f"The model did not return exactly one valid handbook name: {answer!r}. Valid names: {list(options)}. Check the cards and the model output; no handbook was picked this time.")
    return options[name]
