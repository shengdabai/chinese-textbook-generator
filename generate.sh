#!/bin/bash
# Z Turns Chinese — 统一生成入口（默认使用 v3-typst）
# 用法:
#   ./generate.sh hsk --level 1        生成 HSK1 备考指南
#   ./generate.sh hsk --level 2        生成 HSK2 备考指南
#   ./generate.sh hsk --level 79       生成 HSK7-9 备考指南
#   ./generate.sh validate --file x.md --level 3   单文件验证

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
V3_DIR="$SCRIPT_DIR/v3-typst"
PYTHON="${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python3}"
PYTHON="${PYTHON:-python3}"

exec "$PYTHON" "$V3_DIR/generate.py" "$@"
