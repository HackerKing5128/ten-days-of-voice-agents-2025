"""
SQLite Database for FreshMart Shopping Agent
Handles catalog, orders, and order items storage.
"""

import json
import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

DATA_DIR = Path(__file__).parent
DB_FILE = DATA_DIR / "freshmart.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database():
    """Initialize database tables."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Catalog table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS catalog (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            unit TEXT,
            tags TEXT  -- JSON array
        )
    """)
    
    # Orders table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT,
            total REAL,
            status TEXT DEFAULT 'received',
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    # Order items table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            item_id TEXT,
            item_name TEXT,
            unit_price REAL,
            quantity INTEGER,
            subtotal REAL,
            FOREIGN KEY(order_id) REFERENCES orders(order_id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()


def seed_catalog():
    """Seed the catalog from catalog.json if empty."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Check if catalog is empty
    cur.execute("SELECT COUNT(*) FROM catalog")
    if cur.fetchone()[0] > 0:
        conn.close()
        return  # Already seeded
    
    # Load from JSON
    catalog_file = DATA_DIR / "catalog.json"
    with open(catalog_file, "r") as f:
        data = json.load(f)
    
    # Insert items
    for item in data["items"]:
        cur.execute("""
            INSERT INTO catalog (id, name, category, price, unit, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            item["id"],
            item["name"],
            item["category"],
            item["price"],
            item["unit"],
            json.dumps(item.get("tags", []))
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(data['items'])} items into catalog")


def get_catalog_item(item_id: str) -> Optional[dict]:
    """Get a single catalog item by ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM catalog WHERE LOWER(id) = LOWER(?)", (item_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return None
    
    item = dict(row)
    item["tags"] = json.loads(item.get("tags") or "[]")
    return item


def search_catalog(query: str) -> list[dict]:
    """Search catalog by name, category, or tags."""
    conn = get_connection()
    cur = conn.cursor()
    
    query_lower = f"%{query.lower()}%"
    cur.execute("""
        SELECT * FROM catalog 
        WHERE LOWER(name) LIKE ? 
           OR LOWER(category) LIKE ?
           OR LOWER(tags) LIKE ?
        LIMIT 20
    """, (query_lower, query_lower, query_lower))
    
    rows = cur.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        item = dict(row)
        item["tags"] = json.loads(item.get("tags") or "[]")
        results.append(item)
    
    return results


def get_all_catalog_items() -> list[dict]:
    """Get all catalog items."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM catalog ORDER BY category, name")
    rows = cur.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        item = dict(row)
        item["tags"] = json.loads(item.get("tags") or "[]")
        results.append(item)
    
    return results


# Initialize on import
init_database()
seed_catalog()
