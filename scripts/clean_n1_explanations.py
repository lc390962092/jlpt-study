#!/usr/bin/env python3
"""清洗 N1 真题解析中的模板套话，并补充基础说明"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "content"
EXAM_PATH = BASE / "exams" / "N1_bunpou_1800.json"
OUT_PATH = BASE / "exams" / "N1_bunpou_1800.json"

N1_GRAMMAR_PATH = BASE / "N1_grammar.json"


def load_n1_grammar():
    data = json.loads(N1_GRAMMAR_PATH.read_text(encoding="utf-8"))
    index = {}
    for g in data:
        grammar = g["grammar"]
        # 记录可匹配的核心片段
        forms = re.findall(r"[〜～]([^／/\s]+)", grammar)
        for f in forms:
            f = f.strip("〜～")
            if len(f) >= 2:
                index.setdefault(f, []).append(g)
    return index


def clean_template(exp: str, answer: str) -> str:
    """去掉模板套话，尽量保留实质内容"""
    # 删除常见模板
    patterns = [
        r"本题正确答案[:：]「?[^」\n]*」?。?",
        r"正确答案是[:：]?「?[^」\n]*」?。?",
        r"根据句意，[^。]*最符合上下文。其余选项：[^。]*。?",
        r"本题考查N1语法形式的辨析。正确答案是[:：]?「?[^」\n]*」?。?",
        r"本题考查「grammar_form」的用法。正确答案是[:：]?「?[^」\n]*」?。?",
    ]
    for p in patterns:
        exp = re.sub(p, "", exp)
    exp = exp.strip()

    # 如果还有明确释义，保留
    if len(exp) >= 10 and not re.search(r"正确|本题|其余选项", exp):
        return exp

    return ""


def make_fallback(answer: str, grammar_index: dict) -> str:
    """基于答案和语法库生成兜底说明"""
    # 尝试匹配语法库中的核心形态
    for form, gs in grammar_index.items():
        if form in answer or answer in form:
            g = gs[0]
            meaning = g.get("meaning", "").strip("…").strip()
            if meaning:
                return "「{}」表示{}。接续：{}. 本题中填入「{}」，使句子表达相应的语法关系。".format(
                    answer, meaning, g.get("pattern", "（见语法库）"), answer
                )

    # 通用兜底
    return "「{}」是本题正确选项。请结合题干语境，理解该表达在句中的语法功能与含义。".format(answer)


def main():
    grammar_index = load_n1_grammar()
    data = json.loads(EXAM_PATH.read_text(encoding="utf-8"))

    total = 0
    cleaned = 0
    fallbacked = 0
    still_template = 0

    for sec in data.get("sections", []):
        for q in sec.get("questions", []):
            total += 1
            exp = q.get("explanation", "")
            answer = q.get("options", [])[q.get("answer", 0)] if q.get("answer") is not None else ""

            # 判断是否是模板
            is_template = (
                len(exp) < 15
                or "正确答案是" in exp
                or "本题正确答案" in exp
                or "本题考查" in exp
                or "根据句意" in exp
                or "其余选项" in exp
            )

            if not is_template:
                continue

            new_exp = clean_template(exp, answer)
            if new_exp:
                q["explanation"] = new_exp
                cleaned += 1
            else:
                q["explanation"] = make_fallback(answer, grammar_index)
                fallbacked += 1
                if "正确" in q["explanation"] or "本题" in q["explanation"]:
                    still_template += 1

    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Total questions: {}".format(total))
    print("Cleaned: {}, Fallback: {}, Still template: {}".format(cleaned, fallbacked, still_template))


if __name__ == "__main__":
    main()
