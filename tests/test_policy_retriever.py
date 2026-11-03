import json
from src.rag.policy_retriever import consultar_politicas, get_policy_retriever

def test_get_policy_retriever_instanciacao():
    """Garante que o índice FAISS e o modelo de embeddings são instanciados corretamente."""
    retriever = get_policy_retriever()
    assert retriever is not None

def test_consultar_politicas_devolucao():
    """Garante que a busca semântica por devoluções retorna trechos relevantes do PDF."""
    resultado = consultar_politicas.invoke({"duvida": "Qual o prazo para devolução ou troca?"})
    dados = json.loads(resultado)

    assert isinstance(dados, dict)
    assert "trechos_encontrados" in dados
    assert len(dados["trechos_encontrados"]) > 0
    assert "trecho" in dados["trechos_encontrados"][0]
    assert "pagina" in dados["trechos_encontrados"][0]

def test_consultar_politicas_garantia():
    """Garante a recuperação de informações sobre garantia de produtos."""
    resultado = consultar_politicas.invoke({"duvida": "Como funciona a garantia dos instrumentos?"})
    dados = json.loads(resultado)

    assert isinstance(dados, dict)
    assert "trechos_encontrados" in dados
    assert len(dados["trechos_encontrados"]) > 0