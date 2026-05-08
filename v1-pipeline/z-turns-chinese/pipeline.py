#!/usr/bin/env python3
"""
Z Turns Chinese - Standardized Production Pipeline
标准化教材生产管线

A unified entry point for generating all books in the Z Turns Chinese series.

Usage:
    python3 pipeline.py --book 1 --chapters all        # Generate complete Book 1
    python3 pipeline.py --book 2 --chapters 1-5        # Generate Book 2 chapters 1-5
    python3 pipeline.py --book 3 --from-getnotes --topic "restaurant"
    python3 pipeline.py --validate --book 1            # Validate existing content
    python3 pipeline.py --status                       # Show pipeline status
"""

import argparse
import os
import sys
import json
import time
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

from methodology import BOOK_SERIES, METHODOLOGY
from book_template import BookTemplate, validate_chapter
from config import HSK_LEVELS, BOOK1_LESSONS


BANNER = """
  ╔══════════════════════════════════════════════════════════╗
  ║     Z Turns Chinese — Production Pipeline v1.0          ║
  ║     Standardized Multi-Book Generation System           ║
  ╚══════════════════════════════════════════════════════════╝
"""


# ============================================================
# Chapter range parsing
# ============================================================

def parse_chapter_range(chapters_arg: str, book_key: str) -> list[int]:
    """
    Parse a chapters argument into a list of chapter IDs.

    Accepts:
        "all"       → all chapters for the book
        "1-5"       → chapters 1 through 5
        "3"         → chapter 3 only
        "1,3,5"     → chapters 1, 3, and 5
    """
    series = BOOK_SERIES.get(book_key, {})
    total = series.get("chapters", 15)

    if chapters_arg.lower() == "all":
        return list(range(1, total + 1))

    if "-" in chapters_arg and "," not in chapters_arg:
        parts = chapters_arg.split("-")
        try:
            start, end = int(parts[0]), int(parts[1])
            return list(range(start, end + 1))
        except (ValueError, IndexError):
            print(f"  [!] Invalid chapter range: '{chapters_arg}'. Use '1-5' or 'all'.")
            sys.exit(1)

    if "," in chapters_arg:
        try:
            return [int(c.strip()) for c in chapters_arg.split(",")]
        except ValueError:
            print(f"  [!] Invalid chapter list: '{chapters_arg}'. Use '1,3,5'.")
            sys.exit(1)

    try:
        return [int(chapters_arg)]
    except ValueError:
        print(f"  [!] Invalid chapters argument: '{chapters_arg}'.")
        sys.exit(1)


# ============================================================
# Status display
# ============================================================

def handle_status():
    """Show pipeline status: all systems, all books, output files."""
    print("=== Pipeline Status ===\n")

    # AI Engine
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    print(f"  Claude AI Engine:   {'READY' if api_key else 'NOT CONFIGURED'}")
    if not api_key:
        print("    -> export ANTHROPIC_API_KEY='sk-ant-...'")

    # GetNotes
    gn_key = os.environ.get("GETNOTE_API_KEY", "")
    gn_cid = os.environ.get("GETNOTE_CLIENT_ID", "")
    print(f"  GetNotes Client:    {'READY' if (gn_key and gn_cid) else 'NOT CONFIGURED'}")

    # Fonts
    try:
        from pdf_builder import download_fonts
        font_ok = download_fonts()
        print(f"  CJK Fonts:          {'READY' if font_ok else 'MISSING'}")
    except ImportError:
        print("  CJK Fonts:          UNKNOWN (pdf_builder import failed)")

    # Offline lessons
    try:
        from lesson_data import get_available_lessons
        lessons = get_available_lessons()
        print(f"  Offline Lessons:    {len(lessons)} available {lessons}")
    except ImportError:
        print("  Offline Lessons:    UNKNOWN")

    # Output directory
    output_dir = os.path.join(PROJECT_DIR, "output")
    if os.path.exists(output_dir):
        pdfs = [f for f in os.listdir(output_dir) if f.endswith(".pdf")]
        print(f"  Generated PDFs:     {len(pdfs)} files in output/")
    else:
        print("  Generated PDFs:     0 (output/ not yet created)")

    # Book series
    print("\n=== Book Series ===\n")
    for key, info in BOOK_SERIES.items():
        print(f"  [{key}] {info['name']}")
        print(f"         Level: {info['level']} | HSK {info['hsk_target']} | "
              f"{info['chapters']} chapters | {info['vocab_target']} vocab target")
        print(f"         {info['promise']}")
        print()

    # Methodology summary
    print("=== Methodology ===\n")
    proto = METHODOLOGY["daily_protocol"]
    print(f"  Daily Protocol: {len(proto)} steps")
    for step in proto:
        print(f"    {step['step']}. {step['name']} ({step['duration_min']} min) — {step['description'][:60]}...")

    print()


