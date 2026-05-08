#!/usr/bin/env python3
"""
Z Turns Chinese AutoBuilder - Content Extractor
================================================

Extracts and analyzes teaching content from multiple sources:
- Web pages (URL)
- PDF files
- Text/Markdown/DOCX files
- Audio transcripts (GetNotes recordings)

Produces structured teaching material for the lesson generator.

Usage:
    python3 content_extractor.py                    # Run demo
    python3 content_extractor.py --url URL          # Extract from URL
    python3 content_extractor.py --file PATH        # Extract from file
    python3 content_extractor.py --text "TEXT"      # Analyze text directly
"""

import re
import os
import sys
import json
import subprocess
import unicodedata
from html.parser import HTMLParser
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional: jieba for Chinese word segmentation
# ---------------------------------------------------------------------------
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CJK_RANGES = [
    (0x4E00, 0x9FFF),    # CJK Unified Ideographs
    (0x3400, 0x4DBF),    # CJK Unified Ideographs Extension A
    (0x20000, 0x2A6DF),  # CJK Unified Ideographs Extension B
    (0xF900, 0xFAFF),    # CJK Compatibility Ideographs
    (0x2F800, 0x2FA1F),  # CJK Compatibility Ideographs Supplement
]

FILLER_WORDS_ZH = [
    "嗯", "啊", "呃", "那个", "就是说", "然后", "对对对",
    "是的是的", "哦", "额", "这个这个",
]

FILLER_WORDS_EN = [
    "um", "uh", "like", "you know", "so", "well", "I mean",
    "basically", "actually", "right",
]

TIMESTAMP_PATTERN = re.compile(
    r'\[?\d{1,2}:\d{2}(?::\d{2})?\]?'       # [00:12] or 1:23:45
    r'|\(\d{1,2}:\d{2}(?::\d{2})?\)'         # (00:12)
    r'|\d{1,2}:\d{2}(?::\d{2})?(?=\s)',      # bare 00:12 followed by space
)

SPEAKER_PATTERN = re.compile(
    r'^(?:Speaker\s*\d+|老师|学生|Teacher|Student|T|S|A|B)'
    r'\s*[:：]\s*',
    re.IGNORECASE | re.MULTILINE,
)

# Common grammar markers to detect in Chinese text
GRAMMAR_PATTERNS = {
    "SVO word order": re.compile(r'[\u4e00-\u9fff]+[是有在想要能会][\u4e00-\u9fff]+'),
    "的 (possession/description)": re.compile(r'[\u4e00-\u9fff]+的[\u4e00-\u9fff]+'),
    "了 (completed action)": re.compile(r'[\u4e00-\u9fff]+了(?:[\u4e00-\u9fff]|$)'),
    "Question word 吗": re.compile(r'[\u4e00-\u9fff]+吗[？?]?'),
    "Question word 什么": re.compile(r'什么'),
    "Question word 怎么": re.compile(r'怎么'),
    "比 comparison": re.compile(r'[\u4e00-\u9fff]+比[\u4e00-\u9fff]+'),
    "把 construction": re.compile(r'把[\u4e00-\u9fff]+'),
    "被 passive": re.compile(r'被[\u4e00-\u9fff]+'),
    "在 + location": re.compile(r'在[\u4e00-\u9fff]{1,6}(?:里|上|下|旁边|对面|前面|后面)'),
    "想/要 + Verb": re.compile(r'[想要][\u4e00-\u9fff]'),
    "能/可以 (ability/permission)": re.compile(r'(?:能|可以)[\u4e00-\u9fff]'),
    "Number + 个/measure word": re.compile(r'[一二三四五六七八九十百千万\d]+[个只本件条双块杯碗瓶]'),
    "也/都 adverbs": re.compile(r'(?:也|都)[\u4e00-\u9fff]'),
    "Time expressions": re.compile(r'[今明昨][天年]|[上下]午|[早晚]上|星期[一二三四五六日天]|[一二三四五六七八九十]+[点月号日]'),
}


