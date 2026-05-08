"""Markdown parser for v3-typst pipeline.

Defines NodeType enum and MdParser class that converts Markdown text
into a list of AST node dicts consumed by renderers.
"""

from enum import Enum
import re


class NodeType(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    VOCAB_TABLE = "vocab_table"
    TABLE = "table"
    LIST = "list"
    CODE_BLOCK = "code_block"
    BLOCKQUOTE = "blockquote"
    HR = "hr"


_VOCAB_HEADER_PATTERN = re.compile(r"pinyin", re.IGNORECASE)


class MarkdownParser:
    """Parse Markdown text into a list of AST node dicts."""

    def parse(self, text: str) -> list[dict]:
        nodes: list[dict] = []
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]

            # Heading
            m = re.match(r"^(#{1,6})\s+(.*)", line)
            if m:
                nodes.append({
                    "type": NodeType.HEADING,
                    "level": len(m.group(1)),
                    "text": m.group(2).strip(),
                })
                i += 1
                continue

            # HR
            if re.match(r"^---+$", line.strip()):
                nodes.append({"type": NodeType.HR})
                i += 1
                continue

            # Code block
            if line.startswith("```"):
                lang = line[3:].strip()
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # skip closing ```
                nodes.append({
                    "type": NodeType.CODE_BLOCK,
                    "lang": lang,
                    "code": "\n".join(code_lines),
                })
                continue

            # Blockquote
            if line.startswith(">"):
                nodes.append({
                    "type": NodeType.BLOCKQUOTE,
                    "text": line[1:].strip(),
                })
                i += 1
                continue

            # Ordered list item
            if re.match(r"^\d+\.\s+", line):
                items = []
                while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                    items.append(re.sub(r"^\d+\.\s+", "", lines[i]))
                    i += 1
                nodes.append({
                    "type": NodeType.LIST,
                    "ordered": True,
                    "items": items,
                })
                continue

            # Unordered list item
            if re.match(r"^[-*]\s+", line):
                items = []
                while i < len(lines) and re.match(r"^[-*]\s+", lines[i]):
                    items.append(re.sub(r"^[-*]\s+", "", lines[i]))
                    i += 1
                nodes.append({
                    "type": NodeType.LIST,
                    "ordered": False,
                    "items": items,
                })
                continue

            # Table (pipe-delimited)
            if "|" in line:
                headers = [h.strip() for h in line.strip().strip("|").split("|")]
                rows = []
                i += 1
                # skip separator row
                if i < len(lines) and re.match(r"^[\|\-\s:]+$", lines[i]):
                    i += 1
                while i < len(lines) and "|" in lines[i]:
                    row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    rows.append(tuple(row))
                    i += 1
                # Detect vocab table: header contains "Pinyin"
                is_vocab = any(_VOCAB_HEADER_PATTERN.search(h) for h in headers)
                if is_vocab and rows:
                    # 7 cols = hanzi/pinyin/pos/meaning/ex_zh/ex_pinyin/ex_en (HSK 1/2)
                    # 6 cols = hanzi/pinyin/pos/meaning/ex_zh/ex_en (HSK 3-6, no pinyin col)
                    # 4 cols = hanzi/pinyin/pos/meaning (no examples)
                    ncols = len(headers)
                    has_examples = ncols >= 6
                    has_pinyin_example = ncols >= 7
                    vocab_rows = []
                    for row in rows:
                        if has_pinyin_example and len(row) >= 6:
                            vocab_rows.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6] if len(row) > 6 else ""))
                        elif has_examples and len(row) >= 6:
                            # 6-col: insert empty pinyin col between ex_zh and ex_en
                            vocab_rows.append((row[0], row[1], row[2], row[3], row[4], "", row[5]))
                        elif len(row) >= 3:
                            vocab_rows.append((row[0], row[1], row[2], row[-1], "", "", ""))
                    nodes.append({
                        "type": NodeType.VOCAB_TABLE,
                        "has_examples": has_examples,
                        "has_pinyin_example": has_pinyin_example,
                        "rows": vocab_rows,
                    })
                else:
                    nodes.append({
                        "type": NodeType.TABLE,
                        "headers": headers,
                        "rows": rows,
                    })
                continue

            # Blank line
            if not line.strip():
                i += 1
                continue

            # Paragraph — collect until blank line
            para_lines = []
            while i < len(lines) and lines[i].strip():
                para_lines.append(lines[i])
                i += 1
            if para_lines:
                nodes.append({
                    "type": NodeType.PARAGRAPH,
                    "text": " ".join(para_lines),
                })

        return nodes
