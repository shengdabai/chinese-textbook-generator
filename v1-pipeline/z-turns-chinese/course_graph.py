"""
CourseGraph - Multi-track Course Structure Manager
Manages courses, units, and lessons with cross-course vocabulary sharing.
"""

import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional

from config import HSK_LEVELS, BOOK1_LESSONS
from vocab_ledger import VocabLedger


@dataclass
class Lesson:
    lesson_id: str
    unit_id: str
    title_en: str
    title_zh: str
    can_do: str
    seq_order: int
    new_vocab_limit: int = 10
    vocab_ids: list = field(default_factory=list)
    grammar_points: list = field(default_factory=list)
    topic: str = ""


@dataclass
class Unit:
    unit_id: str
    course_id: str
    title: str
    seq_order: int
    lesson_ids: list = field(default_factory=list)


@dataclass
class Course:
    course_id: str
    title: str
    target_level: int
    description: str = ""
    unit_ids: list = field(default_factory=list)


# ==================================================================
# Level Mapping
# ==================================================================

LEVEL_MAPPING = {
    1: {"hsk": "HSK 1", "cefr": "A1", "actfl": "Novice Mid-High"},
    2: {"hsk": "HSK 2", "cefr": "A2", "actfl": "Novice High - Intermediate Low"},
    3: {"hsk": "HSK 3", "cefr": "B1", "actfl": "Intermediate Mid-High"},
    4: {"hsk": "HSK 4", "cefr": "B2", "actfl": "Advanced Low"},
    5: {"hsk": "HSK 5", "cefr": "C1", "actfl": "Advanced Mid-High"},
    6: {"hsk": "HSK 6", "cefr": "C2", "actfl": "Superior"},
}


