"""
Z Turns Chinese AutoBuilder - Configuration
综合6大AI方案的最佳实践配置

Methodology and book series definitions live in methodology.py.
Book template system (validation, schema) lives in book_template.py.
"""

# Lazy imports — avoids circular import at module load time
def get_methodology():
    """Return the full METHODOLOGY dict from methodology.py."""
    from methodology import METHODOLOGY
    return METHODOLOGY

def get_book_series():
    """Return the BOOK_SERIES dict from methodology.py."""
    from methodology import BOOK_SERIES
    return BOOK_SERIES

# ============================================================
# HSK 3.0 (2026) Vocabulary Control
# Source: Claude方案 + Kimi方案 科目一分级新词上限表
# ============================================================
HSK_LEVELS = {
    1: {"total_vocab": 300, "new_words_per_lesson": 8, "max_new_words": 10, "cefr": "A1", "book": "Book 1: 零基础入门"},
    2: {"total_vocab": 497, "new_words_per_lesson": 10, "max_new_words": 12, "cefr": "A2", "book": "Book 2: 日常会话"},
    3: {"total_vocab": 988, "new_words_per_lesson": 12, "max_new_words": 15, "cefr": "B1", "book": "Book 3: 职场中文"},
}

# ============================================================
# Lesson Structure Template (from Claude + Minimax方案)
# ============================================================
LESSON_STRUCTURE = {
    "warmup_rounds": 2,       # 热身复习对话轮数
    "core_dialogue_rounds": 6, # 核心对话轮数
    "extension_rounds": 2,     # 扩展变体轮数
    "culture_notes": 1,        # 文化小贴士数量
    "exercises": 4,            # 练习题数量
    "review_every_n": 5,       # 每N课设1个复习课
}

# ============================================================
# Consistency Rules (from Claude方案 一致性规则引擎)
# ============================================================
CONSISTENCY_RULES = {
    "min_vocab_reuse_ratio": 0.30,    # 每课必须复用前课 ≥30% 已学词汇
    "max_new_words_regular": 10,       # 常规课新词上限
    "max_new_words_review": 2,         # 复习课新词上限
    "grammar_must_increase": True,     # 语法难度单调递增
    "no_duplicate_culture": True,      # 文化主题不重复
    "fixed_character_names": ["小明", "小红", "Tony老师", "David", "Mary"],
}

# ============================================================
# Four-Layer Translation (from Claude方案 四层对照翻译引擎)
# ============================================================
FOUR_LAYERS = {
    "layer_1": "Chinese Characters (汉字)",
    "layer_2": "Pinyin (拼音, with tones)",
    "layer_3": "Word-by-Word English (逐词直译, Chinese word order)",
    "layer_4": "Natural English (自然英译)",
}

# ============================================================
# Privacy Filter Rules (from Grok + Claude方案)
# ============================================================
PRIVACY_PATTERNS = {
    "person_names": r"\b[A-Z][a-z]{1,15}\s[A-Z][a-z]{1,15}(?:\s[A-Z][a-z]{1,15})?\b",
    "phone_numbers": r"\b\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b",
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "addresses": r"\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Blvd|Dr|Rd|Lane|Way)\b",
}

# Words that look like names but are common in educational content
PRIVACY_WHITELIST = {
    "My Family", "Your Name", "What Time", "How Much", "Where Is",
    "Going Shopping", "Phone Call", "Daily Routine", "Final Review",
    "Review One", "Review Two", "Word Order", "Two Ways", "Three Ways",
    "One Time", "Question Word", "Question Patterns", "Measure Word",
    "Time Expressions", "Cash Is", "Xiao Ming", "Xiao Hong",
    "Tony Teacher", "Adjective Predicates", "Weather Small",
    "Popular Hobbies", "Grammar Summary", "Culture Note",
    "Possession Particle", "Morning Routines", "Getting Around",
    "Gaode Maps", "Baidu Maps", "Place Names", "How Many", "How Old",
    "Little Ming", "Little Hong", "Spring Festival", "Beijing Time",
    "During Spring", "During Spring Festival", "Phone Culture", "Kung Pao",
    "Good Morning", "Good Night", "Thank You", "Excuse Me",
    "No Problem", "Not Bad", "Very Good", "Too Expensive",
}

PRIVACY_REPLACEMENTS = {
    "person": "[Student A]",
    "phone": "[REMOVED]",
    "email": "[REMOVED]",
    "address": "[a city]",
    "company": "[an organization]",
    "family": "[family member]",
}