# ============================================================
# Validation
# ============================================================

def handle_validate(book_num: int):
    """Validate all available lesson data for a book."""
    book_key = f"book{book_num}"
    template = BookTemplate(book_key)

    print(f"=== Validating {template.name} ===\n")

    try:
        from lesson_data import LESSONS, get_available_lessons
    except ImportError:
        print("  [!] Could not import lesson_data.")
        return

    available = get_available_lessons()
    if not available:
        print("  No lessons found to validate.")
        return

    errors_found = 0
    for lid in available:
        lesson = LESSONS.get(lid)
        if lesson is None:
            continue
        errors = template.validate_chapter(lesson)
        if errors:
            errors_found += len(errors)
            print(f"  Lesson {lid} ({lesson.get('title_en', '?')}): {len(errors)} issue(s)")
            for e in errors:
                print(f"    - {e}")
        else:
            print(f"  Lesson {lid} ({lesson.get('title_en', '?')}): OK")

    print(f"\n  Total issues: {errors_found}")
    if errors_found == 0:
        print("  All lessons pass validation.")
    else:
        print("  Fix the issues above before generating PDFs.")


# ============================================================
# Book generation
# ============================================================

def handle_generate_book(book_num: int, chapters_arg: str, output_dir: str = None):
    """Generate PDF chapters for a book."""
    book_key = f"book{book_num}"

    if book_key not in BOOK_SERIES:
        print(f"  [!] Unknown book number: {book_num}. Valid: 1, 2, 3")
        sys.exit(1)

    template = BookTemplate(book_key)
    chapter_ids = parse_chapter_range(chapters_arg, book_key)

    output_dir = output_dir or os.path.join(PROJECT_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)

    print(f"=== Generating {template.name} ===")
    print(f"    Chapters: {chapter_ids}")
    print(f"    Output:   {output_dir}\n")

    try:
        from pdf_builder import download_fonts
        from generator import LessonGenerator
        from lesson_data import LESSONS, get_available_lessons
    except ImportError as e:
        print(f"  [!] Import error: {e}")
        sys.exit(1)

    download_fonts()
    gen = LessonGenerator(output_dir)

    available = get_available_lessons()
    generated = []
    skipped = []

    for cid in chapter_ids:
        if cid not in available:
            print(f"  [skip] Chapter {cid}: no pre-built data available")
            skipped.append(cid)
            continue

        lesson = LESSONS.get(cid)
        errors = template.validate_chapter(lesson)
        if errors:
            print(f"  [warn] Chapter {cid} has {len(errors)} validation issue(s) — generating anyway")
            for e in errors:
                print(f"         - {e}")

        path = gen.generate_lesson(cid)
        if path:
            generated.append(path)
            print(f"  [done] Chapter {cid}: {os.path.basename(path)}")
        else:
            print(f"  [fail] Chapter {cid}: generation failed")

    print(f"\n  Generated: {len(generated)} PDF(s)")
    if skipped:
        print(f"  Skipped:   {skipped} (no pre-built data; use AI generation)")
    print(f"  Output:    {output_dir}")
    return generated