class CourseGraph:
    """Multi-track course structure manager."""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.filepath = os.path.join(self.data_dir, "course_graph.json")
        self.courses: dict[str, Course] = {}
        self.units: dict[str, Unit] = {}
        self.lessons: dict[str, Lesson] = {}
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for cid, cdata in data.get("courses", {}).items():
                self.courses[cid] = Course(**cdata)
            for uid, udata in data.get("units", {}).items():
                self.units[uid] = Unit(**udata)
            for lid, ldata in data.get("lessons", {}).items():
                self.lessons[lid] = Lesson(**ldata)

    def _save(self):
        data = {
            "courses": {cid: asdict(c) for cid, c in self.courses.items()},
            "units": {uid: asdict(u) for uid, u in self.units.items()},
            "lessons": {lid: asdict(l) for lid, l in self.lessons.items()},
        }
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Course Management
    # ------------------------------------------------------------------

    def create_course(self, title: str, target_level: int,
                      description: str = "") -> str:
        """Create a new course. Returns course_id."""
        course_id = f"course-{uuid.uuid4().hex[:8]}"
        self.courses[course_id] = Course(
            course_id=course_id, title=title,
            target_level=target_level, description=description,
        )
        self._save()
        return course_id

    def create_unit(self, course_id: str, title: str, seq_order: int) -> str:
        """Create a unit within a course. Returns unit_id."""
        if course_id not in self.courses:
            raise ValueError(f"Course {course_id} not found")
        unit_id = f"unit-{uuid.uuid4().hex[:8]}"
        self.units[unit_id] = Unit(
            unit_id=unit_id, course_id=course_id,
            title=title, seq_order=seq_order,
        )
        self.courses[course_id].unit_ids.append(unit_id)
        self._save()
        return unit_id

    def create_lesson(self, unit_id: str, title_en: str, title_zh: str,
                      can_do: str, seq_order: int,
                      new_vocab_limit: int = 10) -> str:
        """Create a lesson within a unit. Returns lesson_id."""
        if unit_id not in self.units:
            raise ValueError(f"Unit {unit_id} not found")
        lesson_id = f"lesson-{uuid.uuid4().hex[:8]}"
        self.lessons[lesson_id] = Lesson(
            lesson_id=lesson_id, unit_id=unit_id,
            title_en=title_en, title_zh=title_zh,
            can_do=can_do, seq_order=seq_order,
            new_vocab_limit=new_vocab_limit,
        )
        self.units[unit_id].lesson_ids.append(lesson_id)
        self._save()
        return lesson_id

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_course(self, course_id: str) -> dict:
        """Get course details."""
        if course_id in self.courses:
            return asdict(self.courses[course_id])
        return {}

    def get_course_structure(self, course_id: str) -> dict:
        """Get complete tree structure of a course."""
        if course_id not in self.courses:
            return {}
        course = self.courses[course_id]
        structure = asdict(course)
        structure["units"] = []
        # Sort units by seq_order
        sorted_unit_ids = sorted(
            course.unit_ids,
            key=lambda uid: self.units[uid].seq_order if uid in self.units else 0,
        )
        for uid in sorted_unit_ids:
            if uid not in self.units:
                continue
            unit = self.units[uid]
            unit_data = asdict(unit)
            unit_data["lessons"] = []
            sorted_lesson_ids = sorted(
                unit.lesson_ids,
                key=lambda lid: self.lessons[lid].seq_order if lid in self.lessons else 0,
            )
            for lid in sorted_lesson_ids:
                if lid in self.lessons:
                    unit_data["lessons"].append(asdict(self.lessons[lid]))
            structure["units"].append(unit_data)
        return structure

    def get_lesson_position(self, lesson_id: str) -> dict:
        """Get the position of a lesson within the graph."""
        if lesson_id not in self.lessons:
            return {}
        lesson = self.lessons[lesson_id]
        unit = self.units.get(lesson.unit_id)
        if not unit:
            return {}
        course = self.courses.get(unit.course_id)
        if not course:
            return {}
        # Calculate global lesson index
        global_index = 0
        sorted_unit_ids = sorted(
            course.unit_ids,
            key=lambda uid: self.units[uid].seq_order if uid in self.units else 0,
        )
        for uid in sorted_unit_ids:
            if uid not in self.units:
                continue
            u = self.units[uid]
            sorted_lessons = sorted(
                u.lesson_ids,
                key=lambda lid: self.lessons[lid].seq_order if lid in self.lessons else 0,
            )
            for lid in sorted_lessons:
                global_index += 1
                if lid == lesson_id:
                    return {
                        "lesson_id": lesson_id,
                        "unit_id": unit.unit_id,
                        "unit_title": unit.title,
                        "course_id": course.course_id,
                        "course_title": course.title,
                        "seq_in_unit": lesson.seq_order,
                        "global_index": global_index,
                    }
        return {}

    def get_previous_lessons(self, lesson_id: str) -> list:
        """Get all lessons that come before the given lesson in the same course."""
        pos = self.get_lesson_position(lesson_id)
        if not pos:
            return []
        course = self.courses.get(pos["course_id"])
        if not course:
            return []
        previous = []
        sorted_unit_ids = sorted(
            course.unit_ids,
            key=lambda uid: self.units[uid].seq_order if uid in self.units else 0,
        )
        for uid in sorted_unit_ids:
            if uid not in self.units:
                continue
            u = self.units[uid]
            sorted_lessons = sorted(
                u.lesson_ids,
                key=lambda lid: self.lessons[lid].seq_order if lid in self.lessons else 0,
            )
            for lid in sorted_lessons:
                if lid == lesson_id:
                    return previous
                if lid in self.lessons:
                    previous.append(asdict(self.lessons[lid]))
        return previous

    def get_accumulated_vocab(self, lesson_id: str) -> list:
        """Get all vocab_ids accumulated up to and including this lesson."""
        previous = self.get_previous_lessons(lesson_id)
        all_vocab_ids = []
        for les in previous:
            all_vocab_ids.extend(les.get("vocab_ids", []))
        if lesson_id in self.lessons:
            all_vocab_ids.extend(self.lessons[lesson_id].vocab_ids)
        return list(dict.fromkeys(all_vocab_ids))  # deduplicate, preserve order

    # ------------------------------------------------------------------
    # Multi-track Management
    # ------------------------------------------------------------------

    def list_courses(self) -> list:
        """List all courses."""
        return [asdict(c) for c in self.courses.values()]

    def get_shared_vocab(self, course_id_1: str, course_id_2: str) -> list:
        """Find vocabulary shared between two courses."""
        def _collect_vocab(course_id):
            vocab = set()
            course = self.courses.get(course_id)
            if not course:
                return vocab
            for uid in course.unit_ids:
                if uid not in self.units:
                    continue
                for lid in self.units[uid].lesson_ids:
                    if lid in self.lessons:
                        vocab.update(self.lessons[lid].vocab_ids)
            return vocab

        v1 = _collect_vocab(course_id_1)
        v2 = _collect_vocab(course_id_2)
        return list(v1 & v2)

    # ------------------------------------------------------------------
    # ACTFL/CEFR Alignment
    # ------------------------------------------------------------------

    @staticmethod
    def get_level_mapping() -> dict:
        """Return HSK -> CEFR -> ACTFL mapping table."""
        return LEVEL_MAPPING.copy()

    # ------------------------------------------------------------------
    # Initialization Helpers
    # ------------------------------------------------------------------

    def init_default_courses(self) -> None:
        """Create three default course tracks: General, Business, Travel."""
        # 1. General Chinese - A1, 15 lessons from BOOK1_LESSONS
        self.init_book1_from_config()

        # 2. Business Chinese - A2, 10 lessons framework
        biz_id = self.create_course(
            "Business Chinese", target_level=2,
            description="Professional Chinese for workplace communication",
        )
        biz_unit = self.create_unit(biz_id, "Business Essentials", 1)
        biz_lessons = [
            ("Self-Introduction", "自我介绍", "Introduce yourself professionally"),
            ("Company Tour", "参观公司", "Describe office areas"),
            ("Schedule & Meetings", "日程安排", "Schedule meetings"),
            ("Email Basics", "写邮件", "Write simple business emails"),
            ("Business Card", "交换名片", "Exchange business cards"),
            ("Review 1", "复习一", "Review L1-5"),
            ("Phone Etiquette", "商务电话", "Handle business calls"),
            ("Restaurant Hosting", "商务宴请", "Host a business dinner"),
            ("Negotiation Basics", "简单谈判", "Basic negotiation phrases"),
            ("Final Review", "总复习", "Full course review"),
        ]
        for i, (en, zh, can_do) in enumerate(biz_lessons, 1):
            self.create_lesson(biz_unit, en, zh, can_do, i,
                               new_vocab_limit=12 if "Review" not in en else 2)

        # 3. Travel Chinese - A1, 8 lessons framework
        travel_id = self.create_course(
            "Travel Chinese", target_level=1,
            description="Essential Chinese for travelers in China",
        )
        travel_unit = self.create_unit(travel_id, "Travel Essentials", 1)
        travel_lessons = [
            ("At the Airport", "在机场", "Navigate the airport"),
            ("Taking a Taxi", "坐出租车", "Take a taxi and give directions"),
            ("Hotel Check-in", "酒店入住", "Check in and out of a hotel"),
            ("Ordering Food", "点餐", "Order food at a restaurant"),
            ("Street Shopping", "街边购物", "Bargain and buy souvenirs"),
            ("Asking Directions", "问路", "Ask for and understand directions"),
            ("Emergency Help", "紧急求助", "Handle emergencies"),
            ("Final Review", "总复习", "Full course review"),
        ]
        for i, (en, zh, can_do) in enumerate(travel_lessons, 1):
            self.create_lesson(travel_unit, en, zh, can_do, i,
                               new_vocab_limit=8 if "Review" not in en else 0)

    def init_book1_from_config(self) -> None:
        """Initialize the General Chinese course from config.BOOK1_LESSONS."""
        general_id = self.create_course(
            "General Chinese", target_level=1,
            description="Zero-to-A1 general purpose Chinese course",
        )
        # Group lessons into 3 units of 5
        unit_titles = [
            "Getting Started (L1-5)",
            "Daily Life (L6-10)",
            "Expanding Horizons (L11-15)",
        ]
        for unit_idx, unit_title in enumerate(unit_titles):
            unit_id = self.create_unit(general_id, unit_title, unit_idx + 1)
            start = unit_idx * 5
            end = start + 5
            for lesson_cfg in BOOK1_LESSONS[start:end]:
                can_do = f"Topic: {lesson_cfg['topic']}, Grammar: {lesson_cfg['grammar']}"
                new_limit = lesson_cfg.get("new_words", 8)
                self.create_lesson(
                    unit_id,
                    title_en=lesson_cfg["title_en"],
                    title_zh=lesson_cfg["title_zh"],
                    can_do=can_do,
                    seq_order=lesson_cfg["id"],
                    new_vocab_limit=new_limit,
                )


