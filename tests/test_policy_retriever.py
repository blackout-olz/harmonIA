from unittest.mock import MagicMock, patch
from src.rag.policy_retriever import consultar_politicas


@patch("src.rag.policy_retriever.get_policy_retriever")
def test_consultar_politicas_sucesso(mock_get_retriever):
    """Valida se a tool de políticas retorna o texto formatado sem instanciar modelos pesados."""
    doc_mock = MagicMock()
    doc_mock.page_content = (
        "Garantia legal de 90 dias contra defeitos de fabricacao."
    )
    doc_mock.metadata = {"page": 6}

    retriever_mock = MagicMock()
    retriever_mock.invoke.return_value = [doc_mock]
    mock_get_retriever.return_value = retriever_mock

    resultado = consultar_politicas.invoke({"duvida": "garantia"})

    assert isinstance(resultado, str)
    assert "Garantia legal de 90 dias" in resultado


@patch("src.rag.policy_retriever.get_policy_retriever")
def test_consultar_politicas_sem_resultados(mock_get_retriever):
    """Valida a mensagem amigável quando nenhuma política é encontrada."""
    retriever_mock = MagicMock()
    retriever_mock.invoke.return_value = []
    mock_get_retriever.return_value = retriever_mock

    resultado = consultar_politicas.invoke({"duvida": "termo_inexistente"})

    assert (
        resultado
        == "Nenhuma informação relevante encontrada no manual de políticas."
    )