"""
AI Content Generation Engine for Z Turns Chinese AutoBuilder.
Uses Anthropic Claude API for intelligent lesson generation.
Falls back to direct HTTP calls if the anthropic SDK is not installed.
"""

import json
import os
import logging
from typing import Optional

from config import HSK_LEVELS, CONSISTENCY_RULES, LESSON_STRUCTURE, FOUR_LAYERS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Anthropic API abstraction (SDK with HTTP fallback)
# ---------------------------------------------------------------------------

try:
    import anthropic

    _HAS_SDK = True
except ImportError:
    _HAS_SDK = False

MODEL = "claude-sonnet-4-20250514"

_client = None


def _call_anthropic(system_prompt: str, user_prompt: str, *, max_tokens: int = 8192) -> str:
    """Send a request to Anthropic and return the text response.

    Uses the official SDK when available; otherwise falls back to
    urllib.request so the project has zero hard dependencies beyond stdlib.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Please set it to your Anthropic API key before using the AI engine."
        )

    if _HAS_SDK:
        global _client
        if _client is None:
            _client = anthropic.Anthropic(api_key=api_key)
        message = _client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text

    # Fallback: direct HTTP via urllib
    import urllib.request

    payload = json.dumps(
        {
            "model": MODEL,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    return body["content"][0]["text"]


# ---------------------------------------------------------------------------
# JSON extraction helper
# ---------------------------------------------------------------------------

def _extract_json(text: str):
    """Extract a JSON object or array from a string that may contain markdown fences."""
    text = text.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline == -1:
            text = text[3:]
        else:
            text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[: text.rfind("```")]
    text = text.strip()
    return json.loads(text)


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

LESSON_SYSTEM_PROMPT = """\
<Role>
You are a top-tier international Chinese education expert. You specialize in \
creating practical Chinese textbooks for zero-basis English-speaking professionals. \
Your core method is "Four-Layer Translation" — providing Chinese characters, Pinyin, \
word-by-word literal English (preserving Chinese word order), and natural English \
for every sentence.
</Role>

<Constraints>
1. Strictly follow HSK 3.0 (2026) vocabulary standards
2. Every Chinese sentence must have all 4 translation layers
3. Word-by-word English must preserve Chinese word order exactly
4. New words per lesson: max 10 for regular, max 2 for review
5. Output must be valid JSON matching the specified schema
6. Culture notes must reference modern China (2026)
7. Grammar explanations must be designed for English speakers
</Constraints>

<OutputFormat>
Return ONLY a valid JSON object (no markdown fences, no explanation). \
The JSON must match the following schema EXACTLY.

A lesson dict:
{
  "id": <int>,
  "title_en": <str>,
  "title_zh": <str>,
  "book": <str>,              // e.g. "Book 1"
  "hsk_level": <int>,         // 1, 2, or 3
  "learning_goals": [<str>, ...],   // 3 goals
  "new_words": [
    // each word is a list of 5 strings:
    [<chinese>, <pinyin>, <word_by_word_english>, <natural_english>, <part_of_speech>],
    ...
  ],
  "dialogues": [
    {
      "title": <str>,
      "lines": [
        // each line is a list of 5 strings:
        [<speaker>, <chinese>, <pinyin>, <word_by_word_english>, <natural_english>],
        ...
      ]
    },
    ...
  ],
  "grammar_points": [
    {
      "title": <str>,
      "explanation": <str>   // multi-line OK, designed for English speakers
    },
    ...
  ],
  "culture_note": {
    "title": <str>,
    "text": <str>            // reference modern China 2026
  },
  "exercises": [
    // 4 exercises. Possible types: fill_blank, translate, word_by_word, match, reorder
    // fill_blank / translate / word_by_word / reorder:
    {
      "type": <str>,
      "instruction": <str>,
      "question": <str>,
      "answer": <str>
    },
    // match:
    {
      "type": "match",
      "instruction": <str>,
      "pairs": [[<chinese>, <english>], ...]
    }
  ],
  "review_words": [
    // optional — list of previously learned words being reused
    [<chinese>, <pinyin>, <word_by_word>, <natural_english>],
    ...
  ]
}

Important tuple-vs-list note: use JSON arrays (lists) for new_words entries, \
dialogue lines, review_words entries, and match pairs.
</OutputFormat>
"""

COURSE_PLAN_SYSTEM_PROMPT = """\
<Role>
You are a curriculum designer for Chinese language textbooks targeting \
English-speaking professionals. You follow HSK 3.0 (2026) standards and design \
progressive lesson sequences with vocabulary spiraling.
</Role>

