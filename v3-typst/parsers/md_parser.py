"""Markdown parser for v3-typst pipeline.

Defines NodeType enum and MdParser class that converts Markdown text
into a list of AST node dicts consumed by renderers.
"""

import re
from enum import Enum


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
_OUTER_PIPE = re.compile(r"^\||\|$")


def _split_row(line: str) -> list[str]:
    """Split a pipe-table line into stripped cells.

    Only one leading and one trailing ``|`` are removed, so a row ending in
    ``||`` keeps its empty last cell.
    """
    return [c.strip() for c in _OUTER_PIPE.sub("", line.strip()).split("|")]


class MarkdownParser:
    """Parse Markdown text into a list of AST node dicts."""

    def parse(self, text: str) -> list[dict]:
        """Parse ``text`` into a list of node dicts.

        Vocabulary tables (a pipe table whose header mentions "Pinyin") become
        ``NodeType.VOCAB_TABLE`` nodes. Their ``rows`` always hold full
        7-tuples ``(hanzi, pinyin, pos, meaning, ex_zh, ex_pinyin, ex_en)``,
        because ``TypstRenderer`` unpacks all seven fields. A column the
        source table does not have is an empty string. Empty cells, including
        a trailing one written as ``||``, are kept, and a row shorter than the
        header is padded with ``""`` so every cell stays in its header column:

        - 7+ columns: the first seven cells in order.
        - 6 columns: ``ex_pinyin`` is ``""``.
        - fewer columns: ``pos`` is the third cell, ``meaning`` is the cell
          under the last header column, and the three example fields are
          ``""``.

        Rows with fewer than 3 cells are skipped.

        ``has_examples`` (6+ header columns) and ``has_pinyin_example``
        (7+ header columns) tell the renderer which layout to use.
        """
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
                headers = _split_row(line)
                rows = []
                i += 1
                # skip separator row
                if i < len(lines) and re.match(r"^[\|\-\s:]+$", lines[i]):
                    i += 1
                while i < len(lines) and "|" in lines[i]:
                    rows.append(tuple(_split_row(lines[i])))
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
                    meaning_col = max(ncols, 3) - 1
                    for row in rows:
                        if len(row) < 3:
                            continue
                        # Pad short rows so each cell stays under its header.
                        cells = list(row) + [""] * (max(ncols, 7) - len(row))
                        if has_pinyin_example:
                            vocab_rows.append(tuple(cells[:7]))
                        elif has_examples:
                            # 6-col: insert empty pinyin col between ex_zh and ex_en
                            vocab_rows.append((cells[0], cells[1], cells[2], cells[3], cells[4], "", cells[5]))
                        else:
                            vocab_rows.append((cells[0], cells[1], cells[2], cells[meaning_col], "", "", ""))
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
