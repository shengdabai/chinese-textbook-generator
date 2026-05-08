#!/usr/bin/env python3
"""
Enhanced content generator for Z Turns Chinese Books 51-70.
Mixes supplementary teaching content with AI-generated prose.
Add your own content source by implementing load_content_snippets() 
(see content_source_example.py).
Target: 10000+ lines per book (200+ pages PDF).

Usage:
    python3 generate_books_enhanced.py [book_numbers...]
    python3 generate_books_enhanced.py 61
    python3 generate_books_enhanced.py 51 52 53
    python3 generate_books_enhanced.py  # all books 51-70
"""
import os, sys, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "v1-pipeline" / "z-turns-chinese"))

OUTPUT_BASE = Path("output")

def extract_teaching_snippets(content: str, keywords: list, max_chars: int = 1200) -> str:
    """Extract paragraphs from note content matching keywords."""
    if not content:
        return ""
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', content) if p.strip()]
    matched = []
    total = 0
    for p in paragraphs:
        p_lower = p.lower()
        if any(kw.lower() in p_lower for kw in keywords):
            if total + len(p) <= max_chars:
                matched.append(p)
                total += len(p)
    return "\n\n".join(matched[:4])

# ── Note ID mapping per book ──────────────────────────────────────────────────

BOOK_NOTE_MAP = {
    51: {
        "keywords": ["职场", "面试", "求职", "简历", "工作", "薪资"],
    },
    52: {
        "keywords": ["创业", "商业", "企业", "投资", "公司", "AI"],
    },
    53: {
        "keywords": ["谈判", "沟通", "合同", "协议", "外贸"],
    },
    54: {
        "keywords": ["外贸", "商务", "简历", "面试", "职业"],
    },
    55: {
        "keywords": ["职场", "同事", "上司", "办公室", "人际"],
    },
    56: {
        "keywords": ["游戏", "电竞", "娱乐", "科技"],
    },
    57: {
        "keywords": ["音乐", "娱乐", "文化", "艺术"],
    },
    58: {
        "keywords": ["喜剧", "娱乐", "综艺", "脱口秀"],
    },
    59: {
        "keywords": ["小说", "文学", "网络", "阅读"],
    },
    60: {
        "keywords": ["综艺", "娱乐", "节目", "明星"],
    },
    61: {
        "keywords": ["菜市场", "买菜", "烹饪", "点餐", "食材", "炒", "厨房"],
    },
    62: {
        "keywords": ["理财", "金融", "投资", "经济", "钱"],
    },
    63: {
        "keywords": ["健康", "运动", "健身", "中医", "身体"],
    },
    64: {
        "keywords": ["旅行", "交通", "景点", "旅游", "摄影"],
    },
    65: {
        "keywords": ["装修", "房子", "家居", "设计", "建材"],
    },
    66: {
        "keywords": ["新能源", "电动车", "汽车", "充电", "比亚迪"],
    },
    67: {
        "keywords": ["清洁能源", "太阳能", "风能", "碳中和", "绿色"],
    },
    68: {
        "keywords": ["机器人", "AI", "人工智能", "自动化", "科技"],
    },
    69: {
        "keywords": ["量子", "芯片", "半导体", "科技", "技术"],
    },
    70: {
        "keywords": ["航天", "太空", "卫星", "火箭", "探索"],
    },
}

# ── Book metadata ─────────────────────────────────────────────────────────────