# ============================================================
# HTML Stripping
# ============================================================
class _HTMLTextExtractor(HTMLParser):
    """Strip HTML tags, keep text content."""

    SKIP_TAGS = {"script", "style", "noscript", "iframe", "svg", "head"}

    def __init__(self):
        super().__init__()
        self._pieces = []
        self._skip_depth = 0
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag in ("p", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr"):
            self._pieces.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._skip_depth == 0:
            self._pieces.append(data)

    def get_text(self):
        return "".join(self._pieces)


def _strip_html(html_str):
    """Remove HTML tags, return (title, plain_text)."""
    parser = _HTMLTextExtractor()
    try:
        parser.feed(html_str)
    except Exception:
        # Fallback: regex-based stripping
        text = re.sub(r'<script[^>]*>.*?</script>', '', html_str, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        return "", text
    return parser.title.strip(), parser.get_text()


# ============================================================
# Helper: CJK detection
# ============================================================
def is_cjk_char(ch):
    """Check if a character is a CJK ideograph."""
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in CJK_RANGES)


def extract_chinese_text(text):
    """Extract contiguous runs of Chinese characters (with common punctuation)."""
    # Match Chinese chars plus Chinese punctuation and common connecting chars
    pattern = re.compile(
        r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff'
        r'\u3000-\u303f\uff00-\uffef'
        r'\u2000-\u206f，。！？、；：""''（）【】《》]+'
    )
    return pattern.findall(text)


def _detect_encoding(raw_bytes):
    """Best-effort encoding detection for raw bytes."""
    # Check BOM
    if raw_bytes[:3] == b'\xef\xbb\xbf':
        return 'utf-8-sig'
    if raw_bytes[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return 'utf-16'

    # Try common Chinese encodings in order
    for enc in ('utf-8', 'gb18030', 'gb2312', 'gbk', 'big5', 'latin-1'):
        try:
            raw_bytes.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return 'utf-8'  # last resort


# ============================================================
# 1. URL Content Extraction
# ============================================================
def extract_from_url(url, timeout=15):
    """
    Fetch a web page and extract text content.

    Returns:
        dict with keys: title, text, chinese_text, url, success, error
    """
    result = {
        "title": "",
        "text": "",
        "chinese_text": [],
        "url": url,
        "success": False,
        "error": None,
    }

    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            result["error"] = f"Unsupported URL scheme: {parsed.scheme}"
            return result

        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })

        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()

            # Detect encoding from headers or content
            content_type = resp.headers.get("Content-Type", "")
            encoding = None
            if "charset=" in content_type:
                encoding = content_type.split("charset=")[-1].strip().split(";")[0]

            # Try meta tag in HTML for encoding
            if not encoding:
                head_bytes = raw[:4096]
                meta_match = re.search(
                    rb'<meta[^>]+charset=["\']?([a-zA-Z0-9_-]+)',
                    head_bytes, re.IGNORECASE,
                )
                if meta_match:
                    encoding = meta_match.group(1).decode("ascii", errors="ignore")

            if not encoding:
                encoding = _detect_encoding(raw)

            try:
                html_str = raw.decode(encoding, errors="replace")
            except (UnicodeDecodeError, LookupError):
                html_str = raw.decode("utf-8", errors="replace")

            title, text = _strip_html(html_str)

            # Clean up whitespace
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r'[ \t]+', ' ', text)
            text = text.strip()

            result["title"] = title
            result["text"] = text
            result["chinese_text"] = extract_chinese_text(text)
            result["success"] = True

    except HTTPError as e:
        result["error"] = f"HTTP {e.code}: {e.reason}"
    except URLError as e:
        result["error"] = f"URL error: {e.reason}"
    except Exception as e:
        result["error"] = f"Unexpected error: {type(e).__name__}: {e}"

    return result


