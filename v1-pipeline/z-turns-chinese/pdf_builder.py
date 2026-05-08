"""
Z Turns Chinese - PDF Builder
Four-Layer Aligned Chinese Learning Guide PDF Generator

Synthesized from:
- Claude方案: Four-layer translation engine + PDF layout prototype
- Gemini方案: Typst-style block layout concept
- Minimax方案: Dual-engine structure
- All方案: HSK 3.0 compliance
"""

import os
import unicodedata
from fpdf import FPDF
from config import PDF_STYLE, FOUR_LAYERS


class ChinesePDF(FPDF):
    """Custom PDF class for Chinese learning materials with four-layer alignment."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=PDF_STYLE["margin_bottom"])
        self._setup_fonts()
        self.book_title = "Z Turns Chinese"
        self.current_lesson = ""
        # PDF accessibility
        self.set_lang("en")
        self.set_creator("Z Turns Chinese AutoBuilder")
        self.set_title("Z Turns Chinese")

    def _setup_fonts(self):
        """Register fonts including CJK support using system fonts."""
        import platform
        # Primary: Use Arial Unicode (supports Latin + CJK)
        unicode_font_paths = [
            # macOS
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            # Windows
            "C:\\Windows\\Fonts\\arialuni.ttf",
            "C:\\Windows\\Fonts\\msyh.ttc",
            # Linux
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/noto-cjk/NotoSansCJKsc-Regular.otf",
            "/usr/share/fonts/truetype/arialuni.ttf",
        ]

        self.latin_font = None
        for path in unicode_font_paths:
            if os.path.exists(path):
                try:
                    self.add_font("ArialUni", "", path, uni=True)
                    self.latin_font = "ArialUni"
                    break
                except Exception:
                    continue

        if not self.latin_font:
            # Fallback to Helvetica (built-in, no CJK)
            self.latin_font = "Helvetica"

        # CJK font: Try multiple system fonts (macOS, Windows, Linux)
        cjk_paths = [
            # macOS
            ("/System/Library/Fonts/Hiragino Sans GB.ttc", "Hiragino"),
            ("/System/Library/Fonts/Supplemental/Songti.ttc", "Songti"),
            ("/System/Library/Fonts/PingFang.ttc", "PingFang"),
            ("/System/Library/Fonts/STHeiti Light.ttc", "STHeiti"),
            # Windows
            ("C:\\Windows\\Fonts\\msyh.ttc", "MSYaHei"),
            ("C:\\Windows\\Fonts\\simsun.ttc", "SimSun"),
            ("C:\\Windows\\Fonts\\simhei.ttf", "SimHei"),
            # Linux
            ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "NotoSansCJK"),
            ("/usr/share/fonts/noto-cjk/NotoSansCJKsc-Regular.otf", "NotoSansCJKSC"),
            ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "WQYZenHei"),
        ]

        self.cjk_font = None
        for path, name in cjk_paths:
            if os.path.exists(path):
                try:
                    self.add_font(name, "", path, uni=True)
                    self.cjk_font = name
                    break
                except Exception:
                    continue

        # If no dedicated CJK font found, try Arial Unicode (covers CJK)
        if not self.cjk_font:
            if self.latin_font == "ArialUni":
                self.cjk_font = "ArialUni"
            else:
                self.cjk_font = "Helvetica"  # Last resort

    def _set_color(self, color_name):
        """Set text color from config."""
        r, g, b = PDF_STYLE["colors"].get(color_name, (0, 0, 0))
        self.set_text_color(r, g, b)

    def header(self):
        """Page header with book title and lesson name."""
        if not self.current_lesson:
            return
        self.set_font(self.latin_font, "", 9)
        self._set_color("secondary")
        self.cell(0, 8, f"{self.book_title}  |  {self.current_lesson}", align="L")
        self.ln(4)
        # Divider line
        self.set_draw_color(200, 200, 200)
        self.line(PDF_STYLE["margin_left"], self.get_y(),
                  self.w - PDF_STYLE["margin_right"], self.get_y())
        self.ln(8)

    def footer(self):
        """Page footer with page number."""
        self.set_y(-15)
        self.set_font(self.latin_font, "", 9)
        self._set_color("secondary")
        self.cell(0, 10, f"Z Turns Chinese  |  {self.page_no()}", align="C")

    # ================================================================
    # HIGH-LEVEL LAYOUT COMPONENTS
    # ================================================================

    def add_title_page(self, book_name, lesson_num, title_en, title_zh, hsk_level):
        """Create a beautiful title page for the lesson (no header)."""
        saved_lesson = self.current_lesson
        self.current_lesson = ""
        self.add_page()
        self.current_lesson = f"Lesson {lesson_num}"

        # Top spacing
        self.ln(40)

        # Book name
        self.set_font(self.latin_font, "", 12)
        self._set_color("primary")
        self.cell(0, 10, book_name, align="C")
        self.ln(15)

        # Lesson number
        self.set_font(self.latin_font, "", 28)
        self._set_color("text")
        self.cell(0, 15, f"Lesson {lesson_num}", align="C")
        self.ln(15)

        # Chinese title (large)
        self.set_font(self.cjk_font, "", 36)
        self._set_color("text")
        self.cell(0, 20, title_zh, align="C")
        self.ln(12)

        # English title
        self.set_font(self.latin_font, "", 18)
        self._set_color("secondary")
        self.cell(0, 12, title_en, align="C")
        self.ln(20)

        # HSK badge
        self.set_font(self.latin_font, "", 11)
        badge_text = f"HSK {hsk_level}  |  CEFR A{hsk_level}"
        badge_w = self.get_string_width(badge_text) + 20
        x = (self.w - badge_w) / 2
        self.set_xy(x, self.get_y())
        self.set_fill_color(*PDF_STYLE["colors"]["badge_bg"])
        self.set_text_color(*PDF_STYLE["colors"]["badge_text"])
        self.cell(badge_w, 12, badge_text, fill=True, align="C")
        self._set_color("text")
        self.ln(30)

        # Decorative line
        self.set_draw_color(*PDF_STYLE["colors"]["primary"])
        self.set_line_width(1)
        cx = self.w / 2
        self.line(cx - 40, self.get_y(), cx + 40, self.get_y())
        self.set_line_width(0.2)

    def add_learning_goals(self, goals):
        """Add learning goals section."""
        self.add_page()
        self._section_header("Learning Goals", "xuexi mubiao")

        self.set_font(self.latin_font, "", PDF_STYLE["body_font_size"])
        self._set_color("text")

        self.ln(3)
        for i, goal in enumerate(goals, 1):
            self._set_color("text")
            self.set_font(self.latin_font, "", PDF_STYLE["body_font_size"])
            self.cell(0, 8, f"  {i}. {goal}")
            self.ln(8)
        self.ln(5)

    def add_vocabulary_section(self, words, title="New Words"):
        """Add vocabulary table with four-layer alignment."""
        self._section_header(title, "shengci")
        self.ln(3)

        # Table header
        col_widths = [30, 32, 32, 38, 28]
        headers = ["Chinese", "Pinyin", "Literal", "English", "Type"]

        self.set_font(self.latin_font, "", 10)
        self.set_fill_color(*PDF_STYLE["colors"]["primary"])
        self.set_text_color(*PDF_STYLE["colors"]["badge_text"])

        for i, h in enumerate(headers):
            self.cell(col_widths[i], 10, h, border=1, fill=True, align="C")
        self.ln()

        # Table rows
        self._set_color("text")
        for j, word in enumerate(words):
            zh, py, literal, english, pos = word[0], word[1], word[2], word[3], word[4]

            # Alternate row colors
            if j % 2 == 0:
                self.set_fill_color(*PDF_STYLE["colors"]["row_alt"])
            else:
                self.set_fill_color(*PDF_STYLE["colors"]["row_even"])

            # Chinese character (CJK font)
            self.set_font(self.cjk_font, "", 12)
            self._set_color("text")
            self.cell(col_widths[0], 10, zh, border=1, fill=True, align="C")

            # Pinyin
            self.set_font(self.latin_font, "", 10)
            self._set_color("pinyin")
            self.cell(col_widths[1], 10, py, border=1, fill=True, align="C")

            # Literal English
            self._set_color("literal")
            self.cell(col_widths[2], 10, literal, border=1, fill=True, align="C")

            # Natural English
            self._set_color("text")
            self.cell(col_widths[3], 10, english, border=1, fill=True, align="C")

            # Part of speech
            self._set_color("secondary")
            self.set_font(self.latin_font, "", 9)
            self.cell(col_widths[4], 10, pos, border=1, fill=True, align="C")
            self.ln()

        self.ln(8)

    def add_dialogue(self, dialogue_data):
        """Add a dialogue section with four-layer aligned translation blocks."""
        title = dialogue_data.get("title", "Dialogue")
        lines = dialogue_data.get("lines", [])

        self._section_header(f"Dialogue: {title}", "duihua")
        self.ln(3)

        for speaker, zh, pinyin, literal, natural in lines:
            self._check_page_space(35)

            # Speaker label
            self.set_font(self.latin_font, "", 10)
            self._set_color("primary")
            self.cell(0, 7, f"  {speaker}:")
            self.ln(7)

            # Four-layer block with background
            x_start = PDF_STYLE["margin_left"] + 10
            block_w = self.w - PDF_STYLE["margin_left"] - PDF_STYLE["margin_right"] - 12

            # Calculate dynamic block height based on content
            layer_h = 7  # height per layer
            padding = 4  # top + bottom padding
            block_h = layer_h * 4 + padding

            # Background rectangle
            y_start = self.get_y()
            self.set_fill_color(*PDF_STYLE["colors"]["background"])
            self.rect(x_start, y_start, block_w, block_h, "F")

            # Layer 1: Chinese characters
            self.set_xy(x_start + 5, y_start + 2)
            self.set_font(self.cjk_font, "", PDF_STYLE["chinese_font_size"])
            self._set_color("text")
            self.cell(block_w - 10, layer_h, zh)

            # Layer 2: Pinyin
            self.set_xy(x_start + 5, y_start + 2 + layer_h)
            self.set_font(self.latin_font, "", PDF_STYLE["pinyin_font_size"])
            self._set_color("pinyin")
            self.cell(block_w - 10, layer_h, pinyin)

            # Layer 3: Word-by-word literal English
            self.set_xy(x_start + 5, y_start + 2 + layer_h * 2)
            self.set_font(self.latin_font, "", PDF_STYLE["literal_font_size"])
            self._set_color("literal")
            self.cell(block_w - 10, layer_h, literal)

            # Layer 4: Natural English (with arrow)
            self.set_xy(x_start + 5, y_start + 2 + layer_h * 3)
            self.set_font(self.latin_font, "", PDF_STYLE["natural_font_size"])
            self._set_color("text")
            self.cell(block_w - 10, layer_h, f"-> \"{natural}\"")

            self.set_y(y_start + block_h + 4)

        self.ln(5)

    def add_grammar_section(self, grammar_points):
        """Add grammar explanation section."""
        self._section_header("Grammar Points", "yufa yaodin")
        self.ln(3)

        for gp in grammar_points:
            self._check_page_space(40)

            # Grammar title
            self.set_font(self.latin_font, "", 13)
            self._set_color("primary")
            self.cell(0, 8, f"  {gp['title']}")
            self.ln(10)

            # Explanation with background block
            x_start = PDF_STYLE["margin_left"] + 5
            block_w = self.w - PDF_STYLE["margin_left"] - PDF_STYLE["margin_right"] - 10

            self.set_fill_color(*PDF_STYLE["colors"]["grammar_bg"])
            self.set_draw_color(*PDF_STYLE["colors"]["primary"])

            self.set_font(self.cjk_font, "", 11)
            self._set_color("text")
            self.set_x(x_start)
            self.multi_cell(block_w, 6, gp["explanation"], border=1, fill=True)

            self.ln(8)

    def add_culture_note(self, note):
        """Add culture note section with distinctive styling."""
        self._section_header("Culture Note", "wenhua xiaotieshi")
        self.ln(3)

        x_start = PDF_STYLE["margin_left"] + 5
        block_w = self.w - PDF_STYLE["margin_left"] - PDF_STYLE["margin_right"] - 10

        # Green accent border
        self.set_fill_color(*PDF_STYLE["colors"]["culture_bg"])
        self.set_draw_color(*PDF_STYLE["colors"]["culture"])

        # Title
        self.set_font(self.latin_font, "", 12)
        self._set_color("culture")
        self.set_x(x_start)
        self.cell(block_w, 8, f"  {note['title']}")
        self.ln(10)

        # Content
        self.set_font(self.cjk_font, "", 11)
        self._set_color("text")
        self.set_x(x_start)
        self.multi_cell(block_w, 6, note["text"], border=1, fill=True)
        self.ln(8)

    def add_exercises(self, exercises):
        """Add practice exercises section."""
        self._section_header("Practice", "lianxi")
        self.ln(3)

        for i, ex in enumerate(exercises, 1):
            self._check_page_space(25)

            ex_type = ex.get("type", "")
            instruction = ex.get("instruction", "")
            question = ex.get("question", "")

            # Exercise number and instruction
            self.set_font(self.latin_font, "", 11)
            self._set_color("text")
            self.cell(0, 7, f"  {i}. {instruction}")
            self.ln(8)

            # Question
            self.set_font(self.cjk_font, "", 12)
            self._set_color("text")
            self.set_x(PDF_STYLE["margin_left"] + 15)

            if ex_type == "match":
                pairs = ex.get("pairs", [])
                for idx_p, (zh, en) in enumerate(pairs, 1):
                    self.cell(40, 7, zh)
                    self.set_font(self.latin_font, "", 10)
                    self.cell(10, 7, "___")
                    self.set_font(self.latin_font, "", 10)
                    self.cell(0, 7, en)
                    self.ln(7)
                    self.set_x(PDF_STYLE["margin_left"] + 15)
                    self.set_font(self.cjk_font, "", 12)
                self.ln(4)
            else:
                self.multi_cell(0, 7, f"     {question}")

                # Answer line
                self.set_font(self.latin_font, "", 10)
                self._set_color("secondary")
                self.set_x(PDF_STYLE["margin_left"] + 15)
                self.cell(0, 7, "Answer: ________________________________")
            self.ln(12)

    def add_answer_key(self, exercises):
        """Add answer key section at the end."""
        self.add_page()
        self._section_header("Answer Key", "daan")
        self.ln(5)

        for i, ex in enumerate(exercises, 1):
            self.set_font(self.latin_font, "", 10)
            self._set_color("text")
            self.cell(12, 7, f"{i}.")

            if ex.get("type") == "match" and ex.get("pairs"):
                self.set_font(self.cjk_font, "", 11)
                self._set_color("primary")
                match_answers = [f"{zh} — {en}" for zh, en in ex["pairs"]]
                self.cell(0, 7, "; ".join(match_answers))
            else:
                answer = ex.get("answer", "")
                self.set_font(self.cjk_font, "", 11)
                self._set_color("primary")
                self.cell(0, 7, str(answer))
            self.ln(8)

    def add_review_words(self, words):
        """Add review vocabulary from previous lessons."""
        self._section_header("Review Words (from previous lessons)", "fuxi shengci")
        self.ln(3)

        self.set_font(self.cjk_font, "", 11)
        col_w = (self.w - PDF_STYLE["margin_left"] - PDF_STYLE["margin_right"]) / 4

        for zh, py, literal, english in words:
            self._set_color("text")
            self.cell(col_w, 7, zh, align="C")
            self._set_color("pinyin")
            self.cell(col_w, 7, py, align="C")
            self._set_color("literal")
            self.cell(col_w, 7, literal, align="C")
            self._set_color("text")
            self.cell(col_w, 7, english, align="C")
            self.ln(8)

        self.ln(5)

    # ================================================================
    # BOOK-LEVEL LAYOUT COMPONENTS
    # ================================================================

    def add_book_cover(self, book_title="Z Turns Chinese: Book 1", subtitle="Beginner's Guide", author="Tony Sheng"):
        """Create a professional book cover page (no header/footer)."""
        self.add_page()
        self.current_lesson = ""

        # Top spacing
        self.ln(30)

        # Series name
        self.set_font(self.latin_font, "", 14)
        self._set_color("secondary")
        self.cell(0, 10, "Z TURNS CHINESE SERIES", align="C")
        self.ln(20)

        # Main title
        self.set_font(self.latin_font, "", 32)
        self._set_color("primary")
        self.cell(0, 15, "Z Turns Chinese", align="C")
        self.ln(18)

        # Subtitle
        self.set_font(self.latin_font, "", 20)
        self._set_color("text")
        self.cell(0, 12, f"Book 1: {subtitle}", align="C")
        self.ln(12)

        # Chinese subtitle
        self.set_font(self.cjk_font, "", 24)
        self._set_color("text")
        self.cell(0, 15, "零基础入门", align="C")
        self.ln(20)

        # Tagline
        self.set_font(self.latin_font, "", 12)
        self._set_color("secondary")
        self.cell(0, 8, "Word-by-Word Chinese for English Speakers", align="C")
        self.ln(5)
        self.cell(0, 8, "Four-Layer Translation Method", align="C")
        self.ln(5)
        self.cell(0, 8, "HSK 3.0 (2026) Aligned", align="C")
        self.ln(20)

        # Decorative line
        cx = self.w / 2
        self.set_draw_color(*PDF_STYLE["colors"]["primary"])
        self.set_line_width(1.5)
        self.line(cx - 50, self.get_y(), cx + 50, self.get_y())
        self.set_line_width(0.2)
        self.ln(20)

        # Features
        features = [
            "15 Real-Life Lessons | 15 Practical Dialogues",
            "Every sentence: Chinese + Pinyin + Word-by-Word + Natural English",
            "Grammar explanations designed for English speakers",
            "Culture notes about modern China (2026)",
            "Practice exercises with answer keys",
        ]
        self.set_font(self.latin_font, "", 10)
        self._set_color("secondary")
        for feat in features:
            self.cell(0, 7, feat, align="C")
            self.ln(7)

        self.ln(15)

        # Author
        self.set_font(self.latin_font, "", 12)
        self._set_color("text")
        self.cell(0, 8, f"by {author}", align="C")
        self.ln(5)
        self.set_font(self.latin_font, "", 10)
        self._set_color("secondary")
        self.cell(0, 8, "Based on 100+ hours of real Chinese teaching", align="C")

    def add_copyright_page(self, author="Tony Sheng", year="2026"):
        """Copyright page: Copyright, ISBN placeholder, publishing info."""
        self.add_page()
        self.current_lesson = ""

        self.ln(60)

        lines = [
            ("Z Turns Chinese: Book 1 — Beginner's Guide", self.latin_font, 14, "text"),
            ("零基础入门", self.cjk_font, 14, "text"),
            ("", None, 0, None),
            (f"Copyright © {year} {author}", self.latin_font, 11, "text"),
            ("All rights reserved.", self.latin_font, 11, "text"),
            ("", None, 0, None),
            (f"First Edition, {year}", self.latin_font, 10, "secondary"),
            ("", None, 0, None),
            ("ISBN: 978-X-XXXX-XXXX-X (Paperback)", self.latin_font, 10, "secondary"),
            ("ISBN: 978-X-XXXX-XXXX-X (eBook)", self.latin_font, 10, "secondary"),
            ("", None, 0, None),
            ("HSK 3.0 (2026) Aligned", self.latin_font, 10, "primary"),
            ("CEFR Level: A1", self.latin_font, 10, "primary"),
            ("ACTFL Level: Novice Mid - Novice High", self.latin_font, 10, "primary"),
            ("", None, 0, None),
            ("Four-Layer Translation Method™", self.latin_font, 11, "primary"),
            ("Chinese + Pinyin + Word-by-Word English + Natural English", self.latin_font, 10, "secondary"),
            ("", None, 0, None),
            ("No part of this publication may be reproduced, distributed,", self.latin_font, 9, "secondary"),
            ("or transmitted in any form or by any means without the prior", self.latin_font, 9, "secondary"),
            ("written permission of the publisher, except for brief quotations", self.latin_font, 9, "secondary"),
            ("in critical reviews and certain noncommercial uses permitted", self.latin_font, 9, "secondary"),
            ("by copyright law.", self.latin_font, 9, "secondary"),
        ]

        for text, font, size, color in lines:
            if not text:
                self.ln(8)
                continue
            self.set_font(font, "", size)
            self._set_color(color)
            self.cell(0, 7, text, align="C")
            self.ln(7)

    def add_preface_page(self):
        """Preface page: Four-layer method introduction, usage guide, HSK info."""
        self.add_page()
        self.current_lesson = ""

        # Title
        self.ln(10)
        self.set_font(self.latin_font, "", 22)
        self._set_color("text")
        self.cell(0, 12, "How to Use This Book", align="C")
        self.ln(5)
        self.set_font(self.cjk_font, "", 16)
        self._set_color("secondary")
        self.cell(0, 10, "如何使用本书", align="C")
        self.ln(15)

        # Introduction
        x_start = PDF_STYLE["margin_left"]
        block_w = self.w - PDF_STYLE["margin_left"] - PDF_STYLE["margin_right"]

        self.set_font(self.latin_font, "", 11)
        self._set_color("text")
        intro = (
            "Z Turns Chinese uses a unique Four-Layer Translation Method that shows you "
            "exactly how Chinese works, word by word. Instead of just giving you a Chinese "
            "sentence and its English translation, every sentence in this book is presented "
            "in four layers:"
        )
        self.set_x(x_start)
        self.multi_cell(block_w, 6, intro)
        self.ln(8)

        # Four layers explanation
        layers = [
            ("Layer 1: Chinese Characters", "The actual Chinese text you'll learn to read.", "text"),
            ("Layer 2: Pinyin", "Pronunciation guide with tone marks so you know exactly how to say it.", "pinyin"),
            ("Layer 3: Word-by-Word English", "Each Chinese word translated directly, keeping Chinese word order. This is the key to understanding how Chinese thinks!", "literal"),
            ("Layer 4: Natural English", "A natural English translation so you understand the full meaning.", "text"),
        ]

        for title, desc, color in layers:
            self._check_page_space(20)
            self.set_font(self.latin_font, "", 12)
            self._set_color(color)
            self.set_x(x_start + 5)
            self.cell(block_w, 7, title)
            self.ln(7)
            self.set_font(self.latin_font, "", 10)
            self._set_color("secondary")
            self.set_x(x_start + 10)
            self.multi_cell(block_w - 15, 5, desc)
            self.ln(4)

        self.ln(5)

        # Who is this book for
        self._check_page_space(30)
        self.set_font(self.latin_font, "", 14)
        self._set_color("primary")
        self.cell(0, 8, "Who Is This Book For?")
        self.ln(10)

        self.set_font(self.latin_font, "", 11)
        self._set_color("text")
        audiences = [
            "Complete beginners with zero Chinese knowledge",
            "English speakers who want to understand Chinese structure",
            "Self-learners preparing for HSK Level 1",
            "Travelers planning a trip to China",
            "Anyone curious about how Chinese really works",
        ]
        for aud in audiences:
            self.set_x(x_start + 5)
            self.cell(0, 7, f"•  {aud}")
            self.ln(7)

        self.ln(8)

        # Study tips
        self._check_page_space(30)
        self.set_font(self.latin_font, "", 14)
        self._set_color("primary")
        self.cell(0, 8, "Study Tips")
        self.ln(10)

        self.set_font(self.latin_font, "", 11)
        self._set_color("text")
        tips = [
            "Study one lesson per week for best retention.",
            "Always read Layer 3 (word-by-word) carefully — it reveals Chinese logic.",
            "Practice the dialogues out loud, even if you feel silly!",
            "Review previous vocabulary before starting a new lesson.",
            "Use the answer key to check your exercises, then try again.",
        ]
        for tip in tips:
            self._check_page_space(10)
            self.set_x(x_start + 5)
            self.cell(0, 7, f"•  {tip}")
            self.ln(7)

    def add_table_of_contents(self, lessons):
        """Table of contents page listing all lessons with unit groupings."""
        self.add_page()
        self.current_lesson = ""

        self.ln(10)
        self.set_font(self.latin_font, "", 22)
        self._set_color("text")
        self.cell(0, 12, "Table of Contents", align="C")
        self.ln(5)
        self.set_font(self.cjk_font, "", 14)
        self._set_color("secondary")
        self.cell(0, 10, "目录", align="C")
        self.ln(15)

        # Decorative line
        self.set_draw_color(*PDF_STYLE["colors"]["primary"])
        self.set_line_width(0.8)
        cx = self.w / 2
        self.line(cx - 40, self.get_y(), cx + 40, self.get_y())
        self.set_line_width(0.2)
        self.ln(10)

        x_start = PDF_STYLE["margin_left"]
        block_w = self.w - PDF_STYLE["margin_left"] - PDF_STYLE["margin_right"]

        # Unit groupings
        units = [
            ("Unit 1: Getting Started / 入门篇", 1, 5),
            ("Unit 2: Daily Life / 日常生活", 6, 10),
            ("Unit 3: Expanding Horizons / 拓展篇", 11, 15),
        ]

        for unit_title, start, end in units:
            self._check_page_space(15)
            self.set_font(self.latin_font, "", 13)
            self._set_color("primary")
            self.set_x(x_start)
            self.cell(block_w, 9, unit_title)
            self.ln(10)

            for lesson in lessons:
                if start <= lesson["id"] <= end:
                    self._check_page_space(10)
                    # Lesson entry
                    self.set_font(self.latin_font, "", 11)
                    self._set_color("text")
                    self.set_x(x_start + 10)
                    entry_en = f"Lesson {lesson['id']}: {lesson['title_en']}"
                    self.cell(0, 7, entry_en)
                    self.ln(7)

                    # Chinese title
                    self.set_font(self.cjk_font, "", 10)
                    self._set_color("secondary")
                    self.set_x(x_start + 10)
                    self.cell(0, 6, lesson["title_zh"])
                    self.ln(8)

            self.ln(5)

        # Back matter
        self._check_page_space(20)
        self.set_font(self.latin_font, "", 13)
        self._set_color("primary")
        self.set_x(x_start)
        self.cell(block_w, 9, "Appendices / 附录")
        self.ln(10)

        appendices = [
            "Complete Vocabulary Index / 词汇总表",
            "Answer Key Compilation / 答案汇总",
        ]
        for app in appendices:
            self.set_font(self.latin_font, "", 11)
            self._set_color("text")
            self.set_x(x_start + 10)
            self.cell(0, 7, app)
            self.ln(8)

    def add_section_divider(self, title, subtitle=""):
        """Unit divider page with large centered title."""
        self.add_page()
        self.current_lesson = ""

        self.ln(60)

        # Decorative line above
        cx = self.w / 2
        self.set_draw_color(*PDF_STYLE["colors"]["primary"])
        self.set_line_width(1.5)
        self.line(cx - 50, self.get_y(), cx + 50, self.get_y())
        self.set_line_width(0.2)
        self.ln(15)

        # Unit title
        self.set_font(self.latin_font, "", 28)
        self._set_color("primary")
        self.cell(0, 15, title, align="C")
        self.ln(15)

        # Subtitle (Chinese)
        if subtitle:
            self.set_font(self.cjk_font, "", 20)
            self._set_color("text")
            self.cell(0, 12, subtitle, align="C")
            self.ln(15)

        # Decorative line below
        self.set_draw_color(*PDF_STYLE["colors"]["primary"])
        self.set_line_width(1.5)
        self.line(cx - 50, self.get_y(), cx + 50, self.get_y())
        self.set_line_width(0.2)

    def add_vocab_index(self, all_words):
        """Complete vocabulary index sorted alphabetically by pinyin.

        Args:
            all_words: list of tuples (chinese, pinyin, english, lesson_id)
        """
        self.add_page()
        self.current_lesson = ""

        self.ln(5)
        self.set_font(self.latin_font, "", 22)
        self._set_color("text")
        self.cell(0, 12, "Complete Vocabulary Index", align="C")
        self.ln(5)
        self.set_font(self.cjk_font, "", 14)
        self._set_color("secondary")
        self.cell(0, 10, "词汇总表", align="C")
        self.ln(12)

        # Decorative line
        self.set_draw_color(*PDF_STYLE["colors"]["primary"])
        self.set_line_width(0.8)
        cx = self.w / 2
        self.line(cx - 40, self.get_y(), cx + 40, self.get_y())
        self.set_line_width(0.2)
        self.ln(8)

        # Sort by pinyin (strip tone marks for sorting, use lowercase)
        import unicodedata

        def sort_key(word):
            """Generate sort key from pinyin, stripping diacritics."""
            py = word[1].lower()
            # Decompose unicode and strip combining marks (tone diacritics)
            nfkd = unicodedata.normalize("NFKD", py)
            stripped = "".join(c for c in nfkd if not unicodedata.combining(c))
            return stripped

        sorted_words = sorted(all_words, key=sort_key)

        # Group by first letter
        current_letter = ""
        x_start = PDF_STYLE["margin_left"]
        col_zh = 25
        col_py = 35
        col_en = 65
        col_lesson = 25

        for zh, py, english, lesson_id in sorted_words:
            first = sort_key((zh, py, english, lesson_id))[0].upper()
            if first != current_letter:
                current_letter = first
                self._check_page_space(15)
                self.ln(5)
                self.set_font(self.latin_font, "", 14)
                self._set_color("primary")
                self.set_x(x_start)
                self.cell(0, 8, current_letter)
                self.ln(8)
                # Thin line under letter
                self.set_draw_color(*PDF_STYLE["colors"]["primary"])
                self.line(x_start, self.get_y(), x_start + 20, self.get_y())
                self.ln(3)

            self._check_page_space(9)

            # Chinese
            self.set_font(self.cjk_font, "", 11)
            self._set_color("text")
            self.set_x(x_start + 5)
            self.cell(col_zh, 7, zh)

            # Pinyin
            self.set_font(self.latin_font, "", 10)
            self._set_color("pinyin")
            self.cell(col_py, 7, f"({py})")

            # English
            self._set_color("text")
            self.cell(col_en, 7, english)

            # Lesson reference
            self._set_color("secondary")
            self.set_font(self.latin_font, "", 9)
            self.cell(col_lesson, 7, f"L{lesson_id}")
            self.ln(7)

    def add_answer_key_compilation(self, all_exercises):
        """Compiled answer key for all lessons.

        Args:
            all_exercises: list of tuples (lesson_id, lesson_title, exercises_list)
        """
        self.add_page()
        self.current_lesson = ""

        self.ln(5)
        self.set_font(self.latin_font, "", 22)
        self._set_color("text")
        self.cell(0, 12, "Answer Key Compilation", align="C")
        self.ln(5)
        self.set_font(self.cjk_font, "", 14)
        self._set_color("secondary")
        self.cell(0, 10, "答案汇总", align="C")
        self.ln(12)

        # Decorative line
        self.set_draw_color(*PDF_STYLE["colors"]["primary"])
        self.set_line_width(0.8)
        cx = self.w / 2
        self.line(cx - 40, self.get_y(), cx + 40, self.get_y())
        self.set_line_width(0.2)
        self.ln(8)

        x_start = PDF_STYLE["margin_left"]

        for lesson_id, lesson_title, exercises in all_exercises:
            if not exercises:
                continue

            self._check_page_space(20)

            # Lesson header
            self.set_font(self.latin_font, "", 13)
            self._set_color("primary")
            self.set_x(x_start)
            self.cell(0, 8, f"Lesson {lesson_id}: {lesson_title}")
            self.ln(9)

            for i, ex in enumerate(exercises, 1):
                answer = ex.get("answer", "")
                if not answer:
                    continue

                self._check_page_space(10)

                self.set_font(self.latin_font, "", 10)
                self._set_color("secondary")
                self.set_x(x_start + 5)
                self.cell(12, 7, f"{i}.")

                self.set_font(self.cjk_font, "", 11)
                self._set_color("text")
                self.cell(0, 7, str(answer))
                self.ln(7)

            self.ln(5)

    # ================================================================
    # HELPER METHODS
    # ================================================================

    def _section_header(self, title_en, pinyin=""):
        """Add a section header with decorative line."""
        self._check_page_space(20)

        # Section title
        self.set_font(self.latin_font, "", PDF_STYLE["heading_font_size"])
        self._set_color("text")
        self.cell(0, 10, title_en)
        self.ln(10)

        # Accent line under header
        self.set_draw_color(*PDF_STYLE["colors"]["primary"])
        self.set_line_width(0.8)
        self.line(PDF_STYLE["margin_left"], self.get_y(),
                  PDF_STYLE["margin_left"] + 60, self.get_y())
        self.set_line_width(0.2)
        self.ln(3)

    def _check_page_space(self, needed_mm):
        """Check if enough space on page, add new page if not."""
        if self.get_y() + needed_mm > self.h - PDF_STYLE["margin_bottom"] - 10:
            self.add_page()


def download_fonts():
    """Check system fonts availability. Uses macOS system fonts, no download needed."""
    cjk_paths = [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for path in cjk_paths:
        if os.path.exists(path):
            print(f"  Found CJK font: {os.path.basename(path)}")
            return True
    print("  WARNING: No CJK font found. Chinese characters may not render.")
    return False
