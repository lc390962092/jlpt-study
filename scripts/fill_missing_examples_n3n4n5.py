#!/usr/bin/env python3
"""手工填充 N3/N4/N5 grammar JSON 中缺失的 example/example_reading/example_meaning，然后重新生成 description"""
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "content"
SCRIPT_DIR = Path(__file__).resolve().parent

# 手工补全数据：grammar -> {example, example_reading, example_meaning}
# 读音格式：漢字[かな]（与现有格式一致）
FILL = {
    # N5
    "〜など": {
        "example": "机の上には本やノートなどがある",
        "example_reading": "机[つくえ]の 上[うえ]には 本[ほん]やノートなどがある",
        "example_meaning": "桌子上有书和笔记本之类的东西"
    },
    "〜くらい/ぐらい": {
        "example": "駅まで歩いて10分くらいかかる",
        "example_reading": "駅[えき]まで 歩[ある]いて10 分[ふん]くらいかかる",
        "example_meaning": "走到车站大约要花10分钟"
    },

    # N4
    "〜にする": {
        "example": "今日の夕食はカレーにする",
        "example_reading": "今日[きょう]の 夕食[ゆうしょく]はカレーにする",
        "example_meaning": "今天的晚饭决定吃咖喱"
    },
    "〜になる": {
        "example": "彼は先生になった",
        "example_reading": "彼[かれ]は 先生[せんせい]になった",
        "example_meaning": "他成为了老师"
    },
    "〜に決まる": {
        "example": "来週の会議は火曜日に決まった",
        "example_reading": "来週[らいしゅう]の 会議[かいぎ]は 火曜日[かようび]に 決[き]まった",
        "example_meaning": "下周的会议定在周二了"
    },
    "〜ように言う": {
        "example": "先生は学生に宿題を出すように言った",
        "example_reading": "先生[せんせい]は 学生[がくせい]に 宿題[しゅくだい]を 出[だ]すように 言[い]った",
        "example_meaning": "老师让学生们交作业"
    },
    "〜ようになる": {
        "example": "毎日練習したら、泳げるようになった",
        "example_reading": "毎日[まいにち] 練習[れんしゅう]したら、 泳[およ]げるようになった",
        "example_meaning": "每天练习之后，变得会游泳了"
    },
    "〜ことになる": {
        "example": "来月、会社を辞めることになった",
        "example_reading": "来月[らいげつ]、 会社[かいしゃ]を 辞[や]めることになった",
        "example_meaning": "决定下个月辞职"
    },
    "〜ことにする": {
        "example": "毎朝ジョギングすることにしている",
        "example_reading": "毎朝[まいあさ]ジョギングすることにしている",
        "example_meaning": "我养成了每天早上慢跑的习惯"
    },
    "〜ことにしている": {
        "example": "寝る前に本を読むことにしている",
        "example_reading": "寝[ね]る 前[まえ]に 本[ほん]を 読[よ]むことにしている",
        "example_meaning": "我养成了睡前看书的习惯"
    },
    "〜ことになっている": {
        "example": "図書館では静かにすることになっている",
        "example_reading": "図書館[としょかん]では 静[しず]かにすることになっている",
        "example_meaning": "图书馆规定要保持安静"
    },
    "〜つもりだ": {
        "example": "来年、日本へ旅行に行くつもりだ",
        "example_reading": "来年[らいねん]、 日本[にほん]へ 旅行[りょこう]に 行[い]くつもりだ",
        "example_meaning": "明年我打算去日本旅行"
    },
    "〜つもりはない": {
        "example": "もう一度やり直すつもりはない",
        "example_reading": "もう 一度[いちど]やり 直[なお]すつもりはない",
        "example_meaning": "我不打算再重做一遍"
    },
    "〜つもりで": {
        "example": "彼の家は自分の家にいるつもりで寛いでください",
        "example_reading": "彼[かれ]の 家[いえ]は 自分[じぶん]の 家[いえ]にいるつもりで 寛[くつろ]いでください",
        "example_meaning": "在他家就请当作在自己家一样放松"
    },
    "〜ところに": {
        "example": "食事をしているところに、友達が来た",
        "example_reading": "食事[しょくじ]をしているところに、 友達[ともだち]が 来[き]た",
        "example_meaning": "正在吃饭的时候，朋友来了"
    },
    "〜ところへ": {
        "example": "出かけようとしているところへ、電話がかかってきた",
        "example_reading": "出[で]かけようとしているところへ、 電話[でんわ]がかかってきた",
        "example_meaning": "正要出门的时候，电话来了"
    },
    "〜ところを": {
        "example": "忙しいところをすみません",
        "example_reading": "忙[いそが]しいところをすみません",
        "example_meaning": "打扰您正忙的时候，不好意思"
    },
    "〜たばかり": {
        "example": "彼は日本に来たばかりだ",
        "example_reading": "彼[かれ]は 日本[にほん]に 来[き]たばかりだ",
        "example_meaning": "他刚来日本"
    },
    "〜たところ": {
        "example": "帰ったところ、留守番電話が入っていた",
        "example_reading": "帰[かえ]ったところ、 留守番電話[るすばんでんわ]がはいっていた",
        "example_meaning": "刚回家，发现有电话留言"
    },
    "〜かける": {
        "example": "彼は話しかけて、黙ってしまった",
        "example_reading": "彼[かれ]は 話[はな]しかけて、 黙[だま]ってしまった",
        "example_meaning": "他话说到一半就沉默了"
    },
    "〜かけだ": {
        "example": "この仕事はまだやりかけだ",
        "example_reading": "この 仕事[しごと]はまだやりかけだ",
        "example_meaning": "这项工作还只做了一半"
    },
    "〜っこない": {
        "example": "あんな難しい問題は分かりっこない",
        "example_reading": "あんな 難[むずか]しい 問題[もんだい]は 分[わ]かりっこない",
        "example_meaning": "那么难的不可能懂"
    },
    "〜わけにはいかない": {
        "example": "明日試験があるので、遊んでいるわけにはいかない",
        "example_reading": "明日[あした] 試験[しけん]があるので、 遊[あそ]んでいるわけにはいかない",
        "example_meaning": "明天有考试，不能只顾着玩"
    },
    "〜わけがない": {
        "example": "彼が嘘をつくわけがない",
        "example_reading": "彼[かれ]が 嘘[うそ]をつくわけがない",
        "example_meaning": "他不可能说谎"
    },
    "〜わけではない": {
        "example": "嫌いなわけではないが、得意でもない",
        "example_reading": "嫌[きら]いなわけではないが、 得意[とくい]でもない",
        "example_meaning": "并非不喜欢，只是不太擅长"
    },
    "〜わけだ": {
        "example": "毎日練習しているんだから、上手なわけだ",
        "example_reading": "毎日[まいにち] 練習[れんしゅう]しているんだから、 上手[じょうず]なわけだ",
        "example_meaning": "每天都在练习，难怪这么熟练"
    },
    "〜というわけだ": {
        "example": "つまり、彼は来ないというわけだ",
        "example_reading": "つまり、 彼[かれ]は 来[こ]ないというわけだ",
        "example_meaning": "也就是说，他不来了"
    },
    "〜ものか": {
        "example": "あんな人の言うことを信じるものか",
        "example_reading": "あんな 人[ひと]の 言[い]うことを 信[しん]じるものか",
        "example_meaning": "怎么会相信那种人说的话"
    },
    "〜ものだから": {
        "example": "子供が小さいものだから、仕方がない",
        "example_reading": "子供[こども]が 小[ちい]さいものだから、 仕方[しかた]がない",
        "example_meaning": "因为孩子还小，没办法"
    },
    "〜ものではない": {
        "example": "人の悪口を言うものではない",
        "example_reading": "人[ひと]の 悪口[わるぐち]を 言[い]うものではない",
        "example_meaning": "不应该说别人坏话"
    },
    "〜ことか": {
        "example": "どれだけ待ったことか",
        "example_reading": "どれだけ 待[ま]ったことか",
        "example_meaning": "我等了多久啊"
    },
    "〜ことだから": {
        "example": "彼のことだから、きっと大丈夫だ",
        "example_reading": "彼[かれ]のことだから、きっと 大丈夫[だいじょうぶ]だ",
        "example_meaning": "因为是他，一定没问题"
    },
    "〜どころか": {
        "example": "日本語どころか、英語も話せない",
        "example_reading": "日本語[にほんご]どころか、 英語[えいご]も 話[はな]せない",
        "example_meaning": "别说日语了，连英语都不会说"
    },
    "〜どころではない": {
        "example": "試験前なので、遊んでいるどころではない",
        "example_reading": "試験[しけん]まえなので、 遊[あそ]んでいるどころではない",
        "example_meaning": "快考试了，不是玩的时候"
    },
    "〜なんか": {
        "example": "彼なんか知らない",
        "example_reading": "彼[かれ]なんか 知[し]らない",
        "example_meaning": "他那种人我才不认识"
    },
    "〜なんて": {
        "example": "彼が合格したなんて信じられない",
        "example_reading": "彼[かれ]が 合格[ごうかく]したなんて 信[しん]じられない",
        "example_meaning": "他竟然通过了，真不敢相信"
    },
    "〜くらいなら": {
        "example": "あんな映画を見るくらいなら、本を読んだほうがいい",
        "example_reading": "あんな 映画[えいが]を 見[み]るくらいなら、 本[ほん]を 読[よ]んだほうがいい",
        "example_meaning": "与其看那种电影，不如看书"
    },
    "〜ばかりでなく": {
        "example": "彼は頭がいいばかりでなく、勉強も熱心だ",
        "example_reading": "彼[かれ]は 頭[あたま]がいいばかりでなく、 勉強[べんきょう]も 熱心[ねっしん]だ",
        "example_meaning": "他不仅聪明，学习也很认真"
    },
    "〜のみならず": {
        "example": "彼は日本語のみならず、英語も話せる",
        "example_reading": "彼[かれ]は 日本語[にほんご]のみならず、 英語[えいご]も 話[はな]せる",
        "example_meaning": "他不仅会说日语，也会说英语"
    },
    "〜あまり": {
        "example": "嬉しさのあまり、泣き出してしまった",
        "example_reading": "嬉[うれ]しさのあまり、 泣[な]き 出[だ]してしまった",
        "example_meaning": "因为太高兴，不禁哭了出来"
    },
    "〜あまりの": {
        "example": "あまりの驚きで、声も出なかった",
        "example_reading": "あまりの 驚[おどろ]きで、 声[こえ]も 出[で]なかった",
        "example_meaning": "因为太惊讶，连声音都发不出来"
    },
    "〜ないこともない": {
        "example": "週末なら、行かないこともない",
        "example_reading": "週末[しゅうまつ]なら、 行[い]かないこともない",
        "example_meaning": "如果是周末的话，也不是不能去"
    },

    # N3
    "〜ばかりに": {
        "example": "安いばかりに、質の悪いものを買ってしまった",
        "example_reading": "安[やす]いばかりに、 質[しつ]の 悪[わる]いものを 買[か]ってしまった",
        "example_meaning": "只因贪便宜，买到了质量差的东西"
    },
    "〜だけに": {
        "example": "長年の夢だけに、実現した時は感慨深かった",
        "example_reading": "長年[ながねん]の 夢[ゆめ]だけに、 実現[じつげん]した 時[とき]は 感慨深[かんがいぶか]かった",
        "example_meaning": "正因为是多年的梦想，实现时感慨万千"
    },
    "〜だけあって": {
        "example": "プロだけあって、仕事が早い",
        "example_reading": "プロだけあって、 仕事[しごと]が 早[はや]い",
        "example_meaning": "不愧是专业人士，干活很快"
    },
    "〜だけのことはある": {
        "example": "人気店だけのことはある、いつも行列ができている",
        "example_reading": "人気店[にんきてん]だけのことはある、いつも 行列[ぎょうれつ]ができている",
        "example_meaning": "不愧是人气店，总是在排队"
    },
    "〜さえ〜ば": {
        "example": "お金さえあれば、何でも買える",
        "example_reading": "お 金[かね]さえあれば、 何[なん]でも 買[か]える",
        "example_meaning": "只要有钱，什么都能买"
    },
    "〜すら": {
        "example": "彼は子供すら知っている有名な歌手だ",
        "example_reading": "彼[かれ]は 子供[こども]すら 知[し]っている 有名[ゆうめい]な 歌手[かしゅ]だ",
        "example_meaning": "他是连小孩都知道的著名歌手"
    },
    "〜でも": {
        "example": "専門家でも間違うことがある",
        "example_reading": "専門家[せんもんか]でも 間違[まちが]うことがある",
        "example_meaning": "即使是专家也会犯错"
    },
    "〜だに": {
        "example": "彼の顔を見るだに、怒りがこみ上げてくる",
        "example_reading": "彼[かれ]の 顔[かお]を 見[み]るだに、 怒[いか]りがこみ 上[あ]げてくる",
        "example_meaning": "甚至连他的脸都不想看到，怒火就涌上来了"
    },
    "〜ながら": {
        "example": "知りながら、黙っていた",
        "example_reading": "知[し]りながら、 黙[だま]っていた",
        "example_meaning": "虽然知道，却保持沉默"
    },
    "〜つつ": {
        "example": "悩みつつ、前に進んでいる",
        "example_reading": "悩[なや]みつつ、 前[まえ]に 進[すす]んでいる",
        "example_meaning": "虽然烦恼着，但仍在前进"
    },
    "〜ものと思われる": {
        "example": "この政策は多くの国民に支持されるものと思われる",
        "example_reading": "この 政策[せいさく]は 多[おお]くの 国民[こくみん]に 支持[しじ]されるものと 思[おも]われる",
        "example_meaning": "这项政策被认为会得到多数国民的支持"
    },
    "〜ものと考えられる": {
        "example": "この化石は数千万年前のものと考えられる",
        "example_reading": "この 化石[かせき]は 数千万年[すうせんまんねん] 前[まえ]のものと 考[かんが]えられる",
        "example_meaning": "这块化石被认为是数千万年前的"
    },
    "〜とされている": {
        "example": "この習慣は古くから伝わっているとされている",
        "example_reading": "この 習慣[しゅうかん]は 古[ふる]くから 伝[つた]わっているとされている",
        "example_meaning": "这一习俗被认为自古流传至今"
    },
    "〜と言われている": {
        "example": "健康には毎日の運動が大切だと言われている",
        "example_reading": "健康[けんこう]には 毎日[まいにち]の 運動[うんどう]が 大切[たいせつ]だと 言[い]われている",
        "example_meaning": "人们都说每天运动对健康很重要"
    },
    "〜に違いない": {
        "example": "あの人が犯人に違いない",
        "example_reading": "あの 人[ひと]が 犯人[はんにん]に 違[ちが]いない",
        "example_meaning": "那个人一定是凶手"
    },
    "〜に極まっている": {
        "example": "こんなに失礼な態度は、不愉快に極まっている",
        "example_reading": "こんなに 失礼[しつれい]な 態度[たいど]は、 不愉快[ふゆかい]に 極[きわ]まっている",
        "example_meaning": "如此无礼的态度，简直令人极度不快"
    },
    "〜の至りだ": {
        "example": "皆様のご協力に感謝の至りだ",
        "example_reading": "皆様[みなさま]のご 協力[きょうりょく]に 感謝[かんしゃ]の 至[いた]りだ",
        "example_meaning": "对各位的协助感激之至"
    },
    "〜というものだ": {
        "example": "旅行というものは、予想外の出来事も楽しむものだ",
        "example_reading": "旅行[りょこう]というものは、 予想外[よそうがい]の 出来事[できごと]も 楽[たの]しむものだ",
        "example_meaning": "所谓旅行，就是连意外的状况也要享受"
    },
    "〜ということだ": {
        "example": "明日は休みだということだ",
        "example_reading": "明日[あした]は 休[やす]みだということだ",
        "example_meaning": "也就是说明天休息"
    },
    "〜ということはない": {
        "example": "心配するということはない",
        "example_reading": "心配[しんぱい]するということはない",
        "example_meaning": "不必担心"
    },
    "〜からには": {
        "example": "引き受けたからには、最後まで責任を持つ",
        "example_reading": "引[ひ]き 受[う]けたからには、 最後[さいご]まで 責任[せきにん]を 持[も]つ",
        "example_meaning": "既然接受了，就要负责到底"
    },
    "〜以上": {
        "example": "約束した以上、守らなければならない",
        "example_reading": "約束[やくそく]した 以上[いじょう]、 守[まも]らなければならない",
        "example_meaning": "既然约好了，就必须遵守"
    },
    "〜上": {
        "example": "健康の上でも、規則正しい生活が大切だ",
        "example_reading": "健康[けんこう]の 上[うえ]でも、 規則正[きそくただ]しい 生活[せいかつ]が 大切[たいせつ]だ",
        "example_meaning": "在健康方面，规律的生活也很重要"
    },
    "〜上に": {
        "example": "彼は優秀な上に、性格もいい",
        "example_reading": "彼[かれ]は 優秀[ゆうしゅう]な 上[うえ]に、 性格[せいかく]もいい",
        "example_meaning": "他不仅优秀，性格也很好"
    },
    "〜一方": {
        "example": "この町は静かな一方、買い物が不便だ",
        "example_reading": "この 町[まち]は 静[しず]かな 一方[いっぽう]、 買[か]いものが 不便[ふべん]だ",
        "example_meaning": "这个城镇虽然安静，但购物不便"
    },
    "〜反面": {
        "example": "この薬は効く反面、副作用もある",
        "example_reading": "この 薬[くすり]は 効[き]く 反面[はんめん]、 副作用[ふくさよう]もある",
        "example_meaning": "这药有效，但另一方面也有副作用"
    },
    "〜かわりに": {
        "example": "私がかわりに行こう",
        "example_reading": "私[わたし]がかわりに 行[い]こう",
        "example_meaning": "我代替你去吧"
    },
    "〜代わりに": {
        "example": "彼に代わりに、私がお礼を言います",
        "example_reading": "彼[かれ]に 代[か]わりに、 私[わたし]がお 礼[れい]を 言[い]います",
        "example_meaning": "我代替他致谢"
    },
    "〜にしたがって": {
        "example": "年を取るにしたがって、体力が落ちてきた",
        "example_reading": "年[とし]を 取[と]るにしたがって、 体力[たいりょく]が 落[お]ちてきた",
        "example_meaning": "随着年龄增长，体力下降了"
    },
    "〜に伴って": {
        "example": "経済の発展に伴って、生活も豊かになった",
        "example_reading": "経済[けいざい]の 発展[はってん]に 伴[ともな]って、 生活[せいかつ]も 豊[ゆた]かになった",
        "example_meaning": "随着经济发展，生活也变得富裕了"
    },
    "〜に応じて": {
        "example": "経験に応じて給料が変わる",
        "example_reading": "経験[けいけん]に 応[おう]じて 給料[きゅうりょう]が 変[か]わる",
        "example_meaning": "根据经验不同，工资也不同"
    },
    "〜に反して": {
        "example": "予想に反して、試験は簡単だった",
        "example_reading": "予想[よそう]に 反[はん]して、 試験[しけん]は 簡単[かんたん]だった",
        "example_meaning": "与预料相反，考试很简单"
    },
    "〜に基づいて": {
        "example": "事実に基づいて判断する",
        "example_reading": "事実[じじつ]に 基[もと]づいて 判断[はんだん]する",
        "example_meaning": "根据事实作出判断"
    },
    "〜を皮切りに": {
        "example": "東京を皮切りに、全国ツアーが始まった",
        "example_reading": "東京[とうきょう]を 皮切[かわき]りに、 全国[ぜんこく]ツアーがはじまった",
        "example_meaning": "以东京为开端，全国巡演开始了"
    },
    "〜を始め": {
        "example": "社長を始め、全員が会議に出席した",
        "example_reading": "社長[しゃちょう]を はじめ、 全員[ぜんいん]が 会議[かいぎ]に 出席[しゅっせき]した",
        "example_meaning": "以社长为首，全体员工都出席了会议"
    },
    "〜をはじめとする": {
        "example": "彼をはじめとするチームが優勝した",
        "example_reading": "彼[かれ]をはじめとするチームが 優勝[ゆうしょう]した",
        "example_meaning": "以他为首的团队获得了冠军"
    },
    "〜にわたって": {
        "example": "会議は3時間にわたって行われた",
        "example_reading": "会議[かいぎ]は3 時間[じかん]にわたって 行[おこな]われた",
        "example_meaning": "会议持续了3个小时"
    },
    "〜を通じて": {
        "example": "ネットを通じて世界中の情報が得られる",
        "example_reading": "ネットを 通[つう]じて 世界中[せかいじゅう]の 情報[じょうほう]が 得[え]られる",
        "example_meaning": "通过网络可以获取世界各地的信息"
    },
    "〜を通して": {
        "example": "一年を通して暖かい地方だ",
        "example_reading": "一年[いちねん]を 通[とお]して 暖[あたた]かい 地方[ちほう]だ",
        "example_meaning": "这里是一年四季都温暖的地方"
    },
    "〜を込めて": {
        "example": "感謝の気持ちを込めて、贈り物を贈った",
        "example_reading": "感謝[かんしゃ]の 気持[きも]ちを 込[こ]めて、 贈[おく]り 物[もの]を 贈[おく]った",
        "example_meaning": "满怀感激之情送上了礼物"
    },
    "〜をもって": {
        "example": "これをもって、本日の会議を終了いたします",
        "example_reading": "これをもって、 本日[ほんじつ]の 会議[かいぎ]を 終了[しゅうりょう]いたします",
        "example_meaning": "就此结束今天的会议"
    },
    "〜かたわら": {
        "example": "学生のかたわら、アルバイトをしている",
        "example_reading": "学生[がくせい]のかたわら、アルバイトをしている",
        "example_meaning": "一边上学一边打工"
    },
    "〜がてら": {
        "example": "散歩がてら、近くの公園へ行った",
        "example_reading": "散歩[さんぽ]がてら、 近[ちか]くの 公園[こうえん]へ 行[い]った",
        "example_meaning": "顺便散散步，去了附近的公园"
    },
    "〜ついでに": {
        "example": "買い物のついでに、郵便局に寄った",
        "example_reading": "買[か]いもののついでに、 郵便局[ゆうびんきょく]に 寄[よ]った",
        "example_meaning": "趁着买东西的工夫，顺便去了趟邮局"
    },
    "〜かねる": {
        "example": "お忙しいところをお願いするのは恐れ入りますが、お答えしかねます",
        "example_reading": "お 忙[いそが]しいところをお 願[ねが]いするのは 恐[おそ]れ 入[い]りますが、お 答[こた]えしかねます",
        "example_meaning": "在您百忙中提出请求实在抱歉，但这个问题我难以回答"
    },
    "〜がたい": {
        "example": "彼の好意を疑いがたい",
        "example_reading": "彼[かれ]の 好意[こうい]を 疑[うたが]いがたい",
        "example_meaning": "他的好意让人难以怀疑"
    },
}


