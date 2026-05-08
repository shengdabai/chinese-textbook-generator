import re
from .base_rule import BaseRule, Replacement


class RegexRule(BaseRule):
    def __init__(self, rules: list[dict]):
        self._rules = [r for r in rules if r.get("enabled", True)]

    def apply(self, text: str, dry_run: bool = False) -> tuple[str, list[Replacement]]:
        replacements = []
        for rule in self._rules:
            pattern = rule["pattern"]
            replacement = rule["replacement"]
            tag = rule.get("tag", "正则")
            matches = re.findall(pattern, text)
            for match in matches:
                replacements.append(Replacement(match, replacement, tag))
            if not dry_run:
                text = re.sub(pattern, replacement, text)
        return text, replacements
