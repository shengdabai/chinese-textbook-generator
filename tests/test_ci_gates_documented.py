"""The CI gates, the README and requirements-dev.txt must not drift apart.

Run: python -m unittest discover -s tests -p 'test_*.py' -v
"""
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORKFLOW = REPO / '.github' / 'workflows' / 'tests.yml'
README = REPO / 'README.md'
INSTALL_DEV = 'pip install -r requirements-dev.txt'
GATES = (
    'ruff check .',
    "python -m unittest discover -s v2-weasyprint -p 'test_*.py'",
    'python -m pytest -q',
    "python -m unittest discover -s tests -p 'test_*.py'",
)


class CiGatesDocumentedTest(unittest.TestCase):
    def test_ruff_is_pinned_only_in_requirements_dev(self):
        reqs = (REPO / 'requirements-dev.txt').read_text(encoding='utf-8')
        self.assertRegex(reqs, r'(?m)^ruff==\d+\.\d+\.\d+$')
        workflow = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn(INSTALL_DEV, workflow)
        self.assertNotIn('ruff==', workflow)

    def test_readme_documents_every_ci_gate(self):
        workflow = WORKFLOW.read_text(encoding='utf-8')
        readme = README.read_text(encoding='utf-8')
        for command in (INSTALL_DEV, *GATES):
            with self.subTest(command=command):
                self.assertIn(command, workflow)  # still what CI runs
                # Once in the English and once in the Chinese half of the README.
                self.assertGreaterEqual(readme.count(command), 2)


if __name__ == '__main__':
    unittest.main()
