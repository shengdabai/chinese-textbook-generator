# Z Turns Chinese AutoBuilder v3.0 — 统一技术文档

> **版本**: 3.0 | **最后更新**: 2026-03-24 | **状态**: 活跃开发中
>
> 本文档综合了 Claude、Gemini、Grok、Kimi、GPT、Minimax 六大 AI 技术方案的精华，
> 结合项目已有实现，形成统一可执行的技术蓝图。

---

## 目录

1. [产品愿景与核心价值](#1-产品愿景与核心价值)
2. [系统架构总览](#2-系统架构总览)
3. [四层逐字对照翻译引擎（核心差异化）](#3-四层逐字对照翻译引擎核心差异化)
4. [HSK 词汇控制系统](#4-hsk-词汇控制系统)
5. [课程图谱设计](#5-课程图谱设计)
6. [句型记忆库（Phrase Memory）](#6-句型记忆库phrase-memory)
7. [AI Prompt 工程](#7-ai-prompt-工程)
8. [功能模块详细设计](#8-功能模块详细设计)
9. [数据模型设计](#9-数据模型设计)
10. [核心流程设计](#10-核心流程设计)
11. [QA 质量保障体系](#11-qa-质量保障体系)
12. [API 接口设计](#12-api-接口设计)
13. [开发状态与路线图](#13-开发状态与路线图)
14. [技术栈与部署](#14-技术栈与部署)
15. [附录](#附录)

---

## 1. 产品愿景与核心价值

### 1.1 一句话定义

**Z Turns Chinese AutoBuilder** 是一个隐私优先、AI 驱动的中文教材自动生成系统，
通过"四层逐字对照翻译"方法，将教师的真实教学素材转化为符合 HSK 3.0 标准的
专业中文学习教材。

> 来源：Claude 方案（四层翻译引擎）+ Grok 方案（隐私优先架构）+ GPT 方案（Privacy-First Curriculum OS）

### 1.2 核心问题解决矩阵

| 问题 | 现状 | 本系统方案 | 来源 |
|------|------|-----------|------|
| 教材编写耗时 | 一位教师编写一册教材需 6-12 个月 | AI 辅助，数天完成初稿 | Claude |
| 翻译质量差异 | 传统翻译丢失中文语序信息 | 四层对照：汉字→拼音→逐词直译→自然英语 | Claude+Gemini |
| 词汇难度失控 | 教材新词随意引入 | HSK 3.0 词汇账本 + 数学公式控制 | Gemini+Kimi |
| 隐私泄露风险 | 教学笔记含学生 PII | PII 检测→脱敏→闸门审核 | Grok+Kimi |
| 内容一致性 | 手工编写难保术语统一 | 句型记忆库 + 一致性 QA 引擎 | GPT+Claude |
| 风格不统一 | 多人协作风格漂移 | StyleDNA 风格提取 + 注入 | Minimax |

### 1.3 目标用户画像

| 画像 | 描述 | 核心需求 |
|------|------|---------|
| **Tony 老师** (主要) | 有多年中文教学经验的华裔教师，积累了大量教学笔记和录音 | 将零散素材系统化为可出版教材 |
| **独立中文教师** | 在海外开设中文私塾或在线课程的教师 | 快速生成适配学生水平的课程 |
| **语言学校** | 提供中文课程的教育机构 | 批量定制教材、保证质量一致性 |
| **自学者** (间接) | 使用生成教材的英语母语学习者 | 清晰的逐字对照帮助理解中文结构 |

> 来源：Grok 方案（$520 亿在线语言学习市场分析）+ Claude 方案（Tony 品牌个人化）

### 1.4 核心使用场景

1. **Mission 模式**：用自然语言下达任务 → AI Commander 自动编排全流程
2. **单课生成**：指定主题和 HSK 等级 → AI 引擎生成单课内容
3. **素材导入**：从 GetNotes、URL、PDF 提取教学内容 → 隐私过滤 → 结构化
4. **离线演示**：使用预置课程数据生成 PDF，无需 API Key

### 1.5 MVP 范围 vs V1 vs V2

| 范围 | MVP (当前 v3.0) | V1 目标 | V2 愿景 |
|------|-----------------|---------|---------|
| 翻译引擎 | ✅ 四层对照 PDF 输出 | Web 预览 + 交互编辑 | 多语言支持 |
| 词汇控制 | ✅ HSK 1-3 + 硬限制 | 词汇账本持久化 | 自适应词汇推荐 |
| AI 生成 | ✅ Claude API 单次生成 | 多轮迭代优化 | LoRA 微调专属模型 |
| 隐私过滤 | ✅ Regex + 关键词 | spaCy NER + Moderation API | 联邦学习 |
| 课程结构 | ✅ Book 1 (15课) | Book 1-3 完整系列 | 自定义课程树 |
| QA | ✅ 基础校验 | 自动检查 + 审核控制台 | A/B 测试 + 学生反馈闭环 |
| 输出格式 | ✅ PDF (fpdf2) | PDF + EPUB + Web | 交互式练习 + 音频 |

---

## 2. 系统架构总览

### 2.1 分层架构图

```
+============================================================================+
|                           输入层 (Input Layer)                               |
|                                                                              |
|  +----------------+  +--------------+  +-------------+  +----------------+  |
|  | CLI 命令行入口  |  | GetNotes API |  | URL/PDF提取  |  | 文本/文件导入  |  |
|  | (main.py)      |  | (getnotes_   |  | (content_   |  |                |  |
|  |                |  |  client.py)  |  |  extractor  |  |                |  |
|  | 6个命令:       |  |              |  |  .py)       |  |                |  |
|  | mission        |  | 8个API方法   |  |             |  |                |  |
|  | generate       |  | 4个辅助方法  |  | URL提取      |  |                |  |
|  | notes          |  |              |  | PDF提取      |  |                |  |
|  | extract        |  |              |  | 文件提取     |  |                |  |
|  | offline        |  |              |  | 中文分析     |  |                |  |
|  | status         |  |              |  |             |  |                |  |
|  +-------+--------+  +------+-------+  +------+------+  +-------+--------+  |
|          |                   |                 |                 |            |
+========= | ================ | =============== | =============== | ===========+
           |                   |                 |                 |
           v                   v                 v                 v
+============================================================================+
|                          处理层 (Processing Layer)                            |
|                                                                              |
|  +---------------------------------------------------------------------+    |
|  |              AI Commander 智能指挥官 (ai_commander.py)                |    |
|  |              8阶段流水线编排器                                         |    |
|  |                                                                       |    |
|  |  1.任务解析 -> 2.市场分析 -> 3.课程规划 -> 4.素材采集                  |    |
|  |       -> 5.隐私过滤 -> 6.课程生成 -> 7.质量验证 -> 8.PDF输出          |    |
|  +--+--------+----------+---------+---------+----------+---------+------+    |
|     |        |          |         |         |          |         |            |
|     v        v          v         v         v          v         v            |
|  +------+ +------+ +--------+ +-------+ +------+ +--------+ +------+        |
|  |隐私   | |AI    | |HSK词汇 | |课程   | |PDF   | |QA      | |一致性|        |
|  |过滤器 | |引擎  | |控制    | |图谱   | |排版  | |验证    | |规则  |        |
|  |privacy| |ai_   | |hsk_   | |config | |pdf_  | |genera- | |confi-|        |
|  |_filter| |engine| |vocab  | |.py    | |build-| |tor.py  | |g.py  |        |
|  |.py    | |.py   | |.py    | |       | |er.py | |        | |      |        |
|  +------+ +------+ +--------+ +-------+ +------+ +--------+ +------+        |
|                                                                              |
+============================================================================+
           |
           v
+============================================================================+
|                          数据层 (Data Layer)                                 |
|                                                                              |
|  +------------------+  +------------------+  +------------------+            |
|  | Raw Vault        |  | Safe Corpus      |  | Curriculum       |            |
|  | (原始素材)        |  | (脱敏语料)        |  | Assets (课程资产) |            |
|  |                  |  |                  |  |                  |            |
|  | - GetNotes原文   |  | - 匿名化文本     |  | - 课程计划       |            |
|  | - URL抓取内容    |  | - 结构化对话     |  | - 词汇账本       |            |
|  | - PDF文本       |  | - 提取的词汇     |  | - 句型记忆库     |            |
|  | - 音频转写      |  | - 语法模式       |  | - 课次数据       |            |
|  +------------------+  +------------------+  +------------------+            |
|                                                                              |
+============================================================================+
           |
           v
+============================================================================+
|                          输出层 (Output Layer)                               |
|                                                                              |
|  +------------------+  +------------------+  +------------------+            |
|  | PDF 教材         |  | 课程元数据        |  | 生成日志         |            |
|  | (四层对照排版)    |  | (JSON)           |  | (执行报告)        |            |
|  |                  |  |                  |  |                  |            |
|  | - 封面          |  | - lesson.json    |  | - 管线状态       |            |
|  | - 课次PDF       |  | - course_plan    |  | - QA报告        |            |
|  | - 答案页        |  | - vocab_ledger   |  | - 隐私扫描报告   |            |
|  +------------------+  +------------------+  +------------------+            |
|                                                                              |
+============================================================================+
```

### 2.2 模块关系图

```
                        main.py (CLI入口)
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
        ai_commander   (generate)    (offline)
              |
    +---------+---------+---------+---------+
    |         |         |         |         |
    v         v         v         v         v
ai_engine  getnotes  content_  privacy_  generator
   .py     _client   extractor  filter     .py
              .py      .py       .py        |
    |                                       v
    |                                  pdf_builder.py
    |                                       |
    +----> config.py <-----+                |
    |      (配置中心)       |                |
    |                      |                |
    +----> hsk_vocab.py    +--- lesson_data.py
           (词汇库)              (预置数据)
```

### 2.3 技术选型表

| 领域 | 当前选型 | 理由 | 目标选型 (V2) |
|------|---------|------|--------------|
| 语言 | Python 3.10+ | 生态丰富、AI 库完善 | Python + TypeScript (前端) |
| AI 模型 | Claude Sonnet 4 | 长上下文、中文质量优 | Claude + LoRA 微调 |
| PDF 排版 | fpdf2 | 轻量级、CJK 支持好 | Typst (高质量排版) |
| NLP 分词 | jieba (可选) | 中文分词事实标准 | spaCy + 自定义模型 |
| 笔记集成 | GetNotes API | 教师已有数据源 | 多平台集成 |
| 向量存储 | 无 | MVP 阶段 | Pinecone / ChromaDB |
| 工作流 | 同步 Python | 简单直接 | Temporal (分布式) |
| 相似度 | 无 | MVP 阶段 | LaBSE (跨语言嵌入) |
| 前端 | CLI | MVP 阶段 | Streamlit → Next.js |

> 来源：Claude（Claude API）、Gemini（Typst）、Grok（spaCy）、Minimax（Pinecone+LaBSE+LangChain+Temporal）

---

## 3. 四层逐字对照翻译引擎（核心差异化）

### 3.1 设计原理

四层逐字对照翻译是本系统的核心差异化竞争力。传统中文教材只提供中文原文 + 英语翻译，
学习者无法理解中文的语序逻辑。四层方法通过增加拼音层和"逐词直译"层，让学习者
**看见中文的思维方式**。

> 来源：Claude 方案（四层翻译引擎原创设计）

### 3.2 四层定义

```
Layer 1 │ 汉字 (Chinese Characters)    │ 我 想 吃 饺子。
Layer 2 │ 拼音 (Pinyin with tones)     │ wǒ xiǎng chī jiǎozi.
Layer 3 │ 逐词直译 (Word-by-Word)      │ I want eat dumpling.
Layer 4 │ 自然英语 (Natural English)    │ I'd like to have dumplings.
```

**关键规则**：
- Layer 3 **必须保留中文语序**，不可调整为英语语法
- Layer 3 使用连字符连接多字词：`老师` → `old-master`，`不客气` → `not polite`
- Layer 4 是地道的英语表达，可以与 Layer 3 语序不同
- 每一句对话、每一个生词都必须提供完整四层

### 3.3 Few-Shot 直译优化

大语言模型在"字对字直译"时容易滑入自然翻译。通过 Few-Shot 示例 + XML 约束强制精准度：

> 来源：Gemini 方案（Few-Shot 直译优化，解决大模型"字对字直译"精准度问题）

```
<Few-Shot Examples>
  INPUT:  你好！
  Layer3: you good!              ✅ 正确（保留中文语序）
  Layer3: Hello!                 ❌ 错误（这是自然翻译）

  INPUT:  我是老师。
  Layer3: I am old-master.       ✅ 正确（逐词对照）
  Layer3: I am a teacher.        ❌ 错误（添加了冠词 "a"）

  INPUT:  你想吃什么？
  Layer3: you want eat what?     ✅ 正确（what 在句尾，保留中文语序）
  Layer3: What do you want?      ❌ 错误（调整为英语语序）
</Few-Shot Examples>
```

### 3.4 PDF 排版示例

```
+----------------------------------------------------+
|  小明:                                              |
|  +------------------------------------------------+|
|  | 你 想 吃 什么？                                  ||  <- Layer 1: 大号宋体
|  | nǐ xiǎng chī shénme?                           ||  <- Layer 2: 灰色拼音
|  | you want eat what?                              ||  <- Layer 3: 蓝色逐词直译
|  | -> "What would you like to eat?"                ||  <- Layer 4: 黑色自然英语
|  +------------------------------------------------+|
|                                                      |
|  David:                                              |
|  +------------------------------------------------+|
|  | 我 想 吃 饺子。                                  ||
|  | wǒ xiǎng chī jiǎozi.                           ||
|  | I want eat dumpling.                            ||
|  | -> "I'd like to have dumplings."                ||
|  +------------------------------------------------+|
+----------------------------------------------------+
```

> 已实现：`pdf_builder.py` 中 `ChinesePDF.add_dialogue()` 方法完整实现了四层对照排版，
> 含背景色块、颜色区分、自动分页检测。

---

## 4. HSK 词汇控制系统

### 4.1 HSK 3.0 等级映射

> 来源：Claude 方案（HSK 3.0 词汇控制）+ Kimi 方案（科目一分级新词上限表）

| HSK 等级 | 总词汇量 | 常规课新词 | 新词硬上限 | CEFR | 对应教材 |
|----------|---------|-----------|-----------|------|---------|
| HSK 1 | 300 | 8 | 10 | A1 | Book 1: 零基础入门 |
| HSK 2 | 497 | 10 | 12 | A2 | Book 2: 日常会话 |
| HSK 3 | 988 | 12 | 15 | B1 | Book 3: 职场中文 |

复习课特殊规则：新词上限 **2 个**，重点巩固已学词汇。

### 4.2 新词控制公式

> 来源：Gemini 方案（数学词汇控制公式）

```
V_lesson ⊆ (V_HSK_target ∪ V_history ∪ V_new_cultural)

其中:
  V_lesson       = 本课出现的所有词汇集合
  V_HSK_target   = 目标 HSK 等级词汇表
  V_history      = 前序课程已教授词汇的累积集合
  V_new_cultural = 因文化注释必须引入的超纲词（允许少量）

新词约束:
  |V_lesson \ V_history| ≤ MAX_NEW_WORDS(level)

复用约束:
  |V_lesson ∩ V_history| / |V_lesson| ≥ 0.30   (至少复用30%已学词汇)
```

### 4.3 软限制 + 警告机制

系统实现两级控制：

| 控制级别 | 条件 | 行为 |
|---------|------|------|
| **软限制** (推荐值) | 新词数 > `new_words_per_lesson` | 输出 WARNING，允许继续 |
| **硬限制** (上限) | 新词数 > `max_new_words` | 阻断生成，触发替换策略 |
| **复用检查** | 复用率 < 30% | 输出 WARNING，建议增加复习词 |

> 已实现：`generator.py` 中 `_validate_lesson()` 方法执行新词数量检查。
> `config.py` 定义了 `CONSISTENCY_RULES` 配置项。

### 4.4 分级新词上限表

> 来源：Kimi 方案（科目一分级新词上限表）

| 课程阶段 | CEFR | 每课新词上限 | 说明 |
|---------|------|------------|------|
| A1 入门 (L1-L5) | A1 | 8-10 | 高频生存词汇优先 |
| A1+ 过渡 (L6-L10) | A1+ | 10-12 | 开始引入功能词 |
| A2 基础 (L11-L15) | A2 | 12-15 | 场景词汇扩展 |
| 复习课 (L5/L10/L15) | — | ≤2 | 巩固为主 |

---

## 5. 课程图谱设计

### 5.1 多线课程结构

> 来源：Minimax 方案（双引擎架构）+ GPT 方案（课程图谱）

```
                       Z Turns Chinese 系列
                              |
              +---------------+---------------+
              |               |               |
         零基础引擎(L1)   商务引擎(L2-L3)   旅行线(计划中)
              |               |               |
         Book 1           Book 3           Book T
         HSK 1            HSK 3            HSK 2
         15课             15课              10课
         零基础入门        职场中文          旅行中文
```

### 5.2 Course → Unit → Lesson 层级

> 来源：GPT 方案（课程图谱：Course→Unit→Lesson→Can-do/Scenario/Vocab/Phrases/Grammar/Dialogue/Exercises/TeacherNotes）

```
Course (Book 1: 零基础入门)
  |
  +-- Unit 1: 基本问候 (L1-L5)
  |     |
  |     +-- Lesson 1: 你好！
  |     |     +-- Can-Do: "能用中文打招呼和告别"
  |     |     +-- Scenario: 初次见面
  |     |     +-- New Vocab: 8 words (你/好/我/是/谢谢/不客气/老师/再见)
  |     |     +-- Grammar: SVO word order
  |     |     +-- Dialogue: Meeting for the first time
  |     |     +-- Culture Note: The Magic of 你好
  |     |     +-- Exercises: 4 (fill_blank/translate/word_by_word/match)
  |     |     +-- Tony's Teaching Tip
  |     |
  |     +-- Lesson 2: 你叫什么名字？
  |     +-- Lesson 3: 我的家人
  |     +-- Lesson 4: 数字
  |     +-- Lesson 5: 复习一 (Review)
  |
  +-- Unit 2: 日常生活 (L6-L10)
  |     +-- Lesson 6-9: 时间/日常/餐厅/购物
  |     +-- Lesson 10: 复习二
  |
  +-- Unit 3: 拓展交际 (L11-L15)
        +-- Lesson 11-14: 天气/爱好/方位/电话
        +-- Lesson 15: 总复习
```

### 5.3 ACTFL/CEFR 对齐

> 来源：GPT 方案（ACTFL Can-Do Statements + CEFR 对齐）

| Book | HSK | CEFR | ACTFL | Can-Do Statement 示例 |
|------|-----|------|-------|---------------------|
| Book 1 | 1 | A1 | Novice Mid-High | 能进行基本社交问候、自我介绍、点餐、购物 |
| Book 2 | 2 | A2 | Intermediate Low | 能描述日常生活、表达简单意见、处理常见事务 |
| Book 3 | 3 | B1 | Intermediate Mid | 能参与职场对话、理解新闻大意、书写简单报告 |

### 5.4 Book 1 完整课程规划（15 课）

> 来源：Claude 方案（15 课 Book 1 完整课程规划）| 已实现于 `config.py` `BOOK1_LESSONS`

| ID | 英文标题 | 中文标题 | 主题 | 语法重点 | 新词 | 复习来源 |
|----|---------|---------|------|---------|------|---------|
| L1 | Hello! | 你好！ | greetings | SVO word order | 8 | — |
| L2 | What's Your Name? | 你叫什么名字？ | introductions | 什么 question | 8 | L1 |
| L3 | My Family | 我的家人 | family | 的 (possession) | 8 | L1,L2 |
| L4 | Numbers | 数字 | numbers | Numbers + 量词 | 8 | L1-L3 |
| L5 | Review 1 | 复习一 | review | Review L1-4 | 2 | L1-L4 |
| L6 | What Time Is It? | 几点了？ | time | 几 + 量词 | 8 | L4 |
| L7 | My Daily Routine | 我的一天 | daily_routine | Time expressions | 8 | L6 |
| L8 | At the Restaurant | 在餐厅 | restaurant | 想 + Verb | 8 | L4,L6 |
| L9 | Going Shopping | 去超市 | shopping | 多少钱 | 8 | L8 |
| L10 | Review 2 | 复习二 | review | Review L6-9 | 2 | L6-L9 |
| L11 | How's the Weather? | 天气怎么样？ | weather | Adj predicates | 8 | L7 |
| L12 | I Like... | 我喜欢…… | hobbies | 喜欢 + V/N | 8 | L8,L9 |
| L13 | Where Is It? | 在哪里？ | directions | 在 + location | 8 | L9 |
| L14 | Making a Phone Call | 打电话 | phone | 能/可以 | 8 | L2 |
| L15 | Final Review | 总复习 | review | Full book review | 0 | L1-L14 |

---

## 6. 句型记忆库（Phrase Memory）

### 6.1 设计原理

> 来源：GPT 方案（句型记忆库作为核心资产）+ Claude 方案（一致性规则引擎）

句型记忆库确保同一个中文表达在整套教材中始终采用相同的四层翻译。
例如 `谢谢` 一旦在 L1 被翻译为 `thank-thank`，后续所有课次都必须使用这个直译，
而非 `grateful-grateful` 或其他变体。

### 6.2 数据结构

```
PhraseMemory = {
    "谢谢": {
        "pinyin": "xièxie",
        "word_by_word": "thank-thank",
        "natural_en": "thank you",
        "first_appeared": "L1",
        "pos": "v",
        "hsk_level": 1,
        "usage_count": 12,          // 在教材中出现次数
        "contexts": ["greeting", "restaurant", "shopping"]
    },
    "不客气": {
        "pinyin": "bú kèqi",
        "word_by_word": "not polite",
        "natural_en": "you're welcome",
        "first_appeared": "L1",
        "pos": "phrase",
        "hsk_level": 1,
        "usage_count": 6,
        "contexts": ["greeting", "restaurant"]
    },
    ...
}
```

### 6.3 句型复用流程

```
新课生成请求
      |
      v
查询 PhraseMemory
      |
  +---+---+
  |       |
已有记录  无记录
  |       |
  v       v
使用已有翻译  AI生成新翻译
              |
              v
          Few-Shot验证
              |
              v
          写入 PhraseMemory
              |
              v
          更新 usage_count
```

### 6.4 冲突解决策略

| 场景 | 策略 |
|------|------|
| AI 生成了不同的直译 | 以 PhraseMemory 中首次出现的翻译为准 |
| 同一词在不同语境需要不同翻译 | 记录为多义项，按 context 区分 |
| 教师手动修改了翻译 | 人工修改覆盖 AI 生成，全局更新 |

> 当前状态：⏳ PhraseMemory 尚未实现持久化存储，词汇复用逻辑在 `ai_engine.py`
> 的 `previous_vocab` 参数中以列表形式传递。

---

## 7. AI Prompt 工程

### 7.1 XML 结构化 Prompt 架构（5 模块）

> 来源：Gemini 方案（结构化 XML Prompt 链：Role/Context/Constraints/Task/Output_Format 五模块）

系统中所有 AI Prompt 均采用 XML 标签结构化，确保生成结果的确定性和一致性：

```xml
<Role>
  中文教育专家角色定义，明确核心教学方法（四层翻译）
</Role>

<Context>
  当前任务上下文：HSK等级、课次编号、前序词汇列表、教学素材
</Context>

<Constraints>
  硬性约束条件：
  1. 严格遵循 HSK 3.0 词汇标准
  2. 每句中文必须四层翻译完整
  3. 逐词直译必须保持中文语序
  4. 新词上限控制
  5. 输出必须为合法 JSON
</Constraints>

<Task>
  具体任务指令（生成课程/分析素材/规划课程等）
</Task>

<Output_Format>
  精确的 JSON Schema 定义，包含字段名、类型、示例
</Output_Format>
```

> 已实现：`ai_engine.py` 中定义了 4 个 System Prompt（`LESSON_SYSTEM_PROMPT`、
> `COURSE_PLAN_SYSTEM_PROMPT`、`MARKET_ANALYSIS_SYSTEM_PROMPT`、`MATERIAL_SYSTEM_PROMPT`），
> 全部采用 XML 标签结构。

### 7.2 词汇控制数学公式嵌入

在 Prompt 中直接嵌入量化约束，防止 AI "自由发挥"：

```
Requirements:
- Max {max_new} new words (HSK {hsk_level} level only)
- {core_dialogue_rounds}-8 lines per dialogue
- Characters to use: 小明, 小红, Tony老师, David, Mary

Previously taught vocabulary (reuse at least 30% in dialogue):
- 你, 好, 我, 是, 谢谢, 不客气, 老师, 再见 ...
```

### 7.3 Auto-Correction Prompt

> 来源：Gemini 方案（自动纠错提示词）

在生成后追加自动纠错环节，让 AI 检验自身输出：

```
<Auto-Correction>
Before returning, verify:
1. Every Chinese sentence has exactly 4 translation layers
2. Word-by-word English preserves Chinese word order (NOT English order)
3. New word count does not exceed {max_new}
4. All words are within HSK {level} vocabulary
5. JSON is valid and matches the schema
6. No PII or sensitive content in dialogues

If any check fails, fix the issue and regenerate that section.
</Auto-Correction>
```

### 7.4 StyleDNA 风格注入

> 来源：Minimax 方案（StyleDNA 风格提取，5 维度）

StyleDNA 从教师的真实教学素材中提取个人风格特征，注入 AI 生成过程：

| 维度 | 说明 | 示例 |
|------|------|------|
| **词汇 DNA** | 教师偏好的解释用词 | 偏好使用"think of it as..."而非"consider..." |
| **节奏 DNA** | 句子长度和对话节奏 | 短句为主，每轮 2-3 句 |
| **对比 DNA** | 中英对比解释风格 | 常用"Unlike English..."开头 |
| **纠错 DNA** | 纠正常见错误的方式 | "Common mistake: ..." |
| **文化 DNA** | 文化注释的深度和方向 | 偏好现代科技生活实例 |

> 当前状态：⏳ StyleDNA 尚未实现。计划在 V2 中通过分析教师的 GetNotes 笔记
> 自动提取风格向量。

---

## 8. 功能模块详细设计

### 8.1 数据导入模块（ingest-service）

**文件**：`content_extractor.py` + `getnotes_client.py`

**职责**：从多种来源采集原始教学素材

```
数据导入模块
    |
    +-- URL提取
    |     +-- HTTP GET + HTML解析
    |     +-- 自动编码检测 (UTF-8/GB18030/GBK/Big5)
    |     +-- HTML标签剥离 (_HTMLTextExtractor)
    |     +-- 中文文本提取 (extract_chinese_text)
    |
    +-- PDF提取
    |     +-- PyPDF2 / pdfplumber (外部依赖)
    |     +-- macOS textutil (系统工具)
    |     +-- 回退：macOS mdls 元数据提取
    |
    +-- 文件导入
    |     +-- .txt / .md：直接读取
    |     +-- .docx：XML 解析
    |     +-- 自动编码检测
    |
    +-- GetNotes集成
    |     +-- 音频转写 → audio.original
    |     +-- 链接笔记 → web_page.content
    |     +-- 文本笔记 → note.content
    |
    +-- 内容分析
          +-- CJK字符检测与统计
          +-- 语法模式识别 (13种模式)
          +-- 填充词过滤 (中英文)
          +-- 时间戳和说话人标记清理
```

**已实现功能清单**：

| 功能 | 状态 | 说明 |
|------|------|------|
| URL 文本提取 | ✅ | HTTP GET + HTML 解析 |
| PDF 文本提取 | ✅ | 多后端回退 |
| 文件文本提取 | ✅ | txt/md/docx |
| 中文文本识别 | ✅ | CJK Unicode 范围检测 |
| 语法模式分析 | ✅ | 13 种中文语法模式 |
| 编码自动检测 | ✅ | UTF-8/GB18030/GBK/Big5/Latin-1 |

### 8.2 隐私过滤模块（privacy-service）

**文件**：`privacy_filter.py`

**职责**：检测并脱敏原始素材中的 PII（个人可识别信息）

> 来源：Grok 方案（隐私过滤优先架构、GDPR/CCPA 合规）+ Kimi 方案（发布闸门 PII 终检）

```
原始文本输入
      |
      v
+-------------------+
| 1. Regex PII扫描  |  -> 姓名 / 电话 / 邮箱 / 地址
+-------------------+
      |
      v
+-------------------+
| 2. 敏感词检测      |  -> 政治 / 政策 / 选举 等
+-------------------+
      |
      v
+-------------------+
| 3. 匿名化替换      |
|   姓名 -> [Student A]       |
|   电话 -> [REMOVED]         |
|   邮箱 -> [REMOVED]         |
|   地址 -> [a city]          |
|   公司 -> [an organization] |
|   敏感内容 -> [SENSITIVE CONTENT REMOVED] |
+-------------------+
      |
      v
+-------------------+
| 4. 扫描报告生成    |  -> { total_findings, high_risk, categories, details }
+-------------------+
      |
      v
脱敏文本输出
```

**已实现**：

| 功能 | 状态 | 说明 |
|------|------|------|
| Regex PII 检测 | ✅ | 姓名/电话/邮箱/地址 4 种模式 |
| 敏感词过滤 | ✅ | 中英文政治敏感词 11 个 |
| 自动匿名化替换 | ✅ | 6 种替换模板 |
| 扫描报告生成 | ✅ | JSON 格式详细报告 |
| Demo 演示 | ✅ | `--privacy-demo` 命令 |
| spaCy NER 深度检测 | ⏳ | 计划 V1 实现 |
| OpenAI Moderation API | ⏳ | Grok 方案建议，计划 V2 |

### 8.3 教学知识提取模块（asset-service）

**文件**：`ai_engine.py` → `process_raw_material()` 方法

**职责**：从脱敏后的文本中提取结构化教学资产

```
脱敏文本
    |
    v
Claude AI (MATERIAL_SYSTEM_PROMPT)
    |
    +-- vocabulary[]        词汇提取 (chinese/pinyin/word_by_word/english/pos)
    +-- dialogue_snippets[] 对话片段 (context + lines)
    +-- grammar_patterns[]  语法模式 (pattern/explanation/examples)
    +-- cultural_topics[]   文化主题 (topic/notes)
```

### 8.4 AI 内容生成模块（generation-service）

**文件**：`ai_engine.py`

**职责**：调用 Claude API 生成完整课程内容

| 方法 | 功能 | System Prompt | 输出 |
|------|------|---------------|------|
| `generate_lesson()` | 生成完整单课 | LESSON_SYSTEM_PROMPT | lesson dict (JSON) |
| `generate_course_plan()` | 生成课程规划 | COURSE_PLAN_SYSTEM_PROMPT | lesson plan array |
| `analyze_market_demand()` | 市场需求分析 | MARKET_ANALYSIS_SYSTEM_PROMPT | analysis dict |
| `process_raw_material()` | 素材结构化 | MATERIAL_SYSTEM_PROMPT | extracted assets |
| `improve_lesson()` | 课程优化迭代 | LESSON_SYSTEM_PROMPT | improved lesson |

**API 调用架构**：
- 优先使用 `anthropic` SDK
- 回退到 `urllib.request` 直接 HTTP 调用（零外部依赖）
- 模型：`claude-sonnet-4-20250514`
- 最大 Token：8192（课程生成）/ 4096（规划/素材）/ 2048（分析）

### 8.5 GetNotes 集成模块

**文件**：`getnotes_client.py`

**职责**：与汐笔笔记 API 集成，拉取教师教学笔记和录音转写

| API 方法 | 端点 | 说明 |
|---------|------|------|
| `list_notes()` | GET /resource/note/list | 分页列出笔记 |
| `get_note()` | GET /resource/note/detail | 获取单条笔记详情 |
| `save_note()` | POST /resource/note/save | 保存新笔记 |
| `get_note_task_progress()` | POST /resource/note/task/progress | 查询异步任务进度 |
| `list_topics()` | GET /resource/knowledge/list | 列出知识库 |
| `list_topic_notes()` | GET /resource/knowledge/notes | 知识库下笔记列表 |
| `get_live_detail()` | GET /resource/knowledge/live/detail | 获取直播/录音详情 |
| `get_quota()` | GET /resource/rate-limit/quota | 查询 API 配额 |

**高级辅助方法**：

| 方法 | 说明 |
|------|------|
| `search_notes_by_keyword()` | 全量遍历 + 关键词匹配搜索 |
| `get_all_notes_for_topic()` | 自动分页获取知识库全部笔记 |
| `extract_teaching_content()` | 按优先级提取教学内容（音频>链接>文本）|
| `wait_for_link_note()` | 轮询等待异步链接笔记处理完成 |

**容错设计**：
- QPS 限流（< 2 QPS，请求间隔 ≥ 0.55s）
- 5xx 错误自动重试（最多 3 次，线性退避）
- API 错误码解析（`GetNoteAPIError` 结构化异常）

### 8.6 内容提取模块（URL/PDF）

**文件**：`content_extractor.py`

已在 8.1 详述。核心能力：

- **13 种中文语法模式检测**：SVO / 的 / 了 / 吗 / 什么 / 怎么 / 比 / 把 / 被 / 在+地点 / 想+V / 能+V / 数+量
- **填充词过滤**：中文 11 种（嗯/啊/呃/那个/就是说...）+ 英文 10 种
- **时间戳清理**：支持 `[00:12]` / `(1:23:45)` / `00:12` 三种格式
- **说话人标签解析**：支持 `Speaker N:` / `老师:` / `Student:` 等格式

### 8.7 一致性 QA 模块（qa-service）

**文件**：`generator.py` → `_validate_lesson()` + `config.py` → `CONSISTENCY_RULES`

**职责**：确保生成内容的质量和一致性

**当前检查项**：

| 检查项 | 配置键 | 规则 | 状态 |
|--------|--------|------|------|
| 新词数量 | `max_new_words_regular` | 常规课 ≤ 10 | ✅ |
| 复习课新词 | `max_new_words_review` | 复习课 ≤ 2 | ✅ |
| 词汇复用率 | `min_vocab_reuse_ratio` | ≥ 30% | ⏳ |
| 语法递进 | `grammar_must_increase` | 单调递增 | ⏳ |
| 文化不重复 | `no_duplicate_culture` | 主题不重复 | ⏳ |
| 角色名固定 | `fixed_character_names` | 5 个固定角色 | ✅ |

### 8.8 PDF 排版引擎（export-service）

**文件**：`pdf_builder.py`

**职责**：将结构化课程数据渲染为专业 PDF 教材

**排版组件**：

| 组件 | 方法 | 说明 |
|------|------|------|
| 课次标题页 | `add_title_page()` | 书名 + 课号 + 中英标题 + HSK 徽章 |
| 学习目标 | `add_learning_goals()` | 编号列表 |
| 生词表 | `add_vocabulary_section()` | 五列表格（汉字/拼音/直译/英语/词性）|
| 复习词汇 | `add_review_words()` | 四列紧凑布局 |
| 四层对话 | `add_dialogue()` | 带说话人标签的四层对照区块 |
| 语法讲解 | `add_grammar_section()` | 蓝色边框知识框 |
| 文化小贴士 | `add_culture_note()` | 绿色边框文化框 |
| 练习题 | `add_exercises()` | 支持 5 种题型 |
| 答案页 | `add_answer_key()` | 单独页面 |
| 页眉页脚 | `header()` / `footer()` | 书名 + 课名 + 页码 |

**CJK 字体处理**：
- 优先级：Hiragino Sans GB → Songti → PingFang → STHeiti
- Unicode 字体：Arial Unicode（同时支持 Latin + CJK）
- 回退：Helvetica（不支持 CJK，最后手段）

**样式配置** (来自 `config.py` `PDF_STYLE`)：
- 页面：A4，四边距 25mm
- 中文字号：18pt / 拼音：10pt / 直译：11pt / 自然英语：12pt
- 颜色方案：蓝色主色(#0055CC) / 灰色辅助 / 红色强调 / 绿色文化

### 8.9 AI 指挥官模块（commander）

**文件**：`ai_commander.py`

**职责**：自动编排 8 阶段教材生成流水线

> 来源：综合所有方案的流水线设计

```
  用户下达 Mission Brief
  "Create a 10-lesson pinyin course for beginners"
        |
        v
  [1/8] 任务解析 (Mission Parsing)
        |  解析自然语言，提取: theme, hsk_level, num_lessons
        v
  [2/8] 市场分析 (Market Analysis)
        |  评估课程主题的市场需求 (1-10分)
        v
  [3/8] 课程规划 (Course Planning)
        |  生成渐进式课程大纲，含词汇螺旋
        v
  [4/8] 素材采集 (Material Gathering)
        |  从 GetNotes / URL / PDF / 文件 拉取素材
        v
  [5/8] 隐私过滤 (Privacy Filtering)
        |  PII扫描 + 自动脱敏
        v
  [6/8] 课程生成 (Lesson Generation)
        |  逐课调用 AI Engine，传入 previous_vocab
        v
  [7/8] 质量验证 (Quality Validation)
        |  HSK合规 + 新词数量 + 一致性检查
        v
  [8/8] PDF 输出 (PDF Production)
        |  生成封面 + 各课 PDF
        v
  完成! 输出目录: output/
```

**核心特性**：
- **子系统懒加载**：AI Engine / GetNotes / ContentExtractor 按需初始化，缺失则优雅降级
- **素材源管理**：支持 6 种源类型（url/pdf/file/text/getnotes_topic/getnotes_note）
- **管线状态追踪**：完整记录各阶段执行状态、时间、错误
- **日志系统**：带时间戳的操作日志，便于调试

### 8.10 双引擎策略（零基础 + 商务）

> 来源：Minimax 方案（双引擎架构：零基础引擎 L1 + 商务引擎 L2-L3）

| 引擎 | 适用等级 | 特点 | 状态 |
|------|---------|------|------|
| **零基础引擎** | HSK 1 (A1) | 生存词汇优先、大量重复练习、简短对话、夸张的文化对比 | ✅ 已实现 |
| **商务引擎** | HSK 2-3 (A2-B1) | 职场场景、正式用语、较长对话、邮件/会议模板 | ⏳ 待开发 |

双引擎共享同一套 Prompt 架构和词汇控制系统，但在以下维度有差异化配置：

| 配置项 | 零基础引擎 | 商务引擎 |
|--------|-----------|---------|
| 对话轮数 | 6-8 轮 | 8-12 轮 |
| 语法解释风格 | 大量类比、"想象成..." | 规则优先、图表辅助 |
| 文化注释 | 日常生活、趣味事实 | 商务礼仪、谈判文化 |
| 练习类型 | 匹配/填空/翻译 | 情景对话/邮件写作/角色扮演 |

---

## 9. 数据模型设计

### 9.1 分层存储

> 来源：GPT 方案（分层存储设计）+ Grok 方案（隐私分层）

```
+------------------+     +------------------+     +------------------+
|   Raw Vault      | --> |   Safe Corpus    | --> | Curriculum Assets|
|   原始素材库      |     |   安全语料库      |     |   课程资产库      |
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
| raw_notes        |     | safe_texts       |     | courses          |
|   .source_type   |     |   .clean_text    |     | units            |
|   .raw_content   |     |   .pii_report    |     | lessons          |
|   .fetched_at    |     |   .source_ref    |     | vocab_ledger     |
|                  |     |                  |     | phrase_memory    |
| raw_urls         |     | extracted_vocab  |     | grammar_bank     |
|   .url           |     |   .chinese       |     | error_bank       |
|   .html_content  |     |   .pinyin        |     | lesson_versions  |
|   .fetched_at    |     |   .translations  |     |                  |
|                  |     |                  |     | export_files     |
| raw_pdfs         |     | extracted_grammar|     |   .file_path     |
|   .file_path     |     |   .pattern       |     |   .format        |
|   .text_content  |     |   .examples      |     |   .created_at    |
+------------------+     +------------------+     +------------------+
```

### 9.2 核心数据表设计

> 来源：GPT 方案（15+ 表完整 SQL DDL）

**说明**：当前 v3.0 使用内存数据结构 + 文件系统，以下为目标数据库设计。

| 表名 | 说明 | 关键字段 |
|------|------|---------|
| `courses` | 课程/丛书 | id, title, hsk_level, cefr, description |
| `units` | 单元 | id, course_id, unit_num, title, theme |
| `lessons` | 课次 | id, unit_id, lesson_num, title_en, title_zh, topic |
| `lesson_versions` | 课次版本 | id, lesson_id, version, content_json, status |
| `vocab_ledger` | 词汇账本 | id, chinese, pinyin, wbw, english, hsk_level, first_lesson_id |
| `phrase_memory` | 句型记忆 | id, chinese, pinyin, wbw, english, first_lesson_id, usage_count |
| `grammar_points` | 语法点 | id, lesson_id, title, explanation, examples_json |
| `culture_notes` | 文化注释 | id, lesson_id, title, content |
| `exercises` | 练习题 | id, lesson_id, type, instruction, question, answer |
| `raw_materials` | 原始素材 | id, source_type, raw_content, pii_status |
| `safe_corpus` | 脱敏语料 | id, material_id, clean_text, pii_report_json |
| `export_files` | 导出文件 | id, lesson_version_id, format, file_path |
| `error_bank` | 错误库 | id, error_type, chinese, wrong_translation, correct_translation |
| `style_dna` | 风格配置 | id, teacher_id, dimension, vector_json |
| `audit_log` | 审核日志 | id, action, entity_type, entity_id, reviewer, timestamp |

### 9.3 lesson_versions.content_json Schema

> 来源：GPT 方案（完整 JSON Schema 定义）

```json
{
  "id": 1,
  "title_en": "Hello!",
  "title_zh": "你好！",
  "book": "Book 1",
  "hsk_level": 1,
  "learning_goals": ["string", "..."],
  "new_words": [
    ["chinese", "pinyin", "word_by_word", "english", "pos"]
  ],
  "dialogues": [
    {
      "title": "string",
      "lines": [
        ["speaker", "chinese", "pinyin", "word_by_word", "english"]
      ]
    }
  ],
  "grammar_points": [
    {
      "title": "string",
      "explanation": "string (multi-line)"
    }
  ],
  "culture_note": {
    "title": "string",
    "text": "string"
  },
  "exercises": [
    {
      "type": "fill_blank|translate|word_by_word|match|reorder",
      "instruction": "string",
      "question": "string",
      "answer": "string",
      "pairs": [["chinese", "english"]]
    }
  ],
  "review_words": [
    ["chinese", "pinyin", "word_by_word", "english"]
  ]
}
```

> 已实现：`lesson_data.py` 中的 `LESSONS` 字典完全遵循此 Schema。
> `ai_engine.py` 中的 `_normalize_lesson()` 方法确保 AI 输出符合此格式。

### 9.4 实体关系图

```
courses 1---* units 1---* lessons 1---* lesson_versions
                              |
                +-------------+-------------+-------------+
                |             |             |             |
                v             v             v             v
          grammar_points  culture_notes  exercises  vocab_ledger
                                                        |
                                                        v
                                                   phrase_memory

raw_materials 1---1 safe_corpus
lesson_versions 1---* export_files
lessons *---* vocab_ledger (多对多: lesson_vocab_usage)
```

---

## 10. 核心流程设计

### 10.1 端到端主流程

> 来源：GPT 方案（端到端工作流图）+ Kimi 方案（微服务架构 6 服务）

```
教师                    系统                              AI引擎
  |                      |                                  |
  |  1. 下达 Mission     |                                  |
  | ------------------> |                                  |
  |                      |  2. 解析意图                     |
  |                      | ------+                         |
  |                      |       |                         |
  |                      |  3. 市场分析请求                 |
  |                      | -------------------------------->|
  |                      |  4. 返回分析结果                 |
  |                      | <--------------------------------|
  |                      |                                  |
  |                      |  5. 课程规划请求                 |
  |                      | -------------------------------->|
  |                      |  6. 返回课程大纲                 |
  |                      | <--------------------------------|
  |                      |                                  |
  |                      |  7. 采集素材                     |
  |                      | ------+                         |
  |                      |       | GetNotes/URL/PDF        |
  |                      | <-----+                         |
  |                      |                                  |
  |                      |  8. PII 过滤                     |
  |                      | ------+                         |
  |                      | <-----+                         |
  |                      |                                  |
  |                      |  9. 逐课生成 (循环)              |
  |                      | -------------------------------->|
  |                      | <--------------------------------|
  |                      |                                  |
  |                      | 10. QA 验证                      |
  |                      | ------+                         |
  |                      | <-----+                         |
  |                      |                                  |
  |                      | 11. PDF 渲染                     |
  |                      | ------+                         |
  |                      | <-----+                         |
  |                      |                                  |
  | 12. 返回结果         |                                  |
  | <------------------- |                                  |
```

### 10.2 发布闸门流程

> 来源：Kimi 方案（发布闸门流程：PII终检→一致性QA→人工审核→允许导出）

```
课程生成完成
      |
      v
+-------------------+
| Gate 1: PII 终检  |  --> 扫描最终文本，确认无PII残留
+-------------------+
      | PASS
      v
+-------------------+
| Gate 2: 一致性 QA |  --> 词汇数量、HSK合规、格式完整性
+-------------------+
      | PASS
      v
+-------------------+
| Gate 3: 人工审核  |  --> (V2) 审核控制台，教师确认
+-------------------+
      | APPROVE
      v
+-------------------+
| Gate 4: 允许导出  |  --> 生成 PDF，写入 export_files
+-------------------+
      |
      v
  最终 PDF 输出

任何闸门 FAIL:
  --> 记录原因到 audit_log
  --> 触发回退策略（见 10.3）
  --> 通知教师
```

### 10.3 失败回退策略

> 来源：Kimi 方案（失败回退策略）

| 失败场景 | 回退策略 | 重试 |
|---------|---------|------|
| **PII 漏检** | 阻断输出，标记为 `needs_review`，人工介入 | 不自动重试 |
| **新词超限** | 自动替换超限词为已学词汇，重新生成对话 | 自动重试 2 次 |
| **中英不对齐** | 标记问题行，请求 AI 单独修正该句 | 自动重试 2 次 |
| **JSON 解析失败** | 提取 markdown fence 内容，重试解析 | 自动重试 1 次 |
| **API 超时** | 指数退避重试 | 自动重试 3 次 |
| **所有重试耗尽** | 降级为离线模式（使用预置数据），通知用户 | 人工接管 |

> 已实现：`ai_engine.py` 中 `_extract_json()` 实现了 markdown fence 剥离。
> `getnotes_client.py` 实现了 5xx 错误自动重试 + 线性退避。

### 10.4 课次生成工作流

```
                   generate_lesson(topic, hsk, lesson_num, prev_vocab)
                              |
                              v
                   +---------------------+
                   | 1. 检查 HSK 等级    |
                   |    是否为复习课？     |
                   +----------+----------+
                              |
                   +----------+----------+
                   |                     |
                 复习课               常规课
              max_new=2           max_new=10
                   |                     |
                   +----------+----------+
                              |
                              v
                   +---------------------+
                   | 2. 构建 User Prompt |
                   |    注入 prev_vocab   |
                   |    注入 context_notes|
                   +----------+----------+
                              |
                              v
                   +---------------------+
                   | 3. 调用 Claude API  |
                   |    (LESSON_SYSTEM_  |
                   |     PROMPT)         |
                   +----------+----------+
                              |
                              v
                   +---------------------+
                   | 4. 解析 JSON 响应   |
                   |    _extract_json()  |
                   +----------+----------+
                              |
                              v
                   +---------------------+
                   | 5. 规范化数据       |
                   |    _normalize_lesson|
                   |    list -> tuple    |
                   |    设置默认值       |
                   +----------+----------+
                              |
                              v
                   +---------------------+
                   | 6. QA 验证          |
                   |    _validate_lesson |
                   +----------+----------+
                              |
                              v
                   +---------------------+
                   | 7. PDF 渲染         |
                   |    ChinesePDF       |
                   +----------+----------+
                              |
                              v
                        输出 PDF 文件
```

---

## 11. QA 质量保障体系

### 11.1 自动检查项清单

> 来源：Kimi 方案（QA 联动检查）+ GPT 方案（QA 模块）+ Claude 方案（一致性规则）

| # | 检查项 | 类型 | 严重度 | 状态 |
|---|--------|------|--------|------|
| 1 | 新词数量 ≤ 等级上限 | 计数 | ERROR | ✅ |
| 2 | 每句对话有完整四层翻译 | 完整性 | ERROR | ⏳ |
| 3 | Layer 3 保持中文语序 | 语序 | ERROR | ⏳ |
| 4 | 词汇属于目标 HSK 等级 | 合规 | WARNING | ⏳ |
| 5 | 词汇复用率 ≥ 30% | 比率 | WARNING | ⏳ |
| 6 | 语法难度单调递增 | 递进 | WARNING | ⏳ |
| 7 | 文化主题不重复 | 唯一 | WARNING | ⏳ |
| 8 | 角色名在固定列表内 | 集合 | WARNING | ⏳ |
| 9 | JSON Schema 合法 | 格式 | ERROR | ✅ |
| 10 | PII 终检通过 | 安全 | BLOCK | ⏳ |
| 11 | 句型翻译与 PhraseMemory 一致 | 一致性 | WARNING | ⏳ |
| 12 | 练习题答案正确性 | 正确性 | ERROR | ⏳ |

### 11.2 QA 通过标准

```
QA 结果分级:
  PASS   = 0 ERROR + 0 BLOCK + ≤3 WARNING
  REVIEW = 0 ERROR + 0 BLOCK + >3 WARNING  --> 建议人工审核
  FAIL   = ≥1 ERROR 或 ≥1 BLOCK            --> 阻断输出，触发重试
```

### 11.3 审核控制台设计

> 来源：Minimax 方案（智能审核控制台，红/黄/绿三级标记）

```
+================================================================+
|                    QA 审核控制台 (计划中)                         |
+================================================================+
|                                                                  |
|  课次: L8 - At the Restaurant (在餐厅)                          |
|  状态: [REVIEW] 需要人工确认                                     |
|                                                                  |
|  +------------------------------------------------------------+  |
|  | 检查项                          | 结果    | 详情            |  |
|  |---------------------------------|---------|-----------------|  |
|  | [绿] 新词数量                    | 8/10   | PASS            |  |
|  | [绿] JSON Schema                | 有效   | PASS            |  |
|  | [绿] PII 终检                    | 无发现 | PASS            |  |
|  | [黄] 词汇复用率                  | 28%    | WARNING (<30%)  |  |
|  | [黄] Layer 3 语序                | 1处疑似 | WARNING         |  |
|  | [绿] HSK 等级合规                | 全部L1 | PASS            |  |
|  +------------------------------------------------------------+  |
|                                                                  |
|  风格匹配度: 87%  [黄] 建议查看                                  |
|                                                                  |
|  [  通过  ]  [  驳回并重试  ]  [  手动编辑  ]                    |
+================================================================+
```

> 来源：Minimax 方案审核决策树：
> - 风格匹配度 > 90%：自动通过
> - 80-90%：建议查看
> - < 80%：必须审核

---

## 12. API 接口设计

### 12.1 核心 API 矩阵

> 来源：GPT 方案（11 个核心 API 端点设计）

| # | 方法 | 端点 | 说明 | 状态 |
|---|------|------|------|------|
| 1 | POST | `/api/missions` | 创建 Mission | ⏳ (CLI 已实现) |
| 2 | GET | `/api/missions/{id}/status` | 查询 Mission 状态 | ⏳ (CLI 已实现) |
| 3 | POST | `/api/courses` | 创建课程 | ⏳ |
| 4 | GET | `/api/courses/{id}/lessons` | 列出课程下课次 | ⏳ |
| 5 | POST | `/api/lessons/generate` | 生成单课 | ⏳ (CLI 已实现) |
| 6 | GET | `/api/lessons/{id}` | 获取课次详情 | ⏳ |
| 7 | PUT | `/api/lessons/{id}` | 更新课次内容 | ⏳ |
| 8 | POST | `/api/lessons/{id}/qa` | 触发 QA 检查 | ⏳ |
| 9 | POST | `/api/lessons/{id}/export` | 导出 PDF | ⏳ (CLI 已实现) |
| 10 | GET | `/api/vocab/ledger` | 查询词汇账本 | ⏳ |
| 11 | POST | `/api/materials/import` | 导入素材 | ⏳ (CLI 已实现) |

### 12.2 请求/响应示例

**POST /api/missions**

```json
// Request
{
  "brief": "Create a 10-lesson pinyin course for beginners",
  "hsk_level": 1,
  "num_lessons": 10,
  "sources": [
    {"type": "getnotes_topic", "value": "topic_abc123"},
    {"type": "url", "value": "https://example.com/chinese-lesson"}
  ]
}

// Response
{
  "mission_id": "m_20260324_001",
  "status": "running",
  "current_stage": "mission_parsing",
  "stages_total": 8,
  "stages_completed": 0,
  "created_at": "2026-03-24T10:00:00Z"
}
```

**GET /api/lessons/{id}**

```json
// Response
{
  "id": 8,
  "title_en": "At the Restaurant",
  "title_zh": "在餐厅",
  "book": "Book 1",
  "hsk_level": 1,
  "status": "approved",
  "version": 2,
  "qa_result": "PASS",
  "new_words_count": 8,
  "dialogues_count": 2,
  "export_formats": ["pdf"],
  "content": { "...完整 content_json..." }
}
```

---

## 13. 开发状态与路线图

### 13.1 已完成功能清单（v3.0 当前）

| # | 模块 | 文件 | 功能 | 状态 |
|---|------|------|------|------|
| 1 | CLI 入口 | `main.py` | 6 个命令路由（mission/generate/notes/extract/offline/status） | ✅ 已完成 |
| 2 | 配置中心 | `config.py` | HSK 等级/课程模板/一致性规则/四层定义/隐私规则/PDF 样式 | ✅ 已完成 |
| 3 | 词汇库 | `hsk_vocab.py` | HSK 1 级 12 个主题 130+ 词汇，含四层翻译 | ✅ 已完成 |
| 4 | 预置数据 | `lesson_data.py` | Lesson 1 (Hello!) + Lesson 8 (At the Restaurant) 完整数据 | ✅ 已完成 |
| 5 | PDF 排版 | `pdf_builder.py` | 四层对照排版引擎，9 种排版组件，CJK 字体支持 | ✅ 已完成 |
| 6 | 生成器 | `generator.py` | PDF 生成协调器，含基础 QA 验证 | ✅ 已完成 |
| 7 | GetNotes | `getnotes_client.py` | 8 个 API 方法 + 4 个高级辅助方法，限流+重试 | ✅ 已完成 |
| 8 | AI 引擎 | `ai_engine.py` | 6 个 Claude API 方法（含 parse_mission_brief），SDK + HTTP 回退 | ✅ 已完成 |
| 9 | 内容提取 | `content_extractor.py` | URL/PDF/文件提取，13 种语法模式检测 | ✅ 已完成 |
| 10 | 隐私过滤 | `privacy_filter.py` | PII 检测（4 模式）+ 脱敏 + 报告 | ✅ 已完成 |
| 11 | AI 指挥官 | `ai_commander.py` | 8 阶段流水线编排，子系统懒加载 | ✅ 已完成 |

### 13.2 待开发功能清单

| # | 功能 | 优先级 | 来源方案 | 状态 |
|---|------|--------|---------|------|
| 1 | PhraseMemory 持久化（SQLite/JSON） | P0 | GPT | ⏳ 待开发 |
| 2 | VocabLedger 词汇账本持久化 | P0 | GPT | ⏳ 待开发 |
| 3 | 完整 QA 检查（12 项全部实现） | P0 | Kimi+GPT | 🔄 进行中 |
| 4 | 发布闸门流程（4 道闸门） | P1 | Kimi | ⏳ 待开发 |
| 5 | StyleDNA 风格提取与注入 | P1 | Minimax | ⏳ 待开发 |
| 6 | Auto-Correction Prompt（生成后自校） | P1 | Gemini | ⏳ 待开发 |
| 7 | 商务引擎（HSK 2-3 专用模板） | P1 | Minimax | ⏳ 待开发 |
| 8 | 审核控制台（Web UI） | P2 | Minimax+Kimi | ⏳ 待开发 |
| 9 | spaCy NER 深度 PII 检测 | P2 | Grok | ⏳ 待开发 |
| 10 | Typst 高质量排版引擎 | P2 | Gemini | ⏳ 待开发 |
| 11 | Streamlit 工作台 | P2 | Claude | ⏳ 待开发 |
| 12 | 数据库持久化（PostgreSQL） | P2 | GPT | ⏳ 待开发 |
| 13 | REST API 服务（FastAPI） | P2 | GPT | ⏳ 待开发 |
| 14 | ErrorBank 错误库 | P2 | GPT | ⏳ 待开发 |
| 15 | Pinecone 向量搜索 | P3 | Minimax | ⏳ 待开发 |
| 16 | LaBSE 跨语言相似度 | P3 | Minimax | ⏳ 待开发 |
| 17 | LoRA 微调专属模型 | P3 | Minimax | ⏳ 待开发 |
| 18 | Temporal 分布式工作流 | P3 | Minimax | ⏳ 待开发 |
| 19 | Book 1 全部 15 课预置数据 | P1 | Claude | ⏳ 待开发 |
| 20 | Prompt 版本治理 | P1 | Kimi | ⏳ 待开发 |

### 13.3 Sprint 规划

> 来源：Kimi 方案（4 个 Sprint 规划）+ Minimax 方案（12 周实施路线图）

**Sprint 1 (Week 1-3): 核心资产持久化**
- [ ] PhraseMemory SQLite 实现
- [ ] VocabLedger SQLite 实现
- [ ] QA 检查完善（12 项）
- [ ] Book 1 Lesson 2-7 预置数据

**Sprint 2 (Week 4-6): 生成质量提升**
- [ ] Auto-Correction Prompt 实现
- [ ] 发布闸门流程（4 道闸门）
- [ ] 失败回退策略实现
- [ ] Prompt 版本治理
- [ ] Book 1 Lesson 8-15 预置数据

**Sprint 3 (Week 7-9): 扩展与集成**
- [ ] StyleDNA 风格提取（v1: 基于规则）
- [ ] 商务引擎（HSK 2-3 模板）
- [ ] spaCy NER PII 深度检测
- [ ] Streamlit 工作台 MVP

**Sprint 4 (Week 10-12): 产品化**
- [ ] 审核控制台（Streamlit）
- [ ] REST API（FastAPI）
- [ ] Typst 排版引擎
- [ ] 端到端测试覆盖
- [ ] 文档与用户手册

### 13.4 KPI 指标

> 来源：GPT 方案（KPI 指标体系）

| 指标 | 定义 | 目标值 |
|------|------|--------|
| **生成成功率** | 单次 API 调用成功生成合规课次的比率 | ≥ 90% |
| **QA 首次通过率** | 生成课次首次通过全部 QA 检查的比率 | ≥ 75% |
| **PII 漏检率** | 经过隐私过滤后仍残留 PII 的比率 | ≤ 1% |
| **四层完整率** | 对话句子四层翻译全部完整的比率 | 100% |
| **HSK 合规率** | 新词全部属于目标 HSK 等级的比率 | ≥ 95% |
| **词汇复用率** | 每课复用前课已学词汇的实际比率 | ≥ 30% |
| **单课生成时间** | 从请求到 PDF 输出的端到端耗时 | ≤ 60s |
| **教师满意度** | 教师对生成内容的主观评分 (1-5) | ≥ 4.0 |

---

## 14. 技术栈与部署

### 14.1 当前技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 语言 | Python | 3.10+ |
| AI 模型 | Claude Sonnet 4 | claude-sonnet-4-20250514 |
| AI SDK | anthropic (可选) | latest |
| PDF 生成 | fpdf2 | latest |
| 中文分词 | jieba (可选) | latest |
| HTTP | urllib (stdlib) | — |
| CLI | argparse (stdlib) | — |
| 笔记 API | GetNotes Open API | v1 |

**零外部依赖设计**：核心功能仅依赖 Python 标准库。`anthropic` SDK、`jieba`、`fpdf2` 均为可选依赖，
缺失时系统自动降级（HTTP 回退 / 基础分词 / 无 PDF 输出）。

### 14.2 目标技术栈

| 组件 | 当前 | V1 目标 | V2 目标 |
|------|------|---------|---------|
| 数据库 | 内存 + 文件 | SQLite | PostgreSQL |
| Web 框架 | 无 | Streamlit | FastAPI + Next.js |
| 排版引擎 | fpdf2 | fpdf2 + Typst | Typst |
| 向量数据库 | 无 | — | Pinecone / ChromaDB |
| NLP | jieba | jieba + spaCy | spaCy + 自定义模型 |
| 工作流 | 同步 Python | Celery | Temporal |
| 模型 | Claude API | Claude API | Claude + LoRA 微调 |
| 嵌入模型 | 无 | — | LaBSE |
| 部署 | 本地 CLI | Docker | Docker + K8s |

### 14.3 部署方案

**当前（开发环境）**：
```bash
# 1. 克隆项目
cd /path/to/z-turns-chinese

# 2. 安装依赖（可选）
pip install fpdf2 anthropic jieba

# 3. 配置 API Key
export ANTHROPIC_API_KEY="sk-ant-..."
export GETNOTE_API_KEY="..."
export GETNOTE_CLIENT_ID="..."

# 4. 运行
python3 main.py status              # 查看系统状态
python3 main.py offline --all       # 离线生成演示
python3 main.py mission "..."       # AI 指挥官模式
```

**目标（生产环境）**：
```
                   用户浏览器
                       |
                       v
              +------------------+
              |   Nginx 反向代理  |
              +--------+---------+
                       |
              +--------+---------+
              |   FastAPI 服务    |
              |   (API Gateway)  |
              +--------+---------+
                       |
         +-------------+-------------+
         |             |             |
         v             v             v
   +----------+  +----------+  +----------+
   | Worker 1 |  | Worker 2 |  | Worker N |
   | (Celery) |  | (Celery) |  | (Celery) |
   +----------+  +----------+  +----------+
         |             |             |
         +------+------+------+-----+
                |             |
                v             v
         +-----------+  +-----------+
         | PostgreSQL |  |  Redis    |
         | (数据)     |  | (队列)    |
         +-----------+  +-----------+
```

---

## 附录

### A. 6 大 AI 方案贡献对照表

| 方案 | 核心贡献 | 已采纳模块 |
|------|---------|-----------|
| **Claude** | 四层翻译引擎、HSK 词汇控制、15 课 Book 1 规划、PDF 排版原型、Tony 品牌、知识图谱 | `config.py`, `pdf_builder.py`, `lesson_data.py`, `ai_engine.py` |
| **Gemini** | XML Prompt 架构（5 模块）、Few-Shot 直译优化、词汇控制数学公式、Auto-Correction、Typst 建议 | `ai_engine.py` (Prompt 结构), 文档 |
| **Grok** | 隐私优先架构、PII 检测 + 脱敏、GDPR/CCPA 合规思路、市场分析数据、OpenAI Moderation API 建议 | `privacy_filter.py`, `config.py` (PRIVACY_*) |
| **Kimi** | 微服务架构（6 服务）、发布闸门流程、分级新词上限表、失败回退策略、Sprint 规划、ASCII 原型图、Prompt 版本治理 | `generator.py` (QA), `ai_commander.py` (pipeline), 文档 |
| **GPT** | 完整 PRD（86 页）、15+ 表数据库设计、课程图谱、PhraseMemory、VocabLedger、ErrorBank、JSON Schema、API 设计、KPI 体系、权限模型 | `lesson_data.py` (Schema), `ai_engine.py` (normalize), 文档 |
| **Minimax** | 双引擎架构、StyleDNA 风格提取（5 维度）、审核控制台（红/黄/绿）、审核决策树、12 周路线图 | `config.py` (LESSON_STRUCTURE), 文档 |

### B. 命令行使用手册

```
Z Turns Chinese AutoBuilder v3.0 - 命令行参考

=== 基本命令 ===

1. mission - AI 指挥官模式
   python3 main.py mission "Create a 10-lesson pinyin course"
   python3 main.py mission "商务中文教程，15课，HSK2" --hsk 2 --lessons 15
   python3 main.py mission -i                    # 交互模式
   python3 main.py mission "..." --sources URL1 URL2

2. generate - AI 单课生成
   python3 main.py generate --topic "restaurant" --hsk 1 --num 3
   python3 main.py generate --topic "ordering food" --hsk 1 --context notes.txt

3. notes - GetNotes 集成
   python3 main.py notes --list-topics           # 列出知识库
   python3 main.py notes --list-notes            # 列出最近笔记
   python3 main.py notes --search "点餐"          # 搜索笔记
   python3 main.py notes --fetch-topic TOPIC_ID  # 拉取知识库内容
   python3 main.py notes --fetch-note NOTE_ID    # 获取单条笔记
   python3 main.py notes --quota                 # 查看 API 配额

4. extract - 内容提取
   python3 main.py extract --url "https://example.com/article"
   python3 main.py extract --pdf "/path/to/file.pdf"
   python3 main.py extract --file "/path/to/notes.txt"
   python3 main.py extract --url "..." --analyze  # 提取并分析

5. offline - 离线生成（无需 API Key）
   python3 main.py offline --all                  # 生成全部预置课程
   python3 main.py offline --lesson 1             # 生成指定课
   python3 main.py offline --cover                # 生成封面

6. status - 系统状态
   python3 main.py status

=== 全局选项 ===

   python3 main.py --info                        # 显示系统配置
   python3 main.py --privacy-demo                # 隐私过滤演示
```

### C. 环境配置指南

```bash
# ============================================================
# 必需：Python 3.10+
# ============================================================
python3 --version  # 确认版本

# ============================================================
# 可选依赖安装
# ============================================================
pip install fpdf2       # PDF 生成（离线模式必需）
pip install anthropic   # Claude SDK（可选，有 HTTP 回退）
pip install jieba       # 中文分词（可选，增强内容分析）

# ============================================================
# 环境变量配置
# ============================================================

# Claude AI Engine（AI 生成模式必需）
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# GetNotes 集成（笔记拉取必需）
export GETNOTE_API_KEY="your-getnote-api-key"
export GETNOTE_CLIENT_ID="your-client-id"

# ============================================================
# 快速验证
# ============================================================
cd /path/to/z-turns-chinese
python3 main.py status            # 检查所有集成状态
python3 main.py offline --all     # 验证 PDF 生成能力
python3 main.py --info            # 查看课程配置

# ============================================================
# CJK 字体要求（macOS 自动检测系统字体）
# ============================================================
# 系统会自动检测以下字体（按优先级）：
#   1. Hiragino Sans GB (/System/Library/Fonts/)
#   2. Songti           (/System/Library/Fonts/Supplemental/)
#   3. PingFang         (/System/Library/Fonts/)
#   4. STHeiti          (/System/Library/Fonts/)
#   5. Arial Unicode    (/System/Library/Fonts/Supplemental/)
```

---

> **文档维护说明**：
> 本文档由 Claude Opus 4.6 基于项目代码和 6 份 AI 技术方案综合生成。
> 随着项目迭代，请同步更新各模块的实现状态标记。
>
> 状态标记说明：✅ 已完成 | 🔄 进行中 | ⏳ 待开发
