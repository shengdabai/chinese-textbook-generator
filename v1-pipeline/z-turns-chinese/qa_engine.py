"""
QA Engine - Quality Assurance for Z Turns Chinese textbook generation.
Combines Kimi's publish-gate workflow with GPT's QA system.
Implements 12 automated checks, QA reporting, publish gate, and batch course checks.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional

from config import HSK_LEVELS, CONSISTENCY_RULES, BOOK1_LESSONS
from privacy_filter import PrivacyFilter
from hsk_vocab import VOCAB_BY_TOPIC, check_vocab_in_hsk, get_all_vocab_up_to_lesson


# ============================================================
# Data Classes
# ============================================================

@dataclass
class QAIssue:
    """A single QA issue found during checking."""
    category: str           # e.g. "pii", "new_words", "bilingual", "pinyin", etc.
    severity: str           # "error" | "warning" | "info"
    line: Optional[int]     # line/index reference, None if global
    message: str            # description of the issue
    suggestion: str = ""    # suggested fix


@dataclass
class QAReport:
    """Full QA report for a lesson."""
    lesson_id: int
    passed: bool = True
    score: float = 100.0
    issues: list = field(default_factory=list)
    privacy_score: float = 100.0
    consistency_score: float = 100.0
    pedagogy_score: float = 100.0

    def add_issue(self, issue: QAIssue):
        self.issues.append(issue)
        # Recalculate pass status: any error => fail
        if issue.severity == "error":
            self.passed = False

    def summary(self) -> str:
        """Return a human-readable summary string."""
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]
        infos = [i for i in self.issues if i.severity == "info"]
        status = "PASS" if self.passed else "FAIL"
        return (
            f"[{status}] Lesson {self.lesson_id} | "
            f"Score: {self.score:.1f}/100 | "
            f"Errors: {len(errors)}, Warnings: {len(warnings)}, Info: {len(infos)} | "
            f"Privacy: {self.privacy_score:.0f}, Consistency: {self.consistency_score:.0f}, "
            f"Pedagogy: {self.pedagogy_score:.0f}"
        )


# ============================================================
# QA Engine
# ============================================================

class QAEngine:
    """Quality assurance engine for Chinese textbook lessons.
    Runs 12 automated checks and produces QA reports.
    """

    # New word limits by CEFR level label
    NEW_WORD_LIMITS = {"A1": 10, "A1+": 12, "A2": 15}

    # Common English phrases in educational content that are NOT PII
    PII_WHITELIST = {
        "Chinese", "English", "Mandarin", "Pinyin", "Match Chinese",
        "Translate", "Fill", "Write", "Chinese Word Order", "The Magic",
        "Measure Words", "In Chinese", "Unlike English", "Subject Verb",
        "Hello", "Thank", "Goodbye", "Please", "Sorry",
        "China", "America", "England", "Japan", "Korea",
    }

    def __init__(self):
        self.privacy_filter = PrivacyFilter()
        self.fixed_names = CONSISTENCY_RULES.get("fixed_character_names", [])
        self.min_vocab_reuse = CONSISTENCY_RULES.get("min_vocab_reuse_ratio", 0.30)
        self.grammar_must_increase = CONSISTENCY_RULES.get("grammar_must_increase", True)
        self.no_duplicate_culture = CONSISTENCY_RULES.get("no_duplicate_culture", True)

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def check_lesson(self, lesson: dict, prev_lessons: list = None) -> QAReport:
        """Run all 12 checks on a single lesson and return a QAReport.

        Args:
            lesson: lesson dict following the standard schema.
            prev_lessons: list of preceding lesson dicts (for cross-lesson checks).
        """
        prev_lessons = prev_lessons or []
        report = QAReport(lesson_id=lesson.get("id", 0))

        # Run all 12 checks
        self._check_pii(lesson, report)
        self._check_new_word_count(lesson, report)
        self._check_bilingual_completeness(lesson, report)
        self._check_pinyin_coverage(lesson, report)
        self._check_pattern_reuse(lesson, prev_lessons, report)
        self._check_hsk_compliance(lesson, report)
        self._check_grammar_progression(lesson, prev_lessons, report)
        self._check_culture_dedup(lesson, prev_lessons, report)
        self._check_character_names(lesson, report)
        self._check_exercise_completeness(lesson, report)
        self._check_dialogue_turns(lesson, report)
        self._check_vocab_reuse(lesson, prev_lessons, report)

        # Compute composite score
        report.score = self._compute_score(report)
        return report

    def can_export(self, lesson: dict) -> tuple:
        """Publish gate: decide if a lesson may be exported.

        Returns:
            (bool, list[str]) - pass/fail and list of blocking reasons.
        """
        report = self.check_lesson(lesson)
        blockers = []

        # Gate 1: PII must be 100%
        if report.privacy_score < 100.0:
            blockers.append(
                f"PII check failed (score {report.privacy_score:.0f}%). "
                "PII检查未通过，存在隐私信息残留。"
            )

        # Gate 2: new words within limit
        hsk = lesson.get("hsk_level", 1)
        level_info = HSK_LEVELS.get(hsk, {})
        limit = level_info.get("max_new_words", 10)
        actual = len(lesson.get("new_words", []))
        if actual > limit:
            blockers.append(
                f"New words ({actual}) exceed HSK{hsk} limit ({limit}). "
                f"新词数量({actual})超过HSK{hsk}上限({limit})。"
            )

        # Gate 3: bilingual alignment 100%
        bilingual_issues = [
            i for i in report.issues
            if i.category == "bilingual" and i.severity == "error"
        ]
        if bilingual_issues:
            blockers.append(
                f"Bilingual alignment incomplete ({len(bilingual_issues)} issues). "
                f"中英对齐不完整，{len(bilingual_issues)}处缺失。"
            )

        # Gate 4: pinyin coverage >= 95%
        pinyin_issues = [
            i for i in report.issues
            if i.category == "pinyin" and i.severity == "error"
        ]
        if pinyin_issues:
            blockers.append(
                "Pinyin coverage below 95%. "
                "拼音覆盖率低于95%。"
            )

        can = len(blockers) == 0
        return (can, blockers)

    def check_course(self, lessons: list) -> dict:
        """Check an entire course for cross-lesson consistency.

        Args:
            lessons: list of lesson dicts, ordered by id.

        Returns:
            dict with overall stats and per-lesson reports.
        """
        sorted_lessons = sorted(lessons, key=lambda l: l.get("id", 0))
        reports = []
        culture_topics_seen = set()
        grammar_levels = []
        all_issues = []

        # Build cumulative previous lessons list incrementally
        prev_accumulator = []
        for i, lesson in enumerate(sorted_lessons):
            report = self.check_lesson(lesson, prev_accumulator)
            prev_accumulator.append(lesson)
            reports.append(report)
            all_issues.extend(report.issues)

            # Track culture topics across lessons
            cn = lesson.get("culture_note", {})
            topic = cn.get("title", "")
            if topic:
                if topic in culture_topics_seen:
                    report.add_issue(QAIssue(
                        category="culture_dedup",
                        severity="warning",
                        line=None,
                        message=(
                            f"Culture topic '{topic}' duplicated across lessons. "
                            f"文化主题 '{topic}' 在课程中重复出现。"
                        ),
                        suggestion="Use a unique culture topic per lesson. 每课使用不同文化主题。",
                    ))
                culture_topics_seen.add(topic)

        total = len(reports)
        passed = sum(1 for r in reports if r.passed)
        avg_score = sum(r.score for r in reports) / total if total else 0
        error_count = sum(1 for i in all_issues if i.severity == "error")
        warning_count = sum(1 for i in all_issues if i.severity == "warning")

        return {
            "total_lessons": total,
            "passed": passed,
            "failed": total - passed,
            "average_score": round(avg_score, 1),
            "total_errors": error_count,
            "total_warnings": warning_count,
            "reports": reports,
        }

    # ----------------------------------------------------------
    # 12 Checks (private methods)
    # ----------------------------------------------------------

    def _check_pii(self, lesson: dict, report: QAReport):
        """Check #1: PII final scan using PrivacyFilter."""
        text_blob = self._lesson_to_text(lesson)
        findings = self.privacy_filter.scan(text_blob)

        # Filter out false positives: common educational English phrases
        real_findings = []
        for f in findings:
            text = f["text"].strip()
            # Skip if the matched text is a known safe phrase or contains one
            is_whitelisted = False
            for safe in self.PII_WHITELIST:
                if safe.lower() in text.lower():
                    is_whitelisted = True
                    break
            # Skip known character names from config
            if text in self.fixed_names:
                is_whitelisted = True
            if not is_whitelisted:
                real_findings.append(f)

        if real_findings:
            report.privacy_score = max(0.0, 100.0 - len(real_findings) * 20)
            for f in real_findings:
                report.add_issue(QAIssue(
                    category="pii",
                    severity="error",
                    line=None,
                    message=(
                        f"PII detected [{f['category']}]: '{f['text']}'. "
                        f"检测到隐私信息 [{f['category']}]：'{f['text']}'。"
                    ),
                    suggestion="Remove or anonymize this content. 请删除或匿名化处理。",
                ))
        else:
            report.privacy_score = 100.0

    def _check_new_word_count(self, lesson: dict, report: QAReport):
        """Check #2: New word count within HSK level limit."""
        hsk = lesson.get("hsk_level", 1)
        level_info = HSK_LEVELS.get(hsk, {})
        cefr = level_info.get("cefr", "A1")
        limit = self.NEW_WORD_LIMITS.get(cefr, level_info.get("max_new_words", 10))
        actual = len(lesson.get("new_words", []))
        if actual > limit:
            report.add_issue(QAIssue(
                category="new_words",
                severity="error",
                line=None,
                message=(
                    f"New words count ({actual}) exceeds {cefr} limit ({limit}). "
                    f"新词数量({actual})超过{cefr}等级上限({limit})。"
                ),
                suggestion=f"Reduce to {limit} or fewer new words. 减少新词至{limit}个以内。",
            ))
        elif actual == 0 and lesson.get("id", 0) not in (5, 10, 15):
            # Non-review lessons should have some new words
            report.add_issue(QAIssue(
                category="new_words",
                severity="warning",
                line=None,
                message=(
                    "No new words in a non-review lesson. "
                    "非复习课没有新词。"
                ),
                suggestion="Add new vocabulary appropriate to the lesson topic. 添加与课题相关的新词。",
            ))

    def _check_bilingual_completeness(self, lesson: dict, report: QAReport):
        """Check #3: Every dialogue line must have 4-layer translation (zh/pinyin/literal/natural)."""
        for d_idx, dialogue in enumerate(lesson.get("dialogues", [])):
            for l_idx, line in enumerate(dialogue.get("lines", [])):
                if len(line) < 5:
                    report.add_issue(QAIssue(
                        category="bilingual",
                        severity="error",
                        line=l_idx + 1,
                        message=(
                            f"Dialogue {d_idx+1}, line {l_idx+1}: incomplete 4-layer translation "
                            f"(got {len(line)} fields, need 5: speaker/zh/pinyin/literal/natural). "
                            f"对话{d_idx+1}第{l_idx+1}行：四层翻译不完整"
                            f"（有{len(line)}个字段，需要5个：角色/中文/拼音/直译/意译）。"
                        ),
                        suggestion="Add missing translation layers. 补全缺失的翻译层。",
                    ))
                else:
                    speaker, zh, pinyin, literal, natural = line[0], line[1], line[2], line[3], line[4]
                    missing = []
                    if not zh.strip():
                        missing.append("zh/中文")
                    if not pinyin.strip():
                        missing.append("pinyin/拼音")
                    if not literal.strip():
                        missing.append("literal_en/直译")
                    if not natural.strip():
                        missing.append("natural_en/意译")
                    if missing:
                        report.add_issue(QAIssue(
                            category="bilingual",
                            severity="error",
                            line=l_idx + 1,
                            message=(
                                f"Dialogue {d_idx+1}, line {l_idx+1}: empty field(s): {', '.join(missing)}. "
                                f"对话{d_idx+1}第{l_idx+1}行：以下字段为空：{', '.join(missing)}。"
                            ),
                            suggestion="Fill in all translation layers. 填写所有翻译层。",
                        ))

    def _check_pinyin_coverage(self, lesson: dict, report: QAReport):
        """Check #4: All Chinese words in new_words must have pinyin; coverage >= 95%."""
        new_words = lesson.get("new_words", [])
        if not new_words:
            return

        total = len(new_words)
        has_pinyin = 0
        for idx, word in enumerate(new_words):
            # word tuple: (hanzi, pinyin, ...) - at least 2 elements
            if len(word) >= 2 and word[1] and word[1].strip():
                has_pinyin += 1
            else:
                report.add_issue(QAIssue(
                    category="pinyin",
                    severity="warning",
                    line=idx + 1,
                    message=(
                        f"New word '{word[0] if word else '?'}' missing pinyin. "
                        f"新词 '{word[0] if word else '?'}' 缺少拼音标注。"
                    ),
                    suggestion="Add pinyin annotation. 添加拼音标注。",
                ))

        coverage = (has_pinyin / total * 100) if total > 0 else 100.0
        if coverage < 95.0:
            report.add_issue(QAIssue(
                category="pinyin",
                severity="error",
                line=None,
                message=(
                    f"Pinyin coverage {coverage:.1f}% is below 95% threshold. "
                    f"拼音覆盖率 {coverage:.1f}% 低于95%阈值。"
                ),
                suggestion="Ensure all new words have pinyin. 确保所有新词都有拼音标注。",
            ))

        # Also check dialogue lines for pinyin
        dialogue_total = 0
        dialogue_has_pinyin = 0
        for dialogue in lesson.get("dialogues", []):
            for line in dialogue.get("lines", []):
                if len(line) >= 3:
                    dialogue_total += 1
                    if line[2] and line[2].strip():
                        dialogue_has_pinyin += 1

        if dialogue_total > 0:
            d_coverage = dialogue_has_pinyin / dialogue_total * 100
            if d_coverage < 95.0:
                report.add_issue(QAIssue(
                    category="pinyin",
                    severity="error",
                    line=None,
                    message=(
                        f"Dialogue pinyin coverage {d_coverage:.1f}% below 95%. "
                        f"对话拼音覆盖率 {d_coverage:.1f}% 低于95%。"
                    ),
                    suggestion="Add pinyin to all dialogue lines. 为所有对话添加拼音。",
                ))

    def _check_pattern_reuse(self, lesson: dict, prev_lessons: list, report: QAReport):
        """Check #5: Reuse of sentence patterns from previous lessons >= 30%."""
        if not prev_lessons:
            return  # First lesson - nothing to reuse

        # Collect grammar patterns from previous lessons
        prev_patterns = set()
        for pl in prev_lessons:
            for gp in pl.get("grammar_points", []):
                prev_patterns.add(gp.get("title", "").lower().strip())

        if not prev_patterns:
            return

        # Check current lesson's dialogues for references to known patterns
        current_patterns = set()
        for gp in lesson.get("grammar_points", []):
            current_patterns.add(gp.get("title", "").lower().strip())

        reused = prev_patterns & current_patterns
        total_current = len(current_patterns) if current_patterns else 1
        reuse_ratio = len(reused) / max(len(prev_patterns), 1)

        threshold = self.min_vocab_reuse  # reuse threshold from config
        if reuse_ratio < threshold and len(prev_lessons) >= 2:
            report.add_issue(QAIssue(
                category="pattern_reuse",
                severity="warning",
                line=None,
                message=(
                    f"Sentence pattern reuse ratio {reuse_ratio:.0%} < {threshold:.0%}. "
                    f"句型复用率 {reuse_ratio:.0%} 低于 {threshold:.0%} 阈值。"
                ),
                suggestion="Incorporate previously learned patterns. 适当复用前课已学句型。",
            ))
            report.consistency_score = max(0, report.consistency_score - 15)

    def _check_hsk_compliance(self, lesson: dict, report: QAReport):
        """Check #6: All vocabulary within target HSK level."""
        target_level = lesson.get("hsk_level", 1)
        for idx, word in enumerate(lesson.get("new_words", [])):
            hanzi = word[0] if word else ""
            if hanzi and not check_vocab_in_hsk(hanzi, target_level):
                report.add_issue(QAIssue(
                    category="hsk_compliance",
                    severity="warning",
                    line=idx + 1,
                    message=(
                        f"Word '{hanzi}' not found in HSK {target_level} vocabulary. "
                        f"词汇 '{hanzi}' 不在HSK {target_level}级词汇表中。"
                    ),
                    suggestion=(
                        f"Verify this word belongs to HSK {target_level} or mark as supplementary. "
                        f"确认该词是否属于HSK {target_level}级或标记为补充词汇。"
                    ),
                ))

    def _check_grammar_progression(self, lesson: dict, prev_lessons: list, report: QAReport):
        """Check #7: Grammar difficulty should monotonically increase."""
        if not prev_lessons or not self.grammar_must_increase:
            return

        current_count = len(lesson.get("grammar_points", []))
        # Use grammar point count + lesson id as a rough complexity proxy
        current_complexity = lesson.get("id", 0)

        for pl in prev_lessons:
            prev_complexity = pl.get("id", 0)
            prev_count = len(pl.get("grammar_points", []))
            # A later lesson with fewer grammar points than an earlier non-review lesson
            # suggests potential regression
            if (current_complexity > prev_complexity
                    and current_count < prev_count
                    and current_count > 0
                    and pl.get("id", 0) not in (5, 10, 15)):
                report.add_issue(QAIssue(
                    category="grammar_progression",
                    severity="info",
                    line=None,
                    message=(
                        f"Grammar points ({current_count}) fewer than lesson {pl.get('id')} "
                        f"({prev_count}). Consider if this is intentional. "
                        f"语法点({current_count})少于第{pl.get('id')}课({prev_count})，"
                        f"请确认是否合理。"
                    ),
                    suggestion="Ensure grammar difficulty increases over the course. 确保语法难度递增。",
                ))
                break  # Only report once

    def _check_culture_dedup(self, lesson: dict, prev_lessons: list, report: QAReport):
        """Check #8: No duplicate culture topics across lessons."""
        if not self.no_duplicate_culture or not prev_lessons:
            return

        current_topic = lesson.get("culture_note", {}).get("title", "").strip()
        if not current_topic:
            report.add_issue(QAIssue(
                category="culture_dedup",
                severity="info",
                line=None,
                message=(
                    "No culture note found. "
                    "未找到文化小贴士。"
                ),
                suggestion="Add a culture note to enrich the lesson. 添加文化小贴士丰富课程内容。",
            ))
            return

        for pl in prev_lessons:
            prev_topic = pl.get("culture_note", {}).get("title", "").strip()
            if prev_topic and prev_topic.lower() == current_topic.lower():
                report.add_issue(QAIssue(
                    category="culture_dedup",
                    severity="warning",
                    line=None,
                    message=(
                        f"Culture topic '{current_topic}' duplicates lesson {pl.get('id')}. "
                        f"文化主题 '{current_topic}' 与第{pl.get('id')}课重复。"
                    ),
                    suggestion="Choose a unique culture topic. 选择不同的文化主题。",
                ))
                report.consistency_score = max(0, report.consistency_score - 10)
                break

    def _check_character_names(self, lesson: dict, report: QAReport):
        """Check #9: All speakers should be from the fixed character list."""
        speakers_used = set()
        for dialogue in lesson.get("dialogues", []):
            for line in dialogue.get("lines", []):
                if line:
                    speakers_used.add(line[0])

        allowed = set(self.fixed_names)
        # Also allow generic names like 服务员, 售货员 etc.
        generic_roles = {"服务员", "售货员", "老板", "同学", "学生", "医生", "司机"}
        allowed |= generic_roles

        for speaker in speakers_used:
            if speaker not in allowed:
                report.add_issue(QAIssue(
                    category="character_names",
                    severity="warning",
                    line=None,
                    message=(
                        f"Speaker '{speaker}' not in fixed character list. "
                        f"角色 '{speaker}' 不在固定角色名列表中。"
                    ),
                    suggestion=(
                        f"Use one of: {', '.join(self.fixed_names)}. "
                        f"请使用固定角色：{', '.join(self.fixed_names)}。"
                    ),
                ))
                report.consistency_score = max(0, report.consistency_score - 5)

    def _check_exercise_completeness(self, lesson: dict, report: QAReport):
        """Check #10: Each lesson must have at least 4 exercises."""
        exercises = lesson.get("exercises", [])
        count = len(exercises)
        if count < 4:
            report.add_issue(QAIssue(
                category="exercises",
                severity="error",
                line=None,
                message=(
                    f"Only {count} exercise(s), minimum 4 required. "
                    f"仅有{count}道练习题，至少需要4道。"
                ),
                suggestion="Add more exercises to meet the minimum. 增加练习题至4道以上。",
            ))
            report.pedagogy_score = max(0, report.pedagogy_score - 20)

    def _check_dialogue_turns(self, lesson: dict, report: QAReport):
        """Check #11: Core dialogue must have at least 6 turns."""
        dialogues = lesson.get("dialogues", [])
        if not dialogues:
            report.add_issue(QAIssue(
                category="dialogue_turns",
                severity="error",
                line=None,
                message=(
                    "No dialogues found. "
                    "未找到对话内容。"
                ),
                suggestion="Add at least one dialogue with 6+ turns. 添加至少一段6轮以上的对话。",
            ))
            report.pedagogy_score = max(0, report.pedagogy_score - 30)
            return

        # Check the first (core) dialogue
        core_lines = len(dialogues[0].get("lines", []))
        total_lines = sum(len(d.get("lines", [])) for d in dialogues)

        if core_lines < 6:
            report.add_issue(QAIssue(
                category="dialogue_turns",
                severity="error" if total_lines < 6 else "warning",
                line=None,
                message=(
                    f"Core dialogue has {core_lines} turns, minimum 6 required "
                    f"(total across all dialogues: {total_lines}). "
                    f"核心对话仅有{core_lines}轮，至少需要6轮"
                    f"（所有对话合计{total_lines}轮）。"
                ),
                suggestion="Expand the core dialogue. 扩展核心对话轮数。",
            ))
            if total_lines < 6:
                report.pedagogy_score = max(0, report.pedagogy_score - 15)

    def _check_vocab_reuse(self, lesson: dict, prev_lessons: list, report: QAReport):
        """Check #12: Later lessons should reuse >= 30% of previously learned vocabulary."""
        if not prev_lessons:
            return  # First lesson

        # Collect all previously introduced words
        prev_words = set()
        for pl in prev_lessons:
            for w in pl.get("new_words", []):
                if w:
                    prev_words.add(w[0])

        if not prev_words:
            return

        # Check review_words and dialogue text for reuse
        reused = set()

        # From explicit review_words
        for rw in lesson.get("review_words", []):
            if rw and rw[0] in prev_words:
                reused.add(rw[0])

        # From dialogue text
        all_dialogue_text = ""
        for dialogue in lesson.get("dialogues", []):
            for line in dialogue.get("lines", []):
                if len(line) >= 2:
                    all_dialogue_text += line[1]

        for pw in prev_words:
            if pw in all_dialogue_text:
                reused.add(pw)

        reuse_ratio = len(reused) / len(prev_words) if prev_words else 1.0
        threshold = self.min_vocab_reuse

        if reuse_ratio < threshold:
            report.add_issue(QAIssue(
                category="vocab_reuse",
                severity="warning",
                line=None,
                message=(
                    f"Vocabulary reuse ratio {reuse_ratio:.0%} < {threshold:.0%} threshold "
                    f"({len(reused)}/{len(prev_words)} words reused). "
                    f"词汇复现率 {reuse_ratio:.0%} 低于 {threshold:.0%} 阈值"
                    f"（复用{len(reused)}/{len(prev_words)}个已学词汇）。"
                ),
                suggestion="Add review words from previous lessons. 增加前课已学词汇的复现。",
            ))
            report.pedagogy_score = max(0, report.pedagogy_score - 10)

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------

    def _lesson_to_text(self, lesson: dict) -> str:
        """Flatten lesson content that may contain PII into a text blob.

        Only scans dialogue lines and culture note content -- these are
        derived from real teaching notes where personal info might leak.
        Skips titles, grammar explanations, learning goals, and exercises
        as these are authored educational content, not user data.
        """
        parts = []

        # Dialogue lines (most likely to contain PII from real notes)
        for dialogue in lesson.get("dialogues", []):
            for line in dialogue.get("lines", []):
                # Only scan the Chinese text and natural English (indices 1 and 4)
                if len(line) > 1:
                    parts.append(str(line[1]))  # Chinese text
                if len(line) > 4:
                    parts.append(str(line[4]))  # Natural English

        # Culture note content (may reference real people/places)
        cn = lesson.get("culture_note", {})
        parts.append(cn.get("content", cn.get("text", "")))

        return "\n".join(parts)

    def _compute_score(self, report: QAReport) -> float:
        """Compute a composite score from sub-scores and issue severity counts."""
        errors = sum(1 for i in report.issues if i.severity == "error")
        warnings = sum(1 for i in report.issues if i.severity == "warning")

        # Base from sub-scores (weighted average)
        base = (
            report.privacy_score * 0.30
            + report.consistency_score * 0.30
            + report.pedagogy_score * 0.40
        )

        # Deductions
        penalty = errors * 8 + warnings * 2
        score = max(0.0, min(100.0, base - penalty))
        return round(score, 1)


