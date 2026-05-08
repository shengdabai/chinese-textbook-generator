"""
Content Source Interface Example

This module shows how to plug in your own teaching content source
to replace the proprietary GetNote API calls used in the original pipeline.

Replace this with:
- CSV files with vocabulary/dialogue data
- Text files with teaching notes
- Any other structured content source

Usage: Import and use load_content_snippets() in generate_books_enhanced.py
"""
import csv
from pathlib import Path


def load_content_snippets(source_file: str, keywords: list, max_chars: int = 1200) -> str:
    """
    Load teaching content from a CSV or text file filtered by keywords.
    
    Args:
        source_file: Path to your content file (CSV, TXT, etc.)
        keywords: List of keywords to filter relevant content
        max_chars: Maximum characters to return
    
    Returns:
        Filtered content string to inject into the textbook
    """
    path = Path(source_file)
    if not path.exists():
        return ""
    
    matched = []
    total = 0
    
    if path.suffix == ".csv":
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                content = row.get("content", "") or row.get("text", "") or str(row)
                if any(kw.lower() in content.lower() for kw in keywords):
                    if total + len(content) <= max_chars:
                        matched.append(content)
                        total += len(content)
    else:
        # Plain text file
        with open(path, encoding="utf-8") as f:
            paragraphs = [p.strip() for p in f.read().split("\n\n") if p.strip()]
        for p in paragraphs:
            if any(kw.lower() in p.lower() for kw in keywords):
                if total + len(p) <= max_chars:
                    matched.append(p)
                    total += len(p)
    
    return "\n\n".join(matched[:4])


# Example content mapping (replace BOOK_NOTE_MAP in generate_books_enhanced.py)
BOOK_CONTENT_MAP = {
    51: {
        "source_file": "content/job_hunting.csv",   # Your content file
        "keywords": ["职场", "面试", "求职", "简历", "工作", "薪资"],
    },
    52: {
        "source_file": "content/startup.csv",
        "keywords": ["创业", "商业", "企业", "投资", "公司", "AI"],
    },
    # Add more books as needed...
}
