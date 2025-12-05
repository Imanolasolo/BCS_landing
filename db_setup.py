# db_setup.py
import sqlite3
from pathlib import Path

DB_PATH = Path("partners.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        email TEXT,
        telefono TEXT,
        sector TEXT,
        mensaje TEXT,
        source TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        partner_name TEXT,
        contact_email TEXT,
        company TEXT,
        region TEXT,
        sectors TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()
    print(f"DB inicializada en {DB_PATH.resolve()}")

if __name__ == "__main__":
    init_db()
