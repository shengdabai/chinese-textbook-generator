# chinese-textbook-generator

AI pipeline + multi-LLM specs for generating HSK-aligned, theme-based Chinese textbooks — vocab, dialogues, grammar, print-ready PDFs.

## Business Context

- **Category:** education product
- **Audience:** learners, teachers, parents, and education operators who need a clearer learning or exam-prep workflow.
- **Repository status:** Public repository. Keep examples, docs, and issues free of credentials, private data, and machine-specific paths.
- **Topics:** ai, chinese-learning, content-generation, education, hsk, llm, textbook, typst

## What This Project Is For

- AI pipeline + multi-LLM specs for generating HSK-aligned, theme-based Chinese textbooks — vocab, dialogues, grammar, print-ready PDFs.
- Give users a concrete learning workflow instead of a loose collection of content.
- Make practice, feedback, review, or recommendation steps easier to repeat.

## Where It Fits

This repository supports productized learning workflows: diagnostic input, guided practice, review loops, and clearer handoff between learner, teacher, and software.

## Technical Overview

- **Primary language:** Python
- **Detected stack:** Python, Python dependencies
- **Default branch:** `main`
- **Visibility:** `PUBLIC`
- **License:** MIT License

## Repository Map

- `Claude中文教材生成工具技术方案.md`
- `GPT5.4pro 中文教材生成工具技术方案.md`
- `Gemini中文教材生成工具技术方案.md`
- `Grok中文教材生成工具技术方案.md`
- `Kimi中文教材生成工具技术方案.md`
- `LICENSE`
- `Minimax中文教材生成工具技术方案.md`
- `README.md`
- `SECURITY.md`
- `compile_books_51_70.sh`
- `generate.sh`
- `generate_books_51_70.py`

## Quick Start

No universal setup command is declared yet. Start by inspecting the repository map above and the project-specific scripts or docs committed with the code.

## Operating Notes

- Keep real credentials out of the repository. Use local environment files, GitHub repository secrets, or the deployment platform secret manager.
- If a `.env.example` file exists, treat it as documentation only; never commit filled-in `.env` files.
- Before publishing screenshots, demos, or client examples, remove private names, internal paths, account IDs, and API endpoints.
- The `Repository Hygiene` workflow is a lightweight guardrail, not a replacement for product-specific tests.

## Delivery Checklist

- [ ] README describes the user, business outcome, and operating boundary.
- [ ] Setup or preview commands are current and do not rely on private machine state.
- [ ] No real secrets, private user data, or machine-local state are tracked.
- [ ] Screenshots, demos, or sample outputs are safe to share publicly when the repository is public.
- [ ] Product-specific tests or smoke checks are documented before production use.

## Roadmap

- Tighten the fastest path from clone to useful demo.
- Add project-specific screenshots, sample outputs, or a short walkthrough where useful.
- Promote repeated manual steps into scripts, tests, or documented workflows.
- Keep security, privacy, and licensing boundaries explicit as the project evolves.

## Maintainer Notes

