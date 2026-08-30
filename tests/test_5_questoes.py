"""Teste de aceite do MVP do RAG.

A funcao ``executar`` aceita uma lista de perguntas de formas diferentes e
adapta o comportamento sozinha:

- ``perguntas=None``        -> usa as 5 perguntas oficiais (criterio de aceite).
- lista de strings          -> modo LIVRE: so faz a busca e mostra o resultado.
- dict frase -> chunk esperado        -> modo VALIDACAO: aprova/reprova.
- dict frase -> (chunk, descricao)    -> igual acima, com descricao humana.

Uso (da raiz do projeto):
    python -m tests.test_5_questoes

Exemplos de uso:
    # Valida as 5 oficiais (padrao)
    ok = executar()

    # Modo livre: so mostra o que a busca encontra
    ok = executar(["Quais os horarios da musculacao?"])

    # Valida perguntas suas
    ok = executar({
        "Quais os horarios da musculacao?": "FIT-AULA-001",
        "Tem personal?": "FIT-MOD-003",
    })
"""

from rag.retriever import buscar

TOP_K = 3

# (pergunta, chunk esperado, descricao humana do chunk esperado)
PERGUNTAS_OFICIAIS = {
    "Quanto custa o plano anual?": ("FIT-PLAN-003", "Planos - Valor do plano anual"),
    "Posso cancelar meu plano?": ("FIT-POL-002", "Politica - Cancelamento do plano anual"),
    "Que horas abre domingo?": ("FIT-HOR-001", "Horarios - Abertura aos domingos"),
    "Tem funcional?": ("FIT-MOD-002", "Modalidades - Treino Funcional"),
    "Posso fazer aula teste?": ("FIT-FAQ-002", "FAQ - Aula experimental"),
}


def _resumir(ids: list[str], metadatas: list[dict]) -> list[str]:
    """Converte ids em descricoes humanas: 'FIT-PLAN-003 [Planos] Plano Anual'."""
    resumo = []
    for cid, meta in zip(ids, metadatas):
        titulo = meta.get("titulo") or "?"
        categoria = meta.get("categoria") or "?"
        resumo.append(f"{cid} [{categoria}] {titulo}")
    return resumo


def _buscar_e_mostrar(pergunta: str, esperado=None, descricao="", imprimir=True):
    """Executa a busca de uma pergunta e retorna (aprovado, rank, ids, metadatas)."""
    resultado = buscar(pergunta, top_k=TOP_K)
    ids = resultado["ids"][0]
    metadatas = resultado["metadatas"][0]

    # Modo validacao (tem chunk esperado)
    if esperado is not None:
        rank = ids.index(esperado) + 1 if esperado in ids else None
        aprovado = rank is not None
        if imprimir:
            print("=" * 70)
            print(f"Pergunta: {pergunta}")
            print(f"  -> Esperado  : {esperado} [{descricao}]")
            if aprovado:
                print(f"  -> Resultado : APROVADO (rank {rank} no Top-{TOP_K})")
            else:
                print(f"  -> Resultado : REPROVADO (chunk `{esperado}` fora do Top-{TOP_K})")
            print("  -> Os 3 chunks recuperados (mais relevantes primeiro):")
            for linha in _resumir(ids, metadatas):
                print(f"      • {linha}")
        return aprovado, rank, ids, metadatas

    # Modo livre (sem chunk esperado)
    if imprimir:
        print("=" * 70)
        print(f"Pergunta: {pergunta}")
        print("  -> Melhores chunks recuperados (mais relevantes primeiro):")
        for linha in _resumir(ids, metadatas):
            print(f"      • {linha}")
    return None, None, ids, metadatas


def executar(perguntas=None, imprimir=True) -> bool:
    """Valida (ou apenas explora) uma lista de perguntas sobre o RAG.

    Args:
        perguntas: None (oficiais), lista de strings (livre) ou dict (validacao).
        imprimir: se deve exibir o detalhe no console.

    Returns:
        bool: True se todas as perguntas com chunk esperado acertaram
              (ignora perguntas livres). Sem perguntas de validacao, retorna True.
    """
    # Decide o conjunto de perguntas
    if perguntas is None:
        perguntas = PERGUNTAS_OFICIAIS

    # Normaliza: qualquer string vira (frase, None, "")
    if isinstance(perguntas, (list, tuple)):
        perguntas = {p: None for p in perguntas}

    acertos = 0
    validacoes = 0

    for pergunta, alvo in perguntas.items():
        # Normaliza o alvo: "CHUNK" ou ("CHUNK", "descricao")
        if alvo is None:
            esperado, descricao = None, ""
        elif isinstance(alvo, (list, tuple)):
            esperado, descricao = alvo[0], (alvo[1] if len(alvo) > 1 else "")
        else:
            esperado, descricao = alvo, ""

        aprovado, rank, ids, metadatas = _buscar_e_mostrar(
            pergunta, esperado=esperado, descricao=descricao, imprimir=imprimir
        )

        if esperado is not None:
            validacoes += 1
            if aprovado:
                acertos += 1

    if imprimir:
        print("=" * 70)
        if validacoes:
            print("\nResultado: %d/%d perguntas validadas acertaram no Top-%d." % (acertos, validacoes, TOP_K))
            print("MVP do RAG", "APROVADO" if acertos == validacoes else "REPROVADO")
        else:
            print("\nModo livre: nenhuma pergunta tinha chunk esperado — apenas exploracao.")

    # Sem perguntas de validacao: considera aprovado (nada a reprovar)
    return (acertos == validacoes) if validacoes else True


if __name__ == "__main__":
    ok = executar()
    raise SystemExit(0 if ok else 1)
