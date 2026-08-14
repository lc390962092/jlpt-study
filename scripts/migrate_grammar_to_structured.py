#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 N1-N5 grammar JSON 中的长 description 字段拆成结构化字段。
保留旧字段兼容，新增：
  grammar_cn, meaning, pattern, usage, examples(list), common_mistakes(list), comparison, notes
"""
import json
import re
from pathlib import Path

BASE = Path('/mnt/e/kimicode/jlpt-study/content')
LEVELS = ['N1', 'N2', 'N3', 'N4', 'N5']


def extract_section(text, title):
    """提取 【标题】... 到下一个 【 之前的文本"""
    pattern = rf'【{re.escape(title)}】\s*(.*?)\s*(?=\n\n【|\n【|$)'
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        return ''
    return m.group(1).strip()


def split_examples(section_text):
    """
    解析例句区域。格式通常是：
      幸福とは何か、考えたことはあるか
      読み：幸福[こうふく]とは ...
      訳：你考虑过...
    返回 examples list: [{example, example_reading, example_meaning}]
    """
    examples = []
    if not section_text:
        return examples

    # 先按双换行拆分例句块
    blocks = [b.strip() for b in section_text.split('\n\n') if b.strip()]

    for block in blocks:
        lines = [ln.strip() for ln in block.split('\n') if ln.strip()]
        if not lines:
            continue

        ex = {'example': '', 'example_reading': '', 'example_meaning': ''}

        # 简单判断：如果第一行不含“読み”“訳”，则视为例句日文
        first = lines[0]
        if not first.startswith('読み：') and not first.startswith('訳：'):
            ex['example'] = first
            lines = lines[1:]

        for ln in lines:
            if ln.startswith('読み：'):
                ex['example_reading'] = ln[3:].strip()
            elif ln.startswith('訳：'):
                ex['example_meaning'] = ln[2:].strip()
            elif not ex['example']:
                ex['example'] = ln
            elif not ex['example_meaning']:
                ex['example_meaning'] = ln

        if ex['example'] or ex['example_reading'] or ex['example_meaning']:
            examples.append(ex)

    return examples


def parse_mistakes(section_text):
    """把常见错误文本拆成列表"""
    if not section_text:
        return []
    items = []
    for line in section_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        # 去掉前导 • 或 -
        if line.startswith('•') or line.startswith('-'):
            line = line[1:].strip()
        if line:
            items.append(line)
    return items


def parse_notes_and_compare(section_text):
    """解析注意／对比：拆成 notes 和 comparison"""
    notes = section_text.strip() if section_text else ''
    comparison = ''
    # 如果文本里出现 "~X：...；~Y：..." 这种多个语法点对比，视为 comparison
    # 否则归入 notes
    if notes:
        # 检测是否包含多个分号/句号分隔的“~...：”对比项
        if re.search(r'[~～].+?[:：].+?；[~～]', notes) or notes.count('；') >= 1:
            comparison = notes
            notes = ''
    return notes, comparison


def migrate_entry(entry):
    """迁移单条 grammar 条目"""
    desc = entry.get('description', '') or ''
    new_entry = dict(entry)

    # 1. 接续
    new_entry['pattern'] = (entry.get('pattern') or extract_section(desc, '接续') or '').strip()

    # 2. 含义 + 用法 = meaning
    meaning = (entry.get('meaning') or extract_section(desc, '含义') or '').strip()
    usage = extract_section(desc, '用法').strip()
    if meaning and usage:
        meaning = f"{meaning}\n{usage}".strip()
    elif usage:
        meaning = usage
    new_entry['meaning'] = meaning
    if usage:
        new_entry['usage'] = usage

    # 3. grammar_cn：用旧简短 meaning 作为中文别名/提示（没有则留空）
    short_meaning = (entry.get('meaning') or '').strip()
    if short_meaning and short_meaning != meaning:
        new_entry['grammar_cn'] = short_meaning
    elif not new_entry.get('grammar_cn'):
        new_entry['grammar_cn'] = ''

    # 5. 例句
    ex_section = extract_section(desc, '例句')
    parsed_examples = split_examples(ex_section)

    # 兼容旧单条 example
    old_ex = entry.get('example')
    if old_ex and not any(e.get('example') == old_ex for e in parsed_examples):
        parsed_examples.insert(0, {
            'example': old_ex,
            'example_reading': entry.get('example_reading', ''),
            'example_meaning': entry.get('example_meaning', '')
        })

    if parsed_examples:
        new_entry['examples'] = parsed_examples

    # 6. 常见错误
    mistakes = parse_mistakes(extract_section(desc, '常见错误'))
    if mistakes:
        new_entry['common_mistakes'] = mistakes

    # 7. 注意／对比
    notes, comparison = parse_notes_and_compare(extract_section(desc, '注意／对比'))
    # 兼容旧 compare 字段
    if not comparison and entry.get('compare'):
        comparison = entry.get('compare')
    if notes:
        new_entry['notes'] = notes
    if comparison:
        new_entry['comparison'] = comparison

    return new_entry


def main():
    for level in LEVELS:
        path = BASE / f'{level}_grammar.json'
        if not path.exists():
            print(f'[SKIP] {path} not found')
            continue

        data = json.loads(path.read_text(encoding='utf-8'))
        migrated = [migrate_entry(e) for e in data]

        # 备份一次
        bak = path.with_suffix('.json.bak.structured')
        if not bak.exists():
            path.rename(bak)
            print(f'[BACKUP] {bak.name}')

        path.write_text(json.dumps(migrated, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'[MIGRATE] {level}: {len(migrated)} entries')


if __name__ == '__main__':
    main()
