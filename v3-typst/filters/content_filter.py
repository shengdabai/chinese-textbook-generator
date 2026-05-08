from dataclasses import dataclass, field
import yaml

from .rules.base_rule import Replacement
from .rules.name_rule import NameRule
from .rules.org_rule import OrgRule
from .rules.regex_rule import RegexRule
from .rules.keyword_rule import KeywordRule


@dataclass
class FilterResult:
    text: str
    flagged_topics: list[str] = field(default_factory=list)
    replacements: list[Replacement] = field(default_factory=list)


class ContentFilter:
    def __init__(self, config_path: str):
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        self._rules = [
            NameRule(cfg.get("NAMES_REPLACE", {})),
            OrgRule(cfg.get("ORG_NAMES_REPLACE", {})),
            RegexRule(cfg.get("CUSTOM_REGEX", [])),
        ]
        self._keyword_rule = KeywordRule(cfg.get("BLOCKED_KEYWORDS", []))

    def filter(self, text: str, dry_run: bool = False) -> FilterResult:
        all_replacements: list[Replacement] = []

        for rule in self._rules:
            text, reps = rule.apply(text, dry_run=dry_run)
            all_replacements.extend(reps)

        flagged = self._keyword_rule.get_flagged(text)
        text, reps = self._keyword_rule.apply(text, dry_run=dry_run)
        all_replacements.extend(reps)

        return FilterResult(
            text=text,
            flagged_topics=flagged,
            replacements=all_replacements,
        )
