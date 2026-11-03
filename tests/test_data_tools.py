import json
from src.tools.data_tools import buscar_produtos, consultar_status_pedido

def test_buscar_produtos_por_preco():
    """Valida se o filtro de preço máximo funciona e o JSON retornado é uma lista válida."""
    resultado = buscar_produtos.invoke({"preco_maximo": 500.0})
    dados = json.loads(resultado)
    
    assert isinstance(dados, list)
    assert len(dados) > 0
    for prod in dados:
        assert prod["preco_original_brl"] <= 500.0
        assert "preco_final_brl" in prod

def test_buscar_produtos_por_termo():
    """Valida se a busca por palavra-chave funciona no nome ou descrição."""
    resultado = buscar_produtos.invoke({"termo": "violão"})
    dados = json.loads(resultado)
    
    assert isinstance(dados, list)
    assert len(dados) > 0
    assert any("violão" in p["nome"].lower() or "violão" in p["descricao"].lower() for p in dados)

def test_buscar_produtos_sem_resultado():
    """Valida a mensagem de retorno amigável quando nenhum produto é encontrado."""
    resultado = buscar_produtos.invoke({"termo": "produto_inexistente_12345"})
    dados = json.loads(resultado)
    
    assert isinstance(dados, dict)
    assert "mensagem" in dados

def test_consultar_status_pedido_por_id():
    """Valida a busca de pedido por ID numérico."""
    resultado = consultar_status_pedido.invoke({"identificador": "1"})
    dados = json.loads(resultado)
    
    assert isinstance(dados, list)
    assert len(dados) > 0
    assert dados[0]["order_id"] == 1
    assert "itens" in dados[0]
    assert len(dados[0]["itens"]) > 0

def test_consultar_status_pedido_por_nome_cliente():
    """Valida a busca de pedido por nome do cliente."""
    resultado = consultar_status_pedido.invoke({"identificador": "Lucas"})
    dados = json.loads(resultado)
    
    assert isinstance(dados, list)
    assert len(dados) > 0
    assert "Lucas" in dados[0]["cliente"]

def test_consultar_status_pedido_inexistente():
    """Valida retorno quando o pedido ou cliente não existe."""
    resultado = consultar_status_pedido.invoke({"identificador": "999999"})
    dados = json.loads(resultado)
    
    assert isinstance(dados, dict)
    assert "mensagem" in dados