"""Gerencia a persistencia local dos vetores no ChromaDB.

A colecao "fitlife" guarda os 32 chunks da base de conhecimento.
Os embeddings sao gerados localmente por rag.embedder e passados de forma
explicita, entao a colecao nao depende de nenhum servico de embedding externo.
"""

import chromadb
from pathlib import Path

CAMINHO_DB = Path(__file__).resolve().parent.parent / "chroma_db"

cliente = chromadb.PersistentClient(path=str(CAMINHO_DB))

colecao = cliente.get_or_create_collection(
    name="fitlife",
    metadata={"hnsw:space": "cosine"},
)
