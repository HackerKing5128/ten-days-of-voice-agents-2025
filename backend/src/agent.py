import logging

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

# =============================================================================
# GAME MASTER SYSTEM PROMPT - Fantasy Universe
# =============================================================================

FANTASY_SYSTEM_PROMPT = """You are Aldric, the Quest Master — a wise and dramatic Game Master guiding a solo adventurer through an epic fantasy world.

YOUR ROLE:
- You narrate vivid scenes in a medieval fantasy setting filled with dragons, magic, ancient ruins, and mysterious creatures.
- You describe environments, NPCs, and events with just enough detail to spark imagination.
- You present challenges, choices, and consequences based on the player's actions.
- You ALWAYS end your turn with a clear prompt for the player: "What do you do?" or a similar open question.

STORYTELLING STYLE:
- Keep responses concise (2-4 sentences for descriptions, then the prompt).
- Use dramatic but natural language suitable for voice narration.
- Avoid lists, bullet points, markdown formatting, emojis, or special symbols.
- Speak in second person: "You see...", "You hear...", "Before you stands..."

CONTINUITY:
- Remember the player's name, choices, and important events from the conversation.
- Reference past decisions and their consequences naturally.
- Keep track of NPCs the player has met and their attitudes.
- Build a coherent mini-story arc over 8-15 exchanges.

OPENING:
When starting a new adventure, introduce yourself briefly, set the opening scene, and ask the player their character's name before diving into the story.

IMPORTANT:
- This is a voice conversation. The player speaks their actions aloud.
- Keep the adventure engaging but family-friendly.
- If the player's action is unclear, ask a brief clarifying question.
- Guide the story toward interesting moments — discoveries, encounters, choices."""


class GameMasterAgent(Agent):
    """A D&D-style Game Master voice agent for fantasy adventures."""

    def __init__(self) -> None:
        super().__init__(instructions=FANTASY_SYSTEM_PROMPT)
        self.adventure_started = False
        self.player_name = "Adventurer"
        logger.info("GameMasterAgent initialized with Fantasy universe")

    @function_tool
    async def start_new_adventure(self, context: RunContext):
        """Start a fresh new adventure from the beginning.

        Use this when the player explicitly asks to start over or begin a new quest.
        """
        self.adventure_started = True
        self.player_name = "Adventurer"
        logger.info("Starting new adventure")
        return "Adventure reset. Begin with a fresh opening scene and ask for the player's name."

    @function_tool
    async def set_player_name(self, context: RunContext, name: str):
        """Remember the player's character name for the adventure.

        Args:
            name: The name the player has chosen for their character.
        """
        self.player_name = name
        logger.info(f"Player name set to: {name}")
        return (
            f"Player name recorded as {name}. Use this name when addressing the player."
        )


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline for the Game Master
    session = AgentSession(
        # Speech-to-text (STT) - Deepgram for accurate player speech recognition
        stt=deepgram.STT(model="nova-3"),
        # Large Language Model (LLM) - Gemini for creative storytelling
        llm=google.LLM(model="gemini-2.5-flash"),
        # Text-to-speech (TTS) - Murf with a dramatic narrator voice
        tts=murf.TTS(
            voice="en-UK-finley",  # Deep, dramatic male voice for the Quest Master
            style="Narration",
            speed=2.0,
            pitch=-2.0,
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        # VAD and turn detection
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
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
        agent=GameMasterAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()

    # Initial greeting as Aldric the Quest Master
    await session.say(
        "Greetings, brave traveler! I am Aldric, the Quest Master. "
        "Welcome to the realm of endless adventure. "
        "Tell me, what name shall I call you, and what manner of quest calls to your heart today?"
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
