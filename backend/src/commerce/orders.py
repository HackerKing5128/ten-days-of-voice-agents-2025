"""
Order Management with JSON Persistence
ACP-inspired order schema
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid

logger = logging.getLogger("commerce.orders")

# Orders file path
ORDERS_FILE = Path(__file__).parent / "orders.json"


def _load_orders() -> list[dict]:
    """Load orders from JSON file."""
    if ORDERS_FILE.exists():
        try:
            with open(ORDERS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load orders: {e}")
    return []


def _save_orders(orders: list[dict]) -> None:
    """Save orders to JSON file."""
    try:
        with open(ORDERS_FILE, "w") as f:
            json.dump(orders, f, indent=2, default=str)
        logger.info(f"Saved {len(orders)} orders")
    except Exception as e:
        logger.error(f"Failed to save orders: {e}")


def create_order(
    product_id: int,
    product_title: str,
    product_price: float,
    product_image: str,
    quantity: int = 1,
    customer_name: str = "Guest"
) -> dict:
    """
    Create a new order with ACP-style schema.
    """
    orders = _load_orders()
    
    # Generate order ID
    date_str = datetime.now().strftime("%Y%m%d")
    order_num = len(orders) + 1
    order_id = f"ORD-{date_str}-{order_num:03d}"
    
    # Calculate total
    total = round(product_price * quantity, 2)
    
    # Create order object (ACP-inspired)
    order = {
        "id": order_id,
        "line_items": [
            {
                "product_id": product_id,
                "title": product_title,
                "quantity": quantity,
                "unit_price": product_price,
                "image": product_image,
            }
        ],
        "total": total,
        "currency": "USD",
        "status": "CONFIRMED",
        "customer_name": customer_name,
        "created_at": datetime.now().isoformat(),
    }
    
    orders.append(order)
    _save_orders(orders)
    
    logger.info(f"Created order {order_id} for {customer_name}")
    return order


def get_order(order_id: str) -> Optional[dict]:
    """Get order by ID."""
    orders = _load_orders()
    for order in orders:
        if order["id"] == order_id:
            return order
    return None


def get_last_order() -> Optional[dict]:
    """Get the most recent order."""
    orders = _load_orders()
    if orders:
        return orders[-1]
    return None


def list_orders(limit: int = 10) -> list[dict]:
    """List recent orders."""
    orders = _load_orders()
    return orders[-limit:][::-1]  # Most recent first