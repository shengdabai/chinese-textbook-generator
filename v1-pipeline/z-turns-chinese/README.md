# Z Turns Chinese AutoBuilder v4.0 — Standardized Production Pipeline

## AI驱动的标准化中文教材生产管线

**三册系列 | Li Xiaolai方法论 | 四层对照翻译 | GetNotes集成 | Claude API**

---

## 什么是 Z Turns Chinese

A standardized pipeline for generating Chinese learning textbooks as PDFs. Content follows the methodology from two reference works by Li Xiaolai:
- **"1000 Hours" (2024)** — neuroscience-backed density training, 7-step daily protocol, brain-training framing
- **"Everyone Can Use English" (2010)** — use-first philosophy, belief engineering, content before form

The four-layer translation format (Chinese | Pinyin | Word-by-word | Natural English) is the core differentiator of every lesson.

---

## 快速开始 (Quick Start)

### 1. 检查系统状态 (Check Status)
```bash
python3 pipeline.py --status
```

### 2. 生成第一册 (Generate Book 1)
```bash
# Generate all 15 chapters as individual PDFs
python3 pipeline.py --book 1 --chapters all

# Generate a merged single-PDF complete book
python3 pipeline.py --book 1 --complete

# Generate specific chapters only
python3 pipeline.py --book 1 --chapters 1-5
python3 pipeline.py --book 1 --chapters 3
```

### 3. 验证内容 (Validate Content)
```bash
python3 pipeline.py --validate --book 1
```

### 4. 从GetNotes生成 (Generate from GetNotes)
```bash
export GETNOTE_API_KEY='your-key'
export GETNOTE_CLIENT_ID='your-client-id'
export ANTHROPIC_API_KEY='sk-ant-...'

python3 pipeline.py --book 3 --from-getnotes --topic "restaurant"
python3 pipeline.py --book 2 --from-getnotes --topic "workplace"
```

### 5. AI Commander（高级）
```bash
python3 main.py mission "Create a pinyin learning course, 10 lessons"
python3 main.py mission "生成拼音教程" --hsk 1 --lessons 10
python3 main.py mission -i   # 交互模式
```

---

## 三册系列 (Book Series)

| 册 | 名称 | 级别 | 章节 | HSK | CEFR |
|----|------|------|------|-----|------|
| Book 1 | Beginner's Guide to Everyday Chinese | beginner | 15 | HSK 1 | A1 |
| Book 2 | Building Everyday Fluency | elementary | 25 | HSK 2 | A2 |
| Book 3 | Topic-Based Fluency | intermediate | 20 | HSK 3 | B1 |

**Book 1 promise:** Handle greetings, introductions, food, shopping, and directions.  
**Book 2 promise:** Navigate work, travel, and social situations in Chinese.  
**Book 3 promise:** Discuss work, health, culture, and current events in Chinese.

---

## 教学方法论 (Methodology)

### 7步每日练习协议 (7-Step Daily Protocol)
From "1000 Hours" by Li Xiaolai:

| 步骤 | 名称 | 时长 |
|------|------|------|
| 1 | 复习昨天 (Review Yesterday) | 10 min |
| 2 | 慢速听 (Slow Listen) | 15 min |
| 3 | 分段跟读 (Segment Shadow) | 20 min |
| 4 | 全文跟读 (Full Shadow) | 15 min |
| 5 | 背诵 (Memorize) | 20 min |
| 6 | 放松 (Relax) | 10 min |
| 7 | 每日回顾 (Daily Review) | 10 min |

### 核心哲学 (Core Philosophy)
From "Everyone Can Use English" by Li Xiaolai:
- **Use, don't just study** — produce Chinese from day one
- **Belief engineering** — destroy limiting beliefs before teaching methods
- **Content first** — give students a script before asking them to speak
- **No shortcuts** — sustained effort over 3+ hours/day

### 标准章节结构 (Standard Chapter Structure)
Every chapter in every book:
1. Scene Setter (场景导入)
2. Key Vocabulary (核心词汇) — four-layer format
3. Dialogues (对话练习)
4. Grammar Spotlight (语法要点)
5. Culture Note (文化小贴士)
6. Practice (练习) — 4 exercise types
7. Daily Challenge (每日挑战)
8. Answer Key (答案)