def build_description(entry: dict) -> str:
    """复用 enrich_grammar_descriptions.py 的 description 构建逻辑"""
    parts = []
    grammar = entry.get("grammar", "")
    meaning = entry.get("meaning", "").strip()
    pattern = entry.get("pattern", "").strip()
    example = entry.get("example", "").strip()
    example_reading = entry.get("example_reading", "").strip()
    example_meaning = entry.get("example_meaning", "").strip()
    compare = entry.get("compare", "").strip()

    if pattern:
        parts.append(f"【接续】{pattern}")
    if meaning:
        parts.append(f"【含义】{meaning}")

    notes = []
    g = grammar.lower()
    if any(k in g for k in ['です', 'ます']):
        notes.append('礼貌体基本表达')
    if any(k in g for k in ['ない', 'ぬ', 'ず']):
        notes.append('注意否定形式')
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
    if notes:
        parts.append(f"【用法】{ '；'.join(notes) }。")

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
    report_lines = ['# N3/N4/N5 缺失例句补全报告\n']

    for level in ['N3', 'N4', 'N5']:
        src = BASE / f"{level}_grammar.json"
        data = json.loads(src.read_text(encoding="utf-8"))
        bak = BASE / f"{level}_grammar.json.bak.fill_examples"
        shutil.copy2(src, bak)

        filled = 0
        still_missing = []
        for entry in data:
            grammar = entry.get("grammar", "")
            if grammar in FILL and not entry.get("example"):
                entry.update(FILL[grammar])
                filled += 1
            # 重新生成 description
            entry["description"] = build_description(entry)
            if not entry.get("example"):
                still_missing.append(f"{entry.get('id')}: {grammar}")

        src.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        report_lines.append(f"\n## {level}")
        report_lines.append(f"- 补全条目: {filled}")
        report_lines.append(f"- 仍缺例句: {len(still_missing)}")
        if still_missing:
            report_lines.append("- 未补条目:")
            report_lines.extend([f"  - {s}" for s in still_missing])
        report_lines.append(f"- 备份: {bak}")
        print(f"{level}: filled {filled}, still missing {len(still_missing)}")

    report_path = BASE.parent / "reviews" / "fill_missing_examples_n3n4n5_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
