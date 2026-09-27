#!/usr/bin/env python3
"""Generate and push today's JLPT daily content as Feishu card + voice.

Rotates every other day:
- even ordinal  -> 10 vocabulary words
- odd ordinal   -> 10 grammar points
"""
import json
import os
import random
import subprocess
import sys
import re
from datetime import date, datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(BASE_DIR, "content")
PRIVATE_DIR = os.path.join(BASE_DIR, "private")
DAILY_DIR = os.path.join(PRIVATE_DIR, "daily")
MEDIA_DIR = os.path.join(PRIVATE_DIR, "daily-media")
TARGET_CHAT_ID = "oc_88d8933f0bd6049c61c7bf9f894e097c"

GRAMMAR_FILES = {
    "N5": "N5_grammar.json",
    "N4": "N4_grammar.json",
    "N3": "N3_grammar.json",
    "N2": "N2_grammar.json",
    "N1": "N1_grammar.json",
}
LEVEL_WEIGHTS = {"N5": 6, "N4": 5, "N3": 4, "N2": 2, "N1": 1}
WORD_FILES = {
    "N5": "N5_words.json",
    "N4": "N4_words.json",
    "N3": "N3_words.json",
    "N2": "N2_words.json",
    "N1": "N1_words.json",
}


def today_str(tz: timezone) -> str:
    return datetime.now(tz).strftime("%Y-%m-%d")


def clean_tts_text(text: str) -> str:
    """Remove kanji from ruby-annotated strings like 私[わたし] -> わたし.

    Edge-tts would otherwise read the kanji and then the reading separately.
    """
    if not text:
        return ""
    # Replace "漢字[かな]" with "かな"
    text = re.sub(r"[^\s\[]+\[([^\]]+)\]", r"\1", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

def is_words_day(date_str: str) -> bool:
    """Return True if today is vocabulary day (even ordinal) else grammar day."""
    y, m, d = map(int, date_str.split("-"))
    return date(y, m, d).toordinal() % 2 == 0


def load_bank(path_key: str, level: str) -> list:
    mapping = GRAMMAR_FILES if path_key == "grammar" else WORD_FILES
    path = os.path.join(CONTENT_DIR, mapping[level])
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path} is not a list")
    return data


def pick_items(bank_key: str, count: int = 10) -> list:
    items = []
    used = set()
    level_pool = [lvl for lvl in GRAMMAR_FILES for _ in range(LEVEL_WEIGHTS[lvl])]
    while len(items) < count:
        level = random.choice(level_pool)
        bank = load_bank(bank_key, level)
        candidate = random.choice(bank)
        key = candidate.get("id", "") or candidate.get("word", "")
        if key and key not in used:
            used.add(key)
            candidate.setdefault("level", level)
            items.append(candidate)
    return items


def save_daily(items: list, date_str: str, mode: str) -> str:
    os.makedirs(DAILY_DIR, exist_ok=True)
    path = os.path.join(DAILY_DIR, f"{date_str}.{mode}.json")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    return path


