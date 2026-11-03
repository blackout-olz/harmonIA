from unittest.mock import MagicMock, patch

try:
    from langchain.agents import AgentExecutor
except ImportError:
    try:
        from langchain.agents.agent_executor import AgentExecutor
    except ImportError:
        from langchain_classic.agents import AgentExecutor

from src.agent import criar_agente, executar_agente


@patch("src.agent.core.get_llm")
def test_criar_agente_instanciacao(mock_get_llm):
    """Valida se o AgentExecutor é instanciado corretamente com as ferramentas vinculadas."""
    mock_llm = MagicMock()
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)
    mock_get_llm.return_value = mock_llm

    agente = criar_agente(verbose=False)

    assert isinstance(agente, AgentExecutor)
    assert len(agente.tools) == 3

    nomes_tools = [tool.name for tool in agente.tools]
    assert "buscar_produtos" in nomes_tools
    assert "consultar_status_pedido" in nomes_tools
    assert "consultar_politicas" in nomes_tools


@patch("src.agent.orchestrator.criar_agente")
def test_executar_agente_sucesso(mock_criar_agente):
    """Valida se a função de entrada 'executar_agente' processa e retorna a resposta formatada."""
    mock_agente_executor = MagicMock()
    mock_agente_executor.invoke.return_value = {
        "output": "Olá! O produto Violão Yamaha C40 II está em estoque por R$ 899,00."
    }
    mock_criar_agente.return_value = mock_agente_executor

    pergunta = "Qual o preço do violão Yamaha?"
    resposta = executar_agente(pergunta)

    assert isinstance(resposta, str)
    assert "Violão Yamaha" in resposta
    mock_agente_executor.invoke.assert_called_once_with({"input": pergunta})


@patch("src.agent.orchestrator.criar_agente")
def test_executar_agente_fallback_erro(mock_criar_agente):
    """Valida a mensagem amigável de fallback quando o agente não retorna a chave 'output'."""
    mock_agente_executor = MagicMock()
    mock_agente_executor.invoke.return_value = {}
    mock_criar_agente.return_value = mock_agente_executor

    resposta = executar_agente("Dúvida qualquer")

    assert resposta == "Não foi possível processar a resposta."