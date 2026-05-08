#!/usr/bin/env python3
"""Convert merged HSK markdown files to PDF with a robust state-machine parser.

Fixes over the previous version:
* Table parser is a real state machine — contiguous rows form ONE table;
  a blank line (or non-pipe line) closes the table.
* Header separator (|---|---|) is recognised and the next row is NOT
  mistakenly promoted to a new thead.
* Inline markdown (**bold**, *italic*, `code`) is processed inside
  table cells, headings, blockquotes and list items.
* `---` is only treated as <hr> when the line is exactly dashes
  (prevents accidental splits inside tables).
"""

import html as html_mod
import re
import shutil
import sys
from pathlib import Path

try:
    from weasyprint import HTML
except ImportError:
    print("Error: weasyprint not installed. Run: pip install weasyprint")
    sys.exit(1)

BASE = Path(__file__).resolve().parent.parent
OUTPUT = BASE / 'output'
OUTPUT.mkdir(exist_ok=True)

DEST = Path.home() / 'Desktop' / '中文教学' / '中文教材生成工具' / 'HSK考试指南'
DEST.mkdir(parents=True, exist_ok=True)

LEVELS = [
    ('HSK1-merged.md', 'HSK 1 备考完全指南',   'ZTurns_HSK1_Prep.pdf',  'HSK1',   '#1565C0'),
    ('HSK2-merged.md', 'HSK 2 备考完全指南',   'ZTurns_HSK2_Prep.pdf',  'HSK2',   '#009650'),
    ('HSK3-merged.md', 'HSK 3 备考完全指南',   'ZTurns_HSK3_Prep.pdf',  'HSK3',   '#B4321E'),
    ('HSK4-merged.md', 'HSK 4 备考完全指南',   'ZTurns_HSK4_Prep.pdf',  'HSK4',   '#C87800'),
    ('HSK5-merged.md', 'HSK 5 备考完全指南',   'ZTurns_HSK5_Prep.pdf',  'HSK5',   '#643296'),
    ('HSK6-merged.md', 'HSK 6 备考完全指南',   'ZTurns_HSK6_Prep.pdf',  'HSK6',   '#1A1A2E'),
    ('HSK7-9-merged.md', 'HSK 7-9 备考完全指南', 'ZTurns_HSK79_Prep.pdf', 'HSK7-9', '#4A148C'),
]


INLINE_CODE = re.compile(r'`([^`]+)`')
BOLD = re.compile(r'\*\*(.+?)\*\*')
ITALIC = re.compile(r'(?<!\*)\*(?!\*)([^*\n]+?)\*(?!\*)')
HR_LINE = re.compile(r'^\s*-{3,}\s*$')
TABLE_SEP = re.compile(r'^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$')
ORDERED_ITEM = re.compile(r'^\s*(\d+)\.\s+(.+)$')
CJK_RE = re.compile(r'[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]')


def inline(text: str) -> str:
    """Inline markdown: escape first, then apply bold/italic/code."""
    text = html_mod.escape(text)
    text = INLINE_CODE.sub(r'<code>\1</code>', text)
    text = BOLD.sub(r'<strong>\1</strong>', text)
    text = ITALIC.sub(r'<em>\1</em>', text)
    return text


def split_row(line: str) -> list[str]:
    """Split a pipe-row into trimmed cells, ignoring the leading/trailing | ."""
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    return [c.strip() for c in s.split('|')]


def has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def class_attr(classes: list[str]) -> str:
    classes = [c for c in classes if c]
    if not classes:
        return ''
    return f' class="{" ".join(classes)}"'


