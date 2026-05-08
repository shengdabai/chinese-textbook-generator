#!/usr/bin/env python3
"""把大 appendix 文件按子表格拆分，每段派给 Claude 子进程处理后合并。
用法: python process_appendix.py <file> <level>
"""
import re, sys, subprocess, tempfile, os
from pathlib import Path

SEP_RE = re.compile(r"^[\|\-\s:]+$")
HDR_RE = re.compile(r"pinyin", re.IGNORECASE)
ROW_RE = re.compile(r"^\|.+\|$")

def split_sections(text):
    """把文件按 ### 标题拆成 sections，每个 section 是 (header_lines, table_lines, after_lines)"""
    lines = text.splitlines()
    sections = []
    i = 0
    current = []
    while i < len(lines):
        if lines[i].startswith("### ") and current:
            sections.append(current)
            current = [lines[i]]
        else:
            current.append(lines[i])
        i += 1
    if current:
        sections.append(current)
    return sections

def section_needs_update(section_lines):
    for line in section_lines:
        if ROW_RE.match(line) and HDR_RE.search(line):
            cols = len(line.strip().strip("|").split("|"))
            return cols <= 4
    return False

def add_examples_to_section(section_lines, level):
    """对一个 section 的词汇表加例句，返回更新后的行列表。"""
    out = []
    i = 0
    while i < len(section_lines):
        line = section_lines[i]
        if ROW_RE.match(line) and HDR_RE.search(line) and len(line.strip().strip("|").split("|")) <= 4:
            # 收集这个表格
            headers = [h.strip() for h in line.strip().strip("|").split("|")]
            if level == "2":
                new_hdr = "| " + " | ".join(headers) + " | Example (中文) | Example (Pinyin) | Example (English) |"
                new_sep = "|" + "---|" * (len(headers) + 3)
            else:
                new_hdr = "| " + " | ".join(headers) + " | Example (中文) | Example (English) |"
                new_sep = "|" + "---|" * (len(headers) + 2)
            out.append(new_hdr)
            i += 1
            # skip sep
            if i < len(section_lines) and SEP_RE.match(section_lines[i]):
                out.append(new_sep)
                i += 1
            # collect rows
            data_rows = []
            while i < len(section_lines) and ROW_RE.match(section_lines[i]):
                cols = [c.strip() for c in section_lines[i].strip().strip("|").split("|")]
                while len(cols) < 4:
                    cols.append("")
                data_rows.append(cols)
                i += 1
            # generate examples via claude CLI
            enriched = generate_examples(data_rows, level)
            out.extend(enriched)
        else:
            out.append(line)
            i += 1
    return out

def generate_examples(rows, level):
    """调用 claude CLI 为词汇行生成例句。"""
    if level == "2":
        fmt = "7 pipe-delimited columns: Word|Pinyin|PoS|Meaning|Example_ZH|Example_Pinyin|Example_EN"
        rule = "HSK 2 level (5-10 chars), target word must appear, accurate tones in pinyin"
    else:
        fmt = "6 pipe-delimited columns: Word|Pinyin|PoS|Meaning|Example_ZH|Example_EN"
        rule = f"HSK {level} level, target word must appear, natural English"

    rows_txt = "\n".join("|".join(r[:4]) for r in rows)
    prompt = f"""Add example sentence columns to these Chinese vocabulary rows.
Output ONLY the table rows, one per line, pipe-delimited, no header, no explanation.
Format: {fmt}
Rule: {rule}. Keep all original columns unchanged.

Input (Word|Pinyin|PoS|Meaning):
{rows_txt}

Output rows with examples (same count, same order):"""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "text"],
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout.strip()
        result_rows = [l for l in output.splitlines() if ROW_RE.match(l.strip())]
        if len(result_rows) == len(rows):
            return result_rows
        else:
            print(f"  [warn] got {len(result_rows)} rows, expected {len(rows)}, using originals")
            return ["|" + "|".join(r[:4]) + "|" for r in rows]
    except Exception as e:
        print(f"  [error] {e}")
        return ["|" + "|".join(r[:4]) + "|" for r in rows]

def main():
    if len(sys.argv) < 3:
        print("Usage: process_appendix.py <file> <level>")
        sys.exit(1)
    path = Path(sys.argv[1])
    level = sys.argv[2]

    text = path.read_text(encoding="utf-8")
    sections = split_sections(text)

    out_sections = []
    for idx, section in enumerate(sections):
        if section_needs_update(section):
            print(f"  处理 section {idx+1}/{len(sections)} ({len([l for l in section if ROW_RE.match(l)])} 词)...")
            updated = add_examples_to_section(section, level)
            out_sections.append(updated)
        else:
            out_sections.append(section)

    final = "\n".join("\n".join(s) for s in out_sections) + "\n"
    path.write_text(final, encoding="utf-8")
    print(f"✓ 完成: {path.name}")

if __name__ == "__main__":
    main()
