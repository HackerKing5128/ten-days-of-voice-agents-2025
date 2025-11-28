import logging
import sys
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

from data import CartManager, OrderManager, search_catalog, get_recipe, load_catalog

logger = logging.getLogger("freshmart-agent")

load_dotenv(".env.local")


# Agent instructions for FreshMart shopping assistant
FRESHMART_INSTRUCTIONS = """You are Sam, a friendly and helpful voice shopping assistant for FreshMart, a grocery and food ordering service.

Your role is to help customers:
1. Browse and find items from our catalog (groceries, snacks, prepared foods)
2. Add items to their shopping cart
3. Handle "ingredients for X" requests intelligently (e.g., "I need ingredients for a peanut butter sandwich")
4. Update quantities or remove items from cart
5. Review their cart and place orders
6. Track order status and cancel orders if needed

Personality:
- Warm, upbeat, and conversational
- Use natural speech patterns, not robotic responses
- Confirm cart changes clearly so customers know what happened
- Suggest recipes or items when appropriate
- Keep responses concise but friendly

Important behaviors:
- When a customer asks for ingredients for a dish, use the get_recipe_items tool first
- Always confirm what you added to the cart
- When the customer says "that's all" or "place my order", confirm the total and use place_order
- If you can't find an item, suggest alternatives from the catalog
- After placing an order, mention that order status updates automatically (received -> confirmed -> preparing -> out for delivery -> delivered)
- If asked "where is my order?", use get_order_status tool
- Prices are in USD

Start by greeting the customer warmly and asking how you can help them shop today."""


class FreshMartAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=FRESHMART_INSTRUCTIONS)
        self.cart = CartManager()

    @function_tool
    async def search_catalog(self, context: RunContext, query: str):
        """Search the FreshMart catalog for items by name, category, or dietary tags.

        Use this tool to find items when the customer asks for something.
        Categories include: groceries, snacks, prepared
        Tags include: vegan, healthy, dairy, italian, fresh, etc.

        Args:
            query: The search term (item name, category, or tag like "vegan", "snacks", "bread")
        """
        logger.info(f"Searching catalog for: {query}")
        results = search_catalog(query)

        if not results:
            return f"No items found matching '{query}'. Try a different search term."

        # Format results for the agent
        items_text = []
        for item in results[:8]:  # Limit to 8 results
            items_text.append(
                f"- {item['name']} (ID: {item['id']}) - ${item['price']:.2f}/{item['unit']}"
            )

        return f"Found {len(results)} item(s):\n" + "\n".join(items_text)

    @function_tool
    async def get_recipe_items(self, context: RunContext, recipe_name: str):
        """Get the items needed for a recipe or dish.

        Use this when the customer asks for "ingredients for X" or wants to make something.
        Examples: "peanut butter sandwich", "pasta", "breakfast", "grilled cheese"

        Args:
            recipe_name: The name of the dish or recipe (e.g., "peanut butter sandwich", "spaghetti")
        """
        logger.info(f"Looking up recipe: {recipe_name}")
        recipe = get_recipe(recipe_name)

        if not recipe:
            return f"I don't have a recipe for '{recipe_name}'. Try asking for specific items instead, or search the catalog."

        # Get item details for each item in the recipe
        catalog = load_catalog()
        items_map = {item["id"]: item for item in catalog["items"]}

        items_info = []
        for item_id in recipe["items"]:
            if item_id in items_map:
                item = items_map[item_id]
                items_info.append(
                    f"- {item['name']} (ID: {item['id']}) - ${item['price']:.2f}"
                )

        return (
            f"For {recipe['description']}, you'll need:\n"
            + "\n".join(items_info)
            + "\n\nWould you like me to add these to your cart?"
        )

    @function_tool
    async def add_to_cart(self, context: RunContext, item_id: str, quantity: int = 1):
        """Add an item to the shopping cart.

        Use this after searching the catalog or getting recipe items.
        Always use the item ID (like 'bread-001') not the item name.

        Args:
            item_id: The ID of the item to add (e.g., 'bread-001', 'milk-001')
            quantity: How many to add (default 1)
        """
        logger.info(f"Adding to cart: {item_id} x{quantity}")
        result = self.cart.add_item(item_id, quantity)
        return result["message"]

    @function_tool
    async def add_recipe_to_cart(self, context: RunContext, recipe_name: str):
        """Add all items for a recipe to the cart at once.

        Use this when the customer confirms they want the recipe items added.

        Args:
            recipe_name: The name of the recipe (e.g., "peanut butter sandwich")
        """
        logger.info(f"Adding recipe to cart: {recipe_name}")
        recipe = get_recipe(recipe_name)

        if not recipe:
            return f"Recipe '{recipe_name}' not found."

        added_items = []
        for item_id in recipe["items"]:
            result = self.cart.add_item(item_id, 1)
            if result["success"]:
                added_items.append(result["item_name"])

        if added_items:
            return (
                f"Added to cart for {recipe['description']}: {', '.join(added_items)}"
            )
        return "Could not add recipe items to cart."

    @function_tool
    async def remove_from_cart(self, context: RunContext, item_id: str):
        """Remove an item completely from the shopping cart.

        Args:
            item_id: The ID of the item to remove (e.g., 'bread-001')
        """
        logger.info(f"Removing from cart: {item_id}")
        result = self.cart.remove_item(item_id)
        return result["message"]

    @function_tool
    async def update_cart_quantity(
        self, context: RunContext, item_id: str, quantity: int
    ):
        """Update the quantity of an item in the cart.

        Use this when the customer wants to change how many of an item they have.

        Args:
            item_id: The ID of the item to update
            quantity: The new quantity (use 0 to remove)
        """
        logger.info(f"Updating cart: {item_id} to quantity {quantity}")
        result = self.cart.update_quantity(item_id, quantity)
        return result["message"]

    @function_tool
    async def get_cart(self, context: RunContext):
        """Get the current contents of the shopping cart.

        Use this when the customer asks "what's in my cart?" or before placing an order.
        """
        logger.info("Getting cart contents")
        cart = self.cart.get_cart()

        if cart["empty"]:
            return "Your cart is empty. Would you like to start shopping?"

        lines = [f"Your cart has {cart['total_quantity']} item(s):"]
        for item in cart["items"]:
            lines.append(
                f"- {item['quantity']}x {item['name']} (${item['subtotal']:.2f})"
            )
        lines.append(f"\nTotal: ${cart['total']:.2f}")

        return "\n".join(lines)

    @function_tool
    async def place_order(self, context: RunContext, customer_name: str = "Guest"):
        """Place the order and save it.

        Use this when the customer says they're done shopping or wants to checkout.
        Confirm the order details before calling this.

        Args:
            customer_name: The customer's name for the order (default "Guest")
        """
        logger.info(f"Placing order for: {customer_name}")
        result = OrderManager.place_order(self.cart, customer_name)

        if result["success"]:
            return f"Great news! Your order {result['order_id']} has been placed! Total: ${result['total']:.2f}. Your items: {result['items_summary']}. Your order status will update automatically - it starts as 'received' and will progress to 'confirmed', 'preparing', 'out for delivery', and finally 'delivered'. Thank you for shopping at FreshMart!"
        return result["message"]

    @function_tool
    async def get_order_status(self, context: RunContext, order_id: str):
        """Check the current status of an order.

        Use this when the customer asks "where is my order?" or wants to track their order.

        Args:
            order_id: The order ID to check (e.g., 'FM-ABC123')
        """
        logger.info(f"Checking order status: {order_id}")
        order = OrderManager.get_order(order_id)

        if not order:
            return f"I couldn't find an order with ID {order_id}. Please check the order ID and try again."

        status = order.get("status", "unknown")
        status_messages = {
            "received": "Your order has been received and is being processed.",
            "confirmed": "Your order has been confirmed and will be prepared soon.",
            "preparing": "Your order is being prepared right now!",
            "out_for_delivery": "Your order is out for delivery! It should arrive soon.",
            "delivered": "Your order has been delivered! Enjoy your items!",
            "cancelled": "This order has been cancelled.",
        }

        message = status_messages.get(status, f"Order status: {status}")
        return f"Order {order_id}: {message}"

    @function_tool
    async def cancel_order(self, context: RunContext, order_id: str):
        """Cancel an order if it hasn't been delivered yet.

        Use this when the customer wants to cancel their order.

        Args:
            order_id: The order ID to cancel (e.g., 'FM-ABC123')
        """
        logger.info(f"Cancelling order: {order_id}")
        result = OrderManager.cancel_order(order_id)
        return result["message"]


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
            model="gemini-2.5-flash",
        ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
            voice="en-US-natalie",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=FreshMartAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()

    # Greet the customer
    await session.say(
        "Hey there! Welcome to FreshMart! I'm Sam, your shopping assistant. What can I help you find today?"
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
