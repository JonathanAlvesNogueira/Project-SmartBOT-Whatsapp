"""Embedder neural local (offline, sem API).

Usa sentence-transformers com um modelo multilíngue que cobre o português.
O modelo e baixado uma unica vez e fica em cache local; depois disso,
funciona 100% offline (sem custo e sem depender de API externa).
"""

from sentence_transformers import SentenceTransformer

MODELO = "paraphrase-multilingual-MiniLM-L12-v2"
_modelo = SentenceTransformer(MODELO)

def gerar_embedding(texto: str):
    """Gera o vetor de um texto. Retorna uma lista de floats (384 dimensoes)."""
    return _modelo.encode(texto).tolist()


def gerar_embeddings(textos: list[str]):
    """Gera os vetores de uma lista de textos."""
    return _modelo.encode(textos).tolist()
