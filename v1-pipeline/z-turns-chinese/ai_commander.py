#!/usr/bin/env python3
"""
Z Turns Chinese - AI Commander
智能指挥官：自动化中文教材生成管线编排器

The AI Commander is the "brain" of the system. Given a high-level mission brief
like "Create a complete Pinyin learning course", it autonomously orchestrates
the entire pipeline from market analysis to final PDF production.

Pipeline stages:
  1. Mission Parsing      - Understand intent from natural language
  2. Market Analysis      - Analyze demand and positioning
  3. Course Planning      - Design lesson structure and progression
  4. Material Gathering   - Collect content from GetNotes, URLs, files
  5. Privacy Filtering    - Sanitize all gathered materials
  6. Lesson Generation    - Produce each lesson using AI or offline data
  7. Quality Validation   - HSK compliance, vocab control, consistency
  8. PDF Production       - Render final PDFs with four-layer translations

Usage:
    python3 ai_commander.py                     # Interactive mode
    python3 ai_commander.py --mission "..."     # Execute a mission brief
    python3 ai_commander.py --offline           # Offline demo with built-in data
"""

import os
import sys
import json
import time
import re
from datetime import datetime

# Ensure project directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    HSK_LEVELS,
    BOOK1_LESSONS,
    CONSISTENCY_RULES,
    LESSON_STRUCTURE,
    FOUR_LAYERS,
)
from lesson_data import LESSONS, get_lesson, get_available_lessons
from hsk_vocab import (
    VOCAB_BY_TOPIC,
    get_vocab_for_lesson,
    get_all_vocab_up_to_lesson,
    check_vocab_in_hsk,
)
from privacy_filter import PrivacyFilter
from generator import LessonGenerator

try:
    from qa_engine import QAEngine
except ImportError:
    QAEngine = None

try:
    from phrase_memory import PhraseMemory
except ImportError:
    PhraseMemory = None

try:
    from vocab_ledger import VocabLedger
except ImportError:
    VocabLedger = None

try:
    from course_graph import CourseGraph
except ImportError:
    CourseGraph = None


# ---------------------------------------------------------------------------
# Pipeline stage constants
# ---------------------------------------------------------------------------
STAGE_PARSE = "mission_parsing"
STAGE_MARKET = "market_analysis"
STAGE_PLAN = "course_planning"
STAGE_GATHER = "material_gathering"
STAGE_PRIVACY = "privacy_filtering"
STAGE_GENERATE = "lesson_generation"
STAGE_VALIDATE = "quality_validation"
STAGE_PDF = "pdf_production"

ALL_STAGES = [
    STAGE_PARSE,
    STAGE_MARKET,
    STAGE_PLAN,
    STAGE_GATHER,
    STAGE_PRIVACY,
    STAGE_GENERATE,
    STAGE_VALIDATE,
    STAGE_PDF,
]

