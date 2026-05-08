"""
Z Turns Chinese - Teaching Methodology Configuration
教学方法论配置

Encodes design principles from two reference works:
- "1000 Hours" (2024) by Li Xiaolai — neuroscience-backed density training
- "Everyone Can Use English" (2010) by Li Xiaolai — use-first philosophy

These principles drive content tone, pacing, structure, and quality standards
across all books in the Z Turns Chinese series.
"""

# ============================================================
# Core Methodology
# ============================================================

METHODOLOGY = {
    # ----------------------------------------------------------
    # Core Philosophy
    # From "Everyone Can Use English": use, don't just study.
    # From "1000 Hours": density and brain training over passive exposure.
    # ----------------------------------------------------------
    "core_philosophy": {
        "primary": "Use Chinese from day one — production before perfection.",
        "brain_training": (
            "Learning Chinese is the best brain exercise. "
            "Every tonal distinction, every character stroke is a workout "
            "for the neural pathways that handle pattern recognition."
        ),
        "use_not_study": (
            "The problem is never 'I can't say it.' "
            "The problem is 'I have nothing to say.' "
            "Solve content first; fluency follows automatically."
        ),
        "belief_engineering": (
            "Destroy limiting beliefs before teaching methods. "
            "Students fail because they believe they will fail — not because "
            "Chinese is hard."
        ),
        "no_shortcuts": (
            "There are no shortcuts. Sustained effort compounds. "
            "Three hours a day for a year beats ten hours a day for a week."
        ),
        "ai_native": (
            "Write what you want to say → AI translates → Generate audio → Shadow. "
            "Modern learners have tools no previous generation had. Use them."
        ),
    },

    # ----------------------------------------------------------
    # Daily Practice Protocol (7 Steps)
    # Source: "1000 Hours" Chapter 3 — daily loop design
    # ----------------------------------------------------------
    "daily_protocol": [
        {
            "step": 1,
            "name": "Review Yesterday",
            "zh": "复习昨天",
            "duration_min": 10,
            "description": (
                "Read aloud everything from yesterday's lesson. "
                "No new material until yesterday is solid."
            ),
        },
        {
            "step": 2,
            "name": "Slow Listen",
            "zh": "慢速听",
            "duration_min": 15,
            "description": (
                "Listen to today's dialogue at 0.75x speed. "
                "Focus on tones, not meaning. Let the sound patterns land first."
            ),
        },
        {
            "step": 3,
            "name": "Segment Shadow",
            "zh": "分段跟读",
            "duration_min": 20,
            "description": (
                "Shadow sentence by sentence with the transcript. "
                "Pause after each sentence. Reproduce exactly — tone, rhythm, breath."
            ),
        },
        {
            "step": 4,
            "name": "Full Shadow",
            "zh": "全文跟读",
            "duration_min": 15,
            "description": (
                "Shadow the full dialogue without pausing. "
                "Keep pace with the native speaker even if you miss words."
            ),
        },
        {
            "step": 5,
            "name": "Memorize",
            "zh": "背诵",
            "duration_min": 20,
            "description": (
                "Close the book. Reproduce the dialogue from memory. "
                "Write it out. Speak it out. This is the hard part — do it anyway."
            ),
        },
        {
            "step": 6,
            "name": "Relax",
            "zh": "放松",
            "duration_min": 10,
            "description": (
                "Rest. Do something completely unrelated. "
                "The brain consolidates during rest, not during study."
            ),
        },
        {
            "step": 7,
            "name": "Daily Review",
            "zh": "每日回顾",
            "duration_min": 10,
            "description": (
                "Before sleep: read through all vocabulary from today and yesterday. "
                "No pressure — just let the eyes pass over the characters."
            ),
        },
    ],

    # ----------------------------------------------------------
    # Standard Chapter Structure
    # Every chapter in every book follows this exact sequence.
    # ----------------------------------------------------------
    "chapter_structure": [
        {
            "section": 1,
            "name": "Scene Setter",
            "zh": "场景导入",
            "purpose": "Hook the learner with a real situation they will face.",
            "word_count_target": 80,
        },
        {
            "section": 2,
            "name": "Key Vocabulary",
            "zh": "核心词汇",
            "purpose": "New words with four-layer format. Max 10 words per lesson.",
            "word_count_target": None,  # Determined by lesson plan
        },
        {
            "section": 3,
            "name": "Dialogues",
            "zh": "对话练习",
            "purpose": "2-3 dialogues showing vocab in natural context.",
            "word_count_target": None,
        },
        {
            "section": 4,
            "name": "Grammar Spotlight",
            "zh": "语法要点",
            "purpose": "One grammar point per lesson, explained for English speakers.",
            "word_count_target": 150,
        },
        {
            "section": 5,
            "name": "Culture Note",
            "zh": "文化小贴士",
            "purpose": "One cultural insight that makes the lesson memorable.",
            "word_count_target": 100,
        },
        {
            "section": 6,
            "name": "Practice",
            "zh": "练习",
            "purpose": "4 exercises: fill-in, matching, translation, production.",
            "word_count_target": None,
        },
        {
            "section": 7,
            "name": "Daily Challenge",
            "zh": "每日挑战",
            "purpose": "One real-world task using today's language.",
            "word_count_target": 50,
        },
        {
            "section": 8,
            "name": "Answer Key",
            "zh": "答案",
            "purpose": "Answers to all exercises with brief explanations.",
            "word_count_target": None,
        },
    ],

    # ----------------------------------------------------------
    # Four-Layer Translation Format
    # Source: Z Turns original design — core differentiator
    # ----------------------------------------------------------
    "four_layer_format": {
        "layer_1": {
            "name": "Chinese Characters",
            "zh": "汉字",
            "rule": "Standard simplified Chinese. No shortcuts, no approximations.",
        },
        "layer_2": {
            "name": "Pinyin",
            "zh": "拼音",
            "rule": (
                "Always use tone marks (ā á ǎ à). "
                "NEVER use tone numbers (a1 a2 a3 a4). "
                "Syllables separated by spaces. Proper capitalization for names."
            ),
        },
        "layer_3": {
            "name": "Word-by-Word",
            "zh": "逐词直译",
            "rule": (
                "Translate each Chinese word literally, preserving Chinese word order. "
                "This reveals grammatical structure to English speakers. "
                "Use hyphens for multi-morpheme words: 谢谢 → thank-thank."
            ),
        },
        "layer_4": {
            "name": "Natural English",
            "zh": "自然英语",
            "rule": (
                "Idiomatic English translation. "
                "What a native English speaker would actually say. "
                "Use quotation marks for direct speech."
            ),
        },
    },

    # ----------------------------------------------------------
    # Tone and Writing Rules
    # Source: "Everyone Can Use English" — provocative, personal, direct
    # ----------------------------------------------------------
    "tone_rules": {
        "voice": "Personal, direct, slightly provocative. Like a smart friend, not a textbook.",
        "belief_engineering": (
            "Open each chapter by dismantling one false belief about Chinese learning. "
            "Example: 'You think tones are hard. They're not. "
            "English has tones too — you just call them intonation.'"
        ),
        "anecdotal": (
            "Use specific anecdotes, not vague encouragement. "
            "Bad: 'Chinese tones are important.' "
            "Good: 'My first week in Beijing, I asked for a horse instead of a beer "
            "because I got the tone wrong. This is exactly why we drill tones first.'"
        ),
        "motivational_hook": (
            "Every chapter must have one sentence that makes the reader think: "
            "'Oh, I can actually do this.'"
        ),
        "no_padding": (
            "Cut any sentence that does not teach something or shift the reader's belief. "
            "Density over length."
        ),
        "script_preparation": (
            "Before speaking exercises, give learners a script. "
            "Per Li Xiaolai: the problem is having nothing to say, not inability to say it. "
            "Provide the content; let them focus on production."
        ),
    },

    # ----------------------------------------------------------
    # Content Progression Levels
    # ----------------------------------------------------------
    "content_levels": {
        "beginner": {
            "description": "Zero prior Chinese. Complete English scaffolding required.",
            "four_layer": "All four layers on every line.",
            "grammar_depth": "One point per lesson, maximum two sentences of explanation.",
            "cultural_load": "Light. One memorable fact per lesson.",
            "vocab_per_lesson": 8,
            "sentence_length_max": 6,  # words
        },
        "elementary": {
            "description": "Can greet, introduce, order food. Needs expansion.",
            "four_layer": "All four layers, but layer 3 (word-by-word) can be abbreviated.",
            "grammar_depth": "One to two points per lesson.",
            "cultural_load": "Moderate. Can introduce social conventions.",
            "vocab_per_lesson": 10,
            "sentence_length_max": 10,
        },
        "intermediate": {
            "description": "Handles daily situations. Needs topic fluency.",
            "four_layer": "Layers 1 and 4 required. Layers 2 and 3 on new vocabulary only.",
            "grammar_depth": "Two points per lesson, with contrastive analysis.",
            "cultural_load": "Rich. Deep dives into modern Chinese society.",
            "vocab_per_lesson": 12,
            "sentence_length_max": 15,
        },
    },

    # ----------------------------------------------------------
    # Quality Standards
    # ----------------------------------------------------------
    "quality_standards": {
        "pinyin_accuracy": "100% — all tone marks correct, no tone numbers.",
        "vocabulary_control": "No word above the target HSK level without explicit gloss.",
        "cultural_relevance": "All examples must reflect modern China (post-2020).",
        "four_layer_alignment": (
            "Layers 1/2/3/4 must be strictly aligned word-by-word. "
            "Misalignment is a critical error."
        ),
        "dialogue_naturalness": (
            "Every dialogue line must pass the 'would a real person say this?' test."
        ),
        "exercise_variety": "Minimum 4 exercise types per chapter (no two identical formats).",
        "answer_completeness": "Every exercise must have a full answer key with brief explanation.",
        "density_minimum": (
            "Each lesson must be completable in one 3-hour study block. "
            "If it takes less than 90 minutes of active study, add content."
        ),
    },
}


