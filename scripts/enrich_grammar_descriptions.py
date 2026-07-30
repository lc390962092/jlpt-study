#!/usr/bin/env python3
"""为 N1-N5 grammar JSON 统一生成 description 字段，并记录缺失数据"""
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "content"
LEVELS = ['N1', 'N2', 'N3', 'N4', 'N5']


def infer_pattern(grammar: str) -> str:
    """根据语法名推断一个最基础的接续"""
    g = grammar.replace('〜', '').replace('~', '').strip()
    if 'です' in g:
        return '名詞/な形容詞語幹 + です'
    if 'ます' in g:
        return '動詞ます形 + ます'
    if 'ない' in g and ('ければ' in g or 'ければならない' in g):
        return '動詞/い形容詞/な形容詞/名詞 + ければならない'
    if g.endswith('たい'):
        return '動詞ます形語幹 + たい'
    if g.endswith('たがる'):
        return '動詞ます形語幹 + たがる'
    if g.endswith('やすい') or g.endswith('にくい'):
        return '動詞ます形語幹 + やすい／にくい'
    if g.endswith('そうだ'):
        return '動詞ます形語幹/い形容詞語幹/な形容詞語幹 + そうだ（様態）'
    if g.endswith('らしい'):
        return '動詞/い形容詞/な形容詞/名詞 + らしい'
    if g.endswith('ようだ'):
        return '動詞/い形容詞/な形容詞/名詞 + ようだ'
    if g.endswith('そうにない'):
        return '動詞ます形語幹 + そうにない'
    if g.endswith('すぎる'):
        return '動詞ます形語幹/い形容詞語幹/な形容詞語幹 + すぎる'
    if g.endswith('ながら'):
        return '動詞ます形語幹 + ながら'
    if g.endswith('ばかり'):
        return '動詞た形/て形 + ばかり'
    if g.endswith('ところ'):
        return '動詞辞書形/た形/ている + ところ'
    if g.endswith('ば'):
        return '動詞ば形 + ば'
    if g.endswith('のに'):
        return '動詞/い形容詞/な形容詞/名詞 + のに'
    if g.endswith('ので'):
        return '動詞/い形容詞/な形容詞/名詞 + ので'
    if g.endswith('から'):
        return '動詞/い形容詞/な形容詞/名詞 + から'
    if g.endswith('と'):
        return '動詞辞書形/ない形 + と'
    if g.endswith('たら'):
        return '動詞た形 + たら'
    if g.endswith('なら'):
        return '名詞/動詞辞書形 + なら'
    if g.endswith('ても'):
        return '動詞て形 + ても'
    if g.endswith('でも'):
        return '名詞/な形容詞語幹 + でも'
    if g.endswith('に'):
        return '動詞辞書形/名詞 + に'
    if g.endswith('を'):
        return '名詞 + を'
    if g.endswith('が'):
        return '名詞 + が'
    return '（接续待补充）'


def infer_compare(grammar: str, meaning: str) -> str:
    """生成一个泛泛的对比说明"""
    return '（相关近义表达请结合语境区分）'


def build_usage_note(grammar: str, meaning: str) -> str:
    """根据语法名和含义生成用法提示"""
    g = grammar.lower()
    m = meaning.lower()
    notes = []

    if any(k in g for k in ['です', 'ます', 'でした', 'ました']):
        notes.append('礼貌体基本表达')
    if any(k in g for k in ['ない', 'ぬ', 'ず', 'ずに']):
        notes.append('注意否定形式')
    if any(k in g for k in ['たい', 'たがる', 'ほしい', 'ほしがる']):
        notes.append('表达愿望或第三人称愿望')
    if any(k in g for k in ['やすい', 'にくい', 'すぎる', 'すぎる']):
        notes.append('描述动作难易或程度')
    if any(k in g for k in ['そうだ', 'ようだ', 'らしい', 'みたいだ']):
        notes.append('推量、样态或比喻')
    if any(k in g for k in ['ばかり', 'ところ', 'ば', 'たら', 'なら', 'と']):
        notes.append('条件或时间关系')
    if any(k in g for k in ['のに', 'ので', 'から', 'けれども', 'が']):
        notes.append('因果、转折或理由')
    if any(k in g for k in ['ながら', 'つつ', 'かたわら']):
        notes.append('同时进行的动作或状态')
    if any(k in g for k in ['ても', 'でも', 'とうと', 'にしろ', 'であれ']):
        notes.append('让步或极端条件')
    if any(k in g for k in ['ものだ', 'ことだ', 'わけだ', 'はずだ']):
        notes.append('表达常识、道理或推断')
    if any(k in g for k in ['べき', 'べから', 'まじき']):
        notes.append('带有规范、义务或古语文言色彩')

    if notes:
        return '；'.join(notes) + '。'
    return ''


