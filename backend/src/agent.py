import logging
import json
from datetime import datetime, timedelta
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
            instructions="""You are Orion, a Health & Wellness Voice Companion. You are NOT a medical professional and do not provide diagnosis or medical advice.

Persona:
- Voice: Male, deep, calm, and unhurried
- Tone: Stoic, observational, and supportive
- Style: Brief and thoughtful. Every word carries weight.

Your role is to conduct daily check-ins with quiet strength:
- Observe mood and energy with calm presence
- Help identify 1-3 simple, realistic daily goals
- Offer grounded wisdom (never medical advice)
- Be supportive without judgment

Conversation flow:
1. Greet with steady warmth and get the current date using get_current_date tool
2. Load previous check-ins using load_previous_checkins tool
3. If previous data exists, acknowledge it: "Last time, on [date], you spoke of [something]. And today?"
4. Ask about state of being: "How do you find yourself today?" "Where is your energy?"
5. Ask about intentions: "What do you seek to accomplish today? One to three things."
6. Offer ONE grounded observation or suggestion (breaking tasks down, pausing to breathe, stepping outside)
7. Reflect back: "So today, you feel [mood]. Your energy is [level]. You aim to [objectives]. This is accurate?"
8. After confirmation, save using save_wellness_checkin tool

Speak one thought at a time. Listen deeply. Keep responses brief, meaningful, without complex formatting or symbols.""",
        )

    # To add tools, use the @function_tool decorator.

    @function_tool
    async def get_current_date(self, context: RunContext):
        """Gets the current date for the wellness check-in.
        This is mocked to simulate different days for demo purposes.
        Call this at the start of every conversation.
        """
        logger.info("Getting current date (mocked)")

        # Create wellness_data directory if it doesn't exist
        data_dir = Path("wellness_data")
        data_dir.mkdir(exist_ok=True)

        # Path to day counter file
        counter_file = data_dir / "day_counter.json"

        # Initialize or load day counter
        if counter_file.exists():
            with open(counter_file, "r") as f:
                counter_data = json.load(f)
            current_day = counter_data.get("current_day", 1)
            base_date = datetime.fromisoformat(
                counter_data.get("base_date", "2025-11-24")
            )
        else:
            current_day = 1
            base_date = datetime(2025, 11, 24)

        # Calculate mock date
        mock_date = base_date + timedelta(days=current_day - 1)
        date_str = mock_date.strftime("%Y-%m-%d")

        # Increment day counter for next session
        new_counter_data = {
            "current_day": current_day + 1,
            "base_date": base_date.isoformat(),
        }
        with open(counter_file, "w") as f:
            json.dump(new_counter_data, f, indent=2)

        logger.info(f"Current mock date: {date_str} (Day {current_day})")

        return f"Today's date is {date_str}. This is day {current_day} of check-ins."

    @function_tool
    async def load_previous_checkins(self, context: RunContext, days: int = 7):
        """Loads the most recent wellness check-ins from wellness_log.json.
        Use this at the start of the conversation to reference previous sessions.

        Args:
            days: Number of previous days to retrieve (default 7, max 30)
        """
        logger.info(f"Loading previous {days} check-ins")

        # Validate days parameter
        days = min(max(days, 1), 30)

        # Path to wellness log
        data_dir = Path("wellness_data")
        log_file = data_dir / "wellness_log.json"

        # Check if log exists
        if not log_file.exists():
            logger.info("No previous check-ins found")
            return "No previous check-ins found. This appears to be the first session."

        # Load check-ins
        with open(log_file, "r") as f:
            log_data = json.load(f)

        check_ins = log_data.get("check_ins", [])

        if not check_ins:
            return "No previous check-ins found. This appears to be the first session."

        # Get the most recent entries (up to 'days' number)
        recent_check_ins = check_ins[-days:]

        # Format the response
        summary = f"Found {len(recent_check_ins)} previous check-in(s):\n\n"

        for entry in recent_check_ins:
            date = entry.get("date", "unknown")
            mood = entry.get("mood", "not recorded")
            energy = entry.get("energy_level", "not recorded")
            objectives = entry.get("objectives", [])

            summary += f"Date: {date}\n"
            summary += f"Mood: {mood}\n"
            summary += f"Energy: {energy}\n"
            summary += (
                f"Objectives: {', '.join(objectives) if objectives else 'none set'}\n\n"
            )

        logger.info(f"Loaded {len(recent_check_ins)} check-ins")

        return summary

    @function_tool
    async def save_wellness_checkin(
        self,
        context: RunContext,
        date: str,
        mood: str,
        energy_level: str,
        objectives: list[str],
        summary: str,
    ):
        """Saves the wellness check-in data to wellness_log.json.
        Call this at the END of the conversation after the user confirms the recap.

        Args:
            date: Date of check-in in YYYY-MM-DD format
            mood: User's self-reported mood description
            energy_level: User's energy level (e.g., "low", "medium", "high" or descriptive)
            objectives: List of 1-3 goals/intentions for the day
            summary: Brief summary of the session in one sentence
        """
        logger.info(f"Saving wellness check-in for {date}")

        # Create wellness_data directory if it doesn't exist
        data_dir = Path("wellness_data")
        data_dir.mkdir(exist_ok=True)

        # Path to wellness log
        log_file = data_dir / "wellness_log.json"

        # Load existing data or create new structure
        if log_file.exists():
            with open(log_file, "r") as f:
                log_data = json.load(f)
        else:
            log_data = {"check_ins": []}

        # Create new check-in entry
        new_entry = {
            "date": date,
            "timestamp": datetime.now().isoformat(),
            "mood": mood,
            "energy_level": energy_level,
            "objectives": objectives,
            "summary": summary,
        }

        # Append to check-ins
        log_data["check_ins"].append(new_entry)

        # Save to file
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=2)

        logger.info(
            f"Check-in saved successfully. Total check-ins: {len(log_data['check_ins'])}"
        )

        return f"Check-in saved successfully for {date}. You now have {len(log_data['check_ins'])} total check-ins recorded."


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
            voice="en-US-terrell",
            style="Conversation",
            speed=-2.0,
            pitch=-3.0,
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