STAGE_LABELS = {
    STAGE_PARSE:    ("任务解析", "Mission Parsing"),
    STAGE_MARKET:   ("市场分析", "Market Analysis"),
    STAGE_PLAN:     ("课程规划", "Course Planning"),
    STAGE_GATHER:   ("素材采集", "Material Gathering"),
    STAGE_PRIVACY:  ("隐私过滤", "Privacy Filtering"),
    STAGE_GENERATE: ("课程生成", "Lesson Generation"),
    STAGE_VALIDATE: ("质量验证", "Quality Validation"),
    STAGE_PDF:      ("PDF 输出", "PDF Production"),
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _log_msg(zh: str, en: str) -> str:
    """Format a bilingual log message."""
    return f"{zh} / {en}"


def _banner(text: str, width: int = 60):
    """Print a simple banner."""
    print()
    print("=" * width)
    print(f"  {text}")
    print("=" * width)


def _progress(stage: str, detail: str = ""):
    """Print a stage progress line."""
    zh, en = STAGE_LABELS.get(stage, (stage, stage))
    idx = ALL_STAGES.index(stage) + 1 if stage in ALL_STAGES else "?"
    total = len(ALL_STAGES)
    prefix = f"[{idx}/{total}]"
    suffix = f" - {detail}" if detail else ""
    print(f"\n{prefix} {zh} / {en}{suffix}")


# ---------------------------------------------------------------------------
# AICommander
# ---------------------------------------------------------------------------

class AICommander:
    """
    Intelligent orchestrator for the Z Turns Chinese textbook generation
    pipeline.  Accepts a natural-language mission brief and drives every
    stage from analysis to final PDF output.
    """

    def __init__(self, output_dir=None):
        # Subsystem references (lazy-initialized)
        self.ai_engine = None          # Will be AIEngine when available
        self.getnotes = None           # Will be GetNotesClient when available
        self.extractor = None          # Will be ContentExtractor when available
        self.generator = None
        self.privacy_filter = None

        # Pipeline state
        self.state = {
            "current_stage": None,
            "completed_stages": [],
            "started_at": None,
            "finished_at": None,
            "params": {},
            "plan": [],
            "materials": [],
            "lessons": [],
            "validation_report": {},
            "output_files": [],
            "errors": [],
        }

        # Action log
        self.log = []

        # Additional material sources added by the user
        self._sources = []

        # Output directory
        self._output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "output"
        )

        # Try to initialise subsystems
        self._init_subsystems()

    # ------------------------------------------------------------------
    # Subsystem initialization
    # ------------------------------------------------------------------

    def _init_subsystems(self):
        """Lazily initialize available subsystems, skipping those that are
        missing or misconfigured."""

        # Privacy filter is always available (no external deps)
        self.privacy_filter = PrivacyFilter()
        self._log_action("init", "PrivacyFilter initialized")

        # Lesson generator is always available
        self.generator = LessonGenerator(self._output_dir)
        self._log_action("init", "LessonGenerator initialized")

        # AI engine (requires API key)
        try:
            from ai_engine import AIEngine  # type: ignore
            self.ai_engine = AIEngine()
            self._log_action("init", "AIEngine initialized")
        except Exception:
            self.ai_engine = None
            self._log_action(
                "init",
                "AIEngine not available (no API key or module missing) "
                "- will use offline mode",
            )

        # GetNotes client
        try:
            from getnotes_client import GetNotesClient  # type: ignore
            self.getnotes = GetNotesClient()
            self._log_action("init", "GetNotesClient initialized")
        except Exception:
            self.getnotes = None
            self._log_action(
                "init",
                "GetNotesClient not available - skipping GetNotes integration",
            )

        # Content extractor (URLs / PDFs)
        try:
            from content_extractor import ContentExtractor  # type: ignore
            self.extractor = ContentExtractor()
            self._log_action("init", "ContentExtractor initialized")
        except Exception:
            self.extractor = None
            self._log_action(
                "init",
                "ContentExtractor not available - URL/PDF extraction disabled",
            )

        # QA engine
        self.qa_engine = QAEngine() if QAEngine else None
        if self.qa_engine:
            self._log_action("init", "QAEngine initialized")

        # Phrase memory
        self.phrase_memory = PhraseMemory() if PhraseMemory else None
        if self.phrase_memory:
            self._log_action("init", "PhraseMemory initialized")

        # Vocabulary ledger
        self.vocab_ledger = VocabLedger() if VocabLedger else None
        if self.vocab_ledger:
            self._log_action("init", "VocabLedger initialized")

        # Course graph
        self.course_graph = CourseGraph() if CourseGraph else None
        if self.course_graph:
            self._log_action("init", "CourseGraph initialized")

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _log_action(self, action: str, detail: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "detail": detail,
        }
        self.log.append(entry)

    # ------------------------------------------------------------------
    # Source management
    # ------------------------------------------------------------------

    def add_source(self, source_type: str, source_value: str):
        """Add a material source for later processing.

        Args:
            source_type: One of "url", "pdf", "file", "text",
                         "getnotes_topic", "getnotes_note".
            source_value: The URL, file path, text content, or topic string.
        """
        valid_types = {
            "url", "pdf", "file", "text", "getnotes_topic", "getnotes_note",
        }
        if source_type not in valid_types:
            print(f"  [!] 无效的来源类型 / Invalid source type: {source_type}")
            print(f"      有效类型 / Valid types: {', '.join(sorted(valid_types))}")
            return

        self._sources.append({"type": source_type, "value": source_value})
        self._log_action("add_source", f"{source_type}: {source_value[:80]}")
        print(f"  [+] 已添加来源 / Source added: {source_type} = {source_value[:60]}")

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Return current pipeline status as a dict."""
        elapsed = None
        if self.state["started_at"]:
            end = self.state["finished_at"] or datetime.now()
            elapsed = str(end - self.state["started_at"]).split(".")[0]

        return {
            "current_stage": self.state["current_stage"],
            "completed_stages": list(self.state["completed_stages"]),
            "elapsed": elapsed,
            "params": dict(self.state["params"]),
            "lessons_generated": len(self.state["lessons"]),
            "output_files": list(self.state["output_files"]),
            "errors": list(self.state["errors"]),
            "ai_engine_available": self.ai_engine is not None,
            "getnotes_available": self.getnotes is not None,
            "extractor_available": self.extractor is not None,
            "sources_count": len(self._sources),
        }

    def print_status(self):
        """Pretty-print the current pipeline status."""
        s = self.get_status()
        print("\n--- 管线状态 / Pipeline Status ---")
        print(f"  当前阶段 / Current stage : {s['current_stage'] or '(idle)'}")
        print(f"  已完成 / Completed       : {', '.join(s['completed_stages']) or '(none)'}")
        if s["elapsed"]:
            print(f"  耗时 / Elapsed           : {s['elapsed']}")
        print(f"  课程数 / Lessons          : {s['lessons_generated']}")
        print(f"  输出文件 / Output files   : {len(s['output_files'])}")
        print(f"  AI 引擎 / AI engine       : {'available' if s['ai_engine_available'] else 'offline'}")
        print(f"  GetNotes                  : {'available' if s['getnotes_available'] else 'N/A'}")
        print(f"  素材来源 / Sources        : {s['sources_count']}")
        if s["errors"]:
            print(f"  错误 / Errors             : {len(s['errors'])}")
            for err in s["errors"][:5]:
                print(f"    - {err}")

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def execute_mission(self, mission_brief: str):
        """Main entry point.  Parse a natural-language mission brief and
        execute the full pipeline.

        Example briefs:
            "Create a complete Pinyin learning course"
            "Generate HSK 1 Book 1 - 15 lessons about daily life"
            "Build a 5-lesson mini-course about Chinese food culture, HSK 2"
        """
        _banner("Z Turns Chinese - AI Commander")
        print(f"  任务简报 / Mission brief: {mission_brief}")

        self.state["started_at"] = datetime.now()

        # Stage 1: Parse the mission brief
        _progress(STAGE_PARSE, mission_brief[:50])
        self.state["current_stage"] = STAGE_PARSE
        params = self._parse_mission(mission_brief)
        self.state["params"] = params
        self.state["completed_stages"].append(STAGE_PARSE)
        self._log_action(STAGE_PARSE, json.dumps(params, ensure_ascii=False))

        print(f"  解析结果 / Parsed parameters:")
        print(f"    主题 / Theme     : {params['theme']}")
        print(f"    HSK 等级 / Level : {params['hsk_level']}")
        print(f"    课数 / Lessons   : {params['num_lessons']}")
        if params.get("requirements"):
            print(f"    要求 / Reqs       : {'; '.join(params['requirements'])}")

        # Run the pipeline
        self.run_pipeline(
            theme=params["theme"],
            hsk_level=params["hsk_level"],
            num_lessons=params["num_lessons"],
            sources=[s["value"] for s in self._sources],
            requirements=params.get("requirements", []),
        )

    # ------------------------------------------------------------------
    # Mission parsing
    # ------------------------------------------------------------------

    def _parse_mission(self, brief: str) -> dict:
        """Parse a natural-language mission brief into structured parameters.

        If the AI engine is available, use it for intelligent parsing.
        Otherwise, fall back to keyword-based heuristics.
        """
        if self.ai_engine is not None:
            try:
                return self._parse_mission_with_ai(brief)
            except Exception as exc:
                self._log_action("parse_fallback", str(exc))

        # Fallback: keyword heuristics
        return self._parse_mission_heuristic(brief)

    def _parse_mission_with_ai(self, brief: str) -> dict:
        """Use AI engine to parse the mission brief."""
        data = self.ai_engine.parse_mission_brief(brief)
        if isinstance(data, dict) and "theme" in data:
            return {
                "theme": str(data.get("theme", "general Chinese")),
                "hsk_level": int(data.get("hsk_level", 1)),
                "num_lessons": int(data.get("num_lessons", 15)),
                "requirements": list(data.get("requirements", [])),
            }
        raise ValueError("AI did not return valid mission data")

    def _parse_mission_heuristic(self, brief: str) -> dict:
        """Parse mission brief using keyword matching."""
        brief_lower = brief.lower()

        # Detect HSK level
        hsk_level = 1
        for lvl in [3, 2, 1]:
            if f"hsk {lvl}" in brief_lower or f"hsk{lvl}" in brief_lower:
                hsk_level = lvl
                break
        if any(kw in brief_lower for kw in ["intermediate", "中级", "b1"]):
            hsk_level = 3
        elif any(kw in brief_lower for kw in ["elementary", "初级", "a2"]):
            hsk_level = 2

        # Detect number of lessons
        num_lessons = 15  # default
        num_match = re.search(r"(\d+)\s*(?:lesson|课|节)", brief_lower)
        if num_match:
            num_lessons = min(int(num_match.group(1)), 50)

        # Detect theme
        theme = "general Chinese"
        theme_keywords = {
            "pinyin": "Pinyin and pronunciation",
            "拼音": "Pinyin and pronunciation",
            "food": "Chinese food and dining",
            "美食": "Chinese food and dining",
            "餐": "Chinese food and dining",
            "restaurant": "Chinese food and dining",
            "travel": "Travel in China",
            "旅游": "Travel in China",
            "旅行": "Travel in China",
            "business": "Business Chinese",
            "商务": "Business Chinese",
            "职场": "Workplace Chinese",
            "daily": "Daily life conversations",
            "日常": "Daily life conversations",
            "生活": "Daily life conversations",
            "culture": "Chinese culture",
            "文化": "Chinese culture",
            "greetings": "Greetings and introductions",
            "你好": "Greetings and introductions",
            "beginner": "Beginner's complete course",
            "零基础": "Beginner's complete course",
            "入门": "Beginner's complete course",
            "complete": "Complete Book 1 course",
        }
        for kw, th in theme_keywords.items():
            if kw in brief_lower:
                theme = th
                break

        # Detect requirements
        requirements = []
        if "four-layer" in brief_lower or "四层" in brief_lower:
            requirements.append("Use four-layer translation format")
        if "exercise" in brief_lower or "练习" in brief_lower:
            requirements.append("Include exercises with answer keys")
        if "culture" in brief_lower or "文化" in brief_lower:
            requirements.append("Include culture notes")
        if "cover" in brief_lower or "封面" in brief_lower:
            requirements.append("Generate book cover")

        return {
            "theme": theme,
            "hsk_level": hsk_level,
            "num_lessons": num_lessons,
            "requirements": requirements,
        }

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def run_pipeline(
        self,
        theme: str,
        hsk_level: int = 1,
        num_lessons: int = 15,
        sources: list = None,
        requirements: list = None,
    ):
        """Execute the full generation pipeline.

        Args:
            theme: Course topic / theme description.
            hsk_level: Target HSK level (1-3).
            num_lessons: Number of lessons to generate.
            sources: Optional list of source URLs / file paths / text.
            requirements: Optional list of additional requirements.
        """
        sources = sources or []
        requirements = requirements or []

        if self.state.get("started_at") is None:
            self.state["started_at"] = datetime.now()

        hsk_info = HSK_LEVELS.get(hsk_level, HSK_LEVELS[1])

        # ---------------------------------------------------------------
        # Stage 2: Market analysis
        # ---------------------------------------------------------------
        _progress(STAGE_MARKET, theme)
        self.state["current_stage"] = STAGE_MARKET

        market = self._market_analysis(theme, hsk_level)
        self._log_action(STAGE_MARKET, json.dumps(market, ensure_ascii=False))
        self.state["completed_stages"].append(STAGE_MARKET)

        print(f"  目标受众 / Target audience : {market['target_audience']}")
        print(f"  市场定位 / Positioning     : {market['positioning']}")
        print(f"  差异化 / Differentiator    : {market['differentiator']}")

        # ---------------------------------------------------------------
        # Stage 3: Course planning
        # ---------------------------------------------------------------
        _progress(STAGE_PLAN, f"{num_lessons} lessons, HSK {hsk_level}")
        self.state["current_stage"] = STAGE_PLAN

        plan = self._plan_course(theme, hsk_level, num_lessons, requirements)
        self.state["plan"] = plan
        self._log_action(STAGE_PLAN, f"{len(plan)} lessons planned")
        self.state["completed_stages"].append(STAGE_PLAN)

        print(f"  已规划 / Planned: {len(plan)} 课")
        for item in plan[:5]:
            print(f"    L{item['id']:02d}: {item['title_en']} ({item['title_zh']}) - {item['topic']}")
        if len(plan) > 5:
            print(f"    ... 及其余 {len(plan) - 5} 课 / and {len(plan) - 5} more")

        # ---------------------------------------------------------------
        # Stage 4: Material gathering
        # ---------------------------------------------------------------
        _progress(STAGE_GATHER, f"{len(sources) + len(self._sources)} sources")
        self.state["current_stage"] = STAGE_GATHER

        materials = self.gather_materials(theme, sources)
        self.state["materials"] = materials
        self._log_action(STAGE_GATHER, f"{len(materials)} material items collected")
        self.state["completed_stages"].append(STAGE_GATHER)

        print(f"  采集素材 / Materials collected: {len(materials)} items")

        # ---------------------------------------------------------------
        # Stage 5: Privacy filtering
        # ---------------------------------------------------------------
        _progress(STAGE_PRIVACY, f"filtering {len(materials)} items")
        self.state["current_stage"] = STAGE_PRIVACY

        clean_materials = self._filter_privacy(materials)
        self.state["materials"] = clean_materials
        self.state["completed_stages"].append(STAGE_PRIVACY)

        # ---------------------------------------------------------------
        # Stage 6: Lesson generation
        # ---------------------------------------------------------------
        _progress(STAGE_GENERATE, f"generating {len(plan)} lessons")
        self.state["current_stage"] = STAGE_GENERATE

        lessons = self._generate_lessons(plan, clean_materials, hsk_level)
        self.state["lessons"] = lessons
        self._log_action(STAGE_GENERATE, f"{len(lessons)} lessons generated")
        self.state["completed_stages"].append(STAGE_GENERATE)

        print(f"  已生成 / Generated: {len(lessons)} 课")

        # ---------------------------------------------------------------
        # Stage 7: Quality validation
        # ---------------------------------------------------------------
        _progress(STAGE_VALIDATE, f"validating {len(lessons)} lessons")
        self.state["current_stage"] = STAGE_VALIDATE

        report = self.validate_course(lessons)
        self.state["validation_report"] = report
        self.state["completed_stages"].append(STAGE_VALIDATE)

        status = "PASS" if report["passed"] else "ISSUES FOUND"
        print(f"  验证结果 / Validation: {status}")
        if report["warnings"]:
            for w in report["warnings"][:5]:
                print(f"    [!] {w}")

        # ---------------------------------------------------------------
        # Stage 8: PDF production
        # ---------------------------------------------------------------
        _progress(STAGE_PDF, "rendering PDFs")
        self.state["current_stage"] = STAGE_PDF

        output_files = self._produce_pdfs(lessons, plan, theme, hsk_level)
        self.state["output_files"] = output_files
        self.state["completed_stages"].append(STAGE_PDF)

        # ---------------------------------------------------------------
        # Done
        # ---------------------------------------------------------------
        self.state["finished_at"] = datetime.now()
        self.state["current_stage"] = None
        elapsed = self.state["finished_at"] - self.state["started_at"]

        _banner("任务完成 / Mission Complete")
        print(f"  主题 / Theme     : {theme}")
        print(f"  HSK 等级 / Level : HSK {hsk_level} ({hsk_info['cefr']})")
        print(f"  课程数 / Lessons : {len(lessons)}")
        print(f"  输出文件 / Files : {len(output_files)}")
        print(f"  耗时 / Elapsed   : {str(elapsed).split('.')[0]}")
        print(f"  输出目录 / Dir   : {self._output_dir}")
        if output_files:
            print("\n  生成的文件 / Generated files:")
            for fp in output_files:
                print(f"    - {os.path.basename(fp)}")
        print()

    # ------------------------------------------------------------------
    # Stage implementations
    # ------------------------------------------------------------------

    def _market_analysis(self, theme: str, hsk_level: int) -> dict:
        """Stage 2: Analyze market demand and positioning."""
        if self.ai_engine is not None:
            try:
                result = self.ai_engine.analyze_market_demand(theme)
                if isinstance(result, dict):
                    return result
            except Exception as exc:
                self._log_action("market_analysis_fallback", str(exc))

        # Offline fallback
        hsk_info = HSK_LEVELS.get(hsk_level, HSK_LEVELS[1])
        return {
            "target_audience": f"English speakers learning Chinese at {hsk_info['cefr']} level",
            "positioning": (
                f"HSK {hsk_level} ({hsk_info['cefr']}) textbook with unique "
                f"four-layer word-by-word translation method"
            ),
            "differentiator": (
                "Word-by-word literal English preserves Chinese word order, "
                "making grammar patterns intuitive for English speakers"
            ),
            "demand_score": "high" if hsk_level <= 2 else "medium",
            "competitors": "Integrated Chinese, HSK Standard Course, ChinesePod",
        }

    def _plan_course(
        self,
        theme: str,
        hsk_level: int,
        num_lessons: int,
        requirements: list,
    ) -> list:
        """Stage 3: Plan the course structure."""
        if self.ai_engine is not None:
            try:
                plan = self.ai_engine.generate_course_plan(
                    theme, num_lessons, hsk_level
                )
                if isinstance(plan, list) and len(plan) > 0:
                    return plan
            except Exception as exc:
                self._log_action("course_plan_fallback", str(exc))

        # Offline fallback: use BOOK1_LESSONS as template
        plan = []
        template = BOOK1_LESSONS[:num_lessons]
        review_every = LESSON_STRUCTURE["review_every_n"]

        for i, tmpl in enumerate(template):
            plan.append({
                "id": tmpl["id"],
                "title_en": tmpl["title_en"],
                "title_zh": tmpl["title_zh"],
                "topic": tmpl["topic"],
                "grammar": tmpl["grammar"],
                "new_words_target": tmpl["new_words"],
                "review_from": tmpl["review_from"],
                "is_review": tmpl["topic"] == "review",
            })

        # If requesting more lessons than template provides, generate stubs
        if num_lessons > len(template):
            topics = list(VOCAB_BY_TOPIC.keys())
            for i in range(len(template), num_lessons):
                lesson_num = i + 1
                is_review = (lesson_num % review_every == 0)
                topic_idx = i % len(topics)
                plan.append({
                    "id": lesson_num,
                    "title_en": f"Review {lesson_num // review_every}" if is_review else f"Lesson {lesson_num}",
                    "title_zh": f"复习{lesson_num // review_every}" if is_review else f"第{lesson_num}课",
                    "topic": "review" if is_review else topics[topic_idx],
                    "grammar": "Review" if is_review else "TBD",
                    "new_words_target": 2 if is_review else HSK_LEVELS.get(hsk_level, HSK_LEVELS[1])["new_words_per_lesson"],
                    "review_from": list(range(max(1, lesson_num - 4), lesson_num)),
                    "is_review": is_review,
                })

        return plan

    def gather_materials(self, theme: str, sources: list = None) -> list:
        """Stage 4: Gather materials from all available sources.

        Returns a list of material dicts: {"source", "type", "content"}.
        """
        sources = sources or []
        materials: list[dict] = []

        # 1. Built-in lesson data
        for lid, lesson in LESSONS.items():
            materials.append({
                "source": f"lesson_data.py (Lesson {lid})",
                "type": "builtin",
                "content": json.dumps(lesson, ensure_ascii=False, default=str),
            })
        if materials:
            print(f"    内置数据 / Built-in data: {len(materials)} lessons loaded")

        # 2. HSK vocabulary
        topic_matches = []
        for topic, vocab_list in VOCAB_BY_TOPIC.items():
            if topic in theme.lower() or theme.lower() in topic:
                topic_matches.append(topic)
            materials.append({
                "source": f"hsk_vocab.py ({topic})",
                "type": "vocabulary",
                "content": json.dumps(
                    [{"zh": v[0], "pinyin": v[1], "literal": v[2], "en": v[3]} for v in vocab_list],
                    ensure_ascii=False,
                ),
            })
        if topic_matches:
            print(f"    词汇匹配 / Vocab match: {', '.join(topic_matches)}")

        # 3. GetNotes integration
        if self.getnotes is not None:
            try:
                print(f"    GetNotes: 搜索 '{theme}' ...")
                notes = self.getnotes.search_notes_by_keyword(theme)
                for note in (notes or []):
                    materials.append({
                        "source": f"GetNotes: {note.get('title', 'untitled')}",
                        "type": "getnotes",
                        "content": self.getnotes.extract_teaching_content(note),
                    })
                print(f"    GetNotes: {len(notes or [])} notes found")
            except Exception as exc:
                self._log_action("getnotes_error", str(exc))
                print(f"    GetNotes: 跳过 / skipped ({exc})")
        else:
            print("    GetNotes: 不可用 / not available, skipping")

        # 4. Process user-added sources
        all_sources = list(self._sources) + [
            {"type": "url" if s.startswith("http") else "text", "value": s}
            for s in sources
        ]

        for src in all_sources:
            stype = src["type"]
            sval = src["value"]

            if stype in ("url", "pdf", "file") and self.extractor is not None:
                try:
                    print(f"    提取 / Extracting: {sval[:60]}...")
                    if stype == "url":
                        result = self.extractor.extract_from_url(sval)
                    elif stype == "pdf":
                        result = self.extractor.extract_from_pdf(sval)
                    else:
                        result = self.extractor.extract_from_file(sval)
                    content = result.get("content", result.get("text", "")) if isinstance(result, dict) else str(result or "")
                    materials.append({
                        "source": sval[:80],
                        "type": stype,
                        "content": content,
                    })
                except Exception as exc:
                    self._log_action("extract_error", f"{sval}: {exc}")
                    print(f"    [!] 提取失败 / Extraction failed: {exc}")
            elif stype == "text":
                materials.append({
                    "source": "user_text",
                    "type": "text",
                    "content": sval,
                })
            elif stype == "getnotes_topic" and self.getnotes is not None:
                try:
                    notes = self.getnotes.search_notes_by_keyword(sval)
                    for note in (notes or []):
                        materials.append({
                            "source": f"GetNotes: {note.get('title', '')}",
                            "type": "getnotes",
                            "content": self.getnotes.extract_teaching_content(note),
                        })
                except Exception as exc:
                    self._log_action("getnotes_topic_error", str(exc))
            elif stype == "getnotes_note" and self.getnotes is not None:
                try:
                    note = self.getnotes.get_note(sval)
                    if note:
                        materials.append({
                            "source": f"GetNotes: {note.get('title', '')}",
                            "type": "getnotes",
                            "content": self.getnotes.extract_teaching_content(note),
                        })
                except Exception as exc:
                    self._log_action("getnotes_note_error", str(exc))
            elif stype in ("url", "pdf", "file"):
                print(f"    [!] 提取器不可用 / Extractor unavailable for: {sval[:60]}")

        return materials

    def _filter_privacy(self, materials: list[dict]) -> list[dict]:
        """Stage 5: Apply privacy filter to all materials."""
        total_findings = 0
        clean = []
        for mat in materials:
            content = mat["content"]
            findings = self.privacy_filter.scan(content)
            if findings:
                total_findings += len(findings)
                content = self.privacy_filter.anonymize(content)
            clean.append({**mat, "content": content})

        report = self.privacy_filter.get_report()
        print(f"  扫描结果 / Scan results: {total_findings} PII items found & cleaned")
        self._log_action(STAGE_PRIVACY, f"{total_findings} findings anonymized")
        return clean

    def _generate_lessons(
        self,
        plan: list[dict],
        materials: list[dict],
        hsk_level: int,
    ) -> list[dict]:
        """Stage 6: Generate lesson content for each planned lesson."""
        lessons = []
        total = len(plan)

        for idx, item in enumerate(plan):
            lid = item["id"]
            print(f"  [{idx + 1}/{total}] L{lid:02d}: {item['title_en']} ({item['title_zh']})")

            # Try to use existing lesson data first
            existing = get_lesson(lid)
            if existing:
                print(f"         使用内置数据 / Using built-in data")
                lessons.append(existing)
                continue

            # Try AI generation
            if self.ai_engine is not None:
                try:
                    print(f"         AI 生成中 / AI generating...")
                    topic = item.get("topic", item.get("title_en", "general"))
                    lesson_num = item.get("lesson_num", lid)
                    prev_vocab = []
                    for prev in lessons:
                        if prev.get("new_words"):
                            prev_vocab.extend([w[0] if isinstance(w, (list, tuple)) else w for w in prev["new_words"]])
                    context = json.dumps(materials, ensure_ascii=False, default=str) if materials else ""

                    # PhraseMemory: find reusable sentence patterns
                    if self.phrase_memory is not None:
                        try:
                            reusable = self.phrase_memory.find_matching(topic, hsk_level)
                            if reusable:
                                phrase_info = "; ".join(
                                    p.get("pattern", str(p)) if isinstance(p, dict) else str(p)
                                    for p in reusable[:5]
                                )
                                context += f"\n[Reusable sentence patterns: {phrase_info}]"
                                print(f"         复用句型 / Reusable patterns: {len(reusable)}")
                        except Exception as exc:
                            self._log_action("phrase_memory_error", f"L{lid}: {exc}")

                    lesson = self.ai_engine.generate_lesson(
                        topic=topic,
                        hsk_level=hsk_level,
                        lesson_num=lesson_num,
                        previous_vocab=prev_vocab,
                        context_notes=context,
                    )
                    if isinstance(lesson, dict) and "id" in lesson:
                        # VocabLedger: register new words from this lesson
                        if self.vocab_ledger is not None:
                            try:
                                for w in lesson.get("new_words", []):
                                    word = w[0] if isinstance(w, (list, tuple)) else w
                                    self.vocab_ledger.register_word(
                                        word=word, lesson_id=lid, hsk_level=hsk_level
                                    )
                            except Exception as exc:
                                self._log_action("vocab_ledger_error", f"L{lid}: {exc}")
                        lessons.append(lesson)
                        continue
                except Exception as exc:
                    self._log_action(
                        "generate_lesson_error",
                        f"Lesson {lid}: {exc}",
                    )
                    self.state["errors"].append(f"AI generation failed for L{lid}: {exc}")

            # Offline fallback: build a skeleton lesson from vocab data
            print(f"         离线骨架 / Offline skeleton")
            skeleton = self._build_skeleton_lesson(item, hsk_level)

            # VocabLedger: register words even for skeleton lessons
            if self.vocab_ledger is not None:
                try:
                    for w in skeleton.get("new_words", []):
                        word = w[0] if isinstance(w, (list, tuple)) else w
                        self.vocab_ledger.register_word(
                            word=word, lesson_id=lid, hsk_level=hsk_level
                        )
                except Exception as exc:
                    self._log_action("vocab_ledger_error", f"L{lid}: {exc}")

            lessons.append(skeleton)

        return lessons

    def _build_skeleton_lesson(self, plan_item: dict, hsk_level: int) -> dict:
        """Build a minimal lesson structure from offline data when AI is
        not available."""
        topic = plan_item.get("topic", "general")
        vocab = get_vocab_for_lesson(topic)

        # Limit new words
        hsk_info = HSK_LEVELS.get(hsk_level, HSK_LEVELS[1])
        max_new = plan_item.get("new_words_target", hsk_info["new_words_per_lesson"])
        selected_vocab = vocab[:max_new]

        new_words = [
            (v[0], v[1], v[2], v[3], v[4]) for v in selected_vocab
        ]

        return {
            "id": plan_item["id"],
            "title_en": plan_item["title_en"],
            "title_zh": plan_item["title_zh"],
            "book": hsk_info["book"],
            "hsk_level": hsk_level,
            "learning_goals": [
                f"Learn vocabulary about {topic}",
                f"Practice {plan_item.get('grammar', 'basic grammar')}",
                "Build conversational confidence",
            ],
            "new_words": new_words,
            "dialogues": [],
            "grammar_points": [
                {
                    "title": plan_item.get("grammar", "Grammar Point"),
                    "explanation": (
                        f"[AI-generated explanation will appear here when "
                        f"AI engine is available]\n\n"
                        f"Topic: {topic}\nGrammar focus: {plan_item.get('grammar', 'TBD')}"
                    ),
                }
            ],
            "culture_note": {
                "title": f"Culture Note: {topic.replace('_', ' ').title()}",
                "text": (
                    f"[AI-generated culture note about {topic} will appear "
                    f"here when AI engine is available]"
                ),
            },
            "exercises": [],
            "_skeleton": True,  # marker for offline-generated content
        }

    def validate_course(self, lessons: list[dict]) -> dict:
        """Stage 7: Validate using QAEngine if available, else simple validation."""
        if self.qa_engine is not None:
            return self._validate_course(lessons, lessons[0].get("hsk_level", 1) if lessons else 1)
        return self._validate_course_simple(lessons)

    def _validate_course(self, lessons, hsk_level):
        """QAEngine-powered validation with auto-improvement."""
        results = []
        for lesson in lessons:
            report = self.qa_engine.check_lesson(lesson)
            results.append({
                "lesson_id": lesson.get("id"),
                "score": report.score,
                "passed": report.passed,
                "issues": len(report.issues),
                "errors": [i.message for i in report.issues if i.severity == "error"],
            })
            # If QA fails and AI is available, try to improve
            if not report.passed and self.ai_engine is not None:
                try:
                    feedback = "; ".join(i.message for i in report.issues[:3])
                    improved = self.ai_engine.improve_lesson(lesson, feedback)
                    if isinstance(improved, dict) and not improved.get("error"):
                        # Re-check improved version
                        re_report = self.qa_engine.check_lesson(improved)
                        if re_report.score > report.score:
                            lessons[lessons.index(lesson)] = improved
                            results[-1]["score"] = re_report.score
                            results[-1]["passed"] = re_report.passed
                            results[-1]["improved"] = True
                except Exception:
                    pass

        all_passed = all(r["passed"] for r in results)
        total_errors = sum(len(r["errors"]) for r in results)
        warnings = []
        for r in results:
            for err in r["errors"]:
                warnings.append(f"L{r['lesson_id']}: {err}")

        self._log_action(
            STAGE_VALIDATE,
            f"QAEngine: passed={all_passed}, lessons={len(results)}, errors={total_errors}",
        )
        return {
            "passed": all_passed,
            "total_lessons": len(lessons),
            "warnings": warnings,
            "errors": [],
            "stats": {
                "qa_results": results,
                "total_new_words": sum(
                    len(l.get("new_words", [])) for l in lessons
                ),
            },
        }

    def _validate_course_simple(self, lessons: list[dict]) -> dict:
        """Simple validation fallback (original logic).

        Checks:
        - Vocabulary does not exceed HSK level
        - New words per lesson within limits
        - Progressive difficulty
        - No duplicate culture notes
        - Vocab reuse >= 30%
        """
        warnings = []
        errors = []
        culture_titles = set()
        all_learned_words = set()

        for idx, lesson in enumerate(lessons):
            lid = lesson.get("id", idx + 1)
            hsk = lesson.get("hsk_level", 1)
            hsk_info = HSK_LEVELS.get(hsk, HSK_LEVELS[1])
            is_review = lesson.get("title_en", "").lower().startswith("review") or \
                        lesson.get("title_zh", "").startswith("复习") or \
                        lesson.get("title_zh", "").startswith("总复习")

            # Check new word count
            new_words = lesson.get("new_words", [])
            max_allowed = (
                CONSISTENCY_RULES["max_new_words_review"]
                if is_review
                else CONSISTENCY_RULES["max_new_words_regular"]
            )
            if len(new_words) > max_allowed:
                warnings.append(
                    f"L{lid}: {len(new_words)} new words exceeds limit "
                    f"of {max_allowed} ({'review' if is_review else 'regular'})"
                )

            # Check HSK compliance
            for word_tuple in new_words:
                zh = word_tuple[0] if isinstance(word_tuple, (list, tuple)) else ""
                if zh and not check_vocab_in_hsk(zh, hsk):
                    warnings.append(
                        f"L{lid}: '{zh}' may exceed HSK {hsk} vocabulary"
                    )

            # Check vocab reuse (from lesson 3 onwards)
            new_word_chars = {
                w[0] for w in new_words if isinstance(w, (list, tuple))
            }
            if idx >= 2 and all_learned_words:
                # Check review words
                review_words = lesson.get("review_words", [])
                review_chars = {
                    w[0] for w in review_words if isinstance(w, (list, tuple))
                }
                # Also count words used in dialogues
                dialogue_text = ""
                for dlg in lesson.get("dialogues", []):
                    for line in dlg.get("lines", []):
                        if len(line) >= 2:
                            dialogue_text += line[1]

                reused = sum(
                    1 for w in all_learned_words if w in dialogue_text
                ) + len(review_chars & all_learned_words)
                total_context = len(all_learned_words)
                if total_context > 0:
                    ratio = reused / total_context
                    min_ratio = CONSISTENCY_RULES["min_vocab_reuse_ratio"]
                    if ratio < min_ratio and not lesson.get("_skeleton"):
                        warnings.append(
                            f"L{lid}: vocab reuse ratio {ratio:.0%} "
                            f"< required {min_ratio:.0%}"
                        )

            all_learned_words.update(new_word_chars)

            # Check duplicate culture notes
            cn = lesson.get("culture_note", {})
            cn_title = cn.get("title", "") if isinstance(cn, dict) else ""
            if cn_title:
                if cn_title in culture_titles:
                    warnings.append(f"L{lid}: duplicate culture note '{cn_title}'")
                culture_titles.add(cn_title)

        passed = len(errors) == 0
        report = {
            "passed": passed,
            "total_lessons": len(lessons),
            "warnings": warnings,
            "errors": errors,
            "stats": {
                "total_new_words": sum(
                    len(l.get("new_words", [])) for l in lessons
                ),
                "unique_culture_notes": len(culture_titles),
                "skeleton_lessons": sum(
                    1 for l in lessons if l.get("_skeleton")
                ),
            },
        }

        self._log_action(
            STAGE_VALIDATE,
            f"passed={passed}, warnings={len(warnings)}, errors={len(errors)}",
        )
        return report

    def _produce_pdfs(
        self,
        lessons: list[dict],
        plan: list,
        theme: str,
        hsk_level: int,
    ) -> list[str]:
        """Stage 8: Generate PDF files for all lessons."""
        output_files = []

        # Ensure fonts are available
        try:
            from pdf_builder import download_fonts
            print("  字体检查 / Checking fonts...")
            if not download_fonts():
                print("  [!] 字体下载失败，使用后备字体 / Font download failed, using fallback")
        except Exception as exc:
            print(f"  [!] 字体错误 / Font error: {exc}")

        # Generate book cover
        try:
            print("  生成封面 / Generating cover...")
            cover_path = self.generator.generate_sample_book_cover()
            if cover_path:
                output_files.append(cover_path)
        except Exception as exc:
            self._log_action("pdf_cover_error", str(exc))
            self.state["errors"].append(f"Cover generation failed: {exc}")

        # Generate each lesson that has built-in data
        for lesson in lessons:
            lid = lesson.get("id")

            # Export gate: check if lesson passes QA requirements
            if self.qa_engine is not None:
                try:
                    can, reasons = self.qa_engine.can_export(lesson)
                    if not can:
                        print(f"    ⚠ 发布闸门未通过 / Export gate blocked: {'; '.join(reasons)}")
                        continue  # Skip this lesson's PDF
                except Exception as exc:
                    self._log_action("export_gate_error", f"L{lid}: {exc}")

            if lesson.get("_skeleton"):
                # Skeleton lessons cannot produce full PDFs without the
                # complete dialogue/exercise data that the PDF builder expects
                print(
                    f"  L{lid:02d}: 跳过骨架课 / Skipping skeleton lesson "
                    f"(requires AI engine for full content)"
                )
                # Save skeleton as JSON for reference
                json_path = os.path.join(
                    self._output_dir,
                    f"ZTurns_Book{hsk_level}_Lesson{lid:02d}_skeleton.json",
                )
                os.makedirs(self._output_dir, exist_ok=True)
                with open(json_path, "w", encoding="utf-8") as f:
                    # Remove the _skeleton marker for cleaner output
                    clean = {k: v for k, v in lesson.items() if k != "_skeleton"}
                    json.dump(clean, f, ensure_ascii=False, indent=2)
                output_files.append(json_path)
                print(f"         已保存骨架 JSON / Saved skeleton: {os.path.basename(json_path)}")
                continue

            # Full lesson with data -> generate PDF
            try:
                print(f"  L{lid:02d}: 生成 PDF / Generating PDF...")
                path = self.generator.generate_lesson(lid)
                if path:
                    output_files.append(path)
            except Exception as exc:
                self._log_action("pdf_lesson_error", f"Lesson {lid}: {exc}")
                self.state["errors"].append(f"PDF failed for L{lid}: {exc}")
                print(f"  L{lid:02d}: [!] PDF 生成失败 / Failed: {exc}")

        return output_files

    # ------------------------------------------------------------------
    # Interactive CLI mode
    # ------------------------------------------------------------------

    def interactive_mode(self):
        """Run an interactive CLI session."""
        _banner("Z Turns Chinese - AI Commander (Interactive Mode)")
        print("  智能指挥官交互模式 / AI Commander Interactive Mode")
        print()

        self._print_capabilities()

        print("\n可用命令 / Available commands:")
        print("  mission <brief>      - 执行任务 / Execute a mission")
        print("  source <type> <val>  - 添加来源 / Add a material source")
        print("  run                  - 使用默认参数运行 / Run with default params")
        print("  plan <theme>         - 仅规划课程 / Plan course only")
        print("  validate             - 验证已生成课程 / Validate generated lessons")
        print("  status               - 查看状态 / View pipeline status")
        print("  demo                 - 离线演示 / Offline demo")
        print("  log                  - 查看日志 / View action log")
        print("  help                 - 显示帮助 / Show help")
        print("  quit / exit          - 退出 / Exit")
        print()

        while True:
            try:
                raw = input("commander> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再见 / Goodbye!")
                break

            if not raw:
                continue

            parts = raw.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ("quit", "exit", "q"):
                print("再见 / Goodbye!")
                break

            elif cmd == "help":
                self._print_help()

            elif cmd == "status":
                self.print_status()

            elif cmd == "log":
                self._print_log()

            elif cmd == "demo":
                self._run_demo()

            elif cmd == "mission":
                if not arg:
                    arg = input("  请输入任务简报 / Enter mission brief: ").strip()
                if arg:
                    self.execute_mission(arg)

            elif cmd == "source":
                src_parts = arg.split(maxsplit=1)
                if len(src_parts) >= 2:
                    self.add_source(src_parts[0], src_parts[1])
                else:
                    print("  用法 / Usage: source <type> <value>")
                    print("  类型 / Types: url, pdf, file, text, getnotes_topic, getnotes_note")

            elif cmd == "run":
                self.run_pipeline(
                    theme="Beginner's complete course",
                    hsk_level=1,
                    num_lessons=15,
                )

            elif cmd == "plan":
                theme = arg or "general Chinese"
                plan = self._plan_course(theme, 1, 15, [])
                print(f"\n课程计划 / Course Plan ({len(plan)} lessons):")
                for item in plan:
                    marker = " [Review]" if item.get("is_review") else ""
                    print(
                        f"  L{item['id']:02d}: {item['title_en']} "
                        f"({item['title_zh']}) - {item['topic']}{marker}"
                    )

            elif cmd == "validate":
                if self.state["lessons"]:
                    report = self.validate_course(self.state["lessons"])
                    self._print_validation_report(report)
                else:
                    print("  尚无课程数据 / No lessons generated yet. Run a mission first.")

            else:
                # Treat unknown input as a mission brief
                print(f"  未知命令，尝试作为任务执行... / Unknown command, trying as mission...")
                self.execute_mission(raw)

    # ------------------------------------------------------------------
    # Demo / offline mode
    # ------------------------------------------------------------------

    def _run_demo(self):
        """Run an offline demonstration using built-in lesson data."""
        _banner("离线演示模式 / Offline Demo Mode")
        print("  使用内置数据生成可用课程")
        print("  Generating available lessons from built-in data\n")

        available = get_available_lessons()
        if not available:
            print("  没有可用的内置课程数据 / No built-in lesson data available")
            return

        print(f"  可用课程 / Available lessons: {available}")

        # Generate PDFs for available lessons
        try:
            from pdf_builder import download_fonts
            print("\n  字体检查 / Checking fonts...")
            download_fonts()
        except Exception:
            print("  [!] 字体不可用 / Fonts unavailable")

        output_files = []
        try:
            cover = self.generator.generate_sample_book_cover()
            if cover:
                output_files.append(cover)
        except Exception as exc:
            print(f"  [!] 封面生成失败 / Cover failed: {exc}")

        for lid in available:
            try:
                path = self.generator.generate_lesson(lid)
                if path:
                    output_files.append(path)
            except Exception as exc:
                print(f"  [!] L{lid} 失败 / Failed: {exc}")

        print(f"\n  完成 / Done! {len(output_files)} files generated")
        for fp in output_files:
            print(f"    - {os.path.basename(fp)}")

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _print_capabilities(self):
        """Print the current system capabilities."""
        print("系统能力 / System Capabilities:")
        checks = [
            ("AI Engine (AI 引擎)", self.ai_engine is not None),
            ("GetNotes Client", self.getnotes is not None),
            ("Content Extractor (内容提取器)", self.extractor is not None),
            ("Privacy Filter (隐私过滤器)", self.privacy_filter is not None),
            ("Lesson Generator (课程生成器)", self.generator is not None),
        ]
        for name, available in checks:
            icon = "[OK]" if available else "[--]"
            print(f"  {icon} {name}")

        if not self.ai_engine:
            print("\n  提示: AI 引擎未就绪。将使用离线模式(内置数据)。")
            print("  Hint: AI engine not ready. Will use offline mode (built-in data).")
            print("  要启用 AI 生成，请配置 ai_engine.py 及 API key。")

    def _print_help(self):
        """Print detailed help text."""
        print("""