# ============================================================
# 2. PDF Content Extraction
# ============================================================
def extract_from_pdf(file_path):
    """
    Extract text from a PDF file.

    Strategy:
        1. Try PyPDF2
        2. Try pdfplumber
        3. Fallback: macOS textutil
        4. Fallback: macOS mdls for metadata

    Returns:
        dict with keys: text, chinese_text, metadata, file_path, success, error
    """
    file_path = os.path.abspath(file_path)
    result = {
        "text": "",
        "chinese_text": [],
        "metadata": {},
        "file_path": file_path,
        "success": False,
        "error": None,
    }

    if not os.path.isfile(file_path):
        result["error"] = f"File not found: {file_path}"
        return result

    # --- Strategy 1: PyPDF2 ---
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        pages_text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text)
        if pages_text:
            result["text"] = "\n\n".join(pages_text)
            result["metadata"] = dict(reader.metadata) if reader.metadata else {}
            result["chinese_text"] = extract_chinese_text(result["text"])
            result["success"] = True
            return result
    except ImportError:
        pass
    except Exception:
        pass  # Fall through to next strategy

    # --- Strategy 2: pdfplumber ---
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            pages_text = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            if pages_text:
                result["text"] = "\n\n".join(pages_text)
                result["metadata"] = pdf.metadata or {}
                result["chinese_text"] = extract_chinese_text(result["text"])
                result["success"] = True
                return result
    except ImportError:
        pass
    except Exception:
        pass

    # --- Strategy 3: macOS textutil ---
    if sys.platform == "darwin":
        try:
            tmp_txt = file_path + ".extracted.txt"
            proc = subprocess.run(
                ["textutil", "-convert", "txt", "-output", tmp_txt, file_path],
                capture_output=True, text=True, timeout=30,
            )
            if proc.returncode == 0 and os.path.isfile(tmp_txt):
                with open(tmp_txt, "r", encoding="utf-8", errors="replace") as f:
                    result["text"] = f.read().strip()
                os.remove(tmp_txt)
                result["chinese_text"] = extract_chinese_text(result["text"])
                result["success"] = True
                return result
        except Exception:
            pass

    # --- Strategy 4: macOS mdls for metadata ---
    if sys.platform == "darwin":
        try:
            proc = subprocess.run(
                ["mdls", file_path],
                capture_output=True, text=True, timeout=10,
            )
            if proc.returncode == 0:
                result["metadata"]["mdls"] = proc.stdout
                # Not full text, but at least we have metadata
                result["error"] = "Could not extract text; metadata only (install PyPDF2: pip install PyPDF2)"
                return result
        except Exception:
            pass

    result["error"] = "No PDF extraction method available. Install PyPDF2: pip install PyPDF2"
    return result


# ============================================================
# 3. Text File Extraction
# ============================================================
def extract_from_file(file_path):
    """
    Extract text from .txt, .md, or .docx files.

    For .docx on macOS, uses textutil to convert to plain text.

    Returns:
        dict with keys: text, chinese_text, file_path, success, error
    """
    file_path = os.path.abspath(file_path)
    result = {
        "text": "",
        "chinese_text": [],
        "file_path": file_path,
        "success": False,
        "error": None,
    }

    if not os.path.isfile(file_path):
        result["error"] = f"File not found: {file_path}"
        return result

    ext = Path(file_path).suffix.lower()

    # --- .docx via textutil (macOS) ---
    if ext == ".docx":
        if sys.platform == "darwin":
            try:
                tmp_txt = file_path + ".extracted.txt"
                proc = subprocess.run(
                    ["textutil", "-convert", "txt", "-output", tmp_txt, file_path],
                    capture_output=True, text=True, timeout=30,
                )
                if proc.returncode == 0 and os.path.isfile(tmp_txt):
                    with open(tmp_txt, "r", encoding="utf-8", errors="replace") as f:
                        result["text"] = f.read().strip()
                    os.remove(tmp_txt)
                    result["chinese_text"] = extract_chinese_text(result["text"])
                    result["success"] = True
                    return result
                else:
                    result["error"] = f"textutil failed: {proc.stderr}"
                    return result
            except Exception as e:
                result["error"] = f"textutil error: {e}"
                return result
        else:
            result["error"] = "DOCX extraction requires macOS textutil or python-docx"
            return result

    # --- Plain text files (.txt, .md, etc.) ---
    try:
        with open(file_path, "rb") as f:
            raw = f.read()

        encoding = _detect_encoding(raw)
        text = raw.decode(encoding, errors="replace")
        result["text"] = text.strip()
        result["chinese_text"] = extract_chinese_text(result["text"])
        result["success"] = True
    except Exception as e:
        result["error"] = f"Read error: {e}"

    return result


