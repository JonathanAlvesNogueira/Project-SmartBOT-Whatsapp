# Smart WhatsApp Agent — FitLife Academia

Chatbot inteligente para WhatsApp usando **LLM + RAG + (futuro) Análise de Sentimentos**, desenvolvido como trabalho de extensão do curso de **Ciência de Dados**. O contexto é uma academia fictícia (**FitLife Academia**) para demonstrar o produto em um cenário corporativo real.

> **Status atual:** MVP do RAG (Sprint 4) — busca vetorial funcionando e aprovada. Camadas de LLM, sentimento, priorização e WhatsApp são sprints futuros.

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
        → recupera os melhores chunks → (futuro) LLM responde com esse contexto
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
├── tests/
│   └── test_5_questoes.py          # Teste de aceite (5 perguntas obrigatórias)
│
├── inspector.py                    # Retrieval Inspector (Streamlit)
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

## ✅ O que já funciona (MVP do RAG)

- [x] Validar `fitlife_knowledge.json` (52 chunks, sem duplicados);
- [x] Gerar **embeddings neurais locais** (offline, sem custo, sem API);
- [x] Indexar os 52 chunks no **ChromaDB**;
- [x] Buscar **Top-K por similaridade de cosseno**;
- [x] **Retrieval Inspector** em Streamlit (auditoria do RAG);
- [x] **Teste de aceite 5/5** no Top-3.

## 🔜 Próximos sprints (futuro)

- [ ] Camada de **LLM** (montar prompt e gerar resposta a partir do contexto);
- [ ] **Análise de sentimentos** e adaptação de tom;
- [ ] Priorização de atendimentos críticos;
- [ ] Registro de conversas e métricas;
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

---

## 📄 Documentação

- **Fonte oficial da verdade:** `Manual_Institucional_FitLife_Academia_v2_0.docx`
- **Documentação acadêmica:** `Documentação Projeto.docx`
- **Requisitos:** `requisitos_sistema.xlsx`

---

## 👥 Autoria

Projeto de extensão em **Ciência de Dados** — FitLife Academia (ambiente de demonstração).
