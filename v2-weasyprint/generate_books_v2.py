#!/usr/bin/env python3
"""
Z Turns Chinese — Markdown-to-PDF book generator v2.
Uses WeasyPrint (HTML → PDF) for professional Amazon KDP quality.
English text renders correctly via system fonts; Chinese via CJK fonts.
"""

import html
import os
import re
import sys
from pathlib import Path

from content_filter import ContentFilter

# ─────────────────────────────────────────────
# Content Policy — Z Turns Chinese Series
# ─────────────────────────────────────────────
# All books belong to the "Z Turns Chinese" series by Tony Sheng.
# The content filter enforces stricter teaching-safe replacements and
# unified branding / copyright metadata during content parsing.

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent  # v2-weasyprint root (scripts in 工具脚本/)
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

CONTENT_FILTER = ContentFilter(BASE_DIR / "content_filter_config.yaml")
CONTENT_POLICY_CONFIG = CONTENT_FILTER.config

COMPANY_WEBSITE = CONTENT_POLICY_CONFIG.get("COMPANY_WEBSITE", "https://zturnsgo.com/")
SERIES_NAME = "Z Turns Chinese"
DEFAULT_AUTHOR = CONTENT_POLICY_CONFIG.get("DEFAULT_AUTHOR", "Tony Sheng")
COPYRIGHT_HOLDER = CONTENT_POLICY_CONFIG.get("COPYRIGHT_HOLDER", SERIES_NAME)
COPYRIGHT_NOTICE = CONTENT_POLICY_CONFIG.get(
    "COPYRIGHT_NOTICE",
    f"版权所有 {COPYRIGHT_HOLDER}",
)
STRICT_MODE = bool(CONTENT_POLICY_CONFIG.get("STRICT_MODE", True))
ABORT_ON_BLOCKED_CONTENT = bool(
    CONTENT_POLICY_CONFIG.get("ABORT_ON_BLOCKED_CONTENT", False)
)


def sanitize_content(text: str, *, book_key: str, file_path: str) -> tuple[str, list[str]]:
    """Apply the shared content filter and optionally fail in strict mode."""
    sanitized_text, flagged_topics = CONTENT_FILTER.sanitize(
        text,
        book_key=book_key,
        file_path=file_path,
    )
    if flagged_topics and STRICT_MODE and ABORT_ON_BLOCKED_CONTENT:
        joined = ", ".join(flagged_topics)
        raise ValueError(f"Blocked content detected in {file_path}: {joined}")
    return sanitized_text, flagged_topics