def build_description(entry: dict) -> str:
    parts = []
    grammar = entry.get("grammar", "")
    meaning = entry.get("meaning", "").strip()
    pattern = entry.get("pattern", "").strip() or infer_pattern(grammar)
    example = entry.get("example", "").strip()
    example_reading = entry.get("example_reading", "").strip()
    example_meaning = entry.get("example_meaning", "").strip()
    compare = entry.get("compare", "").strip() or infer_compare(grammar, meaning)

    if pattern:
        parts.append(f"【接续】{pattern}")
    if meaning:
        parts.append(f"【含义】{meaning}")

    usage_note = build_usage_note(grammar, meaning)
    if usage_note:
        parts.append(f"【用法】{usage_note}")

    if example:
        ex_text = example
        if example_reading:
            ex_text += f"\n読み：{example_reading}"
        if example_meaning:
            ex_text += f"\n訳：{example_meaning}"
        parts.append(f"【例句】\n{ex_text}")

    if compare:
        parts.append(f"【注意／对比】{compare}")

    return "\n\n".join(parts)


def main():
    report_lines = ['# 语法 description 生成报告\n']

    for level in LEVELS:
        src = BASE / f"{level}_grammar.json"
        if not src.exists():
            report_lines.append(f"\n## {level}\n文件不存在: {src}")
            continue

        data = json.loads(src.read_text(encoding="utf-8"))
        bak = BASE / f"{level}_grammar.json.bak.desc"
        shutil.copy2(src, bak)

        filled_pattern = 0
        filled_compare = 0
        missing_example = 0
        missing_example_reading = 0
        missing_example_meaning = 0

        for entry in data:
            if not entry.get("pattern"):
                entry["pattern"] = infer_pattern(entry.get("grammar", ""))
                filled_pattern += 1
            if not entry.get("compare"):
                entry["compare"] = infer_compare(entry.get("grammar", ""), entry.get("meaning", ""))
                filled_compare += 1

            if not entry.get("example"):
                missing_example += 1
            if not entry.get("example_reading"):
                missing_example_reading += 1
            if not entry.get("example_meaning"):
                missing_example_meaning += 1

            entry["description"] = build_description(entry)

        src.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        report_lines.append(f"\n## {level}")
        report_lines.append(f"- 总条目: {len(data)}")
        report_lines.append(f"- 生成 description: {len(data)}")
        report_lines.append(f"- 自动补充 pattern: {filled_pattern}")
        report_lines.append(f"- 自动补充 compare: {filled_compare}")
        report_lines.append(f"- 缺少 example: {missing_example}")
        report_lines.append(f"- 缺少 example_reading: {missing_example_reading}")
        report_lines.append(f"- 缺少 example_meaning: {missing_example_meaning}")
        report_lines.append(f"- 备份: {bak}")

        if missing_example:
            report_lines.append(f"\n### {level} 缺少 example 的条目")
            for entry in data:
                if not entry.get("example"):
                    report_lines.append(f"- {entry.get('id')}: {entry.get('grammar')} — {entry.get('meaning')}")

    report_path = BASE.parent / "reviews" / "grammar_description_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Report saved: {report_path}")


if __name__ == "__main__":
    main()
