# Smart WhatsApp Agent — FitLife Academia

Chatbot inteligente para WhatsApp usando **LLM + RAG + (futuro) Análise de Sentimentos**, desenvolvido como trabalho de extensão do curso de **Ciência de Dados**. O contexto é uma academia fictícia (**FitLife Academia**) para demonstrar o produto em um cenário corporativo real.

> **Status atual:** MVP do RAG (Sprint 4) + **camada de LLM local (Sprint 5)** — busca vetorial aprovada (5/5) e respostas personalizadas por sentimento via **Llama 3.2 1B** (offline, gratuito). Priorização e integração com WhatsApp são sprints futuros.

---

## 🎯 Objetivo

Criar um agente capaz de:

- Responder dúvidas sobre a academia usando uma base documental (RAG);
- (futuro) Adaptar o tom da resposta conforme o sentimento do cliente;
- (futuro) Priorizar atendimentos críticos;
- (futuro) Registrar conversas para geração de indicadores.

**ODS:** ODS 8 — Trabalho Decente e Crescimento Econômico.

---

## 🧠 Arquitetura

```
Cliente envia pergunta → vira embedding → busca vetorial no ChromaDB
        → recupera os melhores chunks → Llama (LLM local) gera a resposta
        → o Llama percebe o sentimento e ajusta o tom (empático/neutro/etc.)
```

## 📁 Estrutura do projeto

```
smart-whatsapp-agent/
├── data/
│   └── fitlife_knowledge.json      # Base de conhecimento (52 chunks) — FIT-KNOWLEDGE-v2.0
│
├── rag/
│   ├── loader.py                   # Carrega o JSON da base
│   ├── embedder.py                 # Embeddings neurais locais (sentence-transformers)
│   ├── chroma_manager.py           # Conexão com o ChromaDB (coleção "fitlife")
│   ├── indexer.py                  # Indexa os 52 chunks no ChromaDB
│   └── retriever.py                # Busca vetorial Top-K (buscar)
│
├── llm/
│   └── responder.py                # RAG + Llama: sentimento + resposta personalizada
│
├── tests/
│   └── test_5_questoes.py          # Teste de aceite (5 perguntas obrigatórias)
│
├── inspector.py                    # Retrieval Inspector (Streamlit) — auditoria do RAG
├── chat.py                         # Chat com o assistente (Streamlit) — RAG + Llama
├── teste_rag.ipynb                 # Notebook interativo para testar a busca
│
├── Documentação Projeto.docx       # Documentação acadêmica
├── Manual_Institucional_FitLife_Academia_v2_0.docx  # Fonte oficial da verdade
├── requisitos_sistema.xlsx         # Requisitos funcionais e não funcionais
│
├── requirements.txt
└── .env.example                    # Modelo de configuração sem segredos
```

---

## ✅ O que já funciona (MVP do RAG + LLM local)

- [x] Validar `fitlife_knowledge.json` (52 chunks, sem duplicados);
- [x] Gerar **embeddings neurais locais** (offline, sem custo, sem API);
- [x] Indexar os 52 chunks no **ChromaDB**;
- [x] Buscar **Top-K por similaridade de cosseno**;
- [x] **Retrieval Inspector** em Streamlit (auditoria do RAG);
- [x] **Teste de aceite 5/5** no Top-3;
- [x] **LLM local (Llama 3.2 1B)**: gera resposta a partir do chunk recuperado;
- [x] **Análise de sentimento implícita**: o próprio Llama percebe o tom do cliente
      e ajusta a resposta (empático, neutro, etc.) — sem biblioteca separada.

## 🔜 Próximos sprints (futuro)

- [ ] Priorização de atendimentos críticos;
- [ ] Registro de conversas e métricas (indicadores);
- [ ] Integração com **WhatsApp**.

---

## 🚀 Como rodar

> Segurança: copie `.env.example` para `.env` somente se precisar configurar uma futura integração. Nunca publique o arquivo `.env` ou chaves de API.

### 1. Criar e ativar o ambiente virtual (recomendado)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

> 💡 A primeira execução baixa o modelo de embeddings da Hugging Face (uma vez). Depois disso, funciona **100% offline** e sem custo.