# ─────────────────────────────────────────────
# Book metadata
# ─────────────────────────────────────────────
BOOKS = {
    "book1": {
        "title": "Z Turns Chinese",
        "subtitle": "From Zero — Your First Steps in Mandarin",
        "zh_title": "零基础入门",
        "author": "Tony Sheng",
        "color": "#1565C0",
        "output": "ZTurns_Book1_FromZero.pdf",
        "source_dirs": [
            "book1-fromzero/part1",
            "book1-fromzero/part2",
            "book1-fromzero/part3",
        ],
        "part_names": {
            "book1-fromzero/part1": "Part 1: Getting Started — 入门篇",
            "book1-fromzero/part2": "Part 2: Daily Life — 日常生活",
            "book1-fromzero/part3": "Part 3: Expanding Horizons — 拓展篇",
        },
    },
    "book2": {
        "title": "Z Turns Chinese",
        "subtitle": "The Complete Guide to Conversational Chinese",
        "zh_title": "完整会话中文指南",
        "author": "Tony Sheng",
        "color": "#009650",
        "output": "ZTurns_Book2_CompleteGuide.pdf",
        "source_dirs": [
            "book2-completeguide/part0-before-you-begin",
            "book2-completeguide/part1-sound-foundation",
            "book2-completeguide/part2-first-steps",
            "book2-completeguide/part3-daily-life",
            "book2-completeguide/part4-travel-adventure",
            "book2-completeguide/part5-business-chinese",
            "book2-completeguide/part6-living-in-china",
        ],
        "part_names": {
            "book2-completeguide/part0-before-you-begin": "Part 0: Before You Begin",
            "book2-completeguide/part1-sound-foundation": "Part 1: Sound Foundation",
            "book2-completeguide/part2-first-steps": "Part 2: First Steps",
            "book2-completeguide/part3-daily-life": "Part 3: Daily Life",
            "book2-completeguide/part4-travel-adventure": "Part 4: Travel & Adventure",
            "book2-completeguide/part5-business-chinese": "Part 5: Business Chinese",
            "book2-completeguide/part6-living-in-china": "Part 6: Living in China",
        },
    },
    "book3": {
        "title": "Z Turns Chinese",
        "subtitle": "Real Lessons from Real Classrooms",
        "zh_title": "真实课堂的真实课程",
        "author": "Tony Sheng",
        "color": "#B4321E",
        "output": "ZTurns_Book3_RealLessons.pdf",
        "source_dirs": [
            "book3-real-lessons/part1-daily-basics",
            "book3-real-lessons/part2-travel-stories",
            "book3-real-lessons/part3-culture-unlocked",
            "book3-real-lessons/part4-business-modern",
            "book3-real-lessons/part5-going-deeper",
            "book3-real-lessons/reviews",
        ],
        "part_names": {
            "book3-real-lessons/part1-daily-basics": "Part 1: Daily Basics",
            "book3-real-lessons/part2-travel-stories": "Part 2: Travel Stories",
            "book3-real-lessons/part3-culture-unlocked": "Part 3: Culture Unlocked",
            "book3-real-lessons/part4-business-modern": "Part 4: Business Modern",
            "book3-real-lessons/part5-going-deeper": "Part 5: Going Deeper",
            "book3-real-lessons/reviews": "Review Sections",
        },
    },
    "book4": {
        "title": "Z Turns Chinese",
        "subtitle": "Survival Chinese",
        "zh_title": "生存中文",
        "author": "Tony Sheng",
        "color": "#C87800",
        "output": "ZTurns_Book4_SurvivalChinese.pdf",
        "source_dirs": [
            "book4-survival-chinese/sec1-essentials",
            "book4-survival-chinese/sec2-eating",
            "book4-survival-chinese/sec3-transport",
            "book4-survival-chinese/sec4-money",
            "book4-survival-chinese/sec5-emergency",
        ],
        "part_names": {
            "book4-survival-chinese/sec1-essentials": "Section 1: Essentials",
            "book4-survival-chinese/sec2-eating": "Section 2: Eating",
            "book4-survival-chinese/sec3-transport": "Section 3: Transport",
            "book4-survival-chinese/sec4-money": "Section 4: Money",
            "book4-survival-chinese/sec5-emergency": "Section 5: Emergency",
        },
    },
    "book5": {
        "title": "Z Turns Chinese",
        "subtitle": "Business Chinese That Actually Works",
        "zh_title": "真正管用的商务中文",
        "author": "Tony Sheng",
        "color": "#643296",
        "output": "ZTurns_Book5_BusinessChinese.pdf",
        "source_dirs": [
            "book5-business-chinese/part1-first-30-days",
            "book5-business-chinese/part2-daily-work",
            "book5-business-chinese/part3-relationships",
            "book5-business-chinese/part4-deals-money",
            "book5-business-chinese/part5-career-growth",
        ],
        "part_names": {
            "book5-business-chinese/part1-first-30-days": "Part 1: First 30 Days",
            "book5-business-chinese/part2-daily-work": "Part 2: Daily Work",
            "book5-business-chinese/part3-relationships": "Part 3: Relationships",
            "book5-business-chinese/part4-deals-money": "Part 4: Deals & Money",
            "book5-business-chinese/part5-career-growth": "Part 5: Career Growth",
        },
    },
    "book6": {
        "title": "Z Turns Chinese",
        "subtitle": "Unlock Chinese Characters",
        "zh_title": "解码汉字",
        "author": "Tony Sheng",
        "color": "#1E64B4",
        "output": "ZTurns_Book6_Characters.pdf",
        "source_dirs": [
            "book6-characters/part1-system",
            "book6-characters/part2-essential-200",
            "book6-characters/part3-patterns",
            "book6-characters/part4-reading-real",
            "book6-characters/part5-beyond",
        ],
        "part_names": {
            "book6-characters/part1-system": "Part 1: The Character System",
            "book6-characters/part2-essential-200": "Part 2: Essential 200 Characters",
            "book6-characters/part3-patterns": "Part 3: Character Patterns",
            "book6-characters/part4-reading-real": "Part 4: Reading Real Chinese",
            "book6-characters/part5-beyond": "Part 5: Beyond Basics",
        },
    },
    "book7": {
        "title": "Z Turns Chinese",
        "subtitle": "Eat Your Way Through China",
        "zh_title": "吃遍中国",
        "author": "Tony Sheng",
        "color": "#C8321E",
        "output": "ZTurns_Book7_Food.pdf",
        "source_dirs": [
            "book7-food/part1-foundations",
            "book7-food/part2-street-food",
            "book7-food/part3-drinks",
            "book7-food/part4-regional",
            "book7-food/part5-food-life",
        ],
        "part_names": {
            "book7-food/part1-foundations": "Part 1: Food Foundations",
            "book7-food/part2-street-food": "Part 2: Street Food & Snacks",
            "book7-food/part3-drinks": "Part 3: Drinks & Beverages",
            "book7-food/part4-regional": "Part 4: Regional Deep Dives",
            "book7-food/part5-food-life": "Part 5: Food & Life",
        },
    },
    "book8": {
        "title": "Z Turns Chinese",
        "subtitle": "Digital China",
        "zh_title": "数字中国生存指南",
        "author": "Tony Sheng",
        "color": "#0078C8",
        "output": "ZTurns_Book8_DigitalChina.pdf",
        "source_dirs": [
            "book8-digital/sec1-essentials",
            "book8-digital/sec2-shopping",
            "book8-digital/sec3-social-media",
            "book8-digital/sec4-life-apps",
            "book8-digital/sec5-digital-culture",
        ],
        "part_names": {
            "book8-digital/sec1-essentials": "Section 1: Digital Essentials",
            "book8-digital/sec2-shopping": "Section 2: Shopping & Delivery",
            "book8-digital/sec3-social-media": "Section 3: Social Media",
            "book8-digital/sec4-life-apps": "Section 4: Life Apps",
            "book8-digital/sec5-digital-culture": "Section 5: Digital Culture",
        },
    },
    "book9": {
        "title": "Z Turns Chinese",
        "subtitle": "Chinese Through Stories",
        "zh_title": "故事里的中国",
        "author": "Tony Sheng",
        "color": "#96501E",
        "output": "ZTurns_Book9_Stories.pdf",
        "source_dirs": [
            "book9-stories/part1-legends",
            "book9-stories/part2-history",
            "book9-stories/part3-folk-tales",
            "book9-stories/part4-modern",
            "book9-stories/part5-your-story",
        ],
        "part_names": {
            "book9-stories/part1-legends": "Part 1: Ancient Legends",
            "book9-stories/part2-history": "Part 2: Historical Stories",
            "book9-stories/part3-folk-tales": "Part 3: Folk Tales & Wisdom",
            "book9-stories/part4-modern": "Part 4: Modern Stories",
            "book9-stories/part5-your-story": "Part 5: Your Story",
        },
    },
    "book10": {
        "title": "Z Turns Chinese",
        "subtitle": "Love, Family & Social Life in China",
        "zh_title": "中国人的社交密码",
        "author": "Tony Sheng",
        "color": "#C85078",
        "output": "ZTurns_Book10_SocialLife.pdf",
        "source_dirs": [
            "book10-social/part1-meeting-people",
            "book10-social/part2-dating",
            "book10-social/part3-family",
            "book10-social/part4-social-rules",
            "book10-social/part5-belonging",
        ],
        "part_names": {
            "book10-social/part1-meeting-people": "Part 1: Meeting People",
            "book10-social/part2-dating": "Part 2: Dating & Romance",
            "book10-social/part3-family": "Part 3: Family Life",
            "book10-social/part4-social-rules": "Part 4: Social Rules",
            "book10-social/part5-belonging": "Part 5: Belonging",
        },
    },
    "book11": {
        "title": "Z Turns Chinese",
        "subtitle": "Talk About AI, Robots & the Future in Chinese",
        "zh_title": "AI与未来科技",
        "author": "Tony Sheng",
        "color": "#1A1A2E",
        "output": "ZTurns_Book11_AITech.pdf",
        "source_dirs": [
            "book11-ai-tech/part1",
            "book11-ai-tech/part2",
            "book11-ai-tech/part3",
            "book11-ai-tech/part4",
            "book11-ai-tech/part5",
        ],
        "part_names": {
            "book11-ai-tech/part1": "Part 1: AI 基础概念 — 什么是人工智能",
            "book11-ai-tech/part2": "Part 2: 中国 AI 产业 — 弯道超车",
            "book11-ai-tech/part3": "Part 3: 机器人与硬件 — 具身智能时代",
            "book11-ai-tech/part4": "Part 4: AI 工具实战 — 用中文玩 AI",
            "book11-ai-tech/part5": "Part 5: AI 与未来 — 我们往哪里去",
        },
    },
    "book12": {
        "title": "Z Turns Chinese",
        "subtitle": "Livestream Shopping, Electric Cars & the Startup Revolution",
        "zh_title": "中国新经济密码",
        "author": "Tony Sheng",
        "color": "#E63946",
        "output": "ZTurns_Book12_NewEconomy.pdf",
        "source_dirs": [
            "book12-new-economy/part1",
            "book12-new-economy/part2",
            "book12-new-economy/part3",
            "book12-new-economy/part4",
            "book12-new-economy/part5",
        ],
        "part_names": {
            "book12-new-economy/part1": "Part 1: 直播与电商 — 买买买的革命",
            "book12-new-economy/part2": "Part 2: 新能源与出行 — 绿色中国",
            "book12-new-economy/part3": "Part 3: 创业与投资 — 中国创业密码",
            "book12-new-economy/part4": "Part 4: 产业与贸易 — 世界工厂升级",
            "book12-new-economy/part5": "Part 5: 经济热词 — 读懂中国经济",
        },
    },
    "book13": {
        "title": "Z Turns Chinese",
        "subtitle": "C-Drama, Gaming, Music & Everything Young China Loves",
        "zh_title": "中国流行文化",
        "author": "Tony Sheng",
        "color": "#FF6B9D",
        "output": "ZTurns_Book13_PopCulture.pdf",
        "source_dirs": [
            "book13-pop-culture/part1",
            "book13-pop-culture/part2",
            "book13-pop-culture/part3",
            "book13-pop-culture/part4",
            "book13-pop-culture/part5",
        ],
        "part_names": {
            "book13-pop-culture/part1": "Part 1: 追剧文化 — 中国影视",
            "book13-pop-culture/part2": "Part 2: 游戏世界 — 中国游戏",
            "book13-pop-culture/part3": "Part 3: 音乐与偶像 — 中国音乐",
            "book13-pop-culture/part4": "Part 4: 潮流生活 — 年轻中国",
            "book13-pop-culture/part5": "Part 5: 内容创作 — 人人都是创作者",
        },
    },
    "book14": {
        "title": "Z Turns Chinese",
        "subtitle": "Kung Fu, E-Sports, Extreme Sports & the Chinese Athletic Spirit",
        "zh_title": "武术体育与冒险",
        "author": "Tony Sheng",
        "color": "#FF8C00",
        "output": "ZTurns_Book14_Sports.pdf",
        "source_dirs": [
            "book14-sports/part1",
            "book14-sports/part2",
            "book14-sports/part3",
            "book14-sports/part4",
            "book14-sports/part5",
        ],
        "part_names": {
            "book14-sports/part1": "Part 1: 中国武术 — 功夫的世界",
            "book14-sports/part2": "Part 2: 现代体育 — 竞技中国",
            "book14-sports/part3": "Part 3: 极限运动 — 冒险精神",
            "book14-sports/part4": "Part 4: 电子竞技 — 数字运动",
            "book14-sports/part5": "Part 5: 健身与户外 — 健康生活",
        },
    },
    "book15": {
        "title": "Z Turns Chinese",
        "subtitle": "Gaokao, Tiger Parents, Cram Schools & the Education Revolution",
        "zh_title": "中国教育内幕",
        "author": "Tony Sheng",
        "color": "#2D6A4F",
        "output": "ZTurns_Book15_Education.pdf",
        "source_dirs": [
            "book15-education/part1",
            "book15-education/part2",
            "book15-education/part3",
            "book15-education/part4",
            "book15-education/part5",
        ],
        "part_names": {
            "book15-education/part1": "Part 1: 教育体系 — 从幼儿园到大学",
            "book15-education/part2": "Part 2: 家庭教育 — 鸡娃与减负",
            "book15-education/part3": "Part 3: 考试文化 — 一考定终身？",
            "book15-education/part4": "Part 4: 教育热点 — 2026教育变革",
            "book15-education/part5": "Part 5: 教育文化 — 尊师重道",
        },
    },
    "book16": {
        "title": "Z Turns Chinese",
        "subtitle": "A City-by-City Guide to Living, Working & Exploring China",
        "zh_title": "走遍中国城市",
        "author": "Tony Sheng",
        "color": "#457B9D",
        "output": "ZTurns_Book16_Cities.pdf",
        "source_dirs": [
            "book16-cities/part1",
            "book16-cities/part2",
            "book16-cities/part3",
            "book16-cities/part4",
            "book16-cities/part5",
        ],
        "part_names": {
            "book16-cities/part1": "Part 1: 一线城市 — 超级都市",
            "book16-cities/part2": "Part 2: 新一线城市 — 崛起中的力量",
            "book16-cities/part3": "Part 3: 特色城市 — 每座城都有个性",
            "book16-cities/part4": "Part 4: 城市生活 — 在中国城市生存",
            "book16-cities/part5": "Part 5: 城市文化 — 读懂城市性格",
        },
    },
    "book17": {
        "title": "Z Turns Chinese",
        "subtitle": "Traditional Medicine, Hospital Survival & the Art of 养生",
        "zh_title": "中国健康养生",
        "author": "Tony Sheng",
        "color": "#52B788",
        "output": "ZTurns_Book17_Health.pdf",
        "source_dirs": [
            "book17-health/part1",
            "book17-health/part2",
            "book17-health/part3",
            "book17-health/part4",
            "book17-health/part5",
        ],
        "part_names": {
            "book17-health/part1": "Part 1: 中医基础 — 千年智慧",
            "book17-health/part2": "Part 2: 看病指南 — 医院生存",
            "book17-health/part3": "Part 3: 心理健康 — 看不见的伤",
            "book17-health/part4": "Part 4: 养生文化 — 中国式健康",
            "book17-health/part5": "Part 5: 现代健康 — 2026健康趋势",
        },
    },
    "book18": {
        "title": "Z Turns Chinese",
        "subtitle": "Understand Headlines, Political Terms & Current Events in Chinese",
        "zh_title": "读懂中国新闻",
        "author": "Tony Sheng",
        "color": "#264653",
        "output": "ZTurns_Book18_News.pdf",
        "source_dirs": [
            "book18-news/part1",
            "book18-news/part2",
            "book18-news/part3",
            "book18-news/part4",
            "book18-news/part5",
        ],
        "part_names": {
            "book18-news/part1": "Part 1: 新闻阅读基础 — 看懂标题",
            "book18-news/part2": "Part 2: 中国政治 — 读懂体制",
            "book18-news/part3": "Part 3: 经济新闻 — 读懂数据",
            "book18-news/part4": "Part 4: 社会新闻 — 读懂民生",
            "book18-news/part5": "Part 5: 国际视角 — 中国与世界",
        },
    },
    "book19": {
        "title": "Z Turns Chinese",
        "subtitle": "Mountains, Rivers, National Parks & Environmental Chinese",
        "zh_title": "中国自然奇观",
        "author": "Tony Sheng",
        "color": "#2D6A4F",
        "output": "ZTurns_Book19_Nature.pdf",
        "source_dirs": [
            "book19-nature/part1",
            "book19-nature/part2",
            "book19-nature/part3",
            "book19-nature/part4",
            "book19-nature/part5",
        ],
        "part_names": {
            "book19-nature/part1": "Part 1: 中国地理 — 壮丽山河",
            "book19-nature/part2": "Part 2: 国家公园 — 自然宝藏",
            "book19-nature/part3": "Part 3: 四季与节气 — 天人合一",
            "book19-nature/part4": "Part 4: 环保 — 绿色中国",
            "book19-nature/part5": "Part 5: 自然生活 — 亲近自然",
        },
    },
    "book20": {
        "title": "Z Turns Chinese",
        "subtitle": "Jokes, Puns, Cross-Talk & the Art of Being Funny in Chinese",
        "zh_title": "中文幽默与文字游戏",
        "author": "Tony Sheng",
        "color": "#FFB703",
        "output": "ZTurns_Book20_Humor.pdf",
        "source_dirs": [
            "book20-humor/part1",
            "book20-humor/part2",
            "book20-humor/part3",
            "book20-humor/part4",
            "book20-humor/part5",
        ],
        "part_names": {
            "book20-humor/part1": "Part 1: 中国幽默入门 — 什么是好笑",
            "book20-humor/part2": "Part 2: 传统幽默 — 千年笑声",
            "book20-humor/part3": "Part 3: 现代幽默 — 2026的笑",
            "book20-humor/part4": "Part 4: 中文文字游戏 — 玩转中文",
            "book20-humor/part5": "Part 5: 用幽默交朋友 — 实战",
        },
    },
    "book21": {
        "title": "Z Turns Chinese",
        "subtitle": "The Ultimate Step-by-Step Guide to Essential Chinese Apps",
        "zh_title": "中国App全攻略",
        "author": "Tony Sheng",
        "color": "#00C853",
        "output": "ZTurns_Book21_Apps.pdf",
        "source_dirs": ["book21-apps/part1", "book21-apps/part2", "book21-apps/part3", "book21-apps/part4", "book21-apps/part5"],
        "part_names": {
            "book21-apps/part1": "Part 1: 生存必装 — 没有这些寸步难行",
            "book21-apps/part2": "Part 2: 吃喝玩乐 — 享受生活",
            "book21-apps/part3": "Part 3: 社交与内容 — 融入中国",
            "book21-apps/part4": "Part 4: 生活服务 — 日常刚需",
            "book21-apps/part5": "Part 5: 进阶与AI — 效率提升",
        },
    },
    "book22": {
        "title": "Z Turns Chinese",
        "subtitle": "Every Festival, Every Tradition, Every Story Behind the Celebration",
        "zh_title": "中国节日全书",
        "author": "Tony Sheng",
        "color": "#D32F2F",
        "output": "ZTurns_Book22_Festivals.pdf",
        "source_dirs": ["book22-festivals/part1", "book22-festivals/part2", "book22-festivals/part3", "book22-festivals/part4", "book22-festivals/part5"],
        "part_names": {
            "book22-festivals/part1": "Part 1: 春节 — 中国第一大节",
            "book22-festivals/part2": "Part 2: 春夏节日 — 万物复苏到热浪",
            "book22-festivals/part3": "Part 3: 秋冬节日 — 丰收到团圆",
            "book22-festivals/part4": "Part 4: 现代节日与洋节 — 中国特色的过法",
            "book22-festivals/part5": "Part 5: 节日文化 — 深层解读",
        },
    },
    "book23": {
        "title": "Z Turns Chinese",
        "subtitle": "Visas, Work Permits, Tenant Rights & Staying Legal in China",
        "zh_title": "外国人在华法律指南",
        "author": "Tony Sheng",
        "color": "#1565C0",
        "output": "ZTurns_Book23_Law.pdf",
        "source_dirs": ["book23-law/part1", "book23-law/part2", "book23-law/part3", "book23-law/part4", "book23-law/part5"],
        "part_names": {
            "book23-law/part1": "Part 1: 签证与入境",
            "book23-law/part2": "Part 2: 工作与就业",
            "book23-law/part3": "Part 3: 住房与消费",
            "book23-law/part4": "Part 4: 日常法律",
            "book23-law/part5": "Part 5: 权利与资源",
        },
    },
    "book24": {
        "title": "Z Turns Chinese",
        "subtitle": "Renting, Furnishing, Neighbors & Making China Feel Like Home",
        "zh_title": "在中国安家",
        "author": "Tony Sheng",
        "color": "#795548",
        "output": "ZTurns_Book24_Home.pdf",
        "source_dirs": ["book24-home/part1", "book24-home/part2", "book24-home/part3", "book24-home/part4", "book24-home/part5"],
        "part_names": {
            "book24-home/part1": "Part 1: 找房子",
            "book24-home/part2": "Part 2: 搬进去",
            "book24-home/part3": "Part 3: 日常生活",
            "book24-home/part4": "Part 4: 安家深度",
            "book24-home/part5": "Part 5: 让中国成为家",
        },
    },
    "book25": {
        "title": "Z Turns Chinese",
        "subtitle": "Boomers, Gen X, Millennials & Gen Z — Understanding Every Generation",
        "zh_title": "中国代际密码",
        "author": "Tony Sheng",
        "color": "#9C27B0",
        "output": "ZTurns_Book25_Generations.pdf",
        "source_dirs": ["book25-generations/part1", "book25-generations/part2", "book25-generations/part3", "book25-generations/part4", "book25-generations/part5"],
        "part_names": {
            "book25-generations/part1": "Part 1: 老一代 — 吃过苦的人",
            "book25-generations/part2": "Part 2: 中间代 — 承上启下",
            "book25-generations/part3": "Part 3: 新一代 — 数字原住民",
            "book25-generations/part4": "Part 4: 代际冲突 — 碰撞与融合",
            "book25-generations/part5": "Part 5: 理解代际 — 文化密码",
        },
    },
    "book26": {
        "title": "Z Turns Chinese",
        "subtitle": "200 Essential Four-Character Idioms with Stories & Usage",
        "zh_title": "成语大师",
        "author": "Tony Sheng",
        "color": "#4E342E",
        "output": "ZTurns_Book26_Chengyu.pdf",
        "source_dirs": ["book26-chengyu/part1", "book26-chengyu/part2", "book26-chengyu/part3", "book26-chengyu/part4", "book26-chengyu/part5"],
        "part_names": {
            "book26-chengyu/part1": "Part 1: 日常高频成语",
            "book26-chengyu/part2": "Part 2: 历史故事成语",
            "book26-chengyu/part3": "Part 3: 商务与职场成语",
            "book26-chengyu/part4": "Part 4: 智慧与哲理成语",
            "book26-chengyu/part5": "Part 5: 成语实战",
        },
    },
    "book27": {
        "title": "Z Turns Chinese",
        "subtitle": "Cantonese, Shanghainese, Sichuanese & Beyond",
        "zh_title": "方言探秘",
        "author": "Tony Sheng",
        "color": "#F57C00",
        "output": "ZTurns_Book27_Dialects.pdf",
        "source_dirs": ["book27-dialects/part1", "book27-dialects/part2", "book27-dialects/part3", "book27-dialects/part4", "book27-dialects/part5"],
        "part_names": {
            "book27-dialects/part1": "Part 1: 方言地图 — 中国有多少种话",
            "book27-dialects/part2": "Part 2: 四大方言速成",
            "book27-dialects/part3": "Part 3: 地方特色表达",
            "book27-dialects/part4": "Part 4: 方言与文化",
            "book27-dialects/part5": "Part 5: 方言生存",
        },
    },
    "book28": {
        "title": "Z Turns Chinese",
        "subtitle": "Read Ancient Chinese Texts, Poems & Proverbs",
        "zh_title": "文言文入门",
        "author": "Tony Sheng",
        "color": "#3E2723",
        "output": "ZTurns_Book28_Classical.pdf",
        "source_dirs": ["book28-classical/part1", "book28-classical/part2", "book28-classical/part3", "book28-classical/part4", "book28-classical/part5"],
        "part_names": {
            "book28-classical/part1": "Part 1: 文言文基础",
            "book28-classical/part2": "Part 2: 经典名句",
            "book28-classical/part3": "Part 3: 实用文言文",
            "book28-classical/part4": "Part 4: 名篇赏析",
            "book28-classical/part5": "Part 5: 文言文与现代",
        },
    },
    "book29": {
        "title": "Z Turns Chinese",
        "subtitle": "Professional Emails, Reports, Proposals & Formal Chinese",
        "zh_title": "中文商务写作",
        "author": "Tony Sheng",
        "color": "#37474F",
        "output": "ZTurns_Book29_BusinessWriting.pdf",
        "source_dirs": ["book29-business-writing/part1", "book29-business-writing/part2", "book29-business-writing/part3", "book29-business-writing/part4", "book29-business-writing/part5"],
        "part_names": {
            "book29-business-writing/part1": "Part 1: 商务邮件",
            "book29-business-writing/part2": "Part 2: 即时通讯",
            "book29-business-writing/part3": "Part 3: 报告与提案",
            "book29-business-writing/part4": "Part 4: 合同与法务",
            "book29-business-writing/part5": "Part 5: 高阶写作",
        },
    },
    "book30": {
        "title": "Z Turns Chinese",
        "subtitle": "Memes, Slang, Emoji & the Language of Chinese Internet",
        "zh_title": "中国网络语言",
        "author": "Tony Sheng",
        "color": "#E040FB",
        "output": "ZTurns_Book30_InternetLanguage.pdf",
        "source_dirs": ["book30-internet-language/part1", "book30-internet-language/part2", "book30-internet-language/part3", "book30-internet-language/part4", "book30-internet-language/part5"],
        "part_names": {
            "book30-internet-language/part1": "Part 1: 网络语言基础",
            "book30-internet-language/part2": "Part 2: 年度热词",
            "book30-internet-language/part3": "Part 3: 平台专属语言",
            "book30-internet-language/part4": "Part 4: 网络文化现象",
            "book30-internet-language/part5": "Part 5: 创造与使用",
        },
    },
    "book31": {
        "title": "Z Turns Chinese", "subtitle": "Confucianism, Daoism, Buddhism & the Ideas That Built China",
        "zh_title": "中国哲学思想", "author": "Tony Sheng", "color": "#5D4037",
        "output": "ZTurns_Book31_Philosophy.pdf",
        "source_dirs": [f"book31-philosophy/part{i}" for i in range(1,6)],
        "part_names": {"book31-philosophy/part1":"Part 1: 儒家 — 中国社会的基石","book31-philosophy/part2":"Part 2: 道家 — 无为而治","book31-philosophy/part3":"Part 3: 佛学 — 东方智慧","book31-philosophy/part4":"Part 4: 诸子百家 — 百花齐放","book31-philosophy/part5":"Part 5: 哲学与生活"},
    },
    "book32": {
        "title": "Z Turns Chinese", "subtitle": "Tea Ceremony, Baijiu, Beer & the Art of Chinese Drinking",
        "zh_title": "中国茶酒文化", "author": "Tony Sheng", "color": "#33691E",
        "output": "ZTurns_Book32_TeaDrinking.pdf",
        "source_dirs": [f"book32-tea-drinking/part{i}" for i in range(1,6)],
        "part_names": {"book32-tea-drinking/part1":"Part 1: 茶 — 中国的灵魂饮品","book32-tea-drinking/part2":"Part 2: 酒 — 感情的润滑剂","book32-tea-drinking/part3":"Part 3: 茶馆与酒局","book32-tea-drinking/part4":"Part 4: 现代饮品","book32-tea-drinking/part5":"Part 5: 饮品文化"},
    },
    "book33": {
        "title": "Z Turns Chinese", "subtitle": "Brush Calligraphy, Ink Painting, Paper Cutting & Traditional Crafts",
        "zh_title": "中国艺术", "author": "Tony Sheng", "color": "#880E4F",
        "output": "ZTurns_Book33_Art.pdf",
        "source_dirs": [f"book33-art/part{i}" for i in range(1,6)],
        "part_names": {"book33-art/part1":"Part 1: 书法 — 文字即艺术","book33-art/part2":"Part 2: 国画 — 水墨世界","book33-art/part3":"Part 3: 手工艺 — 匠心独运","book33-art/part4":"Part 4: 表演艺术","book33-art/part5":"Part 5: 艺术与生活"},
    },
    "book34": {
        "title": "Z Turns Chinese", "subtitle": "Palaces, Temples, Gardens, Hutongs & the Modern Skyline",
        "zh_title": "中国建筑", "author": "Tony Sheng", "color": "#BF360C",
        "output": "ZTurns_Book34_Architecture.pdf",
        "source_dirs": [f"book34-architecture/part{i}" for i in range(1,6)],
        "part_names": {"book34-architecture/part1":"Part 1: 传统建筑","book34-architecture/part2":"Part 2: 民居建筑","book34-architecture/part3":"Part 3: 现代建筑","book34-architecture/part4":"Part 4: 建筑文化","book34-architecture/part5":"Part 5: 建筑与生活"},
    },
    "book35": {
        "title": "Z Turns Chinese", "subtitle": "Buddhism, Daoism, Folk Religion & Spiritual Life in China",
        "zh_title": "中国宗教信仰", "author": "Tony Sheng", "color": "#F9A825",
        "output": "ZTurns_Book35_Religion.pdf",
        "source_dirs": [f"book35-religion/part{i}" for i in range(1,6)],
        "part_names": {"book35-religion/part1":"Part 1: 中国宗教概览","book35-religion/part2":"Part 2: 宗教场所","book35-religion/part3":"Part 3: 宗教实践","book35-religion/part4":"Part 4: 信仰与生活","book35-religion/part5":"Part 5: 当代信仰"},
    },
    "book36": {
        "title": "Z Turns Chinese", "subtitle": "Matchmaking, Betrothal Gifts, Wedding Banquets & Modern Love",
        "zh_title": "中国婚俗", "author": "Tony Sheng", "color": "#C62828",
        "output": "ZTurns_Book36_Wedding.pdf",
        "source_dirs": [f"book36-wedding/part{i}" for i in range(1,6)],
        "part_names": {"book36-wedding/part1":"Part 1: 从认识到交往","book36-wedding/part2":"Part 2: 订婚与准备","book36-wedding/part3":"Part 3: 婚礼","book36-wedding/part4":"Part 4: 婚后生活","book36-wedding/part5":"Part 5: 婚姻文化"},
    },
    "book37": {
        "title": "Z Turns Chinese", "subtitle": "Lucky Numbers, Feng Shui, Zodiac & the Hidden Rules of Chinese Life",
        "zh_title": "中国迷信与风水", "author": "Tony Sheng", "color": "#FF6F00",
        "output": "ZTurns_Book37_Superstitions.pdf",
        "source_dirs": [f"book37-superstitions/part{i}" for i in range(1,6)],
        "part_names": {"book37-superstitions/part1":"Part 1: 数字与运气","book37-superstitions/part2":"Part 2: 颜色与象征","book37-superstitions/part3":"Part 3: 风水基础","book37-superstitions/part4":"Part 4: 生肖与命理","book37-superstitions/part5":"Part 5: 日常迷信"},
    },
    "book38": {
        "title": "Z Turns Chinese", "subtitle": "Beyond Han Chinese — Discover China's Ethnic Diversity",
        "zh_title": "56个民族", "author": "Tony Sheng", "color": "#00695C",
        "output": "ZTurns_Book38_Ethnic.pdf",
        "source_dirs": [f"book38-ethnic/part{i}" for i in range(1,6)],
        "part_names": {"book38-ethnic/part1":"Part 1: 民族概览","book38-ethnic/part2":"Part 2: 北方与西部民族","book38-ethnic/part3":"Part 3: 南方与西南民族","book38-ethnic/part4":"Part 4: 民族文化","book38-ethnic/part5":"Part 5: 民族与当代"},
    },
    "book39": {
        "title": "Z Turns Chinese", "subtitle": "Rural Life, Farming, Village Culture & the New Countryside",
        "zh_title": "中国乡村", "author": "Tony Sheng", "color": "#558B2F",
        "output": "ZTurns_Book39_Countryside.pdf",
        "source_dirs": [f"book39-countryside/part{i}" for i in range(1,6)],
        "part_names": {"book39-countryside/part1":"Part 1: 乡村风貌","book39-countryside/part2":"Part 2: 人与关系","book39-countryside/part3":"Part 3: 乡村美食","book39-countryside/part4":"Part 4: 变化中的乡村","book39-countryside/part5":"Part 5: 乡愁"},
    },
    "book40": {
        "title": "Z Turns Chinese", "subtitle": "Face, Guanxi, Gift-Giving & the Unwritten Rules of Chinese Society",
        "zh_title": "中国社交礼仪", "author": "Tony Sheng", "color": "#AD1457",
        "output": "ZTurns_Book40_Etiquette.pdf",
        "source_dirs": [f"book40-etiquette/part{i}" for i in range(1,6)],
        "part_names": {"book40-etiquette/part1":"Part 1: 核心概念","book40-etiquette/part2":"Part 2: 日常礼仪","book40-etiquette/part3":"Part 3: 场合礼仪","book40-etiquette/part4":"Part 4: 沟通礼仪","book40-etiquette/part5":"Part 5: 礼仪智慧"},
    },
    "book41": {
        "title": "Z Turns Chinese", "subtitle": "From the Yellow Emperor to Modern China in 25 Chapters",
        "zh_title": "中国朝代简史", "author": "Tony Sheng", "color": "#4A148C",
        "output": "ZTurns_Book41_DynastyHistory.pdf",
        "source_dirs": [f"book41-dynasty-history/part{i}" for i in range(1,6)],
        "part_names": {"book41-dynasty-history/part1":"Part 1: 远古到统一","book41-dynasty-history/part2":"Part 2: 分裂与融合","book41-dynasty-history/part3":"Part 3: 繁荣与变革","book41-dynasty-history/part4":"Part 4: 近现代","book41-dynasty-history/part5":"Part 5: 历史与今天"},
    },
    "book42": {
        "title": "Z Turns Chinese", "subtitle": "Gods, Ghosts, Dragons & the Supernatural World of Chinese Folklore",
        "zh_title": "中国神话与民间传说", "author": "Tony Sheng", "color": "#311B92",
        "output": "ZTurns_Book42_Mythology.pdf",
        "source_dirs": [f"book42-mythology-folklore/part{i}" for i in range(1,6)],
        "part_names": {"book42-mythology-folklore/part1":"Part 1: 创世神话","book42-mythology-folklore/part2":"Part 2: 神仙世界","book42-mythology-folklore/part3":"Part 3: 经典传说","book42-mythology-folklore/part4":"Part 4: 鬼怪与奇谈","book42-mythology-folklore/part5":"Part 5: 神话与今天"},
    },
    "book43": {
        "title": "Z Turns Chinese", "subtitle": "Ancient Inventions, Modern Tech & China's Innovation DNA",
        "zh_title": "中国发明", "author": "Tony Sheng", "color": "#0D47A1",
        "output": "ZTurns_Book43_Inventions.pdf",
        "source_dirs": [f"book43-inventions-innovation/part{i}" for i in range(1,6)],
        "part_names": {"book43-inventions-innovation/part1":"Part 1: 四大发明","book43-inventions-innovation/part2":"Part 2: 古代发明","book43-inventions-innovation/part3":"Part 3: 近代创新","book43-inventions-innovation/part4":"Part 4: 当代科技","book43-inventions-innovation/part5":"Part 5: 创新文化"},
    },
    "book44": {
        "title": "Z Turns Chinese", "subtitle": "Ancient Trade Routes, Cultural Exchange & the Belt and Road",
        "zh_title": "丝绸之路", "author": "Tony Sheng", "color": "#E65100",
        "output": "ZTurns_Book44_SilkRoad.pdf",
        "source_dirs": [f"book44-silk-road/part{i}" for i in range(1,6)],
        "part_names": {"book44-silk-road/part1":"Part 1: 古代丝绸之路","book44-silk-road/part2":"Part 2: 丝路城市","book44-silk-road/part3":"Part 3: 文化遗产","book44-silk-road/part4":"Part 4: 一带一路","book44-silk-road/part5":"Part 5: 丝路文化"},
    },
    "book45": {
        "title": "Z Turns Chinese", "subtitle": "Military Strategy, Business Tactics & the Chinese Way of Winning",
        "zh_title": "孙子兵法与中国战略", "author": "Tony Sheng", "color": "#B71C1C",
        "output": "ZTurns_Book45_ArtOfWar.pdf",
        "source_dirs": [f"book45-art-of-war/part{i}" for i in range(1,6)],
        "part_names": {"book45-art-of-war/part1":"Part 1: 孙子兵法","book45-art-of-war/part2":"Part 2: 三十六计","book45-art-of-war/part3":"Part 3: 历史战争","book45-art-of-war/part4":"Part 4: 策略思维","book45-art-of-war/part5":"Part 5: 战略文化"},
    },
    "book46": {
        "title": "Z Turns Chinese", "subtitle": "How Chinese Companies Conquered the World — And the Chinese to Talk About It",
        "zh_title": "中国品牌出海", "author": "Tony Sheng", "color": "#1B5E20",
        "output": "ZTurns_Book46_BrandsGlobal.pdf",
        "source_dirs": [f"book46-brands-global/part{i}" for i in range(1,6)],
        "part_names": {"book46-brands-global/part1":"Part 1: 出海先锋","book46-brands-global/part2":"Part 2: 行业出海","book46-brands-global/part3":"Part 3: 出海挑战","book46-brands-global/part4":"Part 4: 出海实战","book46-brands-global/part5":"Part 5: 出海未来"},
    },
    "book47": {
        "title": "Z Turns Chinese", "subtitle": "Space Stations, Moon Missions, Quantum Computing & Big Science",
        "zh_title": "中国航天与前沿科技", "author": "Tony Sheng", "color": "#0D47A1",
        "output": "ZTurns_Book47_SpaceScience.pdf",
        "source_dirs": [f"book47-space-science/part{i}" for i in range(1,6)],
        "part_names": {"book47-space-science/part1":"Part 1: 中国航天","book47-space-science/part2":"Part 2: 芯片与计算","book47-space-science/part3":"Part 3: 生命科学","book47-space-science/part4":"Part 4: 深海与极地","book47-space-science/part5":"Part 5: 科学文化"},
    },
    "book48": {
        "title": "Z Turns Chinese", "subtitle": "Box Office, Streaming, Short Drama & the Business of Chinese Entertainment",
        "zh_title": "中国影视产业", "author": "Tony Sheng", "color": "#880E4F",
        "output": "ZTurns_Book48_FilmEntertainment.pdf",
        "source_dirs": [f"book48-film-entertainment/part{i}" for i in range(1,6)],
        "part_names": {"book48-film-entertainment/part1":"Part 1: 电影产业","book48-film-entertainment/part2":"Part 2: 电视与流媒体","book48-film-entertainment/part3":"Part 3: 短剧与新媒体","book48-film-entertainment/part4":"Part 4: 幕后产业","book48-film-entertainment/part5":"Part 5: 产业未来"},
    },
    "book49": {
        "title": "Z Turns Chinese", "subtitle": "Mahjong, Go, Chinese Chess & the Games That Define Chinese Culture",
        "zh_title": "中国传统游戏", "author": "Tony Sheng", "color": "#1A237E",
        "output": "ZTurns_Book49_TraditionalGames.pdf",
        "source_dirs": [f"book49-traditional-games/part{i}" for i in range(1,6)],
        "part_names": {"book49-traditional-games/part1":"Part 1: 麻将 — 国粹","book49-traditional-games/part2":"Part 2: 围棋 — 黑白世界","book49-traditional-games/part3":"Part 3: 象棋 — 楚河汉界","book49-traditional-games/part4":"Part 4: 其他游戏","book49-traditional-games/part5":"Part 5: 游戏文化"},
    },
    "book50": {
        "title": "Z Turns Chinese", "subtitle": "Zodiac Animals, Fortune Telling, Birth Charts & the Chinese Way of Fate",
        "zh_title": "生肖命理", "author": "Tony Sheng", "color": "#FF6F00",
        "output": "ZTurns_Book50_ZodiacFortune.pdf",
        "source_dirs": [f"book50-zodiac-fortune/part{i}" for i in range(1,6)],
        "part_names": {"book50-zodiac-fortune/part1":"Part 1: 十二生肖","book50-zodiac-fortune/part2":"Part 2: 生肖性格","book50-zodiac-fortune/part3":"Part 3: 中国命理学","book50-zodiac-fortune/part4":"Part 4: 占卜与预测","book50-zodiac-fortune/part5":"Part 5: 命运文化"},
    },
    # ─────────────────────────────────────────────
    # HSK 3.0 Exam Prep Guides (2026 Latest Edition)
    # ─────────────────────────────────────────────
    "hsk1": {
        "title": "HSK 备考完全指南", "subtitle": "初等·入门篇 — 一级 Complete Prep Guide",
        "zh_title": "HSK 1级备考", "author": "Tony Sheng", "color": "#1565C0",
        "output": "ZTurns_HSK1_Prep.pdf",
        "source_dirs": [
            "HSK备考/hsk1-prep/part0-exam-overview",
            "HSK备考/hsk1-prep/part1-pinyin",
            "HSK备考/hsk1-prep/part2-vocabulary-grammar",
            "HSK备考/hsk1-prep/part3-listening",
            "HSK备考/hsk1-prep/part4-reading",
            "HSK备考/hsk1-prep/part5-exam-tips",
            "HSK备考/hsk1-prep/part6-mock-exams",
            "HSK备考/hsk1-prep/appendices",
        ],
        "part_names": {
            "HSK备考/hsk1-prep/part0-exam-overview": "Part 0: 考试总览与备考策略",
            "HSK备考/hsk1-prep/part1-pinyin": "Part 1: 拼音与声调基础",
            "HSK备考/hsk1-prep/part2-vocabulary-grammar": "Part 2: 核心词汇与语法",
            "HSK备考/hsk1-prep/part3-listening": "Part 3: 听力专项突破",
            "HSK备考/hsk1-prep/part4-reading": "Part 4: 阅读专项突破",
            "HSK备考/hsk1-prep/part5-exam-tips": "Part 5: 考点精讲与易错点",
            "HSK备考/hsk1-prep/part6-mock-exams": "Part 6: 全真模拟试卷",
            "HSK备考/hsk1-prep/appendices": "附录",
        },
    },
    "hsk2": {
        "title": "HSK 2 备考完全指南", "subtitle": "初等·基础篇 — Level 2 Complete Prep Guide",
        "zh_title": "HSK 2级备考", "author": "Tony Sheng", "color": "#009650",
        "output": "ZTurns_HSK2_Prep.pdf",
        "source_dirs": [
            "HSK备考/hsk2-prep/part0-exam-overview",
            "HSK备考/hsk2-prep/part1-vocabulary-grammar",
            "HSK备考/hsk2-prep/part2-listening",
            "HSK备考/hsk2-prep/part3-reading",
            "HSK备考/hsk2-prep/part4-writing",
            "HSK备考/hsk2-prep/part5-exam-tips",
            "HSK备考/hsk2-prep/part6-mock-exams",
            "HSK备考/hsk2-prep/appendices",
        ],
        "part_names": {
            "HSK备考/hsk2-prep/part0-exam-overview": "Part 0: 考试总览与备考策略",
            "HSK备考/hsk2-prep/part1-vocabulary-grammar": "Part 1: 核心词汇与语法",
            "HSK备考/hsk2-prep/part2-listening": "Part 2: 听力专项突破",
            "HSK备考/hsk2-prep/part3-reading": "Part 3: 阅读专项突破",
            "HSK备考/hsk2-prep/part4-writing": "Part 4: 书写专项突破",
            "HSK备考/hsk2-prep/part5-exam-tips": "Part 5: 考点精讲与易错点",
            "HSK备考/hsk2-prep/part6-mock-exams": "Part 6: 全真模拟试卷",
            "HSK备考/hsk2-prep/appendices": "附录",
        },
    },
    "hsk3": {
        "title": "HSK 3 备考完全指南", "subtitle": "初等·进阶篇 — Level 3 Complete Prep Guide",
        "zh_title": "HSK 3级备考", "author": "Tony Sheng", "color": "#B4321E",
        "output": "ZTurns_HSK3_Prep.pdf",
        "source_dirs": [
            "HSK备考/hsk3-prep/part0-exam-overview",
            "HSK备考/hsk3-prep/part1-vocabulary-grammar",
            "HSK备考/hsk3-prep/part2-listening",
            "HSK备考/hsk3-prep/part3-reading",
            "HSK备考/hsk3-prep/part4-writing",
            "HSK备考/hsk3-prep/part5-exam-tips",
            "HSK备考/hsk3-prep/part6-mock-exams",
            "HSK备考/hsk3-prep/appendices",
        ],
        "part_names": {
            "HSK备考/hsk3-prep/part0-exam-overview": "Part 0: 考试总览与备考策略",
            "HSK备考/hsk3-prep/part1-vocabulary-grammar": "Part 1: 核心词汇与语法",
            "HSK备考/hsk3-prep/part2-listening": "Part 2: 听力专项突破",
            "HSK备考/hsk3-prep/part3-reading": "Part 3: 阅读专项突破",
            "HSK备考/hsk3-prep/part4-writing": "Part 4: 书写专项突破",
            "HSK备考/hsk3-prep/part5-exam-tips": "Part 5: 考点精讲与易错点",
            "HSK备考/hsk3-prep/part6-mock-exams": "Part 6: 全真模拟试卷",
            "HSK备考/hsk3-prep/appendices": "附录",
        },
    },
    "hsk4": {
        "title": "HSK 4 备考完全指南", "subtitle": "中等·突破篇 — Level 4 Complete Prep Guide",
        "zh_title": "HSK 4级备考", "author": "Tony Sheng", "color": "#C87800",
        "output": "ZTurns_HSK4_Prep.pdf",
        "source_dirs": [
            "HSK备考/hsk4-prep/part0-exam-overview",
            "HSK备考/hsk4-prep/part1-vocabulary-grammar",
            "HSK备考/hsk4-prep/part2-listening",
            "HSK备考/hsk4-prep/part3-reading",
            "HSK备考/hsk4-prep/part4-writing",
            "HSK备考/hsk4-prep/part5-exam-tips",
            "HSK备考/hsk4-prep/part6-mock-exams",
            "HSK备考/hsk4-prep/appendices",
        ],
        "part_names": {
            "HSK备考/hsk4-prep/part0-exam-overview": "Part 0: 考试总览与备考策略",
            "HSK备考/hsk4-prep/part1-vocabulary-grammar": "Part 1: 核心词汇与语法",
            "HSK备考/hsk4-prep/part2-listening": "Part 2: 听力专项突破",
            "HSK备考/hsk4-prep/part3-reading": "Part 3: 阅读专项突破",
            "HSK备考/hsk4-prep/part4-writing": "Part 4: 写作专项突破",
            "HSK备考/hsk4-prep/part5-exam-tips": "Part 5: 考点精讲与易错点",
            "HSK备考/hsk4-prep/part6-mock-exams": "Part 6: 全真模拟试卷",
            "HSK备考/hsk4-prep/appendices": "附录",
        },
    },
    "hsk5": {
        "title": "HSK 5 备考完全指南", "subtitle": "中等·精进篇 — Level 5 Complete Prep Guide",
        "zh_title": "HSK 5级备考", "author": "Tony Sheng", "color": "#643296",
        "output": "ZTurns_HSK5_Prep.pdf",
        "source_dirs": [
            "HSK备考/hsk5-prep/part0-exam-overview",
            "HSK备考/hsk5-prep/part1-vocabulary-grammar",
            "HSK备考/hsk5-prep/part2-listening",
            "HSK备考/hsk5-prep/part3-reading",
            "HSK备考/hsk5-prep/part4-writing",
            "HSK备考/hsk5-prep/part5-exam-tips",
            "HSK备考/hsk5-prep/part6-mock-exams",
            "HSK备考/hsk5-prep/appendices",
        ],
        "part_names": {
            "HSK备考/hsk5-prep/part0-exam-overview": "Part 0: 考试总览与备考策略",
            "HSK备考/hsk5-prep/part1-vocabulary-grammar": "Part 1: 核心词汇与语法",
            "HSK备考/hsk5-prep/part2-listening": "Part 2: 听力专项突破",
            "HSK备考/hsk5-prep/part3-reading": "Part 3: 阅读专项突破",
            "HSK备考/hsk5-prep/part4-writing": "Part 4: 写作专项突破",
            "HSK备考/hsk5-prep/part5-exam-tips": "Part 5: 考点精讲与易错点",
            "HSK备考/hsk5-prep/part6-mock-exams": "Part 6: 全真模拟试卷",
            "HSK备考/hsk5-prep/appendices": "附录",
        },
    },
    "hsk6": {
        "title": "HSK 6 备考完全指南", "subtitle": "高等·卓越篇 — Level 6 Complete Prep Guide",
        "zh_title": "HSK 6级备考", "author": "Tony Sheng", "color": "#1A1A2E",
        "output": "ZTurns_HSK6_Prep.pdf",
        "source_dirs": [
            "HSK备考/hsk6-prep/part0-exam-overview",
            "HSK备考/hsk6-prep/part1-vocabulary-grammar",
            "HSK备考/hsk6-prep/part2-listening",
            "HSK备考/hsk6-prep/part3-reading",
            "HSK备考/hsk6-prep/part4-writing",
            "HSK备考/hsk6-prep/part5-exam-tips",
            "HSK备考/hsk6-prep/part6-mock-exams",
            "HSK备考/hsk6-prep/appendices",
        ],
        "part_names": {
            "HSK备考/hsk6-prep/part0-exam-overview": "Part 0: 考试总览与备考策略",
            "HSK备考/hsk6-prep/part1-vocabulary-grammar": "Part 1: 核心词汇与语法",
            "HSK备考/hsk6-prep/part2-listening": "Part 2: 听力专项突破",
            "HSK备考/hsk6-prep/part3-reading": "Part 3: 阅读专项突破",
            "HSK备考/hsk6-prep/part4-writing": "Part 4: 写作专项突破",
            "HSK备考/hsk6-prep/part5-exam-tips": "Part 5: 考点精讲与易错点",
            "HSK备考/hsk6-prep/part6-mock-exams": "Part 6: 全真模拟试卷",
            "HSK备考/hsk6-prep/appendices": "附录",
        },
    },
    "hsk79": {
        "title": "HSK 7-9 备考完全指南", "subtitle": "高等·大师篇 — Levels 7-9 Complete Prep Guide",
        "zh_title": "HSK 7-9级备考", "author": "Tony Sheng", "color": "#4A148C",
        "output": "ZTurns_HSK79_Prep.pdf",
        "source_dirs": [
            "HSK备考/hsk79-prep/part0-exam-overview",
            "HSK备考/hsk79-prep/part1-vocabulary-grammar",
            "HSK备考/hsk79-prep/part2-listening",
            "HSK备考/hsk79-prep/part3-reading",
            "HSK备考/hsk79-prep/part4-writing",
            "HSK备考/hsk79-prep/part5-translation",
            "HSK备考/hsk79-prep/part6-speaking",
            "HSK备考/hsk79-prep/part7-exam-tips",
            "HSK备考/hsk79-prep/part8-mock-exams",
            "HSK备考/hsk79-prep/appendices",
        ],
        "part_names": {
            "HSK备考/hsk79-prep/part0-exam-overview": "Part 0: 考试总览与备考策略",
            "HSK备考/hsk79-prep/part1-vocabulary-grammar": "Part 1: 高级词汇与语法",
            "HSK备考/hsk79-prep/part2-listening": "Part 2: 听力专项突破",
            "HSK备考/hsk79-prep/part3-reading": "Part 3: 阅读专项突破",
            "HSK备考/hsk79-prep/part4-writing": "Part 4: 写作专项突破",
            "HSK备考/hsk79-prep/part5-translation": "Part 5: 翻译专项突破",
            "HSK备考/hsk79-prep/part6-speaking": "Part 6: 口语专项突破",
            "HSK备考/hsk79-prep/part7-exam-tips": "Part 7: 考点精讲与考试技巧",
            "HSK备考/hsk79-prep/part8-mock-exams": "Part 8: 全真模拟试卷",
            "HSK备考/hsk79-prep/appendices": "附录",
        },
    },
}


