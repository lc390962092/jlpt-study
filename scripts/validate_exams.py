#!/usr/bin/env python3
"""JLPT 真题数据校验与 type 标准化脚本"""
import json
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path(__file__).resolve().parent.parent / "content" / "exams"
VALID_TYPES = {"grammar_form", "grammar_meaning", "grammar_pattern", "ordering", "application"}

# type 标准化映射规则
TYPE_NORMALIZE = {
    # 已知类型直接保留
    "grammar_form": "grammar_form",
    "grammar_meaning": "grammar_meaning",
    "grammar_pattern": "grammar_pattern",
    "ordering": "ordering",
    "application": "application",
    # 旧名 / 别名映射
    "並び替え": "ordering",
    "kanji_reading": None,      # 词汇类，不归入文法
    "kanji_usage": None,
    "context_vocabulary": None,
    "synonym": None,
    "sentence_pattern": "grammar_pattern",
}


def is_low_quality_explanation(exp: str) -> bool:
    """判断解析是否过于单薄或模板化"""
    if not exp or len(exp.strip()) < 15:
        return True
    exp = exp.strip()
    bad_patterns = [
        "正确答案是",
        "本题正确答案",
        "本题考查",
        "根据句意",
        "其余选项",
    ]
    return any(p in exp for p in bad_patterns)


def validate_file(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    level = data.get("level", "?")
    questions = []
    for sec in data.get("sections", []):
        questions.extend(sec.get("questions", []))

    report = {
        "file": path.name,
        "level": level,
        "total": len(questions),
        "type_counts": Counter(),
        "normalized_types": Counter(),
        "missing_explanation": 0,
        "low_quality_explanation": 0,
        "bad_answer": 0,
        "empty_question": 0,
        "empty_options": 0,
        "duplicate_ids": [],
        "type_unknown": Counter(),
    }

    seen_ids = defaultdict(list)
    for idx, q in enumerate(questions):
        qid = q.get("id")
        if qid:
            seen_ids[qid].append(idx)
        typ = q.get("type", "")
        report["type_counts"][typ] += 1
        normalized = TYPE_NORMALIZE.get(typ)
        if normalized:
            report["normalized_types"][normalized] += 1
        elif typ not in VALID_TYPES:
            report["type_unknown"][typ] += 1

        exp = q.get("explanation", "")
        if not exp:
            report["missing_explanation"] += 1
        elif is_low_quality_explanation(exp):
            report["low_quality_explanation"] += 1

        opts = q.get("options", [])
        ans = q.get("answer")
        if ans is None or (isinstance(ans, int) and (ans < 0 or ans >= len(opts))):
            report["bad_answer"] += 1
        if not q.get("question", "").strip():
            report["empty_question"] += 1
        if not opts or all(not str(o).strip() for o in opts):
            report["empty_options"] += 1

    report["duplicate_ids"] = [qid for qid, positions in seen_ids.items() if len(positions) > 1]
    return report


def main():
    files = sorted(BASE.glob("N*_bunpou_*.json"))
    for path in files:
        report = validate_file(path)
        print(f"=== {report['file']} (level={report['level']}) ===")
        print(f"  total questions     : {report['total']}")
        print(f"  missing explanation : {report['missing_explanation']}")
        print(f"  low-quality exp     : {report['low_quality_explanation']}")
        print(f"  bad answer index    : {report['bad_answer']}")
        print(f"  empty question      : {report['empty_question']}")
        print(f"  empty options       : {report['empty_options']}")
        print(f"  duplicate ids       : {len(report['duplicate_ids'])}")
        print(f"  original types      : {dict(report['type_counts'])}")
        print(f"  normalized types    : {dict(report['normalized_types'])}")
        print(f"  unknown types       : {dict(report['type_unknown'])}")
        print()


if __name__ == "__main__":
    main()
