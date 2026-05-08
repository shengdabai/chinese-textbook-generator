#!/usr/bin/env python3
"""Generate Z Turns Chinese Books 71-100 as Markdown + PDF.

Follows the Book51-70 template structure:
- 25 chapters per book (5 Parts × 5 chapters)
- Each chapter: Real Scene, Vocabulary, Dialogues, Patterns, Culture, Practice
- Sequential PDF compilation (no parallel subprocess)
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

BASE = Path("../..")
V3 = BASE / "生成工具/v3-typst"
OUTPUT_ROOT = BASE / "中文教材"
GENERATOR = V3 / "generate.py"
VENV_PY = V3 / ".venv/bin/python"


@dataclass(frozen=True)
class Chapter:
    title_en: str
    title_zh: str
    core_term: str  # Chinese keyword for the chapter
    core_term_en: str
    core_term_pinyin: str


@dataclass(frozen=True)
class Book:
    number: int
    slug: str
    title_en: str
    subtitle_zh: str
    color: str
    part_titles: list[tuple[str, str]]  # (English part title, Chinese part title)
    chapters: list[Chapter]  # 25 chapters


# =========================================================================
# BOOK DEFINITIONS (71-100)
# =========================================================================

BOOKS: list[Book] = [
    # -----------------------------------------------------------------
    # BOOK 71: Beijing Deep Dive
    # -----------------------------------------------------------------
    Book(
        number=71,
        slug="Beijing",
        title_en="Beijing Deep Dive",
        subtitle_zh="北京人的语言与生活",
        color="#C62828",
        part_titles=[
            ("Beijing Dialect", "北京话"),
            ("Historical Beijing", "历史北京"),
            ("Modern Beijing", "现代北京"),
            ("Political Capital", "政治中心"),
            ("Living in Beijing", "北京生活"),
        ],
        chapters=[
            Chapter("Features of Beijing Dialect", "北京话的特点", "儿化音", "rhotic ending (erhua)", "érhuà yīn"),
            Chapter("Classic Beijing Vocabulary", "京腔词汇", "倍儿棒", "awesome (Beijing slang)", "bèir bàng"),
            Chapter("Language of the Hutongs", "胡同里的语言", "胡同", "hutong / old alley", "hútòng"),
            Chapter("Beijing-Style Sarcasm", "骂人不带脏字", "损人", "mock/tease someone", "sǔn rén"),
            Chapter("Mandarin vs. Beijing Dialect", "普通话和北京话", "普通话", "standard Mandarin", "pǔtōnghuà"),
            Chapter("Language of the Forbidden City", "故宫语言", "故宫", "the Forbidden City", "Gùgōng"),
            Chapter("Courtyard Homes", "四合院", "四合院", "courtyard house", "sìhéyuàn"),
            Chapter("Imperial Gardens", "皇家园林", "颐和园", "Summer Palace", "Yíhéyuán"),
            Chapter("Time-Honored Brands", "老字号", "老字号", "time-honored brand", "lǎo zìhào"),
            Chapter("Districts of Beijing", "北京城区", "城区", "urban district", "chéngqū"),
            Chapter("Internet Beijing", "互联网北京", "中关村", "Zhongguancun (tech hub)", "Zhōngguāncūn"),
            Chapter("Creative Beijing", "文创北京", "798艺术区", "798 Art District", "qī jiǔ bā yìshù qū"),
            Chapter("International Beijing", "国际北京", "三里屯", "Sanlitun district", "Sānlǐtún"),
            Chapter("University Town", "大学城", "大学城", "university town", "dàxué chéng"),
            Chapter("Beijing Nightlife", "北京夜生活", "簋街", "Ghost Street (food street)", "Guǐ jiē"),
            Chapter("The Two Sessions", "两会语言", "两会", "Two Sessions (NPC+CPPCC)", "liǎng huì"),
            Chapter("Government Agencies", "政府机构", "部委", "ministries and commissions", "bùwěi"),
            Chapter("Political Vocabulary", "政治话语", "政策", "policy", "zhèngcè"),
            Chapter("Diplomatic Language", "外交语言", "使馆", "embassy", "shǐguǎn"),
            Chapter("Reading Press Conferences", "新闻发布会", "发布会", "press conference", "fābùhuì"),
            Chapter("Commuting in Beijing", "北京交通", "地铁", "subway", "dìtiě"),
            Chapter("Beijing Cuisine", "北京美食", "炸酱面", "zhajiangmian (noodles)", "zhájiàngmiàn"),
            Chapter("Sandstorms and Smog", "沙尘暴和雾霾", "雾霾", "smog", "wùmái"),
            Chapter("The Beijing Hukou", "北京户口", "户口", "household registration", "hùkǒu"),
            Chapter("Foreigners' Beijing", "外国人的北京", "融入", "integrate / fit in", "róngrù"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 72: Shanghai Style
    # -----------------------------------------------------------------
    Book(
        number=72,
        slug="Shanghai",
        title_en="Shanghai Style",
        subtitle_zh="上海腔：摩登都市的语言密码",
        color="#1565C0",
        part_titles=[
            ("Shanghai Dialect", "上海话"),
            ("Old Shanghai", "老上海"),
            ("Financial Hub", "金融中心"),
            ("Contemporary Shanghai", "当代上海"),
            ("Shanghai's Future", "上海未来"),
        ],
        chapters=[
            Chapter("Shanghainese Basics", "沪语入门", "沪语", "Shanghainese", "hù yǔ"),
            Chapter("Common Shanghainese", "常用沪语", "阿拉", "we / us (Shanghainese)", "ā lā"),
            Chapter("Shanghai-Accented Mandarin", "上海腔普通话", "腔调", "accent / tone", "qiāngdiào"),
            Chapter("Modern Shanghai Vocabulary", "摩登词汇", "洋气", "stylish / cosmopolitan", "yángqì"),
            Chapter("Dialect Preservation", "方言保护", "方言", "dialect", "fāngyán"),
            Chapter("The Concessions Era", "租界历史", "租界", "foreign concession", "zūjiè"),
            Chapter("Shikumen Alleys", "弄堂文化", "弄堂", "Shanghai lane", "lòngtáng"),
            Chapter("Qipao and Haipai", "旗袍与海派", "海派", "Shanghai style (haipai)", "hǎi pài"),
            Chapter("The Paramount Era", "百乐门时代", "百乐门", "Paramount Ballroom", "Bǎilèmén"),
            Chapter("Literary Shanghai", "文学上海", "张爱玲", "Eileen Chang", "Zhāng Àilíng"),
            Chapter("Lujiazui Language", "陆家嘴语言", "陆家嘴", "Lujiazui financial district", "Lùjiāzuǐ"),
            Chapter("Stock Market Culture", "股市文化", "股票", "stock", "gǔpiào"),
            Chapter("Foreign Capital in Shanghai", "外资在沪", "外资", "foreign investment", "wàizī"),
            Chapter("Free Trade Zone", "自贸区", "自贸区", "free trade zone", "zìmào qū"),
            Chapter("International Settlement", "国际结算", "结算", "settlement", "jiésuàn"),
            Chapter("Xintiandi and Hengfu", "新天地与衡复", "新天地", "Xintiandi district", "Xīntiāndì"),
            Chapter("Shanghai Cuisine", "上海美食", "本帮菜", "local Shanghai cuisine", "běnbāng cài"),
            Chapter("Theatre and Music Scene", "演出文化", "剧院", "theatre", "jùyuàn"),
            Chapter("Expat Communities", "国际社区", "古北", "Gubei expat area", "Gǔběi"),
            Chapter("Shanghai Nightlife", "上海夜生活", "酒吧", "bar / pub", "jiǔbā"),
            Chapter("The Import Expo", "进博会", "进博会", "China Import Expo", "Jìn bó huì"),
            Chapter("Science and Tech Hub", "科创中心", "张江", "Zhangjiang Hi-Tech Park", "Zhāngjiāng"),
            Chapter("Urban Renewal", "城市更新", "更新", "renewal / upgrade", "gēngxīn"),
            Chapter("Yangtze Delta Integration", "长三角一体化", "长三角", "Yangtze River Delta", "Cháng sān jiǎo"),
            Chapter("Foreigners in Shanghai", "外国人的上海", "定居", "settle down", "dìngjū"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 73: Chengdu & Sichuan Living
    # -----------------------------------------------------------------
    Book(
        number=73,
        slug="Chengdu",
        title_en="Chengdu Sichuan Living",
        subtitle_zh="成都慢生活：麻辣与安逸的语言",
        color="#E53935",
        part_titles=[
            ("Sichuan Dialect", "四川话"),
            ("Food Culture", "饮食文化"),
            ("Leisure Life", "休闲生活"),
            ("New Chengdu", "新成都"),
            ("Beyond the City", "成都之外"),
        ],
        chapters=[
            Chapter("Features of Sichuanese", "四川话特点", "四川话", "Sichuanese", "Sìchuān huà"),
            Chapter("Chengdu Local Slang", "成都土话", "巴适", "comfortable / great", "bāshì"),
            Chapter("Chongqing vs. Chengdu", "重庆和成都", "重庆", "Chongqing", "Chóngqìng"),
            Chapter("Dialect in Daily Life", "方言日常", "日常", "daily routine", "rìcháng"),
            Chapter("Why Sichuanese Feels Warm", "四川话的亲切感", "亲切", "warm / friendly", "qīnqiè"),
            Chapter("Hot Pot Deep Dive", "火锅深度", "火锅", "hot pot", "huǒguō"),
            Chapter("Chuanchuan and Maocai", "串串和冒菜", "串串", "skewer hot pot", "chuànchuàn"),
            Chapter("Tofu Dishes", "豆腐系列", "麻婆豆腐", "mapo tofu", "mápó dòufu"),
            Chapter("Hole-in-the-Wall Eateries", "苍蝇馆子", "苍蝇馆子", "hole-in-the-wall eatery", "cāngyíng guǎnzi"),
            Chapter("Teahouse Culture", "茶馆文化", "茶馆", "teahouse", "cháguǎn"),
            Chapter("The Panda Base", "熊猫基地", "大熊猫", "giant panda", "dà xióngmāo"),
            Chapter("Sichuan Opera Face-Changing", "川剧变脸", "变脸", "face changing", "biàn liǎn"),
            Chapter("Mahjong Parlours", "麻将馆", "麻将", "mahjong", "májiàng"),
            Chapter("Kuanzhai Alleys", "宽窄巷子", "宽窄巷子", "Kuanzhai Alley", "Kuān zhǎi xiàngzi"),
            Chapter("Jinli and Wuhou", "锦里和武侯", "锦里", "Jinli street", "Jǐn lǐ"),
            Chapter("Chunxi Road Shopping", "春熙路商圈", "春熙路", "Chunxi Road", "Chūn xī lù"),
            Chapter("New Economy in Chengdu", "新经济成都", "新经济", "new economy", "xīn jīngjì"),
            Chapter("Chengdu Night Economy", "成都夜经济", "夜市", "night market", "yèshì"),
            Chapter("Viral City", "网红城市", "网红", "internet-famous", "wǎnghóng"),
            Chapter("Community Life", "社区生活", "小区", "residential compound", "xiǎoqū"),
            Chapter("Qingcheng Mountain", "青城山", "青城山", "Qingcheng Mountain", "Qīngchéng shān"),
            Chapter("Dujiangyan Irrigation", "都江堰", "都江堰", "Dujiangyan system", "Dūjiāngyàn"),
            Chapter("Jiuzhaigou Travel", "九寨沟旅游", "九寨沟", "Jiuzhaigou valley", "Jiǔzhài gōu"),
            Chapter("Tibetan Borderlands", "藏区边界", "康定", "Kangding town", "Kāngdìng"),
            Chapter("Foreigners in Chengdu", "外国人的成都", "融入", "fit in / integrate", "róngrù"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 74: Hong Kong Chinese
    # -----------------------------------------------------------------
    Book(
        number=74,
        slug="HongKong",
        title_en="Hong Kong Chinese",
        subtitle_zh="香港中文：粤语与普通话之间",
        color="#6A1B9A",
        part_titles=[
            ("Cantonese Essentials", "粤语基础"),
            ("Hong Kong Identity", "香港身份"),
            ("Business Hub", "商业中心"),
            ("Daily Life", "日常生活"),
            ("Cultural Nuances", "文化细节"),
        ],
        chapters=[
            Chapter("Cantonese vs. Mandarin", "粤语和普通话", "粤语", "Cantonese", "yuè yǔ"),
            Chapter("Daily Cantonese Phrases", "日常粤语", "唔该", "thank you (Cantonese)", "m̀h gōi"),
            Chapter("Hong Kong Chinglish", "香港式英语", "港式英语", "Hong Kong English", "gǎng shì yīngyǔ"),
            Chapter("Trilingual Environment", "三语环境", "三语", "trilingual", "sān yǔ"),
            Chapter("Cantonese Slang", "粤语流行语", "巴闭", "showing off (Cantonese)", "bā bì"),
            Chapter("Local Identity", "本地人认同", "本地人", "local person", "běndì rén"),
            Chapter("Post-1997 Language", "九七回归语言", "回归", "handover / return", "huíguī"),
            Chapter("Migration Waves", "移民文化", "移民", "immigration", "yímín"),
            Chapter("International City", "国际城市", "国际化", "internationalization", "guójìhuà"),
            Chapter("Cultural Heritage", "文化遗产", "遗产", "heritage", "yíchǎn"),
            Chapter("Hong Kong Finance", "香港金融", "港交所", "HK Stock Exchange", "Gǎng jiāo suǒ"),
            Chapter("Common Law Language", "普通法语言", "普通法", "common law", "pǔtōngfǎ"),
            Chapter("Trade and Logistics", "贸易与物流", "贸易", "trade", "màoyì"),
            Chapter("Startup Ecosystem", "初创生态", "初创", "startup", "chūchuàng"),
            Chapter("Greater Bay Area", "大湾区语言", "大湾区", "Greater Bay Area", "Dà wān qū"),
            Chapter("MTR and Transport", "港铁与交通", "港铁", "MTR subway", "Gǎng tiě"),
            Chapter("Cha Chaan Teng Culture", "茶餐厅文化", "茶餐厅", "HK-style café", "chá cāntīng"),
            Chapter("Shopping in Hong Kong", "香港购物", "铜锣湾", "Causeway Bay", "Tóngluó wān"),
            Chapter("Finding Housing", "找房子", "租金", "rent", "zūjīn"),
            Chapter("Medical System", "医疗系统", "公立医院", "public hospital", "gōnglì yīyuàn"),
            Chapter("Hong Kong Cinema", "香港电影", "港片", "Hong Kong film", "gǎng piàn"),
            Chapter("Cantopop", "粤语歌曲", "粤语歌", "Cantopop song", "yuèyǔ gē"),
            Chapter("Dragon Boat Festival", "端午龙舟", "龙舟", "dragon boat", "lóngzhōu"),
            Chapter("Expat Communities", "外籍人士社区", "外籍", "foreign nationality", "wàijí"),
            Chapter("Mandarin in HK", "普通话在香港", "礼仪", "etiquette", "lǐyí"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 75: Taiwan Chinese
    # -----------------------------------------------------------------
    Book(
        number=75,
        slug="Taiwan",
        title_en="Taiwan Chinese",
        subtitle_zh="台湾中文：繁体字与宝岛生活",
        color="#00695C",
        part_titles=[
            ("Traditional Characters", "繁体字"),
            ("Taiwan Mandarin", "台湾腔普通话"),
            ("Night Market Culture", "夜市文化"),
            ("Society and Culture", "社会文化"),
            ("Living in Taiwan", "台湾生活"),
        ],
        chapters=[
            Chapter("Traditional vs. Simplified", "繁体和简体", "繁体字", "traditional characters", "fántǐ zì"),
            Chapter("Learning Traditional Characters", "繁体字学习", "学习策略", "learning strategy", "xuéxí cèlüè"),
            Chapter("Zhuyin Phonetic System", "注音符号", "注音", "Zhuyin (Bopomofo)", "zhùyīn"),
            Chapter("Calligraphic Aesthetics", "书写美学", "书写", "handwriting", "shūxiě"),
            Chapter("Taiwan Digital Media", "繁体数字媒体", "繁体媒体", "traditional-char media", "fántǐ méitǐ"),
            Chapter("Taiwan Accent Features", "台湾腔特点", "台湾腔", "Taiwanese accent", "Táiwān qiāng"),
            Chapter("Taiwan-Specific Vocabulary", "台湾词汇", "机车", "motorbike/annoying", "jīchē"),
            Chapter("Hokkien Loanwords", "台语借词", "台语", "Taiwanese Hokkien", "Tái yǔ"),
            Chapter("Taiwan Politeness", "台湾礼貌语言", "礼貌", "politeness", "lǐmào"),
            Chapter("Youth Slang", "台湾年轻人用语", "流行语", "buzzword", "liúxíngyǔ"),
            Chapter("Night Market Navigation", "夜市导航", "夜市", "night market", "yèshì"),
            Chapter("Snack Ordering", "小吃点餐", "珍珠奶茶", "bubble tea", "zhēnzhū nǎichá"),
            Chapter("Bargaining Culture", "夜市议价", "讲价", "bargain / haggle", "jiǎng jià"),
            Chapter("Night Market Games", "夜市游戏", "套圈圈", "ring toss game", "tào quān quān"),
            Chapter("Temple Festivals", "庙会文化", "庙会", "temple fair", "miàohuì"),
            Chapter("Language of Democracy", "民主语言", "选举", "election", "xuǎnjǔ"),
            Chapter("Multicultural Taiwan", "多元文化", "多元", "multicultural", "duōyuán"),
            Chapter("Environmental Awareness", "环保意识", "环保", "environmental protection", "huánbǎo"),
            Chapter("Civil Society", "公民社会", "公民", "citizen", "gōngmín"),
            Chapter("Media Ecosystem", "媒体生态", "媒体", "media", "méitǐ"),
            Chapter("National Health Insurance", "健保制度", "健保", "national health insurance", "jiànbǎo"),
            Chapter("Transportation", "交通", "捷运", "MRT subway", "jiéyùn"),
            Chapter("Taiwan Universities", "台湾教育", "大学", "university", "dàxué"),
            Chapter("Hot Spring Culture", "温泉文化", "温泉", "hot spring", "wēnquán"),
            Chapter("Foreigners' Taiwan", "外国人的台湾", "融入", "integrate", "róngrù"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 76: Friendship in Chinese
    # -----------------------------------------------------------------
    Book(
        number=76,
        slug="Friendship",
        title_en="Friendship in Chinese",
        subtitle_zh="友情语言：建立真实的中文友谊",
        color="#F57F17",
        part_titles=[
            ("Making Friends", "建立友谊"),
            ("Deepening Connection", "深化关系"),
            ("Friend Groups", "朋友圈子"),
            ("Friendship Challenges", "友谊的考验"),
            ("Cross-Cultural Friendship", "跨文化友谊"),
        ],
        chapters=[
            Chapter("Real First Meeting", "真实初次见面", "认识", "get to know / meet", "rènshi"),
            Chapter("Shared Interests", "共同爱好", "爱好", "hobby", "àihào"),
            Chapter("Adding WeChat Friends", "加微信好友", "微信", "WeChat", "Wēixìn"),
            Chapter("Making Plans Together", "约出去玩", "约", "make an appointment", "yuē"),
            Chapter("WeChat Moments Interaction", "朋友圈互动", "朋友圈", "Moments feed", "péngyǒu quān"),
            Chapter("Talking Heart-to-Heart", "聊心事", "心事", "inner thoughts", "xīnshì"),
            Chapter("Sharing Secrets", "分享秘密", "秘密", "secret", "mìmì"),
            Chapter("Expressing Thanks", "说谢谢", "感谢", "thanks / to thank", "gǎnxiè"),
            Chapter("Apology and Repair", "道歉与修复", "道歉", "apology", "dàoqiàn"),
            Chapter("Long-Term Companionship", "长久陪伴", "陪伴", "companionship", "péibàn"),
            Chapter("Roommate Culture", "大学室友文化", "室友", "roommate", "shìyǒu"),
            Chapter("Coworkers to Friends", "同事变朋友", "同事", "coworker", "tóngshì"),
            Chapter("Meeting Online Friends", "网友见面", "网友", "online friend", "wǎngyǒu"),
            Chapter("Multiple Friend Groups", "不同圈子", "圈子", "circle / group", "quānzi"),
            Chapter("Best Friends Gender Talk", "闺蜜和哥们", "闺蜜", "bestie (female)", "guīmì"),
            Chapter("Money Between Friends", "朋友借钱问题", "借钱", "borrow money", "jiè qián"),
            Chapter("Conflict and Cold War", "矛盾与冷战", "冷战", "cold war / silent treatment", "lěngzhàn"),
            Chapter("Friendships Drift Apart", "朋友分道扬镳", "分道扬镳", "part ways", "fēn dào yáng biāo"),
            Chapter("Jealousy Between Friends", "朋友间嫉妒", "嫉妒", "jealousy", "jídù"),
            Chapter("Advising a Friend", "劝朋友", "劝", "advise / persuade", "quàn"),
            Chapter("Foreigner-Chinese Friendship", "跨文化友谊", "跨文化", "cross-cultural", "kuà wénhuà"),
            Chapter("Discussing Differences", "对话差异", "差异", "difference", "chāyì"),
            Chapter("Unequal Language Levels", "语言不对等", "母语", "mother tongue", "mǔyǔ"),
            Chapter("Hosting Foreign Friends", "招待外国朋友", "招待", "entertain guests", "zhāodài"),
            Chapter("Lasting Friendship", "永恒的友谊", "友谊", "friendship", "yǒuyì"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 77: Family Ties Chinese
    # -----------------------------------------------------------------
    Book(
        number=77,
        slug="Family",
        title_en="Family Ties Chinese",
        subtitle_zh="中国家庭：亲情与代际语言",
        color="#4527A0",
        part_titles=[
            ("Family Structure", "家庭结构"),
            ("Parenting Language", "养育语言"),
            ("Filial Piety", "孝道"),
            ("Family Conflicts", "家庭冲突"),
            ("Love Across Generations", "代际之爱"),
        ],
        chapters=[
            Chapter("Complete Kinship Terms", "称呼大全", "称呼", "form of address", "chēnghū"),
            Chapter("Nuclear vs. Extended Family", "核心家庭和大家庭", "家庭", "family", "jiātíng"),
            Chapter("The Only Child Generation", "独生子女一代", "独生子女", "only child", "dúshēng zǐnǚ"),
            Chapter("The Family WeChat Group", "家庭群", "家庭群", "family chat group", "jiātíng qún"),
            Chapter("Spring Festival Reunion", "春节大团圆", "团圆", "family reunion", "tuányuán"),
            Chapter("Chinese Parents' Expectations", "中国父母的期待", "期待", "expectation", "qīdài"),
            Chapter("Praising Children", "夸孩子", "夸奖", "praise", "kuājiǎng"),
            Chapter("Criticizing Children", "批评孩子", "批评", "criticize", "pīpíng"),
            Chapter("Homework Help", "家庭作业", "作业", "homework", "zuòyè"),
            Chapter("Talking With Teens", "青春期对话", "青春期", "adolescence", "qīngchūnqī"),
            Chapter("What Is Filial Piety", "什么是孝", "孝顺", "filial piety", "xiàoshùn"),
            Chapter("Supporting Aging Parents", "赡养老人", "赡养", "support elderly", "shànyǎng"),
            Chapter("Visiting Home Regularly", "回家探望", "探望", "visit", "tànwàng"),
            Chapter("Accepting Parental Critique", "接受父母批评", "尊重", "respect", "zūnzhòng"),
            Chapter("Modern Filial Boundaries", "现代孝道的边界", "边界", "boundary", "biānjiè"),
            Chapter("Mother-in-Law Relations", "婆媳关系", "婆媳", "mother-in-law + daughter-in-law", "pó xí"),
            Chapter("Family of Origin Wounds", "原生家庭伤痛", "原生家庭", "family of origin", "yuánshēng jiātíng"),
            Chapter("Inheritance Conversations", "财产分配", "遗产", "inheritance", "yíchǎn"),
            Chapter("Parents Pushing Marriage", "父母催婚", "催婚", "pressure to marry", "cuī hūn"),
            Chapter("Setting Family Boundaries", "家庭界限", "界限", "limit / boundary", "jièxiàn"),
            Chapter("Grandparental Wisdom", "爷爷奶奶的智慧", "爷爷奶奶", "grandparents", "yéye nǎinai"),
            Chapter("Storytelling to Children", "给孩子讲故事", "故事", "story", "gùshi"),
            Chapter("Distance Family Calls", "远距离家庭联系", "视频通话", "video call", "shìpín tōnghuà"),
            Chapter("Losing a Loved One", "失去亲人", "哀悼", "mourn", "āidào"),
            Chapter("Marrying Into Chinese Family", "融入伴侣家庭", "融入", "integrate", "róngrù"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 78: Love & Romance in Chinese
    # -----------------------------------------------------------------
    Book(
        number=78,
        slug="Romance",
        title_en="Love Romance in Chinese",
        subtitle_zh="爱情中文：从表白到长相厮守",
        color="#E91E63",
        part_titles=[
            ("Finding Love", "寻找爱情"),
            ("Dating", "约会"),
            ("Being Together", "恋爱中"),
            ("Serious Commitment", "认真承诺"),
            ("Love Challenges", "爱情考验"),
        ],
        chapters=[
            Chapter("Traditional Matchmaking", "相亲", "相亲", "matchmaking meeting", "xiāngqīn"),
            Chapter("Dating Apps in China", "交友软件", "交友软件", "dating app", "jiāoyǒu ruǎnjiàn"),
            Chapter("First Impressions", "第一印象", "印象", "impression", "yìnxiàng"),
            Chapter("Expressing a Crush", "暗恋语言", "暗恋", "secret crush", "ànliàn"),
            Chapter("Responding to Pursuers", "被追求", "追求", "pursue / court", "zhuīqiú"),
            Chapter("First Date Language", "第一次约会", "约会", "date / go out", "yuēhuì"),
            Chapter("Who Pays the Bill", "谁买单", "买单", "pay the bill", "mǎi dān"),
            Chapter("Gifts for Partners", "送礼物", "礼物", "gift", "lǐwù"),
            Chapter("Valentine's and Qixi", "情人节和七夕", "七夕", "Qixi festival", "Qī xī"),
            Chapter("Defining the Relationship", "确认关系", "在一起", "together (in a relationship)", "zài yīqǐ"),
            Chapter("Sweet Daily Life", "甜蜜日常", "甜蜜", "sweet", "tiánmì"),
            Chapter("Arguments and Making Up", "争吵与和好", "吵架", "argue / quarrel", "chǎojià"),
            Chapter("Dealing With Jealousy", "处理嫉妒", "吃醋", "jealous (literally: eat vinegar)", "chī cù"),
            Chapter("Long-Distance Love", "异地恋", "异地恋", "long-distance relationship", "yìdì liàn"),
            Chapter("Meeting the Parents", "见家长", "见家长", "meet the parents", "jiàn jiāzhǎng"),
            Chapter("Marriage Talk", "谈婚论嫁", "结婚", "marry", "jiéhūn"),
            Chapter("Proposing in Chinese", "中式求婚", "求婚", "propose marriage", "qiú hūn"),
            Chapter("Housing and Marriage", "房子与婚姻", "房子", "house / apartment", "fángzi"),
            Chapter("Betrothal Gifts", "彩礼和嫁妆", "彩礼", "betrothal gift", "cǎi lǐ"),
            Chapter("Living Together Before Marriage", "婚前同居", "同居", "cohabit", "tóngjū"),
            Chapter("Breaking Up Gracefully", "体面分手", "分手", "break up", "fēnshǒu"),
            Chapter("Getting Back Together", "复合", "复合", "reconcile / reunite", "fùhé"),
            Chapter("Cross-Cultural Romance", "跨国恋", "跨国", "cross-border / international", "kuà guó"),
            Chapter("Healing After Heartbreak", "失恋疗愈", "失恋", "heartbreak", "shīliàn"),
            Chapter("Eternal Love Expressions", "永恒之爱", "永恒", "eternal", "yǒnghéng"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 79: Solitude & Inner Life
    # -----------------------------------------------------------------
    Book(
        number=79,
        slug="Solitude",
        title_en="Solitude Inner Life",
        subtitle_zh="独处中文：内心世界的语言表达",
        color="#455A64",
        part_titles=[
            ("Being Alone", "独处"),
            ("Inner Emotions", "内心情感"),
            ("Reflection and Growth", "反思与成长"),
            ("Finding Peace", "寻找平静"),
            ("Connection Through Solitude", "独处中的连接"),
        ],
        chapters=[
            Chapter("Solitude vs. Loneliness", "独处和孤独", "独处", "solitude", "dúchǔ"),
            Chapter("Living Alone Daily", "独居生活", "独居", "live alone", "dújū"),
            Chapter("Solo Travel", "独自旅行", "独自", "alone / by oneself", "dúzì"),
            Chapter("Eating Alone", "一个人吃饭", "一个人", "by oneself", "yī gè rén"),
            Chapter("Introvert vs. Extrovert", "内向和外向", "内向", "introverted", "nèixiàng"),
            Chapter("Expressing Emotions Openly", "说出来", "表达", "express", "biǎodá"),
            Chapter("Talking About Stress", "说压力", "压力", "pressure / stress", "yālì"),
            Chapter("Modern Anxiety Language", "焦虑语言", "焦虑", "anxiety", "jiāolǜ"),
            Chapter("When You Feel Low", "低落时", "低落", "feeling low", "dīluò"),
            Chapter("Healing Culture", "治愈文化", "治愈", "healing", "zhìyù"),
            Chapter("Chinese Journaling", "中文日记", "日记", "diary", "rìjì"),
            Chapter("Self-Talk in Chinese", "中文自我对话", "自我", "self", "zìwǒ"),
            Chapter("Meaning of Life", "人生意义", "意义", "meaning", "yìyì"),
            Chapter("Accepting Failure", "接受失败", "失败", "failure", "shībài"),
            Chapter("Your Growth Narrative", "成长叙事", "成长", "grow up", "chéngzhǎng"),
            Chapter("Meditation and Mindfulness", "冥想与正念", "正念", "mindfulness", "zhèngniàn"),
            Chapter("Healing in Nature", "自然疗愈", "自然", "nature", "zìrán"),
            Chapter("Books and Music", "书籍与音乐", "书籍", "books", "shūjí"),
            Chapter("Minimalist Living", "断舍离", "断舍离", "minimalism (declutter)", "duàn shě lí"),
            Chapter("Slowing Down", "慢下来", "慢生活", "slow living", "màn shēnghuó"),
            Chapter("Chatting With Strangers", "和陌生人聊天", "陌生人", "stranger", "mòshēng rén"),
            Chapter("Writing Letters", "写信", "写信", "write a letter", "xiě xìn"),
            Chapter("Social Media Solitude", "社交媒体独处", "社交媒体", "social media", "shèjiāo méitǐ"),
            Chapter("Pet Companionship", "宠物陪伴", "宠物", "pet", "chǒngwù"),
            Chapter("One Person Is Fine", "一个人也很好", "独立", "independent", "dúlì"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 80: Mental Health Chinese
    # -----------------------------------------------------------------
    Book(
        number=80,
        slug="MentalHealth",
        title_en="Mental Health Chinese",
        subtitle_zh="心理健康：说出内心的中文",
        color="#2E7D32",
        part_titles=[
            ("Mental Health Basics", "心理健康基础"),
            ("In the Therapy Room", "咨询室里"),
            ("Social Stigma", "社会污名"),
            ("Self-Care Language", "自我关怀语言"),
            ("System and Resources", "系统与资源"),
        ],
        chapters=[
            Chapter("Concept of Mental Health", "心理健康概念", "心理健康", "mental health", "xīnlǐ jiànkāng"),
            Chapter("Common Mental Concerns", "常见心理问题", "抑郁", "depression", "yìyù"),
            Chapter("Asking for Help", "求助第一步", "求助", "ask for help", "qiú zhù"),
            Chapter("Booking a Counselor", "预约心理咨询", "咨询", "counseling", "zīxún"),
            Chapter("Crisis Hotlines", "心理热线", "热线", "hotline", "rèxiàn"),
            Chapter("Describing Symptoms", "描述症状", "症状", "symptom", "zhèngzhuàng"),
            Chapter("Narrating Your Past", "讲述过去", "过去", "past", "guòqù"),
            Chapter("Naming Emotions", "情绪命名", "情绪", "emotion", "qíngxù"),
            Chapter("CBT Techniques", "认知行为技术", "认知", "cognition", "rènzhī"),
            Chapter("Ending Therapy", "结束咨询", "结束", "end / finish", "jiéshù"),
            Chapter("Facing Prejudice", "面对偏见", "偏见", "prejudice", "piānjiàn"),
            Chapter("Telling Your Parents", "告诉家人", "告诉", "tell / inform", "gàosu"),
            Chapter("Mental Health at Work", "职场心理健康", "职场", "workplace", "zhíchǎng"),
            Chapter("Overcoming Stigma", "病耻感", "病耻感", "illness stigma", "bìng chǐ gǎn"),
            Chapter("Supporting Others", "支持他人", "支持", "support", "zhīchí"),
            Chapter("Emotion Journaling", "情绪日记", "情绪日记", "emotion journal", "qíngxù rìjì"),
            Chapter("Self-Compassion", "自我慈悲", "慈悲", "compassion", "cíbēi"),
            Chapter("Setting Boundaries", "边界设定", "边界", "boundary", "biānjiè"),
            Chapter("Communicating Overwhelm", "表达压力过大", "压垮", "overwhelm", "yā kuǎ"),
            Chapter("Asking for Help Is OK", "求助不丢人", "坚强", "strong / resilient", "jiānqiáng"),
            Chapter("Chinese Therapy Industry", "中国心理行业", "咨询师", "counselor", "zīxún shī"),
            Chapter("University Counseling", "大学心理中心", "心理中心", "counseling center", "xīnlǐ zhōngxīn"),
            Chapter("Employee Assistance Programs", "企业EAP", "EAP", "Employee Assistance Program", "EAP"),
            Chapter("Online Therapy Platforms", "线上心理平台", "线上", "online", "xiànshàng"),
            Chapter("Expat Mental Health", "在华外国人心理", "在华", "in China", "zài Huá"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 81: Traditional Chinese Medicine
    # -----------------------------------------------------------------
    Book(
        number=81,
        slug="TCM",
        title_en="Traditional Chinese Medicine",
        subtitle_zh="中医语言：从经络到药方",
        color="#BF360C",
        part_titles=[
            ("TCM Philosophy", "中医哲学"),
            ("Diagnosis Methods", "望闻问切"),
            ("Treatments", "治疗方法"),
            ("Herbs and Pharmacy", "草药与药房"),
            ("Modern TCM", "现代中医"),
        ],
        chapters=[
            Chapter("Yin-Yang Balance", "阴阳平衡", "阴阳", "yin and yang", "yīn yáng"),
            Chapter("Five Elements and Organs", "五行五脏", "五行", "Five Elements", "wǔ xíng"),
            Chapter("The Concept of Qi", "气的概念", "气", "vital energy / qi", "qì"),
            Chapter("Meridian System", "经络系统", "经络", "meridians", "jīngluò"),
            Chapter("Body Constitution", "体质辨识", "体质", "body constitution", "tǐzhì"),
            Chapter("Inspection (Wang)", "望诊", "望诊", "visual inspection", "wàng zhěn"),
            Chapter("Listening and Smelling (Wen)", "闻诊", "闻诊", "listening/smelling diag", "wén zhěn"),
            Chapter("Questioning (Wen)", "问诊", "问诊", "inquiry diagnosis", "wèn zhěn"),
            Chapter("Pulse Taking (Qie)", "切诊", "切诊", "pulse diagnosis", "qiè zhěn"),
            Chapter("Describing Your Issue", "向中医描述", "症状", "symptoms", "zhèngzhuàng"),
            Chapter("Acupuncture Terms", "针灸", "针灸", "acupuncture", "zhēnjiǔ"),
            Chapter("Tui Na Massage", "推拿按摩", "推拿", "Tui Na massage", "tuīná"),
            Chapter("Cupping and Gua Sha", "拔罐刮痧", "拔罐", "cupping", "bá guàn"),
            Chapter("Moxibustion", "艾灸", "艾灸", "moxibustion", "àijiǔ"),
            Chapter("Reading Herbal Prescriptions", "中药方剂", "方剂", "herbal formula", "fāngjì"),
            Chapter("Visiting a TCM Pharmacy", "中药房对话", "中药", "Chinese medicine", "zhōngyào"),
            Chapter("Common Chinese Herbs", "常见中草药", "人参", "ginseng", "rénshēn"),
            Chapter("Decocting Medicine", "煎药", "煎药", "decoct herbs", "jiān yào"),
            Chapter("Patent Medicines", "中成药", "中成药", "patent TCM medicine", "zhōng chéng yào"),
            Chapter("Food as Medicine", "食疗", "食疗", "food therapy", "shí liáo"),
            Chapter("Integrated Medicine", "中西医结合", "中西医", "Chinese + Western medicine", "zhōng xī yī"),
            Chapter("TCM Beauty", "中医美容", "美容", "beauty / cosmetology", "měiróng"),
            Chapter("Tai Chi and Qigong", "太极气功", "太极", "tai chi", "tàijí"),
            Chapter("Seasonal Wellness", "四季养生", "养生", "wellness / health cultivation", "yǎngshēng"),
            Chapter("Foreigners Try TCM", "外国人看中医", "体验", "experience", "tǐyàn"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 82: Chinese Calligraphy
    # -----------------------------------------------------------------
    Book(
        number=82,
        slug="Calligraphy",
        title_en="Chinese Calligraphy",
        subtitle_zh="书法语言：笔墨之间的文化密码",
        color="#212121",
        part_titles=[
            ("Getting Started", "入门"),
            ("Script Styles", "字体风格"),
            ("Masters and Classics", "名家与经典"),
            ("Practice and Culture", "练习与文化"),
            ("Appreciation and Beyond", "欣赏与延伸"),
        ],
        chapters=[
            Chapter("Why Learn Calligraphy", "为什么学书法", "书法", "calligraphy", "shūfǎ"),
            Chapter("Four Treasures of the Study", "文房四宝", "文房四宝", "four treasures of study", "wén fáng sì bǎo"),
            Chapter("Brush Grip Posture", "执笔姿势", "执笔", "brush grip", "zhí bǐ"),
            Chapter("Basic Strokes", "基本笔画", "笔画", "stroke", "bǐhuà"),
            Chapter("The Character Yong", "永字八法", "永字八法", "Eight Methods of Yong", "yǒng zì bā fǎ"),
            Chapter("Regular Script", "楷书", "楷书", "regular script", "kǎishū"),
            Chapter("Running Script", "行书", "行书", "running script", "xíngshū"),
            Chapter("Cursive Script", "草书", "草书", "cursive script", "cǎoshū"),
            Chapter("Clerical Script", "隶书", "隶书", "clerical script", "lìshū"),
            Chapter("Seal Script", "篆书", "篆书", "seal script", "zhuànshū"),
            Chapter("Wang Xizhi", "王羲之", "王羲之", "Wang Xizhi (master)", "Wáng Xīzhī"),
            Chapter("Yan Zhenqing", "颜真卿", "颜真卿", "Yan Zhenqing (master)", "Yán Zhēnqīng"),
            Chapter("Su Shi's Calligraphy", "苏轼书法", "苏轼", "Su Shi (poet-calligrapher)", "Sū Shì"),
            Chapter("Stele vs. Copybook", "碑和帖", "碑帖", "stele and copybook", "bēi tiè"),
            Chapter("Contemporary Masters", "当代书法家", "当代", "contemporary", "dāngdài"),
            Chapter("Calligraphy Class in China", "中国书法课", "老师", "teacher", "lǎoshī"),
            Chapter("Copying Masterworks", "临帖方法", "临帖", "copy a masterwork", "lín tiè"),
            Chapter("Exhibition Appreciation", "书法展览", "展览", "exhibition", "zhǎnlǎn"),
            Chapter("Calligraphy Competitions", "书法比赛", "比赛", "competition", "bǐsài"),
            Chapter("Gifting Calligraphy", "书法礼品", "题字", "inscribe characters", "tí zì"),
            Chapter("Reading Calligraphy Works", "读懂作品", "落款", "signature/inscription", "luòkuǎn"),
            Chapter("Calligraphy and Poetry", "书法与诗词", "诗词", "poetry", "shīcí"),
            Chapter("Modern Calligraphy Art", "现代书法", "现代", "modern", "xiàndài"),
            Chapter("Digital Calligraphy", "数字书法", "数字", "digital", "shùzì"),
            Chapter("Foreigners Calligraphy Journey", "外国人书法之旅", "爱好", "hobby / pursuit", "àihào"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 83: Paper Cutting & Folk Art
    # -----------------------------------------------------------------
    Book(
        number=83,
        slug="FolkArt",
        title_en="Paper Cutting Folk Art",
        subtitle_zh="剪纸与民间艺术：手工中国的语言",
        color="#880E4F",
        part_titles=[
            ("Paper Cutting", "剪纸艺术"),
            ("New Year Art", "年画与门神"),
            ("Embroidery and Textile", "刺绣与纺织"),
            ("Clay and Sculpture", "泥塑与雕刻"),
            ("Kites and Puppets", "风筝与皮影"),
        ],
        chapters=[
            Chapter("Origins of Paper Cutting", "剪纸的起源", "剪纸", "paper cutting", "jiǎn zhǐ"),
            Chapter("Tools and Materials", "工具与材料", "剪刀", "scissors", "jiǎndāo"),
            Chapter("Basic Patterns", "基本图案", "窗花", "window paper-cut", "chuānghuā"),
            Chapter("Learning from Artisans", "跟艺人学", "艺人", "folk artist", "yìrén"),
            Chapter("Paper Cuts as Gifts", "剪纸礼物", "礼物", "gift", "lǐwù"),
            Chapter("New Year Woodblock Prints", "年画传统", "年画", "New Year painting", "niánhuà"),
            Chapter("Door God Culture", "门神文化", "门神", "door god", "ménshén"),
            Chapter("Spring Couplets", "春联创作", "春联", "Spring Festival couplet", "chūnlián"),
            Chapter("The Fu Character", "福字艺术", "福", "fortune / good luck", "fú"),
            Chapter("Buying New Year Art", "购买年画", "集市", "market fair", "jíshì"),
            Chapter("Four Famous Embroideries", "四大名绣", "刺绣", "embroidery", "cìxiù"),
            Chapter("Learning Embroidery", "学刺绣", "针法", "stitch technique", "zhēn fǎ"),
            Chapter("Brocade and Silk", "织锦缎", "丝绸", "silk", "sīchóu"),
            Chapter("Indigo and Tie-Dye", "蓝染扎染", "扎染", "tie-dye", "zā rǎn"),
            Chapter("Buying Handmade Embroidery", "购买刺绣", "手工", "handmade", "shǒugōng"),
            Chapter("Wuxi Clay Figures", "无锡惠山泥人", "泥人", "clay figurine", "nírén"),
            Chapter("Chaozhou Wood Carving", "潮州木雕", "木雕", "wood carving", "mùdiāo"),
            Chapter("Ceramics Hand Throwing", "陶瓷手工", "拉坯", "throwing pottery", "lā pī"),
            Chapter("Stone Carving", "石雕", "石雕", "stone carving", "shídiāo"),
            Chapter("Interviewing Craftsmen", "采访艺人", "非遗", "intangible heritage", "fēi yí"),
            Chapter("Weifang Kites", "潍坊风筝", "风筝", "kite", "fēngzheng"),
            Chapter("Flying Kites in the Park", "公园放风筝", "放风筝", "fly a kite", "fàng fēngzheng"),
            Chapter("Shaanxi Shadow Puppets", "陕西皮影", "皮影", "shadow puppet", "píyǐng"),
            Chapter("Quanzhou Puppetry", "泉州木偶", "木偶", "puppet", "mù'ǒu"),
            Chapter("Craft Tourism", "手工艺旅游", "旅游", "tourism", "lǚyóu"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 84: Kung Fu & Martial Arts
    # -----------------------------------------------------------------
    Book(
        number=84,
        slug="KungFu",
        title_en="Kung Fu Martial Arts",
        subtitle_zh="功夫语言：武术的精神与实践",
        color="#B71C1C",
        part_titles=[
            ("Philosophy of Kung Fu", "功夫哲学"),
            ("Styles and Techniques", "门派与技法"),
            ("Training Life", "训练生活"),
            ("Competition and Performance", "比赛与表演"),
            ("Kung Fu in Culture", "功夫文化"),
        ],
        chapters=[
            Chapter("Meaning of Kung Fu", "功夫的含义", "功夫", "kung fu", "gōngfu"),
            Chapter("Internal and External Styles", "内家和外家", "内家", "internal style", "nèi jiā"),
            Chapter("Master-Disciple Relation", "师徒关系", "师父", "master / teacher", "shīfu"),
            Chapter("Martial Virtue", "武德", "武德", "martial virtue", "wǔ dé"),
            Chapter("Patience and Persistence", "忍耐与坚持", "坚持", "persevere", "jiānchí"),
            Chapter("Shaolin Kung Fu", "少林功夫", "少林", "Shaolin", "Shàolín"),
            Chapter("Tai Chi", "太极拳", "太极拳", "tai chi", "tàijí quán"),
            Chapter("Wing Chun", "咏春拳", "咏春", "Wing Chun", "yǒngchūn"),
            Chapter("Wudang Daoist Arts", "武当道家", "武当", "Wudang", "Wǔdāng"),
            Chapter("Modern Sanda", "散打", "散打", "Sanda (fighting)", "sǎndǎ"),
            Chapter("Joining a Dojo", "武馆文化", "武馆", "martial arts school", "wǔguǎn"),
            Chapter("Warmup and Basics", "热身与基本功", "基本功", "fundamentals", "jīběn gōng"),
            Chapter("Forms Practice", "套路练习", "套路", "form / routine", "tàolù"),
            Chapter("Sparring Safety", "对练与实战", "对练", "sparring", "duì liàn"),
            Chapter("Martial Injury Care", "跌打损伤", "跌打", "martial injury care", "diē dǎ"),
            Chapter("Entering Competitions", "武术比赛", "比赛", "competition", "bǐsài"),
            Chapter("Judging Criteria", "裁判评分", "裁判", "referee / judge", "cáipàn"),
            Chapter("Martial Arts Shows", "武术表演", "表演", "performance", "biǎoyǎn"),
            Chapter("Kung Fu Tourism", "功夫旅游", "少林寺", "Shaolin Temple", "Shàolín sì"),
            Chapter("Martial Arts Festivals", "武林大会", "武林", "martial arts world", "wǔlín"),
            Chapter("Kung Fu Film Legacy", "功夫电影", "李小龙", "Bruce Lee", "Lǐ Xiǎolóng"),
            Chapter("Kung Fu Philosophy", "功夫哲学", "哲学", "philosophy", "zhéxué"),
            Chapter("Female Martial Artists", "女性武术家", "女武术家", "female martial artist", "nǚ wǔshù jiā"),
            Chapter("Modern Wushu", "现代武术", "武术", "wushu", "wǔshù"),
            Chapter("Learning Kung Fu as Foreigner", "外国人学功夫", "外国人", "foreigner", "wàiguó rén"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 85: Traditional Instruments
    # -----------------------------------------------------------------
    Book(
        number=85,
        slug="Instruments",
        title_en="Chinese Traditional Instruments",
        subtitle_zh="传统乐器：琴声里的中国",
        color="#4A148C",
        part_titles=[
            ("String Instruments", "弦乐器"),
            ("Wind Instruments", "吹管乐器"),
            ("Percussion", "打击乐器"),
            ("Learning and Performing", "学习与表演"),
            ("Cultural Context", "文化语境"),
        ],
        chapters=[
            Chapter("Guqin", "古琴", "古琴", "guqin (seven-string)", "gǔqín"),
            Chapter("Guzheng", "古筝", "古筝", "guzheng (zither)", "gǔzhēng"),
            Chapter("Erhu", "二胡", "二胡", "erhu (two-string fiddle)", "èrhú"),
            Chapter("Pipa", "琵琶", "琵琶", "pipa (lute)", "pípá"),
            Chapter("Ruan and Yueqin", "阮与月琴", "阮", "ruan lute", "ruǎn"),
            Chapter("Chinese Flute", "竹笛", "竹笛", "bamboo flute (dizi)", "zhú dí"),
            Chapter("Xiao Flute", "箫", "箫", "xiao (vertical flute)", "xiāo"),
            Chapter("Suona Horn", "唢呐", "唢呐", "suona (double-reed horn)", "suǒnà"),
            Chapter("Hulusi", "葫芦丝", "葫芦丝", "hulusi (gourd flute)", "húlusī"),
            Chapter("Guan and Sheng", "管与笙", "笙", "sheng (mouth organ)", "shēng"),
            Chapter("Drum Culture", "鼓文化", "鼓", "drum", "gǔ"),
            Chapter("Bianzhong Bells", "编钟", "编钟", "bianzhong bells", "biānzhōng"),
            Chapter("Gongs and Cymbals", "锣钹", "锣", "gong", "luó"),
            Chapter("Muyu and Qing", "木鱼与磬", "木鱼", "wooden fish percussion", "mùyú"),
            Chapter("Percussion Ensembles", "打击乐组合", "打击乐", "percussion music", "dǎjī yuè"),
            Chapter("Finding a Teacher", "找老师", "拜师", "take on as teacher", "bài shī"),
            Chapter("First Lesson", "第一节课", "课", "class", "kè"),
            Chapter("Musical Notation", "乐谱", "乐谱", "musical score", "yuèpǔ"),
            Chapter("Concert Etiquette", "音乐会礼仪", "音乐会", "concert", "yīnyuè huì"),
            Chapter("Joining an Orchestra", "加入乐团", "乐团", "orchestra / ensemble", "yuètuán"),
            Chapter("Instruments in Poetry", "诗词乐器", "意象", "imagery", "yìxiàng"),
            Chapter("Opera Accompaniment", "戏曲配乐", "戏曲", "Chinese opera", "xìqǔ"),
            Chapter("Regional Folk Music", "民间音乐", "民乐", "folk music", "mínyuè"),
            Chapter("Instrument Making", "乐器制作", "制琴师", "instrument maker", "zhì qín shī"),
            Chapter("Foreigners Learning", "外国人学乐器", "入门", "entry / beginner", "rùmén"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 86: Hanfu
    # -----------------------------------------------------------------
    Book(
        number=86,
        slug="Hanfu",
        title_en="Hanfu Traditional Fashion",
        subtitle_zh="汉服文化：穿越历史的语言",
        color="#AD1457",
        part_titles=[
            ("What is Hanfu", "汉服是什么"),
            ("Styles and Components", "款式与构成"),
            ("Shopping and Making", "购买与制作"),
            ("Wearing and Events", "穿着与活动"),
            ("Cultural Depth", "文化深度"),
        ],
        chapters=[
            Chapter("Defining Hanfu", "汉服定义", "汉服", "Hanfu (Han clothing)", "hànfú"),
            Chapter("Historical Forms", "历史形制", "形制", "form / style", "xíngzhì"),
            Chapter("Hanfu vs. Kimono vs. Qipao", "汉服和服旗袍", "旗袍", "qipao", "qípáo"),
            Chapter("The Hanfu Revival Movement", "汉服复兴", "复兴", "revival", "fùxīng"),
            Chapter("Hanfu Community Culture", "汉服圈文化", "汉服圈", "Hanfu community", "hànfú quān"),
            Chapter("Top and Skirt", "上衣下裳", "上衣", "upper garment", "shàngyī"),
            Chapter("Shenyi Robe", "深衣", "深衣", "shenyi robe", "shēnyī"),
            Chapter("Ao and Beizi", "袄裙与褙子", "袄裙", "ao skirt", "ǎo qún"),
            Chapter("Hair Ornaments", "配饰系统", "发簪", "hairpin", "fà zān"),
            Chapter("Fabrics and Craft", "面料与工艺", "面料", "fabric", "miànliào"),
            Chapter("Physical Hanfu Stores", "汉服实体店", "实体店", "physical store", "shítǐ diàn"),
            Chapter("Online Hanfu Shopping", "网购汉服", "网购", "online shopping", "wǎnggòu"),
            Chapter("Custom-Made Hanfu", "定制汉服", "定制", "custom made", "dìngzhì"),
            Chapter("Second-Hand Hanfu", "二手汉服", "二手", "second-hand", "èrshǒu"),
            Chapter("Making Your Own Hanfu", "自制汉服", "自制", "self-made", "zìzhì"),
            Chapter("Wearing Hanfu Out", "汉服出行", "出行", "going out", "chūxíng"),
            Chapter("Hanfu Photography", "汉服摄影", "写真", "photo shoot", "xiězhēn"),
            Chapter("Hanfu Festivals", "汉服活动", "花朝节", "Flower Festival", "huācháo jié"),
            Chapter("Traditional Etiquette", "汉服礼仪", "礼仪", "etiquette", "lǐyí"),
            Chapter("Hanfu Celebration Events", "汉服节", "文化节", "culture festival", "wénhuà jié"),
            Chapter("Hanfu and Identity", "汉服与认同", "认同", "identity", "rèntóng"),
            Chapter("Hanfu in Media", "汉服与影视", "古装剧", "historical drama", "gǔzhuāng jù"),
            Chapter("Ethnic Minority Dress", "少数民族服饰", "少数民族", "ethnic minority", "shǎoshù mínzú"),
            Chapter("Qipao Story", "旗袍的故事", "民国", "Republic era", "Mínguó"),
            Chapter("Foreigners Wearing Hanfu", "外国人穿汉服", "文化欣赏", "cultural appreciation", "wénhuà xīnshǎng"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 87: Guochao National Pride
    # -----------------------------------------------------------------
    Book(
        number=87,
        slug="Guochao",
        title_en="Guochao National Pride",
        subtitle_zh="国潮崛起：新国货的语言与美学",
        color="#E65100",
        part_titles=[
            ("What is Guochao", "国潮是什么"),
            ("Fashion and Lifestyle", "时尚生活"),
            ("Food and Beverage", "餐饮国潮"),
            ("Tech and Products", "科技国货"),
            ("Culture and Criticism", "文化与批评"),
        ],
        chapters=[
            Chapter("Defining Guochao", "国潮定义", "国潮", "national trend (guochao)", "guó cháo"),
            Chapter("Historical Arc", "历史脉络", "国货", "national product", "guóhuò"),
            Chapter("Guochao Consumer Profile", "消费者画像", "消费者", "consumer", "xiāofèi zhě"),
            Chapter("Guochao vs. Counterfeits", "国潮与山寨", "山寨", "knockoff", "shānzhài"),
            Chapter("Guochao Economic Data", "国潮经济数据", "数据", "data / statistics", "shùjù"),
            Chapter("Li-Ning and Anta", "李宁与安踏", "李宁", "Li-Ning brand", "Lǐníng"),
            Chapter("Florasis Beauty", "花西子", "花西子", "Florasis brand", "Huāxīzi"),
            Chapter("Chayan Yuese Tea", "茶颜悦色", "茶颜悦色", "Chayan Yuese brand", "Chá yán yuè sè"),
            Chapter("Pop Mart", "泡泡玛特", "泡泡玛特", "Pop Mart", "Pàopao mǎtè"),
            Chapter("Guochao Design", "国潮设计", "设计", "design", "shèjì"),
            Chapter("Time-Honored Reinventions", "老字号新玩法", "老字号", "time-honored brand", "lǎo zìhào"),
            Chapter("New Chinese Fast Food", "中式快餐", "快餐", "fast food", "kuàicān"),
            Chapter("New Chinese Tea Shops", "新中式茶馆", "喜茶", "Heytea brand", "Xǐ chá"),
            Chapter("Chinese Spirits Rebrand", "白酒年轻化", "白酒", "baijiu spirit", "báijiǔ"),
            Chapter("Guochao Snacks", "国潮零食", "零食", "snack", "língshí"),
            Chapter("Huawei Narrative", "华为叙事", "华为", "Huawei", "Huáwéi"),
            Chapter("DJI Drones", "大疆无人机", "大疆", "DJI brand", "Dàjiāng"),
            Chapter("Xiaomi Ecosystem", "小米生态", "小米", "Xiaomi brand", "Xiǎomǐ"),
            Chapter("BYD Rising", "比亚迪崛起", "比亚迪", "BYD", "Bǐyàdí"),
            Chapter("Domestic Smartphones", "国产手机", "国产", "domestically made", "guóchǎn"),
            Chapter("Guochao and Nationalism", "国潮与民族主义", "民族主义", "nationalism", "mínzú zhǔyì"),
            Chapter("Guochao Going Global", "海外国潮", "出海", "go abroad", "chū hǎi"),
            Chapter("Critiquing Guochao", "批评国潮", "批评", "criticism", "pīpíng"),
            Chapter("Designers' Perspective", "设计师视角", "设计师", "designer", "shèjì shī"),
            Chapter("Foreigners on Guochao", "外国人看国潮", "观察", "observe", "guānchá"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 88: ACG Culture
    # -----------------------------------------------------------------
    Book(
        number=88,
        slug="ACG",
        title_en="Anime Cosplay ACG Culture",
        subtitle_zh="二次元语言：ACG文化全图谱",
        color="#1A237E",
        part_titles=[
            ("ACG Basics", "ACG基础"),
            ("Chinese Animation", "国产动画"),
            ("Cosplay", "角色扮演"),
            ("Fandom Culture", "粉丝文化"),
            ("Industry and Future", "产业与未来"),
        ],
        chapters=[
            Chapter("Otaku Culture in China", "中国二次元", "二次元", "ACG / 2D world", "èr cì yuán"),
            Chapter("Bilibili Culture", "B站文化", "B站", "Bilibili", "B zhàn"),
            Chapter("Anime Vocabulary", "动漫词汇", "番剧", "anime series", "fān jù"),
            Chapter("Manga Language", "漫画语言", "国漫", "Chinese manga", "guó màn"),
            Chapter("ACG Community Roles", "ACG圈子", "圈子", "circle / scene", "quānzi"),
            Chapter("Rise of Guoman", "国漫崛起", "哪吒", "Ne Zha", "Nézhā"),
            Chapter("Guofeng Animation", "国风动画", "国风", "national style", "guófēng"),
            Chapter("Online Anime Viewing", "追番文化", "追番", "watch ongoing anime", "zhuī fān"),
            Chapter("Anime Criticism", "动漫批评", "评价", "evaluation", "píngjià"),
            Chapter("Chinese Voice Acting", "动漫配音", "配音", "voice acting", "pèiyīn"),
            Chapter("Cosplay Culture", "Cosplay文化", "Cosplay", "cosplay", "Cosplay"),
            Chapter("Comic Conventions", "漫展参与", "漫展", "comic convention", "mànzhǎn"),
            Chapter("Cosplay Photography", "拍摄Cosplay", "摄影师", "photographer", "shèyǐng shī"),
            Chapter("Costume Making", "制作服装", "服装", "costume", "fúzhuāng"),
            Chapter("Cosplay Competitions", "Cos比赛", "比赛", "competition", "bǐsài"),
            Chapter("Fan Creation", "同人创作", "同人", "fan work / doujin", "tóngrén"),
            Chapter("Sweet vs. Tragic Plots", "虐与甜", "甜", "sweet romance", "tián"),
            Chapter("Shipping Culture", "磕CP", "CP", "couple pairing", "CP"),
            Chapter("Fandom Activism", "声讨与控评", "控评", "review control", "kòng píng"),
            Chapter("IP Ranking Campaigns", "打榜应援", "应援", "support / cheer", "yìngyuán"),
            Chapter("Domestic Mobile Games", "国产手游", "原神", "Genshin Impact", "Yuán shén"),
            Chapter("Virtual Idols", "虚拟偶像", "洛天依", "Luo Tianyi", "Luò Tiānyī"),
            Chapter("Learning Chinese via Anime", "动漫学中文", "学中文", "learn Chinese", "xué Zhōngwén"),
            Chapter("Chinese Anime Going Global", "国漫出海", "出海", "go abroad", "chū hǎi"),
            Chapter("Foreign ACG Fans", "外国二次元爱好者", "爱好者", "enthusiast", "àihào zhě"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 89: Street Culture
    # -----------------------------------------------------------------
    Book(
        number=89,
        slug="StreetCulture",
        title_en="Street Culture Skateboarding",
        subtitle_zh="街头文化：从滑板到涂鸦的中文",
        color="#263238",
        part_titles=[
            ("Skateboarding", "滑板"),
            ("Street Dance", "街舞"),
            ("Graffiti and Urban Art", "涂鸦与城市艺术"),
            ("Streetwear Fashion", "潮流穿搭"),
            ("Community and Identity", "社群与身份"),
        ],
        chapters=[
            Chapter("Chinese Skate Scene", "中国滑板圈", "滑板", "skateboard", "huábǎn"),
            Chapter("Skate Vocabulary", "滑板术语", "动作", "trick / move", "dòngzuò"),
            Chapter("Skate Parks", "滑板公园", "滑板场", "skatepark", "huábǎn chǎng"),
            Chapter("Skate Brands", "滑板品牌", "品牌", "brand", "pǐnpái"),
            Chapter("Street vs. Bowl", "街头与碗池", "街头", "street", "jiētóu"),
            Chapter("Breaking and Popping", "Breaking与Popping", "街舞", "street dance", "jiē wǔ"),
            Chapter("Reality Show Impact", "街舞综艺", "综艺", "variety show", "zōngyì"),
            Chapter("Battle Culture", "Battle文化", "对决", "duel / battle", "duìjué"),
            Chapter("Dance Crews", "舞团文化", "舞团", "dance crew", "wǔtuán"),
            Chapter("Choreography Language", "编舞语言", "编舞", "choreography", "biān wǔ"),
            Chapter("Graffiti in China", "涂鸦在中国", "涂鸦", "graffiti", "túyā"),
            Chapter("Legal Walls", "合法墙", "合法", "legal", "héfǎ"),
            Chapter("Graffiti Terms", "涂鸦词汇", "tag", "tag (signature)", "tag"),
            Chapter("Urban Art Festivals", "城市艺术节", "艺术节", "art festival", "yìshù jié"),
            Chapter("Street Photography", "街头摄影", "拍摄", "shoot / photograph", "pāishè"),
            Chapter("Streetwear Brands", "潮牌文化", "潮牌", "streetwear brand", "cháo pái"),
            Chapter("Sneaker Culture", "球鞋文化", "炒鞋", "sneaker flipping", "chǎo xié"),
            Chapter("OOTD Sharing", "穿搭分享", "OOTD", "outfit of the day", "OOTD"),
            Chapter("Second-Hand Trading", "二手潮品", "得物", "Dewu app", "Déwù"),
            Chapter("Domestic Streetwear", "国产潮牌", "国潮", "national trend", "guó cháo"),
            Chapter("Mainstream Crossover", "亚文化主流化", "亚文化", "subculture", "yà wénhuà"),
            Chapter("Joining the Scene", "圈子进入", "进入", "enter / join", "jìnrù"),
            Chapter("Cultural Appropriation Talk", "文化挪用", "挪用", "appropriation", "nuóyòng"),
            Chapter("Starting a Skate Shop", "开滑板店", "开店", "open a store", "kāi diàn"),
            Chapter("City Differences", "城市差异", "城市", "city", "chéngshì"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 90: Coffee, Tea & New Beverage
    # -----------------------------------------------------------------
    Book(
        number=90,
        slug="CoffeeTea",
        title_en="Coffee Tea New Beverage",
        subtitle_zh="咖啡茶饮：第三空间的语言",
        color="#3E2723",
        part_titles=[
            ("Coffee Culture", "咖啡文化"),
            ("New Tea Beverages", "新式茶饮"),
            ("Traditional Tea Modern Way", "传统茶现代喝"),
            ("Third Places", "第三空间"),
            ("Making and Sharing", "自制与分享"),
        ],
        chapters=[
            Chapter("Coffee Market Competition", "中国咖啡市场", "瑞幸", "Luckin Coffee", "Ruìxìng"),
            Chapter("Specialty Coffee Terms", "精品咖啡语言", "手冲", "pour-over", "shǒu chōng"),
            Chapter("Coffee Ordering", "咖啡点单", "拿铁", "latte", "nátiě"),
            Chapter("Working From Cafés", "咖啡馆办公", "咖啡馆", "café", "kāfēi guǎn"),
            Chapter("Coffee Meetings", "咖啡社交", "约咖啡", "grab a coffee", "yuē kāfēi"),
            Chapter("Milk Tea Customization", "奶茶定制", "奶茶", "milk tea", "nǎichá"),
            Chapter("Heytea Language", "喜茶语言", "喜茶", "Heytea brand", "Xǐ chá"),
            Chapter("Guming and Mixue", "古茗与蜜雪", "蜜雪冰城", "Mixue ice city", "Mìxuě bīng chéng"),
            Chapter("Fruit Tea Era", "水果茶时代", "水果茶", "fruit tea", "shuǐguǒ chá"),
            Chapter("Seasonal Limited Drinks", "季节限定", "限定", "limited edition", "xiàndìng"),
            Chapter("New Chinese Tea", "新中式茶饮", "新中式", "new Chinese style", "xīn zhōng shì"),
            Chapter("Tea Bags and Cold Brew", "袋泡与冷泡", "袋泡", "tea bag", "dài pào"),
            Chapter("Sparkling Tea", "气泡茶", "气泡茶", "sparkling tea", "qìpào chá"),
            Chapter("Tea Cocktails", "茶鸡尾酒", "鸡尾酒", "cocktail", "jīwěi jiǔ"),
            Chapter("Wellness Tea", "养生茶", "养生", "wellness", "yǎngshēng"),
            Chapter("Third Place Concept", "第三空间", "第三空间", "third place", "dì sān kōngjiān"),
            Chapter("Indie Cafés", "独立咖啡馆", "独立", "independent", "dúlì"),
            Chapter("Bookstore Cafés", "书店咖啡馆", "书店", "bookstore", "shūdiàn"),
            Chapter("Co-Working Spaces", "共享办公", "共享", "shared", "gòngxiǎng"),
            Chapter("Outdoor Coffee Camping", "露营咖啡", "露营", "camping", "lùyíng"),
            Chapter("Home Coffee", "家庭咖啡", "咖啡机", "coffee machine", "kāfēi jī"),
            Chapter("Homemade Milk Tea", "自制奶茶", "自制", "homemade", "zìzhì"),
            Chapter("Coffee Content Creators", "咖啡博主", "博主", "blogger", "bózhǔ"),
            Chapter("Coffee Cupping Events", "咖啡杯测", "杯测", "cupping", "bēi cè"),
            Chapter("Foreign Coffee Culture Comparison", "中外咖啡对比", "对比", "comparison", "duìbǐ"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 91: Chinese vs Western Culture
    # -----------------------------------------------------------------
    Book(
        number=91,
        slug="CultureCompare",
        title_en="Chinese vs Western Culture",
        subtitle_zh="文化对比：中西碰撞的语言",
        color="#1B5E20",
        part_titles=[
            ("Communication Styles", "沟通风格"),
            ("Values and Worldview", "价值观与世界观"),
            ("Family and Society", "家庭与社会"),
            ("Hot Topics", "热点议题"),
            ("Finding Common Ground", "寻找共同点"),
        ],
        chapters=[
            Chapter("Direct vs. Indirect", "直接与迂回", "迂回", "indirect", "yūhuí"),
            Chapter("Face and Candor", "面子与坦诚", "面子", "face (mianzi)", "miànzi"),
            Chapter("Meaning of Silence", "沉默的含义", "沉默", "silence", "chénmò"),
            Chapter("Humor Boundaries", "幽默边界", "幽默", "humor", "yōumò"),
            Chapter("Apology Culture", "道歉文化", "道歉", "apology", "dàoqiàn"),
            Chapter("Individual vs. Collective", "个人和集体", "集体", "collective", "jítǐ"),
            Chapter("Relationships vs. Rules", "关系与规则", "关系", "guanxi / relations", "guānxi"),
            Chapter("Time Perception", "时间观念", "守时", "punctuality", "shǒu shí"),
            Chapter("Defining Success", "成功定义", "成功", "success", "chénggōng"),
            Chapter("Religion and Secular", "宗教与世俗", "世俗", "secular", "shìsú"),
            Chapter("Family Duties", "家庭责任", "责任", "responsibility", "zérèn"),
            Chapter("Marriage and Freedom", "婚姻与自由", "自由", "freedom", "zìyóu"),
            Chapter("Work vs. Leisure", "工作与休闲", "休闲", "leisure", "xiūxián"),
            Chapter("Privacy Boundaries", "公私边界", "隐私", "privacy", "yǐnsī"),
            Chapter("Sense of Community", "社区感", "社区", "community", "shèqū"),
            Chapter("Discussing Politics", "讨论政治", "政治", "politics", "zhèngzhì"),
            Chapter("Media and Information", "媒体与信息", "信息", "information", "xìnxī"),
            Chapter("Environmental Views", "环境观念", "环保", "environmental protection", "huánbǎo"),
            Chapter("Education Philosophy", "教育哲学", "虎妈", "tiger mom", "hǔ mā"),
            Chapter("Food Philosophy", "饮食哲学", "饮食", "food / diet", "yǐnshí"),
            Chapter("Non-Judgmental Language", "不评判的语言", "评判", "judge", "píngpàn"),
            Chapter("Cultural Relativism", "文化相对主义", "相对主义", "relativism", "xiāngduì zhǔyì"),
            Chapter("Blended Culture", "混血文化", "混血", "mixed heritage", "hùnxuè"),
            Chapter("Global Citizenship", "全球公民", "全球", "global", "quánqiú"),
            Chapter("Cultural Bridges", "文化桥梁", "桥梁", "bridge", "qiáoliáng"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 92: Foreigners in China
    # -----------------------------------------------------------------
    Book(
        number=92,
        slug="ForeignersChina",
        title_en="Foreigners in China",
        subtitle_zh="老外在中国：真实生活的语言指南",
        color="#0D47A1",
        part_titles=[
            ("Legal and Administrative", "证件与行政"),
            ("Housing and Neighborhood", "住房与社区"),
            ("Family Life", "家庭生活"),
            ("Social Integration", "社会融入"),
            ("Long-term Commitment", "长期承诺"),
        ],
        chapters=[
            Chapter("Visa Types", "签证类型", "签证", "visa", "qiānzhèng"),
            Chapter("Residence Permits", "居留许可", "居留", "residence", "jūliú"),
            Chapter("Notarization", "公证与翻译", "公证", "notarization", "gōngzhèng"),
            Chapter("Emergency Contacts", "紧急联系", "领事馆", "consulate", "lǐngshì guǎn"),
            Chapter("Foreigner Rights", "外国人权益", "权益", "rights and interests", "quányì"),
            Chapter("Finding an Apartment", "找房子", "租房", "rent a place", "zū fáng"),
            Chapter("Signing Lease", "签租约", "合同", "contract", "hétóng"),
            Chapter("Landlord Relations", "和房东相处", "房东", "landlord", "fángdōng"),
            Chapter("Property Management", "物业管理", "物业", "property mgmt", "wùyè"),
            Chapter("Joining Your Community", "融入小区", "邻居", "neighbor", "línjū"),
            Chapter("Foreign Kids in School", "子女入学", "入学", "enrol school", "rù xué"),
            Chapter("International vs. Local School", "国际学校和本地学校", "国际学校", "international school", "guójì xuéxiào"),
            Chapter("Family Doctor", "家庭医生", "医生", "doctor", "yīshēng"),
            Chapter("Hiring a Nanny", "保姆与育儿嫂", "保姆", "nanny", "bǎomǔ"),
            Chapter("Foreign Parent Groups", "外国家长圈", "家长", "parent", "jiāzhǎng"),
            Chapter("Chinese Friendship Circle", "中国朋友圈", "朋友圈", "friend circle", "péngyǒu quān"),
            Chapter("Community Activities", "社区活动", "志愿者", "volunteer", "zhìyuàn zhě"),
            Chapter("Culture Courses", "文化课程", "课程", "course", "kèchéng"),
            Chapter("Sport Communities", "体育社群", "社群", "community", "shèqún"),
            Chapter("Religious Communities", "宗教活动", "宗教", "religion", "zōngjiào"),
            Chapter("Permanent Residence", "永久居留权", "绿卡", "green card", "lǜkǎ"),
            Chapter("Marrying a Chinese", "涉外婚姻", "婚姻", "marriage", "hūnyīn"),
            Chapter("Filing Taxes", "纳税", "个税", "personal income tax", "gè shuì"),
            Chapter("Retiring in China", "在华养老", "养老", "retirement", "yǎnglǎo"),
            Chapter("Do I Belong Here?", "归属感探索", "归属感", "sense of belonging", "guīshǔ gǎn"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 93: Chinese Abroad
    # -----------------------------------------------------------------
    Book(
        number=93,
        slug="ChineseAbroad",
        title_en="Chinese Abroad",
        subtitle_zh="海外华人：离散与归属的语言",
        color="#4E342E",
        part_titles=[
            ("Chinese Diaspora", "华人离散史"),
            ("Language Preservation", "语言保存"),
            ("Cultural Identity", "文化认同"),
            ("Modern Connections", "现代联系"),
            ("Looking Forward", "向前看"),
        ],
        chapters=[
            Chapter("Migration History", "华人移民史", "移民", "immigration", "yímín"),
            Chapter("Origin of Chinatowns", "唐人街的诞生", "唐人街", "Chinatown", "Tángrén jiē"),
            Chapter("Southeast Asian Chinese", "南洋华人", "南洋", "South Seas (SE Asia)", "Nányáng"),
            Chapter("American and European Chinese", "欧美华人", "华侨", "overseas Chinese", "huáqiáo"),
            Chapter("New Wave Migrants", "新移民潮", "新移民", "new immigrants", "xīn yímín"),
            Chapter("Chinese Schools Abroad", "海外中文学校", "中文学校", "Chinese school", "Zhōngwén xuéxiào"),
            Chapter("Dialect Preservation", "方言保存", "方言", "dialect", "fāngyán"),
            Chapter("Language Mixing", "语言混合", "混合", "blend / mix", "hùnhé"),
            Chapter("Chinglish", "中英夹杂", "夹杂", "mixed in", "jiāzá"),
            Chapter("Third-Generation Chinese", "第三代的中文", "第三代", "third generation", "dì sān dài"),
            Chapter("ABC Identity", "香蕉人", "香蕉人", "banana (ABC)", "xiāngjiāo rén"),
            Chapter("Returning to China", "回到中国", "回国", "return home", "huí guó"),
            Chapter("Dual Identity", "双重归属", "双重", "dual", "shuāngchóng"),
            Chapter("Festivals Abroad", "海外节日", "春节", "Spring Festival", "Chūnjié"),
            Chapter("Chinese Food Abroad", "海外中餐", "中餐", "Chinese cuisine", "zhōngcān"),
            Chapter("WeChat With Parents", "微信与父母", "微信", "WeChat", "Wēixìn"),
            Chapter("Raising Bilingual Kids", "双语子女", "双语", "bilingual", "shuāng yǔ"),
            Chapter("Family Visits", "回国探亲", "探亲", "visit family", "tànqīn"),
            Chapter("Remittances", "汇款投资", "汇款", "remittance", "huì kuǎn"),
            Chapter("Overseas Chinese Media", "海外华人媒体", "媒体", "media", "méitǐ"),
            Chapter("New Generation Chinese", "新一代华人", "Z世代", "Gen Z", "Z shìdài"),
            Chapter("Political Diversity", "政治多元", "多元", "diverse", "duōyuán"),
            Chapter("Cultural Ambassadors", "文化大使", "大使", "ambassador", "dàshǐ"),
            Chapter("Roots Journey", "寻根之旅", "寻根", "seek roots", "xún gēn"),
            Chapter("Foreigner-Chinese Connection", "跨背景学习", "共同体", "community", "gòngtóng tǐ"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 94: Cultural Misunderstandings
    # -----------------------------------------------------------------
    Book(
        number=94,
        slug="Misunderstandings",
        title_en="Cultural Misunderstandings",
        subtitle_zh="文化误区：那些让外国人崩溃的中文时刻",
        color="#F57F17",
        part_titles=[
            ("Social Faux Pas", "社交失误"),
            ("Language Traps", "语言陷阱"),
            ("Non-verbal Miscommunication", "非语言失误"),
            ("Workplace Misunderstandings", "职场误解"),
            ("Recovery and Growth", "修复与成长"),
        ],
        chapters=[
            Chapter("Privacy Questions", "隐私问题", "隐私", "privacy", "yǐnsī"),
            Chapter("Saying No Directly", "直接说不", "拒绝", "refuse", "jùjué"),
            Chapter("Gift Taboos", "礼物文化雷区", "禁忌", "taboo", "jìnjì"),
            Chapter("Title Mistakes", "称呼失误", "头衔", "title", "tóuxián"),
            Chapter("Table Accidents", "餐桌事故", "餐桌", "dining table", "cānzhuō"),
            Chapter("Literal Translation Fails", "字面直译", "直译", "literal translation", "zhíyì"),
            Chapter("The Modesty Paradox", "谦虚悖论", "谦虚", "modesty", "qiānxū"),
            Chapter("Reading Between Lines", "暗示与明说", "暗示", "hint / imply", "ànshì"),
            Chapter("Emoji Misuse", "表情包误用", "表情包", "emoji/sticker", "biǎoqíng bāo"),
            Chapter("Color and Number Taboos", "颜色数字禁忌", "禁忌", "taboo", "jìnjì"),
            Chapter("Nodding Meaning", "点头的含义", "点头", "nod", "diǎntóu"),
            Chapter("Smiling in Context", "微笑的语境", "微笑", "smile", "wēixiào"),
            Chapter("Eye Contact", "眼神接触", "眼神", "gaze / eye contact", "yǎnshén"),
            Chapter("Personal Space", "个人空间", "距离", "distance", "jùlí"),
            Chapter("Queueing Culture", "排队文化", "排队", "queue", "pái duì"),
            Chapter("Silence as Consent", "沉默即同意", "沉默", "silence", "chénmò"),
            Chapter("Praising Subordinates", "表扬下属", "表扬", "praise", "biǎoyáng"),
            Chapter("Sick Leave Culture", "请假文化", "请假", "request leave", "qǐng jià"),
            Chapter("Implied Overtime", "加班暗示", "加班", "overtime", "jiābān"),
            Chapter("Reporting Frequency", "汇报频率", "汇报", "report", "huìbào"),
            Chapter("Elegant Apology", "优雅道歉", "优雅", "elegant", "yōuyǎ"),
            Chapter("Making It a Teaching Moment", "学习时刻", "学习", "learn", "xuéxí"),
            Chapter("Asking the Right Questions", "问对问题", "问题", "question", "wèntí"),
            Chapter("Building Cultural Advisors", "文化顾问", "顾问", "advisor", "gùwèn"),
            Chapter("Misunderstandings as Gifts", "误解是礼物", "误解", "misunderstanding", "wùjiě"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 95: Translation & Meaning
    # -----------------------------------------------------------------
    Book(
        number=95,
        slug="Translation",
        title_en="Translation Lost Art of Meaning",
        subtitle_zh="翻译的艺术：中英之间的意义旅行",
        color="#37474F",
        part_titles=[
            ("The Translation Problem", "翻译的困境"),
            ("Untranslatable Chinese", "无法翻译的中文"),
            ("Idioms and Four-Character Phrases", "成语翻译"),
            ("Interpreting in Real Life", "现实翻译"),
            ("Becoming a Cultural Translator", "成为文化翻译者"),
        ],
        chapters=[
            Chapter("Translation-ese", "翻译腔", "翻译腔", "translation-ese", "fānyì qiāng"),
            Chapter("Untranslatable Words", "不可译词", "缘分", "fate / serendipity", "yuánfèn"),
            Chapter("Culture-Loaded Terms", "文化负载词", "负载", "load / burden", "fùzài"),
            Chapter("Literal vs. Free Translation", "字面与意译", "意译", "free translation", "yìyì"),
            Chapter("Machine Translation Limits", "机器翻译的局限", "机器翻译", "machine translation", "jīqì fānyì"),
            Chapter("The Word Guanxi", "关系这个词", "关系", "guanxi", "guānxi"),
            Chapter("Mianzi in Depth", "面子详解", "面子", "face / mianzi", "miànzi"),
            Chapter("Chabuduo", "差不多", "差不多", "more or less", "chàbuduō"),
            Chapter("Yuanfen", "缘分", "缘分", "fateful connection", "yuánfèn"),
            Chapter("Chiku (Eating Bitter)", "吃苦", "吃苦", "endure hardship", "chī kǔ"),
            Chapter("Why Idioms Are Hard", "成语难译", "成语", "chengyu / idiom", "chéngyǔ"),
            Chapter("Idiom Stories", "成语故事", "故事", "story", "gùshi"),
            Chapter("Modern Idioms", "现代成语", "四字", "four-character", "sì zì"),
            Chapter("Cross-Language Idiom Matches", "成语对译", "对译", "matched translation", "duì yì"),
            Chapter("Idioms in Formal Speech", "正式场合成语", "正式", "formal", "zhèngshì"),
            Chapter("Business Interpretation", "商务口译", "口译", "interpretation", "kǒu yì"),
            Chapter("Diplomatic Language", "外交语言", "表态", "express stance", "biǎotài"),
            Chapter("Translating Humor", "幽默翻译", "笑点", "punch line", "xiàodiǎn"),
            Chapter("Poetry Translation", "诗词翻译", "李白", "Li Bai", "Lǐ Bái"),
            Chapter("Film Subtitling", "电影字幕", "字幕", "subtitle", "zìmù"),
            Chapter("Language + Culture Ability", "语言和文化能力", "能力", "ability", "nénglì"),
            Chapter("Explaining Not Translating", "学习解释", "解释", "explain", "jiěshì"),
            Chapter("Reverse Translation", "反向翻译", "反向", "reverse", "fǎnxiàng"),
            Chapter("Translation as Career", "翻译职业", "职业", "profession", "zhíyè"),
            Chapter("Learner as Translator", "学习者即翻译者", "翻译", "translation", "fānyì"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 96: Carbon Neutrality & Green China
    # -----------------------------------------------------------------
    Book(
        number=96,
        slug="GreenChina",
        title_en="Carbon Neutrality Green China",
        subtitle_zh="绿色中国：碳中和时代的语言",
        color="#1B5E20",
        part_titles=[
            ("Climate Policy", "气候政策"),
            ("Green Economy", "绿色经济"),
            ("Sustainable Living", "可持续生活"),
            ("Technology Solutions", "技术解决方案"),
            ("Global Climate Dialogue", "全球气候对话"),
        ],
        chapters=[
            Chapter("Dual Carbon Goals", "双碳目标", "双碳", "dual carbon (peak + neutrality)", "shuāng tàn"),
            Chapter("National Climate Plan", "国家气候方案", "气候", "climate", "qìhòu"),
            Chapter("Carbon Peaking Path", "碳达峰路径", "达峰", "peak reaching", "dá fēng"),
            Chapter("Local Government Action", "地方政府行动", "地方", "local / regional", "dìfāng"),
            Chapter("Corporate Carbon Targets", "企业碳目标", "目标", "goal / target", "mùbiāo"),
            Chapter("Green Finance", "绿色金融", "绿债", "green bond", "lǜ zhài"),
            Chapter("Carbon Trading", "碳交易", "碳市场", "carbon market", "tàn shìchǎng"),
            Chapter("Green Supply Chain", "绿色供应链", "供应链", "supply chain", "gōngyìng liàn"),
            Chapter("Circular Economy", "循环经济", "循环", "circular", "xúnhuán"),
            Chapter("Green Jobs", "绿色就业", "就业", "employment", "jiùyè"),
            Chapter("Waste Sorting", "垃圾分类", "垃圾分类", "waste sorting", "lājī fēnlèi"),
            Chapter("Energy Saving Daily", "日常节能", "节能", "energy saving", "jié néng"),
            Chapter("Vegetarian and Environment", "素食与环保", "素食", "vegetarian", "sù shí"),
            Chapter("Sustainable Shopping", "可持续购物", "可持续", "sustainable", "kěchíxù"),
            Chapter("Green Commuting", "绿色出行", "出行", "travel / commute", "chūxíng"),
            Chapter("Carbon Capture", "碳捕集", "碳捕集", "carbon capture", "tàn bǔjí"),
            Chapter("Green Hydrogen", "绿氢", "绿氢", "green hydrogen", "lǜ qīng"),
            Chapter("Smart Energy", "智慧能源", "智慧", "smart", "zhìhuì"),
            Chapter("Ecological Restoration", "生态修复", "生态", "ecology", "shēngtài"),
            Chapter("Climate Tech Startups", "气候科技创业", "创业", "startup", "chuàngyè"),
            Chapter("COP Conferences", "COP大会", "COP", "COP conference", "COP"),
            Chapter("China-US Climate", "中美气候合作", "合作", "cooperation", "hézuò"),
            Chapter("Climate Justice", "气候正义", "正义", "justice", "zhèngyì"),
            Chapter("Climate Storytelling", "气候传播", "传播", "communication", "chuánbō"),
            Chapter("Foreign Climate Experts", "外国环保人士", "环保人士", "environmentalist", "huánbǎo rénshì"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 97: Metaverse
    # -----------------------------------------------------------------
    Book(
        number=97,
        slug="Metaverse",
        title_en="Metaverse Digital Reality",
        subtitle_zh="元宇宙：虚实之间的中文语言",
        color="#311B92",
        part_titles=[
            ("Metaverse Basics", "元宇宙基础"),
            ("Digital Economy", "数字经济"),
            ("Virtual Worlds", "虚拟世界"),
            ("Digital Culture", "数字文化"),
            ("Future Scenarios", "未来场景"),
        ],
        chapters=[
            Chapter("China's Metaverse", "中国元宇宙", "元宇宙", "metaverse", "yuán yǔzhòu"),
            Chapter("VR and AR Terms", "VR与AR语言", "虚拟现实", "VR / virtual reality", "xūnǐ xiànshí"),
            Chapter("Digital Twins", "数字孪生", "数字孪生", "digital twin", "shùzì luánshēng"),
            Chapter("Virtual Identity", "虚拟身份", "头像", "avatar", "tóuxiàng"),
            Chapter("Immersive Experience", "沉浸体验", "沉浸", "immersive", "chénjìn"),
            Chapter("NFTs in China", "NFT在中国", "数字藏品", "digital collectible", "shùzì cángpǐn"),
            Chapter("Blockchain", "区块链", "区块链", "blockchain", "qūkuài liàn"),
            Chapter("Digital RMB", "数字人民币", "数字人民币", "digital yuan", "shùzì rénmínbì"),
            Chapter("Platform Economy", "平台经济", "平台", "platform", "píngtái"),
            Chapter("Live-Stream Commerce", "直播电商", "直播", "live stream", "zhíbō"),
            Chapter("Online Game Worlds", "网游世界", "网游", "online game", "wǎng yóu"),
            Chapter("Virtual Concerts", "虚拟演唱会", "演唱会", "concert", "yǎnchàng huì"),
            Chapter("Social Metaverse", "社交元宇宙", "社交", "social", "shèjiāo"),
            Chapter("Education Metaverse", "教育元宇宙", "虚拟课堂", "virtual classroom", "xūnǐ kètáng"),
            Chapter("Medical VR", "医疗VR", "医疗", "medical", "yīliáo"),
            Chapter("Digital Humans", "数字人", "数字人", "digital human", "shùzì rén"),
            Chapter("Virtual Idol Economy", "虚拟偶像经济", "偶像", "idol", "ǒuxiàng"),
            Chapter("Cyberpunk Aesthetics", "赛博朋克", "赛博朋克", "cyberpunk", "sàibó péngkè"),
            Chapter("AI Generated Art", "AI生成艺术", "AI生成", "AI-generated", "AI shēngchéng"),
            Chapter("Privacy and Surveillance", "隐私与监控", "监控", "surveillance", "jiānkòng"),
            Chapter("Remote Work Metaverse", "工作元宇宙", "远程", "remote", "yuǎnchéng"),
            Chapter("Shopping Metaverse", "购物元宇宙", "试衣", "try on clothes", "shì yī"),
            Chapter("Tourism Metaverse", "旅游元宇宙", "数字文旅", "digital tourism", "shùzì wén lǚ"),
            Chapter("Regulating the Metaverse", "监管元宇宙", "监管", "regulation", "jiānguǎn"),
            Chapter("Real and Virtual", "真实与虚拟", "虚拟", "virtual", "xūnǐ"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 98: Aging China
    # -----------------------------------------------------------------
    Book(
        number=98,
        slug="AgingChina",
        title_en="Aging China",
        subtitle_zh="银发中国：老龄化时代的语言",
        color="#4A148C",
        part_titles=[
            ("Understanding Aging China", "理解老龄化"),
            ("Healthcare for Elderly", "老年医疗"),
            ("Elder Care", "养老方式"),
            ("Retirement Life", "退休生活"),
            ("Intergenerational Language", "代际语言"),
        ],
        chapters=[
            Chapter("Data and Reality", "数据与现实", "老龄化", "aging", "lǎolíng huà"),
            Chapter("Only Child Impact", "独生子女影响", "独生子女", "only child", "dúshēng zǐnǚ"),
            Chapter("Urban vs. Rural Elderly", "城乡老人", "老人", "elderly person", "lǎorén"),
            Chapter("Elderly Poverty", "老年贫困", "贫困", "poverty", "pínkùn"),
            Chapter("Digital Life for Elderly", "老年数字生活", "广场舞", "square dancing", "guǎngchǎng wǔ"),
            Chapter("Chronic Disease", "慢性病管理", "慢性病", "chronic disease", "mànxìng bìng"),
            Chapter("Dementia", "认知症", "认知症", "dementia", "rènzhī zhèng"),
            Chapter("Elder Rehab", "老年康复", "康复", "rehabilitation", "kāngfù"),
            Chapter("End-of-Life Care", "临终关怀", "临终", "end of life", "línzhōng"),
            Chapter("Talking About Death", "谈论死亡", "死亡", "death", "sǐwáng"),
            Chapter("Home Care", "居家养老", "护工", "caregiver", "hùgōng"),
            Chapter("Nursing Home", "养老院", "养老院", "nursing home", "yǎnglǎo yuàn"),
            Chapter("Community Care", "社区养老", "日间照料", "day care", "rì jiān zhàoliào"),
            Chapter("Smart Eldercare", "智慧养老", "智慧", "smart", "zhìhuì"),
            Chapter("Talking to Parents About Aging", "和父母谈养老", "养老", "aging / retirement", "yǎnglǎo"),
            Chapter("Pensions", "退休金", "退休金", "pension", "tuìxiū jīn"),
            Chapter("Seniors University", "老年大学", "老年大学", "senior university", "lǎonián dàxué"),
            Chapter("Senior Tourism", "银发旅游", "银发", "silver-haired", "yín fà"),
            Chapter("Square Dance Culture", "广场舞文化", "广场舞", "square dance", "guǎngchǎng wǔ"),
            Chapter("Elder Entrepreneurship", "老有所为", "返聘", "rehire retiree", "fǎn pìn"),
            Chapter("Speaking With Elderly", "和老人沟通", "沟通", "communicate", "gōutōng"),
            Chapter("Bridging Digital Divide", "数字鸿沟", "鸿沟", "chasm / gap", "hónggōu"),
            Chapter("Modern Filial Piety", "现代孝顺", "孝顺", "filial piety", "xiàoshùn"),
            Chapter("Foreigners and Chinese Seniors", "外国人和中国老人", "关怀", "care", "guānhuái"),
            Chapter("Elder Wisdom", "老年智慧", "智慧", "wisdom", "zhìhuì"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 99: Urbanization & New Cities
    # -----------------------------------------------------------------
    Book(
        number=99,
        slug="NewCities",
        title_en="Urbanization New Cities",
        subtitle_zh="新城记：中国城镇化的语言",
        color="#01579B",
        part_titles=[
            ("The Great Migration", "大迁徙"),
            ("New City Development", "新城建设"),
            ("Urban Villages and Renewal", "城中村与更新"),
            ("Housing and Real Estate", "住房与房地产"),
            ("Future Cities", "未来城市"),
        ],
        chapters=[
            Chapter("Rural-Urban Migration", "农村进城", "进城", "move to the city", "jìn chéng"),
            Chapter("Migrant Workers", "流动人口", "农民工", "migrant worker", "nóngmín gōng"),
            Chapter("The Hukou System", "户籍制度", "户口", "household registration", "hùkǒu"),
            Chapter("Spring Festival Migration", "春运", "春运", "Chunyun travel rush", "chūn yùn"),
            Chapter("Left-Behind Children", "留守儿童", "留守", "left behind", "liúshǒu"),
            Chapter("Xiong'an New Area", "雄安新区", "雄安", "Xiong'an", "Xióng'ān"),
            Chapter("Greater Bay Area", "大湾区", "大湾区", "Greater Bay Area", "Dà wān qū"),
            Chapter("Characteristic Towns", "特色小镇", "特色小镇", "characteristic town", "tèsè xiǎozhèn"),
            Chapter("Smart Cities", "智慧城市", "智慧城市", "smart city", "zhìhuì chéngshì"),
            Chapter("Eco Cities", "生态城市", "生态", "ecology", "shēngtài"),
            Chapter("Urban Villages", "城中村", "城中村", "urban village", "chéng zhōng cūn"),
            Chapter("Renovation and Relocation", "旧改与拆迁", "拆迁", "demolition-relocation", "chāiqiān"),
            Chapter("Historic Area Protection", "历史街区保护", "街区", "district / block", "jiēqū"),
            Chapter("Community Placemaking", "社区营造", "营造", "cultivation / building", "yíngzào"),
            Chapter("Night Economy", "夜间经济", "夜间经济", "night economy", "yèjiān jīngjì"),
            Chapter("High Housing Prices", "高房价语言", "房价", "housing price", "fáng jià"),
            Chapter("Housing Regulation", "限购限贷", "限购", "purchase restriction", "xiàn gòu"),
            Chapter("Affordable Housing", "保障房", "保障房", "affordable housing", "bǎozhàng fáng"),
            Chapter("Evergrande Crisis", "恒大危机", "恒大", "Evergrande", "Héngdà"),
            Chapter("Ministry of Housing", "住建部", "住建部", "housing ministry", "zhù jiàn bù"),
            Chapter("Carbon Neutral Cities", "碳中和城市", "中和", "neutralize", "zhōnghé"),
            Chapter("Vertical Green City", "立体城市", "立体", "three-dimensional", "lìtǐ"),
            Chapter("Autonomous Driving Cities", "无人驾驶城市", "无人驾驶", "autonomous driving", "wúrén jiàshǐ"),
            Chapter("Sponge Cities", "海绵城市", "海绵城市", "sponge city", "hǎimián chéngshì"),
            Chapter("Foreign Urban Planners", "外国规划师", "规划师", "planner", "guīhuà shī"),
        ],
    ),
    # -----------------------------------------------------------------
    # BOOK 100: Belt & Road
    # -----------------------------------------------------------------
    Book(
        number=100,
        slug="BeltRoad",
        title_en="Belt Road Initiative",
        subtitle_zh="一带一路：中国全球化的语言",
        color="#B71C1C",
        part_titles=[
            ("What is BRI", "一带一路是什么"),
            ("Infrastructure Projects", "基础设施项目"),
            ("People and Culture", "人与文化"),
            ("Business Language", "商务语言"),
            ("Geopolitics and the Future", "地缘政治与未来"),
        ],
        chapters=[
            Chapter("Historical Origins", "历史起点", "丝绸之路", "Silk Road", "sīchóu zhī lù"),
            Chapter("Policy Declarations", "政策宣言", "倡议", "initiative", "chàngyì"),
            Chapter("Six Economic Corridors", "六大走廊", "走廊", "corridor", "zǒuláng"),
            Chapter("Participating Countries", "参与国家", "参与", "participate", "cānyù"),
            Chapter("Critics' Voice", "批评者语言", "债务陷阱", "debt trap", "zhàiwù xiànjǐng"),
            Chapter("Railway Diplomacy", "铁路外交", "中欧班列", "China-Europe freight train", "zhōng ōu bānliè"),
            Chapter("Overseas Port Investment", "港口投资", "港口", "port", "gǎngkǒu"),
            Chapter("Energy Projects", "能源项目", "能源", "energy", "néngyuán"),
            Chapter("Digital Silk Road", "数字丝绸之路", "数字", "digital", "shùzì"),
            Chapter("Agricultural Cooperation", "农业合作", "援非", "aid Africa", "yuán fēi"),
            Chapter("Confucius Institutes", "孔子学院", "孔子学院", "Confucius Institute", "Kǒngzǐ xuéyuàn"),
            Chapter("Scholarship Exchange", "留学生交流", "留学生", "international student", "liúxué shēng"),
            Chapter("Cultural Festivals", "文化节庆", "节庆", "festival", "jiéqìng"),
            Chapter("Media Cooperation", "媒体合作", "新华社", "Xinhua News", "Xīnhuá shè"),
            Chapter("BRI Chinese Diaspora", "沿线华人", "沿线", "along the route", "yánxiàn"),
            Chapter("Project Negotiation", "项目谈判", "谈判", "negotiate", "tánpàn"),
            Chapter("Local Hire Management", "当地雇员", "雇员", "employee", "gùyuán"),
            Chapter("Anti-Corruption Compliance", "合规与廉洁", "合规", "compliance", "hé guī"),
            Chapter("Localization Language", "本地化语言", "本地化", "localization", "běndì huà"),
            Chapter("Investment Return", "投资回报", "回报", "return / reward", "huíbào"),
            Chapter("Great Power Competition", "大国竞争", "竞争", "competition", "jìngzhēng"),
            Chapter("China-Africa Forum", "中非合作论坛", "中非", "China-Africa", "zhōng fēi"),
            Chapter("European Response", "欧洲反应", "欧盟", "EU", "Ōuméng"),
            Chapter("Global South Voice", "全球南方", "全球南方", "Global South", "quánqiú nánfāng"),
            Chapter("Language as Soft Power", "语言软实力", "软实力", "soft power", "ruǎn shílì"),
        ],
    ),
]


# =========================================================================
# CONTENT GENERATION — per chapter
# =========================================================================

STUDENT_NAMES = [
    ("Ahmed", "Sarah"),
    ("Lisa", "Carlos"),
    ("Maria", "David"),
    ("Yuki", "James"),
    ("Priya", "Tom"),
    ("Olga", "Pablo"),
    ("Aisha", "Lucas"),
    ("Fatima", "Michael"),
    ("Anna", "Ravi"),
    ("Elena", "Hassan"),
]


def render_vocab(core_term: str, core_en: str, core_pinyin: str) -> str:
    """Render the 20-row core vocabulary table."""
    shared_vocab = [
        (core_term, core_pinyin, core_en, "noun/verb", "核心词汇，贯穿本章"),
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
        ("经验", "jīngyàn", "experience", "noun", "经验丰富 = rich in experience"),
        ("建议", "jiànyì", "suggestion / to suggest", "noun/verb", "我建议 = I suggest"),
        ("了解", "liǎojiě", "to understand / to find out", "verb", "了解情况 = get to know the situation"),
        ("发现", "fāxiàn", "to discover / to find", "verb", "我发现 = I found that / I noticed"),
        ("感觉", "gǎnjué", "to feel / feeling", "noun/verb", "感觉很好 = feels great"),
        ("可能", "kěnéng", "maybe / possible", "adverb/adj", "可能是 = it's possible that"),
        ("需要", "xūyào", "to need", "verb", "你需要 = you need to"),
        ("已经", "yǐjīng", "already", "adverb", "已经完成 = already completed"),
        ("还是", "háishi", "or / still", "conjunction", "你还是不明白 = you still don't understand"),
    ]
    lines = ["| Chinese | Pinyin | English | Part of Speech | Usage Note |",
             "|---------|--------|---------|----------------|------------|"]
    for row in shared_vocab:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |")
    return "\n".join(lines)


def render_chapter(book: Book, chapter_num: int, chapter: Chapter, part_idx: int) -> str:
    """Render one chapter as Markdown (~1500 words)."""
    term = chapter.core_term
    term_en = chapter.core_term_en
    term_py = chapter.core_term_pinyin
    part_title_en, part_title_zh = book.part_titles[part_idx]
    student_a, student_b = STUDENT_NAMES[(chapter_num - 1) % len(STUDENT_NAMES)]

    return f"""