# ─────────────────────────────────────────────
# Markdown parser — state machine (from generate_books.py)
# ─────────────────────────────────────────────
class Block:
    """Parsed content block."""
    __slots__ = ("kind", "data")

    def __init__(self, kind, data):
        self.kind = kind  # h1 h2 h3 four_layer table paragraph rule bullet numbered
        self.data = data


def parse_markdown(text: str) -> list:
    """Parse markdown into a list of Block objects."""
    lines = text.splitlines()
    blocks = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # Headings
        if line.startswith("#### "):
            blocks.append(Block("h3", line[5:].strip()))
            i += 1
            continue
        if line.startswith("### "):
            blocks.append(Block("h3", line[4:].strip()))
            i += 1
            continue
        if line.startswith("## "):
            blocks.append(Block("h2", line[3:].strip()))
            i += 1
            continue
        if line.startswith("# "):
            blocks.append(Block("h1", line[2:].strip()))
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^-{3,}$", line.strip()):
            blocks.append(Block("rule", None))
            i += 1
            continue

        # Code block — four-layer translation
        if line.strip().startswith("```"):
            block_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                block_lines.append(lines[i])
                i += 1
            i += 1  # consume closing ```
            parsed = _parse_four_layer(block_lines)
            if parsed:
                blocks.append(Block("four_layer", parsed))
            else:
                blocks.append(Block("paragraph", "\n".join(block_lines)))
            continue

        # Table
        if line.startswith("|") and i + 1 < n and re.match(r"^\|[-| :]+\|", lines[i + 1]):
            table_lines = []
            while i < n and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            blocks.append(Block("table", _parse_table(table_lines)))
            continue

        # Bullet list
        if re.match(r"^[-*] ", line):
            items = []
            while i < n and re.match(r"^[-*] ", lines[i]):
                items.append(lines[i][2:].strip())
                i += 1
            blocks.append(Block("bullet", items))
            continue

        # Numbered list
        if re.match(r"^\d+\. ", line):
            items = []
            while i < n and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i]).strip())
                i += 1
            blocks.append(Block("numbered", items))
            continue

        # Empty line — skip
        if line.strip() == "":
            i += 1
            continue

        # Paragraph — collect consecutive non-special lines
        para_lines = []
        start_i = i
        while i < n:
            l = lines[i]
            if (l.strip() == "" or l.startswith("#") or l.startswith("|")
                    or l.strip().startswith("```") or re.match(r"^-{3,}$", l.strip())
                    or re.match(r"^[-*] ", l) or re.match(r"^\d+\. ", l)):
                break
            para_lines.append(l)
            i += 1
        if i == start_i:
            i += 1  # safety: prevent infinite loop on unrecognized lines
        if para_lines:
            blocks.append(Block("paragraph", " ".join(para_lines)))

    return blocks


