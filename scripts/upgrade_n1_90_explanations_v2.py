#!/usr/bin/env python3
"""升级 N1_bunpou_90.json 的 explanation，根据语义类型生成针对性干扰项辨析"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "content"
EXAM_PATH = BASE / "exams" / "N1_bunpou_90.json"
OUT_PATH = BASE / "exams" / "N1_bunpou_90.json"


def extract_grammar_point(question: str) -> str:
    m = re.search(r"(「[〜～].*?」)", question)
    if m:
        return m.group(1).strip("「」")
    m = re.search(r"([〜～][^\s「」]+)", question)
    if m:
        return m.group(1)
    return question


def extract_core_exp(exp: str) -> str:
    """从当前三段式 explanation 中提取核心语义说明"""
    # 尝试提取 【正确项】...\n【干扰项】 之间的内容
    m = re.search(r"【正确项】[^。]*。(.*?)\n【干扰项】", exp, re.S)
    if m:
        core = m.group(1).strip()
        if len(core) > 5:
            return core
    # 兼容旧格式：直接返回
    return exp.strip()


def classify_and_wrong_text(ans_text: str, core: str, wrong_labels: list) -> str:
    """根据正确答案文本和核心语义，生成针对性的干扰项说明"""
    combined = (ans_text + core).lower()

    # 特殊处理：如果正确项本身就说"原因/理由"，而选项里也有"原因/理由"
    if any(k in ans_text for k in ["原因", "理由"]) and any("原因" in w or "理由" in w for w in wrong_labels):
        return "本句型确实表达因果关系中的'原因'一面，但它强调的是'强烈强调前项正是导致后项的真正原因'这一语气（类似から的加强版），不是泛泛陈述原因；同时也不是转折对比或愿望命令。"

    # 1. 禁止/规范
    if any(k in combined for k in ["禁止", "不得", "不应", "べから", "まじき", "たりとも"]):
        return "本句型表达规范、禁止或最低限度的限制，不是说明因果关系、转折对比，也不是表达愿望或命令请求。"

    # 2. 不得不/被迫/客观情势/必然发生
    if any(k in combined for k in ["不得不", "被迫", "余儀なく", "やむを得", "禁じえ", "ずにはすま", "ないことには", "必然", "自然情勢", "強烈意志", "ずにはおか"]):
        return "本句型强调因外在情势、义务或强烈意志而必然发生，不是单纯陈述主观原因、转折对比或愿望命令。"

    # 3. 刚一...就.../时间紧接
    if any(k in combined for k in ["刚", "一發", "早いか", "や否や", "そばから", "かと思うと", "最後"]):
        return "本句型描述两个动作在时间上紧密接连或条件-结果的连锁，不是表达原因理由、转折对比或愿望命令。"

    # 4. 即使/最低限度/让步
    if any(k in combined for k in ["即使", "至少", "ないまでも", "であれ", "いかんによら", "いかんにかか", "なしに", "をおいて"]):
        return "本句型表达让步、最低限度或无条件，不是因果关系、转折对比或愿望命令。"

    # 5. 倾向/习惯性
    if any(k in combined for k in ["傾向", "容易", "往往会", "きらい", "がち", "っぽい", "気味", "めく"]):
        return "本句型表达某种反复出现的倾向或状态，不是一次性原因、转折对比或愿望命令。"

    # 6. 程度评价/之极/不堪/强烈情感（排除"原因""理由""導致"）
    if any(k in combined for k in ["極み", "至り", "この上", "たまらない", "ならない", "しようがない", "にたえ", "堪え", "強烈", "持續不斷", "極ま"]) and not any(k in combined for k in ["原因", "理由", "導致", "から"]):
        return "本句型表达某种情绪或状态达到极点，属于程度评价，不是原因理由、转折对比或愿望命令。"

    # 13. 表面/样子/夸张描写/无视/不顾（但"沾满"类属于物理状态，单独处理）
    if any(k in combined for k in ["看起來", "幾乎", "簡直", "好像", "誇張", "實際", "貌", "振り", "ばかりに", "めく", "無視", "不顧", "よそに", "ものともせず"]):
        return "本句型用于描写表面样子、夸张、虚拟状态，或表示无视、不顾某种情况，不是原因理由、转折对比或愿望命令。"

    # 7. 身份/资格/方式/状态（排除"相反""出乎意料""沾满"）
    if any(k in combined for k in ["身份", "资格", "方式", "唯有", "相應", "ならでは", "にして", "にあって", "なりに", "ながらに"]) and not any(k in combined for k in ["相反", "出乎意料", "轉捩", "转折", "讓步", "姑且", "沾滿", "滿是", "全身"]):
        return "本句型围绕身份、资格、方式或状态展开，不是单纯的原因理由、转折对比或愿望命令。"

    # 8. 时间/起点/持续（放在"状态"之前优先匹配）
    if any(k in combined for k in ["自從", "轉捩點", "持续", "一發", "早いか", "や否や", "そばから", "最後", "かと思うと"]):
        return "本句型用于表达时间关系、起点或持续状态，不是原因理由、转折对比或愿望命令。"

    # 9. 物理/抽象状态（沾满、覆盖、堆满）
    if any(k in combined for k in ["沾滿", "滿是", "全身", "堆滿", "覆蓋", "遍佈", "まみれ", "だらけ", "ずくめ"]):
        return "本句型用于描述某种状态覆盖、沾满或弥漫，属于状态描写，不是原因理由、转折对比或愿望命令。"

    # 10. 出乎意料/反转/对比
    if any(k in combined for k in ["相反", "出乎意料", "預期", "反轉", "思いきや", "にもかかわらず", "反して", "とは裏腹"]):
        return "本句型表达结果与预期相反或形成对照，不是单纯的原因理由或愿望命令；注意与表达因果的句型区分。"

    # 11. 转折/让步（本身）
    if any(k in combined for k in ["转折", "雖然", "但是", "つつも", "ながらも", "にもかかわらず", "反して", "いながら", "讓步", "姑且", "いざしらず", "ながらも"]):
        return "本句型确实表达转折或让步，但它不是表达原因理由、愿望命令；注意与单纯表示因果的句型区分。"

    # 12. 条件/不可或缺/判断/双重否定委婉/值得
    if any(k in combined for k in ["不可或缺", "條件", "必要", "なくして", "あってこそ", "なしに", "をおいて", "おいて", "決ま", "相違", "値する", "足る", "足りる", "なくもない", "至って", "至る", "すら", "双重否定", "委婉"]):
        return "本句型强调条件、必要性、判断、双重否定委婉、价值判断或极端示例，不是单纯的原因理由、转折对比或愿望命令。"

    # 13. 列举/示例/定义/极端强调
    if any(k in combined for k in ["列舉", "例舉", "所謂", "定義", "とは", "というのは", "をはじめ", "など", "や/", "极端", "連這種", "すら", "さえ", "至って", "至る"]):
        return "本句型用于解释定义、举例、列举或举极端例子强调，不是表达原因理由、转折对比或愿望命令。"

    # 14. 比喻/比较/转换说法
    if any(k in combined for k in ["比喻", "好比", "與其", "不如", "言うより", "というより", "と言えば", "と言ったら", "思いきや"]):
        return "本句型用于比喻、比较或转换说法，不是表达原因理由、转折对比或愿望命令。"

    # 15. 结果/结局/始末（排除"原因/理由"类正确项）
    if any(k in combined for k in ["結果", "結局", "始末", "ようがない", "仕様がない", "ずじまい", "損ねる", "そびれる", "かねる"]) and not any(k in ans_text for k in ["原因", "理由"]):
        return "本句型表达某种结果、结局或无法挽回的状态，不是原因理由、转折对比或愿望命令。"

    # 默认
    return "本句型表达的是特定语义关系，不是泛泛的原因理由、转折对比或愿望命令；学习时应抓住其核心功能和典型接续。"


def upgrade_meaning_exp(q: dict) -> str:
    gp = extract_grammar_point(q["question"])
    options = q["options"]
    ans_idx = q.get("answer", 0)
    ans_text = options[ans_idx] if 0 <= ans_idx < len(options) else ""
    core = extract_core_exp(q.get("explanation", ""))

    wrong_labels = [opt for i, opt in enumerate(options) if i != ans_idx]
    wrong_list = ", ".join(f"「{w}」" for w in wrong_labels)
    wrong_text = classify_and_wrong_text(ans_text, core, wrong_labels)

    # 特殊：如果正确项含"原因/理由"而选项里也有"原因/理由"，避免"并非表达原因/理由"的矛盾
    if any(k in ans_text for k in ["原因", "理由"]) and any("原因" in w or "理由" in w for w in wrong_labels):
        other_wrong = [w for w in wrong_labels if "原因" not in w and "理由" not in w]
        other_list = ", ".join(f"「{w}」" for w in other_wrong)
        return (
            f"【考点】{gp} 的含义辨析。\n"
            f"【正确项】{ans_text}。{core}\n"
            f"【干扰项】本句型不是一般意义上的「原因/理由」，更不是 {other_list}。{wrong_text}"
        )

    return (
        f"【考点】{gp} 的含义辨析。\n"
        f"【正确项】{ans_text}。{core}\n"
        f"【干扰项】本句型并非表达 {wrong_list}。{wrong_text}"
    )


def classify_pattern_wrong(ans_text: str, wrong_patterns: list) -> str:
    """根据正确接续方式，指出每个错误选项具体错在哪里"""
    ans = ans_text.lower()
    remarks = []
    for wp in wrong_patterns:
        w = wp.lower()
        # 错误类型判断
        if "動詞辭書形" in w and ("普通形" in ans or "名詞" in ans or "イ形容詞" in ans or "ナ形容詞" in ans):
            remarks.append(f"「{wp}」只適用於純動詞句型，不能套用於本句型")
        elif "普通形" in w and ("名詞" in ans or "動詞辭書形" not in ans and "普通形" not in ans):
            remarks.append(f"「{wp}」範圍過寬，本句型不接所有普通形")
        elif "名詞" in w and "名詞" not in ans:
            remarks.append(f"「{wp}」錯誤地將名詞直接接入，本句型不接名詞")
        elif "動詞原形＋こと" in w or "动词原形 + こと" in wp:
            remarks.append(f"「{wp}」是形式名詞化結構，本句型不經由こと接續")
        elif "名词 + の" in wp or "名詞＋の" in wp:
            remarks.append(f"「{wp}」是名詞修飾結構，不適用於本句型的固定接續")
        elif "形容词 + くて" in wp or "イ形容詞＋くて" in wp:
            remarks.append(f"「{wp}」是形容詞的て形連接，本句型不接續形容詞て形")
        elif "な形容詞" in w or "ナ形容詞" in w:
            if "名詞" in ans or "普通形" in ans:
                remarks.append(f"「{wp}」雖與名詞修飾有關，但不符本句型要求")
            else:
                remarks.append(f"「{wp}」是ナ形容詞接續形式，本句型不接ナ形容詞")
        elif "動詞て形" in w or "動詞た形" in w or "動詞ない形" in w:
            if "動詞" in ans:
                remarks.append(f"「{wp}」是動詞的特定活用形，本句型要求「{ans_text.split('＋')[0]}」")
            else:
                remarks.append(f"「{wp}」涉及動詞活用形，本句型不接該形態")
        elif "名詞＋で" in w or "名词 + で" in wp:
            remarks.append(f"「{wp}」是で格標記，本句型不使用で接續")
        elif "名詞＋に" in w or "名词 + に" in wp:
            remarks.append(f"「{wp}」是に格標記，本句型不使用に接續")
        elif "名詞＋を" in w or "名词 + を" in wp:
            remarks.append(f"「{wp}」是を格標記，本句型不使用を接續")
        else:
            remarks.append(f"「{wp}」不符合该句型的接续要求")
    return "；".join(remarks)


def upgrade_pattern_exp(q: dict) -> str:
    gp = extract_grammar_point(q["question"])
    options = q["options"]
    ans_idx = q.get("answer", 0)
    ans_text = options[ans_idx] if 0 <= ans_idx < len(options) else ""
    core = extract_core_exp(q.get("explanation", ""))

    wrong_patterns = [opt for i, opt in enumerate(options) if i != ans_idx]
    wrong_list = ", ".join(f"「{w}」" for w in wrong_patterns)
    wrong_text = classify_pattern_wrong(ans_text, wrong_patterns)

    return (
        f"【考点】{gp} 的接续方式。\n"
        f"【正确项】{ans_text}。{core}\n"
        f"【干扰项】{wrong_list} 均不符合该句型的接续要求。{wrong_text}。"
        f"学习时应牢记该句型的固定前接形式，避免用通用结构套用。"
    )


def main():
    data = json.loads(EXAM_PATH.read_text(encoding="utf-8"))
    for sec in data.get("sections", []):
        for q in sec.get("questions", []):
            qtype = q.get("type", "")
            if qtype == "grammar_meaning":
                q["explanation"] = upgrade_meaning_exp(q)
            elif qtype == "grammar_pattern":
                q["explanation"] = upgrade_pattern_exp(q)
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Upgraded {} questions.".format(sum(len(s.get("questions", [])) for s in data.get("sections", []))))


if __name__ == "__main__":
    main()
