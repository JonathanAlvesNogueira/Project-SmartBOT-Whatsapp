"""Indexacao da base de conhecimento FitLife no ChromaDB.

Le o ``data/fitlife_knowledge.json``, gera os vetores com o embedder neural
local (sentence-transformers) e alimenta a colecao "fitlife".

Uso (da raiz do projeto):
    python -m rag.indexer
"""

from pathlib import Path

from rag.loader import carregar_base
from rag.embedder import gerar_embeddings
from rag.chroma_manager import colecao


PASTA_PROJETO = Path(__file__).resolve().parent.parent

def montar_texto_para_busca(chunk: dict) -> str:
    """Combina campos que ajudam a busca a achar o chunk (titulo, categoria, tags, conteudo).

    Indexar apenas o conteudo perde palavras-chave importantes (ex.: "funcional" e uma
    tag, nao aparece no corpo do texto). Combinar os campos melhora a recuperacao.
    """
    tags = " ".join(chunk.get("tags", [])) if isinstance(chunk.get("tags"), list) else str(chunk.get("tags", ""))
    return " ".join(
        [
            chunk.get("titulo", ""),
            chunk.get("categoria", ""),
            tags,
            chunk.get("conteudo", ""),
        ]
    )


def _metadados_do_chunk(chunk: dict) -> dict:
    """Transforma um chunk em metadados aceitos pelo ChromaDB (apenas escalares)."""
    tags = ", ".join(chunk.get("tags", [])) if isinstance(chunk.get("tags"), list) else str(chunk.get("tags", ""))
    relacionamentos = ", ".join(chunk.get("relacionamentos", [])) if isinstance(chunk.get("relacionamentos"), list) else str(chunk.get("relacionamentos", ""))
    return {
        "chunk_id": chunk.get("chunk_id", ""),
        "documento": chunk.get("documento", ""),
        "titulo": chunk.get("titulo", ""),
        "categoria": chunk.get("categoria", ""),
        "tipo_conhecimento": chunk.get("tipo_conhecimento", ""),
        "versao": chunk.get("versao", ""),
        "responsavel": chunk.get("responsavel", ""),
        "ultima_atualizacao": chunk.get("ultima_atualizacao", ""),
        "status": chunk.get("status", ""),
        "prioridade": chunk.get("prioridade", ""),
        "tags": tags,
        "relacionamentos": relacionamentos,
        "conteudo": chunk.get("conteudo", ""),
    }


def indexar_base() -> int:
    """Le o JSON e alimenta a colecao ChromaDB. Retorna quantos chunks foram indexados."""
    base = carregar_base(PASTA_PROJETO / "data" / "fitlife_knowledge.json")
    chunks = [chunk for chunk in base["chunks"] if chunk.get("status") == "Ativo"]

    if not chunks:
        raise ValueError("Nenhum chunk ativo foi encontrado na base de conhecimento.")

    ids = [chunk["chunk_id"] for chunk in chunks]
    documentos = [montar_texto_para_busca(chunk) for chunk in chunks]
    embeddings = gerar_embeddings(documentos)
    metadados = [_metadados_do_chunk(chunk) for chunk in chunks]

    # Evita duplicar a colecao entre execucoes.
    if colecao.count() > 0:
        ids_existentes = colecao.get(include=[])["ids"]
        if ids_existentes:
            colecao.delete(ids=ids_existentes)

    colecao.add(
        ids=ids,
        documents=documentos,
        embeddings=embeddings,
        metadatas=metadados,
    )

    return len(chunks)


if __name__ == "__main__":
    total = indexar_base()
    print(f"Colecao ChromaDB criada com {total} chunks ativos.")
