#!/usr/bin/env python3
"""v3-typst 统一生成入口"""
import argparse
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"
OUTPUT = BASE / "output"
OUTPUT.mkdir(exist_ok=True)

sys.path.insert(0, str(BASE))

from filters.content_filter import ContentFilter
from parsers.md_parser import MarkdownParser
from renderers.typst_renderer import TypstRenderer

FILTER = ContentFilter(str(BASE / "config" / "filter_rules.yaml"))
PARSER = MarkdownParser()
RENDERER = TypstRenderer()

HSK_LEVELS = {
    "1":  "入门 · Entry",
    "2":  "基础 · Foundation",
    "3":  "进阶 · Advancing",
    "4":  "突破 · Breakthrough",
    "5":  "精进 · Refinement",
    "6":  "卓越 · Excellence",
    "79": "大师 · Mastery",
}

V2_HSK_ROOT = Path("../v2-weasyprint/HSK备考")
HSK_OUTPUT_DIR = Path("output")

# HSK levels where full-text Chinese annotation is applied (all paragraphs)
FULL_ANNOTATION_LEVELS = {"1", "2"}


def v3_content_dir(level: str) -> Path:
    """Return v3 content override directory for a given HSK level."""
    if level == "1":
        return BASE / "content"
    return BASE / f"content-hsk{level}"


def md_files_for_hsk(level: str) -> list[Path]:
    """按部分顺序收集 HSK{level} 的所有 Markdown 文件。
    v3 content 目录下的同名文件优先于 v2 源文件。
    """
    candidates = [
        V2_HSK_ROOT / f"hsk{level}-prep",
    ]
    prep_dir = next((d for d in candidates if d.exists()), None)
    if prep_dir is None:
        return []

    v2_files = sorted(prep_dir.rglob("*.md"))

    # Build override map from v3 content dir (keyed by filename)
    v3_overrides: dict[str, Path] = {}
    v3_dir = v3_content_dir(level)
    if v3_dir.exists():
        for p in v3_dir.rglob("*.md"):
            v3_overrides[p.name] = p

    result = []
    for p in v2_files:
        result.append(v3_overrides.get(p.name, p))
    return result


HARD_BLOCK_KEYWORDS = {
    "习近平", "毛泽东", "天安门事件", "六四事件", "文化大革命",
    "法轮功", "法轮大法", "台独", "港独", "疆独", "藏独",
    "中共", "总书记", "国家主席", "全国人大", "政治局",
}


def md_to_body(md_path: Path, annotate: bool = False) -> str:
    """单个 MD 文件 → Typst body 片段。"""
    raw = md_path.read_text(encoding="utf-8")
    result = FILTER.filter(raw)
    if result.flagged_topics:
        print(f"  ⚠ {md_path.name} 命中敏感话题: {result.flagged_topics}")
    if result.replacements:
        print(f"  ✎ {md_path.name} 替换 {len(result.replacements)} 处")
    # Hard-block: abort if truly dangerous keywords slip through unfiltered
    for kw in HARD_BLOCK_KEYWORDS:
        if kw in result.text:
            print(f"  ✗ HARD BLOCK: '{kw}' 仍存在于 {md_path.name}，请手动修改源文件")
            sys.exit(2)
    nodes = PARSER.parse(result.text)
    return RENDERER.render(nodes, annotate=annotate)


def build_hsk_typ(level: str, title: str) -> str:
    """合并所有章节，生成完整 HSK Typst 源码。"""
    md_files = md_files_for_hsk(level)
    if not md_files:
        print(f"未找到 HSK {level} 源文件，路径: {V2_HSK_ROOT}/hsk{level}-prep")
        sys.exit(1)

    print(f"找到 {len(md_files)} 个章节文件...")
    template_src = (TEMPLATES / "hsk-prep.typ").read_text(encoding="utf-8")
    annotate = level in FULL_ANNOTATION_LEVELS

    body_parts = []
    for md in md_files:
        try:
            rel = md.relative_to(V2_HSK_ROOT)
        except ValueError:
            rel = md.relative_to(BASE)
        print(f"  处理: {rel}")
        body_parts.append(md_to_body(md, annotate=annotate))

    body = "\n".join(body_parts)

    # HSK 79 → display as "7-9"
    display_level = "7-9" if level == "79" else level

    return f"""#let hsk-level = "{display_level}"
#let hsk-title = "{title}"

{template_src}

{body}
"""