---

## 四层逐字对照翻译 (Four-Layer Translation)

Every sentence in every lesson:

```
Layer 1:  你   想    吃   什么？         (汉字)
Layer 2:  nǐ   xiǎng  chī  shénme?      (拼音 — always tone marks, never numbers)
Layer 3:  you  want   eat  what?         (逐词直译, Chinese word order)
Layer 4:  "What would you like to eat?" (自然英语)
```

**Pinyin rule:** ALWAYS `ā á ǎ à` — NEVER `a1 a2 a3 a4`

---

## 项目架构 (Architecture)

```
pipeline.py          ← NEW: Standardized production entry point
main.py              ← Original CLI (still works)
    |
    ├── methodology.py   ← NEW: Li Xiaolai method encoding
    ├── book_template.py ← NEW: Reusable template + validators
    ├── ai_commander.py  ← AI orchestrator (8-stage pipeline)
    ├── ai_engine.py     ← Claude API content generation
    ├── getnotes_client.py  ← GetNotes API client
    ├── content_extractor.py ← URL/PDF extraction
    ├── pdf_builder.py   ← PDF layout engine
    ├── generator.py     ← Generation coordinator
    ├── config.py        ← Configuration (HSK, consistency, styling)
    ├── hsk_vocab.py     ← HSK 3.0 vocabulary database
    ├── lesson_data.py   ← Pre-built lesson content
    ├── privacy_filter.py ← PII detection and anonymization
    ├── qa_engine.py     ← Quality assurance
    └── output/          ← Generated PDFs
```

### AI Commander Pipeline (8 Stages)
```
Mission Brief
    [1] 任务解析  Mission Parsing
    [2] 市场分析  Market Analysis
    [3] 课程规划  Course Planning
    [4] 素材采集  Material Gathering  ← GetNotes (audio transcripts), URLs, files
    [5] 隐私过滤  Privacy Filtering
    [6] 课程生成  Lesson Generation   ← Claude API
    [7] 质量验证  Quality Validation
    [8] PDF输出   PDF Production
        ↓
    output/ PDFs
```

---

## 环境要求 (Requirements)

```bash
pip3 install fpdf2 pypinyin jieba anthropic
```

Environment variables:
```bash
export ANTHROPIC_API_KEY='sk-ant-...'    # Required for AI generation
export GETNOTE_API_KEY='your-key'         # Required for GetNotes integration
export GETNOTE_CLIENT_ID='your-client-id' # Required for GetNotes integration
```

---

## 项目文件 (Project Files)

| 文件 | 功能 |
|------|------|
| `pipeline.py` | 标准化生产入口，支持三册系列 |
| `methodology.py` | Li Xiaolai方法论配置（7步协议、哲学、质量标准） |
| `book_template.py` | 书籍模板系统（验证器、schema、拼音检查） |
| `main.py` | 原始CLI入口（向后兼容） |
| `ai_commander.py` | AI指挥官，编排全流水线 |
| `ai_engine.py` | Claude API集成，四层对照生成 |
| `getnotes_client.py` | GetNotes API客户端（录音转写优先） |
| `content_extractor.py` | URL/PDF/文件内容提取 |
| `pdf_builder.py` | PDF排版引擎 |
| `generator.py` | PDF生成协调器 |
| `config.py` | HSK标准/一致性规则/样式配置 |
| `hsk_vocab.py` | HSK 3.0词汇库 |
| `lesson_data.py` | 预置课程内容（离线模式） |
| `privacy_filter.py` | PII检测脱敏 |
| `qa_engine.py` | 质量验证引擎 |

---

## 技术方案来源 (Technical Sources)

| 特性 | 来源 |
|------|------|
| 四层对照翻译引擎 | Claude方案 |
| XML Prompt链设计 | Gemini方案 |
| 双引擎(零基础+商务) | Minimax方案 |
| QA校验+发布闸门 | Kimi方案 |
| 句型记忆库+课程图谱 | GPT方案 |
| 隐私过滤优先 | Grok方案 |
| 7步每日协议 | Li Xiaolai "1000 Hours" (2024) |
| 使用第一哲学 | Li Xiaolai "Everyone Can Use English" (2010) |
