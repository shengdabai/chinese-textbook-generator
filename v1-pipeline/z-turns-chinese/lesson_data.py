"""
Pre-built lesson content data for demonstration and offline generation.
Each lesson contains structured content following the four-layer translation format.
Source: Synthesized from Claude方案 PDF排版原型 + Gemini方案 Few-Shot examples
"""

LESSONS = {
    # ==================================================================
    # Lesson 1: Hello! / 你好！
    # ==================================================================
    1: {
        "id": 1,
        "title_en": "Hello!",
        "title_zh": "你好！",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Greet people in Chinese",
            "Say 'thank you' and 'you're welcome'",
            "Understand basic Chinese word order (SVO)",
        ],
        "new_words": [
            ("你", "nǐ", "you", "you", "pron"),
            ("好", "hǎo", "good", "good/well", "adj"),
            ("我", "wǒ", "I", "I/me", "pron"),
            ("是", "shì", "am", "to be", "v"),
            ("谢谢", "xièxie", "thank-thank", "thank you", "v"),
            ("不客气", "bú kèqi", "not polite", "you're welcome", "phrase"),
            ("老师", "lǎoshī", "old master", "teacher", "n"),
            ("再见", "zàijiàn", "again see", "goodbye", "phrase"),
        ],
        "review_words": [],
        "dialogues": [
            {
                "title": "Meeting for the first time",
                "lines": [
                    ("Tony老师", "你好！", "nǐ hǎo!", "you good!", "Hello!"),
                    ("David", "你好！", "nǐ hǎo!", "you good!", "Hello!"),
                    ("Tony老师", "我是老师。", "wǒ shì lǎoshī.", "I am old-master.", "I am the teacher."),
                    ("David", "谢谢老师！", "xièxie lǎoshī!", "thank-thank old-master!", "Thank you, teacher!"),
                    ("Tony老师", "不客气！", "bú kèqi!", "not polite!", "You're welcome!"),
                    ("David", "再见！", "zàijiàn!", "again see!", "Goodbye!"),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "Chinese Word Order: SVO",
                "explanation": (
                    "Chinese follows Subject-Verb-Object order, just like English!\n\n"
                    "我 是 老师 → I am teacher → 'I am a teacher'\n"
                    "你 好 → you good → 'You are good' (= Hello!)\n\n"
                    "Notice: No articles ('a', 'the') in Chinese! '我是老师' means "
                    "'I am a teacher' — the 'a' is simply not there."
                ),
            }
        ],
        "culture_note": {
            "title": "The Magic of 你好",
            "text": (
                "你好 (nǐ hǎo) literally means 'you good' — it's like saying "
                "'May you be well!' Chinese greetings are wishes, not questions. "
                "Unlike 'How are you?' in English, 你好 doesn't expect an answer "
                "about your health. Just say 你好 back!\n\n"
                "Fun fact: In modern China, close friends rarely say 你好 — it "
                "sounds too formal. They might just say 嗨 (hāi, from 'hi') or "
                "directly start talking!"
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "___好！(Hello!)",
                "answer": "你",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'Thank you, teacher!'",
                "answer": "谢谢老师！",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "我是老师。",
                "answer": "I am old-master.",
            },
            {
                "type": "match",
                "instruction": "Match Chinese to English:",
                "pairs": [("再见", "Goodbye"), ("谢谢", "Thank you"), ("不客气", "You're welcome"), ("老师", "Teacher")],
                "answer": "再见—Goodbye, 谢谢—Thank you, 不客气—You're welcome, 老师—Teacher",
            },
        ],
    },

    # ==================================================================
    # Lesson 2: What's Your Name? / 你叫什么名字？
    # ==================================================================
    2: {
        "id": 2,
        "title_en": "What's Your Name?",
        "title_zh": "你叫什么名字？",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Ask and answer 'What is your name?'",
            "Use the question word 什么 (shénme)",
            "Introduce yourself and others",
            "Understand the difference between 叫 and 是",
        ],
        "new_words": [
            ("叫", "jiào", "call", "to be called/named", "v"),
            ("什么", "shénme", "what", "what", "pron"),
            ("名字", "míngzi", "name-character", "name", "n"),
            ("他", "tā", "he", "he/him", "pron"),
            ("她", "tā", "she", "she/her", "pron"),
            ("同学", "tóngxué", "same-study", "classmate", "n"),
            ("请问", "qǐngwèn", "please-ask", "may I ask", "v"),
            ("很", "hěn", "very", "very", "adv"),
        ],
        "review_words": [
            ("你", "nǐ", "you", "you"),
            ("好", "hǎo", "good", "good/well"),
            ("我", "wǒ", "I", "I/me"),
            ("是", "shì", "am", "to be"),
            ("老师", "lǎoshī", "old master", "teacher"),
        ],
        "dialogues": [
            {
                "title": "In the classroom",
                "lines": [
                    ("Tony老师", "你好！你叫什么名字？", "nǐ hǎo! nǐ jiào shénme míngzi?", "you good! you call what name-character?", "Hello! What is your name?"),
                    ("David", "我叫David。", "wǒ jiào David.", "I call David.", "My name is David."),
                    ("Tony老师", "很好！她叫什么名字？", "hěn hǎo! tā jiào shénme míngzi?", "very good! she call what name-character?", "Very good! What is her name?"),
                    ("David", "她叫Mary。", "tā jiào Mary.", "she call Mary.", "Her name is Mary."),
                    ("Tony老师", "他是同学吗？", "tā shì tóngxué ma?", "he am same-study (question)?", "Is he a classmate?"),
                    ("David", "是，他是同学。", "shì, tā shì tóngxué.", "am, he am same-study.", "Yes, he is a classmate."),
                    ("Mary", "请问，你是老师吗？", "qǐngwèn, nǐ shì lǎoshī ma?", "please-ask, you am old-master (question)?", "May I ask, are you the teacher?"),
                    ("Tony老师", "是，我是老师。我叫Tony。", "shì, wǒ shì lǎoshī. wǒ jiào Tony.", "am, I am old-master. I call Tony.", "Yes, I am the teacher. My name is Tony."),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "Question Word 什么 (shénme) = 'what'",
                "explanation": (
                    "In Chinese, the question word stays where the answer would be:\n\n"
                    "你 叫 什么 名字？ → you call what name?\n"
                    "我 叫 David。 → I call David.\n\n"
                    "Notice: The word order does NOT change for questions! "
                    "English moves 'what' to the front: 'What is your name?' "
                    "Chinese keeps it in place: 你叫【什么】名字？"
                ),
            },
            {
                "title": "叫 vs 是 — Two Ways to Identify",
                "explanation": (
                    "叫 (jiào) = 'to be called' — used for names:\n"
                    "我叫David → I am-called David\n\n"
                    "是 (shì) = 'to be' — used for identity/role:\n"
                    "我是老师 → I am teacher\n"
                    "他是同学 → he is classmate\n\n"
                    "Remember: 叫 for names, 是 for identities!"
                ),
            },
        ],
        "culture_note": {
            "title": "Chinese Names: Family First!",
            "text": (
                "In Chinese, the family name (姓 xìng) always comes first. "
                "For example, a person named 王明 (Wáng Míng) has the family "
                "name 王 and the given name 明.\n\n"
                "In 2026 China, young people often use English names at work "
                "or with foreign friends. It's very common to hear '我叫Tony' "
                "in international settings. But with Chinese friends, they "
                "use their Chinese names — or nicknames like 小明 (Little Ming)."
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "你___什么名字？(What is your name?)",
                "answer": "叫",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'What is his name?'",
                "answer": "他叫什么名字？",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "她叫Mary。",
                "answer": "she call Mary.",
            },
            {
                "type": "match",
                "instruction": "Match Chinese to English:",
                "pairs": [("叫", "to be called"), ("什么", "what"), ("名字", "name"), ("同学", "classmate")],
                "answer": "叫—to be called, 什么—what, 名字—name, 同学—classmate",
            },
        ],
    },

    # ==================================================================
    # Lesson 3: My Family / 我的家人
    # ==================================================================
    3: {
        "id": 3,
        "title_en": "My Family",
        "title_zh": "我的家人",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Talk about family members",
            "Use 的 (de) to show possession",
            "Describe your family in simple sentences",
            "Count family members",
        ],
        "new_words": [
            ("家", "jiā", "home", "home/family", "n"),
            ("爸爸", "bàba", "dad-dad", "father", "n"),
            ("妈妈", "māma", "mom-mom", "mother", "n"),
            ("的", "de", "(possessive)", "possessive particle", "part"),
            ("有", "yǒu", "have", "to have", "v"),
            ("没有", "méiyǒu", "not-have", "don't have", "v"),
            ("和", "hé", "and", "and", "conj"),
            ("人", "rén", "person", "person/people", "n"),
        ],
        "review_words": [
            ("我", "wǒ", "I", "I/me"),
            ("他", "tā", "he", "he/him"),
            ("她", "tā", "she", "she/her"),
            ("叫", "jiào", "call", "to be called"),
            ("是", "shì", "am", "to be"),
            ("很", "hěn", "very", "very"),
            ("好", "hǎo", "good", "good"),
        ],
        "dialogues": [
            {
                "title": "Talking about family",
                "lines": [
                    ("小红", "David，你的家有几个人？", "David, nǐ de jiā yǒu jǐ ge rén?", "David, you (possessive) home have how-many (measure) person?", "David, how many people are in your family?"),
                    ("David", "我的家有三个人。", "wǒ de jiā yǒu sān ge rén.", "I (possessive) home have three (measure) person.", "There are three people in my family."),
                    ("小红", "他们是谁？", "tāmen shì shéi?", "they am who?", "Who are they?"),
                    ("David", "爸爸、妈妈和我。", "bàba, māma hé wǒ.", "dad-dad, mom-mom and I.", "My dad, my mom, and me."),
                    ("小红", "你有没有同学？", "nǐ yǒu méiyǒu tóngxué?", "you have not-have same-study?", "Do you have classmates?"),
                    ("David", "有！Mary是我的同学。", "yǒu! Mary shì wǒ de tóngxué.", "have! Mary am I (possessive) same-study.", "Yes! Mary is my classmate."),
                    ("小红", "她好吗？", "tā hǎo ma?", "she good (question)?", "Is she well?"),
                    ("David", "她很好，谢谢！", "tā hěn hǎo, xièxie!", "she very good, thank-thank!", "She's very well, thank you!"),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "的 (de) — The Possession Particle",
                "explanation": (
                    "的 (de) works like 's in English — but comes AFTER the owner:\n\n"
                    "我 的 家 → I (possessive) home → 'my home'\n"
                    "他 的 名字 → he (possessive) name → 'his name'\n"
                    "Mary 的 老师 → Mary (possessive) teacher → 'Mary's teacher'\n\n"
                    "Pattern: Owner + 的 + Thing\n"
                    "Note: 的 is often dropped with close relationships: "
                    "我妈妈 (my mom) sounds more natural than 我的妈妈."
                ),
            },
            {
                "title": "有 (yǒu) — 'to have' and Existence",
                "explanation": (
                    "有 means 'to have'. Its negative is 没有 (not 不有!):\n\n"
                    "我 有 同学 → I have classmate → 'I have classmates'\n"
                    "我 没有 → I not-have → 'I don't have'\n\n"
                    "To ask yes/no: 你有没有...？ (you have-not-have...?)\n"
                    "This is the A-not-A pattern — very common in Chinese!"
                ),
            },
        ],
        "culture_note": {
            "title": "Chinese Family Values",
            "text": (
                "Family (家 jiā) is the center of Chinese culture. The word "
                "家 itself appears in many important words: 国家 (guójiā, country), "
                "大家 (dàjiā, everyone), 家人 (jiārén, family members).\n\n"
                "In 2026, many young Chinese adults live in big cities away from "
                "their parents. Video calls on WeChat are how families stay "
                "connected. During Spring Festival (春节), millions of people "
                "travel home — it's the world's largest annual migration!"
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "我___家有三个人。(My family has three people.)",
                "answer": "的",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'She is my mom.'",
                "answer": "她是我的妈妈。",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "你的家有几个人？",
                "answer": "you (possessive) home have how-many (measure) person?",
            },
            {
                "type": "match",
                "instruction": "Match Chinese to English:",
                "pairs": [("爸爸", "father"), ("妈妈", "mother"), ("家", "home/family"), ("的", "possessive particle")],
                "answer": "爸爸—father, 妈妈—mother, 家—home/family, 的—possessive particle",
            },
        ],
    },

    # ==================================================================
    # Lesson 4: Numbers / 数字
    # ==================================================================
    4: {
        "id": 4,
        "title_en": "Numbers",
        "title_zh": "数字",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Count from 1 to 100 in Chinese",
            "Use the general measure word 个 (ge)",
            "Ask 'how many' with 几 (jǐ)",
            "Give your phone number in Chinese",
        ],
        "new_words": [
            ("一", "yī", "one", "one", "num"),
            ("二", "èr", "two", "two", "num"),
            ("三", "sān", "three", "three", "num"),
            ("十", "shí", "ten", "ten", "num"),
            ("个", "ge", "(measure)", "general measure word", "mw"),
            ("几", "jǐ", "how-many", "how many", "pron"),
            ("多", "duō", "many", "many/much", "adj"),
            ("岁", "suì", "year-of-age", "years old", "mw"),
        ],
        "review_words": [
            ("你", "nǐ", "you", "you"),
            ("我", "wǒ", "I", "I/me"),
            ("有", "yǒu", "have", "to have"),
            ("家", "jiā", "home", "home/family"),
            ("人", "rén", "person", "person"),
            ("的", "de", "(possessive)", "possessive particle"),
        ],
        "dialogues": [
            {
                "title": "How old are you?",
                "lines": [
                    ("Tony老师", "David，你几岁？", "David, nǐ jǐ suì?", "David, you how-many year-of-age?", "David, how old are you?"),
                    ("David", "我二十一岁。", "wǒ èrshíyī suì.", "I two-ten-one year-of-age.", "I'm twenty-one years old."),
                    ("Tony老师", "你的家有几个人？", "nǐ de jiā yǒu jǐ ge rén?", "you (possessive) home have how-many (measure) person?", "How many people are in your family?"),
                    ("David", "三个人。爸爸、妈妈和我。", "sān ge rén. bàba, māma hé wǒ.", "three (measure) person. dad-dad, mom-mom and I.", "Three people. Dad, mom, and me."),
                    ("Mary", "老师，你有几个同学？", "lǎoshī, nǐ yǒu jǐ ge tóngxué?", "old-master, you have how-many (measure) same-study?", "Teacher, how many students do you have?"),
                    ("Tony老师", "我有十二个同学。", "wǒ yǒu shí'èr ge tóngxué.", "I have ten-two (measure) same-study.", "I have twelve students."),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "Numbers + Measure Word 个",
                "explanation": (
                    "In Chinese, you MUST put a measure word between a number and a noun:\n\n"
                    "三 个 人 → three (measure) person → 'three people'\n"
                    "一 个 老师 → one (measure) teacher → 'one teacher'\n"
                    "几 个 同学 → how-many (measure) classmate → 'how many classmates'\n\n"
                    "个 (ge) is the most common measure word — use it when you're unsure!"
                ),
            },
            {
                "title": "Chinese Numbers 1-100",
                "explanation": (
                    "Chinese numbers are beautifully logical:\n\n"
                    "1-10: 一 二 三 四 五 六 七 八 九 十\n"
                    "11 = 十一 (ten-one)\n"
                    "20 = 二十 (two-ten)\n"
                    "21 = 二十一 (two-ten-one)\n"
                    "99 = 九十九 (nine-ten-nine)\n\n"
                    "It's like math: 二十一 = 2×10 + 1 = 21!"
                ),
            },
        ],
        "culture_note": {
            "title": "Lucky and Unlucky Numbers",
            "text": (
                "In Chinese culture, numbers carry meaning! 八 (bā, 8) sounds "
                "like 发 (fā, to get rich), so 8 is very lucky. Phone numbers "
                "and license plates with 8 are expensive!\n\n"
                "四 (sì, 4) sounds like 死 (sǐ, death), so 4 is avoided. "
                "Many buildings in China skip the 4th floor! In 2026, even "
                "digital payments prefer amounts with 8 — sending 88 yuan "
                "in a WeChat red envelope (红包) is a popular lucky gift."
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "我有三___同学。(I have three classmates.)",
                "answer": "个",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'How old are you?'",
                "answer": "你几岁？",
            },
            {
                "type": "multiple_choice",
                "instruction": "Choose the correct answer:",
                "question": "二十五 means:",
                "options": ["15", "25", "52", "50"],
                "answer": "25",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "你的家有几个人？",
                "answer": "you (possessive) home have how-many (measure) person?",
            },
        ],
    },

    # ==================================================================
    # Lesson 5: Review 1 / 复习一 (Reviews L1-4)
    # ==================================================================
    5: {
        "id": 5,
        "title_en": "Review 1",
        "title_zh": "复习一",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Review greetings, introductions, family, and numbers (L1-4)",
            "Practice combining vocabulary from all four lessons",
            "Strengthen SVO word order and 的 possession",
        ],
        "new_words": [
            ("吗", "ma", "(question)", "question particle", "part"),
            ("也", "yě", "also", "also/too", "adv"),
        ],
        "review_words": [
            ("你好", "nǐ hǎo", "you good", "hello"),
            ("我", "wǒ", "I", "I/me"),
            ("是", "shì", "am", "to be"),
            ("叫", "jiào", "call", "to be called"),
            ("什么", "shénme", "what", "what"),
            ("名字", "míngzi", "name-character", "name"),
            ("的", "de", "(possessive)", "possessive particle"),
            ("家", "jiā", "home", "home/family"),
            ("爸爸", "bàba", "dad-dad", "father"),
            ("妈妈", "māma", "mom-mom", "mother"),
            ("有", "yǒu", "have", "to have"),
            ("几", "jǐ", "how-many", "how many"),
            ("个", "ge", "(measure)", "measure word"),
            ("岁", "suì", "year-of-age", "years old"),
        ],
        "dialogues": [
            {
                "title": "A party — meeting new friends",
                "lines": [
                    ("小明", "你好！我叫小明。你叫什么名字？", "nǐ hǎo! wǒ jiào Xiǎo Míng. nǐ jiào shénme míngzi?", "you good! I call Little-Bright. you call what name-character?", "Hello! My name is Xiao Ming. What's your name?"),
                    ("David", "我叫David。你好！", "wǒ jiào David. nǐ hǎo!", "I call David. you good!", "My name is David. Hello!"),
                    ("小明", "她叫什么名字？", "tā jiào shénme míngzi?", "she call what name-character?", "What is her name?"),
                    ("David", "她叫Mary。她也是同学。", "tā jiào Mary. tā yě shì tóngxué.", "she call Mary. she also am same-study.", "Her name is Mary. She is also a classmate."),
                    ("小明", "你的家有几个人？", "nǐ de jiā yǒu jǐ ge rén?", "you (possessive) home have how-many (measure) person?", "How many people are in your family?"),
                    ("David", "三个人。爸爸、妈妈和我。你呢？", "sān ge rén. bàba, māma hé wǒ. nǐ ne?", "three (measure) person. dad-dad, mom-mom and I. you (question)?", "Three people. Dad, mom, and me. And you?"),
                    ("小明", "我的家也有三个人！", "wǒ de jiā yě yǒu sān ge rén!", "I (possessive) home also have three (measure) person!", "My family also has three people!"),
                    ("David", "很好！再见！", "hěn hǎo! zàijiàn!", "very good! again see!", "Great! Goodbye!"),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "Review: Question Patterns",
                "explanation": (
                    "We've learned several ways to ask questions in Chinese:\n\n"
                    "1. 吗 at the end: 你好吗？ (Are you well?)\n"
                    "2. 什么 in place: 你叫什么名字？ (What's your name?)\n"
                    "3. 几 for 'how many': 你几岁？ (How old are you?)\n"
                    "4. A-not-A: 你有没有？ (Do you have or not?)\n\n"
                    "Remember: Chinese word order stays the same in questions!"
                ),
            },
        ],
        "culture_note": {
            "title": "呢 (ne) — The Conversation Bounce-Back",
            "text": (
                "你呢？(nǐ ne?) means 'And you?' or 'What about you?' "
                "It's a super useful shortcut! Instead of repeating the "
                "whole question, just add 呢:\n\n"
                "A: 我很好。你呢？ (I'm good. And you?)\n"
                "B: 我也很好！ (I'm also good!)\n\n"
                "This is very natural in everyday Chinese conversation!"
            ),
        },
        "exercises": [
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'My name is David. I am 21 years old.'",
                "answer": "我叫David。我二十一岁。",
            },
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "她___是同学。(She is also a classmate.)",
                "answer": "也",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "我的家也有三个人。",
                "answer": "I (possessive) home also have three (measure) person.",
            },
            {
                "type": "match",
                "instruction": "Match Chinese to English:",
                "pairs": [("你叫什么名字？", "What's your name?"), ("你几岁？", "How old are you?"), ("你的家有几个人？", "How many in your family?"), ("再见！", "Goodbye!")],
                "answer": "你叫什么名字？—What's your name?, 你几岁？—How old are you?, 你的家有几个人？—How many in your family?, 再见！—Goodbye!",
            },
        ],
    },

    # ==================================================================
    # Lesson 6: What Time Is It? / 几点了？
    # ==================================================================
    6: {
        "id": 6,
        "title_en": "What Time Is It?",
        "title_zh": "几点了？",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Tell time in Chinese",
            "Use 几 (jǐ) with 点 (diǎn) to ask 'what time'",
            "Understand 了 (le) for change of state",
            "Talk about daily schedules",
        ],
        "new_words": [
            ("点", "diǎn", "dot", "o'clock", "mw"),
            ("半", "bàn", "half", "half (past)", "num"),
            ("分", "fēn", "divide", "minute", "mw"),
            ("现在", "xiànzài", "now-at", "now", "n"),
            ("了", "le", "(change)", "change-of-state particle", "part"),
            ("上午", "shàngwǔ", "upper-noon", "morning/AM", "n"),
            ("下午", "xiàwǔ", "lower-noon", "afternoon/PM", "n"),
            ("去", "qù", "go", "to go", "v"),
        ],
        "review_words": [
            ("几", "jǐ", "how-many", "how many"),
            ("一", "yī", "one", "one"),
            ("二", "èr", "two", "two"),
            ("三", "sān", "three", "three"),
            ("十", "shí", "ten", "ten"),
            ("我", "wǒ", "I", "I/me"),
        ],
        "dialogues": [
            {
                "title": "What time is it?",
                "lines": [
                    ("David", "请问，现在几点了？", "qǐngwèn, xiànzài jǐ diǎn le?", "please-ask, now-at how-many dot (change)?", "Excuse me, what time is it now?"),
                    ("小明", "现在上午十点半。", "xiànzài shàngwǔ shí diǎn bàn.", "now-at upper-noon ten dot half.", "It's 10:30 AM now."),
                    ("David", "谢谢！你几点去？", "xièxie! nǐ jǐ diǎn qù?", "thank-thank! you how-many dot go?", "Thanks! What time are you going?"),
                    ("小明", "我下午两点去。", "wǒ xiàwǔ liǎng diǎn qù.", "I lower-noon two dot go.", "I'm going at 2 PM."),
                    ("David", "好，我也下午两点去！", "hǎo, wǒ yě xiàwǔ liǎng diǎn qù!", "good, I also lower-noon two dot go!", "Great, I'll also go at 2 PM!"),
                    ("小明", "好！再见！", "hǎo! zàijiàn!", "good! again see!", "Good! See you!"),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "几点 — Asking 'What Time'",
                "explanation": (
                    "几 (how many) + 点 (o'clock) = 'what time':\n\n"
                    "现在 几 点 了？ → now how-many dot (change)? → 'What time is it?'\n"
                    "现在 三 点。 → now three dot. → 'It's 3 o'clock.'\n"
                    "现在 三 点 半。 → now three dot half. → 'It's 3:30.'\n"
                    "现在 三 点 十五 分。 → now three dot fifteen minute. → 'It's 3:15.'\n\n"
                    "Time words come BEFORE the verb: 我三点去 (I at-3 go)."
                ),
            },
        ],
        "culture_note": {
            "title": "Time in China — One Time Zone!",
            "text": (
                "China is huge, but the entire country uses one time zone: "
                "Beijing Time (北京时间 Běijīng shíjiān). That means when it's "
                "8 AM in Beijing, it's also officially 8 AM in western China "
                "— even though the sun hasn't risen yet!\n\n"
                "In 2026, Chinese people are very punctual for business. "
                "Being 5 minutes early is considered 'on time'. For social "
                "events, being a little late is more acceptable."
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "现在___点了？(What time is it?)",
                "answer": "几",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'It is now 3:30 PM.'",
                "answer": "现在下午三点半。",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "我下午两点去。",
                "answer": "I lower-noon two dot go.",
            },
            {
                "type": "multiple_choice",
                "instruction": "Choose the correct answer:",
                "question": "上午十点半 means:",
                "options": ["10:30 PM", "10:30 AM", "10:50 AM", "Half past 11 AM"],
                "answer": "10:30 AM",
            },
        ],
    },

    # ==================================================================
    # Lesson 7: My Daily Routine / 我的一天
    # ==================================================================
    7: {
        "id": 7,
        "title_en": "My Daily Routine",
        "title_zh": "我的一天",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Describe your daily routine in Chinese",
            "Use time expressions before verbs",
            "Learn common daily activity words",
            "Understand the time-first word order",
        ],
        "new_words": [
            ("起床", "qǐchuáng", "rise-bed", "to get up", "v"),
            ("吃", "chī", "eat", "to eat", "v"),
            ("喝", "hē", "drink", "to drink", "v"),
            ("睡觉", "shuìjiào", "sleep-sleep", "to sleep", "v"),
            ("看", "kàn", "look", "to look/watch/read", "v"),
            ("书", "shū", "book", "book", "n"),
            ("天", "tiān", "day", "day", "n"),
            ("早上", "zǎoshang", "early-up", "morning (early)", "n"),
        ],
        "review_words": [
            ("点", "diǎn", "dot", "o'clock"),
            ("半", "bàn", "half", "half past"),
            ("上午", "shàngwǔ", "upper-noon", "morning/AM"),
            ("下午", "xiàwǔ", "lower-noon", "afternoon/PM"),
            ("去", "qù", "go", "to go"),
            ("现在", "xiànzài", "now-at", "now"),
        ],
        "dialogues": [
            {
                "title": "My day",
                "lines": [
                    ("Tony老师", "David，你早上几点起床？", "David, nǐ zǎoshang jǐ diǎn qǐchuáng?", "David, you early-up how-many dot rise-bed?", "David, what time do you get up in the morning?"),
                    ("David", "我早上七点起床。", "wǒ zǎoshang qī diǎn qǐchuáng.", "I early-up seven dot rise-bed.", "I get up at 7 AM."),
                    ("Tony老师", "你早上吃什么？", "nǐ zǎoshang chī shénme?", "you early-up eat what?", "What do you eat in the morning?"),
                    ("David", "我吃面包，喝一杯茶。", "wǒ chī miànbāo, hē yī bēi chá.", "I eat bread, drink one cup tea.", "I eat bread and drink a cup of tea."),
                    ("Tony老师", "你下午做什么？", "nǐ xiàwǔ zuò shénme?", "you lower-noon do what?", "What do you do in the afternoon?"),
                    ("David", "我下午看书。", "wǒ xiàwǔ kàn shū.", "I lower-noon look book.", "I read books in the afternoon."),
                    ("Tony老师", "你几点睡觉？", "nǐ jǐ diǎn shuìjiào?", "you how-many dot sleep-sleep?", "What time do you go to sleep?"),
                    ("David", "我十一点睡觉。", "wǒ shíyī diǎn shuìjiào.", "I ten-one dot sleep-sleep.", "I go to sleep at 11 o'clock."),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "Time Expressions Come Before the Verb",
                "explanation": (
                    "In Chinese, time words go BEFORE the verb (not after like English):\n\n"
                    "我 早上 七点 起床。\n"
                    "→ I morning seven-o'clock get-up.\n"
                    "→ 'I get up at 7 in the morning.'\n\n"
                    "Pattern: Subject + Time + Verb\n"
                    "我 下午 看 书 → I afternoon read book → 'I read in the afternoon'\n"
                    "他 十点 睡觉 → he ten-o'clock sleep → 'He sleeps at 10'"
                ),
            },
        ],
        "culture_note": {
            "title": "Morning Routines in China",
            "text": (
                "In China, many people start the day with a warm breakfast — "
                "often 豆浆 (dòujiāng, soy milk) and 油条 (yóutiáo, fried "
                "dough sticks). In parks, you'll see people doing 太极拳 "
                "(tàijíquán, tai chi) or square dancing (广场舞 guǎngchǎngwǔ).\n\n"
                "In 2026, many young people buy breakfast from apps like "
                "Meituan (美团) and have it delivered to their door. The old "
                "and the new live side by side in modern China!"
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "我早上七点___。(I get up at 7 AM.)",
                "answer": "起床",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'I read books in the afternoon.'",
                "answer": "我下午看书。",
            },
            {
                "type": "reorder",
                "instruction": "Put in correct order:",
                "question": "吃 / 早上 / 什么 / 你",
                "answer": "你早上吃什么？",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "他十一点睡觉。",
                "answer": "he ten-one dot sleep-sleep.",
            },
        ],
    },

    # ==================================================================
    # Lesson 8: At the Restaurant / 在餐厅
    # ==================================================================
    8: {
        "id": 8,
        "title_en": "At the Restaurant",
        "title_zh": "在餐厅",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Order food in a Chinese restaurant",
            "Use measure words (量词) for food items",
            "Express preferences with 想 (xiǎng)",
        ],
        "new_words": [
            ("菜单", "càidān", "dish-list", "menu", "n"),
            ("点菜", "diǎncài", "select-dish", "to order food", "v"),
            ("饺子", "jiǎozi", "dumpling", "dumplings", "n"),
            ("碗", "wǎn", "bowl", "bowl (measure word)", "mw"),
            ("杯", "bēi", "cup", "cup (measure word)", "mw"),
            ("好吃", "hǎochī", "good-eat", "delicious", "adj"),
            ("服务员", "fúwùyuán", "serve-person", "waiter/waitress", "n"),
            ("买单", "mǎidān", "buy-bill", "to pay the bill", "v"),
        ],
        "dialogues": [
            {
                "title": "Ordering food",
                "lines": [
                    ("小明", "你想吃什么？", "nǐ xiǎng chī shénme?", "you want eat what?", "What would you like to eat?"),
                    ("David", "我想吃饺子。", "wǒ xiǎng chī jiǎozi.", "I want eat dumpling.", "I'd like to have dumplings."),
                    ("小明", "好！你想喝什么？", "hǎo! nǐ xiǎng hē shénme?", "good! you want drink what?", "Great! What would you like to drink?"),
                    ("David", "一杯茶，谢谢。", "yī bēi chá, xièxie.", "one cup tea, thank-you.", "A cup of tea, please."),
                    ("小明", "服务员！点菜！", "fúwùyuán! diǎncài!", "serve-person! select-dish!", "Waiter! We'd like to order!"),
                    ("服务员", "好的，请看菜单。", "hǎo de, qǐng kàn càidān.", "good (particle), please look dish-list.", "Sure, please look at the menu."),
                    ("David", "这个饺子好吃吗？", "zhège jiǎozi hǎochī ma?", "this dumpling good-eat (question)?", "Are these dumplings delicious?"),
                    ("服务员", "很好吃！", "hěn hǎochī!", "very good-eat!", "Very delicious!"),
                ],
            },
            {
                "title": "Paying the bill",
                "lines": [
                    ("David", "服务员，买单！", "fúwùyuán, mǎidān!", "serve-person, buy-bill!", "Waiter, the check please!"),
                    ("服务员", "好的，一共三十五块。", "hǎo de, yígòng sānshíwǔ kuài.", "good (particle), altogether thirty-five piece.", "Sure, that's 35 yuan total."),
                    ("David", "好，谢谢！", "hǎo, xièxie!", "good, thank-thank!", "Okay, thank you!"),
                    ("服务员", "不客气，再见！", "bú kèqi, zàijiàn!", "not polite, again see!", "You're welcome, goodbye!"),
                ],
            },
        ],
        "grammar_points": [
            {
                "title": "想 + Verb = 'want to' / 'would like to'",
                "explanation": (
                    "In Chinese, 想 (xiǎng) is placed directly before the verb:\n\n"
                    "我 想 吃 → I want eat → 'I want to eat'\n"
                    "你 想 喝 → you want drink → 'you want to drink'\n"
                    "他 想 去 → he want go → 'he wants to go'\n\n"
                    "Notice: No 'to' between 想 and the verb! Unlike English "
                    "'want TO eat', Chinese is simply 想吃."
                ),
            },
            {
                "title": "Measure Words: 碗 and 杯",
                "explanation": (
                    "Chinese requires a 'measure word' between a number and a noun:\n\n"
                    "一 碗 米饭 → one bowl rice → 'a bowl of rice'\n"
                    "一 杯 茶 → one cup tea → 'a cup of tea'\n"
                    "两 个 饺子 → two piece dumpling → 'two dumplings'\n\n"
                    "Think of measure words as 'counters' — every noun needs one!"
                ),
            },
        ],
        "culture_note": {
            "title": "Calling the Waiter in China",
            "text": (
                "In Chinese restaurants, you call the waiter by saying "
                "'服务员！' (fúwùyuán!) — literally 'service-person!' "
                "This is perfectly polite and is the standard way to get "
                "attention.\n\n"
                "In modern China, many restaurants use QR codes on the table. "
                "You scan with WeChat (微信) to see the menu and order — "
                "no waiter needed! The phrase '扫码点餐' (sǎo mǎ diǎn cān) "
                "means 'scan code order food' — very common in 2026 China."
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "我___吃饺子。(I want to eat dumplings)",
                "answer": "想",
            },
            {
                "type": "reorder",
                "instruction": "Put in correct order:",
                "question": "茶 / 想 / 我 / 喝 / 一杯",
                "answer": "我想喝一杯茶。",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'What would you like to drink?'",
                "answer": "你想喝什么？",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English for:",
                "question": "我想吃面条。",
                "answer": "I want eat flour-strip.",
            },
        ],
        "review_words": [
            ("你", "nǐ", "you", "you"),
            ("什么", "shénme", "what", "what"),
            ("谢谢", "xièxie", "thank-thank", "thank you"),
            ("不客气", "bú kèqi", "not polite", "you're welcome"),
            ("再见", "zàijiàn", "again see", "goodbye"),
            ("一", "yī", "one", "one"),
        ],
    },

    # ==================================================================
    # Lesson 9: Going Shopping / 去超市
    # ==================================================================
    9: {
        "id": 9,
        "title_en": "Going Shopping",
        "title_zh": "去超市",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Ask and answer prices with 多少钱",
            "Use basic money expressions (块/元)",
            "Shop for common items in Chinese",
            "Bargain politely at a market",
        ],
        "new_words": [
            ("多少", "duōshao", "many-few", "how much/how many", "pron"),
            ("钱", "qián", "money", "money", "n"),
            ("块", "kuài", "piece", "yuan (spoken)", "mw"),
            ("买", "mǎi", "buy", "to buy", "v"),
            ("太", "tài", "too", "too (excessive)", "adv"),
            ("贵", "guì", "expensive", "expensive", "adj"),
            ("这个", "zhège", "this-piece", "this one", "pron"),
            ("那个", "nàge", "that-piece", "that one", "pron"),
        ],
        "review_words": [
            ("想", "xiǎng", "want", "to want"),
            ("好", "hǎo", "good", "good"),
            ("谢谢", "xièxie", "thank-thank", "thank you"),
            ("几", "jǐ", "how-many", "how many"),
            ("个", "ge", "(measure)", "measure word"),
            ("一", "yī", "one", "one"),
        ],
        "dialogues": [
            {
                "title": "At the supermarket",
                "lines": [
                    ("David", "请问，这个多少钱？", "qǐngwèn, zhège duōshao qián?", "please-ask, this-piece many-few money?", "Excuse me, how much is this?"),
                    ("小红", "这个十五块。", "zhège shíwǔ kuài.", "this-piece ten-five piece.", "This one is 15 yuan."),
                    ("David", "那个呢？", "nàge ne?", "that-piece (question)?", "What about that one?"),
                    ("小红", "那个二十块。", "nàge èrshí kuài.", "that-piece two-ten piece.", "That one is 20 yuan."),
                    ("David", "太贵了！", "tài guì le!", "too expensive (change)!", "Too expensive!"),
                    ("小红", "好，十五块，你买吗？", "hǎo, shíwǔ kuài, nǐ mǎi ma?", "good, ten-five piece, you buy (question)?", "OK, 15 yuan, will you buy it?"),
                    ("David", "好，我买这个。", "hǎo, wǒ mǎi zhège.", "good, I buy this-piece.", "OK, I'll buy this one."),
                    ("小红", "谢谢！", "xièxie!", "thank-thank!", "Thank you!"),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "多少钱 — Asking 'How Much Money'",
                "explanation": (
                    "多少 (duōshao) = 'how much/how many' (for larger numbers):\n\n"
                    "这个 多少 钱？ → this many-few money? → 'How much is this?'\n"
                    "那个 二十 块。 → that twenty piece. → 'That's 20 yuan.'\n\n"
                    "几 vs 多少:\n"
                    "几 = 'how many' (expect answer under 10)\n"
                    "多少 = 'how many/much' (any number, or for prices)"
                ),
            },
            {
                "title": "太 + Adjective + 了 = 'too...'",
                "explanation": (
                    "太...了 wraps around the adjective to mean 'too...':\n\n"
                    "太 贵 了 → too expensive (particle) → 'too expensive!'\n"
                    "太 好 了 → too good (particle) → 'too good!' / 'Great!'\n\n"
                    "Notice: 太好了 is actually a positive expression — "
                    "'That's wonderful!'"
                ),
            },
        ],
        "culture_note": {
            "title": "Paying in China — Cash Is Rare!",
            "text": (
                "In 2026 China, almost nobody uses cash anymore. People pay "
                "for everything with their phones — using WeChat Pay (微信支付) "
                "or Alipay (支付宝). Even street food vendors and taxi drivers "
                "accept mobile payments.\n\n"
                "When shopping, you might hear '扫一扫' (sǎo yī sǎo, scan it) "
                "instead of '多少钱.' The vendor shows a QR code, you scan it, "
                "enter the amount, and done! But knowing 多少钱 is still "
                "essential for asking prices."
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "这个___钱？(How much is this?)",
                "answer": "多少",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'That one is too expensive!'",
                "answer": "那个太贵了！",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "我想买这个。",
                "answer": "I want buy this-piece.",
            },
            {
                "type": "multiple_choice",
                "instruction": "Choose the correct answer:",
                "question": "三十五块 means:",
                "options": ["3.5 yuan", "35 yuan", "305 yuan", "53 yuan"],
                "answer": "35 yuan",
            },
        ],
    },

    # ==================================================================
    # Lesson 10: Review 2 / 复习二 (Reviews L6-9)
    # ==================================================================
    10: {
        "id": 10,
        "title_en": "Review 2",
        "title_zh": "复习二",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Review time, daily routine, restaurant, and shopping (L6-9)",
            "Practice combining time expressions with actions",
            "Strengthen measure words and price expressions",
        ],
        "new_words": [
            ("还是", "háishi", "still-am", "or (in questions)", "conj"),
            ("都", "dōu", "all", "all/both", "adv"),
        ],
        "review_words": [
            ("现在", "xiànzài", "now-at", "now"),
            ("几点", "jǐ diǎn", "how-many dot", "what time"),
            ("起床", "qǐchuáng", "rise-bed", "to get up"),
            ("吃", "chī", "eat", "to eat"),
            ("喝", "hē", "drink", "to drink"),
            ("想", "xiǎng", "want", "to want"),
            ("多少钱", "duōshao qián", "many-few money", "how much"),
            ("买", "mǎi", "buy", "to buy"),
            ("太", "tài", "too", "too"),
            ("贵", "guì", "expensive", "expensive"),
            ("好吃", "hǎochī", "good-eat", "delicious"),
            ("服务员", "fúwùyuán", "serve-person", "waiter"),
        ],
        "dialogues": [
            {
                "title": "A busy Saturday",
                "lines": [
                    ("小明", "David，你今天早上几点起床？", "David, nǐ jīntiān zǎoshang jǐ diǎn qǐchuáng?", "David, you today early-up how-many dot rise-bed?", "David, what time did you get up this morning?"),
                    ("David", "我早上八点起床。", "wǒ zǎoshang bā diǎn qǐchuáng.", "I early-up eight dot rise-bed.", "I got up at 8 AM."),
                    ("小明", "你想吃什么？饺子还是面条？", "nǐ xiǎng chī shénme? jiǎozi háishi miàntiáo?", "you want eat what? dumpling still-am noodle?", "What do you want to eat? Dumplings or noodles?"),
                    ("David", "我都想吃！", "wǒ dōu xiǎng chī!", "I all want eat!", "I want to eat both!"),
                    ("小明", "好！下午我们去买东西。", "hǎo! xiàwǔ wǒmen qù mǎi dōngxi.", "good! lower-noon we go buy thing.", "Great! In the afternoon we'll go shopping."),
                    ("David", "好的！那个超市的东西贵吗？", "hǎo de! nàge chāoshì de dōngxi guì ma?", "good (particle)! that-piece supermarket (possessive) thing expensive (question)?", "OK! Are things expensive at that supermarket?"),
                    ("小明", "不贵，很好！", "bú guì, hěn hǎo!", "not expensive, very good!", "Not expensive, very good!"),
                    ("David", "太好了！", "tài hǎo le!", "too good (change)!", "That's great!"),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "Review: Word Order in Chinese Sentences",
                "explanation": (
                    "Chinese sentence order follows clear patterns:\n\n"
                    "1. Basic: Subject + Verb + Object\n"
                    "   我吃饺子 → I eat dumplings\n\n"
                    "2. With time: Subject + Time + Verb + Object\n"
                    "   我早上吃饺子 → I morning eat dumplings\n\n"
                    "3. With 想: Subject + 想 + Verb + Object\n"
                    "   我想吃饺子 → I want eat dumplings\n\n"
                    "4. With 太...了: 太 + Adj + 了\n"
                    "   太贵了 → too expensive!"
                ),
            },
        ],
        "culture_note": {
            "title": "还是 vs 或者 — Two Ways to Say 'Or'",
            "text": (
                "Chinese has two words for 'or':\n\n"
                "还是 (háishi) — used in QUESTIONS:\n"
                "你喝茶还是喝水？ (Tea or water?)\n\n"
                "或者 (huòzhě) — used in STATEMENTS:\n"
                "茶或者水都可以。 (Tea or water, both are fine.)\n\n"
                "This is a common mistake — even advanced learners mix "
                "them up! Just remember: questions use 还是."
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "你喝茶___喝水？(Do you want tea or water?)",
                "answer": "还是",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'I get up at 7 AM and eat dumplings.'",
                "answer": "我早上七点起床，吃饺子。",
            },
            {
                "type": "reorder",
                "instruction": "Put in correct order:",
                "question": "多少 / 那个 / 钱",
                "answer": "那个多少钱？",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "我都想吃！",
                "answer": "I all want eat!",
            },
        ],
    },

    # ==================================================================
    # Lesson 11: How's the Weather? / 天气怎么样？
    # ==================================================================
    11: {
        "id": 11,
        "title_en": "How's the Weather?",
        "title_zh": "天气怎么样？",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Talk about the weather in Chinese",
            "Use adjective predicates (no 是 needed)",
            "Express 'how is...?' with 怎么样",
            "Describe today's weather",
        ],
        "new_words": [
            ("天气", "tiānqì", "sky-air", "weather", "n"),
            ("怎么样", "zěnmeyàng", "how-kind", "how is it / what's it like", "pron"),
            ("冷", "lěng", "cold", "cold", "adj"),
            ("热", "rè", "hot", "hot", "adj"),
            ("今天", "jīntiān", "this-day", "today", "n"),
            ("明天", "míngtiān", "bright-day", "tomorrow", "n"),
            ("下雨", "xiàyǔ", "down-rain", "to rain", "v"),
            ("大", "dà", "big", "big", "adj"),
        ],
        "review_words": [
            ("很", "hěn", "very", "very"),
            ("好", "hǎo", "good", "good"),
            ("太", "tài", "too", "too"),
            ("了", "le", "(change)", "particle"),
            ("看", "kàn", "look", "to look"),
            ("天", "tiān", "day", "day"),
        ],
        "dialogues": [
            {
                "title": "Talking about the weather",
                "lines": [
                    ("Mary", "今天天气怎么样？", "jīntiān tiānqì zěnmeyàng?", "this-day sky-air how-kind?", "How's the weather today?"),
                    ("小明", "今天很冷！", "jīntiān hěn lěng!", "this-day very cold!", "It's very cold today!"),
                    ("Mary", "明天呢？", "míngtiān ne?", "bright-day (question)?", "What about tomorrow?"),
                    ("小明", "明天也冷。明天下雨。", "míngtiān yě lěng. míngtiān xiàyǔ.", "bright-day also cold. bright-day down-rain.", "Tomorrow is also cold. It will rain tomorrow."),
                    ("Mary", "太冷了！我不想去。", "tài lěng le! wǒ bù xiǎng qù.", "too cold (change)! I not want go.", "Too cold! I don't want to go."),
                    ("小明", "好，明天我们看书吧。", "hǎo, míngtiān wǒmen kàn shū ba.", "good, bright-day we look book (suggestion).", "OK, let's read books tomorrow."),
                    ("Mary", "好的！", "hǎo de!", "good (particle)!", "Sounds good!"),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "Adjective Predicates — No 是 Needed!",
                "explanation": (
                    "In Chinese, adjectives can be the main verb of a sentence. "
                    "Do NOT use 是 with adjectives:\n\n"
                    "今天 很 冷。 → today very cold. → 'It is very cold today.'\n"
                    "天气 很 好。 → weather very good. → 'The weather is good.'\n\n"
                    "WRONG: 今天是冷 ✗\n"
                    "RIGHT: 今天很冷 ✓\n\n"
                    "When using an adjective alone as a statement, 很 is usually "
                    "added (even without a 'very' meaning) — it's just how Chinese works!"
                ),
            },
        ],
        "culture_note": {
            "title": "Weather Small Talk in China",
            "text": (
                "Unlike in English, Chinese people don't talk about weather "
                "as much for small talk. Instead, a common greeting is "
                "'你吃了吗？' (Have you eaten?) — food is more important "
                "than weather!\n\n"
                "In 2026, weather apps are very popular in China. People "
                "check their phones for air quality index (AQI) alongside "
                "temperature. In big cities, 'PM2.5' is almost as commonly "
                "discussed as the temperature!"
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "今天天气___？(How's the weather today?)",
                "answer": "怎么样",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'Tomorrow is very hot.'",
                "answer": "明天很热。",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "今天天气很好。",
                "answer": "this-day sky-air very good.",
            },
            {
                "type": "multiple_choice",
                "instruction": "Choose the correct sentence:",
                "question": "'Today is cold' in Chinese is:",
                "options": ["今天是冷。", "今天很冷。", "今天冷是。", "是今天冷。"],
                "answer": "今天很冷。",
            },
        ],
    },

    # ==================================================================
    # Lesson 12: I Like... / 我喜欢……
    # ==================================================================
    12: {
        "id": 12,
        "title_en": "I Like...",
        "title_zh": "我喜欢……",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Express what you like and dislike",
            "Use 喜欢 + Verb or 喜欢 + Noun",
            "Talk about hobbies and interests",
            "Ask others about their preferences",
        ],
        "new_words": [
            ("喜欢", "xǐhuan", "happy-joyful", "to like", "v"),
            ("不", "bù", "not", "not", "adv"),
            ("打", "dǎ", "hit", "to play (ball sports)/to make (a call)", "v"),
            ("球", "qiú", "ball", "ball", "n"),
            ("听", "tīng", "listen", "to listen", "v"),
            ("音乐", "yīnyuè", "sound-music", "music", "n"),
            ("电影", "diànyǐng", "electric-shadow", "movie", "n"),
            ("做", "zuò", "do", "to do/to make", "v"),
        ],
        "review_words": [
            ("想", "xiǎng", "want", "to want"),
            ("看", "kàn", "look", "to watch/read"),
            ("书", "shū", "book", "book"),
            ("吃", "chī", "eat", "to eat"),
            ("喝", "hē", "drink", "to drink"),
            ("好吃", "hǎochī", "good-eat", "delicious"),
        ],
        "dialogues": [
            {
                "title": "Talking about hobbies",
                "lines": [
                    ("小红", "David，你喜欢做什么？", "David, nǐ xǐhuan zuò shénme?", "David, you happy-joyful do what?", "David, what do you like to do?"),
                    ("David", "我喜欢看电影。你呢？", "wǒ xǐhuan kàn diànyǐng. nǐ ne?", "I happy-joyful look electric-shadow. you (question)?", "I like watching movies. And you?"),
                    ("小红", "我喜欢听音乐。", "wǒ xǐhuan tīng yīnyuè.", "I happy-joyful listen sound-music.", "I like listening to music."),
                    ("David", "你喜欢打球吗？", "nǐ xǐhuan dǎ qiú ma?", "you happy-joyful hit ball (question)?", "Do you like playing ball?"),
                    ("小红", "不喜欢。我不喜欢打球。", "bù xǐhuan. wǒ bù xǐhuan dǎ qiú.", "not happy-joyful. I not happy-joyful hit ball.", "No. I don't like playing ball."),
                    ("David", "你喜欢看书吗？", "nǐ xǐhuan kàn shū ma?", "you happy-joyful look book (question)?", "Do you like reading?"),
                    ("小红", "喜欢！我很喜欢看书！", "xǐhuan! wǒ hěn xǐhuan kàn shū!", "happy-joyful! I very happy-joyful look book!", "Yes! I really like reading!"),
                    ("David", "太好了！我也喜欢看书。", "tài hǎo le! wǒ yě xǐhuan kàn shū.", "too good (change)! I also happy-joyful look book.", "Great! I also like reading."),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "喜欢 + Verb / Noun = 'to like'",
                "explanation": (
                    "喜欢 can be followed by a verb OR a noun:\n\n"
                    "With verbs:\n"
                    "我 喜欢 看 电影 → I like watch movie → 'I like watching movies'\n"
                    "她 喜欢 听 音乐 → she like listen music → 'She likes listening to music'\n\n"
                    "With nouns:\n"
                    "我 喜欢 茶 → I like tea → 'I like tea'\n"
                    "他 喜欢 书 → he like book → 'He likes books'\n\n"
                    "Negative: 不喜欢 (bù xǐhuan) = don't like"
                ),
            },
        ],
        "culture_note": {
            "title": "Popular Hobbies in Modern China",
            "text": (
                "In 2026 China, young people love watching short videos on "
                "Douyin (抖音, the Chinese version of TikTok). They also "
                "enjoy mobile gaming, online shopping, and going to "
                "网红店 (wǎnghóng diàn, 'internet-famous stores').\n\n"
                "Basketball (篮球 lánqiú) is hugely popular thanks to the "
                "NBA. Table tennis (乒乓球 pīngpāngqiú) remains the "
                "'national sport.' And KTV (karaoke) is still a favorite "
                "way to spend an evening with friends!"
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "我___看电影。(I like watching movies.)",
                "answer": "喜欢",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'She doesn't like playing ball.'",
                "answer": "她不喜欢打球。",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "我喜欢听音乐。",
                "answer": "I happy-joyful listen sound-music.",
            },
            {
                "type": "match",
                "instruction": "Match Chinese to English:",
                "pairs": [("看电影", "watch movies"), ("听音乐", "listen to music"), ("打球", "play ball"), ("看书", "read books")],
                "answer": "看电影—watch movies, 听音乐—listen to music, 打球—play ball, 看书—read books",
            },
        ],
    },

    # ==================================================================
    # Lesson 13: Where Is It? / 在哪里？
    # ==================================================================
    13: {
        "id": 13,
        "title_en": "Where Is It?",
        "title_zh": "在哪里？",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Ask and answer 'where' questions with 在哪里",
            "Use 在 + location to express 'at/in a place'",
            "Learn common location words",
            "Give simple directions",
        ],
        "new_words": [
            ("在", "zài", "at", "at/in (location)", "prep"),
            ("哪里", "nǎli", "which-inside", "where", "pron"),
            ("这里", "zhèli", "this-inside", "here", "pron"),
            ("那里", "nàli", "that-inside", "there", "pron"),
            ("前面", "qiánmiàn", "front-face", "in front", "n"),
            ("后面", "hòumiàn", "back-face", "behind", "n"),
            ("学校", "xuéxiào", "study-school", "school", "n"),
            ("医院", "yīyuàn", "heal-yard", "hospital", "n"),
        ],
        "review_words": [
            ("去", "qù", "go", "to go"),
            ("这个", "zhège", "this-piece", "this one"),
            ("那个", "nàge", "that-piece", "that one"),
            ("请问", "qǐngwèn", "please-ask", "may I ask"),
            ("谢谢", "xièxie", "thank-thank", "thank you"),
        ],
        "dialogues": [
            {
                "title": "Asking for directions",
                "lines": [
                    ("David", "请问，学校在哪里？", "qǐngwèn, xuéxiào zài nǎli?", "please-ask, study-school at which-inside?", "Excuse me, where is the school?"),
                    ("小红", "学校在前面。", "xuéxiào zài qiánmiàn.", "study-school at front-face.", "The school is ahead."),
                    ("David", "谢谢！医院在哪里？", "xièxie! yīyuàn zài nǎli?", "thank-thank! heal-yard at which-inside?", "Thanks! Where is the hospital?"),
                    ("小红", "医院在学校后面。", "yīyuàn zài xuéxiào hòumiàn.", "heal-yard at study-school back-face.", "The hospital is behind the school."),
                    ("David", "他在哪里？", "tā zài nǎli?", "he at which-inside?", "Where is he?"),
                    ("小红", "他在那里。", "tā zài nàli.", "he at that-inside.", "He is over there."),
                    ("David", "太好了，谢谢你！", "tài hǎo le, xièxie nǐ!", "too good (change), thank-thank you!", "Great, thank you!"),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "在 + Location — Expressing 'at/in a place'",
                "explanation": (
                    "在 (zài) means 'at' or 'in'. It goes BEFORE the location:\n\n"
                    "他 在 学校。 → he at school. → 'He is at school.'\n"
                    "学校 在 前面。 → school at front. → 'The school is ahead.'\n\n"
                    "To ask where: ...在哪里？\n"
                    "学校 在 哪里？ → school at where? → 'Where is the school?'\n"
                    "你 在 哪里？ → you at where? → 'Where are you?'\n\n"
                    "Pattern: Thing/Person + 在 + Place"
                ),
            },
        ],
        "culture_note": {
            "title": "Getting Around in Chinese Cities",
            "text": (
                "In 2026, Chinese cities have excellent public transport. "
                "The subway (地铁 dìtiě) is fast, cheap, and everywhere. "
                "Most people use map apps like 高德地图 (Gaode Maps) or "
                "百度地图 (Baidu Maps) on their phones.\n\n"
                "Ride-hailing apps like Didi (滴滴) are also very popular. "
                "But knowing how to ask 在哪里 is still essential — "
                "especially when your phone battery dies!"
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "学校___哪里？(Where is the school?)",
                "answer": "在",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'The hospital is behind the school.'",
                "answer": "医院在学校后面。",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "他在那里。",
                "answer": "he at that-inside.",
            },
            {
                "type": "match",
                "instruction": "Match Chinese to English:",
                "pairs": [("哪里", "where"), ("这里", "here"), ("前面", "in front"), ("后面", "behind")],
                "answer": "哪里—where, 这里—here, 前面—in front, 后面—behind",
            },
        ],
    },

    # ==================================================================
    # Lesson 14: Making a Phone Call / 打电话
    # ==================================================================
    14: {
        "id": 14,
        "title_en": "Making a Phone Call",
        "title_zh": "打电话",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Make and receive phone calls in Chinese",
            "Use 能 (néng) and 可以 (kěyǐ) for 'can'",
            "Ask for permission politely",
            "Handle common phone call phrases",
        ],
        "new_words": [
            ("打电话", "dǎ diànhuà", "hit electric-speech", "to make a phone call", "v"),
            ("喂", "wéi", "hello", "hello (on phone)", "interj"),
            ("能", "néng", "able", "can (ability)", "v"),
            ("可以", "kěyǐ", "may-with", "can (permission)", "v"),
            ("说", "shuō", "speak", "to speak/say", "v"),
            ("会", "huì", "able", "can (learned skill)", "v"),
            ("电话", "diànhuà", "electric-speech", "telephone", "n"),
            ("等", "děng", "wait", "to wait", "v"),
        ],
        "review_words": [
            ("叫", "jiào", "call", "to be called"),
            ("名字", "míngzi", "name-character", "name"),
            ("请问", "qǐngwèn", "please-ask", "may I ask"),
            ("你好", "nǐ hǎo", "you good", "hello"),
            ("谢谢", "xièxie", "thank-thank", "thank you"),
            ("再见", "zàijiàn", "again see", "goodbye"),
        ],
        "dialogues": [
            {
                "title": "Calling a friend",
                "lines": [
                    ("David", "喂？你好！", "wéi? nǐ hǎo!", "hello? you good!", "Hello? Hi!"),
                    ("小明", "喂！David，你好！", "wéi! David, nǐ hǎo!", "hello! David, you good!", "Hello! David, hi!"),
                    ("David", "小明，你明天能去学校吗？", "Xiǎo Míng, nǐ míngtiān néng qù xuéxiào ma?", "Little-Bright, you bright-day able go study-school (question)?", "Xiao Ming, can you go to school tomorrow?"),
                    ("小明", "能去！你几点去？", "néng qù! nǐ jǐ diǎn qù?", "able go! you how-many dot go?", "Yes I can! What time are you going?"),
                    ("David", "上午九点。你可以等我吗？", "shàngwǔ jiǔ diǎn. nǐ kěyǐ děng wǒ ma?", "upper-noon nine dot. you may-with wait I (question)?", "9 AM. Can you wait for me?"),
                    ("小明", "可以！我等你。", "kěyǐ! wǒ děng nǐ.", "may-with! I wait you.", "Sure! I'll wait for you."),
                    ("David", "太好了！谢谢，再见！", "tài hǎo le! xièxie, zàijiàn!", "too good (change)! thank-thank, again see!", "Great! Thanks, bye!"),
                    ("小明", "再见！", "zàijiàn!", "again see!", "Bye!"),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "能 / 可以 / 会 — Three Ways to Say 'Can'",
                "explanation": (
                    "Chinese has three words for 'can', each with a different meaning:\n\n"
                    "能 (néng) = can (physical ability / circumstances):\n"
                    "你明天能去吗？ → Can you go tomorrow?\n\n"
                    "可以 (kěyǐ) = may / can (permission):\n"
                    "我可以打电话吗？ → May I make a phone call?\n\n"
                    "会 (huì) = can (learned skill):\n"
                    "他会说中文。 → He can speak Chinese.\n\n"
                    "All three go directly before the verb, just like 想."
                ),
            },
        ],
        "culture_note": {
            "title": "Phone Culture in China",
            "text": (
                "In 2026, phone calls are less common than voice messages! "
                "Chinese people love sending 语音 (yǔyīn, voice messages) "
                "on WeChat. You'll hear people holding their phone sideways "
                "and talking into the bottom — that's a voice message!\n\n"
                "When answering the phone, Chinese people say 喂 (wéi) — "
                "this is ONLY used on the phone. Never say 喂 face to face! "
                "It's the Chinese equivalent of 'Hello?' when picking up."
            ),
        },
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank:",
                "question": "你明天___去学校吗？(Can you go to school tomorrow?)",
                "answer": "能",
            },
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'He can speak Chinese.'",
                "answer": "他会说中文。",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "你可以等我吗？",
                "answer": "you may-with wait I (question)?",
            },
            {
                "type": "multiple_choice",
                "instruction": "Choose the correct answer:",
                "question": "Which word for 'can' is used for learned skills?",
                "options": ["能", "可以", "会", "想"],
                "answer": "会",
            },
        ],
    },

    # ==================================================================
    # Lesson 15: Final Review / 总复习 (Reviews L1-14)
    # ==================================================================
    15: {
        "id": 15,
        "title_en": "Final Review",
        "title_zh": "总复习",
        "book": "Book 1",
        "hsk_level": 1,
        "learning_goals": [
            "Review all vocabulary and grammar from Book 1 (L1-14)",
            "Practice combining skills from all lessons",
            "Build confidence for real-world Chinese conversations",
        ],
        "new_words": [],
        "review_words": [
            ("你好", "nǐ hǎo", "you good", "hello"),
            ("叫", "jiào", "call", "to be called"),
            ("什么", "shénme", "what", "what"),
            ("的", "de", "(possessive)", "possessive particle"),
            ("家", "jiā", "home", "home/family"),
            ("有", "yǒu", "have", "to have"),
            ("几", "jǐ", "how-many", "how many"),
            ("点", "diǎn", "dot", "o'clock"),
            ("起床", "qǐchuáng", "rise-bed", "to get up"),
            ("吃", "chī", "eat", "to eat"),
            ("想", "xiǎng", "want", "to want"),
            ("多少钱", "duōshao qián", "many-few money", "how much"),
            ("天气", "tiānqì", "sky-air", "weather"),
            ("喜欢", "xǐhuan", "happy-joyful", "to like"),
            ("在", "zài", "at", "at/in"),
            ("哪里", "nǎli", "which-inside", "where"),
            ("能", "néng", "able", "can"),
            ("可以", "kěyǐ", "may-with", "may/can"),
        ],
        "dialogues": [
            {
                "title": "A day in China — putting it all together",
                "lines": [
                    ("David", "你好！我叫David。你叫什么名字？", "nǐ hǎo! wǒ jiào David. nǐ jiào shénme míngzi?", "you good! I call David. you call what name-character?", "Hello! My name is David. What's your name?"),
                    ("小明", "我叫小明。你好！你几岁？", "wǒ jiào Xiǎo Míng. nǐ hǎo! nǐ jǐ suì?", "I call Little-Bright. you good! you how-many year-of-age?", "My name is Xiao Ming. Hi! How old are you?"),
                    ("David", "我二十一岁。今天天气怎么样？", "wǒ èrshíyī suì. jīntiān tiānqì zěnmeyàng?", "I two-ten-one year-of-age. this-day sky-air how-kind?", "I'm 21. How's the weather today?"),
                    ("小明", "今天很热！你想吃什么？", "jīntiān hěn rè! nǐ xiǎng chī shénme?", "this-day very hot! you want eat what?", "It's very hot today! What do you want to eat?"),
                    ("David", "我想吃饺子。你喜欢吃饺子吗？", "wǒ xiǎng chī jiǎozi. nǐ xǐhuan chī jiǎozi ma?", "I want eat dumpling. you happy-joyful eat dumpling (question)?", "I want to eat dumplings. Do you like eating dumplings?"),
                    ("小明", "喜欢！我们去那个餐厅吧。", "xǐhuan! wǒmen qù nàge cāntīng ba.", "happy-joyful! we go that-piece restaurant (suggestion).", "Yes! Let's go to that restaurant."),
                    ("David", "餐厅在哪里？", "cāntīng zài nǎli?", "restaurant at which-inside?", "Where is the restaurant?"),
                    ("小明", "在学校前面。我们现在能去吗？", "zài xuéxiào qiánmiàn. wǒmen xiànzài néng qù ma?", "at study-school front-face. we now-at able go (question)?", "In front of the school. Can we go now?"),
                    ("David", "可以！太好了！我们走吧！", "kěyǐ! tài hǎo le! wǒmen zǒu ba!", "may-with! too good (change)! we walk (suggestion)!", "Sure! Great! Let's go!"),
                    ("小明", "好！", "hǎo!", "good!", "OK!"),
                ],
            }
        ],
        "grammar_points": [
            {
                "title": "Book 1 Grammar Summary",
                "explanation": (
                    "Here are all the grammar patterns from Book 1:\n\n"
                    "1. SVO word order: 我是老师 (I am teacher)\n"
                    "2. 什么 questions: 你叫什么名字？ (What's your name?)\n"
                    "3. 的 possession: 我的家 (my home)\n"
                    "4. Number + 个 + Noun: 三个人 (three people)\n"
                    "5. 几点 time: 现在几点了？ (What time is it?)\n"
                    "6. Time before verb: 我七点起床 (I 7-o'clock get-up)\n"
                    "7. 想 + Verb: 我想吃 (I want to eat)\n"
                    "8. 多少钱: 这个多少钱？ (How much is this?)\n"
                    "9. Adj predicates: 今天很冷 (Today is cold)\n"
                    "10. 喜欢 + V/N: 我喜欢看书 (I like reading)\n"
                    "11. 在 + location: 学校在前面 (School is ahead)\n"
                    "12. 能/可以/会: 你能去吗？ (Can you go?)"
                ),
            },
        ],
        "culture_note": {
            "title": "Congratulations! Your Chinese Journey",
            "text": (
                "Congratulations on completing Book 1! You now know enough "
                "Chinese to: greet people, introduce yourself, talk about "
                "family, tell time, order food, go shopping, discuss weather, "
                "share hobbies, ask for directions, and make phone calls.\n\n"
                "In 2026 China, even basic Chinese will open many doors. "
                "People appreciate when foreigners try to speak their language. "
                "Don't be afraid to make mistakes — Chinese people will be "
                "thrilled that you're learning! Remember: 加油！(jiāyóu, "
                "literally 'add oil' — it means 'keep going!')"
            ),
        },
        "exercises": [
            {
                "type": "translate",
                "instruction": "Translate to Chinese:",
                "question": "'Hello! My name is David. I am 21 years old. I like eating dumplings.'",
                "answer": "你好！我叫David。我二十一岁。我喜欢吃饺子。",
            },
            {
                "type": "fill_blank",
                "instruction": "Fill in the blanks:",
                "question": "餐厅___学校前面。(The restaurant is in front of the school.)",
                "answer": "在",
            },
            {
                "type": "reorder",
                "instruction": "Put in correct order:",
                "question": "吗 / 明天 / 你 / 去 / 能 / 学校",
                "answer": "你明天能去学校吗？",
            },
            {
                "type": "word_by_word",
                "instruction": "Write the word-by-word English:",
                "question": "今天天气很热，我想吃饺子。",
                "answer": "this-day sky-air very hot, I want eat dumpling.",
            },
        ],
    },
}


def get_lesson(lesson_id: int) -> dict:
    """Get lesson data by ID."""
    return LESSONS.get(lesson_id)


def get_available_lessons() -> list:
    """Get list of available lesson IDs."""
    return sorted(LESSONS.keys())
