# HarmonIA - Agente Virtual da Empório da Música

O HarmonIA é um agente conversacional modular baseado na arquitetura ReAct (Reasoning + Acting), desenvolvido para automatizar o atendimento ao cliente da loja Empório da Música. O sistema realiza consultas relacionais ao catálogo de produtos em tempo real, efetua cálculo de descontos vigentes, monitora o status de pedidos de clientes e esclarece dúvidas institucionais e regulatórias por meio de busca semântica em documentos oficiais (RAG).

---

## Estrutura do Repositório

```text
harmonIA/
├── data/                       # Arquivos de dados operacionais e PDFs
│   ├── faiss_index/            # Índice vetorial persistido localmente (RAG)
│   ├── models/                 # Pesos locais do modelo de embeddings
│   ├── database.sqlite         # Banco de dados relacional SQLite
│   └── políticas_da_loja.pdf   # Documento oficial de políticas da loja
├── examples/                   # Exemplos documentados de interação com a interface
│   ├── assets/                 # Evidências em imagem da interface gráfica
│   ├── 01_consulta_catalogo.md
│   ├── 02_informacoes_gerais.md
│   ├── 03_status_pedido_e_preco.md
│   └── 04_politica_devolucao_e_arrependimento.md
├── src/                        # Código-fonte da aplicação
│   ├── agent/                  # Módulo de orquestração do agente (ReAct)
│   │   ├── __init__.py
│   │   ├── core.py             # Instanciação do agente e binding de ferramentas
│   │   ├── orchestrator.py     # Ponto de entrada para execução do fluxo
│   │   └── prompts.py          # Definidores de persona e System Prompt
│   ├── rag/
│   │   └── policy_retriever.py # Pipeline RAG com FAISS e embeddings locais
│   ├── tools/
│   │   ├── database.py         # Conexão SQLite e inicialização de tabelas
│   │   └── data_tools.py       # Ferramentas compostas de produtos e pedidos
│   └── config.py               # Fábrica de LLM e gerenciamento de ambiente
├── tests/                      # Suíte de testes unitários isolados
│   ├── test_agent.py
│   ├── test_config.py
│   ├── test_data_tools.py
│   ├── test_database.py
│   └── test_policy_retriever.py
├── app.py                      # Interface Web principal (Streamlit)
├── main.py                     # Interface de linha de comando (CLI)
├── requirements.txt            # Dependências do projeto
└── README.md                   # Documentação técnica do sistema
```

---

## Decisões Técnicas e Arquitetura

### 1. Framework do Agente e Padrão ReAct (`src/agent/`)

- **Abordagem:** Agente ReAct (Reasoning + Acting) implementado via LangChain / LangGraph com suporte a chamadas de função (`tool calling`).
- **Justificativa:** O padrão ReAct autoriza a LLM a raciocinar sobre qual ferramenta invocar dinamicamente, permitindo resolução de consultas compostas ou encadeadas em uma única sessão.
- **Modularização:** O repositório segue o Princípio da Responsabilidade Única (SRP):
  - `prompts.py`: Concentra as diretrizes operacionais, limitações de escopo e definições de persona.
  - `core.py`: Monta a instância do `AgentExecutor` e realiza a vinculação do modelo às ferramentas disponíveis.
  - `orchestrator.py`: Exporta a interface de execução padronizada para as camadas de apresentação.

### 2. Modelo de Linguagem e Resiliência de API (`src/config.py`)

- **Provedor Padrão:** Groq executando o modelo `qwen/qwen3.8-27b` (ou `llama-3.3-70b-versatile`).
- **Resiliência a Limites de Quota:** Configuração do limite máximo de saída (`max_tokens=800`) para evitar erros HTTP 429 decorrentes das restrições de Tokens de Saída por Minuto (OTPM) da API.
- **Arquitetura Multi-Provedor:** Implementação do padrão Factory parametrizado por variáveis de ambiente (`.env`), garantindo alternância transparente entre Groq, OpenAI, Google Gemini e Ollama.

### 3. Camada Relacional e Ferramentas Compostas (`src/tools/`)

- **Persistência SQLite (`database.py`):** Carga dos dados operacionais organizados em tabelas relacionais (`products`, `categories`, `promotions`, `orders`, `customers`, `order_items`). Utilização do parâmetro `check_same_thread=False` para garantir thread-safety no ambiente concorrente do Streamlit.
- **Composite Tools (`data_tools.py`):** Consolidação de queries em ferramentas de alto nível para reduzir o consumo de tokens e mitigar alucinações:
  1. `buscar_produtos`: Executa junções relacionais entre produtos, categorias e promoções ativas, aplicando o cálculo do preço final promocional em tempo de execução.
  2. `consultar_status_pedido`: Agrupa os dados do comprador, estado do despacho, código de rastreamento e itens vinculados por ID de pedido ou nome do cliente.

