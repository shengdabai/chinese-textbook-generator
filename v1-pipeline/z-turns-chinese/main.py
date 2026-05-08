#!/usr/bin/env python3
"""
Z Turns Chinese AutoBuilder v3.0 - AI-Powered Edition
=====================================================

Automated Chinese Learning Guide Generator with AI Commander

Features:
  - AI Commander: Give a mission, get a complete course
  - GetNotes Integration: Pull from your teaching notes & recordings
  - Multi-source Input: URLs, PDFs, text files
  - Claude AI Engine: Intelligent content generation
  - Four-Layer Translation: Chinese + Pinyin + Word-by-Word + Natural English
  - HSK 3.0 (2026) Compliant

Usage:
    python3 main.py mission "Create a pinyin learning course"
    python3 main.py mission "商务中文教程，15课，HSK2"
    python3 main.py generate --topic "restaurant" --hsk 1 --lessons 3
    python3 main.py notes --list-topics
    python3 main.py notes --search "点餐"
    python3 main.py extract --url "https://example.com/article"
    python3 main.py extract --pdf "/path/to/file.pdf"
    python3 main.py offline --lesson 1
    python3 main.py offline --all
    python3 main.py status
    python3 main.py --info
"""

import argparse
import sys
import os

# Add project dir to path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)


BANNER = """
  ╔══════════════════════════════════════════════════════════╗
  ║        Z Turns Chinese AutoBuilder v3.0                 ║
  ║        AI-Powered Chinese Learning Guide Generator      ║
  ║                                                          ║
  ║   AI Commander | GetNotes | Claude API | Multi-Source    ║
  ╚══════════════════════════════════════════════════════════╝
"""