### 3. Indexar a base de conhecimento

```bash
python -m rag.indexer
```

> O índice é criado na pasta `chroma_db/` (gerada automaticamente).

### 4. Testar o RAG

**Teste de aceite (5 perguntas obrigatórias):**

```bash
python -m tests.test_5_questoes
```

Esperado: `5/5 acertos no Top-3`.

### 5. Abrir o Retrieval Inspector (Streamlit)

```bash
streamlit run inspector.py
```

Digite uma pergunta e veja quais chunks foram recuperados, a similaridade, a categoria e o contexto que seria enviado ao LLM.

### 6. Testar no notebook interativo

```bash
.venv\Scripts\python.exe -m pip install jupyter
.venv\Scripts\python.exe -m jupyter notebook
```

Abra `teste_rag.ipynb` e use as células para testar frases livremente.

### 7. Gerar resposta com o LLM local (Llama 3.2 1B)

```bash
python -m llm.responder
```

A primeira execução baixa o modelo (≈2,5 GB) da Hugging Face. Depois disso é
**100% offline e gratuito**. Escreva o uso no código para customizar a pergunta:

```python
from llm.responder import responder
resposta = responder("Quero cancelar meu plano AGORA!")   # demora ~15-30s na CPU
```

### 8. Abrir o Chat do assistente (Streamlit)

```bash
streamlit run chat.py
```

Interface de conversa no navegador: digite a pergunta, veja a resposta do
Llama e marque **"Ver contexto RAG"** para inspecionar quais chunks embasaram
a resposta (prova de funcionamento do pipeline).

> ⚠️ **Sobre a velocidade:** na CPU (sem GPU) cada resposta leva ~15–30 s — aceitável
> para demonstração acadêmica, não para um chat em tempo real. Uma GPU permitiria
> respostas em poucos segundos. O modelo usado é o Llama 3.2 **1B** (quantizado),
> o que o mantém leve e viável para portfólio/demo.

---

## 🧪 Perguntas de exemplo

| Pergunta | Chunk esperado |
|---|---|
| Quanto custa o plano anual? | FIT-PLAN-003 |
| Posso cancelar meu plano? | FIT-POL-002 |
| Que horas abre domingo? | FIT-HOR-001 |
| Tem funcional? | FIT-MOD-002 |
| Posso fazer aula teste? | FIT-FAQ-002 |
| Onde fica a FitLife Academia? | FIT-LOC-001 |
| Como chegar à academia? | FIT-LOC-002 |
| A academia tem estacionamento? | FIT-LOC-003 |

Outras: `"Quais os horários da musculação?"`, `"Quero cancelar meu plano."`

> A localização cadastrada é fictícia e existe exclusivamente para a demonstração do projeto.

---

## 🧩 Sobre os embeddings (decisão de arquitetura)

