#!/usr/bin/env python3
"""
Generate Z Turns Chinese Books 51-70 content as merged MD files.
Each book has 25 chapters with 6 sections each.
"""
import os
from pathlib import Path

OUTPUT_BASE = Path("output")

# ─── Book definitions ───────────────────────────────────────────────
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
            ("Benefits Talk", "谈福利五险一金", "benefits", "福利", "benefits"),
            ("Background Check", "背景调查应对", "background checks", "背调", "background check"),
            ("Contract Review", "劳动合同中文解读", "employment contracts", "合同", "contract"),
            ("Declining an Offer", "体面拒绝Offer", "declining offers", "拒绝", "decline"),
            ("Day One Introduction", "入职第一天自我介绍", "onboarding", "入职", "onboarding"),
            ("Meeting Colleagues", "茶水间破冰话术", "workplace socializing", "同事", "colleague"),
            ("Company Hierarchy", "读懂公司层级", "org structure", "层级", "hierarchy"),
            ("Probation Period", "试用期生存指南", "probation", "试用期", "probation"),
            ("One-on-One Meeting", "与上司对齐目标", "1-on-1 meetings", "一对一", "one-on-one"),
            ("Year-End Review", "年终述职报告", "annual reviews", "述职", "year-end review"),
            ("Asking for Promotion", "主动申请晋升", "promotions", "晋升", "promotion"),
            ("Resignation", "体面提离职", "quitting jobs", "离职", "resignation"),
            ("Workplace Conflicts", "处理同事矛盾", "conflict resolution", "矛盾", "conflict"),
            ("Top 10 Mistakes", "外国人职场语言误区", "common mistakes", "误区", "mistake"),
        ],
    },
    52: {
        "dir": "Book52_Startup",
        "filename": "ZTurns_Book52_Startup.md",
        "title": "Startup Chinese",
        "subtitle": "创业者的中文生存手册",
        "color": "#F57C00",
        "chapters": [
            ("Brainstorming", "头脑风暴会", "idea generation", "创意", "brainstorm"),
            ("Market Research", "市场调研", "user research", "调研", "research"),
            ("Business Plan", "商业计划书", "business planning", "计划书", "business plan"),
            ("Finding Co-founders", "寻找合伙人", "co-founder relationships", "合伙人", "co-founder"),
            ("Company Registration", "注册公司流程", "business registration", "注册", "registration"),
            ("Pitch Opening", "Pitch开场白", "investor pitching", "融资", "pitch"),
            ("Product Pitch", "产品价值主张", "product presentation", "产品", "product"),
            ("Data Presentation", "数据展示GMV/DAU", "metrics and data", "数据", "data"),
            ("Investor Q&A", "回答投资人问题", "investor relations", "投资人", "investor"),
            ("Term Sheet", "投资条款解读", "investment terms", "条款", "term sheet"),
            ("Hiring Talent", "招聘顶尖人才", "talent acquisition", "招聘", "hiring"),
            ("Stock Options", "期权激励方案", "equity compensation", "期权", "stock options"),
            ("Meeting Culture", "创业公司开会", "startup meetings", "会议", "meeting"),
            ("OKR & KPI", "目标管理实操", "goal setting", "目标", "OKR"),
            ("Firing Employees", "合规解雇员工", "termination", "解雇", "firing"),
            ("Supplier Negotiation", "供应商谈价", "procurement", "供应商", "supplier"),
            ("Customer Complaints", "处理用户投诉", "customer service", "投诉", "complaint"),
            ("Government Relations", "政府关系沟通", "regulatory affairs", "政府", "government"),
            ("Media Interview", "接受媒体采访", "PR and media", "媒体", "media"),
            ("Crisis PR", "危机公关发声", "crisis management", "危机", "crisis"),
            ("Expanding Cities", "进入新城市", "market expansion", "扩张", "expansion"),
            ("Strategic Partnership", "战略合作谈判", "partnerships", "合作", "partnership"),
            ("Going Global", "出海全球化", "internationalization", "出海", "global"),
            ("M&A Negotiation", "并购谈判话术", "mergers and acquisitions", "并购", "M&A"),
            ("Cultural Pitfalls", "外国创始人陷阱", "cultural mistakes", "陷阱", "pitfall"),
        ],
    },
    53: {
        "dir": "Book53_Negotiation",
        "filename": "ZTurns_Book53_Negotiation.md",
        "title": "The Art of Chinese Negotiation",
        "subtitle": "谈判桌上的中文智慧",
        "color": "#7B1FA2",
        "chapters": [
            ("Relationship First", "谈判前的关系铺垫", "relationship building", "关系", "relationship"),
            ("Opening Offer", "开价的艺术", "price negotiation", "开价", "opening offer"),
            ("Power of Silence", "沉默的策略", "silence tactics", "沉默", "silence"),
            ("Face & Substance", "面子与里子", "face-saving", "面子", "face"),
            ("Reading Delays", "识别拖延信号", "delay tactics", "拖延", "delay"),
            ("Data Arguments", "用数据说话", "evidence-based negotiation", "数据", "data"),
            ("Storytelling Strategy", "讲故事代替要求", "storytelling", "故事", "story"),
            ("Emotional Cards", "情感牌的时机", "emotional appeals", "情感", "emotion"),
            ("Anchoring Effect", "锚定效应", "anchoring", "锚定", "anchor"),
            ("Concession Rhythm", "让步节奏控制", "concessions", "让步", "concession"),
            ("Holding the Line", "守住底线话术", "firm positioning", "底线", "bottom line"),
            ("No Budget Response", "应对没有预算", "budget objections", "预算", "budget"),
            ("Ultimatums", "最后通牒判断", "ultimatums", "通牒", "ultimatum"),
            ("Multiple Decision Makers", "多方谈判", "multi-party negotiation", "多方", "multi-party"),
            ("Repair After Breakdown", "谈判破裂修复", "relationship repair", "修复", "repair"),
            ("Relationship Insiders", "成为被优待者", "building trust", "信任", "trust"),
            ("Using Middlemen", "中间人的作用", "intermediaries", "中间人", "middleman"),
            ("Banquet Negotiation", "酒桌非正式决策", "banquet culture", "酒桌", "banquet"),
            ("Unwritten Rules", "潜规则理解", "implicit rules", "潜规则", "unwritten rules"),
            ("Post-Contract Relations", "合同后维护关系", "contract management", "合同", "contract"),
            ("Beyond Price", "用条款换价格", "value negotiation", "条款", "terms"),
            ("Contract Duration", "长短期合同谈判", "contract terms", "期限", "duration"),
            ("Cross-Cultural Styles", "中美中欧对比", "cultural negotiation styles", "风格", "style"),
            ("Online Negotiation", "视频会议谈判", "remote negotiation", "视频", "video"),
            ("20 Universal Phrases", "谈判万用句", "negotiation phrases", "话术", "phrases"),
        ],
    },
    54: {
        "dir": "Book54_Resume",
        "filename": "ZTurns_Book54_Resume.md",
        "title": "Chinese Resume & LinkedIn",
        "subtitle": "中文简历与职业品牌打造",
        "color": "#1976D2",
        "chapters": [
            ("Resume Format", "中文简历格式", "resume writing", "简历", "resume"),
            ("Personal Info", "个人信息填写", "personal details", "个人信息", "personal info"),
            ("Work Experience", "工作经历描述", "work history", "工作经历", "work experience"),
            ("Education Section", "教育背景表达", "education credentials", "教育", "education"),
            ("Skills & Certifications", "技能与证书", "professional skills", "技能", "skills"),
            ("Top 10 Mistakes", "常犯的10大错误", "common errors", "错误", "mistake"),
            ("Industry Keywords", "行业必备词汇", "industry terminology", "关键词", "keywords"),
            ("Quantifying Achievements", "成就数字化", "achievement metrics", "成就", "achievement"),
            ("Self-Summary Writing", "自我评价写法", "personal branding", "自我评价", "self-summary"),
            ("Length Decisions", "一页还是两页", "resume length", "篇幅", "length"),
            ("Cover Letter Structure", "求职信结构", "cover letters", "求职信", "cover letter"),
            ("Tailoring Applications", "针对性定制", "targeted applications", "定制", "tailoring"),
            ("Expressing Enthusiasm", "热情不谄媚", "professional tone", "热情", "enthusiasm"),
            ("Email Subject Lines", "让HR点开的邮件", "email writing", "邮件", "email"),
            ("Follow-Up Emails", "跟进邮件技巧", "follow-up communication", "跟进", "follow-up"),
            ("Maimai Profile", "脉脉主页优化", "professional networking", "脉脉", "networking"),
            ("WeChat Moments", "朋友圈职业形象", "social media presence", "朋友圈", "WeChat"),
            ("Sharing Reports", "分享行业报告", "thought leadership", "报告", "report"),
            ("Professional Groups", "加入专业社群", "professional communities", "社群", "community"),
            ("Personal Brand", "个人品牌建立", "personal branding", "品牌", "brand"),
            ("Reference Letters", "中文推荐信", "recommendations", "推荐信", "reference"),
            ("LinkedIn Endorsements", "领英推荐语", "LinkedIn recommendations", "领英", "LinkedIn"),
            ("Thank-You Notes", "面试感谢信", "thank you letters", "感谢信", "thank you"),
            ("Rejection Replies", "拒信体面回复", "handling rejection", "拒绝", "rejection"),
            ("Career Portfolio", "职业档案管理", "career documentation", "档案", "portfolio"),
        ],
    },
    55: {
        "dir": "Book55_WorkplacePolitics",
        "filename": "ZTurns_Book55_WorkplacePolitics.md",
        "title": "Chinese Workplace Politics",
        "subtitle": "办公室政治生存指南",
        "color": "#388E3C",
        "chapters": [
            ("Power Map", "识别真正决策者", "organizational power", "权力", "power"),
            ("Factions", "辨别公司派系", "office factions", "派系", "faction"),
            ("Reporting Lines", "汇报关系学问", "reporting structures", "汇报", "reporting"),
            ("Credit Claiming", "功劳归属政治", "credit attribution", "功劳", "credit"),
            ("Meeting Politics", "会议发言时机", "meeting dynamics", "会议", "meeting"),
            ("Managing Up", "向上管理技巧", "managing your boss", "向上管理", "managing up"),
            ("Peer Relations", "平级同事相处", "peer relationships", "同事", "peer"),
            ("Cross-Department Work", "跨部门合作", "cross-functional teams", "跨部门", "cross-dept"),
            ("Dealing with Enemies", "处理小人同事", "difficult colleagues", "小人", "difficult person"),
            ("Building Alliances", "建立职场盟友", "workplace allies", "盟友", "ally"),
            ("Performance Review Language", "绩效考核话术", "performance reviews", "绩效", "performance"),
            ("Asking for Promotion", "升职申请策略", "promotion requests", "晋升", "promotion"),
            ("Getting Backstabbed", "被背刺应对", "dealing with betrayal", "背刺", "backstab"),
            ("Information Wars", "职场信息战", "information control", "信息", "information"),
            ("Handling Rumors", "流言蜚语应对", "workplace rumors", "流言", "rumor"),
            ("Foreigner Advantages", "外国人职场优势", "foreigner benefits", "优势", "advantage"),
            ("Using Cultural Differences", "利用文化差异", "cultural leverage", "文化", "culture"),
            ("Drinking Culture", "喝酒应酬文化", "business drinking", "喝酒", "drinking"),
            ("Gift Culture", "送礼文化边界", "gift-giving", "送礼", "gift"),
            ("Forms of Address", "称呼礼仪学问", "professional titles", "称呼", "address"),
            ("Exit Politics", "离职政治艺术", "leaving gracefully", "离职", "exit"),
            ("Stay or Go", "留退两难决策", "career decisions", "去留", "stay or go"),
            ("Workplace Bullying", "职场霸凌应对", "workplace harassment", "霸凌", "bullying"),
            ("Emotional Management", "职场情绪管理", "emotional intelligence", "情绪", "emotion"),
            ("Work-Life Balance", "工作生活平衡", "work-life integration", "平衡", "balance"),
        ],
    },
    56: {
        "dir": "Book56_Gaming",
        "filename": "ZTurns_Book56_Gaming.md",
        "title": "Gaming Chinese",
        "subtitle": "游戏玩家的中文世界",
        "color": "#00897B",
        "chapters": [
            ("China Gaming Market", "中国游戏市场", "gaming industry", "游戏", "gaming"),
            ("Mobile Game Culture", "手游文化生态", "mobile gaming", "手游", "mobile game"),
            ("Gaming Vocabulary", "电竞核心词汇", "gaming terms", "电竞", "esports"),
            ("Game Streaming Intro", "游戏直播文化", "game streaming", "直播", "streaming"),
            ("Gaming Social Life", "游戏社交语言", "gaming community", "社交", "social"),
            ("Honor of Kings", "王者荣耀词汇", "MOBA games", "王者", "Honor of Kings"),
            ("PUBG Mobile", "和平精英语言", "battle royale", "吃鸡", "PUBG"),
            ("Genshin Impact", "原神二次元词汇", "RPG games", "原神", "Genshin"),
            ("League of Legends", "英雄联盟中文", "PC gaming", "英雄联盟", "LoL"),
            ("Reading Game Guides", "看攻略学中文", "game guides", "攻略", "guide"),
            ("Streaming Platforms", "虎牙斗鱼词汇", "streaming platforms", "平台", "platform"),
            ("Danmaku Culture", "弹幕文化用语", "live comments", "弹幕", "danmaku"),
            ("Tipping Streamers", "打赏礼物文化", "virtual gifts", "打赏", "tipping"),
            ("Esports Careers", "电竞职业赛事", "professional gaming", "职业", "professional"),
            ("Guilds & Teams", "公会组队话术", "team play", "公会", "guild"),
            ("Playing Together", "开黑组队沟通", "team communication", "开黑", "team up"),
            ("In-Game Expressions", "游戏内常用语", "gaming slang", "游戏语", "game slang"),
            ("Apology & Reconciliation", "游戏道歉和好", "conflict in games", "道歉", "apology"),
            ("Making Friends Online", "游戏结交朋友", "online friendships", "交友", "friendship"),
            ("In-App Purchases", "手游充值系统", "gaming economy", "充值", "purchase"),
            ("Gaming Peer Pressure", "游戏攀比文化", "social pressure", "攀比", "comparison"),
            ("Gaming Addiction Debate", "网瘾文化讨论", "gaming addiction", "网瘾", "addiction"),
            ("Parents vs Games", "家长游戏对话", "parental concerns", "家长", "parent"),
            ("Chinese Games Global", "游戏出海现象", "global gaming", "出海", "global"),
            ("Gamer Identity", "玩家身份社群", "gamer community", "玩家", "gamer"),
        ],
    },
    57: {
        "dir": "Book57_Music",
        "filename": "ZTurns_Book57_Music.md",
        "title": "Music & KTV Chinese",
        "subtitle": "音乐与KTV的中文世界",
        "color": "#C62828",
        "chapters": [
            ("Chinese Pop Overview", "华语乐坛概览", "Chinese pop music", "华语", "C-pop"),
            ("Music Streaming Apps", "音乐流媒体App", "music platforms", "音乐", "music"),
            ("Learning via Lyrics", "用歌词学中文", "song lyrics", "歌词", "lyrics"),
            ("KTV Culture Intro", "KTV文化入门", "karaoke culture", "KTV", "KTV"),
            ("Ordering Songs", "KTV点歌系统", "song selection", "点歌", "song order"),
            ("Mic Etiquette", "抢麦演唱礼仪", "KTV manners", "麦克风", "microphone"),
            ("Judging Singing", "唱功评价词汇", "vocal performance", "唱功", "singing"),
            ("KTV Spending", "KTV消费套餐", "KTV prices", "消费", "spending"),
            ("Cantonese vs Mandarin", "粤语普通话对比", "Chinese dialects in music", "粤语", "Cantonese"),
            ("Folk Music Scene", "民谣文化", "folk music", "民谣", "folk"),
            ("Chinese Rap", "说唱中文词汇", "hip-hop culture", "说唱", "rap"),
            ("Electronic Music", "电子音乐场景", "EDM culture", "电子", "electronic"),
            ("Talent Show Language", "选秀节目语言", "talent competitions", "选秀", "talent show"),
            ("Idol Culture", "偶像文化词汇", "idol industry", "偶像", "idol"),
            ("Fan Language", "粉丝用语表达", "fan culture", "粉丝", "fan"),
            ("Fan Support Activities", "应援文化打榜", "fan activities", "应援", "fan support"),
            ("Voting & Charts", "控评数据操作", "music charts", "排行榜", "chart"),
            ("Music Festivals", "音乐节文化", "outdoor concerts", "音乐节", "festival"),
            ("Livehouse Scene", "Livehouse现场", "live music venues", "现场", "live music"),
            ("Street Musicians", "街头音乐歌手", "busking culture", "街头", "street music"),
            ("Learning Instruments", "乐器学习词汇", "music instruments", "乐器", "instrument"),
            ("Chinese Musicals", "中文音乐剧", "musical theatre", "音乐剧", "musical"),
            ("Classic Songs", "经典老歌中文", "classic Chinese songs", "经典", "classic"),
            ("Trending Music", "流行单曲话题", "current hits", "流行", "trending"),
            ("Music as Bridge", "音乐融入中国", "cultural integration", "融入", "integration"),
        ],
    },
    58: {
        "dir": "Book58_Comedy",
        "filename": "ZTurns_Book58_Comedy.md",
        "title": "Chinese Comedy & Xiangsheng",
        "subtitle": "相声与中国笑文化",
        "color": "#F9A825",
        "chapters": [
            ("Xiangsheng Origins", "相声的历史起源", "traditional comedy", "相声", "xiangsheng"),
            ("Roles in Xiangsheng", "捧哏与逗哏", "comedy roles", "角色", "roles"),
            ("Guo Degang & Deyun", "郭德纲德云社", "modern xiangsheng", "德云社", "Deyun"),
            ("Following Xiangsheng", "相声听懂技巧", "understanding comedy", "听懂", "comprehension"),
            ("Chinese Puns", "谐音梗双关语", "wordplay", "谐音", "pun"),
            ("Chengyu in Jokes", "成语典故笑点", "idiom humor", "成语", "chengyu"),
            ("Tongue Twisters", "绕口令趣味", "pronunciation practice", "绕口令", "tongue twister"),
            ("Stand-up Comedy", "脱口秀文化", "stand-up comedy", "脱口秀", "stand-up"),
            ("Spring Festival Sketches", "春晚小品文化", "TV comedy sketches", "小品", "sketch"),
            ("Zhao Benshan", "赵本山东北喜剧", "regional comedy", "东北", "northeast"),
            ("Shen Teng & Ma Li", "沈腾马丽喜剧", "modern comedy stars", "喜剧", "comedy star"),
            ("Viral Comedy Videos", "搞笑视频鬼畜", "internet comedy", "鬼畜", "viral video"),
            ("Internet Memes", "网络梗大全", "meme culture", "梗", "meme"),
            ("Meme Language", "表情包流行语", "emoji culture", "表情包", "emoji"),
            ("Involution Humor", "内卷梗文化", "social satire", "内卷", "involution"),
            ("Lying Flat Jokes", "摆烂emo文化", "anti-work humor", "摆烂", "lying flat"),
            ("Regional Stereotypes", "地域笑话", "regional humor", "地域", "regional"),
            ("Dialect Humor", "方言里的笑点", "dialect comedy", "方言", "dialect"),
            ("Dark Humor", "黑色幽默边界", "dark comedy", "黑色", "dark"),
            ("Satire & Metaphor", "讽刺文化隐喻", "political satire", "讽刺", "satire"),
            ("Humor Limits", "幽默的尺度", "comedy boundaries", "尺度", "boundaries"),
            ("Making Chinese Laugh", "让中国人发笑", "cross-cultural humor", "发笑", "laughter"),
            ("Self-Deprecating Humor", "自嘲文化", "self-deprecation", "自嘲", "self-deprecation"),
            ("Roast Culture", "脱口秀吐槽", "roast comedy", "吐槽", "roast"),
            ("Foreigner Comedy", "外国人搞笑中文", "foreigner humor", "外国人", "foreigner"),
        ],
    },
    59: {
        "dir": "Book59_WebNovels",
        "filename": "ZTurns_Book59_WebNovels.md",
        "title": "Chinese Web Novels",
        "subtitle": "网络小说与玄幻世界",
        "color": "#5E35B1",
        "chapters": [
            ("Web Novel Culture", "网文文化起点", "online fiction", "网文", "web novel"),
            ("The Shuang Formula", "爽文公式主角光环", "power fantasy", "爽文", "power fantasy"),
            ("Reader Economy", "读者打赏订阅", "monetization", "打赏", "tipping"),
            ("Xianxia Vocabulary", "仙侠修仙词汇", "cultivation novels", "修仙", "cultivation"),
            ("Fantasy World Settings", "玄幻世界设定", "fantasy worldbuilding", "玄幻", "fantasy"),
            ("Leveling Up", "升级打怪系统", "RPG mechanics in fiction", "升级", "level up"),
            ("System Novels", "系统文词汇", "game-like fiction", "系统", "system"),
            ("Time Travel Stories", "穿越文类型", "time travel fiction", "穿越", "time travel"),
            ("Romance Web Novels", "言情网文类型", "romance fiction", "言情", "romance"),
            ("CEO Romance Trope", "霸道总裁文", "CEO romance", "总裁", "CEO romance"),
            ("Sweet Romance", "甜宠文表达", "sweet romance", "甜宠", "sweet romance"),
            ("Angst Novels", "虐文HE/BE结局", "tragedy romance", "虐文", "angst"),
            ("Historical Fiction", "历史文古言", "historical novels", "历史", "historical"),
            ("Palace Intrigue", "宫斗权谋词汇", "court intrigue", "宫斗", "palace drama"),
            ("Alternate History", "架空历史设定", "alternate history", "架空", "alternate"),
            ("Novel to Screen", "网文影视改编", "adaptation culture", "改编", "adaptation"),
            ("Drama Adaptations", "改编剧原著党", "book vs drama debate", "原著", "original"),
            ("Tomato Novel App", "番茄小说平台", "reading platforms", "番茄", "platform"),
            ("Global Web Novels", "网文出海翻译", "global readership", "出海", "global"),
            ("AI Writing Novels", "AI写网文讨论", "AI in fiction", "AI写作", "AI writing"),
            ("Reading Reviews", "看书评学中文", "book reviews", "书评", "review"),
            ("Writing Your Own", "尝试写网文", "creative writing", "写作", "writing"),
            ("Fan Fiction Culture", "同人文二创", "fan fiction", "同人", "fan fiction"),
            ("Web Novel Slang", "网文专属黑话", "fiction slang", "黑话", "slang"),
            ("Web Novels for Learning", "用网文学中文", "study methods", "学习", "learning"),
        ],
    },
    60: {
        "dir": "Book60_VarietyShows",
        "filename": "ZTurns_Book60_VarietyShows.md",
        "title": "Chinese Reality TV & Variety Shows",
        "subtitle": "综艺节目中文",
        "color": "#00838F",
        "chapters": [
            ("Variety Show Types", "综艺节目类型", "reality TV genres", "综艺", "variety show"),
            ("Streaming Platforms", "爱优腾芒平台", "video platforms", "平台", "platform"),
            ("Watching with Danmaku", "弹幕看综艺", "interactive viewing", "弹幕", "danmaku"),
            ("Guest & Judge Language", "嘉宾导师词汇", "show participants", "嘉宾", "guest"),
            ("Talent Show Language", "选秀节目词汇", "talent competitions", "选秀", "talent show"),
            ("Sisters Who Make Waves", "乘风破浪语言", "women's reality show", "乘风破浪", "Sisters"),
            ("Idol Training Shows", "创造营词汇", "idol competition", "创造营", "idol camp"),
            ("Fan Voting Language", "粉丝打榜投票", "fan voting", "打榜", "voting"),
            ("Debuting Language", "出道成团词汇", "idol debut", "出道", "debut"),
            ("Outdoor Reality Shows", "户外真人秀", "outdoor challenges", "户外", "outdoor"),
            ("Slow Life Shows", "向往的生活", "lifestyle shows", "慢综艺", "slow variety"),
            ("Parenting Shows", "亲子综艺词汇", "family shows", "亲子", "parenting"),
            ("Travel Variety", "旅行综艺表达", "travel shows", "旅行", "travel"),
            ("Stand-up Shows", "脱口秀节目", "comedy shows", "脱口秀", "stand-up"),
            ("Talk Show Language", "脱口秀大会词汇", "comedy competition", "大会", "competition"),
            ("Li Dan & Comedy", "李诞笑场文化", "comedy hosts", "主持人", "host"),
            ("Variety Sense", "综艺感综艺人格", "entertainment personality", "综艺感", "variety sense"),
            ("Famous Show Memes", "综艺名梗大全", "iconic moments", "名梗", "famous meme"),
            ("CP Culture", "综艺CP文化", "shipping culture", "CP", "CP culture"),
            ("Show Disasters", "综艺翻车事件", "show controversies", "翻车", "controversy"),
            ("Production Tricks", "节目组套路", "production tactics", "节目组", "production"),
            ("Reality vs Scripted", "真人秀真实性", "authenticity debate", "真实性", "authenticity"),
            ("Behind the Scenes", "幕后制作词汇", "production vocabulary", "幕后", "behind scenes"),
            ("Global Variety Shows", "综艺出海改编", "international formats", "出海", "global"),
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
        "title": "Money & Investment Chinese",
        "subtitle": "中文理财：从存钱到投资",
        "color": "#1B5E20",
        "chapters": [
            ("Opening a Bank Account", "外国人开户", "banking basics", "开户", "account opening"),
            ("Mobile Banking Apps", "手机银行操作", "digital banking", "网银", "mobile banking"),
            ("Transfers & Payments", "转账收款操作", "money transfers", "转账", "transfer"),
            ("Sending Money Abroad", "汇款回国外汇", "international transfers", "汇款", "remittance"),
            ("Credit Cards", "信用卡额度账单", "credit cards", "信用卡", "credit card"),
            ("Stock Market Basics", "A股上证入门", "Chinese stocks", "股票", "stocks"),
            ("Fund Investment", "基金指数主动", "mutual funds", "基金", "fund"),
            ("Alipay Finance", "余额宝理财", "Alipay investment", "余额宝", "Yu'E Bao"),
            ("Real Estate Investment", "外国人买房", "property investment", "房产", "property"),
            ("Insurance Basics", "社保商业险", "insurance types", "保险", "insurance"),
            ("Reading Financial News", "财经新闻CPI", "economic news", "财经", "financial news"),
            ("RMB Exchange Rate", "人民币汇率", "currency exchange", "汇率", "exchange rate"),
            ("Mortgage Concepts", "房贷首付月供", "home loans", "房贷", "mortgage"),
            ("Tax Knowledge", "个人所得税", "personal taxes", "税务", "taxes"),
            ("Saving vs Spending", "储蓄消费观念", "financial mindset", "储蓄", "savings"),
            ("Digital RMB", "数字人民币e-CNY", "CBDC", "数字人民币", "digital yuan"),
            ("Ant Group Ecosystem", "花呗借呗芝麻", "fintech products", "花呗", "Huabei"),
            ("Stock Communities", "雪球东方财富", "investor communities", "股民", "retail investor"),
            ("Crypto in China", "比特币监管讨论", "crypto regulation", "比特币", "Bitcoin"),
            ("Fintech Vocabulary", "金融科技区块链", "fintech terms", "金融科技", "fintech"),
            ("Family Budget", "家庭月度预算", "budgeting", "预算", "budget"),
            ("Emergency Fund", "急用金储备", "emergency savings", "紧急储备", "emergency fund"),
            ("Retirement Planning", "养老金个人账户", "retirement", "养老", "retirement"),
            ("Children's Education Fund", "教育金规划", "education savings", "教育金", "education fund"),
            ("5 Tips for Foreigners", "外国人理财注意", "financial advice", "注意事项", "tips"),
        ],
    },
    63: {
        "dir": "Book63_Fitness",
        "filename": "ZTurns_Book63_Fitness.md",
        "title": "Fitness & Wellness Chinese",
        "subtitle": "健身房到瑜伽馆：运动与健康中文",
        "color": "#4527A0",
        "chapters": [
            ("Joining a Gym", "健身房办卡谈价", "gym membership", "健身房", "gym"),
            ("Equipment Area", "器械区礼仪", "gym equipment", "器械", "equipment"),
            ("Personal Training", "请私教第一课", "personal training", "私教", "personal trainer"),
            ("Strength Training", "深蹲硬拉卧推", "weight training", "力量", "strength"),
            ("Cardio Machines", "跑步机椭圆机", "cardio exercise", "有氧", "cardio"),
            ("Yoga Class", "瑜伽体式指令", "yoga", "瑜伽", "yoga"),
            ("Pilates", "普拉提动作术语", "pilates", "普拉提", "pilates"),
            ("Spin Class", "动感单车骑行", "cycling class", "单车", "spin bike"),
            ("Combat Fitness", "搏击操出拳踢腿", "combat fitness", "搏击", "combat"),
            ("Dance Fitness", "广场舞爵士舞", "dance exercise", "广场舞", "square dance"),
            ("Sports Nutrition", "蛋白质碳水脂肪", "sports nutrition", "营养", "nutrition"),
            ("Protein Supplements", "蛋白粉乳清选购", "protein powder", "蛋白粉", "protein powder"),
            ("Sports Drinks", "电解质能量棒", "sports drinks", "运动饮料", "sports drink"),
            ("Diet Planning", "减脂增肌计划", "fitness diet", "饮食计划", "diet plan"),
            ("Healthy Food Delivery", "外卖健康选择", "healthy eating", "健康外卖", "healthy takeout"),
            ("Running Community", "跑步社群团练", "running groups", "跑步", "running"),
            ("Cycling", "城市骑行长途", "cycling culture", "骑行", "cycling"),
            ("Hiking", "登山安全路线", "hiking vocabulary", "爬山", "hiking"),
            ("Swimming", "泳池规则泳姿", "swimming", "游泳", "swimming"),
            ("Ball Sports", "约人打球预订", "team sports", "球类", "ball sports"),
            ("Massage & Recovery", "按摩推拿需求", "massage therapy", "按摩", "massage"),
            ("Meditation", "冥想正念引导", "mindfulness", "冥想", "meditation"),
            ("TCM Recovery", "中医调理运动", "traditional medicine", "中医", "TCM"),
            ("Sleep Optimization", "睡眠优化讨论", "sleep health", "睡眠", "sleep"),
            ("Fitness Blogger Language", "B站健身视频", "fitness content", "博主", "blogger"),
        ],
    },
    64: {
        "dir": "Book64_TravelPhoto",
        "filename": "ZTurns_Book64_TravelPhoto.md",
        "title": "Travel Photography Chinese",
        "subtitle": "旅拍中文：镜头里的中国",
        "color": "#006064",
        "chapters": [
            ("Camera Brands", "相机品牌购买", "camera shopping", "相机", "camera"),
            ("Lens Language", "镜头焦距光圈", "photography terms", "镜头", "lens"),
            ("Accessories", "三脚架滤镜存储", "camera accessories", "配件", "accessories"),
            ("Second-Hand Market", "闲鱼买相机", "used equipment", "二手", "second-hand"),
            ("Drones", "大疆无人机飞行", "drone photography", "无人机", "drone"),
            ("Shooting at Scenic Spots", "景区找机位", "location scouting", "景区", "scenic spot"),
            ("Portrait Requests", "邀请陌生人拍照", "portrait photography", "人像", "portrait"),
            ("Street Photography", "街头抓拍文化", "street photography", "街拍", "street photo"),
            ("Folk Event Photography", "民俗活动拍摄", "cultural photography", "民俗", "folk event"),
            ("Light & Weather", "最佳拍摄时机", "natural light", "光线", "lighting"),
            ("Editing Software", "Lightroom修图", "photo editing", "修图", "photo editing"),
            ("Color Adjustment", "色温饱和对比度", "color grading", "调色", "color grading"),
            ("Filter Culture", "中国修图风格", "filter trends", "滤镜", "filter"),
            ("Printing Services", "照片书海报打印", "photo printing", "印刷", "printing"),
            ("Pro Photographer Talk", "和摄影师交流", "photography community", "摄影师", "photographer"),
            ("Xiaohongshu Posts", "小红书旅拍博主", "social media content", "小红书", "RED"),
            ("Weibo Photo Circle", "微博摄影话题", "online photography", "微博", "Weibo"),
            ("Photo Competitions", "摄影比赛投稿", "photography contests", "比赛", "competition"),
            ("Copyright Awareness", "摄影版权知识", "intellectual property", "版权", "copyright"),
            ("Commercial Shoots", "品牌合作报价", "commercial photography", "商业拍摄", "commercial"),
            ("Classic Photo Spots", "中国经典摄影地", "photography destinations", "摄影地", "photo location"),
            ("Photography Festivals", "平遥大理摄影节", "photo festivals", "摄影节", "photo festival"),
            ("Photography Communities", "本地摄影俱乐部", "photography clubs", "摄影圈", "photo circle"),
            ("Film Photography Revival", "胶片复兴冲洗", "film photography", "胶片", "film"),
            ("Photography as Language", "镜头理解中国", "visual culture", "视角", "perspective"),
        ],
    },
    65: {
        "dir": "Book65_HomeReno",
        "filename": "ZTurns_Book65_HomeReno.md",
        "title": "Home Decoration Chinese",
        "subtitle": "装修那些事：新家的中文旅程",
        "color": "#4E342E",
        "chapters": [
            ("Viewing Properties", "看房中介语言", "apartment hunting", "看房", "house viewing"),
            ("Shell vs Finished", "毛坯精装区别", "property types", "毛坯", "shell unit"),
            ("Measuring & Planning", "量房设计确认", "space planning", "量房", "measuring"),
            ("Renovation Budget", "装修预算控制", "budget planning", "预算", "budget"),
            ("Signing Contracts", "装修合同条款", "renovation contracts", "合同", "contract"),
            ("Communicating Style", "和设计师谈风格", "interior design", "风格", "style"),
            ("Building Material Markets", "红星美凯龙导购", "material shopping", "建材", "building materials"),
            ("Tiles & Flooring", "瓷砖地板选材", "flooring choices", "瓷砖", "tiles"),
            ("Kitchen & Bathroom", "橱柜马桶淋浴", "fixtures", "厨卫", "kitchen/bathroom"),
            ("Soft Furnishings", "软装家具搭配", "interior decoration", "软装", "soft furnishing"),
            ("Plumbing & Electrical", "水电改造沟通", "construction work", "水电", "utilities"),
            ("Tiling Work", "瓦工验收标准", "quality inspection", "瓦工", "tiling"),
            ("Carpentry Work", "木工定制家具", "custom furniture", "木工", "carpentry"),
            ("Paint & Coating", "油漆颜色选择", "painting", "涂料", "paint"),
            ("Inspection Skills", "识别偷工减料", "quality control", "验收", "acceptance"),
            ("IKEA in China", "宜家购物技巧", "furniture shopping", "宜家", "IKEA"),
            ("Online Furniture", "天猫京东网购", "online shopping", "网购", "online shopping"),
            ("Custom Furniture", "定制家具尺寸", "custom orders", "定制", "custom"),
            ("Home Appliances", "空调洗衣机冰箱", "appliance selection", "家电", "appliances"),
            ("Moving Companies", "搬家公司选择", "moving services", "搬家", "moving"),
            ("Final Inspection", "验收整改追责", "defect inspection", "整改", "rectification"),
            ("Maintenance & Repairs", "叫物业找师傅", "home maintenance", "维修", "repair"),
            ("Neighbor Relations", "装修扰邻协商", "neighbor disputes", "邻居", "neighbor"),
            ("Rental Renovation", "租约内改善居住", "rental improvements", "租房", "rental"),
            ("Renovation Pitfalls", "外国人装修踩坑", "renovation mistakes", "踩坑", "pitfalls"),
        ],
    },
    66: {
        "dir": "Book66_EV",
        "filename": "ZTurns_Book66_EV.md",
        "title": "Electric Vehicles & New Mobility Chinese",
        "subtitle": "电动车革命：中国新出行语言",
        "color": "#00695C",
        "chapters": [
            ("EV Market Overview", "中国EV格局", "Chinese EV market", "电动车", "EV"),
            ("Buying an EV", "新能源车购买", "EV purchase", "新能源", "new energy"),
            ("Subsidies & Policy", "购车补贴申请", "government incentives", "补贴", "subsidy"),
            ("Charging Infrastructure", "找桩充电操作", "EV charging", "充电桩", "charging station"),
            ("License Plates", "绿牌蓝牌办理", "EV registration", "牌照", "license plate"),
            ("Battery Technology", "磷酸铁锂三元", "battery types", "电池", "battery"),
            ("Range Anxiety", "续航焦虑讨论", "driving range", "续航", "range"),
            ("Autonomous Driving", "辅助自动驾驶", "self-driving tech", "自动驾驶", "autonomous"),
            ("OTA Updates", "车机系统更新", "software updates", "升级", "OTA update"),
            ("Service & Repair", "和4S店沟通", "EV maintenance", "维修", "maintenance"),
            ("Public Charging", "公共充电全流程", "public charging", "公共充电", "public charge"),
            ("Home Charging Installation", "家庭充电桩安装", "home charging", "家用充电", "home charger"),
            ("Charging Etiquette", "充电桩占用礼仪", "charging manners", "礼仪", "etiquette"),
            ("Road Trip Planning", "长途出行规划", "trip planning", "长途", "road trip"),
            ("Emergency Breakdown", "紧急救援处理", "roadside assistance", "救援", "rescue"),
            ("BYD Deep Dive", "比亚迪品牌语言", "BYD brand", "比亚迪", "BYD"),
            ("NIO Experience", "蔚来换电服务", "NIO brand", "蔚来", "NIO"),
            ("Xpeng Features", "小鹏智能驾驶", "Xpeng brand", "小鹏", "Xpeng"),
            ("EV Community", "车主社群论坛", "EV community", "车主", "car owner"),
            ("Ridesharing EVs", "网约车顺风车", "ride-hailing", "网约车", "ride-hailing"),
            ("E-Bikes & Scooters", "电动自行车摩托", "e-bikes", "电瓶车", "e-bike"),
            ("EV Investment Talk", "新能源股票投资", "EV investment", "投资", "investment"),
            ("Global EV Competition", "中国EV出海", "global competition", "出海", "export"),
            ("Future Mobility", "未来出行趋势", "mobility trends", "未来", "future"),
            ("EV Vocabulary Master", "电动车词汇总结", "EV vocabulary", "词汇", "vocabulary"),
        ],
    },
    67: {
        "dir": "Book67_CleanEnergy",
        "filename": "ZTurns_Book67_CleanEnergy.md",
        "title": "Clean Energy & Carbon Neutrality Chinese",
        "subtitle": "新能源与碳中和中文",
        "color": "#558B2F",
        "chapters": [
            ("Dual Carbon Goals", "双碳目标政策", "carbon neutrality", "碳中和", "carbon neutral"),
            ("Solar Energy", "光伏太阳能发电", "solar power", "光伏", "solar"),
            ("Wind Energy", "风力发电词汇", "wind power", "风能", "wind power"),
            ("Hydropower", "水力发电大坝", "hydropower", "水电", "hydropower"),
            ("Energy Policy", "新能源政策解读", "energy policy", "政策", "policy"),
            ("Carbon Trading", "碳交易市场机制", "carbon market", "碳交易", "carbon trading"),
            ("Green Certificates", "绿证绿电交易", "green energy", "绿证", "green cert"),
            ("Energy Efficiency", "能耗词汇节能", "energy efficiency", "节能", "energy saving"),
            ("Green Certification", "节能认证标准", "green standards", "认证", "certification"),
            ("Energy Storage", "储能技术电池", "energy storage", "储能", "storage"),
            ("Hydrogen Energy", "氢能燃料电池", "hydrogen power", "氢能", "hydrogen"),
            ("Nuclear Energy", "核能安全词汇", "nuclear power", "核能", "nuclear"),
            ("Smart Grid", "智能电网系统", "smart grid", "电网", "power grid"),
            ("Green Buildings", "绿色建筑认证", "sustainable buildings", "绿色建筑", "green building"),
            ("Energy-Saving Appliances", "节能家电选购", "eco appliances", "节能家电", "eco appliance"),
            ("Green Transport", "绿色出行方式", "sustainable transport", "绿色出行", "green transport"),
            ("Waste Sorting", "垃圾分类规定", "recycling", "垃圾分类", "waste sorting"),
            ("Carbon Footprint", "碳足迹减碳生活", "carbon footprint", "碳足迹", "carbon footprint"),
            ("Green Investment", "绿色投资ESG", "ESG investing", "ESG", "ESG"),
            ("Carbon Disclosure", "企业碳披露报告", "corporate sustainability", "碳披露", "disclosure"),
            ("Green Enterprise", "环保企业案例", "green business", "环保企业", "eco company"),
            ("Climate Negotiations", "气候谈判COP", "climate diplomacy", "气候", "climate"),
            ("Sustainable Development", "可持续发展目标", "SDGs", "可持续", "sustainable"),
            ("Green Lifestyle", "低碳生活实践", "low-carbon living", "低碳", "low carbon"),
            ("Future Energy", "能源转型未来", "energy transition", "转型", "transition"),
        ],
    },
    68: {
        "dir": "Book68_Robotics",
        "filename": "ZTurns_Book68_Robotics.md",
        "title": "Robotics & AI Manufacturing Chinese",
        "subtitle": "机器人与智能制造中文",
        "color": "#37474F",
        "chapters": [
            ("Industrial Robots", "工业机器人基础", "industrial robots", "机器人", "robot"),
            ("Humanoid Robots", "人形机器人发展", "humanoid robots", "人形机器人", "humanoid"),
            ("Factory Automation", "工厂自动化生产", "factory automation", "自动化", "automation"),
            ("Factory Visit Language", "工厂参观词汇", "factory tours", "工厂", "factory"),
            ("Production Line", "生产线运营词汇", "production line", "生产线", "production line"),
            ("Quality Control", "质检良率标准", "quality control", "质检", "QC"),
            ("Lean Manufacturing", "精益生产管理", "lean manufacturing", "精益", "lean"),
            ("AI in Manufacturing", "AI制造智慧工厂", "smart manufacturing", "智慧工厂", "smart factory"),
            ("Digital Twin", "数字孪生技术", "digital twin", "数字孪生", "digital twin"),
            ("Industrial IoT", "工业互联网系统", "industrial IoT", "工业互联网", "IIoT"),
            ("MES Systems", "MES制造执行", "manufacturing systems", "MES", "MES system"),
            ("Supply Chain", "供应链采购词汇", "supply chain", "供应链", "supply chain"),
            ("Procurement Talk", "采购谈价合同", "procurement", "采购", "procurement"),
            ("Inventory Management", "库存管理系统", "inventory", "库存", "inventory"),
            ("Logistics & Customs", "物流海关通关", "logistics", "物流", "logistics"),
            ("Lighthouse Factories", "灯塔工厂案例", "lighthouse factories", "灯塔工厂", "lighthouse"),
            ("Engineer Culture", "工程师职场文化", "engineering culture", "工程师", "engineer"),
            ("Industrial Upgrade", "产业升级词汇", "industrial upgrading", "产业升级", "upgrade"),
            ("Made in China 2025", "中国制造2025", "manufacturing policy", "制造", "manufacturing"),
            ("R&D Language", "研发创新词汇", "R&D", "研发", "R&D"),
            ("Patent & IP", "专利知识产权", "intellectual property", "专利", "patent"),
            ("Tech Transfer", "技术转让合作", "technology transfer", "技术转让", "tech transfer"),
            ("International Manufacturing", "中外制造合作", "global manufacturing", "合作", "cooperation"),
            ("Robotics Competition", "机器人大赛词汇", "robotics competitions", "竞赛", "competition"),
            ("Future of Work", "智能制造未来", "future manufacturing", "未来", "future"),
        ],
    },
    69: {
        "dir": "Book69_Quantum",
        "filename": "ZTurns_Book69_Quantum.md",
        "title": "Quantum & Semiconductor Chinese",
        "subtitle": "量子芯片前沿中文",
        "color": "#1A237E",
        "chapters": [
            ("Chip Basics", "芯片基础词汇CPU", "semiconductor basics", "芯片", "chip"),
            ("GPU & AI Chips", "GPU人工智能芯片", "AI chips", "GPU", "GPU"),
            ("Lithography Machines", "光刻机EUV工艺", "chip manufacturing", "光刻机", "lithography"),
            ("TSMC & SMIC", "台积电中芯国际", "chip foundries", "代工", "foundry"),
            ("Semiconductor Supply Chain", "半导体产业链", "chip industry", "半导体", "semiconductor"),
            ("Packaging & Testing", "封装测试工艺", "chip packaging", "封装", "packaging"),
            ("EDA Software", "EDA设计软件", "chip design", "EDA", "EDA"),
            ("Advanced Process Nodes", "先进制程工艺", "process nodes", "制程", "process node"),
            ("Chip Sanctions", "芯片禁令管制", "trade restrictions", "禁令", "sanctions"),
            ("Quantum Computing Basics", "量子计算入门", "quantum computing", "量子计算", "quantum computing"),
            ("Qubits", "量子比特原理", "quantum bits", "量子比特", "qubit"),
            ("Quantum Entanglement", "量子纠缠现象", "quantum physics", "量子纠缠", "entanglement"),
            ("Quantum Communication", "量子通信网络", "quantum networks", "量子通信", "quantum comm"),
            ("Quantum Cryptography", "量子密码安全", "quantum security", "量子密码", "quantum crypto"),
            ("China Chip Policy", "大基金芯片政策", "chip policy", "大基金", "big fund"),
            ("Domestic Substitution", "国产替代进程", "localization", "国产替代", "domestic sub"),
            ("Chip Investment", "芯片投资生态", "chip investment", "芯片投资", "chip invest"),
            ("Talent War", "芯片人才争夺", "talent competition", "人才", "talent"),
            ("Lab Tour Language", "实验室参观词汇", "lab visits", "实验室", "laboratory"),
            ("Academic Exchange", "学术交流合作", "academic collaboration", "学术", "academic"),
            ("Paper Publishing", "论文发表SCI", "research papers", "论文", "paper"),
            ("Patent Filing", "专利申请保护", "patent protection", "专利", "patent"),
            ("Tech Licensing", "技术许可协议", "tech licensing", "许可", "licensing"),
            ("Quantum Future", "量子计算未来", "quantum future", "未来", "future"),
            ("Chip Vocabulary Master", "芯片词汇总结", "chip vocabulary", "词汇", "vocabulary"),
        ],
    },
    70: {
        "dir": "Book70_Space",
        "filename": "ZTurns_Book70_Space.md",
        "title": "Space & Commercial Aviation Chinese",
        "subtitle": "航天与商业航空中文",
        "color": "#0D1B2A",
        "chapters": [
            ("China Space Achievements", "中国航天成就", "space program", "航天", "space"),
            ("Shenzhou Program", "神舟载人航天", "crewed spaceflight", "神舟", "Shenzhou"),
            ("Chang'e Moon Missions", "嫦娥探月工程", "lunar exploration", "嫦娥", "Chang'e"),
            ("Tiangong Station", "天宫空间站", "space station", "天宫", "Tiangong"),
            ("Rocket Vocabulary", "火箭发射词汇", "rocket science", "火箭", "rocket"),
            ("Satellite Technology", "卫星技术应用", "satellites", "卫星", "satellite"),
            ("Taikonauts", "航天员太空生活", "astronauts", "航天员", "taikonaut"),
            ("Spacewalks", "出舱活动EVA", "spacewalk", "出舱", "EVA"),
            ("Commercial Space", "商业航天公司", "commercial space", "商业航天", "commercial space"),
            ("LandSpace & iSpace", "蓝箭星际荣耀", "private rockets", "民营火箭", "private rocket"),
            ("Commercial Satellites", "长光商业卫星", "satellite services", "商业卫星", "commercial satellite"),
            ("Commercial Launches", "商业发射服务", "launch services", "发射", "launch"),
            ("Aviation Vocabulary", "航空基础词汇", "civil aviation", "航空", "aviation"),
            ("C919 Domestic Aircraft", "国产大飞机C919", "Chinese aviation", "大飞机", "C919"),
            ("Airlines in China", "中国航空公司", "airlines", "航空公司", "airline"),
            ("Flight Vocabulary", "飞行专业词汇", "flight terms", "飞行", "flight"),
            ("Airport Operations", "机场运营词汇", "airports", "机场", "airport"),
            ("Satellite Internet", "卫星互联网StarNet", "satellite internet", "卫星互联网", "satellite internet"),
            ("Remote Sensing", "遥感技术应用", "remote sensing", "遥感", "remote sensing"),
            ("BeiDou Navigation", "北斗导航系统", "navigation systems", "北斗", "BeiDou"),
            ("Deep Space Exploration", "深空探测任务", "deep space", "深空", "deep space"),
            ("Mars Mission Tianwen", "天问火星探测", "Mars exploration", "天问", "Tianwen"),
            ("Crewed Moon Landing", "载人登月计划", "moon landing", "登月", "moon landing"),
            ("Space Economy", "太空经济产业", "space economy", "太空经济", "space economy"),
            ("Space Vocabulary Master", "航天词汇总结", "space vocabulary", "词汇", "vocabulary"),
        ],
    },
}

