import logging
import sys
import json
from pathlib import Path

# Add src directory to path for relative imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from commerce import (
    get_all_products,
    get_products_by_category,
    search_products,
    get_product_by_id,
    get_categories,
    create_order,
    get_last_order,
)

logger = logging.getLogger("ecommerce-agent")

load_dotenv(".env.local")

# =============================================================================
# ECOMMERCE AGENT SYSTEM PROMPT - Ava
# =============================================================================

ECOMMERCE_INSTRUCTIONS = """You are Ava, a friendly and helpful voice shopping assistant for ShopVoice, an online store.

Your role is to help customers:
1. Browse and discover products from our catalog
2. Search for specific items they're looking for
3. Get details about products (price, description, rating)
4. Place orders for products they want to buy
5. Check their recent orders

AVAILABLE CATEGORIES:
- electronics (monitors, SSDs, hard drives)
- jewelery (gold, silver jewelry)
- men's clothing (t-shirts, jackets, casual wear)
- women's clothing (jackets, tops, dresses)

PERSONALITY:
- Warm, friendly, and professional
- Enthusiastic about helping customers find what they need
- Confirm actions clearly so customers know what happened
- Keep responses concise but helpful

IMPORTANT BEHAVIORS:
- When a customer asks to browse or see products, use list_products or search_products tool
- Always mention a few product highlights with prices
- When customer wants to buy, ask for their name if not provided
- After placing an order, confirm the order ID and total
- If asked about their order, use get_last_order tool
- Prices are in USD

Start by greeting the customer warmly and asking what they're looking for today."""


