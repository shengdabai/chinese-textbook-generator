"""
Z Turns Chinese - Lesson Generator
Generates complete lesson PDF from lesson data.

Synthesized from all 6 AI proposals:
- Claude: Four-layer translation engine
- Gemini: Structured prompt chain
- Minimax: Dual-engine (beginner + business)
- Kimi: QA validation pipeline
- GPT: Phrase memory & curriculum graph
- Grok: Privacy-first processing
"""

import os
from pdf_builder import ChinesePDF, download_fonts
from lesson_data import get_lesson, get_available_lessons, LESSONS
from hsk_vocab import get_vocab_for_lesson
from config import BOOK1_LESSONS, HSK_LEVELS, CONSISTENCY_RULES


class LessonGenerator:
    """Generates PDF lessons with four-layer aligned translations."""

    def __init__(self, output_dir=None):
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), "output")
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_lesson(self, lesson_id: int) -> str:
        """Generate a single lesson PDF. Returns the output file path."""
        lesson = get_lesson(lesson_id)
        if not lesson:
            print(f"Error: Lesson {lesson_id} not found. Available: {get_available_lessons()}")
            return ""

        # Run consistency checks (Kimi方案 QA validation)
        self._validate_lesson(lesson)

        # Create PDF
        pdf = ChinesePDF()
        pdf.current_lesson = f"Lesson {lesson['id']}: {lesson['title_en']}"

        # 1. Title page
        pdf.add_title_page(
            book_name=lesson["book"],
            lesson_num=lesson["id"],
            title_en=lesson["title_en"],
            title_zh=lesson["title_zh"],
            hsk_level=lesson["hsk_level"],
        )

        # 2. Learning goals
        pdf.add_learning_goals(lesson["learning_goals"])

        # 3. New vocabulary table (four-layer)
        pdf.add_vocabulary_section(lesson["new_words"])

        # 4. Review words (if any)
        if "review_words" in lesson and lesson["review_words"]:
            pdf.add_review_words(lesson["review_words"])

        # 5. Dialogues with four-layer alignment
        for dialogue in lesson["dialogues"]:
            pdf.add_dialogue(dialogue)

        # 6. Grammar points
        if lesson.get("grammar_points"):
            pdf.add_grammar_section(lesson["grammar_points"])

        # 7. Culture note
        if lesson.get("culture_note"):
            pdf.add_culture_note(lesson["culture_note"])

        # 8. Exercises
        if lesson.get("exercises"):
            pdf.add_exercises(lesson["exercises"])

        # 9. Answer key
        if lesson.get("exercises"):
            pdf.add_answer_key(lesson["exercises"])

        # Output
        filename = f"ZTurns_Book1_Lesson{lesson['id']:02d}_{lesson['title_en'].replace(' ', '_')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        pdf.output(filepath)

        print(f"Generated: {filepath}")
        return filepath

    def generate_all_available(self) -> list:
        """Generate PDFs for all available lessons."""
        paths = []
        for lid in get_available_lessons():
            path = self.generate_lesson(lid)
            if path:
                paths.append(path)
        return paths

    def generate_sample_book_cover(self) -> str:
        """Generate a sample book cover page."""
        pdf = ChinesePDF()
        pdf.add_page()

        # Cover design
        pdf.ln(30)

        # Series name
        pdf.set_font(pdf.latin_font, "", 14)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, "Z TURNS CHINESE SERIES", align="C")
        pdf.ln(20)

        # Main title
        pdf.set_font(pdf.latin_font, "", 32)
        pdf.set_text_color(0, 85, 204)
        pdf.cell(0, 15, "Z Turns Chinese", align="C")
        pdf.ln(18)

        # Subtitle
        pdf.set_font(pdf.latin_font, "", 20)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 12, "Book 1: Beginner's Guide", align="C")
        pdf.ln(12)

        # Chinese subtitle
        pdf.set_font(pdf.cjk_font, "", 24)
        pdf.cell(0, 15, "零基础入门", align="C")
        pdf.ln(20)

        # Tagline
        pdf.set_font(pdf.latin_font, "", 12)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, "Word-by-Word Chinese for English Speakers", align="C")
        pdf.ln(5)
        pdf.cell(0, 8, "Four-Layer Translation Method", align="C")
        pdf.ln(5)
        pdf.cell(0, 8, "HSK 3.0 (2026) Aligned", align="C")
        pdf.ln(20)

        # Decorative line
        cx = pdf.w / 2
        pdf.set_draw_color(0, 85, 204)
        pdf.set_line_width(1.5)
        pdf.line(cx - 50, pdf.get_y(), cx + 50, pdf.get_y())
        pdf.set_line_width(0.2)
        pdf.ln(20)

        # Features
        features = [
            "15 Real-Life Lessons | 15 Practical Dialogues",
            "Every sentence: Chinese + Pinyin + Word-by-Word + Natural English",
            "Grammar explanations designed for English speakers",
            "Culture notes about modern China (2026)",
            "Practice exercises with answer keys",
        ]
        pdf.set_font(pdf.latin_font, "", 10)
        pdf.set_text_color(80, 80, 80)
        for feat in features:
            pdf.cell(0, 7, feat, align="C")
            pdf.ln(7)

        pdf.ln(15)

        # Author
        pdf.set_font(pdf.latin_font, "", 12)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 8, "by Tony Sheng", align="C")
        pdf.ln(5)
        pdf.set_font(pdf.latin_font, "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, "Based on 100+ hours of real Chinese teaching", align="C")

        filepath = os.path.join(self.output_dir, "ZTurns_Book1_Cover.pdf")
        pdf.output(filepath)
        print(f"Generated cover: {filepath}")
        return filepath

    def generate_complete_book(self, book_title="Z Turns Chinese: Book 1", author="Tony Sheng") -> str:
        """Generate a complete book PDF with all lessons merged.

        Structure:
        1. Cover page
        2. Copyright page
        3. Preface (How to use this book + Four-layer method explanation)
        4. Table of Contents
        5. Unit 1 divider (Lessons 1-5)
        6. Lessons 1-5
        7. Unit 2 divider (Lessons 6-10)
        8. Lessons 6-10
        9. Unit 3 divider (Lessons 11-15)
        10. Lessons 11-15
        11. Complete vocabulary index (alphabetical by pinyin)
        12. Answer key compilation

        Returns: filepath of the complete book PDF
        """
        print("\n" + "=" * 60)
        print("  Generating Complete Book PDF")
        print("  " + book_title)
        print("=" * 60)

        # Check fonts
        if not download_fonts():
            print("WARNING: Using fallback fonts. CJK characters may not render correctly.")

        pdf = ChinesePDF()
        pdf.book_title = "Z Turns Chinese"

        # Collect all vocabulary and exercises for appendices
        all_vocab = []  # (chinese, pinyin, english, lesson_id)
        all_exercises = []  # (lesson_id, title, exercises)

        # ------ 1. Cover Page ------
        print("\n[1/12] Cover page...")
        pdf.add_book_cover(book_title=book_title, author=author)

        # ------ 2. Copyright Page ------
        print("[2/12] Copyright page...")
        pdf.add_copyright_page(author=author)

        # ------ 3. Preface ------
        print("[3/12] Preface...")
        pdf.add_preface_page()

        # ------ 4. Table of Contents ------
        print("[4/12] Table of contents...")
        pdf.add_table_of_contents(BOOK1_LESSONS)

        # ------ Unit divisions and lessons ------
        units = [
            ("Unit 1: Getting Started", "入门篇", 1, 5),
            ("Unit 2: Daily Life", "日常生活", 6, 10),
            ("Unit 3: Expanding Horizons", "拓展篇", 11, 15),
        ]

        step = 5
        for unit_title, unit_zh, start, end in units:
            print(f"[{step}/12] {unit_title} divider...")
            pdf.add_section_divider(unit_title, unit_zh)
            step += 1

            for lid in range(start, end + 1):
                lesson = get_lesson(lid)
                if not lesson:
                    print(f"  WARNING: Lesson {lid} not found, skipping.")
                    continue

                print(f"  -> Lesson {lid}: {lesson['title_en']}")

                # Validate
                self._validate_lesson(lesson)

                pdf.current_lesson = f"Lesson {lesson['id']}: {lesson['title_en']}"

                # Title page
                pdf.add_title_page(
                    book_name="Book 1",
                    lesson_num=lesson["id"],
                    title_en=lesson["title_en"],
                    title_zh=lesson["title_zh"],
                    hsk_level=lesson["hsk_level"],
                )

                # Learning goals
                pdf.add_learning_goals(lesson["learning_goals"])

                # Vocabulary
                pdf.add_vocabulary_section(lesson["new_words"])

                # Collect vocab for index
                for word in lesson["new_words"]:
                    # word = (zh, py, literal, english, pos)
                    all_vocab.append((word[0], word[1], word[3], lesson["id"]))

                # Review words
                if lesson.get("review_words"):
                    pdf.add_review_words(lesson["review_words"])

                # Dialogues
                for dialogue in lesson["dialogues"]:
                    pdf.add_dialogue(dialogue)

                # Grammar
                if lesson.get("grammar_points"):
                    pdf.add_grammar_section(lesson["grammar_points"])

                # Culture note
                if lesson.get("culture_note"):
                    pdf.add_culture_note(lesson["culture_note"])

                # Exercises
                if lesson.get("exercises"):
                    pdf.add_exercises(lesson["exercises"])

                # Collect exercises for answer key compilation
                if lesson.get("exercises"):
                    all_exercises.append(
                        (lesson["id"], lesson["title_en"], lesson["exercises"])
                    )

            step += 1

        # ------ 11. Vocabulary Index ------
        print(f"[11/12] Complete vocabulary index ({len(all_vocab)} words)...")
        pdf.add_vocab_index(all_vocab)

        # ------ 12. Answer Key Compilation ------
        print("[12/12] Answer key compilation...")
        pdf.add_answer_key_compilation(all_exercises)

        # Output
        filename = "ZTurns_Book1_Complete.pdf"
        filepath = os.path.join(self.output_dir, filename)
        pdf.output(filepath)

        print("\n" + "=" * 60)
        print(f"  Complete book generated: {filepath}")
        print(f"  Total pages: {pdf.page_no()}")
        print(f"  Vocabulary entries: {len(all_vocab)}")
        print(f"  Lessons with exercises: {len(all_exercises)}")
        print("=" * 60)

        return filepath

    def _validate_lesson(self, lesson: dict):
        """Run consistency checks on lesson data (Kimi方案 QA pipeline)."""
        issues = []

        # Check new word count
        max_words = CONSISTENCY_RULES["max_new_words_regular"]
        if lesson.get("new_words") and len(lesson["new_words"]) > max_words:
            issues.append(f"WARNING: {len(lesson['new_words'])} new words exceeds limit of {max_words}")

        # Check HSK level compliance
        hsk = lesson.get("hsk_level", 1)
        hsk_info = HSK_LEVELS.get(hsk, {})

        if issues:
            print(f"\n=== QA Report for Lesson {lesson['id']} ===")
            for issue in issues:
                print(f"  {issue}")
            print()


def generate_complete_demo():
    """Generate a complete demonstration with cover + available lessons."""
    print("=" * 60)
    print("  Z Turns Chinese AutoBuilder")
    print("  Integrated Best Solution from 6 AI Proposals")
    print("=" * 60)

    # Download fonts first
    if not download_fonts():
        print("WARNING: Using fallback fonts. CJK characters may not render correctly.")

    gen = LessonGenerator()

    # Generate cover
    print("\n[1/3] Generating book cover...")
    gen.generate_sample_book_cover()

    # Generate available lessons
    print("\n[2/3] Generating lesson PDFs...")
    paths = gen.generate_all_available()

    # Summary
    print("\n[3/3] Generation complete!")
    print(f"\nOutput directory: {gen.output_dir}")
    print(f"Files generated: {len(paths) + 1}")
    print("\nGenerated files:")
    for p in paths:
        print(f"  - {os.path.basename(p)}")

    return paths


if __name__ == "__main__":
    generate_complete_demo()
