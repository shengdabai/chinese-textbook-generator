"""
Privacy Filter Module (from Grok + Claude + Kimi方案)
Implements PII detection and anonymization for raw teaching notes.
Uses regex + keyword matching for immediate execution without external NLP models.
"""

import re
from config import PRIVACY_PATTERNS, PRIVACY_REPLACEMENTS, PRIVACY_WHITELIST


class PrivacyFilter:
    """Filters personally identifiable information from text."""

    def __init__(self):
        self.patterns = {k: re.compile(v) for k, v in PRIVACY_PATTERNS.items()}
        self.replacements = PRIVACY_REPLACEMENTS
        self.whitelist = PRIVACY_WHITELIST
        self.sensitive_keywords = [
            "政治", "政府", "政策", "选举", "党", "抗议",
            "government", "politics", "election", "protest", "regime",
        ]
        self.findings = []

    def scan(self, text: str) -> list:
        """Scan text for PII and sensitive content. Returns list of findings."""
        self.findings = []

        # Check regex patterns
        for category, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                matched_text = match.group()
                # Skip whitelisted terms (common in educational content)
                if matched_text in self.whitelist:
                    continue
                self.findings.append({
                    "category": category,
                    "text": matched_text,
                    "start": match.start(),
                    "end": match.end(),
                    "risk": "high",
                })

        # Check sensitive keywords
        for keyword in self.sensitive_keywords:
            if keyword.lower() in text.lower():
                idx = text.lower().find(keyword.lower())
                self.findings.append({
                    "category": "sensitive_topic",
                    "text": keyword,
                    "start": idx,
                    "end": idx + len(keyword),
                    "risk": "high",
                })

        return self.findings

    def anonymize(self, text: str) -> str:
        """Remove or replace all detected PII in text."""
        result = text

        # Apply regex replacements, respecting whitelist
        def _replace_if_not_safe(pattern, replacement):
            def _repl(match):
                if match.group() in self.whitelist:
                    return match.group()
                return replacement
            return _repl

        result = self.patterns["person_names"].sub(_replace_if_not_safe(self.patterns["person_names"], self.replacements["person"]), result)
        result = self.patterns["phone_numbers"].sub(_replace_if_not_safe(self.patterns["phone_numbers"], self.replacements["phone"]), result)
        result = self.patterns["email"].sub(_replace_if_not_safe(self.patterns["email"], self.replacements["email"]), result)
        result = self.patterns["addresses"].sub(_replace_if_not_safe(self.patterns["addresses"], self.replacements["address"]), result)

        # Remove sensitive topic paragraphs
        lines = result.split("\n")
        clean_lines = []
        for line in lines:
            is_sensitive = False
            for keyword in self.sensitive_keywords:
                if keyword.lower() in line.lower():
                    is_sensitive = True
                    break
            if not is_sensitive:
                clean_lines.append(line)
            else:
                clean_lines.append("[SENSITIVE CONTENT REMOVED]")

        return "\n".join(clean_lines)

    def get_report(self) -> dict:
        """Generate a privacy scan report."""
        return {
            "total_findings": len(self.findings),
            "high_risk": sum(1 for f in self.findings if f["risk"] == "high"),
            "categories": list(set(f["category"] for f in self.findings)),
            "details": self.findings,
        }


def demo_privacy_filter():
    """Demonstrate the privacy filter with sample text."""
    sample = """
    Today John Smith discussed his experience working at World Bank.
    His wife Mary lives at 123 Oak Street, Arlington.
    Contact: john.smith@worldbank.org, 202-555-0147.
    He mentioned some government policies about education.
    The student wants to learn how to order food in Chinese.
    """

    pf = PrivacyFilter()
    findings = pf.scan(sample)
    clean = pf.anonymize(sample)
    report = pf.get_report()

    print("=== Privacy Filter Demo ===")
    print(f"Findings: {report['total_findings']}")
    print(f"High risk: {report['high_risk']}")
    print(f"\nCleaned text:\n{clean}")
    return clean


if __name__ == "__main__":
    demo_privacy_filter()
