"""
CLI tool to view FreshMart orders.
Run with: uv run python -m src.data.view_orders
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent
ORDERS_FILE = DATA_DIR / "orders.json"


def format_order(order: dict) -> str:
    """Format a single order for display."""
    lines = []
    lines.append("=" * 50)
    lines.append(f"📦 Order: {order['order_id']}")
    lines.append(f"👤 Customer: {order['customer_name']}")
    lines.append(f"📅 Date: {order['timestamp'][:19].replace('T', ' ')}")
    lines.append(f"📊 Status: {order['status'].upper()}")
    lines.append("-" * 50)
    lines.append("Items:")
    
    for item in order['items']:
        lines.append(f"  • {item['quantity']}x {item['name']} @ ${item['unit_price']:.2f} = ${item['subtotal']:.2f}")
    
    lines.append("-" * 50)
    lines.append(f"💰 Total: ${order['total']:.2f}")
    lines.append("=" * 50)
    
    return "\n".join(lines)


def main():
    print("\n🛒 FreshMart Orders Viewer\n")
    
    if not ORDERS_FILE.exists():
        print("No orders found. The orders.json file doesn't exist yet.")
        print("Place an order through the voice agent to create it!")
        return
    
    with open(ORDERS_FILE, "r") as f:
        data = json.load(f)
    
    orders = data.get("orders", [])
    
    if not orders:
        print("No orders found in orders.json.")
        return
    
    print(f"Found {len(orders)} order(s):\n")
    
    for order in reversed(orders):  # Most recent first
        print(format_order(order))
        print()


if __name__ == "__main__":
    main()
