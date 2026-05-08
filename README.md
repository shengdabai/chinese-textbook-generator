# Chinese Textbook Generator · 中文教材生成工具

A production-grade AI pipeline for generating structured Chinese language textbooks — complete with vocabulary tables, authentic dialogues, grammar explanations, cultural notes, and PDF typesetting.

[中文说明见下方 · Chinese version below](#中文说明)

---

## What This Is

**Z Turns Chinese** is a series of topic-themed Chinese textbooks aligned to HSK vocabulary, designed for adult learners who want practical, real-world language skills. Each book covers 25 chapters across a single theme (job hunting, startups, travel, gaming, etc.), with:

- 📚 Core vocabulary with pinyin, part of speech, and usage notes
- 💬 Authentic multi-turn dialogues in classroom settings
- 📖 Grammar patterns explained in context
- 🎯 Pronunciation and tone drills
- 🌏 Cultural insight essays
- ✍️ Writing and speaking exercises
- 🧪 Self-assessment quizzes

Books 51–100 cover advanced themes: career, startup, negotiation, gaming, music, finance, clean energy, robotics, space, and more.

---

## Pipeline Architecture

```
v1-pipeline/z-turns-chinese/   ← Core AI generation engine
    main.py                    ← CLI entry point
    generator.py               ← Chapter content generator
    ai_engine.py               ← OpenAI API wrapper
    ai_commander.py            ← Prompt orchestration
    pipeline.py                ← End-to-end pipeline runner
    config.py                  ← Configuration management
    hsk_vocab.py               ← HSK vocabulary database
    course_graph.py            ← Book/chapter structure graph
    lesson_data.py             ← Lesson metadata
    pdf_builder.py             ← PDF assembly
    qa_engine.py               ← Quality assurance checks
    privacy_filter.py          ← PII scrubbing
    phrase_memory.py           ← Cross-chapter phrase consistency
    vocab_ledger.py            ← Vocabulary tracking

v3-typst/                      ← Typst-based PDF typesetting
    generate.py                ← Main generation script
    config/                    ← YAML configuration files
    parsers/                   ← Markdown/content parsers
    renderers/                 ← Typst template renderers
    filters/                   ← Content filters
    templates/                 ← Typst document templates
    tests/                     ← Test suite

generate_books_51_70.py        ← Batch generator for Books 51–70
generate_books_enhanced.py     ← Enhanced generator with content injection
compile_books_51_70.sh         ← Batch PDF compiler (Typst)
generate.sh                    ← Unified entry point
```

---

## Requirements

- **Python 3.10+**
- **OpenAI API key** (set as `OPENAI_API_KEY` environment variable)
- **[Typst](https://typst.app/)** — for PDF compilation (`brew install typst` on macOS)
- Python packages: see `v3-typst/requirements.txt`

---

## Quickstart

### 1. Clone and set up

```bash
git clone https://github.com/your-username/chinese-textbook-generator
cd chinese-textbook-generator
python -m venv .venv && source .venv/bin/activate
pip install -r v3-typst/requirements.txt
```

### 2. Set your OpenAI API key

```bash
export OPENAI_API_KEY="sk-..."
```

### 3. Generate a book

```bash
# Generate Book 51 (Job Hunter's Chinese)
python generate_books_enhanced.py 51

# Generate all books 51–70
python generate_books_enhanced.py

# Compile to PDF using Typst
./compile_books_51_70.sh
```

### 4. Generate HSK study guides (v3-typst pipeline)

```bash
./generate.sh hsk --level 1
./generate.sh hsk --level 4
```

---

## Adding Your Own Content

The generator supports plugging in your own teaching materials to supplement the AI-generated content. See `v1-pipeline/z-turns-chinese/content_source_example.py` for a full interface example.

**Quick setup:**

1. Create a CSV file with your teaching content:
   ```csv
   content
   "在面试中，你需要展示你的专业技能和沟通能力..."
   "求职的关键步骤包括：准备简历、网络联系..."
   ```

2. Update `BOOK_CONTENT_MAP` in `content_source_example.py` to point to your files.

3. Uncomment the content-loading code in `generate_books_enhanced.py`'s `generate_book()` function.

---

## Book Series: Z Turns Chinese

| Book | Title | Theme |
|------|-------|-------|
| 51 | Job Hunter's Chinese | 求职面试 Job hunting & interviews |
| 52 | Startup Chinese | 创业创新 Entrepreneurship |
| 53 | Negotiation Chinese | 商务谈判 Business negotiation |
| 54 | Business Chinese Mastery | 职业发展 Career development |
| 55 | Workplace Politics Chinese | 职场人际 Office relationships |
| 56 | Gaming in Chinese | 电竞游戏 Gaming & e-sports |
| 57 | Music in Chinese | 音乐娱乐 Music & entertainment |
| 58 | Comedy in Chinese | 脱口秀 Stand-up comedy |
| 59 | Web Novel Chinese | 网络文学 Web fiction |
| 60 | Variety Show Chinese | 综艺节目 Reality & variety shows |
| 62 | Finance in Chinese | 理财投资 Personal finance |
| 63 | Fitness in Chinese | 健身运动 Sports & fitness |
| 64 | Travel Photography Chinese | 旅行摄影 Travel & photography |
| 65 | Home Renovation Chinese | 装修家居 Home renovation |
| 66 | Electric Vehicle Chinese | 新能源汽车 EVs & auto tech |
| 67 | Clean Energy Chinese | 清洁能源 Renewable energy |
| 68 | Robotics in Chinese | 机器人AI Robotics & automation |
| 69 | Quantum Tech Chinese | 量子半导体 Quantum & semiconductors |
| 70 | Space Exploration Chinese | 航天探索 Space & aerospace |

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

---

# 中文说明

## 这是什么

**Z Turns Chinese** 是一套以话题为主线、与HSK词汇体系对齐的中文教材生成工具，专为成年学习者设计，帮助他们掌握实用、真实的中文表达能力。

每本教材包含25个章节，围绕单一主题展开（求职、创业、旅行、游戏等），内容涵盖：

- 📚 核心词汇（含拼音、词性、用法说明）
- 💬 真实课堂对话场景
- 📖 语法要点精讲
- 🎯 发音与声调练习
- 🌏 文化背景知识
- ✍️ 写作与口语练习
- 🧪 自我测评

## 快速开始

```bash
# 安装依赖
pip install -r v3-typst/requirements.txt

# 设置 OpenAI API 密钥
export OPENAI_API_KEY="sk-..."

# 生成第51本书（求职中文）
python generate_books_enhanced.py 51

# 生成全套书籍（51-70）
python generate_books_enhanced.py

# 编译为 PDF（需要安装 Typst）
./compile_books_51_70.sh
```

## 添加自己的内容

参考 `v1-pipeline/z-turns-chinese/content_source_example.py` 了解如何将自己的教学内容（CSV文件、文本笔记等）接入到生成流程中，替代内置的内容接口。

## 技术架构

详见本文档顶部的架构说明（英文）及各子目录中的 README 文件。

## 许可证

MIT 开源许可证。
