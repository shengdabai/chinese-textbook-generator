#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from pypinyin import Style, pinyin


ROOT = Path(".")
DEST_ROOT = Path("../../output")
PLAN_PATH = DEST_ROOT / "BOOKS_71_TO_80_CONFIDENT_SPEAKING_PLAN.md"
GENERATE = ROOT / "generate.py"
PYTHON = ROOT / ".venv" / "bin" / "python"

def ensure_dirs() -> None:
    DEST_ROOT.mkdir(parents=True, exist_ok=True)


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
    safe_zh = sanitize_privacy_text(zh)
    safe_en = sanitize_privacy_text(en)
    return (
        f"**中文**：{safe_zh}\n\n"
        f"**拼音**：{auto_pinyin(safe_zh)}\n\n"
        f"**English**: {safe_en}\n"
    )


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def _generic_speaker_label(speaker: str, fallback_index: int) -> str:
    mapping = {
        "teacher": "老师",
        "doctor": "医生",
        "manager": "经理",
        "lead": "负责人",
        "driver": "司机",
        "server": "服务员",
        "clerk": "店员",
        "reception": "前台",
        "receptionist": "前台",
        "friend": "朋友",
        "caller": "来电方",
        "receiver": "接听方",
        "buyer": "顾客",
        "seller": "商家",
        "tourist": "游客",
        "local": "路人",
        "passenger": "乘客",
        "pharmacist": "药师",
        "patient": "患者",
        "colleague": "同事",
        "customer": "顾客",
    }
    key = speaker.strip().lower()
    if key in mapping:
        return mapping[key]
    if re.search(r"[\u4e00-\u9fff]", speaker):
        return speaker
    return f"人物{chr(64 + fallback_index)}"


def sanitize_privacy_text(text: str) -> str:
    demo_names = [
        "Lina", "Mark", "Sofia", "Mia", "Leo", "Emma", "Noah", "Amy",
        "Olivia", "Daniel", "Chris", "Iris", "Nina", "Grace", "Tom",
        "Kevin", "Maya", "Ella", "Ryan", "Anna", "Ava", "Ben", "Lucy",
        "Sam", "Mila", "June", "Helen",
    ]
    text = re.sub(r"我叫[^。！？，,]+", "我叫……", text)
    text = re.sub(r"My name is [^.!,?]+", "My name is ...", text)
    text = re.sub(r"Hello, this is [^.!,?]+", "Hello, this is ...", text, flags=re.IGNORECASE)
    text = text.replace("安娜", "……")
    for name in demo_names:
        text = re.sub(rf"\b{name}\b", "...", text)
    return text


def dialogue_table(turns: list[tuple[str, str, str]]) -> str:
    speaker_map: dict[str, str] = {}
    rows = []
    next_index = 1
    for speaker, zh, en in turns:
        if speaker not in speaker_map:
            speaker_map[speaker] = _generic_speaker_label(speaker, next_index)
            next_index += 1
        safe_zh = sanitize_privacy_text(zh)
        safe_en = sanitize_privacy_text(en)
        rows.append([speaker_map[speaker], safe_zh, auto_pinyin(safe_zh), safe_en])
    return md_table(["说话人", "中文", "拼音", "English"], rows)


def build_expression_rows(expressions: list[dict[str, str]]) -> list[list[str]]:
    rows = []
    for item in expressions:
        safe_zh = sanitize_privacy_text(item["zh"])
        safe_en = sanitize_privacy_text(item["en"])
        rows.append(
            [
                safe_zh,
                auto_pinyin(safe_zh),
                safe_en,
                item["note"],
            ]
        )
    return rows


def build_frame_rows(frames: list[dict[str, str]]) -> list[list[str]]:
    rows = []
    for item in frames:
        safe_zh = sanitize_privacy_text(item["zh"])
        safe_en = sanitize_privacy_text(item["en"])
        rows.append(
            [
                safe_zh,
                auto_pinyin(safe_zh),
                safe_en,
                item["usage"],
            ]
        )
    return rows


def build_mistake_rows(mistakes: list[dict[str, str]]) -> list[list[str]]:
    rows = []
    for item in mistakes:
        natural = sanitize_privacy_text(item["natural"])
        natural_en = sanitize_privacy_text(item["natural_en"])
        wrong = sanitize_privacy_text(item["wrong"])
        wrong_en = sanitize_privacy_text(item["wrong_en"])
        rows.append(
            [
                natural,
                auto_pinyin(natural),
                natural_en,
                wrong,
                auto_pinyin(wrong),
                wrong_en,
                item["note"],
            ]
        )
    return rows


def build_drills(chapter: dict) -> list[dict[str, str]]:
    expressions = chapter["expressions"]
    frames = chapter["frames"]
    mistakes = chapter["mistakes"]
    drills: list[dict[str, str]] = []

    for idx, expr in enumerate(expressions[:4], 1):
        drills.append(
            {
                "prompt": f"请用“{expr['zh']}”说一句完整的话，场景是：{chapter['scene_zh']}。",
                "task": "把核心表达放进完整句子里。",
                "answer": f"{expr['zh']}。{chapter['goal_zh'][:16]}。",
                "answer_en": f"Use '{expr['zh']}' in a full sentence for the target scene.",
            }
        )

    for frame in frames[:3]:
        sentence = frame["zh"].replace("……", expressions[0]["zh"])
        drills.append(
            {
                "prompt": f"请按句型说一句：{frame['zh']}",
                "task": "完成句型替换练习。",
                "answer": sentence,
                "answer_en": frame["en"],
            }
        )

    for item in mistakes[:3]:
        drills.append(
            {
                "prompt": f"把这句不太自然的话改好：{item['wrong']}",
                "task": "改成更自然的中文。",
                "answer": item["natural"],
                "answer_en": item["natural_en"],
            }
        )

    return drills


def build_roleplay_rows(chapter: dict) -> list[list[str]]:
    expressions = chapter["expressions"]
    frames = chapter["frames"]
    rows = []
    for idx in range(1, 7):
        expr = sanitize_privacy_text(expressions[(idx - 1) % len(expressions)]["zh"])
        frame = sanitize_privacy_text(frames[(idx - 1) % len(frames)]["zh"])
        rows.append(
            [
                str(idx),
                chapter["scene_zh"],
                f"至少用上“{expr}”和“{frame}”各一次。",
                "先说短句，再补充细节，最后加一句礼貌收尾。",
            ]
        )
    return rows


def build_reflection_rows(chapter: dict) -> list[list[str]]:
    prompts = chapter["reflection"]
    rows = []
    for idx, prompt in enumerate(prompts, 1):
        rows.append([str(idx), prompt, auto_pinyin(prompt), "录音后回听并检查语气、节奏和完整度。"])
    return rows


def build_dialogue_recap(turns: list[tuple[str, str, str]]) -> str:
    rows = []
    for idx, (_, zh, en) in enumerate(turns, 1):
        safe_zh = sanitize_privacy_text(zh)
        safe_en = sanitize_privacy_text(en)
        rows.append([str(idx), safe_zh, auto_pinyin(safe_zh), safe_en])
    return md_table(["顺序", "关键句", "拼音", "English"], rows)


def build_chapter_md(book: dict, chapter: dict, index: int) -> str:
    expressions = chapter["expressions"]
    frames = chapter["frames"]
    mistakes = chapter["mistakes"]
    dialogue = chapter["dialogue"]
    drills = build_drills(chapter)

    parts: list[str] = []
    parts.append(f"# Part {index}: {chapter['title_en']} — {chapter['title_zh']}\n\n")
    parts.append("## 学习目标 Learning Goal\n\n")
    parts.append(triad(chapter["goal_zh"], chapter["goal_en"]))
    parts.append("\n")
    parts.append(triad(chapter["confidence_tip_zh"], chapter["confidence_tip_en"]))
    parts.append("\n\n## 场景说明 Scene Brief\n\n")
    parts.append(triad(chapter["scene_zh"], chapter["scene_en"]))
    parts.append("\n\n## 核心表达 Expression Bank\n\n")
    parts.append(md_table(["中文", "拼音", "English", "使用提醒"], build_expression_rows(expressions)))
    parts.append("\n\n## 核心表达逐条拆解\n\n")
    for item in expressions:
        explain_zh = (
            f"在这个专题里，“{item['zh']}”是高频实用句。你不需要一次说很多，先把这一句说稳，说清楚，再接下一句就会更自然。"
        )
        explain_en = (
            f"In this topic, “{item['zh']}” is a high-frequency practical line. "
            f"You do not need to say too much at once. Say this line steadily and clearly first, and then add the next sentence."
        )
        example_zh = f"你可以这样练习：{item['zh']}。然后再补一句更具体的内容。"
        example_en = f"Practice it like this: {item['zh']}. Then add one more specific detail."
        parts.append(triad(explain_zh, explain_en))
        parts.append("\n\n")
        parts.append(triad(example_zh, example_en))
        parts.append("\n\n")

    parts.append("## 自信句型 Sentence Frames\n\n")
    parts.append(md_table(["句型", "拼音", "English", "适用场景"], build_frame_rows(frames)))
    parts.append("\n\n## 句型使用提示\n\n")
    for item in frames:
        zh = (
            f"句型“{item['zh']}”的价值在于给你一个安全的开头。哪怕后面只补三个到五个字，也已经是一句完整而自然的中文。"
        )
        en = (
            f"The pattern “{item['zh']}” gives you a safe beginning. "
            f"Even if you only add three to five characters after it, you already have a complete and natural Chinese sentence."
        )
        parts.append(triad(zh, en))
        parts.append("\n\n")

    parts.append("## 场景对话 Main Dialogue\n\n")
    parts.append(dialogue_table(dialogue))
    parts.append("\n\n## 对话复述 Dialogue Recap\n\n")
    parts.append(build_dialogue_recap(dialogue))
    parts.append("\n\n## 常见误区 Common Mistakes\n\n")
    parts.append(
        md_table(
            ["更自然的中文", "拼音", "English", "常见误说", "拼音", "English", "提醒"],
            build_mistake_rows(mistakes),
        )
    )
    parts.append("\n\n## 引导练习 Guided Practice\n\n")
    drill_rows = []
    answer_rows = []
    for idx, drill in enumerate(drills, 1):
        safe_prompt = sanitize_privacy_text(drill["prompt"])
        safe_answer = sanitize_privacy_text(drill["answer"])
        safe_answer_en = sanitize_privacy_text(drill["answer_en"])
        drill_rows.append([str(idx), safe_prompt, auto_pinyin(safe_prompt), drill["task"]])
        answer_rows.append([str(idx), safe_answer, auto_pinyin(safe_answer), safe_answer_en])
    parts.append(md_table(["题号", "中文", "拼音", "任务"], drill_rows))
    parts.append("\n\n## 参考答案 Model Answers\n\n")
    parts.append(md_table(["题号", "参考答案", "拼音", "English"], answer_rows))
    parts.append("\n\n## 角色扮演 Role Play Tasks\n\n")
    parts.append(md_table(["任务", "场景", "要求", "完成标准"], build_roleplay_rows(chapter)))
    parts.append("\n\n## 复盘问题 Reflection Prompts\n\n")
    parts.append(md_table(["题号", "问题", "拼音", "完成方式"], build_reflection_rows(chapter)))
    parts.append("\n\n")
    return "".join(parts)


def build_appendix(book: dict) -> str:
    vocab_rows = []
    for chapter in book["chapters"]:
        for item in chapter["expressions"][:6]:
            safe_zh = sanitize_privacy_text(item["zh"])
            safe_en = sanitize_privacy_text(item["en"])
            vocab_rows.append([safe_zh, auto_pinyin(safe_zh), safe_en, chapter["title_zh"]])

    challenge_rows = []
    for idx in range(1, 15):
        chapter = book["chapters"][(idx - 1) % len(book["chapters"])]
        challenge_rows.append(
            [
                str(idx),
                f"围绕“{chapter['title_zh']}”录一段 45 秒中文。",
                auto_pinyin(f"围绕“{chapter['title_zh']}”录一段 45 秒中文。"),
                "先说场景，再说需求，再加一句礼貌收尾。",
            ]
        )

    recap_rows = []
    for chapter in book["chapters"]:
        for idx, expr in enumerate(chapter["expressions"][:4], 1):
            recap_rows.append(
                [
                    f"{chapter['title_zh']}-{idx}",
                    sanitize_privacy_text(f"请围绕“{expr['zh']}”做 30 秒口头表达。"),
                    auto_pinyin(sanitize_privacy_text(f"请围绕“{expr['zh']}”做 30 秒口头表达。")),
                    sanitize_privacy_text(f"先说场景，再说核心句“{expr['zh']}”，最后补一个细节。"),
                ]
            )

    translation_rows = []
    for chapter in book["chapters"]:
        for item in chapter["expressions"][:5]:
            translation_rows.append(
                [
                    sanitize_privacy_text(item["en"]),
                    sanitize_privacy_text(item["zh"]),
                    auto_pinyin(sanitize_privacy_text(item["zh"])),
                    chapter["title_zh"],
                ]
            )

    parts = []
    parts.append("# Appendix A: 高频表达总表 High-Frequency Bank\n\n")
    parts.append(md_table(["中文", "拼音", "English", "所属章节"], vocab_rows))
    parts.append("\n\n# Appendix B: 14-Day Speaking Challenge\n\n")
    parts.append(md_table(["Day", "任务", "拼音", "目标"], challenge_rows))
    parts.append("\n\n# Appendix C: 30-Second Speaking Recap\n\n")
    parts.append(md_table(["编号", "任务", "拼音", "完成提示"], recap_rows))
    parts.append("\n\n# Appendix D: English-to-Chinese Quick Review\n\n")
    parts.append(md_table(["English Prompt", "中文", "拼音", "章节"], translation_rows))
    parts.append("\n\n# Appendix E: 自信表达检查表 Confidence Checklist\n\n")
    checklist = [
        "我有没有先把第一句说短、说清楚？",
        "我有没有把核心意思放在句子前半部分？",
        "我有没有在卡住时改用更简单的表达？",
        "我有没有加上礼貌收尾，比如谢谢、麻烦你了、好的？",
        "我有没有用上本书里至少三个固定句型？",
        "我有没有在录音回听时注意语速和停顿？",
    ]
    for item in checklist:
        parts.append(triad(item, "Use this question to audit your real speaking after each practice round."))
        parts.append("\n\n")
    return "".join(parts)


def build_book_md(book: dict) -> str:
    parts: list[str] = []
    parts.append(f"# Z Turns Chinese Book {book['number']}\n")
    parts.append(f"## {book['title']} — {book['subtitle']}\n\n")
    parts.append("**Author:** Tony Sheng\n")
    parts.append("**Website:** zturnsgo.com\n")
    parts.append("**Series:** Foreign Learners' Confident Chinese Expression\n")
    parts.append("**Format Focus:** 中文 + 拼音 + English\n\n")
    parts.append("---\n\n")
    parts.append("# 本书定位 Book Positioning\n\n")
    parts.append(triad(book["intro_zh"], book["intro_en"]))
    parts.append("\n")
    parts.append(triad(book["method_zh"], book["method_en"]))
    parts.append("\n")
    for idx, chapter in enumerate(book["chapters"], 1):
        parts.append(build_chapter_md(book, chapter, idx))
    parts.append(build_appendix(book))
    return "".join(parts)


def write_plan(books: list[dict]) -> None:
    lines = []
    lines.append("# Z Turns Chinese — Books 71-80 Plan\n")
    lines.append("## 外国学员自信中文表达专题练习系列\n\n")
    lines.append("**Date:** 2026-04-19  \n")
    lines.append("**Output Folder:** `output`  \n")
    lines.append("**Rendering Tool:** `v3-typst`\n\n")
    lines.append("### 专题目录\n\n")
    for book in books:
        lines.append(f"## Book {book['number']}: {book['title']}\n")
        lines.append(f"**中文副标题：** {book['subtitle']}\n\n")
        lines.append(f"{book['intro_zh']}\n\n")
        lines.append("**Chapters:**\n")
        for idx, chapter in enumerate(book["chapters"], 1):
            lines.append(f"{idx}. {chapter['title_zh']} / {chapter['title_en']}\n")
        lines.append("\n")
    PLAN_PATH.write_text("".join(lines), encoding="utf-8")


