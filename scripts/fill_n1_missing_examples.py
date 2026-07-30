#!/usr/bin/env python3
"""给 N1_grammar.json 中缺少 example 的条目补上例句"""
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "content"
SRC = BASE / "N1_grammar.json"
BAK = BASE / "N1_grammar.json.bak.fill_examples"

# 手工补全 22 条例句
FILL = {
    "〜に足る": {
        "example": "彼の行動は信頼に足る",
        "example_reading": "彼[かれ]の 行動[こうどう]は 信頼[しんらい]に 足[た]る",
        "example_meaning": "他的行为值得信赖"
    },
    "〜に足りる": {
        "example": "この証拠は裁判に足りる",
        "example_reading": "この 証拠[しょうこ]は 裁判[さいばん]に 足[た]りる",
        "example_meaning": "这个证据足以用于审判"
    },
    "〜べき": {
        "example": "学生はまず勉強すべきだ",
        "example_reading": "学生[がくせい]はまず 勉強[べんきょう]すべきだ",
        "example_meaning": "学生首先应该学习"
    },
    "〜べし": {
        "example": "君子は危うきに近寄るべからず",
        "example_reading": "君子[くんし]は 危[あや]うきに 近寄[ちかよ]るべからず",
        "example_meaning": "君子不涉险地"
    },
    "〜まじき": {
        "example": "教育者としてあるまじき発言だ",
        "example_reading": "教育者[きょういくしゃ]としてあるまじき 発言[はつげん]だ",
        "example_meaning": "这是作为教育者不该有的发言"
    },
    "〜きらいがある": {
        "example": "彼の意見には独善的なきらいがある",
        "example_reading": "彼[かれ]の 意見[いけん]には 独善的[どくぜんてき]なきらいがある",
        "example_meaning": "他的意见有点自以为是"
    },
    "〜気味だ": {
        "example": "最近、少し疲れ気味だ",
        "example_reading": "最近[さいきん]、すこし 疲[つか]れ 気味[ぎみ]だ",
        "example_meaning": "最近有点疲惫"
    },
    "〜がちだ": {
        "example": "彼は約束を忘れがちだ",
        "example_reading": "彼[かれ]は 約束[やくそく]を 忘[わす]れがちだ",
        "example_meaning": "他容易忘记约定"
    },
    "〜だらけ": {
        "example": "机の上は埃だらけだ",
        "example_reading": "机[つくえ]の 上[うえ]は 埃[ほこり]だらけだ",
        "example_meaning": "桌子上全是灰尘"
    },
    "〜ずくめ": {
        "example": "今日は良いことずくめだ",
        "example_reading": "今日[きょう]は 良[よ]いことずくめだ",
        "example_meaning": "今天全是好事"
    },
    "〜まみれ": {
        "example": "子供が泥まみれで帰ってきた",
        "example_reading": "子供[こども]が 泥[どろ]まみれで 帰[かえ]ってきた",
        "example_meaning": "孩子满身是泥地回来了"
    },
    "〜つつ": {
        "example": "知りつつ、黙っていた",
        "example_reading": "知[し]りつつ、 黙[だま]っていた",
        "example_meaning": "明知却保持沉默"
    },
    "〜つつも": {
        "example": "分かっているつつも、言えなかった",
        "example_reading": "分[わ]かっているつつも、 言[い]えなかった",
        "example_meaning": "虽然明白，却说不出口"
    },
    "〜かたわら": {
        "example": "彼女は主婦のかたわら、小説を書いている",
        "example_reading": "彼女[かのじょ]は 主婦[しゅふ]のかたわら、 小説[しょうせつ]を 書[か]いている",
        "example_meaning": "她一边做家庭主妇一边写小说"
    },
    "〜そばから": {
        "example": "覚えるそばから忘れる",
        "example_reading": "覚[おぼ]えるそばから 忘[わす]れる",
        "example_meaning": "刚记住就忘了"
    },
    "〜が早いか": {
        "example": "彼は私の顔を見るが早いか、逃げ出した",
        "example_reading": "彼[かれ]は 私[わたし]の 顔[かお]を 見[み]るが 早[はや]いか、 にげだした",
        "example_meaning": "他一看到我的脸就逃跑了"
    },
    "〜や否や": {
        "example": "彼は目を覚ますや否や、飛び起きた",
        "example_reading": "彼[かれ]は 目[め]を 覚[さ]ますや 否[いな]や、 とび 起[お]きた",
        "example_meaning": "他刚醒来就跳了起来"
    },
    "〜かと思うと/思えば": {
        "example": "静かになったかと思うと、大きな音がした",
        "example_reading": "静[しず]かになったかと 思[おも]うと、 大[おお]きな 音[おと]がした",
        "example_meaning": "刚安静下来就传来了巨响"
    },
    "〜なり": {
        "example": "彼は会議室に入るなり、泣き始めた",
        "example_reading": "彼[かれ]は 会議室[かいぎしつ]にはいるなり、 泣[な]き はじ[始]めた",
        "example_meaning": "他一进会议室就开始哭"
    },
    "〜そばらく": {
        "example": "彼が来たそばらく、仕事が始まった",
        "example_reading": "彼[かれ]が 来[き]たそばらく、 仕事[しごと]が はじ[始]まった",
        "example_meaning": "他来了不一会儿，工作就开始了"
    },
    "〜たかと思うと/思えば": {
        "example": "彼は怒ったかと思うと、すぐに笑った",
        "example_reading": "彼[かれ]は 怒[おこ]ったかと 思[おも]うと、すぐに 笑[わら]った",
        "example_meaning": "他刚生气马上又笑了"
    },
    "〜と思いきや": {
        "example": "彼は怒ったと思いきや、実は喜んでいた",
        "example_reading": "彼[かれ]は 怒[おこ]ったと 思[おも]いきや、 実[じつ]は 喜[よろこ]んでいた",
        "example_meaning": "原以为他生气了，其实他在高兴"
    }
}


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    shutil.copy2(SRC, BAK)
    print(f"Backup: {BAK}")

    filled = 0
    for entry in data:
        grammar = entry.get("grammar", "")
        if grammar in FILL and not entry.get("example"):
            entry.update(FILL[grammar])
            filled += 1
            print(f"Filled: {grammar}")

    SRC.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Filled {filled} missing examples.")


if __name__ == "__main__":
    main()
