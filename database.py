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
