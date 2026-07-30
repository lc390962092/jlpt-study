#!/usr/bin/env python3
"""为 N1_grammar.json 的每条语法生成统一的 description 字段"""
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "content"
SRC = BASE / "N1_grammar.json"
BAK = BASE / "N1_grammar.json.bak.grammar_desc"


def build_description(entry: dict) -> str:
    parts = []
    grammar = entry.get("grammar", "")
    meaning = entry.get("meaning", "").strip()
    pattern = entry.get("pattern", "").strip()
    example = entry.get("example", "").strip()
    example_reading = entry.get("example_reading", "").strip()
    example_meaning = entry.get("example_meaning", "").strip()
    compare = entry.get("compare", "").strip()

    # 接续
    if pattern:
        parts.append(f"【接续】{pattern}")

    # 含义
    if meaning:
        parts.append(f"【含义】{meaning}")

    # 用法说明：根据 grammar/meaning 补充常见注意点
    usage_note = build_usage_note(grammar, meaning)
    if usage_note:
        parts.append(f"【用法】{usage_note}")

    # 例句
    if example:
        ex_text = example
        if example_reading:
            ex_text += f"\n読み：{example_reading}"
        if example_meaning:
            ex_text += f"\n訳：{example_meaning}"
        parts.append(f"【例句】\n{ex_text}")

    # 对比/注意
    if compare:
        parts.append(f"【注意／对比】{compare}")

    return "\n\n".join(parts)


def build_usage_note(grammar: str, meaning: str) -> str:
    """根据语法条目生成一些通用的接续或用法提醒"""
    notes = []
    g = grammar.lower()
    m = meaning.lower()

    # 古語／書面語標記
    if any(k in g or k in m for k in ["べから", "べし", "まじき", "なり ", "ずくめ", "かたわら", "がてら", "余儀なく", "禁じえ"]):
        notes.append("偏書面、正式或古語色彩")

    # 否定／雙重否定
    if any(k in g for k in ["ずには", "ないことに", "なしに", "ずくめ"]):
        notes.append("常與否定或條件呼應")

    # 感情極點
    if any(k in g for k in ["たまらない", "てならない", "しようがない", "極ま", "の至り", "の極み", "堪え", "にたえ"]):
        notes.append("多表達強烈情感或極致狀態")

    # 傾向／狀態
    if any(k in g for k in ["きらい", "がち", "気味", "めく", "だらけ", "まみれ", "ずくめ"]):
        notes.append("用於描述傾向、狀態或覆蓋程度")

    # 剛一…就…
    if any(k in g for k in ["そばから", "が早いか", "や否や", "かと思う", "思いきや", "たかと"]):
        notes.append("強調時間上的緊接或出乎意料")

    # 條件／讓步
    if any(k in g for k in ["ともな", "ないまでも", "ながらも", "つつも", "たりとも", "であれ", "いかんに"]):
        notes.append("屬於條件、讓步或極端列舉表達")

    # 義務／必然
    if any(k in g for k in ["ずにはすま", "ずにはおか", "ないことには", "に決まって", "に相違", "やむを得"]):
        notes.append("表達義務、必然性或強烈推斷")

    # 價值／判斷
    if any(k in g for k in ["に足る", "に足りる", "に値する", "べき", "べく", "に堪え", "にたえる"]):
        notes.append("用於價值判斷、義務或資格說明")

    if notes:
        return "；".join(notes) + "。"
    return ""


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    shutil.copy2(SRC, BAK)
    print(f"Backup created: {BAK}")

    for entry in data:
        entry["description"] = build_description(entry)

    SRC.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Enriched {len(data)} grammar entries with description.")


if __name__ == "__main__":
    main()