AI Commander 帮助 / Help
========================

命令 / Commands:
  mission <brief>       以自然语言描述任务，自动解析并执行完整管线
                        Describe a task in natural language; auto-parse and run pipeline

  source <type> <val>   添加素材来源
                        Add a material source
                        Types: url, pdf, file, text, getnotes_topic, getnotes_note
                        Example: source url https://example.com/lesson.html
                        Example: source text "How to order food in Chinese"

  run                   使用默认参数运行完整管线 (Book 1, 15 lessons, HSK 1)
                        Run full pipeline with default params

  plan <theme>          仅生成课程计划，不生成 PDF
                        Generate course plan only, no PDFs

  validate              验证已生成的课程质量
                        Validate generated lessons for quality

  demo                  离线演示 - 使用内置数据生成 PDF
                        Offline demo - generate PDFs from built-in data

  status                查看管线状态
                        View pipeline status

  log                   查看操作日志
                        View action log

  help                  显示此帮助
                        Show this help

  quit / exit           退出
                        Exit

示例任务 / Example Missions:
  "Create a complete Pinyin learning course"
  "Generate HSK 1 Book 1 with 15 daily-life lessons"
  "Build a 5-lesson mini-course about Chinese food culture, HSK 2"
  "零基础入门中文课程，15课"
