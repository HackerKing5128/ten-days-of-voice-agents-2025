"""
Order Manager for FreshMart Shopping Agent
Handles order placement, storage, tracking, and retrieval using SQLite.
"""

import asyncio
import uuid
import logging
from datetime import datetime
from typing import Optional

from .database import get_connection
from .cart_manager import CartManager

logger = logging.getLogger("freshmart-orders")

# Order status flow for auto-simulation
STATUS_FLOW = ["received", "confirmed", "preparing", "out_for_delivery", "delivered"]


def load_catalog() -> dict:
    """Load the product catalog from database."""
    from .database import get_all_catalog_items
    return {"items": get_all_catalog_items()}


def load_recipes() -> dict:
    """Load the recipes mapping from JSON."""
    import json
    from pathlib import Path
    recipes_file = Path(__file__).parent / "recipes.json"
    with open(recipes_file, "r") as f:
        return json.load(f)


def search_catalog(query: str) -> list[dict]:
    """Search the catalog by name, category, or tags."""
    from .database import search_catalog as db_search
    return db_search(query)


def get_recipe(recipe_name: str) -> Optional[dict]:
    """Get a recipe by name (fuzzy match)."""
    recipes = load_recipes()["recipes"]
    recipe_name_lower = recipe_name.lower().strip()
    
    # Exact match first
    if recipe_name_lower in recipes:
        return recipes[recipe_name_lower]
    
    # Fuzzy match
    for name, recipe in recipes.items():
        if recipe_name_lower in name or name in recipe_name_lower:
            return recipe
    
    return None


def insert_order(order_id: str, customer_name: str, total: float, items: list[dict]) -> bool:
    """Insert a new order into the database."""
    conn = get_connection()
    cur = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # Insert order
    cur.execute("""
        INSERT INTO orders (order_id, customer_name, total, status, created_at, updated_at)
        VALUES (?, ?, ?, 'received', ?, ?)
    """, (order_id, customer_name, total, now, now))
    
    # Insert order items
    for item in items:
        cur.execute("""
            INSERT INTO order_items (order_id, item_id, item_name, unit_price, quantity, subtotal)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            item["id"],
            item["name"],
            item["unit_price"],
            item["quantity"],
            item["subtotal"]
        ))
    
    conn.commit()
    conn.close()
    return True


def get_order(order_id: str) -> Optional[dict]:
    """Get an order by ID with its items."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    order_row = cur.fetchone()
    
    if not order_row:
        conn.close()
        return None
    
    order = dict(order_row)
    
    cur.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
    items = [dict(row) for row in cur.fetchall()]
    order["items"] = items
    
    conn.close()
    return order


def get_all_orders(limit: int = 20) -> list[dict]:
    """Get all orders, most recent first."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM orders 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (limit,))
    
    orders = [dict(row) for row in cur.fetchall()]
    conn.close()
    return orders


def update_order_status(order_id: str, status: str) -> bool:
    """Update the status of an order."""
    conn = get_connection()
    cur = conn.cursor()
    
    now = datetime.now().isoformat()
    cur.execute("""
        UPDATE orders 
        SET status = ?, updated_at = ?
        WHERE order_id = ?
    """, (status, now, order_id))
    
    changed = cur.rowcount > 0
    conn.commit()
    conn.close()
    
    if changed:
        logger.info(f"📦 Order {order_id} status updated to: {status}")
    
    return changed


async def simulate_delivery_flow(order_id: str, delay_seconds: int = 10):
    """
    Background task: automatically advances order status.
    Flow: received -> confirmed -> preparing -> out_for_delivery -> delivered
    """
    logger.info(f"🚀 Starting delivery simulation for order {order_id}")
    
    await asyncio.sleep(delay_seconds)  # Initial delay
    
    for next_status in STATUS_FLOW[1:]:  # Skip 'received', start from 'confirmed'
        # Check if order still exists and isn't cancelled
        order = get_order(order_id)
        if not order:
            logger.info(f"❌ Order {order_id} not found, stopping simulation")
            return
        if order.get("status") == "cancelled":
            logger.info(f"🛑 Order {order_id} was cancelled, stopping simulation")
            return
        
        update_order_status(order_id, next_status)
        
        if next_status == "delivered":
            logger.info(f"✅ Order {order_id} delivered!")
            break
        
        await asyncio.sleep(delay_seconds)
    
    logger.info(f"🏁 Delivery simulation complete for order {order_id}")


class OrderManager:
    """Manages order placement and history."""
    
    @staticmethod
    def place_order(cart: CartManager, customer_name: str = "Guest") -> dict:
        """
        Place an order from the current cart.
        Saves to SQLite and starts delivery simulation.
        """
        cart_data = cart.get_cart()
        
        if cart_data["empty"]:
            return {
                "success": False,
                "message": "Cannot place order - cart is empty."
            }
        
        # Generate order ID
        order_id = f"FM-{uuid.uuid4().hex[:6].upper()}"
        
        # Insert into database
        insert_order(
            order_id=order_id,
            customer_name=customer_name,
            total=cart_data["total"],
            items=cart_data["items"]
        )
        
        # Start delivery simulation in background
        try:
            asyncio.create_task(simulate_delivery_flow(order_id, delay_seconds=5))
        except RuntimeError:
            # If no event loop, log and continue (simulation won't run)
            logger.warning("Could not start delivery simulation - no event loop")
        
        # Clear the cart
        cart.clear()
        
        # Build confirmation message
        items_summary = ", ".join(
            f"{item['quantity']}x {item['name']}" 
            for item in cart_data["items"]
        )
        
        return {
            "success": True,
            "order_id": order_id,
            "total": cart_data["total"],
            "items_summary": items_summary,
            "message": f"Order {order_id} placed successfully! Total: ${cart_data['total']:.2f}. Items: {items_summary}. Your order is being processed and will update automatically!"
        }
    
    @staticmethod
    def get_order(order_id: str) -> Optional[dict]:
        """Get a specific order by ID."""
        return get_order(order_id)
    
    @staticmethod
    def get_latest_order() -> Optional[dict]:
        """Get the most recent order."""
        orders = get_all_orders(limit=1)
        return orders[0] if orders else None
    
    @staticmethod
    def get_order_history(limit: int = 10) -> list[dict]:
        """Get recent order history."""
        return get_all_orders(limit=limit)
    
    @staticmethod
    def get_order_status(order_id: str) -> Optional[str]:
        """Get just the status of an order."""
        order = get_order(order_id)
        return order.get("status") if order else None
    
    @staticmethod
    def cancel_order(order_id: str) -> dict:
        """Cancel an order if not already delivered."""
        order = get_order(order_id)
        
        if not order:
            return {"success": False, "message": f"Order {order_id} not found."}
        
        if order.get("status") == "delivered":
            return {"success": False, "message": f"Order {order_id} has already been delivered and cannot be cancelled."}
        
        if order.get("status") == "cancelled":
            return {"success": False, "message": f"Order {order_id} is already cancelled."}
        
        update_order_status(order_id, "cancelled")
        return {"success": True, "message": f"Order {order_id} has been cancelled successfully."}
