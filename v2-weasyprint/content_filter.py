#!/usr/bin/env python3
"""
Content filtering module for Z Turns Chinese.

This module keeps generated teaching materials aligned with a stricter
product policy:
1. Hide real personal names.
2. Hide organization and brand names.
3. Filter teaching-inappropriate topics such as politics, religion,
   relationship content, and work/job contexts.
4. Apply custom regex rules for contact details and role titles.
"""

from __future__ import annotations

import ast
import copy
import re
import warnings
from pathlib import Path
from typing import Any, Optional


DEFAULT_CONFIG = {
    "FILTERS": {
        "name_sanitization": True,
        "organization_sanitization": True,
        "topic_filtering": True,
        "custom_rules": True,
    },
    "STRICT_MODE": True,
    "ABORT_ON_BLOCKED_CONTENT": False,
    "BLOCKED_CONTENT_PLACEHOLDER": "[FILTERED]",
    "DEFAULT_AUTHOR": "Tony Sheng",
    "COPYRIGHT_HOLDER": "Z Turns Chinese",
    "COPYRIGHT_NOTICE": "版权所有 Z Turns Chinese",
    "COMPANY_WEBSITE": "https://zturnsgo.com/",
    "NAMES_REPLACE": {
        "盛长春": "Tony Sheng",
        "Sheng Changchun": "Tony Sheng",
        "盛长": "Tony Sheng",
    },
    "ORG_SUFFIXES": [
        "有限公司",
        "责任公司",
        "股份公司",
        "集团公司",
        "株式会社",
        "Co\\.,? Ltd\\.?",
        "Inc\\.?",
        "Corp\\.?",
        "LLC",
    ],
    "ORG_NAMES_REPLACE": {
        "Google": "[ORGANIZATION]",
        "Apple": "[ORGANIZATION]",
        "Amazon": "[ORGANIZATION]",
        "Meta": "[ORGANIZATION]",
        "OpenAI": "[ORGANIZATION]",
        "TikTok": "[ORGANIZATION]",
        "Douyin": "[ORGANIZATION]",
        "Bilibili": "[ORGANIZATION]",
        "Tencent": "[ORGANIZATION]",
        "Alibaba": "[ORGANIZATION]",
        "ByteDance": "[ORGANIZATION]",
        "Huawei": "[ORGANIZATION]",
        "Baidu": "[ORGANIZATION]",
        "谷歌": "[ORGANIZATION]",
        "苹果": "[ORGANIZATION]",
        "亚马逊": "[ORGANIZATION]",
        "腾讯": "[ORGANIZATION]",
        "阿里巴巴": "[ORGANIZATION]",
        "字节跳动": "[ORGANIZATION]",
        "华为": "[ORGANIZATION]",
        "百度": "[ORGANIZATION]",
        "小红书": "[ORGANIZATION]",
        "抖音": "[ORGANIZATION]",
        "微信": "[ORGANIZATION]",
        "微博": "[ORGANIZATION]",
        "哔哩哔哩": "[ORGANIZATION]",
    },
    "BLOCKED_TOPICS": [
        "政治内容",
        "宗教内容",
        "婚恋关系",
        "职位与工作",
        "公司与品牌",
        "迷信命理",
    ],
    "BLOCKED_KEYWORDS": [
        "政治",
        "政策",
        "政府",
        "体制",
        "外交",
        "宣传",
        "民主",
        "选举",
        "抗议",
        "共产党",
        "台独",
        "港独",
        "藏独",
        "法轮功",
        "宗教",
        "信仰",
        "佛教",
        "道教",
        "基督教",
        "天主教",
        "伊斯兰",
        "清真",
        "寺庙",
        "教堂",
        "恋爱",
        "约会",
        "婚姻",
        "结婚",
        "离婚",
        "相亲",
        "性关系",
        "男朋友",
        "女朋友",
        "夫妻",
        "彩礼",
        "风水",
        "算命",
        "命理",
        "八字",
        "生肖",
        "职位",
        "岗位",
        "职业",
        "就业",
        "招聘",
        "面试",
        "简历",
        "薪资",
        "工资",
        "升职",
        "裁员",
    ],
    "CUSTOM_REGEX": [
        {
            "pattern": r"1[3-9]\d{9}",
            "replacement": "[PHONE_NUMBER]",
            "tag": "联系方式",
            "enabled": True,
        },
        {
            "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "replacement": "[EMAIL]",
            "tag": "联系方式",
            "enabled": True,
        },
        {
            "pattern": r"\d{17}[\dXx]",
            "replacement": "[ID_NUMBER]",
            "tag": "身份信息",
            "enabled": True,
        },
        {
            "pattern": (
                r"(总监|经理|主任|主管|高管|老板|工程师|律师|医生|记者|翻译|顾问|教授|"
                r"总裁|CEO|CFO|COO|CTO|founder|manager|director|engineer|lawyer|"
                r"doctor|journalist|translator|consultant|executive)"
            ),
            "replacement": "[ROLE]",
            "tag": "职位与身份",
            "enabled": True,
            "ignore_case": True,
        },
        {
            "pattern": r"(工作|职位|岗位|职业|就业|招聘|面试|简历|薪资|工资|升职|跳槽|裁员|绩效|加班|实习|劳动合同)",
            "replacement": "[WORK]",
            "tag": "工作与职场",
            "enabled": True,
        },
        {
            "pattern": r"(?<!\])(公司|企业|集团|品牌|商会|工作室|事务所)",
            "replacement": "[ORGANIZATION]",
            "tag": "公司与机构",
            "enabled": True,
        },
        {
            "pattern": r"(恋爱|约会|婚姻|结婚|离婚|相亲|男朋友|女朋友|夫妻|婆媳|丈母娘|彩礼|性关系|同居|婚礼|新郎|新娘)",
            "replacement": "[RELATIONSHIP]",
            "tag": "婚恋关系",
            "enabled": True,
        },
        {
            "pattern": r"(宗教|信仰|佛教|道教|基督教|天主教|伊斯兰|清真|寺庙|教堂|法轮功|无神论)",
            "replacement": "[RELIGION]",
            "tag": "宗教内容",
            "enabled": True,
        },
        {
            "pattern": r"(政治|政策|政府|体制|外交|地缘政治|领导人|共产党|民主|选举|抗议|台独|港独|藏独)",
            "replacement": "[POLITICS]",
            "tag": "政治内容",
            "enabled": True,
        },
        {
            "pattern": r"(风水|算命|命理|八字|生肖|改运|面相)",
            "replacement": "[BELIEF]",
            "tag": "迷信命理",
            "enabled": True,
        },
    ],
}


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""

    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]

    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def _parse_key(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        try:
            parsed = ast.literal_eval(value)
            return str(parsed)
        except (SyntaxError, ValueError):
            return value[1:-1]
    return value


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    for index, char in enumerate(line):
        if char == "\\" and not escaped:
            escaped = True
            continue
        if char == "'" and not in_double and not escaped:
            in_single = not in_single
        elif char == '"' and not in_single and not escaped:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:index]
        escaped = False
    return line