def _parse_four_layer(lines: list) -> dict | None:
    """Extract Chinese/Pinyin/Literal/English from code block lines."""
    result = {}
    for line in lines:
        for key in ("Chinese", "Pinyin", "Literal", "English"):
            if line.startswith(key + ":"):
                result[key.lower()] = line[len(key) + 1:].strip()
    if "chinese" in result and len(result) >= 2:
        return result
    return None


def _parse_table(lines: list) -> list:
    """Parse markdown table into list of rows (each row is a list of cells)."""
    rows = []
    for line in lines:
        if re.match(r"^\|[-| :]+\|", line):
            continue  # separator row
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells:
            rows.append(cells)
    return rows


def strip_inline_md(text: str) -> str:
    """Remove bold/italic/link markdown for plain text."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text


# ─────────────────────────────────────────────
# Text utilities
# ─────────────────────────────────────────────
_CJK_RE = re.compile(
    r"([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\u3040-\u309f\u30a0-\u30ff]+)"
)


def wrap_cjk(text: str) -> str:
    """Wrap CJK character runs in <span class='zh'> for correct font rendering."""
    return _CJK_RE.sub(r'<span class="zh">\1</span>', text)


def esc(text: str) -> str:
    """HTML-escape then wrap CJK spans."""
    return wrap_cjk(html.escape(str(text)))


def render_inline_md(text: str) -> str:
    """Convert markdown bold/italic/code/links to HTML, then wrap CJK."""
    text = html.escape(text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Code
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Links
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return wrap_cjk(text)


# ─────────────────────────────────────────────
# HTML / CSS builder
# ─────────────────────────────────────────────

def build_css(color: str) -> str:
    return f"""
