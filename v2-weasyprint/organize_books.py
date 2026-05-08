#!/usr/bin/env python3
"""
Organize Z Turns Chinese ebooks into final-books/ directory.
Merges chapters and copies PDFs.
"""

import os
import shutil
from pathlib import Path

BASE = Path(".").parent
FINAL = BASE / "final-books"
OUTPUT = BASE / "output"

# ── Book definitions ──────────────────────────────────────────────────────────

BOOKS = [
    {
        "num": "01",
        "slug": "FromZero",
        "title": "Z Turns Chinese Book 1",
        "subtitle": "From Zero: Your First Steps in Mandarin",
        "pdf_src": "ZTurns_Book1_FromZero.pdf",
        "pdf_dst": "ZTurns_Book01_FromZero.pdf",
        "md_dst": "ZTurns_Book01_FromZero.md",
        "parts": None,  # No source chapters – create placeholder
    },
    {
        "num": "02",
        "slug": "CompleteGuide",
        "title": "Z Turns Chinese Book 2",
        "subtitle": "The Complete Guide to Conversational Mandarin",
        "pdf_src": "ZTurns_Book2_CompleteGuide.pdf",
        "pdf_dst": "ZTurns_Book02_CompleteGuide.pdf",
        "md_dst": "ZTurns_Book02_CompleteGuide.md",
        "parts": [
            ("Part 0: Before You Begin",        BASE / "part0-before-you-begin",   None),
            ("Part 1: Sound Foundation",         BASE / "part1-sound-foundation",   None),
            ("Part 2: First Steps",              BASE / "part2-first-steps",        None),
            ("Part 3: Daily Life",               BASE / "part3-daily-life",         None),
            ("Part 4: Travel & Adventure",       BASE / "part4-travel-adventure",   None),
            ("Part 5: Business Chinese",         BASE / "part5-business-chinese",   None),
            ("Part 6: Living in China",          BASE / "part6-living-in-china",    None),
        ],
    },
    {
        "num": "03",
        "slug": "RealLessons",
        "title": "Z Turns Chinese Book 3",
        "subtitle": "Real Lessons from Real Life in China",
        "pdf_src": "ZTurns_Book3_RealLessons.pdf",
        "pdf_dst": "ZTurns_Book03_RealLessons.pdf",
        "md_dst": "ZTurns_Book03_RealLessons.md",
        "parts": [
            ("Part 1: Daily Basics",             BASE / "book3-real-lessons/part1-daily-basics",      None),
            ("Part 2: Travel Stories",           BASE / "book3-real-lessons/part2-travel-stories",    None),
            ("Part 3: Culture Unlocked",         BASE / "book3-real-lessons/part3-culture-unlocked",  None),
            ("Part 4: Business & Modern Life",   BASE / "book3-real-lessons/part4-business-modern",   None),
            ("Part 5: Going Deeper",             BASE / "book3-real-lessons/part5-going-deeper",      None),
            ("Reviews",                          BASE / "book3-real-lessons/reviews",                  None),
        ],
    },
    {
        "num": "04",
        "slug": "SurvivalChinese",
        "title": "Z Turns Chinese Book 4",
        "subtitle": "Survival Chinese: Everything You Need to Get Through the Day",
        "pdf_src": "ZTurns_Book4_SurvivalChinese.pdf",
        "pdf_dst": "ZTurns_Book04_SurvivalChinese.pdf",
        "md_dst": "ZTurns_Book04_SurvivalChinese.md",
        "parts": [
            ("Section 1: Essentials",            BASE / "book4-survival-chinese/sec1-essentials",     None),
            ("Section 2: Eating",                BASE / "book4-survival-chinese/sec2-eating",         None),
            ("Section 3: Transport",             BASE / "book4-survival-chinese/sec3-transport",      None),
            ("Section 4: Money & Shopping",      BASE / "book4-survival-chinese/sec4-money",          None),
            ("Section 5: Emergency",             BASE / "book4-survival-chinese/sec5-emergency",      None),
        ],
    },
    {
        "num": "05",
        "slug": "BusinessChinese",
        "title": "Z Turns Chinese Book 5",
        "subtitle": "Business Chinese: Succeed in the Chinese Workplace",
        "pdf_src": "ZTurns_Book5_BusinessChinese.pdf",
        "pdf_dst": "ZTurns_Book05_BusinessChinese.pdf",
        "md_dst": "ZTurns_Book05_BusinessChinese.md",
        "parts": [
            ("Part 1: First 30 Days",            BASE / "book5-business-chinese/part1-first-30-days", None),
            ("Part 2: Daily Work",               BASE / "book5-business-chinese/part2-daily-work",    None),
            ("Part 3: Relationships",            BASE / "book5-business-chinese/part3-relationships", None),
            ("Part 4: Deals & Money",            BASE / "book5-business-chinese/part4-deals-money",   None),
            ("Part 5: Career Growth",            BASE / "book5-business-chinese/part5-career-growth", None),
        ],
    },
    {
        "num": "06",
        "slug": "Characters",
        "title": "Z Turns Chinese Book 6",
        "subtitle": "Characters: Read and Write Chinese",
        "pdf_src": "ZTurns_Book6_Characters.pdf",
        "pdf_dst": "ZTurns_Book06_Characters.pdf",
        "md_dst": "ZTurns_Book06_Characters.md",
        "parts": [
            ("Part 1: The Character System",     BASE / "book6-characters/part1-system",              None),
            ("Part 2: Essential 200 Characters", BASE / "book6-characters/part2-essential-200",       None),
            ("Part 3: Character Patterns",       BASE / "book6-characters/part3-patterns",            None),
            ("Part 4: Reading Real Chinese",     BASE / "book6-characters/part4-reading-real",        None),
            ("Part 5: Beyond Basics",            BASE / "book6-characters/part5-beyond",              None),
        ],
    },
    {
        "num": "07",
        "slug": "Food",
        "title": "Z Turns Chinese Book 7",
        "subtitle": "Food: Eat, Drink, and Speak Chinese",
        "pdf_src": "ZTurns_Book7_Food.pdf",
        "pdf_dst": "ZTurns_Book07_Food.pdf",
        "md_dst": "ZTurns_Book07_Food.md",
        "parts": [
            ("Part 1: Food Foundations",         BASE / "book7-food/part1-foundations",               None),
            ("Part 2: Street Food & Snacks",     BASE / "book7-food/part2-street-food",               None),
            ("Part 3: Drinks & Beverages",       BASE / "book7-food/part3-drinks",                    None),
            ("Part 4: Regional Deep Dives",      BASE / "book7-food/part4-regional",                  None),
            ("Part 5: Food & Life",              BASE / "book7-food/part5-food-life",                 None),
        ],
    },
    {
        "num": "08",
        "slug": "DigitalChina",
        "title": "Z Turns Chinese Book 8",
        "subtitle": "Digital China: Navigate Apps, WeChat, and Online Life",
        "pdf_src": "ZTurns_Book8_DigitalChina.pdf",
        "pdf_dst": "ZTurns_Book08_DigitalChina.pdf",
        "md_dst": "ZTurns_Book08_DigitalChina.md",
        "parts": [
            ("Section 1: Digital Essentials",    BASE / "book8-digital/sec1-essentials",              None),
            ("Section 2: Shopping & Delivery",   BASE / "book8-digital/sec2-shopping",                None),
            ("Section 3: Social Media",          BASE / "book8-digital/sec3-social-media",            None),
            ("Section 4: Life Apps",             BASE / "book8-digital/sec4-life-apps",               None),
            ("Section 5: Digital Culture",       BASE / "book8-digital/sec5-digital-culture",         None),
        ],
    },
    {
        "num": "09",
        "slug": "Stories",
        "title": "Z Turns Chinese Book 9",
        "subtitle": "Stories: Chinese Legends, History, and Modern Tales",
        "pdf_src": "ZTurns_Book9_Stories.pdf",
        "pdf_dst": "ZTurns_Book09_Stories.pdf",
        "md_dst": "ZTurns_Book09_Stories.md",
        "parts": [
            ("Part 1: Ancient Legends",          BASE / "book9-stories/part1-legends",                None),
            ("Part 2: Historical Stories",       BASE / "book9-stories/part2-history",                None),
            ("Part 3: Folk Tales & Wisdom",      BASE / "book9-stories/part3-folk-tales",             None),
            ("Part 4: Modern Stories",           BASE / "book9-stories/part4-modern",                 None),
            ("Part 5: Your Story",               BASE / "book9-stories/part5-your-story",             None),
        ],
    },
    {
        "num": "10",
        "slug": "SocialLife",
        "title": "Z Turns Chinese Book 10",
        "subtitle": "Social Life: Connect, Belong, and Thrive in China",
        "pdf_src": "ZTurns_Book10_SocialLife.pdf",
        "pdf_dst": "ZTurns_Book10_SocialLife.pdf",
        "md_dst": "ZTurns_Book10_SocialLife.md",
        "parts": [
            ("Part 1: Meeting People",           BASE / "book10-social/part1-meeting-people",         None),
            ("Part 2: Dating & Romance",         BASE / "book10-social/part2-dating",                 None),
            ("Part 3: Family Life",              BASE / "book10-social/part3-family",                 None),
            ("Part 4: Social Rules",             BASE / "book10-social/part4-social-rules",           None),
            ("Part 5: Belonging",                BASE / "book10-social/part5-belonging",              None),
        ],
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_md_files(directory: Path) -> list[Path]:
    """Return sorted .md files from a directory."""
    return sorted(directory.glob("*.md"))

def merge_book(book: dict) -> tuple[int, int]:
    """
    Build merged markdown for one book.
    Returns (chapter_count, line_count).
    """
    book_dir = FINAL / f"Book{book['num']}_{book['slug']}"
    book_dir.mkdir(parents=True, exist_ok=True)

    md_path = book_dir / book["md_dst"]

    # ── Book 1 placeholder ────────────────────────────────────────────────────
    if book["parts"] is None:
        content = f"""# {book['title']}
## {book['subtitle']}
**Author:** Tony Sheng

---

*Source markdown files for Book 1 are not available in this repository.*
*Please refer to the accompanying PDF: {book['pdf_dst']}*
"""
        md_path.write_text(content, encoding="utf-8")
        lines = content.count("\n")
        return 0, lines

    # ── Multi-part books ──────────────────────────────────────────────────────
    sections: list[str] = []

    # Header
    sections.append(f"# {book['title']}\n## {book['subtitle']}\n**Author:** Tony Sheng\n")

    chapter_count = 0

    for part_name, part_dir, _ in book["parts"]:
        sections.append(f"\n---\n\n# {part_name}\n")

        files = get_md_files(part_dir)
        if not files:
            sections.append(f"*No files found in {part_dir}*\n")
            continue

        for i, f in enumerate(files):
            chapter_count += 1
            content = f.read_text(encoding="utf-8").rstrip()
            if i > 0:
                sections.append("\n\n---\n")
            sections.append(f"\n{content}\n")

    full_text = "\n".join(sections)
    md_path.write_text(full_text, encoding="utf-8")
    line_count = full_text.count("\n")
    return chapter_count, line_count


def copy_pdf(book: dict):
    """Copy PDF from output/ to final-books/BookNN_Slug/."""
    src = OUTPUT / book["pdf_src"]
    dst = FINAL / f"Book{book['num']}_{book['slug']}" / book["pdf_dst"]
    if src.exists():
        shutil.copy2(src, dst)
        return True
    else:
        print(f"  WARNING: PDF not found: {src}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    FINAL.mkdir(exist_ok=True)

    print(f"\n{'Book':<35} {'Chapters':>8} {'Lines':>8} {'PDF':>6}")
    print("-" * 62)

    for book in BOOKS:
        ch, ln = merge_book(book)
        pdf_ok = copy_pdf(book)
        label = f"Book{book['num']} {book['slug']}"
        pdf_status = "OK" if pdf_ok else "MISS"
        print(f"{label:<35} {ch:>8} {ln:>8} {pdf_status:>6}")

    print("-" * 62)
    print(f"\nDone. Output: {FINAL}\n")


if __name__ == "__main__":
    main()