# ============================================================
# Book Series Definition
# ============================================================

BOOK_SERIES = {
    "book1": {
        "name": "Z Turns Chinese: From Zero to Your First Conversation",
        "subtitle": "A Beginner's Guide with Four-Layer Word-by-Word Translation",
        "zh_name": "从零开始的第一次对话",
        "level": "beginner",
        "hsk_target": 1,
        "cefr": "A1",
        "chapters": 15,
        "vocab_target": 120,
        "audience": "Complete beginners. No Chinese background required.",
        "promise": "After Book 1 you can handle greetings, introductions, food, shopping, and directions.",
        "methodology_focus": [
            "Pronunciation-first approach",
            "Full four-layer scaffolding on every sentence",
            "Belief engineering: you CAN learn tones",
        ],
        "units": [
            {"name": "Unit 1: Getting Started", "zh": "入门篇", "chapters": "1-5"},
            {"name": "Unit 2: Daily Life", "zh": "日常生活", "chapters": "6-10"},
            {"name": "Unit 3: Expanding Horizons", "zh": "拓展篇", "chapters": "11-15"},
        ],
    },
    "book2": {
        "name": "Z Turns Chinese: The Complete Guide to Conversational Chinese",
        "subtitle": "25 Real-World Lessons for Travel, Daily Life & Business",
        "zh_name": "完整会话中文指南",
        "level": "beginner-intermediate",
        "hsk_target": 3,
        "cefr": "A1-B1",
        "chapters": 25,
        "vocab_target": 1050,
        "audience": "Zero to intermediate. Complete self-study course.",
        "promise": "After Book 2 you can navigate travel, daily life, business, and modern China with confidence.",
        "methodology_focus": [
            "Script preparation before speaking",
            "Read-aloud as primary exercise",
            "Brain training through daily protocol",
        ],
        "units": [
            {"name": "Part 0: Before You Begin", "zh": "开始之前", "chapters": "0.1-0.3"},
            {"name": "Part 1: Sound Foundation", "zh": "语音基础", "chapters": "1.1-1.5"},
            {"name": "Part 2: First Steps", "zh": "第一步", "chapters": "1-5"},
            {"name": "Part 3: Daily Life", "zh": "日常生活", "chapters": "6-10"},
            {"name": "Part 4: Travel & Adventure", "zh": "旅行探索", "chapters": "11-15"},
            {"name": "Part 5: Business Chinese", "zh": "商务中文", "chapters": "16-20"},
            {"name": "Part 6: Living in China", "zh": "融入中国", "chapters": "21-25"},
        ],
    },
    "book3": {
        "name": "Z Turns Chinese: Real Lessons from Real Classrooms",
        "subtitle": "Authentic Chinese from 200+ Hours of Teaching Recordings",
        "zh_name": "真实课堂的真实课程",
        "level": "beginner-intermediate",
        "hsk_target": 3,
        "cefr": "A1-B1",
        "chapters": 25,
        "vocab_target": 300,
        "audience": "Learners who want authentic, conversation-based content.",
        "promise": "After Book 3 you understand how China really works — culture, business, society, and modern life.",
        "methodology_focus": [
            "Content over form: real conversations first",
            "AI-native workflow: real recordings → structured content",
            "Cultural immersion through authentic material",
        ],
        "getnotes_topic_id": "qY2WB1E0",
        "units": [
            {"name": "Part 1: Real-Life Basics", "zh": "日常实用", "chapters": "1-5"},
            {"name": "Part 2: Travel Stories", "zh": "旅行故事", "chapters": "6-10"},
            {"name": "Part 3: Culture Unlocked", "zh": "文化解锁", "chapters": "11-15"},
            {"name": "Part 4: Business & Modern China", "zh": "商务与现代中国", "chapters": "16-20"},
            {"name": "Part 5: Going Deeper", "zh": "深度中国", "chapters": "21-25"},
        ],
    },
    "book4": {
        "name": "Z Turns Chinese: Survival Chinese",
        "subtitle": "50 Essential Phrases for Your First Week in China",
        "zh_name": "生存中文",
        "level": "zero-prerequisite",
        "hsk_target": 0,
        "cefr": "Pre-A1",
        "chapters": 20,
        "vocab_target": 300,
        "audience": "Travelers, business visitors, expats in first week. Zero Chinese required.",
        "promise": "You can survive your first week in China — eat, travel, pay, and get help.",
        "methodology_focus": [
            "Situation-based, not grammar-based",
            "Show-and-point phrase format",
            "Zero prerequisite — use immediately",
        ],
        "units": [
            {"name": "Section 1: Absolute Essentials", "zh": "到达必备", "scenarios": "1-4"},
            {"name": "Section 2: Eating & Drinking", "zh": "吃喝生存", "scenarios": "5-8"},
            {"name": "Section 3: Getting Around", "zh": "出行生存", "scenarios": "9-12"},
            {"name": "Section 4: Money & Shopping", "zh": "花钱生存", "scenarios": "13-15"},
            {"name": "Section 5: Emergency & Practical", "zh": "紧急实用", "scenarios": "16-20"},
        ],
    },
    "book5": {
        "name": "Z Turns Chinese: Business Chinese That Actually Works",
        "subtitle": "Real Workplace Conversations for Expats, Entrepreneurs & Global Professionals",
        "zh_name": "真正管用的商务中文",
        "level": "intermediate",
        "hsk_target": 3,
        "cefr": "B1-B2",
        "chapters": 25,
        "vocab_target": 350,
        "audience": "Expats, entrepreneurs, and professionals working in or with China.",
        "promise": "After Book 5 you can navigate any professional situation in China — from job interviews to investor pitches.",
        "methodology_focus": [
            "Immediately actionable professional language",
            "Business culture decoded alongside vocabulary",
            "Real workplace scenarios, not textbook fiction",
        ],
        "units": [
            {"name": "Part 1: Your First 30 Days", "zh": "入职第一个月", "chapters": "1-5"},
            {"name": "Part 2: Daily Work Life", "zh": "日常工作", "chapters": "6-10"},
            {"name": "Part 3: Business Relationships", "zh": "商务关系", "chapters": "11-15"},
            {"name": "Part 4: Deals & Money", "zh": "交易与财务", "chapters": "16-20"},
            {"name": "Part 5: Career Growth & Beyond", "zh": "职业发展", "chapters": "21-25"},
        ],
    },
}