def generate_audio(items: list, date_str: str, mode: str) -> str:
    os.makedirs(MEDIA_DIR, exist_ok=True)
    mp3_path = os.path.join(MEDIA_DIR, f"{date_str}.{mode}.mp3")
    opus_path = os.path.join(MEDIA_DIR, f"{date_str}.{mode}.opus")

    lines = []
    for i, item in enumerate(items, 1):
        if mode == "words":
            word = (item.get("word") or "").strip()
            reading = clean_tts_text((item.get("reading") or "").strip())
            sentence = (item.get("sentence") or "").strip()
            sentence_reading = clean_tts_text((item.get("sentence_reading") or "").strip())
            lines.append(f"{i}. {word}")
            if reading:
                lines.append(reading)
            if sentence_reading:
                lines.append(sentence_reading)
            elif sentence:
                lines.append(sentence)
        else:
            grammar = (item.get("grammar") or "").strip()
            reading = clean_tts_text((item.get("reading") or "").strip())
            example = (item.get("example") or "").strip()
            example_reading = clean_tts_text((item.get("example_reading") or "").strip())
            lines.append(f"{i}. {grammar}")
            if reading:
                lines.append(reading)
            if example_reading:
                lines.append(example_reading)
            elif example:
                lines.append(example)
    text = "\n\n".join(lines)

    subprocess.run(
        ["edge-tts", "-t", text, "-v", "ja-JP-NanamiNeural", "--write-media", mp3_path],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", mp3_path,
            "-c:a", "libopus", "-b:a", "24k", "-vbr", "on",
            "-ar", "24000", "-ac", "1",
            opus_path,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return opus_path


def build_card(items: list, date_str: str, mode: str) -> dict:
    mode_label = "单词" if mode == "words" else "语法点"
    mode_title = "每日日语单词" if mode == "words" else "每日日语文法"
    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**今日目标：{len(items)} {mode_label}**  坚持打卡，积少成多 💪",
            },
        },
        {"tag": "hr"},
    ]
    for i, item in enumerate(items, 1):
        level = item.get("level", "")
        if mode == "words":
            word = (item.get("word") or "").strip()
            reading = (item.get("reading") or "").strip()
            accent = (item.get("accent") or "").strip()
            pos = (item.get("pos") or "").strip()
            meaning = (item.get("meaning") or "").strip()
            sentence = (item.get("sentence") or "").strip()
            sentence_reading = (item.get("sentence_reading") or "").strip()
            sentence_meaning = (item.get("sentence_meaning") or "").strip()

            content = f"**{i}. {word}**  `{level}`\n"
            if reading:
                content += f"读音：{reading}\n"
            if accent:
                content += f"声调：{accent}\n"
            if pos:
                content += f"词性：{pos}\n"
            if meaning:
                content += f"含义：{meaning}"
            if sentence:
                content += f"\n\n*例：{sentence}*"
                if sentence_reading:
                    content += f"\n*读：{sentence_reading}*"
                if sentence_meaning:
                    content += f"\n*译：{sentence_meaning}*"
        else:
            grammar = (item.get("grammar") or "").strip()
            reading = (item.get("reading") or "").strip()
            grammar_cn = (item.get("grammar_cn") or "").strip() or (item.get("meaning") or "").strip()
            pattern = (item.get("pattern") or "").strip()
            example = (item.get("example") or "").strip()
            example_reading = (item.get("example_reading") or "").strip()
            example_meaning = (item.get("example_meaning") or "").strip()

            content = f"**{i}. {grammar}**  `{level}`\n"
            if reading:
                content += f"读音：{reading}\n"
            if grammar_cn:
                content += f"含义：{grammar_cn}\n"
            if pattern:
                content += f"接续：{pattern}"
            if example:
                content += f"\n\n*例：{example}*"
                if example_reading:
                    content += f"\n*读：{example_reading}*"
                if example_meaning:
                    content += f"\n*译：{example_meaning}*"
        elements.append(
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": content},
            }
        )
        elements.append({"tag": "hr"})

    elements.append(
        {
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": "回复「今日日语打卡」标记今日为已完成",
                }
            ],
        }
    )

    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": "blue",
            "title": {
                "tag": "plain_text",
                "content": f"{mode_title} · {date_str}",
            },
        },
        "elements": elements,
    }


def send_card(card: dict, date_str: str) -> None:
    content_json = json.dumps(card, ensure_ascii=False, separators=(",", ":"))
    cmd = [
        "lark-cli", "im", "+messages-send",
        "--chat-id", TARGET_CHAT_ID,
        "--msg-type", "interactive",
        "--content", content_json,
    ]
    subprocess.run(cmd, check=True, cwd=BASE_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def send_voice(date_str: str, mode: str) -> None:
    rel_audio = f"private/daily-media/{date_str}.{mode}.opus"
    cmd = [
        "lark-cli", "im", "+messages-send",
        "--chat-id", TARGET_CHAT_ID,
        "--audio", rel_audio,
    ]
    subprocess.run(cmd, check=True, cwd=BASE_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    tz = timezone(timedelta(hours=9), "Asia/Tokyo")
    date_str = today_str(tz)
    force = "--force" in sys.argv

    mode = "words" if is_words_day(date_str) else "grammar"
    daily_path = os.path.join(DAILY_DIR, f"{date_str}.{mode}.json")
    if os.path.exists(daily_path) and not force:
        label = "单词" if mode == "words" else "语法点"
        print(f"ℹ️ 今日（{date_str}）日语{label}已推送过，跳过重复发送。\n如需重新推送，请使用：python3 scripts/daily-push.py --force")
        return

    items = pick_items(mode, 10)
    save_daily(items, date_str, mode)

    audio_path = generate_audio(items, date_str, mode)
    card = build_card(items, date_str, mode)
    send_card(card, date_str)
    send_voice(date_str, mode)

    label = "单词" if mode == "words" else "语法点"
    print(f"📚 今日 {len(items)} {label}（{date_str}）已推送\n卡片 + 语音已发送，回复「今日日语打卡」标记完成。")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 推送失败：{e}")
        sys.exit(1)