# ============================================================
# 4. Audio Transcript Processing
# ============================================================
def process_transcript(text):
    """
    Clean up raw audio transcripts (e.g. from GetNotes recordings).

    - Remove timestamps
    - Remove filler words
    - Identify speaker turns (teacher vs student)
    - Extract dialogue segments

    Returns:
        dict with keys: cleaned_text, speakers, dialogues, raw_segments
    """
    result = {
        "cleaned_text": "",
        "speakers": [],
        "dialogues": [],
        "raw_segments": [],
    }

    if not text or not text.strip():
        return result

    lines = text.strip().split("\n")
    cleaned_lines = []
    current_speaker = None
    dialogues = []
    speakers_seen = set()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Remove timestamps
        line = TIMESTAMP_PATTERN.sub("", line).strip()
        if not line:
            continue

        # Detect speaker
        speaker_match = SPEAKER_PATTERN.match(line)
        if speaker_match:
            speaker_label = speaker_match.group(0).rstrip(":： ")
            # Normalize speaker labels
            if any(k in speaker_label.lower() for k in ("teacher", "老师", "t")):
                current_speaker = "Teacher"
            elif any(k in speaker_label.lower() for k in ("student", "学生", "s")):
                current_speaker = "Student"
            else:
                current_speaker = speaker_label
            speakers_seen.add(current_speaker)
            line = line[speaker_match.end():].strip()

        if not line:
            continue

        # Remove filler words (whole-word matching for English)
        for filler in FILLER_WORDS_EN:
            line = re.sub(
                r'\b' + re.escape(filler) + r'\b',
                '', line, flags=re.IGNORECASE,
            )
        # Remove Chinese filler words
        for filler in FILLER_WORDS_ZH:
            line = line.replace(filler, "")

        # Collapse extra spaces
        line = re.sub(r'\s{2,}', ' ', line).strip()
        if not line:
            continue

        result["raw_segments"].append({
            "speaker": current_speaker,
            "text": line,
        })

        cleaned_lines.append(line)

        # Build dialogue pairs
        if current_speaker:
            dialogues.append({
                "speaker": current_speaker,
                "text": line,
            })

    result["cleaned_text"] = "\n".join(cleaned_lines)
    result["speakers"] = sorted(speakers_seen)

    # Pair up dialogues as (teacher, student) exchanges
    paired = []
    i = 0
    while i < len(dialogues) - 1:
        a = dialogues[i]
        b = dialogues[i + 1]
        if a["speaker"] != b["speaker"]:
            paired.append({"A": a, "B": b})
            i += 2
        else:
            i += 1
    result["dialogues"] = paired

    return result


