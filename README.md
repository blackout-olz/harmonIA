# HarmonIA - Agente Virtual da Empório da Música

O HarmonIA é um agente inteligente modular desenvolvido para automatizar o atendimento ao cliente da Empório da Música. O sistema consulta o catálogo de produtos em tempo real, calcula promoções ativas, rastreia pedidos de clientes e responde dúvidas institucionais e políticas da loja através de busca semântica em documentos oficiais (RAG).

## Estrutura do Projeto

```text
harmonIA/
├── data/                       # CSVs operacionais e PDF de políticas
│   ├── faiss_index/            # Índice vetorial persistido localmente (RAG)
│   └── políticas_da_loja.pdf   # Documento oficial de políticas
├── src/
│   ├── agent/                  # Módulo do agente conversacional (ReAct)
│   │   ├── __init__.py
│   │   ├── core.py             # Instanciação do agente e vinculação de ferramentas
│   │   ├── orchestrator.py     # Função de entrada para execução do fluxo
│   │   └── prompts.py          # Persona e diretrizes do sistema (System Prompt)
│   ├── rag/
│   │   └── policy_retriever.py # RAG com FAISS e embeddings locais
│   ├── tools/
│   │   ├── database.py         # SQLite em memória e carregamento dos CSVs
│   │   └── data_tools.py       # Composite Tools de produtos e pedidos
│   └── config.py               # Factory de LLMs multi-provedor
├── tests/                      # Suíte de testes unitários e de integração
│   ├── test_agent.py
│   ├── test_config.py
│   ├── test_data_tools.py
│   ├── test_database.py
│   └── test_policy_retriever.py
├── app.py                      # Interface Web em Streamlit
├── main.py                     # Interface CLI (linha de comando)
├── requirements.txt            # Dependências do projeto
└── README.md                   # Documentação do projeto
```

## Decisões Técnicas e Arquitetura

### 1. Framework do Agente e Padrão ReAct (`src/agent/`)

- **Abordagem:** Agente ReAct (Reasoning + Acting) utilizando a função `create_tool_calling_agent` da biblioteca LangChain.
- **Justificativa:** O padrão ReAct permite que o modelo de linguagem raciocine dinamicamente sobre qual ferramenta invocar com base na intenção do usuário, viabilizando chamadas encadeadas e simultâneas (por exemplo, pesquisar produtos em promoção e consultar a política de troca em uma única interação).
- **Modularização:** O pacote foi estruturado segundo o Princípio de Responsabilidade Única (SRP):
  - `prompts.py`: Define o System Prompt, a persona institucional e as regras de engajamento.
  - `core.py`: Constrói a instância do `AgentExecutor` e vincula o LLM às ferramentas.
  - `orchestrator.py`: Fornece a interface simplificada para invocação do fluxo.

### 2. Modelo e Provedor de LLM (`src/config.py`)

- **Provedor Padrão:** Groq com o modelo `qwen/qwen3.8-27b` (ou `llama-3.3-70b-versatile`).
- **Justificativa:**
  - **Baixa Latência:** A infraestrutura de processamento da Groq oferece tempos de resposta otimizados para interações em tempo real.
  - **Suporte a Tool Calling:** Alta precisão na geração do esquema JSON para chamadas de ferramentas.
  - **Fluência em Português:** Compreensão contextual adequada para atendimento comercial no Brasil.
- **Arquitetura Multi-Provedor:** Implementação do padrão Factory parametrizado via `.env`, permitindo alternância transparente entre Groq, Google Gemini, OpenAI e Ollama.

### 3. Tratamento de Dados e Estratégia de Ferramentas (`src/tools/`)

- **Camada Relacional SQLite (`database.py`):** Carregamento dos 6 arquivos CSV operacionais (`products`, `categories`, `promotions`, `orders`, `customers`, `order_items`) para um banco SQLite em memória. A flag `check_same_thread=False` garante a execução segura em ambientes concorrentes multi-thread (Streamlit).
- **Ferramentas Compostas / Composite Tools (`data_tools.py`):** Consolidação das tabelas relacionais em 2 ferramentas principais para otimizar o consumo de tokens e a precisão do agente:
  1. `buscar_produtos`: Executa consultas relacionais com junções entre produtos, categorias e promoções ativas, aplicando o cálculo exato de desconto em tempo de execução.
  2. `consultar_status_pedido`: Integra pedidos, dados do cliente e itens associados em uma resposta consolidada, aceitando buscas por ID do pedido ou nome do cliente.

