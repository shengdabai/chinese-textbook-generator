#!/usr/bin/env python3
"""拆分 appendix 为临时文件，处理后合并回去。"""
import re, sys
from pathlib import Path

ROW_RE = re.compile(r"^\|.+\|$")

def main():
    path = Path(sys.argv[1])
    action = sys.argv[2]  # "split" or "merge"
    tmp_dir = path.parent / "_tmp_parts"

    if action == "split":
        tmp_dir.mkdir(exist_ok=True)
        lines = path.read_text(encoding="utf-8").splitlines()
        sections = []
        start = 0
        for i, l in enumerate(lines):
            if l.startswith("### ") and i > 0:
                sections.append((start, i - 1))
                start = i
        sections.append((start, len(lines) - 1))

        for idx, (s, e) in enumerate(sections):
            part = lines[s:e+1]
            (tmp_dir / f"part_{idx:02d}.md").write_text("\n".join(part) + "\n", encoding="utf-8")
        print(f"Split into {len(sections)} parts in {tmp_dir}")

    elif action == "merge":
        parts = sorted(tmp_dir.glob("part_*.md"))
        merged = "\n".join(p.read_text(encoding="utf-8").rstrip() for p in parts) + "\n"
        path.write_text(merged, encoding="utf-8")
        # cleanup
        for p in parts:
            p.unlink()
        tmp_dir.rmdir()
        print(f"Merged {len(parts)} parts → {path.name}")

if __name__ == "__main__":
    main()
