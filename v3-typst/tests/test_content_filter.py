import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from filters.content_filter import ContentFilter, FilterResult

CONFIG = os.path.join(os.path.dirname(__file__), "../config/filter_rules.yaml")


def make_filter():
    return ContentFilter(CONFIG)


def test_name_replacement():
    f = make_filter()
    result = f.filter("盛长春是老师。")
    assert "盛长春" not in result.text
    assert "Tony Sheng" in result.text


def test_org_replacement():
    f = make_filter()
    result = f.filter("他在Google工作。")
    assert "Google" not in result.text
    assert "[ORGANIZATION]" in result.text


def test_phone_regex():
    f = make_filter()
    result = f.filter("电话：13812345678")
    assert "13812345678" not in result.text
    assert "[PHONE_NUMBER]" in result.text


def test_email_regex():
    f = make_filter()
    result = f.filter("邮箱：test@example.com")
    assert "test@example.com" not in result.text
    assert "[EMAIL]" in result.text


def test_dry_run_no_replacement():
    f = make_filter()
    result = f.filter("盛长春", dry_run=True)
    assert "盛长春" in result.text
    assert len(result.replacements) > 0


def test_filter_result_type():
    f = make_filter()
    result = f.filter("测试文本")
    assert isinstance(result, FilterResult)
    assert isinstance(result.text, str)
    assert isinstance(result.flagged_topics, list)
    assert isinstance(result.replacements, list)