@page {{
    size: 152.4mm 228.6mm;  /* 6" x 9" */
    margin-top: 20mm;
    margin-bottom: 22mm;
    margin-inside: 22mm;
    margin-outside: 18mm;

    @bottom-center {{
        content: string(book-footer);
        font-family: "Helvetica Neue", Arial, sans-serif;
        font-size: 8pt;
        color: #888;
    }}
    @bottom-right {{
        content: counter(page);
        font-family: "Helvetica Neue", Arial, sans-serif;
        font-size: 8pt;
        color: #888;
    }}
}}

@page :first {{
    margin: 0;
    @bottom-center {{ content: none; }}
    @bottom-right {{ content: none; }}
}}

@page cover {{
    margin: 0;
    @bottom-center {{ content: none; }}
    @bottom-right {{ content: none; }}
}}

@page toc {{
    @bottom-center {{ content: none; }}
    @bottom-right {{ content: none; }}
}}

@page part-divider {{
    @bottom-center {{ content: none; }}
    @bottom-right {{ content: none; }}
}}

* {{
    box-sizing: border-box;
}}

body {{
    font-family: "Helvetica Neue", "Arial", Helvetica, sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #1a1a1a;
    margin: 0;
    padding: 0;
}}

.zh {{
    font-family: "Songti SC", "STSong", "SimSun", "Hiragino Mincho ProN",
                 "Hiragino Sans GB", "PingFang SC", serif;
}}