# Chapter {chapter_num}: {chapter.title_en} · {chapter.title_zh}

*Part {part_idx + 1}: {part_title_en} {part_title_zh}*

## 1. Real Scene 真实场景

Tony stood at the front of the classroom and looked at his students with a warm smile. "今天我们来聊一个非常实用的话题，" he said. "{chapter.title_en} — {chapter.title_zh}."

{student_a} leaned forward with obvious curiosity. "I've been wondering about this," {student_a} said. "Every time I try to deal with {term_en} in Chinese, something feels off — like I'm saying the right words but in the wrong way."

"That feeling," Tony said, "is one of the most important signals you can have as a language learner. It means you're hearing the gap between translation and communication. Let's close that gap today."

He wrote **{term}** on the board — the Chinese term for {term_en} — and let the class study it for a moment.

"This character, or these characters, carry more meaning than any dictionary definition can capture," Tony continued. "They are embedded in culture, in history, in the way Chinese people see the world. By the end of today's class, you won't just know the word — you'll understand it."

The class was quiet, attentive. {student_b} had already opened a notebook. Outside, the sounds of Shanghai's afternoon traffic filtered through the windows — motorbikes, horns, the occasional announcement from a nearby subway station. The city itself was a constant reminder of why they were here, learning this language, one character at a time.

