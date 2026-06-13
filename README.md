# chinese-textbook-generator

AI pipeline + multi-LLM specs for generating HSK-aligned, theme-based Chinese textbooks — vocab, dialogues, grammar, print-ready PDFs.

## Business Context

- **Category:** security and governance tool
- **Audience:** builders and operators who need safer repositories, cleaner handoffs, and repeatable security checks.
- **Repository status:** Public repository. Keep examples, docs, and issues free of credentials, private data, and machine-specific paths.
- **Topics:** ai, chinese-learning, content-generation, education, hsk, llm, textbook, typst

## What This Project Is For

- AI pipeline + multi-LLM specs for generating HSK-aligned, theme-based Chinese textbooks — vocab, dialogues, grammar, print-ready PDFs.
- Find repository risks early without exposing secrets in reports.
- Make security review repeatable across public and private codebases.

## Where It Fits

This repository belongs in the trust-and-safety layer of the workbench: it helps make code, configuration, and public handoffs safer before they are reused or shown to clients.

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
