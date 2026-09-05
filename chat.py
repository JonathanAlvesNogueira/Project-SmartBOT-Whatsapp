"""Chat FitLife — interface de conversa com o agente (Streamlit).

Pipeline completo em uma unica tela: o usuario digita a pergunta, o RAG
recupera o chunk mais relevante e o Llama (LLM local) gera a resposta no tom
adequado ao sentimento do cliente. Um expander mostra o contexto RAG usado
(prova de funcionamento, como no Inspector).
"""

import streamlit as st

from llm.responder import responder

st.set_page_config(page_title="Chat FitLife — Smart WhatsApp Agent", page_icon="💬", layout="centered")

st.title("💬 Chat FitLife — Assistent Virtual")
st.caption("RAG (ChromaDB) + Llama 3.2 1B local. O assistente percebe o tom da pergunta e ajusta a resposta.")

# Histórico da conversa (persistente enquanto o app estiver aberto).
if "historico" not in st.session_state:
    st.session_state.historico = []

# Campo do cliente + opção de ver contexto.
col_pergunta, col_ver = st.columns([5, 1])
pergunta = col_pergunta.text_input(
    "Sua mensagem",
    placeholder="Ex.: Quanto custa o plano anual?",
    label_visibility="collapsed",
)
enviar = col_pergunta.button("Enviar", type="primary", use_container_width=True)

ver_contexto = col_ver.checkbox("Ver contexto RAG", value=False)

if enviar and pergunta.strip():
    with st.spinner("Consultando a base e gerando resposta (pode levar ~15-30s na CPU)..."):
        try:
            resposta = responder(pergunta.strip())
            st.session_state.historico.append({"pergunta": pergunta.strip(), "resposta": resposta})
        except Exception as exc:  # noqa: BLE001
            st.error(f"Não foi possível responder. Verifique se a base está indexada (python -m rag.indexer) e se o modelo foi baixado.\n\nDetalhe: {exc}")

# Exibe a conversa (mais recente embaixo).
for i, turno in reversed(list(enumerate(st.session_state.historico))):
    st.container(border=True).markdown(
        f"**Você:** {turno['pergunta']}\n\n"
        f"**Assistente:**\n\n{turno['resposta']}"
    )

# Mostra o contexto RAG usado na última resposta (prova de funcionamento).
if ver_contexto and st.session_state.historico:
    ultima = st.session_state.historico[-1]
    contexto = __import__("llm.responder", fromlist=["montar_contexto"]).montar_contexto(ultima["pergunta"])
    with st.expander("Contexto RAG usado na última resposta"):
        st.code(contexto, language="markdown")

st.divider()
st.caption("Demo acadêmica — respostas podem levar alguns segundos e usar conhecimento apenas da base FitLife.")