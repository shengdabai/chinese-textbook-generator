"""Checks for the COMMON_TRANSLATIONS glossary in generate_hsk_content.py.

The generator runs at import time, so these tests read the source with `ast`
instead of importing it.

Run: python3 -m pytest v2-weasyprint/test_hsk_translations.py
  or python3 -m unittest discover -s v2-weasyprint -p 'test_*.py'
"""
import ast
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'generate_hsk_content.py'


def glossary_entries():
    """Return [(word, english, line)] in source order."""
    tree = ast.parse(SCRIPT.read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            getattr(t, 'id', None) == 'COMMON_TRANSLATIONS' for t in node.targets
        ):
            return [(k.value, v.value, k.lineno) for k, v in zip(node.value.keys, node.value.values)]
    raise AssertionError('COMMON_TRANSLATIONS not found')


class GlossaryTest(unittest.TestCase):
    def test_every_word_appears_once(self):
        # A dict literal keeps the LAST duplicate, so a repeated word silently
        # overrides the gloss written for an earlier HSK level.
        first_line = {}
        repeats = []
        for word, _, line in glossary_entries():
            if word in first_line:
                repeats.append(f'{word} (L{first_line[word]} and L{line})')
            else:
                first_line[word] = line
        self.assertEqual(repeats, [], f'{len(repeats)} repeated words, e.g. {repeats[:5]}')

    def test_first_gloss_is_the_one_kept(self):
        glossary = {word: english for word, english, _ in glossary_entries()}
        self.assertEqual(glossary['爸爸'], 'father')
        self.assertEqual(glossary['妈妈'], 'mother')
        self.assertEqual(glossary['在'], 'at/in/on')
        self.assertEqual(glossary['衣服'], 'clothes')


if __name__ == '__main__':
    unittest.main()
