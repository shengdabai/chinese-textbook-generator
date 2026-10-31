"""create_kdp_series_b01_b10's helpers must work when the module is imported, not only via main()."""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import create_kdp_series_b01_b10 as kdp_module

V3 = Path(__file__).resolve().parent.parent
MD = "# 第一章\n\n| 汉字 | Pinyin | English |\n|---|---|---|\n| 学 | xué | learn |\n"


@pytest.fixture
def kdp(monkeypatch):
    # The script's paths are relative to the directory it is run from; point them at this checkout.
    monkeypatch.setattr(kdp_module, "V3_DIR", V3)
    monkeypatch.setattr(kdp_module, "TEMPLATE_PATH", V3 / "templates" / "textbook.typ")
    yield kdp_module
    kdp_module._pipeline.cache_clear()
    kdp_module._kdp_template.cache_clear()


def test_md_to_body_without_main(kdp, tmp_path):
    md = tmp_path / "book.md"
    md.write_text(MD, encoding="utf-8")
    body = kdp.md_to_body(md)
    assert "= 第一章" in body
    assert "#vocab-table((" in body
    assert "[learn]" in body


def test_build_typst_source_without_main(kdp, tmp_path):
    md = tmp_path / "book.md"
    md.write_text(MD, encoding="utf-8")
    src = kdp.build_typst_source(kdp.SERIES_META[0], md)
    assert f'#let book-title = "{kdp.SERIES_META[0].title}"' in src
    assert "width: 6in" in src  # the KDP trim-size template, not the A4 one
    assert "[learn]" in src