Tony paced slowly across the front of the room, pausing as he always did before transitioning to core content. "在中国，每一个词都有它背后的故事。Today, as we dig into {term}, I want you to notice not only the vocabulary but the values underneath. This is how real fluency develops — when you see the word, feel the context, and hear the echoes of three thousand years of living language all at once."

---

## 2. Key Vocabulary 核心词汇

{render_vocab(term, term_en, term_py)}

---

## 3. Authentic Dialogues 真实对话

**Dialogue 1: First Encounter**

*Setting: Tony's classroom. {student_a} has just arrived in China and is navigating {term_en} for the first time.*

Tony: 好，今天我们来聊{term}。{student_a}，你有没有遇到过这种情况？
*Hǎo, jīntiān wǒmen lái liáo {term_py}. {student_a}, nǐ yǒu méiyǒu yùdào guò zhè zhǒng qíngkuàng?*
*Okay, today let's talk about {term_en}. {student_a}, have you encountered this kind of situation?*

{student_a}: 有，上个星期我就遇到了，但是我不知道怎么说。
*Yǒu, shàng gè xīngqī wǒ jiù yùdào le, dànshì wǒ bù zhīdào zěnme shuō.*
*Yes, I encountered it just last week, but I didn't know what to say.*

Tony: 这很正常。第一次面对{term}，很多人都不知道从哪里开始。
*Zhè hěn zhèngcháng. Dì yī cì miàn duì {term_py}, hěn duō rén dōu bù zhīdào cóng nǎlǐ kāishǐ.*
*That's completely normal. Facing {term_en} for the first time, many people don't know where to begin.*

