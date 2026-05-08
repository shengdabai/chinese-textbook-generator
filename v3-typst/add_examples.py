#!/usr/bin/env python3
"""批量给 HSK 2-79 词汇表加例句，使用 Anthropic API。"""
import re
import sys
import time
from pathlib import Path
import anthropic

BASE = Path(__file__).parent

# Files to process: (path, hsk_level)
# HSK 2: 7-col (中/拼/英例句), HSK 3-79: 6-col (中/英例句, no pinyin)
TARGETS = []
for level in ["2", "3", "4", "5", "6", "79"]:
    content_dir = BASE / f"content-hsk{level}"
    for md in sorted(content_dir.rglob("*.md")):
        TARGETS.append((md, level))

VOCAB_HEADER = re.compile(r"pinyin", re.IGNORECASE)
TABLE_ROW = re.compile(r"^\|(.+)\|$")
SEP_ROW = re.compile(r"^[\|\-\s:]+$")


def count_cols(line: str) -> int:
    return len(line.strip().strip("|").split("|"))


def needs_processing(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if TABLE_ROW.match(line) and VOCAB_HEADER.search(line):
            return count_cols(line) <= 4
    return False


def build_prompt(words: list[tuple], level: str) -> str:
    if level == "2":
        fmt = "7 columns: Word | Pinyin | PoS | Meaning | Example_ZH | Example_Pinyin | Example_EN"
        rules = "HSK 2 level sentences (5-10 chars), include the target word, accurate tones, natural English."
    else:
        fmt = "6 columns: Word | Pinyin | PoS | Meaning | Example_ZH | Example_EN"
        rules = f"HSK {level} level sentences, include the target word, natural English. No pinyin column."

    rows_txt = "\n".join(f"{w} | {p} | {pos} | {m}" for w, p, pos, m in words)
    return f"""You are a Chinese language teacher creating example sentences for HSK {level} vocabulary.

For each word below, add example sentence columns. Output ONLY the table rows, one per line, pipe-delimited, no header.
Format: {fmt}

Rules:
- {rules}
- Keep all existing columns exactly as given
- Short, practical sentences (5-12 characters for ZH)
- The target word MUST appear in the example sentence

Input rows (Word | Pinyin | PoS | Meaning):
{rows_txt}

Output the complete rows with examples added (same order, no extra text):"""


def process_file(path: Path, level: str, client: anthropic.Anthropic) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out_lines = []
    i = 0
    changed = False

    while i < len(lines):
        line = lines[i]
        # Detect vocab table header
        if TABLE_ROW.match(line) and VOCAB_HEADER.search(line) and count_cols(line) <= 4:
            headers = [h.strip() for h in line.strip().strip("|").split("|")]
            # Add new header
            if level == "2":
                new_header = "| " + " | ".join(headers) + " | Example (中文) | Example (Pinyin) | Example (English) |"
                new_sep = "|" + "---|" * (len(headers) + 3)
            else:
                new_header = "| " + " | ".join(headers) + " | Example (中文) | Example (English) |"
                new_sep = "|" + "---|" * (len(headers) + 2)

            out_lines.append(new_header)
            i += 1

            # Skip separator
            if i < len(lines) and SEP_ROW.match(lines[i]):
                out_lines.append(new_sep)
                i += 1

            # Collect data rows
            data_rows = []
            row_lines = []
            while i < len(lines) and TABLE_ROW.match(lines[i]):
                cols = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if len(cols) >= 4:
                    data_rows.append((cols[0], cols[1], cols[2], cols[3]))
                else:
                    data_rows.append(tuple(cols) + ("",) * (4 - len(cols)))
                row_lines.append(lines[i])
                i += 1

            # Call API in batches of 20
            enriched = []
            for batch_start in range(0, len(data_rows), 20):
                batch = data_rows[batch_start:batch_start + 20]
                prompt = build_prompt(batch, level)
                for attempt in range(3):
                    try:
                        msg = client.messages.create(
                            model="claude-haiku-4-5-20251001",
                            max_tokens=4096,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        result_text = msg.content[0].text.strip()
                        result_rows = [l for l in result_text.splitlines() if TABLE_ROW.match(l.strip())]
                        if len(result_rows) == len(batch):
                            enriched.extend(result_rows)
                            break
                        else:
                            print(f"  [warn] got {len(result_rows)} rows, expected {len(batch)}, retry {attempt+1}")
                            time.sleep(2)
                    except Exception as e:
                        print(f"  [error] {e}, retry {attempt+1}")
                        time.sleep(5)
                else:
                    # fallback: keep original rows
                    enriched.extend(row_lines[batch_start:batch_start + 20])

                time.sleep(0.5)  # rate limit

            out_lines.extend(enriched)
            changed = True
        else:
            out_lines.append(line)
            i += 1

    if changed:
        path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return changed


def main():
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    to_process = [(p, l) for p, l in TARGETS if needs_processing(p)]
    print(f"需要处理: {len(to_process)} 个文件")

    for idx, (path, level) in enumerate(to_process, 1):
        rel = path.relative_to(BASE)
        print(f"[{idx}/{len(to_process)}] HSK {level}: {rel}")
        ok = process_file(path, level, client)
        print(f"  {'✓ 已更新' if ok else '- 跳过'}")

    print("全部完成！")


if __name__ == "__main__":
    main()
