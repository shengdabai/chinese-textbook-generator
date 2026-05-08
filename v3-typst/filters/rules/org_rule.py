from .base_rule import BaseRule, Replacement


class OrgRule(BaseRule):
    def __init__(self, orgs: dict[str, str]):
        self._orgs = orgs

    def apply(self, text: str, dry_run: bool = False) -> tuple[str, list[Replacement]]:
        replacements = []
        for original, replacement in self._orgs.items():
            if original in text:
                replacements.append(Replacement(original, replacement, "组织名"))
                if not dry_run:
                    text = text.replace(original, replacement)
        return text, replacements
