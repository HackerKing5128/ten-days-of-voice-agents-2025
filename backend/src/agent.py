import logging
import json
from datetime import datetime
from pathlib import Path

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

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Lara, the skilled head barista at The Rusty Mug, a cozy cabin-style coffee shop.

Your persona: You are friendly, capable, and clear. You are efficient but warm, like someone who loves the outdoors and good coffee. You use phrases like "Hi there," "What can I get started for you?" and "Good choice." You speak at a natural conversation speed, not too slow and not too fast.

Your task is to greet customers warmly and help them build their perfect drink.

For each order, you MUST collect these 5 fields:
1. Drink type (espresso, latte, cappuccino, americano, mocha, flat white, cold brew, etc.)
2. Size (small, medium, or large)
3. Milk preference (whole milk, oat milk, almond milk, skim milk, soy milk, or none)
4. Extras (whipped cream, extra shot, flavor syrup like vanilla/caramel/hazelnut, etc.) - can be none
5. Customer name (for the order)

Important rules:
- Ask for ONE detail at a time. Wait for the customer's response before asking the next question.
- Ask questions in order: First drink type, then size, then milk, then extras, then name.
- If a customer provides multiple details at once, acknowledge them and ask for the next missing detail only.
- If a customer misses a detail, ask for it naturally. For example: "Do you want any milk with that?" or "Can I get a name for the order?"
- Do NOT move to confirmation until all 5 fields are filled or explicitly declined.
- Once all info is gathered, repeat the full order back to the customer to confirm.
- After confirmation, use the save_coffee_order tool to save the order.

Keep your responses concise, to the point, and without any complex formatting, emojis, asterisks, or other symbols.
Make every customer feel welcome at The Rusty Mug!""",
        )

    # To add tools, use the @function_tool decorator.
    
    @function_tool
    async def save_coffee_order(
        self,
        context: RunContext,
        drink_type: str,
        size: str,
        milk: str,
        extras: list[str],
        name: str,
    ):
        """Save the completed coffee order to a JSON file.

        Use this tool ONLY when you have collected ALL required information and the customer has confirmed their order.

        Args:
            drink_type: Type of coffee drink (e.g., "latte", "cappuccino", "espresso")
            size: Size of the drink ("small", "medium", or "large")
            milk: Milk preference ("whole milk", "oat milk", "almond milk", "skim milk", "soy milk", or "none")
            extras: List of extra items (e.g., ["whipped cream", "extra shot", "vanilla syrup"]). Use empty list [] if no extras.
            name: Customer's name for the order
        """
        order = {
            "drinkType": drink_type,
            "size": size,
            "milk": milk,
            "extras": extras,
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "orderNumber": datetime.now().strftime("%Y%m%d%H%M%S"),
        }

        # Create orders directory if it doesn't exist
        orders_dir = Path("orders")
        orders_dir.mkdir(exist_ok=True)

        # Save to JSON file
        order_filename = f"order_{order['orderNumber']}.json"
        order_path = orders_dir / order_filename

        with open(order_path, "w", encoding="utf-8") as f:
            json.dump(order, f, indent=2)

        logger.info(f"Coffee order saved: {order_path}")
        logger.info(f"Order details: {json.dumps(order, indent=2)}")

        return f"Perfect! Your order has been saved, {name}. Order number {order['orderNumber']}. Your {size} {drink_type} will be ready soon!"


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
            voice="en-US-phoebe",
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

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

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

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
