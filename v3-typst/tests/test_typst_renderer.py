import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from parsers.md_parser import NodeType
from renderers.typst_renderer import TypstRenderer


def make_renderer():
    return TypstRenderer()


def test_heading_level1():
    r = make_renderer()
    node = {"type": NodeType.HEADING, "level": 1, "text": "第一章"}
    assert r.render_node(node) == "= 第一章\n"


def test_heading_level2():
    r = make_renderer()
    node = {"type": NodeType.HEADING, "level": 2, "text": "小节"}
    assert r.render_node(node) == "== 小节\n"


def test_paragraph():
    r = make_renderer()
    node = {"type": NodeType.PARAGRAPH, "text": "这是段落。"}
    assert r.render_node(node) == "这是段落。\n\n"


def test_vocab_table():
    r = make_renderer()
    node = {
        "type": NodeType.VOCAB_TABLE,
        "rows": [("学习", "xué xí", "study")],
    }
    result = r.render_node(node)
    assert "#vocab-table" in result
    assert "学习" in result
    assert "xué xí" in result
    assert "study" in result


def test_ordered_list():
    r = make_renderer()
    node = {"type": NodeType.LIST, "ordered": True, "items": ["第一", "第二"]}
    result = r.render_node(node)
    assert "+ 第一" in result
    assert "+ 第二" in result


def test_unordered_list():
    r = make_renderer()
    node = {"type": NodeType.LIST, "ordered": False, "items": ["苹果", "香蕉"]}
    result = r.render_node(node)
    assert "- 苹果" in result


def test_render_document():
    r = make_renderer()
    nodes = [
        {"type": NodeType.HEADING, "level": 1, "text": "测试"},
        {"type": NodeType.PARAGRAPH, "text": "内容"},
    ]
    result = r.render(nodes)
    assert "= 测试" in result
    assert "内容" in result
