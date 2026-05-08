#!/usr/bin/env python3
"""
Z Turns Chinese — Markdown-to-PDF book generator.
Generates Books 2-5 from source markdown files.
"""

import os
import re
import sys
from pathlib import Path
from fpdf import FPDF, XPos, YPos
from fpdf.enums import Align

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# CJK font — try in order until one works
FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/STHeiti Medium.ttc",
]

# ─────────────────────────────────────────────
# Book metadata
# ─────────────────────────────────────────────
BOOKS = {
    "book2": {
        "title": "Z Turns Chinese",
        "subtitle": "The Complete Guide to Conversational Chinese",
        "zh_title": "完整会话中文指南",
        "author": "Tony Sheng",
        "color": (0, 150, 80),
        "output": "ZTurns_Book2_CompleteGuide.pdf",
        "source_dirs": [
            "part0-before-you-begin",
            "part1-sound-foundation",
            "part2-first-steps",
            "part3-daily-life",
            "part4-travel-adventure",
            "part5-business-chinese",
            "part6-living-in-china",
        ],
        "part_names": {
            "part0-before-you-begin": "Part 0: Before You Begin",
            "part1-sound-foundation": "Part 1: Sound Foundation",
            "part2-first-steps": "Part 2: First Steps",
            "part3-daily-life": "Part 3: Daily Life",
            "part4-travel-adventure": "Part 4: Travel & Adventure",
            "part5-business-chinese": "Part 5: Business Chinese",
            "part6-living-in-china": "Part 6: Living in China",
        },
    },
    "book3": {
        "title": "Z Turns Chinese",
        "subtitle": "Real Lessons from Real Classrooms",
        "zh_title": "真实课堂的真实课程",
        "author": "Tony Sheng",
        "color": (180, 50, 30),
        "output": "ZTurns_Book3_RealLessons.pdf",
        "source_dirs": [
            "book3-real-lessons/part1-daily-basics",
            "book3-real-lessons/part2-travel-stories",
            "book3-real-lessons/part3-culture-unlocked",
            "book3-real-lessons/part4-business-modern",
            "book3-real-lessons/part5-going-deeper",
            "book3-real-lessons/reviews",
        ],
        "part_names": {
            "book3-real-lessons/part1-daily-basics": "Part 1: Daily Basics",
            "book3-real-lessons/part2-travel-stories": "Part 2: Travel Stories",
            "book3-real-lessons/part3-culture-unlocked": "Part 3: Culture Unlocked",
            "book3-real-lessons/part4-business-modern": "Part 4: Business Modern",
            "book3-real-lessons/part5-going-deeper": "Part 5: Going Deeper",
            "book3-real-lessons/reviews": "Review Sections",
        },
    },
    "book4": {
        "title": "Z Turns Chinese",
        "subtitle": "Survival Chinese",
        "zh_title": "生存中文",
        "author": "Tony Sheng",
        "color": (200, 120, 0),
        "output": "ZTurns_Book4_SurvivalChinese.pdf",
        "source_dirs": [
            "book4-survival-chinese/sec1-essentials",
            "book4-survival-chinese/sec2-eating",
            "book4-survival-chinese/sec3-transport",
            "book4-survival-chinese/sec4-money",
            "book4-survival-chinese/sec5-emergency",
        ],
        "part_names": {
            "book4-survival-chinese/sec1-essentials": "Section 1: Essentials",
            "book4-survival-chinese/sec2-eating": "Section 2: Eating",
            "book4-survival-chinese/sec3-transport": "Section 3: Transport",
            "book4-survival-chinese/sec4-money": "Section 4: Money",
            "book4-survival-chinese/sec5-emergency": "Section 5: Emergency",
        },
    },
    "book5": {
        "title": "Z Turns Chinese",
        "subtitle": "Business Chinese That Actually Works",
        "zh_title": "真正管用的商务中文",
        "author": "Tony Sheng",
        "color": (100, 50, 150),
        "output": "ZTurns_Book5_BusinessChinese.pdf",
        "source_dirs": [
            "book5-business-chinese/part1-first-30-days",
            "book5-business-chinese/part2-daily-work",
            "book5-business-chinese/part3-relationships",
            "book5-business-chinese/part4-deals-money",
            "book5-business-chinese/part5-career-growth",
        ],
        "part_names": {
            "book5-business-chinese/part1-first-30-days": "Part 1: First 30 Days",
            "book5-business-chinese/part2-daily-work": "Part 2: Daily Work",
            "book5-business-chinese/part3-relationships": "Part 3: Relationships",
            "book5-business-chinese/part4-deals-money": "Part 4: Deals & Money",
            "book5-business-chinese/part5-career-growth": "Part 5: Career Growth",
        },
    },
    "book6": {
        "title": "Z Turns Chinese",
        "subtitle": "Unlock Chinese Characters",
        "zh_title": "解码汉字",
        "author": "Tony Sheng",
        "color": (30, 100, 180),
        "output": "ZTurns_Book6_Characters.pdf",
        "source_dirs": [
            "book6-characters/part1-system",
            "book6-characters/part2-essential-200",
            "book6-characters/part3-patterns",
            "book6-characters/part4-reading-real",
            "book6-characters/part5-beyond",
        ],
        "part_names": {
            "book6-characters/part1-system": "Part 1: The Character System",
            "book6-characters/part2-essential-200": "Part 2: Essential 200 Characters",
            "book6-characters/part3-patterns": "Part 3: Character Patterns",
            "book6-characters/part4-reading-real": "Part 4: Reading Real Chinese",
            "book6-characters/part5-beyond": "Part 5: Beyond Basics",
        },
    },
    "book7": {
        "title": "Z Turns Chinese",
        "subtitle": "Eat Your Way Through China",
        "zh_title": "吃遍中国",
        "author": "Tony Sheng",
        "color": (200, 50, 30),
        "output": "ZTurns_Book7_Food.pdf",
        "source_dirs": [
            "book7-food/part1-foundations",
            "book7-food/part2-street-food",
            "book7-food/part3-drinks",
            "book7-food/part4-regional",
            "book7-food/part5-food-life",
        ],
        "part_names": {
            "book7-food/part1-foundations": "Part 1: Food Foundations",
            "book7-food/part2-street-food": "Part 2: Street Food & Snacks",
            "book7-food/part3-drinks": "Part 3: Drinks & Beverages",
            "book7-food/part4-regional": "Part 4: Regional Deep Dives",
            "book7-food/part5-food-life": "Part 5: Food & Life",
        },
    },
    "book8": {
        "title": "Z Turns Chinese",
        "subtitle": "Digital China",
        "zh_title": "数字中国生存指南",
        "author": "Tony Sheng",
        "color": (0, 120, 200),
        "output": "ZTurns_Book8_DigitalChina.pdf",
        "source_dirs": [
            "book8-digital/sec1-essentials",
            "book8-digital/sec2-shopping",
            "book8-digital/sec3-social-media",
            "book8-digital/sec4-life-apps",
            "book8-digital/sec5-digital-culture",
        ],
        "part_names": {
            "book8-digital/sec1-essentials": "Section 1: Digital Essentials",
            "book8-digital/sec2-shopping": "Section 2: Shopping & Delivery",
            "book8-digital/sec3-social-media": "Section 3: Social Media",
            "book8-digital/sec4-life-apps": "Section 4: Life Apps",
            "book8-digital/sec5-digital-culture": "Section 5: Digital Culture",
        },
    },
    "book9": {
        "title": "Z Turns Chinese",
        "subtitle": "Chinese Through Stories",
        "zh_title": "故事里的中国",
        "author": "Tony Sheng",
        "color": (150, 80, 30),
        "output": "ZTurns_Book9_Stories.pdf",
        "source_dirs": [
            "book9-stories/part1-legends",
            "book9-stories/part2-history",
            "book9-stories/part3-folk-tales",
            "book9-stories/part4-modern",
            "book9-stories/part5-your-story",
        ],
        "part_names": {
            "book9-stories/part1-legends": "Part 1: Ancient Legends",
            "book9-stories/part2-history": "Part 2: Historical Stories",
            "book9-stories/part3-folk-tales": "Part 3: Folk Tales & Wisdom",
            "book9-stories/part4-modern": "Part 4: Modern Stories",
            "book9-stories/part5-your-story": "Part 5: Your Story",
        },
    },
    "book10": {
        "title": "Z Turns Chinese",
        "subtitle": "Love, Family & Social Life in China",
        "zh_title": "中国人的社交密码",
        "author": "Tony Sheng",
        "color": (200, 80, 120),
        "output": "ZTurns_Book10_SocialLife.pdf",
        "source_dirs": [
            "book10-social/part1-meeting-people",
            "book10-social/part2-dating",
            "book10-social/part3-family",
            "book10-social/part4-social-rules",
            "book10-social/part5-belonging",
        ],
        "part_names": {
            "book10-social/part1-meeting-people": "Part 1: Meeting People",
            "book10-social/part2-dating": "Part 2: Dating & Romance",
            "book10-social/part3-family": "Part 3: Family Life",
            "book10-social/part4-social-rules": "Part 4: Social Rules",
            "book10-social/part5-belonging": "Part 5: Belonging",
        },
    },
}