def handle_generate_complete_book(book_num: int, output_dir: str = None):
    """Generate a merged complete book PDF."""
    book_key = f"book{book_num}"
    template = BookTemplate(book_key)

    output_dir = output_dir or os.path.join(PROJECT_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)

    print(f"=== Generating Complete {template.name} PDF ===\n")

    try:
        from pdf_builder import download_fonts
        from generator import LessonGenerator
    except ImportError as e:
        print(f"  [!] Import error: {e}")
        sys.exit(1)

    download_fonts()
    gen = LessonGenerator(output_dir)

    if book_num == 1:
        path = gen.generate_complete_book(
            book_title=template.name,
            author=template.author,
        )
        if path:
            print(f"\n  Complete book: {path}")
        return path
    else:
        print(f"  [!] Complete book generation for Book {book_num} not yet implemented.")
        print("      Use --chapters all to generate individual chapter PDFs.")
        return None


# ============================================================
# GetNotes-based generation
# ============================================================

def handle_from_getnotes(book_num: int, topic: str, output_dir: str = None):
    """Generate lessons by pulling content from GetNotes."""
    book_key = f"book{book_num}"
    template = BookTemplate(book_key)

    print(f"=== Generating from GetNotes: topic='{topic}' ===\n")

    gn_key = os.environ.get("GETNOTE_API_KEY", "")
    gn_cid = os.environ.get("GETNOTE_CLIENT_ID", "")
    if not (gn_key and gn_cid):
        print("  [!] GetNotes credentials not configured.")
        print("      Set GETNOTE_API_KEY and GETNOTE_CLIENT_ID environment variables.")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("  [!] ANTHROPIC_API_KEY not set. AI generation requires this.")
        sys.exit(1)

    try:
        from ai_commander import AICommander
    except ImportError as e:
        print(f"  [!] Import error: {e}")
        sys.exit(1)

    output_dir = output_dir or os.path.join(PROJECT_DIR, "output")
    commander = AICommander(output_dir=output_dir)

    # Add GetNotes source for this topic
    commander.add_source("getnotes_topic", topic)

    # Build mission brief with methodology context
    brief = (
        f"Create {template.chapter_count} lessons about '{topic}' "
        f"for {template.name} ({template.level} level, HSK {template.hsk_level}). "
        f"{template.metadata['promise']}"
    )

    print(f"  Mission: {brief}\n")
    commander.execute_mission(mission_brief=brief)


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Z Turns Chinese Production Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 pipeline.py --book 1 --chapters all
  python3 pipeline.py --book 1 --chapters 1-5
  python3 pipeline.py --book 1 --chapters 3
  python3 pipeline.py --book 2 --chapters 1-5 --output /tmp/book2
  python3 pipeline.py --book 3 --from-getnotes --topic "restaurant"
  python3 pipeline.py --validate --book 1
  python3 pipeline.py --status
        """,
    )

    parser.add_argument("--book", type=int, choices=[1, 2, 3], help="Book number (1, 2, or 3)")
    parser.add_argument("--chapters", type=str, default="all",
                        help="Chapters to generate: 'all', '1-5', '3', '1,3,5'")
    parser.add_argument("--complete", action="store_true",
                        help="Generate a merged single-PDF complete book")
    parser.add_argument("--from-getnotes", action="store_true",
                        help="Pull content from GetNotes (requires --topic)")
    parser.add_argument("--topic", type=str,
                        help="Topic for GetNotes search or AI generation")
    parser.add_argument("--validate", action="store_true",
                        help="Validate existing lesson content (requires --book)")
    parser.add_argument("--status", action="store_true",
                        help="Show pipeline and system status")
    parser.add_argument("--output", type=str,
                        help="Output directory (default: ./output/)")

    args = parser.parse_args()

    print(BANNER)

    if args.status:
        handle_status()
        return

    if args.validate:
        if not args.book:
            print("  [!] --validate requires --book N")
            sys.exit(1)
        handle_validate(args.book)
        return

    if not args.book:
        parser.print_help()
        print("\n  Tip: Start with 'python3 pipeline.py --status' to check system readiness.")
        return

    if args.from_getnotes:
        if not args.topic:
            print("  [!] --from-getnotes requires --topic TOPIC")
            sys.exit(1)
        handle_from_getnotes(args.book, args.topic, args.output)
        return

    if args.complete:
        handle_generate_complete_book(args.book, args.output)
        return

    handle_generate_book(args.book, args.chapters, args.output)


if __name__ == "__main__":
    main()
