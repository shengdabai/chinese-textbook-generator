#!/usr/bin/env python3
"""Merge Book48 duplicates by appending film-entertainment's unique
Chapter 24 (industry perspective) and Chapter 25 (poetic perspective)
as bonus appendix chapters to the Film_Entertainment version.
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path("../../output")
KEEP = ROOT / "Book48_Film_Entertainment/ZTurns_Book48_Film_Entertainment.md"
SRC = ROOT / "Book48_film-entertainment/ZTurns_Book48_film-entertainment.md"


def extract_chapter(md_text: str, chapter_num: int) -> str:
    """Extract text from '# Chapter N:' up to next '# Chapter' or EOF."""
    lines = md_text.split("\n")
    start = -1
    end = len(lines)
    for i, ln in enumerate(lines):
        if ln.startswith(f"# Chapter {chapter_num}:"):
            start = i
            continue
        if start >= 0 and ln.startswith("# Chapter ") and not ln.startswith(f"# Chapter {chapter_num}:"):
            end = i
            break
    return "\n".join(lines[start:end]) if start >= 0 else ""


def main() -> None:
    keep_text = KEEP.read_text(encoding="utf-8")
    src_text = SRC.read_text(encoding="utf-8")

    # Extract film-entertainment's Ch24 (industry vocab) and Ch25 (poetic summary)
    src_ch24 = extract_chapter(src_text, 24)
    src_ch25 = extract_chapter(src_text, 25)

    # Rename for appendix positioning
    src_ch24_renamed = src_ch24.replace(
        "# Chapter 24: Entertainment Vocabulary — 影视词汇大全",
        "# Appendix A: Industry Production Vocabulary — 行业制作词汇",
        1,
    )
    src_ch25_renamed = src_ch25.replace(
        "# Chapter 25: Your Entertainment Industry Guide — 影视产业中文之旅",
        "# Appendix B: Cinema as Light and Shadow — 光影叙事视角",
        1,
    )

    appendix_intro = """
---

# Bonus Appendices — 附录

*The following two appendices offer alternative vocabulary perspectives on the same chapters above. The original Chapter 24 covered viral-hit and audience-side vocabulary; Appendix A below covers the working vocabulary of the production crew. The original Chapter 25 was a course-wide industry summary; Appendix B reframes the same material through the poetic lens of 光影 — light and shadow.*

---
"""

    merged = keep_text.rstrip() + "\n" + appendix_intro + "\n" + src_ch24_renamed.rstrip() + "\n\n---\n\n" + src_ch25_renamed.rstrip() + "\n"
    KEEP.write_text(merged, encoding="utf-8")

    new_size = KEEP.stat().st_size
    print(f"✓ Merged Book48: {KEEP.name}")
    print(f"  New size: {new_size:,} bytes")
    print(f"  Appendix A ({len(src_ch24_renamed):,} chars) and Appendix B ({len(src_ch25_renamed):,} chars) appended.")


if __name__ == "__main__":
    main()
