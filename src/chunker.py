import os, re
from dotenv import load_dotenv

load_dotenv()  # if you’re using a .env locally; Streamlit Cloud will pick up st.secrets

def chunk_document(text: str, max_tokens: int = None, overlap: int = None) -> list[str]:
    # Defaults from env (or fall back to hard-coded)
    if max_tokens is None:
        max_tokens = int(os.getenv("CHUNK_SIZE", "2000"))
    if overlap is None:
        overlap = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Normalize whitespace & split
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunks.append(" ".join(words[start:end]))
        # move forward, but keep an overlap window
        start = end - overlap if end - overlap > start else end
    return chunks