/* ── Footer string ── */
.book-footer-marker {{
    string-set: book-footer content();
    display: none;
}}

/* ── Cover page ── */
.cover-page {{
    page: cover;
    page-break-after: always;
    width: 152.4mm;
    height: 228.6mm;
    position: relative;
    overflow: hidden;
    background: white;
}}

.cover-top-band {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 75mm;
    background: {color};
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 8mm 10mm 6mm;
}}

.cover-series {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 9pt;
    font-weight: 600;
    letter-spacing: 2px;
    color: rgba(255,255,255,0.85);
    text-transform: uppercase;
    margin-bottom: 4mm;
}}

.cover-divider-line {{
    width: 80%;
    height: 0.5pt;
    background: rgba(255,255,255,0.5);
    margin-bottom: 4mm;
}}

.cover-title {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 22pt;
    font-weight: 800;
    color: white;
    text-align: center;
    line-height: 1.2;
    margin-bottom: 3mm;
}}

.cover-subtitle {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    font-weight: 400;
    color: rgba(255,255,255,0.9);
    text-align: center;
    line-height: 1.4;
}}

.cover-body {{
    position: absolute;
    top: 75mm;
    left: 0;
    right: 0;
    bottom: 45mm;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5mm 10mm;
}}

.cover-zh-title {{
    font-family: "Songti SC", "STSong", "SimSun", serif;
    font-size: 16pt;
    color: {color};
    text-align: center;
    margin-bottom: 6mm;
}}