O projeto usa embeddings **neurais locais** com `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensões, multilíngue — cobre o português), em vez da API da OpenAI. Motivos:

- **Custo zero** e **100% offline** após o primeiro download;
- Ideal para demonstração acadêmica e portfólio;
- Qualidade semântica superior ao TF-IDF.

Para a busca, cada chunk é indexado com **título + categoria + tags + conteúdo**, o que melhora a recuperação de termos que não aparecem no corpo do texto (ex.: "funcional" é uma tag).

## 🤖 Sobre o LLM (decisão de arquitetura — Sprint 5)

A resposta final é gerada pelo **Llama 3.2 1B Instruct** (via HuggingFace/`transformers`),
escolhido em vez da API da OpenAI pelos mesmos motivos do RAG: **gratuito, offline** e sem
expor dados de clientes. Usamos a versão pública do **Unsloth** (não exige aceite de
licença da Meta nem token).

**Por que não usar uma biblioteca separada de análise de sentimentos?**
O próprio Llama, ao receber o prompt com o contexto do RAG + a mensagem do cliente,
**identifica o sentimento no texto** (irritado, ansioso, neutro, feliz...) e já gera a
resposta **no tom adequado**. Isso simplifica o código, reduz dependências e é mais
fácil de explicar no trabalho ("o LLM entende o contexto e a emoção"). Exemplos medidos:

| Entrada | Comportamento |
|---|---|
| "Quanto custa o plano anual?" | Tom **neutro/objetivo**, com o dado do chunk (R$69/mês) |
| "REVOLTADO! Vou processar vocês!" | Tom **empático/acolhedor**, sem confrontar |

**Limitação conhecida:** a CPU gera ~15–30 s por resposta (modelo 1B em float32).
É suficiente para demonstração; uma GPU tornaria o agente viável em tempo real.

---

## 🔑 Decisões de projeto que você não pode esquecer

> ⚠️ Esta seção documenta duas decisões importantes para você **não se perder** ao
> revisitar o código (ou apresentá-lo). Leia antes de mexer.

### 1. O LLM é **stateless** — sem memória de conversa

O Llama **não guarda nada** entre uma resposta e outra. Cada chamada a
`responder()` é independente: ele "esquece" toda a conversa anterior, e o prompt
é montado do zero a cada vez. O que **fica armazenado** é apenas a **base fixa de
conhecimento** (os 52 chunks do JSON indexados no ChromaDB) — não a memória do
diálogo.

**Por que isso importa e como vira diferencial no futuro:**

- Hoje, o agente trata cada mensagem isoladamente (adequado para demonstração).
- Um **diferencial futuro/feature vendável**: adicionar **histórico de conversa**
  (uma lista das mensagens trocadas que é passada junto no prompt), para o agente
  responder com contexto do diálogo (`"como você disse antes..."`).
- Implementar isso = manter as mensagens acumuladas e incluí-las no `montar_prompt()`,
  respeitando o limite de contexto do modelo.

### 2. `responder.py` **já integra RAG + LLM** (não são coisas separadas)

RAG e LLM **não** são módulos desconectados. O `llm/responder.py` é exatamente a
**integração** entre eles — uma única chamada `responder(pergunta)` executa o
pipeline completo em sequência:

```
responder("pergunta")
   ├─ 1° RAG : buscar() → embedding → ChromaDB → recupera o chunk (linha 46)
   ├─ 2° montar_prompt() : junta chunk + instrução de tom (linha 84)
   ├─ 3° _carregar() : carrega o Llama (linha 85)
   └─ 4° model.generate() : gera a resposta (linha 94)
```

Para uso, basta chamar `responder()` — a integração já acontece por dentro.
**Rode sempre da raiz do projeto** (`python -m llm.responder`), nunca de dentro
da pasta `llm/`, para os imports (`from rag.retriever import`) continuarem valendo.

**Duas bibliotecas distintas (evite confundir no relatório):**

| Componente | Biblioteca | Papel |
|---|---|---|
| **RAG (busca)** | `sentence-transformers` | transforma texto em embeddings p/ a busca |
| **LLM (resposta)** | `transformers` (Llama) | gera a resposta a partir do chunk |

O RAG **não** usa o Llama para buscar, e o LLM **não** usa os embeddings para
responder. São camadas conectadas pelo `responder.py`.

---

## 📄 Documentação

- **Fonte oficial da verdade:** `Manual_Institucional_FitLife_Academia_v2_0.docx`
- **Documentação acadêmica:** `Documentação Projeto.docx`
- **Requisitos:** `requisitos_sistema.xlsx`

---

## 👥 Autoria

Projeto de extensão em **Ciência de Dados** — FitLife Academia (ambiente de demonstração).

---

## 📚 Referências

Referências técnicas que fundamentam o projeto (usadas como **base de consulta**):

- **HUYEN, Chip.** *Designing Machine Learning Systems: An Iterative Process for
  Production-Ready Applications*. O'Reilly Media, 2022. — **Referência principal**
  do projeto: fundamenta o pipeline de **RAG** (recuperação + geração), a busca
  vetorial por embeddings, e as decisões de produção (custo, offline, qualidade).

### Principais bibliotecas / tecnologias aplicadas
- **sentence-transformers** — embeddings neurais locais (busca semântica no RAG);
- **ChromaDB** — banco vetorial (indexação e consulta por similaridade de cosseno);
- **transformers (Hugging Face)** — execução do LLM **Llama 3.2 1B** local;
- **Streamlit** — interface do *Retrieval Inspector* (auditoria do RAG).