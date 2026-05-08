from .base_rule import BaseRule, Replacement


class NameRule(BaseRule):
    def __init__(self, names: dict[str, str]):
        self._names = names

    def apply(self, text: str, dry_run: bool = False) -> tuple[str, list[Replacement]]:
        replacements = []
        for original, replacement in self._names.items():
            if original in text:
                replacements.append(Replacement(original, replacement, "名字"))
                if not dry_run:
                    text = text.replace(original, replacement)
        return text, replacements