.cover-tagline-box {{
    border: 1.5pt solid {color};
    background: #F8F8F8;
    border-radius: 2mm;
    padding: 3mm 6mm;
    text-align: center;
    margin-bottom: 6mm;
}}

.cover-tagline-en {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 9pt;
    color: #444;
    font-weight: 500;
}}

.cover-tagline-zh {{
    font-family: "Songti SC", "STSong", "SimSun", serif;
    font-size: 9pt;
    color: #666;
    margin-top: 1mm;
}}

.cover-big-char {{
    font-family: "Songti SC", "STSong", "SimSun", serif;
    font-size: 60pt;
    color: {color};
    opacity: 0.15;
    line-height: 1;
    position: absolute;
    right: 8mm;
    bottom: 50mm;
}}

.cover-bottom-band {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 45mm;
    background: {color};
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4mm;
}}

.cover-author {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 11pt;
    font-weight: 500;
    color: white;
    text-align: center;
    margin-bottom: 3mm;
}}

.cover-website {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 8pt;
    color: rgba(255,255,255,0.7);
}}

/* ── TOC page ── */
.toc-page {{
    page: toc;
    page-break-after: always;
    padding: 8mm 0;
}}

.toc-title {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 20pt;
    font-weight: 800;
    color: {color};
    text-align: center;
    margin-bottom: 1mm;
}}

.toc-subtitle {{
    font-family: "Songti SC", "STSong", "SimSun", serif;
    font-size: 11pt;
    color: #888;
    text-align: center;
    margin-bottom: 4mm;
}}

.toc-rule {{
    border: none;
    border-top: 1.5pt solid {color};
    margin-bottom: 5mm;
}}

.toc-part {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    font-weight: 700;
    color: {color};
    margin-top: 4mm;
    margin-bottom: 1mm;
    display: flex;
    justify-content: space-between;
}}

.toc-chapter {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 9pt;
    color: #333;
    margin-left: 5mm;
    margin-bottom: 1mm;
    display: flex;
    justify-content: space-between;
}}

.toc-dots {{
    flex: 1;
    border-bottom: 1pt dotted #bbb;
    margin: 0 2mm;
    align-self: flex-end;
    margin-bottom: 1.5pt;
}}

/* ── Part divider ── */
.part-page {{
    page: part-divider;
    page-break-before: always;
    page-break-after: always;
    width: 152.4mm;
    height: 228.6mm;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
}}

.part-band {{
    position: absolute;
    left: 0;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    background: {color};
    padding: 15mm 12mm;
    text-align: center;
}}

.part-name {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 18pt;
    font-weight: 800;
    color: white;
    line-height: 1.3;
    margin-bottom: 3mm;
}}

/* ── Chapter page ── */
.chapter-header {{
    page-break-before: always;
    background: {color};
    margin: -20mm -18mm 8mm -22mm;
    padding: 6mm 12mm 8mm;
}}

.chapter-series-marker {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 7pt;
    font-weight: 600;
    letter-spacing: 2px;
    color: rgba(255,255,255,0.7);
    text-transform: uppercase;
    margin-bottom: 2mm;
}}

.chapter-title {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 16pt;
    font-weight: 800;
    color: white;
    line-height: 1.3;
}}

/* ── Content elements ── */
h2 {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 12pt;
    font-weight: 700;
    color: white;
    background: {color};
    padding: 2.5mm 4mm;
    margin: 5mm 0 3mm 0;
    page-break-after: avoid;
}}

h3 {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 10.5pt;
    font-weight: 700;
    color: {color};
    margin: 4mm 0 2mm 0;
    padding-bottom: 1mm;
    border-bottom: 0.5pt solid {color};
    page-break-after: avoid;
}}

p {{
    margin: 0 0 3mm 0;
    text-align: left;
    orphans: 2;
    widows: 2;
}}

/* Blockquote / callout */
blockquote {{
    margin: 3mm 0 3mm 4mm;
    padding: 2mm 4mm;
    border-left: 3pt solid {color};
    background: #F8F8F8;
    font-style: italic;
    color: #555;
    font-size: 9.5pt;
}}

/* Horizontal rule */
hr {{
    border: none;
    border-top: 0.5pt solid {color};
    margin: 4mm 0;
    opacity: 0.4;
}}

/* Bullet & numbered lists */
ul, ol {{
    margin: 2mm 0 3mm 0;
    padding-left: 6mm;
}}

li {{
    margin-bottom: 1.5mm;
    font-size: 10pt;
}}

/* ── Four-layer translation box ── */
.four-layer {{
    background: #F5F5F8;
    border-left: 3pt solid {color};
    border: 0.5pt solid #D0D0DC;
    border-left-width: 3pt;
    padding: 3mm 4mm 3mm 5mm;
    margin: 3mm 0;
    page-break-inside: avoid;
}}

.fl-chinese {{
    font-family: "Songti SC", "STSong", "SimSun", serif;
    font-size: 13pt;
    font-weight: 600;
    color: #111;
    line-height: 1.5;
    margin-bottom: 1.5mm;
}}

.fl-pinyin {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 8.5pt;
    color: #505078;
    margin-bottom: 1mm;
    font-style: italic;
}}

.fl-literal {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 8.5pt;
    color: #644832;
    margin-bottom: 1mm;
    font-style: italic;
}}

.fl-english {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 9.5pt;
    color: #111;
    font-weight: 500;
}}

/* ── Vocabulary table ── */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 3mm 0;
    font-size: 8.5pt;
    page-break-inside: auto;
}}

thead tr {{
    background: {color};
    color: white;
}}

thead th {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-weight: 700;
    padding: 2mm 2.5mm;
    text-align: left;
    border: 0.5pt solid rgba(0,0,0,0.15);
    font-size: 8pt;
}}

tbody tr:nth-child(even) {{
    background: #EEF4FF;
}}

tbody tr:nth-child(odd) {{
    background: white;
}}

tbody td {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    padding: 1.5mm 2.5mm;
    border: 0.5pt solid #D0D8E8;
    vertical-align: top;
    line-height: 1.4;
}}

tbody td .zh {{
    font-family: "Songti SC", "STSong", "SimSun", serif;
    font-size: 9pt;
}}

/* ── Front matter ── */
.front-matter {{
    page-break-before: always;
    page-break-after: always;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100mm;
    text-align: center;
}}

.front-content {{
    padding: 10mm;
}}

.front-logo {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 20pt;
    font-weight: 800;
    color: {color};
    margin-bottom: 3mm;
}}

.front-rule {{
    width: 60%;
    border: none;
    border-top: 1pt solid {color};
    margin: 3mm 0;
}}

.front-en {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    color: #555;
    margin-bottom: 2mm;
}}

.front-zh {{
    font-family: "Songti SC", "STSong", "SimSun", serif;
    font-size: 10pt;
    color: #777;
    margin-bottom: 3mm;
}}

.front-website {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 9pt;
    color: {color};
    font-weight: 500;
}}

/* ── Copyright page ── */
.copyright-page {{
    page-break-before: always;
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 120mm;
    text-align: center;
    padding: 0 12mm;
}}

.copyright-title {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 18pt;
    font-weight: 800;
    color: {color};
    margin-bottom: 2mm;
}}

.copyright-subtitle {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    color: #555;
    margin-bottom: 8mm;
}}

.copyright-line {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    color: #333;
    line-height: 1.7;
}}

.copyright-line.zh {{
    font-family: "Songti SC", "STSong", "SimSun", serif;
    color: #555;
}}

/* ── Back matter ── */
.back-matter {{
    page-break-before: always;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 120mm;
    text-align: center;
}}

.back-band {{
    background: {color};
    width: 152.4mm;
    margin-left: -22mm;
    margin-right: -18mm;
    padding: 14mm 14mm;
    text-align: center;
}}

.back-title {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 16pt;
    font-weight: 800;
    color: white;
    margin-bottom: 3mm;
}}

.back-zh {{
    font-family: "Songti SC", "STSong", "SimSun", serif;
    font-size: 12pt;
    color: rgba(255,255,255,0.9);
    margin-bottom: 5mm;
}}

.back-tagline {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 9pt;
    color: rgba(255,255,255,0.75);
    line-height: 1.6;
}}

