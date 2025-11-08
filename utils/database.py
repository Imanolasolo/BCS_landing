import sqlite3

DB_NAME = "leads.db"

def get_connection(db_name=DB_NAME):
    """
    Crea y devuelve una conexión a la base de datos SQLite.
    Si la base de datos no existe, se crea automáticamente.
    """
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def init_leads_table():
    """
    Crea la tabla de leads si no existe.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            empresa TEXT,
            email TEXT,
            sector TEXT,
            mensaje TEXT
        )
    """)
    conn.commit()
    conn.close()
