import glob
import os
import sqlite3
import pandas as pd

DB_PATH = ":memory:"

def init_db() -> sqlite3.Connection:
    """Carrega todos os arquivos CSV da pasta data/ para um banco SQLite em memória."""
    conn = sqlite3.connect(DB_PATH)
    csv_files = glob.glob("data/*.csv")
    
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        # Sanitiza o nome da tabela (ex: 'desafio_tecnico_ai_eng - products.csv' -> 'products')
        table_name = filename.replace("desafio_tecnico_ai_eng - ", "").replace(".csv", "").strip()
        
        df = pd.read_csv(file_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        
    return conn

if __name__ == "__main__":
    connection = init_db()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tabelas carregadas com sucesso no SQLite:", [t[0] for t in tables])