<OutputFormat>
Return ONLY a valid JSON array of lesson plan objects (no markdown, no explanation):
[
  {
    "lesson_num": <int>,
    "title_en": <str>,
    "title_zh": <str>,
    "topic": <str>,
    "grammar_focus": <str>,
    "new_word_count": <int>,
    "learning_goals": [<str>, ...]
  },
  ...
]
</OutputFormat>
"""

MARKET_ANALYSIS_SYSTEM_PROMPT = """\
<Role>
You are a market analyst specializing in the Chinese language education industry. \
You understand the global demand for Chinese learning materials, especially for \
English-speaking professionals.
</Role>

<OutputFormat>
Return ONLY a valid JSON object (no markdown, no explanation):
{
  "score": <int 1-10>,
  "reasoning": <str>,
  "target_audience": <str>,
  "competition": <str>,
  "suggestions": [<str>, ...]
}
</OutputFormat>
"""

MATERIAL_SYSTEM_PROMPT = """\
<Role>
You are a Chinese language teaching material analyzer. You extract structured \
educational content from raw text — identifying vocabulary, dialogue snippets, \
grammar patterns, and cultural topics suitable for a Chinese textbook.
</Role>

<OutputFormat>
Return ONLY a valid JSON object (no markdown, no explanation):
{
  "vocabulary": [
    {"chinese": <str>, "pinyin": <str>, "word_by_word": <str>, "english": <str>, "pos": <str>},
    ...
  ],
  "dialogue_snippets": [
    {"context": <str>, "lines": [<str>, ...]},
    ...
  ],
  "grammar_patterns": [
    {"pattern": <str>, "explanation": <str>, "examples": [<str>, ...]},
    ...
  ],
  "cultural_topics": [
    {"topic": <str>, "notes": <str>},
    ...
  ]
}
</OutputFormat>
"""


# ---------------------------------------------------------------------------
# AIEngine
# ---------------------------------------------------------------------------

class AIEngine:
    """AI-powered content generation engine for Z Turns Chinese textbooks."""

    def __init__(self):
        self.hsk_levels = HSK_LEVELS
        self.consistency_rules = CONSISTENCY_RULES
        self.lesson_structure = LESSON_STRUCTURE
        self._api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    def is_available(self) -> bool:
        """Check if Claude API key is configured."""
        return bool(self._api_key)

    def parse_mission_brief(self, brief: str) -> dict:
        """Parse a mission brief to extract theme and parameters."""
        prompt = f'Extract the course theme from this brief. Return only JSON: {{"theme": "..."}}\nBrief: {brief}'
        try:
            result = _call_anthropic("", prompt, max_tokens=200)
            return json.loads(result)
        except Exception:
            return {"theme": brief[:50]}

    # ------------------------------------------------------------------
    # a) generate_lesson
    # ------------------------------------------------------------------
    def generate_lesson(
        self,
        topic: str,
        hsk_level: int,
        lesson_num: int,
        previous_vocab: Optional[list] = None,
        context_notes: str = "",
    ) -> dict:
        """Generate a complete lesson dict matching lesson_data.py format.

        Args:
            topic: lesson topic, e.g. "ordering food at restaurant"
            hsk_level: 1, 2, or 3
            lesson_num: sequential lesson number
            previous_vocab: list of previously taught words for continuity
            context_notes: optional extra context from GetNotes or user

        Returns:
            A lesson dict whose structure matches LESSONS in lesson_data.py.
        """
        if hsk_level not in self.hsk_levels:
            raise ValueError(f"hsk_level must be 1, 2, or 3. Got {hsk_level}")

        level_info = self.hsk_levels[hsk_level]
        previous_vocab = previous_vocab or []

        prev_vocab_str = ""
        if previous_vocab:
            prev_vocab_str = (
                "Previously taught vocabulary (reuse at least 30% in dialogue):\n"
                + "\n".join(f"- {w}" for w in previous_vocab[:60])
            )

        context_str = ""
        if context_notes:
            context_str = f"\nAdditional context / teaching notes:\n{context_notes}\n"

        is_review = (lesson_num % self.lesson_structure["review_every_n"] == 0)
        max_new = (
            self.consistency_rules["max_new_words_review"]
            if is_review
            else level_info["max_new_words"]
        )

        user_prompt = f"""\
Generate lesson {lesson_num} for HSK Level {hsk_level} ({level_info['cefr']}).
Book: {level_info['book']}
Topic: {topic}
{"This is a REVIEW lesson — max 2 new words, focus on consolidating previous vocabulary." if is_review else ""}

