import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from parsers.md_parser import MarkdownParser, NodeType


def test_parse_heading():
    p = MarkdownParser()
    nodes = p.parse("# 标题一\n## 标题二\n")
    headings = [n for n in nodes if n["type"] == NodeType.HEADING]
    assert len(headings) == 2
    assert headings[0]["level"] == 1
    assert headings[0]["text"] == "标题一"
    assert headings[1]["level"] == 2


def test_parse_vocab_table():
    p = MarkdownParser()
    md = "| Word (简体) | Pinyin | Part of Speech | English Meaning |\n|---|---|---|---|\n| 学 | xué | verb | learn |\n"
    nodes = p.parse(md)
    tables = [n for n in nodes if n["type"] == NodeType.VOCAB_TABLE]
    assert len(tables) == 1
    assert tables[0]["has_examples"] is False
    assert tables[0]["has_pinyin_example"] is False
    # Rows are always full 7-tuples; see MarkdownParser.parse.
    assert tables[0]["rows"][0] == ("学", "xué", "verb", "learn", "", "", "")


def test_parse_regular_table():
    p = MarkdownParser()
    md = "| 列A | 列B |\n|---|---|\n| 值1 | 值2 |\n"
    nodes = p.parse(md)
    tables = [n for n in nodes if n["type"] == NodeType.TABLE]
    assert len(tables) == 1


def test_parse_paragraph():
    p = MarkdownParser()
    nodes = p.parse("这是一段中文。English mixed。\n")
    paras = [n for n in nodes if n["type"] == NodeType.PARAGRAPH]
    assert len(paras) == 1
    assert "中文" in paras[0]["text"]


def test_parse_list():
    p = MarkdownParser()
    nodes = p.parse("1. 第一项\n2. 第二项\n")
    lists = [n for n in nodes if n["type"] == NodeType.LIST]
    assert len(lists) == 1
    assert len(lists[0]["items"]) == 2


def test_vocab_row_keeps_trailing_empty_cell():
    # A 6-column row whose last cell (ex_en) is empty ends in "||"; it must stay 6 cells.
    p = MarkdownParser()
    md = (
        "| Word | Pinyin | PoS | Meaning | Example_ZH | Example_EN |\n"
        "|---|---|---|---|---|---|\n"
        "| 学 | xué | verb | learn | 我学中文。||\n"
    )
    table = next(n for n in p.parse(md) if n["type"] == NodeType.VOCAB_TABLE)
    assert table["rows"][0] == ("学", "xué", "verb", "learn", "我学中文。", "", "")


def test_short_vocab_row_is_padded_to_header_width():
    p = MarkdownParser()
    md = (
        "| Word | Pinyin | PoS | Meaning | Example_ZH | Example_Pinyin | Example_EN |\n"
        "|---|---|---|---|---|---|---|\n"
        "| 学 | xué | verb | learn | 我学中文。 |\n"
        "| 书 | shū | noun |\n"
    )
    table = next(n for n in p.parse(md) if n["type"] == NodeType.VOCAB_TABLE)
    assert table["rows"] == [
        ("学", "xué", "verb", "learn", "我学中文。", "", ""),
        ("书", "shū", "noun", "", "", "", ""),
    ]


def test_three_column_vocab_table_meaning_is_last_column():
    p = MarkdownParser()
    md = "| 汉字 | Pinyin | English |\n|---|---|---|\n| 学 | xué | learn |\n"
    table = next(n for n in p.parse(md) if n["type"] == NodeType.VOCAB_TABLE)
    assert table["rows"][0][3] == "learn"


def test_regular_table_keeps_trailing_empty_cell():
    p = MarkdownParser()
    md = "| 列A | 列B | 列C |\n|---|---|---|\n| 值1 | 值2 ||\n"
    table = next(n for n in p.parse(md) if n["type"] == NodeType.TABLE)
    assert table["rows"][0] == ("值1", "值2", "")