# ─── Chapter content generator ──────────────────────────────────────

STUDENT_NAMES = ["James", "Lisa", "Sarah", "David", "Emma", "Michael"]

def make_chapter(book_num, ch_num, en_title, zh_title, topic_en, key_word_zh, key_word_en):
    """Generate a complete chapter with 6 sections."""
    s = STUDENT_NAMES[ch_num % len(STUDENT_NAMES)]
    s2 = STUDENT_NAMES[(ch_num + 1) % len(STUDENT_NAMES)]

    vocab_rows = [
        (f"{key_word_zh}技巧", f"{key_word_en} skills", "noun", "核心技能词汇"),
        (f"专业", "professional", "adjective", "用于描述人或行为"),
        (f"沟通", "communicate", "verb", "沟通 = communicate，非常常用"),
        (f"重要", "important", "adjective", "很重要 = very important"),
        (f"经验", "experience", "noun", "工作经验 = work experience"),
        (f"机会", "opportunity", "noun", "抓住机会 = seize the opportunity"),
        (f"成功", "success/succeed", "noun/verb", "成功地 = successfully"),
        (f"问题", "question/problem", "noun", "语境决定是问题还是问题"),
        (f"方法", "method/approach", "noun", "有效的方法 = effective method"),
        (f"结果", "result/outcome", "noun", "期望结果 = expected outcome"),
    ]

    vocab_table = "| Chinese | Pinyin | English | Part of Speech | Usage Note |\n"
    vocab_table += "|---------|--------|---------|----------------|------------|\n"
    pinyin_map = {
        "技巧": "jìqiǎo", "专业": "zhuānyè", "沟通": "gōutōng",
        "重要": "zhòngyào", "经验": "jīngyàn", "机会": "jīhuì",
        "成功": "chénggōng", "问题": "wèntí", "方法": "fāngfǎ", "结果": "jiéguǒ",
    }
    for zh, en, pos, note in vocab_rows:
        base = zh.replace("技巧", "").replace(key_word_zh, "")
        py = pinyin_map.get(zh, pinyin_map.get(zh[-2:], "..."))
        vocab_table += f"| {zh} | {py} | {en} | {pos} | {note} |\n"

    chapter = f"""# Chapter {ch_num}: {en_title} — {zh_title}

## 1. Real Scene

Tony stood at the front of the classroom and smiled at the students. "Today we're going to talk about something very practical," he said. "Have any of you had to deal with {topic_en} in China?"

{s} raised his hand immediately. "Yes! Last week I tried to handle this, but I didn't know what to say in Chinese. I just stood there looking confused."

"That's exactly why we're here," Tony said. The key phrase you need is related to '{key_word_zh}' — which means '{key_word_en}'. Once you understand this concept in the Chinese context, everything becomes much clearer."

{s2} leaned forward with interest. "Is it really that different from what we'd do back home?"

"Very different," Tony nodded. "In China, the approach to {topic_en} reflects deeper cultural values. Let's learn the language and the culture together."

---

## 2. Key Vocabulary

{vocab_table}
---

## 3. Authentic Dialogues

**Dialogue 1: Basic Exchange**

A: 你好，我想了解一下关于{key_word_zh}的情况。
*Nǐ hǎo, wǒ xiǎng liǎojiě yīxià guānyú {key_word_zh} de qíngkuàng.*
*Hello, I'd like to understand the situation regarding {key_word_en}.*

B: 没问题，请坐。我来给你解释一下。
*Méi wèntí, qǐng zuò. Wǒ lái gěi nǐ jiěshì yīxià.*
*No problem, please have a seat. Let me explain.*

A: 谢谢，我在中国的时间不长，还在学习。
*Xièxiè, wǒ zài Zhōngguó de shíjiān bù cháng, hái zài xuéxí.*
*Thank you, I haven't been in China long and I'm still learning.*

B: 没关系，你的中文已经很不错了！
*Méi guānxi, nǐ de Zhōngwén yǐjīng hěn búcuò le!*
*No worries, your Chinese is already very good!*

**Dialogue 2: Follow-up**

A: 关于{key_word_zh}，我应该怎么做比较好？
*Guānyú {key_word_zh}, wǒ yīnggāi zěnme zuò bǐjiào hǎo?*
*Regarding {key_word_en}, what's the best approach?*

B: 一般来说，在中国你需要先建立关系，然后再谈具体的事情。
*Yībān lái shuō, zài Zhōngguó nǐ xūyào xiān jiànlì guānxi, ránhòu zài tán jùtǐ de shìqíng.*
*Generally speaking, in China you need to first build a relationship, then discuss specific matters.*

A: 我明白了。关系很重要，对吗？
*Wǒ míngbái le. Guānxi hěn zhòngyào, duì ma?*
*I understand. Relationships are very important, right?*

B: 对，在中国，关系是一切的基础。
*Duì, zài Zhōngguó, guānxi shì yīqiè de jīchǔ.*
*Yes, in China, relationships are the foundation of everything.*

---

## 4. Grammar in Context

**Pattern 1: 关于…来说 (Regarding... / As for...)**

Use 关于 (guānyú) to introduce a topic, similar to "regarding" or "as for" in English.

**Chinese:** 关于{key_word_zh}，你有什么经验？
**Pinyin:** Guānyú {key_word_zh}, nǐ yǒu shénme jīngyàn?
**Literal:** Regarding {key_word_en}, you have what experience?
**English:** What experience do you have with {key_word_en}?

**Chinese:** 关于这个问题，我们需要认真考虑。
**Pinyin:** Guānyú zhège wèntí, wǒmen xūyào rènzhēn kǎolǜ.
**Literal:** Regarding this problem, we need seriously consider.
**English:** We need to think carefully about this issue.

**Pattern 2: 需要先…然后再… (Need to first... then...)**

This pattern shows sequential steps — very common in Chinese instructions and advice.

**Chinese:** 你需要先了解情况，然后再做决定。
**Pinyin:** Nǐ xūyào xiān liǎojiě qíngkuàng, ránhòu zài zuò juédìng.
**Literal:** You need first understand situation, then again make decision.
**English:** You need to first understand the situation, then make a decision.

**Chinese:** 在中国，需要先建立信任，然后再谈合作。
**Pinyin:** Zài Zhōngguó, xūyào xiān jiànlì xìnrèn, ránhòu zài tán hézuò.
**Literal:** In China, need first establish trust, then again discuss cooperation.
**English:** In China, you need to first build trust, then discuss cooperation.

---

## 5. Practice

**Exercise 1:** How do you say "I want to learn about {key_word_en}" in Chinese?
**Answer:** 我想了解一下{key_word_zh}。(Wǒ xiǎng liǎojiě yīxià {key_word_zh}.)

**Exercise 2:** Translate: "Relationships are the foundation of everything in China."
**Answer:** 在中国，关系是一切的基础。(Zài Zhōngguó, guānxi shì yīqiè de jīchǔ.)

**Exercise 3:** Fill in the blank: 你需要先___，然后再___。(Complete with appropriate actions for the context of {topic_en}.)
**Answer:** 你需要先建立关系，然后再谈具体事情。(You need to first build relationships, then discuss specific matters.)

---

## 6. Cultural Insight

Understanding {topic_en} in China requires awareness of cultural context. Chinese professionals approach this differently from Westerners — relationships (关系 guānxi), face (面子 miànzi), and indirect communication all play important roles. When dealing with {key_word_zh}-related situations, patience is key. Don't rush to the point; build rapport first. This approach, while slower, leads to more durable outcomes. Foreign professionals who adapt to this style consistently report better results in their Chinese professional and social lives.

---

"""
    return chapter