def main():
    parser = argparse.ArgumentParser(
        description="Z Turns Chinese AutoBuilder v3.0 - AI-Powered Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  mission     Give AI Commander a mission to create a complete course
  generate    Generate lessons with AI (requires ANTHROPIC_API_KEY)
  notes       Interact with GetNotes (list topics, search notes, fetch content)
  extract     Extract content from URLs or PDF files
  offline     Generate from pre-built lesson data (no API needed)
  status      Show system status and available integrations

Examples:
  python3 main.py mission "Create a 10-lesson pinyin course for beginners"
  python3 main.py mission "生成一套拼音学习教程，10课，零基础"
  python3 main.py generate --topic "ordering food" --hsk 1 --num 3
  python3 main.py notes --list-topics
  python3 main.py notes --search "餐厅"
  python3 main.py notes --fetch-topic TOPIC_ID
  python3 main.py extract --url "https://example.com/chinese-article"
  python3 main.py extract --pdf "/path/to/document.pdf"
  python3 main.py offline --lesson 1
  python3 main.py offline --all
  python3 main.py --info
        """,
    )

    subparsers = parser.add_subparsers(dest="command")

    # === Mission command ===
    mission_parser = subparsers.add_parser("mission", help="Give AI Commander a mission")
    mission_parser.add_argument("brief", nargs="?", help="Mission description (Chinese or English)")
    mission_parser.add_argument("--sources", nargs="*", help="Additional source URLs or file paths")
    mission_parser.add_argument("--hsk", type=int, default=1, help="Target HSK level (1-3)")
    mission_parser.add_argument("--lessons", type=int, default=10, help="Number of lessons")
    mission_parser.add_argument("--output", type=str, help="Output directory")
    mission_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")

    # === Generate command ===
    gen_parser = subparsers.add_parser("generate", help="Generate lessons with AI")
    gen_parser.add_argument("--topic", required=True, help="Lesson topic")
    gen_parser.add_argument("--hsk", type=int, default=1, help="HSK level (1-3)")
    gen_parser.add_argument("--num", type=int, default=1, help="Number of lessons")
    gen_parser.add_argument("--context", type=str, help="Additional context (file path or text)")
    gen_parser.add_argument("--output", type=str, help="Output directory")

    # === Notes command ===
    notes_parser = subparsers.add_parser("notes", help="GetNotes integration")
    notes_parser.add_argument("--list-topics", action="store_true", help="List all knowledge bases")
    notes_parser.add_argument("--list-notes", action="store_true", help="List recent notes")
    notes_parser.add_argument("--search", type=str, help="Search notes by keyword")
    notes_parser.add_argument("--fetch-topic", type=str, help="Fetch all notes from a topic")
    notes_parser.add_argument("--fetch-note", type=str, help="Fetch a specific note by ID")
    notes_parser.add_argument("--quota", action="store_true", help="Show API quota")

    # === Extract command ===
    extract_parser = subparsers.add_parser("extract", help="Extract content from sources")
    extract_parser.add_argument("--url", type=str, help="Extract from URL")
    extract_parser.add_argument("--pdf", type=str, help="Extract from PDF file")
    extract_parser.add_argument("--file", type=str, help="Extract from text/markdown file")
    extract_parser.add_argument("--analyze", action="store_true", help="Analyze extracted content for teaching material")

    # === Offline command ===
    offline_parser = subparsers.add_parser("offline", help="Generate from pre-built data (no API)")
    offline_parser.add_argument("--lesson", type=int, help="Generate specific lesson")
    offline_parser.add_argument("--all", action="store_true", help="Generate all available lessons")
    offline_parser.add_argument("--cover", action="store_true", help="Generate book cover")
    offline_parser.add_argument("--book", action="store_true", help="Generate complete book PDF")
    offline_parser.add_argument("--output", type=str, help="Output directory")

    # === Status command ===
    subparsers.add_parser("status", help="Show system status")

    # === Global flags ===
    parser.add_argument("--info", action="store_true", help="Show system configuration")
    parser.add_argument("--privacy-demo", action="store_true", help="Run privacy filter demo")

    args = parser.parse_args()

    print(BANNER)

    # Global flags
    if args.info:
        show_info()
        return

    if args.privacy_demo:
        from privacy_filter import demo_privacy_filter
        demo_privacy_filter()
        return

    # Route to command handlers
    if args.command == "mission":
        handle_mission(args)
    elif args.command == "generate":
        handle_generate(args)
    elif args.command == "notes":
        handle_notes(args)
    elif args.command == "extract":
        handle_extract(args)
    elif args.command == "offline":
        handle_offline(args)
    elif args.command == "status":
        handle_status()
    else:
        # No command given - show help
        parser.print_help()
        print("\n  Tip: Try 'python3 main.py mission \"Create a pinyin course\"' to get started!")
        print("  Tip: Try 'python3 main.py offline --all' for quick demo (no API needed)")


# ================================================================
# COMMAND HANDLERS
# ================================================================

def handle_mission(args):
    """Handle the 'mission' command - AI Commander."""
    from ai_commander import AICommander

    commander = AICommander(output_dir=args.output)

    if args.interactive:
        commander.interactive_mode()
        return

    if not args.brief:
        print("Usage: python3 main.py mission \"Your mission description\"")
        print("\nExamples:")
        print("  python3 main.py mission \"Create a pinyin learning course, 10 lessons\"")
        print("  python3 main.py mission \"生成拼音教程\" --hsk 1 --lessons 10")
        print("  python3 main.py mission -i  (interactive mode)")
        return

    # Add any additional sources
    sources = []
    if args.sources:
        for src in args.sources:
            if src.startswith("http"):
                sources.append({"type": "url", "value": src})
            elif os.path.isfile(src):
                sources.append({"type": "file", "value": src})
            else:
                sources.append({"type": "text", "value": src})

    # Build enhanced brief with parameters
    brief = args.brief
    if args.hsk != 1:
        brief += f" (HSK level {args.hsk})"
    if args.lessons != 10:
        brief += f" ({args.lessons} lessons)"

    # Add sources to commander
    for src in sources:
        commander.add_source(src.get("type", "text"), src.get("value", ""))

    # Execute the mission
    commander.execute_mission(mission_brief=brief)


def handle_generate(args):
    """Handle the 'generate' command - AI-powered lesson generation."""
    try:
        from ai_engine import AIEngine
    except ImportError as e:
        print(f"Error importing AI engine: {e}")
        print("Make sure all dependencies are installed.")
        return

    engine = AIEngine()

    if not engine.is_available():
        print("AI Engine not available.")
        print("Set ANTHROPIC_API_KEY environment variable to enable AI generation.")
        print("\n  export ANTHROPIC_API_KEY='your-key-here'")
        print("\nOr use 'python3 main.py offline --all' for pre-built content.")
        return

    output_dir = args.output or os.path.join(PROJECT_DIR, "output")

    print(f"[AI Generate] Topic: {args.topic} | HSK: {args.hsk} | Lessons: {args.num}")
    print()

    from generator import LessonGenerator
    from pdf_builder import download_fonts
    download_fonts()
    gen = LessonGenerator(output_dir)

    previous_vocab = []
    for i in range(1, args.num + 1):
        print(f"\n--- Generating Lesson {i}/{args.num} ---")
        lesson_data = engine.generate_lesson(
            topic=args.topic,
            hsk_level=args.hsk,
            lesson_num=i,
            previous_vocab=previous_vocab,
            context_notes=args.context or "",
        )

        if lesson_data and not lesson_data.get("error"):
            # Register and generate PDF
            from lesson_data import LESSONS
            LESSONS[lesson_data["id"]] = lesson_data
            path = gen.generate_lesson(lesson_data["id"])
            if path:
                print(f"  PDF: {path}")

            # Track vocabulary for next lesson
            if lesson_data.get("new_words"):
                previous_vocab.extend([w[0] for w in lesson_data["new_words"]])
        else:
            print(f"  Failed to generate lesson {i}")

    print(f"\nGeneration complete! Output: {output_dir}")


def handle_notes(args):
    """Handle the 'notes' command - GetNotes integration."""
    try:
        from getnotes_client import GetNotesClient
    except ImportError as e:
        print(f"Error importing GetNotes client: {e}")
        return

    client = GetNotesClient()
    if not client.is_available():
        print("GetNotes not available.")
        print("Set environment variables: GETNOTE_API_KEY, GETNOTE_CLIENT_ID")
        return

    if args.quota:
        print("[GetNotes] Checking API quota...")
        quota = client.get_quota()
        if quota:
            print(f"\n  Read  - Daily: {quota.get('read', {}).get('daily', {})}")
            print(f"  Write - Daily: {quota.get('write', {}).get('daily', {})}")
        return

    if args.list_topics:
        print("[GetNotes] Listing knowledge bases...")
        topics = client.list_topics()
        if topics and topics.get("topics"):
            print(f"\n  Found {topics['total']} knowledge bases:\n")
            for t in topics["topics"]:
                print(f"  [{t['id']}] {t['name']}")
                if t.get("description"):
                    print(f"      {t['description']}")
        else:
            print("  No knowledge bases found.")
        return

    if args.list_notes:
        print("[GetNotes] Listing recent notes...")
        result = client.list_notes()
        if result and result.get("notes"):
            print(f"\n  Found {result['total']} notes (showing first 20):\n")
            for n in result["notes"]:
                tags = ", ".join(t["name"] for t in n.get("tags", []))
                print(f"  [{n['id']}] {n['title'][:60]}")
                if tags:
                    print(f"      Tags: {tags}")
        return

    if args.search:
        print(f"[GetNotes] Searching for: {args.search}")
        results = client.search_notes_by_keyword(args.search)
        if results:
            print(f"\n  Found {len(results)} matching notes:\n")
            for n in results:
                print(f"  [{n['id']}] {n['title'][:60]}")
                preview = n.get("content", "")[:100].replace("\n", " ")
                if preview:
                    print(f"      {preview}...")
        else:
            print("  No matching notes found.")
        return

    if args.fetch_topic:
        print(f"[GetNotes] Fetching notes from topic: {args.fetch_topic}")
        notes = client.get_all_notes_for_topic(args.fetch_topic)
        if notes:
            print(f"\n  Retrieved {len(notes)} notes from topic.")
            for n in notes[:10]:
                print(f"  [{n.get('note_id', '?')}] {n.get('title', 'Untitled')[:60]}")
            if len(notes) > 10:
                print(f"  ... and {len(notes) - 10} more")
        return

    if args.fetch_note:
        print(f"[GetNotes] Fetching note: {args.fetch_note}")
        note = client.get_note(args.fetch_note)
        if note and note.get("note"):
            n = note["note"]
            print(f"\n  Title: {n.get('title', 'Untitled')}")
            print(f"  Type: {n.get('note_type', 'unknown')}")
            print(f"  Created: {n.get('created_at', '?')}")
            content = client.extract_teaching_content(n)
            print(f"\n  Content preview:\n  {content[:500]}...")
        return

    # Default: show help
    print("Usage: python3 main.py notes [--list-topics|--list-notes|--search KEYWORD|--quota]")


def handle_extract(args):
    """Handle the 'extract' command - Content extraction."""
    try:
        from content_extractor import ContentExtractor
    except ImportError as e:
        print(f"Error importing content extractor: {e}")
        return

    extractor = ContentExtractor()

    if args.url:
        print(f"[Extract] Fetching URL: {args.url}")
        result = extractor.extract_from_url(args.url)
        if result:
            print(f"\n  Title: {result.get('title', 'N/A')}")
            print(f"  Content length: {len(result.get('content', ''))} chars")
            preview = result.get("content", "")[:500]
            print(f"\n  Preview:\n  {preview}...")

            if args.analyze:
                print("\n[Analyze] Analyzing content for teaching material...")
                analysis = extractor.analyze_content(result.get("content", ""))
                print(f"  Chinese text found: {len(analysis.get('chinese_text', ''))} chars")
                print(f"  Vocabulary items: {len(analysis.get('vocabulary', []))}")
                print(f"  Topics detected: {analysis.get('topics', [])}")
        return

    if args.pdf:
        print(f"[Extract] Processing PDF: {args.pdf}")
        result = extractor.extract_from_pdf(args.pdf)
        if result:
            print(f"\n  Content length: {len(result.get('content', ''))} chars")
            preview = result.get("content", "")[:500]
            print(f"\n  Preview:\n  {preview}...")
        return

    if args.file:
        print(f"[Extract] Processing file: {args.file}")
        result = extractor.extract_from_file(args.file)
        if result:
            print(f"\n  Content length: {len(result.get('content', ''))} chars")
            preview = result.get("content", "")[:500]
            print(f"\n  Preview:\n  {preview}...")
        return

    print("Usage: python3 main.py extract [--url URL|--pdf FILE|--file FILE] [--analyze]")


def handle_offline(args):
    """Handle the 'offline' command - Pre-built content generation."""
    from pdf_builder import download_fonts
    from generator import LessonGenerator

    print("[Setup] Checking fonts...")
    download_fonts()

    output_dir = args.output or os.path.join(PROJECT_DIR, "output")
    gen = LessonGenerator(output_dir)

    if args.book:
        print("\n[Offline] Generating complete book PDF...")
        path = gen.generate_complete_book()
        if path:
            print(f"\n  Done! Complete book: {path}")

    elif args.cover:
        print("\n[Offline] Generating book cover...")
        path = gen.generate_sample_book_cover()
        print(f"  Done! {path}")

    elif args.lesson:
        print(f"\n[Offline] Generating Lesson {args.lesson}...")
        path = gen.generate_lesson(args.lesson)
        if path:
            print(f"  Done! {path}")
        else:
            from lesson_data import get_available_lessons
            print(f"  Error: Lesson {args.lesson} not available.")
            print(f"  Available: {get_available_lessons()}")

    elif args.all:
        print("\n[Offline] Generating all available lessons + cover...")
        gen.generate_sample_book_cover()
        paths = gen.generate_all_available()
        print(f"\n  Complete! {len(paths) + 1} PDFs in {output_dir}")

    else:
        print("Usage: python3 main.py offline [--lesson N|--all|--cover]")


def handle_status():
    """Show system status and integration availability."""
    print("=== System Status ===\n")

    # Check AI Engine
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    print(f"  Claude AI Engine:  {'READY' if api_key else 'NOT CONFIGURED'}")
    if not api_key:
        print("    -> Set ANTHROPIC_API_KEY to enable AI generation")

    # Check GetNotes
    gn_key = os.environ.get("GETNOTE_API_KEY", "")
    gn_client = os.environ.get("GETNOTE_CLIENT_ID", "")
    print(f"  GetNotes Client:   {'READY' if (gn_key and gn_client) else 'NOT CONFIGURED'}")
    if not (gn_key and gn_client):
        print("    -> Set GETNOTE_API_KEY and GETNOTE_CLIENT_ID")

    # Check fonts
    from pdf_builder import download_fonts
    font_ok = download_fonts()
    print(f"  CJK Fonts:         {'READY' if font_ok else 'MISSING'}")

    # Check available lessons
    from lesson_data import get_available_lessons
    lessons = get_available_lessons()
    print(f"  Offline Lessons:   {len(lessons)} available ({lessons})")

    # Check output directory
    output_dir = os.path.join(PROJECT_DIR, "output")
    if os.path.exists(output_dir):
        pdfs = [f for f in os.listdir(output_dir) if f.endswith(".pdf")]
        print(f"  Generated PDFs:    {len(pdfs)} files")
    else:
        print(f"  Generated PDFs:    0 files")

    print(f"\n=== Quick Start ===\n")
    if api_key:
        print("  python3 main.py mission \"Create a pinyin course\"   # AI Commander")
        print("  python3 main.py generate --topic \"food\" --hsk 1    # Single topic")
    else:
        print("  python3 main.py offline --all                        # Pre-built content")
        print("  export ANTHROPIC_API_KEY='sk-...'                     # Enable AI mode")

    if gn_key:
        print("  python3 main.py notes --list-topics                   # Browse notes")
        print("  python3 main.py notes --search \"拼音\"               # Search notes")


def show_info():
    """Display system configuration and curriculum info."""
    from config import HSK_LEVELS, BOOK1_LESSONS, CONSISTENCY_RULES, FOUR_LAYERS
    from lesson_data import get_available_lessons

    print("=== System Configuration ===\n")

    print("Four-Layer Translation Method:")
    for key, desc in FOUR_LAYERS.items():
        print(f"  {key}: {desc}")

    print("\n\nHSK 3.0 (2026) Level Mapping:")
    print(f"  {'Level':<8} {'Vocab':<10} {'New/Lesson':<12} {'CEFR':<6} {'Book'}")
    print(f"  {'-'*60}")
    for level, info in HSK_LEVELS.items():
        print(f"  HSK {level:<4} {info['total_vocab']:<10} {info['new_words_per_lesson']:<12} {info['cefr']:<6} {info['book']}")

    print("\n\nBook 1 Curriculum (15 Lessons):")
    print(f"  {'ID':<4} {'Title':<30} {'Topic':<15} {'New Words':<10} {'Grammar'}")
    print(f"  {'-'*80}")
    for lesson in BOOK1_LESSONS:
        print(f"  L{lesson['id']:<3} {lesson['title_en']:<30} {lesson['topic']:<15} {lesson['new_words']:<10} {lesson['grammar']}")

    print(f"\n\nConsistency Rules:")
    for key, val in CONSISTENCY_RULES.items():
        print(f"  {key}: {val}")

    print(f"\n\nAvailable Offline Lessons: {get_available_lessons()}")

    print("\n\n=== Architecture ===\n")
    print("  Mission Brief (user input)")
    print("      |")
    print("      v")
    print("  AI Commander (ai_commander.py)")
    print("      |--- Market Analysis (ai_engine.py)")
    print("      |--- Course Planning (ai_engine.py)")
    print("      |--- Material Gathering")
    print("      |       |--- GetNotes (getnotes_client.py)")
    print("      |       |--- URL/PDF (content_extractor.py)")
    print("      |       |--- Privacy Filter (privacy_filter.py)")
    print("      |--- Lesson Generation (ai_engine.py)")
    print("      |--- Quality Validation (config.py rules)")
    print("      |--- PDF Production (pdf_builder.py)")
    print("      v")
    print("  Final PDFs (output/)")


if __name__ == "__main__":
    main()