Requirements:
- Max {max_new} new words (HSK {hsk_level} level only)
- {self.lesson_structure['core_dialogue_rounds']}-8 lines per dialogue
- 1-2 dialogues
- 1-2 grammar points with English-speaker-friendly explanations
- 1 culture note about modern China (2026)
- 4 exercises (mix of fill_blank, translate, word_by_word, match, reorder)
- 3 learning goals
- Characters to use: {', '.join(self.consistency_rules['fixed_character_names'])}

{prev_vocab_str}
{context_str}

Return the lesson as a single JSON object matching the schema in your instructions."""

        try:
            raw = _call_anthropic(LESSON_SYSTEM_PROMPT, user_prompt, max_tokens=8192)
            lesson = _extract_json(raw)
            lesson = self._normalize_lesson(lesson)
            return lesson
        except EnvironmentError:
            raise
        except Exception as e:
            logger.error("Failed to generate lesson: %s", e, exc_info=True)
            return {
                "error": True,
                "message": f"AI generation failed: {e}",
                "suggestion": (
                    "Check your ANTHROPIC_API_KEY and network connection. "
                    "You can also use pre-built lessons from lesson_data.py."
                ),
            }

    # ------------------------------------------------------------------
    # b) generate_course_plan
    # ------------------------------------------------------------------
    def generate_course_plan(
        self, theme: str, num_lessons: int, hsk_level: int
    ) -> list:
        """Generate a progressive course plan.

        Args:
            theme: e.g. "Pinyin Learning", "Business Chinese"
            num_lessons: total number of lessons
            hsk_level: 1, 2, or 3

        Returns:
            List of lesson plan dicts with keys: lesson_num, title_en,
            title_zh, topic, grammar_focus, new_word_count, learning_goals.
        """
        if hsk_level not in self.hsk_levels:
            raise ValueError(f"hsk_level must be 1, 2, or 3. Got {hsk_level}")

        level_info = self.hsk_levels[hsk_level]
        review_every = self.lesson_structure["review_every_n"]

        user_prompt = f"""\
Design a {num_lessons}-lesson course plan.
Theme: {theme}
HSK Level: {hsk_level} ({level_info['cefr']})
Book: {level_info['book']}
Total available vocabulary: {level_info['total_vocab']} words

Rules:
- Insert a review lesson every {review_every} lessons (max 2 new words in review lessons)
- Regular lessons: {level_info['new_words_per_lesson']}-{level_info['max_new_words']} new words
- Ensure vocabulary spiraling: later lessons reuse earlier vocabulary
- Progressive difficulty: grammar builds on previous lessons
- Practical, real-life topics suitable for English-speaking professionals
- Characters: {', '.join(self.consistency_rules['fixed_character_names'])}

Return a JSON array of {num_lessons} lesson plan objects."""

        try:
            raw = _call_anthropic(COURSE_PLAN_SYSTEM_PROMPT, user_prompt, max_tokens=4096)
            plans = _extract_json(raw)
            if not isinstance(plans, list):
                raise ValueError("Expected a JSON array of lesson plans")
            return plans
        except EnvironmentError:
            raise
        except Exception as e:
            logger.error("Failed to generate course plan: %s", e, exc_info=True)
            return []

    # ------------------------------------------------------------------
    # c) analyze_market_demand
    # ------------------------------------------------------------------
    def analyze_market_demand(self, theme: str) -> dict:
        """Analyze market demand for a course theme.

        Returns:
            Dict with keys: score (1-10), reasoning, target_audience,
            competition, suggestions.
        """
        user_prompt = f"""\
Analyze the market demand for the following Chinese language course theme:
"{theme}"

Consider:
1. Global demand for this type of Chinese learning content (2026 market)
2. Target audience size and willingness to pay
3. Competition from existing products (apps, textbooks, online courses)
4. Unique selling points of a "Four-Layer Translation" approach
5. Specific suggestions to improve marketability

Return a JSON object with your analysis."""

        try:
            raw = _call_anthropic(MARKET_ANALYSIS_SYSTEM_PROMPT, user_prompt, max_tokens=2048)
            return _extract_json(raw)
        except EnvironmentError:
            raise
        except Exception as e:
            logger.error("Failed to analyze market demand: %s", e, exc_info=True)
            return {
                "error": True,
                "message": f"AI analysis failed: {e}",
                "score": 0,
                "reasoning": "Unable to complete analysis.",
                "target_audience": "Unknown",
                "competition": "Unknown",
                "suggestions": ["Retry when API is available."],
            }

    # ------------------------------------------------------------------
    # d) process_raw_material
    # ------------------------------------------------------------------
    def process_raw_material(
        self, raw_text: str, source_type: str = "notes"
    ) -> dict:
        """Extract structured teaching material from raw text.

        Args:
            raw_text: raw teaching notes, article text, etc.
            source_type: "notes", "article", "transcript", or "url_content"

        Returns:
            Dict with keys: vocabulary, dialogue_snippets, grammar_patterns,
            cultural_topics.
        """
        user_prompt = f"""\