# ─────────────────────────────────────────────
# Font management
# ─────────────────────────────────────────────
def find_cjk_font():
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    raise RuntimeError("No CJK font found. Install one of: " + str(FONT_CANDIDATES))


# ─────────────────────────────────────────────
# Markdown parser — state machine
# ─────────────────────────────────────────────
class Block:
    """Parsed content block."""
    __slots__ = ("kind", "data")

    def __init__(self, kind, data):
        self.kind = kind   # h1 h2 h3 four_layer table paragraph rule bullet numbered
        self.data = data


def parse_markdown(text: str) -> list:
    """Parse markdown into a list of Block objects."""
    lines = text.splitlines()
    blocks = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # Headings
        if line.startswith("#### "):
            blocks.append(Block("h3", line[5:].strip()))
            i += 1
            continue
        if line.startswith("### "):
            blocks.append(Block("h3", line[4:].strip()))
            i += 1
            continue
        if line.startswith("## "):
            blocks.append(Block("h2", line[3:].strip()))
            i += 1
            continue
        if line.startswith("# "):
            blocks.append(Block("h1", line[2:].strip()))
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^-{3,}$", line.strip()):
            blocks.append(Block("rule", None))
            i += 1
            continue

        # Code block — four-layer translation
        if line.strip().startswith("```"):
            block_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                block_lines.append(lines[i])
                i += 1
            i += 1  # consume closing ```
            # Parse four-layer fields
            parsed = _parse_four_layer(block_lines)
            if parsed:
                blocks.append(Block("four_layer", parsed))
            else:
                # Plain code block — treat as paragraph
                blocks.append(Block("paragraph", "\n".join(block_lines)))
            continue

        # Table
        if line.startswith("|") and i + 1 < n and re.match(r"^\|[-| :]+\|", lines[i + 1]):
            table_lines = []
            while i < n and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            blocks.append(Block("table", _parse_table(table_lines)))
            continue

        # Bullet list
        if re.match(r"^[-*] ", line):
            items = []
            while i < n and re.match(r"^[-*] ", lines[i]):
                items.append(lines[i][2:].strip())
                i += 1
            blocks.append(Block("bullet", items))
            continue

        # Numbered list
        if re.match(r"^\d+\. ", line):
            items = []
            while i < n and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i]).strip())
                i += 1
            blocks.append(Block("numbered", items))
            continue

        # Empty line — skip
        if line.strip() == "":
            i += 1
            continue

        # Paragraph — collect consecutive non-special lines
        para_lines = []
        while i < n:
            l = lines[i]
            if (l.strip() == "" or l.startswith("#") or l.startswith("|")
                    or l.strip().startswith("```") or re.match(r"^-{3,}$", l.strip())
                    or re.match(r"^[-*] ", l) or re.match(r"^\d+\. ", l)):
                break
            para_lines.append(l)
            i += 1
        if para_lines:
            blocks.append(Block("paragraph", " ".join(para_lines)))

    return blocks


