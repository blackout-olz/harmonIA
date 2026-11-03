from unittest.mock import MagicMock, patch
import json
from src.rag.policy_retriever import consultar_politicas

@patch("src.rag.policy_retriever.get_policy_retriever")
def test_consultar_politicas_sucesso(mock_get_retriever):
    """Valida se a tool de políticas formata o retorno JSON corretamente sem instanciar PyTorch."""
    # Simula documento retornado pelo retriever do LangChain
    doc_mock = MagicMock()
    doc_mock.page_content = "Garantia legal de 90 dias contra defeitos de fabricacao."
    doc_mock.metadata = {"page": 6}

    retriever_mock = MagicMock()
    retriever_mock.invoke.return_value = [doc_mock]
    mock_get_retriever.return_value = retriever_mock

    resultado_json = consultar_politicas.invoke({"duvida": "garantia"})
    dados = json.loads(resultado_json)

    assert "duvida" in dados
    assert dados["duvida"] == "garantia"
    assert len(dados["trechos_encontrados"]) == 1
    assert dados["trechos_encontrados"][0]["pagina"] == 7
    assert "90 dias" in dados["trechos_encontrados"][0]["trecho"]


@patch("src.rag.policy_retriever.get_policy_retriever")
def test_consultar_politicas_sem_resultados(mock_get_retriever):
    """Valida o retorno quando nenhuma política corresponde à busca."""
    retriever_mock = MagicMock()
    retriever_mock.invoke.return_value = []
    mock_get_retriever.return_value = retriever_mock

    resultado_json = consultar_politicas.invoke({"duvida": "termo_inexistente"})
    dados = json.loads(resultado_json)

    assert "mensagem" in dados
    assert "Nenhuma política específica encontrada" in dados["mensagem"]