Process the following raw {source_type} material and extract structured content \
suitable for a Chinese language textbook using the Four-Layer Translation method.

Source type: {source_type}

--- RAW MATERIAL START ---
{raw_text}
--- RAW MATERIAL END ---

Extract:
1. Key vocabulary (with pinyin, word-by-word English, natural English, part of speech)
2. Potential dialogue snippets or conversational patterns
3. Grammar patterns with explanations for English speakers
4. Cultural topics relevant to modern China (2026)

Return a JSON object with your extraction."""

        try:
            raw = _call_anthropic(MATERIAL_SYSTEM_PROMPT, user_prompt, max_tokens=4096)
            return _extract_json(raw)
        except EnvironmentError:
            raise
        except Exception as e:
            logger.error("Failed to process raw material: %s", e, exc_info=True)
            return {
                "error": True,
                "message": f"AI processing failed: {e}",
                "vocabulary": [],
                "dialogue_snippets": [],
                "grammar_patterns": [],
                "cultural_topics": [],
            }

    # ------------------------------------------------------------------
    # e) improve_lesson
    # ------------------------------------------------------------------
    def improve_lesson(self, lesson_dict: dict, feedback: str = "") -> dict:
        """Improve an existing lesson based on feedback.

        Args:
            lesson_dict: existing lesson in lesson_data.py format
            feedback: optional human feedback for improvement direction

        Returns:
            Improved lesson dict in the same format.
        """
        feedback_section = ""
        if feedback:
            feedback_section = f"\nUser feedback to address:\n{feedback}\n"

        user_prompt = f"""\
Improve the following Chinese lesson. Keep the same id, title, and HSK level, \
but enhance the quality of dialogues, grammar explanations, culture notes, \
and exercises.

Current lesson:
{json.dumps(lesson_dict, ensure_ascii=False, indent=2)}

{feedback_section}

Improvement guidelines:
- Make dialogues more natural and practical
- Improve grammar explanations for English speakers (add more comparisons)
- Update culture notes to reflect modern China (2026)
- Make exercises more varied and engaging
- Ensure all 4 translation layers are accurate
- Keep word-by-word English strictly in Chinese word order

Return the improved lesson as a single JSON object matching the schema."""

        try:
            raw = _call_anthropic(LESSON_SYSTEM_PROMPT, user_prompt, max_tokens=8192)
            lesson = _extract_json(raw)
            lesson = self._normalize_lesson(lesson)
            return lesson
        except EnvironmentError:
            raise
        except Exception as e:
            logger.error("Failed to improve lesson: %s", e, exc_info=True)
            return {
                "error": True,
                "message": f"AI improvement failed: {e}",
                "suggestion": "The original lesson was preserved. Retry when API is available.",
                "original_lesson": lesson_dict,
            }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _normalize_lesson(self, lesson: dict) -> dict:
        """Convert JSON lists to tuples where lesson_data.py uses tuples,
        and ensure all expected keys exist."""
        # new_words: list of tuples (chinese, pinyin, wbw, english, pos)
        if "new_words" in lesson:
            lesson["new_words"] = [
                tuple(w) if isinstance(w, list) else w for w in lesson["new_words"]
            ]

        # dialogues -> lines: list of tuples
        if "dialogues" in lesson:
            for dialogue in lesson["dialogues"]:
                if "lines" in dialogue:
                    dialogue["lines"] = [
                        tuple(line) if isinstance(line, list) else line
                        for line in dialogue["lines"]
                    ]

        # exercises -> match pairs: list of tuples
        if "exercises" in lesson:
            for ex in lesson["exercises"]:
                if ex.get("type") == "match" and "pairs" in ex:
                    ex["pairs"] = [
                        tuple(p) if isinstance(p, list) else p for p in ex["pairs"]
                    ]

        # review_words: list of tuples
        if "review_words" in lesson:
            lesson["review_words"] = [
                tuple(w) if isinstance(w, list) else w for w in lesson["review_words"]
            ]

        # Ensure required keys have defaults
        lesson.setdefault("id", 0)
        lesson.setdefault("title_en", "")
        lesson.setdefault("title_zh", "")
        lesson.setdefault("book", "Book 1")
        lesson.setdefault("hsk_level", 1)
        lesson.setdefault("learning_goals", [])
        lesson.setdefault("new_words", [])
        lesson.setdefault("dialogues", [])
        lesson.setdefault("grammar_points", [])
        lesson.setdefault("culture_note", {"title": "", "text": ""})
        lesson.setdefault("exercises", [])

        return lesson
