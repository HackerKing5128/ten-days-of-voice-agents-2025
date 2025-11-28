"""
CLI tool to view FreshMart orders and catalog from SQLite database.
Run with: uv run python -m src.data.view_orders
"""

import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent
DB_FILE = DATA_DIR / "freshmart.db"


def get_connection():
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


def view_catalog():
    """Display all catalog items."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM catalog ORDER BY category, name")
    rows = cur.fetchall()
    conn.close()
    
    print("\n" + "=" * 60)
    print("🛒 FRESHMART CATALOG")
    print("=" * 60)
    
    current_category = None
    for row in rows:
        if row["category"] != current_category:
            current_category = row["category"]
            print(f"\n📦 {current_category.upper()}")
            print("-" * 40)
        
        print(f"  {row['id']:20} | {row['name']:25} | ${row['price']:.2f}/{row['unit']}")
    
    print(f"\n📊 Total items: {len(rows)}")


def view_orders():
    """Display all orders with their items."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = cur.fetchall()
    
    print("\n" + "=" * 60)
    print("📦 FRESHMART ORDERS")
    print("=" * 60)
    
    if not orders:
        print("\n  No orders yet. Place an order through the voice agent!")
        conn.close()
        return
    
    for order in orders:
        status_emoji = {
            "received": "📥",
            "confirmed": "✅",
            "preparing": "👨‍🍳",
            "out_for_delivery": "🚚",
            "delivered": "🎉",
            "cancelled": "❌"
        }.get(order["status"], "❓")
        
        print(f"\n{'=' * 50}")
        print(f"📦 Order: {order['order_id']}")
        print(f"👤 Customer: {order['customer_name']}")
        print(f"📅 Date: {order['created_at'][:19] if order['created_at'] else 'N/A'}")
        print(f"{status_emoji} Status: {order['status'].upper()}")
        print(f"🕐 Updated: {order['updated_at'][:19] if order['updated_at'] else 'N/A'}")
        print("-" * 50)
        
        # Get order items
        cur.execute("SELECT * FROM order_items WHERE order_id = ?", (order['order_id'],))
        items = cur.fetchall()
        
        print("Items:")
        for item in items:
            print(f"  • {item['quantity']}x {item['item_name']} @ ${item['unit_price']:.2f} = ${item['subtotal']:.2f}")
        
        print("-" * 50)
        print(f"💰 Total: ${order['total']:.2f}")
    
    print(f"\n{'=' * 60}")
    print(f"📊 Total orders: {len(orders)}")
    conn.close()


def main():
    print("\n🛒 FreshMart Database Viewer\n")
    
    if not DB_FILE.exists():
        print(f"Database not found at {DB_FILE}")
        print("Start the agent first to create the database!")
        return
    
    view_catalog()
    view_orders()


if __name__ == "__main__":
    main()
