def chunk_document(text: str, max_tokens: int = 2_000):
    # collapse runs of whitespace so tokenisation is repeatable
    import re
    text = re.sub(r'\s+', ' ', text).strip()

    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunks.append(" ".join(words[start:end]))
        start = end
    return chunks
