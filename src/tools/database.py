import glob
import os
import sqlite3
from pathlib import Path
import pandas as pd

# Caminho absoluto para a pasta data/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

_db_connection: sqlite3.Connection | None = None

def init_db() -> sqlite3.Connection:
    """
    Carrega todos os arquivos CSV da pasta data/ para um banco SQLite em memória.
    Utiliza check_same_thread=False para permitir uso seguro em aplicações multi-thread (ex: Streamlit).
    """
    global _db_connection
    if _db_connection is not None:
        return _db_connection

    # check_same_thread=False resolve o erro de acesso em threads do Streamlit
    conn = sqlite3.connect(":memory:", check_same_thread=False)

    # Localiza arquivos CSV
    csv_files = list(DATA_DIR.glob("*.csv"))
    if not csv_files:
        csv_files = [Path(p) for p in glob.glob("data/*.csv")]

    for file_path in csv_files:
        filename = file_path.name
        # Sanitiza o nome da tabela (ex: 'desafio_tecnico_ai_eng - products.csv' -> 'products')
        table_name = filename.replace("desafio_tecnico_ai_eng - ", "").replace(".csv", "").strip()

        df = pd.read_csv(file_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    _db_connection = conn
    return _db_connection


if __name__ == "__main__":
    connection = init_db()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tabelas carregadas com sucesso no SQLite:", [t[0] for t in tables])