BOOKS = {
    51: {
        "dir": "Book51_JobHunter",
        "filename": "ZTurns_Book51_JobHunter.md",
        "title": "Job Hunter's Chinese",
        "subtitle": "求职面试中文实战手册",
        "color": "#E53935",
        "chapters": [
            ("Submitting Your CV", "投简历的艺术", "job applications", "简历", "résumé/CV"),
            ("Job Platforms", "招聘网站实战", "online recruiting", "招聘", "recruiting"),
            ("Phone Screening", "HR电话初筛", "phone interviews", "筛选", "screening"),
            ("Internal Referrals", "内推文化", "referral culture", "内推", "referral"),
            ("Headhunter Calls", "猎头电话", "headhunters", "猎头", "headhunter"),
            ("60-Second Introduction", "面试自我介绍", "self-introduction", "自我介绍", "self-intro"),
            ("Classic Interview Questions", "经典面试题", "interview questions", "面试", "interview"),
            ("Asking Back", "反问面试官", "asking questions", "提问", "question"),
            ("Stress Interview", "压力面试应对", "stress interviews", "压力", "pressure"),
            ("Final Round", "终面与高管对话", "executive interviews", "终面", "final interview"),
            ("Salary Negotiation", "薪资谈判话术", "salary negotiation", "薪资", "salary"),
            ("Benefits Package", "五险一金福利", "benefits", "福利", "benefits"),
            ("Background Check", "背景调查应对", "background checks", "背调", "background check"),
            ("Labour Contract", "劳动合同解读", "employment contracts", "合同", "contract"),
            ("Declining an Offer", "体面拒绝Offer", "offer rejection", "拒绝", "decline"),
            ("First Day Introduction", "入职自我介绍", "onboarding", "入职", "onboarding"),
            ("Office Small Talk", "茶水间破冰", "workplace chat", "聊天", "small talk"),
            ("Company Hierarchy", "公司层级结构", "org structure", "层级", "hierarchy"),
            ("Probation Period", "试用期生存", "probation", "试用期", "probation"),
            ("One-on-One Meetings", "一对一对齐目标", "1:1 meetings", "对齐", "alignment"),
            ("Annual Review", "年终述职报告", "performance review", "述职", "review"),
            ("Seeking Promotion", "申请晋升路径", "promotions", "晋升", "promotion"),
            ("Graceful Exit", "体面离职手续", "resignation", "离职", "resignation"),
            ("Office Conflicts", "处理同事矛盾", "workplace conflict", "矛盾", "conflict"),
            ("Foreigner's Pitfalls", "外国人职场误区", "cultural mistakes", "误区", "pitfall"),
        ],
    },
    52: {
        "dir": "Book52_Startup",
        "filename": "ZTurns_Book52_Startup.md",
        "title": "Startup Chinese",
        "subtitle": "创业创新中文实战词汇",
        "color": "#1565C0",
        "chapters": [
            ("The Startup Idea", "创业想法验证", "idea validation", "创业", "startup"),
            ("Finding Co-Founders", "寻找联合创始人", "co-founders", "合伙人", "co-founder"),
            ("Business Registration", "公司注册流程", "company registration", "注册", "registration"),
            ("Seed Funding", "天使轮融资", "seed funding", "融资", "funding"),
            ("Pitching Investors", "路演投资人", "investor pitch", "路演", "pitch"),
            ("Term Sheet", "投资条款谈判", "term sheets", "条款", "term sheet"),
            ("Building the Team", "组建核心团队", "team building", "团队", "team"),
            ("Product Launch", "产品发布上线", "product launch", "发布", "launch"),
            ("User Acquisition", "获客增长策略", "user growth", "获客", "acquisition"),
            ("Pivot Strategy", "转型调整决策", "pivoting", "转型", "pivot"),
            ("Series A", "A轮融资准备", "Series A", "A轮", "Series A"),
            ("Board Meetings", "董事会会议", "board meetings", "董事会", "board"),
            ("Hiring & Firing", "招人开人文化", "HR decisions", "裁员", "hiring"),
            ("Office Culture", "创业公司文化", "startup culture", "文化", "culture"),
            ("Burn Rate", "烧钱速度控制", "burn rate", "烧钱", "burn rate"),
            ("Competitor Analysis", "竞品分析报告", "competitive analysis", "竞品", "competitor"),
            ("China Market Entry", "进入中国市场", "market entry", "市场", "market"),
            ("WeChat Marketing", "微信营销策略", "WeChat marketing", "微信", "WeChat"),
            ("Government Relations", "政府关系维护", "gov relations", "政府", "government"),
            ("Supply Chain", "供应链管理", "supply chain", "供应链", "supply chain"),
            ("Scaling Operations", "规模化运营", "scaling", "规模", "scaling"),
            ("Exit Strategy", "退出策略规划", "exit strategy", "退出", "exit"),
            ("Failure Stories", "失败案例复盘", "failure analysis", "失败", "failure"),
            ("Success Metrics", "衡量成功指标", "KPIs", "指标", "KPI"),
            ("Founder Wellbeing", "创始人身心健康", "founder health", "健康", "wellbeing"),
        ],
    },
    53: {
        "dir": "Book53_Negotiation",
        "filename": "ZTurns_Book53_Negotiation.md",
        "title": "Negotiation Chinese",
        "subtitle": "商务谈判中文实战手册",
        "color": "#6A1B9A",
        "chapters": [
            ("Opening the Negotiation", "谈判开场白", "opening moves", "开场", "opening"),
            ("Price Anchoring", "价格锚定策略", "price anchoring", "锚定", "anchoring"),
            ("Making Concessions", "让步的艺术", "making concessions", "让步", "concession"),
            ("Reading Body Language", "读懂肢体语言", "body language", "肢体语言", "body language"),
            ("Deadlock Breaking", "打破僵局策略", "breaking deadlock", "僵局", "deadlock"),
            ("Contract Terms", "合同条款逐项", "contract terms", "合同", "contract"),
            ("Payment Terms", "付款方式谈判", "payment terms", "付款", "payment"),
            ("Delivery Negotiation", "交货期协商", "delivery terms", "交货", "delivery"),
            ("Quality Standards", "质量标准确认", "quality standards", "质量", "quality"),
            ("After-Sales Terms", "售后服务条款", "after-sales", "售后", "after-sales"),
            ("Partnership Deals", "合作协议谈判", "partnerships", "合作", "partnership"),
            ("License Agreements", "授权许可谈判", "licensing", "授权", "licensing"),
            ("Joint Ventures", "合资企业谈判", "joint ventures", "合资", "joint venture"),
            ("IP Protection", "知识产权保护", "IP protection", "知识产权", "IP"),
            ("Dispute Resolution", "争议解决机制", "dispute resolution", "争议", "dispute"),
            ("Cultural Differences", "中西谈判差异", "cultural differences", "差异", "differences"),
            ("Building Guanxi", "关系建立技巧", "building guanxi", "关系", "guanxi"),
            ("Face-Saving Tactics", "保全面子策略", "saving face", "面子", "face"),
            ("Banquet Negotiations", "饭局谈判文化", "banquet culture", "饭局", "banquet"),
            ("Gift-Giving Protocol", "送礼商务礼仪", "gift protocol", "送礼", "gifts"),
            ("Email Negotiations", "邮件谈判技巧", "email negotiation", "邮件", "email"),
            ("Phone Negotiations", "电话谈判技巧", "phone negotiation", "电话", "phone"),
            ("Final Agreement", "最终协议签署", "final agreement", "协议", "agreement"),
            ("Post-Deal Follow-up", "成交后跟进", "follow-up", "跟进", "follow-up"),
            ("Negotiation Debrief", "谈判复盘总结", "debrief", "复盘", "debrief"),
        ],
    },
    54: {
        "dir": "Book54_Resume",
        "filename": "ZTurns_Book54_Resume.md",
        "title": "Business Chinese Mastery",
        "subtitle": "职业发展中文全面提升",
        "color": "#2E7D32",
        "chapters": [
            ("Writing a Chinese CV", "中文简历写作", "CV writing", "简历", "CV"),
            ("Cover Letters", "求职信写作", "cover letters", "求职信", "cover letter"),
            ("LinkedIn in China", "领英使用技巧", "LinkedIn China", "领英", "LinkedIn"),
            ("Professional Email", "商务邮件写作", "business email", "邮件", "email"),
            ("Formal Reports", "正式报告撰写", "business reports", "报告", "report"),
            ("Meeting Minutes", "会议纪要记录", "meeting minutes", "纪要", "minutes"),
            ("Presentations", "商务演讲汇报", "presentations", "汇报", "presentation"),
            ("Data & Numbers", "数据报告表达", "data presentation", "数据", "data"),
            ("Finance Vocabulary", "财务词汇基础", "finance terms", "财务", "finance"),
            ("Marketing Terms", "市场营销词汇", "marketing", "营销", "marketing"),
            ("Legal Chinese", "法律文件基础", "legal Chinese", "法律", "legal"),
            ("HR Terminology", "人力资源词汇", "HR terms", "人力资源", "HR"),
            ("Supply Chain Terms", "供应链词汇", "supply chain", "供应链", "supply chain"),
            ("IT & Tech Terms", "科技行业词汇", "IT terms", "科技", "IT"),
            ("Manufacturing", "制造业词汇", "manufacturing", "制造", "manufacturing"),
            ("Trade Finance", "外贸金融词汇", "trade finance", "外贸", "trade"),
            ("Import & Export", "进出口流程词汇", "import export", "进出口", "import export"),
            ("Customs & Duty", "海关关税词汇", "customs", "海关", "customs"),
            ("Shipping Terms", "物流运输词汇", "shipping", "物流", "shipping"),
            ("Insurance Terms", "保险合同词汇", "insurance", "保险", "insurance"),
            ("Banking Terms", "银行金融词汇", "banking", "银行", "banking"),
            ("Tax Vocabulary", "税务相关词汇", "taxation", "税务", "tax"),
            ("Real Estate", "房地产词汇", "real estate", "房产", "real estate"),
            ("E-commerce Terms", "电商平台词汇", "e-commerce", "电商", "e-commerce"),
            ("Career Planning", "职业规划话语", "career planning", "职业规划", "career"),
        ],
    },
    55: {
        "dir": "Book55_WorkplacePolitics",
        "filename": "ZTurns_Book55_WorkplacePolitics.md",
        "title": "Workplace Politics Chinese",
        "subtitle": "职场人际关系中文指南",
        "color": "#E65100",
        "chapters": [
            ("Reading the Room", "察言观色技巧", "reading dynamics", "察言观色", "read the room"),
            ("Flattering the Boss", "向上管理话术", "managing up", "拍马屁", "flattery"),
            ("Office Gossip", "办公室八卦应对", "office gossip", "八卦", "gossip"),
            ("Taking Credit", "功劳归属话术", "taking credit", "功劳", "credit"),
            ("Blame Deflection", "锅从天而降应对", "blame deflection", "甩锅", "blame"),
            ("Alliance Building", "结盟拉人头", "building alliances", "站队", "alliance"),
            ("Meeting Dynamics", "会议发言技巧", "meeting politics", "发言", "speaking"),
            ("Email Cc Tactics", "抄送邮件学问", "email tactics", "抄送", "CC"),
            ("Salary Talk", "薪资保密文化", "salary secrecy", "薪资", "salary"),
            ("Performance Review", "绩效考核应对", "performance", "绩效", "performance"),
            ("Promotion Politics", "晋升背后逻辑", "promotion games", "晋升", "promotion"),
            ("New Boss Tactics", "新领导来了怎么办", "new boss", "新领导", "new boss"),
            ("Cross-Department", "跨部门合作", "cross-department", "跨部门", "cross-dept"),
            ("Toxic Colleagues", "难相处同事应对", "toxic colleagues", "难相处", "toxic"),
            ("Office Romance", "职场恋情文化", "office romance", "恋情", "romance"),
            ("Remote Work", "远程办公文化", "remote work", "远程", "remote"),
            ("996 Culture", "加班文化应对", "overtime culture", "加班", "overtime"),
            ("Year-End Bonus", "年终奖博弈", "bonus politics", "年终奖", "bonus"),
            ("Job Hopping", "跳槽时机判断", "job hopping", "跳槽", "job hop"),
            ("Whistleblowing", "举报投诉文化", "whistleblowing", "举报", "whistleblowing"),
            ("Dress Code", "职场穿着规范", "dress code", "穿着", "dress code"),
            ("Business Dining", "工作饭局文化", "business dining", "饭局", "dining"),
            ("KTV Obligations", "KTV应酬文化", "KTV culture", "KTV", "KTV"),
            ("WeChat Etiquette", "微信职场礼仪", "WeChat etiquette", "微信", "WeChat"),
            ("Exit Interview", "离职面谈话术", "exit interview", "离职", "exit"),
        ],
    },
    56: {
        "dir": "Book56_Gaming",
        "filename": "ZTurns_Book56_Gaming.md",
        "title": "Gaming in Chinese",
        "subtitle": "电竞游戏中文词汇大全",
        "color": "#1A237E",
        "chapters": [
            ("PC Gaming Setup", "电脑游戏装备", "PC gaming", "电脑", "PC gaming"),
            ("Mobile Games", "手游文化词汇", "mobile gaming", "手游", "mobile game"),
            ("Console Gaming", "主机游戏词汇", "console gaming", "主机", "console"),
            ("League of Legends", "英雄联盟词汇", "LoL vocabulary", "英雄联盟", "LoL"),
            ("Honor of Kings", "王者荣耀词汇", "Honor of Kings", "王者荣耀", "HoK"),
            ("Genshin Impact", "原神游戏词汇", "Genshin Impact", "原神", "Genshin"),
            ("eSports Teams", "电竞战队词汇", "eSports teams", "战队", "team"),
            ("Streaming Culture", "游戏直播词汇", "game streaming", "直播", "streaming"),
            ("Gaming Slang", "游戏黑话大全", "gaming slang", "黑话", "slang"),
            ("Team Communication", "游戏团队沟通", "team comms", "沟通", "comms"),
            ("Ranked Matches", "天梯排位系统", "ranked system", "排位", "ranked"),
            ("Tournament Talk", "赛事解说词汇", "tournament language", "赛事", "tournament"),
            ("Hero/Character Types", "英雄角色分类", "character types", "英雄", "hero"),
            ("Game Economy", "游戏经济词汇", "game economy", "游戏币", "economy"),
            ("Patch & Updates", "版本更新词汇", "game updates", "版本", "patch"),
            ("Cheating & Hacks", "作弊外挂词汇", "cheating terms", "外挂", "hacks"),
            ("Gaming Cafés", "网吧文化词汇", "internet cafés", "网吧", "café"),
            ("VR Gaming", "VR游戏词汇", "VR gaming", "VR", "VR gaming"),
            ("Game Reviews", "游戏评测词汇", "game reviews", "评测", "review"),
            ("Game Merchandise", "游戏周边文化", "game merch", "周边", "merchandise"),
            ("Game Music", "游戏音乐文化", "game music", "音乐", "music"),
            ("Game Lore", "游戏世界观词汇", "game lore", "世界观", "lore"),
            ("Online Communities", "游戏社区词汇", "gaming community", "社区", "community"),
            ("Pro Gamer Life", "职业选手生活", "pro gamer life", "职业选手", "pro"),
            ("Parents vs Gaming", "打游戏被父母骂", "gaming vs parents", "父母", "parents"),
        ],
    },
    57: {
        "dir": "Book57_Music",
        "filename": "ZTurns_Book57_Music.md",
        "title": "Music in Chinese",
        "subtitle": "音乐娱乐中文词汇全集",
        "color": "#880E4F",
        "chapters": [
            ("C-Pop Basics", "华语流行音乐", "C-Pop", "华语", "C-Pop"),
            ("Concert Language", "演唱会现场词汇", "concert vocabulary", "演唱会", "concert"),
            ("Music Streaming", "音乐平台词汇", "music streaming", "音乐平台", "streaming"),
            ("Singing Competitions", "歌唱比赛词汇", "singing shows", "歌唱比赛", "competition"),
            ("Music Genres", "音乐流派词汇", "music genres", "流派", "genre"),
            ("Instruments", "乐器名称词汇", "musical instruments", "乐器", "instrument"),
            ("Traditional Music", "传统音乐文化", "traditional music", "传统音乐", "traditional"),
            ("Music Theory", "乐理基础词汇", "music theory", "乐理", "theory"),
            ("Lyrics Analysis", "歌词分析词汇", "lyrics analysis", "歌词", "lyrics"),
            ("Music Production", "音乐制作词汇", "music production", "制作", "production"),
            ("KTV Culture", "KTV点歌文化", "KTV culture", "KTV", "KTV"),
            ("Fan Culture", "粉丝应援词汇", "fan culture", "粉丝", "fan"),
            ("Music Charts", "音乐榜单词汇", "music charts", "榜单", "chart"),
            ("Music Awards", "音乐颁奖词汇", "music awards", "颁奖", "award"),
            ("Band Culture", "乐队组合词汇", "band culture", "乐队", "band"),
            ("DJ & Club Music", "夜店DJ文化", "club music", "夜店", "club"),
            ("Hip-Hop Culture", "嘻哈文化词汇", "hip-hop", "嘻哈", "hip-hop"),
            ("Folk Music", "民谣文化词汇", "folk music", "民谣", "folk"),
            ("Opera", "戏曲文化词汇", "Chinese opera", "戏曲", "opera"),
            ("Music Criticism", "音乐评论词汇", "music criticism", "评论", "criticism"),
            ("Album Release", "专辑发行词汇", "album release", "专辑", "album"),
            ("Music Videos", "MV制作词汇", "music videos", "MV", "MV"),
            ("Live Streaming Music", "音乐直播词汇", "music livestream", "直播", "livestream"),
            ("Music Business", "音乐产业词汇", "music business", "产业", "industry"),
            ("Learning Music", "学乐器中文表达", "learning music", "学习", "learning"),
        ],
    },
    58: {
        "dir": "Book58_Comedy",
        "filename": "ZTurns_Book58_Comedy.md",
        "title": "Comedy in Chinese",
        "subtitle": "脱口秀喜剧中文词汇",
        "color": "#F57F17",
        "chapters": [
            ("Stand-up Comedy", "脱口秀基础词汇", "stand-up", "脱口秀", "stand-up"),
            ("Punchline Structure", "段子结构分析", "punchlines", "包袱", "punchline"),
            ("Internet Memes", "网络梗词汇大全", "internet memes", "网络梗", "memes"),
            ("Self-Deprecating Humor", "自嘲文化词汇", "self-deprecation", "自嘲", "self-deprecation"),
            ("Regional Jokes", "地域梗词汇", "regional humor", "地域梗", "regional"),
            ("Political Satire", "政治讽刺词汇", "political satire", "讽刺", "satire"),
            ("Wordplay & Puns", "文字游戏双关", "wordplay", "双关", "pun"),
            ("Dark Humor", "丧文化黑色幽默", "dark humor", "丧文化", "dark"),
            ("Sketch Comedy", "小品相声词汇", "sketch comedy", "小品", "sketch"),
            ("Crosstalk Comedy", "相声艺术词汇", "crosstalk", "相声", "crosstalk"),
            ("Comedy Competitions", "喜剧竞赛词汇", "comedy shows", "喜剧", "comedy show"),
            ("Audience Interaction", "与观众互动语言", "audience interaction", "互动", "interaction"),
            ("Roast Culture", "吐槽文化词汇", "roasting", "吐槽", "roast"),
            ("Viral Content", "爆款内容词汇", "viral content", "爆款", "viral"),
            ("Comedy Timing", "节奏时机词汇", "comedy timing", "节奏", "timing"),
            ("Celebrity Parody", "模仿秀词汇", "celebrity parody", "模仿", "parody"),
            ("Social Commentary", "社会讽刺词汇", "social commentary", "社会", "commentary"),
            ("Generational Humor", "代际幽默词汇", "gen humor", "代际", "generation"),
            ("Workplace Comedy", "打工人幽默", "workplace humor", "打工人", "worker"),
            ("Online Comedians", "网红段子手词汇", "online comedians", "段子手", "comedian"),
            ("Talk Show Language", "脱口秀大会词汇", "talk shows", "大会", "talk show"),
            ("Li Dan & Comedy", "李诞笑场文化", "comedy hosts", "主持人", "host"),
            ("Variety Sense", "综艺感综艺人格", "entertainment personality", "综艺感", "variety sense"),
            ("Famous Show Memes", "综艺名梗大全", "iconic moments", "名梗", "famous meme"),
            ("Learning via Comedy", "用喜剧学中文", "study methods", "学习", "learning"),
        ],
    },
    59: {
        "dir": "Book59_WebNovels",
        "filename": "ZTurns_Book59_WebNovels.md",
        "title": "Web Novel Chinese",
        "subtitle": "网络小说文学中文词汇",
        "color": "#4E342E",
        "chapters": [
            ("Novel Platforms", "网文平台词汇", "novel platforms", "网文平台", "platform"),
            ("Fantasy Worlds", "玄幻世界词汇", "fantasy genres", "玄幻", "fantasy"),
            ("Cultivation System", "修仙修炼词汇", "cultivation", "修仙", "cultivation"),
            ("Romance Novels", "言情小说词汇", "romance fiction", "言情", "romance"),
            ("Urban Fiction", "都市文学词汇", "urban fiction", "都市", "urban"),
            ("Historical Fiction", "历史穿越词汇", "historical fiction", "穿越", "historical"),
            ("Military Fiction", "军事战争词汇", "military fiction", "军事", "military"),
            ("System Novels", "系统流小说词汇", "system novels", "系统", "system"),
            ("Power Levels", "等级能力词汇", "power systems", "境界", "power level"),
            ("Character Archetypes", "主角配角词汇", "character types", "主角", "protagonist"),
            ("Plot Devices", "情节套路词汇", "plot tropes", "套路", "trope"),
            ("Reader Interaction", "读者评论词汇", "reader comments", "评论", "comment"),
            ("VIP Chapters", "付费章节文化", "paid chapters", "付费", "VIP"),
            ("Author Life", "网文作者生活", "author lifestyle", "作者", "author"),
            ("Fanfiction", "同人文化词汇", "fanfiction", "同人", "fanfic"),
            ("Adaptation News", "影视改编词汇", "adaptations", "改编", "adaptation"),
            ("Novel Communities", "书友圈文化词汇", "reading communities", "书友", "community"),
            ("Novel Critique", "书评分析词汇", "book reviews", "书评", "review"),
            ("Cliffhangers", "断更太监词汇", "cliffhangers", "断更", "cliffhanger"),
            ("Golden Fingers", "主角光环词汇", "protagonist halo", "金手指", "golden finger"),
            ("Novel Slang", "网文黑话大全", "novel slang", "黑话", "slang"),
            ("Female Lead Novels", "女频小说词汇", "female lead fiction", "女频", "female lead"),
            ("Male Lead Novels", "男频小说词汇", "male lead fiction", "男频", "male lead"),
            ("Novel Rankings", "网文排行榜词汇", "novel rankings", "排行榜", "ranking"),
            ("Reading Habits", "读网文的日常", "reading habits", "阅读", "reading"),
        ],
    },
    60: {
        "dir": "Book60_VarietyShows",
        "filename": "ZTurns_Book60_VarietyShows.md",
        "title": "Variety Show Chinese",
        "subtitle": "综艺节目中文词汇全集",
        "color": "#00838F",
        "chapters": [
            ("Variety Show Types", "综艺节目分类", "show types", "综艺", "variety"),
            ("Survival Shows", "生存竞技节目", "survival shows", "生存", "survival"),
            ("Dating Shows", "恋爱相亲节目", "dating shows", "相亲", "dating"),
            ("Cooking Shows", "美食烹饪节目", "cooking shows", "美食", "cooking show"),
            ("Travel Shows", "旅行探险节目", "travel shows", "旅行", "travel"),
            ("Celebrity Life", "明星生活节目", "celebrity shows", "明星", "celebrity"),
            ("Talent Shows", "才艺表演节目", "talent shows", "才艺", "talent"),
            ("Game Shows", "游戏竞技节目", "game shows", "竞技", "game show"),
            ("Talk Shows", "访谈类节目词汇", "talk shows", "访谈", "talk show"),
            ("Reality TV", "真人秀节目词汇", "reality TV", "真人秀", "reality"),
            ("Kid Shows", "亲子育儿节目", "kids shows", "亲子", "kids"),
            ("Idol Training Shows", "偶像养成节目", "idol shows", "偶像", "idol"),
            ("Documentary Style", "纪录片综艺词汇", "documentary", "纪录", "documentary"),
            ("Hosts & MCs", "主持人主持词汇", "hosting language", "主持人", "host"),
            ("Behind the Scenes", "幕后花絮词汇", "BTS content", "幕后", "behind scenes"),
            ("Fan Support", "粉丝打榜词汇", "fan voting", "打榜", "voting"),
            ("Episode Recaps", "剧情回顾词汇", "episode recap", "回顾", "recap"),
            ("Season Finales", "大结局词汇", "season finale", "大结局", "finale"),
            ("Show Controversies", "综艺翻车词汇", "controversies", "翻车", "controversy"),
            ("Production Teams", "节目组制作词汇", "production", "节目组", "production"),
            ("Talk Show Language", "脱口秀大会词汇", "comedy competition", "大会", "competition"),
            ("Li Dan & Comedy", "李诞笑场文化", "comedy hosts", "主持人", "host"),
            ("Variety Sense", "综艺感综艺人格", "entertainment personality", "综艺感", "variety sense"),
            ("Famous Show Memes", "综艺名梗大全", "iconic moments", "名梗", "famous meme"),
            ("Learning via Shows", "用综艺学中文", "study methods", "学习", "learning"),
        ],
    },
    61: {
        "dir": "Book61_Cooking",
        "filename": "ZTurns_Book61_Cooking.md",
        "title": "Cooking in Chinese",
        "subtitle": "中国厨房：从菜市场到餐桌",
        "color": "#E64A19",
        "chapters": [
            ("The Market Layout", "菜市场导航", "wet markets", "菜市场", "wet market"),
            ("Buying Vegetables", "买蔬菜时令", "seasonal vegetables", "蔬菜", "vegetables"),
            ("Buying Meat", "买肉各部位", "meat cuts", "猪肉", "pork/meat"),
            ("Buying Seafood", "买海鲜活鱼", "fresh seafood", "海鲜", "seafood"),
            ("Bargaining at Market", "菜市场砍价", "price negotiation", "砍价", "bargaining"),
            ("Kitchen Equipment", "厨房锅碗瓢盆", "kitchen tools", "厨具", "kitchen tools"),
            ("Knife Skills", "刀工切法", "knife techniques", "刀工", "knife work"),
            ("Heat Control", "火候大中小火", "cooking heat", "火候", "heat control"),
            ("Condiments & Sauces", "调味品使用", "Chinese condiments", "调味", "seasoning"),
            ("Pre-Processing", "腌制焯水", "food preparation", "腌制", "marinating"),
            ("Reading Recipes", "菜谱结构理解", "Chinese recipes", "菜谱", "recipe"),
            ("Measurement Words", "少许适量一勺", "cooking measurements", "分量", "measurement"),
            ("Cooking Terminology", "翻炒勾芡收汁", "cooking verbs", "烹饪", "cooking"),
            ("Recipe Apps", "下厨房美食杰", "cooking apps", "App", "cooking app"),
            ("Adjusting Taste", "少放辣椒请求", "flavor adjustment", "口味", "taste"),
            ("Sichuan Cooking", "川菜麻婆豆腐", "Sichuan cuisine", "川菜", "Sichuan"),
            ("Cantonese Techniques", "粤菜清蒸白灼", "Cantonese cuisine", "粤菜", "Cantonese"),
            ("Jiangsu Cuisine", "淮扬扬州炒饭", "Jiangsu cuisine", "淮扬", "Huaiyang"),
            ("Northern Noodles", "北方面食饺子", "northern food", "面食", "noodles"),
            ("Northeast Stew", "东北乱炖豪放", "northeastern cuisine", "东北菜", "northeastern"),
            ("Hosting Guests", "请客家庭聚餐", "Chinese hospitality", "请客", "hosting"),
            ("Food Photography", "拍食物朋友圈", "food photography", "拍照", "food photo"),
            ("Describing Taste", "口感味道描述", "flavor vocabulary", "味道", "taste/flavor"),
            ("Teaching Foreigners", "教外国人做菜", "food education", "教学", "teaching"),
            ("Food Taboos", "中国饮食禁忌", "food culture rules", "禁忌", "taboo"),
        ],
    },
    62: {
        "dir": "Book62_Finance",
        "filename": "ZTurns_Book62_Finance.md",
        "title": "Finance in Chinese",
        "subtitle": "理财投资中文实战",
        "color": "#1565C0",
        "chapters": [
            ("Bank Accounts", "开银行账户", "banking basics", "银行", "bank"),
            ("Mobile Payments", "微信支付宝", "mobile payment", "支付宝", "Alipay"),
            ("Savings Products", "理财产品选购", "savings products", "理财", "savings"),
            ("Stock Market Basics", "A股入门词汇", "stock market", "股票", "stocks"),
            ("Fund Investment", "基金定投词汇", "fund investment", "基金", "fund"),
            ("Real Estate", "房产投资词汇", "real estate", "房产", "property"),
            ("Insurance Types", "保险种类词汇", "insurance", "保险", "insurance"),
            ("Credit Cards", "信用卡使用词汇", "credit cards", "信用卡", "credit card"),
            ("Loans & Mortgages", "贷款房贷词汇", "loans", "贷款", "loan"),
            ("Tax Filing", "报税纳税词汇", "taxes", "税务", "tax"),
            ("Cryptocurrency", "数字货币词汇", "crypto", "数字货币", "crypto"),
            ("Ant Group Products", "蚂蚁金服词汇", "fintech", "蚂蚁", "Ant"),
            ("Wealth Management", "私人银行词汇", "wealth management", "私行", "wealth"),
            ("Pension System", "社保养老词汇", "pension", "社保", "pension"),
            ("Budget Planning", "家庭预算词汇", "budgeting", "预算", "budget"),
            ("Inflation Talk", "通货膨胀词汇", "inflation", "通胀", "inflation"),
            ("Exchange Rates", "汇率外汇词汇", "forex", "汇率", "forex"),
            ("P2P Lending", "网贷借贷词汇", "P2P lending", "网贷", "P2P"),
            ("Financial Scams", "金融诈骗词汇", "financial fraud", "诈骗", "fraud"),
            ("Financial News", "财经新闻词汇", "financial news", "财经", "finance news"),
            ("Company Valuation", "企业估值词汇", "valuation", "估值", "valuation"),
            ("IPO Process", "上市IPO词汇", "IPO", "上市", "IPO"),
            ("Bonds & Fixed Income", "债券固收词汇", "bonds", "债券", "bonds"),
            ("Gold Investment", "黄金投资词汇", "gold investment", "黄金", "gold"),
            ("Financial Goals", "财务目标规划", "financial goals", "目标", "goals"),
        ],
    },
    63: {
        "dir": "Book63_Fitness",
        "filename": "ZTurns_Book63_Fitness.md",
        "title": "Fitness in Chinese",
        "subtitle": "健身运动中文词汇",
        "color": "#2E7D32",
        "chapters": [
            ("Gym Registration", "健身房办卡", "gym membership", "健身房", "gym"),
            ("Equipment Names", "健身器械词汇", "gym equipment", "器械", "equipment"),
            ("Personal Trainer", "私人教练沟通", "personal trainer", "私教", "trainer"),
            ("Workout Routines", "训练计划词汇", "workout plans", "训练", "workout"),
            ("Muscle Groups", "肌肉群名称词汇", "muscle groups", "肌肉", "muscle"),
            ("Cardio Exercise", "有氧运动词汇", "cardio", "有氧", "cardio"),
            ("Strength Training", "力量训练词汇", "strength training", "力量", "strength"),
            ("Yoga & Stretching", "瑜伽拉伸词汇", "yoga", "瑜伽", "yoga"),
            ("Running Culture", "跑步文化词汇", "running", "跑步", "running"),
            ("Swimming", "游泳相关词汇", "swimming", "游泳", "swimming"),
            ("Group Classes", "团课集体操词汇", "group fitness", "团课", "group class"),
            ("Sports Nutrition", "运动营养词汇", "sports nutrition", "营养", "nutrition"),
            ("Protein & Supplements", "蛋白粉营养品", "supplements", "蛋白粉", "protein"),
            ("Diet & Weight Loss", "减脂减肥词汇", "weight loss", "减肥", "diet"),
            ("Body Composition", "体脂肌肉词汇", "body composition", "体脂", "body comp"),
            ("Injury Prevention", "运动损伤词汇", "injury prevention", "损伤", "injury"),
            ("Traditional Chinese Exercise", "太极气功词汇", "tai chi", "太极", "tai chi"),
            ("Cycling & Spinning", "骑行单车词汇", "cycling", "骑行", "cycling"),
            ("Martial Arts", "武术搏击词汇", "martial arts", "武术", "martial arts"),
            ("Sports Events", "运动赛事词汇", "sports events", "赛事", "events"),
            ("Fitness Apps", "健身App词汇", "fitness apps", "App", "app"),
            ("Recovery Methods", "恢复休息词汇", "recovery", "恢复", "recovery"),
            ("Mental Health & Fitness", "运动心理健康", "mental fitness", "心理", "mental"),
            ("Gym Etiquette", "健身房礼仪词汇", "gym etiquette", "礼仪", "etiquette"),
            ("Outdoor Exercise", "户外运动词汇", "outdoor fitness", "户外", "outdoor"),
        ],
    },
    64: {
        "dir": "Book64_TravelPhoto",
        "filename": "ZTurns_Book64_TravelPhoto.md",
        "title": "Travel Photography Chinese",
        "subtitle": "旅行摄影中文实战",
        "color": "#6A1B9A",
        "chapters": [
            ("Planning the Trip", "旅行计划词汇", "trip planning", "旅行", "travel"),
            ("Booking Transport", "订票交通词汇", "transport booking", "订票", "booking"),
            ("Train Travel", "高铁火车词汇", "train travel", "高铁", "high-speed rail"),
            ("Flight Language", "飞机航班词汇", "flight vocabulary", "航班", "flight"),
            ("Hotel Check-in", "酒店入住词汇", "hotel vocabulary", "酒店", "hotel"),
            ("Tourist Attractions", "景区景点词汇", "tourist sites", "景区", "attraction"),
            ("Asking for Directions", "问路指路词汇", "directions", "问路", "directions"),
            ("Camera Settings", "相机参数词汇", "camera settings", "相机", "camera"),
            ("Photography Terms", "摄影技巧词汇", "photography", "摄影", "photography"),
            ("Scenic Spots", "拍照打卡词汇", "photo spots", "打卡", "photo spot"),
            ("Food Travel", "美食旅行词汇", "food tourism", "美食", "food travel"),
            ("Cultural Sites", "历史文化词汇", "cultural sites", "历史", "culture"),
            ("Nature Photography", "自然风景词汇", "nature photography", "自然", "nature"),
            ("Street Photography", "街拍城市词汇", "street photography", "街拍", "street"),
            ("Portrait Photography", "人物肖像词汇", "portrait photography", "肖像", "portrait"),
            ("Golden Hour", "拍摄时机词汇", "golden hour", "光线", "lighting"),
            ("Editing Photos", "后期修图词汇", "photo editing", "修图", "editing"),
            ("Sharing on WeChat", "发朋友圈词汇", "social sharing", "朋友圈", "moments"),
            ("Travel Vlogging", "旅行视频词汇", "travel vlogging", "视频", "vlog"),
            ("Travel Insurance", "旅行保险词汇", "travel insurance", "保险", "insurance"),
            ("Budget Travel", "穷游预算词汇", "budget travel", "穷游", "budget"),
            ("Luxury Travel", "高端旅行词汇", "luxury travel", "高端", "luxury"),
            ("Travel Companions", "同行旅伴词汇", "travel companions", "旅伴", "companion"),
            ("Travel Safety", "旅行安全词汇", "travel safety", "安全", "safety"),
            ("Souvenir Shopping", "纪念品购物词汇", "souvenirs", "纪念品", "souvenir"),
        ],
    },
    65: {
        "dir": "Book65_HomeReno",
        "filename": "ZTurns_Book65_HomeReno.md",
        "title": "Home Renovation Chinese",
        "subtitle": "装修家居中文全攻略",
        "color": "#4E342E",
        "chapters": [
            ("Finding a Contractor", "找装修公司", "finding contractors", "装修公司", "contractor"),
            ("Design Consultation", "设计方案咨询", "design consultation", "设计", "design"),
            ("Floor Plans", "户型图读懂", "floor plans", "户型", "floor plan"),
            ("Material Selection", "建材选购词汇", "building materials", "建材", "materials"),
            ("Flooring Options", "地板地砖词汇", "flooring", "地板", "flooring"),
            ("Wall Treatments", "墙面涂料词汇", "wall treatments", "墙面", "walls"),
            ("Kitchen Renovation", "厨房装修词汇", "kitchen renovation", "厨房", "kitchen"),
            ("Bathroom Renovation", "卫生间装修词汇", "bathroom renovation", "卫生间", "bathroom"),
            ("Electrical Work", "水电改造词汇", "electrical work", "水电", "electrical"),
            ("Lighting Design", "灯光设计词汇", "lighting design", "灯光", "lighting"),
            ("Furniture Shopping", "家具选购词汇", "furniture shopping", "家具", "furniture"),
            ("IKEA vs Local", "宜家还是国产", "furniture brands", "宜家", "IKEA"),
            ("Appliances", "家电选购词汇", "home appliances", "家电", "appliances"),
            ("Smart Home", "智能家居词汇", "smart home", "智能家居", "smart home"),
            ("Decoration Style", "装修风格词汇", "interior design styles", "风格", "style"),
            ("Storage Solutions", "收纳整理词汇", "storage solutions", "收纳", "storage"),
            ("Garden & Balcony", "阳台花园词汇", "balcony garden", "阳台", "balcony"),
            ("Renovation Budget", "装修预算控制", "renovation budget", "预算", "budget"),
            ("Contractor Disputes", "与装修公司纠纷", "contractor disputes", "纠纷", "dispute"),
            ("Moving In", "搬家入住词汇", "moving in", "搬家", "moving"),
            ("Property Purchase", "买房流程词汇", "property purchase", "买房", "buying"),
            ("Renting Language", "租房合同词汇", "renting", "租房", "renting"),
            ("Neighborhood Talk", "小区物业词汇", "neighborhood", "小区", "community"),
            ("Home Maintenance", "日常维修词汇", "home maintenance", "维修", "maintenance"),
            ("Green Home", "环保节能词汇", "green home", "环保", "eco-friendly"),
        ],
    },
    66: {
        "dir": "Book66_EV",
        "filename": "ZTurns_Book66_EV.md",
        "title": "Electric Vehicle Chinese",
        "subtitle": "新能源汽车中文词汇",
        "color": "#00695C",
        "chapters": [
            ("EV Brands in China", "中国电动车品牌", "EV brands", "品牌", "brand"),
            ("Battery Technology", "电池技术词汇", "battery tech", "电池", "battery"),
            ("Charging at Home", "家用充电词汇", "home charging", "充电", "charging"),
            ("Public Charging", "公共充电桩词汇", "public charging", "充电桩", "charger"),
            ("Range Anxiety", "续航焦虑词汇", "range anxiety", "续航", "range"),
            ("Smart Driving Features", "智能驾驶词汇", "smart driving", "智能", "smart drive"),
            ("EV vs Fuel Car", "油车电车比较", "EV vs ICE", "油车", "ICE vs EV"),
            ("BYD Vocabulary", "比亚迪相关词汇", "BYD", "比亚迪", "BYD"),
            ("NIO & Xiaopeng", "蔚来小鹏词汇", "NIO Xpeng", "蔚来", "NIO"),
            ("Tesla in China", "特斯拉中文词汇", "Tesla China", "特斯拉", "Tesla"),
            ("EV Test Drive", "试驾体验词汇", "test drive", "试驾", "test drive"),
            ("Buying Process", "购车流程词汇", "purchase process", "购车", "buying"),
            ("Government Subsidies", "补贴政策词汇", "EV subsidies", "补贴", "subsidy"),
            ("License Plates", "新能源牌照词汇", "license plates", "牌照", "plates"),
            ("Insurance for EVs", "电动车保险词汇", "EV insurance", "保险", "insurance"),
            ("Maintenance Costs", "电动车维护词汇", "maintenance", "维护", "maintenance"),
            ("Software Updates", "车机OTA词汇", "OTA updates", "OTA", "updates"),
            ("Autopilot Features", "自动驾驶词汇", "autopilot", "自动驾驶", "autopilot"),
            ("EV Community", "车主社群词汇", "EV community", "车主", "owner"),
            ("Road Trips in EV", "电动车长途旅行", "EV road trips", "长途", "road trip"),
            ("EV Industry News", "新能源行业资讯", "EV industry", "行业", "industry"),
            ("Charging Networks", "充电网络运营商", "charging networks", "运营商", "network"),
            ("Second-hand EVs", "二手电动车词汇", "used EVs", "二手车", "used car"),
            ("EV Racing & Sport", "电动赛车词汇", "EV racing", "赛车", "racing"),
            ("Future of EVs", "电动车未来趋势", "EV future", "未来", "future"),
        ],
    },
    67: {
        "dir": "Book67_CleanEnergy",
        "filename": "ZTurns_Book67_CleanEnergy.md",
        "title": "Clean Energy Chinese",
        "subtitle": "清洁能源中文实战",
        "color": "#F57F17",
        "chapters": [
            ("Solar Energy Basics", "太阳能基础词汇", "solar energy", "太阳能", "solar"),
            ("Wind Power", "风力发电词汇", "wind power", "风力", "wind"),
            ("Hydropower", "水力发电词汇", "hydropower", "水电", "hydro"),
            ("Nuclear Energy", "核能相关词汇", "nuclear energy", "核能", "nuclear"),
            ("Carbon Neutrality", "碳中和碳达峰", "carbon neutrality", "碳中和", "carbon neutral"),
            ("Green Finance", "绿色金融词汇", "green finance", "绿色金融", "green finance"),
            ("Energy Storage", "储能技术词汇", "energy storage", "储能", "storage"),
            ("Smart Grid", "智能电网词汇", "smart grid", "电网", "grid"),
            ("Energy Policy", "能源政策词汇", "energy policy", "政策", "policy"),
            ("Renewable Certificates", "绿证绿电词汇", "green certificates", "绿证", "certificate"),
            ("Carbon Trading", "碳排放交易词汇", "carbon trading", "碳交易", "carbon trade"),
            ("Hydrogen Energy", "氢能源词汇", "hydrogen energy", "氢能", "hydrogen"),
            ("Energy Efficiency", "节能减排词汇", "energy efficiency", "节能", "efficiency"),
            ("Building Energy", "建筑节能词汇", "building energy", "建筑", "building"),
            ("Industrial Decarbonization", "工业脱碳词汇", "decarbonization", "脱碳", "decarb"),
            ("Climate Change", "气候变化词汇", "climate change", "气候", "climate"),
            ("ESG Investing", "ESG投资词汇", "ESG investing", "ESG", "ESG"),
            ("Energy Companies", "新能源公司词汇", "energy companies", "公司", "company"),
            ("Offshore Wind", "海上风电词汇", "offshore wind", "海上", "offshore"),
            ("Rooftop Solar", "屋顶光伏词汇", "rooftop solar", "光伏", "photovoltaic"),
            ("Electric Grid", "电力系统词汇", "power grid", "电力", "power"),
            ("Energy Transition", "能源转型词汇", "energy transition", "转型", "transition"),
            ("Climate Summit", "气候峰会词汇", "climate summit", "峰会", "summit"),
            ("Green Jobs", "绿色就业词汇", "green jobs", "就业", "jobs"),
            ("Future Energy", "未来能源趋势", "future energy", "未来", "future"),
        ],
    },
    68: {
        "dir": "Book68_Robotics",
        "filename": "ZTurns_Book68_Robotics.md",
        "title": "Robotics in Chinese",
        "subtitle": "机器人AI中文词汇",
        "color": "#283593",
        "chapters": [
            ("Robot Types", "机器人种类词汇", "robot types", "机器人", "robot"),
            ("AI Basics", "人工智能基础词汇", "AI basics", "人工智能", "AI"),
            ("Machine Learning", "机器学习词汇", "machine learning", "机器学习", "ML"),
            ("Industrial Robots", "工业机器人词汇", "industrial robots", "工业", "industrial"),
            ("Service Robots", "服务机器人词汇", "service robots", "服务", "service"),
            ("Humanoid Robots", "仿人机器人词汇", "humanoid robots", "仿人", "humanoid"),
            ("Drone Technology", "无人机技术词汇", "drones", "无人机", "drone"),
            ("Autonomous Vehicles", "自动驾驶词汇", "autonomous vehicles", "自动驾驶", "AV"),
            ("Computer Vision", "计算机视觉词汇", "computer vision", "视觉", "vision"),
            ("Natural Language AI", "自然语言处理词汇", "NLP", "自然语言", "NLP"),
            ("Robot Programming", "机器人编程词汇", "robot programming", "编程", "programming"),
            ("AI Chips", "AI芯片词汇", "AI chips", "芯片", "chip"),
            ("Large Language Models", "大语言模型词汇", "LLMs", "大模型", "LLM"),
            ("AI Applications", "AI应用词汇", "AI applications", "应用", "application"),
            ("Robot Ethics", "机器人伦理词汇", "robot ethics", "伦理", "ethics"),
            ("AI in Manufacturing", "AI制造业词汇", "AI manufacturing", "制造", "manufacturing"),
            ("AI in Healthcare", "医疗AI词汇", "AI healthcare", "医疗", "healthcare"),
            ("AI in Education", "教育AI词汇", "AI education", "教育", "education"),
            ("Robot Competition", "机器人竞赛词汇", "robot competition", "竞赛", "competition"),
            ("AI Startup Ecosystem", "AI创业生态词汇", "AI startups", "创业", "startup"),
            ("China AI Policy", "中国AI政策词汇", "China AI policy", "政策", "policy"),
            ("AI Safety", "AI安全词汇", "AI safety", "安全", "safety"),
            ("Automation Impact", "自动化就业影响", "automation impact", "自动化", "automation"),
            ("Robot Maintenance", "机器人维护词汇", "robot maintenance", "维护", "maintenance"),
            ("Future of Robotics", "机器人未来趋势", "robotics future", "未来", "future"),
        ],
    },
    69: {
        "dir": "Book69_Quantum",
        "filename": "ZTurns_Book69_Quantum.md",
        "title": "Quantum Tech Chinese",
        "subtitle": "量子半导体中文实战",
        "color": "#4A148C",
        "chapters": [
            ("Quantum Basics", "量子基础词汇", "quantum basics", "量子", "quantum"),
            ("Quantum Computing", "量子计算词汇", "quantum computing", "量子计算", "quantum computing"),
            ("Semiconductor Basics", "半导体基础词汇", "semiconductor basics", "半导体", "semiconductor"),
            ("Chip Design", "芯片设计词汇", "chip design", "芯片设计", "chip design"),
            ("SMIC & Foundries", "中芯国际代工词汇", "chip foundries", "代工", "foundry"),
            ("Huawei Chips", "华为芯片词汇", "Huawei chips", "华为", "Huawei"),
            ("Memory Technology", "内存存储词汇", "memory tech", "内存", "memory"),
            ("Photolithography", "光刻机技术词汇", "lithography", "光刻", "lithography"),
            ("Quantum Cryptography", "量子加密词汇", "quantum crypto", "加密", "cryptography"),
            ("Quantum Communication", "量子通信词汇", "quantum communication", "通信", "communication"),
            ("Supply Chain Chips", "芯片供应链词汇", "chip supply chain", "供应链", "supply chain"),
            ("TSMC Discussion", "台积电相关词汇", "TSMC", "台积电", "TSMC"),
            ("Intel & AMD", "英特尔AMD词汇", "Intel AMD", "英特尔", "Intel"),
            ("Nvidia in China", "英伟达中国词汇", "Nvidia China", "英伟达", "Nvidia"),
            ("Chip Sanctions", "芯片制裁词汇", "chip sanctions", "制裁", "sanctions"),
            ("Moore's Law", "摩尔定律词汇", "Moore's Law", "摩尔定律", "Moore's law"),
            ("Quantum Entanglement", "量子纠缠词汇", "quantum entanglement", "纠缠", "entanglement"),
            ("Quantum Supremacy", "量子优越性词汇", "quantum supremacy", "优越性", "supremacy"),
            ("Chinese Quantum Research", "中国量子研究", "China quantum research", "研究", "research"),
            ("Tech Sovereignty", "科技自主词汇", "tech sovereignty", "自主", "sovereignty"),
            ("Quantum Sensing", "量子传感词汇", "quantum sensing", "传感", "sensing"),
            ("Chip Investment", "芯片投资词汇", "chip investment", "投资", "investment"),
            ("Semiconductor Jobs", "半导体就业词汇", "semiconductor jobs", "就业", "jobs"),
            ("Quantum Internet", "量子互联网词汇", "quantum internet", "互联网", "internet"),
            ("Future Quantum Tech", "量子技术未来", "quantum future", "未来", "future"),
        ],
    },
    70: {
        "dir": "Book70_Space",
        "filename": "ZTurns_Book70_Space.md",
        "title": "Space Exploration Chinese",
        "subtitle": "航天探索中文词汇",
        "color": "#01579B",
        "chapters": [
            ("China Space Program", "中国航天历史", "China space history", "航天", "space program"),
            ("Rocket Technology", "火箭发射词汇", "rocket technology", "火箭", "rocket"),
            ("Satellites", "卫星通信词汇", "satellites", "卫星", "satellite"),
            ("Space Station", "空间站词汇", "space station", "空间站", "space station"),
            ("Moon Mission", "月球探测词汇", "moon mission", "月球", "moon"),
            ("Mars Exploration", "火星探测词汇", "Mars exploration", "火星", "Mars"),
            ("Astronaut Life", "航天员生活词汇", "astronaut life", "航天员", "astronaut"),
            ("Spacewalk Language", "太空行走词汇", "spacewalk", "出舱", "spacewalk"),
            ("Space Science", "空间科学词汇", "space science", "空间科学", "space science"),
            ("Commercial Space", "商业航天词汇", "commercial space", "商业航天", "commercial"),
            ("GPS & Navigation", "北斗导航词汇", "navigation systems", "北斗", "Beidou"),
            ("Telescope Technology", "望远镜天文词汇", "telescopes", "望远镜", "telescope"),
            ("SpaceX Discussion", "SpaceX讨论词汇", "SpaceX", "SpaceX", "SpaceX"),
            ("Space Tourism", "太空旅游词汇", "space tourism", "太空旅游", "space tourism"),
            ("Space Debris", "太空垃圾词汇", "space debris", "太空垃圾", "space debris"),
            ("International Cooperation", "航天国际合作", "space cooperation", "合作", "cooperation"),
            ("Space Economy", "太空经济词汇", "space economy", "太空经济", "space economy"),
            ("Astronomy Basics", "天文基础词汇", "astronomy basics", "天文", "astronomy"),
            ("Black Holes", "黑洞宇宙词汇", "black holes", "黑洞", "black hole"),
            ("Chinese Constellations", "中国星座词汇", "Chinese astronomy", "星座", "constellation"),
            ("Space Materials", "航天材料词汇", "space materials", "材料", "materials"),
            ("Launch Sites", "发射场词汇", "launch sites", "发射场", "launch site"),
            ("Space Food", "航天食品词汇", "space food", "航天食品", "space food"),
            ("Space Medicine", "太空医学词汇", "space medicine", "太空医学", "space medicine"),
            ("Future Space Vision", "人类太空未来", "future space", "未来", "future"),
        ],
    },
}