# ============================================================
# 5. Teaching Content Analyzer
# ============================================================
def analyze_content(text):
    """
    Analyze text for Chinese teaching content.

    - Identify Chinese vocabulary (CJK characters)
    - Segment words with jieba (if available)
    - Extract potential dialogue pairs
    - Identify grammar patterns
    - Detect topic/theme keywords

    Returns:
        dict: {chinese_text, vocabulary, dialogues, grammar_hints, topics, raw_segments}
    """
    result = {
        "chinese_text": [],
        "vocabulary": [],
        "dialogues": [],
        "grammar_hints": [],
        "topics": [],
        "raw_segments": [],
    }

    if not text or not text.strip():
        return result

    # --- Extract Chinese text runs ---
    chinese_runs = extract_chinese_text(text)
    result["chinese_text"] = chinese_runs

    # --- Vocabulary extraction via jieba ---
    all_chinese = "".join(chinese_runs)
    if JIEBA_AVAILABLE and all_chinese:
        words = list(jieba.cut(all_chinese))
        # Filter: keep words with at least one CJK char, length >= 1
        vocab_counts = {}
        for w in words:
            w = w.strip()
            if w and any(is_cjk_char(c) for c in w) and len(w) >= 1:
                vocab_counts[w] = vocab_counts.get(w, 0) + 1
        # Sort by frequency descending
        result["vocabulary"] = sorted(
            vocab_counts.items(), key=lambda x: (-x[1], x[0])
        )
    elif all_chinese:
        # Fallback: extract individual characters
        char_counts = {}
        for ch in all_chinese:
            if is_cjk_char(ch):
                char_counts[ch] = char_counts.get(ch, 0) + 1
        result["vocabulary"] = sorted(
            char_counts.items(), key=lambda x: (-x[1], x[0])
        )

    # --- Dialogue detection ---
    # Look for lines with quotation marks or speaker patterns
    lines = text.strip().split("\n")
    dialogue_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Chinese dialogue markers
        if re.search(r'[""「」『』]', line):
            dialogue_lines.append(line)
        # A:/B: or 老师:/学生: patterns
        elif SPEAKER_PATTERN.match(line):
            dialogue_lines.append(line)
        # Colon-based dialogue
        elif re.match(r'^[\u4e00-\u9fff]{1,4}[:：]', line):
            dialogue_lines.append(line)

    result["dialogues"] = dialogue_lines

    # --- Grammar pattern detection ---
    detected_grammar = []
    for name, pattern in GRAMMAR_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            detected_grammar.append({
                "pattern": name,
                "examples": matches[:5],  # Up to 5 examples
                "count": len(matches),
            })
    # Sort by count descending
    detected_grammar.sort(key=lambda x: -x["count"])
    result["grammar_hints"] = detected_grammar

    # --- Topic detection ---
    topic_keywords = {
        "greetings": ["你好", "您好", "早上好", "晚上好", "再见", "hello", "hi"],
        "introductions": ["名字", "叫", "姓", "认识", "自我介绍"],
        "family": ["家", "爸爸", "妈妈", "哥哥", "姐姐", "弟弟", "妹妹", "家人", "孩子"],
        "numbers": ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "多少", "几"],
        "time": ["点", "分", "小时", "今天", "明天", "昨天", "星期", "时间", "早", "晚"],
        "food": ["吃", "喝", "餐", "饭", "菜", "水", "茶", "咖啡", "饿", "渴"],
        "shopping": ["买", "卖", "钱", "块", "元", "贵", "便宜", "超市", "商店"],
        "weather": ["天气", "冷", "热", "下雨", "晴", "阴", "风", "雪", "温度"],
        "travel": ["去", "来", "飞机", "火车", "机场", "酒店", "旅游", "地铁"],
        "work": ["工作", "公司", "上班", "下班", "老板", "同事", "会议", "办公室"],
        "hobbies": ["喜欢", "爱好", "运动", "音乐", "电影", "书", "游戏", "跑步"],
        "directions": ["在哪", "左", "右", "前面", "后面", "旁边", "对面", "东", "西", "南", "北"],
        "health": ["医院", "医生", "病", "药", "疼", "感冒", "健康", "身体"],
        "phone": ["电话", "打电话", "手机", "号码", "微信"],
    }

    text_lower = text.lower()
    detected_topics = []
    for topic, keywords in topic_keywords.items():
        matches = sum(1 for kw in keywords if kw in text_lower)
        if matches >= 2:  # At least 2 keyword hits
            detected_topics.append((topic, matches))

    detected_topics.sort(key=lambda x: -x[1])
    result["topics"] = [t[0] for t in detected_topics]

    # --- Raw segments (line-based) ---
    result["raw_segments"] = [
        line.strip() for line in lines if line.strip()
    ]

    return result


