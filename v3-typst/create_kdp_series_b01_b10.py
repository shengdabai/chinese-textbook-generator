#!/usr/bin/env python3
"""Create a fresh Book01-10 Amazon/KDP-oriented Chinese learning series.

This script:
1. Creates a brand-new standalone folder for the series.
2. Generates a planning markdown file.
3. Expands each book into 12 chapters.
4. Compiles each book to PDF in a trim size closer to Amazon/KDP (6x9).
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from pypinyin import Style, pinyin


BASE_DIR = Path("../..")
V3_DIR = BASE_DIR / "生成工具" / "v3-typst"
TARGET_ROOT = BASE_DIR / "中文教材" / "Amazon_KDP_中文学习系列_1-10"
TEMPLATE_PATH = V3_DIR / "templates" / "textbook.typ"

sys.path.insert(0, str(V3_DIR))

from filters.content_filter import ContentFilter  # type: ignore
from parsers.md_parser import MarkdownParser  # type: ignore
from renderers.typst_renderer import TypstRenderer  # type: ignore
from create_amazon_b71_b80 import BOOKS as SOURCE_BOOKS  # type: ignore


FILTER = ContentFilter(str(V3_DIR / "config" / "filter_rules.yaml"))
PARSER = MarkdownParser()
RENDERER = TypstRenderer()


@dataclass(frozen=True)
class KdpBookMeta:
    number: str
    slug: str
    title: str
    subtitle: str
    tagline: str
    color: str


SERIES_META: list[KdpBookMeta] = [
    KdpBookMeta(
        number="01",
        slug="SpeakChineseInChina",
        title="Speak Chinese in China",
        subtitle="生存中文 · 15 Essential Survival Scenarios for Adult Beginners",
        tagline="Airports, taxis, hotels, food, directions, and daily problem-solving in real Chinese.",
        color="#D1495B",
    ),
    KdpBookMeta(
        number="02",
        slug="DailyChineseConversations",
        title="101 Daily Chinese Conversations",
        subtitle="日常会话中文 · Natural Beginner Dialogues for Real Life",
        tagline="Greetings, schedules, feelings, invitations, and everyday speaking confidence.",
        color="#2A9D8F",
    ),
    KdpBookMeta(
        number="03",
        slug="MandarinPronunciation",
        title="Mandarin Pronunciation for Adult Beginners",
        subtitle="发音入门 · Pinyin, Tones, and the Sounds Foreigners Confuse Most",
        tagline="A practical pronunciation book built for clarity, confidence, and real conversation.",
        color="#264653",
    ),
    KdpBookMeta(
        number="04",
        slug="ChineseGrammarMadePractical",
        title="Chinese Grammar Made Practical",
        subtitle="实用语法 · The Everyday Patterns Beginners Need Most",
        tagline="Time, numbers, sentence order, 不, 没, and the grammar that actually shows up in life.",
        color="#8AB17D",
    ),
    KdpBookMeta(
        number="05",
        slug="OrderFoodWithConfidence",
        title="Order Food with Confidence in Chinese",
        subtitle="餐馆中文 · Menus, Taste, Bills, and Food Culture Across China",
        tagline="Learn to order, describe flavors, pay the bill, and talk about food naturally.",
        color="#F4A261",
    ),
    KdpBookMeta(
        number="06",
        slug="DigitalLifeInChina",
        title="Digital Life in China",
        subtitle="数字生活中文 · WeChat, Alipay, Delivery, Didi, and QR Code Survival",
        tagline="The Chinese you need for mobile payment, apps, ride-hailing, and China’s phone-first life.",
        color="#577590",
    ),
    KdpBookMeta(
        number="07",
        slug="BusinessChineseThatGetsThingsDone",
        title="Business Chinese That Gets Things Done",
        subtitle="商务中文 · Prices, MOQs, Delivery, and Supplier Follow-Ups",
        tagline="Short, useful Chinese for buyers, suppliers, distributors, and real work conversations.",
        color="#C1121F",
    ),
    KdpBookMeta(
        number="08",
        slug="ChineseFestivalsAndTraditions",
        title="Learn Chinese Through Chinese Festivals",
        subtitle="节日文化中文 · Spring Festival, Lantern Festival, Mid-Autumn, and Dragon Boat",
        tagline="Memorable Chinese through holidays, greetings, food, gifting, and family traditions.",
        color="#D62828",
    ),
    KdpBookMeta(
        number="09",
        slug="SocialChineseAndEtiquette",
        title="Social Chinese and Cultural Etiquette",
        subtitle="社交中文 · Titles, Invitations, Refusals, Gratitude, and Face",
        tagline="Sound warmer, more natural, and more culturally fluent in real relationships.",
        color="#9C6644",
    ),
    KdpBookMeta(
        number="10",
        slug="EverydayServicesInChinese",
        title="Everyday Services in Chinese",
        subtitle="生活服务中文 · Shopping, Haircuts, Pharmacies, Returns, and Customer Service",
        tagline="Chinese for the errands, fixes, and service moments that make daily life feel real.",
        color="#6D597A",
    ),
]


def zh_pinyin(text: str) -> str:
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


def typst_escape_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def md_to_body(md_path: Path) -> str:
    raw = md_path.read_text(encoding="utf-8")
    result = FILTER.filter(raw)
    nodes = PARSER.parse(result.text)
    return RENDERER.render(nodes, annotate=False)


def build_template() -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    template = template.replace(
        'paper: "a4",\n  margin: (x: 18mm, y: 20mm),',
        'width: 6in,\n  height: 9in,\n  margin: (x: 14mm, y: 16mm),',
    )
    template = template.replace(
        '#let accent = rgb(book-color)\n',
        '#let accent = rgb(book-color)\n#let book-tagline = ""\n',
    )
    template = template.replace(
        '#text(size: 18pt, fill: accent)[#book-subtitle]\n'
        '        #v(1.2cm)\n',
        '#text(size: 16pt, fill: accent)[#book-subtitle]\n'
        '        #v(0.45cm)\n'
        '        #text(size: 10.5pt, fill: rgb("#667085"))[#book-tagline]\n'
        '        #v(0.9cm)\n',
    )
    template = template.replace(
        '© 2026 Z Turns Chinese. All rights reserved.\\\n'
        '    No part of this publication may be reproduced, distributed, or transmitted\n'
        '    in any form or by any means without the prior written permission of the\n'
        '    publisher, except in the case of brief quotations embodied in critical\n'
        '    reviews and certain other noncommercial uses permitted by copyright law.\\\n'
        '    \\\n'
        '    For permissions, contact: #link("mailto:tony@zturnsgo.com")[tony\\@zturnsgo.com]',
        'Series: Z Turns Chinese — Amazon KDP Edition\\\n'
        '    Author: Tony Sheng\\\n'
        '    Website: zturnsgo.com\\\n'
        '    \\\n'
        '    Copyright © 2026 Z Turns Chinese. All rights reserved.\\\n'
        '    No part of this publication may be reproduced, stored, or transmitted in any form\n'
        '    without prior written permission from the publisher, except for brief quotations\n'
        '    in reviews and educational references permitted by copyright law.\\\n'
        '    \\\n'
        '    This edition is designed for adult learners of Chinese and created from real-world\n'
        '    teaching scenarios, practical speaking patterns, and cultural notes for English-speaking learners.\\\n'
        '    \\\n'
        '    For permissions or bulk licensing, contact: #link("mailto:tony@zturnsgo.com")[tony\\@zturnsgo.com]',
    )
    return template


KDP_TEMPLATE = build_template()


def compile_typ(typ_src: str, out_pdf: Path) -> None:
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".typ", dir=str(V3_DIR / "templates"), delete=False, encoding="utf-8") as f:
        f.write(typ_src)
        tmp_path = Path(f.name)
    try:
        result = subprocess.run(
            ["typst", "compile", str(tmp_path), str(out_pdf)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Typst compile failed for {out_pdf.name}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )
    finally:
        tmp_path.unlink(missing_ok=True)


def render_vocab_table(vocab: list[tuple[str, str, str]]) -> str:
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
    return "\n".join(
        f"{idx}. **{pattern}** — {meaning} Example: {example} ({zh_pinyin(example)})"
        for idx, (pattern, meaning, example) in enumerate(patterns, start=1)
    )


def power_sentences(module) -> list[tuple[str, str]]:
    sentences: list[tuple[str, str]] = []
    for _, zh, en in module.dialogue[:3]:
        sentences.append((zh, en))
    for _, _, example in module.patterns[:2]:
        sentences.append((example, "Pattern example"))
    return sentences[:5]


def render_power_sentences(module) -> str:
    lines = [
        "| Chinese | Pronunciation | English |",
        "|---|---|---|",
    ]
    for zh, en in power_sentences(module):
        lines.append(f"| {zh} | {zh_pinyin(zh)} | {en} |")
    return "\n".join(lines)


def line_takeaways(module) -> str:
    items = []
    for speaker, zh, en in module.dialogue[:4]:
        items.append(
            f"- **{speaker}:** {zh} ({zh_pinyin(zh)}) — {en}"
        )
    return "\n".join(items)


def substitution_drills(module) -> str:
    drills = []
    for pattern, meaning, example in module.patterns:
        drills.append(f"- Say this pattern aloud: **{pattern}**")
        drills.append(f"- Replace one key word in: {example}")
        drills.append(f"- Use it once for your own life: {meaning}")
    return "\n".join(drills[:6])


def common_mistakes(module) -> str:
    focus_words = [v[0] for v in module.vocab[:3]]
    pattern_examples = [p[2] for p in module.patterns[:2]]
    lines = [
        f"- Do not translate English word for word. Short Chinese chunks like **{focus_words[0]}** and **{focus_words[1]}** usually sound better.",
        f"- If you are nervous, use the ready-made sentence **{pattern_examples[0]}** instead of building a long sentence from scratch.",
        f"- Keep your tone polite and steady. In real life, clarity plus rhythm often matters more than perfect tones, especially with phrases like **{focus_words[2]}**.",
    ]
    return "\n".join(lines)


def extended_example(module) -> str:
    zh_lines = [zh for _, zh, _ in module.dialogue[:4]]
    en_lines = [en for _, _, en in module.dialogue[:4]]
    zh_text = " ".join(zh_lines)
    en_text = " ".join(en_lines)
    py_text = zh_pinyin(zh_text)
    return (
        f"**Chinese:** {zh_text}\n\n"
        f"**Pronunciation:** {py_text}\n\n"
        f"**English:** {en_text}"
    )


def chapter_type_title(base: str, variant: int) -> str:
    if variant == 1:
        return f"{base} — Core Vocabulary and Power Sentences"
    if variant == 2:
        return f"{base} — Dialogue Lab and Pattern Practice"
    return f"{base} — Culture, Mistakes, and Fluency"


def render_chapter_one(module, book_title: str) -> str:
    return (
        "## Situation\n\n"
        f"{module.situation}\n\n"
        "## Why This Chapter Matters\n\n"
        f"This chapter helps you turn a high-pressure real-life moment from **{book_title}** into a small set of Chinese phrases you can actually use. "
        "The goal is not perfection. The goal is being understood quickly, politely, and confidently.\n\n"
        "## Key Vocabulary\n\n"
        f"{render_vocab_table(module.vocab)}\n\n"
        "## Five Power Sentences\n\n"
        f"{render_power_sentences(module)}\n\n"
        "## Quick Drill\n\n"
        "- Read each vocabulary item aloud three times.\n"
        "- Cover the English and try to explain the Chinese meaning from memory.\n"
        "- Use at least two words in one short sentence.\n\n"
        "## Mini Challenge\n\n"
        "- Say one sentence you would actually use in this situation.\n"
        "- Say the same sentence again, but slower and more naturally.\n"
    )


def render_chapter_two(module) -> str:
    return (
        "## Scene Dialogue\n\n"
        f"{render_dialogue_table(module.dialogue)}\n\n"
        "## Line-by-Line Takeaways\n\n"
        f"{line_takeaways(module)}\n\n"
        "## High-Frequency Patterns\n\n"
        f"{render_patterns(module.patterns)}\n\n"
        "## Substitution Drills\n\n"
        f"{substitution_drills(module)}\n\n"
        "## Shadowing Practice\n\n"
        "- Read the dialogue once for meaning.\n"
        "- Read it again while copying the rhythm.\n"
        "- Read it a third time without looking at the English.\n"
    )


def render_chapter_three(module) -> str:
    return (
        "## Culture Note\n\n"
        f"{module.culture_note}\n\n"
        "## Common Mistakes Learners Make\n\n"
        f"{common_mistakes(module)}\n\n"
        "## Extended Example\n\n"
        f"{extended_example(module)}\n\n"
        "## Review Checklist\n\n"
        "- I can say the key phrases without reading every word.\n"
        "- I understand when to use the polite opener in this scene.\n"
        "- I can explain one cultural detail in English after reading this chapter.\n\n"
        "## Self-Study Prompt\n\n"
        "- Record yourself speaking one useful sentence from this chapter.\n"
        "- Rewrite one dialogue line so it fits your own life.\n"
    )


def build_book_md(meta: KdpBookMeta, source_book) -> str:
    modules = source_book.units
    lines = [
        f"# Z Turns Chinese Book {meta.number}",
        f"## {meta.title}",
        f"**Author:** Tony Sheng",
        f"**Series:** Amazon KDP Chinese Learning Collection",
        f"**Website:** zturnsgo.com",
        f"**Teaching Foundation:** Based on real Chinese teaching scenarios and English-speaker learner needs.",
        f"**Book Positioning:** {meta.tagline}",
        f"**Source Knowledge Notes:** {', '.join(source_book.source_notes)}",
        "",
        "---",
        "",
        "# Table of Contents",
        "",
    ]

    toc: list[str] = []
    chapter_number = 1
    for module in modules:
        for variant in (1, 2, 3):
            toc.append(f"{chapter_number}. {chapter_type_title(module.title, variant)}")
            chapter_number += 1
    lines.extend(toc)
    lines.extend(["", "---", ""])

    chapter_number = 1
    for part_index, module in enumerate(modules, start=1):
        lines.extend([f"## Part {part_index}", "", f"**Theme:** {module.title}", ""])
        for variant in (1, 2, 3):
            lines.append(f"# Chapter {chapter_number}: {chapter_type_title(module.title, variant)}")
            lines.append("")
            if variant == 1:
                lines.append(render_chapter_one(module, meta.title))
            elif variant == 2:
                lines.append(render_chapter_two(module))
            else:
                lines.append(render_chapter_three(module))
            lines.extend(["", "---", ""])
            chapter_number += 1

    lines.extend(
        [
            "# Final Review and Study Plan",
            "",
            "## How to Use This Book",
            "",
            "1. Read one chapter for input.",
            "2. Repeat the power sentences aloud.",
            "3. Shadow the dialogue until it feels smoother.",
            "4. Reuse one pattern in your own life.",
            "",
            "## What Makes This Book Different",
            "",
            "- Real scenarios instead of textbook abstraction.",
            "- English support without destroying Chinese sentence rhythm.",
            "- Cultural explanation so the language feels meaningful, not random.",
            "- Short patterns you can actually remember and reuse.",
            "",
            "## Next Step",
            "",
            "When you can read the dialogue aloud without following every English line, you are no longer only studying Chinese — you are starting to think in usable Chinese.",
            "",
        ]
    )
    return "\n".join(lines)


def build_plan_md() -> str:
    lines = [
        "# Amazon / KDP 中文学习系列 Book01-10",
        "",
        "这是独立新建的一套 1-10 系列，不复用 71-80 书号。",
        "",
        "设计目标：",
        "",
        "- 更适合 Amazon / KDP 的标题与副标题",
        "- 每本书扩展为 12 章完整版",
        "- 保持结构：场景对话 + 拼音 + 英文翻译 + 高频句型 + 文化解释",
        "- 主题优先覆盖外国学员最愿意购买的中文学习方向",
        "",
        "## 选题总览",
        "",
    ]
    for meta, source_book in zip(SERIES_META, SOURCE_BOOKS):
        lines.extend(
            [
                f"## Book {meta.number}: {meta.title}",
                "",
                f"- 副标题：{meta.subtitle}",
                f"- 封面卖点：{meta.tagline}",
                f"- 基础模块：",
            ]
        )
        for unit in source_book.units:
            lines.append(f"  - {unit.title}")
        lines.extend(
            [
                "- 章节扩展方式：每个模块拆成 3 章",
                "  - Core Vocabulary and Power Sentences",
                "  - Dialogue Lab and Pattern Practice",
                "  - Culture, Mistakes, and Fluency",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def build_typst_source(meta: KdpBookMeta, md_path: Path) -> str:
    body = md_to_body(md_path)
    return (
        f'#let book-number = "{typst_escape_string(meta.number)}"\n'
        f'#let book-title = "{typst_escape_string(meta.title)}"\n'
        f'#let book-subtitle = "{typst_escape_string(meta.subtitle)}"\n'
        f'#let book-tagline = "{typst_escape_string(meta.tagline)}"\n'
        f'#let book-color = "{typst_escape_string(meta.color)}"\n\n'
        f"{KDP_TEMPLATE}\n\n"
        f"{body}\n"
    )


def main() -> None:
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)

    plan_path = TARGET_ROOT / "KDP_Book01-10_选题与目录.md"
    plan_path.write_text(build_plan_md(), encoding="utf-8")

    generated: list[str] = []
    for meta, source_book in zip(SERIES_META, SOURCE_BOOKS):
        folder = TARGET_ROOT / f"Book{meta.number}_{meta.slug}"
        folder.mkdir(parents=True, exist_ok=True)
        md_path = folder / f"ZTurns_Book{meta.number}_{meta.slug}.md"
        pdf_path = folder / f"ZTurns_Book{meta.number}_{meta.slug}.pdf"

        md_text = build_book_md(meta, source_book)
        md_path.write_text(md_text, encoding="utf-8")

        typ_src = build_typst_source(meta, md_path)
        compile_typ(typ_src, pdf_path)

        generated.append(f"- {md_path}")
        generated.append(f"- {pdf_path}")

    summary_path = TARGET_ROOT / "GENERATED_FILES.md"
    summary_path.write_text("# Generated Files\n\n" + "\n".join(generated) + "\n", encoding="utf-8")

    print(f"Generated standalone KDP series at: {TARGET_ROOT}")


if __name__ == "__main__":
    main()
