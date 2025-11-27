"""
Order Manager for FreshMart Shopping Agent
Handles order placement, storage, and retrieval.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from .cart_manager import CartManager

DATA_DIR = Path(__file__).parent
ORDERS_FILE = DATA_DIR / "orders.json"


def load_catalog() -> dict:
    """Load the product catalog from JSON."""
    with open(DATA_DIR / "catalog.json", "r") as f:
        return json.load(f)


def load_recipes() -> dict:
    """Load the recipes mapping from JSON."""
    with open(DATA_DIR / "recipes.json", "r") as f:
        return json.load(f)


def search_catalog(query: str) -> list[dict]:
    """
    Search the catalog by name, category, or tags.
    Returns matching items.
    """
    catalog = load_catalog()
    query_lower = query.lower().strip()
    results = []
    
    for item in catalog["items"]:
        # Check name
        if query_lower in item["name"].lower():
            results.append(item)
            continue
        # Check category
        if query_lower == item["category"].lower():
            results.append(item)
            continue
        # Check tags
        if any(query_lower in tag.lower() for tag in item.get("tags", [])):
            results.append(item)
            continue
    
    return results


def get_recipe(recipe_name: str) -> Optional[dict]:
    """
    Get a recipe by name (fuzzy match).
    Returns recipe with item IDs and description.
    """
    recipes = load_recipes()["recipes"]
    recipe_name_lower = recipe_name.lower().strip()
    
    # Exact match first
    if recipe_name_lower in recipes:
        return recipes[recipe_name_lower]
    
    # Fuzzy match - check if query is contained in recipe name
    for name, recipe in recipes.items():
        if recipe_name_lower in name or name in recipe_name_lower:
            return recipe
    
    return None


def load_orders() -> list[dict]:
    """Load all orders from the orders file."""
    if not ORDERS_FILE.exists():
        return []
    
    with open(ORDERS_FILE, "r") as f:
        data = json.load(f)
        return data.get("orders", [])


def save_orders(orders: list[dict]):
    """Save orders to the orders file."""
    with open(ORDERS_FILE, "w") as f:
        json.dump({"orders": orders}, f, indent=2, default=str)


class OrderManager:
    """Manages order placement and history."""
    
    @staticmethod
    def place_order(cart: CartManager, customer_name: str = "Guest") -> dict:
        """
        Place an order from the current cart.
        Saves to orders.json and returns order confirmation.
        """
        cart_data = cart.get_cart()
        
        if cart_data["empty"]:
            return {
                "success": False,
                "message": "Cannot place order - cart is empty."
            }
        
        # Generate order ID
        order_id = f"FM-{uuid.uuid4().hex[:6].upper()}"
        timestamp = datetime.now().isoformat()
        
        # Create order object
        order = {
            "order_id": order_id,
            "customer_name": customer_name,
            "timestamp": timestamp,
            "status": "received",
            "items": cart_data["items"],
            "total": cart_data["total"],
            "item_count": cart_data["item_count"],
            "total_quantity": cart_data["total_quantity"]
        }
        
        # Save to orders file
        orders = load_orders()
        orders.append(order)
        save_orders(orders)
        
        # Clear the cart
        cart.clear()
        
        # Build confirmation message
        items_summary = ", ".join(
            f"{item['quantity']}x {item['name']}" 
            for item in order["items"]
        )
        
        return {
            "success": True,
            "order_id": order_id,
            "total": order["total"],
            "items_summary": items_summary,
            "message": f"Order {order_id} placed successfully! Total: ${order['total']:.2f}. Items: {items_summary}"
        }
    
    @staticmethod
    def get_order(order_id: str) -> Optional[dict]:
        """Get a specific order by ID."""
        orders = load_orders()
        for order in orders:
            if order["order_id"] == order_id:
                return order
        return None
    
    @staticmethod
    def get_latest_order() -> Optional[dict]:
        """Get the most recent order."""
        orders = load_orders()
        if not orders:
            return None
        return orders[-1]
    
    @staticmethod
    def get_order_history(limit: int = 10) -> list[dict]:
        """Get recent order history."""
        orders = load_orders()
        return orders[-limit:][::-1]  # Most recent first
    
    @staticmethod
    def update_order_status(order_id: str, status: str) -> dict:
        """Update the status of an order."""
        orders = load_orders()
        for order in orders:
            if order["order_id"] == order_id:
                order["status"] = status
                order["status_updated"] = datetime.now().isoformat()
                save_orders(orders)
                return {
                    "success": True,
                    "message": f"Order {order_id} status updated to '{status}'."
                }
        
        return {
            "success": False,
            "message": f"Order {order_id} not found."
        }
