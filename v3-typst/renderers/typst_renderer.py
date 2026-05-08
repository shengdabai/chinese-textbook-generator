import re
from pypinyin import pinyin as get_pinyin, Style
from parsers.md_parser import NodeType


class TypstRenderer:
    def render(self, nodes: list[dict], annotate: bool = False) -> str:
        self._annotate = annotate
        return "".join(self.render_node(n) for n in nodes)

    def render_node(self, node: dict) -> str:
        t = node["type"]

        if t == NodeType.HEADING:
            prefix = "=" * node["level"]
            return f"{prefix} {node['text']}\n"

        if t == NodeType.PARAGRAPH:
            return f"{self._inline(node['text'])}\n\n"

        if t == NodeType.VOCAB_TABLE:
            rows_typst = ""
            if node.get("has_pinyin_example"):
                # 7-col: hanzi/pinyin/pos/meaning/ex_zh/ex_pinyin/ex_en (HSK 1/2)
                for hanzi, pinyin, pos, meaning, ex_zh, ex_pinyin, ex_en in node["rows"]:
                    rows_typst += (
                        f"  [{self._escape(hanzi)}], [{self._escape(pinyin)}], "
                        f"[{self._escape(pos)}], [{self._escape(meaning)}], "
                        f"[{self._escape(ex_zh)}], [{self._escape(ex_pinyin)}], "
                        f"[{self._escape(ex_en)}],\n"
                    )
                return f"#vocab-table-extended((\n{rows_typst}))\n\n"
            elif node.get("has_examples"):
                # 6-col: hanzi/pinyin/pos/meaning/ex_zh/ex_en (HSK 3-6, no pinyin col)
                for hanzi, pinyin, pos, meaning, ex_zh, _, ex_en in node["rows"]:
                    rows_typst += (
                        f"  [{self._escape(hanzi)}], [{self._escape(pinyin)}], "
                        f"[{self._escape(pos)}], [{self._escape(meaning)}], "
                        f"[{self._escape(ex_zh)}], [{self._escape(ex_en)}],\n"
                    )
                return f"#vocab-table-simple((\n{rows_typst}))\n\n"
            else:
                for hanzi, pinyin, pos, meaning, *_ in node["rows"]:
                    rows_typst += f"  [{self._escape(hanzi)}], [{self._escape(pinyin)}], [{self._escape(meaning)}],\n"
                return f"#vocab-table((\n{rows_typst}))\n\n"

        if t == NodeType.TABLE:
            headers = node["headers"]
            rows = node["rows"]
            col_count = len(headers)
            col_spec = ", ".join(["1fr"] * col_count)
            header_cells = ", ".join(f"[#strong[{self._escape(h)}]]" for h in headers)
            body_cells = ""
            for row in rows:
                body_cells += "  " + ", ".join(f"[{self._inline(c)}]" for c in row) + ",\n"
            return (
                f"#table(\n"
                f"  columns: ({col_spec}),\n"
                f"  table.header({header_cells}),\n"
                f"{body_cells}"
                f")\n\n"
            )

        if t == NodeType.LIST:
            prefix = "+" if node["ordered"] else "-"
            items = "\n".join(f"{prefix} {self._inline(item)}" for item in node["items"])
            return f"{items}\n\n"

        if t == NodeType.CODE_BLOCK:
            lang = node.get("lang", "")
            code = node["code"]
            return f"```{lang}\n{code}\n```\n\n"

        if t == NodeType.BLOCKQUOTE:
            return f"#quote[{self._inline(node['text'])}]\n\n"

        if t == NodeType.HR:
            return "#line(length: 100%)\n\n"

        return ""

    def _escape(self, text: str) -> str:
        """转义 Typst 特殊字符（在 content 块内）。"""
        text = text.replace("\\", "\\\\")
        text = text.replace("#", r"\#")
        text = text.replace("[", r"\[")
        text = text.replace("]", r"\]")
        # Curly/smart quotes are invalid in Typst code context — normalize to straight
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        return text

    def _annotate_and_escape(self, text: str) -> str:
        """汉字注音+非汉字转义（仅 annotate 模式）。"""
        if not self._annotate:
            return self._escape(text)
        CJK = re.compile(r"[\u4e00-\u9fff]+")
        result = []
        pos = 0
        for m in CJK.finditer(text):
            result.append(self._escape(text[pos:m.start()]))
            chars = m.group()
            pinyins = get_pinyin(chars, style=Style.TONE, heteronym=False)
            for char, py_list in zip(chars, pinyins):
                py = py_list[0]
                result.append(f"#py[{char}][{py}]")
            pos = m.end()
        result.append(self._escape(text[pos:]))
        return "".join(result)

    def _inline(self, text: str) -> str:
        bold_re = re.compile(r"\*\*(.+?)\*\*")
        italic_re = re.compile(r"\*([^*\n]+?)\*")
        result = []
        pos = 0
        for m in sorted(
            list(bold_re.finditer(text)) + list(italic_re.finditer(text)),
            key=lambda x: x.start()
        ):
            if m.start() < pos:
                continue
            result.append(self._annotate_and_escape(text[pos:m.start()]))
            inner = self._escape(m.group(1))
            if m.group(0).startswith("**"):
                result.append(f"#strong[{inner}]")
            else:
                result.append(f"#emph[{inner}]")
            pos = m.end()
        result.append(self._annotate_and_escape(text[pos:]))
        return "".join(result)