def _parse_four_layer(lines: list) -> dict | None:
    """Extract Chinese/Pinyin/Literal/English from code block lines."""
    result = {}
    for line in lines:
        for key in ("Chinese", "Pinyin", "Literal", "English"):
            if line.startswith(key + ":"):
                result[key.lower()] = line[len(key) + 1:].strip()
    # Require at least Chinese + one other
    if "chinese" in result and len(result) >= 2:
        return result
    return None


def _parse_table(lines: list) -> list:
    """Parse markdown table into list of rows (each row is a list of cells)."""
    rows = []
    for line in lines:
        if re.match(r"^\|[-| :]+\|", line):
            continue  # separator row
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells:
            rows.append(cells)
    return rows


def strip_inline_md(text: str) -> str:
    """Remove bold/italic/link markdown for plain text rendering."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text


# ─────────────────────────────────────────────
# PDF builder
# ─────────────────────────────────────────────
class BookPDF(FPDF):
    def __init__(self, book_meta: dict, font_path: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.meta = book_meta
        self.color = book_meta["color"]
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(auto=True, margin=20)

        # Register CJK font (covers both CJK and Latin)
        self.add_font("CJK", "", font_path)
        self.add_font("CJK", "B", font_path)
        self.add_font("CJK", "I", font_path)

        # TOC data: list of (level, title, page_num)
        self.toc_entries = []
        self._chapter_count = 0

    # ── Header / Footer ──────────────────────

    def header(self):
        pass  # handled manually

    def footer(self):
        if self.page_no() <= 2:
            return
        self.set_y(-15)
        self.set_font("CJK", size=9)
        r, g, b = self.color
        self.set_text_color(r, g, b)
        self.cell(0, 10, f"{self.meta['title']} — {self.meta['subtitle']}", align=Align.C)
        self.set_text_color(0, 0, 0)
        self.set_font("CJK", size=9)
        self.set_y(-15)
        self.cell(0, 10, str(self.page_no()), align=Align.R)

    # ── Cover ────────────────────────────────

    def add_cover(self):
        self.add_page()
        r, g, b = self.color
        w, h = 210, 297  # A4

        # Color band top
        self.set_fill_color(r, g, b)
        self.rect(0, 0, w, 80, style="F")

        # Series name
        self.set_y(12)
        self.set_font("CJK", size=14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "Z TURNS CHINESE SERIES", align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # White divider line
        self.set_draw_color(255, 255, 255)
        self.set_line_width(0.5)
        self.line(40, 28, 170, 28)

        # Main title
        self.set_y(32)
        self.set_font("CJK", size=28)
        self.cell(0, 14, self.meta["title"], align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Subtitle
        self.set_y(52)
        self.set_font("CJK", size=14)
        self.multi_cell(0, 8, self.meta["subtitle"], align=Align.C)

        # Colored band bottom edge decorative line
        self.set_draw_color(255, 255, 255)
        self.set_line_width(1.5)
        self.line(0, 80, w, 80)

        # Chinese title
        self.set_y(90)
        self.set_text_color(r, g, b)
        self.set_font("CJK", size=22)
        self.cell(0, 12, self.meta["zh_title"], align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Tagline box
        self.set_y(115)
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(r, g, b)
        self.set_line_width(0.8)
        self.rect(30, 112, 150, 22, style="DF")
        self.set_y(117)
        self.set_text_color(60, 60, 60)
        self.set_font("CJK", size=11)
        self.cell(0, 7, "Four-Layer Word-by-Word Translation Method", align=Align.C,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("CJK", size=10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 7, "四层逐字翻译法", align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Large decorative character
        self.set_y(148)
        self.set_text_color(r, g, b)
        self.set_font("CJK", size=72)
        self.set_fill_color(250, 250, 250)
        self.cell(0, 50, "中", align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Bottom color band
        self.set_fill_color(r, g, b)
        self.rect(0, 240, w, 57, style="F")

        # Author
        self.set_y(252)
        self.set_text_color(255, 255, 255)
        self.set_font("CJK", size=13)
        self.cell(0, 10, self.meta["author"], align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Bottom line
        self.set_draw_color(255, 255, 255)
        self.set_line_width(0.5)
        self.line(40, 268, 170, 268)

        self.set_y(272)
        self.set_font("CJK", size=10)
        self.set_text_color(220, 220, 220)
        self.cell(0, 8, "www.zturns.com", align=Align.C)

        self.set_text_color(0, 0, 0)

    # ── TOC ──────────────────────────────────

    def add_toc_page(self):
        """Add a placeholder TOC page; will be populated after all pages generated."""
        self.add_page()
        r, g, b = self.color
        self.set_y(20)
        self.set_font("CJK", size=24)
        self.set_text_color(r, g, b)
        self.cell(0, 14, "Table of Contents", align=Align.C,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("CJK", size=12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "目录", align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(r, g, b)
        self.set_line_width(0.8)
        self.line(20, self.get_y() + 2, 190, self.get_y() + 2)
        self.ln(8)
        self.set_text_color(0, 0, 0)

        # Render TOC entries (populated before this is called)
        for level, title, page in self.toc_entries:
            if level == "part":
                self.set_font("CJK", size=12)
                self.set_text_color(r, g, b)
                self.ln(3)
                # Title left, page right
                title_clean = strip_inline_md(title)
                self.cell(160, 8, title_clean, new_x=XPos.RIGHT, new_y=YPos.TOP)
                self.cell(10, 8, str(page), align=Align.R,
                          new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.set_text_color(0, 0, 0)
            else:
                self.set_font("CJK", size=10)
                self.set_text_color(50, 50, 50)
                title_clean = strip_inline_md(title)
                self.cell(10, 7, "", new_x=XPos.RIGHT, new_y=YPos.TOP)
                self.cell(150, 7, title_clean, new_x=XPos.RIGHT, new_y=YPos.TOP)
                self.cell(10, 7, str(page), align=Align.R,
                          new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.set_text_color(0, 0, 0)

    # ── Part divider ─────────────────────────

    def add_part_divider(self, part_name: str, part_zh: str = ""):
        self.add_page()
        r, g, b = self.color
        self.toc_entries.append(("part", part_name, self.page_no()))

        self.set_fill_color(r, g, b)
        self.rect(0, 80, 210, 140, style="F")

        self.set_y(100)
        self.set_text_color(255, 255, 255)
        self.set_font("CJK", size=22)
        self.multi_cell(0, 14, part_name, align=Align.C)

        if part_zh:
            self.set_font("CJK", size=14)
            self.set_text_color(220, 220, 220)
            self.cell(0, 10, part_zh, align=Align.C,
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_text_color(0, 0, 0)

    # ── Chapter ──────────────────────────────

    def add_chapter_page(self, title: str):
        self.add_page()
        r, g, b = self.color
        self._chapter_count += 1
        self.toc_entries.append(("chapter", title, self.page_no()))

        # Chapter header band
        self.set_fill_color(r, g, b)
        self.rect(0, 0, 210, 38, style="F")

        self.set_y(8)
        self.set_text_color(255, 255, 255)
        self.set_font("CJK", size=10)
        self.cell(0, 8, "Z TURNS CHINESE", align=Align.C,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("CJK", size=16)
        title_clean = strip_inline_md(title)
        self.multi_cell(0, 10, title_clean, align=Align.C)

        self.set_y(44)
        self.set_text_color(0, 0, 0)

    # ── Block renderers ──────────────────────

    def render_h2(self, text: str):
        r, g, b = self.color
        self.ln(4)
        self.set_fill_color(r, g, b)
        self.rect(self.l_margin, self.get_y(), 170, 9, style="F")
        self.set_font("CJK", size=12)
        self.set_text_color(255, 255, 255)
        self.set_x(self.l_margin + 3)
        self.cell(164, 9, strip_inline_md(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def render_h3(self, text: str):
        r, g, b = self.color
        self.ln(3)
        self.set_font("CJK", size=11)
        self.set_text_color(r, g, b)
        self.multi_cell(0, 8, strip_inline_md(text))
        self.set_text_color(0, 0, 0)
        # underline
        y = self.get_y()
        self.set_draw_color(r, g, b)
        self.set_line_width(0.3)
        self.line(self.l_margin, y, 190, y)
        self.ln(2)

    def render_paragraph(self, text: str):
        self.set_font("CJK", size=10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, strip_inline_md(text))
        self.ln(2)

    def render_four_layer(self, data: dict):
        """Render four-layer translation box with gray background."""
        r, g, b = self.color
        self.ln(2)

        x = self.l_margin
        w = 170
        start_y = self.get_y()

        # Estimate height
        chinese = data.get("chinese", "")
        pinyin = data.get("pinyin", "")
        literal = data.get("literal", "")
        english = data.get("english", "")

        # Calculate required height with rough estimate
        line_ht = 7
        box_h = 10  # top padding
        if chinese:
            box_h += 10
        if pinyin:
            box_h += 7
        if literal:
            box_h += 7
        if english:
            box_h += 7
        box_h += 4  # bottom padding

        # Check page break
        if start_y + box_h > 270:
            self.add_page()
            start_y = self.get_y()

        # Background
        self.set_fill_color(245, 245, 248)
        self.set_draw_color(r, g, b)
        self.set_line_width(0.5)
        # Left color bar
        self.set_fill_color(r, g, b)
        self.rect(x, start_y, 3, box_h, style="F")
        self.set_fill_color(245, 245, 248)
        self.rect(x + 3, start_y, w - 3, box_h, style="F")

        # Light border
        self.set_draw_color(200, 200, 210)
        self.set_line_width(0.3)
        self.rect(x, start_y, w, box_h, style="D")

        inner_x = x + 8
        inner_w = w - 12
        cy = start_y + 4

        if chinese:
            self.set_xy(inner_x, cy)
            self.set_font("CJK", size=14)
            self.set_text_color(20, 20, 20)
            self.multi_cell(inner_w, 10, chinese)
            cy = self.get_y()

        if pinyin:
            self.set_xy(inner_x, cy)
            self.set_font("CJK", size=9)
            self.set_text_color(80, 80, 120)
            self.multi_cell(inner_w, 6, pinyin)
            cy = self.get_y()

        if literal:
            self.set_xy(inner_x, cy)
            self.set_font("CJK", size=9)
            self.set_text_color(100, 80, 50)
            self.multi_cell(inner_w, 6, "[ " + literal + " ]")
            cy = self.get_y()

        if english:
            self.set_xy(inner_x, cy)
            self.set_font("CJK", size=10)
            self.set_text_color(30, 30, 30)
            self.multi_cell(inner_w, 7, "→ " + english)
            cy = self.get_y()

        self.set_y(cy + 4)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def render_table(self, rows: list):
        if not rows:
            return
        r, g, b = self.color
        self.ln(3)

        header_row = rows[0]
        data_rows = rows[1:]
        n_cols = len(header_row)
        col_w = 170 / n_cols

        # Header
        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 255)
        self.set_font("CJK", size=9)
        for cell in header_row:
            self.cell(col_w, 8, strip_inline_md(cell)[:30], border=1,
                      fill=True, align=Align.C, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln()

        # Data rows
        self.set_text_color(0, 0, 0)
        for row_i, row in enumerate(data_rows):
            if self.get_y() > 270:
                self.add_page()
            fill = (row_i % 2 == 0)
            self.set_fill_color(240, 245, 255) if fill else self.set_fill_color(255, 255, 255)
            self.set_font("CJK", size=8)
            for j, cell in enumerate(row):
                self.cell(col_w, 7, strip_inline_md(cell)[:35], border=1,
                          fill=True, align=Align.L, new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.ln()

        self.ln(3)

    def render_bullet(self, items: list):
        self.ln(1)
        self.set_font("CJK", size=10)
        self.set_text_color(30, 30, 30)
        for item in items:
            self.set_x(self.l_margin + 3)
            self.cell(5, 7, "•", new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.multi_cell(155, 7, strip_inline_md(item))
        self.ln(1)

    def render_numbered(self, items: list):
        self.ln(1)
        self.set_font("CJK", size=10)
        self.set_text_color(30, 30, 30)
        for i, item in enumerate(items, 1):
            self.set_x(self.l_margin + 3)
            self.cell(8, 7, f"{i}.", new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.multi_cell(152, 7, strip_inline_md(item))
        self.ln(1)

    def render_rule(self):
        r, g, b = self.color
        self.ln(2)
        self.set_draw_color(r, g, b)
        self.set_line_width(0.3)
        y = self.get_y()
        self.line(self.l_margin, y, 190, y)
        self.ln(3)

    # ── Block dispatcher ─────────────────────

    def render_blocks(self, blocks: list):
        for block in blocks:
            if self.get_y() > 275:
                self.add_page()
            k = block.kind
            if k == "h1":
                self.add_chapter_page(block.data)
            elif k == "h2":
                self.render_h2(block.data)
            elif k == "h3":
                self.render_h3(block.data)
            elif k == "four_layer":
                self.render_four_layer(block.data)
            elif k == "table":
                self.render_table(block.data)
            elif k == "paragraph":
                self.render_paragraph(block.data)
            elif k == "bullet":
                self.render_bullet(block.data)
            elif k == "numbered":
                self.render_numbered(block.data)
            elif k == "rule":
                self.render_rule()


# ─────────────────────────────────────────────
# File collection
# ─────────────────────────────────────────────
def collect_files(source_dirs: list) -> list:
    """Return sorted list of (part_dir, Path) for all .md files."""
    result = []
    for source_dir in source_dirs:
        dir_path = BASE_DIR / source_dir
        if not dir_path.exists():
            print(f"  [WARN] Directory not found: {dir_path}")
            continue
        md_files = sorted(dir_path.glob("*.md"))
        for f in md_files:
            result.append((source_dir, f))
    return result


# ─────────────────────────────────────────────
# Build a single book
# ─────────────────────────────────────────────
def build_book(book_key: str, meta: dict, font_path: str):
    print(f"\nBuilding {meta['output']} ...")

    # First pass: parse all files to build TOC
    files = collect_files(meta["source_dirs"])
    print(f"  Found {len(files)} markdown files")

    pdf = BookPDF(meta, font_path)

    # Cover
    pdf.add_cover()

    # TOC placeholder page (we'll insert entries as we go)
    toc_page_num = 2
    pdf.add_page()  # reserve page 2 for TOC — we'll rewrite it

    # Content pages
    current_part = None
    for source_dir, file_path in files:
        part_name = meta["part_names"].get(source_dir, source_dir)
        if part_name != current_part:
            current_part = part_name
            pdf.add_part_divider(part_name)

        text = file_path.read_text(encoding="utf-8")
        blocks = parse_markdown(text)
        pdf.render_blocks(blocks)

    # Back matter
    pdf.add_page()
    r, g, b = meta["color"]
    pdf.set_y(120)
    pdf.set_font("CJK", size=20)
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 14, "Thank You for Learning with Us", align=Align.C,
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("CJK", size=14)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "感谢您与我们一起学习", align=Align.C,
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(10)
    pdf.set_font("CJK", size=11)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 8,
        "Keep practicing. Real fluency comes from real conversations.\n"
        "继续练习。真正的流利来自真实的对话。",
        align=Align.C)
    pdf.set_text_color(0, 0, 0)

    # Now rewrite TOC page (page 2)
    # fpdf2 does not support rewriting pages in-place, so we use the insert_page approach:
    # We already reserved page 2 as a blank — we need to output a fresh PDF with TOC.
    # Strategy: output to a temp buffer, then inject TOC via a second PDF pass.
    # Simpler: just generate TOC at the end appended, and accept it's not on page 2.

    out_path = OUTPUT_DIR / meta["output"]
    pdf.output(str(out_path))
    print(f"  Written: {out_path} ({out_path.stat().st_size // 1024} KB)")
    return out_path


# ─────────────────────────────────────────────
# Two-pass approach for proper TOC
# ─────────────────────────────────────────────
def build_book_with_toc(book_key: str, meta: dict, font_path: str):
    """
    Two-pass build:
    Pass 1 — collect TOC entries and page numbers.
    Pass 2 — build final PDF with TOC on page 2.
    """
    print(f"\nBuilding {meta['output']} ...")
    files = collect_files(meta["source_dirs"])
    print(f"  Found {len(files)} markdown files")

    # ── Pass 1: Dry run to collect page numbers ──
    pdf1 = BookPDF(meta, font_path)
    pdf1.add_cover()
    pdf1.add_page()  # TOC placeholder

    current_part = None
    for source_dir, file_path in files:
        part_name = meta["part_names"].get(source_dir, source_dir)
        if part_name != current_part:
            current_part = part_name
            pdf1.add_part_divider(part_name)
        text = file_path.read_text(encoding="utf-8")
        blocks = parse_markdown(text)
        pdf1.render_blocks(blocks)

    toc_data = list(pdf1.toc_entries)
    # Adjust page numbers: TOC is on page 2, everything shifts by ~toc_pages
    # Estimate TOC pages needed
    toc_lines = len(toc_data)
    toc_pages_needed = max(1, (toc_lines * 7) // 240)  # rough

    # Page offset: pass1 page 2 is placeholder (1 page); final will have actual TOC
    # If toc_pages_needed > 1, shift by (toc_pages_needed - 1)
    page_offset = toc_pages_needed - 1

    # ── Pass 2: Final build with TOC ──
    pdf2 = BookPDF(meta, font_path)
    pdf2.add_cover()

    # TOC — set entries adjusted for offset
    pdf2.toc_entries = [
        (lvl, title, pg + page_offset) for lvl, title, pg in toc_data
    ]
    for _ in range(toc_pages_needed):
        pdf2.add_toc_page()
        # Only first TOC page renders properly; break after first
        break

    # If we need more TOC pages, add blank continuation
    if toc_pages_needed > 1:
        for _ in range(toc_pages_needed - 1):
            pdf2.add_page()

    current_part = None
    for source_dir, file_path in files:
        part_name = meta["part_names"].get(source_dir, source_dir)
        if part_name != current_part:
            current_part = part_name
            pdf2.add_part_divider(part_name)
        text = file_path.read_text(encoding="utf-8")
        blocks = parse_markdown(text)
        pdf2.render_blocks(blocks)

    # Back matter
    pdf2.add_page()
    r, g, b = meta["color"]
    pdf2.set_fill_color(r, g, b)
    pdf2.rect(0, 100, 210, 100, style="F")
    pdf2.set_y(120)
    pdf2.set_font("CJK", size=20)
    pdf2.set_text_color(255, 255, 255)
    pdf2.cell(0, 14, "Thank You for Learning with Us",
              align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf2.set_font("CJK", size=14)
    pdf2.cell(0, 10, "感谢您与我们一起学习",
              align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf2.ln(8)
    pdf2.set_font("CJK", size=11)
    pdf2.set_text_color(230, 230, 230)
    pdf2.multi_cell(
        0, 8,
        "Keep practicing. Real fluency comes from real conversations.\n"
        "继续练习。真正的流利来自真实的对话。",
        align=Align.C,
    )
    pdf2.set_text_color(0, 0, 0)

    out_path = OUTPUT_DIR / meta["output"]
    pdf2.output(str(out_path))
    size_kb = out_path.stat().st_size // 1024
    print(f"  Written: {out_path} ({size_kb} KB, {pdf2.page} pages)")
    return out_path


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    import time as _time
    font_path = find_cjk_font()
    print(f"Using font: {font_path}")

    # Allow filtering which books to build via CLI args
    # Usage: python generate_books.py book6 book7   (only those)
    # Usage: python generate_books.py               (all books)
    requested = set(sys.argv[1:]) if len(sys.argv) > 1 else None

    results = []
    errors = []

    for book_key, meta in BOOKS.items():
        if requested and book_key not in requested:
            print(f"\nSkipping {book_key} (not requested)")
            continue
        try:
            t0 = _time.monotonic()
            out = build_book_with_toc(book_key, meta, font_path)
            elapsed = _time.monotonic() - t0
            print(f"  ⏱ {elapsed:.1f}s")
            results.append(out)
        except Exception as e:
            import traceback
            print(f"\n[ERROR] {book_key}: {e}")
            traceback.print_exc()
            errors.append((book_key, str(e)))

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for path in results:
        size = path.stat().st_size
        print(f"  OK  {path.name}  ({size:,} bytes)")
    for book_key, err in errors:
        print(f"  FAIL {book_key}: {err}")

    if errors:
        sys.exit(1)
    print("\nAll books generated successfully.")


if __name__ == "__main__":
    main()