### 4. Pipeline RAG de Políticas e Otimizações (`src/rag/policy_retriever.py`)

- **Indexação Vetorial:** Utilização de repositório vetorial FAISS associado ao modelo de embeddings `sentence-transformers/all-MiniLM-L6-v2`.
- **Estratégia de Chunking:** Fatiamento com `chunk_size=1200` e `chunk_overlap=200` para garantir a preservação de dados tabulares e seções completas de contato e horários sem truncamento.
- **Recuperação Contextual:** Busca parametrizada para $k=6$ documentos mais relevantes, assegurando a extração de dados abrangentes em perguntas compostas.
- **Eliminação de Latência:**
  - **Carregamento Offline (`local_files_only=True`):** Supressão de chamadas de checagem remota na inicialização dos modelos do Hugging Face Hub.
  - **Rotina de Warm-up:** Pré-carregamento do índice FAISS e do banco SQLite na inicialização do `app.py` e `main.py`, eliminando a latência de primeira resposta (*cold start*).

### 5. Interface de Usuário e Controle de Estado

- **Interface Web (`app.py`):** Desenvolvida em Streamlit, oferecendo formatação dinâmica em Markdown, gerenciamento visual de estado e feedback de processamento via componentes de carga.
- **Interface CLI (`main.py`):** Módulo de linha de comando para simulações locais ou execução de consultas pontuais via argumento de sistema.
- **Gerenciamento de Histórico:** Histórico mantido no estado da sessão (`st.session_state`) e integrado ao pipeline ReAct por meio do componente `MessagesPlaceholder`.

---

## Instruções de Instalação e Execução

### 1. Requisitos do Sistema

- Python 3.10 ou superior.

### 2. Configuração do Ambiente Virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

### 3. Instalação de Dependências

```bash
pip install -r requirements.txt
```

### 4. Variáveis de Ambiente (`.env`)

Crie o arquivo `.env` na raiz do repositório contendo as chaves de acesso necessárias:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=sua_chave_groq_aqui
GROQ_MODEL=qwen/qwen3.8-27b
```

---

## Modos de Execução

### Interface Web (Streamlit)

```bash
streamlit run app.py
```
A aplicação estará disponível em `http://localhost:8501`.

### Interface de Linha de Comando (CLI)

- **Modo Interativo:**
  ```bash
  python main.py
  ```

- **Consulta Direta:**
  ```bash
  python main.py "Quais violões estão em promoção e qual o horário de funcionamento da loja?"
  ```

### Execução da Suíte de Testes (Pytest)

```bash
pytest
```
A suíte executa 15 testes unitários isolados através de *mocks*, validando a fábrica de LLMs, a camada de banco de dados, o retriever do RAG e a orquestração do agente.

---

## Registros de Interação

A pasta [`examples/`](./examples/) contém documentados quatro cenários reais de interação do agente, cobrindo buscas no catálogo, informações institucionais, status de pedidos e tratamento de políticas de devolução, acompanhados das respectivas capturas de tela da interface.

---

## Uso de Assistentes de IA no Desenvolvimento

No decorrer do projeto, utilizou-se o modelo de Pair Programming em colaboração com o assistente **Gemini**.

**Aplicações principais no fluxo de trabalho:**
1. **Refatoração do Agente:** Adequação da arquitetura às convenções recentes do LangChain v0.3+ e desacoplamento dos componentes do agente.
2. **Concorrência do SQLite:** Resolução de bloqueios de thread na conexão do SQLite ao operar sob o gerenciador de estado concorrente do Streamlit.
3. **Otimização do Pipeline de Testes:** Criação de testes unitários isolados com substituição de dependências externas (*mocking*), reduzindo a execução da suíte para frações de segundo.

---

## Limitações Conhecidas e Evoluções Futuras

1. **Persistência Externa de Memória:** Migração do histórico em memória para bancos de dados persistentes (como Redis ou PostgreSQL).
2. **Camada de Segurança e Moderação:** Implementação de mecanismos de filtragem (*guardrails*) para contenção de ataques de injeção de prompt ou desvio de escopo comercial.
3. **Respostas em Streaming:** Atualização da interface Streamlit para renderização incremental de respostas (*token streaming*).
4. **Métricas Contínuas de RAG:** Automação de avaliação da qualidade da recuperação vetorial (precisão e relevância) por meio do framework Ragas ou integração com LangSmith.