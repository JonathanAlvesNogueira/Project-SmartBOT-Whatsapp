"""Gera respostas personalizadas a partir do RAG usando um LLM local (Llama).

O Llama 3.2 1B Instruct (carregado via transformers, 100% offline) faz dois
trabalhos em uma unica chamada:
  1) percebe o sentimento/tom do cliente a partir da mensagem;
  2) gera a resposta usando apenas o conteudo relevante recuperado pelo RAG,
     ajustando o tom de acordo com o sentimento detectado.

Isso dispensa uma biblioteca separada de analise de sentimentos: o proprio
LLM entende o contexto e a emocao embutida na pergunta.
"""

import os
import sys
from functools import lru_cache

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from transformers import AutoModelForCausalLM, AutoTokenizer

from rag.retriever import buscar

# Modelo publico da Unsloth (nao exige aceite de licenca da Meta nem token).
MODELO_LLAMA = "unsloth/Llama-3.2-1B-Instruct"
# Quantos chunks recuperar e usar como contexto.
TOP_K = 3
# Respostas longas demais sao lentas na CPU; limite e prudente.
MAX_NEW_TOKENS = 120

_tok = None
_model = None


@lru_cache(maxsize=1)
def _carregar():
    """Carrega o Llama uma unica vez (lazy) e reutiliza nas proximas chamadas."""
    global _tok, _model
    if _model is None:
        _tok = AutoTokenizer.from_pretrained(MODELO_LLAMA)
        _model = AutoModelForCausalLM.from_pretrained(MODELO_LLAMA)
    return _tok, _model


def montar_contexto(pergunta: str, top_k: int = TOP_K):
    """Executa o RAG e devolve o contexto pronto para montar o prompt."""
    resultado = buscar(pergunta, top_k=top_k)
    docs = resultado["documents"][0] or []
    metas = resultado["metadatas"][0] or []
    dists = resultado["distances"][0] or []
    blocos = []
    for doc, meta, dist in zip(docs, metas, dists):
        sim = max(0.0, 1.0 - dist)  # distancia de cosseno -> similaridade
        titulo = meta.get("titulo", "?")
        categoria = meta.get("categoria", "?")
        codigo = meta.get("chunk_id") or meta.get("codigo") or "?"
        conteudo = meta.get("conteudo") or doc
        blocos.append(
            f"[{codigo} | {categoria} | {titulo} | confianca {sim:.0%}]\n{conteudo}"
        )
    return "\n\n".join(blocos)


def montar_prompt(pergunta: str, contexto: str):
    """Monta o prompt que instrui o LLM a usar so o contexto (RAG) e a
    ajustar o tom conforme o sentimento do cliente."""
    return (
        "Voce e o assistente da academia FitLife. Responda usando SOMENTE o "
        "contexto abaixo (nao invente informacoes).\n\n"
        "IDENTIFIQUE o sentimento do cliente na mensagem (ex.: irritado, ansioso, "
        "feliz, neutro) e ajuste o tom da resposta de acordo: seja calmante e "
        "empatico se ele estiver insatisfeito, e cordial e objetivo se neutro.\n"
        "Seja breve, claro e em portugues.\n\n"
        "### CONTEXTO (da base de conhecimento)\n"
        f"{contexto}\n\n"
        "### MENSAGEM DO CLIENTE\n"
        f"{pergunta}\n\n"
        "### RESPOSTA"
    )


def responder(pergunta: str, top_k: int = TOP_K, imprimir: bool = False) -> str:
    """Pipeline completo: RAG (recupera chunk) -> Llama (sentimento + resposta)."""
    contexto = montar_contexto(pergunta, top_k)
    prompt = montar_prompt(pergunta, contexto)
    tok, model = _carregar()

    enc = tok.apply_chat_template(
        [{"role": "user", "content": prompt}],
        return_tensors="pt",
        add_generation_prompt=True,
    )
    inputs = enc.input_ids

    out = model.generate(
        inputs,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=False,
        eos_token_id=tok.eos_token_id,
        pad_token_id=tok.eos_token_id,
    )
    novo = out[0][inputs.shape[1]:]
    # Desconsidera tokens especiais/BOS que o modelo re-emite. `skip_special_tokens`
    # remove os marcadores <|eot_id|>; o id 1 (BOS) e consumido como token comum,
    # entao forca o pad_token a nao decodificar lixo.
    resposta = tok.decode(novo, skip_special_tokens=True).strip()
    # O Llama costuma embrulhar a resposta em aspas duplas; remove para exibicao limpa.
    if len(resposta) >= 2 and resposta[0] == '"' and resposta[-1] == '"':
        resposta = resposta[1:-1].strip()

    if imprimir:
        print("\n--- RAG (contexto usado) ---")
        print(contexto)
        print("\n--- RESPOSTA DO LLAMA ---")
        print(resposta)
        print("--------------------------------\n")
    return resposta


if __name__ == "__main__":
    responder("Quero cancelar meu plano AGORA, estou muito insatisfeito!", imprimir=True)
