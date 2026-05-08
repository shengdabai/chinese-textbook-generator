#!/usr/bin/env python3
"""Generate 10 Amazon-focused Chinese textbooks as Markdown + PDF.

Outputs:
- Planning markdown file
- 10 book markdown files
- 10 PDFs compiled via the existing v3-typst pipeline
"""

from __future__ import annotations

import re
import subprocess
import textwrap
from dataclasses import dataclass
from pathlib import Path

from pypinyin import Style, pinyin


BASE_DIR = Path("../..")
V3_DIR = BASE_DIR / "生成工具" / "v3-typst"
TARGET_ROOT = BASE_DIR / "中文教材" / "Amazon畅销中文系列"
GENERATOR = V3_DIR / "generate.py"
VENV_PYTHON = V3_DIR / ".venv" / "bin" / "python"


def zh_pinyin(text: str) -> str:
    """Convert mixed Chinese text into readable tone-mark pinyin."""
    punctuation_map = {
        "，": ",",
        "。": ".",
        "？": "?",
        "！": "!",
        "：": ":",
        "；": ";",
        "（": "(",
        "）": ")",
        "、": ",",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
    }
    out: list[str] = []
    prev_alpha = False
    for ch in text:
        if re.match(r"[\u4e00-\u9fff]", ch):
            py = pinyin(ch, style=Style.TONE, heteronym=False)[0][0]
            if prev_alpha and out and not out[-1].endswith(" "):
                out.append(" ")
            out.append(py)
            prev_alpha = True
            continue

        mapped = punctuation_map.get(ch, ch)
        if mapped.isspace():
            if out and not out[-1].endswith(" "):
                out.append(" ")
            prev_alpha = False
        elif mapped in ",.!?:;)":
            if out and out[-1] == " ":
                out.pop()
            out.append(mapped)
            out.append(" ")
            prev_alpha = False
        elif mapped == "(":
            if prev_alpha and out and not out[-1].endswith(" "):
                out.append(" ")
            out.append(mapped)
            prev_alpha = False
        else:
            if prev_alpha and out and not out[-1].endswith(" "):
                out.append(" ")
            out.append(mapped)
            prev_alpha = False

    result = "".join(out)
    result = re.sub(r"\s+", " ", result).strip()
    return result


@dataclass(frozen=True)
class Unit:
    title: str
    situation: str
    vocab: list[tuple[str, str, str]]
    dialogue: list[tuple[str, str, str]]
    patterns: list[tuple[str, str, str]]
    culture_note: str
    practice: list[str]


@dataclass(frozen=True)
class Book:
    number: str
    slug: str
    title: str
    subtitle: str
    color: str
    audience: str
    promise: str
    source_notes: list[str]
    units: list[Unit]


