import sys, os
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
    assert tables[0]["rows"][0] == ("学", "xué", "learn")


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
