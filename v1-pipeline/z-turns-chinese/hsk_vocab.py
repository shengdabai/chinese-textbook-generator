"""
HSK 3.0 (2026) Core Vocabulary Database
Selected high-frequency words for Book 1 (HSK 1, 300 words)
Organized by lesson topic with four-layer translations
"""

# Format: (chinese, pinyin, word_by_word_en, natural_en, pos, hsk_level)
# Source: HSK 3.0 2026 standard vocabulary list

VOCAB_BY_TOPIC = {
    "greetings": [
        ("你", "nǐ", "you", "you", "pron", 1),
        ("好", "hǎo", "good", "good/well", "adj", 1),
        ("你好", "nǐ hǎo", "you good", "hello", "phrase", 1),
        ("我", "wǒ", "I", "I/me", "pron", 1),
        ("是", "shì", "am/is", "to be", "v", 1),
        ("谢谢", "xièxie", "thank-thank", "thank you", "v", 1),
        ("不客气", "bú kèqi", "not polite", "you're welcome", "phrase", 1),
        ("再见", "zàijiàn", "again see", "goodbye", "phrase", 1),
        ("老师", "lǎoshī", "old master", "teacher", "n", 1),
        ("同学", "tóngxué", "same study", "classmate", "n", 1),
        ("请", "qǐng", "please", "please", "v", 1),
        ("对不起", "duìbuqǐ", "face-not-up", "sorry", "phrase", 1),
        ("没关系", "méi guānxi", "not relation", "it's okay", "phrase", 1),
    ],
    "introductions": [
        ("叫", "jiào", "called", "to be called", "v", 1),
        ("什么", "shénme", "what", "what", "pron", 1),
        ("名字", "míngzi", "name-character", "name", "n", 1),
        ("他", "tā", "he", "he/him", "pron", 1),
        ("她", "tā", "she", "she/her", "pron", 1),
        ("哪", "nǎ", "which", "which", "pron", 1),
        ("国", "guó", "country", "country", "n", 1),
        ("人", "rén", "person", "person/people", "n", 1),
        ("中国", "Zhōngguó", "middle country", "China", "n", 1),
        ("美国", "Měiguó", "beautiful country", "America/USA", "n", 1),
        ("英国", "Yīngguó", "brave country", "England/UK", "n", 1),
        ("认识", "rènshi", "recognize know", "to know (someone)", "v", 1),
        ("很高兴", "hěn gāoxìng", "very high-spirit", "very happy", "phrase", 1),
    ],
    "family": [
        ("家", "jiā", "home", "home/family", "n", 1),
        ("爸爸", "bàba", "dad", "father", "n", 1),
        ("妈妈", "māma", "mom", "mother", "n", 1),
        ("哥哥", "gēge", "older-brother", "older brother", "n", 1),
        ("姐姐", "jiějie", "older-sister", "older sister", "n", 1),
        ("弟弟", "dìdi", "younger-brother", "younger brother", "n", 1),
        ("妹妹", "mèimei", "younger-sister", "younger sister", "n", 1),
        ("的", "de", "'s", "(possessive particle)", "part", 1),
        ("有", "yǒu", "have", "to have", "v", 1),
        ("几", "jǐ", "how-many", "how many", "pron", 1),
        ("口", "kǒu", "mouth", "(measure word for family)", "mw", 1),
        ("和", "hé", "and", "and", "conj", 1),
        ("大", "dà", "big", "big/old (age)", "adj", 1),
        ("小", "xiǎo", "small", "small/young", "adj", 1),
    ],
    "numbers": [
        ("一", "yī", "one", "1", "num", 1),
        ("二", "èr", "two", "2", "num", 1),
        ("三", "sān", "three", "3", "num", 1),
        ("四", "sì", "four", "4", "num", 1),
        ("五", "wǔ", "five", "5", "num", 1),
        ("六", "liù", "six", "6", "num", 1),
        ("七", "qī", "seven", "7", "num", 1),
        ("八", "bā", "eight", "8", "num", 1),
        ("九", "jiǔ", "nine", "9", "num", 1),
        ("十", "shí", "ten", "10", "num", 1),
        ("百", "bǎi", "hundred", "100", "num", 1),
        ("个", "gè", "piece", "(general measure word)", "mw", 1),
        ("多少", "duōshao", "much-few", "how much/many", "pron", 1),
        ("两", "liǎng", "two(pair)", "two (before measure word)", "num", 1),
        ("岁", "suì", "year-of-age", "years old", "mw", 1),
    ],
    "time": [
        ("点", "diǎn", "dot", "o'clock", "mw", 1),
        ("分", "fēn", "divide", "minute", "mw", 1),
        ("半", "bàn", "half", "half", "num", 1),
        ("现在", "xiànzài", "now-at", "now", "n", 1),
        ("今天", "jīntiān", "this-day", "today", "n", 1),
        ("明天", "míngtiān", "bright-day", "tomorrow", "n", 1),
        ("昨天", "zuótiān", "past-day", "yesterday", "n", 1),
        ("早上", "zǎoshang", "early-upon", "morning", "n", 1),
        ("中午", "zhōngwǔ", "middle-noon", "noon", "n", 1),
        ("下午", "xiàwǔ", "below-noon", "afternoon", "n", 1),
        ("晚上", "wǎnshang", "late-upon", "evening", "n", 1),
    ],
    "daily_routine": [
        ("起床", "qǐchuáng", "rise-bed", "to get up", "v", 1),
        ("睡觉", "shuìjiào", "sleep-sleep", "to sleep", "v", 1),
        ("吃", "chī", "eat", "to eat", "v", 1),
        ("喝", "hē", "drink", "to drink", "v", 1),
        ("去", "qù", "go", "to go", "v", 1),
        ("来", "lái", "come", "to come", "v", 1),
        ("工作", "gōngzuò", "work-do", "to work", "v/n", 1),
        ("学习", "xuéxí", "study-practice", "to study", "v", 1),
        ("上班", "shàngbān", "up-shift", "to go to work", "v", 1),
        ("下班", "xiàbān", "down-shift", "to get off work", "v", 1),
    ],
    "restaurant": [
        ("菜单", "càidān", "dish-list", "menu", "n", 1),
        ("点菜", "diǎncài", "select-dish", "to order food", "v", 1),
        ("饺子", "jiǎozi", "dumpling", "dumplings", "n", 1),
        ("米饭", "mǐfàn", "rice-food", "rice", "n", 1),
        ("面条", "miàntiáo", "flour-strip", "noodles", "n", 1),
        ("茶", "chá", "tea", "tea", "n", 1),
        ("水", "shuǐ", "water", "water", "n", 1),
        ("碗", "wǎn", "bowl", "bowl (measure word)", "mw", 1),
        ("杯", "bēi", "cup", "cup (measure word)", "mw", 1),
        ("好吃", "hǎochī", "good-eat", "delicious", "adj", 1),
        ("服务员", "fúwùyuán", "serve-person", "waiter/waitress", "n", 1),
        ("买单", "mǎidān", "buy-bill", "to pay the bill", "v", 1),
        ("想", "xiǎng", "want", "to want/would like", "v", 1),
    ],
    "shopping": [
        ("买", "mǎi", "buy", "to buy", "v", 1),
        ("卖", "mài", "sell", "to sell", "v", 1),
        ("钱", "qián", "money", "money", "n", 1),
        ("块", "kuài", "piece", "yuan (currency)", "mw", 1),
        ("贵", "guì", "expensive", "expensive", "adj", 1),
        ("便宜", "piányi", "cheap", "cheap", "adj", 1),
        ("这", "zhè", "this", "this", "pron", 1),
        ("那", "nà", "that", "that", "pron", 1),
        ("要", "yào", "want", "to want/need", "v", 1),
        ("超市", "chāoshì", "super-market", "supermarket", "n", 1),
    ],
    "weather": [
        ("天气", "tiānqì", "sky-air", "weather", "n", 1),
        ("冷", "lěng", "cold", "cold", "adj", 1),
        ("热", "rè", "hot", "hot", "adj", 1),
        ("下雨", "xià yǔ", "fall-rain", "to rain", "v", 1),
        ("晴天", "qíngtiān", "clear-day", "sunny day", "n", 1),
        ("怎么样", "zěnmeyàng", "how-kind", "how is it", "pron", 1),
        ("太", "tài", "too", "too (much)", "adv", 1),
        ("了", "le", "(change)", "(particle)", "part", 1),
    ],
    "hobbies": [
        ("喜欢", "xǐhuan", "happy-like", "to like", "v", 1),
        ("看", "kàn", "look", "to watch/read", "v", 1),
        ("书", "shū", "book", "book", "n", 1),
        ("电影", "diànyǐng", "electric-shadow", "movie", "n", 1),
        ("音乐", "yīnyuè", "sound-joy", "music", "n", 1),
        ("运动", "yùndòng", "move-action", "sports/exercise", "n/v", 1),
        ("打球", "dǎqiú", "hit-ball", "to play ball", "v", 1),
        ("跑步", "pǎobù", "run-step", "to jog/run", "v", 1),
    ],
    "directions": [
        ("在", "zài", "at", "at/in", "prep", 1),
        ("哪里", "nǎlǐ", "where-inside", "where", "pron", 1),
        ("这里", "zhèlǐ", "this-inside", "here", "pron", 1),
        ("那里", "nàlǐ", "that-inside", "there", "pron", 1),
        ("前面", "qiánmiàn", "front-face", "in front", "n", 1),
        ("后面", "hòumiàn", "back-face", "behind", "n", 1),
        ("左边", "zuǒbiān", "left-side", "left side", "n", 1),
        ("右边", "yòubiān", "right-side", "right side", "n", 1),
    ],
    "phone": [
        ("打电话", "dǎ diànhuà", "hit electric-talk", "to make a phone call", "v", 1),
        ("手机", "shǒujī", "hand-machine", "mobile phone", "n", 1),
        ("号码", "hàomǎ", "number-code", "number", "n", 1),
        ("喂", "wèi", "hey", "hello (on phone)", "interj", 1),
        ("等", "děng", "wait", "to wait", "v", 1),
        ("能", "néng", "can", "can/be able to", "v", 1),
        ("可以", "kěyǐ", "can-with", "may/can", "v", 1),
        ("会", "huì", "know-how", "can/will", "v", 1),
    ],
}


def get_vocab_for_lesson(topic: str) -> list:
    """Get vocabulary list for a specific lesson topic."""
    return VOCAB_BY_TOPIC.get(topic, [])


def get_all_vocab_up_to_lesson(lesson_id: int, lesson_list: list) -> list:
    """Get all vocabulary accumulated up to a specific lesson."""
    all_vocab = []
    for lesson in lesson_list:
        if lesson["id"] <= lesson_id:
            topic = lesson["topic"]
            if topic != "review":
                all_vocab.extend(VOCAB_BY_TOPIC.get(topic, []))
    return all_vocab


def check_vocab_in_hsk(word: str, level: int = 1) -> bool:
    """Check if a word is within the specified HSK level."""
    for topic_vocab in VOCAB_BY_TOPIC.values():
        for item in topic_vocab:
            if item[0] == word and item[5] <= level:
                return True
    return False
