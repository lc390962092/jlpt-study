#!/usr/bin/env python3
"""
批量修复 N1-N5 语法 description 的【用法】和【注意/对比】字段。
根据 grammar/meaning 关键词分类，替换原来"条件或时间关系"这类套话，
并给出对应近似表达。不修改例句原文，避免批量制造错误例句。
"""
import json
import shutil
from pathlib import Path
from typing import Optional

BASE = Path(__file__).resolve().parent.parent / "content"


class GrammarClass:
    def __init__(self, name: str, keywords: list[str], usage: str, compare: str):
        self.name = name
        self.keywords = keywords
        self.usage = usage
        self.compare = compare


CLASSES: list[GrammarClass] = [
    # 时间/紧接
    GrammarClass(
        "时间紧接",
        ["そばから", "が早いか", "や否や", "かと思う", "思いきや", "たかと", "が最後", "た末", "た結果", "に至って", "を経て"],
        "强调前项动作刚一发生，后项立即随之发生；或表示经过某过程后得出某种结果。多带意外、必然或总结语气。",
        "~そばから（刚做完又重复）、~や否や（几乎同时）、~かと思ったら（意外转折）、~た末（经过较长过程）",
    ),
    # 条件/让步
    GrammarClass(
        "条件让步",
        ["ともな", "ないまでも", "ながらも", "つつも", "たりとも", "であれ", "いかんに", "いかんによらず", "かぎり", "さえ", "すら", "でさえ", "ても", "たとえ", "としても", "にしても"],
        "前项提出条件、极端情况或让步，后项表达与之相反或不受其影响的结果。",
        "~ても（一般让步）、~たとしても（假设让步）、~にしても（评价性让步）、~であれ（极端列举）",
    ),
    # 强烈情感/极点
    GrammarClass(
        "强烈情感",
        ["たまらない", "てならない", "しようがない", "仕様がない", "極ま", "の至り", "の極み", "堪え", "にたえ", "がひどい", "て堪らない"],
        "表达说话人强烈的情感、感受达到极点，常用于心理、生理反应或难以抑制的心情。",
        "~てならない（不由自主）、~に堪えない（不堪忍受）、~の至り（极为荣幸/难过）",
    ),
    # 倾向/状态
    GrammarClass(
        "倾向状态",
        ["きらい", "がち", "気味", "めく", "だらけ", "まみれ", "ずくめ", "がちだ", "っぽい", "気味だ"],
        "描述事物或人具有的某种倾向、状态、外貌特征，常带负面或消极评价。",
        "~がち（习惯性负面倾向）、~気味（稍微偏向某种状态）、~だらけ（充满负面事物）、~っぽい（像/容易）",
    ),
    # 义务/必然/价值判断
    GrammarClass(
        "义务必然",
        ["ずにはすま", "ずにはおか", "ないことには", "に決まって", "に相違", "やむを得", "べき", "べく", "べから", "べし", "まじき", "に足る", "に足りる", "に値する", "に堪え", "にたえる", "に違いない"],
        "表达义务、必然性、推断或价值判断。书面语色彩较强，语气较硬。",
        "~べき（主观义务）、~に違いない（有依据推断）、~に決まっている（强烈确信）、~わけにはいかない（情理上不能）",
    ),
    # 否定/双重否定
    GrammarClass(
        "否定条件",
        ["ずには", "ないことに", "なしに", "ずに", "ないでは", "ずくめ", "ないものではない"],
        "通过否定形式表达条件、伴随或部分肯定。'ずには~ない'常构成双重否定表必然。",
        "~ずにはいられない（情不自禁）、~ないことには（不……就无法）、~ないものではない（并非不/也可以）",
    ),
    # 书面/古语文体
    GrammarClass(
        "书面古语",
        ["かたわら", "がてら", "余儀なく", "禁じえ", "なり ", "なりに", "なりの", "ずとも", "ともすれば", "ともなると", "からある", "からの"],
        "偏书面、正式或略带古语的表达，日常口语中较少单独使用。",
        "~かたわら（书面'一边…一边'）、~がてら（顺便）、~なりに（以自己的方式）",
    ),
    # 引用/说明
    GrammarClass(
        "引用说明",
        ["とは", "というのは", "というより", "と言うより", "と言えば", "と言ったら", "というものだ", "ということだ"],
        "用于解释、引用、转述或下定义；也可表达'与其说A不如说B'的评价。",
        "~とは（下定义/惊讶）、~というより（比较选择）、~と言えば（话题联想）",
    ),
    # 原因/理由
    GrammarClass(
        "原因理由",
        ["だけに", "だけあって", "ゆえ", "故に", "こととて", "ことだし", "ものだから", "もので", "ことだし"],
        "前项提出原因或背景，后项表达由此产生的判断、结果或理所当然的评价。",
        "~だけに（正因为）、~ものだから（辩解理由）、~こととて（书面理由）",
    ),
    # 限定/追加
    GrammarClass(
        "限定追加",
        ["ならでは", "にしろ", "にせよ", "にしては", "からして", "からいうと", "に関して", "につけ", "につけて"],
        "从某个立场、范围或身份出发进行评价，强调'只有…才…'或'从…来看'。",
        "~ならでは（只有…才有的）、~にしては（从…来看却…）、~からして（从…就看得出）",
    ),
    # 推量/传闻
    GrammarClass(
        "推量传闻",
        ["らしい", "みたいだ", "ようだ", "そうだ", "とのこと", "という", "に違いない", "に決まっている"],
        "根据外观、传闻或证据进行推断。注意根据信息来源选择表达方式。",
        "~ようだ（主观推测/比喻）、~らしい（典型特征/传闻）、~そうだ（听说/样态）",
    ),
    # 使役/被动/授受
    GrammarClass(
        "使役被动授受",
        ["せる", "させる", "れる", "られる", "てもらう", "てくれる", "てあげる", "ていただく"],
        "属于复合表达方式，涉及使役、被动或授受关系，注意主语和受益方向。",
        "~させる（使役）、~られる（被动/可能/尊敬/自发）、~てもらう（请求受益）",
    ),
    # 目的/意图
    GrammarClass(
        "目的意图",
        ["ために", "ようと", "つもり", "つもりだ", "はずだ", "はずがない", "わけだ", "わけがない", "わけではない", "に越したことはない"],
        "表达目的、意图、预定或逻辑推断。'わけ'系列注意与'はず'的语义差别。",
        "~ために（目的/原因）、~ようとする（试图）、~わけだ（当然/解释）、~はずだ（推断/预定）",
    ),
]