# ============================================================
# 6. Multi-Source Aggregator
# ============================================================
def aggregate_sources(sources):
    """
    Process multiple content sources and merge results.

    Args:
        sources: list of dicts, each with:
            - type: "url" | "pdf" | "file" | "text" | "getnotes"
            - content: str (URL, file path, or raw text)

    Returns:
        dict with merged teaching material:
            {
                all_text, chinese_text, vocabulary, dialogues,
                grammar_hints, topics, source_results, errors
            }
    """
    merged = {
        "all_text": [],
        "chinese_text": [],
        "vocabulary": {},
        "dialogues": [],
        "grammar_hints": [],
        "topics": [],
        "source_results": [],
        "errors": [],
    }

    for src in sources:
        src_type = src.get("type", "text")
        content = src.get("content", "")

        extracted_text = ""
        error = None

        try:
            if src_type == "url":
                r = extract_from_url(content)
                extracted_text = r.get("text", "")
                if not r["success"]:
                    error = r["error"]

            elif src_type == "pdf":
                r = extract_from_pdf(content)
                extracted_text = r.get("text", "")
                if not r["success"]:
                    error = r["error"]

            elif src_type == "file":
                r = extract_from_file(content)
                extracted_text = r.get("text", "")
                if not r["success"]:
                    error = r["error"]

            elif src_type == "getnotes":
                transcript = process_transcript(content)
                extracted_text = transcript.get("cleaned_text", "")
                merged["dialogues"].extend(
                    [d for d in transcript.get("dialogues", [])]
                )

            elif src_type == "text":
                extracted_text = content

            else:
                error = f"Unknown source type: {src_type}"

        except Exception as e:
            error = f"Error processing {src_type}: {type(e).__name__}: {e}"

        if error:
            merged["errors"].append({"source": src, "error": error})

        if extracted_text:
            merged["all_text"].append(extracted_text)
            merged["source_results"].append({
                "type": src_type,
                "content_preview": content[:100] if isinstance(content, str) else str(content)[:100],
                "text_length": len(extracted_text),
            })

    # Analyze all collected text
    combined_text = "\n\n".join(merged["all_text"])
    if combined_text:
        analysis = analyze_content(combined_text)

        # Merge chinese_text (deduplicate)
        seen = set()
        for chunk in analysis["chinese_text"]:
            if chunk not in seen:
                merged["chinese_text"].append(chunk)
                seen.add(chunk)

        # Merge vocabulary (sum counts)
        for word, count in analysis["vocabulary"]:
            merged["vocabulary"][word] = merged["vocabulary"].get(word, 0) + count

        # Sort vocabulary by frequency
        merged["vocabulary"] = sorted(
            merged["vocabulary"].items(), key=lambda x: (-x[1], x[0])
        )

        # Merge dialogues
        merged["dialogues"].extend(analysis["dialogues"])

        # Merge grammar hints (deduplicate by pattern name)
        seen_patterns = {g["pattern"] for g in merged["grammar_hints"]}
        for g in analysis["grammar_hints"]:
            if g["pattern"] not in seen_patterns:
                merged["grammar_hints"].append(g)
                seen_patterns.add(g["pattern"])

        # Merge topics (deduplicate, keep order)
        seen_topics = set(merged["topics"])
        for t in analysis["topics"]:
            if t not in seen_topics:
                merged["topics"].append(t)
                seen_topics.add(t)

    # Convert all_text to single string
    merged["all_text"] = combined_text

    return merged


