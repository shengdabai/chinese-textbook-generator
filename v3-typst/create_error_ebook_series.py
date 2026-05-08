#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from pypinyin import Style, pinyin


ROOT = Path(".")
GENERATE = ROOT / "generate.py"
SERIES_ROOT = Path("output/error-ebook-series")
MD_DIR = SERIES_ROOT / "md"
PDF_DIR = SERIES_ROOT / "pdf"


def ensure_dirs() -> None:
    MD_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)


def auto_pinyin(text: str) -> str:
    cjk = re.compile(r"[\u4e00-\u9fff]+")
    result: list[str] = []
    pos = 0
    for match in cjk.finditer(text):
        result.append(text[pos:match.start()])
        chunk = match.group()
        pys = pinyin(chunk, style=Style.TONE, heteronym=False)
        result.append(" ".join(s[0] for s in pys))
        pos = match.end()
    result.append(text[pos:])
    rendered = "".join(result)
    rendered = re.sub(r"\s+([，。？！；：、）】》”])", r"\1", rendered)
    rendered = re.sub(r"([（【《“])\s+", r"\1", rendered)
    rendered = re.sub(r"\s+", " ", rendered).strip()
    return rendered


def triad(zh: str, en: str) -> str:
    return (
        f"**中文**：{zh}\n\n"
        f"**拼音**：{auto_pinyin(zh)}\n\n"
        f"**English**: {en}\n"
    )


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join([head, sep, *body])


def sound_example_rows(pairs: list[dict[str, str]]) -> list[list[str]]:
    rows = []
    for item in pairs:
        rows.append(
            [
                item["a"],
                auto_pinyin(item["a"]),
                item["en_a"],
                item["b"],
                auto_pinyin(item["b"]),
                item["en_b"],
                item["note"],
            ]
        )
    return rows


def correctness_rows(items: list[dict[str, str]]) -> list[list[str]]:
    rows = []
    for item in items:
        rows.append(
            [
                item["right"],
                auto_pinyin(item["right"]),
                item["right_en"],
                item["wrong"],
                auto_pinyin(item["wrong"]),
                item["wrong_en"],
                item["note"],
            ]
        )
    return rows


def dialogue_table(turns: list[tuple[str, str, str]]) -> str:
    rows = []
    for speaker, zh, en in turns:
        rows.append([speaker, zh, auto_pinyin(zh), en])
    return md_table(["说话人", "中文", "拼音", "English"], rows)


def practice_table(items: list[dict[str, str]]) -> str:
    rows = []
    for idx, item in enumerate(items, 1):
        rows.append(
            [
                str(idx),
                item["prompt"],
                auto_pinyin(item["prompt"]),
                item["task"],
            ]
        )
    return md_table(["题号", "中文", "拼音", "任务"], rows)


def answer_table(items: list[dict[str, str]]) -> str:
    rows = []
    for idx, item in enumerate(items, 1):
        rows.append(
            [
                str(idx),
                item["answer"],
                auto_pinyin(item["answer"]),
                item["answer_en"],
            ]
        )
    return md_table(["题号", "参考答案", "拼音", "English"], rows)


def build_sound_module(module: dict) -> str:
    parts: list[str] = []
    parts.append(f"## {module['title']}\n")
    parts.append(triad(module["overview_zh"], module["overview_en"]))
    parts.append("\n")
    parts.append(triad(module["tip_zh"], module["tip_en"]))
    parts.append("\n")
    parts.append("### 核心对比表\n\n")
    parts.append(
        md_table(
            ["对比一", "拼音", "English", "对比二", "拼音", "English", "提醒"],
            sound_example_rows(module["pairs"]),
        )
    )
    parts.append("\n\n### 讲解与提醒\n\n")
    for item in module["pairs"]:
        zh = (
            f"先把“{item['a']}”和“{item['b']}”分开读，再放进短句里读。"
            f"如果你把“{item['a']}”读成“{item['b']}”，听的人往往会先想到错误的意思。"
        )
        en = (
            f"Read “{item['a']}” and “{item['b']}” separately first, and then read them inside short sentences. "
            f"If you pronounce “{item['a']}” like “{item['b']}”, listeners may understand the wrong meaning first."
        )
        parts.append(triad(zh, en))
        parts.append("\n\n")
        ex_zh = f"这是“{item['a']}”，不是“{item['b']}”。"
        ex_en = f"This is “{item['a']}”, not “{item['b']}”."
        parts.append(triad(ex_zh, ex_en))
        parts.append("\n\n")
        ex2_zh = f"请你先说“{item['a']}”，再说“{item['b']}”，最后连起来快速读两遍。"
        ex2_en = (
            f"Please say “{item['a']}” first, then “{item['b']}”, and finally read them quickly twice in sequence."
        )
        parts.append(triad(ex2_zh, ex2_en))
        parts.append("\n\n")

    turns = [
        ("老师", f"我们先练习“{module['pairs'][0]['a']}”和“{module['pairs'][0]['b']}”。", "Let's practice the first contrast pair."),
        ("学生", f"我常常把“{module['pairs'][0]['a']}”读成“{module['pairs'][0]['b']}”。", "I often pronounce the first word like the second one."),
        ("老师", "没关系，先慢一点，再清楚一点。", "That's okay. Slow down first and make it clearer."),
        ("学生", f"好，我再读一遍：“{module['pairs'][0]['a']}”“{module['pairs'][0]['b']}”。", "Okay, I'll read them again."),
        ("老师", "很好。现在把它们放进句子里。", "Good. Now put them into sentences."),
        ("学生", f"这是“{module['pairs'][0]['a']}”，不是“{module['pairs'][0]['b']}”。", "This is the first word, not the second one."),
    ]
    parts.append("### 场景对话\n\n")
    parts.append(dialogue_table(turns))
    parts.append("\n\n")

    drill_items = []
    answer_items = []
    for item in module["pairs"]:
        drill_items.append(
            {
                "prompt": f"把“{item['a']}”和“{item['b']}”各读三遍，再说一句“这是{item['a']}，不是{item['b']}”。",
                "task": "朗读并完成最小对比句。",
            }
        )
        answer_items.append(
            {
                "answer": f"这是{item['a']}，不是{item['b']}。",
                "answer_en": f"This is {item['a']}, not {item['b']}.",
            }
        )
        drill_items.append(
            {
                "prompt": f"如果老师说“{item['b']}”，请你立刻改成“{item['a']}”。",
                "task": "做即时纠音练习。",
            }
        )
        answer_items.append(
            {
                "answer": f"我应该说“{item['a']}”，不应该说“{item['b']}”。",
                "answer_en": f"I should say {item['a']}, not {item['b']}.",
            }
        )

    parts.append("### 纠音练习\n\n")
    parts.append(practice_table(drill_items))
    parts.append("\n\n### 参考答案\n\n")
    parts.append(answer_table(answer_items))
    parts.append("\n\n")
    return "".join(parts)


def build_correctness_module(module: dict) -> str:
    parts: list[str] = []
    parts.append(f"## {module['title']}\n")
    parts.append(triad(module["overview_zh"], module["overview_en"]))
    parts.append("\n")
    parts.append(triad(module["tip_zh"], module["tip_en"]))
    parts.append("\n")
    parts.append("### 核心对比表\n\n")
    parts.append(
        md_table(
            ["更自然或正确", "拼音", "English", "常见误说", "拼音", "English", "提醒"],
            correctness_rows(module["items"]),
        )
    )
    parts.append("\n\n### 规则精讲\n\n")
    for item in module["items"]:
        explain_zh = (
            f"在这个场景里，更自然的说法是“{item['right']}”。"
            f"很多学习者会先按英文逻辑说成“{item['wrong']}”，但中文母语者通常不会这样说。"
        )
        explain_en = (
            f"In this situation, the more natural expression is “{item['right']}”. "
            f"Many learners first follow English logic and say “{item['wrong']}”, but native speakers usually do not say it that way."
        )
        parts.append(triad(explain_zh, explain_en))
        parts.append("\n\n")
        reminder_zh = f"你可以先记住一句话：{item['note']}。"
        reminder_en = f"A simple reminder is: {item['note_en']}."
        parts.append(triad(reminder_zh, reminder_en))
        parts.append("\n\n")

    turns = [
        ("老师", f"今天我们重点练习“{module['items'][0]['right']}”。", f"Today we will focus on “{module['items'][0]['right']}”."),
        ("学生", f"我以前总是说“{module['items'][0]['wrong']}”。", f"I used to say “{module['items'][0]['wrong']}”."),
        ("老师", "没关系，先理解规则，再多说几遍。", "That's okay. Understand the rule first, then repeat it several times."),
        ("学生", f"现在我知道更自然的说法是“{module['items'][0]['right']}”。", f"Now I know the more natural expression is “{module['items'][0]['right']}”."),
        ("老师", "很好。下一步是放进真实场景里。", "Very good. The next step is to put it into a real-life scene."),
        ("学生", f"我会用“{module['items'][0]['right']}”说完整句子。", f"I will use “{module['items'][0]['right']}” in full sentences."),
    ]
    parts.append("### 场景对话\n\n")
    parts.append(dialogue_table(turns))
    parts.append("\n\n")

    drill_items = []
    answer_items = []
    for item in module["items"]:
        drill_items.append(
            {
                "prompt": f"把“{item['wrong']}”改成更自然的中文。",
                "task": "改写错误或不自然表达。",
            }
        )
        answer_items.append(
            {
                "answer": item["right"],
                "answer_en": item["right_en"],
            }
        )
        drill_items.append(
            {
                "prompt": f"用“{item['right']}”自己再造一个短句。",
                "task": "口语输出练习。",
            }
        )
        answer_items.append(
            {
                "answer": f"我会优先说：{item['right']}。",
                "answer_en": f"I will prefer saying: {item['right']}.",
            }
        )

    parts.append("### 纠错与改写练习\n\n")
    parts.append(practice_table(drill_items))
    parts.append("\n\n### 参考答案\n\n")
    parts.append(answer_table(answer_items))
    parts.append("\n\n")
    return "".join(parts)


def build_book(book: dict) -> str:
    parts: list[str] = []
    parts.append(f"# {book['cn_title']}\n\n")
    parts.append(triad(book["intro_zh"], book["intro_en"]))
    parts.append("\n")
    parts.append(triad(book["use_zh"], book["use_en"]))
    parts.append("\n")
    parts.append("## 全书结构\n\n")
    for idx, module in enumerate(book["modules"], 1):
        parts.append(f"- 第{idx}章：{module['title']}\n")
    parts.append("- 附录：高频句型总复习\n")
    parts.append("- 附录：全书学习建议\n\n")

    for module in book["modules"]:
        parts.append(build_sound_module(module) if module["kind"] == "sound" else build_correctness_module(module))

    parts.append("## 附录一：高频句型总复习\n\n")
    review_rows = []
    for module in book["modules"]:
        if module["kind"] == "sound":
            for item in module["pairs"]:
                zh = f"这是{item['a']}，不是{item['b']}。"
                review_rows.append([zh, auto_pinyin(zh), f"This is {item['a']}, not {item['b']}."])
        else:
            for item in module["items"]:
                review_rows.append([item["right"], auto_pinyin(item["right"]), item["right_en"]])
    parts.append(md_table(["中文", "拼音", "English"], review_rows[:60]))
    parts.append("\n\n## 附录二：全书学习建议\n\n")
    study_tips = [
        (
            "第一遍学习时，请先大声读中文，再看拼音，最后看英文，不要一开始就盯着英文翻译。",
            "When studying for the first time, read the Chinese aloud first, then check the pinyin, and finally read the English. Do not stare at the English translation first."
        ),
        (
            "第二遍学习时，请把最容易说错的两组内容放在一起做对比，比如“二和两”“不和没”“一点儿和有点儿”。",
            "During the second round, compare the most confusing pairs side by side, such as '二 and 两', '不 and 没', or '一点儿 and 有点儿'."
        ),
        (
            "第三遍学习时，请把每章的场景对话录成自己的语音，听一遍，再纠正一遍，这样进步最快。",
            "During the third round, record each chapter dialogue in your own voice, listen once, and correct it once. This is one of the fastest ways to improve."
        ),
        (
            "如果你暂时说不完整句子，也不要停下来。先把关键词说出来，再慢慢补完整，这就是口语真正的成长方式。",
            "If you cannot produce a full sentence yet, do not stop. Say the key words first and complete the sentence gradually. That is how real speaking ability grows."
        ),
    ]
    for zh, en in study_tips:
        parts.append(triad(zh, en))
        parts.append("\n\n")

    parts.append("## 附录三：综合替换句朗读稿\n\n")
    for module in book["modules"]:
        if module["kind"] == "sound":
            for item in module["pairs"]:
                zh1 = f"老师先读“{item['a']}”，学生再读“{item['b']}”，最后把这两个词放进同一个句子里。"
                en1 = f"The teacher reads “{item['a']}” first, the student reads “{item['b']}” next, and finally both words are placed in the same sentence."
                parts.append(triad(zh1, en1))
                parts.append("\n\n")
                zh2 = f"如果你把“{item['a']}”读成“{item['b']}”，听的人会先想到“{item['en_b']}”，所以一定要把差别说出来。"
                en2 = f"If you pronounce “{item['a']}” like “{item['b']}”, listeners may first think of “{item['en_b']}”, so you must make the distinction clear."
                parts.append(triad(zh2, en2))
                parts.append("\n\n")
                zh3 = f"请连续读三遍：“{item['a']}，{item['b']}，{item['a']}，{item['b']}”，速度可以慢一点，但一定要清楚。"
                en3 = f"Please read this three times in a row: “{item['a']}, {item['b']}, {item['a']}, {item['b']}”. You may go slowly, but you must stay clear."
                parts.append(triad(zh3, en3))
                parts.append("\n\n")
        else:
            for item in module["items"]:
                zh1 = f"在这个场景里，更自然的说法是“{item['right']}”，因为它更符合中文母语者的表达习惯。"
                en1 = f"In this situation, the more natural expression is “{item['right']}” because it fits native Mandarin usage better."
                parts.append(triad(zh1, en1))
                parts.append("\n\n")
                zh2 = f"如果你先说成“{item['wrong']}”，也不要紧。你只要立刻改成“{item['right']}”，交流通常还是可以继续。"
                en2 = f"If you first say “{item['wrong']}”, that is still okay. As long as you quickly correct it to “{item['right']}”, communication can usually continue."
                parts.append(triad(zh2, en2))
                parts.append("\n\n")
                zh3 = f"请你把“{item['right']}”连读三遍，再自己造一个和生活有关的句子。"
                en3 = f"Read “{item['right']}” three times in connected speech, and then create one life-related sentence of your own."
                parts.append(triad(zh3, en3))
                parts.append("\n\n")

    parts.append("## 附录四：中英双向翻译强化任务\n\n")
    translation_prompts = []
    translation_answers = []
    counter = 1
    for module in book["modules"]:
        if module["kind"] == "sound":
            for item in module["pairs"]:
                prompt_zh = f"把下面意思说成中文：This is {item['a']}, not {item['b']}."
                answer_zh = f"这是{item['a']}，不是{item['b']}。"
                translation_prompts.append([str(counter), prompt_zh, auto_pinyin(prompt_zh), "Translate into Chinese"])
                translation_answers.append([str(counter), answer_zh, auto_pinyin(answer_zh), f"This is {item['a']}, not {item['b']}."])
                counter += 1
                prompt_zh2 = f"把下面中文译成英文：我常常把“{item['a']}”读成“{item['b']}”。"
                answer_zh2 = f"I often pronounce “{item['a']}” as “{item['b']}”."
                translation_prompts.append([str(counter), prompt_zh2, auto_pinyin(prompt_zh2), "Translate into English"])
                translation_answers.append([str(counter), answer_zh2, answer_zh2, answer_zh2])
                counter += 1
        else:
            for item in module["items"]:
                prompt_zh = f"把下面意思说成中文：The more natural expression is “{item['right']}”."
                answer_zh = f"更自然的说法是“{item['right']}”。"
                translation_prompts.append([str(counter), prompt_zh, auto_pinyin(prompt_zh), "Translate into Chinese"])
                translation_answers.append([str(counter), answer_zh, auto_pinyin(answer_zh), f'The more natural expression is "{item["right"]}".'])
                counter += 1
                prompt_zh2 = f"把下面中文译成英文：不要说“{item['wrong']}”，要说“{item['right']}”。"
                answer_zh2 = f'Do not say "{item["wrong"]}". Say "{item["right"]}" instead.'
                translation_prompts.append([str(counter), prompt_zh2, auto_pinyin(prompt_zh2), "Translate into English"])
                translation_answers.append([str(counter), answer_zh2, answer_zh2, answer_zh2])
                counter += 1
    parts.append(md_table(["题号", "任务", "拼音", "说明"], translation_prompts[:80]))
    parts.append("\n\n### 参考答案\n\n")
    parts.append(md_table(["题号", "答案", "拼音", "English"], translation_answers[:80]))
    parts.append("\n\n")

    parts.append("## 附录五：综合场景长对话\n\n")
    long_dialogues = [
        [
            ("老师", "今天我们不只看规则，我们要把这些表达放进真实对话里。", "Today we are not only looking at rules; we are putting these expressions into real conversation."),
            ("学生", "好，我最怕的就是一开口就不知道该用哪个词。", "Okay. What I fear most is not knowing which word to use the moment I open my mouth."),
            ("老师", "没关系，先说出核心意思，再慢慢修正细节。", "That's fine. Say the core meaning first and then fix the details gradually."),
            ("学生", "如果我说错了，你可以马上帮我改出来吗？", "If I say it wrong, can you correct it for me right away?"),
            ("老师", "可以。你说错的时候，我会先告诉你更自然的说法。", "Yes. When you say it incorrectly, I will first tell you the more natural expression."),
            ("学生", "这样我就能把正确的句子记下来。", "That way I can write down the correct sentence."),
            ("老师", "对，而且你要多说几遍，最好把它们录下来再听。", "Exactly, and you need to repeat them several times. It is even better to record them and listen again."),
            ("学生", "我发现听自己说话的时候，更容易听出来问题在哪儿。", "I have found that when I listen to myself speaking, it is easier to hear where the problem is."),
            ("老师", "这就是进步最快的方法之一。", "That is one of the fastest ways to improve."),
            ("学生", "好，那我们继续。", "Okay, then let's continue."),
        ],
        [
            ("学生", "不好意思，我想问一下，男厕所在哪儿？", "Excuse me, I would like to ask where the men's restroom is."),
            ("路人", "你先上三楼，然后向左走，往里走一点儿就能看见。", "First go up to the third floor, then turn left, and walk a little further inside. You will see it."),
            ("学生", "谢谢。如果我走错了，可以再问别人吗？", "Thank you. If I go the wrong way, can I ask someone else again?"),
            ("路人", "当然可以。你要是没看出来，也可以直接问服务员。", "Of course. If you still cannot figure it out, you can ask the staff directly."),
            ("学生", "好，我记下来了。", "Okay, I have written it down."),
            ("路人", "不客气。", "You're welcome."),
            ("学生", "对了，下楼的时候，电梯在右边还是左边？", "By the way, when I come down, is the elevator on the right or on the left?"),
            ("路人", "在右边。你出来以后就能看见。", "It is on the right. You will see it after you come out."),
            ("学生", "明白了，谢谢你。", "Got it. Thank you."),
            ("路人", "没事。", "No problem."),
        ],
        [
            ("顾客", "你好，我想点菜。你们有什么推荐菜吗？", "Hello. I'd like to order. Do you have any recommended dishes?"),
            ("服务员", "有，我们的招牌菜很多人都喜欢。", "Yes. Many people like our signature dishes."),
            ("顾客", "我不太能吃辣，有没有不辣的？", "I cannot really eat spicy food. Do you have anything that is not spicy?"),
            ("服务员", "有。这道菜一点儿也不辣，但是味道很好。", "Yes. This dish is not spicy at all, but it tastes very good."),
            ("顾客", "听起来不错。我想试试。", "That sounds good. I want to try it."),
            ("服务员", "好的。你还要什么？", "Sure. What else would you like?"),
            ("顾客", "再来一杯茶吧，不要太甜。", "Please add a cup of tea, and not too sweet."),
            ("服务员", "没问题。你们两个人吃这些应该够了。", "No problem. This should be enough for the two of you."),
            ("顾客", "好的，谢谢。", "Okay, thank you."),
            ("服务员", "不客气。", "You're welcome."),
        ],
    ]
    for idx, turns in enumerate(long_dialogues, 1):
        parts.append(f"### 场景对话 {idx}\n\n")
        parts.append(dialogue_table(turns))
        parts.append("\n\n")
    return "".join(parts)


