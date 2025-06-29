# database.py
import sqlite3
from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def add_category(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_all_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM categories")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_sausage(name, category_id, grade, packaging, casing, shelf_life, price, image_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sausages (name, category_id, grade, packaging, casing, shelf_life, price, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, category_id, grade, packaging, casing, shelf_life, price, image_path))
    conn.commit()
    conn.close()

def get_sausages_by_category(category_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sausages WHERE category_id = ?", (category_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_sausage_by_id(sausage_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sausages WHERE id = ?", (sausage_id,))
    row = cur.fetchone()
    conn.close()
    return row

def add_to_cart(user_id: int, sausage_id: int, quantity: int = 1):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT quantity FROM cart WHERE user_id = ? AND sausage_id = ?
    """, (user_id, sausage_id))
    row = cur.fetchone()

    if row:
        cur.execute("""
            UPDATE cart SET quantity = quantity + ? WHERE user_id = ? AND sausage_id = ?
        """, (quantity, user_id, sausage_id))
    else:
        cur.execute("""
            INSERT INTO cart (user_id, sausage_id, quantity) VALUES (?, ?, ?)
        """, (user_id, sausage_id, quantity))

    conn.commit()
    conn.close()

def get_cart(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT sausages.id, sausages.name, sausages.price, cart.quantity
        FROM cart
        JOIN sausages ON cart.sausage_id = sausages.id
        WHERE cart.user_id = ?
    """, (user_id,))
    results = cur.fetchall()
    conn.close()
    return results

def clear_cart(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def place_order(user_id: int, sausage_id: int, quantity: int, customer_info: str):
    conn = get_connection()
    cur = conn.cursor()

    # Розбий текст: очікується "телефон, відділення, коментар"
    phone = customer_info.strip()
    customer_name = "Клієнт"  # або виокремити з customer_info, якщо хочеш

    for _ in range(quantity):
        cur.execute("""
            INSERT INTO orders (sausage_id, customer_name, phone, telegram_user_id)
            VALUES (?, ?, ?, ?)
        """, (sausage_id, customer_name, phone, user_id))

    conn.commit()
    conn.close()

def get_order_history(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    print(user_id)
    cur.execute("""
        SELECT sausages.name, sausages.price, orders.created_at
        FROM orders
        JOIN sausages ON orders.sausage_id = sausages.id
        WHERE orders.telegram_user_id = ?
        ORDER BY orders.created_at DESC
    """, (user_id,))
    result = cur.fetchall()
    conn.close()
    print(result)
    return result