def render_table(rows: list[str]) -> str:
    """rows is the raw lines belonging to one table block.

    If a separator row exists, rows before it form <thead>, rest form <tbody>.
    Otherwise the first row is <thead>.
    """
    if not rows:
        return ''

    sep_idx = next((i for i, r in enumerate(rows) if TABLE_SEP.match(r)), None)

    if sep_idx is not None and sep_idx > 0:
        header_rows = rows[:sep_idx]
        body_rows = rows[sep_idx + 1:]
    else:
        header_rows = rows[:1]
        body_rows = rows[1:]

    # Suppress empty tables (header only, no data rows) — they're meaningless.
    if not body_rows:
        return ''

    header_probe = split_row(header_rows[0]) if header_rows else []
    is_vocab_table = any('简体' in c for c in header_probe)
    table_classes = ['vocab-table'] if is_vocab_table else []
    out = [f'<table{class_attr(table_classes)}>']
    if header_rows:
        out.append('<thead>')
        for r in header_rows:
            cells = split_row(r)
            rendered = []
            for idx, c in enumerate(cells):
                classes = []
                if has_cjk(c):
                    classes.append('cjk')
                if is_vocab_table and idx == 0:
                    classes.append('vocab-word')
                rendered.append(f'<th{class_attr(classes)}>{inline(c)}</th>')
            out.append('<tr>' + ''.join(rendered) + '</tr>')
        out.append('</thead>')
    if body_rows:
        out.append('<tbody>')
        for r in body_rows:
            cells = split_row(r)
            rendered = []
            for idx, c in enumerate(cells):
                classes = []
                if has_cjk(c):
                    classes.append('cjk')
                if is_vocab_table and idx == 0:
                    classes.append('vocab-word')
                if c == '':
                    classes.append('na')
                    rendered.append(f'<td{class_attr(classes)}>—</td>')
                else:
                    rendered.append(f'<td{class_attr(classes)}>{inline(c)}</td>')
            out.append('<tr>' + ''.join(rendered) + '</tr>')
        out.append('</tbody>')
    out.append('</table>')
    return '\n'.join(out)


def render_list(items: list[str], ordered: bool = False, start: int = 1) -> str:
    tag = 'ol' if ordered else 'ul'
    open_tag = f'<{tag} start="{start}">' if ordered and start != 1 else f'<{tag}>'
    out = [open_tag]
    for it in items:
        out.append(f'<li>{inline(it)}</li>')
    out.append(f'</{tag}>')
    return '\n'.join(out)


SERIES_LEVELS = [
    ('HSK 1', '入门 · Entry'),
    ('HSK 2', '基础 · Foundation'),
    ('HSK 3', '进阶 · Advancing'),
    ('HSK 4', '突破 · Breakthrough'),
    ('HSK 5', '精进 · Refinement'),
    ('HSK 6', '卓越 · Excellence'),
    ('HSK 7-9', '大师 · Mastery'),
]


def cover_html(level_label: str, level_subtitle: str, color: str) -> str:
    return f"""
<div class="cover" style="--cover-color:{color};">
  <div class="cover-block">
    <div class="cover-top">Z TURNS CHINESE</div>
    <div class="cover-ribbon"></div>
    <div class="cover-main">{level_label}</div>
    <div class="cover-sub">备考完全指南</div>
    <div class="cover-tag">Complete Preparation Guide</div>
    <div class="cover-level-badge">{level_subtitle}</div>
  </div>
  <div class="cover-bottom">
    <div>Tony Sheng · 盛长春</div>
    <div>2026 Edition · HSK 3.0 Syllabus</div>
  </div>
</div>
"""


def colophon_html(level_label: str) -> str:
    # Build series navigation list
    items = ''.join(
        f'<li>{lv} — {sub}</li>'
        for lv, sub in SERIES_LEVELS
    )
    return f"""
<div class="colophon">
  <div class="colophon-inner">
    <div class="brand">Z TURNS CHINESE</div>
    <div class="subtitle">HSK Preparation Series · 备考系列</div>
    <div class="divider"></div>
    <div class="encourage">Good luck on your {level_label} exam!</div>
    <div class="encourage-cn">祝你 {level_label} 考试顺利！</div>
    <div class="divider"></div>
    <div class="series-title">Also in this Series</div>
    <ul class="series-list">{items}</ul>
    <div class="divider small"></div>
    <div class="meta">
      <div><strong>Series</strong> · Z Turns Chinese — HSK Prep Guide</div>
      <div><strong>Author</strong> · Tony Sheng (盛长春)</div>
      <div><strong>Edition</strong> · 2026 · Based on HSK 3.0 Syllabus</div>
      <div style="margin-top:10pt">© 2026 Z Turns Chinese. All rights reserved.</div>
    </div>
  </div>
</div>
"""


LEVEL_SUBTITLES = {
    'HSK 1': '入门 · Entry',
    'HSK 2': '基础 · Foundation',
    'HSK 3': '进阶 · Advancing',
    'HSK 4': '突破 · Breakthrough',
    'HSK 5': '精进 · Refinement',
    'HSK 6': '卓越 · Excellence',
    'HSK 7-9': '大师 · Mastery',
}


