import os, re

def chunk_document(text: str, max_tokens: int = None, overlap: int = None):
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()

    # read defaults from env if not passed in
    if max_tokens is None:
        max_tokens = int(os.getenv("CHUNK_SIZE", "2000"))
    if overlap is None:
        overlap = int(os.getenv("CHUNK_OVERLAP", "200"))

    chunks, start = [], 0
    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunks.append(" ".join(words[start:end]))
        start = max(end - overlap, end)
    return chunks
