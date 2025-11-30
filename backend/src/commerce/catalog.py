"""
DummyJSON API Integration for Product Catalog
https://dummyjson.com/docs/products
"""

import httpx
import logging
from typing import Optional

logger = logging.getLogger("commerce.catalog")

DUMMYJSON_BASE_URL = "https://dummyjson.com"

async def get_all_products(limit: int = 0) -> list[dict]:
    """Fetch products from DummyJSON API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DUMMYJSON_BASE_URL}/products",
                params={"limit": limit},
                timeout=10.0
            )
            response.raise_for_status()
            # DummyJSON returns { "products": [...], "total": 100, ... }
            data = response.json()
            products = data.get("products", [])
            logger.info(f"Fetched {len(products)} products")
            return products
    except Exception as e:
        logger.error(f"Failed to fetch products: {e}")
        return []

async def get_products_by_category(category: str, limit: int = 0) -> list[dict]:
    """Fetch products by category."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DUMMYJSON_BASE_URL}/products/category/{category}",
                params={"limit": limit},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            products = data.get("products", [])
            logger.info(f"Fetched {len(products)} products in category '{category}'")
            return products
    except Exception as e:
        logger.error(f"Failed to fetch products by category: {e}")
        return []

async def search_products(query: str, limit: int = 0) -> list[dict]:
    """Search products using DummyJSON search endpoint."""
    try:
        async with httpx.AsyncClient() as client:
            # Real search API!
            response = await client.get(
                f"{DUMMYJSON_BASE_URL}/products/search",
                params={"q": query, "limit": limit},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            products = data.get("products", [])
            logger.info(f"Found {len(products)} products matching '{query}'")
            return products
    except Exception as e:
        logger.error(f"Failed to search products: {e}")
        return []

async def get_product_by_id(product_id: int) -> Optional[dict]:
    """Fetch a single product by ID."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DUMMYJSON_BASE_URL}/products/{product_id}",
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
                f"{DUMMYJSON_BASE_URL}/products/category-list",
                timeout=10.0
            )
            response.raise_for_status()
            # Returns simple list of strings ["beauty", "fragrances", ...]
            categories = response.json()
            logger.info(f"Fetched {len(categories)} categories")
            return categories
    except Exception as e:
        logger.error(f"Failed to fetch categories: {e}")
        return []