{student_a}: 那我应该怎么做？有什么技巧吗？
*Nà wǒ yīnggāi zěnme zuò? Yǒu shénme jìqiǎo ma?*
*So what should I do? Are there any techniques?*

Tony: 当然有。最重要的是要先了解文化背景，然后再学语言表达。
*Dāngrán yǒu. Zuì zhòngyào de shì yào xiān liǎojiě wénhuà bèijǐng, ránhòu zài xué yǔyán biǎodá.*
*Of course there are. The most important thing is to first understand the cultural context, then learn the language expressions.*

{student_a}: 我明白了。文化和语言是分不开的，对吗？
*Wǒ míngbái le. Wénhuà hé yǔyán shì fēn bù kāi de, duì ma?*
*I understand. Culture and language are inseparable, right?*

Tony: 说得非常好！在中国，很多表达方式背后都有深厚的文化含义。
*Shuō de fēicháng hǎo! Zài Zhōngguó, hěn duō biǎodá fāngshì bèihòu dōu yǒu shēnhòu de wénhuà hányì.*
*Very well said! In China, many ways of expression carry deep cultural meanings behind them.*

---

**Dialogue 2: Real-World Application**

*Setting: {student_a} and {student_b} practice together after class, applying what they learned about {term_en}.*

{student_a}: {student_b}，你上课的时候听懂了吗？关于{term}的部分。
*{student_a}: {student_b}, nǐ shàngkè de shíhòu tīng dǒng le ma? Guānyú {term_py} de bùfen.*
*{student_a}: {student_b}, did you understand during class? The part about {term_en}.*

