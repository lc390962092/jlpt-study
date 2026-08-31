#!/usr/bin/env python3
"""Generate and push today's JLPT daily grammar points as Feishu card + voice."""
import json
import os
import random
import subprocess
import sys
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(BASE_DIR, "content")
PRIVATE_DIR = os.path.join(BASE_DIR, "private")
DAILY_DIR = os.path.join(PRIVATE_DIR, "daily-grammar")
MEDIA_DIR = os.path.join(PRIVATE_DIR, "daily-media")
TARGET_CHAT_ID = "oc_e4395471375838dfcee7f9fc04c120c7"

LEVEL_FILES = {
    "N5": "N5_grammar.json",
    "N4": "N4_grammar.json",
    "N3": "N3_grammar.json",
    "N2": "N2_grammar.json",
    "N1": "N1_grammar.json",
}
LEVEL_WEIGHTS = {"N5": 5, "N4": 4, "N3": 3, "N2": 2, "N1": 1}


def today_str(tz: timezone) -> str:
    return datetime.now(tz).strftime("%Y-%m-%d")


def load_grammar_bank(level: str) -> list:
    path = os.path.join(CONTENT_DIR, LEVEL_FILES[level])
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path} is not a list")
    return data


def pick_grammar(count: int = 10) -> list:
    items = []
    used = set()
    level_pool = [lvl for lvl in LEVEL_FILES for _ in range(LEVEL_WEIGHTS[lvl])]
    while len(items) < count:
        level = random.choice(level_pool)
        bank = load_grammar_bank(level)
        candidate = random.choice(bank)
        key = candidate.get("id", "")
        if key and key not in used:
            used.add(key)
            candidate.setdefault("level", level)
            items.append(candidate)
    return items


def save_daily(items: list, date_str: str) -> str:
    os.makedirs(DAILY_DIR, exist_ok=True)
    path = os.path.join(DAILY_DIR, f"{date_str}.json")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    return path


def generate_audio(items: list, date_str: str) -> str:
    os.makedirs(MEDIA_DIR, exist_ok=True)
    mp3_path = os.path.join(MEDIA_DIR, f"{date_str}.mp3")
    opus_path = os.path.join(MEDIA_DIR, f"{date_str}.opus")

    lines = []
    for i, item in enumerate(items, 1):
        grammar = item.get("grammar", "").strip()
        reading = item.get("reading", "").strip()
        example = item.get("example", "").strip()
        example_reading = item.get("example_reading", "").strip()
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


def build_card(items: list, date_str: str) -> dict:
    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**今日目标：{len(items)} 条语法点**  坚持打卡，积少成多 💪",
            },
        },
        {"tag": "hr"},
    ]
    for i, item in enumerate(items, 1):
        level = item.get("level", "")
        grammar = item.get("grammar", "").strip()
        reading = item.get("reading", "").strip()
        grammar_cn = item.get("grammar_cn", "").strip() or item.get("meaning", "").strip()
        pattern = item.get("pattern", "").strip()
        example = item.get("example", "").strip()
        example_reading = item.get("example_reading", "").strip()
        example_meaning = item.get("example_meaning", "").strip()

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
                "content": f"每日日语 · {date_str}",
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


def send_voice(date_str: str) -> None:
    rel_audio = f"private/daily-media/{date_str}.opus"
    cmd = [
        "lark-cli", "im", "+messages-send",
        "--chat-id", TARGET_CHAT_ID,
        "--audio", rel_audio,
    ]
    subprocess.run(cmd, check=True, cwd=BASE_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    tz = timezone(timedelta(hours=9), "Asia/Tokyo")
    date_str = today_str(tz)

    items = pick_grammar(10)
    save_daily(items, date_str)

    audio_path = generate_audio(items, date_str)
    card = build_card(items, date_str)
    send_card(card, date_str)
    send_voice(date_str)

    print(f"📚 今日 {len(items)} 条日语文法点（{date_str}）已推送\n卡片 + 语音已发送，回复「今日日语打卡」标记完成。")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 推送失败：{e}")
        sys.exit(1)
