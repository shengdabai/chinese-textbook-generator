from .base_rule import BaseRule, Replacement


class KeywordRule(BaseRule):
    def __init__(self, keywords: list[str]):
        self._keywords = keywords

    def apply(self, text: str, dry_run: bool = False) -> tuple[str, list[Replacement]]:
        replacements = []
        for kw in self._keywords:
            if kw in text:
                replacements.append(Replacement(kw, "[FILTERED]", "敏感词"))
                if not dry_run:
                    text = text.replace(kw, "[FILTERED]")
        return text, replacements

    def get_flagged(self, text: str) -> list[str]:
        return [kw for kw in self._keywords if kw in text]
