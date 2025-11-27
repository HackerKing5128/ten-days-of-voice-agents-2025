"""
Cart Manager for FreshMart Shopping Agent
Handles shopping cart operations: add, remove, update, view
"""

import json
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent


def load_catalog() -> dict:
    """Load the product catalog from JSON."""
    with open(DATA_DIR / "catalog.json", "r") as f:
        return json.load(f)


def get_item_by_id(item_id: str) -> Optional[dict]:
    """Get a catalog item by its ID."""
    catalog = load_catalog()
    for item in catalog["items"]:
        if item["id"] == item_id:
            return item
    return None


class CartManager:
    """Manages the shopping cart for a session."""
    
    def __init__(self):
        self.items: dict[str, dict] = {}  # item_id -> {item_data, quantity}
    
    def add_item(self, item_id: str, quantity: int = 1) -> dict:
        """
        Add an item to the cart.
        Returns result with success status and message.
        """
        item = get_item_by_id(item_id)
        if not item:
            return {
                "success": False,
                "message": f"Item with ID '{item_id}' not found in catalog."
            }
        
        if item_id in self.items:
            self.items[item_id]["quantity"] += quantity
        else:
            self.items[item_id] = {
                "item": item,
                "quantity": quantity
            }
        
        return {
            "success": True,
            "message": f"Added {quantity}x {item['name']} (${item['price']:.2f} each) to cart.",
            "item_name": item["name"],
            "quantity": self.items[item_id]["quantity"],
            "unit_price": item["price"]
        }
    
    def remove_item(self, item_id: str) -> dict:
        """
        Remove an item completely from the cart.
        Returns result with success status and message.
        """
        if item_id not in self.items:
            return {
                "success": False,
                "message": f"Item not found in cart."
            }
        
        item_name = self.items[item_id]["item"]["name"]
        del self.items[item_id]
        
        return {
            "success": True,
            "message": f"Removed {item_name} from cart."
        }
    
    def update_quantity(self, item_id: str, quantity: int) -> dict:
        """
        Update the quantity of an item in the cart.
        If quantity is 0 or less, removes the item.
        """
        if item_id not in self.items:
            return {
                "success": False,
                "message": f"Item not found in cart."
            }
        
        if quantity <= 0:
            return self.remove_item(item_id)
        
        item_name = self.items[item_id]["item"]["name"]
        self.items[item_id]["quantity"] = quantity
        
        return {
            "success": True,
            "message": f"Updated {item_name} quantity to {quantity}."
        }
    
    def get_cart(self) -> dict:
        """
        Get the current cart contents with total.
        """
        if not self.items:
            return {
                "empty": True,
                "message": "Your cart is empty.",
                "items": [],
                "total": 0.0
            }
        
        cart_items = []
        total = 0.0
        
        for item_id, data in self.items.items():
            item = data["item"]
            quantity = data["quantity"]
            subtotal = item["price"] * quantity
            total += subtotal
            
            cart_items.append({
                "id": item_id,
                "name": item["name"],
                "quantity": quantity,
                "unit_price": item["price"],
                "unit": item["unit"],
                "subtotal": subtotal
            })
        
        return {
            "empty": False,
            "items": cart_items,
            "item_count": len(cart_items),
            "total_quantity": sum(d["quantity"] for d in self.items.values()),
            "total": round(total, 2)
        }
    
    def clear(self):
        """Clear all items from the cart."""
        self.items = {}
    
    def get_cart_summary_text(self) -> str:
        """Get a human-readable cart summary."""
        cart = self.get_cart()
        if cart["empty"]:
            return "Your cart is empty."
        
        lines = []
        for item in cart["items"]:
            lines.append(f"- {item['quantity']}x {item['name']} @ ${item['unit_price']:.2f} = ${item['subtotal']:.2f}")
        
        lines.append(f"\nTotal: ${cart['total']:.2f}")
        return "\n".join(lines)