BOOKS: list[Book] = [
    Book(
        number="71",
        slug="SurvivalChineseTravel",
        title="Survival Chinese for Travelers",
        subtitle="生存中文：机场、打车、酒店和点餐",
        color="#E76F51",
        audience="Adult beginners who need practical Chinese from the first day in China.",
        promise="Master the phrases that solve the most urgent travel situations fast.",
        source_notes=["49", "77", "120", "150"],
        units=[
            Unit(
                title="Airport Arrival and the Taxi Line",
                situation="You have just landed in China and need to leave the airport without getting lost, overcharged, or stuck with no internet.",
                vocab=[
                    ("请问", "Excuse me, may I ask", "Start a question politely"),
                    ("出口", "Exit", "Follow signs or ask for the terminal exit"),
                    ("出租车", "Taxi", "Use at airports and stations"),
                    ("酒店", "Hotel", "Show your destination"),
                    ("在哪里", "Where is it", "Find a place fast"),
                ],
                dialogue=[
                    ("You", "请问，出租车在哪里？", "Excuse me, where is the taxi line?"),
                    ("Staff", "一直走，出口外面就是。", "Go straight. It is right outside the exit."),
                    ("You", "谢谢。我的酒店在这里。", "Thanks. My hotel is here."),
                    ("Driver", "好，给我看一下地址。", "Okay, show me the address."),
                    ("You", "好的，麻烦你。", "Sure. Thank you for your help."),
                    ("Driver", "没问题，上车吧。", "No problem. Get in."),
                ],
                patterns=[
                    ("请问，......在哪里？", "Excuse me, where is ...?", "请问，地铁站在哪里？"),
                    ("我的......在这里。", "My ... is here.", "我的酒店在这里。"),
                    ("给我看一下......。", "Show me ...", "给我看一下地址。"),
                ],
                culture_note="At large Chinese airports, the official taxi line is usually safer and cheaper than drivers who approach you inside the terminal. Showing a Chinese address on your phone is often faster than trying to pronounce it perfectly.",
                practice=[
                    "Ask where the exit is.",
                    "Show a driver your hotel address and say thank you politely.",
                ],
            ),
            Unit(
                title="Checking In at the Hotel",
                situation="You arrive at the hotel, feel tired, and just want to check in, ask about breakfast, and get the room key.",
                vocab=[
                    ("入住", "Check in", "Use at hotels"),
                    ("预订", "Reservation", "Confirm your booking"),
                    ("护照", "Passport", "Hotel staff will ask for it"),
                    ("房卡", "Room card", "Get access to your room"),
                    ("早餐", "Breakfast", "Ask about time and place"),
                ],
                dialogue=[
                    ("You", "你好，我有预订。", "Hello, I have a reservation."),
                    ("Reception", "好的，请给我护照。", "Okay. Please give me your passport."),
                    ("You", "这是我的护照。", "Here is my passport."),
                    ("Reception", "你住两晚，这是房卡。", "You are staying for two nights. Here is the room card."),
                    ("You", "请问，早餐几点开始？", "Excuse me, what time does breakfast start?"),
                    ("Reception", "早上七点到十点。", "From 7 a.m. to 10 a.m."),
                ],
                patterns=[
                    ("我有预订。", "I have a reservation.", "我有预订。"),
                    ("这是我的......。", "Here is my ...", "这是我的护照。"),
                    ("......几点开始？", "What time does ... start?", "早餐几点开始？"),
                ],
                culture_note="In China, even high-end hotels often ask to scan your passport at check-in. Many hotels also collect a small deposit, although mobile payment has made that less common than before.",
                practice=[
                    "Tell reception that you have a reservation.",
                    "Ask when breakfast starts.",
                ],
            ),
            Unit(
                title="Ordering Food When You Are Hungry",
                situation="You are tired, hungry, and need a simple way to order food even if you cannot read the full menu.",
                vocab=[
                    ("菜单", "Menu", "Ask for or scan it"),
                    ("这个", "This one", "Point and order"),
                    ("不要辣", "No spicy food", "Useful for food preferences"),
                    ("推荐", "Recommend", "Ask what the restaurant suggests"),
                    ("买单", "Pay the bill", "Use at the end of the meal"),
                ],
                dialogue=[
                    ("You", "你好，可以看一下菜单吗？", "Hello, may I see the menu?"),
                    ("Server", "可以，你也可以扫码点餐。", "Sure. You can also scan to order."),
                    ("You", "我看不太懂，我要这个，不要辣。", "I do not understand it very well. I want this one, not spicy."),
                    ("Server", "好的，还要别的吗？", "Okay. Anything else?"),
                    ("You", "你有什么推荐？", "What do you recommend?"),
                    ("Server", "这个鱼很受欢迎。", "This fish dish is very popular."),
                ],
                patterns=[
                    ("我要这个。", "I want this one.", "我要这个。"),
                    ("不要 + adjective / noun", "Do not want ...", "不要辣。"),
                    ("你有什么推荐？", "What do you recommend?", "你有什么推荐？"),
                ],
                culture_note="Many restaurants in China now use QR-code menus. If your phone setup is not ready, pointing, smiling, and saying 我要这个 is still one of the most useful food strategies you can have.",
                practice=[
                    "Order one dish and say you do not want spicy food.",
                    "Ask the server for one recommendation.",
                ],
            ),
            Unit(
                title="Directions, Battery, and Asking for Help",
                situation="Your phone battery is low and you need to find the subway, charge your phone, or ask for simple help in public.",
                vocab=[
                    ("地铁站", "Subway station", "Ask for transport"),
                    ("充电", "Charge", "Ask to charge your phone"),
                    ("帮帮我", "Please help me", "Use in a genuine need"),
                    ("我不懂", "I do not understand", "Reset the conversation politely"),
                    ("近", "Near", "Ask whether a place is nearby"),
                ],
                dialogue=[
                    ("You", "请问，地铁站近吗？", "Excuse me, is the subway station near?"),
                    ("Local", "很近，走五分钟就到了。", "Yes. It is close. You can get there in five minutes."),
                    ("You", "谢谢。我的手机没电了，可以充电吗？", "Thanks. My phone is out of battery. May I charge it?"),
                    ("Clerk", "可以，在这里。", "Sure. Here."),
                    ("You", "太好了，谢谢你。", "Great. Thank you."),
                    ("Clerk", "不客气。", "You are welcome."),
                ],
                patterns=[
                    ("......近吗？", "Is ... near?", "地铁站近吗？"),
                    ("可以 + verb + 吗？", "May I ...?", "可以充电吗？"),
                    ("太好了。", "That is great.", "太好了，谢谢你。"),
                ],
                culture_note="If you are polite and direct, many people in China are willing to help with charging, directions, or short explanations. Saying 请问 first makes you sound respectful instead of demanding.",
                practice=[
                    "Ask if the subway station is near.",
                    "Ask if you may charge your phone.",
                ],
            ),
        ],
    ),
    Book(
        number="72",
        slug="DailyChineseConversations",
        title="Daily Chinese Conversations for Beginners",
        subtitle="日常会话中文：问候、时间、计划和感受",
        color="#2A9D8F",
        audience="Learners who want to speak simple, natural Chinese in everyday life.",
        promise="Build confidence through short, repeatable dialogues you can use every week.",
        source_notes=["11", "13", "77", "100", "158"],
        units=[
            Unit(
                title="Greetings and Self-Introduction",
                situation="You meet someone for the first time and want to sound friendly, simple, and natural.",
                vocab=[
                    ("你好", "Hello", "Basic greeting"),
                    ("我叫......", "My name is ...", "Introduce yourself"),
                    ("你呢", "And you", "Return the question"),
                    ("很高兴认识你", "Nice to meet you", "First meetings"),
                    ("我是美国人", "I am American", "Say your nationality"),
                ],
                dialogue=[
                    ("A", "你好，我叫Anna。", "Hello, my name is Anna."),
                    ("B", "你好，我叫李明。", "Hello, my name is Li Ming."),
                    ("A", "很高兴认识你。", "Nice to meet you."),
                    ("B", "我也很高兴认识你。", "Nice to meet you too."),
                    ("A", "我是美国人，你呢？", "I am American. And you?"),
                    ("B", "我是中国人。", "I am Chinese."),
                ],
                patterns=[
                    ("我叫......。", "My name is ...", "我叫Anna。"),
                    ("我是......人。", "I am from ...", "我是中国人。"),
                    ("你呢？", "And you?", "我是老师，你呢？"),
                ],
                culture_note="In Chinese, self-introductions are usually short and efficient. You do not need a long speech. A name, a country, and one friendly sentence are enough for a smooth beginning.",
                practice=[
                    "Introduce yourself with your name and country.",
                    "Say nice to meet you and ask the other person the same question.",
                ],
            ),
            Unit(
                title="Talking About Time and Schedule",
                situation="You want to say when you are free, what day it is, and when to meet again.",
                vocab=[
                    ("今天", "Today", "Talk about now"),
                    ("明天", "Tomorrow", "Make simple plans"),
                    ("星期四", "Thursday", "Name weekdays"),
                    ("几点", "What time", "Ask time"),
                    ("有空", "Be free", "Check availability"),
                ],
                dialogue=[
                    ("A", "你明天有空吗？", "Are you free tomorrow?"),
                    ("B", "明天不行，我星期四有空。", "Tomorrow does not work. I am free on Thursday."),
                    ("A", "好，星期四下午三点可以吗？", "Okay. Is Thursday at 3 p.m. okay?"),
                    ("B", "可以。", "Yes, that works."),
                    ("A", "那我们星期四见。", "Then see you on Thursday."),
                    ("B", "好，星期四见。", "Great, see you on Thursday."),
                ],
                patterns=[
                    ("你......有空吗？", "Are you free ...?", "你明天有空吗？"),
                    ("......可以吗？", "Is ... okay?", "下午三点可以吗？"),
                    ("......见。", "See you ...", "星期四见。"),
                ],
                culture_note="Chinese time expressions usually move from bigger time to smaller time: 星期四下午三点. This order feels very logical once you get used to it.",
                practice=[
                    "Ask a friend if they are free tomorrow.",
                    "Set a meeting for Thursday afternoon.",
                ],
            ),
            Unit(
                title="Making Plans with Friends",
                situation="You want to suggest coffee, dinner, or a simple weekend plan without sounding too formal.",
                vocab=[
                    ("要不要", "Do you want to", "Friendly suggestion"),
                    ("一起", "Together", "Invite someone"),
                    ("吃饭", "Eat a meal", "A common activity"),
                    ("周末", "Weekend", "Plan free time"),
                    ("当然", "Of course", "Warm positive answer"),
                ],
                dialogue=[
                    ("A", "周末要不要一起吃饭？", "Do you want to have a meal together this weekend?"),
                    ("B", "好啊。你想吃什么？", "Sure. What do you want to eat?"),
                    ("A", "我想吃火锅。", "I want to eat hotpot."),
                    ("B", "当然可以。", "Of course."),
                    ("A", "那我们星期六去吧。", "Then let us go on Saturday."),
                    ("B", "没问题。", "No problem."),
                ],
                patterns=[
                    ("要不要 + verb", "Do you want to ...?", "要不要一起去？"),
                    ("我想 + verb", "I want to ...", "我想吃火锅。"),
                    ("那我们......吧。", "Then let us ...", "那我们星期六去吧。"),
                ],
                culture_note="好啊 is warmer than just 好. It often sounds more natural in friendly invitations because it shows emotion, not only agreement.",
                practice=[
                    "Invite someone to eat together this weekend.",
                    "Answer yes and suggest a day.",
                ],
            ),
            Unit(
                title="Talking About Feelings and Preferences",
                situation="You want to say what you like, do not like, and how you feel in simple daily conversation.",
                vocab=[
                    ("喜欢", "Like", "Talk about preference"),
                    ("不喜欢", "Do not like", "Negative preference"),
                    ("觉得", "Feel / think", "Give your opinion"),
                    ("累", "Tired", "State your condition"),
                    ("开心", "Happy", "Talk about emotions"),
                ],
                dialogue=[
                    ("A", "你喜欢上海吗？", "Do you like Shanghai?"),
                    ("B", "喜欢，我觉得很有意思。", "Yes. I think it is very interesting."),
                    ("A", "你今天怎么样？", "How are you today?"),
                    ("B", "有点累，但是很开心。", "A little tired, but very happy."),
                    ("A", "为什么开心？", "Why are you happy?"),
                    ("B", "因为今天中文说得不错。", "Because I spoke Chinese well today."),
                ],
                patterns=[
                    ("你喜欢......吗？", "Do you like ...?", "你喜欢火锅吗？"),
                    ("我觉得......", "I think / feel ...", "我觉得很有意思。"),
                    ("有点 + adjective", "A little ...", "有点累。"),
                ],
                culture_note="Saying 有点累 sounds softer and more natural than a very strong statement. Chinese often prefers a slightly gentler tone in daily conversation.",
                practice=[
                    "Say what city or food you like.",
                    "Say you are a little tired but happy.",
                ],
            ),
        ],
    ),
    Book(
        number="73",
        slug="PronunciationThatWorks",
        title="Chinese Pronunciation That Actually Works",
        subtitle="实用发音中文：拼音、声调和易混音",
        color="#264653",
        audience="Beginners who want clear pronunciation without drowning in theory.",
        promise="Fix the sounds that matter most for being understood in real conversation.",
        source_notes=["173", "171", "182"],
        units=[
            Unit(
                title="The Four Tones in Real Conversation",
                situation="You know pinyin letters, but the tones still feel abstract. This unit turns tones into practical speaking tools.",
                vocab=[
                    ("妈", "Mother", "First tone example"),
                    ("麻", "Hemp / numb", "Second tone example"),
                    ("马", "Horse", "Third tone example"),
                    ("骂", "Scold", "Fourth tone example"),
                    ("吗", "Question particle", "Neutral tone example"),
                ],
                dialogue=[
                    ("Teacher", "今天我们先练四个声调。", "Today we will first practice the four tones."),
                    ("Student", "我最怕第三声。", "I am most afraid of the third tone."),
                    ("Teacher", "没关系，先听，再慢慢说。", "It is okay. Listen first, then say it slowly."),
                    ("Student", "妈，麻，马，骂。", "ma level, ma rising, ma dipping, ma falling."),
                    ("Teacher", "很好，再加一个吗。", "Very good. Add one more: ma neutral."),
                    ("Student", "我觉得清楚多了。", "I feel it is much clearer now."),
                ],
                patterns=[
                    ("先......，再......", "First ..., then ...", "先听，再说。"),
                    ("我最怕......。", "I am most afraid of ...", "我最怕第三声。"),
                    ("......多了。", "... much more", "清楚多了。"),
                ],
                culture_note="Teachers in China often tell learners not to chase perfection too early. Clear rhythm, patient repetition, and good listening usually improve tones faster than memorizing theory alone.",
                practice=[
                    "Say 妈, 麻, 马, 骂 slowly and clearly.",
                    "Use 先......再...... to describe your study order.",
                ],
            ),
            Unit(
                title="j q x and zh ch sh",
                situation="Many learners can hear that these sounds are different, but they still mix them when speaking fast.",
                vocab=[
                    ("鸡", "Chicken", "j sound"),
                    ("七", "Seven", "q sound"),
                    ("西", "West", "x sound"),
                    ("知", "Know", "zh sound"),
                    ("吃", "Eat", "ch sound"),
                ],
                dialogue=[
                    ("Teacher", "今天我们分两组练：j q x 和 zh ch sh。", "Today we will practice two groups: j q x and zh ch sh."),
                    ("Student", "我总是把七和吃说得很像。", "I always say qi and chi too similarly."),
                    ("Teacher", "很好，这就是今天要解决的问题。", "Good. That is exactly the problem we will solve today."),
                    ("Student", "鸡，七，西。", "ji, qi, xi."),
                    ("Teacher", "再来：知，吃，师。", "Again: zhi, chi, shi."),
                    ("Student", "现在差别大一点了。", "Now the difference is a bit bigger."),
                ],
                patterns=[
                    ("我总是把 A 和 B 说得很像。", "I always pronounce A and B too similarly.", "我总是把七和吃说得很像。"),
                    ("这就是......。", "This is exactly ...", "这就是问题。"),
                    ("再来。", "Again.", "再来。"),
                ],
                culture_note="A lot of teachers use physical mouth position and air flow instead of long explanations. That practical style often works well because learners can copy what they hear and feel immediately.",
                practice=[
                    "Read 鸡，七，西 three times.",
                    "Read 知，吃，师 three times.",
                ],
            ),
            Unit(
                title="Finals, Tone Pairs, and Natural Rhythm",
                situation="Single sounds are one thing. Natural two-syllable rhythm is the next step to sounding smoother.",
                vocab=[
                    ("谢谢", "Thank you", "Tone pair practice"),
                    ("可以", "Can / may", "Common daily rhythm"),
                    ("明天", "Tomorrow", "Two-syllable rhythm"),
                    ("地方", "Place", "Neutral stress practice"),
                    ("一起", "Together", "Frequent speech chunk"),
                ],
                dialogue=[
                    ("Teacher", "单个音会了，现在练两个音的节奏。", "You know the single sounds. Now practice the rhythm of two syllables."),
                    ("Student", "谢谢和学习我都容易说快。", "I say xiexie and xuexi too quickly."),
                    ("Teacher", "先慢一点，再连起来。", "First slow down, then connect them."),
                    ("Student", "谢谢，可以，明天，一起。", "thank you, can, tomorrow, together."),
                    ("Teacher", "很好，你的节奏更自然了。", "Great. Your rhythm is more natural now."),
                    ("Student", "我听起来没那么硬了。", "I do not sound as stiff now."),
                ],
                patterns=[
                    ("先慢一点，再......", "First slower, then ...", "先慢一点，再连起来。"),
                    ("......更自然了。", "... is more natural now.", "节奏更自然了。"),
                    ("没那么 + adjective", "Not so ...", "没那么硬了。"),
                ],
                culture_note="Natural Chinese rhythm is not only about tones. It is also about where the voice relaxes and where it stays light. Common two-syllable chunks are one of the fastest ways to sound more natural.",
                practice=[
                    "Say 谢谢，可以，明天，一起 with a smooth rhythm.",
                    "Describe whether your speech sounds more natural now.",
                ],
            ),
            Unit(
                title="The Most Common Sound-Alike Traps",
                situation="You want to avoid the embarrassing mistakes that come from saying one familiar word like another.",
                vocab=[
                    ("师傅", "Master / skilled worker", "Useful service title"),
                    ("舒服", "Comfortable", "Common adjective"),
                    ("沙发", "Sofa", "Frequent sound trap with 师傅"),
                    ("四", "Four", "Often confused with 十"),
                    ("十", "Ten", "Often confused with 四"),
                ],
                dialogue=[
                    ("Student", "我上次想说师傅，结果说成了舒服。", "Last time I wanted to say shifu, but I said shufu."),
                    ("Teacher", "没关系，这个错误很常见。", "That is okay. This mistake is very common."),
                    ("Student", "还有四和十，我也常常说错。", "And si and shi. I often say those wrong too."),
                    ("Teacher", "今天我们只练这些高频陷阱。", "Today we will practice only these high-frequency traps."),
                    ("Student", "师傅，舒服，沙发。", "shifu, shufu, shafa."),
                    ("Teacher", "对，就是这样。", "Yes, exactly like that."),
                ],
                patterns=[
                    ("我上次想说 A，结果说成了 B。", "Last time I wanted to say A, but said B instead.", "我上次想说师傅，结果说成了舒服。"),
                    ("......很常见。", "... is very common.", "这个错误很常见。"),
                    ("就是这样。", "Exactly like that.", "对，就是这样。"),
                ],
                culture_note="Sound-alike mistakes are a normal part of Chinese learning. The most useful strategy is not to panic. Learn a short list of common traps and over-practice them until they feel automatic.",
                practice=[
                    "Read 师傅，舒服，沙发 slowly.",
                    "Read 四 and 十 clearly in contrast.",
                ],
            ),
        ],
    ),
    Book(
        number="74",
        slug="GrammarThroughRealLife",
        title="Chinese Grammar Through Real Life",
        subtitle="真实场景语法：时间、数字、不没和句子顺序",
        color="#8AB17D",
        audience="Beginners who want to understand grammar through useful situations instead of dry rules.",
        promise="Learn the grammar points foreigners struggle with most by seeing them in action.",
        source_notes=["49", "77", "84", "175", "182"],
        units=[
            Unit(
                title="是, 很, 有: The Three Building Blocks",
                situation="You want to make simple but correct sentences about identity, description, and possession.",
                vocab=[
                    ("我是老师", "I am a teacher", "Use 是 with nouns"),
                    ("上海很大", "Shanghai is big", "Use 很 with adjectives"),
                    ("我有时间", "I have time", "Use 有 for possession"),
                    ("不是", "Is not", "Negative with nouns"),
                    ("没有", "Do not have", "Negative with possession"),
                ],
                dialogue=[
                    ("Teacher", "中文里，是、很、有的用法很重要。", "In Chinese, the usage of shi, hen, and you is very important."),
                    ("Student", "我可以说上海是大吗？", "Can I say Shanghai shi big?"),
                    ("Teacher", "不可以，要说上海很大。", "No. You should say Shanghai is very big."),
                    ("Student", "那我可以说我是学生。", "Then I can say I am a student."),
                    ("Teacher", "对，还可以说我有时间。", "Correct. You can also say I have time."),
                    ("Student", "现在我清楚一点了。", "Now I understand it a bit better."),
                ],
                patterns=[
                    ("A 是 B。", "A is B.", "我是学生。"),
                    ("A 很 + adjective", "A is ...", "上海很大。"),
                    ("A 有 B。", "A has B.", "我有时间。"),
                ],
                culture_note="One reason Chinese feels efficient is that adjectives do not need the same kind of linking verb pattern that English uses. Once learners understand this, their sentences often become much smoother.",
                practice=[
                    "Write one sentence with 是, one with 很, and one with 有.",
                    "Say how to describe your city correctly.",
                ],
            ),
            Unit(
                title="不 and 没 in Daily Speech",
                situation="You know both words mean no or not, but you are never sure which one to use.",
                vocab=[
                    ("不吃", "Do not eat", "Habit or refusal"),
                    ("没吃", "Did not eat yet", "Past / current completion"),
                    ("不去", "Will not go", "Plan or refusal"),
                    ("没去", "Did not go", "Past event"),
                    ("没问题", "No problem", "Very common phrase"),
                ],
                dialogue=[
                    ("Student", "老师，不和没我总是分不清。", "Teacher, I always cannot clearly tell bu and mei apart."),
                    ("Teacher", "很简单，不常常说习惯和想法，没常常说结果。", "It is simple. Bu often talks about habits or intentions. Mei often talks about results."),
                    ("Student", "所以我不吃辣，是习惯。", "So I do not eat spicy food is a habit."),
                    ("Teacher", "对。你没吃饭，是还没有完成。", "Right. You have not eaten yet means the action is not completed."),
                    ("Student", "明白了。", "I understand."),
                    ("Teacher", "好，我们再多练几个。", "Great. Let us practice a few more."),
                ],
                patterns=[
                    ("不 + verb", "Do not / will not ...", "我不去。"),
                    ("没 + verb", "Did not / have not ...", "我没去。"),
                    ("还没 + verb", "Have not ... yet", "我还没吃饭。"),
                ],
                culture_note="The difference between 不 and 没 becomes easier when you stop translating word by word and start asking: am I talking about a habit, an intention, or a completed result?",
                practice=[
                    "Say one sentence with 不 and one with 没.",
                    "Explain whether you do not eat spicy food or just have not eaten yet.",
                ],
            ),
            Unit(
                title="二, 两, Dates, and Daily Numbers",
                situation="You can count in Chinese, but using 二 and 两 still feels unpredictable.",
                vocab=[
                    ("两个", "Two of something", "Count objects"),
                    ("二号", "Number two / second day", "Use in dates or numbers"),
                    ("两点", "Two o'clock", "Use for time"),
                    ("二十四号", "The 24th", "Use for date"),
                    ("一个月", "One month", "Duration"),
                ],
                dialogue=[
                    ("Student", "老师，为什么是两个，不是二个？", "Teacher, why is it liang ge and not er ge?"),
                    ("Teacher", "因为两常常用在量词前面。", "Because liang is often used before measure words."),
                    ("Student", "那二号为什么用二？", "Then why do we use er in date number two?"),
                    ("Teacher", "因为这里是编号，不是数量。", "Because here it is a number label, not a quantity."),
                    ("Student", "明白了，两点，二号。", "I get it: liang dian, er hao."),
                    ("Teacher", "对，就是这个感觉。", "Yes, that is exactly the feeling."),
                ],
                patterns=[
                    ("两 + measure word", "Two ...", "两个朋友。"),
                    ("二 + number label", "Number two as a label", "二号房间。"),
                    ("......号", "...th day / number", "二十四号。"),
                ],
                culture_note="This topic frustrates many beginners because both 二 and 两 mean two. The practical shortcut is simple: 两 usually comes before a measure word, while 二 often reads like a label, date, or number sequence.",
                practice=[
                    "Say two friends and room number two correctly.",
                    "Say the 24th and 2 o'clock correctly.",
                ],
            ),
            Unit(
                title="Chinese Sentence Order Without Fear",
                situation="Your words are right, but your sentence order still feels like translated English.",
                vocab=[
                    ("我明天去上海", "I go to Shanghai tomorrow", "Time before action is common"),
                    ("在这里", "Here / at this place", "Location phrase"),
                    ("给你", "Give to you", "Recipient pattern"),
                    ("跟朋友一起", "Together with friends", "Company phrase"),
                    ("先......再......", "First... then...", "Useful connector"),
                ],
                dialogue=[
                    ("Teacher", "中文句子常常先放时间，再放动作。", "Chinese sentences often place time before the action."),
                    ("Student", "所以我明天去上海，比我去上海明天更自然。", "So wo mingtian qu Shanghai is more natural than wo qu Shanghai mingtian."),
                    ("Teacher", "对。位置和对象也常常放在动词前后固定的位置。", "Right. Location and recipient also often have fixed positions around the verb."),
                    ("Student", "我给你发消息。", "I will send you a message."),
                    ("Teacher", "很好，这个顺序很自然。", "Good. That order is natural."),
                    ("Student", "中文没有我想的那么乱。", "Chinese is not as chaotic as I thought."),
                ],
                patterns=[
                    ("time + subject + verb", "Time often comes early.", "我明天去上海。"),
                    ("给 + person + verb", "Do something for / to someone.", "我给你发消息。"),
                    ("跟 + person + 一起 + verb", "Do something together with someone.", "我跟朋友一起吃饭。"),
                ],
                culture_note="Many learners discover that Chinese word order feels clearer once they think in blocks: time block, people block, place block, then action block. It is less random than it first appears.",
                practice=[
                    "Say: I am going to Shanghai tomorrow.",
                    "Say: I will send you a message tonight.",
                ],
            ),
        ],
    ),
    Book(
        number="75",
        slug="RestaurantChineseFoodCulture",
        title="Restaurant Chinese and Food Culture",
        subtitle="餐馆中文与饮食文化：点菜、口味、买单和中国胃",
        color="#F4A261",
        audience="Food-loving learners who want useful restaurant language plus cultural context.",
        promise="Order confidently while understanding how Chinese people talk about taste, sharing, and recommendations.",
        source_notes=["49", "68", "109", "123", "141"],
        units=[
            Unit(
                title="Ordering Like a Beginner Who Sounds Smart",
                situation="You are in a local restaurant and want to order clearly, even if the menu feels overwhelming.",
                vocab=[
                    ("服务员", "Server", "Get attention politely"),
                    ("菜单", "Menu", "Restaurant basic"),
                    ("招牌菜", "Signature dish", "Ask for a house special"),
                    ("来一个", "Bring one", "Order naturally"),
                    ("够了", "That is enough", "Stop ordering"),
                ],
                dialogue=[
                    ("You", "服务员，麻烦看一下菜单。", "Server, may I see the menu?"),
                    ("Server", "好的。你们几位？", "Sure. How many people are you?"),
                    ("You", "两位。你们有什么招牌菜？", "Two people. What signature dishes do you have?"),
                    ("Server", "这个鱼和这个牛肉都很受欢迎。", "This fish and this beef are both very popular."),
                    ("You", "好，那鱼来一个，牛肉也来一个。", "Okay, then one fish and one beef dish."),
                    ("Server", "好的。", "Okay."),
                ],
                patterns=[
                    ("......来一个。", "Bring one ...", "鱼来一个。"),
                    ("有什么 + noun", "What ... do you have?", "有什么招牌菜？"),
                    ("......也来一个。", "Also bring one ...", "牛肉也来一个。"),
                ],
                culture_note="Chinese ordering is often collaborative. People ask for recommendations, think aloud, and build the order together. A short phrase like 来一个 sounds natural because it fits this shared decision style.",
                practice=[
                    "Ask for the menu and a signature dish.",
                    "Order two dishes for two people.",
                ],
            ),
            Unit(
                title="Taste, Spice, and Food Preferences",
                situation="You need to say what you can eat, what you cannot eat, and how you want the flavor adjusted.",
                vocab=[
                    ("辣", "Spicy", "Very important in China"),
                    ("咸", "Salty", "Describe flavor"),
                    ("甜", "Sweet", "Describe flavor"),
                    ("我不吃......", "I do not eat ...", "Say food restrictions"),
                    ("少一点", "A little less", "Adjust flavor politely"),
                ],
                dialogue=[
                    ("Server", "你吃辣吗？", "Do you eat spicy food?"),
                    ("You", "吃一点，但是不要太辣。", "A little, but not too spicy."),
                    ("Server", "好的。还有别的要求吗？", "Okay. Any other requests?"),
                    ("You", "盐少一点，我不吃太咸的。", "A little less salt. I do not eat very salty food."),
                    ("Server", "明白。", "Understood."),
                    ("You", "谢谢。", "Thank you."),
                ],
                patterns=[
                    ("吃一点，但是不要太......", "A little, but not too ...", "吃一点，但是不要太辣。"),
                    ("......少一点。", "A little less ...", "盐少一点。"),
                    ("我不吃太......的。", "I do not eat things that are too ...", "我不吃太甜的。"),
                ],
                culture_note="Regional Chinese food can vary hugely in spice, oil, sweetness, and texture. Asking for 少一点 is often more natural than asking for a complete change, because it sounds flexible instead of demanding.",
                practice=[
                    "Say you eat a little spicy food, but not too much.",
                    "Ask for less salt or less oil.",
                ],
            ),
            Unit(
                title="Paying the Bill, Splitting, and Packing Food",
                situation="The meal is over. Now you need to pay, maybe split, or take leftovers home.",
                vocab=[
                    ("买单", "Pay the bill", "Common phrase"),
                    ("一起付", "Pay together", "Group payment"),
                    ("分开付", "Pay separately", "Split the bill"),
                    ("打包", "Pack to go", "Take leftovers"),
                    ("发票", "Receipt / fapiao", "Ask for an official receipt"),
                ],
                dialogue=[
                    ("You", "服务员，买单。", "Server, bill please."),
                    ("Server", "好的，一起付还是分开付？", "Sure. Together or separately?"),
                    ("You", "一起付。可以开发票吗？", "Together. Can you issue a receipt?"),
                    ("Server", "可以。还要打包吗？", "Yes. Do you also want takeaway packing?"),
                    ("You", "要，这个菜帮我打包一下。", "Yes. Please pack this dish for me."),
                    ("Server", "好的。", "Okay."),
                ],
                patterns=[
                    ("买单。", "Bill please.", "服务员，买单。"),
                    ("一起付还是分开付？", "Together or separately?", "一起付还是分开付？"),
                    ("帮我 + verb + 一下", "Help me ... please", "帮我打包一下。"),
                ],
                culture_note="In China, one person often offers to pay for the whole table, especially in business or family settings. Even when people eventually split the cost, there may be a small ritual of refusing and insisting first.",
                practice=[
                    "Ask to pay together.",
                    "Ask the server to pack one dish for you.",
                ],
            ),
            Unit(
                title="Why Chinese People Talk About Food So Much",
                situation="You want to move beyond ordering and actually join a Chinese conversation about food and taste.",
                vocab=[
                    ("口味", "Taste preference", "Talk about style"),
                    ("清淡", "Light flavor", "Describe gentle food"),
                    ("重口味", "Strong flavor", "Describe bold food"),
                    ("推荐", "Recommend", "Talk about what is good"),
                    ("下次", "Next time", "Plan future food outings"),
                ],
                dialogue=[
                    ("Friend", "你觉得这个菜怎么样？", "What do you think of this dish?"),
                    ("You", "我觉得很好吃，而且不太油。", "I think it is delicious, and not too oily."),
                    ("Friend", "你喜欢清淡一点的口味吗？", "Do you like lighter flavors?"),
                    ("You", "对，我比较喜欢清淡一点。", "Yes. I prefer lighter flavors."),
                    ("Friend", "那下次我带你去吃粤菜。", "Then next time I will take you to eat Cantonese food."),
                    ("You", "好啊，很期待。", "Great, I am looking forward to it."),
                ],
                patterns=[
                    ("你觉得......怎么样？", "What do you think of ...?", "你觉得这个菜怎么样？"),
                    ("我比较喜欢......", "I relatively prefer ...", "我比较喜欢清淡一点。"),
                    ("下次我带你去......", "Next time I will take you to ...", "下次我带你去吃粤菜。"),
                ],
                culture_note="Food is one of the easiest doors into Chinese social life. Talking about taste, restaurants, hometown dishes, and what to try next is a natural way to build relationships.",
                practice=[
                    "Say what kind of taste you prefer.",
                    "Ask a friend what they think of a dish.",
                ],
            ),
        ],
    ),
    Book(
        number="76",
        slug="DigitalLifeInChina",
        title="Digital Life in China",
        subtitle="数字生活中文：扫码、支付、外卖、打车和App沟通",
        color="#577590",
        audience="Foreign learners who want to function in China’s app-first daily life.",
        promise="Learn the Chinese that unlocks QR codes, mobile payment, delivery, and ride-hailing.",
        source_notes=["49", "64", "113", "166"],
        units=[
            Unit(
                title="QR Codes, Wi-Fi, and Getting Connected",
                situation="You arrive at a cafe, shop, or office and need to connect to the local digital system quickly.",
                vocab=[
                    ("扫码", "Scan the code", "Common daily action"),
                    ("二维码", "QR code", "Everywhere in China"),
                    ("无线网", "Wi-Fi", "Ask for internet"),
                    ("密码", "Password", "Get access"),
                    ("连接", "Connect", "Basic digital verb"),
                ],
                dialogue=[
                    ("You", "请问，你们有无线网吗？", "Excuse me, do you have Wi-Fi?"),
                    ("Staff", "有，先扫码。", "Yes. Scan the code first."),
                    ("You", "好的，密码是什么？", "Okay. What is the password?"),
                    ("Staff", "不用密码，扫码就可以连接。", "No password needed. Just scan and connect."),
                    ("You", "明白了。", "Got it."),
                    ("Staff", "如果不行，我帮你。", "If it does not work, I will help you."),
                ],
                patterns=[
                    ("有......吗？", "Do you have ...?", "有无线网吗？"),
                    ("先......，再......", "First ..., then ...", "先扫码，再连接。"),
                    ("如果不行，......", "If it does not work, ...", "如果不行，我帮你。"),
                ],
                culture_note="Scanning a QR code is normal in China for menus, Wi-Fi, ticketing, and account registration. Many businesses assume customers are comfortable with it, so learning 扫码 early saves a lot of friction.",
                practice=[
                    "Ask if a cafe has Wi-Fi.",
                    "Tell someone you cannot connect and need help.",
                ],
            ),
            Unit(
                title="Paying with WeChat or Alipay",
                situation="You are ready to buy something, but the whole payment process happens on the phone.",
                vocab=[
                    ("微信支付", "WeChat Pay", "Common payment method"),
                    ("支付宝", "Alipay", "Common payment app"),
                    ("现金", "Cash", "Ask whether cash works"),
                    ("付款", "Pay", "Action verb"),
                    ("收款码", "Payment code", "Merchant QR code"),
                ],
                dialogue=[
                    ("You", "可以用现金吗？", "Can I use cash?"),
                    ("Clerk", "可以，不过微信支付更方便。", "Yes, but WeChat Pay is more convenient."),
                    ("You", "我也有支付宝。", "I also have Alipay."),
                    ("Clerk", "好，扫这个收款码就可以付款。", "Great. Just scan this payment code to pay."),
                    ("You", "好了，你收到了吗？", "Done. Did you receive it?"),
                    ("Clerk", "收到了，谢谢。", "Yes, I got it. Thanks."),
                ],
                patterns=[
                    ("可以用......吗？", "Can I use ...?", "可以用现金吗？"),
                    ("......更方便。", "... is more convenient.", "微信支付更方便。"),
                    ("扫这个......就可以......", "Scan this ... and then you can ...", "扫这个收款码就可以付款。"),
                ],
                culture_note="Cash is still legal and usable in China, but mobile payment often moves faster. Foreigners who set up WeChat Pay or Alipay usually find daily life much smoother, especially in small shops.",
                practice=[
                    "Ask if you can use cash.",
                    "Say that you also have Alipay and can pay by phone.",
                ],
            ),
            Unit(
                title="Ordering Delivery and Sending an Address",
                situation="You want food or coffee delivered, but need to understand address details and delivery timing.",
                vocab=[
                    ("外卖", "Delivery food", "Daily city life"),
                    ("地址", "Address", "Core logistics word"),
                    ("备注", "Order note", "Tell the courier a detail"),
                    ("到了", "Arrived", "Very common notification"),
                    ("楼下", "Downstairs", "Meet the courier"),
                ],
                dialogue=[
                    ("Friend", "你会点外卖吗？", "Do you know how to order delivery?"),
                    ("You", "还不太会。", "Not really yet."),
                    ("Friend", "先写地址，再写备注。", "First write the address, then add an order note."),
                    ("You", "备注可以写什么？", "What can I write in the note?"),
                    ("Friend", "你可以写：到了以后放楼下。", "You can write: after arriving, leave it downstairs."),
                    ("You", "懂了。", "Got it."),
                ],
                patterns=[
                    ("还不太会。", "Not really yet.", "我还不太会。"),
                    ("先 + verb，再 + verb", "First ..., then ...", "先写地址，再写备注。"),
                    ("可以写：......", "You can write: ...", "可以写：到了以后放楼下。"),
                ],
                culture_note="In Chinese cities, exact addresses often include building number, gate, floor, and even nearby landmarks. The order note matters because it helps delivery workers move faster and call less.",
                practice=[
                    "Say that you do not really know how to order delivery yet.",
                    "Write a short note asking the courier to leave food downstairs.",
                ],
            ),
            Unit(
                title="Ride-Hailing, Location, and Mini Programs",
                situation="You need a ride and want to share your destination smoothly through an app-based system.",
                vocab=[
                    ("打车", "Call a ride", "General term"),
                    ("定位", "Location", "Phone location feature"),
                    ("目的地", "Destination", "Core transport word"),
                    ("司机", "Driver", "Useful title"),
                    ("小程序", "Mini program", "WeChat built-in app"),
                ],
                dialogue=[
                    ("You", "我已经打车了。", "I have already called a ride."),
                    ("Friend", "司机到哪儿了？", "Where is the driver now?"),
                    ("You", "他快到了，但是定位不太准。", "He is almost here, but the location is not very accurate."),
                    ("Driver", "你好，你的目的地是这个地址吗？", "Hello. Is your destination this address?"),
                    ("You", "对，是这里。", "Yes, it is here."),
                    ("Driver", "好，我到了给你打电话。", "Okay. I will call you when I arrive."),
                ],
                patterns=[
                    ("我已经 + verb + 了。", "I have already ...", "我已经打车了。"),
                    ("......不太准。", "... is not very accurate.", "定位不太准。"),
                    ("......是这个地址吗？", "Is ... this address?", "你的目的地是这个地址吗？"),
                ],
                culture_note="Chinese digital life is deeply integrated. Sometimes you do not need a separate app at all because a service already exists as a mini program inside WeChat. That convenience is one reason people rely on phones so heavily.",
                practice=[
                    "Say that you already called a ride.",
                    "Confirm that the destination is the correct address.",
                ],
            ),
        ],
    ),
    Book(
        number="77",
        slug="BusinessChineseBuyersSuppliers",
        title="Business Chinese for Buyers and Suppliers",
        subtitle="商务中文：询价、起订量、交期和跟进",
        color="#C1121F",
        audience="Professionals who need Chinese for practical supplier and distributor communication.",
        promise="Use short, high-value business phrases that help real work conversations move forward.",
        source_notes=["88", "129", "189"],
        units=[
            Unit(
                title="The First Meeting and Proper Titles",
                situation="You are meeting a supplier or distributor for the first time and want to sound polite and businesslike.",
                vocab=[
                    ("王总", "General Manager Wang", "Polite business title"),
                    ("老板", "Boss", "Common business title"),
                    ("认识你很高兴", "Nice to meet you", "Business greeting"),
                    ("介绍一下", "Introduce briefly", "Ask for background"),
                    ("合作", "Cooperate", "Talk about working together"),
                ],
                dialogue=[
                    ("You", "王总，你好，认识你很高兴。", "Hello, Manager Wang. Nice to meet you."),
                    ("Partner", "你好，欢迎你来。", "Hello. Welcome."),
                    ("You", "我想先介绍一下我们公司。", "I would like to briefly introduce our company first."),
                    ("Partner", "好，也请你介绍一下需求。", "Good. Please also introduce your needs."),
                    ("You", "我们希望找长期合作的供应商。", "We hope to find a long-term supplier."),
                    ("Partner", "明白。", "Understood."),
                ],
                patterns=[
                    ("X总，你好。", "Hello, Manager X.", "王总，你好。"),
                    ("我想先介绍一下......", "I want to first introduce ...", "我想先介绍一下我们公司。"),
                    ("我们希望......", "We hope to ...", "我们希望长期合作。"),
                ],
                culture_note="Titles matter in Chinese business settings, especially early in the relationship. Using 王总 or 李总 signals respect and helps the conversation begin on the right footing.",
                practice=[
                    "Greet a supplier politely using a title.",
                    "Say that your company wants long-term cooperation.",
                ],
            ),
            Unit(
                title="Price, Quantity, and Minimum Order Quantity",
                situation="You need the basic numbers: price, quantity, and MOQ before the conversation gets more detailed.",
                vocab=[
                    ("多少钱", "How much", "Ask the price"),
                    ("数量", "Quantity", "Talk about order size"),
                    ("最少", "Minimum", "Ask for MOQ"),
                    ("报价", "Quotation", "Request formal pricing"),
                    ("样品", "Sample", "Ask to test first"),
                ],
                dialogue=[
                    ("You", "这个产品多少钱？", "How much is this product?"),
                    ("Supplier", "要看数量。", "That depends on quantity."),
                    ("You", "最少买多少个？", "What is the minimum order quantity?"),
                    ("Supplier", "最少一千个。", "The minimum is 1,000 pieces."),
                    ("You", "可以先给我报价和样品吗？", "Can you first give me a quotation and samples?"),
                    ("Supplier", "可以。", "Yes."),
                ],
                patterns=[
                    ("......多少钱？", "How much is ...?", "这个产品多少钱？"),
                    ("最少 + verb + quantity", "Minimum amount", "最少买多少个？"),
                    ("可以先给我......吗？", "Can you first give me ...?", "可以先给我报价吗？"),
                ],
                culture_note="Chinese business conversations often move from broad interest to exact numbers quite fast. Being able to ask for price, sample, and MOQ efficiently makes you sound prepared, even with simple Chinese.",
                practice=[
                    "Ask the price of a product.",
                    "Ask for the MOQ and a sample.",
                ],
            ),
            Unit(
                title="Delivery Time, Payment, and Next Steps",
                situation="Now you need to talk about schedule, production capacity, and how the deal would actually move forward.",
                vocab=[
                    ("交期", "Delivery time", "Core production word"),
                    ("定金", "Deposit", "Common payment term"),
                    ("尾款", "Final payment", "Payment completion"),
                    ("发货", "Ship goods", "Logistics action"),
                    ("确认", "Confirm", "Push process forward"),
                ],
                dialogue=[
                    ("You", "交期大概多久？", "Roughly how long is the delivery time?"),
                    ("Supplier", "如果现在确认，三周可以发货。", "If you confirm now, we can ship in three weeks."),
                    ("You", "付款方式是什么？", "What is the payment method?"),
                    ("Supplier", "先付三成定金，发货前付尾款。", "First pay a 30 percent deposit, then pay the balance before shipment."),
                    ("You", "好，我回去以后确认一下。", "Okay. I will confirm after I go back."),
                    ("Supplier", "没问题。", "No problem."),
                ],
                patterns=[
                    ("大概多久？", "Roughly how long?", "交期大概多久？"),
                    ("如果......，就......", "If ..., then ...", "如果现在确认，三周可以发货。"),
                    ("我回去以后......", "After I go back, I will ...", "我回去以后确认一下。"),
                ],
                culture_note="Business Chinese often uses clear step-by-step logic: confirm, pay deposit, produce, ship, settle the balance. Learning that flow helps you understand not only words, but the rhythm of the deal.",
                practice=[
                    "Ask about delivery time.",
                    "Repeat the payment terms in one sentence.",
                ],
            ),
            Unit(
                title="Negotiating Politely and Following Up",
                situation="You want a better price or better terms, but you also want to protect the relationship.",
                vocab=[
                    ("便宜一点", "A little cheaper", "Simple negotiation phrase"),
                    ("再考虑一下", "Consider again", "Push gently"),
                    ("邮件", "Email", "Follow-up communication"),
                    ("下周", "Next week", "Set a timeline"),
                    ("保持联系", "Keep in touch", "Close a meeting well"),
                ],
                dialogue=[
                    ("You", "如果数量大一点，价格可以便宜一点吗？", "If the quantity is larger, can the price be a little lower?"),
                    ("Supplier", "我可以再考虑一下。", "I can think about it again."),
                    ("You", "好，你可以下周给我发邮件吗？", "Okay. Can you send me an email next week?"),
                    ("Supplier", "可以。", "Yes."),
                    ("You", "那我们保持联系。", "Then let us keep in touch."),
                    ("Supplier", "好的。", "Okay."),
                ],
                patterns=[
                    ("如果......，可以......吗？", "If ..., can ...?", "如果数量大一点，价格可以便宜一点吗？"),
                    ("再 + verb + 一下", "Do ... again briefly", "再考虑一下。"),
                    ("保持联系。", "Keep in touch.", "我们保持联系。"),
                ],
                culture_note="In Chinese negotiation, directness works best when it stays calm and relational. A phrase like 便宜一点 sounds softer and more natural than an aggressive discount demand.",
                practice=[
                    "Ask for a slightly lower price if quantity is larger.",
                    "Ask the supplier to follow up by email next week.",
                ],
            ),
        ],
    ),
    Book(
        number="78",
        slug="ChineseFestivals",
        title="Learn Chinese Through Chinese Festivals",
        subtitle="节日中文：春节、元宵、中秋和端午",
        color="#D62828",
        audience="Learners who want culture-rich Chinese that feels memorable and human.",
        promise="Use festival language to learn both Chinese expressions and the cultural logic behind them.",
        source_notes=["200", "201", "205", "209"],
        units=[
            Unit(
                title="Spring Festival Greetings and Family Talk",
                situation="You want to greet people naturally during the biggest holiday in the Chinese calendar.",
                vocab=[
                    ("春节快乐", "Happy Spring Festival", "Holiday greeting"),
                    ("新年快乐", "Happy New Year", "General greeting"),
                    ("红包", "Red envelope", "Holiday custom"),
                    ("团圆", "Reunion", "Family-centered idea"),
                    ("过年", "Celebrate the new year", "Common verb phrase"),
                ],
                dialogue=[
                    ("You", "春节快乐！", "Happy Spring Festival!"),
                    ("Friend", "春节快乐，新年快乐！", "Happy Spring Festival. Happy New Year!"),
                    ("You", "你今年怎么过年？", "How are you celebrating the new year this year?"),
                    ("Friend", "我回老家，跟家人团圆。", "I am going back to my hometown to reunite with family."),
                    ("You", "你们发红包吗？", "Do you give red envelopes?"),
                    ("Friend", "当然发。", "Of course we do."),
                ],
                patterns=[
                    ("......快乐！", "Happy ...!", "新年快乐！"),
                    ("你今年怎么......？", "How are you ... this year?", "你今年怎么过年？"),
                    ("当然 + verb", "Of course ...", "当然发。"),
                ],
                culture_note="Spring Festival language is warm, relational, and full of good wishes. Even learners with limited Chinese can make a strong impression by using a few sincere festival greetings well.",
                practice=[
                    "Wish someone a happy Spring Festival.",
                    "Ask a friend how they celebrate the new year.",
                ],
            ),
            Unit(
                title="Lantern Festival, Family, and the End of the Holiday Season",
                situation="You want to talk about 元宵节 and understand why it feels like the closing chapter of Spring Festival.",
                vocab=[
                    ("元宵节", "Lantern Festival", "Holiday name"),
                    ("汤圆", "Sweet rice balls", "Holiday food"),
                    ("灯笼", "Lantern", "Classic symbol"),
                    ("热闹", "Lively", "Describe festival atmosphere"),
                    ("结束", "End", "Talk about holiday timing"),
                ],
                dialogue=[
                    ("You", "元宵节你们吃什么？", "What do you eat for the Lantern Festival?"),
                    ("Friend", "我们吃汤圆。", "We eat tangyuan."),
                    ("You", "城市里也会挂灯笼吗？", "Do cities also hang lanterns?"),
                    ("Friend", "会，有的地方很热闹。", "Yes. Some places are very lively."),
                    ("You", "元宵节以后春节就结束了，是吗？", "After the Lantern Festival, Spring Festival is basically over, right?"),
                    ("Friend", "对。", "Right."),
                ],
                patterns=[
                    ("......你们吃什么？", "What do you eat for ...?", "元宵节你们吃什么？"),
                    ("有的地方......", "Some places ...", "有的地方很热闹。"),
                    ("......以后......就结束了。", "After ..., ... ends.", "元宵节以后春节就结束了。"),
                ],
                culture_note="Lantern Festival is not only about a food or decoration. It marks a psychological shift: family reunion time winds down, and ordinary life begins again.",
                practice=[
                    "Ask what people eat during Lantern Festival.",
                    "Say that some places are very lively.",
                ],
            ),
            Unit(
                title="Mid-Autumn Festival and Giving Gifts",
                situation="You want to talk about mooncakes, family gatherings, and polite holiday gift language.",
                vocab=[
                    ("中秋节", "Mid-Autumn Festival", "Holiday name"),
                    ("月饼", "Mooncake", "Core food"),
                    ("赏月", "Appreciate the moon", "Holiday activity"),
                    ("送礼", "Give gifts", "Polite social action"),
                    ("心意", "Thought / goodwill", "Gift language"),
                ],
                dialogue=[
                    ("You", "中秋节快乐！", "Happy Mid-Autumn Festival!"),
                    ("Friend", "谢谢，你也一样。", "Thanks. Same to you."),
                    ("You", "你喜欢吃月饼吗？", "Do you like eating mooncakes?"),
                    ("Friend", "有的喜欢，有的太甜了。", "Some I like. Some are too sweet."),
                    ("You", "中秋节会送礼吗？", "Do people give gifts during Mid-Autumn Festival?"),
                    ("Friend", "会，最重要的是心意。", "Yes. The most important thing is the thought behind it."),
                ],
                patterns=[
                    ("你也一样。", "Same to you.", "谢谢，你也一样。"),
                    ("有的......，有的......", "Some ..., some ...", "有的喜欢，有的太甜了。"),
                    ("最重要的是......", "The most important thing is ...", "最重要的是心意。"),
                ],
                culture_note="Festival gift language in Chinese often emphasizes sincerity over the object itself. Saying 最重要的是心意 sounds natural because it highlights relationship, not only material value.",
                practice=[
                    "Wish someone a happy Mid-Autumn Festival.",
                    "Say that the most important thing in a gift is the thought.",
                ],
            ),
            Unit(
                title="Dragon Boat Festival, Zongzi, and Holiday Movement",
                situation="You want to speak about a shorter but still important holiday in China.",
                vocab=[
                    ("端午节", "Dragon Boat Festival", "Holiday name"),
                    ("粽子", "Rice dumpling", "Holiday food"),
                    ("放假", "Have holiday", "Talk about days off"),
                    ("回家", "Go home", "Travel pattern"),
                    ("人很多", "There are many people", "Useful travel comment"),
                ],
                dialogue=[
                    ("You", "端午节放假吗？", "Do people have time off for Dragon Boat Festival?"),
                    ("Friend", "放，一般放三天。", "Yes. Usually three days."),
                    ("You", "很多人会回家吗？", "Do many people go home?"),
                    ("Friend", "会，所以路上人很多。", "Yes, so there are a lot of people on the road."),
                    ("You", "你喜欢吃粽子吗？", "Do you like zongzi?"),
                    ("Friend", "喜欢，但是我吃得不多。", "Yes, but I do not eat a lot of them."),
                ],
                patterns=[
                    ("......放假吗？", "Is there a holiday for ...?", "端午节放假吗？"),
                    ("一般 + verb / phrase", "Usually ...", "一般放三天。"),
                    ("......人很多。", "... is crowded.", "路上人很多。"),
                ],
                culture_note="Even a short holiday can create major travel movement in China. This is why holiday vocabulary is not only cultural. It is also very practical for trains, roads, and daily planning.",
                practice=[
                    "Ask if people get a holiday for Dragon Boat Festival.",
                    "Say that the roads are crowded during the holiday.",
                ],
            ),
        ],
    ),
    Book(
        number="79",
        slug="SocialChineseRelationships",
        title="Social Chinese for Real Relationships",
        subtitle="社交中文：称呼、邀请、拒绝、感谢和面子",
        color="#9C6644",
        audience="Learners who want Chinese that helps them build trust, not just complete transactions.",
        promise="Sound warmer, more aware, and more culturally fluent in real social situations.",
        source_notes=["79", "80", "86", "119", "134"],
        units=[
            Unit(
                title="Titles, Small Talk, and First Impressions",
                situation="You want to sound polite and socially aware when meeting people in China.",
                vocab=[
                    ("师傅", "Master / driver / repair worker", "Respectful service title"),
                    ("阿姨", "Auntie", "Common title for older women"),
                    ("老板", "Boss", "Friendly shop title"),
                    ("最近怎么样", "How have you been recently", "Natural small talk"),
                    ("辛苦了", "You worked hard", "Warm social phrase"),
                ],
                dialogue=[
                    ("You", "老板，你好。", "Hello, boss."),
                    ("Shop Owner", "你好，你想看什么？", "Hello. What would you like to look at?"),
                    ("You", "我先随便看看。最近生意怎么样？", "I will just look around first. How has business been recently?"),
                    ("Shop Owner", "还可以。", "Not bad."),
                    ("You", "你每天这么忙，辛苦了。", "You are so busy every day. You work hard."),
                    ("Shop Owner", "谢谢。", "Thanks."),
                ],
                patterns=[
                    ("最近怎么样？", "How have things been recently?", "最近怎么样？"),
                    ("我先随便看看。", "I will just look around first.", "我先随便看看。"),
                    ("辛苦了。", "You worked hard.", "辛苦了。"),
                ],
                culture_note="Social Chinese often uses titles instead of names in shops, service settings, and casual conversations. A good title plus a small warm sentence can change the whole tone of an interaction.",
                practice=[
                    "Greet a shop owner politely.",
                    "Say that someone has been working hard.",
                ],
            ),
            Unit(
                title="Inviting Someone and Saying No Politely",
                situation="You want to invite someone, or refuse without sounding cold or rude.",
                vocab=[
                    ("有空一起吃饭", "Have time to eat together", "Soft invitation"),
                    ("下次吧", "Maybe next time", "Gentle refusal"),
                    ("不太方便", "Not very convenient", "Polite limit"),
                    ("改天", "Another day", "Reschedule softly"),
                    ("一定", "Definitely", "Friendly future promise"),
                ],
                dialogue=[
                    ("A", "你这周有空一起吃饭吗？", "Are you free to eat together this week?"),
                    ("B", "这周不太方便，下次吧。", "This week is not very convenient. Maybe next time."),
                    ("A", "好，那改天。", "Okay, then another day."),
                    ("B", "不好意思。", "Sorry about that."),
                    ("A", "没事。", "No worries."),
                    ("B", "下次我一定来。", "Next time I will definitely come."),
                ],
                patterns=[
                    ("有空一起 + verb 吗？", "Are you free to ... together?", "有空一起吃饭吗？"),
                    ("......不太方便。", "... is not very convenient.", "这周不太方便。"),
                    ("下次吧。", "Maybe next time.", "下次吧。"),
                ],
                culture_note="Polite refusal in Chinese often leaves the relationship open. Instead of a hard no, people may say 不太方便 or 下次吧 to reduce tension and protect the feeling between both sides.",
                practice=[
                    "Invite someone to eat together.",
                    "Refuse politely and suggest another day.",
                ],
            ),
            Unit(
                title="Family, Relationship Status, and Boundaries",
                situation="You are in social conversation and personal questions come up quickly.",
                vocab=[
                    ("结婚", "Get married", "Common personal topic"),
                    ("孩子", "Child", "Family conversation"),
                    ("单身", "Single", "Relationship status"),
                    ("先不说这个", "Let us not talk about this yet", "Soft boundary"),
                    ("慢慢来", "Take it slowly", "Defuse pressure"),
                ],
                dialogue=[
                    ("Friend", "你结婚了吗？", "Are you married?"),
                    ("You", "还没有，我现在单身。", "Not yet. I am single now."),
                    ("Friend", "那你想什么时候结婚？", "Then when do you want to get married?"),
                    ("You", "哈哈，先不说这个，慢慢来。", "Haha, let us not talk about that yet. Slowly, slowly."),
                    ("Friend", "好。", "Okay."),
                    ("You", "我们还是聊旅行吧。", "Let us talk about travel instead."),
                ],
                patterns=[
                    ("还没有。", "Not yet.", "我还没有。"),
                    ("先不说这个。", "Let us not talk about this yet.", "先不说这个。"),
                    ("我们还是聊......吧。", "Let us talk about ... instead.", "我们还是聊旅行吧。"),
                ],
                culture_note="Questions about marriage, family, and children can come up early in Chinese social life. They are often meant as involvement, not intrusion. Still, it is helpful to learn soft boundary language you can use comfortably.",
                practice=[
                    "Say that you are not married yet.",
                    "Change the topic politely.",
                ],
            ),
            Unit(
                title="Asking Favors, Saying Thanks, and Protecting Face",
                situation="You need help, but want to ask in a way that sounds considerate and socially smooth.",
                vocab=[
                    ("帮个忙", "Do me a favor", "Soft ask"),
                    ("方便吗", "Is it convenient", "Check willingness"),
                    ("太感谢了", "I am very grateful", "Strong thanks"),
                    ("不好意思", "Sorry / excuse me", "Softens requests"),
                    ("面子", "Face / social dignity", "Core concept"),
                ],
                dialogue=[
                    ("You", "不好意思，能帮个忙吗？", "Sorry to bother you. Can you do me a favor?"),
                    ("Friend", "可以，什么事？", "Sure. What is it?"),
                    ("You", "你现在方便吗？我想请你看一下这个中文。", "Is now convenient? I want to ask you to look at this Chinese for me."),
                    ("Friend", "没问题。", "No problem."),
                    ("You", "太感谢了。", "I am very grateful."),
                    ("Friend", "小事。", "It is a small thing."),
                ],
                patterns=[
                    ("能帮个忙吗？", "Can you do me a favor?", "能帮个忙吗？"),
                    ("你现在方便吗？", "Is now convenient for you?", "你现在方便吗？"),
                    ("太感谢了。", "I am very grateful.", "太感谢了。"),
                ],
                culture_note="Chinese requests often include small buffers like 不好意思 and 方便吗 because they respect the other person’s situation. This style reduces pressure and helps everyone keep social ease, or what many people loosely describe as 面子.",
                practice=[
                    "Ask someone for a favor politely.",
                    "Say you are very grateful for the help.",
                ],
            ),
        ],
    ),
    Book(
        number="80",
        slug="ShoppingServicesErrands",
        title="Shopping, Services, and Everyday Errands in Chinese",
        subtitle="购物与日常服务中文：买菜、理发、药店和售后",
        color="#6D597A",
        audience="Foreign learners who want to handle ordinary city life with more independence.",
        promise="Use Chinese for the errands that make daily life feel real: markets, salons, pharmacies, and customer service.",
        source_notes=["55", "59", "81", "92", "280", "286"],
        units=[
            Unit(
                title="Markets, Supermarkets, and Buying Fresh Food",
                situation="You need to buy fruit, vegetables, or daily items in a local market or supermarket.",
                vocab=[
                    ("多少钱一斤", "How much per jin", "Very common market phrase"),
                    ("便宜一点", "A little cheaper", "Useful in markets"),
                    ("新鲜", "Fresh", "Food shopping adjective"),
                    ("刷卡", "Pay by card", "Modern retail"),
                    ("袋子", "Bag", "At checkout"),
                ],
                dialogue=[
                    ("You", "这个苹果多少钱一斤？", "How much are these apples per jin?"),
                    ("Seller", "六块。", "Six yuan."),
                    ("You", "新鲜吗？", "Are they fresh?"),
                    ("Seller", "今天早上来的，很新鲜。", "They came this morning. Very fresh."),
                    ("You", "好，给我两斤。", "Great. Give me two jin."),
                    ("Seller", "好。", "Okay."),
                ],
                patterns=[
                    ("多少钱一斤？", "How much per jin?", "苹果多少钱一斤？"),
                    ("给我 + quantity", "Give me ...", "给我两斤。"),
                    ("......吗？", "Is ...?", "新鲜吗？"),
                ],
                culture_note="At produce markets, 斤 is still one of the most common weight units. Foreign learners often understand the numbers but miss the unit itself, so learning 多少钱一斤 immediately increases confidence.",
                practice=[
                    "Ask how much fruit costs per jin.",
                    "Buy two jin of something fresh.",
                ],
            ),
            Unit(
                title="Haircuts, Washing, and Saying What You Want",
                situation="You walk into a salon and need to explain your haircut clearly enough to avoid surprises.",
                vocab=[
                    ("理发", "Get a haircut", "Main service"),
                    ("洗头", "Wash hair", "Usually part of the process"),
                    ("剪短一点", "Cut it a little shorter", "Clear instruction"),
                    ("不要太短", "Not too short", "Safety phrase"),
                    ("刘海", "Bangs", "Hair vocabulary"),
                ],
                dialogue=[
                    ("Stylist", "你好，想做什么？", "Hello. What would you like to do?"),
                    ("You", "理发。", "A haircut."),
                    ("Stylist", "想剪多短？", "How short do you want it?"),
                    ("You", "剪短一点，但是不要太短。", "Cut it a little shorter, but not too short."),
                    ("Stylist", "好，先洗头。", "Okay. Let us wash your hair first."),
                    ("You", "好的。", "Okay."),
                ],
                patterns=[
                    ("想 + verb + 多 + adjective", "How ... do you want ...?", "想剪多短？"),
                    ("......一点。", "A little more ...", "剪短一点。"),
                    ("不要太......", "Not too ...", "不要太短。"),
                ],
                culture_note="Chinese salon talk often moves quickly because the stylist assumes you already know the basic service flow. A few short phrases like 剪短一点 and 不要太短 can prevent most beginner mistakes.",
                practice=[
                    "Ask for a haircut.",
                    "Say cut it a little shorter, but not too short.",
                ],
            ),
            Unit(
                title="Pharmacy Chinese and Feeling Unwell",
                situation="You need basic medicine and want to describe simple symptoms without panic.",
                vocab=[
                    ("药店", "Pharmacy", "Find medicine"),
                    ("头疼", "Headache", "Basic symptom"),
                    ("发烧", "Fever", "Basic symptom"),
                    ("感冒药", "Cold medicine", "Useful purchase word"),
                    ("一天几次", "How many times a day", "Dosage question"),
                ],
                dialogue=[
                    ("You", "请问，药店在哪里？", "Excuse me, where is the pharmacy?"),
                    ("Local", "前面右转。", "Turn right ahead."),
                    ("You", "你好，我有点头疼，还有点发烧。", "Hello. I have a bit of a headache and a little fever."),
                    ("Pharmacist", "你可以买这个感冒药。", "You can buy this cold medicine."),
                    ("You", "一天几次？", "How many times a day?"),
                    ("Pharmacist", "一天两次，饭后吃。", "Twice a day, after meals."),
                ],
                patterns=[
                    ("我有点 + symptom", "I have a little ...", "我有点头疼。"),
                    ("可以买这个......", "You can buy this ...", "可以买这个感冒药。"),
                    ("一天几次？", "How many times a day?", "一天几次？"),
                ],
                culture_note="In pharmacies, simple symptom language is often enough for minor issues. Being able to say 头疼, 发烧, and 一天几次 helps you navigate common situations without switching to English immediately.",
                practice=[
                    "Say that you have a little headache and fever.",
                    "Ask how many times a day to take the medicine.",
                ],
            ),
            Unit(
                title="Returns, Repairs, and Customer Service",
                situation="Something you bought is broken, incorrect, or not suitable, and now you need after-sales help.",
                vocab=[
                    ("有问题", "Has a problem", "Report an issue"),
                    ("坏了", "Broken", "Describe malfunction"),
                    ("换一个", "Exchange for another one", "Common request"),
                    ("退货", "Return goods", "After-sales action"),
                    ("售后", "After-sales service", "Important service term"),
                ],
                dialogue=[
                    ("You", "你好，这个有问题。", "Hello. This has a problem."),
                    ("Staff", "怎么了？", "What is wrong?"),
                    ("You", "昨天买的，今天就坏了。", "I bought it yesterday, and today it already broke."),
                    ("Staff", "你想换一个还是退货？", "Do you want to exchange it or return it?"),
                    ("You", "我想换一个。", "I want to exchange it."),
                    ("Staff", "好，我帮你处理。", "Okay. I will handle it for you."),
                ],
                patterns=[
                    ("这个有问题。", "This has a problem.", "这个有问题。"),
                    ("......就坏了。", "... already broke.", "今天就坏了。"),
                    ("我想换一个。", "I want to exchange it.", "我想换一个。"),
                ],
                culture_note="Chinese customer service language is often very direct: report the problem, say what you want, and let the staff move to a solution. Phrases like 有问题 and 换一个 get to the point quickly and clearly.",
                practice=[
                    "Report that something has a problem.",
                    "Choose whether you want an exchange or a return.",
                ],
            ),
        ],
    ),
]


