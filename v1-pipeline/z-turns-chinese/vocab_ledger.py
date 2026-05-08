"""
VocabLedger - Cross-lesson Vocabulary Tracking System
Tracks all vocabulary across courses with HSK compliance checking.
"""

import json
import os
import uuid
import csv
from dataclasses import dataclass, field, asdict
from typing import Optional

from hsk_vocab import VOCAB_BY_TOPIC
from config import HSK_LEVELS, BOOK1_LESSONS


@dataclass
class VocabEntry:
    hanzi: str
    pinyin: str
    english: str
    pos: str
    level: int
    first_lesson_id: str
    word_id: str = ""
    lessons_used: list = field(default_factory=list)

    def __post_init__(self):
        if not self.word_id:
            self.word_id = str(uuid.uuid4())[:8]
        if self.first_lesson_id and self.first_lesson_id not in self.lessons_used:
            self.lessons_used.append(self.first_lesson_id)


class VocabLedger:
    """Cross-lesson vocabulary tracking ledger."""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.filepath = os.path.join(self.data_dir, "vocab_ledger.json")
        self.vocab: dict[str, VocabEntry] = {}  # keyed by hanzi
        self._hsk_vocab: dict[str, dict] = {}  # HSK reference cache
        self._load_hsk_reference()
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for hanzi, entry_data in data.items():
                self.vocab[hanzi] = VocabEntry(**entry_data)

    def _save(self):
        data = {hanzi: asdict(entry) for hanzi, entry in self.vocab.items()}
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # HSK Reference
    # ------------------------------------------------------------------

    def _load_hsk_reference(self):
        """Load HSK vocabulary from hsk_vocab.py as reference."""
        for topic, words in VOCAB_BY_TOPIC.items():
            for item in words:
                hanzi, pinyin, _wbw, english, pos, level = item
                self._hsk_vocab[hanzi] = {
                    "hanzi": hanzi,
                    "pinyin": pinyin,
                    "english": english,
                    "pos": pos,
                    "level": level,
                    "topic": topic,
                }

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def register_word(self, hanzi: str, pinyin: str, english: str,
                      pos: str, level: int, first_lesson_id: str) -> str:
        """Register a word in the ledger. Returns the word_id."""
        if hanzi in self.vocab:
            entry = self.vocab[hanzi]
            if first_lesson_id not in entry.lessons_used:
                entry.lessons_used.append(first_lesson_id)
            self._save()
            return entry.word_id
        entry = VocabEntry(
            hanzi=hanzi, pinyin=pinyin, english=english,
            pos=pos, level=level, first_lesson_id=first_lesson_id,
        )
        self.vocab[hanzi] = entry
        self._save()
        return entry.word_id

    def get_word(self, hanzi: str) -> dict:
        """Look up word details. Returns dict or empty dict if not found."""
        if hanzi in self.vocab:
            return asdict(self.vocab[hanzi])
        return {}

    def get_lesson_vocab(self, lesson_id: str) -> dict:
        """Get all vocabulary for a lesson (new + review)."""
        result = {"new": [], "review": []}
        for hanzi, entry in self.vocab.items():
            if lesson_id in entry.lessons_used:
                if entry.first_lesson_id == lesson_id:
                    result["new"].append(asdict(entry))
                else:
                    result["review"].append(asdict(entry))
        return result

    def get_new_words_count(self, lesson_id: str) -> int:
        """Count how many words were first introduced in this lesson."""
        count = 0
        for entry in self.vocab.values():
            if entry.first_lesson_id == lesson_id:
                count += 1
        return count

    def get_reuse_count(self, hanzi: str) -> int:
        """Get how many lessons this word has been used in."""
        if hanzi in self.vocab:
            return len(self.vocab[hanzi].lessons_used)
        return 0

    def check_hsk_compliance(self, words: list, target_level: int) -> list:
        """Check if words exceed the target HSK level.

        Returns a list of non-compliant words (those above target_level
        or not found in the HSK reference).
        """
        non_compliant = []
        for word in words:
            if word in self._hsk_vocab:
                if self._hsk_vocab[word]["level"] > target_level:
                    non_compliant.append({
                        "hanzi": word,
                        "word_level": self._hsk_vocab[word]["level"],
                        "target_level": target_level,
                        "reason": "above_target_level",
                    })
            else:
                non_compliant.append({
                    "hanzi": word,
                    "word_level": None,
                    "target_level": target_level,
                    "reason": "not_in_hsk_reference",
                })
        return non_compliant

    def get_vocab_by_level(self, level: int) -> list:
        """Get all registered words at a specific HSK level."""
        return [asdict(e) for e in self.vocab.values() if e.level == level]

    def get_vocab_stats(self) -> dict:
        """Return summary statistics of the ledger."""
        total = len(self.vocab)
        level_dist: dict[int, int] = {}
        total_reuse = 0
        reused_count = 0
        for entry in self.vocab.values():
            level_dist[entry.level] = level_dist.get(entry.level, 0) + 1
            uses = len(entry.lessons_used)
            if uses > 1:
                reused_count += 1
                total_reuse += uses
        reuse_rate = (reused_count / total * 100) if total > 0 else 0.0
        return {
            "total_words": total,
            "level_distribution": dict(sorted(level_dist.items())),
            "reused_words": reused_count,
            "reuse_rate_pct": round(reuse_rate, 1),
            "avg_reuse_count": round(total_reuse / reused_count, 2) if reused_count else 0,
        }

    def build_from_lessons(self, lessons: list) -> None:
        """Build the ledger from a list of lesson dicts (BOOK1_LESSONS style).

        Each lesson must have 'id' and 'topic' keys. Words are pulled from
        hsk_vocab.VOCAB_BY_TOPIC using the topic, and review_from is used
        to mark reuse.
        """
        for lesson in lessons:
            lesson_id = str(lesson["id"])
            topic = lesson.get("topic", "")
            # Register new words for this lesson
            if topic != "review":
                words = VOCAB_BY_TOPIC.get(topic, [])
                for item in words:
                    hanzi, pinyin, _wbw, english, pos, level = item
                    self.register_word(hanzi, pinyin, english, pos, level, lesson_id)
            # Mark review words
            for rev_id in lesson.get("review_from", []):
                rev_lesson_id = str(rev_id)
                for entry in self.vocab.values():
                    if entry.first_lesson_id == rev_lesson_id:
                        if lesson_id not in entry.lessons_used:
                            entry.lessons_used.append(lesson_id)
        self._save()

    def export_csv(self, filepath: str) -> str:
        """Export the ledger as a flashcard CSV file."""
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["hanzi", "pinyin", "english", "pos", "level",
                             "first_lesson", "times_used"])
            for entry in self.vocab.values():
                writer.writerow([
                    entry.hanzi, entry.pinyin, entry.english, entry.pos,
                    entry.level, entry.first_lesson_id, len(entry.lessons_used),
                ])
        return filepath


