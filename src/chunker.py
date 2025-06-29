import os, re
from dotenv import load_dotenv

load_dotenv()  # for local .env; Streamlit will use st.secrets

def chunk_document(text: str, max_tokens: int = 2_000):
    import re
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunks.append(" ".join(words[start:end]))
        start = end
    return chunks