def compile_typ(typ_src: str, out_pdf: Path, tmp_name: str = "_build_tmp.typ") -> bool:
    """写入临时 .typ 文件到 templates/ 并编译，返回是否成功。"""
    import tempfile, os
    # Use a unique temp file per call to avoid race conditions in parallel builds
    fd, tmp_path = tempfile.mkstemp(suffix=".typ", dir=TEMPLATES)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(typ_src)
        result = subprocess.run(
            ["typst", "compile", tmp_path, str(out_pdf)],
            capture_output=True, text=True,
        )
        if result.stderr.strip():
            errors = [l for l in result.stderr.splitlines() if "error" in l.lower()]
            if errors:
                print("\n".join(errors))
        return result.returncode == 0
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def cmd_hsk(args):
    level = args.level
    title = HSK_LEVELS.get(level, f"HSK {level}")
    print(f"生成 HSK {level} 备考指南 ({title})...")

    typ_src = build_hsk_typ(level, title)

    out_pdf = OUTPUT / f"ZTurns_HSK{level}_Prep.pdf"
    print(f"编译中...")
    if compile_typ(typ_src, out_pdf):
        print(f"✓ 生成成功: {out_pdf}")
        # 同时复制到 HSK考试指南 目录
        HSK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        dest = HSK_OUTPUT_DIR / out_pdf.name
        dest.write_bytes(out_pdf.read_bytes())
        print(f"✓ 已复制到: {dest}")
    else:
        print(f"✗ 编译失败")
        sys.exit(1)


def cmd_textbook(args):
    md_path = Path(args.md)
    if not md_path.exists():
        print(f"文件不存在: {md_path}")
        sys.exit(1)

    number = args.number
    title = args.title
    subtitle = args.subtitle
    color = args.color

    print(f"生成教材书 #{number}: {title} — {subtitle}")
    print(f"  源文件: {md_path}")

    template_src = (TEMPLATES / "textbook.typ").read_text(encoding="utf-8")
    body = md_to_body(md_path, annotate=False)

    typ_src = f"""#let book-number = "{number}"
#let book-title = "{title}"
#let book-subtitle = "{subtitle}"
#let book-color = "{color}"

{template_src}

{body}
"""

    if args.out:
        out_pdf = Path(args.out)
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
    else:
        safe_title = title.replace(" ", "_").replace("/", "-")
        out_pdf = OUTPUT / f"ZTC_Book{number}_{safe_title}.pdf"

    print("编译中...")
    if compile_typ(typ_src, out_pdf):
        print(f"✓ 生成成功: {out_pdf}")
    else:
        print("✗ 编译失败")
        sys.exit(1)


def cmd_validate(args):
    md_path = Path(args.file)
    if not md_path.exists():
        print(f"文件不存在: {md_path}")
        sys.exit(1)

    level = args.level
    title = HSK_LEVELS.get(level, f"HSK {level}")
    template_src = (TEMPLATES / "hsk-prep.typ").read_text(encoding="utf-8")
    body = md_to_body(md_path)
    typ_src = f"""#let hsk-level = "{level}"
#let hsk-title = "{title}"

{template_src}

{body}
"""
    out_pdf = OUTPUT / (md_path.stem + ".pdf")
    if compile_typ(typ_src, out_pdf, "_validate_tmp.typ"):
        print(f"✓ 编译成功: {out_pdf}")
    else:
        print(f"✗ 编译失败")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="v3-typst 中文教学 PDF 生成器")
    sub = parser.add_subparsers(dest="cmd")

    hsk_cmd = sub.add_parser("hsk", help="生成 HSK 备考指南")
    hsk_cmd.add_argument("--level", required=True, help="HSK 级别 (1/2/3/4/5/6/79)")

    val = sub.add_parser("validate", help="单文件 dry-run 验证")
    val.add_argument("--file", required=True, help="Markdown 文件路径")
    val.add_argument("--level", default="1", help="HSK 级别 (default: 1)")

    tb = sub.add_parser("textbook", help="生成教材书 PDF")
    tb.add_argument("--md", required=True, help="Markdown 源文件路径")
    tb.add_argument("--number", required=True, help="书号，如 51")
    tb.add_argument("--title", required=True, help="英文书名")
    tb.add_argument("--subtitle", required=True, help="中文副标题")
    tb.add_argument("--color", default="#1565C0", help="主题色 hex，如 #E53935")
    tb.add_argument("--out", default=None, help="输出 PDF 路径（默认 output/ 目录）")

    args = parser.parse_args()
    if args.cmd == "hsk":
        cmd_hsk(args)
    elif args.cmd == "validate":
        cmd_validate(args)
    elif args.cmd == "textbook":
        cmd_textbook(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
