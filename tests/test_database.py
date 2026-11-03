import sqlite3
from src.tools.database import init_db

def test_init_db_creates_tables():
    """Garante que todas as 6 tabelas dos CSVs foram carregadas corretamente."""
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    
    expected_tables = {
        'categories', 'customers', 'orders', 
        'order_items', 'products', 'promotions'
    }
    
    assert expected_tables.issubset(tables)

def test_init_db_has_data():
    """Verifica se dados de produtos e clientes foram efetivamente inseridos."""
    conn = init_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM products;")
    products_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM customers;")
    customers_count = cursor.fetchone()[0]
    
    assert products_count > 0
    assert customers_count > 0