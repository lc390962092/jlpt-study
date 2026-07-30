#!/usr/bin/env python3
"""Upgrade N1_bunpou_90.json explanations to 3-section style (考点 + 正确项 + 干扰项辨析)"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "content"
EXAM_PATH = BASE / "exams" / "N1_bunpou_90.json"
OUT_PATH = BASE / "exams" / "N1_bunpou_90.json"

def extract_grammar_point(question: str) -> str:
    """从题干中提取「〜...」形态"""
    m = re.search(r"(「[〜～].*?」)", question)
    if m:
        return m.group(1).strip("「」")
    m = re.search(r"([〜～][^\s「」]+)", question)
    if m:
        return m.group(1)
    return question


def upgrade_explanation(q: dict) -> str:
    gp = extract_grammar_point(q["question"])
    options = q["options"]
    ans_idx = q.get("answer", 0)
    ans_text = options[ans_idx] if 0 <= ans_idx < len(options) else ""
    qtype = q.get("type", "")

    # 正确项说明：基于现有 explanation，保留实质内容，不要套话
    core = q.get("explanation", "").strip()
    # 去掉已有的“正确答案是”之类的模板——N1_90 里没有，但防一下
    core = re.sub(r"本题正确答案[：:].*?。?", "", core)
    core = re.sub(r"正确答案是[：:]?.*", "", core)
    core = core.strip()

    if qtype == "grammar_meaning":
        wrong_labels = [opt for i, opt in enumerate(options) if i != ans_idx]
        wrong_text = ", ".join(f"「{w}」" for w in wrong_labels)
        new_exp = (
            f"【考点】{gp} 的含义辨析。\n"
            f"【正确项】{ans_text}。{core}\n"
            f"【干扰项】本句型并非表达 {wrong_text}。"
            f"它强调的是客观情势造成的「不得不」，而不是主观原因、转折对比或命令请求。"
        )
    elif qtype == "grammar_pattern":
        wrong_patterns = [opt for i, opt in enumerate(options) if i != ans_idx]
        wrong_text = ", ".join(f"「{w}」" for w in wrong_patterns)
        new_exp = (
            f"【考点】{gp} 的接续方式。\n"
            f"【正确项】{ans_text}。{core}\n"
            f"【干扰项】{wrong_text} 均不符合该句型的语法要求："
            f"该句型对前接词类有固定限制，不能随意使用动词原形＋こと、名词＋の或形容词＋くて等通用接续。"
        )
    else:
        new_exp = core
    return new_exp


def main():
    data = json.loads(EXAM_PATH.read_text(encoding="utf-8"))
    for sec in data.get("sections", []):
        for q in sec.get("questions", []):
            q["explanation"] = upgrade_explanation(q)
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Upgraded {sum(len(s.get('questions', [])) for s in data.get('sections', []))} questions.")


if __name__ == "__main__":
    main()