{student_b}: 大部分听懂了，但是有一个地方不太明白。
*Dà bùfen tīng dǒng le, dànshì yǒu yī gè dìfāng bù tài míngbái.*
*I understood most of it, but there's one part I wasn't too clear on.*

{student_a}: 哪个部分？我来帮你解释一下。
*Nǎ gè bùfen? Wǒ lái bāng nǐ jiěshì yīxià.*
*Which part? Let me help explain it.*

{student_b}: 就是为什么在中国，处理{term}的方式跟我们国家那么不一样？
*Jiùshì wèishénme zài Zhōngguó, chǔlǐ {term_py} de fāngshì gēn wǒmen guójiā nàme bù yīyàng?*
*Why is the way of dealing with {term_en} in China so different from our country?*

{student_a}: Tony说过，这是因为中国有自己独特的历史和文化传统。
*Tony shuō guò, zhè shì yīnwèi Zhōngguó yǒu zìjǐ dútè de lìshǐ hé wénhuà chuántǒng.*
*Tony said it's because China has its own unique history and cultural traditions.*

{student_b}: 对，我也记得他说过。那我们来练习一下刚才学的表达方式吧。
*Duì, wǒ yě jìde tā shuō guò. Nà wǒmen lái liànxí yīxià gāngcái xué de biǎodá fāngshì ba.*
*Right, I remember him saying that too. Let's practice the expressions we just learned.*

