"""
Phrase Memory - 句型记忆库
Z Turns Chinese 核心资产系统，管理和复用教材中的句型模板。
基于GPT方案的Phrase Memory设计，实现句型的持久化存储、搜索和复用。
"""

import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional


# ============================================================
# Data Model
# ============================================================

@dataclass
class Phrase:
    """单个句型的完整数据结构"""
    phrase_id: str
    en_text: str
    zh_text: str
    pinyin: str
    gloss: str
    level: str          # CEFR: A1 / A2 / B1
    function: str       # greetings / introductions / family / etc.
    first_lesson_id: int
    aliases: list = field(default_factory=list)
    status: str = "approved"   # approved / draft / deprecated

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Phrase":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ============================================================
# PhraseMemory Core
# ============================================================

class PhraseMemory:
    """
    句型记忆库：存储、搜索、复用教材中出现过的所有句型。

    用法:
        pm = PhraseMemory()              # 自动加载或创建初始数据
        pm.add_phrase("Hello", "你好", "nǐ hǎo", "you good", "A1", "greetings", 1)
        results = pm.search("name", by="en")
    """

    DEFAULT_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "phrase_memory.json"
    )

    def __init__(self, filepath: Optional[str] = None):
        self.filepath = filepath or self.DEFAULT_PATH
        self._phrases: dict[str, Phrase] = {}
        self._load_or_init()

    # ----------------------------------------------------------
    # Persistence
    # ----------------------------------------------------------

    def _load_or_init(self):
        """加载已有数据，或首次运行时填充初始句型"""
        if os.path.exists(self.filepath):
            self.import_json(self.filepath)
        else:
            self._seed_initial_data()
            self._save()

    def _save(self):
        """持久化到JSON文件"""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        data = {pid: p.to_dict() for pid, p in self._phrases.items()}
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ----------------------------------------------------------
    # CRUD
    # ----------------------------------------------------------

    def add_phrase(
        self,
        en_text: str,
        zh_text: str,
        pinyin: str,
        gloss: str,
        level: str,
        function: str,
        first_lesson_id: int,
        aliases: Optional[list] = None,
        status: str = "approved",
    ) -> str:
        """添加新句型，返回 phrase_id"""
        phrase_id = f"PH-{uuid.uuid4().hex[:8].upper()}"
        phrase = Phrase(
            phrase_id=phrase_id,
            en_text=en_text,
            zh_text=zh_text,
            pinyin=pinyin,
            gloss=gloss,
            level=level,
            function=function,
            first_lesson_id=first_lesson_id,
            aliases=aliases or [],
            status=status,
        )
        self._phrases[phrase_id] = phrase
        self._save()
        return phrase_id

    def get_phrase(self, phrase_id: str) -> Optional[dict]:
        """按ID获取句型"""
        phrase = self._phrases.get(phrase_id)
        return phrase.to_dict() if phrase else None

    # ----------------------------------------------------------
    # Search & Query
    # ----------------------------------------------------------

    def search(self, query: str, by: str = "en") -> list[dict]:
        """
        搜索句型。
        by: "en" | "zh" | "function" | "pinyin"
        """
        query_lower = query.lower()
        results = []
        for p in self._phrases.values():
            if by == "en" and query_lower in p.en_text.lower():
                results.append(p.to_dict())
            elif by == "zh" and query in p.zh_text:
                results.append(p.to_dict())
            elif by == "function" and query_lower == p.function.lower():
                results.append(p.to_dict())
            elif by == "pinyin" and query_lower in p.pinyin.lower():
                results.append(p.to_dict())
        return results

    def get_by_level(self, level: str) -> list[dict]:
        """获取指定CEFR等级的所有句型"""
        return [p.to_dict() for p in self._phrases.values() if p.level == level]

    def get_by_function(self, function: str) -> list[dict]:
        """获取指定交际功能分类的所有句型"""
        return [
            p.to_dict()
            for p in self._phrases.values()
            if p.function.lower() == function.lower()
        ]

    # ----------------------------------------------------------
    # Reuse Logic (句型复用)
    # ----------------------------------------------------------

    # 功能→主题关联映射表
    _TOPIC_FUNCTION_MAP: dict[str, list[str]] = {
        "restaurant": ["food", "numbers", "daily"],
        "hotel": ["daily", "numbers", "directions"],
        "shopping": ["shopping", "numbers", "daily"],
        "travel": ["directions", "time", "daily"],
        "school": ["introductions", "time", "daily"],
        "meeting": ["greetings", "introductions", "daily"],
        "market": ["shopping", "numbers", "food"],
        "family": ["family", "introductions", "daily"],
        "taxi": ["directions", "numbers", "daily"],
        "weather": ["daily", "time"],
        "birthday": ["time", "numbers", "family", "food"],
        "hospital": ["daily", "numbers", "directions"],
        "phone": ["greetings", "introductions", "daily"],
        "work": ["introductions", "time", "daily"],
    }

    def find_matching(self, topic: str, level: str) -> list[dict]:
        """
        为新课查找可复用句型：根据主题和等级匹配。
        优先返回已批准（approved）的句型。
        """
        topic_lower = topic.lower()
        # 1. 精确主题匹配
        related_functions = self._TOPIC_FUNCTION_MAP.get(topic_lower, [])
        # 2. 模糊主题→功能匹配
        if not related_functions:
            for key, funcs in self._TOPIC_FUNCTION_MAP.items():
                if topic_lower in key or key in topic_lower:
                    related_functions = funcs
                    break
        # 3. 搜集匹配句型
        results = []
        seen_ids = set()
        level_order = {"A1": 0, "A2": 1, "B1": 2}
        target_level_num = level_order.get(level, 0)

        for p in self._phrases.values():
            p_level_num = level_order.get(p.level, 0)
            if p_level_num > target_level_num:
                continue
            if p.function.lower() in [f.lower() for f in related_functions]:
                if p.phrase_id not in seen_ids:
                    results.append(p.to_dict())
                    seen_ids.add(p.phrase_id)

        # 按状态排序：approved优先
        results.sort(key=lambda x: (0 if x["status"] == "approved" else 1))
        return results

    def get_reuse_candidates(self, lesson_id: int, max_results: int = 10) -> list[dict]:
        """
        获取可在 lesson_id 课次复用的句型候选。
        选取在之前课次出现过的、approved状态的句型。
        """
        candidates = [
            p.to_dict()
            for p in self._phrases.values()
            if p.first_lesson_id < lesson_id and p.status == "approved"
        ]
        # 按 first_lesson_id 降序排列（最近学过的优先复用）
        candidates.sort(key=lambda x: x["first_lesson_id"], reverse=True)
        return candidates[:max_results]

    # ----------------------------------------------------------
    # Conflict Resolution (冲突解决)
    # ----------------------------------------------------------

    def resolve_conflict(
        self, phrase_id_1: str, phrase_id_2: str, strategy: str = "primary_alias"
    ) -> dict:
        """
        解决两个句型冲突。
        strategy:
          - "primary_alias": 保留 phrase_id_1 为主句型，phrase_id_2 降级为别名
          - "merge": 合并两者别名，保留 phrase_id_1
          - "deprecate": 废弃 phrase_id_2
        """
        p1 = self._phrases.get(phrase_id_1)
        p2 = self._phrases.get(phrase_id_2)
        if not p1 or not p2:
            return {"error": "One or both phrase_ids not found"}

        if strategy == "primary_alias":
            if p2.en_text not in p1.aliases:
                p1.aliases.append(p2.en_text)
            if p2.zh_text not in p1.aliases:
                p1.aliases.append(p2.zh_text)
            p2.status = "deprecated"

        elif strategy == "merge":
            merged_aliases = list(set(p1.aliases + p2.aliases + [p2.en_text, p2.zh_text]))
            p1.aliases = merged_aliases
            p2.status = "deprecated"

        elif strategy == "deprecate":
            p2.status = "deprecated"

        else:
            return {"error": f"Unknown strategy: {strategy}"}

        self._save()
        return {
            "primary": p1.to_dict(),
            "secondary": p2.to_dict(),
            "strategy": strategy,
        }

    # ----------------------------------------------------------
    # Import / Export
    # ----------------------------------------------------------

    def export_json(self, filepath: Optional[str] = None) -> str:
        """导出为JSON。返回JSON字符串；如指定filepath则同时写入文件。"""
        data = {pid: p.to_dict() for pid, p in self._phrases.items()}
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if filepath:
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)
        return json_str

    def import_json(self, filepath: str) -> int:
        """从JSON文件导入句型，返回导入数量。"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for pid, pdata in data.items():
            self._phrases[pid] = Phrase.from_dict(pdata)
            count += 1
        return count

    # ----------------------------------------------------------
    # Stats
    # ----------------------------------------------------------

    def stats(self) -> dict:
        """句型库统计信息"""
        total = len(self._phrases)
        by_level: dict[str, int] = {}
        by_function: dict[str, int] = {}
        by_status: dict[str, int] = {}

        for p in self._phrases.values():
            by_level[p.level] = by_level.get(p.level, 0) + 1
            by_function[p.function] = by_function.get(p.function, 0) + 1
            by_status[p.status] = by_status.get(p.status, 0) + 1

        return {
            "total": total,
            "by_level": dict(sorted(by_level.items())),
            "by_function": dict(sorted(by_function.items())),
            "by_status": dict(sorted(by_status.items())),
        }

    # ----------------------------------------------------------
    # Initial Seed Data (A1级别30+常用句型)
    # ----------------------------------------------------------

    def _seed_initial_data(self):
        """预填充A1级别常用句型"""
        seed = [
            # === greetings (问候) ===
            ("Hello.", "你好。", "nǐ hǎo", "you / good", "A1", "greetings", 1),
            ("How are you?", "你好吗？", "nǐ hǎo ma", "you / good / [question]", "A1", "greetings", 1),
            ("Good morning.", "早上好。", "zǎoshang hǎo", "morning / good", "A1", "greetings", 1),
            ("Goodbye.", "再见。", "zàijiàn", "again / see", "A1", "greetings", 1),
            ("Thank you.", "谢谢。", "xièxie", "thank / thank", "A1", "greetings", 1),
            ("You're welcome.", "不客气。", "bú kèqi", "not / polite", "A1", "greetings", 1),
            ("Sorry.", "对不起。", "duìbuqǐ", "face / not / up", "A1", "greetings", 2),
            ("It's okay.", "没关系。", "méi guānxi", "not-have / relation", "A1", "greetings", 2),

            # === introductions (自我介绍) ===
            ("What's your name?", "你叫什么名字？", "nǐ jiào shénme míngzi", "you / called / what / name", "A1", "introductions", 1),
            ("My name is ...", "我叫……", "wǒ jiào ...", "I / called / ...", "A1", "introductions", 1),
            ("Where are you from?", "你是哪国人？", "nǐ shì nǎ guó rén", "you / are / which / country / person", "A1", "introductions", 2),
            ("I am American.", "我是美国人。", "wǒ shì Měiguó rén", "I / am / America / person", "A1", "introductions", 2),
            ("Nice to meet you.", "认识你很高兴。", "rènshi nǐ hěn gāoxìng", "know / you / very / happy", "A1", "introductions", 2),

            # === family (家庭) ===
            ("How many people are in your family?", "你家有几口人？", "nǐ jiā yǒu jǐ kǒu rén", "your / home / have / how-many / [measure] / person", "A1", "family", 3),
            ("This is my ...", "这是我的……", "zhè shì wǒ de ...", "this / is / my / ...", "A1", "family", 3),
            ("Do you have siblings?", "你有兄弟姐妹吗？", "nǐ yǒu xiōngdì jiěmèi ma", "you / have / brothers / sisters / [question]", "A1", "family", 3),
            ("She is my mother.", "她是我妈妈。", "tā shì wǒ māma", "she / is / my / mother", "A1", "family", 3),

            # === numbers (数字) ===
            ("How many?", "多少？", "duōshao", "how / many", "A1", "numbers", 2),
            ("How many (small number)?", "几个？", "jǐ gè", "how-many / [measure]", "A1", "numbers", 2),
            ("Which number? / What place?", "第几？", "dì jǐ", "ordinal / how-many", "A1", "numbers", 4),
            ("I have two.", "我有两个。", "wǒ yǒu liǎng gè", "I / have / two / [measure]", "A1", "numbers", 3),

            # === time (时间) ===
            ("What time is it?", "几点了？", "jǐ diǎn le", "how-many / o'clock / [change]", "A1", "time", 4),
            ("When?", "什么时候？", "shénme shíhou", "what / time", "A1", "time", 4),
            ("What day is today?", "今天星期几？", "jīntiān xīngqī jǐ", "today / week / how-many", "A1", "time", 4),
            ("Now is three o'clock.", "现在三点。", "xiànzài sān diǎn", "now / three / o'clock", "A1", "time", 4),

            # === food (饮食) ===
            ("What do you want to eat?", "你想吃什么？", "nǐ xiǎng chī shénme", "you / want / eat / what", "A1", "food", 5),
            ("I want ...", "我要……", "wǒ yào ...", "I / want / ...", "A1", "food", 5),
            ("How much is it?", "多少钱？", "duōshao qián", "how-many / money", "A1", "food", 5),
            ("I like eating Chinese food.", "我喜欢吃中国菜。", "wǒ xǐhuan chī Zhōngguó cài", "I / like / eat / China / dish", "A1", "food", 5),

            # === shopping (购物) ===
            ("How much is this?", "这个多少钱？", "zhège duōshao qián", "this-[measure] / how-many / money", "A1", "shopping", 6),
            ("Too expensive.", "太贵了。", "tài guì le", "too / expensive / [emphasis]", "A1", "shopping", 6),
            ("Can it be cheaper?", "可以便宜一点吗？", "kěyǐ piányi yīdiǎn ma", "can / cheap / a-little / [question]", "A1", "shopping", 6),
            ("I want to buy this.", "我想买这个。", "wǒ xiǎng mǎi zhège", "I / want / buy / this-[measure]", "A1", "shopping", 6),

            # === directions (方向) ===
            ("Where is it?", "在哪里？", "zài nǎlǐ", "at / where", "A1", "directions", 7),
            ("How do I get there?", "怎么走？", "zěnme zǒu", "how / walk", "A1", "directions", 7),
            ("Turn left.", "左转。", "zuǒ zhuǎn", "left / turn", "A1", "directions", 7),
            ("Turn right.", "右转。", "yòu zhuǎn", "right / turn", "A1", "directions", 7),

            # === daily (日常) ===
            ("I every day ...", "我每天……", "wǒ měitiān ...", "I / every-day / ...", "A1", "daily", 3),
            ("Do you like ...?", "你喜欢……吗？", "nǐ xǐhuan ... ma", "you / like / ... / [question]", "A1", "daily", 3),
            ("How's the weather?", "天气怎么样？", "tiānqì zěnmeyàng", "weather / how-about", "A1", "daily", 8),
            ("I want to go to ...", "我想去……", "wǒ xiǎng qù ...", "I / want / go / ...", "A1", "daily", 5),
            ("Can you speak Chinese?", "你会说中文吗？", "nǐ huì shuō Zhōngwén ma", "you / can / speak / Chinese / [question]", "A1", "daily", 2),
        ]

        for item in seed:
            en, zh, py, gl, lv, fn, lesson = item
            self.add_phrase(en, zh, py, gl, lv, fn, lesson)


# ============================================================
# Demo
# ============================================================

def demo():
    """演示 PhraseMemory 的基本功能"""
    import tempfile

    # 使用临时目录避免污染项目数据
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, "demo_phrase_memory.json")

    print("=" * 60)
    print("  PhraseMemory 句型记忆库 - 功能演示")
    print("=" * 60)

    # 1. 初始化（自动填充种子数据）
    pm = PhraseMemory(filepath=tmp_path)
    print(f"\n[1] 初始化完成，已加载 {pm.stats()['total']} 个句型")
    print(f"    统计: {json.dumps(pm.stats(), ensure_ascii=False, indent=4)}")

    # 2. 搜索
    print("\n[2] 搜索 'name' (by=en):")
    for r in pm.search("name", by="en"):
        print(f"    {r['en_text']}  →  {r['zh_text']}  [{r['pinyin']}]")

    print("\n[3] 搜索 '吃' (by=zh):")
    for r in pm.search("吃", by="zh"):
        print(f"    {r['zh_text']}  →  {r['en_text']}  [{r['gloss']}]")

    # 3. 按功能分类
    print("\n[4] 获取 greetings 分类:")
    for r in pm.get_by_function("greetings"):
        print(f"    {r['zh_text']}  ({r['pinyin']})")

    # 4. 按等级
    a1_count = len(pm.get_by_level("A1"))
    print(f"\n[5] A1等级句型数量: {a1_count}")

    # 5. 句型复用：为 restaurant 主题查找可用句型
    print("\n[6] 为 'restaurant' 主题 (A1) 查找可复用句型:")
    matches = pm.find_matching("restaurant", "A1")
    for m in matches[:5]:
        print(f"    [{m['function']}] {m['zh_text']}  →  {m['en_text']}")

    # 6. 获取复用候选
    print("\n[7] 第6课的复用候选 (之前课次的句型):")
    candidates = pm.get_reuse_candidates(lesson_id=6, max_results=5)
    for c in candidates:
        print(f"    L{c['first_lesson_id']}: {c['zh_text']}  →  {c['en_text']}")

    # 7. 添加新句型
    new_id = pm.add_phrase(
        en_text="What time do we eat?",
        zh_text="我们几点吃饭？",
        pinyin="wǒmen jǐ diǎn chīfàn",
        gloss="we / how-many / o'clock / eat-rice",
        level="A1",
        function="food",
        first_lesson_id=9,
        status="draft",
    )
    print(f"\n[8] 新增句型 (draft): {new_id}")
    print(f"    {json.dumps(pm.get_phrase(new_id), ensure_ascii=False)}")

    # 8. 冲突解决
    food_phrases = pm.search("food", by="function")
    if len(food_phrases) >= 2:
        id1 = food_phrases[0]["phrase_id"]
        id2 = food_phrases[1]["phrase_id"]
        result = pm.resolve_conflict(id1, id2, strategy="primary_alias")
        print(f"\n[9] 冲突解决 ({id1} vs {id2}):")
        print(f"    主句型: {result['primary']['zh_text']}")
        print(f"    别名: {result['primary']['aliases']}")
        print(f"    次句型状态: {result['secondary']['status']}")

    # 9. 导出
    export_path = os.path.join(tmp_dir, "export_test.json")
    pm.export_json(export_path)
    print(f"\n[10] 已导出到: {export_path}")

    # 10. 最终统计
    print(f"\n最终统计: {json.dumps(pm.stats(), ensure_ascii=False, indent=2)}")
    print("\n" + "=" * 60)
    print("  演示完成！")
    print("=" * 60)

    # 清理
    os.remove(tmp_path)
    os.remove(export_path)
    os.rmdir(tmp_dir)


if __name__ == "__main__":
    demo()