def pdf_pages(pdf_path: Path) -> int:
    result = subprocess.run(
        ["pdfinfo", str(pdf_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError(f"Could not read page count for {pdf_path}")


def compile_book(book: dict, md_path: Path, pdf_path: Path) -> None:
    cmd = [
        str(PYTHON),
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


BOOKS = [
    {
        "number": "71",
        "slug": "FirstConnections",
        "title": "Confident Chinese: First Connections",
        "subtitle": "自我介绍与破冰表达",
        "color": "#1E88E5",
        "intro_zh": "这本书围绕外国学员最常遇到的第一类场景展开：第一次见面、简单介绍自己、继续把话题聊下去。很多人不是不会说，而是不敢先开口，所以本书特别强调短句起步、稳住节奏和自然续聊。",
        "intro_en": "This book focuses on the first situations foreign learners meet most often: first meetings, simple self-introduction, and keeping the conversation going. Many learners are not unable to speak; they simply hesitate to start. That is why this book emphasizes short openings, steady rhythm, and natural follow-up.",
        "method_zh": "每一章都用核心表达、句型框架、场景对话、误区改写和角色扮演，帮助学员从会背句子走向能自信说出口。",
        "method_en": "Each chapter uses key expressions, sentence frames, scene dialogues, mistake correction, and role-play so learners can move from memorizing lines to saying them with confidence.",
        "chapters": [
            {
                "title_zh": "第一次见面先开口",
                "title_en": "Start the Conversation",
                "goal_zh": "学会在第一次见面时自然问候、说名字、说自己来自哪里，并顺利把对话打开。",
                "goal_en": "Learn to greet naturally in a first meeting, say your name, say where you are from, and open the conversation smoothly.",
                "confidence_tip_zh": "第一句话越简单越好。先把声音放稳，再去追求更多内容。",
                "confidence_tip_en": "The first line should be as simple as possible. Stabilize your voice first and then add more content.",
                "scene_zh": "你第一次在活动、课堂或朋友聚会上认识新朋友。",
                "scene_en": "You are meeting a new person for the first time at an event, in class, or at a gathering.",
                "expressions": [
                    {"zh": "你好，很高兴认识你。", "en": "Hello, nice to meet you.", "note": "标准开场句，安全又自然。"},
                    {"zh": "我叫安娜。", "en": "My name is Anna.", "note": "自我介绍先说名字。"},
                    {"zh": "我来自加拿大。", "en": "I'm from Canada.", "note": "来自 + 国家/城市。"},
                    {"zh": "这是我第一次来上海。", "en": "This is my first time in Shanghai.", "note": "很适合继续展开话题。"},
                    {"zh": "你的中文说得很好。", "en": "Your Chinese is very good.", "note": "友好夸奖，容易带来后续聊天。"},
                    {"zh": "你也是在这边工作吗？", "en": "Do you also work here?", "note": "自然过渡到背景问题。"},
                    {"zh": "我还在学中文。", "en": "I'm still learning Chinese.", "note": "减轻压力，也能争取对方放慢速度。"},
                    {"zh": "以后请多关照。", "en": "Please take care of me going forward.", "note": "礼貌收尾，很有中文感觉。"},
                ],
                "frames": [
                    {"zh": "我叫……，来自……。", "en": "My name is ..., and I'm from ....", "usage": "第一次自我介绍。"},
                    {"zh": "这是我第一次……。", "en": "This is my first time ....", "usage": "介绍新经历。"},
                    {"zh": "我现在在……。", "en": "Right now I am ....", "usage": "说明目前的学习或工作状态。"},
                    {"zh": "你也是……吗？", "en": "Do you also ...?", "usage": "把话题转到对方身上。"},
                    {"zh": "以后请多关照。", "en": "Please take care of me in the future.", "usage": "礼貌结束开场。"},
                ],
                "dialogue": [
                    ("Lina", "你好，很高兴认识你。", "Hi, nice to meet you."),
                    ("Mark", "你好，我也很高兴认识你。", "Hi, I'm happy to meet you too."),
                    ("Lina", "我叫Lina，来自加拿大。", "My name is Lina, and I'm from Canada."),
                    ("Mark", "我叫Mark，我来自英国。", "My name is Mark, and I'm from the UK."),
                    ("Lina", "这是我第一次来上海。", "This is my first time in Shanghai."),
                    ("Mark", "真的吗？你觉得上海怎么样？", "Really? What do you think of Shanghai?"),
                    ("Lina", "我觉得很方便，也很有活力。", "I think it's very convenient and full of energy."),
                    ("Mark", "你也是在这边工作吗？", "Do you also work here?"),
                    ("Lina", "我现在在这边学中文，也做一点设计工作。", "I'm studying Chinese here now, and I also do some design work."),
                    ("Mark", "太好了，以后请多关照。", "That's great. Please take care of me going forward."),
                ],
                "mistakes": [
                    {"natural": "你好，很高兴认识你。", "natural_en": "Hello, nice to meet you.", "wrong": "你好，我很高兴看见你。", "wrong_en": "Hello, I'm happy to see you.", "note": "认识你更符合初次见面的中文习惯。"},
                    {"natural": "我来自加拿大。", "natural_en": "I'm from Canada.", "wrong": "我是从加拿大。", "wrong_en": "I am from Canada in an awkward way.", "note": "来自更稳定。"},
                    {"natural": "我还在学中文。", "natural_en": "I'm still learning Chinese.", "wrong": "我还学习中文。", "wrong_en": "I still study Chinese.", "note": "口语里更常说在学。"},
                    {"natural": "你也是在这边工作吗？", "natural_en": "Do you also work here?", "wrong": "你也工作在这里吗？", "wrong_en": "Do you also work at here?", "note": "在这边工作更顺。"},
                    {"natural": "以后请多关照。", "natural_en": "Please take care of me going forward.", "wrong": "未来请照顾我。", "wrong_en": "Please take care of me in the future.", "note": "固定礼貌表达更自然。"},
                ],
                "reflection": [
                    "请用三句话介绍自己：名字、国家、现在在做什么。",
                    "请录一段初次见面自我介绍，控制在二十秒以内。",
                    "如果对方也来自国外，你会怎么继续问下去？",
                    "你最常卡住的是第一句还是第二句？为什么？",
                ],
            },
            {
                "title_zh": "介绍背景和来中国的原因",
                "title_en": "Share Your Background",
                "goal_zh": "学会介绍职业、学习背景、来中国的原因，以及目前最想提高的中文能力。",
                "goal_en": "Learn to talk about your work, study background, reasons for coming to China, and the Chinese skill you most want to improve right now.",
                "confidence_tip_zh": "讲背景时不要追求完整简历。先说最核心的两三点，听的人更容易跟上。",
                "confidence_tip_en": "When talking about your background, do not aim for a complete resume. State the two or three key points first so the listener can follow easily.",
                "scene_zh": "你在课堂、交换活动或工作社交场合进一步介绍自己。",
                "scene_en": "You are introducing yourself in more detail in class, at an exchange event, or in a work-related social setting.",
                "expressions": [
                    {"zh": "我以前在美国做市场。", "en": "I used to work in marketing in the U.S.", "note": "说明过去经历。"},
                    {"zh": "我现在在北京读硕士。", "en": "I'm doing a master's degree in Beijing now.", "note": "说明现在的主线。"},
                    {"zh": "我来中国是因为我对这里的文化很感兴趣。", "en": "I came to China because I am very interested in the culture here.", "note": "表达来中国的理由。"},
                    {"zh": "我想提高口语和听力。", "en": "I want to improve my speaking and listening.", "note": "清楚表达学习目标。"},
                    {"zh": "我平时也喜欢跟中国朋友聊天。", "en": "I also like chatting with Chinese friends in daily life.", "note": "补充个人学习方式。"},
                    {"zh": "我希望以后能用中文工作。", "en": "I hope I can work in Chinese in the future.", "note": "表达长期目标。"},
                    {"zh": "我最怕的就是不敢开口。", "en": "What I fear most is not daring to speak.", "note": "诚实表达困难。"},
                    {"zh": "所以我现在每天都练一点。", "en": "So now I practice a little every day.", "note": "用所以自然收束。"},
                ],
                "frames": [
                    {"zh": "我以前在……，现在在……。", "en": "I used to be in ..., and now I am in ....", "usage": "对比过去和现在。"},
                    {"zh": "我来中国是因为……。", "en": "I came to China because ....", "usage": "说明原因。"},
                    {"zh": "我最想提高的是……。", "en": "What I most want to improve is ....", "usage": "说学习目标。"},
                    {"zh": "我平时会通过……来练习。", "en": "I usually practice through ....", "usage": "介绍方法。"},
                    {"zh": "所以我现在……。", "en": "So now I ....", "usage": "做自然总结。"},
                ],
                "dialogue": [
                    ("Teacher", "你可以再介绍一下你的背景吗？", "Could you introduce your background a bit more?"),
                    ("Sofia", "可以。我以前在美国做市场，现在在北京读硕士。", "Sure. I used to work in marketing in the U.S., and now I'm doing a master's degree in Beijing."),
                    ("Teacher", "你为什么来中国？", "Why did you come to China?"),
                    ("Sofia", "我来中国是因为我对这里的文化很感兴趣。", "I came to China because I am very interested in the culture here."),
                    ("Teacher", "你现在最想提高什么？", "What do you want to improve most now?"),
                    ("Sofia", "我最想提高口语和听力。", "I most want to improve my speaking and listening."),
                    ("Teacher", "你平时怎么练习？", "How do you usually practice?"),
                    ("Sofia", "我平时会跟中国朋友聊天，也会跟读播客。", "I usually chat with Chinese friends, and I shadow podcasts as well."),
                    ("Teacher", "听起来很不错。", "That sounds great."),
                    ("Sofia", "我最怕的就是不敢开口，所以我现在每天都练一点。", "What I fear most is not daring to speak, so now I practice a little every day."),
                ],
                "mistakes": [
                    {"natural": "我以前在美国做市场。", "natural_en": "I used to work in marketing in the U.S.", "wrong": "我以前在美国是市场。", "wrong_en": "I used to be marketing in the U.S.", "note": "做 + 工作更自然。"},
                    {"natural": "我来中国是因为……", "natural_en": "I came to China because ...", "wrong": "我来中国为了……", "wrong_en": "I came to China for ... in a stiff way.", "note": "说理由时因为更常见。"},
                    {"natural": "我最想提高口语。", "natural_en": "I most want to improve my speaking.", "wrong": "我最想上升口语。", "wrong_en": "I most want to raise my speaking.", "note": "提高比上升自然。"},
                    {"natural": "我平时会跟中国朋友聊天。", "natural_en": "I usually chat with Chinese friends.", "wrong": "我平时和中国朋友说话。", "wrong_en": "I speak words with Chinese friends.", "note": "聊天更像自然口语活动。"},
                    {"natural": "所以我现在每天都练一点。", "natural_en": "So now I practice a little every day.", "wrong": "所以我现在每天练一点点是。", "wrong_en": "So now every day practice a little is.", "note": "句尾不要多余收尾。"},
                ],
                "reflection": [
                    "请用四句话介绍你的过去、现在、来中国的原因和学习目标。",
                    "你最常用哪一种方式练中文？请录音说明。",
                    "如果别人问你为什么学中文，你会怎么回答得更自然？",
                    "你能不能把“我最怕的就是……”换成自己的真实困难？",
                ],
            },
            {
                "title_zh": "把话题聊下去并交换联系方式",
                "title_en": "Keep the Chat Going",
                "goal_zh": "学会继续追问、回应共同兴趣、提出下次见面，并自然地交换微信或联系方式。",
                "goal_en": "Learn to ask follow-up questions, respond to shared interests, suggest meeting again, and exchange WeChat or other contact information naturally.",
                "confidence_tip_zh": "续聊不一定要很精彩，只要围绕一个共同点多问一步，就已经成功了。",
                "confidence_tip_en": "A follow-up conversation does not have to be brilliant. If you ask one more question around a shared point, you are already succeeding.",
                "scene_zh": "你和刚认识的人聊得不错，想把话题继续下去并保持联系。",
                "scene_en": "You are having a good chat with someone you just met and want to continue the conversation and stay in touch.",
                "expressions": [
                    {"zh": "你平时喜欢做什么？", "en": "What do you usually like to do?", "note": "常用续聊问题。"},
                    {"zh": "我也很喜欢这个。", "en": "I like that too.", "note": "找到共同点。"},
                    {"zh": "听起来很有意思。", "en": "That sounds very interesting.", "note": "给出积极反馈。"},
                    {"zh": "有机会我们可以一起去。", "en": "If there's a chance, we can go together.", "note": "自然提出下次活动。"},
                    {"zh": "你方便加个微信吗？", "en": "Would it be convenient to add WeChat?", "note": "礼貌地交换联系方式。"},
                    {"zh": "我扫你，还是你扫我？", "en": "Should I scan you, or will you scan me?", "note": "非常实用的微信表达。"},
                    {"zh": "以后有活动可以一起参加。", "en": "We can join activities together in the future.", "note": "为后续见面埋下伏笔。"},
                    {"zh": "今天认识你很开心。", "en": "I'm very happy to have met you today.", "note": "自然收尾。"},
                ],
                "frames": [
                    {"zh": "你平时喜欢……吗？", "en": "Do you usually like ...?", "usage": "问兴趣爱好。"},
                    {"zh": "我也很喜欢……。", "en": "I also really like ....", "usage": "回应共同点。"},
                    {"zh": "有机会我们可以一起……。", "en": "If there is a chance, we can ... together.", "usage": "提出下次见面。"},
                    {"zh": "你方便……吗？", "en": "Would it be convenient for you to ...?", "usage": "礼貌发出请求。"},
                    {"zh": "今天认识你很开心。", "en": "I'm glad to have met you today.", "usage": "结束聊天。"},
                ],
                "dialogue": [
                    ("Mia", "你平时喜欢做什么？", "What do you usually like to do?"),
                    ("Leo", "我平时喜欢爬山，也喜欢喝咖啡。", "I usually like hiking, and I also like coffee."),
                    ("Mia", "真的啊？我也很喜欢爬山。", "Really? I like hiking too."),
                    ("Leo", "那太好了。你一般去哪里？", "That's great. Where do you usually go?"),
                    ("Mia", "我最近常去香山，听起来你应该也会喜欢。", "I've been going to Fragrant Hills recently. It sounds like you'd like it too."),
                    ("Leo", "听起来很有意思。", "That sounds interesting."),
                    ("Mia", "有机会我们可以一起去。", "If there's a chance, we can go together."),
                    ("Leo", "好啊。你方便加个微信吗？", "Sure. Would it be convenient to add WeChat?"),
                    ("Mia", "可以，我扫你，还是你扫我？", "Sure. Should I scan you, or will you scan me?"),
                    ("Leo", "你扫我吧。今天认识你很开心。", "You scan me. I'm very happy to have met you today."),
                ],
                "mistakes": [
                    {"natural": "你平时喜欢做什么？", "natural_en": "What do you usually like to do?", "wrong": "你通常喜欢什么做？", "wrong_en": "What do you usually like to do in awkward order?", "note": "做什么是固定搭配。"},
                    {"natural": "我也很喜欢这个。", "natural_en": "I like this too.", "wrong": "我也非常like这个。", "wrong_en": "I also very like this.", "note": "尽量不用中英硬混。"},
                    {"natural": "有机会我们可以一起去。", "natural_en": "If there's a chance, we can go together.", "wrong": "未来我们可能一起去。", "wrong_en": "In the future we maybe go together.", "note": "有机会更自然。"},
                    {"natural": "你方便加个微信吗？", "natural_en": "Would it be convenient to add WeChat?", "wrong": "你给我你的微信。", "wrong_en": "Give me your WeChat.", "note": "加个微信更礼貌。"},
                    {"natural": "我扫你，还是你扫我？", "natural_en": "Should I scan you, or will you scan me?", "wrong": "我扫描你还是你扫描我？", "wrong_en": "Should I scan you or should you scan me?", "note": "口语里更常说扫。"},
                ],
                "reflection": [
                    "请录一段三十秒的聊天续接，主题是咖啡、运动或旅行。",
                    "你会怎么礼貌地提出“有机会一起去”？",
                    "你最习惯用哪个问题继续聊天？为什么？",
                    "请练习一次加微信的完整收尾。",
                ],
            },
        ],
    },
    {
        "number": "72",
        "slug": "FoodAndPreferences",
        "title": "Confident Chinese: Food and Preferences",
        "subtitle": "点餐与口味表达",
        "color": "#FB8C00",
        "intro_zh": "很多外国学员会背菜名，却不会自然表达自己的口味要求。这个专题把点咖啡、点正餐、反馈味道和买单串起来，让学员在餐饮场景里说得更清楚、更主动。",
        "intro_en": "Many foreign learners can memorize dish names, but they cannot naturally express their preferences. This volume connects ordering drinks, ordering a meal, giving taste feedback, and paying the bill so learners can speak more clearly and proactively in food-related situations.",
        "method_zh": "本书强调“我想要什么”“我不要什么”“我觉得怎么样”三类句子，让学员能从被动回答转到主动表达。",
        "method_en": "This book emphasizes three kinds of sentences: what I want, what I do not want, and how I feel about it. The goal is to move learners from passive response to active expression.",
        "chapters": [
            {
                "title_zh": "咖啡和饮料这样点",
                "title_en": "Order Drinks Clearly",
                "goal_zh": "学会点咖啡、奶茶和其他饮料，并清楚表达冷热、甜度、大小和打包需求。",
                "goal_en": "Learn to order coffee, milk tea, and other drinks while clearly expressing temperature, sweetness, size, and takeout needs.",
                "confidence_tip_zh": "点单最重要的是顺序清楚。先说饮料，再说要求，最后说打包或堂食。",
                "confidence_tip_en": "The key to ordering is clear order: say the drink first, then your preferences, and finally whether it is for here or to go.",
                "scene_zh": "你在咖啡店、奶茶店或便利店柜台点饮料。",
                "scene_en": "You are ordering a drink at a cafe, bubble tea shop, or convenience-store counter.",
                "expressions": [
                    {"zh": "我要一杯热拿铁。", "en": "I'd like a hot latte.", "note": "先说品类和温度。"},
                    {"zh": "少糖，不加冰。", "en": "Less sugar, no ice.", "note": "口味要求最常见。"},
                    {"zh": "中杯就可以。", "en": "A medium is fine.", "note": "简洁回应大小问题。"},
                    {"zh": "请帮我打包。", "en": "Please make it to go.", "note": "打包很实用。"},
                    {"zh": "我现在喝，堂食。", "en": "I'm drinking it now, for here.", "note": "对应堂食场景。"},
                    {"zh": "可以换成燕麦奶吗？", "en": "Can I change it to oat milk?", "note": "换配料时很好用。"},
                    {"zh": "一共多少钱？", "en": "How much is it in total?", "note": "付款前确认。"},
                    {"zh": "我用微信支付。", "en": "I'll pay with WeChat.", "note": "中国高频付款句。"},
                ],
                "frames": [
                    {"zh": "我要一杯……。", "en": "I'd like a cup of ....", "usage": "开口点单。"},
                    {"zh": "……，不要……。", "en": "... and don't want ....", "usage": "加偏好要求。"},
                    {"zh": "可以换成……吗？", "en": "Can it be changed to ...?", "usage": "询问替换。"},
                    {"zh": "请帮我……。", "en": "Please help me ....", "usage": "礼貌请求。"},
                    {"zh": "我用……支付。", "en": "I'll pay with ....", "usage": "说明支付方式。"},
                ],
                "dialogue": [
                    ("Clerk", "你好，请问想喝点什么？", "Hello, what would you like to drink?"),
                    ("Emma", "我要一杯热拿铁。", "I'd like a hot latte."),
                    ("Clerk", "好的，要大杯还是中杯？", "Sure. Large or medium?"),
                    ("Emma", "中杯就可以。", "A medium is fine."),
                    ("Clerk", "糖和冰需要调整吗？", "Would you like to adjust the sugar or ice?"),
                    ("Emma", "少糖，不加冰。", "Less sugar, no ice."),
                    ("Clerk", "需要换成燕麦奶吗？", "Would you like to change it to oat milk?"),
                    ("Emma", "可以换成燕麦奶吗？", "Can I change it to oat milk?"),
                    ("Clerk", "可以的，一共三十二块。", "Yes, that will be 32 yuan in total."),
                    ("Emma", "好，我用微信支付，请帮我打包。", "Okay, I'll pay with WeChat. Please make it to go."),
                ],
                "mistakes": [
                    {"natural": "我要一杯热拿铁。", "natural_en": "I'd like a hot latte.", "wrong": "我想一杯热拿铁。", "wrong_en": "I want a hot latte with missing verb.", "note": "要一杯更完整。"},
                    {"natural": "少糖，不加冰。", "natural_en": "Less sugar, no ice.", "wrong": "糖少，冰没有。", "wrong_en": "Sugar little, ice no.", "note": "固定店铺表达更自然。"},
                    {"natural": "中杯就可以。", "natural_en": "A medium is fine.", "wrong": "中的杯。", "wrong_en": "Middle cup.", "note": "中杯是固定说法。"},
                    {"natural": "请帮我打包。", "natural_en": "Please make it to go.", "wrong": "请包它。", "wrong_en": "Please pack it.", "note": "打包更像店铺口语。"},
                    {"natural": "我用微信支付。", "natural_en": "I'll pay with WeChat.", "wrong": "我微信付。", "wrong_en": "I WeChat pay.", "note": "完整说法更稳。"},
                ],
                "reflection": [
                    "请录一段完整饮料点单，从饮料到付款一口气说出来。",
                    "你最常喝什么？请用本章句型表达。",
                    "如果店员问你要不要换牛奶，你会怎么回应？",
                    "练习一次堂食版本，再练习一次打包版本。",
                ],
            },
            {
                "title_zh": "在餐厅点菜和改要求",
                "title_en": "Order Food Naturally",
                "goal_zh": "学会看菜单、点菜、问推荐、改辣度和说明忌口，在餐厅里自然表达自己的需求。",
                "goal_en": "Learn to read a menu, order dishes, ask for recommendations, adjust spice level, and explain dietary restrictions naturally in a restaurant.",
                "confidence_tip_zh": "你不用一次把所有菜都说完。可以先说一两个，再补充口味要求。",
                "confidence_tip_en": "You do not need to say every dish all at once. Order one or two items first, and then add your taste preferences.",
                "scene_zh": "你在中餐馆和服务员点菜、确认份量，并表达自己的饮食偏好。",
                "scene_en": "You are ordering with a server in a Chinese restaurant, confirming portions, and expressing dietary preferences.",
                "expressions": [
                    {"zh": "我们先点这几个菜。", "en": "We'll start with these dishes.", "note": "避免一次太长。"},
                    {"zh": "你们这边有什么推荐？", "en": "What do you recommend here?", "note": "问推荐很自然。"},
                    {"zh": "这个可以不要太辣吗？", "en": "Can this be not too spicy?", "note": "改辣度很常见。"},
                    {"zh": "我不吃牛肉。", "en": "I don't eat beef.", "note": "直接说明忌口。"},
                    {"zh": "这个是一份还是两个人吃？", "en": "Is this one portion or for two people?", "note": "问份量。"},
                    {"zh": "再来一碗米饭。", "en": "One more bowl of rice.", "note": "补单表达。"},
                    {"zh": "我们先这样。", "en": "We'll do this for now.", "note": "点单收尾很实用。"},
                    {"zh": "麻烦你帮我们确认一下。", "en": "Please help us confirm it.", "note": "礼貌复核订单。"},
                ],
                "frames": [
                    {"zh": "我们先点……。", "en": "We'll order ... first.", "usage": "开始点菜。"},
                    {"zh": "这个可以不要……吗？", "en": "Can this be without ...?", "usage": "改要求。"},
                    {"zh": "我不吃……。", "en": "I don't eat ....", "usage": "表达忌口。"},
                    {"zh": "再来……。", "en": "One more ....", "usage": "追加点单。"},
                    {"zh": "我们先这样。", "en": "We'll keep it like this for now.", "usage": "结束点单。"},
                ],
                "dialogue": [
                    ("Server", "两位，请问现在点菜吗？", "Two guests. Are you ready to order?"),
                    ("Noah", "可以。我们先点这几个菜。", "Yes. We'll start with these dishes."),
                    ("Server", "好的，需要我推荐一下吗？", "Sure. Would you like some recommendations?"),
                    ("Noah", "你们这边有什么推荐？", "What do you recommend here?"),
                    ("Server", "这个鱼很受欢迎，不过会有一点辣。", "This fish is very popular, but it's a little spicy."),
                    ("Noah", "这个可以不要太辣吗？", "Can this be not too spicy?"),
                    ("Server", "可以的。还有其他要求吗？", "Yes. Any other requests?"),
                    ("Noah", "我朋友不吃牛肉，这个是一份还是两个人吃？", "My friend doesn't eat beef. Is this one portion or for two people?"),
                    ("Server", "两个人吃差不多。", "It's about right for two people."),
                    ("Noah", "好，那再来一碗米饭，我们先这样。", "Okay, then one more bowl of rice. We'll keep it like this for now."),
                ],
                "mistakes": [
                    {"natural": "你们这边有什么推荐？", "natural_en": "What do you recommend here?", "wrong": "你推荐什么给我？", "wrong_en": "What recommend to me?", "note": "完整口语结构更自然。"},
                    {"natural": "这个可以不要太辣吗？", "natural_en": "Can this be not too spicy?", "wrong": "这个不辣太多可以吗？", "wrong_en": "Can this not spicy too much?", "note": "不要太辣最稳。"},
                    {"natural": "我不吃牛肉。", "natural_en": "I don't eat beef.", "wrong": "我没有吃牛肉。", "wrong_en": "I didn't eat beef.", "note": "表达习惯或忌口用不吃。"},
                    {"natural": "再来一碗米饭。", "natural_en": "One more bowl of rice.", "wrong": "再一个米饭。", "wrong_en": "One more rice.", "note": "要带量词。"},
                    {"natural": "我们先这样。", "natural_en": "We'll do this for now.", "wrong": "我们完成。", "wrong_en": "We finish.", "note": "先这样很地道。"},
                ],
                "reflection": [
                    "请录一段两人点菜的对话，至少加一个口味要求。",
                    "你最常需要表达哪一种忌口？请用中文说出来。",
                    "如果服务员推荐太辣的菜，你会怎么改要求？",
                    "练习一次点菜收尾：我们先这样。",
                ],
            },
            {
                "title_zh": "评价味道、买单和礼貌反馈",
                "title_en": "Give Feedback and Pay",
                "goal_zh": "学会评价味道、补充需求、要求买单并礼貌反馈用餐体验。",
                "goal_en": "Learn to comment on taste, add small requests, ask for the bill, and give polite feedback about the meal.",
                "confidence_tip_zh": "反馈不一定要很复杂。两个重点就够了：你觉得怎么样、你接下来要什么。",
                "confidence_tip_en": "Feedback does not need to be complicated. Two points are enough: how you feel about it and what you want next.",
                "scene_zh": "你已经开始吃饭，需要表达感受、再加点东西，最后买单离开。",
                "scene_en": "You have already started eating and need to express how it tastes, add something else, and finally ask for the bill before leaving.",
                "expressions": [
                    {"zh": "这个味道很好。", "en": "This tastes very good.", "note": "最安全的好评。"},
                    {"zh": "这个有点咸。", "en": "This is a little salty.", "note": "礼貌反馈问题。"},
                    {"zh": "可以再给我们一点热水吗？", "en": "Could you give us a bit more hot water?", "note": "加需求。"},
                    {"zh": "麻烦帮我们打包一下。", "en": "Please help us pack this up.", "note": "剩菜打包。"},
                    {"zh": "我们想买单。", "en": "We'd like to pay the bill.", "note": "餐厅高频句。"},
                    {"zh": "可以分开付吗？", "en": "Can we pay separately?", "note": "AA表达。"},
                    {"zh": "今天吃得很开心。", "en": "We ate very happily today.", "note": "礼貌结束。"},
                    {"zh": "下次我还想再来。", "en": "I'd like to come again next time.", "note": "很自然的正面反馈。"},
                ],
                "frames": [
                    {"zh": "这个有点……。", "en": "This is a little ....", "usage": "礼貌评价。"},
                    {"zh": "可以再……吗？", "en": "Could you ... again?", "usage": "追加请求。"},
                    {"zh": "麻烦帮我们……。", "en": "Please help us ....", "usage": "礼貌求助。"},
                    {"zh": "我们想……。", "en": "We would like to ....", "usage": "说接下来的动作。"},
                    {"zh": "下次我还想……。", "en": "Next time I would still like to ....", "usage": "给正面反馈。"},
                ],
                "dialogue": [
                    ("Amy", "这个味道很好，不过这个菜有点咸。", "This tastes very good, but this dish is a little salty."),
                    ("Server", "好的，我可以帮你们换一盘。", "Okay, I can help you change it."),
                    ("Amy", "不用了，可以再给我们一点热水吗？", "No need. Could you give us a bit more hot water?"),
                    ("Server", "可以，马上来。", "Sure, right away."),
                    ("Amy", "谢谢。对了，这个可以打包吗？", "Thanks. By the way, can this be packed up?"),
                    ("Server", "可以的。", "Yes, of course."),
                    ("Amy", "那麻烦帮我们打包一下，我们想买单。", "Then please help us pack it up. We'd like to pay the bill."),
                    ("Server", "好的，可以一起付，也可以分开付。", "Sure. You can pay together or separately."),
                    ("Amy", "那我们分开付吧。今天吃得很开心。", "Then let's pay separately. We ate very happily today."),
                    ("Server", "谢谢，欢迎下次再来。", "Thank you. Welcome back next time."),
                ],
                "mistakes": [
                    {"natural": "这个有点咸。", "natural_en": "This is a little salty.", "wrong": "这个太咸一点。", "wrong_en": "This too salty a little.", "note": "有点咸更自然。"},
                    {"natural": "可以再给我们一点热水吗？", "natural_en": "Could you give us a bit more hot water?", "wrong": "你给我热水再。", "wrong_en": "Give me hot water again.", "note": "礼貌问句更合适。"},
                    {"natural": "麻烦帮我们打包一下。", "natural_en": "Please help us pack it up.", "wrong": "帮我包这个。", "wrong_en": "Help me pack this.", "note": "麻烦+一下更柔和。"},
                    {"natural": "我们想买单。", "natural_en": "We'd like to pay.", "wrong": "我们要付钱现在。", "wrong_en": "We want to pay money now.", "note": "买单是更自然的餐厅说法。"},
                    {"natural": "今天吃得很开心。", "natural_en": "We ate very happily today.", "wrong": "今天我们开心吃。", "wrong_en": "Today we happy eat.", "note": "吃得很开心是成句表达。"},
                ],
                "reflection": [
                    "请练习一次从反馈味道到买单的完整表达。",
                    "如果菜有点辣而不是咸，你会怎么说？",
                    "你更常用一起付还是分开付？请录音表达。",
                    "练习一句自然的离店反馈。",
                ],
            },
        ],
    },
    {
        "number": "73",
        "slug": "ShoppingAndChoices",
        "title": "Confident Chinese: Shopping and Choices",
        "subtitle": "购物、比较与砍价表达",
        "color": "#43A047",
        "intro_zh": "购物场景不是只会问价格就够了。外国学员还需要会比较、会说明尺寸、会表达犹豫，也会礼貌地砍一点价。",
        "intro_en": "Shopping is not just about asking the price. Foreign learners also need to compare options, talk about size, express hesitation, and bargain a little politely.",
        "method_zh": "本书从问价开始，延伸到试穿、比较和售后，让学员在购买决策里有更主动的表达能力。",
        "method_en": "This book starts with asking the price and expands to trying things on, comparing options, and after-sales issues so learners can speak more actively through the whole buying decision.",
        "chapters": [
            {
                "title_zh": "问价格和看商品",
                "title_en": "Ask About Price",
                "goal_zh": "学会问价格、问颜色和问有没有库存，让购物对话顺利开始。",
                "goal_en": "Learn to ask about price, color, and stock so the shopping conversation can start smoothly.",
                "confidence_tip_zh": "购物开场不用太复杂，先问这个多少钱，再看下一步。",
                "confidence_tip_en": "The shopping opening does not need to be complicated. Start with how much this is and then move to the next step.",
                "scene_zh": "你在服装店、文创店或日用品店里挑东西。",
                "scene_en": "You are looking at items in a clothing store, gift shop, or daily-goods store.",
                "expressions": [
                    {"zh": "这个多少钱？", "en": "How much is this?", "note": "购物第一句。"},
                    {"zh": "有别的颜色吗？", "en": "Do you have other colors?", "note": "比较选择。"},
                    {"zh": "这个有小一点的吗？", "en": "Do you have a smaller one?", "note": "问尺寸。"},
                    {"zh": "我可以看看这个吗？", "en": "Can I take a look at this?", "note": "礼貌开口。"},
                    {"zh": "这个现在有货吗？", "en": "Is this in stock now?", "note": "库存表达。"},
                    {"zh": "我想先比较一下。", "en": "I'd like to compare first.", "note": "表达犹豫。"},
                    {"zh": "这个看起来不错。", "en": "This looks pretty good.", "note": "给出初步评价。"},
                    {"zh": "我再想一想。", "en": "I'll think about it a bit more.", "note": "不买时也礼貌。"},
                ],
                "frames": [
                    {"zh": "这个……吗？", "en": "Is this ...?", "usage": "快速问信息。"},
                    {"zh": "有……的吗？", "en": "Do you have one that is ...?", "usage": "问颜色或尺寸。"},
                    {"zh": "我可以……吗？", "en": "Can I ...?", "usage": "礼貌请求。"},
                    {"zh": "我想先……。", "en": "I'd like to ... first.", "usage": "拖延决策。"},
                    {"zh": "我再……。", "en": "I'll ... again / later.", "usage": "柔和收尾。"},
                ],
                "dialogue": [
                    ("Customer", "你好，我可以看看这个吗？", "Hello, can I take a look at this?"),
                    ("Clerk", "可以，这个是我们新到的。", "Sure. This is one of our new arrivals."),
                    ("Customer", "这个多少钱？", "How much is this?"),
                    ("Clerk", "这个是一百八十。", "This one is 180 yuan."),
                    ("Customer", "有别的颜色吗？", "Do you have other colors?"),
                    ("Clerk", "有黑色和米色。", "Yes, black and beige."),
                    ("Customer", "这个有小一点的吗？", "Do you have a smaller one?"),
                    ("Clerk", "有，不过现在只剩一件。", "Yes, but only one is left right now."),
                    ("Customer", "好的，我想先比较一下。", "Okay, I'd like to compare first."),
                    ("Clerk", "没问题，你再想一想。", "No problem. Take your time."),
                ],
                "mistakes": [
                    {"natural": "这个多少钱？", "natural_en": "How much is this?", "wrong": "这个多少？", "wrong_en": "This how many?", "note": "问价格常说多少钱。"},
                    {"natural": "有别的颜色吗？", "natural_en": "Do you have other colors?", "wrong": "你有另颜色吗？", "wrong_en": "Do you have other color?", "note": "别的更自然。"},
                    {"natural": "这个有小一点的吗？", "natural_en": "Do you have a smaller one?", "wrong": "这个小一点有吗？", "wrong_en": "This smaller have?", "note": "有……的吗是稳定句型。"},
                    {"natural": "我想先比较一下。", "natural_en": "I'd like to compare first.", "wrong": "我先比较。", "wrong_en": "I compare first.", "note": "加想和一下更柔和。"},
                    {"natural": "我再想一想。", "natural_en": "I'll think about it a bit more.", "wrong": "我以后想。", "wrong_en": "I think later.", "note": "再想一想很地道。"},
                ],
                "reflection": [
                    "请录一次在店里问价格、颜色和尺寸的三连问。",
                    "你买东西时最常比较什么？颜色、价格还是大小？",
                    "如果你还没决定，要怎么礼貌收尾？",
                    "练习一次从看商品到暂时不买的完整对话。",
                ],
            },
            {
                "title_zh": "试穿、比较和做决定",
                "title_en": "Compare Before You Buy",
                "goal_zh": "学会试穿、比较两件商品，并表达自己更喜欢哪一个以及为什么。",
                "goal_en": "Learn to try things on, compare two items, and express which one you prefer and why.",
                "confidence_tip_zh": "比较时只要抓住两点：更舒服、更适合、更便宜或更好看。",
                "confidence_tip_en": "When comparing, you only need two points: more comfortable, more suitable, cheaper, or nicer-looking.",
                "scene_zh": "你在店里试衣服、试鞋或比较两种同类商品。",
                "scene_en": "You are trying on clothes or shoes in a store, or comparing two similar products.",
                "expressions": [
                    {"zh": "我可以试一下吗？", "en": "Can I try it on?", "note": "试穿第一句。"},
                    {"zh": "这个穿起来更舒服。", "en": "This feels more comfortable when worn.", "note": "说明感受。"},
                    {"zh": "我觉得这个更适合我。", "en": "I think this suits me better.", "note": "比较后表态。"},
                    {"zh": "那个颜色更好看一点。", "en": "That color looks a bit better.", "note": "轻度比较。"},
                    {"zh": "这个稍微贵一点。", "en": "This one is a little more expensive.", "note": "价格比较。"},
                    {"zh": "如果便宜一点，我就买。", "en": "If it were a little cheaper, I'd buy it.", "note": "进入谈价前的铺垫。"},
                    {"zh": "我还是选这个吧。", "en": "I'll go with this one.", "note": "最终决定。"},
                    {"zh": "麻烦帮我拿这个号码。", "en": "Please get me this size.", "note": "试穿很实用。"},
                ],
                "frames": [
                    {"zh": "这个更……。", "en": "This is more ....", "usage": "做比较。"},
                    {"zh": "那个更……一点。", "en": "That one is a little more ....", "usage": "给另一件做评价。"},
                    {"zh": "我觉得……更适合我。", "en": "I think ... suits me better.", "usage": "表达选择。"},
                    {"zh": "如果……，我就……。", "en": "If ..., then I will ....", "usage": "说明条件。"},
                    {"zh": "我还是选……吧。", "en": "I'll still choose ....", "usage": "做最后决定。"},
                ],
                "dialogue": [
                    ("Clerk", "你可以试一下。试衣间在那边。", "You can try it on. The fitting room is over there."),
                    ("Olivia", "好。麻烦帮我拿这个号码。", "Okay. Please get me this size."),
                    ("Clerk", "可以。你觉得怎么样？", "Sure. What do you think?"),
                    ("Olivia", "这个穿起来更舒服。", "This feels more comfortable."),
                    ("Clerk", "那另一件呢？", "What about the other one?"),
                    ("Olivia", "那个颜色更好看一点，不过这个更适合我。", "That color looks a bit better, but this one suits me better."),
                    ("Clerk", "这个稍微贵一点。", "This one is a little more expensive."),
                    ("Olivia", "如果便宜一点，我就买。", "If it were a little cheaper, I'd buy it."),
                    ("Clerk", "今天可以给你打九折。", "Today I can give you a 10% discount."),
                    ("Olivia", "那好，我还是选这个吧。", "All right, then I'll go with this one."),
                ],
                "mistakes": [
                    {"natural": "我可以试一下吗？", "natural_en": "Can I try it on?", "wrong": "我可以试吗一下？", "wrong_en": "Can I try it on with broken order?", "note": "一下位置要自然。"},
                    {"natural": "这个穿起来更舒服。", "natural_en": "This feels more comfortable.", "wrong": "这个穿更舒服。", "wrong_en": "This wear more comfortable.", "note": "穿起来是完整口语块。"},
                    {"natural": "我觉得这个更适合我。", "natural_en": "I think this suits me better.", "wrong": "我觉得这个适合更多我。", "wrong_en": "I think this suits more me.", "note": "更适合我整体记。"},
                    {"natural": "如果便宜一点，我就买。", "natural_en": "If it were a little cheaper, I'd buy it.", "wrong": "如果便宜我买。", "wrong_en": "If cheap I buy.", "note": "条件句要完整。"},
                    {"natural": "我还是选这个吧。", "natural_en": "I'll go with this one.", "wrong": "我选择这个现在。", "wrong_en": "I choose this now.", "note": "还是选这个吧更口语。"},
                ],
                "reflection": [
                    "请比较两件你最近想买的东西，说出理由。",
                    "你更常用舒服、好看还是便宜来做决定？",
                    "练习一次试穿到下决定的完整表达。",
                    "如果你不想买了，怎么礼貌结束？",
                ],
            },
            {
                "title_zh": "礼貌砍价和售后沟通",
                "title_en": "Bargain and Handle After-Sales",
                "goal_zh": "学会礼貌询价、谈一点优惠、问退换规则，并在有问题时清楚说明情况。",
                "goal_en": "Learn to ask politely for a discount, ask about return or exchange rules, and explain clearly when there is a problem.",
                "confidence_tip_zh": "砍价不一定要强硬。语气礼貌、理由明确，往往更有效。",
                "confidence_tip_en": "Bargaining does not have to sound aggressive. A polite tone and a clear reason are often more effective.",
                "scene_zh": "你在市场、小店或线上售后场景里谈价格、问政策、处理小问题。",
                "scene_en": "You are negotiating price, asking about policy, or handling a small problem in a market, small shop, or after-sales situation.",
                "expressions": [
                    {"zh": "这个可以便宜一点吗？", "en": "Can this be a little cheaper?", "note": "最常见的礼貌砍价句。"},
                    {"zh": "如果我买两个，可以优惠吗？", "en": "If I buy two, can I get a discount?", "note": "用数量谈条件。"},
                    {"zh": "最低多少钱？", "en": "What's the lowest price?", "note": "更直接一点。"},
                    {"zh": "这个可以退吗？", "en": "Can this be returned?", "note": "售后基础句。"},
                    {"zh": "我昨天刚买的。", "en": "I just bought this yesterday.", "note": "说明时间。"},
                    {"zh": "这个尺寸不太合适。", "en": "This size isn't very suitable.", "note": "退换常用理由。"},
                    {"zh": "我想换一个颜色。", "en": "I'd like to change to another color.", "note": "换货需求。"},
                    {"zh": "麻烦你帮我看看怎么处理。", "en": "Please help me see how to handle this.", "note": "柔和推进售后。"},
                ],
                "frames": [
                    {"zh": "可以……一点吗？", "en": "Can it be a little ...?", "usage": "谈价格和要求。"},
                    {"zh": "如果我……，可以……吗？", "en": "If I ..., can I ...?", "usage": "谈条件。"},
                    {"zh": "这个……不太合适。", "en": "This ... isn't very suitable.", "usage": "说明问题。"},
                    {"zh": "我想换……。", "en": "I'd like to change ....", "usage": "表达换货意图。"},
                    {"zh": "麻烦你帮我……。", "en": "Please help me ....", "usage": "礼貌请求处理。"},
                ],
                "dialogue": [
                    ("Buyer", "老板，这个可以便宜一点吗？", "Boss, can this be a little cheaper?"),
                    ("Seller", "这个已经很便宜了。", "This is already very cheap."),
                    ("Buyer", "如果我买两个，可以优惠吗？", "If I buy two, can I get a discount?"),
                    ("Seller", "那我给你便宜十块。", "Then I'll reduce it by ten yuan for you."),
                    ("Buyer", "好。对了，这个可以退吗？", "Okay. By the way, can this be returned?"),
                    ("Seller", "七天内可以。", "Within seven days, yes."),
                    ("Buyer", "我昨天刚买的另一个，尺寸不太合适。", "I just bought another one yesterday, and the size isn't very suitable."),
                    ("Seller", "那你可以拿过来换。", "Then you can bring it back and exchange it."),
                    ("Buyer", "我想换一个颜色，麻烦你帮我看看怎么处理。", "I'd like to change to another color. Please help me see how to handle it."),
                    ("Seller", "可以，我们一起看看。", "Sure, let's take a look together."),
                ],
                "mistakes": [
                    {"natural": "这个可以便宜一点吗？", "natural_en": "Can this be a little cheaper?", "wrong": "这个便宜一点。", "wrong_en": "This cheaper a little.", "note": "问句更礼貌。"},
                    {"natural": "如果我买两个，可以优惠吗？", "natural_en": "If I buy two, can I get a discount?", "wrong": "我买两个，你优惠。", "wrong_en": "I buy two, you discount.", "note": "条件句更自然。"},
                    {"natural": "这个尺寸不太合适。", "natural_en": "This size isn't very suitable.", "wrong": "这个尺寸不对我。", "wrong_en": "This size is not right to me.", "note": "合适很常用。"},
                    {"natural": "我想换一个颜色。", "natural_en": "I'd like to change to another color.", "wrong": "我想改变颜色。", "wrong_en": "I want to change color.", "note": "换一个颜色更口语。"},
                    {"natural": "麻烦你帮我看看怎么处理。", "natural_en": "Please help me see how to handle this.", "wrong": "你现在处理这个。", "wrong_en": "Handle this now.", "note": "礼貌推进更有效。"},
                ],
                "reflection": [
                    "请练习一次礼貌砍价，不要显得太强硬。",
                    "如果衣服尺寸不合适，你会怎么说？",
                    "你更喜欢直接问最低多少钱，还是先谈条件？",
                    "录一段售后沟通，至少用上“麻烦你帮我看看怎么处理”。",
                ],
            },
        ],
    },
    {
        "number": "74",
        "slug": "TransportAndDirections",
        "title": "Confident Chinese: Transport and Directions",
        "subtitle": "打车、问路与行程沟通",
        "color": "#8E24AA",
        "intro_zh": "出行场景要求反应快，所以更需要短句和高频表达。本书帮学员把目的地、路线、换乘和临时问题都说清楚。",
        "intro_en": "Travel situations require quick reactions, so short lines and high-frequency expressions matter even more. This book helps learners state destinations, routes, transfers, and temporary problems clearly.",
        "method_zh": "三章分别覆盖打车、问路和行程变化，帮助学员在真实移动中保持表达稳定。",
        "method_en": "The three chapters cover taxis, asking for directions, and changes in the plan so learners can stay stable while speaking in real movement contexts.",
        "chapters": [
            {
                "title_zh": "上车先把目的地说清楚",
                "title_en": "State the Destination",
                "goal_zh": "学会在打车时说目的地、说明时间要求，并确认司机是否走导航。",
                "goal_en": "Learn to state your destination in a taxi, explain your timing needs, and confirm whether the driver will follow the navigation.",
                "confidence_tip_zh": "上车先说地点，再补充要求，司机最容易听清楚。",
                "confidence_tip_en": "Say the place first and add the request after that. This is the easiest way for the driver to understand you.",
                "scene_zh": "你上出租车或网约车后，需要告诉司机去哪里以及怎么走。",
                "scene_en": "You have entered a taxi or ride-share car and need to tell the driver where to go and how to get there.",
                "expressions": [
                    {"zh": "师傅，去国贸。", "en": "Driver, to Guomao please.", "note": "地点先说最有效。"},
                    {"zh": "麻烦你开导航。", "en": "Please turn on the navigation.", "note": "避免走错路。"},
                    {"zh": "我有点赶时间。", "en": "I'm a bit in a hurry.", "note": "说明需求。"},
                    {"zh": "走高架会不会快一点？", "en": "Would taking the elevated road be a bit faster?", "note": "路线提议。"},
                    {"zh": "请在前面路口停一下。", "en": "Please stop at the intersection ahead.", "note": "临时停车需求。"},
                    {"zh": "到这儿就可以了。", "en": "Here is fine.", "note": "下车常用句。"},
                    {"zh": "我从这边下车。", "en": "I'll get out on this side.", "note": "安全下车。"},
                    {"zh": "谢谢，辛苦了。", "en": "Thank you, you've worked hard.", "note": "礼貌收尾。"},
                ],
                "frames": [
                    {"zh": "去……。", "en": "To ....", "usage": "目的地表达。"},
                    {"zh": "麻烦你……。", "en": "Please ....", "usage": "礼貌要求。"},
                    {"zh": "我有点……。", "en": "I'm a bit ....", "usage": "说明状态。"},
                    {"zh": "请在……停一下。", "en": "Please stop at ....", "usage": "临时停靠。"},
                    {"zh": "到……就可以了。", "en": "Up to ... is fine.", "usage": "结束行程。"},
                ],
                "dialogue": [
                    ("Passenger", "师傅，去国贸。", "Driver, to Guomao please."),
                    ("Driver", "好，走三环可以吗？", "Sure. Is Third Ring Road okay?"),
                    ("Passenger", "可以，麻烦你开导航。", "Sure. Please turn on the navigation."),
                    ("Driver", "好的。", "Okay."),
                    ("Passenger", "我有点赶时间，走高架会不会快一点？", "I'm a bit in a hurry. Would taking the elevated road be a bit faster?"),
                    ("Driver", "现在高架有点堵。", "The elevated road is a bit congested right now."),
                    ("Passenger", "那就按导航走吧。", "Then let's follow the navigation."),
                    ("Driver", "好。到了以后停哪里？", "Okay. Where should I stop when we arrive?"),
                    ("Passenger", "请在前面路口停一下，到这儿就可以了。", "Please stop at the intersection ahead. Here is fine."),
                    ("Passenger", "谢谢，辛苦了。", "Thanks, you've worked hard."),
                ],
                "mistakes": [
                    {"natural": "师傅，去国贸。", "natural_en": "Driver, to Guomao please.", "wrong": "你去国贸。", "wrong_en": "You go to Guomao.", "note": "省略也要自然。"},
                    {"natural": "麻烦你开导航。", "natural_en": "Please turn on the navigation.", "wrong": "你开导航现在。", "wrong_en": "You open navigation now.", "note": "麻烦你更礼貌。"},
                    {"natural": "我有点赶时间。", "natural_en": "I'm a bit in a hurry.", "wrong": "我很着急时间。", "wrong_en": "I am very anxious time.", "note": "赶时间是固定说法。"},
                    {"natural": "请在前面路口停一下。", "natural_en": "Please stop at the intersection ahead.", "wrong": "前面停。", "wrong_en": "Stop ahead.", "note": "补足地点更清楚。"},
                    {"natural": "到这儿就可以了。", "natural_en": "Here is fine.", "wrong": "到这里结束。", "wrong_en": "End here.", "note": "就可以了更像中文口语。"},
                ],
                "reflection": [
                    "请录一段打车开场：目的地、导航、时间要求。",
                    "如果你赶时间但不想太直接，怎么说？",
                    "练习一次临时下车：请在前面路口停一下。",
                    "你会怎么礼貌结束一段车程？",
                ],
            },
            {
                "title_zh": "问路和确认换乘",
                "title_en": "Ask for Directions",
                "goal_zh": "学会问怎么走、地铁怎么换乘、路程远不远，以及确认自己有没有走错。",
                "goal_en": "Learn to ask how to get somewhere, how to transfer on the subway, whether it is far, and whether you are going the wrong way.",
                "confidence_tip_zh": "问路时重点不是复杂句，而是地点、方向、交通方式三个信息点。",
                "confidence_tip_en": "When asking for directions, the key is not complex grammar but three information points: place, direction, and transport mode.",
                "scene_zh": "你在路上、地铁站或商场里需要问别人怎么走。",
                "scene_en": "You need to ask someone for directions on the street, in a subway station, or in a mall.",
                "expressions": [
                    {"zh": "请问，地铁站怎么走？", "en": "Excuse me, how do I get to the subway station?", "note": "问路万能开头。"},
                    {"zh": "离这儿远吗？", "en": "Is it far from here?", "note": "判断距离。"},
                    {"zh": "我需要换乘吗？", "en": "Do I need to transfer?", "note": "交通关键信息。"},
                    {"zh": "坐几号线？", "en": "Which line should I take?", "note": "地铁高频问法。"},
                    {"zh": "往左还是往右？", "en": "To the left or to the right?", "note": "确认方向。"},
                    {"zh": "我是不是走错了？", "en": "Did I go the wrong way?", "note": "迷路时很好用。"},
                    {"zh": "大概走几分钟？", "en": "About how many minutes is the walk?", "note": "问时间。"},
                    {"zh": "谢谢，我明白了。", "en": "Thank you, I understand now.", "note": "收尾自然。"},
                ],
                "frames": [
                    {"zh": "请问，……怎么走？", "en": "Excuse me, how do I get to ...?", "usage": "问路线。"},
                    {"zh": "离这儿……吗？", "en": "Is it ... from here?", "usage": "问远近。"},
                    {"zh": "我需要……吗？", "en": "Do I need to ...?", "usage": "确认步骤。"},
                    {"zh": "往……还是往……？", "en": "Toward ... or toward ...?", "usage": "确认分叉方向。"},
                    {"zh": "我是不是……了？", "en": "Did I ...?", "usage": "检查错误。"},
                ],
                "dialogue": [
                    ("Tourist", "请问，地铁站怎么走？", "Excuse me, how do I get to the subway station?"),
                    ("Local", "一直往前走，然后右转。", "Walk straight ahead, then turn right."),
                    ("Tourist", "离这儿远吗？", "Is it far from here?"),
                    ("Local", "不远，走五分钟左右。", "Not far, about a five-minute walk."),
                    ("Tourist", "我要去天安门，我需要换乘吗？", "I'm going to Tiananmen. Do I need to transfer?"),
                    ("Local", "要，你先坐二号线，再换一号线。", "Yes. Take Line 2 first, then transfer to Line 1."),
                    ("Tourist", "那我现在往左还是往右？", "Then should I go left or right now?"),
                    ("Local", "往右。你如果看到商场，就说明你走错了。", "To the right. If you see the mall, that means you've gone the wrong way."),
                    ("Tourist", "明白了，谢谢。我是不是刚才差点走错了？", "Got it, thank you. Was I almost going the wrong way just now?"),
                    ("Local", "对，不过现在没问题了。", "Yes, but now it's fine."),
                ],
                "mistakes": [
                    {"natural": "请问，地铁站怎么走？", "natural_en": "Excuse me, how do I get to the subway station?", "wrong": "地铁站怎么去走？", "wrong_en": "How go walk to subway station?", "note": "怎么走更顺。"},
                    {"natural": "离这儿远吗？", "natural_en": "Is it far from here?", "wrong": "这个远从这里吗？", "wrong_en": "Is this far from here?", "note": "离这儿远吗是固定问法。"},
                    {"natural": "我需要换乘吗？", "natural_en": "Do I need to transfer?", "wrong": "我需要改变车吗？", "wrong_en": "Do I need to change car?", "note": "换乘更地道。"},
                    {"natural": "往左还是往右？", "natural_en": "Left or right?", "wrong": "左还是右边去？", "wrong_en": "Go left or right side?", "note": "短句更清楚。"},
                    {"natural": "我是不是走错了？", "natural_en": "Did I go the wrong way?", "wrong": "我错走了吗？", "wrong_en": "Did I wrong-walk?", "note": "走错了是自然搭配。"},
                ],
                "reflection": [
                    "请录一段你在地铁站问路的对话。",
                    "你最想先问距离、方向还是换乘？为什么？",
                    "如果你快迟到了，怎么更快地问路？",
                    "练习一句迷路时的自救句子。",
                ],
            },
            {
                "title_zh": "改路线、迟到和突发问题",
                "title_en": "Handle Changes on the Way",
                "goal_zh": "学会表达迟到、改路线、联系对方说明情况，并在行程变化时保持礼貌和清楚。",
                "goal_en": "Learn to explain lateness, change the route, contact the other person, and stay polite and clear when plans change.",
                "confidence_tip_zh": "出行突发状况时，先说明问题，再说你要怎么办，对方最容易理解。",
                "confidence_tip_en": "When something unexpected happens on the way, explain the problem first and then say what you will do. That is easiest for the other person to understand.",
                "scene_zh": "你堵车、坐错线、找不到出口，或者需要通知别人自己会晚到。",
                "scene_en": "You are stuck in traffic, took the wrong line, cannot find the exit, or need to tell someone you will be late.",
                "expressions": [
                    {"zh": "不好意思，我可能会晚一点。", "en": "Sorry, I might be a little late.", "note": "迟到预警。"},
                    {"zh": "我这边有点堵车。", "en": "There's a bit of traffic on my side.", "note": "解释原因。"},
                    {"zh": "我刚刚坐错线了。", "en": "I just took the wrong line.", "note": "说明具体问题。"},
                    {"zh": "我现在正在往那边赶。", "en": "I'm on my way there now.", "note": "说明行动。"},
                    {"zh": "你能等我十分钟吗？", "en": "Can you wait for me ten minutes?", "note": "提出请求。"},
                    {"zh": "我们要不要换个地方见？", "en": "Should we meet somewhere else?", "note": "改计划。"},
                    {"zh": "我到的时候给你发消息。", "en": "I'll message you when I arrive.", "note": "给出后续安排。"},
                    {"zh": "谢谢你理解。", "en": "Thank you for understanding.", "note": "礼貌收尾。"},
                ],
                "frames": [
                    {"zh": "不好意思，我可能会……。", "en": "Sorry, I might ....", "usage": "提前说明。"},
                    {"zh": "我这边有点……。", "en": "There's a bit of ... on my side.", "usage": "解释原因。"},
                    {"zh": "我现在正在……。", "en": "I'm ... right now.", "usage": "说当前动作。"},
                    {"zh": "你能……吗？", "en": "Can you ...?", "usage": "提请求。"},
                    {"zh": "我……的时候给你发消息。", "en": "I'll message you when I ....", "usage": "交代后续。"},
                ],
                "dialogue": [
                    ("Ava", "不好意思，我可能会晚一点。", "Sorry, I might be a little late."),
                    ("Ben", "没关系，怎么了？", "No problem. What happened?"),
                    ("Ava", "我这边有点堵车，而且我刚刚坐错线了。", "There's a bit of traffic on my side, and I just took the wrong line."),
                    ("Ben", "你现在到哪儿了？", "Where are you now?"),
                    ("Ava", "我现在正在往那边赶。", "I'm heading there now."),
                    ("Ben", "大概还要多久？", "About how much longer will it take?"),
                    ("Ava", "你能等我十分钟吗？", "Can you wait for me ten minutes?"),
                    ("Ben", "可以。要不要换个地方见？", "Sure. Do you want to meet somewhere else?"),
                    ("Ava", "不用，我到的时候给你发消息。", "No need. I'll message you when I arrive."),
                    ("Ben", "好，路上小心。", "Okay, be careful on the way."),
                ],
                "mistakes": [
                    {"natural": "不好意思，我可能会晚一点。", "natural_en": "Sorry, I might be a little late.", "wrong": "对不起，我会晚。", "wrong_en": "Sorry, I will late.", "note": "可能会晚一点更柔和。"},
                    {"natural": "我这边有点堵车。", "natural_en": "There's a bit of traffic on my side.", "wrong": "这里很多车堵。", "wrong_en": "Here many cars are stuck.", "note": "堵车是固定块。"},
                    {"natural": "我刚刚坐错线了。", "natural_en": "I just took the wrong line.", "wrong": "我刚坐错误线。", "wrong_en": "I just took wrong line.", "note": "坐错线了更自然。"},
                    {"natural": "我现在正在往那边赶。", "natural_en": "I'm on my way there now.", "wrong": "我现在去快那里。", "wrong_en": "I go fast there now.", "note": "往那边赶是高频口语。"},
                    {"natural": "我到的时候给你发消息。", "natural_en": "I'll message you when I arrive.", "wrong": "我到给你消息。", "wrong_en": "I arrive give you message.", "note": "发消息是完整表达。"},
                ],
                "reflection": [
                    "请练习一次迟到说明，从原因到后续安排都说出来。",
                    "如果你真的找不到出口，下一句会说什么？",
                    "你会怎么提出“能不能等我十分钟”？",
                    "录一段路上变化后的完整通知消息。",
                ],
            },
        ],
    },
    {
        "number": "75",
        "slug": "HealthAndSymptoms",
        "title": "Confident Chinese: Health and Symptoms",
        "subtitle": "看病、症状与身体表达",
        "color": "#E53935",
        "intro_zh": "身体不舒服时最怕说不清楚。本书帮助学员用简单、稳定的中文描述症状、回答医生问题，并处理买药和请假等后续事情。",
        "intro_en": "When you do not feel well, the biggest fear is not being able to explain clearly. This book helps learners describe symptoms in simple, steady Chinese, answer a doctor's questions, and handle next steps like getting medicine or asking for leave.",
        "method_zh": "从挂号到就诊，再到买药与请假，本书把常见健康表达串成可直接上口的场景练习。",
        "method_en": "From registration to the doctor's consultation and then to medicine and leave requests, this book turns common health expressions into direct speaking practice.",
        "chapters": [
            {
                "title_zh": "挂号和描述不舒服",
                "title_en": "Describe the Problem",
                "goal_zh": "学会挂号、表达哪里不舒服、什么时候开始的，以及症状是轻还是重。",
                "goal_en": "Learn to register, say where you feel unwell, explain when it started, and describe whether the symptoms are mild or serious.",
                "confidence_tip_zh": "身体表达不需要复杂词汇，地点、感觉、时间三件事先说清楚就够了。",
                "confidence_tip_en": "Health descriptions do not require complicated vocabulary. If you make the place, feeling, and time clear first, that is enough.",
                "scene_zh": "你在诊所或医院前台挂号，并向护士或医生简单说明症状。",
                "scene_en": "You are registering at a clinic or hospital and briefly explaining your symptoms to a nurse or doctor.",
                "expressions": [
                    {"zh": "我今天想挂内科。", "en": "I'd like to register for internal medicine today.", "note": "挂号先说科室。"},
                    {"zh": "我有点发烧。", "en": "I have a slight fever.", "note": "常见症状。"},
                    {"zh": "我一直咳嗽。", "en": "I've been coughing continuously.", "note": "持续症状。"},
                    {"zh": "我喉咙很痛。", "en": "My throat hurts a lot.", "note": "部位+感觉。"},
                    {"zh": "从昨天晚上开始的。", "en": "It started last night.", "note": "说明时间。"},
                    {"zh": "这两天越来越严重。", "en": "It has been getting worse these two days.", "note": "说变化。"},
                    {"zh": "我想先看一下医生。", "en": "I'd like to see a doctor first.", "note": "自然请求。"},
                    {"zh": "需要先量体温吗？", "en": "Do I need to take my temperature first?", "note": "流程确认。"},
                ],
                "frames": [
                    {"zh": "我有点……。", "en": "I have a little ....", "usage": "说轻微症状。"},
                    {"zh": "我一直……。", "en": "I've been ....", "usage": "说持续状态。"},
                    {"zh": "我……很痛。", "en": "My ... hurts a lot.", "usage": "说疼痛部位。"},
                    {"zh": "从……开始的。", "en": "It started from ....", "usage": "说明时间。"},
                    {"zh": "需要先……吗？", "en": "Do I need to ... first?", "usage": "确认流程。"},
                ],
                "dialogue": [
                    ("Reception", "你好，请问你想挂什么科？", "Hello. Which department would you like to register for?"),
                    ("Daniel", "我今天想挂内科。", "I'd like to register for internal medicine today."),
                    ("Reception", "你哪里不舒服？", "Where do you feel uncomfortable?"),
                    ("Daniel", "我有点发烧，也一直咳嗽。", "I have a slight fever, and I've been coughing."),
                    ("Reception", "还有别的症状吗？", "Any other symptoms?"),
                    ("Daniel", "我喉咙很痛。", "My throat hurts a lot."),
                    ("Reception", "是什么时候开始的？", "When did it start?"),
                    ("Daniel", "从昨天晚上开始的。", "It started last night."),
                    ("Reception", "好的，这两天越来越严重吗？", "Okay. Has it gotten worse these two days?"),
                    ("Daniel", "对，我想先看一下医生。", "Yes. I'd like to see a doctor first."),
                ],
                "mistakes": [
                    {"natural": "我有点发烧。", "natural_en": "I have a slight fever.", "wrong": "我一点发烧。", "wrong_en": "I a little fever.", "note": "有点要完整。"},
                    {"natural": "我一直咳嗽。", "natural_en": "I've been coughing.", "wrong": "我一直有咳嗽。", "wrong_en": "I always have cough.", "note": "直接说咳嗽更像口语。"},
                    {"natural": "我喉咙很痛。", "natural_en": "My throat hurts a lot.", "wrong": "我的喉咙有很多痛。", "wrong_en": "My throat has a lot of pain.", "note": "很痛最自然。"},
                    {"natural": "从昨天晚上开始的。", "natural_en": "It started last night.", "wrong": "开始在昨天晚上。", "wrong_en": "Started at last night.", "note": "从……开始的记整体。"},
                    {"natural": "我想先看一下医生。", "natural_en": "I'd like to see a doctor first.", "wrong": "我先想看医生。", "wrong_en": "I first want see doctor.", "note": "想先看一下医生更柔和。"},
                ],
                "reflection": [
                    "请录一段挂号说明，说出科室、症状和开始时间。",
                    "如果你只有轻微发烧，会怎么表达？",
                    "练习一次“我一直……”句型。",
                    "你最容易说错的是部位、感觉还是时间？",
                ],
            },
            {
                "title_zh": "回答医生问题和说明症状变化",
                "title_en": "Answer the Doctor",
                "goal_zh": "学会回答医生关于疼痛程度、吃药情况、过敏史和生活状态的问题。",
                "goal_en": "Learn to answer the doctor's questions about pain level, medicine use, allergy history, and general condition.",
                "confidence_tip_zh": "医生问得快时，先抓关键词。你可以先回答重点，再补一句细节。",
                "confidence_tip_en": "When the doctor asks quickly, catch the keywords first. You can answer the main point first and then add one more detail.",
                "scene_zh": "你在诊室里回答医生的问题，并描述症状有没有好转或加重。",
                "scene_en": "You are in the consultation room answering the doctor's questions and describing whether the symptoms are improving or worsening.",
                "expressions": [
                    {"zh": "现在比昨天严重一点。", "en": "It's a little more serious than yesterday now.", "note": "做对比。"},
                    {"zh": "晚上会更明显。", "en": "It becomes more obvious at night.", "note": "时间变化。"},
                    {"zh": "我还没有吃药。", "en": "I haven't taken medicine yet.", "note": "说明处理情况。"},
                    {"zh": "我对青霉素过敏。", "en": "I'm allergic to penicillin.", "note": "过敏史很重要。"},
                    {"zh": "咳的时候胸口会不舒服。", "en": "When I cough, my chest feels uncomfortable.", "note": "条件描述。"},
                    {"zh": "我昨天晚上没睡好。", "en": "I didn't sleep well last night.", "note": "补充身体状态。"},
                    {"zh": "大概是七分左右。", "en": "It's about a seven out of ten.", "note": "疼痛量化。"},
                    {"zh": "我最近工作压力比较大。", "en": "My work pressure has been quite high recently.", "note": "补充背景。"},
                ],
                "frames": [
                    {"zh": "现在比……更……。", "en": "Now it's more ... than ....", "usage": "对比变化。"},
                    {"zh": "……的时候会……。", "en": "When ..., it will ....", "usage": "描述条件。"},
                    {"zh": "我还没有……。", "en": "I haven't ... yet.", "usage": "说明未做事项。"},
                    {"zh": "我对……过敏。", "en": "I'm allergic to ....", "usage": "说过敏史。"},
                    {"zh": "大概是……分。", "en": "It's about ... points.", "usage": "量化疼痛。"},
                ],
                "dialogue": [
                    ("Doctor", "现在感觉怎么样？", "How do you feel now?"),
                    ("Patient", "现在比昨天严重一点。", "It's a little more serious than yesterday."),
                    ("Doctor", "什么时候最明显？", "When is it most obvious?"),
                    ("Patient", "晚上会更明显。", "It becomes more obvious at night."),
                    ("Doctor", "你自己吃过药吗？", "Have you taken any medicine yourself?"),
                    ("Patient", "我还没有吃药。", "I haven't taken medicine yet."),
                    ("Doctor", "你有过敏史吗？", "Do you have any allergy history?"),
                    ("Patient", "我对青霉素过敏。", "I'm allergic to penicillin."),
                    ("Doctor", "疼痛大概几分？", "About how many points is the pain?"),
                    ("Patient", "大概是七分左右，咳的时候胸口会不舒服。", "It's about a seven, and my chest feels uncomfortable when I cough."),
                ],
                "mistakes": [
                    {"natural": "现在比昨天严重一点。", "natural_en": "It's a little more serious than yesterday.", "wrong": "现在昨天更严重一点。", "wrong_en": "Now yesterday more serious.", "note": "比结构要完整。"},
                    {"natural": "我还没有吃药。", "natural_en": "I haven't taken medicine yet.", "wrong": "我还没吃一个药。", "wrong_en": "I haven't taken one medicine yet.", "note": "一般不用量词。"},
                    {"natural": "我对青霉素过敏。", "natural_en": "I'm allergic to penicillin.", "wrong": "我有青霉素过敏。", "wrong_en": "I have penicillin allergy.", "note": "对……过敏最自然。"},
                    {"natural": "咳的时候胸口会不舒服。", "natural_en": "When I cough, my chest feels uncomfortable.", "wrong": "我咳嗽时间胸口不舒服。", "wrong_en": "When I cough time chest uncomfortable.", "note": "……的时候会……更顺。"},
                    {"natural": "大概是七分左右。", "natural_en": "It's about seven points.", "wrong": "差不多七点。", "wrong_en": "About seven o'clock.", "note": "疼痛要说分，不是点。"},
                ],
                "reflection": [
                    "请录一段医生问诊回答，至少说三个症状细节。",
                    "如果你没有吃药，该怎么说得自然？",
                    "练习一次疼痛打分，从三分到八分都说一遍。",
                    "如果医生问过敏史，你能马上回答吗？",
                ],
            },
            {
                "title_zh": "买药、请假和后续安排",
                "title_en": "Medicine and Next Steps",
                "goal_zh": "学会去药房拿药、问怎么吃药、向老师或同事请假，并说明自己接下来的安排。",
                "goal_en": "Learn to get medicine at the pharmacy, ask how to take it, ask a teacher or coworker for leave, and explain your next steps.",
                "confidence_tip_zh": "后续安排越清楚，对方越放心。你可以说现在要做什么、什么时候恢复。",
                "confidence_tip_en": "The clearer your next steps are, the more reassured the other person will be. Say what you need to do now and when you may return.",
                "scene_zh": "你在药房、微信或工作群里处理治疗后的实际安排。",
                "scene_en": "You are at the pharmacy or communicating on WeChat or in a work chat about what to do after the appointment.",
                "expressions": [
                    {"zh": "这个药怎么吃？", "en": "How do I take this medicine?", "note": "药房必备句。"},
                    {"zh": "一天吃几次？", "en": "How many times a day should I take it?", "note": "频率问题。"},
                    {"zh": "饭前还是饭后？", "en": "Before meals or after meals?", "note": "服药方式。"},
                    {"zh": "医生让我休息两天。", "en": "The doctor told me to rest for two days.", "note": "说明医嘱。"},
                    {"zh": "我今天想请半天假。", "en": "I'd like to ask for half a day off today.", "note": "请假表达。"},
                    {"zh": "我下午去医院复查。", "en": "I'm going to the hospital for a follow-up this afternoon.", "note": "后续安排。"},
                    {"zh": "如果好一点，我明天就回来。", "en": "If I feel better, I'll come back tomorrow.", "note": "说明恢复时间。"},
                    {"zh": "谢谢你的理解。", "en": "Thank you for your understanding.", "note": "礼貌收尾。"},
                ],
                "frames": [
                    {"zh": "这个药怎么……？", "en": "How do I ... with this medicine?", "usage": "问吃法。"},
                    {"zh": "一天……次？", "en": "... times a day?", "usage": "问频率。"},
                    {"zh": "我今天想请……假。", "en": "I'd like to ask for ... leave today.", "usage": "请假。"},
                    {"zh": "如果……，我就……。", "en": "If ..., then I will ....", "usage": "说明后续。"},
                    {"zh": "谢谢你的……。", "en": "Thank you for your ....", "usage": "礼貌结束。"},
                ],
                "dialogue": [
                    ("Pharmacist", "你的药都在这里了。", "All your medicine is here."),
                    ("Patient", "谢谢。这个药怎么吃？", "Thank you. How do I take this medicine?"),
                    ("Pharmacist", "一天吃三次。", "Take it three times a day."),
                    ("Patient", "饭前还是饭后？", "Before meals or after meals?"),
                    ("Pharmacist", "饭后吃。", "Take it after meals."),
                    ("Patient", "好的。对了，医生让我休息两天。", "Okay. By the way, the doctor told me to rest for two days."),
                    ("Patient", "我今天想请半天假，下午去医院复查。", "I'd like to ask for half a day off today, and I'm going to the hospital for a follow-up this afternoon."),
                    ("Manager", "没问题，你先好好休息。", "No problem. Have a good rest first."),
                    ("Patient", "如果好一点，我明天就回来。", "If I feel better, I'll come back tomorrow."),
                    ("Manager", "好，谢谢你及时告诉我。", "Okay. Thanks for telling me promptly."),
                ],
                "mistakes": [
                    {"natural": "这个药怎么吃？", "natural_en": "How do I take this medicine?", "wrong": "这个药怎么使用嘴巴？", "wrong_en": "How do I use my mouth for this medicine?", "note": "直接问怎么吃即可。"},
                    {"natural": "一天吃几次？", "natural_en": "How many times a day?", "wrong": "一天多少次吃？", "wrong_en": "A day how many times eat?", "note": "几次更自然。"},
                    {"natural": "我今天想请半天假。", "natural_en": "I'd like to ask for half a day off today.", "wrong": "我今天想要半天自由。", "wrong_en": "I want half a day free today.", "note": "请假是固定表达。"},
                    {"natural": "我下午去医院复查。", "natural_en": "I'm going to the hospital for a follow-up this afternoon.", "wrong": "我下午回医院检查再次。", "wrong_en": "I go back hospital check again.", "note": "复查更精炼。"},
                    {"natural": "如果好一点，我明天就回来。", "natural_en": "If I feel better, I'll come back tomorrow.", "wrong": "如果更好我明天回来。", "wrong_en": "If better I tomorrow come back.", "note": "完整条件句更清楚。"},
                ],
                "reflection": [
                    "请录一段药房问药和公司请假的连续表达。",
                    "你会怎么问饭前还是饭后？",
                    "如果你想请一天假而不是半天，怎么改？",
                    "练习一次说明复查安排和回归时间。",
                ],
            },
        ],
    },
    {
        "number": "76",
        "slug": "WorkplaceAndMeetings",
        "title": "Confident Chinese: Workplace and Meetings",
        "subtitle": "职场介绍、会议与汇报表达",
        "color": "#3949AB",
        "intro_zh": "外国学员在职场里最常见的问题，不是词不够，而是不知道怎样用简短中文表达清楚自己在做什么、需要什么、担心什么。",
        "intro_en": "The most common problem foreign learners face in the workplace is not a lack of vocabulary but not knowing how to express clearly in short Chinese what they are doing, what they need, and what concerns them.",
        "method_zh": "本书从入职介绍、会议发言到进度汇报，帮助学员建立稳定的职场表达框架。",
        "method_en": "This book moves from onboarding introductions to speaking in meetings and progress updates to build a stable framework for workplace Chinese.",
        "chapters": [
            {
                "title_zh": "入职自我介绍和破冰",
                "title_en": "Introduce Yourself at Work",
                "goal_zh": "学会在团队里做简短入职介绍，说清职位、职责和想合作的方向。",
                "goal_en": "Learn to give a short onboarding introduction in a team, clearly state your role and responsibilities, and mention how you want to collaborate.",
                "confidence_tip_zh": "职场自我介绍最重要的是让别人记住你负责什么，不是把所有经历都说完。",
                "confidence_tip_en": "In a workplace self-introduction, the most important thing is that people remember what you are responsible for, not that you tell your whole life story.",
                "scene_zh": "你刚加入新团队，需要在例会或群里做一个简短介绍。",
                "scene_en": "You have just joined a new team and need to give a short introduction in a meeting or group chat.",
                "expressions": [
                    {"zh": "大家好，我是新来的产品经理。", "en": "Hello everyone, I'm the new product manager.", "note": "开场清楚。"},
                    {"zh": "以后请大家多多指教。", "en": "Please guide me a lot in the future.", "note": "职场礼貌。"},
                    {"zh": "我主要负责用户研究和需求整理。", "en": "I'm mainly responsible for user research and organizing requirements.", "note": "说明职责。"},
                    {"zh": "如果有需要，也欢迎随时找我。", "en": "If there's a need, please feel free to find me anytime.", "note": "表达合作态度。"},
                    {"zh": "我之前在新加坡做过类似项目。", "en": "I worked on similar projects in Singapore before.", "note": "补充经验。"},
                    {"zh": "我最近会先熟悉业务。", "en": "Recently I'll first get familiar with the business.", "note": "说明短期计划。"},
                    {"zh": "很高兴加入这个团队。", "en": "I'm very happy to join this team.", "note": "自然正面表达。"},
                    {"zh": "以后还请大家多支持。", "en": "Please continue to support me in the future.", "note": "结束得体。"},
                ],
                "frames": [
                    {"zh": "大家好，我是……。", "en": "Hello everyone, I'm ....", "usage": "团队开场。"},
                    {"zh": "我主要负责……。", "en": "I'm mainly responsible for ....", "usage": "说明职责。"},
                    {"zh": "我之前……过。", "en": "I have ... before.", "usage": "补充经验。"},
                    {"zh": "我最近会先……。", "en": "Recently I'll first ....", "usage": "说短期计划。"},
                    {"zh": "以后还请大家……。", "en": "Going forward, please ....", "usage": "礼貌收尾。"},
                ],
                "dialogue": [
                    ("Manager", "今天请新同事做个简单自我介绍。", "Today let's ask our new coworker to give a short introduction."),
                    ("Chris", "大家好，我是新来的产品经理。", "Hello everyone, I'm the new product manager."),
                    ("Chris", "我之前在新加坡做过类似项目。", "I worked on similar projects in Singapore before."),
                    ("Chris", "我主要负责用户研究和需求整理。", "I'm mainly responsible for user research and organizing requirements."),
                    ("Chris", "我最近会先熟悉业务。", "Recently I'll first get familiar with the business."),
                    ("Chris", "如果有需要，也欢迎随时找我。", "If there's a need, please feel free to find me anytime."),
                    ("Colleague", "欢迎加入。", "Welcome aboard."),
                    ("Chris", "很高兴加入这个团队。", "I'm very happy to join this team."),
                    ("Chris", "以后请大家多多指教。", "Please guide me a lot going forward."),
                    ("Chris", "以后还请大家多支持。", "Please continue to support me in the future."),
                ],
                "mistakes": [
                    {"natural": "我主要负责用户研究。", "natural_en": "I'm mainly responsible for user research.", "wrong": "我主要做负责用户研究。", "wrong_en": "I mainly do responsible for user research.", "note": "负责直接接内容。"},
                    {"natural": "我之前在新加坡做过类似项目。", "natural_en": "I worked on similar projects in Singapore before.", "wrong": "我之前在新加坡做类似项目。", "wrong_en": "I before in Singapore do similar project.", "note": "做过更自然。"},
                    {"natural": "我最近会先熟悉业务。", "natural_en": "Recently I'll first get familiar with the business.", "wrong": "最近我先熟悉业务会。", "wrong_en": "Recently I first business familiar will.", "note": "语序要稳。"},
                    {"natural": "以后请大家多多指教。", "natural_en": "Please guide me a lot in the future.", "wrong": "以后请你们教我很多。", "wrong_en": "Please teach me a lot in the future.", "note": "固定礼貌表达更自然。"},
                    {"natural": "如果有需要，也欢迎随时找我。", "natural_en": "If there's a need, feel free to find me anytime.", "wrong": "你需要找我。", "wrong_en": "You need find me.", "note": "完整邀请更柔和。"},
                ],
                "reflection": [
                    "请录一段二十秒的入职自我介绍。",
                    "你负责的工作可以用哪一句说清楚？",
                    "如果你想显得更开放合作，该怎么说？",
                    "练习一次例会中的自我介绍版本。",
                ],
            },
            {
                "title_zh": "会议里表达观点和提问",
                "title_en": "Speak Up in Meetings",
                "goal_zh": "学会在会议中插入观点、提出问题、表达同意或保留意见。",
                "goal_en": "Learn to enter the conversation in meetings, ask questions, and express agreement or reservations.",
                "confidence_tip_zh": "会议发言不用一次讲完所有想法。先说一个观点，再说一个问题，已经很有效。",
                "confidence_tip_en": "You do not need to say every thought at once in a meeting. One point and one question are already very effective.",
                "scene_zh": "你在团队会议里需要发言、确认需求或补充自己的看法。",
                "scene_en": "You need to speak in a team meeting, confirm requirements, or add your own view.",
                "expressions": [
                    {"zh": "我先补充一点。", "en": "Let me add one point first.", "note": "柔和进入话题。"},
                    {"zh": "我有一个问题。", "en": "I have one question.", "note": "直接而自然。"},
                    {"zh": "我基本同意这个方向。", "en": "I basically agree with this direction.", "note": "表达同意。"},
                    {"zh": "不过我有一点担心。", "en": "But I do have one concern.", "note": "转入保留意见。"},
                    {"zh": "这个时间是不是有点紧？", "en": "Isn't this timeline a bit tight?", "note": "会议高频句。"},
                    {"zh": "我们要不要先确认需求？", "en": "Should we confirm the requirements first?", "note": "提建议。"},
                    {"zh": "我想再听听大家的意见。", "en": "I'd like to hear everyone's opinions a bit more.", "note": "推进讨论。"},
                    {"zh": "这个部分我可以跟进。", "en": "I can follow up on this part.", "note": "主动承担。"},
                ],
                "frames": [
                    {"zh": "我先……一点。", "en": "Let me ... one point first.", "usage": "礼貌插话。"},
                    {"zh": "我有一个……。", "en": "I have one ....", "usage": "提出问题或担心。"},
                    {"zh": "不过我有一点……。", "en": "But I do have one ....", "usage": "说保留意见。"},
                    {"zh": "我们要不要先……？", "en": "Should we first ...?", "usage": "提建议。"},
                    {"zh": "这个部分我可以……。", "en": "I can ... this part.", "usage": "承担任务。"},
                ],
                "dialogue": [
                    ("Lead", "大家对这个方案有什么看法？", "What do you all think of this proposal?"),
                    ("Iris", "我先补充一点。", "Let me add one point first."),
                    ("Iris", "我基本同意这个方向。", "I basically agree with this direction."),
                    ("Iris", "不过我有一点担心。", "But I do have one concern."),
                    ("Lead", "你担心什么？", "What are you concerned about?"),
                    ("Iris", "这个时间是不是有点紧？", "Isn't this timeline a bit tight?"),
                    ("Iris", "我们要不要先确认需求？", "Should we confirm the requirements first?"),
                    ("Lead", "这个建议不错。还有别的问题吗？", "That's a good suggestion. Any other questions?"),
                    ("Iris", "我有一个问题，测试资源够吗？", "I have one question: are the testing resources enough?"),
                    ("Iris", "如果需要，这个部分我可以跟进。", "If needed, I can follow up on this part."),
                ],
                "mistakes": [
                    {"natural": "我先补充一点。", "natural_en": "Let me add one point first.", "wrong": "我先增加一点。", "wrong_en": "I first increase one point.", "note": "补充更适合会议。"},
                    {"natural": "我基本同意这个方向。", "natural_en": "I basically agree with this direction.", "wrong": "我同意基本这个方向。", "wrong_en": "I agree basically this direction.", "note": "基本放前面更顺。"},
                    {"natural": "不过我有一点担心。", "natural_en": "But I do have one concern.", "wrong": "但是我一个担心有。", "wrong_en": "But I one concern have.", "note": "口语顺序要自然。"},
                    {"natural": "这个时间是不是有点紧？", "natural_en": "Isn't this timeline a bit tight?", "wrong": "这个时间很紧吗是不是？", "wrong_en": "This time very tight is it?", "note": "是不是有点紧常用。"},
                    {"natural": "这个部分我可以跟进。", "natural_en": "I can follow up on this part.", "wrong": "这个部分我可以继续后面。", "wrong_en": "This part I can continue later.", "note": "跟进是职场高频词。"},
                ],
                "reflection": [
                    "请录一段会议发言，先同意，再提出一个担心。",
                    "如果你想提一个问题，开头怎么最自然？",
                    "练习一次“我们要不要先……”的建议句。",
                    "你愿意主动跟进什么类型的工作？",
                ],
            },
            {
                "title_zh": "汇报进度、表达困难和请求支持",
                "title_en": "Report Progress and Ask for Support",
                "goal_zh": "学会汇报当前进度、解释卡点，并明确提出自己需要的帮助。",
                "goal_en": "Learn to report current progress, explain blockers, and clearly ask for the help you need.",
                "confidence_tip_zh": "进度汇报最怕空。你可以按“做了什么、卡在哪里、需要什么”三个部分说。",
                "confidence_tip_en": "The worst progress update is an empty one. Use three parts: what has been done, where you are blocked, and what you need.",
                "scene_zh": "你在例会、一对一或群聊里更新工作进度，并请求支持。",
                "scene_en": "You are updating work progress in a regular meeting, one-on-one, or group chat and asking for support.",
                "expressions": [
                    {"zh": "目前进度还算顺利。", "en": "At the moment, progress is fairly smooth.", "note": "先给整体判断。"},
                    {"zh": "这个部分已经完成了。", "en": "This part has already been finished.", "note": "明确完成项。"},
                    {"zh": "现在卡在数据整理这一步。", "en": "Right now we're blocked at the data cleanup step.", "note": "说卡点。"},
                    {"zh": "主要问题是时间不太够。", "en": "The main problem is that time is a bit tight.", "note": "说明原因。"},
                    {"zh": "我需要设计团队的支持。", "en": "I need support from the design team.", "note": "明确资源需求。"},
                    {"zh": "如果今天能确认，我明天就能继续。", "en": "If we can confirm it today, I can continue tomorrow.", "note": "说明依赖关系。"},
                    {"zh": "我会在下午之前更新给大家。", "en": "I'll update everyone before this afternoon.", "note": "承诺下一步。"},
                    {"zh": "有新的情况我会及时同步。", "en": "If there's anything new, I'll sync it in time.", "note": "稳定团队预期。"},
                ],
                "frames": [
                    {"zh": "目前……还算……。", "en": "At the moment ... is fairly ....", "usage": "给整体状态。"},
                    {"zh": "现在卡在……。", "en": "Right now we're blocked at ....", "usage": "说卡点。"},
                    {"zh": "主要问题是……。", "en": "The main problem is ....", "usage": "说原因。"},
                    {"zh": "我需要……的支持。", "en": "I need ... support.", "usage": "提资源需求。"},
                    {"zh": "如果……，我就……。", "en": "If ..., then I will ....", "usage": "说明后续。"},
                ],
                "dialogue": [
                    ("Manager", "你这边进度怎么样？", "How is the progress on your side?"),
                    ("Nina", "目前进度还算顺利。", "At the moment, progress is fairly smooth."),
                    ("Nina", "这个部分已经完成了。", "This part has already been finished."),
                    ("Manager", "那现在还有什么问题？", "Then what problems remain now?"),
                    ("Nina", "现在卡在数据整理这一步。", "Right now we're blocked at the data cleanup step."),
                    ("Nina", "主要问题是时间不太够。", "The main problem is that time is a bit tight."),
                    ("Manager", "你需要什么支持？", "What support do you need?"),
                    ("Nina", "我需要设计团队的支持。", "I need support from the design team."),
                    ("Nina", "如果今天能确认，我明天就能继续。", "If we can confirm it today, I can continue tomorrow."),
                    ("Nina", "我会在下午之前更新给大家。", "I'll update everyone before this afternoon."),
                ],
                "mistakes": [
                    {"natural": "目前进度还算顺利。", "natural_en": "Progress is fairly smooth at the moment.", "wrong": "现在进度是顺利一点。", "wrong_en": "Now progress is smooth a little.", "note": "还算顺利用得更多。"},
                    {"natural": "现在卡在数据整理这一步。", "natural_en": "We're blocked at the data cleanup step.", "wrong": "现在停在数据整理。", "wrong_en": "Now stop at data cleanup.", "note": "卡在更像职场口语。"},
                    {"natural": "主要问题是时间不太够。", "natural_en": "The main problem is that time is a bit tight.", "wrong": "主要问题时间没有够。", "wrong_en": "The main problem time not enough.", "note": "说法要完整。"},
                    {"natural": "我需要设计团队的支持。", "natural_en": "I need support from the design team.", "wrong": "我需要设计团队支持我。", "wrong_en": "I need the design team support me.", "note": "的支持是更稳的结构。"},
                    {"natural": "我会在下午之前更新给大家。", "natural_en": "I'll update everyone before this afternoon.", "wrong": "我下午以前更新大家。", "wrong_en": "I before afternoon update everyone.", "note": "更新给大家更自然。"},
                ],
                "reflection": [
                    "请录一段一分钟进度汇报，包含完成项、卡点和请求。",
                    "你最常需要什么类型的支持？",
                    "如果今天确认不了，你会怎么改说法？",
                    "练习一次对团队承诺后续更新时间。",
                ],
            },
        ],
    },
    {
        "number": "77",
        "slug": "SocialAndInvitations",
        "title": "Confident Chinese: Social and Invitations",
        "subtitle": "社交聊天、邀请与回应表达",
        "color": "#F06292",
        "intro_zh": "社交场景的难点在于既要自然，又不能太硬。本书帮助学员在小聚、邀请和兴趣话题里找到轻松而有礼貌的表达方式。",
        "intro_en": "The difficulty in social settings is being natural without sounding too blunt. This book helps learners find relaxed but polite ways to speak in meetups, invitations, and interest-based conversations.",
        "method_zh": "三章分别聚焦破冰、邀请回应和兴趣闲聊，让学员会接话、会回应、也会体面拒绝。",
        "method_en": "The three chapters focus on ice-breaking, responding to invitations, and chatting about interests so learners can join in, respond, and also refuse gracefully.",
        "chapters": [
            {
                "title_zh": "小聚里怎么自然破冰",
                "title_en": "Break the Ice at Gatherings",
                "goal_zh": "学会在朋友聚会、饭局或活动里用轻松中文开始聊天。",
                "goal_en": "Learn to start light conversations in Chinese at a gathering, meal, or social event.",
                "confidence_tip_zh": "社交破冰不要急着问太深。先聊现在的场景，再慢慢转到人。",
                "confidence_tip_en": "Do not jump into deep questions too quickly when breaking the ice. Start with the current situation and then move gradually toward the person.",
                "scene_zh": "你在朋友聚会、公司活动或周末小聚里第一次和别人闲聊。",
                "scene_en": "You are making small talk for the first time with someone at a gathering, company event, or weekend meetup.",
                "expressions": [
                    {"zh": "你今天也是第一次来吗？", "en": "Is this also your first time here today?", "note": "安全破冰。"},
                    {"zh": "这边人还挺多的。", "en": "There are quite a lot of people here.", "note": "从场景切入。"},
                    {"zh": "气氛很好。", "en": "The atmosphere is nice.", "note": "轻松评价。"},
                    {"zh": "你是怎么知道这个活动的？", "en": "How did you hear about this event?", "note": "自然续聊问题。"},
                    {"zh": "我朋友推荐我来的。", "en": "A friend recommended it to me.", "note": "常见回答。"},
                    {"zh": "我最近也想多认识一些朋友。", "en": "Recently I also want to meet more friends.", "note": "表达来意。"},
                    {"zh": "跟你聊天很轻松。", "en": "Talking with you is very easy.", "note": "积极反馈。"},
                    {"zh": "我们可以继续聊一会儿。", "en": "We can keep chatting for a while.", "note": "自然延续。"},
                ],
                "frames": [
                    {"zh": "你今天也是……吗？", "en": "Are you also ... today?", "usage": "建立共同点。"},
                    {"zh": "这边……还挺……的。", "en": "Over here, ... is quite ....", "usage": "从环境切入。"},
                    {"zh": "你是怎么……的？", "en": "How did you ...?", "usage": "问经历。"},
                    {"zh": "我最近也想……。", "en": "Recently I also want to ....", "usage": "表达个人意图。"},
                    {"zh": "我们可以继续……。", "en": "We can continue to ....", "usage": "延续聊天。"},
                ],
                "dialogue": [
                    ("Grace", "你好，你今天也是第一次来吗？", "Hi, is this also your first time here today?"),
                    ("Tom", "对，是第一次。", "Yes, it's my first time."),
                    ("Grace", "这边人还挺多的，气氛很好。", "There are quite a lot of people here, and the atmosphere is nice."),
                    ("Tom", "是啊。你是怎么知道这个活动的？", "Yeah. How did you hear about this event?"),
                    ("Grace", "我朋友推荐我来的。", "A friend recommended it to me."),
                    ("Tom", "我也是。", "Me too."),
                    ("Grace", "我最近也想多认识一些朋友。", "Recently I also want to meet more friends."),
                    ("Tom", "那很好啊。", "That's great."),
                    ("Grace", "跟你聊天很轻松。", "Talking with you is very easy."),
                    ("Tom", "我们可以继续聊一会儿。", "We can keep chatting for a while."),
                ],
                "mistakes": [
                    {"natural": "你今天也是第一次来吗？", "natural_en": "Is this also your first time here today?", "wrong": "你第一次今天来吗？", "wrong_en": "You first today come?", "note": "语序要稳。"},
                    {"natural": "这边人还挺多的。", "natural_en": "There are quite a lot of people here.", "wrong": "这里人很多还。", "wrong_en": "Here people many still.", "note": "还挺……的很口语。"},
                    {"natural": "你是怎么知道这个活动的？", "natural_en": "How did you hear about this event?", "wrong": "你怎么知道这个活动？", "wrong_en": "How do you know this event?", "note": "完整问法更自然。"},
                    {"natural": "我朋友推荐我来的。", "natural_en": "A friend recommended it to me.", "wrong": "我的朋友推荐。", "wrong_en": "My friend recommended.", "note": "把信息说完整。"},
                    {"natural": "跟你聊天很轻松。", "natural_en": "Talking with you is very easy.", "wrong": "我和你聊天很简单。", "wrong_en": "Chatting with you is simple.", "note": "轻松更自然。"},
                ],
                "reflection": [
                    "请录一段聚会破冰对话。",
                    "你最喜欢从场景、活动还是人开始聊？",
                    "练习一次“你是怎么知道这个活动的？”",
                    "如果对方看起来有点紧张，你会怎么让气氛更轻松？",
                ],
            },
            {
                "title_zh": "邀请、答应和礼貌拒绝",
                "title_en": "Invite and Respond Gracefully",
                "goal_zh": "学会邀请别人吃饭、喝咖啡、参加活动，也学会自然答应或礼貌拒绝。",
                "goal_en": "Learn to invite someone to eat, drink coffee, or join an event, and also learn how to accept or refuse naturally and politely.",
                "confidence_tip_zh": "拒绝时不要只说不行，最好给一个简单理由或下次机会。",
                "confidence_tip_en": "When refusing, do not only say no. It is better to give a simple reason or leave room for another chance.",
                "scene_zh": "你想邀请朋友一起活动，或者回应别人对你的邀请。",
                "scene_en": "You want to invite a friend to do something together, or you need to respond to someone else's invitation.",
                "expressions": [
                    {"zh": "你周末有空吗？", "en": "Are you free this weekend?", "note": "邀请前先探时间。"},
                    {"zh": "要不要一起喝杯咖啡？", "en": "Do you want to grab a coffee together?", "note": "轻松邀请。"},
                    {"zh": "听起来不错。", "en": "That sounds good.", "note": "答应前的自然回应。"},
                    {"zh": "好啊，我很想去。", "en": "Sure, I'd really like to go.", "note": "积极接受。"},
                    {"zh": "不好意思，我那天已经有安排了。", "en": "Sorry, I already have plans that day.", "note": "礼貌拒绝。"},
                    {"zh": "这次可能不行，下次吧。", "en": "This time probably won't work; next time.", "note": "保留关系。"},
                    {"zh": "要不我们改到周日？", "en": "How about moving it to Sunday?", "note": "主动改时间。"},
                    {"zh": "到时候我再跟你确认。", "en": "I'll confirm with you again then.", "note": "留后续。"},
                ],
                "frames": [
                    {"zh": "你……有空吗？", "en": "Are you free ...?", "usage": "先问时间。"},
                    {"zh": "要不要一起……？", "en": "Do you want to ... together?", "usage": "发邀请。"},
                    {"zh": "不好意思，我……。", "en": "Sorry, I ....", "usage": "礼貌拒绝。"},
                    {"zh": "这次……，下次吧。", "en": "This time ..., next time.", "usage": "留余地。"},
                    {"zh": "要不我们改到……？", "en": "How about moving it to ...?", "usage": "改计划。"},
                ],
                "dialogue": [
                    ("Kevin", "你周末有空吗？", "Are you free this weekend?"),
                    ("Maya", "应该有空，怎么了？", "I should be. What's up?"),
                    ("Kevin", "要不要一起喝杯咖啡？", "Do you want to grab a coffee together?"),
                    ("Maya", "听起来不错。", "That sounds good."),
                    ("Kevin", "周六下午怎么样？", "How about Saturday afternoon?"),
                    ("Maya", "不好意思，我那天已经有安排了。", "Sorry, I already have plans that day."),
                    ("Kevin", "没关系。", "No problem."),
                    ("Maya", "这次可能不行，下次吧。", "This time probably won't work; next time."),
                    ("Maya", "要不我们改到周日？", "How about moving it to Sunday?"),
                    ("Kevin", "可以，到时候我再跟你确认。", "Sure. I'll confirm with you again then."),
                ],
                "mistakes": [
                    {"natural": "你周末有空吗？", "natural_en": "Are you free this weekend?", "wrong": "你周末空吗？", "wrong_en": "Weekend empty?", "note": "有空更完整。"},
                    {"natural": "要不要一起喝杯咖啡？", "natural_en": "Do you want to grab a coffee together?", "wrong": "你一起喝咖啡要吗？", "wrong_en": "You together drink coffee want?", "note": "要不要是很自然的邀请形式。"},
                    {"natural": "不好意思，我那天已经有安排了。", "natural_en": "Sorry, I already have plans that day.", "wrong": "不好意思，我不去。", "wrong_en": "Sorry, I don't go.", "note": "给原因更柔和。"},
                    {"natural": "这次可能不行，下次吧。", "natural_en": "This time probably won't work; next time.", "wrong": "这次不，下次。", "wrong_en": "This time no, next time.", "note": "完整表达更自然。"},
                    {"natural": "到时候我再跟你确认。", "natural_en": "I'll confirm with you again then.", "wrong": "那个时候我再说。", "wrong_en": "At that time I'll say again.", "note": "确认更具体。"},
                ],
                "reflection": [
                    "请练习一次发出邀请的完整对话。",
                    "你更常遇到答应别人还是拒绝别人？",
                    "如果你真的想去但当天没空，怎么说最好？",
                    "录一段从拒绝到改时间的表达。",
                ],
            },
            {
                "title_zh": "聊兴趣、周末计划和轻松表达自己",
                "title_en": "Talk About Interests",
                "goal_zh": "学会聊兴趣、周末安排和自己最近的状态，让聊天更轻松、更有来回。",
                "goal_en": "Learn to talk about interests, weekend plans, and your recent state so the conversation becomes lighter and more balanced.",
                "confidence_tip_zh": "闲聊最重要的是来回。你说一句，也给对方一个接球的机会。",
                "confidence_tip_en": "The key to small talk is back-and-forth. Say one thing, and then give the other person a chance to respond.",
                "scene_zh": "你和朋友、同学或同事继续闲聊，分享自己最近喜欢做的事。",
                "scene_en": "You continue a casual chat with friends, classmates, or coworkers, sharing what you have been enjoying lately.",
                "expressions": [
                    {"zh": "我最近迷上了跑步。", "en": "Recently I've become obsessed with running.", "note": "说近况很自然。"},
                    {"zh": "周末我一般会在家休息。", "en": "On weekends I usually rest at home.", "note": "说习惯。"},
                    {"zh": "如果天气好，我会出去走走。", "en": "If the weather is good, I'll go for a walk.", "note": "补充条件。"},
                    {"zh": "我最近压力有点大。", "en": "I've been a bit stressed recently.", "note": "适度表达状态。"},
                    {"zh": "所以我想找一点轻松的事情做。", "en": "So I want to find something relaxing to do.", "note": "自然解释。"},
                    {"zh": "你平时怎么放松？", "en": "How do you usually relax?", "note": "把话题给对方。"},
                    {"zh": "听起来很适合你。", "en": "That sounds like it suits you well.", "note": "积极回应。"},
                    {"zh": "下次你也可以带我一起。", "en": "Next time you can take me along too.", "note": "轻松建立下一次互动。"},
                ],
                "frames": [
                    {"zh": "我最近……。", "en": "Recently I ....", "usage": "说近况。"},
                    {"zh": "周末我一般会……。", "en": "On weekends I usually ....", "usage": "说习惯。"},
                    {"zh": "如果……，我会……。", "en": "If ..., I will ....", "usage": "条件表达。"},
                    {"zh": "所以我想……。", "en": "So I want to ....", "usage": "解释原因。"},
                    {"zh": "你平时怎么……？", "en": "How do you usually ...?", "usage": "让对方参与。"},
                ],
                "dialogue": [
                    ("Ella", "你周末一般做什么？", "What do you usually do on weekends?"),
                    ("Ryan", "周末我一般会在家休息。", "On weekends I usually rest at home."),
                    ("Ryan", "如果天气好，我会出去走走。", "If the weather is good, I'll go for a walk."),
                    ("Ella", "听起来不错。", "That sounds nice."),
                    ("Ryan", "我最近压力有点大，所以我想找一点轻松的事情做。", "I've been a bit stressed recently, so I want to find something relaxing to do."),
                    ("Ella", "我最近迷上了跑步。", "Recently I've become obsessed with running."),
                    ("Ryan", "真的？你平时怎么放松？", "Really? How do you usually relax?"),
                    ("Ella", "我会跑步，也会听播客。", "I run, and I also listen to podcasts."),
                    ("Ryan", "听起来很适合你。", "That sounds like it suits you well."),
                    ("Ryan", "下次你也可以带我一起。", "Next time you can take me along too."),
                ],
                "mistakes": [
                    {"natural": "我最近迷上了跑步。", "natural_en": "Recently I've become obsessed with running.", "wrong": "我最近爱跑步很多。", "wrong_en": "I recently love running a lot.", "note": "迷上了更地道。"},
                    {"natural": "周末我一般会在家休息。", "natural_en": "On weekends I usually rest at home.", "wrong": "周末一般我在家会休息。", "wrong_en": "Weekend generally I at home will rest.", "note": "常见口语顺序更自然。"},
                    {"natural": "如果天气好，我会出去走走。", "natural_en": "If the weather is good, I'll go for a walk.", "wrong": "如果天气很好我出去走。", "wrong_en": "If weather good I go walk.", "note": "走走更像轻松口语。"},
                    {"natural": "我最近压力有点大。", "natural_en": "I've been a bit stressed recently.", "wrong": "我最近压力很大一点。", "wrong_en": "I recently pressure very big a little.", "note": "有点大很自然。"},
                    {"natural": "你平时怎么放松？", "natural_en": "How do you usually relax?", "wrong": "你怎么平常放松？", "wrong_en": "How do you normally relax?", "note": "平时怎么更常见。"},
                ],
                "reflection": [
                    "请录一段介绍你最近兴趣爱好的表达。",
                    "你周末最常做什么？用中文说完整。",
                    "如果你最近压力大，怎么自然表达而不显得太重？",
                    "练习一句把话题抛回给对方的问题。",
                ],
            },
        ],
    },
    {
        "number": "78",
        "slug": "PhoneWechatAndScheduling",
        "title": "Confident Chinese: Phone, WeChat and Scheduling",
        "subtitle": "电话、微信与时间安排表达",
        "color": "#00897B",
        "intro_zh": "很多外国学员在面对电话和微信确认时会突然紧张，因为信息密度高、节奏快。本书把自报身份、确认细节、改时间和提醒四类高频任务讲透。",
        "intro_en": "Many foreign learners suddenly become nervous when dealing with phone calls and WeChat confirmations because the information density is high and the rhythm is fast. This book covers four high-frequency tasks: stating who you are, confirming details, rescheduling, and sending reminders.",
        "method_zh": "三章从电话开场、微信确认到改约提醒，帮助学员在时间沟通上更清楚、更可靠。",
        "method_en": "The three chapters move from phone openings to WeChat confirmation and then to rescheduling and reminders so learners can sound clearer and more reliable in time-related communication.",
        "chapters": [
            {
                "title_zh": "打电话先说明你是谁",
                "title_en": "Identify Yourself on the Phone",
                "goal_zh": "学会打电话开场、自报身份、说明来意，并确认对方现在是否方便。",
                "goal_en": "Learn to open a phone call, identify yourself, state your purpose, and confirm whether the other person is available right now.",
                "confidence_tip_zh": "电话里声音看不见，所以结构更重要：你是谁、找谁、为什么打来。",
                "confidence_tip_en": "On the phone, your face cannot be seen, so structure matters even more: who you are, whom you want, and why you are calling.",
                "scene_zh": "你给老师、同事、快递员或服务方打电话确认事情。",
                "scene_en": "You are calling a teacher, coworker, delivery person, or service provider to confirm something.",
                "expressions": [
                    {"zh": "你好，我是安娜。", "en": "Hello, this is Anna.", "note": "自报身份。"},
                    {"zh": "请问现在方便说话吗？", "en": "Is it convenient to talk right now?", "note": "礼貌确认。"},
                    {"zh": "我想确认一下明天的时间。", "en": "I'd like to confirm tomorrow's time.", "note": "说明来意。"},
                    {"zh": "我找王老师。", "en": "I'm looking for Teacher Wang.", "note": "找人表达。"},
                    {"zh": "是这样的……", "en": "Here's the situation ...", "note": "进入说明。"},
                    {"zh": "我这边有一个小问题。", "en": "I have a small issue on my side.", "note": "引出问题。"},
                    {"zh": "那我晚一点再打给你。", "en": "Then I'll call you again a bit later.", "note": "对方不方便时。"},
                    {"zh": "谢谢，不打扰你了。", "en": "Thanks, I won't disturb you further.", "note": "礼貌收尾。"},
                ],
                "frames": [
                    {"zh": "你好，我是……。", "en": "Hello, this is ....", "usage": "电话开场。"},
                    {"zh": "请问现在方便……吗？", "en": "Is it convenient to ... now?", "usage": "确认时机。"},
                    {"zh": "我想确认一下……。", "en": "I'd like to confirm ....", "usage": "说明来意。"},
                    {"zh": "我这边有一个……。", "en": "I have a ... on my side.", "usage": "引出情况。"},
                    {"zh": "那我……再……。", "en": "Then I'll ... again later.", "usage": "改到之后。"},
                ],
                "dialogue": [
                    ("Caller", "你好，我是安娜。", "Hello, this is Anna."),
                    ("Receiver", "你好，请问有什么事？", "Hello. What can I do for you?"),
                    ("Caller", "请问现在方便说话吗？", "Is it convenient to talk right now?"),
                    ("Receiver", "方便，你说吧。", "Yes, go ahead."),
                    ("Caller", "我想确认一下明天的时间。", "I'd like to confirm tomorrow's time."),
                    ("Receiver", "好的。", "Okay."),
                    ("Caller", "是这样的，我这边有一个小问题。", "Here's the situation: I have a small issue on my side."),
                    ("Receiver", "什么问题？", "What issue?"),
                    ("Caller", "如果你现在不方便，那我晚一点再打给你。", "If it's not convenient right now, I can call you again a bit later."),
                    ("Receiver", "没关系，现在可以说。", "No problem. You can say it now."),
                ],
                "mistakes": [
                    {"natural": "你好，我是安娜。", "natural_en": "Hello, this is Anna.", "wrong": "你好，我叫是安娜。", "wrong_en": "Hello, my called is Anna.", "note": "电话里直接说我是……更自然。"},
                    {"natural": "请问现在方便说话吗？", "natural_en": "Is it convenient to talk right now?", "wrong": "现在你可以说话？", "wrong_en": "Can you speak now?", "note": "方便说话更礼貌。"},
                    {"natural": "我想确认一下明天的时间。", "natural_en": "I'd like to confirm tomorrow's time.", "wrong": "我想确认明天时间一下。", "wrong_en": "I want confirm tomorrow time a bit.", "note": "一下位置更自然。"},
                    {"natural": "我这边有一个小问题。", "natural_en": "I have a small issue on my side.", "wrong": "我有一个小问题在这里。", "wrong_en": "I have a small problem here.", "note": "我这边是高频电话表达。"},
                    {"natural": "谢谢，不打扰你了。", "natural_en": "Thanks, I won't disturb you further.", "wrong": "谢谢，我结束你。", "wrong_en": "Thanks, I finish you.", "note": "固定礼貌收尾。"},
                ],
                "reflection": [
                    "请录一段电话开场，从自报身份到说明来意。",
                    "如果你打电话前不确定对方方不方便，第一句怎么说？",
                    "练习一次对方忙碌时的礼貌收尾。",
                    "你最怕电话里哪一部分？",
                ],
            },
            {
                "title_zh": "微信里确认细节和时间",
                "title_en": "Confirm Details on WeChat",
                "goal_zh": "学会在微信里确认时间、地点、材料和步骤，让对方一看就明白。",
                "goal_en": "Learn to confirm time, place, materials, and steps on WeChat so the other person can understand immediately.",
                "confidence_tip_zh": "微信最怕一句话里塞太多信息。分成时间、地点、需要带什么三块就很清楚。",
                "confidence_tip_en": "The biggest problem on WeChat is packing too much into one sentence. Divide it into time, place, and what to bring, and it becomes clear.",
                "scene_zh": "你在微信里和老师、同事、朋友确认明天或下周的安排。",
                "scene_en": "You are confirming plans for tomorrow or next week with a teacher, coworker, or friend on WeChat.",
                "expressions": [
                    {"zh": "我再确认一下。", "en": "Let me confirm once more.", "note": "消息开头很常见。"},
                    {"zh": "我们明天下午三点见。", "en": "We'll meet tomorrow at 3 p.m.", "note": "时间句。"},
                    {"zh": "地点还是在原来的教室吗？", "en": "Is the location still the original classroom?", "note": "确认地点。"},
                    {"zh": "需要我提前准备什么吗？", "en": "Is there anything I need to prepare in advance?", "note": "问材料。"},
                    {"zh": "我会提前十分钟到。", "en": "I'll arrive ten minutes early.", "note": "表达可靠。"},
                    {"zh": "如果有变化，请告诉我。", "en": "If there are any changes, please tell me.", "note": "留后路。"},
                    {"zh": "我已经记下来了。", "en": "I've already written it down.", "note": "确认收到。"},
                    {"zh": "好的，明天见。", "en": "Okay, see you tomorrow.", "note": "简洁收尾。"},
                ],
                "frames": [
                    {"zh": "我再确认一下……。", "en": "Let me confirm ... once more.", "usage": "消息开头。"},
                    {"zh": "地点还是在……吗？", "en": "Is the location still at ...?", "usage": "问地点。"},
                    {"zh": "需要我提前……吗？", "en": "Do I need to ... in advance?", "usage": "问准备。"},
                    {"zh": "如果有变化，请……。", "en": "If there are changes, please ....", "usage": "留变动空间。"},
                    {"zh": "好的，……见。", "en": "Okay, see you ....", "usage": "简洁收尾。"},
                ],
                "dialogue": [
                    ("A", "老师好，我再确认一下。", "Hello teacher, let me confirm once more."),
                    ("B", "好的，你说。", "Okay, go ahead."),
                    ("A", "我们明天下午三点见。", "We'll meet tomorrow at 3 p.m."),
                    ("A", "地点还是在原来的教室吗？", "Is the location still the original classroom?"),
                    ("B", "对，还是原来的教室。", "Yes, still the original classroom."),
                    ("A", "需要我提前准备什么吗？", "Is there anything I need to prepare in advance?"),
                    ("B", "带上你的作业就可以。", "Just bring your homework."),
                    ("A", "好，我会提前十分钟到。", "Okay, I'll arrive ten minutes early."),
                    ("A", "如果有变化，请告诉我。", "If there are any changes, please tell me."),
                    ("B", "没问题，好的，明天见。", "No problem. Okay, see you tomorrow."),
                ],
                "mistakes": [
                    {"natural": "我再确认一下。", "natural_en": "Let me confirm once more.", "wrong": "我再检查这个。", "wrong_en": "Let me check this again.", "note": "确认更适合约时间。"},
                    {"natural": "地点还是在原来的教室吗？", "natural_en": "Is the location still the original classroom?", "wrong": "地点还是原来教室？", "wrong_en": "Location still original classroom?", "note": "完整问句更清楚。"},
                    {"natural": "需要我提前准备什么吗？", "natural_en": "Do I need to prepare anything in advance?", "wrong": "我提前需要准备什么？", "wrong_en": "I in advance need prepare what?", "note": "把需要放前面更自然。"},
                    {"natural": "我会提前十分钟到。", "natural_en": "I'll arrive ten minutes early.", "wrong": "我提前十分钟会到。", "wrong_en": "I ten minutes early will arrive.", "note": "语序更常见。"},
                    {"natural": "如果有变化，请告诉我。", "natural_en": "If there are any changes, please tell me.", "wrong": "有变化告诉我如果。", "wrong_en": "Tell me if have changes.", "note": "完整条件句更稳。"},
                ],
                "reflection": [
                    "请写一段微信确认消息并朗读出来。",
                    "你更常确认时间还是地点？",
                    "练习一次提前准备材料的提问。",
                    "如果临时改地点，你会怎么发消息？",
                ],
            },
            {
                "title_zh": "改约、提醒和跟进",
                "title_en": "Reschedule and Follow Up",
                "goal_zh": "学会改时间、发提醒、跟进对方回复，并在安排变化时保持礼貌专业。",
                "goal_en": "Learn to reschedule, send reminders, and follow up on replies while staying polite and professional when plans change.",
                "confidence_tip_zh": "改约时先道歉，再给新方案，对方最容易接受。",
                "confidence_tip_en": "When rescheduling, apologize first and then offer a new option. That is easiest for the other person to accept.",
                "scene_zh": "你需要把约定改到别的时间，或者在见面前做最后提醒。",
                "scene_en": "You need to move an appointment to another time or send a final reminder before meeting.",
                "expressions": [
                    {"zh": "不好意思，我想改一下时间。", "en": "Sorry, I'd like to change the time a little.", "note": "改约开头。"},
                    {"zh": "我临时有点事情。", "en": "Something came up at the last minute.", "note": "说明原因但不过度展开。"},
                    {"zh": "我们能不能改到周五？", "en": "Could we move it to Friday?", "note": "给新方案。"},
                    {"zh": "如果你不方便，也没关系。", "en": "If it's not convenient for you, that's okay too.", "note": "给对方空间。"},
                    {"zh": "我想提醒你一下明天的安排。", "en": "I'd like to remind you about tomorrow's arrangement.", "note": "提醒用语。"},
                    {"zh": "到时候我们在门口见。", "en": "Let's meet at the entrance then.", "note": "收束细节。"},
                    {"zh": "你到了以后给我发个消息。", "en": "Send me a message after you arrive.", "note": "现场对接。"},
                    {"zh": "好的，那就这么定了。", "en": "Okay, then let's settle it like that.", "note": "确认最终方案。"},
                ],
                "frames": [
                    {"zh": "不好意思，我想……。", "en": "Sorry, I'd like to ....", "usage": "改约开头。"},
                    {"zh": "我们能不能改到……？", "en": "Could we move it to ...?", "usage": "给新时间。"},
                    {"zh": "如果你不方便，也……。", "en": "If it's not convenient for you, ... too.", "usage": "给空间。"},
                    {"zh": "我想提醒你一下……。", "en": "I'd like to remind you about ....", "usage": "发提醒。"},
                    {"zh": "那就这么定了。", "en": "Then let's settle it like this.", "usage": "最终确认。"},
                ],
                "dialogue": [
                    ("A", "不好意思，我想改一下时间。", "Sorry, I'd like to change the time a little."),
                    ("B", "怎么了？", "What happened?"),
                    ("A", "我临时有点事情。", "Something came up at the last minute."),
                    ("A", "我们能不能改到周五？", "Could we move it to Friday?"),
                    ("B", "周五下午可以。", "Friday afternoon works."),
                    ("A", "如果你不方便，也没关系。", "If it's not convenient for you, that's okay too."),
                    ("B", "没事，就周五吧。", "No worries, let's do Friday."),
                    ("A", "好。我想提醒你一下明天的安排，到时候我们在门口见。", "Okay. I'd like to remind you about tomorrow's arrangement. Let's meet at the entrance then."),
                    ("B", "好的，我到了以后给你发个消息。", "Okay. I'll message you after I arrive."),
                    ("A", "好，那就这么定了。", "Great, then let's settle it like that."),
                ],
                "mistakes": [
                    {"natural": "不好意思，我想改一下时间。", "natural_en": "Sorry, I'd like to change the time.", "wrong": "我想改变时间。", "wrong_en": "I want to change time.", "note": "改一下时间更口语。"},
                    {"natural": "我临时有点事情。", "natural_en": "Something came up at the last minute.", "wrong": "我临时有事情一点。", "wrong_en": "I have something a little at the last minute.", "note": "固定说法直接记。"},
                    {"natural": "我们能不能改到周五？", "natural_en": "Could we move it to Friday?", "wrong": "我们改周五能不能？", "wrong_en": "We move Friday can or not?", "note": "完整句更自然。"},
                    {"natural": "我想提醒你一下明天的安排。", "natural_en": "I'd like to remind you about tomorrow's plan.", "wrong": "我提醒你明天安排。", "wrong_en": "I remind you tomorrow arrangement.", "note": "一下更柔和。"},
                    {"natural": "那就这么定了。", "natural_en": "Then let's settle it like that.", "wrong": "那这样结束。", "wrong_en": "Then finish like this.", "note": "定了是高频口语。"},
                ],
                "reflection": [
                    "请录一次礼貌改约，从道歉到新时间。",
                    "你会怎么在前一天提醒别人？",
                    "如果对方周五不方便，你还有什么替代方案？",
                    "练习一次最终敲定时间的表达。",
                ],
            },
        ],
    },
    {
        "number": "79",
        "slug": "FamilyLifeAndFeelings",
        "title": "Confident Chinese: Family, Life and Feelings",
        "subtitle": "家庭、生活与情感表达",
        "color": "#6D4C41",
        "intro_zh": "会说生活，不只是会描述日常，更要会表达压力、感谢、安慰和需要帮助的时候。本书让外国学员在更私人的话题里也能自然开口。",
        "intro_en": "Speaking about life is not only about describing daily routines. It also means being able to express stress, gratitude, comfort, and the need for help. This book helps foreign learners speak naturally even on more personal topics.",
        "method_zh": "从介绍家人和住处，到分享日常和情绪，再到表达感谢与求助，本书帮助学员把中文真正带进生活。",
        "method_en": "From introducing family and your home to sharing daily life and emotions and then expressing thanks and asking for help, this book helps learners bring Chinese into real life.",
        "chapters": [
            {
                "title_zh": "介绍家人和住处",
                "title_en": "Talk About Family and Home",
                "goal_zh": "学会介绍家人、住在哪里、和谁一起住，以及自己现在的生活安排。",
                "goal_en": "Learn to introduce family members, say where you live, who you live with, and what your current life arrangement is.",
                "confidence_tip_zh": "介绍生活时不用面面俱到。先说人，再说地方，再说一个感受就够了。",
                "confidence_tip_en": "When talking about life, you do not need to cover everything. Start with people, then place, then one feeling.",
                "scene_zh": "你和朋友、同学或同事聊自己的家人和居住情况。",
                "scene_en": "You are talking with a friend, classmate, or coworker about your family and living situation.",
                "expressions": [
                    {"zh": "我现在跟室友一起住。", "en": "Right now I live with roommates.", "note": "说明居住状态。"},
                    {"zh": "我家人在国外。", "en": "My family is abroad.", "note": "说明家人位置。"},
                    {"zh": "我平时会跟他们视频。", "en": "I usually video call them.", "note": "补充互动方式。"},
                    {"zh": "我住的地方离公司不远。", "en": "The place I live is not far from the office.", "note": "位置和生活便利。"},
                    {"zh": "我比较喜欢现在的生活节奏。", "en": "I quite like my current pace of life.", "note": "表达感受。"},
                    {"zh": "周末我有时候会自己做饭。", "en": "Sometimes I cook for myself on weekends.", "note": "说日常习惯。"},
                    {"zh": "一个人住也有一个人的好处。", "en": "Living alone also has its own benefits.", "note": "说看法。"},
                    {"zh": "不过我偶尔也会想家。", "en": "But sometimes I also miss home.", "note": "表达情感。"},
                ],
                "frames": [
                    {"zh": "我现在跟……一起住。", "en": "Right now I live with ....", "usage": "介绍同住人。"},
                    {"zh": "我家人在……。", "en": "My family is in ....", "usage": "说家人位置。"},
                    {"zh": "我平时会……。", "en": "I usually ....", "usage": "说习惯。"},
                    {"zh": "我比较喜欢……。", "en": "I quite like ....", "usage": "说感受。"},
                    {"zh": "不过我也会……。", "en": "But I also will ....", "usage": "补充另一面。"},
                ],
                "dialogue": [
                    ("Friend", "你现在一个人住吗？", "Do you live alone now?"),
                    ("Helen", "我现在跟室友一起住。", "Right now I live with roommates."),
                    ("Friend", "你的家人也在中国吗？", "Is your family also in China?"),
                    ("Helen", "没有，我家人在国外。", "No, my family is abroad."),
                    ("Friend", "那你们怎么联系？", "Then how do you stay in touch?"),
                    ("Helen", "我平时会跟他们视频。", "I usually video call them."),
                    ("Friend", "你住得离公司远吗？", "Do you live far from the office?"),
                    ("Helen", "我住的地方离公司不远。", "The place I live is not far from the office."),
                    ("Helen", "我比较喜欢现在的生活节奏，不过我偶尔也会想家。", "I quite like my current pace of life, but I also sometimes miss home."),
                    ("Friend", "很正常。", "That's very normal."),
                ],
                "mistakes": [
                    {"natural": "我现在跟室友一起住。", "natural_en": "Right now I live with roommates.", "wrong": "我现在一起住和室友。", "wrong_en": "I now together live with roommates.", "note": "跟……一起住是整体。"},
                    {"natural": "我家人在国外。", "natural_en": "My family is abroad.", "wrong": "我的家人们在外国。", "wrong_en": "My family members are in foreign country.", "note": "国外更自然。"},
                    {"natural": "我平时会跟他们视频。", "natural_en": "I usually video call them.", "wrong": "我平时跟他们视频电话。", "wrong_en": "I usually video phone them.", "note": "跟……视频最口语。"},
                    {"natural": "我住的地方离公司不远。", "natural_en": "The place I live is not far from the office.", "wrong": "我的住地方不远离公司。", "wrong_en": "My living place not far office.", "note": "住的地方更顺。"},
                    {"natural": "不过我偶尔也会想家。", "natural_en": "But sometimes I also miss home.", "wrong": "但是我会想我的家有时。", "wrong_en": "But I miss my home sometimes.", "note": "想家是固定表达。"},
                ],
                "reflection": [
                    "请录一段介绍你现在和谁住、家人在哪里的表达。",
                    "你平时怎么和家人联系？",
                    "练习一句说喜欢现在生活节奏的话。",
                    "如果你想表达想家，怎么说最自然？",
                ],
            },
            {
                "title_zh": "分享日常、压力和真实感受",
                "title_en": "Share Daily Life and Stress",
                "goal_zh": "学会描述最近的日常节奏、压力来源和自己的真实感受，而不是只说很好。",
                "goal_en": "Learn to describe your recent daily rhythm, sources of stress, and real feelings instead of only saying 'fine'.",
                "confidence_tip_zh": "表达感受时，先说事实，再说感觉，会更真实也更容易懂。",
                "confidence_tip_en": "When expressing feelings, say the facts first and then the feeling. It sounds more real and is easier to understand.",
                "scene_zh": "你在和朋友聊天，想更真实地表达自己最近的状态。",
                "scene_en": "You are chatting with a friend and want to express your recent state more honestly.",
                "expressions": [
                    {"zh": "我最近有点忙。", "en": "I've been a bit busy recently.", "note": "基础状态句。"},
                    {"zh": "这周事情特别多。", "en": "There are especially many things this week.", "note": "描述压力来源。"},
                    {"zh": "我晚上常常睡得不太好。", "en": "I often don't sleep very well at night.", "note": "说具体影响。"},
                    {"zh": "有时候我会觉得有点累。", "en": "Sometimes I feel a bit tired.", "note": "说感受。"},
                    {"zh": "不过整体还可以。", "en": "But overall it's still okay.", "note": "保持平衡语气。"},
                    {"zh": "我最近在努力调整。", "en": "Recently I'm trying to adjust.", "note": "表达积极面。"},
                    {"zh": "跟你聊完我轻松多了。", "en": "After talking with you, I feel much lighter.", "note": "真实互动反馈。"},
                    {"zh": "谢谢你愿意听我说。", "en": "Thank you for being willing to listen to me.", "note": "礼貌而真诚。"},
                ],
                "frames": [
                    {"zh": "我最近有点……。", "en": "I've been a bit ... recently.", "usage": "说近况。"},
                    {"zh": "这周……特别多。", "en": "This week there is especially a lot of ....", "usage": "说压力来源。"},
                    {"zh": "有时候我会觉得……。", "en": "Sometimes I feel ....", "usage": "表达感受。"},
                    {"zh": "不过整体还……。", "en": "But overall it's still ....", "usage": "平衡情绪。"},
                    {"zh": "谢谢你愿意……。", "en": "Thank you for being willing to ....", "usage": "感谢对方。"},
                ],
                "dialogue": [
                    ("Sam", "你最近怎么样？", "How have you been recently?"),
                    ("Lucy", "我最近有点忙。", "I've been a bit busy recently."),
                    ("Lucy", "这周事情特别多。", "There are especially many things this week."),
                    ("Sam", "听起来挺累的。", "That sounds tiring."),
                    ("Lucy", "是啊，我晚上常常睡得不太好。", "Yeah, I often don't sleep very well at night."),
                    ("Lucy", "有时候我会觉得有点累，不过整体还可以。", "Sometimes I feel a bit tired, but overall it's still okay."),
                    ("Sam", "那你现在怎么调整？", "Then how are you adjusting now?"),
                    ("Lucy", "我最近在努力调整。", "Recently I'm trying to adjust."),
                    ("Lucy", "跟你聊完我轻松多了。", "After talking with you, I feel much lighter."),
                    ("Lucy", "谢谢你愿意听我说。", "Thank you for being willing to listen to me."),
                ],
                "mistakes": [
                    {"natural": "我最近有点忙。", "natural_en": "I've been a bit busy recently.", "wrong": "我最近忙一点。", "wrong_en": "I'm busy a little recently.", "note": "有点忙很自然。"},
                    {"natural": "这周事情特别多。", "natural_en": "There are especially many things this week.", "wrong": "这周很多事情特别。", "wrong_en": "This week many things especially.", "note": "特别多是自然组合。"},
                    {"natural": "我晚上常常睡得不太好。", "natural_en": "I often don't sleep very well at night.", "wrong": "我晚上睡不好常常。", "wrong_en": "I at night sleep badly often.", "note": "语序更自然。"},
                    {"natural": "跟你聊完我轻松多了。", "natural_en": "After talking with you, I feel much lighter.", "wrong": "和你聊天以后我更轻松很多。", "wrong_en": "After chatting with you I'm more relaxed a lot.", "note": "多了是高频口语。"},
                    {"natural": "谢谢你愿意听我说。", "natural_en": "Thank you for being willing to listen to me.", "wrong": "谢谢你听我。", "wrong_en": "Thanks you listen me.", "note": "愿意听我说更完整。"},
                ],
                "reflection": [
                    "请录一段真实近况，不要只说很好。",
                    "你最近最累的一件事是什么？",
                    "练习一句“不过整体还可以”的平衡表达。",
                    "你会怎么感谢一个愿意听你说话的人？",
                ],
            },
            {
                "title_zh": "求助、感谢和安慰别人",
                "title_en": "Ask for Help and Offer Comfort",
                "goal_zh": "学会礼貌求助、表达感谢，也能在别人状态不好时给出自然安慰。",
                "goal_en": "Learn to ask for help politely, express gratitude, and also offer natural comfort when someone else is not doing well.",
                "confidence_tip_zh": "求助不是弱，而是清楚表达需要。安慰别人时也不用太复杂，重点是真诚。",
                "confidence_tip_en": "Asking for help is not weakness; it is clear communication of need. When comforting someone, you do not need complex language either. Sincerity matters most.",
                "scene_zh": "你需要请朋友帮忙，或者朋友遇到困难时你想回应一下。",
                "scene_en": "You need to ask a friend for help, or a friend has a problem and you want to respond.",
                "expressions": [
                    {"zh": "你能帮我一个忙吗？", "en": "Can you help me with something?", "note": "求助开头。"},
                    {"zh": "我一个人可能搞不定。", "en": "I might not be able to handle it alone.", "note": "说明原因。"},
                    {"zh": "如果你方便的话。", "en": "If it's convenient for you.", "note": "给对方空间。"},
                    {"zh": "真的太谢谢你了。", "en": "Thank you so much, really.", "note": "加强感谢。"},
                    {"zh": "别太担心。", "en": "Don't worry too much.", "note": "安慰别人。"},
                    {"zh": "慢慢来，没关系。", "en": "Take it slowly, it's okay.", "note": "温和支持。"},
                    {"zh": "如果你想说，我可以听。", "en": "If you want to talk, I can listen.", "note": "很自然的支持句。"},
                    {"zh": "有需要你随时告诉我。", "en": "If you need anything, tell me anytime.", "note": "长期支持。"},
                ],
                "frames": [
                    {"zh": "你能帮我……吗？", "en": "Can you help me ...?", "usage": "直接求助。"},
                    {"zh": "如果你方便的话。", "en": "If it's convenient for you.", "usage": "给空间。"},
                    {"zh": "真的太……了。", "en": "It's really so ....", "usage": "加强感谢。"},
                    {"zh": "别太……。", "en": "Don't ... too much.", "usage": "安慰开场。"},
                    {"zh": "有需要你随时……。", "en": "If needed, you can ... anytime.", "usage": "留支持。"},
                ],
                "dialogue": [
                    ("Mila", "你能帮我一个忙吗？", "Can you help me with something?"),
                    ("June", "可以，怎么了？", "Sure. What's up?"),
                    ("Mila", "我一个人可能搞不定，如果你方便的话，能不能帮我搬一下箱子？", "I might not be able to handle it alone. If it's convenient for you, could you help me move a box?"),
                    ("June", "没问题。", "No problem."),
                    ("Mila", "真的太谢谢你了。", "Thank you so much, really."),
                    ("June", "小事。对了，你看起来有点累。", "It's a small thing. By the way, you look a bit tired."),
                    ("Mila", "是啊，我最近有点烦。", "Yeah, I've been a bit troubled lately."),
                    ("June", "别太担心，慢慢来，没关系。", "Don't worry too much. Take it slowly, it's okay."),
                    ("June", "如果你想说，我可以听。", "If you want to talk, I can listen."),
                    ("June", "有需要你随时告诉我。", "If you need anything, tell me anytime."),
                ],
                "mistakes": [
                    {"natural": "你能帮我一个忙吗？", "natural_en": "Can you help me with something?", "wrong": "你帮我一个忙能吗？", "wrong_en": "You help me a favor can?", "note": "固定问法记整体。"},
                    {"natural": "我一个人可能搞不定。", "natural_en": "I might not be able to handle it alone.", "wrong": "我一个人可能不能做完这个。", "wrong_en": "I alone maybe can't finish this.", "note": "搞不定更口语。"},
                    {"natural": "真的太谢谢你了。", "natural_en": "Thank you so much, really.", "wrong": "真的谢谢很多你。", "wrong_en": "Really thank many you.", "note": "固定感谢表达。"},
                    {"natural": "别太担心。", "natural_en": "Don't worry too much.", "wrong": "不要担心很多。", "wrong_en": "Don't worry a lot.", "note": "别太……更自然。"},
                    {"natural": "如果你想说，我可以听。", "natural_en": "If you want to talk, I can listen.", "wrong": "如果你想，我可以听你说话全部。", "wrong_en": "If you want, I can listen all your words.", "note": "简单更有力量。"},
                ],
                "reflection": [
                    "请练习一次求助，从请求到感谢。",
                    "如果朋友情绪不好，你最想先说哪一句？",
                    "你有没有一句自己最喜欢的安慰表达？",
                    "录一段既请求帮助又给对方空间的话。",
                ],
            },
        ],
    },
    {
        "number": "80",
        "slug": "OpinionsAndPoliteBoundaries",
        "title": "Confident Chinese: Opinions and Polite Boundaries",
        "subtitle": "观点、建议与礼貌拒绝表达",
        "color": "#546E7A",
        "intro_zh": "真正自信的中文表达，不只是敢说喜欢，也包括敢说不同意、敢提建议、敢表达边界，而且还能保持礼貌。",
        "intro_en": "Truly confident Chinese is not only about daring to say what you like. It also means daring to disagree, offer suggestions, and state boundaries while remaining polite.",
        "method_zh": "本书从同意与不同意、提建议与委婉纠正，到表达边界和礼貌拒绝，帮助学员建立成熟的中文表达能力。",
        "method_en": "This book moves from agreement and disagreement to giving suggestions and soft corrections, and then to stating boundaries and polite refusals so learners can develop more mature Chinese expression.",
        "chapters": [
            {
                "title_zh": "表达同意和不同意",
                "title_en": "Agree and Disagree Clearly",
                "goal_zh": "学会自然表达同意、部分同意和不同意，不显得太生硬。",
                "goal_en": "Learn to express agreement, partial agreement, and disagreement naturally without sounding too harsh.",
                "confidence_tip_zh": "不同意时先接住对方一点，再说自己的看法，听起来会更舒服。",
                "confidence_tip_en": "When you disagree, acknowledge one part first and then say your own view. It sounds much smoother.",
                "scene_zh": "你在讨论、聊天或会议中需要表达自己的看法。",
                "scene_en": "You need to express your view in a discussion, casual chat, or meeting.",
                "expressions": [
                    {"zh": "我同意你的看法。", "en": "I agree with your view.", "note": "直接同意。"},
                    {"zh": "我基本上同意。", "en": "I basically agree.", "note": "保留空间。"},
                    {"zh": "这个角度我能理解。", "en": "I can understand this angle.", "note": "先接住对方。"},
                    {"zh": "不过我有不同的想法。", "en": "But I have a different thought.", "note": "柔和转折。"},
                    {"zh": "我不完全这么看。", "en": "I don't see it completely that way.", "note": "委婉不同意。"},
                    {"zh": "也许我们可以换个角度看。", "en": "Maybe we can look at it from another angle.", "note": "转向讨论。"},
                    {"zh": "对我来说，重点不太一样。", "en": "For me, the key point is a bit different.", "note": "表达个人立场。"},
                    {"zh": "我想听听你的理由。", "en": "I'd like to hear your reasons.", "note": "保持对话开放。"},
                ],
                "frames": [
                    {"zh": "我……你的看法。", "en": "I ... your view.", "usage": "表达同意。"},
                    {"zh": "不过我有……。", "en": "But I have ....", "usage": "转入不同意见。"},
                    {"zh": "我不完全……。", "en": "I don't completely ....", "usage": "委婉保留。"},
                    {"zh": "也许我们可以……。", "en": "Maybe we can ....", "usage": "拉回讨论。"},
                    {"zh": "对我来说，……。", "en": "For me, ....", "usage": "说明个人角度。"},
                ],
                "dialogue": [
                    ("A", "我觉得这个方案已经很好了。", "I think this plan is already very good."),
                    ("B", "我基本上同意。", "I basically agree."),
                    ("B", "这个角度我能理解。", "I can understand this angle."),
                    ("A", "那你还有别的想法吗？", "Then do you have other thoughts?"),
                    ("B", "不过我有不同的想法。", "But I do have a different thought."),
                    ("B", "我不完全这么看。", "I don't see it completely that way."),
                    ("A", "为什么？", "Why?"),
                    ("B", "对我来说，重点不太一样。", "For me, the key point is a bit different."),
                    ("B", "也许我们可以换个角度看。", "Maybe we can look at it from another angle."),
                    ("B", "我想听听你的理由。", "I'd like to hear your reasons."),
                ],
                "mistakes": [
                    {"natural": "我基本上同意。", "natural_en": "I basically agree.", "wrong": "我同意基本。", "wrong_en": "I agree basically.", "note": "基本上放前面。"},
                    {"natural": "不过我有不同的想法。", "natural_en": "But I have a different thought.", "wrong": "但是我有不一样想法一个。", "wrong_en": "But I have different thought one.", "note": "说法要简洁。"},
                    {"natural": "我不完全这么看。", "natural_en": "I don't see it completely that way.", "wrong": "我不这样完全看。", "wrong_en": "I don't this way completely see.", "note": "固定块更自然。"},
                    {"natural": "也许我们可以换个角度看。", "natural_en": "Maybe we can look at it from another angle.", "wrong": "我们可以看另外角度也许。", "wrong_en": "We can look another angle maybe.", "note": "也许放前面更柔和。"},
                    {"natural": "对我来说，重点不太一样。", "natural_en": "For me, the key point is a bit different.", "wrong": "对我重点不一样。", "wrong_en": "To me key point different.", "note": "对我来说是完整结构。"},
                ],
                "reflection": [
                    "请录一段先同意一点、再表达不同意见的回答。",
                    "你最喜欢哪一种委婉不同意的说法？",
                    "如果对方比你强势，你会怎么柔和地表达不同意？",
                    "练习一次“对我来说……”的个人立场句。",
                ],
            },
            {
                "title_zh": "提建议和委婉纠正",
                "title_en": "Give Suggestions Softly",
                "goal_zh": "学会提出建议、委婉纠正别人，以及在不冒犯对方的情况下表达更好的做法。",
                "goal_en": "Learn to give suggestions, correct someone gently, and express a better way without offending the other person.",
                "confidence_tip_zh": "提建议时不要只说错了，最好加一个更好的替代方案。",
                "confidence_tip_en": "When giving a suggestion, do not only say something is wrong. Add a better alternative too.",
                "scene_zh": "你在工作、学习或生活里想给别人一点建议。",
                "scene_en": "You want to give someone a bit of advice in work, study, or life.",
                "expressions": [
                    {"zh": "我有一个小建议。", "en": "I have a small suggestion.", "note": "柔和开头。"},
                    {"zh": "也许这样会更好。", "en": "Maybe this would be better.", "note": "高频建议句。"},
                    {"zh": "我们是不是可以先……？", "en": "Could we first ...?", "note": "用疑问句更柔和。"},
                    {"zh": "如果改成这个，可能会更清楚。", "en": "If we change it to this, it might be clearer.", "note": "给替代方案。"},
                    {"zh": "我不是说现在这样不行。", "en": "I'm not saying the current way doesn't work.", "note": "降低冲突。"},
                    {"zh": "我只是觉得可以再优化一下。", "en": "I just think it could be optimized a bit more.", "note": "缓和语气。"},
                    {"zh": "你觉得这样怎么样？", "en": "What do you think about doing it this way?", "note": "把球交回去。"},
                    {"zh": "我们可以先试一次。", "en": "We can try it once first.", "note": "让建议更容易接受。"},
                ],
                "frames": [
                    {"zh": "我有一个小……。", "en": "I have a small ....", "usage": "提建议。"},
                    {"zh": "也许……会更好。", "en": "Maybe ... would be better.", "usage": "给方向。"},
                    {"zh": "如果改成……，可能会……。", "en": "If we change it to ..., it might ....", "usage": "给替代。"},
                    {"zh": "我只是觉得……。", "en": "I just think ....", "usage": "降低冲突。"},
                    {"zh": "你觉得……怎么样？", "en": "What do you think about ...?", "usage": "邀对方回应。"},
                ],
                "dialogue": [
                    ("A", "这个版本你看过了吗？", "Have you looked at this version?"),
                    ("B", "看过了。我有一个小建议。", "Yes. I have a small suggestion."),
                    ("A", "你说。", "Go ahead."),
                    ("B", "也许这样会更好。", "Maybe this would be better."),
                    ("B", "我们是不是可以先把重点放前面？", "Could we put the key point first?"),
                    ("A", "为什么？", "Why?"),
                    ("B", "如果改成这个，可能会更清楚。", "If we change it to this, it might be clearer."),
                    ("B", "我不是说现在这样不行，我只是觉得可以再优化一下。", "I'm not saying the current way doesn't work; I just think it could be optimized a bit more."),
                    ("A", "听起来有道理。", "That sounds reasonable."),
                    ("B", "你觉得这样怎么样？我们可以先试一次。", "What do you think about doing it this way? We can try it once first."),
                ],
                "mistakes": [
                    {"natural": "我有一个小建议。", "natural_en": "I have a small suggestion.", "wrong": "我有一个建议小。", "wrong_en": "I have a suggestion small.", "note": "小建议是固定组合。"},
                    {"natural": "也许这样会更好。", "natural_en": "Maybe this would be better.", "wrong": "这样也许更好的。", "wrong_en": "This maybe better.", "note": "会更好更自然。"},
                    {"natural": "如果改成这个，可能会更清楚。", "natural_en": "If we change it to this, it might be clearer.", "wrong": "改这个可能清楚。", "wrong_en": "Change this maybe clear.", "note": "完整条件句更柔和。"},
                    {"natural": "我只是觉得可以再优化一下。", "natural_en": "I just think it could be optimized a bit more.", "wrong": "我只是想优化。", "wrong_en": "I just want optimize.", "note": "觉得可以……一下更自然。"},
                    {"natural": "我们可以先试一次。", "natural_en": "We can try it once first.", "wrong": "我们先一次试。", "wrong_en": "We first once try.", "note": "先试一次是高频块。"},
                ],
                "reflection": [
                    "请录一次给建议的表达，不要显得太硬。",
                    "你最喜欢用哪句来降低冲突？",
                    "如果你要纠正别人，怎么先接住对方？",
                    "练习一次给建议并邀请对方反馈。",
                ],
            },
            {
                "title_zh": "表达边界和礼貌拒绝",
                "title_en": "State Boundaries Politely",
                "goal_zh": "学会表达自己不想做、做不到或不太方便的事情，同时保持礼貌和清楚。",
                "goal_en": "Learn to say that you don't want to do something, can't do it, or that it isn't convenient, while staying polite and clear.",
                "confidence_tip_zh": "边界表达越清楚，对关系反而越轻松。关键不是强硬，而是明确。",
                "confidence_tip_en": "The clearer your boundaries are, the easier the relationship often becomes. The key is not harshness but clarity.",
                "scene_zh": "你需要拒绝请求、推掉安排，或者说明自己现在不能接受某件事。",
                "scene_en": "You need to refuse a request, turn down a plan, or explain that you cannot accept something right now.",
                "expressions": [
                    {"zh": "不好意思，这个我可能帮不了。", "en": "Sorry, I probably can't help with this.", "note": "清楚拒绝帮助。"},
                    {"zh": "我现在不太方便。", "en": "It's not very convenient for me right now.", "note": "说当前边界。"},
                    {"zh": "这个我需要再考虑一下。", "en": "I need to think about this a bit more.", "note": "暂不答应。"},
                    {"zh": "我可能没办法参加。", "en": "I may not be able to attend.", "note": "推掉安排。"},
                    {"zh": "谢谢你想到我。", "en": "Thank you for thinking of me.", "note": "先表达善意。"},
                    {"zh": "不过这次我还是先不去了。", "en": "But this time I'll pass for now.", "note": "柔和拒绝。"},
                    {"zh": "如果以后合适，我再告诉你。", "en": "If it works in the future, I'll let you know.", "note": "留空间。"},
                    {"zh": "希望你能理解。", "en": "I hope you can understand.", "note": "收尾清楚。"},
                ],
                "frames": [
                    {"zh": "不好意思，这个我……。", "en": "Sorry, I ....", "usage": "拒绝开头。"},
                    {"zh": "我现在不太……。", "en": "Right now I'm not very ....", "usage": "说明限制。"},
                    {"zh": "这个我需要再……。", "en": "I need to ... this a bit more.", "usage": "暂缓回应。"},
                    {"zh": "不过这次我还是……。", "en": "But this time I will still ....", "usage": "明确决定。"},
                    {"zh": "如果以后……，我再……。", "en": "If in the future ..., then I'll ....", "usage": "留下后续。"},
                ],
                "dialogue": [
                    ("A", "这周末你能来帮我们搬家吗？", "Can you come help us move this weekend?"),
                    ("B", "不好意思，这个我可能帮不了。", "Sorry, I probably can't help with this."),
                    ("A", "怎么了？", "What happened?"),
                    ("B", "我现在不太方便。", "It's not very convenient for me right now."),
                    ("B", "这个我需要再考虑一下，不过这次我还是先不去了。", "I need to think about this a bit more, but this time I'll pass for now."),
                    ("A", "好吧。", "Okay."),
                    ("B", "谢谢你想到我。", "Thank you for thinking of me."),
                    ("B", "我可能没办法参加。", "I may not be able to attend."),
                    ("B", "如果以后合适，我再告诉你。", "If it works in the future, I'll let you know."),
                    ("B", "希望你能理解。", "I hope you can understand."),
                ],
                "mistakes": [
                    {"natural": "不好意思，这个我可能帮不了。", "natural_en": "Sorry, I probably can't help with this.", "wrong": "这个我不帮。", "wrong_en": "I don't help with this.", "note": "柔和拒绝更自然。"},
                    {"natural": "我现在不太方便。", "natural_en": "It's not very convenient for me right now.", "wrong": "我现在没有方便。", "wrong_en": "I don't have convenience now.", "note": "固定表达记整体。"},
                    {"natural": "这个我需要再考虑一下。", "natural_en": "I need to think about this a bit more.", "wrong": "这个我要想。", "wrong_en": "This I need think.", "note": "考虑一下更柔和。"},
                    {"natural": "不过这次我还是先不去了。", "natural_en": "But this time I'll pass for now.", "wrong": "但是这次我不去先。", "wrong_en": "But this time I not go first.", "note": "先不去了很常见。"},
                    {"natural": "如果以后合适，我再告诉你。", "natural_en": "If it works in the future, I'll let you know.", "wrong": "以后合适我告诉你。", "wrong_en": "Future suitable I tell you.", "note": "条件句更完整。"},
                ],
                "reflection": [
                    "请录一段礼貌拒绝别人请求的表达。",
                    "如果你真的现在不方便，怎么说更自然？",
                    "你更喜欢直接拒绝还是先感谢再拒绝？",
                    "练习一次既拒绝又保留未来空间的话。",
                ],
            },
        ],
    },
]


def main() -> None:
    ensure_dirs()
    write_plan(BOOKS)

    for book in BOOKS:
        folder = DEST_ROOT / f"Book{book['number']}_{book['slug']}"
        folder.mkdir(parents=True, exist_ok=True)
        stem = f"ZTurns_Book{book['number']}_{book['slug']}"
        md_path = folder / f"{stem}.md"
        pdf_path = folder / f"{stem}.pdf"

        md_path.write_text(build_book_md(book), encoding="utf-8")
        compile_book(book, md_path, pdf_path)

        pages = pdf_pages(pdf_path)
        if pages < 50:
            raise RuntimeError(f"{pdf_path} only has {pages} pages; expected at least 50.")
        print(f"✓ Book {book['number']} generated: {md_path.name} / {pdf_path.name} ({pages} pages)")


if __name__ == "__main__":
    main()
