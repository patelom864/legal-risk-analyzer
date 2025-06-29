# src/rag_index.py
from pathlib import Path
import faiss, numpy as np
from ibm_watsonx_ai import Credentials, APIClient
import os, uuid
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

creds = Credentials(
    api_key=os.getenv("WX_API_KEY"),
    url="https://us-south.ml.cloud.ibm.com"
)
client = APIClient(credentials=creds,
                   project_id=os.getenv("WX_PROJECT_ID"))

EMBED_MODEL = "ibm/granite-embedding-107m-multilingual"

class RAGIndex:
    def __init__(self, dim:int=1024):
        self.index = faiss.IndexFlatIP(dim)
        self.chunks = []

    def add(self, text:str):
        vec = self._embed(text)
        self.index.add(vec)           # (1, dim)
        self.chunks.append(text)

    def query(self, text:str, top_k:int=3):
        vec = self._embed(text)
        _, idx = self.index.search(vec, top_k)
        return [self.chunks[i] for i in idx[0] if i < len(self.chunks)]

    def _embed(self, text:str):
        resp = client.embeddings.create(
            model_id=EMBED_MODEL,
            input=[text]
        )
        return np.array(resp["data"][0]["embedding"], dtype="float32").reshape(1, -1)