PLAN_FILENAME = "AMAZON_TOP10_选题与目录.md"


def build_plan_md(books: list[Book]) -> str:
    lines = [
        "# Amazon中文学习教材 TOP 10 选题与目录",
        "",
        "基于 GetNote 中文教学知识库与 Amazon 中文学习畅销书方向整理。",
        "",
        "核心产品结构：场景对话 + 拼音 + 英文翻译 + 高频句型 + 文化解释。",
        "",
        "## 总体定位",
        "",
        "这 10 本书聚焦最容易被外国学员购买的方向：生存场景、日常会话、发音、语法、饮食、数字生活、商务、节日文化、社交规则、日常服务。",
        "",
    ]
    for book in books:
        lines.extend(
            [
                f"## Book {book.number}: {book.title}",
                "",
                f"- 中文副标题：{book.subtitle}",
                f"- 目标读者：{book.audience}",
                f"- 核心卖点：{book.promise}",
                f"- 知识库参考笔记：{', '.join(book.source_notes)}",
                "- 内容目录：",
                "",
            ]
        )
        for idx, unit in enumerate(book.units, start=1):
            lines.append(f"  {idx}. {unit.title}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_vocabulary_table(vocab: list[tuple[str, str, str]]) -> str:
    lines = [
        "| Chinese | Pronunciation | English | Use |",
        "|---|---|---|---|",
    ]
    for zh, en, use in vocab:
        lines.append(f"| {zh} | {zh_pinyin(zh)} | {en} | {use} |")
    return "\n".join(lines)


def render_dialogue_table(dialogue: list[tuple[str, str, str]]) -> str:
    lines = [
        "| Speaker | Chinese | Pronunciation | English |",
        "|---|---|---|---|",
    ]
    for speaker, zh, en in dialogue:
        lines.append(f"| {speaker} | {zh} | {zh_pinyin(zh)} | {en} |")
    return "\n".join(lines)


def render_patterns(patterns: list[tuple[str, str, str]]) -> str:
    lines: list[str] = []
    for idx, (pattern, meaning, example) in enumerate(patterns, start=1):
        lines.append(
            f"{idx}. **{pattern}** — {meaning} Example: {example} ({zh_pinyin(example)})"
        )
    return "\n".join(lines)


def render_practice(practice: list[str]) -> str:
    return "\n".join(f"- {item}" for item in practice)


def build_book_md(book: Book) -> str:
    lines = [
        f"# Z Turns Chinese Amazon Series Book {book.number}",
        f"## {book.title}",
        f"**Author:** Tony Sheng",
        f"**Website:** zturnsgo.com",
        f"**Teaching Experience:** 3000+ hours of real Chinese teaching",
        f"**Target Learner:** {book.audience}",
        f"**Book Promise:** {book.promise}",
        f"**Knowledge Base Notes:** {', '.join(book.source_notes)}",
        "",
        "---",
        "",
        "# Table of Contents",
        "",
    ]
    for idx, unit in enumerate(book.units, start=1):
        lines.append(f"{idx}. {unit.title}")
    lines.extend(["", "---", ""])

    for idx, unit in enumerate(book.units, start=1):
        lines.extend(
            [
                f"# Unit {idx}: {unit.title}",
                "",
                "## Situation",
                "",
                unit.situation,
                "",
                "## Key Vocabulary",
                "",
                render_vocabulary_table(unit.vocab),
                "",
                "## Scene Dialogue",
                "",
                render_dialogue_table(unit.dialogue),
                "",
                "## High-Frequency Patterns",
                "",
                render_patterns(unit.patterns),
                "",
                "## Culture Note",
                "",
                unit.culture_note,
                "",
                "## Quick Practice",
                "",
                render_practice(unit.practice),
                "",
                "---",
                "",
            ]
        )

    lines.extend(
        [
            "# Final Review",
            "",
            "Use this book in three passes:",
            "",
            "1. Read the situation and dialogue aloud.",
            "2. Memorize the high-frequency patterns.",
            "3. Use the culture note to understand why the Chinese feels natural in context.",
            "",
            "If you can repeat each unit without reading every line, this book has already started working for you.",
            "",
        ]
    )
    return "\n".join(lines)


def ensure_python() -> Path:
    if VENV_PYTHON.exists():
        return VENV_PYTHON
    raise FileNotFoundError(f"Python venv not found: {VENV_PYTHON}")


def compile_book(md_path: Path, book: Book, pdf_path: Path) -> None:
    python_bin = ensure_python()
    cmd = [
        str(python_bin),
        str(GENERATOR),
        "textbook",
        "--md",
        str(md_path),
        "--number",
        book.number,
        "--title",
        book.title,
        "--subtitle",
        book.subtitle,
        "--color",
        book.color,
        "--out",
        str(pdf_path),
    ]
    result = subprocess.run(cmd, cwd=str(V3_DIR), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to compile {md_path.name}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def main() -> None:
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)

    plan_path = TARGET_ROOT / PLAN_FILENAME
    plan_path.write_text(build_plan_md(BOOKS), encoding="utf-8")

    generated: list[str] = []
    for book in BOOKS:
        folder = TARGET_ROOT / f"Book{book.number}_{book.slug}"
        folder.mkdir(parents=True, exist_ok=True)
        md_name = f"ZTurns_Book{book.number}_{book.slug}.md"
        pdf_name = f"ZTurns_Book{book.number}_{book.slug}.pdf"
        md_path = folder / md_name
        pdf_path = folder / pdf_name

        md_path.write_text(build_book_md(book), encoding="utf-8")
        compile_book(md_path, book, pdf_path)
        generated.append(f"- {md_path}")
        generated.append(f"- {pdf_path}")

    summary = TARGET_ROOT / "GENERATED_FILES.md"
    summary.write_text(
        "# Generated Files\n\n"
        + "\n".join(generated)
        + "\n",
        encoding="utf-8",
    )

    print(f"Generated plan: {plan_path}")
    print(f"Generated {len(BOOKS)} books under: {TARGET_ROOT}")


if __name__ == "__main__":
    main()