def _preprocess_yaml(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        cleaned = _strip_comment(raw_line).rstrip()
        if not cleaned.strip():
            continue
        indent = len(cleaned) - len(cleaned.lstrip(" "))
        content = cleaned.lstrip(" ")
        lines.append((indent, content))
    return lines


def _parse_mapping(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(lines):
        current_indent, content = lines[index]
        if current_indent < indent:
            break
        if current_indent != indent or content.startswith("- "):
            break

        key, sep, raw_value = content.partition(":")
        if not sep:
            raise ValueError(f"Invalid YAML line: {content}")

        parsed_key = _parse_key(key)
        raw_value = raw_value.strip()
        index += 1

        if raw_value:
            result[parsed_key] = _parse_scalar(raw_value)
            continue

        if index >= len(lines) or lines[index][0] <= current_indent:
            result[parsed_key] = {}
            continue

        next_indent, next_content = lines[index]
        if next_content.startswith("- "):
            result[parsed_key], index = _parse_list(lines, index, next_indent)
        else:
            result[parsed_key], index = _parse_mapping(lines, index, next_indent)
    return result, index


def _parse_list(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(lines):
        current_indent, content = lines[index]
        if current_indent < indent:
            break
        if current_indent != indent or not content.startswith("- "):
            break

        item_body = content[2:].strip()
        index += 1

        if not item_body:
            result.append(None)
            continue

        if ":" not in item_body:
            result.append(_parse_scalar(item_body))
            continue

        key, _, raw_value = item_body.partition(":")
        parsed_key = _parse_key(key)
        raw_value = raw_value.strip()
        item: dict[str, Any] = {}

        if raw_value:
            item[parsed_key] = _parse_scalar(raw_value)
        elif index < len(lines) and lines[index][0] > current_indent:
            next_indent, next_content = lines[index]
            if next_content.startswith("- "):
                item[parsed_key], index = _parse_list(lines, index, next_indent)
            else:
                item[parsed_key], index = _parse_mapping(lines, index, next_indent)
        else:
            item[parsed_key] = {}

        while index < len(lines):
            next_indent, next_content = lines[index]
            if next_indent < current_indent + 2:
                break
            if next_indent != current_indent + 2 or next_content.startswith("- "):
                break

            sub_key, sep, sub_value = next_content.partition(":")
            if not sep:
                raise ValueError(f"Invalid YAML line: {next_content}")

            parsed_sub_key = _parse_key(sub_key)
            sub_value = sub_value.strip()
            index += 1

            if sub_value:
                item[parsed_sub_key] = _parse_scalar(sub_value)
                continue

            if index < len(lines) and lines[index][0] > next_indent:
                child_indent, child_content = lines[index]
                if child_content.startswith("- "):
                    item[parsed_sub_key], index = _parse_list(lines, index, child_indent)
                else:
                    item[parsed_sub_key], index = _parse_mapping(lines, index, child_indent)
            else:
                item[parsed_sub_key] = {}

        result.append(item)
    return result, index


def _load_yaml_simple(text: str) -> dict[str, Any]:
    lines = _preprocess_yaml(text)
    if not lines:
        return {}
    parsed, _ = _parse_mapping(lines, 0, 0)
    return parsed


def _deep_merge(default_value: Any, parsed_value: Any) -> Any:
    if parsed_value is None:
        return copy.deepcopy(default_value)

    if isinstance(default_value, dict):
        merged = copy.deepcopy(default_value)
        if not isinstance(parsed_value, dict):
            return merged
        for key, value in parsed_value.items():
            if key in merged:
                merged[key] = _deep_merge(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged

    return copy.deepcopy(parsed_value)


def load_config(config_path: Optional[Path] = None) -> dict[str, Any]:
    """Load config from YAML file, fallback to defaults."""
    if config_path is None:
        config_path = Path(__file__).parent / "content_filter_config.yaml"

    if not config_path.exists():
        return copy.deepcopy(DEFAULT_CONFIG)

    try:
        text = config_path.read_text(encoding="utf-8")
        parsed = _load_yaml_simple(text)
        if not isinstance(parsed, dict):
            raise ValueError("Parsed config is not a mapping")
        return _deep_merge(DEFAULT_CONFIG, parsed)
    except Exception as exc:
        warnings.warn(
            f"Failed to parse content filter config at {config_path}: {exc}. "
            "Using default policy settings."
        )
        return copy.deepcopy(DEFAULT_CONFIG)


class ContentFilter:
    """Sanitize and filter content for teaching-safe output."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = load_config(config_path)
        self.filters = self.config.get("FILTERS", DEFAULT_CONFIG["FILTERS"])
        self.placeholder = self.config.get(
            "BLOCKED_CONTENT_PLACEHOLDER",
            DEFAULT_CONFIG["BLOCKED_CONTENT_PLACEHOLDER"],
        )
        self._build_patterns()

    def _build_patterns(self) -> None:
        org_suffixes = self.config.get("ORG_SUFFIXES", DEFAULT_CONFIG["ORG_SUFFIXES"])
        literal_suffixes = [
            re.escape(suffix)
            for suffix in org_suffixes
            if not any(char in suffix for char in r"\.,?+*()[]{}|")
        ]
        regex_suffixes = [
            suffix
            for suffix in org_suffixes
            if any(char in suffix for char in r"\.,?+*()[]{}|")
        ]
        suffix_parts = literal_suffixes + regex_suffixes

        self._org_suffix_re = None
        if suffix_parts:
            suffix_pattern = "|".join(suffix_parts)
            self._org_suffix_re = re.compile(
                r"([\u4e00-\u9fff]{2,12}(?:" + suffix_pattern + r"))"
            )

    def _replace_literal(self, text: str, needle: str, replacement: str) -> str:
        if re.search(r"[A-Za-z]", needle):
            return re.sub(re.escape(needle), replacement, text, flags=re.IGNORECASE)
        return text.replace(needle, replacement)

    def sanitize_names(self, text: str) -> str:
        """Replace configured personal names."""
        if not self.filters.get("name_sanitization", True):
            return text

        name_map = self.config.get("NAMES_REPLACE", DEFAULT_CONFIG["NAMES_REPLACE"])
        for name, replacement in name_map.items():
            text = self._replace_literal(text, name, replacement)
        return text

    def sanitize_organizations(self, text: str) -> str:
        """Replace configured organization names and formal entities."""
        if not self.filters.get("organization_sanitization", True):
            return text

        org_map = self.config.get("ORG_NAMES_REPLACE", DEFAULT_CONFIG["ORG_NAMES_REPLACE"])
        for organization, replacement in org_map.items():
            text = self._replace_literal(text, organization, replacement)

        text = re.sub(
            r"\[ORGANIZATION\](?:公司|企业|集团|品牌|商会|工作室|事务所)",
            "[ORGANIZATION]",
            text,
        )

        if self._org_suffix_re:
            text = self._org_suffix_re.sub("[ORGANIZATION]", text)

        return text

    def check_topics(self, text: str, book_key: str = "", file_path: str = "") -> list[str]:
        """
        Return a unique list of blocked keywords or regex tags found in text.
        """
        if not self.filters.get("topic_filtering", True):
            return []

        found: list[str] = []

        for keyword in self.config.get("BLOCKED_KEYWORDS", DEFAULT_CONFIG["BLOCKED_KEYWORDS"]):
            if keyword and keyword in text and keyword not in found:
                found.append(keyword)

        if self.filters.get("custom_rules", True):
            for rule in self.config.get("CUSTOM_REGEX", DEFAULT_CONFIG["CUSTOM_REGEX"]):
                if not rule.get("enabled", True):
                    continue
                tag = rule.get("tag")
                pattern = rule.get("pattern", "")
                if not tag or not pattern:
                    continue

                flags = re.IGNORECASE if rule.get("ignore_case", False) else 0
                try:
                    if re.search(pattern, text, flags=flags) and tag not in found:
                        found.append(tag)
                except re.error as exc:
                    warnings.warn(
                        f"Invalid custom regex '{pattern}' while checking topics: {exc}"
                    )

        return found

    def filter_blocked_keywords(self, text: str) -> str:
        """Replace blocked keywords with the configured placeholder."""
        if not self.filters.get("topic_filtering", True):
            return text

        for keyword in self.config.get("BLOCKED_KEYWORDS", DEFAULT_CONFIG["BLOCKED_KEYWORDS"]):
            if keyword:
                text = text.replace(keyword, self.placeholder)
        return text

    def apply_custom_rules(self, text: str) -> str:
        """Apply custom regex replacement rules."""
        if not self.filters.get("custom_rules", True):
            return text

        for rule in self.config.get("CUSTOM_REGEX", DEFAULT_CONFIG["CUSTOM_REGEX"]):
            if not rule.get("enabled", True):
                continue

            pattern = rule.get("pattern", "")
            replacement = rule.get("replacement", self.placeholder)
            flags = re.IGNORECASE if rule.get("ignore_case", False) else 0
            if not pattern:
                continue

            try:
                text = re.sub(pattern, replacement, text, flags=flags)
            except re.error as exc:
                warnings.warn(f"Invalid custom regex '{pattern}': {exc}")
        return text

    def sanitize(self, text: str, book_key: str = "", file_path: str = "") -> tuple[str, list[str]]:
        """Apply the full sanitization pipeline and return flagged topics."""
        flagged = self.check_topics(text, book_key=book_key, file_path=file_path)
        if flagged:
            warnings.warn(
                f"[{book_key}] Blocked content found in {file_path}: {flagged}"
            )

        text = self.sanitize_names(text)
        text = self.sanitize_organizations(text)
        text = self.filter_blocked_keywords(text)
        text = self.apply_custom_rules(text)
        return text, flagged
