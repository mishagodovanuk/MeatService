# models.py
import sqlite3
from config import DB_PATH



def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Категорії
    cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)

    # Товари
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sausages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER,
        grade TEXT,
        packaging TEXT,
        casing TEXT,
        shelf_life TEXT,
        price REAL,
        image_path TEXT,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    """)

    # Замовлення (оновлена)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sausage_id INTEGER,
        customer_name TEXT,
        phone TEXT,
        telegram_user_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sausage_id) REFERENCES sausages(id)
    )
    """)

    # Кошик користувача
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        user_id INTEGER,
        sausage_id INTEGER,
        quantity INTEGER DEFAULT 1,
        PRIMARY KEY (user_id, sausage_id),
        FOREIGN KEY (sausage_id) REFERENCES sausages(id)
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Tables created.")