# ==================================================================
# Demo
# ==================================================================

def demo():
    print("=" * 60)
    print("CourseGraph Demo")
    print("=" * 60)

    graph = CourseGraph()

    # Initialize default courses
    print("\n[1] Initializing default courses...")
    graph.init_default_courses()

    # List courses
    courses = graph.list_courses()
    print(f"\n[2] Courses created: {len(courses)}")
    for c in courses:
        print(f"    - {c['title']} (level {c['target_level']}): {c['description']}")

    # Show structure of General Chinese
    general = [c for c in courses if c["title"] == "General Chinese"]
    if general:
        cid = general[0]["course_id"]
        structure = graph.get_course_structure(cid)
        print(f"\n[3] General Chinese structure:")
        for unit in structure.get("units", []):
            print(f"    Unit: {unit['title']}")
            for les in unit.get("lessons", []):
                print(f"      L{les['seq_order']}: {les['title_en']} ({les['title_zh']})")

    # Lesson position
    if graph.lessons:
        first_lid = list(graph.lessons.keys())[0]
        pos = graph.get_lesson_position(first_lid)
        if pos:
            print(f"\n[4] Position of '{first_lid}': "
                  f"global #{pos['global_index']} in {pos['course_title']}")

    # Level mapping
    mapping = CourseGraph.get_level_mapping()
    print(f"\n[5] Level mapping (HSK -> CEFR -> ACTFL):")
    for lvl, m in list(mapping.items())[:3]:
        print(f"    {m['hsk']}: {m['cefr']} / {m['actfl']}")

    print("\n" + "=" * 60)
    print("Demo complete!")


if __name__ == "__main__":
    demo()
