#!/usr/bin/env python3
"""Fix Book51-70 vocabulary first-row placeholder bug.

Bug: every chapter's first vocab row reads:
  | <term> | kěyǐ | core term | noun/verb | 核心词汇，贯穿本章 |

Fix: replace `kěyǐ` with real pinyin and `core term` with real English
     (both extracted from the "He wrote **term** ... Chinese term for <en>" line).
Then re-compile PDFs sequentially.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from pypinyin import Style, pinyin

BASE = Path("../..")
V3 = BASE / "生成工具/v3-typst"
ROOT = BASE / "中文教材"
GENERATOR = V3 / "generate.py"
VENV_PY = V3 / ".venv/bin/python"

BOOK_META = {
    51: ("JobHunter", "Job Hunter's Chinese", "求职面试中文实战手册", "#E53935"),
    52: ("Startup", "Startup Chinese", "创业者的中文生存手册", "#F9A825"),
    53: ("Negotiation", "The Art of Chinese Negotiation", "谈判桌上的中文智慧", "#6A1B9A"),
    54: ("Resume", "Chinese Resume & LinkedIn", "中文简历与职业品牌打造", "#00838F"),
    55: ("WorkplacePolitics", "Chinese Workplace Politics", "办公室政治生存指南", "#5D4037"),
    56: ("Gaming", "Gaming in Chinese", "游戏玩家的中文世界", "#283593"),
    57: ("Music", "Chinese Music Scene", "中国音乐现场", "#AD1457"),
    58: ("Comedy", "Crosstalk & Comedy Chinese", "相声与中国喜剧语言", "#EF6C00"),
    59: ("WebNovels", "Chinese Web Fiction", "网络小说", "#37474F"),
    60: ("VarietyShows", "Variety Show Chinese", "综艺节目语言指南", "#D84315"),
    61: ("Cooking", "Cooking in Chinese", "中国厨房：从菜市场到餐桌", "#C62828"),
    62: ("Finance", "Money & Investment Chinese", "中文理财：从存钱到投资", "#1B5E20"),
    63: ("Fitness", "Fitness & Wellness Chinese", "健身房到瑜伽馆", "#00695C"),
    64: ("TravelPhoto", "Travel Photography Chinese", "旅拍中文：镜头里的中国", "#283593"),
    65: ("HomeReno", "Home Decoration Chinese", "装修那些事：新家的中文旅程", "#6D4C41"),
    66: ("EV", "Electric Vehicles & New Mobility", "电动车革命：中国新出行语言", "#1565C0"),
    67: ("CleanEnergy", "Renewable Energy Chinese", "绿色中国：新能源语言全图谱", "#2E7D32"),
    68: ("Robotics", "Robotics & AI Hardware", "机器人与智能硬件：未来制造语言", "#455A64"),
    69: ("Quantum", "Quantum & Semiconductor", "量子与芯片：硬核科技语言", "#4527A0"),
    70: ("Space", "Space & Aviation Chinese", "航天升级版：从卫星到商业航天", "#01579B"),
}


def zh_to_pinyin(text: str) -> str:
    """Convert Chinese characters to tone-mark pinyin."""
    parts = []
    for ch in text:
        if re.match(r"[\u4e00-\u9fff]", ch):
            py = pinyin(ch, style=Style.TONE, heteronym=False)[0][0]
            parts.append(py)
    return " ".join(parts)


def fix_md_file(md_path: Path) -> int:
    """Fix the vocabulary bug in one MD file. Returns count of fixed rows."""
    text = md_path.read_text(encoding="utf-8")

    # Find all chapter core terms from "He wrote **X** on the board — the Chinese term for Y"
    # Pattern: **term** on the board — the Chinese term for <description>
    pattern = re.compile(
        r"He wrote \*\*([^*]+)\*\* on the board — the Chinese term for ([^—]+?) — and",
        re.MULTILINE
    )
    matches = list(pattern.finditer(text))
    if not matches:
        print(f"  ⚠ No core terms found in {md_path.name}")
        return 0

    # Build replacement map: (term, english) pairs, in order of appearance
    # Each match corresponds to a chapter's Real Scene; the bugged vocab row follows.

    # Now do replacement: for each chapter, the first vocab row after its "Real Scene"
    # reads: | <term> | kěyǐ | core term | noun/verb | 核心词汇，贯穿本章 |
    # We replace kěyǐ -> real pinyin and core term -> real english

    fixed_text = text
    fix_count = 0
    for m in matches:
        term = m.group(1).strip()
        english = m.group(2).strip()
        real_pinyin = zh_to_pinyin(term)

        # Specific replacement: the vocab row for this specific term
        bad = f"| {term} | kěyǐ | core term | noun/verb | 核心词汇，贯穿本章 |"
        good = f"| {term} | {real_pinyin} | {english} | noun/verb | 核心词汇，贯穿本章 |"

        if bad in fixed_text:
            fixed_text = fixed_text.replace(bad, good, 1)
            fix_count += 1

    if fix_count > 0:
        md_path.write_text(fixed_text, encoding="utf-8")
    return fix_count


def compile_pdf(md_path: Path, number: int, title: str, subtitle: str, color: str, pdf_path: Path) -> bool:
    cmd = [
        str(VENV_PY), str(GENERATOR), "textbook",
        "--md", str(md_path),
        "--number", str(number),
        "--title", title,
        "--subtitle", subtitle,
        "--color", color,
        "--out", str(pdf_path),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            print(f"  ✗ PDF fail: {r.stderr[:300]}")
            return False
        return True
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--only", type=int, help="Only fix this book")
    p.add_argument("--from", dest="start", type=int, default=51)
    p.add_argument("--to", dest="end", type=int, default=70)
    p.add_argument("--md-only", action="store_true", help="Only fix MD, skip PDF recompile")
    args = p.parse_args()

    targets = [n for n in BOOK_META if args.start <= n <= args.end]
    if args.only:
        targets = [args.only]

    for n in targets:
        slug, title, subtitle, color = BOOK_META[n]
        book_dir = ROOT / f"Book{n}_{slug}"
        md = book_dir / f"ZTurns_Book{n}_{slug}.md"
        pdf = book_dir / f"ZTurns_Book{n}_{slug}.pdf"

        if not md.exists():
            print(f"Book{n}: MD missing at {md}")
            continue

        print(f"Book{n} ({slug}):")
        count = fix_md_file(md)
        print(f"  ✓ Fixed {count} vocab rows")

        if not args.md_only and count > 0:
            if compile_pdf(md, n, title, subtitle, color, pdf):
                print(f"  ✓ PDF recompiled")
            else:
                print(f"  ✗ PDF recompile failed")


if __name__ == "__main__":
    main()