{student_a}: 好主意。你先说，我来纠正。
*Hǎo zhǔyì. Nǐ xiān shuō, wǒ lái jiūzhèng.*
*Good idea. You go first, I'll correct.*

---

**Dialogue 3: Tony's Teaching Story**

Tony: 我想给你们讲一个真实的故事。有一次，一个我的学生……
*Wǒ xiǎng gěi nǐmen jiǎng yī gè zhēnshí de gùshi. Yǒu yī cì, yī gè wǒ de xuésheng……*
*I want to tell you a real story. Once, one of my students...*

{student_a}: 这个学生也是外国人吗？
*Zhège xuésheng yě shì wàiguó rén ma?*
*Was this student also a foreigner?*

Tony: 对，他来自欧洲，在中国工作了两年。他觉得自己的中文已经很好了，但是在处理{term}的时候，还是经常出错。
*Duì, tā lái zì Ōuzhōu, zài Zhōngguó gōngzuò le liǎng nián. Tā juéde zìjǐ de Zhōngwén yǐjīng hěn hǎo le, dànshì zài chǔlǐ {term_py} de shíhòu, háishi jīngcháng chū cuò.*
*Yes, he came from Europe and had worked in China for two years. He felt his Chinese was already good, but when dealing with {term_en}, he still made frequent mistakes.*