def generate_book(book_num, book_info):
    """Generate a complete book and write to file."""
    out_dir = OUTPUT_BASE / book_info["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / book_info["filename"]

    header = f"""# Z Turns Chinese Book {book_num}
## {book_info['title']} — {book_info['subtitle']}
**Author:** Tony Sheng
**Website:** zturnsgo.com
**Teaching Experience:** 3000+ hours of real Chinese teaching
**Series Color:** {book_info['color']}

---

"""
    content = header
    for i, ch_data in enumerate(book_info["chapters"], 1):
        en_title, zh_title, topic_en, key_word_zh, key_word_en = ch_data
        content += make_chapter(book_num, i, en_title, zh_title, topic_en, key_word_zh, key_word_en)

    out_file.write_text(content, encoding="utf-8")
    lines = content.count("\n")
    size_kb = len(content.encode("utf-8")) // 1024
    print(f"  Book {book_num}: {out_file.name} — {lines} lines, {size_kb} KB")
    return out_file


def main():
    import sys
    # Which books to generate
    if len(sys.argv) > 1:
        book_nums = [int(x) for x in sys.argv[1:]]
    else:
        book_nums = sorted(BOOKS.keys())

    print(f"Generating {len(book_nums)} books...")
    for num in book_nums:
        if num in BOOKS:
            generate_book(num, BOOKS[num])
        else:
            print(f"  Book {num}: not defined, skipping")
    print("Done.")


if __name__ == "__main__":
    main()
