"""Where the HSK prep guides live.

Shared by generate_hsk_content.py (writes them), enrich_hsk_content.py
(rewrites parts of them) and merge_hsk_levels.py (merges them per level).
v3-typst/generate.py reads the same tree as ``../v2-weasyprint/HSK备考``.
"""
from pathlib import Path

HSK_ROOT = Path(__file__).resolve().parent / 'HSK备考'