{student_b}: 他出了什么错？
*Tā chū le shénme cuò?*
*What mistakes did he make?*

Tony: 他把自己国家的思维方式直接翻译成中文，结果虽然语法对了，但是感觉不对。这就是我们今天要深入探讨的核心问题。
*Tā bǎ zìjǐ guójiā de sīwéi fāngshì zhíjiē fānyì chéng Zhōngwén, jiéguǒ suīrán yǔfǎ duì le, dànshì gǎnjué bù duì. Zhè jiùshì wǒmen jīntiān yào shēnrù tàntǎo de héxīn wèntí.*
*He directly translated his own country's way of thinking into Chinese. The grammar was correct, but it felt wrong. This is exactly the core issue we're going to explore in depth today.*

---

## 4. Language Patterns 语言模式

**Pattern 1: 先…然后再… (First... then...)**

This sequential pattern is crucial when discussing {term_en} because Chinese communication often emphasizes the proper order of steps.

**Chinese:** 我们应该先了解{term}的文化背景，然后再学具体的表达方式。
**Pinyin:** Wǒmen yīnggāi xiān liǎojiě {term_py} de wénhuà bèijǐng, ránhòu zài xué jùtǐ de biǎodá fāngshì.
**English:** We should first understand the cultural background of {term_en}, and then learn the specific expressions.