def md_to_html(md_text: str, color: str, level_label: str = '') -> str:
    lines = md_text.split('\n')
    out: list[str] = []

    i = 0
    n = len(lines)
    in_code = False
    code_buf: list[str] = []

    while i < n:
        line = lines[i]

        # fenced code
        if line.startswith('```'):
            if in_code:
                out.append('<pre>' + html_mod.escape('\n'.join(code_buf)) + '</pre>')
                code_buf = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        stripped = line.strip()

        # raw style block: skip markdown rendering (styles are already in template CSS)
        if stripped.startswith('<style'):
            i += 1
            while i < n and '</style>' not in lines[i]:
                i += 1
            if i < n:
                i += 1
            continue

        # table block: contiguous lines that contain a pipe
        if stripped.startswith('|'):
            table_rows = []
            while i < n and lines[i].strip().startswith('|'):
                table_rows.append(lines[i])
                i += 1
            out.append(render_table(table_rows))
            continue

        # bullet list block
        if stripped.startswith(('- ', '* ')):
            items = []
            while i < n:
                s = lines[i].strip()
                if s.startswith(('- ', '* ')):
                    items.append(s[2:])
                    i += 1
                else:
                    break
            out.append(render_list(items))
            continue

        # ordered list block (1. foo / 2. bar ...)
        m = ORDERED_ITEM.match(line)
        if m:
            items = []
            start = int(m.group(1))
            while i < n:
                mm = ORDERED_ITEM.match(lines[i])
                if mm:
                    items.append(mm.group(2).rstrip())
                    i += 1
                else:
                    break
            out.append(render_list(items, ordered=True, start=start))
            continue

        # headings
        if stripped.startswith('# '):
            out.append(f'<h1>{inline(stripped[2:])}</h1>')
            i += 1; continue
        if stripped.startswith('## '):
            out.append(f'<h2>{inline(stripped[3:])}</h2>')
            i += 1; continue
        if stripped.startswith('### '):
            out.append(f'<h3>{inline(stripped[4:])}</h3>')
            i += 1; continue
        if stripped.startswith('#### '):
            out.append(f'<h4>{inline(stripped[5:])}</h4>')
            i += 1; continue

        # blockquote
        if stripped.startswith('> '):
            quote_lines = []
            while i < n and lines[i].strip().startswith('> '):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            out.append('<blockquote>' + inline(' '.join(quote_lines)) + '</blockquote>')
            continue

        # horizontal rule
        if HR_LINE.match(line):
            out.append('<hr>')
            i += 1; continue

        # blank line
        if stripped == '':
            i += 1; continue

        # paragraph: collect consecutive non-special lines
        para_lines = [stripped]
        i += 1
        while i < n:
            nxt = lines[i]
            ns = nxt.strip()
            if (ns == '' or ns.startswith(('#', '>', '- ', '* ', '|', '```'))
                    or HR_LINE.match(nxt) or ORDERED_ITEM.match(nxt)):
                break
            para_lines.append(ns)
            i += 1
        out.append('<p>' + inline(' '.join(para_lines)) + '</p>')

    body = '\n'.join(out)
    if level_label:
        subtitle = LEVEL_SUBTITLES.get(level_label, '')
        body = cover_html(level_label, subtitle, color) + '\n' + body
        body += '\n' + colophon_html(level_label)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
:root {{
    --accent: {color};
    --latin-sans: "Avenir Next", "Helvetica Neue", Helvetica, Arial, sans-serif;
    --cjk-sans: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                "Noto Sans CJK SC", "Source Han Sans CN", sans-serif;
    --cjk-serif: "Songti SC", "STSong", "Hiragino Mincho ProN",
                 "Noto Serif CJK SC", "Source Han Serif SC", serif;
    --ink: #1f2633;
    --muted: #667085;
    --rule: #d7deea;
    --paper-tint: #f6f8fb;
}}