Maintained by [Tony Sheng](https://github.com/shengdabai). This README is written as a business-facing handoff: it should help a future collaborator, client, or reviewer understand why the repository exists, how to inspect it, and what must be true before it is reused or shipped.

### Live AI generation (v1 pipeline, Claude API)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."     # required for live generation
cd v1-pipeline/z-turns-chinese
python main.py                            # see this dir's README for options
```

## 📖 Usage notes

- **Bring your own content.** The generator can splice in your own teaching material instead of (or alongside) generated text. See `v1-pipeline/z-turns-chinese/content_source_example.py` for the interface and `BOOK_CONTENT_MAP` wiring.
- **Pick a pipeline.** `v3-typst` is the current/recommended path for typesetting; `v1-pipeline` is the live-AI generation engine; `v2-weasyprint` is kept for reference.
- **Run the tests.** `cd v3-typst && pytest` exercises the parser, renderer, and content filter.

## 🗺️ Status — honest read

This is an **active, single-maintainer project**, not a polished framework. Expect:

- Working but opinionated code shaped around my own book series (Z Turns Chinese, books 51–100).
- Paths and book maps that assume my content layout — you'll adapt some hardcoded bits.
- The six provider specs are **design documents**, not all fully implemented end-to-end; the Claude path is the most battle-tested.

If you're an educator or builder experimenting with LLM-generated curricula, there's plenty here to fork, learn from, and remix.

## 🤝 Connect

I build AI + Chinese-teaching tools in public. If this is useful, a ⭐ **Star** and **[Follow @shengdabai](https://github.com/shengdabai)** genuinely help and keep me shipping.

Sibling projects:
- **[hsk-prep-platform](https://github.com/shengdabai/hsk-prep-platform)** — HSK exam prep
- **[chinese-mission](https://github.com/shengdabai/chinese-mission)** — learning-mission content
- **[Chinese-character-content](https://github.com/shengdabai/Chinese-character-content)** — character-level study material

## License

Licensed under the MIT License — see [LICENSE](LICENSE).

---

# 中文

> 把大模型变成你的中文教学合著者 —— 生成与 HSK 对齐、以话题为主线的中文教材，含词汇表、真实对话、语法讲解和可直接印刷的 PDF。

**[English](#-chinese-textbook-generator--中文教材生成工具)** | 中文

## 为什么做这个

我是一名全职中文老师，有 6000+ 学员。手写一本主题教材 —— 词汇、对话、语法、文化、练习再加排版 —— 往往要花上几周。这个仓库是我把这套流程压缩成可复用管线的尝试：给定一个主题和 HSK 等级，产出结构化、可直接印刷的整本书。完全公开开发，方便其他语言教育者借用结构、提示词，乃至整条管线。

## 仓库里有什么

这个仓库**同时是两样东西**，使用前请先了解这个区分：

- **🛠️ 可运行代码（Python）。** 三代实际的生成 / 排版管线（`v1-pipeline`、`v2-weasyprint`、`v3-typst`），外加批量生成器和 PDF 编译脚本。`v3-typst` 带有 parser / renderer / filter 架构和一套 `pytest` 测试。
- **📐 多模型方案文档（Markdown）。** 六份 `*技术方案.md` 设计文档，分别规划如何针对不同 LLM 提供商构建本工具 —— 即使不跑代码，也能当作提示词 / 蓝图使用。

每本生成的教材围绕单一主题（求职、创业、游戏、理财、航天探索……）展开约 25 章，包含：

- 📚 核心词汇（拼音、词性、用法说明）
- 💬 真实多轮课堂对话
- 📖 语境中的语法精讲
- 🎯 发音与声调练习
- 🌏 文化背景文章
- ✍️ 写作与口语练习
- 🧪 自我测评

## 🧱 技术栈与 LLM 提供商

| 层 | 技术 |
|----|------|
| 生成引擎（v1） | Python + **Anthropic Claude API**（`ANTHROPIC_API_KEY`），未装 SDK 时回退到 HTTP 调用 |
| 增强批量生成器 | Python，模板驱动的结构化内容（无需 API key） |
| 排版（v3，当前） | **[Typst](https://typst.app/)** 模板 + 自研 Markdown parser / renderer / filter |
| 排版（v2，遗留） | WeasyPrint / HTML → PDF |
| 测试 | `pytest`（parser、renderer、content filter） |

**提供商设计方案** 覆盖：**Claude · GPT-5.4pro · Gemini · Kimi · Grok · Minimax**（各一份 `技术方案.md`），描述同一套教材生成思路如何映射到各家 API 与特性。

## 🚀 快速开始

```bash
git clone https://github.com/shengdabai/chinese-textbook-generator
cd chinese-textbook-generator
python -m venv .venv && source .venv/bin/activate
pip install -r v3-typst/requirements.txt
brew install typst   # 其他平台见 https://typst.app
```

### 生成主题教材（模板生成器 —— 无需 API key）

```bash
python generate_books_enhanced.py 51      # 单本（求职中文）
python generate_books_enhanced.py         # 全套 51–70
./compile_books_51_70.sh                  # 用 Typst 编译为 PDF
```

### 生成 HSK 备考指南（v3-typst 管线）

```bash
./generate.sh hsk --level 1
./generate.sh hsk --level 4
```

### 实时 AI 生成（v1 管线，Claude API）

```bash
export ANTHROPIC_API_KEY="sk-ant-..."     # 实时生成必需
cd v1-pipeline/z-turns-chinese
python main.py                            # 选项见该目录 README
```

## 📖 使用说明

- **接入自己的内容。** 生成器支持把你自己的教学素材接入流程，替换或补充生成内容。接口见 `v1-pipeline/z-turns-chinese/content_source_example.py`，并配置 `BOOK_CONTENT_MAP`。
- **选择管线。** `v3-typst` 是当前推荐的排版路径；`v1-pipeline` 是实时 AI 生成引擎；`v2-weasyprint` 作为参考保留。
- **跑测试。** `cd v3-typst && pytest` 会覆盖 parser、renderer 和 content filter。

## 🗺️ 项目状态 —— 实话实说

这是一个**活跃的、单人维护**的项目，不是打磨完善的框架。请预期：

- 代码可用但带有个人取向，围绕我自己的书系（Z Turns Chinese，第 51–100 本）构建。
- 路径和书目映射假设了我的内容目录结构 —— 部分硬编码需要你自行适配。
- 六份提供商方案是**设计文档**，并非全部端到端落地；Claude 路径最成熟、最经得起实战。

如果你是正在用 LLM 探索课程生成的教育者或开发者，这里有很多可以 fork、学习和二次创作的东西。

## 🤝 联系

我在公开开发 AI + 中文教学工具。如果它对你有用，点个 ⭐ **Star** 并 **[关注 @shengdabai](https://github.com/shengdabai)**，对我帮助很大，也能让我持续更新。

姊妹项目：
- **[hsk-prep-platform](https://github.com/shengdabai/hsk-prep-platform)** —— HSK 应试备考
- **[chinese-mission](https://github.com/shengdabai/chinese-mission)** —— 学习任务内容
- **[Chinese-character-content](https://github.com/shengdabai/Chinese-character-content)** —— 汉字层级学习素材

## 许可证

采用 MIT 许可证 —— 详见 [LICENSE](LICENSE)。
