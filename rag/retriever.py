"""Recupera os melhores chunks para uma pergunta (busca vetorial Top-K).

O vetor da pergunta e comparado, por similaridade de cosseno, contra os
embeddings dos 35 chunks armazenados no ChromaDB.
"""

from rag.embedder import gerar_embedding
from rag.chroma_manager import colecao


def buscar(pergunta: str, top_k: int = 3):
    """Retorna os Top-K chunks mais similares a pergunta."""
    vetor = gerar_embedding(pergunta)
    resultado = colecao.query(
        query_embeddings=[vetor],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    return resultado