# ── Chapter content generator ─────────────────────────────────────────────────

def make_chapter(book_num: int, ch_num: int, en_title: str, zh_title: str,
                 topic_en: str, key_word_zh: str, key_word_en: str,
                 note_snippet: str = "") -> str:
    """Generate a rich, Book02-style chapter with ~500 lines of content."""

    # Varied teacher/student names for dialogue realism
    students = ["Maria", "David", "Yuki", "Ahmed", "Sarah", "James", "Lisa", "Carlos"]
    s1 = students[(ch_num * 3) % len(students)]
    s2 = students[(ch_num * 3 + 1) % len(students)]

    # Build 20 vocabulary items (more than before)
    vocab_items = [
        (key_word_zh, "kěyǐ", "core term", "noun/verb", f"核心词汇，贯穿本章"),
        ("理解", "lǐjiě", "to understand", "verb", "理解 = understand deeply, not just know"),
        ("表达", "biǎodá", "to express", "verb", "表达自己 = express yourself"),
        ("文化", "wénhuà", "culture", "noun", "文化背景 = cultural background"),
        ("实践", "shíjiàn", "practice / to practice", "noun/verb", "实践出真知 = practice makes perfect"),
        ("习惯", "xíguàn", "habit / custom", "noun/verb", "养成习惯 = develop a habit"),
        ("关系", "guānxi", "relationship / connection", "noun", "建立关系 = build a relationship"),
        ("方式", "fāngshì", "way / method / manner", "noun", "用这种方式 = in this way"),
        ("重要", "zhòngyào", "important", "adjective", "非常重要 = extremely important"),
        ("注意", "zhùyì", "to pay attention / to notice", "verb", "注意一下 = just pay attention"),
        ("情况", "qíngkuàng", "situation / circumstances", "noun", "根据情况 = depending on the situation"),
        ("经验", "jīngyàn", "experience", "noun", "工作经验 = work experience"),
        ("建议", "jiànyì", "suggestion / to suggest", "noun/verb", "我建议 = I suggest"),
        ("了解", "liǎojiě", "to understand / to find out", "verb", "了解情况 = get to know the situation"),
        ("发现", "fāxiàn", "to discover / to find", "verb", "我发现 = I found that / I noticed"),
        ("感觉", "gǎnjué", "to feel / feeling", "noun/verb", "感觉很好 = feels great"),
        ("可能", "kěnéng", "maybe / possible", "adverb/adj", "可能是 = it's possible that"),
        ("需要", "xūyào", "to need", "verb", "你需要 = you need to"),
        ("已经", "yǐjīng", "already", "adverb", "已经完成 = already completed"),
        ("还是", "háishi", "or / still", "conjunction", "你还是不明白 = you still don't understand"),
    ]

    vocab_table = "\n".join(
        f"| {zh} | {py} | {en} | {pos} | {note} |"
        for zh, py, en, pos, note in vocab_items
    )

    # Generate 3 dialogues with 8 turns each
    dialogue_block = f"""**Dialogue 1: First Encounter**

*Setting: Tony's classroom. {s1} has just arrived in China and is navigating {topic_en} for the first time.*

Tony: 好，今天我们来聊{key_word_zh}。{s1}，你有没有遇到过这种情况？
*Hǎo, jīntiān wǒmen lái liáo {key_word_zh}. {s1}, nǐ yǒu méiyǒu yùdào guò zhè zhǒng qíngkuàng?*
*Okay, today let's talk about {key_word_en}. {s1}, have you encountered this kind of situation?*

{s1}: 有，上个星期我就遇到了，但是我不知道怎么说。
*Yǒu, shàng gè xīngqī wǒ jiù yùdào le, dànshì wǒ bù zhīdào zěnme shuō.*
*Yes, I encountered it just last week, but I didn't know what to say.*

Tony: 这很正常。第一次面对{key_word_zh}，很多人都不知道从哪里开始。
*Zhè hěn zhèngcháng. Dì yī cì miàn duì {key_word_zh}, hěn duō rén dōu bù zhīdào cóng nǎlǐ kāishǐ.*
*That's completely normal. Facing {key_word_en} for the first time, many people don't know where to begin.*

{s1}: 那我应该怎么做？有什么技巧吗？
*Nà wǒ yīnggāi zěnme zuò? Yǒu shénme jìqiǎo ma?*
*So what should I do? Are there any techniques?*

Tony: 当然有。最重要的是要先了解文化背景，然后再学语言表达。
*Dāngrán yǒu. Zuì zhòngyào de shì yào xiān liǎojiě wénhuà bèijǐng, ránhòu zài xué yǔyán biǎodá.*
*Of course there are. The most important thing is to first understand the cultural context, then learn the language expressions.*

{s1}: 我明白了。文化和语言是分不开的，对吗？
*Wǒ míngbái le. Wénhuà hé yǔyán shì fēn bù kāi de, duì ma?*
*I understand. Culture and language are inseparable, right?*

Tony: 说得非常好！在中国，很多表达方式背后都有深厚的文化含义。
*Shuō de fēicháng hǎo! Zài Zhōngguó, hěn duō biǎodá fāngshì bèihòu dōu yǒu shēnhòu de wénhuà hányì.*
*Very well said! In China, many ways of expression carry deep cultural meanings behind them.*

{s1}: 那我们今天能不能多学几个这样的表达？
*Nà wǒmen jīntiān néng bu néng duō xué jǐ gè zhèyàng de biǎodá?*
*Can we learn a few more such expressions today?*

Tony: 当然！这正是我们接下来要做的事情。
*Dāngrán! Zhè zhèng shì wǒmen jiē xià lái yào zuò de shìqíng.*
*Of course! That's exactly what we're going to do next.*

---

**Dialogue 2: Real-World Application**

*Setting: {s1} and {s2} practice together after class, applying what they learned about {topic_en}.*

{s1}: {s2}，你上课的时候听懂了吗？关于{key_word_zh}的部分。
*{s1}: {s2}, nǐ shàngkè de shíhòu tīng dǒng le ma? Guānyú {key_word_zh} de bùfen.*
*{s1}: {s2}, did you understand during class? The part about {key_word_en}.*

{s2}: 大部分听懂了，但是有一个地方不太明白。
*Dà bùfen tīng dǒng le, dànshì yǒu yī gè dìfāng bù tài míngbái.*
*I understood most of it, but there's one part I wasn't too clear on.*

{s1}: 哪个部分？我来帮你解释一下。
*Nǎ gè bùfen? Wǒ lái bāng nǐ jiěshì yīxià.*
*Which part? Let me help explain it.*

{s2}: 就是为什么在中国，处理{key_word_zh}的方式跟我们国家那么不一样？
*Jiùshì wèishénme zài Zhōngguó, chǔlǐ {key_word_zh} de fāngshì gēn wǒmen guójiā nàme bù yīyàng?*
*Why is the way of dealing with {key_word_en} in China so different from our country?*

{s1}: Tony说过，这是因为中国有自己独特的历史和文化传统。
*Tony shuō guò, zhè shì yīnwèi Zhōngguó yǒu zìjǐ dútè de lìshǐ hé wénhuà chuántǒng.*
*Tony said it's because China has its own unique history and cultural traditions.*

{s2}: 对，我也记得他说过。那我们来练习一下刚才学的表达方式吧。
*Duì, wǒ yě jìde tā shuō guò. Nà wǒmen lái liànxí yīxià gāngcái xué de biǎodá fāngshì ba.*
*Right, I remember him saying that too. Let's practice the expressions we just learned.*

{s1}: 好主意。你先说，我来纠正。
*Hǎo zhǔyì. Nǐ xiān shuō, wǒ lái jiūzhèng.*
*Good idea. You go first, I'll correct.*

{s2}: 好的，关于{key_word_zh}，我觉得最重要的是先了解文化背景。
*Hǎo de, guānyú {key_word_zh}, wǒ juéde zuì zhòngyào de shì xiān liǎojiě wénhuà bèijǐng.*
*Okay. Regarding {key_word_en}, I think the most important thing is to first understand the cultural background.*

---

**Dialogue 3: Tony's Teaching Story**

*Setting: Tony shares a real story from his teaching experience about {topic_en}.*

Tony: 我想给你们讲一个真实的故事。有一次，一个我的学生……
*Wǒ xiǎng gěi nǐmen jiǎng yī gè zhēnshí de gùshi. Yǒu yī cì, yī gè wǒ de xuésheng……*
*I want to tell you a real story. Once, one of my students...*

{s1}: 这个学生也是外国人吗？
*Zhège xuésheng yě shì wàiguó rén ma?*
*Was this student also a foreigner?*

Tony: 对，他来自欧洲，在中国工作了两年。他觉得自己的中文已经很好了，但是在处理{key_word_zh}的时候，还是经常出错。
*Duì, tā lái zì Ōuzhōu, zài Zhōngguó gōngzuò le liǎng nián. Tā juéde zìjǐ de Zhōngwén yǐjīng hěn hǎo le, dànshì zài chǔlǐ {key_word_zh} de shíhòu, háishi jīngcháng chū cuò.*
*Yes, he came from Europe and had worked in China for two years. He felt his Chinese was already good, but when dealing with {key_word_en}, he still made frequent mistakes.*

{s2}: 他出了什么错？
*Tā chū le shénme cuò?*
*What mistakes did he make?*

Tony: 他把自己国家的思维方式直接翻译成中文，结果虽然语法对了，但是感觉不对。
*Tā bǎ zìjǐ guójiā de sīwéi fāngshì zhíjiē fānyì chéng Zhōngwén, jiéguǒ suīrán yǔfǎ duì le, dànshì gǎnjué bù duì.*
*He directly translated his own country's way of thinking into Chinese. The grammar was correct, but it felt wrong.*

{s1}: 语法对但感觉不对？这是什么意思？
*Yǔfǎ duì dàn gǎnjué bù duì? Zhè shì shénme yìsi?*
*Grammar correct but feeling wrong? What does that mean?*

Tony: 这就是我们今天要深入探讨的核心问题。语言和文化是密不可分的。
*Zhè jiùshì wǒmen jīntiān yào shēnrù tàntǎo de héxīn wèntí. Yǔyán hé wénhuà shì mì bù kě fēn de.*
*This is exactly the core issue we're going to explore in depth today. Language and culture are inseparable.*"""

    # Grammar section with 4 patterns
    grammar_section = f"""**Pattern 1: 先…然后再… (First... then...)**

This is one of the most useful sequential patterns in Chinese. It signals that the first step must be completed before the second begins.

**Structure:** 需要/要先 + [Action 1]，然后再 + [Action 2]

**Chinese:** 你需要先了解{key_word_zh}，然后再做决定。
**Pinyin:** Nǐ xūyào xiān liǎojiě {key_word_zh}, ránhòu zài zuò juédìng.
**Literal:** You need first understand {key_word_en}, then again make decision.
**English:** You need to first understand {key_word_en}, then make a decision.

**More examples:**
- 你先把内容看完，然后再发表意见。(Read the content first, then express your opinion.)
- 在中国做生意，要先建立关系，然后再谈合同。(In Chinese business, build the relationship first, then discuss contracts.)
- 学语言要先打好基础，然后再练习高级表达。(When learning a language, first build a solid foundation, then practice advanced expressions.)

---

**Pattern 2: 虽然…但是… (Although... but...)**

This concessive pattern is incredibly common in Chinese discourse. Unlike English, the "but" (但是) must appear explicitly even when "although" (虽然) is already used.

**Structure:** 虽然 + [Concession]，但是 + [Main Point]

**Chinese:** 虽然{key_word_zh}很复杂，但是只要掌握了基本规律，就不难了。
**Pinyin:** Suīrán {key_word_zh} hěn fùzá, dànshì zhǐyào zhǎngwò le jīběn guīlǜ, jiù bù nán le.
**English:** Although {key_word_en} is complex, as long as you grasp the basic patterns, it's not difficult.

**More examples:**
- 虽然他中文说得不流利，但是他的意思表达得很清楚。(Although his Chinese isn't fluent, he expresses his meaning very clearly.)
- 虽然第一次做不好，但是多练习就会进步。(Although you won't do well the first time, you'll improve with more practice.)

---

**Pattern 3: 关于…来说 (As for... / Regarding...)**

Use 关于 (guānyú) to frame a topic, and 来说 (lái shuō) to introduce a perspective.

**Chinese:** 关于{key_word_zh}来说，文化背景比语言本身更重要。
**Pinyin:** Guānyú {key_word_zh} lái shuō, wénhuà bèijǐng bǐ yǔyán běnshēn gèng zhòngyào.
**English:** As far as {key_word_en} is concerned, cultural background is more important than the language itself.

**Variation — 对…来说 (For someone):**
- 对外国人来说，掌握{key_word_zh}需要时间。(For foreigners, mastering {key_word_en} takes time.)
- 对中国人来说，这是非常自然的事情。(For Chinese people, this is a very natural thing.)

---

**Pattern 4: 只要…就… (As long as... then...)**

This conditional pattern expresses that a sufficient condition leads to a guaranteed result.

**Chinese:** 只要多练习，就一定能学好{key_word_zh}。
**Pinyin:** Zhǐyào duō liànxí, jiù yīdìng néng xué hǎo {key_word_zh}.
**English:** As long as you practice more, you will definitely be able to learn {key_word_en} well.

- 只要你愿意学，就没有学不会的东西。(As long as you're willing to learn, there's nothing you can't learn.)
- 只要方法对，学中文其实不难。(As long as the method is right, learning Chinese is actually not difficult.)"""

    # Practice section with 6 exercises
    practice_section = f"""**Exercise 1 — Translation:**
Translate into Chinese: "I need to first understand {key_word_en}, then make a decision."
**Answer:** 我需要先了解{key_word_zh}，然后再做决定。(Wǒ xūyào xiān liǎojiě {key_word_zh}, ránhòu zài zuò juédìng.)

**Exercise 2 — Fill in the blank:**
虽然___很困难，但是_____。(Complete the sentence about learning {key_word_en}.)
**Sample answer:** 虽然{key_word_zh}很困难，但是只要坚持练习就能进步。

**Exercise 3 — Create a sentence:**
Use 关于…来说 to make a sentence about {key_word_en} from your own perspective.
**Sample answer:** 关于{key_word_zh}来说，我觉得文化理解是最重要的。

**Exercise 4 — Dialogue reconstruction:**
Put these lines in the correct order to form a logical exchange about {key_word_en}:
a) 我明白了，谢谢你的解释。
b) 你需要先了解文化背景。
c) 我应该怎么处理{key_word_zh}？
d) 然后再学具体的语言表达。
**Answer:** c → b → d → a

**Exercise 5 — Real-world task:**
Imagine you are explaining {key_word_en} to a Chinese friend who has never experienced it. Write 3-5 sentences in Chinese describing what it is and why it matters.
**Guidance:** Use 关于, 虽然…但是…, and 只要…就… in your explanation.

**Exercise 6 — Cultural reflection:**
How is {topic_en} handled differently in China vs. your home country? Write 2 sentences in Chinese comparing the two approaches.
**Sample:** 在中国，{key_word_zh}通常要考虑关系和面子。在我的国家，更直接一些。"""

    # Cultural insight — long-form prose
    cultural_section = f"""Understanding **{key_word_zh}** ({key_word_en}) in China requires more than vocabulary — it demands a shift in cultural perspective.

China's approach to {topic_en} has been shaped by thousands of years of Confucian philosophy, which places enormous value on **harmony (和谐 héxié)**, **relationships (关系 guānxi)**, and **face (面子 miànzi)**. These three concepts permeate every aspect of Chinese social and professional life, including how people navigate {topic_en}.

**Harmony** means avoiding direct confrontation whenever possible. In practical terms, this means Chinese speakers often express disagreement or difficulty indirectly — through hesitation, subject-changing, or soft language like 可能 (maybe) and 有一点 (a little bit). When dealing with {key_word_zh}, foreigners who are trained to be direct often misread this indirectness as agreement, only to be surprised later.

**Relationships** are the operating system beneath the surface of Chinese society. Before any transaction, negotiation, or request, there is an implicit question: *What is our relationship?* The quality and depth of the relationship determines what can be asked, how it should be asked, and what the likely outcome will be. This is why Chinese professionals invest so much time in dinners, small talk, and favors — they are building the relational infrastructure that makes everything else possible.

**Face** — both giving it (给面子 gěi miànzi) and protecting it (保面子 bǎo miànzi) — operates as an invisible social currency. A request phrased in a way that publicly embarrasses someone will fail not because of the request's content, but because of the shame it creates. Conversely, a well-placed compliment or a graceful handling of a difficult situation earns enormous goodwill.

For foreigners learning to navigate {key_word_zh}, Tony's advice is consistent: **observe first, speak second.** Watch how Chinese people around you handle similar situations. Notice the pacing, the tone, the level of formality. Then practice using the vocabulary you've learned in low-stakes situations before applying it in high-stakes moments.

The students who succeed fastest are not those with the largest vocabulary — they are those who understand that Chinese communication operates on multiple levels simultaneously: what is said, what is meant, and what is felt."""

    # Optional: insert real teaching note
    getnote_section = ""
    if note_snippet:
        getnote_section = f"""
## 10. Tony's Real Classroom Notes 真实课堂记录

*The following is an excerpt from Tony's actual teaching sessions, captured in real-time:*

---

{note_snippet[:1000]}

---

*These notes reflect real conversations and questions from Tony's students. The struggles and insights shared here are authentic — every learner faces similar challenges on their journey.*
"""

    lines = [
        f"# Chapter {ch_num}: {en_title} · {zh_title}",
        "",
        "## 1. Real Scene 真实场景",
        "",
        f"Tony stood at the front of the classroom and looked at his students with a warm smile. \"今天我们来聊一个非常实用的话题，\" he said. \"{en_title} — {zh_title}.\"",
        "",
        f"{s1} leaned forward with obvious curiosity. \"I've been wondering about this,\" {s1} said. \"Every time I try to deal with {topic_en} in Chinese, something feels off — like I'm saying the right words but in the wrong way.\"",
        "",
        "\"That feeling,\" Tony said, \"is one of the most important signals you can have as a language learner. It means you're hearing the gap between translation and communication. Let's close that gap today.\"",
        "",
        f"He wrote **{key_word_zh}** on the board — the Chinese term for {key_word_en} — and let the class study it for a moment.",
        "",
        f"\"This character, or these characters, carry more meaning than any dictionary definition can capture,\" Tony continued. \"They are embedded in culture, in history, in the way Chinese people see the world. By the end of today's class, you won't just know the word — you'll understand it.\"",
        "",
        f"The class was quiet, attentive. {s2} had already opened a notebook. Outside, the sounds of Shanghai's afternoon traffic filtered through the windows — motorbikes, horns, the occasional announcement from a nearby subway station. The city itself was a constant reminder of why they were here, learning this language, one character at a time.",
        "",
        "---",
        "",
        "## 2. Key Vocabulary 核心词汇",
        "",
        "| Chinese | Pinyin | English | Part of Speech | Usage Note |",
        "|---------|--------|---------|----------------|------------|",
        vocab_table,
        "",
        "---",
        "",
        "## 3. Authentic Dialogues 真实对话",
        "",
        dialogue_block,
        "",
        "---",
        "",
        "## 4. Grammar in Context 语法精讲",
        "",
        grammar_section,
        "",
        "---",
        "",
        "## 5. Pronunciation & Tone Guide 发音与声调",
        "",
        f"The key term **{key_word_zh}** requires careful attention to tones. In Mandarin, the same syllable spoken with different tones produces completely different meanings — a fact that trips up learners at every level.",
        "",
        "**Tony's Tone Drill:**",
        f"Say {key_word_zh} three times: once normally, once slowly with exaggerated tones, once at natural conversation speed. Record yourself if possible and compare.",
        "",
        "**Common tone mistakes with related vocabulary:**",
        "- 买 (mǎi, 3rd tone) vs 卖 (mài, 4th tone): buy vs sell — these are often confused in market contexts",
        "- 问 (wèn, 4th tone) vs 闻 (wén, 2nd tone): to ask vs to smell — context saves you most of the time",
        "- 是 (shì, 4th tone) vs 使 (shǐ, 3rd tone): to be vs to use — fast speech can blur these",
        "",
        "**Tony's Trick:** Don't try to *remember* tones in isolation. Always learn a word in a full sentence. Your brain stores tones better in context than as abstract facts.",
        "",
        "---",
        "",
        "## 6. Practice Exercises 练习",
        "",
        practice_section,
        "",
        "---",
        "",
        "## 7. Cultural Deep Dive 文化深度解析",
        "",
        cultural_section,
        "",
        "---",
        "",
        "## 8. Common Mistakes 常见错误",
        "",
        f"Based on Tony's experience teaching hundreds of foreign students, here are the most common mistakes learners make when dealing with {key_word_zh}:",
        "",
        f"**Mistake 1: Direct translation**",
        f"Translating your native language's approach to {topic_en} word-for-word into Chinese. This produces grammatically correct but culturally jarring sentences.",
        f"❌ Wrong approach: Translate literally",
        f"✓ Right approach: Think in the Chinese cultural framework first, then speak",
        "",
        f"**Mistake 2: Ignoring register**",
        f"Using casual language (口语 kǒuyǔ) in formal situations, or overly formal language in casual settings. Chinese has a wider register gap than many Western languages.",
        f"❌ 你好，我要问个事儿。(Too casual for a formal office context)",
        f"✓ 您好，我想请教一个问题。(Appropriately polite)",
        "",
        f"**Mistake 3: Rushing the relationship**",
        f"Getting straight to the point without the expected preliminary small talk. In Chinese communication, especially for {topic_en}, the journey matters as much as the destination.",
        f"❌ Immediately: 我需要你帮我处理{key_word_zh}。",
        f"✓ First: 最近忙吗？……（after some conversation）对了，我有个事情想请你帮忙……",
        "",
        f"**Mistake 4: Not accounting for face**",
        f"Phrasing a request or correction in a way that causes embarrassment. Always soften corrections with 可能 or 也许, and always give the other person a way to agree gracefully.",
        "",
        "---",
        "",
        "## 9. Review & Summary 本章总结",
        "",
        f"In this chapter, we covered **{en_title}** — **{zh_title}** — one of the essential topics for navigating {topic_en} in a Chinese context.",
        "",
        "**Key takeaways:**",
        f"1. The term **{key_word_zh}** carries cultural weight beyond its dictionary definition",
        "2. Sequential patterns (先…然后再…) and concessive patterns (虽然…但是…) are fundamental to Chinese communication",
        "3. Culture shapes language — understanding the Confucian values of harmony, relationship, and face helps you interpret and produce more natural Chinese",
        "4. The most common mistakes come from direct translation — resist the urge to simply render your native language into Chinese",
        "",
        f"**Your homework:** Find one real-life situation this week where you can apply what you learned about {key_word_zh}. It doesn't have to be perfect — the goal is to try, notice, and learn from what happens.",
        "",
        f"*As Tony always says: 学语言不只是学说话，更是学做人。Learning a language is not just learning to speak — it's learning a whole way of being.*",
    ]

    if getnote_section:
        lines.append(getnote_section)

    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def generate_book(book_num: int, book_info: dict) -> None:
    out_dir = OUTPUT_BASE / book_info["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / book_info["filename"]

    # To add your own teaching content, implement load_content_snippets()
    # from content_source_example.py and populate note_snippets here.
    # Example:
    #   from content_source_example import load_content_snippets, BOOK_CONTENT_MAP
    #   if book_num in BOOK_CONTENT_MAP:
    #       mapping = BOOK_CONTENT_MAP[book_num]
    #       snippet = load_content_snippets(mapping["source_file"], mapping["keywords"])
    #       for ch in range(1, 6):
    #           note_snippets[ch] = snippet
    note_snippets: dict[int, str] = {}

    header = f"""# Z Turns Chinese Book {book_num}
## {book_info['title']} — {book_info['subtitle']}
**Author:** Tony Sheng
**Website:** zturnsgo.com
**Teaching Experience:** 3000+ hours of real Chinese teaching
**Series Color:** {book_info['color']}

---

"""

    chapters_md = ""
    for i, ch in enumerate(book_info["chapters"], 1):
        en_title, zh_title, topic_en, key_word_zh, key_word_en = ch
        snippet = note_snippets.get(i, "")
        chapters_md += make_chapter(
            book_num, i, en_title, zh_title, topic_en,
            key_word_zh, key_word_en, snippet
        )

    full_content = header + chapters_md
    out_path.write_text(full_content, encoding="utf-8")
    lines = full_content.count("\n")
    kb = len(full_content.encode("utf-8")) // 1024
    print(f"  Book {book_num}: {book_info['filename']} — {lines} lines, {kb} KB")


def main():
    args = sys.argv[1:]
    if args:
        book_nums = [int(a) for a in args if a.isdigit()]
    else:
        book_nums = list(range(51, 71))

    invalid = [n for n in book_nums if n not in BOOKS]
    if invalid:
        print(f"未知书号: {invalid}")
        sys.exit(1)

    print(f"生成 {len(book_nums)} 本书...")
    for n in book_nums:
        generate_book(n, BOOKS[n])
    print("完成。")


if __name__ == "__main__":
    main()