.back-website {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 9pt;
    color: rgba(255,255,255,0.9);
    margin-top: 5mm;
}}
"""


def render_blocks_html(blocks: list) -> str:
    """Convert parsed blocks to HTML string."""
    parts = []

    for block in blocks:
        k = block.kind

        if k == "h1":
            # Chapter heading — styled header band
            parts.append(
                f'<div class="chapter-header">'
                f'<div class="chapter-series-marker">{html.escape(SERIES_NAME.upper())}</div>'
                f'<div class="chapter-title">{esc(strip_inline_md(block.data))}</div>'
                f'</div>'
            )

        elif k == "h2":
            parts.append(f'<h2>{esc(strip_inline_md(block.data))}</h2>')

        elif k == "h3":
            parts.append(f'<h3>{esc(strip_inline_md(block.data))}</h3>')

        elif k == "paragraph":
            text = block.data.strip()
            # Blockquote detection: lines starting with >
            if text.startswith(">"):
                inner = text.lstrip(">").strip().strip("*").strip()
                parts.append(f'<blockquote>{render_inline_md(inner)}</blockquote>')
            else:
                parts.append(f'<p>{render_inline_md(text)}</p>')

        elif k == "four_layer":
            d = block.data
            inner = []
            if d.get("chinese"):
                inner.append(
                    f'<div class="fl-chinese"><span class="zh">'
                    f'{html.escape(d["chinese"])}</span></div>'
                )
            if d.get("pinyin"):
                inner.append(
                    f'<div class="fl-pinyin">{html.escape(d["pinyin"])}</div>'
                )
            if d.get("literal"):
                inner.append(
                    f'<div class="fl-literal">[ {html.escape(d["literal"])} ]</div>'
                )
            if d.get("english"):
                inner.append(
                    f'<div class="fl-english">&rarr; {html.escape(d["english"])}</div>'
                )
            parts.append(f'<div class="four-layer">{"".join(inner)}</div>')

        elif k == "table":
            rows = block.data
            if not rows:
                continue
            header = rows[0]
            data_rows = rows[1:]
            cells = "".join(
                f'<th>{esc(strip_inline_md(c))}</th>' for c in header
            )
            html_rows = [f'<thead><tr>{cells}</tr></thead>']
            body_rows = []
            for row in data_rows:
                tds = "".join(
                    f'<td>{esc(strip_inline_md(c))}</td>' for c in row
                )
                body_rows.append(f'<tr>{tds}</tr>')
            html_rows.append(f'<tbody>{"".join(body_rows)}</tbody>')
            parts.append(f'<table>{"".join(html_rows)}</table>')

        elif k == "bullet":
            items = "".join(
                f'<li>{render_inline_md(strip_inline_md(item))}</li>'
                for item in block.data
            )
            parts.append(f'<ul>{items}</ul>')

        elif k == "numbered":
            items = "".join(
                f'<li>{render_inline_md(strip_inline_md(item))}</li>'
                for item in block.data
            )
            parts.append(f'<ol>{items}</ol>')

        elif k == "rule":
            parts.append('<hr>')

    return "\n".join(parts)


def build_cover_html(meta: dict) -> str:
    color = meta["color"]
    title = html.escape(meta["title"])
    subtitle = html.escape(meta["subtitle"])
    zh_title = html.escape(meta["zh_title"])
    author = html.escape(DEFAULT_AUTHOR)
    return f"""
<div class="cover-page">
  <div class="cover-top-band">
    <div class="cover-series">{html.escape(SERIES_NAME)} Series</div>
    <div class="cover-divider-line"></div>
    <div class="cover-title">{title}</div>
    <div class="cover-subtitle">{subtitle}</div>
  </div>
  <div class="cover-body">
    <div class="cover-zh-title">{zh_title}</div>
    <div class="cover-tagline-box">
      <div class="cover-tagline-en">Four-Layer Word-by-Word Translation Method</div>
      <div class="cover-tagline-zh">四层逐字翻译法</div>
    </div>
  </div>
  <div class="cover-big-char">中</div>
  <div class="cover-bottom-band">
    <div class="cover-author">{author} — 3000+ hours of real Chinese teaching</div>
    <div class="cover-website">zturnsgo.com</div>
  </div>
</div>
"""


def build_toc_html(toc_entries: list, color: str) -> str:
    rows = []
    for level, title, _page in toc_entries:
        escaped = html.escape(strip_inline_md(title))
        wrapped = wrap_cjk(escaped)
        if level == "part":
            rows.append(
                f'<div class="toc-part">'
                f'<span>{wrapped}</span>'
                f'<span class="toc-dots"></span>'
                f'</div>'
            )
        else:
            rows.append(
                f'<div class="toc-chapter">'
                f'<span>{wrapped}</span>'
                f'<span class="toc-dots"></span>'
                f'</div>'
            )
    return f"""
<div class="toc-page">
  <div class="toc-title">Table of Contents</div>
  <div class="toc-subtitle"><span class="zh">目录</span></div>
  <hr class="toc-rule">
  {"".join(rows)}
</div>
"""


def build_part_html(part_name: str) -> str:
    escaped = html.escape(part_name)
    wrapped = wrap_cjk(escaped)
    return f"""
<div class="part-page">
  <div class="part-band">
    <div class="part-name">{wrapped}</div>
  </div>
</div>
"""


def build_front_matter_html() -> str:
    return """
<div class="front-matter">
  <div class="front-content">
    <div class="front-logo">{series_name}</div>
    <hr class="front-rule">
    <div class="front-en">Learn real conversational Chinese through our four-layer translation method.</div>
    <div class="front-zh">通过四层逐字翻译法学习真实的中国日常对话。</div>
    <hr class="front-rule">
    <div class="front-website">{website}</div>
  </div>
</div>
""".format(series_name=html.escape(SERIES_NAME), website=html.escape(COMPANY_WEBSITE))


def build_copyright_html(meta: dict) -> str:
    title = html.escape(meta["title"])
    subtitle = html.escape(meta["subtitle"])
    return f"""
<div class="copyright-page">
  <div class="copyright-title">{title}</div>
  <div class="copyright-subtitle">{subtitle}</div>
  <div class="copyright-line">Author: {html.escape(DEFAULT_AUTHOR)}</div>
  <div class="copyright-line">Copyright Holder: {html.escape(COPYRIGHT_HOLDER)}</div>
  <div class="copyright-line zh">{html.escape(COPYRIGHT_NOTICE)}</div>
  <div class="copyright-line">Website: {html.escape(COMPANY_WEBSITE)}</div>
</div>
"""


def build_back_matter_html() -> str:
    return """
<div class="back-matter">
  <div class="back-band">
    <div class="back-title">Thank You for Learning with Us</div>
    <div class="back-zh"><span class="zh">感谢您与我们一起学习</span></div>
    <div class="back-tagline">
      Keep practicing. Real fluency comes from real conversations.<br>
      <span class="zh">继续练习。真正的流利来自真实的对话。</span>
    </div>
    <div class="back-website">{website}</div>
  </div>
</div>
""".format(website=html.escape(COMPANY_WEBSITE))


def build_full_html(book_key: str, meta: dict, content_html: str, toc_entries: list) -> str:
    css = build_css(meta["color"])
    title = html.escape(meta["title"])
    subtitle = html.escape(meta["subtitle"])
    footer_text = f"{meta['title']} — {meta['subtitle']}"
    cover = build_cover_html(meta)
    copyright_page = build_copyright_html(meta)
    toc = build_toc_html(toc_entries, meta["color"])
    front = build_front_matter_html()
    back = build_back_matter_html()
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{title} — {subtitle}</title>
<style>
{css}
</style>
</head>
<body>
<span class="book-footer-marker">{html.escape(footer_text)}</span>
{cover}
{copyright_page}
{front}
{toc}
{content_html}
{back}
</body>
</html>
"""


# ─────────────────────────────────────────────
# File collection
# ─────────────────────────────────────────────
def collect_files(source_dirs: list) -> list:
    """Return sorted list of (part_dir, Path) for all .md files."""
    result = []
    for source_dir in source_dirs:
        dir_path = BASE_DIR / source_dir
        if not dir_path.exists():
            print(f"  [WARN] Directory not found: {dir_path}")
            continue
        md_files = sorted(dir_path.glob("*.md"))
        for f in md_files:
            result.append((source_dir, f))
    return result


# ─────────────────────────────────────────────
# Build a single book
# ─────────────────────────────────────────────
def build_book(book_key: str, meta: dict):
    normalized_meta = dict(meta)
    normalized_meta["author"] = DEFAULT_AUTHOR

    print(f"\nBuilding {normalized_meta['output']} ...")

    files = collect_files(normalized_meta["source_dirs"])
    print(f"  Found {len(files)} markdown files")

    toc_entries = []
    content_parts = []
    current_part = None
    flagged_files = 0

    for source_dir, file_path in files:
        part_name = normalized_meta["part_names"].get(source_dir, source_dir)

        # New part divider
        if part_name != current_part:
            current_part = part_name
            toc_entries.append(("part", part_name, 0))
            content_parts.append(build_part_html(part_name))

        # Parse chapter
        text = file_path.read_text(encoding="utf-8")
        relative_path = str(file_path.relative_to(BASE_DIR))
        text, flagged_topics = sanitize_content(
            text,
            book_key=book_key,
            file_path=relative_path,
        )
        if flagged_topics:
            flagged_files += 1
        blocks = parse_markdown(text)

        # Extract chapter title from first h1 block for TOC
        chapter_title = file_path.stem
        for blk in blocks:
            if blk.kind == "h1":
                chapter_title = strip_inline_md(blk.data)
                break
        toc_entries.append(("chapter", chapter_title, 0))

        content_parts.append(render_blocks_html(blocks))

    content_html = "\n".join(content_parts)
    full_html = build_full_html(book_key, normalized_meta, content_html, toc_entries)

    out_path = OUTPUT_DIR / normalized_meta["output"]

    # Optional: save HTML for debugging
    # (OUTPUT_DIR / meta["output"].replace(".pdf", ".html")).write_text(full_html, encoding="utf-8")

    from weasyprint import HTML
    HTML(string=full_html, base_url=str(BASE_DIR)).write_pdf(str(out_path))

    size_kb = out_path.stat().st_size // 1024
    print(f"  Written: {out_path} ({size_kb} KB)")
    if flagged_files:
        print(f"  Filtered chapters: {flagged_files}")
    return out_path


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    import time as _time

    requested = set(sys.argv[1:]) if len(sys.argv) > 1 else None

    results = []
    errors = []

    for book_key, meta in BOOKS.items():
        if requested and book_key not in requested:
            print(f"\nSkipping {book_key} (not requested)")
            continue
        try:
            t0 = _time.monotonic()
            out = build_book(book_key, meta)
            elapsed = _time.monotonic() - t0
            print(f"  {elapsed:.1f}s")
            results.append(out)
        except Exception as e:
            import traceback
            print(f"\n[ERROR] {book_key}: {e}")
            traceback.print_exc()
            errors.append((book_key, str(e)))

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for path in results:
        size = path.stat().st_size
        print(f"  OK  {path.name}  ({size:,} bytes)")
    for book_key, err in errors:
        print(f"  FAIL {book_key}: {err}")

    if errors:
        sys.exit(1)
    print("\nAll books generated successfully.")


if __name__ == "__main__":
    main()