# ============================================================
# Prompt Engineering Templates
# (Used by ai_engine.py to inject methodology into generation)
# ============================================================

SYSTEM_PROMPT_PREAMBLE = """
You are generating content for the Z Turns Chinese textbook series.

METHODOLOGY PRINCIPLES (non-negotiable):
1. Four-layer format: every sentence needs Chinese | Pinyin (tone marks, NEVER numbers) | Word-by-word | Natural English
2. Tone: personal, direct, slightly provocative — like a smart friend, not a textbook
3. Belief engineering: open with something that dismantles a false belief about Chinese
4. Content first: give students a script before asking them to produce
5. Density: every sentence must teach or shift belief — no padding
6. Cultural relevance: all examples post-2020, modern China
7. Pinyin: ALWAYS use ā á ǎ à — NEVER a1 a2 a3 a4

QUALITY GATE: Before finalizing any content, check:
- All pinyin has tone marks
- Four layers are word-by-word aligned
- Dialogue sounds natural (would a real person say this?)
- There is at least one belief-engineering sentence per chapter
- Answer key is complete
"""

DAILY_PROTOCOL_REMINDER = """
Remind students at the end of each chapter:
"Follow the 7-step daily protocol: Review → Slow Listen → Segment Shadow →
Full Shadow → Memorize → Rest → Daily Review.
Minimum 90 minutes of active study per chapter. No shortcuts."
"""
