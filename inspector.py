"""Retrieval Inspector — ferramenta de auditoria do RAG (Streamlit).

Mostra, para cada pergunta, quais chunks foram recuperados, em que ordem,
com qual similaridade e quais metadados — além de montar o contexto que
seria enviado ao LLM. Funciona como prova de funcionamento do RAG.
"""

import streamlit as st
from rag.retriever import buscar

st.set_page_config(page_title="Retrieval Inspector — FitLife", layout="wide")

st.title("Retrieval Inspector — FitLife Academia")
st.caption("Auditoria do RAG: visualize quais chunks a busca recuperou e o contexto montado para o LLM.")

TOP_K = st.sidebar.slider("Top-K (número de chunks)", 1, 10, 3)

pergunta = st.text_input("Faça uma pergunta", placeholder="Ex.: Quanto custa o plano anual?")

if pergunta:
    try:
        resultado = buscar(pergunta, top_k=TOP_K)

        ids = resultado["ids"][0]
        documentos = resultado["documents"][0]
        metadados = resultado["metadatas"][0]
        distancias = resultado["distances"][0]

        st.subheader("Ranking de chunks recuperados")

        colunas = st.columns([1, 3, 2, 2, 3])
        colunas[0].markdown("**Rank**")
        colunas[1].markdown("**Chunk / Título**")
        colunas[2].markdown("**Categoria**")
        colunas[3].markdown("**Similaridade**")
        colunas[4].markdown("**Documento**")

        for i in range(len(ids)):
            meta = metadados[i]
            colunas = st.columns([1, 3, 2, 2, 3])
            colunas[0].write(i + 1)
            colunas[1].markdown(f"**{ids[i]}**\n\n{meta.get('titulo', '')}")
            colunas[2].write(meta.get("categoria", ""))
            colunas[3].write(f"{1 - distancias[i]:.3f}")
            colunas[4].write(meta.get("documento", ""))

        with st.expander("Ver detalhe dos chunks (metadados + texto)"):
            for i in range(len(ids)):
                meta = metadados[i]
                st.markdown(f"### {i + 1}. {ids[i]} — {meta.get('titulo', '')}")
                st.write("**Similaridade (coseno):**", f"{1 - distancias[i]:.3f}")
                st.write("**Metadados:**")
                st.json({k: v for k, v in meta.items() if k != "conteudo"})
                st.write("**Texto do chunk:**")
                st.write(meta.get("conteudo", ""))
                st.divider()

        contexto_llm = "\n\n".join(
            f"[id: {ids[i]}]\n{titulo}\n\n{conteudo}"
            for i, (titulo, conteudo) in enumerate(
                [(m.get("titulo", ""), m.get("conteudo", "")) for m in metadados]
            )
        )
        st.subheader("Contexto que seria enviado ao LLM")
        st.code(contexto_llm, language="markdown")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Não foi possível executar a busca. Talvez a base ainda não esteja indexada. Rode: python -m rag.indexer\n\nDetalhe: {exc}")