# ============================================================
# PDF Styling (from Claude方案 排版原型)
# ============================================================
PDF_STYLE = {
    "page_size": "A4",
    "margin_left": 25,
    "margin_right": 25,
    "margin_top": 25,
    "margin_bottom": 25,
    "title_font_size": 22,
    "subtitle_font_size": 14,
    "heading_font_size": 16,
    "body_font_size": 12,
    "chinese_font_size": 18,
    "pinyin_font_size": 10,
    "literal_font_size": 11,
    "natural_font_size": 12,
    "line_spacing": 1.5,
    "colors": {
        "primary": (0, 85, 204),        # #0055CC blue
        "secondary": (85, 85, 85),       # #555555 gray
        "accent": (220, 50, 50),         # Red for important
        "background": (245, 245, 245),   # Light gray blocks
        "text": (30, 30, 30),            # Near black
        "pinyin": (100, 100, 100),       # Gray
        "literal": (0, 85, 204),         # Blue
        "culture": (0, 128, 0),          # Green
        "badge_bg": (0, 85, 204),        # HSK badge background
        "badge_text": (255, 255, 255),   # Badge text (white)
        "row_alt": (245, 245, 250),      # Alternating table row
        "row_even": (255, 255, 255),     # Even table row
        "grammar_bg": (240, 245, 255),   # Grammar box background
        "culture_bg": (240, 255, 240),   # Culture note background
        "white": (255, 255, 255),        # Pure white
    }
}

# ============================================================
# Book 1 Curriculum Map (from Claude方案 知识图谱)
# ============================================================
BOOK1_LESSONS = [
    {"id": 1, "title_en": "Hello!", "title_zh": "你好！", "topic": "greetings",
     "grammar": "SVO word order", "new_words": 8, "review_from": []},
    {"id": 2, "title_en": "What's Your Name?", "title_zh": "你叫什么名字？", "topic": "introductions",
     "grammar": "Question word 什么", "new_words": 8, "review_from": [1]},
    {"id": 3, "title_en": "My Family", "title_zh": "我的家人", "topic": "family",
     "grammar": "的 (possession)", "new_words": 8, "review_from": [1, 2]},
    {"id": 4, "title_en": "Numbers", "title_zh": "数字", "topic": "numbers",
     "grammar": "Numbers + measure words", "new_words": 8, "review_from": [1, 2, 3]},
    {"id": 5, "title_en": "Review 1", "title_zh": "复习一", "topic": "review",
     "grammar": "Review L1-4", "new_words": 2, "review_from": [1, 2, 3, 4]},
    {"id": 6, "title_en": "What Time Is It?", "title_zh": "几点了？", "topic": "time",
     "grammar": "几 + measure word", "new_words": 8, "review_from": [4]},
    {"id": 7, "title_en": "My Daily Routine", "title_zh": "我的一天", "topic": "daily_routine",
     "grammar": "Time expressions", "new_words": 8, "review_from": [6]},
    {"id": 8, "title_en": "At the Restaurant", "title_zh": "在餐厅", "topic": "restaurant",
     "grammar": "想 + Verb", "new_words": 8, "review_from": [4, 6]},
    {"id": 9, "title_en": "Going Shopping", "title_zh": "去超市", "topic": "shopping",
     "grammar": "多少钱", "new_words": 8, "review_from": [8]},
    {"id": 10, "title_en": "Review 2", "title_zh": "复习二", "topic": "review",
     "grammar": "Review L6-9", "new_words": 2, "review_from": [6, 7, 8, 9]},
    {"id": 11, "title_en": "How's the Weather?", "title_zh": "天气怎么样？", "topic": "weather",
     "grammar": "Adjective predicates", "new_words": 8, "review_from": [7]},
    {"id": 12, "title_en": "I Like...", "title_zh": "我喜欢……", "topic": "hobbies",
     "grammar": "喜欢 + V/N", "new_words": 8, "review_from": [8, 9]},
    {"id": 13, "title_en": "Where Is It?", "title_zh": "在哪里？", "topic": "directions",
     "grammar": "在 + location", "new_words": 8, "review_from": [9]},
    {"id": 14, "title_en": "Making a Phone Call", "title_zh": "打电话", "topic": "phone",
     "grammar": "能/可以", "new_words": 8, "review_from": [2]},
    {"id": 15, "title_en": "Final Review", "title_zh": "总复习", "topic": "review",
     "grammar": "Full book review", "new_words": 0, "review_from": list(range(1, 15))},
]
