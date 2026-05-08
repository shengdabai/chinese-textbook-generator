"""
Z Turns Chinese - Book Template System
书籍模板系统

Provides reusable templates, validators, and schema definitions
for all books in the Z Turns Chinese series.

Usage:
    from book_template import BookTemplate, validate_chapter, validate_pinyin

    template = BookTemplate("book1")
    template.validate_chapter(chapter_dict)
"""

import re
import unicodedata
from typing import Any


# ============================================================
# Pinyin Validation
# ============================================================

# All valid tone-marked vowels (decomposed form check)
_TONE_MARK_CHARS = set("āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ")

# Tone number pattern — forbidden
_TONE_NUMBER_PATTERN = re.compile(r"[aeiouüv][1-4]\b", re.IGNORECASE)


def has_tone_marks(pinyin_text: str) -> bool:
    """Return True if pinyin_text contains at least one tone-marked vowel."""
    return any(ch in _TONE_MARK_CHARS for ch in pinyin_text)


def has_tone_numbers(pinyin_text: str) -> bool:
    """Return True if pinyin_text uses forbidden tone-number notation."""
    return bool(_TONE_NUMBER_PATTERN.search(pinyin_text))


def validate_pinyin(pinyin_text: str) -> list[str]:
    """
    Validate a pinyin string.

    Returns a list of error messages (empty = valid).
    """
    errors = []
    if not pinyin_text or not pinyin_text.strip():
        errors.append("Pinyin is empty.")
        return errors

    if has_tone_numbers(pinyin_text):
        errors.append(
            f"Tone numbers detected in pinyin: '{pinyin_text}'. "
            "Use tone marks (ā á ǎ à) instead of numbers (a1 a2 a3 a4)."
        )

    # For non-neutral-tone text, expect at least one tone mark
    # (neutral-tone syllables like 'ma' in 吗 have no mark — acceptable)
    stripped = pinyin_text.strip().lower()
    has_vowel = any(c in "aeiouüv" for c in stripped)
    if has_vowel and not has_tone_marks(pinyin_text) and len(stripped) > 3:
        errors.append(
            f"No tone marks found in pinyin: '{pinyin_text}'. "
            "All pinyin must include tone marks."
        )

    return errors


# ============================================================
# Four-Layer Alignment Validator
# ============================================================

def validate_four_layers(line_tuple: tuple | list) -> list[str]:
    """
    Validate a four-layer dialogue line.

    Expected format:
        (speaker, chinese, pinyin, word_by_word, natural_english)
        OR (chinese, pinyin, word_by_word, natural_english)  — for vocab rows

    Returns a list of error messages.
    """
    errors = []

    if len(line_tuple) == 5:
        _speaker, chinese, pinyin, word_by_word, natural = line_tuple
    elif len(line_tuple) == 4:
        chinese, pinyin, word_by_word, natural = line_tuple
    else:
        errors.append(
            f"Expected 4 or 5 elements in line tuple, got {len(line_tuple)}: {line_tuple}"
        )
        return errors

    if not chinese or not chinese.strip():
        errors.append("Chinese (layer 1) is empty.")

    pinyin_errors = validate_pinyin(pinyin)
    errors.extend(pinyin_errors)

    if not word_by_word or not word_by_word.strip():
        errors.append("Word-by-word translation (layer 3) is empty.")

    if not natural or not natural.strip():
        errors.append("Natural English translation (layer 4) is empty.")

    return errors


# ============================================================
# Chapter Schema
# ============================================================

# Required top-level keys for every chapter/lesson dict
CHAPTER_REQUIRED_FIELDS = {
    "id",
    "title_en",
    "title_zh",
    "book",
    "hsk_level",
    "learning_goals",
    "new_words",
    "dialogues",
}

# Optional but validated if present
CHAPTER_OPTIONAL_FIELDS = {
    "review_words",
    "grammar_points",
    "culture_note",
    "exercises",
}