@page {{
    size: A4;
    margin: 18mm 15mm 18mm 15mm;
    @bottom-center {{
        content: "Z Turns Chinese — HSK Prep Guide";
        font-family: var(--latin-sans), var(--cjk-sans);
        font-size: 8pt;
        color: #98a2b3;
        letter-spacing: 0.4pt;
    }}
    @bottom-right {{
        content: counter(page);
        font-family: var(--latin-sans), var(--cjk-sans);
        font-size: 8pt;
        color: #98a2b3;
    }}
}}
* {{
    box-sizing: border-box;
}}
body {{
    font-family: var(--latin-sans), var(--cjk-sans);
    font-size: 10pt;
    line-height: 1.72;
    color: var(--ink);
    text-rendering: geometricPrecision;
}}
h1 {{
    color: var(--accent);
    font-family: var(--latin-sans), var(--cjk-sans);
    font-size: 22pt;
    border-bottom: 2.5pt solid var(--accent);
    padding-bottom: 10pt;
    page-break-before: always;
    margin-top: 0;
    margin-bottom: 18pt;
    letter-spacing: -0.3pt;
}}
h1:first-of-type {{ page-break-before: avoid; }}
h2 {{
    color: var(--accent);
    font-family: var(--latin-sans), var(--cjk-sans);
    font-size: 14.5pt;
    margin-top: 22pt;
    margin-bottom: 10pt;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 6pt;
    page-break-after: avoid;
    letter-spacing: -0.2pt;
}}
h3 {{
    color: #1f2a37;
    font-family: var(--latin-sans), var(--cjk-sans);
    font-size: 11.5pt;
    margin-top: 14pt;
    margin-bottom: 8pt;
    background: var(--paper-tint);
    border-left: 3pt solid var(--accent);
    padding: 6pt 10pt;
    page-break-after: avoid;
}}
h4 {{
    font-size: 11pt;
    font-weight: bold;
    margin-top: 10pt;
    page-break-after: avoid;
    color: var(--ink);
}}
p {{
    margin: 0 0 9pt 0;
    orphans: 2;
    widows: 2;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0 14pt;
    font-size: 8.9pt;
    page-break-inside: auto;
}}
tr {{ page-break-inside: avoid; page-break-after: auto; }}
thead {{ display: table-header-group; }}
th {{
    background: var(--accent);
    font-family: var(--latin-sans), var(--cjk-sans);
    color: white;
    padding: 7pt 8pt;
    text-align: left;
    font-weight: bold;
    border: 1px solid var(--accent);
    letter-spacing: 0.1pt;
}}
td {{
    padding: 6pt 8pt;
    border-bottom: 1px solid #e5e7eb;
    vertical-align: top;
    word-break: break-word;
    font-family: var(--latin-sans), var(--cjk-sans);
}}
th.cjk, td.cjk {{
    font-family: var(--cjk-sans);
}}
.vocab-table th.vocab-word,
.vocab-table td.vocab-word {{
    font-family: var(--cjk-serif), var(--cjk-sans);
}}
tbody tr:nth-child(even) td {{ background: #f8fafc; }}
td.na {{ color: #bbb; text-align: center; }}
code {{
    background: #f1f1f1;
    padding: 1pt 4pt;
    border-radius: 2pt;
    font-family: "SF Mono", "Fira Code", Consolas, monospace;
    font-size: 9pt;
}}
pre {{
    background: #f5f5f5;
    border-left: 4px solid {color};
    padding: 10pt 14pt;
    font-family: "SF Mono", "Fira Code", Consolas, monospace;
    font-size: 9pt;
    line-height: 1.5;
    white-space: pre-wrap;
    margin: 8pt 0;
}}
blockquote {{
    border-left: 3px solid var(--accent);
    background: var(--paper-tint);
    padding: 8pt 12pt;
    margin: 12pt 0;
    color: #475467;
}}
hr {{
    border: none;
    border-top: 1px solid var(--rule);
    margin: 18pt 0;
}}
strong {{ font-weight: bold; }}
em {{ font-style: italic; }}
ul, ol {{ margin: 6pt 0 10pt 20pt; padding: 0; }}
ol {{ padding-left: 4pt; }}
li {{
    margin: 4pt 0;
    padding-left: 2pt;
    line-height: 1.65;
    color: var(--ink);
}}
ol > li::marker {{ color: var(--accent); font-weight: bold; }}

/* === COVER PAGE === */
.cover {{
    page-break-after: always;
    text-align: center;
    min-height: 25cm;
    position: relative;
    color: #333;
    padding-top: 8pt;
}}
.cover-block {{
    background: var(--accent);
    color: white;
    padding: 88pt 42pt 70pt 42pt;
    margin: 0 -15mm;
    box-shadow: inset 0 -18pt 0 rgba(255,255,255,0.08);
}}
.cover-top {{
    font-family: var(--latin-sans), var(--cjk-sans);
    font-size: 10pt;
    letter-spacing: 6pt;
    opacity: 0.85;
    margin-bottom: 34pt;
}}
.cover-ribbon {{
    width: 70pt;
    height: 4pt;
    background: white;
    margin: 0 auto 42pt auto;
    opacity: 0.9;
}}
.cover-main {{
    font-family: var(--latin-sans), var(--cjk-sans);
    font-size: 58pt;
    font-weight: 800;
    letter-spacing: 2pt;
    margin-bottom: 14pt;
    line-height: 1.1;
}}
.cover-sub {{
    font-family: var(--cjk-serif), var(--cjk-sans);
    font-size: 22pt;
    font-weight: 500;
    margin-bottom: 8pt;
    letter-spacing: 1pt;
}}
.cover-tag {{
    font-family: var(--latin-sans), var(--cjk-sans);
    font-size: 11pt;
    opacity: 0.85;
    letter-spacing: 2pt;
    margin-bottom: 34pt;
}}
.cover-level-badge {{
    display: inline-block;
    font-family: var(--latin-sans), var(--cjk-sans);
    font-size: 14pt;
    color: var(--accent);
    background: white;
    padding: 9pt 24pt;
    letter-spacing: 2pt;
    margin-top: 10pt;
    margin-bottom: 26pt;
    font-weight: bold;
    border-radius: 999px;
    box-shadow: 0 8pt 20pt rgba(0,0,0,0.12);
}}
.cover-bottom {{
    position: absolute;
    bottom: 28pt;
    left: 0;
    right: 0;
    color: var(--ink);
    font-family: var(--latin-sans), var(--cjk-sans);
    font-size: 10pt;
    line-height: 1.9;
    letter-spacing: 1pt;
}}

/* === COLOPHON === */
.colophon {{
    page-break-before: always;
    text-align: center;
    color: #555;
    padding-top: 7cm;
}}
.colophon-inner {{
    padding: 20pt 0;
}}
.colophon .brand {{
    color: var(--accent);
    font-size: 28pt;
    font-family: var(--latin-sans), var(--cjk-sans);
    font-weight: bold;
    letter-spacing: 2pt;
    margin-bottom: 4pt;
}}
.colophon .subtitle {{
    font-size: 11pt;
    color: var(--muted);
    margin-bottom: 30pt;
    letter-spacing: 1pt;
}}
.colophon .encourage {{
    font-size: 14pt;
    font-weight: bold;
    color: var(--ink);
    margin: 14pt 0 8pt 0;
}}
.colophon .encourage-cn {{
    font-size: 13pt;
    color: #475467;
    margin-bottom: 20pt;
    font-family: var(--cjk-serif), var(--cjk-sans);
}}
.colophon .divider {{
    width: 60pt;
    height: 2pt;
    background: var(--accent);
    margin: 20pt auto;
}}
.colophon .divider.small {{
    width: 40pt;
    height: 1pt;
    margin: 16pt auto;
    background: #ccc;
}}
.colophon .series-title {{
    font-size: 11pt;
    font-weight: bold;
    color: var(--accent);
    letter-spacing: 1pt;
    margin-top: 10pt;
    margin-bottom: 8pt;
}}
.colophon .series-list {{
    list-style: none;
    padding: 0;
    margin: 0 auto;
    font-size: 10pt;
    line-height: 1.9;
    color: #555;
}}
.colophon .series-list li {{ margin: 0; }}
.colophon .meta {{
    font-size: 9pt;
    color: var(--muted);
    line-height: 1.8;
    margin-top: 20pt;
}}
.colophon .meta strong {{ color: var(--ink); }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def main():
    for md_name, title, pdf_name, folder, color in LEVELS:
        src = OUTPUT / md_name
        if not src.exists():
            print(f"  SKIP: {md_name} not found")
            continue

        md_text = src.read_text(encoding='utf-8')
        level_label = folder.replace('HSK', 'HSK ')
        html_content = md_to_html(md_text, color, level_label=level_label)

        pdf_path = OUTPUT / pdf_name
        HTML(string=html_content, base_url=str(OUTPUT)).write_pdf(str(pdf_path))
        size = pdf_path.stat().st_size
        print(f"  {folder}: {pdf_name} ({size/1024:.1f} KB)")

        dest_folder = DEST / folder
        dest_folder.mkdir(exist_ok=True)
        shutil.copy2(src, dest_folder / f'{folder}-备考完全指南.md')
        shutil.copy2(pdf_path, dest_folder / pdf_name)
        print(f"  -> Copied to {dest_folder}/")


if __name__ == '__main__':
    main()