# ============================================================
# Demo / Test
# ============================================================

def demo():
    """Run QA checks on existing lesson data for demonstration."""
    from lesson_data import LESSONS

    engine = QAEngine()

    print("=" * 70)
    print("  Z Turns Chinese - QA Engine Demo")
    print("  中文教材生成工具 - 质量保障引擎演示")
    print("=" * 70)

    # --- Single Lesson Check ---
    lesson1 = LESSONS.get(1)
    if lesson1:
        print("\n--- Lesson 1 QA Check / 第1课质量检查 ---")
        report1 = engine.check_lesson(lesson1)
        print(report1.summary())
        if report1.issues:
            print(f"\n  Issues found / 发现问题：")
            for issue in report1.issues:
                sev_icon = {"error": "[ERROR]", "warning": "[WARN] ", "info": "[INFO] "}
                print(f"    {sev_icon.get(issue.severity, '[?]')} [{issue.category}] {issue.message}")
                if issue.suggestion:
                    print(f"           -> {issue.suggestion}")
        else:
            print("  No issues found! / 未发现问题！")

        # --- Publish Gate ---
        print(f"\n--- Publish Gate / 发布闸门 ---")
        can, blockers = engine.can_export(lesson1)
        status = "APPROVED / 通过" if can else "BLOCKED / 阻断"
        print(f"  Export status: {status}")
        if blockers:
            for b in blockers:
                print(f"    BLOCKER: {b}")

    # --- Lesson 8 Check (with lesson 1 as previous) ---
    lesson8 = LESSONS.get(8)
    if lesson8 and lesson1:
        print(f"\n--- Lesson 8 QA Check (with L1 context) / 第8课质量检查（含第1课上下文） ---")
        report8 = engine.check_lesson(lesson8, prev_lessons=[lesson1])
        print(report8.summary())
        if report8.issues:
            print(f"\n  Issues found / 发现问题：")
            for issue in report8.issues:
                sev_icon = {"error": "[ERROR]", "warning": "[WARN] ", "info": "[INFO] "}
                print(f"    {sev_icon.get(issue.severity, '[?]')} [{issue.category}] {issue.message}")
                if issue.suggestion:
                    print(f"           -> {issue.suggestion}")

    # --- Batch Course Check ---
    available_lessons = [LESSONS[k] for k in sorted(LESSONS.keys())]
    if len(available_lessons) >= 2:
        print(f"\n--- Course-Level Check / 课程级检查 ---")
        course_result = engine.check_course(available_lessons)
        print(f"  Total lessons / 总课数: {course_result['total_lessons']}")
        print(f"  Passed / 通过: {course_result['passed']}")
        print(f"  Failed / 未通过: {course_result['failed']}")
        print(f"  Average score / 平均分: {course_result['average_score']}")
        print(f"  Total errors / 总错误: {course_result['total_errors']}")
        print(f"  Total warnings / 总警告: {course_result['total_warnings']}")

    print("\n" + "=" * 70)
    print("  QA Engine demo complete. / 质量保障引擎演示完成。")
    print("=" * 70)


if __name__ == "__main__":
    demo()
