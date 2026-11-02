"""skill_loader：AI 選手冊只看「名片」，選中了才翻開內文。

漸進式揭露三層：
1. 書背（名片）：SKILL.md 開頭兩條 --- 之間的 name 和 description，約 100 token，一直在桌上
2. 內文：整份 SKILL.md，被選中才讀
3. 附錄：scripts/、references/ 裡的檔案，用到才打開
"""

from pathlib import Path

SKILLS = Path(__file__).resolve().parent / "skills"


def 讀名片(path: Path) -> dict:
    """只讀兩條 --- 之間的 name 和 description。"""
    text = Path(path).read_text(encoding="utf-8")
    card = {"name": Path(path).parent.name, "description": "", "path": str(path)}
    if text.startswith("---"):
        head = text.split("---", 2)[1]
        for line in head.strip().splitlines():
            key, _, value = line.partition(":")
            if key.strip() in ("name", "description"):
                card[key.strip()] = value.strip()
    return card


def 讀內文(card: dict) -> str:
    """選中之後才翻開：名片以下的手冊內容。"""
    text = Path(card["path"]).read_text(encoding="utf-8")
    return text.split("---", 2)[2].strip() if text.startswith("---") else text


def 列出名片(只要: list[str] | None = None) -> list[dict]:
    cards = [讀名片(p) for p in sorted(SKILLS.glob("*/SKILL.md"))]
    if 只要:
        cards = [c for c in cards if Path(c["path"]).parent.name in 只要]
    return cards


def 挑手冊(model, 需求: str, cards: list[dict]) -> dict:
    """把所有名片給模型看，讓它挑一本；回傳被挑中的那張名片。"""
    清單 = "\n".join(f"- {c['name']}：{c['description']}" for c in cards)
    回答 = model.invoke(
        "你要替下面的批改需求挑一本最適合的手冊。\n"
        f"批改需求：{需求}\n\n"
        f"手冊名片：\n{清單}\n\n"
        "只回答手冊的 name，不要其他字。"
    ).text.strip()
    提到的 = [(回答.find(c["name"]), c) for c in cards if c["name"] in 回答]
    return min(提到的, key=lambda x: x[0])[1] if 提到的 else cards[0]