### 4. RAG de Políticas e Otimização de Desempenho (`src/rag/policy_retriever.py`)

- **Arquitetura RAG:** Busca vetorial semântica baseada no FAISS combinada com embeddings locais (`sentence-transformers/all-MiniLM-L6-v2`).
- **Otimização de Latência:**
  - **Persistência de Índice Local (`data/faiss_index`):** O índice vetorial é construído na primeira execução e salvo em disco. Nas chamadas subsequentes, o repositório é recarrega instantaneamente em memória.
  - **Execução Offline (`local_files_only=True`):** Desativação de checagens remotas via HTTP no Hugging Face Hub, eliminando atrasos no tempo de inicialização.

### 5. Interface do Usuário e Gerenciamento de Estado

- **Interface Web (`app.py`):** Desenvolvida em Streamlit, oferecendo interface gráfica com suporte a formatação Markdown, tabelas e indicadores de carregamento (`st.spinner`).
- **Interface CLI (`main.py`):** Utilitário de linha de comando para execuções em modo interativo ou via argumentos diretos.
- **Histórico da Conversa:** Mantido através do `st.session_state` no Streamlit e integrado ao pipeline do LangChain via `MessagesPlaceholder(variable_name="chat_history")`.

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

### 4. Configuração das Variáveis de Ambiente (`.env`)

Crie o arquivo `.env` na raiz do projeto com as credenciais do provedor selecionado:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=sua_chave_groq_aqui
GROQ_MODEL=qwen/qwen3.8-27b
```

## Modos de Execução

### Interface Web (Streamlit)

```bash
streamlit run app.py
```

O aplicativo estará acessível no endereço `http://localhost:8501`.

### Interface de Linha de Comando (CLI)

- **Modo Interativo:**

  ```bash
  python main.py
  ```

- **Consulta Direta:**

  ```bash
  python main.py "Quais violões estão em promoção e qual a política de devolução?"
  ```

### Suíte de Testes Automatizados (Pytest)

```bash
pytest
```

A suíte executa 16 testes unitários e de integração, cobrindo o banco relacional, as Composite Tools, a fábrica de LLMs, o RAG e a orquestração do Agente ReAct.

## Uso de Assistentes de IA no Desenvolvimento

Durante a execução do projeto, foi adotado o modelo de Pair Programming com o assistente **Gemini**.

**Principais contribuições do assistente no fluxo:**

1. **Arquitetura do Agente:** Apoio no desacoplamento dos módulos em `src/agent/` e padronização do código segundo as diretrizes recentes do LangChain v0.3+.
2. **Resolução de Concorrência:** Diagnóstico do bloqueio de threads no SQLite quando consumido pelo gerenciador de estado do Streamlit.
3. **Otimização do RAG e Testes:** Identificação de gargalos na verificação de arquivos remotos da Hugging Face e criação de Mocks no Pytest, reduzindo o tempo de execução da suíte de testes de 112s para menos de 2s.

## Limitações Conhecidas e Evoluções Futuras

1. **Persistência Externa de Memória:** Integração com bancos como Redis ou PostgreSQL (pgvector) para persistir o histórico de conversas entre sessões distintas de usuários.
2. **Camada de Moderação e Safety:** Implementação de Guardrails (ex: NeMo Guardrails ou Llama Guard) para filtrar ataques de Prompt Injection ou consultas completamente desalinhadas ao escopo da loja.
3. **Respostas em Streaming:** Adaptação da interface Streamlit para exibir as respostas da LLM em formato token por token (`st.write_stream`).
4. **Avaliação Contínua (Evals):** Automação do cálculo de métricas de qualidade de RAG (Fidelidade e Relevância) via plataformas como LangSmith ou Ragas.