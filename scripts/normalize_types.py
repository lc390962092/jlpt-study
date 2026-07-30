#!/usr/bin/env python3
"""把真题的 type 字段统一成标准分类，并把 N5 的语法点名迁移到 grammar_point 字段"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "content" / "exams"
VALID_TYPES = {"grammar_form", "grammar_meaning", "grammar_pattern", "ordering", "application"}

TYPE_NORMALIZE = {
    # 明确分类
    "grammar_form": "grammar_form",
    "grammar_meaning": "grammar_meaning",
    "grammar_pattern": "grammar_pattern",
    "ordering": "ordering",
    "application": "application",
    "並び替え": "ordering",
    "sentence_pattern": "grammar_pattern",
    # 词汇类题型，不属于当前文法题库，按 None 处理
    "kanji_reading": None,
    "kanji_usage": None,
    "context_vocabulary": None,
    "synonym": None,
}


def normalize_type(old_type: str) -> str | None:
    if old_type in VALID_TYPES:
        return old_type
    return TYPE_NORMALIZE.get(old_type)


def process_file(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    level = data.get("level", "")
    changed_type = 0
    extracted_grammar_point = 0
    unknown_types = set()

    for sec in data.get("sections", []):
        for q in sec.get("questions", []):
            old = q.get("type", "")
            new = normalize_type(old)

            if new is None:
                # N5 用语法点名作为 type，迁移到 grammar_point
                if level == "N5":
                    q["grammar_point"] = old
                    q["type"] = "grammar_form"
                    # 排序题特殊处理：题干含括弧多个空或选项为排序
                    if "並び替え" in old or old == "ordering":
                        q["type"] = "ordering"
                    extracted_grammar_point += 1
                else:
                    unknown_types.add(old)
                continue

            if new != old:
                q["type"] = new
                changed_type += 1

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{path.name}: changed {changed_type} type(s), extracted {extracted_grammar_point} grammar_point(s)")
    if unknown_types:
        print(f"  unknown types left: {unknown_types}")


def main():
    for path in sorted(BASE.glob("N*_bunpou_*.json")):
        process_file(path)


if __name__ == "__main__":
    main()