""")

    def _print_log(self):
        """Print the action log."""
        if not self.log:
            print("  日志为空 / Log is empty")
            return
        print(f"\n操作日志 / Action Log ({len(self.log)} entries):")
        for entry in self.log[-20:]:
            ts = entry["timestamp"].split("T")[1].split(".")[0]
            print(f"  [{ts}] {entry['action']}: {entry['detail'][:80]}")

    def _print_validation_report(self, report: dict):
        """Pretty-print a validation report."""
        status = "PASS" if report["passed"] else "ISSUES FOUND"
        print(f"\n=== 质量报告 / Quality Report: {status} ===")
        print(f"  课程数 / Lessons   : {report['total_lessons']}")
        print(f"  总新词 / Total new : {report['stats']['total_new_words']}")
        print(f"  文化笔记 / Culture : {report['stats']['unique_culture_notes']}")
        print(f"  骨架课 / Skeletons : {report['stats']['skeleton_lessons']}")
        if report["warnings"]:
            print(f"\n  警告 / Warnings ({len(report['warnings'])}):")
            for w in report["warnings"]:
                print(f"    [!] {w}")
        if report["errors"]:
            print(f"\n  错误 / Errors ({len(report['errors'])}):")
            for e in report["errors"]:
                print(f"    [X] {e}")
        if not report["warnings"] and not report["errors"]:
            print("  所有检查通过 / All checks passed!")


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

def run_mission(brief: str):
    """Convenience function: create a commander and execute a mission."""
    commander = AICommander()
    commander.execute_mission(brief)
    return commander


def run_offline_demo():
    """Convenience function: run offline demo."""
    commander = AICommander()
    commander._run_demo()
    return commander


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Z Turns Chinese - AI Commander",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ai_commander.py                                  Interactive mode
  python3 ai_commander.py --mission "Create HSK 1 course"  Execute mission
  python3 ai_commander.py --offline                        Offline demo
  python3 ai_commander.py --status                         Show capabilities
        """,
    )
    parser.add_argument(
        "--mission", type=str,
        help="Mission brief to execute (natural language)",
    )
    parser.add_argument(
        "--offline", action="store_true",
        help="Run offline demo with built-in data",
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Show system capabilities and exit",
    )

    args = parser.parse_args()

    if args.status:
        commander = AICommander()
        commander._print_capabilities()
        commander.print_status()
    elif args.offline:
        run_offline_demo()
    elif args.mission:
        run_mission(args.mission)
    else:
        commander = AICommander()
        commander.interactive_mode()
