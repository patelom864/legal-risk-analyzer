# src/extract_text.py
from pathlib import Path
from pypdf import PdfReader
from docx import Document

# ── add near the top of the file ────────────────────────────────
import re
from ftfy import fix_text

# map mojibake → correct Unicode
_MOJI_MAP = {
    "â€™": "’",   # right single quote
    "â€˜": "‘",   # left single quote
    "â€œ": "“",   # left double quote
    "â€�": "”",   # right double quote
    "â€“": "–",   # en-dash
    "â€”": "—",   # em-dash
}

_MOJI_RE = re.compile("|".join(map(re.escape, _MOJI_MAP)))

def _clean_mojibake(s: str) -> str:
    """Replace known mojibake patterns, then run ftfy for good measure."""
    s = _MOJI_RE.sub(lambda m: _MOJI_MAP[m.group(0)], s)
    return fix_text(s)


def extract_text(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(uploaded_file)
        raw = "\n".join(page.extract_text() or "" for page in reader.pages)

    elif suffix in {".docx", ".doc"}:
        doc = Document(uploaded_file)
        raw = "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError("Unsupported file type")
    # 1️⃣ force-round-trip through Latin-1 to expose hidden mojibake bytes
    raw = raw.encode("latin1", "ignore").decode("utf8", "ignore")

    # 2️⃣ let ftfy clean any remaining glitches
    return _clean_mojibake(raw)