def validate_chapter(chapter: dict) -> list[str]:
    """
    Validate a chapter/lesson dict against the standard schema.

    Checks:
    - All required fields present
    - new_words count within limit
    - Pinyin tone marks on all vocabulary
    - Four-layer alignment on dialogues
    - At least one dialogue present
    - learning_goals is a non-empty list

    Returns a list of error messages (empty = valid).
    """
    from config import CONSISTENCY_RULES

    errors = []

    # Required field presence
    missing = CHAPTER_REQUIRED_FIELDS - set(chapter.keys())
    if missing:
        errors.append(f"Missing required fields: {', '.join(sorted(missing))}")

    # ID and titles
    if not isinstance(chapter.get("id"), int):
        errors.append("Field 'id' must be an integer.")

    if not chapter.get("title_en", "").strip():
        errors.append("Field 'title_en' must not be empty.")

    if not chapter.get("title_zh", "").strip():
        errors.append("Field 'title_zh' must not be empty.")

    # HSK level
    hsk = chapter.get("hsk_level")
    if hsk not in (1, 2, 3):
        errors.append(f"Field 'hsk_level' must be 1, 2, or 3. Got: {hsk!r}")

    # Learning goals
    goals = chapter.get("learning_goals", [])
    if not isinstance(goals, list) or len(goals) == 0:
        errors.append("Field 'learning_goals' must be a non-empty list.")

    # New words
    new_words = chapter.get("new_words", [])
    if not isinstance(new_words, list):
        errors.append("Field 'new_words' must be a list.")
    else:
        max_words = CONSISTENCY_RULES.get("max_new_words_regular", 10)
        if len(new_words) > max_words:
            errors.append(
                f"Too many new words: {len(new_words)} (max {max_words})."
            )
        # Validate each word's pinyin
        for i, word in enumerate(new_words):
            if isinstance(word, (list, tuple)) and len(word) >= 2:
                pinyin_str = str(word[1])
                pin_errors = validate_pinyin(pinyin_str)
                for pe in pin_errors:
                    errors.append(f"new_words[{i}] pinyin: {pe}")

    # Dialogues
    dialogues = chapter.get("dialogues", [])
    if not isinstance(dialogues, list) or len(dialogues) == 0:
        errors.append("Field 'dialogues' must be a non-empty list.")
    else:
        for di, dialogue in enumerate(dialogues):
            lines = dialogue.get("lines", [])
            if not lines:
                errors.append(f"dialogues[{di}] has no lines.")
            for li, line in enumerate(lines):
                line_errors = validate_four_layers(line)
                for le in line_errors:
                    errors.append(f"dialogues[{di}].lines[{li}]: {le}")

    return errors


# ============================================================
# Book Metadata Schema
# ============================================================

def build_book_metadata(
    book_key: str,
    author: str = "Tony Sheng",
    year: int = 2026,
) -> dict:
    """
    Build a complete book metadata dict from the series definition.

    Args:
        book_key: One of "book1", "book2", "book3"
        author: Author name for copyright page
        year: Publication year

    Returns:
        Dict with all book metadata needed for PDF generation.
    """
    from methodology import BOOK_SERIES

    series_info = BOOK_SERIES.get(book_key)
    if series_info is None:
        raise ValueError(
            f"Unknown book key: {book_key!r}. "
            f"Valid keys: {list(BOOK_SERIES.keys())}"
        )

    return {
        "book_key": book_key,
        "name": series_info["name"],
        "subtitle": series_info["subtitle"],
        "zh_name": series_info["zh_name"],
        "author": author,
        "year": year,
        "level": series_info["level"],
        "hsk_target": series_info["hsk_target"],
        "cefr": series_info["cefr"],
        "chapters": series_info["chapters"],
        "vocab_target": series_info["vocab_target"],
        "audience": series_info["audience"],
        "promise": series_info["promise"],
        "units": series_info.get("units", []),
        "series_name": "Z Turns Chinese",
    }


# ============================================================
# BookTemplate
# ============================================================

class BookTemplate:
    """
    Reusable book template for the Z Turns Chinese series.

    Wraps metadata, validation, and chapter structure for a specific book.

    Usage:
        template = BookTemplate("book1")
        errors = template.validate_chapter(my_chapter)
        metadata = template.metadata
    """

    def __init__(self, book_key: str, author: str = "Tony Sheng", year: int = 2026):
        self.book_key = book_key
        self.author = author
        self.year = year
        self.metadata = build_book_metadata(book_key, author, year)

    @property
    def name(self) -> str:
        return self.metadata["name"]

    @property
    def level(self) -> str:
        return self.metadata["level"]

    @property
    def hsk_level(self) -> int:
        return self.metadata["hsk_target"]

    @property
    def chapter_count(self) -> int:
        return self.metadata["chapters"]

    def validate_chapter(self, chapter: dict) -> list[str]:
        """Validate a chapter dict. Returns list of error messages."""
        return validate_chapter(chapter)

    def validate_pinyin(self, pinyin_text: str) -> list[str]:
        """Validate a pinyin string. Returns list of error messages."""
        return validate_pinyin(pinyin_text)

    def validate_all_chapters(self, chapters: list[dict]) -> dict[int, list[str]]:
        """
        Validate a list of chapters.

        Returns a dict mapping chapter id → list of errors.
        Only chapters with errors are included.
        """
        report = {}
        for ch in chapters:
            errors = self.validate_chapter(ch)
            if errors:
                cid = ch.get("id", "?")
                report[cid] = errors
        return report

    def chapter_structure(self) -> list[dict]:
        """Return the standard chapter structure for this book's level."""
        from methodology import METHODOLOGY
        return METHODOLOGY["chapter_structure"]

    def daily_protocol(self) -> list[dict]:
        """Return the 7-step daily practice protocol."""
        from methodology import METHODOLOGY
        return METHODOLOGY["daily_protocol"]

    def quality_standards(self) -> dict:
        """Return the quality standards for this book."""
        from methodology import METHODOLOGY
        return METHODOLOGY["quality_standards"]

    def __repr__(self) -> str:
        return (
            f"BookTemplate(book_key={self.book_key!r}, "
            f"name={self.name!r}, level={self.level!r}, "
            f"chapters={self.chapter_count})"
        )
