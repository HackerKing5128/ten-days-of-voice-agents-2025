"""
FakeStore API Integration for Product Catalog
https://fakestoreapi.com/
"""

import httpx
import logging
from typing import Optional

logger = logging.getLogger("commerce.catalog")

FAKESTORE_BASE_URL = "https://fakestoreapi.com"


async def get_all_products(limit: int = 20) -> list[dict]:
    """Fetch all products from FakeStore API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FAKESTORE_BASE_URL}/products",
                params={"limit": limit},
                timeout=10.0
            )
            response.raise_for_status()
            products = response.json()
            logger.info(f"Fetched {len(products)} products")
            return products
    except Exception as e:
        logger.error(f"Failed to fetch products: {e}")
        return []


async def get_products_by_category(category: str, limit: int = 10) -> list[dict]:
    """Fetch products by category."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FAKESTORE_BASE_URL}/products/category/{category}",
                timeout=10.0
            )
            response.raise_for_status()
            products = response.json()[:limit]
            logger.info(f"Fetched {len(products)} products in category '{category}'")
            return products
    except Exception as e:
        logger.error(f"Failed to fetch products by category: {e}")
        return []


async def search_products(query: str, limit: int = 10) -> list[dict]:
    """Search products by title or description."""
    try:
        all_products = await get_all_products(limit=20)
        query_lower = query.lower()
        
        matches = [
            p for p in all_products
            if query_lower in p.get("title", "").lower()
            or query_lower in p.get("description", "").lower()
            or query_lower in p.get("category", "").lower()
        ]
        
        logger.info(f"Found {len(matches)} products matching '{query}'")
        return matches[:limit]
    except Exception as e:
        logger.error(f"Failed to search products: {e}")
        return []


async def get_product_by_id(product_id: int) -> Optional[dict]:
    """Fetch a single product by ID."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FAKESTORE_BASE_URL}/products/{product_id}",
                timeout=10.0
            )
            response.raise_for_status()
            product = response.json()
            logger.info(f"Fetched product: {product.get('title')}")
            return product
    except Exception as e:
        logger.error(f"Failed to fetch product {product_id}: {e}")
        return None


async def get_categories() -> list[str]:
    """Get all available product categories."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FAKESTORE_BASE_URL}/products/categories",
                timeout=10.0
            )
            response.raise_for_status()
            categories = response.json()
            logger.info(f"Fetched categories: {categories}")
            return categories
    except Exception as e:
        logger.error(f"Failed to fetch categories: {e}")
        return []