# ============================================================
# Demo / CLI
# ============================================================
def demo():
    """Run a demonstration of all extractor capabilities."""
    print("=" * 60)
    print("Z Turns Chinese - Content Extractor Demo")
    print("=" * 60)

    # --- Demo 1: Analyze Chinese text ---
    sample_text = """
    老师：同学们，今天我们学习第八课——在餐厅。
    学生：老师好！
    老师：你好！你想吃什么？
    学生：我想吃米饭和鸡肉。
    老师：好的。你想喝什么？
    学生：我想喝茶，谢谢。
    老师：一碗米饭，一个鸡肉，一杯茶。一共三十五块。
    学生：好的，给你钱。
    老师：谢谢！慢慢吃！
    学生：谢谢老师！
    """

    print("\n--- 1. Content Analysis Demo ---")
    analysis = analyze_content(sample_text)

    print(f"  Chinese text fragments: {len(analysis['chinese_text'])}")
    print(f"  Vocabulary items: {len(analysis['vocabulary'])}")
    if analysis['vocabulary']:
        top5 = analysis['vocabulary'][:5]
        print(f"  Top 5 words: {', '.join(f'{w}({c})' for w, c in top5)}")

    print(f"  Detected topics: {', '.join(analysis['topics']) or 'none'}")
    print(f"  Grammar patterns found: {len(analysis['grammar_hints'])}")
    for g in analysis['grammar_hints'][:3]:
        print(f"    - {g['pattern']}: {g['count']} occurrences")
        if g['examples']:
            print(f"      e.g. {g['examples'][0]}")
    print(f"  Dialogue lines: {len(analysis['dialogues'])}")

    # --- Demo 2: Transcript processing ---
    print("\n--- 2. Transcript Processing Demo ---")
    raw_transcript = """
    [00:01] Teacher: 好，我们开始吧。嗯，今天学习点菜。
    [00:15] Student: 嗯，好的老师。
    [00:20] Teacher: 你想吃什么？What do you want to eat?
    [00:30] Student: 呃，我想吃……那个……米饭。
    [00:40] Teacher: 很好！"我想吃米饭" - I want to eat rice.
    [00:50] Student: 我想吃米饭。
    [01:00] Teacher: 你想喝什么？
    [01:05] Student: 那个，我想喝茶。
    """

    transcript = process_transcript(raw_transcript)
    print(f"  Speakers found: {', '.join(transcript['speakers'])}")
    print(f"  Cleaned segments: {len(transcript['raw_segments'])}")
    print(f"  Dialogue pairs: {len(transcript['dialogues'])}")
    if transcript['dialogues']:
        pair = transcript['dialogues'][0]
        print(f"    First pair:")
        print(f"      {pair['A']['speaker']}: {pair['A']['text']}")
        print(f"      {pair['B']['speaker']}: {pair['B']['text']}")

    # --- Demo 3: Multi-source aggregation ---
    print("\n--- 3. Multi-Source Aggregation Demo ---")
    sources = [
        {"type": "text", "content": sample_text},
        {"type": "getnotes", "content": raw_transcript},
    ]
    merged = aggregate_sources(sources)
    print(f"  Total text length: {len(merged['all_text'])} chars")
    print(f"  Unique Chinese fragments: {len(merged['chinese_text'])}")
    print(f"  Total vocabulary: {len(merged['vocabulary'])} items")
    print(f"  Total dialogues: {len(merged['dialogues'])}")
    print(f"  Topics: {', '.join(merged['topics']) or 'none'}")
    print(f"  Errors: {len(merged['errors'])}")

    print(f"\n  jieba available: {JIEBA_AVAILABLE}")
    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


# ── Convenience class wrapper for main.py compatibility ──


class ContentExtractor:
    """OOP wrapper around the module-level functions."""

    @staticmethod
    def extract_from_url(url):
        return extract_from_url(url)

    @staticmethod
    def extract_from_pdf(file_path):
        return extract_from_pdf(file_path)

    @staticmethod
    def extract_from_file(file_path):
        return extract_from_file(file_path)

    @staticmethod
    def process_transcript(text):
        return process_transcript(text)

    @staticmethod
    def analyze_content(text):
        return analyze_content(text)

    @staticmethod
    def aggregate_sources(sources):
        return aggregate_sources(sources)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Z Turns Chinese - Content Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--url", help="Extract content from URL")
    parser.add_argument("--file", help="Extract content from file")
    parser.add_argument("--text", help="Analyze text directly")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.url:
        result = extract_from_url(args.url)
        analysis = analyze_content(result["text"]) if result["success"] else {}
        if args.json:
            print(json.dumps({"extraction": result, "analysis": analysis}, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"Title: {result['title']}")
            print(f"Success: {result['success']}")
            if result['error']:
                print(f"Error: {result['error']}")
            print(f"Text length: {len(result['text'])} chars")
            print(f"Chinese fragments: {len(result['chinese_text'])}")

    elif args.file:
        ext = Path(args.file).suffix.lower()
        if ext == ".pdf":
            result = extract_from_file(args.file) if ext != ".pdf" else extract_from_pdf(args.file)
        else:
            result = extract_from_file(args.file)
        analysis = analyze_content(result["text"]) if result["success"] else {}
        if args.json:
            print(json.dumps({"extraction": result, "analysis": analysis}, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"Success: {result['success']}")
            if result.get('error'):
                print(f"Error: {result['error']}")
            print(f"Text length: {len(result['text'])} chars")

    elif args.text:
        analysis = analyze_content(args.text)
        if args.json:
            print(json.dumps(analysis, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"Vocabulary: {len(analysis['vocabulary'])} items")
            print(f"Topics: {', '.join(analysis['topics'])}")
            print(f"Grammar: {len(analysis['grammar_hints'])} patterns")

    else:
        demo()


if __name__ == "__main__":
    main()
