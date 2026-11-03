import json
import sqlite3
from typing import Optional
from langchain_core.tools import tool
from src.tools.database import init_db

# Instância global da conexão com o SQLite em memória populado
db_conn = init_db()

@tool
def buscar_produtos(
    termo: Optional[str] = None, 
    categoria: Optional[str] = None, 
    preco_maximo: Optional[float] = None
) -> str:
    """
    Busca produtos no catálogo da Empório da Música por nome/descrição, categoria ou preço máximo.
    Calcula automaticamente o preço final considerando promoções ativas.

    Args:
        termo: Nome do produto ou palavra-chave na descrição (ex: 'violão', 'yamaha', 'encordoamento').
        categoria: Nome da categoria de produto (ex: 'Cordas', 'Sopro', 'Acessórios').
        preco_maximo: Valor limite em Reais (BRL) para filtrar produtos de até determinado preço.
    """
    cursor = db_conn.cursor()
    query = """
        SELECT 
            p.product_id, 
            p.name, 
            c.name as category, 
            p.price_brl, 
            p.stock_quantity, 
            p.description, 
            pr.discount_percent
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1
        WHERE 1=1
    """
    params = []

    if termo:
        query += " AND (p.name LIKE ? OR p.description LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%"])
    
    if categoria:
        query += " AND c.name LIKE ?"
        params.append(f"%{categoria}%")
        
    if preco_maximo is not None:
        query += " AND p.price_brl <= ?"
        params.append(preco_maximo)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    if not rows:
        return json.dumps({"mensagem": "Nenhum produto encontrado com os critérios fornecidos."}, ensure_ascii=False)

    produtos = []
    for r in rows:
        preco_base = float(r[3])
        desconto = float(r[6]) if r[6] is not None else 0.0
        preco_final = preco_base * (1.0 - (desconto / 100.0))
        
        produtos.append({
            "id": r[0],
            "nome": r[1],
            "categoria": r[2],
            "preco_original_brl": round(preco_base, 2),
            "desconto_percent": desconto,
            "preco_final_brl": round(preco_final, 2),
            "estoque": r[4],
            "descricao": r[5]
        })

    return json.dumps(produtos, ensure_ascii=False, indent=2)


@tool
def consultar_status_pedido(identificador: str) -> str:
    """
    Consulta o status de um pedido na Empório da Música buscando pelo código/ID do pedido ou pelo nome do cliente.
    Retorna os detalhes do pedido, cliente, valor total, código de rastreio e previsão de entrega.

    Args:
        identificador: ID do pedido (ex: '1', '102') ou nome/parte do nome do cliente (ex: 'Lucas').
    """
    cursor = db_conn.cursor()
    
    query_orders = """
        SELECT 
            o.order_id, 
            c.name as customer_name, 
            c.email,
            o.order_date, 
            o.status, 
            o.total_brl, 
            o.tracking_code, 
            o.estimated_delivery
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE CAST(o.order_id AS TEXT) = ? OR c.name LIKE ?
    """
    cursor.execute(query_orders, [identificador, f"%{identificador}%"])
    pedidos_rows = cursor.fetchall()

    if not pedidos_rows:
        return json.dumps({"mensagem": f"Nenhum pedido encontrado para o identificador '{identificador}'."}, ensure_ascii=False)

    resultado = []
    for ped in pedidos_rows:
        order_id = ped[0]
        
        query_items = """
            SELECT p.name, oi.quantity, p.price_brl
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        """
        cursor.execute(query_items, [order_id])
        itens_rows = cursor.fetchall()

        itens = [
            {"produto": item[0], "quantidade": item[1], "preco_unitario_brl": item[2]}
            for item in itens_rows
        ]

        resultado.append({
            "order_id": order_id,
            "cliente": ped[1],
            "email_cliente": ped[2],
            "data_pedido": ped[3],
            "status": ped[4],
            "total_brl": ped[5],
            "codigo_rastreio": ped[6],
            "previsao_entrega": ped[7],
            "itens": itens
        })

    return json.dumps(resultado, ensure_ascii=False, indent=2)