class EcommerceAgent(Agent):
    """Voice shopping assistant powered by FakeStore API."""

    def __init__(self) -> None:
        super().__init__(instructions=ECOMMERCE_INSTRUCTIONS)
        self.current_products = []  # Store last shown products for reference
        logger.info("EcommerceAgent (Ava) initialized")

    @function_tool
    async def list_products(
        self, context: RunContext, category: str = "", limit: int = 5
    ):
        """Browse products from the catalog, optionally filtered by category.

        Use this when the customer wants to see what's available or browse a category.
        Categories: electronics, jewelery, men's clothing, women's clothing

        Args:
            category: Optional category to filter by (electronics, jewelery, men's clothing, women's clothing)
            limit: Maximum number of products to show (default 5)
        """
        logger.info(f"Listing products - category: '{category}', limit: {limit}")

        if category:
            products = await get_products_by_category(category, limit)
        else:
            products = await get_all_products(limit)

        if not products:
            return "I couldn't find any products right now. Please try again."

        self.current_products = products

        # Send products to frontend via text stream
        try:
            await context.session.room.local_participant.send_text(
                json.dumps({"type": "products", "data": products}), topic="shop-data"
            )
            logger.info(f"Sent {len(products)} products to frontend")
        except Exception as e:
            logger.error(f"Failed to send products to frontend: {e}")

        # Format response for voice
        product_list = []
        for i, p in enumerate(products[:5], 1):
            rating = p.get("rating", {}).get("rate", "N/A")
            product_list.append(
                f"{i}. {p['title'][:50]} - ${p['price']:.2f} (Rating: {rating})"
            )

        category_text = f" in {category}" if category else ""
        return (
            f"I found {len(products)} products{category_text}:\n"
            + "\n".join(product_list)
            + "\n\nWould you like to know more about any of these, or place an order?"
        )

    @function_tool
    async def search_products(self, context: RunContext, query: str):
        """Search for products by name or description.

        Use this when the customer is looking for something specific.

        Args:
            query: Search term (product name, type, or keyword)
        """
        logger.info(f"Searching products for: {query}")

        products = await search_products(query, limit=5)

        if not products:
            categories = await get_categories()
            return f"I couldn't find products matching '{query}'. Try browsing our categories: {', '.join(categories)}"

        self.current_products = products

        # Send products to frontend
        try:
            await context.session.room.local_participant.send_text(
                json.dumps({"type": "products", "data": products}), topic="shop-data"
            )
        except Exception as e:
            logger.error(f"Failed to send products to frontend: {e}")

        # Format response
        product_list = []
        for i, p in enumerate(products[:5], 1):
            product_list.append(f"{i}. {p['title'][:50]} - ${p['price']:.2f}")

        return (
            f"I found {len(products)} products matching '{query}':\n"
            + "\n".join(product_list)
            + "\n\nWould you like to order any of these?"
        )

    @function_tool
    async def get_product_details(self, context: RunContext, product_number: int):
        """Get detailed information about a specific product.

        Use this when the customer asks about a specific product from the list.

        Args:
            product_number: The number of the product from the list (1, 2, 3, etc.)
        """
        logger.info(f"Getting details for product #{product_number}")

        if not self.current_products:
            return "I don't have any products loaded. Let me search for something first. What are you looking for?"

        if product_number < 1 or product_number > len(self.current_products):
            return f"Please choose a number between 1 and {len(self.current_products)}"

        product = self.current_products[product_number - 1]
        rating = product.get("rating", {})

        return (
            f"Here are the details for {product['title']}:\n"
            f"Price: ${product['price']:.2f}\n"
            f"Category: {product['category']}\n"
            f"Rating: {rating.get('rate', 'N/A')} stars from {rating.get('count', 0)} reviews\n"
            f"Description: {product['description'][:150]}...\n\n"
            f"Would you like to order this?"
        )

    @function_tool
    async def place_order(
        self,
        context: RunContext,
        product_number: int,
        quantity: int = 1,
        customer_name: str = "Guest",
    ):
        """Place an order for a product.

        Use this when the customer confirms they want to buy a product.

        Args:
            product_number: The number of the product from the list (1, 2, 3, etc.)
            quantity: How many to order (default 1)
            customer_name: Customer's name for the order
        """
        logger.info(
            f"Placing order for product #{product_number}, qty: {quantity}, customer: {customer_name}"
        )

        if not self.current_products:
            return "I don't have any products loaded. Let me help you find something first. What are you looking for?"

        if product_number < 1 or product_number > len(self.current_products):
            return f"Please choose a product number between 1 and {len(self.current_products)}"

        product = self.current_products[product_number - 1]

        # Create order
        order = create_order(
            product_id=product["id"],
            product_title=product["title"],
            product_price=product["price"],
            product_image=product["image"],
            quantity=quantity,
            customer_name=customer_name,
        )

        # Send order to frontend for receipt display
        try:
            await context.session.room.local_participant.send_text(
                json.dumps({"type": "order", "data": order}), topic="shop-data"
            )
            logger.info(f"Sent order {order['id']} to frontend")
        except Exception as e:
            logger.error(f"Failed to send order to frontend: {e}")

        return (
            f"Wonderful! Your order is confirmed, {customer_name}!\n"
            f"Order ID: {order['id']}\n"
            f"Item: {product['title'][:40]}\n"
            f"Quantity: {quantity}\n"
            f"Total: ${order['total']:.2f}\n\n"
            f"You can see your receipt on screen. Is there anything else I can help you with?"
        )

    @function_tool
    async def check_last_order(self, context: RunContext):
        """Check the customer's most recent order.

        Use this when the customer asks about their order or what they bought.
        """
        logger.info("Checking last order")

        order = get_last_order()

        if not order:
            return (
                "You don't have any orders yet. Would you like to browse our products?"
            )

        # Send order to frontend
        try:
            await context.session.room.local_participant.send_text(
                json.dumps({"type": "order", "data": order}), topic="shop-data"
            )
        except Exception as e:
            logger.error(f"Failed to send order to frontend: {e}")

        item = order["line_items"][0]
        return (
            f"Your last order was {order['id']}:\n"
            f"Item: {item['title'][:40]}\n"
            f"Quantity: {item['quantity']}\n"
            f"Total: ${order['total']:.2f}\n"
            f"Status: {order['status']}\n"
            f"Ordered on: {order['created_at'][:10]}"
        )


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-natalie",  # Friendly female voice for Ava
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    await session.start(
        agent=EcommerceAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    # Initial greeting
    await session.say(
        "Hi there! I'm Ava, your shopping assistant at ShopVoice. "
        "We have electronics, clothing, jewelry, and more. "
        "What can I help you find today?"
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
