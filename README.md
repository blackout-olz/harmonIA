# HarmonIA - Agente Inteligente Empório da Música

O HarmonIA é um agente virtual modular projetado para o desafio da Empório da Música. O sistema atende dúvidas sobre catálogo de produtos, rastreamento de pedidos e regras/políticas da loja através de uma arquitetura baseada em chamada de ferramentas (Tool Calling) e geração aumentada por recuperação (RAG).

---

## Estrutura do Projeto

```text
harmonIA/
├── data/                    # Base de dados em CSV e PDF de políticas
├── src/
│   ├── config.py            # Factory de LLMs multi-provedor
│   ├── rag/
│   │   └── policy_retriever.py # Recuperador vetorial RAG (FAISS + HuggingFace)
│   └── tools/
│       ├── database.py      # Camada de persistência SQLite em memória
│       └── data_tools.py    # Ferramentas compostas de busca de produtos e pedidos
├── tests/                   # Suíte de testes unitários com Pytest
└── requirements.txt         # Dependências do projeto
```

---

## Decisões de Arquitetura e Engenharia

### 1. Factory de LLM Multi-Provedor (`src/config.py`)
- **Abordagem:** Implementação do padrão Factory parametrizado via variáveis de ambiente (`.env`).
- **Provedores Suportados:** Groq, Google Gemini, OpenAI e Ollama.
- **Modelo Padrão:** `qwen/qwen3.8-27b` (Groq), selecionado pelo desempenho no idioma português e suporte a Tool Calling.
- **Objetivo:** Permitir a alternância entre provedores de linguagem sem alterações no código da aplicação.

### 2. Camada Relacional em Memória (`src/tools/database.py`)
- **Abordagem:** Carregamento automatizado de 6 arquivos CSV para uma instância de banco SQLite em memória (`:memory:`).
- **Objetivo:** Garantir tempo de resposta reduzido, isolamento de estado nos testes unitários e eliminação de dependências de infraestrutura de banco de dados externa.

### 3. Ferramentas Compostas / Composite Tools (`src/tools/data_tools.py`)
- **Abordagem:** Consolidação de 6 tabelas relacionais em 2 ferramentas integradas por consultas SQL JOIN:
  - `buscar_produtos`: Integração entre produtos, categorias e promoções ativas, aplicando cálculo de descontos em tempo de execução.
  - `consultar_status_pedido`: Integração entre pedidos, clientes e itens, permitindo busca por código do pedido ou nome do cliente.
- **Objetivo:** Minimizar a carga cognitiva do modelo de linguagem, reduzindo chamadas de rede redundantes e evitando inconsistências em associações de dados.

### 4. RAG Local para Políticas (`src/rag/policy_retriever.py`)
- **Abordagem:** Utilização de FAISS em memória com embeddings locais (`sentence-transformers/all-MiniLM-L6-v2`) via HuggingFace.
- **Ferramenta:** `consultar_politicas`.
- **Objetivo:** Execução offline na CPU sem consumo de cotas de APIs de embeddings, garantindo previsibilidade e autonomia.

---

## Estratégia de Testes (TDD)

A aplicação possui cobertura de testes automatizados com `pytest`, utilizando mocks para isolar requisições de rede externas:

- `tests/test_database.py`: Validação de carregamento dos CSVs e integridade do schema SQLite.
- `tests/test_config.py`: Validação da fábrica de LLMs e tratamento de exceções de provedores.
- `tests/test_data_tools.py`: Validação das consultas de produtos, filtros de preços e rastreamento de pedidos.
- `tests/test_policy_retriever.py`: Validação da busca semântica em trechos do PDF de políticas.

---

## Instruções de Execução

### 1. Configuração do Ambiente Virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalação de Dependências
```bash
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente
Crie o arquivo `.env` seguindo o modelo abaixo:
```env
LLM_PROVIDER=groq
GROQ_API_KEY=sua_chave_groq
GROQ_MODEL=qwen/qwen3.8-27b
```

### 4. Execução dos Testes Unitários
```bash
pytest
```