BOOKS = [
    {
        "number": "101",
        "slug": "01-pinyin-contrast-mastery",
        "title": "Pinyin Contrast Mastery",
        "cn_title": "拼音易混音系统训练",
        "subtitle": "学员最常读错的拼音对比与纠音训练",
        "color": "#C84C09",
        "intro_zh": "这本书专门解决中文学习者最常见的发音混淆问题。很多人不是不会拼音，而是会拼不会分，尤其在真实对话里，一紧张就把相近的音混在一起。",
        "intro_en": "This book focuses on the most common pronunciation confusions for Chinese learners. Many learners do not fail because they do not know pinyin, but because they cannot keep similar sounds apart in real conversations.",
        "use_zh": "全书按照“先听出差别，再读出差别，最后放进句子里”的顺序设计。每一章都有中文、拼音和英文翻译，也有最小对比、场景对话和纠音练习。",
        "use_en": "The whole book is designed in the order of hearing the difference first, reading the difference second, and using the contrast inside sentences last. Every chapter includes Chinese, pinyin, English translation, minimal pairs, dialogues, and correction drills.",
        "modules": [
            {
                "kind": "sound",
                "title": "j、q、x：最容易混成一团的一组音",
                "overview_zh": "j、q、x 这一组音对很多学习者来说最难，因为它们都出现在嘴前部，听起来又很近。你如果只靠感觉，不靠口型和送气差别，就很容易混。",
                "overview_en": "For many learners, j, q, and x are the hardest group because they are all produced in the front part of the mouth and sound very close to one another. If you rely only on feeling and ignore mouth shape and aspiration, you will easily mix them up.",
                "tip_zh": "记忆时不要孤立背字母，要把字母和最常见的字、词、短句一起练。只会背规则，不会说句子，到了真实交流还是会读错。",
                "tip_en": "Do not memorize the letters alone. Practice the letters together with common characters, words, and short sentences. If you only remember the rule but cannot say a sentence, you will still mispronounce it in real communication.",
                "pairs": [
                    {"a": "鸡", "b": "七", "en_a": "chicken", "en_b": "seven", "note": "先分清 j 和 q 的送气差别"},
                    {"a": "钱", "b": "咸", "en_a": "money", "en_b": "salty", "note": "q 和 x 不要都读成英语的 sh"},
                    {"a": "西", "b": "鸡", "en_a": "west", "en_b": "chicken", "note": "x 比 j 更轻更扁"},
                    {"a": "去", "b": "需", "en_a": "go", "en_b": "need", "note": "q 和 x 在句子里更要分开"},
                    {"a": "学习", "b": "七夕", "en_a": "study", "en_b": "the Qixi Festival", "note": "双音节词更能检验稳定度"},
                ],
            },
            {
                "kind": "sound",
                "title": "zh、ch、sh、r：卷舌音总是不稳定",
                "overview_zh": "很多学习者知道中文有卷舌音，但真正说的时候，舌头还是回不去，最后就把 zh、ch、sh、r 全部说平了。",
                "overview_en": "Many learners know that Mandarin has retroflex sounds, but when they actually speak, the tongue still does not curl back enough, and zh, ch, sh, and r all become flat.",
                "tip_zh": "训练卷舌音时，先把舌尖往后收，再把声音送出来。先慢，后快；先单字，后句子；先准确，后流利。",
                "tip_en": "When training retroflex sounds, curl the tongue tip back first and then release the sound. Go from slow to fast, from single characters to sentences, and from accuracy to fluency.",
                "pairs": [
                    {"a": "知道", "b": "子道", "en_a": "to know", "en_b": "incorrect flat pronunciation", "note": "卷舌和平舌要明确分开"},
                    {"a": "吃", "b": "词", "en_a": "eat", "en_b": "word / phrase", "note": "ch 和 c 是经典误读"},
                    {"a": "是", "b": "四", "en_a": "is", "en_b": "four", "note": "sh 和 s 容易互相替代"},
                    {"a": "热", "b": "乐", "en_a": "hot", "en_b": "happy / music", "note": "r 不要随便滑成 l"},
                    {"a": "认识", "b": "冷四", "en_a": "to know / recognize", "en_b": "incorrect chunk", "note": "连续卷舌音更需要慢练"},
                ],
            },
            {
                "kind": "sound",
                "title": "z、c、s：平舌音不等于英语的 z 和 s",
                "overview_zh": "z、c、s 经常被学习者用英语发音逻辑去替代。结果就是中文听起来像英文口音很重，而且有些词会完全变义。",
                "overview_en": "Learners often replace z, c, and s with English sound patterns. As a result, the Mandarin sounds heavily accented, and in some cases the meaning changes completely.",
                "tip_zh": "平舌音练习一定要把送气和不送气分开。z 不送气，c 送气，s 则保持清楚稳定的摩擦感。",
                "tip_en": "For alveolar sounds, you must separate aspirated and unaspirated sounds. z is unaspirated, c is aspirated, and s should keep a clear, steady friction.",
                "pairs": [
                    {"a": "早", "b": "草", "en_a": "early", "en_b": "grass", "note": "z 和 c 送气差别要明显"},
                    {"a": "菜", "b": "再", "en_a": "dish", "en_b": "again", "note": "c 和 z 不能混读"},
                    {"a": "三", "b": "山", "en_a": "three", "en_b": "mountain", "note": "s 和 sh 要分开"},
                    {"a": "字", "b": "志", "en_a": "character", "en_b": "will / ambition", "note": "平舌和卷舌是两套系统"},
                    {"a": "四次", "b": "试纸", "en_a": "four times", "en_b": "test paper", "note": "双音节对比更能暴露问题"},
                ],
            },
            {
                "kind": "sound",
                "title": "an、ang、en、eng、in、ing：鼻音尾巴不能丢",
                "overview_zh": "很多人读韵母的时候，只把前面的元音读出来，后面的鼻音尾巴很弱。这样一来，安和昂、因和英就会混在一起。",
                "overview_en": "Many learners pronounce only the vowel clearly and leave the nasal ending too weak. Then pairs like an and ang, or in and ing, collapse into each other.",
                "tip_zh": "鼻音韵母要有“收尾动作”。如果结尾没有收住，前面的音再准，整个词听起来还是不对。",
                "tip_en": "Nasal finals need a clear closing movement. If the ending is not closed properly, the whole word still sounds wrong even if the first part is accurate.",
                "pairs": [
                    {"a": "安", "b": "昂", "en_a": "peace", "en_b": "raise / hold high", "note": "an 和 ang 的尾音长度不同"},
                    {"a": "真", "b": "争", "en_a": "real", "en_b": "to fight for", "note": "en 和 eng 要把尾音读满"},
                    {"a": "新", "b": "星", "en_a": "new", "en_b": "star", "note": "in 和 ing 是高频错误"},
                    {"a": "银行", "b": "银韩", "en_a": "bank", "en_b": "incorrect chunk", "note": "双音节里尾音更容易掉"},
                    {"a": "北京", "b": "北金", "en_a": "Beijing", "en_b": "incorrect chunk", "note": "地名是检验鼻音稳定度的好材料"},
                ],
            },
            {
                "kind": "sound",
                "title": "u、ü、yu、yue、yuan：嘴形不对，词义就跑偏",
                "overview_zh": "很多学习者看到 yu、yue、yuan 时，以为就是英语的 you，其实中文里的 ü 音非常关键，嘴形不对就会整体跑偏。",
                "overview_en": "Many learners see yu, yue, or yuan and assume they sound like English 'you', but the ü sound is crucial in Mandarin. If the lip shape is wrong, the whole word shifts away from the target.",
                "tip_zh": "练这一组音时，先把嘴唇往前收圆，再保持声音稳定。不要让它滑成普通的 u，也不要滑成英语的 yoo。",
                "tip_en": "When practicing this sound group, round the lips forward first and keep the sound steady. Do not let it slide into a normal u sound or an English-style 'yoo'.",
                "pairs": [
                    {"a": "女", "b": "鲁", "en_a": "female", "en_b": "Lu / rough incorrect replacement", "note": "ü 不是普通的 u"},
                    {"a": "去", "b": "处", "en_a": "go", "en_b": "place / handle", "note": "qu 和 chu 的嘴形不同"},
                    {"a": "月", "b": "我", "en_a": "month / moon", "en_b": "I / me", "note": "yue 不能随便扁平化"},
                    {"a": "元", "b": "完", "en_a": "yuan", "en_b": "finish", "note": "yuan 和 wan 不是一回事"},
                    {"a": "语言", "b": "五言", "en_a": "language", "en_b": "five-character style", "note": "多音节里更容易失真"},
                ],
            },
        ],
    },
    {
        "number": "102",
        "slug": "02-tones-light-tone-and-tone-change",
        "title": "Tone Ladder for Real Speech",
        "cn_title": "声调、轻声与变调精讲",
        "subtitle": "从四声到语流，解决会拼不会调的问题",
        "color": "#7B2CBF",
        "intro_zh": "很多学习者可以认拼音，却不能稳定地说出正确声调。一到真实交流里，第一声不平，第三声不转，轻声也丢掉，整句话就变得很像单词堆积。",
        "intro_en": "Many learners can recognize pinyin but cannot produce stable tones. In real conversation, the first tone is not level, the third tone does not turn properly, and the light tone disappears, making the whole sentence sound like a pile of disconnected words.",
        "use_zh": "这本书把声调训练拆成一个个真实问题：四声本身怎么练，轻声为什么容易丢，“一”和“不”为什么会变调，连续第三声为什么总是拗口。",
        "use_en": "This book breaks tone training into real problems: how to train the four tones themselves, why the neutral tone disappears so easily, why '一' and '不' change tone, and why sequences of third tone words often feel awkward.",
        "modules": [
            {
                "kind": "correctness",
                "title": "四声的底层稳定：先分清，再加速",
                "overview_zh": "四声不是背下来就结束了，而是要在词里、句子里都稳定。初学者最大的问题是第二声和第三声混，或者第一声根本不平。",
                "overview_en": "The four tones are not finished once you memorize them. They must stay stable inside words and sentences. Beginners often confuse the second and third tones, or fail to keep the first tone level.",
                "tip_zh": "训练四声时，不要一开始就追求快。先把音高轮廓做准确，再把速度慢慢提上来。",
                "tip_en": "Do not chase speed at the beginning. First make the pitch contour accurate, and then increase the speed gradually.",
                "items": [
                    {"right": "妈、麻、马、骂", "wrong": "妈、麻、马、骂都读得差不多", "right_en": "mā, má, mǎ, mà", "wrong_en": "all four tones sound almost the same", "note": "四个声调一定要拉开距离", "note_en": "Make the four tones clearly distinct"},
                    {"right": "第一声要平", "wrong": "第一声往上滑", "right_en": "The first tone should stay level", "wrong_en": "The first tone slides upward", "note": "第一声不是英语重音", "note_en": "The first tone is not an English-style stressed syllable"},
                    {"right": "第二声要上扬", "wrong": "第二声太平", "right_en": "The second tone should rise", "wrong_en": "The second tone is too flat", "note": "二声像提问时往上带", "note_en": "The second tone rises like a lifted question contour"},
                    {"right": "第三声先下后上", "wrong": "第三声只往下不回来", "right_en": "The third tone falls and then rises", "wrong_en": "The third tone only falls and never returns", "note": "第三声不能只读半截", "note_en": "Do not leave the third tone unfinished"},
                    {"right": "第四声要干脆", "wrong": "第四声拖太长", "right_en": "The fourth tone should be decisive", "wrong_en": "The fourth tone is too long and dragged out", "note": "第四声像往下切", "note_en": "The fourth tone cuts downward sharply"},
                ],
            },
            {
                "kind": "correctness",
                "title": "轻声：不是没有声调，而是弱下来",
                "overview_zh": "轻声是中文口语节奏的重要部分。很多学习者把轻声字也读得很重，于是中文听起来就不自然。",
                "overview_en": "The neutral tone is an important part of Mandarin rhythm. Many learners pronounce neutral-tone syllables too heavily, which makes the speech sound unnatural.",
                "tip_zh": "轻声不是随便读，而是前一个字重，后一个字轻。你要听出节奏，再去模仿。",
                "tip_en": "The neutral tone is not random. The previous syllable stays stronger and the next one becomes lighter. Hear the rhythm first and then imitate it.",
                "items": [
                    {"right": "妈妈", "wrong": "妈 妈两个字一样重", "right_en": "māma", "wrong_en": "both syllables are equally heavy", "note": "第二个字轻下来更自然", "note_en": "The second syllable should become lighter"},
                    {"right": "谢谢", "wrong": "谢 谢两个字都很重", "right_en": "xièxie", "wrong_en": "both syllables are equally heavy", "note": "礼貌词常见轻声", "note_en": "Polite words often use the neutral tone"},
                    {"right": "东西", "wrong": "东 西都读满", "right_en": "dōngxi", "wrong_en": "both syllables are fully stressed", "note": "高频双音节词更要自然", "note_en": "Common two-syllable words should sound natural"},
                    {"right": "孩子", "wrong": "孩 子分得太开", "right_en": "háizi", "wrong_en": "the two syllables are separated too strongly", "note": "口语里第二个字往往更轻", "note_en": "The second syllable is often lighter in speech"},
                    {"right": "看看", "wrong": "看 看都重读", "right_en": "kànkan", "wrong_en": "both syllables are stressed", "note": "动词重叠常带轻声节奏", "note_en": "Verb reduplication often carries a neutral-tone rhythm"},
                ],
            },
            {
                "kind": "correctness",
                "title": "“一”为什么总在变",
                "overview_zh": "“一”是最容易被学员读死的字。它在不同声调前的读法不一样，如果每次都读成 yī，口语就会很僵。",
                "overview_en": "The character '一' is one of the easiest words to pronounce too rigidly. Its tone changes before different following tones. If you always read it as yī, your speech will sound stiff.",
                "tip_zh": "你不需要背很复杂的术语，只要先记住两个高频结果：一件衣服读 yí jiàn，一本书常读 yì běn。",
                "tip_en": "You do not need complicated technical terms at first. Just remember two high-frequency outcomes: yí jiàn yīfu and yì běn shū.",
                "items": [
                    {"right": "一个", "wrong": "yī ge 每次都不变", "right_en": "yí ge", "wrong_en": "always saying yī ge without change", "note": "第四声前常变成 yí", "note_en": "It often changes to yí before a fourth tone"},
                    {"right": "一件", "wrong": "yī jiàn", "right_en": "yí jiàn", "wrong_en": "yī jiàn", "note": "要跟后面的声调连起来听", "note_en": "Listen to it together with the following tone"},
                    {"right": "一本", "wrong": "yī běn", "right_en": "yì běn", "wrong_en": "yī běn", "note": "非四声前常读 yì", "note_en": "Before non-fourth tones, it often becomes yì"},
                    {"right": "一起", "wrong": "yī qǐ", "right_en": "yì qǐ", "wrong_en": "yī qǐ", "note": "口语高频搭配一定要熟", "note_en": "This common phrase must be automatic in speech"},
                    {"right": "一天", "wrong": "yī tiān 每次都重读", "right_en": "yì tiān", "wrong_en": "always stressing yī tiān heavily", "note": "高频时间词先练熟", "note_en": "Master frequent time expressions first"},
                ],
            },
            {
                "kind": "correctness",
                "title": "“不”的变调与语流",
                "overview_zh": "“不”看起来很简单，但一到句子里就常常变化。你如果每次都读成原来的样子，语流会显得很生硬。",
                "overview_en": "'不' looks simple, but it often changes inside sentences. If you always keep the citation tone, the flow of your speech becomes stiff.",
                "tip_zh": "最重要的一条先记住：在第四声前，“不”常读成 bú。先把最常见的搭配练熟，再去扩展。",
                "tip_en": "Remember the most important rule first: before a fourth tone, '不' often becomes bú. Master the common combinations first and expand later.",
                "items": [
                    {"right": "不对", "wrong": "bù duì 读得很硬", "right_en": "bú duì", "wrong_en": "a rigid bù duì", "note": "第四声前更自然的是 bú", "note_en": "Before a fourth tone, bú sounds more natural"},
                    {"right": "不是", "wrong": "bù shì 生硬断开", "right_en": "bú shì", "wrong_en": "an overly separated bù shì", "note": "高频否定一定要顺", "note_en": "High-frequency negation must flow smoothly"},
                    {"right": "不去", "wrong": "bù qù 每次都完全重读", "right_en": "bú qù", "wrong_en": "always fully stressing bù qù", "note": "口语语流比单字更重要", "note_en": "Speech flow matters more than isolated syllables"},
                    {"right": "不高", "wrong": "bú gāo", "right_en": "bù gāo", "wrong_en": "bú gāo", "note": "不是所有情况都改", "note_en": "It does not change in every environment"},
                    {"right": "不忙", "wrong": "bú máng", "right_en": "bù máng", "wrong_en": "bú máng", "note": "二声前通常保持原调", "note_en": "Before a second tone it usually stays in the original tone"},
                ],
            },
            {
                "kind": "correctness",
                "title": "连续第三声与真实句子节奏",
                "overview_zh": "第三声一多，很多学习者就卡住了。原因不是不会第三声，而是不会在连续语流里调整第三声。",
                "overview_en": "When too many third-tone syllables appear together, many learners get stuck. The problem is not that they do not know the third tone, but that they cannot adjust it inside connected speech.",
                "tip_zh": "连续第三声时，不要每个字都完整地先下后上。真实口语里，前面的第三声经常会先变得更像第二声。",
                "tip_en": "In a chain of third tones, do not make every syllable fully fall and rise. In real speech, earlier third tones often shift and sound more like a rising tone.",
                "items": [
                    {"right": "你好", "wrong": "两个字都读完整第三声", "right_en": "ní hǎo", "wrong_en": "two full third tones in a row", "note": "这是最经典的语流例子", "note_en": "This is the classic connected-speech example"},
                    {"right": "很好", "wrong": "很和好都压得太低", "right_en": "hén hǎo", "wrong_en": "both syllables stay too low", "note": "前一个要先带起来", "note_en": "The first one should shift upward"},
                    {"right": "我很好", "wrong": "三个第三声全部分开读", "right_en": "wó hén hǎo", "wrong_en": "three full isolated third tones", "note": "句子里更要顾整体节奏", "note_en": "Inside a sentence, overall rhythm matters even more"},
                    {"right": "你想买什么", "wrong": "想和买都处理得太僵", "right_en": "a smoother connected pattern", "wrong_en": "a stiff sequence", "note": "第三声链条要一起练", "note_en": "Train third-tone chains as one unit"},
                    {"right": "我想请你给我讲讲", "wrong": "每个第三声都单独读", "right_en": "a connected spoken pattern", "wrong_en": "each third tone isolated", "note": "长句最能检验稳定度", "note_en": "Long sentences reveal whether the pattern is stable"},
                ],
            },
        ],
    },
    {
        "number": "103",
        "slug": "03-number-sense-and-liang-er",
        "title": "Number Sense in Chinese",
        "cn_title": "二、两、数字与编号全攻略",
        "subtitle": "从数量、日期到编号，把数字说自然",
        "color": "#198754",
        "intro_zh": "很多学习者学完数字以后，仍然会在最简单的地方出错，比如把两个星期说成二个星期，或者把二零二六年读得很奇怪。问题不是数字不会，而是中文里数字有不同系统。",
        "intro_en": "Many learners still make mistakes in very basic places after learning Chinese numbers, such as saying 二个星期 instead of 两个星期, or reading the year 2026 in an unnatural way. The issue is not the numbers themselves, but the fact that Chinese uses numbers in different systems.",
        "use_zh": "这本书把数字分成数量、编号、日期、时间、价格和次数六大场景。你会看到什么时候更适合用两，什么时候只能用二，什么时候要逐位读。",
        "use_en": "This book divides number use into six major contexts: quantity, numbering, dates, time, prices, and frequency. You will see when 两 is more natural, when only 二 works, and when digit-by-digit reading is required.",
        "modules": [
            {
                "kind": "correctness",
                "title": "二和两：先分清“数东西”和“读编号”",
                "overview_zh": "中文里的二和两不是随便换的。最简单的记法是：数具体东西时多用两，读编号、数学数字、日期时常用二。",
                "overview_en": "In Chinese, 二 and 两 are not freely interchangeable. The simplest rule is: use 两 more often when counting actual things, and use 二 for numbering, math, dates, and coded numbers.",
                "tip_zh": "初学阶段先抓住高频口语。你只要把“两个、两天、两个人”说顺，很多问题会自然减少。",
                "tip_en": "At the beginner stage, focus on frequent spoken patterns. Once '两个', '两天', and '两个人' become natural, many problems disappear on their own.",
                "items": [
                    {"right": "两个星期", "wrong": "二个星期", "right_en": "two weeks", "wrong_en": "a less natural spoken form", "note": "数量加量词时优先用两", "note_en": "Use 两 first when a classifier follows"},
                    {"right": "两个人", "wrong": "二个人", "right_en": "two people", "wrong_en": "a less natural spoken form", "note": "口语里两个人最自然", "note_en": "两个人 is the most natural spoken form"},
                    {"right": "二十四号", "wrong": "两十四号", "right_en": "the 24th", "wrong_en": "incorrect date reading", "note": "日期编号通常用二", "note_en": "Dates usually use 二"},
                    {"right": "二楼", "wrong": "两楼", "right_en": "second floor", "wrong_en": "incorrect floor reading", "note": "楼层编号一般用二", "note_en": "Floor numbering usually uses 二"},
                    {"right": "二零二六年", "wrong": "两零两六年", "right_en": "year 2026", "wrong_en": "incorrect year reading", "note": "年份通常逐位读数字", "note_en": "Years are usually read digit by digit"},
                ],
            },
            {
                "kind": "correctness",
                "title": "日期、月份、年份：数字系统要换档",
                "overview_zh": "一到日期，很多学习者就把数量系统和编号系统混在一起。结果就是月份、号数和年份都说得不自然。",
                "overview_en": "When dates come in, many learners mix the quantity system and the numbering system. As a result, months, day numbers, and years all sound unnatural.",
                "tip_zh": "记日期时先固定顺序：年、月、日或号。顺序固定了，再去纠正每个数字的读法。",
                "tip_en": "Fix the order first: year, month, day. Once the order is stable, correct the pronunciation of each number inside the date.",
                "items": [
                    {"right": "三月二十四号", "wrong": "三月两十四号", "right_en": "March 24th", "wrong_en": "incorrect day reading", "note": "号是编号，不是数量", "note_en": "The day number is a label, not a quantity"},
                    {"right": "一月", "wrong": "一个月（当作月份）", "right_en": "January", "wrong_en": "one month used as a month name", "note": "一月是月份，一个月是时长", "note_en": "一月 is a month name, 一个月 is a duration"},
                    {"right": "二零零八年", "wrong": "两千零八年也每次都硬读", "right_en": "the year 2008", "wrong_en": "a rigid overgeneralized reading", "note": "年份要先听真实用法", "note_en": "Listen to real usage when reading years"},
                    {"right": "二零二六年四月十九号", "wrong": "两零两六年四月十九号", "right_en": "April 19, 2026", "wrong_en": "incorrect year reading", "note": "年份和日期常连读", "note_en": "Years and dates often appear together"},
                    {"right": "星期二", "wrong": "星期两", "right_en": "Tuesday", "wrong_en": "incorrect weekday reading", "note": "星期里的数字通常用二三四五", "note_en": "Weekday names normally use 二三四五"},
                ],
            },
            {
                "kind": "correctness",
                "title": "时间长度：半、个半、点、分、刻",
                "overview_zh": "中文里的时间长度表达看起来简单，但对外语学习者很不友好，因为一个半小时、半小时、两点半、三刻都不是一个逻辑。",
                "overview_en": "Length of time in Chinese looks simple, but it is not learner-friendly because expressions like 一个半小时, 半小时, 两点半, and 三刻 do not follow the same surface logic.",
                "tip_zh": "先把最有用的几种表达练熟：半小时、一个小时、一个半小时、两点半。不要一开始追求所有古老说法。",
                "tip_en": "Master the most useful expressions first: 半小时, 一个小时, 一个半小时, and 两点半. Do not chase every old-fashioned expression at the beginning.",
                "items": [
                    {"right": "半小时", "wrong": "一半小时", "right_en": "half an hour", "wrong_en": "incorrect expression", "note": "半小时本身就是固定说法", "note_en": "半小时 is a fixed expression"},
                    {"right": "一个半小时", "wrong": "一个小时半", "right_en": "one and a half hours", "wrong_en": "less natural word order", "note": "口语里个半结构很重要", "note_en": "The 个半 pattern is very important in speech"},
                    {"right": "两点半", "wrong": "两点三十分（太书面化）", "right_en": "2:30", "wrong_en": "overly formal in daily speech", "note": "半更口语，三十分更书面", "note_en": "半 is more conversational, 三十分 is more formal"},
                    {"right": "十分钟", "wrong": "十分", "right_en": "ten minutes", "wrong_en": "incomplete time unit", "note": "时长要把单位说完整", "note_en": "State the time unit clearly"},
                    {"right": "两小时二十分钟", "wrong": "二小时两十分", "right_en": "two hours and twenty minutes", "wrong_en": "mixed unnatural phrasing", "note": "先把高频单位说顺", "note_en": "Make the common units flow naturally first"},
                ],
            },
            {
                "kind": "correctness",
                "title": "价格、折扣、电话号码：逐位读还是按数量读",
                "overview_zh": "价格和电话号码是两个完全不同的数字世界。价格要考虑量和货币，电话号码则更多是编号系统。",
                "overview_en": "Prices and phone numbers belong to two completely different numerical worlds. Prices involve quantity and currency, while phone numbers belong more to the numbering system.",
                "tip_zh": "问价格时注意钱、块、毛、分。读电话时不要想量词，直接把数字顺下来就行。",
                "tip_en": "When asking about price, pay attention to 钱, 块, 毛, and 分. When reading phone numbers, forget classifiers and simply read the digits in sequence.",
                "items": [
                    {"right": "九折", "wrong": "九十 percent off 的直译思路", "right_en": "pay 90 percent", "wrong_en": "an English discount logic transfer", "note": "中文折扣说的是你要付多少", "note_en": "Chinese discounts describe how much you pay"},
                    {"right": "八五折", "wrong": "八十五折", "right_en": "85 percent of the price", "wrong_en": "incorrect expansion", "note": "折扣口语有固定压缩形式", "note_en": "Discount expressions have a fixed compressed form"},
                    {"right": "一百二十块", "wrong": "一百二十个块", "right_en": "120 yuan", "wrong_en": "incorrect classifier insertion", "note": "价格单位前通常不用个", "note_en": "Do not add 个 before common money units"},
                    {"right": "一二零", "wrong": "一百二十（读急救号码时）", "right_en": "120 as a number code", "wrong_en": "one hundred twenty for a code number", "note": "编号常逐位读", "note_en": "Code numbers are often read digit by digit"},
                    {"right": "我的电话是一三八……", "wrong": "一百三十八……", "right_en": "my phone number is one-three-eight...", "wrong_en": "reading it as a quantity", "note": "电话不是数量，是编号", "note_en": "A phone number is a code, not a quantity"},
                ],
            },
            {
                "kind": "correctness",
                "title": "次数、序数与课堂口语",
                "overview_zh": "学习者常把数量和顺序混掉。一次、两次、第三次、第二课、第二个问题，看起来相似，逻辑却不一样。",
                "overview_en": "Learners often mix quantity and sequence. Expressions like 一次, 两次, 第三次, 第二课, and 第二个问题 look similar, but the logic behind them is different.",
                "tip_zh": "只要抓住两个关键点就够了：表示顺序时常加第，表示次数时常加次。",
                "tip_en": "Two key points are enough at first: add 第 for order, and add 次 for frequency.",
                "items": [
                    {"right": "第一次", "wrong": "第一次数", "right_en": "the first time", "wrong_en": "incorrect expansion", "note": "顺序和次数合在一起", "note_en": "This combines order and occurrence"},
                    {"right": "第二课", "wrong": "两课（表示第二课时）", "right_en": "Lesson Two", "wrong_en": "incorrect quantity reading", "note": "课号属于顺序系统", "note_en": "Lesson numbers belong to the order system"},
                    {"right": "两次", "wrong": "二次（普通口语里不自然）", "right_en": "twice", "wrong_en": "less natural in ordinary speech", "note": "口语频率常优先用两次", "note_en": "In speech, 两次 is usually preferred"},
                    {"right": "第二个问题", "wrong": "两个问题（如果你想表达顺序）", "right_en": "the second question", "wrong_en": "two questions when order is intended", "note": "数量和顺序不能混", "note_en": "Do not confuse quantity with order"},
                    {"right": "我去过两次", "wrong": "我去过第二次", "right_en": "I have been there twice", "wrong_en": "incorrect order expression", "note": "次数说的是总量，不是顺序", "note_en": "Frequency refers to total count, not sequence"},
                ],
            },
        ],
    },
    {
        "number": "104",
        "slug": "04-time-expressions-decoder",
        "title": "Time Expressions Decoder",
        "cn_title": "日期、星期与时间表达解码",
        "subtitle": "约时间、说日期、表达时长的系统训练",
        "color": "#006D77",
        "intro_zh": "时间表达是中文口语里最常用、也最容易出错的模块之一。学员常常知道词，却不会把它们按中文习惯组合起来。",
        "intro_en": "Time expression is one of the most frequently used but also one of the easiest areas to get wrong in spoken Chinese. Learners often know the words but cannot combine them according to Chinese habits.",
        "use_zh": "这本书把时间表达拆成六个最实用的场景：今天和明天、星期系统、月份和时长、几点和什么时候、前后结构，以及约时间对话。",
        "use_en": "This book breaks time expression into six practical contexts: today and tomorrow, the weekday system, month names and duration, what time versus when, before-and-after structures, and appointment dialogues.",
        "modules": [
            {
                "kind": "correctness",
                "title": "今天、明天、后天、前天：先把时间轴立起来",
                "overview_zh": "很多学习者知道这些词的意思，但一说到连续几天，就会混乱。根本原因是脑子里还没有一条稳定的中文时间轴。",
                "overview_en": "Many learners know the meanings of these words, but become confused when talking about several consecutive days. The root problem is that they do not yet have a stable Chinese timeline in their head.",
                "tip_zh": "学习这些词时，不要只背单词，要把它们放到同一条线里比较：前天、昨天、今天、明天、后天。",
                "tip_en": "Do not memorize these words one by one. Put them on the same line and compare them: the day before yesterday, yesterday, today, tomorrow, and the day after tomorrow.",
                "items": [
                    {"right": "后天", "wrong": "明天后", "right_en": "the day after tomorrow", "wrong_en": "tomorrow after", "note": "中文有固定单词，不要硬翻", "note_en": "Chinese has a fixed word for this; do not translate word by word"},
                    {"right": "前天", "wrong": "昨天前", "right_en": "the day before yesterday", "wrong_en": "before yesterday", "note": "时间词常有固定整体", "note_en": "Time words are often fixed wholes"},
                    {"right": "今天下午", "wrong": "今天的下午（普通口语里太重）", "right_en": "this afternoon", "wrong_en": "an overly heavy possessive phrasing", "note": "口语里通常直接并列", "note_en": "In speech, simple adjacency is often enough"},
                    {"right": "明天晚上", "wrong": "明天的晚上", "right_en": "tomorrow evening", "wrong_en": "an overly marked structure", "note": "时间短语先求顺口", "note_en": "Make time phrases sound natural first"},
                    {"right": "这几天", "wrong": "这些天（有时可用，但语气不同）", "right_en": "these days", "wrong_en": "those days / these days with a different feel", "note": "近口语里这几天很高频", "note_en": "这几天 is extremely frequent in speech"},
                ],
            },
            {
                "kind": "correctness",
                "title": "星期系统：星期二、星期天、周末到底怎么说",
                "overview_zh": "星期表达看起来规律，实际误区很多。学习者常常把星期二说成星期两，或者把星期日和星期天当作完全不同的词。",
                "overview_en": "Weekday expressions look regular, but there are many traps. Learners may say 星期两 instead of 星期二, or think 星期日 and 星期天 are totally different words.",
                "tip_zh": "先抓最有用的三组：星期一到星期六，星期天或星期日，以及周末。把这三组说顺，日常交流就够用了。",
                "tip_en": "Focus first on the three most useful sets: Monday to Saturday, Sunday or 星期日, and the weekend. Once these become natural, daily communication becomes much easier.",
                "items": [
                    {"right": "星期二", "wrong": "星期两", "right_en": "Tuesday", "wrong_en": "incorrect weekday reading", "note": "星期里的数字多用二三四", "note_en": "Weekdays normally use 二三四"},
                    {"right": "星期天", "wrong": "星期七", "right_en": "Sunday", "wrong_en": "weekday seven", "note": "星期天和星期日都对", "note_en": "Both 星期天 and 星期日 are correct"},
                    {"right": "周末", "wrong": "星期末", "right_en": "weekend", "wrong_en": "incorrect literal transfer", "note": "周末是高频固定词", "note_en": "周末 is a high-frequency fixed phrase"},
                    {"right": "下星期", "wrong": "下个星期（也对，但语气长度不同）", "right_en": "next week", "wrong_en": "next week with a different rhythm", "note": "两种都可以，但要会听", "note_en": "Both are possible, but you must recognize both"},
                    {"right": "两个星期", "wrong": "二星期", "right_en": "two weeks", "wrong_en": "a less natural spoken form", "note": "时长和星期几不要混", "note_en": "Do not mix duration with weekday naming"},
                ],
            },
            {
                "kind": "correctness",
                "title": "一月和一个月：月份和时长是两套逻辑",
                "overview_zh": "初学者最常见的一类时间错误，就是把月份和时间长度混为一谈。看到 month，就什么都想成一个月。",
                "overview_en": "A common early error is to mix month names with time duration. Learners see the idea of 'month' and want to turn everything into 一个月.",
                "tip_zh": "你要先问自己一个问题：这里是在说日历上的名字，还是在说持续了多久？这个问题一想清楚，很多错误就会消失。",
                "tip_en": "Ask yourself one question first: are you naming a month on the calendar, or are you talking about duration? Once that becomes clear, many errors disappear.",
                "items": [
                    {"right": "一月", "wrong": "一个月（表示一月份时）", "right_en": "January", "wrong_en": "one month used as a month name", "note": "月份名称和时长不能混", "note_en": "Do not mix the month name with duration"},
                    {"right": "我在中国住了一个月", "wrong": "我在中国住了一月", "right_en": "I lived in China for one month", "wrong_en": "using a month name for duration", "note": "时长更常用个", "note_en": "Duration usually takes 个"},
                    {"right": "二月", "wrong": "两月（表示月份名时）", "right_en": "February", "wrong_en": "incorrect month-name reading", "note": "月份名走编号系统", "note_en": "Month names follow the numbering system"},
                    {"right": "两个月", "wrong": "二个月（普通口语里不自然）", "right_en": "two months", "wrong_en": "less natural in speech", "note": "时长加量词时优先用两", "note_en": "Use 两 more often in duration with a classifier"},
                    {"right": "这个月", "wrong": "这月（有地区差异）", "right_en": "this month", "wrong_en": "a shorter form that may sound regional or marked", "note": "教材阶段先记高频主流说法", "note_en": "At the textbook stage, focus on the mainstream form first"},
                ],
            },
            {
                "kind": "correctness",
                "title": "几点和什么时候：问钟点，还是问时间范围",
                "overview_zh": "很多学习者把什么时候和几点当成一个词来用。其实它们的差别很大，一个问具体钟点，一个问更宽的时间范围。",
                "overview_en": "Many learners use 什么时候 and 几点 as if they were the same. In fact, they are quite different: one asks for a clock time, and the other asks for a broader time frame.",
                "tip_zh": "如果你想听到像三点半、七点、九点四十这种答案，用几点；如果你想听到明天、下周、晚一点这种答案，用什么时候。",
                "tip_en": "If you expect an answer like 3:30, 7 o'clock, or 9:40, use 几点. If you expect tomorrow, next week, or a little later, use 什么时候.",
                "items": [
                    {"right": "你几点下班", "wrong": "你什么时候下班（如果你只想问钟点）", "right_en": "What time do you get off work?", "wrong_en": "When do you get off work? if the target is a precise clock time", "note": "几点更具体", "note_en": "几点 is more specific"},
                    {"right": "你什么时候去北京", "wrong": "你几点去北京（如果只问哪一天或哪段时间）", "right_en": "When are you going to Beijing?", "wrong_en": "What time are you going to Beijing? when you only want a broad time", "note": "什么时候更宽", "note_en": "什么时候 is broader"},
                    {"right": "我们几点见面", "wrong": "我们什么时候见面（如果你要精确约时）", "right_en": "What time shall we meet?", "wrong_en": "When shall we meet? if you are fixing a clock time", "note": "约见面时常需要几点", "note_en": "Appointments often need 几点"},
                    {"right": "你什么时候有空", "wrong": "你几点有空", "right_en": "When are you free?", "wrong_en": "At what exact time are you free? when the scope should be broad", "note": "有空更适合宽时间", "note_en": "Being free is usually a broader time question"},
                    {"right": "大概七点", "wrong": "大概什么时候：七点（问法和答法不配）", "right_en": "around seven o'clock", "wrong_en": "mismatched question-answer type", "note": "问法和答法要匹配", "note_en": "The question type and answer type must match"},
                ],
            },
            {
                "kind": "correctness",
                "title": "前、后、以前、以后、之前、之后：中文时间关系词怎么排",
                "overview_zh": "时间关系词表面上很多，其实核心就是前和后。问题在于，学习者常常把中文顺序和英语顺序混用，所以说出来很别扭。",
                "overview_en": "On the surface there are many time relation words, but the core is simply before and after. The problem is that learners often mix Chinese order with English order, which makes their sentences sound awkward.",
                "tip_zh": "先记最有用的几组：三天后、一小时前、吃饭以前、开会之后。把这些固定结构练顺，再扩展。",
                "tip_en": "Memorize the most useful patterns first: three days later, one hour ago, before eating, and after the meeting. Make these fixed structures smooth before expanding.",
                "items": [
                    {"right": "三天后", "wrong": "后三天", "right_en": "three days later", "wrong_en": "three days after in reversed order", "note": "中文常先说数量，再说后", "note_en": "Chinese usually puts the amount before 后"},
                    {"right": "一小时前", "wrong": "前一小时（表示过去时间时）", "right_en": "one hour ago", "wrong_en": "an unnatural reversed order", "note": "前和后多放在数量后面", "note_en": "前 and 后 often come after the amount"},
                    {"right": "吃饭以前", "wrong": "以前吃饭（如果你想说 before eating）", "right_en": "before eating", "wrong_en": "eat before in mismatched order", "note": "动作短语后面能接以前", "note_en": "A verb phrase can be followed by 以前"},
                    {"right": "开会之后", "wrong": "之后开会（如果你想说 after the meeting）", "right_en": "after the meeting", "wrong_en": "afterwards meeting in mismatched order", "note": "整体时间块要稳定", "note_en": "Keep the whole time block stable"},
                    {"right": "下课以后我们去吃饭", "wrong": "我们以后下课去吃饭", "right_en": "After class, we will go eat", "wrong_en": "a confusing order", "note": "以后的位置会影响意思", "note_en": "The position of 以后 changes the meaning"},
                ],
            },
        ],
    },
    {
        "number": "105",
        "slug": "05-question-words-mastery",
        "title": "Question Words Mastery",
        "cn_title": "疑问词与提问系统精讲",
        "subtitle": "把什么、多少、谁、哪儿、为什么、怎么样真正用对",
        "color": "#D62828",
        "intro_zh": "疑问词不是一个个背下来就会用了。真正的难点在于：你要知道自己到底在问什么类型的信息，问数字、问人、问地点、问选择、问原因还是问方式。",
        "intro_en": "Question words are not something you can use correctly just by memorizing them one by one. The real difficulty is knowing what type of information you are asking for: number, person, place, choice, reason, or manner.",
        "use_zh": "这本书会把高频疑问词拆成一套系统。每一章不仅讲词义，还讲它和别的疑问词为什么不一样，为什么很多外语学习者会在这里被英文逻辑带偏。",
        "use_en": "This book breaks common question words into a coherent system. Each chapter explains not only what the word means, but also why it differs from other question words and how English logic often pushes learners in the wrong direction.",
        "modules": [
            {
                "kind": "correctness",
                "title": "什么：问事物，不要拿来问数字",
                "overview_zh": "很多学习者学会什么以后，就想用它去问一切。但中文不是这样，什么主要问事物、内容、名称，不负责所有问题。",
                "overview_en": "Many learners learn 什么 and then try to use it for everything. Mandarin does not work that way. 什么 mainly asks about things, content, or names; it does not cover every type of question.",
                "tip_zh": "如果你想知道这个东西叫什么、是什么、做什么，可以先想到什么。如果你想知道数字，就要换别的词。",
                "tip_en": "If you want to know what something is called, what it is, or what someone is doing, start with 什么. If you want a number, use a different question word.",
                "items": [
                    {"right": "这是什么", "wrong": "这是多少", "right_en": "What is this?", "wrong_en": "How much is this? when you only want the identity", "note": "认东西时用什么", "note_en": "Use 什么 when identifying something"},
                    {"right": "你叫什么名字", "wrong": "你多少名字", "right_en": "What is your name?", "wrong_en": "incorrect number question", "note": "姓名不是数字信息", "note_en": "A name is not a numeric item"},
                    {"right": "你想吃什么", "wrong": "你想吃多少（如果不是问数量）", "right_en": "What do you want to eat?", "wrong_en": "How much do you want to eat? when quantity is not the target", "note": "内容和数量要分开", "note_en": "Separate content from quantity"},
                    {"right": "你做什么工作", "wrong": "你做哪个工作（普通问职业时）", "right_en": "What work do you do?", "wrong_en": "which work in an unnatural way", "note": "泛问类别时用什么", "note_en": "Use 什么 when the category is broad"},
                    {"right": "你在看什么", "wrong": "你在看怎么样", "right_en": "What are you watching?", "wrong_en": "how are you watching", "note": "动作内容最适合什么", "note_en": "Action content fits 什么 best"},
                ],
            },
            {
                "kind": "correctness",
                "title": "多少：中文里问数字的核心词",
                "overview_zh": "多少是中文里非常核心的疑问词。很多学习者只把它理解成 how many，但中文里它的使用范围比英文直觉更大。",
                "overview_en": "多少 is a core question word in Mandarin. Many learners understand it only as 'how many', but its range of use is broader than English intuition suggests.",
                "tip_zh": "中文里只要结果和数字有关，你都应该先想到多少。电话、价格、年龄、门牌、地址信息都可以往这个方向想。",
                "tip_en": "In Mandarin, if the answer is related to a number, you should first think of 多少. Phone numbers, prices, ages, apartment numbers, and address information often move in that direction.",
                "items": [
                    {"right": "你的电话多少", "wrong": "你的电话什么", "right_en": "What is your phone number?", "wrong_en": "what is your phone", "note": "电话号属于数字信息", "note_en": "A phone number is numeric information"},
                    {"right": "这个多少钱", "wrong": "这个什么钱", "right_en": "How much is this?", "wrong_en": "what money is this", "note": "价格表达最常见", "note_en": "This is the most common price question"},
                    {"right": "你多大", "wrong": "你什么年龄", "right_en": "How old are you?", "wrong_en": "what age are you", "note": "年龄常用多大，不直接硬翻", "note_en": "Age often uses 多大, not a literal translation"},
                    {"right": "你有多少学生", "wrong": "你有什么学生（如果你想问数量）", "right_en": "How many students do you have?", "wrong_en": "what students do you have when quantity is intended", "note": "数量问题优先多少", "note_en": "Use 多少 first for quantity"},
                    {"right": "你的地址多少", "wrong": "你的地址什么", "right_en": "What is your address?", "wrong_en": "what is your address with the wrong pattern", "note": "教材口语里常见这种问法", "note_en": "This pattern appears often in practical spoken teaching"},
                ],
            },
            {
                "kind": "correctness",
                "title": "谁、哪儿、哪个：问人、问地点、问选择",
                "overview_zh": "这三个词看起来都很简单，但在真实交流里经常被混用。核心区别是：谁问人，哪儿问地点，哪个问选项。",
                "overview_en": "These three words all look simple, but they are often mixed up in actual communication. The core difference is this: 谁 asks about people, 哪儿 asks about places, and 哪个 asks about choices.",
                "tip_zh": "如果答案可能是一个名字，用谁；如果答案是一个地方，用哪儿；如果答案是几个选项中的一个，用哪个。",
                "tip_en": "If the answer could be a person's name, use 谁. If the answer is a place, use 哪儿. If the answer is one choice among several, use 哪个.",
                "items": [
                    {"right": "他是谁", "wrong": "他是哪个", "right_en": "Who is he?", "wrong_en": "which one is he", "note": "问人先用谁", "note_en": "Use 谁 for people"},
                    {"right": "你在哪儿", "wrong": "你是谁地方", "right_en": "Where are you?", "wrong_en": "incorrect mixed form", "note": "地点问哪儿", "note_en": "Use 哪儿 for place"},
                    {"right": "你喜欢哪个", "wrong": "你喜欢哪儿（如果不是问地方）", "right_en": "Which one do you like?", "wrong_en": "where do you like when choice is intended", "note": "选项问哪个", "note_en": "Use 哪个 for choice"},
                    {"right": "你找谁", "wrong": "你找哪儿", "right_en": "Who are you looking for?", "wrong_en": "where are you looking", "note": "宾语如果是人，就用谁", "note_en": "If the object is a person, use 谁"},
                    {"right": "洗手间在哪儿", "wrong": "洗手间是谁", "right_en": "Where is the restroom?", "wrong_en": "who is the restroom", "note": "问厕所是地点，不是选择也不是人", "note_en": "A restroom question is about location"},
                ],
            },
            {
                "kind": "correctness",
                "title": "为什么、怎么、怎么样：原因、方法、状态别混",
                "overview_zh": "这三个疑问词很容易在英语直觉里混掉。因为英文 how 的范围很大，但中文会把原因、方法、状态拆得更细。",
                "overview_en": "These three question words are easy to mix if you follow English intuition, because English 'how' covers a large range. Mandarin separates reason, method, and state more clearly.",
                "tip_zh": "想问原因时先想到为什么，想问做法时先想到怎么，想问感受或评价时先想到怎么样。",
                "tip_en": "Use 为什么 when you ask for a reason, 怎么 when you ask for a method, and 怎么样 when you ask for a condition or evaluation.",
                "items": [
                    {"right": "你为什么喜欢北京", "wrong": "你怎么样喜欢北京", "right_en": "Why do you like Beijing?", "wrong_en": "how do you like Beijing in the wrong sense", "note": "问原因用为什么", "note_en": "Use 为什么 for reasons"},
                    {"right": "你怎么去公司", "wrong": "你为什么去公司（如果你只想问交通方式）", "right_en": "How do you go to the office?", "wrong_en": "why do you go to the office when you only want the method", "note": "问方式用怎么", "note_en": "Use 怎么 for method"},
                    {"right": "你觉得这家店怎么样", "wrong": "你觉得这家店怎么", "right_en": "How do you find this shop?", "wrong_en": "an incomplete form", "note": "评价和感受常用怎么样", "note_en": "Use 怎么样 for evaluation"},
                    {"right": "天气怎么样", "wrong": "天气为什么", "right_en": "How is the weather?", "wrong_en": "why is the weather", "note": "状态问题不等于原因问题", "note_en": "A state question is not a reason question"},
                    {"right": "这个字怎么读", "wrong": "这个字怎么样读", "right_en": "How do you read this character?", "wrong_en": "a mismatched evaluation form", "note": "具体方法更适合怎么", "note_en": "Specific method fits 怎么 better"},
                ],
            },
            {
                "kind": "correctness",
                "title": "什么时候、几点、哪一天：时间问题要问准",
                "overview_zh": "时间疑问词之所以难，是因为很多答案都和时间有关，但精确度不同。中文在这里区分得比很多学习者想象的更清楚。",
                "overview_en": "Time question words are difficult because many answers relate to time, but not with the same degree of precision. Mandarin distinguishes these more clearly than many learners expect.",
                "tip_zh": "如果答案可能是“周五”“明天”“下个月”，优先想到什么时候或哪一天；如果答案是“三点半”，优先想到几点。",
                "tip_en": "If the answer may be Friday, tomorrow, or next month, think first of 什么时候 or 哪一天. If the answer is 3:30, think first of 几点.",
                "items": [
                    {"right": "你什么时候有空", "wrong": "你几点有空", "right_en": "When are you free?", "wrong_en": "At what exact time are you free? when the scope is broad", "note": "有空通常是宽时间", "note_en": "Being free usually refers to a broad span"},
                    {"right": "我们哪一天见面", "wrong": "我们什么天见面", "right_en": "Which day shall we meet?", "wrong_en": "what day in an unnatural form", "note": "具体日期常说哪一天", "note_en": "Use 哪一天 for a specific day choice"},
                    {"right": "电影几点开始", "wrong": "电影什么时候开始（如果你只想知道具体钟点）", "right_en": "What time does the movie start?", "wrong_en": "when does the movie start if you want a precise time", "note": "钟点更适合几点", "note_en": "Clock time fits 几点 better"},
                    {"right": "今天是什么天气", "wrong": "今天是哪一天（如果你问的是天气）", "right_en": "What is the weather like today?", "wrong_en": "which day is it today when weather is intended", "note": "什么天在口语里容易被误听", "note_en": "什么天 can be confusing in speech"},
                    {"right": "哪一天都可以", "wrong": "什么天都可以", "right_en": "Any day is okay", "wrong_en": "an unnatural form", "note": "任指结构也要用对基本词", "note_en": "Even free-choice structures need the right base word"},
                ],
            },
        ],
    },
    {
        "number": "106",
        "slug": "06-question-words-with-dou",
        "title": "Question Words with 都",
        "cn_title": "疑问词的扩展用法与“都”结构",
        "subtitle": "从提问到任指，学会谁都、什么都、哪儿都",
        "color": "#3A86FF",
        "intro_zh": "很多学习者学会疑问词以后，只会拿来提问，却不会它们和“都”连用后的另一套意思。结果就是听得懂问题，听不懂口语里的自由表达。",
        "intro_en": "Many learners know how to use question words to ask questions, but do not understand the second set of meanings that appears when these words combine with 都. As a result, they understand the question form but miss the freer spoken usage.",
        "use_zh": "这本书会把“谁都、什么都、哪儿都、什么时候都可以”这一类表达彻底讲清楚。你会看到同一个词为什么一会儿表示疑问，一会儿又表示所有、任何。",
        "use_en": "This book explains expressions such as 谁都, 什么都, 哪儿都, and 什么时候都可以 in a complete way. You will see why the same word can express a question in one place and a meaning like 'everyone' or 'anything' in another.",
        "modules": [
            {
                "kind": "correctness",
                "title": "谁都、什么都：不再是问句，而是任指",
                "overview_zh": "一看到谁、什么，很多学习者本能就觉得这是在提问。可是一旦和都连起来，它们常常不再问，而是在表示“所有的人”或“所有的东西”。",
                "overview_en": "The moment learners see 谁 or 什么, they often assume a question is being asked. But once these words combine with 都, they often stop asking and start meaning 'everyone' or 'everything'.",
                "tip_zh": "判断方法很简单：如果后面已经有完整信息，不是在等答案，那它大概率就不是问句。",
                "tip_en": "The test is simple: if the sentence already contains complete information and is not waiting for an answer, it is probably no longer a question.",
                "items": [
                    {"right": "谁都喜欢他", "wrong": "谁喜欢他（如果你想表达 everybody）", "right_en": "Everyone likes him", "wrong_en": "Who likes him? when you mean everybody", "note": "都把疑问词拉成任指", "note_en": "都 turns the question word into a free-choice expression"},
                    {"right": "我什么都吃", "wrong": "我吃什么（如果你想表达 I eat everything）", "right_en": "I eat everything", "wrong_en": "What do I eat? when you mean everything", "note": "什么都常表示 everything", "note_en": "什么都 often means everything"},
                    {"right": "他谁都不认识", "wrong": "他不认识谁（如果不是问句）", "right_en": "He knows nobody", "wrong_en": "Who does he not know? if not meant as a question", "note": "否定句里也非常常见", "note_en": "This is also common in negative sentences"},
                    {"right": "这个问题谁都懂", "wrong": "这个问题谁懂（如果你想表达 everyone understands it）", "right_en": "Everyone understands this question", "wrong_en": "Who understands this question?", "note": "语气要从问变陈述", "note_en": "Shift from a questioning tone to a statement"},
                    {"right": "小孩子什么都想试试", "wrong": "小孩子想试什么（如果你想表达 everything）", "right_en": "Children want to try everything", "wrong_en": "What do children want to try? when everything is intended", "note": "口语里很高频", "note_en": "This is very common in daily speech"},
                ],
            },
            {
                "kind": "correctness",
                "title": "哪儿都、怎么都：地点和方式的任指表达",
                "overview_zh": "哪儿和怎么也一样，一旦和都连用，就常常从问地点、问方式，变成“任何地方”“不管怎么”的意思。",
                "overview_en": "哪儿 and 怎么 behave the same way. Once they combine with 都, they often shift from asking about location or method to meanings such as 'any place' or 'no matter how'.",
                "tip_zh": "先听语气，再看结构。如果说话人不是在等你回答地点，那哪儿都很可能是在表示 everywhere 或 anywhere。",
                "tip_en": "Listen to the tone first and then look at the structure. If the speaker is not waiting for a location answer, 哪儿都 is likely to mean everywhere or anywhere.",
                "items": [
                    {"right": "哪儿都可以", "wrong": "哪儿可以（如果你想表达 anywhere is okay）", "right_en": "Anywhere is okay", "wrong_en": "where is okay? when you mean free choice", "note": "哪儿都常表达 anywhere", "note_en": "哪儿都 often means anywhere"},
                    {"right": "我最近哪儿都不想去", "wrong": "我最近去哪儿（如果你想表达 nowhere）", "right_en": "I don't want to go anywhere recently", "wrong_en": "Where am I going? when nowhere is intended", "note": "否定句里常接 anywhere", "note_en": "In negatives it often corresponds to anywhere"},
                    {"right": "怎么去都行", "wrong": "怎么去（如果你想表达 any way is fine）", "right_en": "Any way of going is fine", "wrong_en": "How do we go? when method freedom is intended", "note": "方式自由时怎么都很好用", "note_en": "怎么都 works well when any method is acceptable"},
                    {"right": "他怎么说我都不生气", "wrong": "他说我怎么不生气", "right_en": "No matter what he says, I won't get angry", "wrong_en": "a scrambled structure", "note": "都结构要看清主干", "note_en": "Keep the sentence backbone clear"},
                    {"right": "你坐地铁、坐车、走路都行，怎么去都可以", "wrong": "你怎么去都问我", "right_en": "Subway, taxi, or walking are all fine; any way is okay", "wrong_en": "an incorrect mixed form", "note": "先列方式，再总结", "note_en": "List options first, then summarize"},
                ],
            },
            {
                "kind": "correctness",
                "title": "什么时候都可以、哪一天都可以：约时间的自由表达",
                "overview_zh": "这类表达在口语里特别常用，因为约时间时，中文经常要表示“我都行”“你定也可以”。如果不会这种结构，回答会显得很硬。",
                "overview_en": "These expressions are extremely common in speech because when scheduling, Mandarin often needs to express 'I'm okay with any time' or 'you can decide'. Without this structure, your answer may sound stiff.",
                "tip_zh": "时间自由选择时，最常用的不是简单重复 yes，而是用都结构把空间打开。",
                "tip_en": "When the time is flexible, Mandarin often opens the space with a 都 structure instead of just repeating 'yes'.",
                "items": [
                    {"right": "什么时候都可以", "wrong": "什么时候可以（如果你想表达 anytime）", "right_en": "Any time is okay", "wrong_en": "when is possible? when anytime is intended", "note": "都把它从问句变成自由回答", "note_en": "都 changes it from a question into a free-choice reply"},
                    {"right": "哪一天都行", "wrong": "什么天都行", "right_en": "Any day is fine", "wrong_en": "an unnatural form", "note": "哪一天比什么天自然得多", "note_en": "哪一天 is much more natural than 什么天 here"},
                    {"right": "上午下午都可以", "wrong": "上午下午可以吗（如果你已经在回答）", "right_en": "Morning or afternoon are both fine", "wrong_en": "a question form when answering", "note": "回答时要从问句切换到陈述句", "note_en": "Switch from a question form to a statement when answering"},
                    {"right": "你定时间吧，我什么时候都可以", "wrong": "你定时间吧，我什么时候", "right_en": "You choose the time; I am free anytime", "wrong_en": "an unfinished response", "note": "完整回应更自然", "note_en": "A complete response sounds more natural"},
                    {"right": "周一到周五我都忙，周末什么时候都可以", "wrong": "周末什么时候忙（如果你想表达 free time）", "right_en": "I'm busy from Monday to Friday, but anytime on the weekend is okay", "wrong_en": "asking about weekend busyness by mistake", "note": "句子层级要清楚", "note_en": "Keep the sentence hierarchy clear"},
                ],
            },
            {
                "kind": "correctness",
                "title": "都和也：不是一回事",
                "overview_zh": "学习者常把都和也互换，因为都觉得它们像英文里的 also。其实都更强调整体覆盖，也更强调“也一样”。",
                "overview_en": "Learners often swap 都 and 也 because both can feel similar to 'also' in English. In fact, 都 emphasizes total coverage, while 也 highlights 'also' in relation to another item.",
                "tip_zh": "你可以这样记：有整体、全部、两边都算进去的时候，先想都；有另外一个也一样的时候，先想也。",
                "tip_en": "Remember it this way: when you mean total coverage or both sides together, think of 都 first; when you mean another item is also the same, think of 也 first.",
                "items": [
                    {"right": "我和他都喜欢咖啡", "wrong": "我和他也喜欢咖啡（如果你想表达 both of us）", "right_en": "Both he and I like coffee", "wrong_en": "also like coffee when total coverage is intended", "note": "并列主语后常用都", "note_en": "After a combined subject, 都 is common"},
                    {"right": "我喜欢咖啡，他也喜欢", "wrong": "我喜欢咖啡，他都喜欢", "right_en": "I like coffee, and he also likes it", "wrong_en": "using 都 where 也 is needed", "note": "第二个主体跟着前一个主体", "note_en": "The second subject follows the first one"},
                    {"right": "这些问题我都懂", "wrong": "这些问题我也懂（如果没有前文对比）", "right_en": "I understand all these questions", "wrong_en": "I also understand these questions without a comparison base", "note": "整体覆盖感很强", "note_en": "This strongly expresses total coverage"},
                    {"right": "你去，我也去", "wrong": "你去，我都去", "right_en": "If you go, I will go too", "wrong_en": "using 都 without a set to cover", "note": "跟着别人做同样动作时常用也", "note_en": "Use 也 when following another person's action"},
                    {"right": "北京和上海我都去过", "wrong": "北京和上海我也去过", "right_en": "I have been to both Beijing and Shanghai", "wrong_en": "also have been when total coverage is intended", "note": "两个地点一起覆盖时更适合都", "note_en": "都 is better when both places are covered together"},
                ],
            },
            {
                "kind": "correctness",
                "title": "把疑问词扩展用法放进真实口语",
                "overview_zh": "最后一步不是做语法题，而是把这种结构放进真实口语。只有到了真实句子里，你才会真正分清它是在问，还是在陈述。",
                "overview_en": "The final step is not solving grammar exercises but putting these patterns into real speech. Only inside real sentences will you fully distinguish whether the structure is asking a question or making a statement.",
                "tip_zh": "看到疑问词时，不要马上机械翻译。先判断整句话是不是在等答案，再决定怎么理解。",
                "tip_en": "When you see a question word, do not translate mechanically right away. First judge whether the sentence is actually waiting for an answer.",
                "items": [
                    {"right": "你喜欢吃什么", "wrong": "你什么都喜欢吃（如果你其实想提问）", "right_en": "What do you like to eat?", "wrong_en": "You like to eat everything when you actually want a question", "note": "问句和任指句不能混", "note_en": "Do not mix the question form with the free-choice form"},
                    {"right": "我什么都喜欢吃", "wrong": "我喜欢吃什么（如果你想回答）", "right_en": "I like to eat everything", "wrong_en": "what do I like to eat? when answering", "note": "回答时结构要换", "note_en": "The structure must change when you answer"},
                    {"right": "你去哪儿玩", "wrong": "你哪儿都玩（如果你其实想提问）", "right_en": "Where are you going to have fun?", "wrong_en": "you play everywhere when you mean a question", "note": "先看句子功能", "note_en": "Look at sentence function first"},
                    {"right": "周末哪儿都可以去", "wrong": "周末去哪儿（如果你想说 anywhere is fine）", "right_en": "Anywhere is okay on the weekend", "wrong_en": "where are we going on the weekend? when freedom is intended", "note": "自由表达需要都", "note_en": "Free-choice meaning needs 都"},
                    {"right": "谁都能学好中文，只是时间快慢不一样", "wrong": "谁能学好中文（如果你想表达 everyone can）", "right_en": "Everyone can learn Chinese well; only the speed differs", "wrong_en": "who can learn Chinese well? when everyone is intended", "note": "鼓励型口语很常见", "note_en": "This is common in encouraging speech"},
                ],
            },
        ],
    },
    {
        "number": "107",
        "slug": "07-negation-and-question-patterns",
        "title": "Negation and Question Patterns",
        "cn_title": "不、没、吗、A不A 与是不是系统训练",
        "subtitle": "把否定句和疑问句说自然",
        "color": "#2B2D42",
        "intro_zh": "否定和提问是中文口语的骨架。如果这里不稳，哪怕词汇很多，说出来也会像一块一块拼起来，不够自然。",
        "intro_en": "Negation and questioning form the skeleton of spoken Chinese. If this part is unstable, even a large vocabulary will still sound pieced together and unnatural.",
        "use_zh": "这本书会把不和没、吗和 A不A、是不是和有没有放在同一个系统里讲清楚，让你知道它们分别处理什么信息，为什么不能随便换。",
        "use_en": "This book explains 不 and 没, 吗 and the A-not-A pattern, as well as 是不是 and 有没有, inside one unified system so that you know what each one handles and why they are not freely interchangeable.",
        "modules": [
            {
                "kind": "correctness",
                "title": "不和没：现在不做，还是过去没做",
                "overview_zh": "很多学习者一学会否定，就只会用一个词。可中文里，不和没的分工非常重要，尤其在日常对话里。",
                "overview_en": "Many learners use only one negative marker after first learning negation. In Mandarin, however, the division between 不 and 没 is crucial, especially in daily conversation.",
                "tip_zh": "先记最简单的区别：不更常说现在或习惯上的否定，没更常说过去没发生或到现在还没发生。",
                "tip_en": "Remember the simplest distinction first: 不 is often used for present or habitual negation, while 没 is often used for things that did not happen in the past or have not happened yet.",
                "items": [
                    {"right": "我今天不去", "wrong": "我今天没去（如果你还没出门，只是在说计划）", "right_en": "I am not going today", "wrong_en": "I didn't go today when you are only stating a present decision", "note": "计划或态度更常用不", "note_en": "Plans and attitudes more often use 不"},
                    {"right": "我昨天没去", "wrong": "我昨天不去", "right_en": "I didn't go yesterday", "wrong_en": "I do not go yesterday", "note": "过去事实更常用没", "note_en": "Past facts more often use 没"},
                    {"right": "我不喝咖啡", "wrong": "我没喝咖啡（如果你想说习惯上不喝）", "right_en": "I don't drink coffee", "wrong_en": "I didn't drink coffee when you mean a habit", "note": "习惯性表达多用不", "note_en": "Habitual statements often use 不"},
                    {"right": "我还没吃饭", "wrong": "我还不吃饭（如果你想说 not yet）", "right_en": "I haven't eaten yet", "wrong_en": "I don't eat yet", "note": "还没是高频固定结构", "note_en": "还没 is a very frequent fixed structure"},
                    {"right": "我不想去", "wrong": "我没想去（如果你想表达 unwillingness）", "right_en": "I don't want to go", "wrong_en": "I didn't think to go when you mean unwillingness", "note": "意愿否定更常用不", "note_en": "Negating intention often takes 不"},
                ],
            },
            {
                "kind": "correctness",
                "title": "不是和没有：固定搭配要熟到不想",
                "overview_zh": "是和有各自有自己的高频否定形式。很多学习者知道规则，但说话时还是会临时拼，所以反应速度不够。",
                "overview_en": "是 and 有 each have their own high-frequency negative forms. Many learners know the rule, but still assemble them on the spot in speech, which slows them down.",
                "tip_zh": "不是和没有要练到像一个词一样，一开口就能整块出来。",
                "tip_en": "Train 不是 and 没有 until they come out like single chunks.",
                "items": [
                    {"right": "我不是老师", "wrong": "我不老师", "right_en": "I am not a teacher", "wrong_en": "I not teacher", "note": "名词判断句离不开是", "note_en": "Nominal judgments need 是"},
                    {"right": "我没有车", "wrong": "我不有车", "right_en": "I don't have a car", "wrong_en": "I not have a car", "note": "有的否定通常是没有", "note_en": "The negative of 有 is usually 没有"},
                    {"right": "今天不是周末", "wrong": "今天没有周末", "right_en": "Today is not the weekend", "wrong_en": "today does not have a weekend", "note": "身份和类别判断要用不是", "note_en": "Use 不是 for identity or category judgments"},
                    {"right": "这里没有人", "wrong": "这里不是人（如果你想说 there is nobody）", "right_en": "There is nobody here", "wrong_en": "this is not a person when you mean nobody is here", "note": "存在句多用没有", "note_en": "Existence statements often use 没有"},
                    {"right": "他不是中国人，但是他有很多中国朋友", "wrong": "他没有中国人", "right_en": "He is not Chinese, but he has many Chinese friends", "wrong_en": "he doesn't have Chinese person", "note": "不是和有不能互换", "note_en": "不是 and 有 cannot replace each other"},
                ],
            },
            {
                "kind": "correctness",
                "title": "吗和 A不A：两种问法，语气不一样",
                "overview_zh": "中文的一般疑问句不只一种。句末加吗是最明显的做法，但 A不A 结构在口语里也非常高频。",
                "overview_en": "Mandarin has more than one way to form a yes-no question. Adding 吗 at the end is the most obvious way, but the A-not-A pattern is also very common in speech.",
                "tip_zh": "初学时先学句末加吗，口语进阶后再把忙不忙、去不去、喜欢不喜欢练顺。",
                "tip_en": "Learn sentence-final 吗 first, and then move on to spoken patterns like 忙不忙, 去不去, and 喜欢不喜欢.",
                "items": [
                    {"right": "你忙吗", "wrong": "你吗忙", "right_en": "Are you busy?", "wrong_en": "incorrect word order", "note": "吗通常放在句末", "note_en": "吗 usually goes at the end of the sentence"},
                    {"right": "你忙不忙", "wrong": "你不忙忙", "right_en": "Are you busy?", "wrong_en": "incorrect A-not-A pattern", "note": "A不A 结构要完整", "note_en": "The A-not-A structure must stay complete"},
                    {"right": "你去不去", "wrong": "你去吗不去", "right_en": "Are you going or not?", "wrong_en": "mixed question forms", "note": "不要把两种问法乱拼", "note_en": "Do not mix the two question patterns randomly"},
                    {"right": "你喜欢吗", "wrong": "你吗喜欢", "right_en": "Do you like it?", "wrong_en": "incorrect word order", "note": "简单问法最适合吗", "note_en": "The simple form fits 吗 best"},
                    {"right": "你喜欢不喜欢上海", "wrong": "你喜欢上海不喜欢", "right_en": "Do you like Shanghai or not?", "wrong_en": "incorrect placement", "note": "A不A 一般贴着动词或形容词", "note_en": "A-not-A stays close to the verb or adjective"},
                ],
            },
            {
                "kind": "correctness",
                "title": "是不是、有没有：把核心信息提出来问",
                "overview_zh": "是不是和有没有特别适合口语，因为它们把核心争议点直接提出来。你是不是老师，你有没有时间，都非常自然。",
                "overview_en": "是不是 and 有没有 are especially useful in speech because they bring the core issue to the front. Questions like 你是不是老师 and 你有没有时间 sound very natural.",
                "tip_zh": "如果你已经知道句子大概的结构，只想确认核心点，是不是和有没有会特别方便。",
                "tip_en": "If you already know the basic sentence structure and only want to confirm the key point, 是不是 and 有没有 are especially convenient.",
                "items": [
                    {"right": "你是不是老师", "wrong": "你是吗老师", "right_en": "Are you a teacher?", "wrong_en": "incorrect order", "note": "是不是能把判断点提前", "note_en": "是不是 brings the judgment point forward"},
                    {"right": "你有没有时间", "wrong": "你有吗时间", "right_en": "Do you have time?", "wrong_en": "incorrect order", "note": "有没有是确认有无的固定块", "note_en": "有没有 is a fixed chunk for presence or absence"},
                    {"right": "这是不是你的书", "wrong": "这是吗你的书", "right_en": "Is this your book?", "wrong_en": "incorrect mixed structure", "note": "名词判断句很适合是不是", "note_en": "是不是 works well in nominal judgments"},
                    {"right": "你今天有没有课", "wrong": "你今天有不有课", "right_en": "Do you have class today?", "wrong_en": "a less standard spoken form in this context", "note": "先记主流高频形式", "note_en": "Learn the mainstream high-frequency form first"},
                    {"right": "你是不是还没吃饭", "wrong": "你还没是不是吃饭", "right_en": "Haven't you eaten yet?", "wrong_en": "scrambled structure", "note": "核心确认块要放前面", "note_en": "Keep the confirmation chunk near the front"},
                ],
            },
            {
                "kind": "correctness",
                "title": "不用、不要、没关系：口语里的否定和回应",
                "overview_zh": "真实对话里，否定不只是语法问题，还包括回应方式。你会不会拒绝、会不会安慰，直接影响口语自然度。",
                "overview_en": "In real conversation, negation is not only a grammar issue. It also includes response patterns. Knowing how to refuse or reassure someone directly affects how natural your speech sounds.",
                "tip_zh": "先掌握最高频的几个块：不用、不用了、不要、没关系、没事。它们在生活里出现的频率远远高于书面例句。",
                "tip_en": "Master the highest-frequency chunks first: 不用, 不用了, 不要, 没关系, and 没事. They appear far more often in real life than textbook-style examples.",
                "items": [
                    {"right": "不用谢", "wrong": "不要谢", "right_en": "You're welcome", "wrong_en": "don't thank", "note": "回应感谢常用不用谢", "note_en": "Use 不用谢 to respond to thanks"},
                    {"right": "不用了", "wrong": "没有了（如果你想礼貌拒绝）", "right_en": "No need anymore", "wrong_en": "there is none left when refusal is intended", "note": "礼貌拒绝很常见", "note_en": "This is a common polite refusal"},
                    {"right": "不要辣", "wrong": "不用辣（如果你在点菜说不要）", "right_en": "No spicy, please", "wrong_en": "no need for spicy when ordering", "note": "点菜排除某样东西更常用不要", "note_en": "Use 不要 when excluding something in ordering"},
                    {"right": "没关系", "wrong": "不关系", "right_en": "It's okay", "wrong_en": "incorrect form", "note": "安慰和回应是固定搭配", "note_en": "Reassurance formulas are fixed chunks"},
                    {"right": "没事", "wrong": "不事", "right_en": "No problem / It's fine", "wrong_en": "incorrect form", "note": "高频口语块要整块记", "note_en": "Memorize high-frequency spoken chunks as wholes"},
                ],
            },
        ],
    },
    {
        "number": "108",
        "slug": "08-shi-hen-hui-neng-keyi",
        "title": "Predicate and Modal Verbs",
        "cn_title": "是、很、会、能、可以 精细辨析",
        "subtitle": "摆脱英文直译，让句子真正像中文",
        "color": "#8338EC",
        "intro_zh": "很多中文学习者到了中级阶段，词汇已经不少，但句子依然有明显的“翻译腔”。最常见的来源，就是把英文里的 be、can、will 直接搬进中文。",
        "intro_en": "By the intermediate stage, many learners already know a lot of vocabulary, yet their sentences still sound translated. One of the main reasons is direct transfer from English be, can, and will structures into Mandarin.",
        "use_zh": "这本书会系统处理五个高频小词：是、很、会、能、可以。它们都很常见，也都很容易被误用，因为它们看起来像能互相替代，实际上分工很细。",
        "use_en": "This book systematically addresses five high-frequency words: 是, 很, 会, 能, and 可以. They all appear constantly and are easy to misuse because they seem interchangeable on the surface, but their functions are actually quite specific.",
        "modules": [
            {
                "kind": "correctness",
                "title": "是：名词判断句的核心，不要到处乱放",
                "overview_zh": "学员最常见的错误之一，就是把是塞进所有句子里。可中文不是英文，形容词作谓语时通常不需要是。",
                "overview_en": "One of the most common learner errors is putting 是 into almost every sentence. Mandarin is not English, and adjectives usually do not need 是 when they act as predicates.",
                "tip_zh": "你可以先记一个最有用的原则：后面如果是身份、职业、国籍这类名词，常常需要是；后面如果是大、小、忙、冷这类形容词，通常不要是。",
                "tip_en": "A useful first principle is this: if the following word is a noun like identity, profession, or nationality, you often need 是; if it is an adjective like big, small, busy, or cold, you usually do not.",
                "items": [
                    {"right": "我是老师", "wrong": "我老师", "right_en": "I am a teacher", "wrong_en": "I teacher", "note": "名词判断常用是", "note_en": "Use 是 in noun judgments"},
                    {"right": "上海很大", "wrong": "上海是大", "right_en": "Shanghai is big", "wrong_en": "Shanghai is big with an unnecessary 是", "note": "形容词前通常不用是", "note_en": "Adjectives usually do not take 是"},
                    {"right": "我很忙", "wrong": "我是很忙", "right_en": "I am busy", "wrong_en": "I am very busy with an unnecessary 是", "note": "忙是状态形容词", "note_en": "忙 is a predicate adjective"},
                    {"right": "他是中国人", "wrong": "他很中国人", "right_en": "He is Chinese", "wrong_en": "he is very Chinese person", "note": "国籍身份属于名词判断", "note_en": "Nationality and identity are noun judgments"},
                    {"right": "今天很冷", "wrong": "今天是冷", "right_en": "It is cold today", "wrong_en": "today is cold with an unnecessary 是", "note": "天气形容词也通常直接作谓语", "note_en": "Weather adjectives also usually act as predicates directly"},
                ],
            },
            {
                "kind": "correctness",
                "title": "很：不一定是“非常”，常常只是让句子完整",
                "overview_zh": "很多学习者一看到很，就以为一定是 very。可在很多基础句子里，很并不是强调，而只是让句子更顺、更像中文。",
                "overview_en": "Many learners see 很 and assume it always means 'very'. In many basic sentences, however, 很 is not strong emphasis. It simply makes the sentence sound complete and natural.",
                "tip_zh": "你可以先把很理解成中文里的常见连接垫子。它有时候真的表示很，有时候只是让形容词句听起来更自然。",
                "tip_en": "You can first think of 很 as a common bridge word in Mandarin. Sometimes it truly means 'very', and sometimes it simply makes an adjective sentence sound natural.",
                "items": [
                    {"right": "我很忙", "wrong": "我忙（有时也对，但在中性陈述里常显得硬）", "right_en": "I am busy", "wrong_en": "I busy, which can sound abrupt in a neutral statement", "note": "很常让句子更平稳", "note_en": "很 often smooths the sentence"},
                    {"right": "今天很热", "wrong": "今天热（在教材入门句里容易显得太硬）", "right_en": "It is hot today", "wrong_en": "today hot, which may sound abrupt in textbook beginner speech", "note": "入门阶段先用很更安全", "note_en": "At the beginner stage, 很 is often the safer default"},
                    {"right": "这个问题很重要", "wrong": "这个问题是重要", "right_en": "This question is important", "wrong_en": "this question is important with a wrong 是 pattern", "note": "重要是形容词", "note_en": "重要 is an adjective"},
                    {"right": "她很好", "wrong": "她是好", "right_en": "She is well / she is good", "wrong_en": "she is good with the wrong predicate pattern", "note": "好在这里作状态词", "note_en": "好 acts as a state adjective here"},
                    {"right": "这个地方很安静", "wrong": "这个地方是安静", "right_en": "This place is quiet", "wrong_en": "this place is quiet with a wrong 是 pattern", "note": "安静也常直接作谓语", "note_en": "安静 also commonly acts as a predicate directly"},
                ],
            },
            {
                "kind": "correctness",
                "title": "会：能力、将来、熟练掌握，不是一种意思",
                "overview_zh": "会是一个让学习者非常头疼的词，因为它不只对应一种英文意思。有时是会做，有时是将会，有时还带熟练掌握的感觉。",
                "overview_en": "会 is a difficult word for learners because it does not match only one English meaning. Sometimes it means knowing how to do something, sometimes it marks the future, and sometimes it carries the sense of learned ability.",
                "tip_zh": "判断会的时候，要先看句子到底在说能力、未来安排，还是一种已经学会的技能。",
                "tip_en": "When you interpret 会, first decide whether the sentence is talking about ability, future action, or a learned skill.",
                "items": [
                    {"right": "我会开车", "wrong": "我可以开车（如果你想强调 skill）", "right_en": "I know how to drive", "wrong_en": "I may drive when skill is intended", "note": "学会的能力常用会", "note_en": "Learned ability often takes 会"},
                    {"right": "明天我会去北京", "wrong": "明天我能去北京（如果你想说未来安排）", "right_en": "I will go to Beijing tomorrow", "wrong_en": "I can go to Beijing tomorrow when future plan is intended", "note": "未来预测或安排可用会", "note_en": "会 can mark future plan or expectation"},
                    {"right": "你会说中文吗", "wrong": "你可以说中文吗（如果你想问 ability）", "right_en": "Can you speak Chinese?", "wrong_en": "may you speak Chinese when ability is intended", "note": "语言技能常用会", "note_en": "Language ability often takes 会"},
                    {"right": "他很快就会回来", "wrong": "他很快就能回来（如果重点不是条件许可）", "right_en": "He will come back soon", "wrong_en": "he can come back soon when prediction is intended", "note": "会也有推测色彩", "note_en": "会 can also carry prediction"},
                    {"right": "我不会游泳", "wrong": "我不能游泳（如果你想表达 I don't know how）", "right_en": "I can't swim / I don't know how to swim", "wrong_en": "I am not allowed / not able due to conditions", "note": "不会更偏技能缺失", "note_en": "不会 points more to lack of skill"},
                ],
            },
            {
                "kind": "correctness",
                "title": "能和可以：能力、条件、许可，重点不同",
                "overview_zh": "能和可以都常被翻成 can，所以很多学习者直接乱换。其实能更常带条件、能力、实现可能性，可以更常带许可和合适性。",
                "overview_en": "Both 能 and 可以 are often translated as 'can', so learners freely swap them. In fact, 能 more often points to ability, conditions, or possibility of realization, while 可以 more often points to permission or appropriateness.",
                "tip_zh": "如果你在请求别人帮忙、问可不可以坐、可不可以拍照，可以很常见；如果你在说今天身体不好，不能跑步，能更自然。",
                "tip_en": "If you are asking for permission or making a polite request, 可以 is common. If you are saying that you cannot run today because your body is not in good shape, 能 is often more natural.",
                "items": [
                    {"right": "你能帮我吗", "wrong": "你会帮我吗（如果你想请求帮助）", "right_en": "Can you help me?", "wrong_en": "do you know how to help me when a request is intended", "note": "请求帮助时能更自然", "note_en": "能 is more natural in direct help requests"},
                    {"right": "这里可以坐吗", "wrong": "这里会坐吗", "right_en": "May I sit here?", "wrong_en": "will sit here / know how to sit here", "note": "许可场景常用可以", "note_en": "Permission contexts often use 可以"},
                    {"right": "我今天不能喝酒", "wrong": "我今天不会喝酒（如果不是说 skill）", "right_en": "I can't drink alcohol today", "wrong_en": "I don't know how to drink today", "note": "条件限制更适合能", "note_en": "Condition-based limits fit 能 better"},
                    {"right": "现在可以进去吗", "wrong": "现在能进去吗（两者都可，但许可感上可以更常见）", "right_en": "May I go in now?", "wrong_en": "can I go in now with weaker permission focus", "note": "问规则许可时先想到可以", "note_en": "Think of 可以 first for permission rules"},
                    {"right": "明天我能来", "wrong": "明天我可以来（如果你想强调条件允许也可以，但重点不同）", "right_en": "I will be able to come tomorrow", "wrong_en": "I may come tomorrow with a different focus", "note": "能更突出客观条件", "note_en": "能 highlights objective possibility more"},
                ],
            },
            {
                "kind": "correctness",
                "title": "把这些小词放进真实场景里",
                "overview_zh": "最后一步不是背定义，而是把它们放回生活里。你在介绍自己、问路、拍照、请人帮忙、说天气时，都要快速做出选择。",
                "overview_en": "The final step is not memorizing abstract definitions, but putting these words back into life. When introducing yourself, asking directions, taking photos, asking for help, or talking about the weather, you need to choose quickly.",
                "tip_zh": "口语里最重要的是先自然，再精细。先把主流说法练熟，再慢慢体会更细的差别。",
                "tip_en": "In speaking, naturalness comes before fine-grained distinction. Master the mainstream forms first, and then refine the differences gradually.",
                "items": [
                    {"right": "我是Tony，我是老师", "wrong": "我是Tony，我很老师", "right_en": "I am Tony. I am a teacher.", "wrong_en": "I am very teacher", "note": "身份判断和形容词判断要分开", "note_en": "Separate noun judgments from adjective judgments"},
                    {"right": "今天天气很冷", "wrong": "今天天气是冷", "right_en": "The weather is cold today", "wrong_en": "today's weather is cold with the wrong predicate pattern", "note": "天气形容词直接作谓语", "note_en": "Weather adjectives act directly as predicates"},
                    {"right": "你可以帮我拍照片吗", "wrong": "你会帮我拍照片吗（如果不是问 skill）", "right_en": "Can you help me take a photo?", "wrong_en": "do you know how to help me take a photo when a request is intended", "note": "礼貌请求时可以非常高频", "note_en": "可以 is very common in polite requests"},
                    {"right": "我不会开车，但是我能坐地铁去", "wrong": "我不能开车（如果你想表达 lack of skill）", "right_en": "I can't drive, but I can take the subway", "wrong_en": "I cannot drive when you mean lack of skill", "note": "不会和不能并不一样", "note_en": "不会 and 不能 are not the same"},
                    {"right": "明天我会早点来", "wrong": "明天我可以早点来（如果你想表达 future intention）", "right_en": "I will come earlier tomorrow", "wrong_en": "I may come earlier tomorrow when intention is intended", "note": "会能表达未来安排", "note_en": "会 can express a future arrangement"},
                ],
            },
        ],
    },
    {
        "number": "109",
        "slug": "09-small-words-big-meaning",
        "title": "Small Words Big Meaning",
        "cn_title": "一点儿、有点儿、量词、的、叠词 深度训练",
        "subtitle": "最小的词，最容易出错",
        "color": "#F77F00",
        "intro_zh": "很多真正影响口语自然度的地方，不在大语法，而在这些很小的词上。你一张口，母语者先听到的往往就是一点儿和有点儿、个和件、我的和我妈妈这些细节。",
        "intro_en": "Many of the details that truly affect how natural your Chinese sounds are not in the big grammar points, but in these tiny words. The first things native speakers notice are often details like 一点儿 versus 有点儿, 个 versus 件, or 我的 versus 我妈妈.",
        "use_zh": "这本书专门处理最容易被忽视的小结构：轻量表达、量词、的的省略、动词重叠、形容词转动词式表达。每个点都很小，但都直接影响日常口语。",
        "use_en": "This book focuses on the small structures that are easiest to overlook: small-quantity expressions, classifiers, omission of 的, verb reduplication, and adjective-to-verb-like spoken patterns. Each point is small, but all of them directly shape everyday speech.",
        "modules": [
            {
                "kind": "correctness",
                "title": "一点儿和有点儿：中性一点，还是带一点不满意",
                "overview_zh": "这两个表达看起来只差一个字，但语气差别很大。一点儿更中性，有点儿常常带轻微负面评价。",
                "overview_en": "These two expressions differ by only one character on the surface, but their tone is very different. 一点儿 is more neutral, while 有点儿 often carries a mild negative evaluation.",
                "tip_zh": "如果你只是说数量少，先想到一点儿；如果你在表达不舒服、不满意、不方便，先想到有点儿。",
                "tip_en": "If you are simply talking about a small amount, think of 一点儿 first. If you are expressing discomfort, dissatisfaction, or inconvenience, think of 有点儿 first.",
                "items": [
                    {"right": "我会说一点儿中文", "wrong": "我会说有点儿中文", "right_en": "I can speak a little Chinese", "wrong_en": "I can speak somewhat Chinese in an unnatural way", "note": "数量少更适合一点儿", "note_en": "A small amount fits 一点儿 better"},
                    {"right": "今天有点儿累", "wrong": "今天一点儿累", "right_en": "I'm a little tired today", "wrong_en": "incorrect neutral pattern", "note": "身体不舒服常用有点儿", "note_en": "Mild discomfort often takes 有点儿"},
                    {"right": "请给我一点儿水", "wrong": "请给我有点儿水", "right_en": "Please give me a little water", "wrong_en": "an unnatural request form", "note": "请求少量东西常用一点儿", "note_en": "Requests for a small amount often use 一点儿"},
                    {"right": "这个有点儿贵", "wrong": "这个一点儿贵", "right_en": "This is a bit expensive", "wrong_en": "an unnatural neutral form", "note": "评价偏负面时常用有点儿", "note_en": "Mildly negative evaluations often use 有点儿"},
                    {"right": "他说得快一点儿", "wrong": "他说得有点儿", "right_en": "He should speak a little faster", "wrong_en": "an incomplete form", "note": "程度微调常用一点儿", "note_en": "Slight degree adjustment often uses 一点儿"},
                ],
            },
            {
                "kind": "correctness",
                "title": "量词：忘了专用量词时，个是安全网",
                "overview_zh": "量词是很多学习者的痛点，因为中文几乎什么名词都要配量词。但好消息是，初学阶段个确实能救很多场。",
                "overview_en": "Classifiers are a pain point for many learners because Mandarin uses them with a huge number of nouns. The good news is that at the beginner stage, 个 really can save you in many situations.",
                "tip_zh": "不要因为不会量词就不敢开口。先用个把句子说出来，再慢慢升级成更准确的量词。",
                "tip_en": "Do not stop speaking just because you are not sure about a classifier. Use 个 to get the sentence out first, and then gradually upgrade to more accurate classifiers.",
                "items": [
                    {"right": "一个问题", "wrong": "一问题", "right_en": "one question", "wrong_en": "missing classifier", "note": "大多数名词前不能直接空着", "note_en": "Most nouns cannot stand there without a classifier"},
                    {"right": "一件衬衫", "wrong": "一个衬衫（不够准确）", "right_en": "a shirt", "wrong_en": "a generic classifier instead of the specific one", "note": "衣服更准确的是件", "note_en": "件 is more accurate for clothes"},
                    {"right": "一杯咖啡", "wrong": "一个咖啡（不够准确）", "right_en": "a cup of coffee", "wrong_en": "generic classifier instead of the specific one", "note": "饮品更准确的是杯", "note_en": "杯 is more accurate for drinks"},
                    {"right": "一本书", "wrong": "一个书（不够准确）", "right_en": "a book", "wrong_en": "generic classifier instead of the specific one", "note": "书常配本", "note_en": "Books often take 本"},
                    {"right": "一张票", "wrong": "一个票（不够准确）", "right_en": "a ticket", "wrong_en": "generic classifier instead of the specific one", "note": "纸片状常配张", "note_en": "Flat objects often take 张"},
                ],
            },
            {
                "kind": "correctness",
                "title": "的：什么时候要说，什么时候可以省",
                "overview_zh": "“的”是中文里最常见、也最容易被乱删乱加的词。它既能标记修饰关系，也能表示所属关系。",
                "overview_en": "'的' is one of the most common and most frequently mishandled words in Mandarin. It can mark modification, and it can also indicate possession.",
                "tip_zh": "如果你拿不准，加上的通常比删掉更安全。但你也要知道，人称亲属关系里，经常可以自然省掉。",
                "tip_en": "If you are not sure, adding 的 is usually safer than deleting it. Still, you should know that in family-related possession, it can often be omitted naturally.",
                "items": [
                    {"right": "我的公司", "wrong": "我公司", "right_en": "my company", "wrong_en": "my company without 的", "note": "非亲属类所属一般保留的", "note_en": "Keep 的 for ordinary possession outside family terms"},
                    {"right": "我妈妈", "wrong": "我的妈妈（也对，但很多口语场景更自然的是省掉）", "right_en": "my mom", "wrong_en": "my mother with a heavier structure", "note": "亲属关系里常可省的", "note_en": "Family possession often allows omission"},
                    {"right": "白色的衬衫", "wrong": "白色衬衫（有时也能成立，但教材入门阶段先记完整）", "right_en": "a white shirt", "wrong_en": "white shirt without 的 in a simplified form", "note": "形容词短语修饰名词时常要的", "note_en": "Adjective-like modifiers often take 的 before nouns"},
                    {"right": "漂亮的地方", "wrong": "漂亮地方", "right_en": "a beautiful place", "wrong_en": "beautiful place without 的", "note": "描述性修饰先记的结构", "note_en": "Learn the descriptive 的 pattern first"},
                    {"right": "这是我的名片", "wrong": "这是我名片", "right_en": "This is my business card", "wrong_en": "this is my card without 的", "note": "正式场景更要稳", "note_en": "Formal contexts require more stability"},
                ],
            },
            {
                "kind": "correctness",
                "title": "看看、试试、休息休息：重叠不是重复，而是变柔和",
                "overview_zh": "动词重叠是中文口语特别有味道的一部分。它不是简单地说两遍，而是把语气变轻、变柔和、变得更像建议或尝试。",
                "overview_en": "Verb reduplication is one of the features that gives spoken Mandarin its special flavor. It is not just repetition. It softens the tone and makes the expression sound more like a suggestion or a trial.",
                "tip_zh": "如果你想让语气更轻一点、更像“试一下”，就可以考虑看看、试试、想想、问问这类结构。",
                "tip_en": "If you want to soften the tone and make it sound more like 'try it a bit', think of patterns such as 看看, 试试, 想想, and 问问.",
                "items": [
                    {"right": "你看看", "wrong": "你看看看", "right_en": "Have a look", "wrong_en": "an unnatural over-repetition", "note": "重叠有固定长度", "note_en": "Reduplication has a stable shape"},
                    {"right": "你试试", "wrong": "你试一下一下", "right_en": "Try it", "wrong_en": "an awkward double structure", "note": "试试本身已经有轻量感", "note_en": "试试 already carries a light trial meaning"},
                    {"right": "我们休息休息吧", "wrong": "我们休息吧休息吧", "right_en": "Let's rest a little", "wrong_en": "awkward repetition", "note": "重叠能让建议更柔和", "note_en": "Reduplication softens a suggestion"},
                    {"right": "你想想", "wrong": "你一直想", "right_en": "Think about it", "wrong_en": "keep thinking in a different meaning", "note": "想想更像短时尝试", "note_en": "想想 suggests a short reflective attempt"},
                    {"right": "我问问他", "wrong": "我问他问", "right_en": "I'll ask him", "wrong_en": "incorrect word order", "note": "问问是很自然的口语块", "note_en": "问问 is a very natural spoken chunk"},
                ],
            },
            {
                "kind": "correctness",
                "title": "松一松、慢一点儿、轻一点儿：口语里的柔化命令",
                "overview_zh": "很多时候，中文不是靠复杂语法来显得礼貌，而是靠这些小结构来把命令变柔和。你说得越细，听起来越像中文。",
                "overview_en": "In many situations, Mandarin sounds polite not through complex grammar, but through small softening structures. The more precisely you use them, the more natural your speech becomes.",
                "tip_zh": "当你想让别人放松一点、慢一点、小一点、轻一点，就可以直接把形容词带进这种结构里。",
                "tip_en": "When you want someone to relax a little, go slower, make it smaller, or lighter, you can bring the adjective directly into this softening pattern.",
                "items": [
                    {"right": "慢一点儿", "wrong": "慢", "right_en": "a little slower", "wrong_en": "slow, said too directly", "note": "一点儿能让语气更柔和", "note_en": "一点儿 softens the tone"},
                    {"right": "轻一点儿", "wrong": "轻", "right_en": "a little lighter / softer", "wrong_en": "light, said too directly", "note": "请求时很常见", "note_en": "Very common in requests"},
                    {"right": "放松一点儿", "wrong": "放松", "right_en": "relax a little", "wrong_en": "relax, said too directly", "note": "安慰时常这样说", "note_en": "This is common in reassurance"},
                    {"right": "松一松", "wrong": "松", "right_en": "loosen it a bit", "wrong_en": "loose", "note": "形容词也能在口语里活起来", "note_en": "Adjectives can act dynamically in spoken Chinese"},
                    {"right": "再想一想", "wrong": "再想", "right_en": "think about it again", "wrong_en": "think again without the softening shape", "note": "一想一想更像建议", "note_en": "The fuller shape sounds more suggestive"},
                ],
            },
        ],
    },
    {
        "number": "110",
        "slug": "10-directional-complements-and-daily-scenarios",
        "title": "Directional Complements in Daily Life",
        "cn_title": "趋向补语与生活场景表达",
        "subtitle": "把出来、下来、起来和现实对话连起来",
        "color": "#0A9396",
        "intro_zh": "很多学习者学了补语以后，觉得规则很抽象，到了真实说话时还是不会用。其实趋向补语最好的学法不是背定义，而是把它们放进真实场景里。",
        "intro_en": "Many learners study complements and still feel that the rules are abstract. In real speaking, they still cannot use them. The best way to learn directional complements is not to memorize definitions, but to put them into real-life situations.",
        "use_zh": "这本书会围绕最常见的几组表达：出来、下来、起来，以及上下左右、前后里外、打车、问厕所、点餐等真实生活场景，一步一步把补语练成熟口语。",
        "use_en": "This book focuses on the most common complement groups such as 出来, 下来, and 起来, together with real-life scenarios like directions, taxis, restrooms, and ordering food, so that complements become usable spoken Chinese.",
        "modules": [
            {
                "kind": "correctness",
                "title": "出来：做出来、看出来、听出来",
                "overview_zh": "出来不是只有一个意思。它可以表示“从里面出来”，也可以表示“结果出现了”“被识别出来了”。这就是为什么它在口语里特别常见。",
                "overview_en": "出来 does not have just one meaning. It can mean movement from the inside, but also that a result has emerged or that something has been recognized. This is why it is extremely common in spoken Mandarin.",
                "tip_zh": "先不要把出来理解得太窄。只要你感到“从不清楚到清楚”“从没有到有”，很多时候都可能用出来。",
                "tip_en": "Do not interpret 出来 too narrowly at first. Whenever you feel a movement from unclear to clear, or from absent to present, 出来 may be possible.",
                "items": [
                    {"right": "写出来", "wrong": "写出", "right_en": "write it out", "wrong_en": "write out in an incomplete learning stage form", "note": "结果成形时出来很自然", "note_en": "出来 is natural when a result takes shape"},
                    {"right": "想出来", "wrong": "想到出来", "right_en": "figure out", "wrong_en": "incorrect mixed form", "note": "思考后得到结果", "note_en": "A result is obtained after thinking"},
                    {"right": "看出来", "wrong": "看见出来", "right_en": "tell / recognize", "wrong_en": "incorrect mixed form", "note": "从观察中识别出来", "note_en": "Recognized through observation"},
                    {"right": "听出来", "wrong": "听见出来", "right_en": "recognize by hearing", "wrong_en": "incorrect mixed form", "note": "从声音里分辨出来", "note_en": "Recognized through sound"},
                    {"right": "洗出来", "wrong": "洗好照片出来（太绕）", "right_en": "develop the photo", "wrong_en": "an overlong workaround", "note": "固定搭配要整块记", "note_en": "Memorize the fixed chunk as a whole"},
                ],
            },
            {
                "kind": "correctness",
                "title": "下来：慢下来、停下来、安静下来",
                "overview_zh": "下来在很多场景里不是真的“向下移动”，而是在表示一种状态稳定下来、弱下来、慢下来。",
                "overview_en": "In many contexts, 下来 does not literally mean moving downward. Instead, it signals that a state settles down, weakens, or slows down.",
                "tip_zh": "如果你感觉一个动作从强变弱、从快变慢、从动变静，就可以优先想到下来。",
                "tip_en": "If you feel that an action changes from strong to weak, fast to slow, or active to still, think of 下来 first.",
                "items": [
                    {"right": "慢下来", "wrong": "慢起来（如果你想说 slow down）", "right_en": "slow down", "wrong_en": "become slow in the wrong direction", "note": "从快到慢常用下来", "note_en": "Moving from fast to slow often uses 下来"},
                    {"right": "停下来", "wrong": "停起来", "right_en": "stop", "wrong_en": "incorrect opposite direction form", "note": "从动到静是典型下来", "note_en": "From movement to stillness is a classic 下来 pattern"},
                    {"right": "安静下来", "wrong": "安静起来（如果你想说 calm down）", "right_en": "calm down", "wrong_en": "become lively in the wrong direction", "note": "情绪平稳时很常见", "note_en": "Very common when emotional state settles"},
                    {"right": "记下来", "wrong": "记出来（如果你想说 write it down and keep it）", "right_en": "write it down", "wrong_en": "recognize/produce it out when you mean record it", "note": "保存信息时常用下来", "note_en": "Use 下来 when the information is captured and kept"},
                    {"right": "留下来", "wrong": "留出来（如果你想说 stay behind）", "right_en": "stay behind / remain", "wrong_en": "leave out in the wrong sense", "note": "状态持续保留时很常见", "note_en": "Common when a state remains in place"},
                ],
            },
            {
                "kind": "correctness",
                "title": "起来：想起来、记起来、听起来",
                "overview_zh": "起来常常和“从无到有”的感觉有关，尤其是记忆被激活、感受被形成的时候。它和下来、出来形成很好的对比。",
                "overview_en": "起来 often relates to a sense of emergence, especially when memory is activated or when a perception takes shape. It forms a helpful contrast with 下来 and 出来.",
                "tip_zh": "如果你感觉一个想法、记忆、印象从脑子里“起来了”，那很多时候就是起来的范围。",
                "tip_en": "If you feel that an idea, memory, or impression 'comes up' in the mind, it often falls into the range of 起来.",
                "items": [
                    {"right": "想起来", "wrong": "想出来（如果你想说 remember rather than figure out）", "right_en": "remember", "wrong_en": "figure out when remember is intended", "note": "记忆被唤起时常用起来", "note_en": "Use 起来 when memory is activated"},
                    {"right": "记起来", "wrong": "记出来", "right_en": "remember", "wrong_en": "incorrect contrast form", "note": "回忆成功是起来", "note_en": "Successful recollection often takes 起来"},
                    {"right": "听起来", "wrong": "听出来（如果你想说 it sounds...) ", "right_en": "it sounds...", "wrong_en": "recognize by hearing when evaluation is intended", "note": "评价印象时常用起来", "note_en": "Use 起来 for impressions and evaluation"},
                    {"right": "看起来", "wrong": "看出来（如果你想说 it looks...) ", "right_en": "it looks...", "wrong_en": "recognize by seeing when appearance is intended", "note": "外观印象和识别不是一回事", "note_en": "Appearance is not the same as recognition"},
                    {"right": "站起来", "wrong": "站下来", "right_en": "stand up", "wrong_en": "stand down", "note": "真实方向移动也常用起来", "note_en": "Literal upward movement also uses 起来"},
                ],
            },
            {
                "kind": "correctness",
                "title": "上下左右、前后里外：方向词与补语放在一起练",
                "overview_zh": "很多学习者会单独背方向词，但一到真实口语，比如问厕所、坐电梯、让司机左转右转，就接不上了。方向词一定要和动作一起练。",
                "overview_en": "Many learners memorize direction words by themselves, but in real speech, such as asking for the restroom, taking the elevator, or telling a driver to turn left or right, they cannot connect the pieces. Direction words must be practiced together with actions.",
                "tip_zh": "你不要只背左、右、上、下，要背成整块：向左、向右、上去、下来、往里走、往外走。",
                "tip_en": "Do not memorize only left, right, up, and down. Memorize them as chunks: 向左, 向右, 上去, 下来, 往里走, and 往外走.",
                "items": [
                    {"right": "向左转", "wrong": "左转向", "right_en": "turn left", "wrong_en": "incorrect order", "note": "方向和动作顺序要稳", "note_en": "Keep direction and action in a stable order"},
                    {"right": "向右走", "wrong": "走右边向", "right_en": "walk to the right", "wrong_en": "incorrect order", "note": "真实问路里要说顺", "note_en": "Make it smooth for real-life asking directions"},
                    {"right": "往里走", "wrong": "走里", "right_en": "walk inside", "wrong_en": "walk inside with an incomplete structure", "note": "里外常和往连用", "note_en": "里 and 外 often go with 往"},
                    {"right": "往外走", "wrong": "外走", "right_en": "walk outside", "wrong_en": "incomplete form", "note": "场景表达要整块", "note_en": "Treat the phrase as a full chunk"},
                    {"right": "上三楼以后，厕所就在左边", "wrong": "上三楼左边厕所就在", "right_en": "After you go up to the third floor, the restroom is on the left", "wrong_en": "scrambled order", "note": "方向信息要分层", "note_en": "Direction information needs clear layering"},
                ],
            },
            {
                "kind": "correctness",
                "title": "打车、问厕所、点餐：把补语用进生活对话",
                "overview_zh": "补语真正有用的时候，不是在语法解释里，而是在你需要马上开口的时候。你要打车、问厕所、点餐、问路时，整块表达要随时能出来。",
                "overview_en": "Complements become truly useful not in grammar explanations, but when you need to speak immediately. In taxis, restrooms, food ordering, and asking directions, full chunks should come out instantly.",
                "tip_zh": "这一章的重点不是规则，而是整块表达。只要你把高频句子练熟，很多补语会在语感里自动稳定下来。",
                "tip_en": "The focus of this chapter is not rule explanation but full chunks. Once the high-frequency sentences become familiar, many complement patterns stabilize automatically inside your intuition.",
                "items": [
                    {"right": "不好意思，男厕所在哪儿", "wrong": "对不起，男厕所是谁", "right_en": "Excuse me, where is the men's restroom?", "wrong_en": "Sorry, who is the men's restroom?", "note": "真实场景先求能用", "note_en": "In real life, usability comes first"},
                    {"right": "师傅，麻烦你停下来", "wrong": "师傅，麻烦你停起来", "right_en": "Driver, please stop", "wrong_en": "please stop up", "note": "从开动到停止是下来", "note_en": "From movement to stopping uses 下来"},
                    {"right": "你能帮我写下来吗", "wrong": "你能帮我写起来吗", "right_en": "Can you write it down for me?", "wrong_en": "can you write it up for me", "note": "记录信息常用下来", "note_en": "Recording information often uses 下来"},
                    {"right": "我想起来了，火车站在前面", "wrong": "我想出来了，火车站在前面（如果你是突然记起来）", "right_en": "I remember now; the train station is ahead", "wrong_en": "I figured it out now when remember is intended", "note": "回忆和推理要分开", "note_en": "Separate recalling from figuring out"},
                    {"right": "这个菜听起来不错，我想试试", "wrong": "这个菜听出来不错", "right_en": "This dish sounds good; I want to try it", "wrong_en": "this dish is heard out good", "note": "印象判断更适合起来", "note_en": "Impression judgments fit 起来 better"},
                ],
            },
        ],
    },
]


def write_books() -> list[tuple[dict, Path, Path]]:
    ensure_dirs()
    outputs = []
    for book in BOOKS:
        md_path = MD_DIR / f"{book['slug']}.md"
        pdf_path = PDF_DIR / f"{book['slug']}.pdf"
        md_path.write_text(build_book(book), encoding="utf-8")
        outputs.append((book, md_path, pdf_path))
    return outputs


def compile_books(outputs: Iterable[tuple[dict, Path, Path]]) -> None:
    for book, md_path, pdf_path in outputs:
        cmd = [
            sys.executable,
            str(GENERATE),
            "textbook",
            "--md",
            str(md_path),
            "--number",
            book["number"],
            "--title",
            book["title"],
            "--subtitle",
            book["subtitle"],
            "--color",
            book["color"],
            "--out",
            str(pdf_path),
        ]
        subprocess.run(cmd, check=True, cwd=str(ROOT))


def main() -> None:
    outputs = write_books()
    compile_books(outputs)
    for book, md_path, pdf_path in outputs:
        print(f"OK {book['number']} {md_path}")
        print(f"OK {book['number']} {pdf_path}")


if __name__ == "__main__":
    main()