def classify(grammar: str, meaning: str) -> Optional[GrammarClass]:
    g = grammar.lower()
    m = meaning.lower()
    best: Optional[GrammarClass] = None
    best_score = 0
    for cls in CLASSES:
        score = sum(1 for k in cls.keywords if k in g or k in m)
        if score > best_score:
            best_score = score
            best = cls
    return best if best_score > 0 else None


def build_usage_note(grammar: str, meaning: str) -> str:
    cls = classify(grammar, meaning)
    if cls:
        return cls.usage
    # fallback: 根据 meaning 给通用说明
    if "应该" in meaning or "不应该" in meaning:
        return "用于表达说话人的判断、建议或义务，语气较直接。"
    if "不必" in meaning or "不需要" in meaning:
        return "用于打消必要性，表达'没有必要做某事'。"
    if "感慨" in meaning:
        return "表达对自然规律、人生道理的感慨，带有说话人情绪。"
    if "推断" in meaning or "一定" in meaning:
        return "根据某种依据进行推断，表达较高程度的确定性。"
    if "比较" in meaning or "与其说" in meaning:
        return "用于比较两个事物，选择其中一方作为更合适的说法。"
    return "结合接续和语境使用，注意与近义表达在语气和使用场景上的区别。"


def build_compare(grammar: str, meaning: str, original: str) -> str:
    cls = classify(grammar, meaning)
    if cls:
        return cls.compare
    if original and "相关近义表达" not in original:
        return original
    return "注意与近义表达在接续、语气及使用场景上的差异。"


def enrich_entry(entry: dict) -> dict:
    grammar = entry.get("grammar", "")
    meaning = entry.get("meaning", "")
    pattern = entry.get("pattern", "").strip()
    example = entry.get("example", "").strip()
    example_reading = entry.get("example_reading", "").strip()
    example_meaning = entry.get("example_meaning", "").strip()
    original_compare = entry.get("compare", "").strip()

    usage = build_usage_note(grammar, meaning)
    compare = build_compare(grammar, meaning, original_compare)

    parts = []
    if pattern:
        parts.append(f"【接续】{pattern}")
    if meaning:
        parts.append(f"【含义】{meaning}")
    if usage:
        parts.append(f"【用法】{usage}")

    # 例句部分保留原文
    if example:
        ex_text = example
        if example_reading:
            ex_text += f"\n読み：{example_reading}"
        if example_meaning:
            ex_text += f"\n訳：{example_meaning}"
        parts.append(f"【例句】\n{ex_text}")

    if compare:
        parts.append(f"【注意／对比】{compare}")

    entry["description"] = "\n\n".join(parts)
    entry["compare"] = compare
    return entry


def process_file(filename: str):
    src = BASE / filename
    if not src.exists():
        print(f"Skip {filename}: not found")
        return

    bak = src.with_suffix(src.suffix + ".bak.enrich_desc")
    shutil.copy2(src, bak)

    data = json.loads(src.read_text(encoding="utf-8"))
    for entry in data:
        enrich_entry(entry)

    src.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Enriched {len(data)} entries in {filename}; backup: {bak.name}")


def main():
    for name in ["N1_grammar.json", "N2_grammar.json", "N3_grammar.json", "N4_grammar.json", "N5_grammar.json"]:
        process_file(name)


if __name__ == "__main__":
    main()