# ==================================================================
# Demo
# ==================================================================

def demo():
    print("=" * 60)
    print("VocabLedger Demo")
    print("=" * 60)

    ledger = VocabLedger()

    # Build from Book 1 lessons
    print("\n[1] Building ledger from BOOK1_LESSONS...")
    ledger.build_from_lessons(BOOK1_LESSONS)

    # Stats
    stats = ledger.get_vocab_stats()
    print(f"\n[2] Vocab Stats:")
    for k, v in stats.items():
        print(f"    {k}: {v}")

    # Look up a word
    word = ledger.get_word("你好")
    if word:
        print(f"\n[3] Lookup '你好': pinyin={word['pinyin']}, "
              f"english={word['english']}, used in {len(word['lessons_used'])} lessons")

    # HSK compliance check
    test_words = ["你好", "电脑", "咖啡"]
    issues = ledger.check_hsk_compliance(test_words, target_level=1)
    print(f"\n[4] HSK compliance check for {test_words}:")
    if issues:
        for issue in issues:
            print(f"    {issue['hanzi']}: {issue['reason']}")
    else:
        print("    All compliant!")

    # Lesson vocab
    lv = ledger.get_lesson_vocab("1")
    print(f"\n[5] Lesson 1 vocab: {len(lv['new'])} new, {len(lv['review'])} review")

    # Export CSV
    csv_path = os.path.join(ledger.data_dir, "vocab_export.csv")
    ledger.export_csv(csv_path)
    print(f"\n[6] Exported CSV to: {csv_path}")

    print("\n" + "=" * 60)
    print("Demo complete!")


if __name__ == "__main__":
    demo()
