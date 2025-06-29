import os, re

def chunk_document(text: str):
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()

    # allow you to tune from secrets/env
    max_tokens  = int(os.getenv("CHUNK_SIZE",    "2000"))
    overlap     = int(os.getenv("CHUNK_OVERLAP", "200"))

    chunks, start = [], 0
    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunks.append(" ".join(words[start:end]))
        # back up by `overlap` so the next chunk re-includes the last few words
        start = max(end - overlap, end)
    return chunks