---

**Pattern 2: 虽然…但是… (Although... but...)**

This concessive pattern allows speakers to acknowledge complexity — a highly valued rhetorical move in Chinese.

**Chinese:** 虽然{term}看起来简单，但是背后有很深的文化含义。
**Pinyin:** Suīrán {term_py} kàn qǐlái jiǎndān, dànshì bèihòu yǒu hěn shēn de wénhuà hányì.
**English:** Although {term_en} looks simple, there are deep cultural meanings behind it.

---

**Pattern 3: 对…来说 (For / As for...)**

Use this to frame a topic from a specific perspective.

**Chinese:** 对外国人来说，掌握{term}需要时间和耐心。
**Pinyin:** Duì wàiguó rén lái shuō, zhǎngwò {term_py} xūyào shíjiān hé nàixīn.
**English:** For foreigners, mastering {term_en} takes time and patience.

---

**Pattern 4: 只要…就… (As long as... then...)**

A conditional pattern that frames success as achievable with the right attitude.

**Chinese:** 只要你认真练习，就一定能学好{term}。
**Pinyin:** Zhǐyào nǐ rènzhēn liànxí, jiù yīdìng néng xué hǎo {term_py}.
**English:** As long as you practice seriously, you will definitely be able to master {term_en}.

---

## 5. Pronunciation & Tone Guide 发音与声调

The key term **{term}** ({term_py}) requires careful attention to tones. In Mandarin, the same syllable spoken with different tones produces completely different meanings — a fact that trips up learners at every level.

**Tony's Tone Drill:** Say {term} three times — once normally, once slowly with exaggerated tones, once at natural conversation speed. Record yourself and compare.

**Tony's Trick:** Don't try to *remember* tones in isolation. Always learn a word in a full sentence. Your brain stores tones better in context than as abstract facts.

---

## 6. Practice Exercises 练习

**Exercise 1 — Translation:**
Translate into Chinese: "I need to first understand {term_en}, then make a decision."
**Answer:** 我需要先了解{term}，然后再做决定。(Wǒ xūyào xiān liǎojiě {term_py}, ránhòu zài zuò juédìng.)

**Exercise 2 — Fill in the blank:**
虽然___很复杂，但是_____。(Complete the sentence about {term_en}.)
**Sample answer:** 虽然{term}很复杂，但是只要多练习就会明白。

**Exercise 3 — Create a sentence:**
Use 对…来说 to make a sentence about {term_en} from your own perspective.
**Sample answer:** 对我来说，{term}是一个很新的概念。

**Exercise 4 — Dialogue reconstruction:**
Put these lines in the correct order to form a logical exchange about {term_en}:
a) 我明白了，谢谢你的解释。
b) 你需要先了解文化背景。
c) 我应该怎么处理{term}？
d) 然后再学具体的语言表达。
**Answer:** c → b → d → a

**Exercise 5 — Real-world task:**
Imagine you are explaining {term_en} to a friend who has never experienced it. Write 3–5 sentences in Chinese describing what it is and why it matters.

**Exercise 6 — Cultural reflection:**
How is {term_en} handled differently in China vs. your home country? Write 2 sentences in Chinese comparing the two approaches.

---

## 7. Cultural Deep Dive 文化深度解析

Understanding **{term}** ({term_en}) in China requires more than vocabulary — it demands a shift in cultural perspective.

China's approach to {term_en} has been shaped by thousands of years of Confucian philosophy, which places enormous value on **harmony (和谐 héxié)**, **relationships (关系 guānxi)**, and **face (面子 miànzi)**. These three concepts permeate every aspect of Chinese social and professional life, including how people navigate {term_en}.

**Harmony** means avoiding direct confrontation whenever possible. In practical terms, this means Chinese speakers often express disagreement or difficulty indirectly — through hesitation, subject-changing, or soft language like 可能 (maybe) and 有一点 (a little bit). When dealing with {term}, foreigners who are trained to be direct often misread this indirectness as agreement, only to be surprised later.

**Relationships** are the operating system beneath the surface of Chinese society. Before any transaction, negotiation, or request, there is an implicit question: *What is our relationship?* The quality and depth of the relationship determines what can be asked, how it should be asked, and what the likely outcome will be. This is why Chinese professionals invest so much time in dinners, small talk, and favors — they are building the relational infrastructure that makes everything else possible.

**Face** — both giving it (给面子 gěi miànzi) and protecting it (保面子 bǎo miànzi) — operates as an invisible social currency. A request phrased in a way that publicly embarrasses someone will fail not because of the request's content, but because of the shame it creates. Conversely, a well-placed compliment or a graceful handling of a difficult situation earns enormous goodwill.

For foreigners learning to navigate {term}, Tony's advice is consistent: **observe first, speak second.** Watch how Chinese people around you handle similar situations. Notice the pacing, the tone, the level of formality. Then practice using the vocabulary you've learned in low-stakes situations before applying it in high-stakes moments. The students who succeed fastest are not those with the largest vocabulary — they are those who understand that Chinese communication operates on multiple levels simultaneously: what is said, what is meant, and what is felt.

---

## 8. Common Mistakes 常见错误

**Mistake 1: Direct translation**
Translating your native language's approach to {term_en} word-for-word into Chinese. This produces grammatically correct but culturally jarring sentences.

**Mistake 2: Ignoring register**
Using casual language in formal situations, or overly formal language in casual settings. Chinese has a wider register gap than many Western languages.

**Mistake 3: Rushing the relationship**
Getting straight to the point without the expected preliminary small talk. In Chinese communication, especially for {term_en}, the journey matters as much as the destination.

**Mistake 4: Not accounting for face**
Phrasing a request or correction in a way that causes embarrassment. Always soften corrections with 可能 or 也许.

---

## 9. Review & Summary 本章总结

In this chapter, we covered **{chapter.title_en}** — **{chapter.title_zh}** — one of the essential topics for navigating {term_en} in a Chinese context.

**Key takeaways:**
1. The term **{term}** carries cultural weight beyond its dictionary definition.
2. Sequential patterns (先…然后再…) and concessive patterns (虽然…但是…) are fundamental to Chinese communication.
3. Culture shapes language — understanding Confucian values of harmony, relationship, and face helps you interpret and produce more natural Chinese.
4. The most common mistakes come from direct translation — resist the urge to simply render your native language into Chinese.

**Your homework:** Find one real-life situation this week where you can apply what you learned about {term}. It doesn't have to be perfect — the goal is to try, notice, and learn.

*As Tony always says: 学语言不只是学说话，更是学做人。Learning a language is not just learning to speak — it's learning a whole way of being.*

---
"""


def build_book_md(book: Book) -> str:
    """Assemble the complete Markdown for one book."""
    parts = []
    parts.append(f"""# Z Turns Chinese Book {book.number}
## {book.title_en} — {book.subtitle_zh}
**Author:** Tony Sheng
**Website:** zturnsgo.com
**Teaching Experience:** 3000+ hours of real Chinese teaching
**Series Color:** {book.color}

---

## About This Book

This book is part of the Z Turns Chinese series — a comprehensive curriculum designed to take foreign learners from survival Chinese through advanced cultural fluency. Unlike traditional textbooks that focus solely on grammar and vocabulary, each Z Turns book immerses you in the lived experience of modern China through dialogues, cultural analysis, and real-world scenarios.

**Book {book.number}** focuses on {book.title_en.lower()}, offering 25 chapters across 5 thematic parts. Each chapter follows a consistent structure: a classroom scene with Tony and his international students, core vocabulary, three authentic dialogues, four language patterns, pronunciation guidance, practice exercises, cultural deep-dive, common mistakes, and a review summary.

**How to use this book:**
- Read one chapter per day. Do not rush.
- Say every sentence aloud three times — once slowly, once naturally, once as if you were really in that situation.
- Complete the practice exercises before checking the answers.
- Review the Cultural Deep Dive sections multiple times — they contain the "why" behind the "what".

**Who this book is for:**
- Intermediate to advanced learners (HSK 4–6) who want to go beyond textbook Chinese.
- Professionals, residents, travelers, and students seeking real fluency in specific cultural contexts.
- Teachers looking for ready-to-use materials.

---
""")

    for i, chapter in enumerate(book.chapters):
        part_idx = i // 5
        parts.append(render_chapter(book, i + 1, chapter, part_idx))

    parts.append(f"""
---

# Final Words 最后的话

Congratulations on completing Book {book.number} of the Z Turns Chinese series!

You have now worked through 25 chapters covering the full spectrum of {book.title_en.lower()}. This is no small achievement. The vocabulary, patterns, and cultural insights you've absorbed are the building blocks of real fluency — not textbook Chinese, but the living language spoken by real people in real situations every day.

**What to do next:**
1. **Review** — Return to chapters that felt challenging. True mastery comes from revisiting, not just reading once.
2. **Apply** — Find one opportunity each week to use what you learned. The Chinese saying 熟能生巧 (shú néng shēng qiǎo — "practice makes perfect") is especially true here.
3. **Continue** — The Z Turns Chinese series has 100 books covering every major cultural domain. Whatever area of Chinese life fascinates you, there is a book waiting for you.

**A final word from Tony:**

每一个学中文的外国人都有自己的故事。你的故事还在继续。不要害怕犯错——每一次错误都是一次学习的机会。最重要的是，不要放弃。

*Every foreigner who learns Chinese has their own story. Your story is still being written. Don't be afraid of making mistakes — each mistake is a learning opportunity. Most importantly, don't give up.*

学中文，就是学做朋友。用语言跨越文化，用文化理解人心。

*Learning Chinese is learning to make friends. Use language to bridge cultures; use culture to understand hearts.*

祝你在中文的旅程中越走越远。

— Tony Sheng

---

*Z Turns Chinese Book {book.number}. © 2026 Tony Sheng. All rights reserved.*
*Website: zturnsgo.com*
""")

    return "\n".join(parts)


# =========================================================================
# PDF COMPILATION
# =========================================================================

def compile_pdf(md_path: Path, book: Book, pdf_path: Path) -> bool:
    """Call v3 generator to compile PDF."""
    cmd = [
        str(VENV_PY),
        str(GENERATOR),
        "textbook",
        "--md", str(md_path),
        "--number", str(book.number),
        "--title", book.title_en,
        "--subtitle", book.subtitle_zh,
        "--color", book.color,
        "--out", str(pdf_path),
    ]
    print(f"  PDF: {pdf_path.name}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            print(f"  ✗ PDF compile failed (exit {result.returncode})")
            if result.stderr:
                print(f"    stderr: {result.stderr[:500]}")
            return False
        print(f"  ✓ PDF compiled")
        return True
    except subprocess.TimeoutExpired:
        print(f"  ✗ PDF compile timeout")
        return False
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False


def generate_one_book(book: Book) -> tuple[bool, bool]:
    """Generate MD + PDF for one book. Returns (md_ok, pdf_ok)."""
    book_dir = OUTPUT_ROOT / f"Book{book.number}_{book.slug}"
    book_dir.mkdir(parents=True, exist_ok=True)

    md_path = book_dir / f"ZTurns_Book{book.number}_{book.slug}.md"
    pdf_path = book_dir / f"ZTurns_Book{book.number}_{book.slug}.pdf"

    print(f"\n{'=' * 60}")
    print(f"Book {book.number}: {book.title_en}")
    print(f"{'=' * 60}")

    # Generate Markdown
    try:
        md_content = build_book_md(book)
        md_path.write_text(md_content, encoding="utf-8")
        md_size = md_path.stat().st_size
        print(f"  ✓ MD written: {md_size:,} bytes")
        md_ok = True
    except Exception as e:
        print(f"  ✗ MD generation failed: {e}")
        return False, False

    # Compile PDF (sequential, no parallel)
    pdf_ok = compile_pdf(md_path, book, pdf_path)

    return md_ok, pdf_ok


def main() -> None:
    """Main entry point: generate all books sequentially."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", type=int, help="Only generate this book number")
    parser.add_argument("--from", dest="start", type=int, default=71, help="Start from book number")
    parser.add_argument("--to", dest="end", type=int, default=100, help="End at book number")
    parser.add_argument("--md-only", action="store_true", help="Only generate MD, skip PDF")
    args = parser.parse_args()

    if args.only:
        books_to_gen = [b for b in BOOKS if b.number == args.only]
    else:
        books_to_gen = [b for b in BOOKS if args.start <= b.number <= args.end]

    if not books_to_gen:
        print("No books to generate.")
        return

    print(f"Generating {len(books_to_gen)} books: {[b.number for b in books_to_gen]}")
    print(f"Mode: {'MD only' if args.md_only else 'MD + PDF'}")

    results = []
    for book in books_to_gen:
        if args.md_only:
            # MD only
            book_dir = OUTPUT_ROOT / f"Book{book.number}_{book.slug}"
            book_dir.mkdir(parents=True, exist_ok=True)
            md_path = book_dir / f"ZTurns_Book{book.number}_{book.slug}.md"
            print(f"\nBook {book.number}: {book.title_en}")
            md_content = build_book_md(book)
            md_path.write_text(md_content, encoding="utf-8")
            size = md_path.stat().st_size
            print(f"  ✓ MD written: {size:,} bytes")
            results.append((book.number, True, None))
        else:
            md_ok, pdf_ok = generate_one_book(book)
            results.append((book.number, md_ok, pdf_ok))

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    md_ok_count = sum(1 for _, md, _ in results if md)
    pdf_ok_count = sum(1 for _, _, pdf in results if pdf)
    print(f"MD generated: {md_ok_count}/{len(results)}")
    if not args.md_only:
        print(f"PDF compiled: {pdf_ok_count}/{len(results)}")
        failed = [n for n, md, pdf in results if not pdf]
        if failed:
            print(f"Failed PDFs: {failed}")


if __name__ == "__main__":
    main()
