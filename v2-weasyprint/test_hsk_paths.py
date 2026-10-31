"""generate_hsk_content, enrich_hsk_content and merge_hsk_levels must agree on where
the HSK prep guides live, so enriched content is what gets merged.

Import-only: the generators build their paths inside main(), so the per-level
directories are checked in the source instead of by running a generation.

Run: python -m unittest discover -s v2-weasyprint -p 'test_*.py' -v
"""
import ast
import re
import unittest
from pathlib import Path

import enrich_hsk_content
import generate_hsk_content
import merge_hsk_levels

HERE = Path(__file__).resolve().parent
SCRIPTS = (generate_hsk_content, enrich_hsk_content, merge_hsk_levels)
PREP_DIR = re.compile(r'hsk[\w{}]*-prep')  # also matches f'hsk{level}-prep'


def source_tree(module):
    return ast.parse(Path(module.__file__).read_text(encoding='utf-8'))


class HskRootTest(unittest.TestCase):
    def test_scripts_share_one_root_inside_v2_weasyprint(self):
        # v3-typst/generate.py reads the same tree as ../v2-weasyprint/HSK备考.
        for module in SCRIPTS:
            with self.subTest(module=module.__name__):
                self.assertEqual(module.HSK_ROOT, HERE / 'HSK备考')

    def test_every_prep_dir_is_built_from_hsk_root(self):
        for module in SCRIPTS:
            for node in ast.walk(source_tree(module)):
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div) and PREP_DIR.search(ast.unparse(node.right)):
                    with self.subTest(module=module.__name__, line=node.lineno):
                        self.assertEqual(ast.unparse(node.left), 'HSK_ROOT')

    def test_merge_reads_every_dir_enrich_writes(self):
        merged = {src for src, _ in merge_hsk_levels.LEVELS}
        enriched = {
            node.value for node in ast.walk(source_tree(enrich_hsk_content))
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and PREP_DIR.fullmatch(node.value)
        }
        self.assertTrue(enriched)
        self.assertLessEqual(enriched, merged)


if __name__ == '__main__':
    unittest.main()
