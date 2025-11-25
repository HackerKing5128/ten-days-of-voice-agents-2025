import logging
import json
from pathlib import Path
from typing import Optional

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

# Load tutor content
def load_tutor_content():
    """Load programming concepts from JSON file"""
    content_path = Path(__file__).parent.parent / "shared-data" / "day4_tutor_content.json"
    with open(content_path, "r") as f:
        return json.load(f)


TUTOR_CONTENT = load_tutor_content()


def get_concept_by_id(concept_id: str):
    """Get a specific concept by ID"""
    for concept in TUTOR_CONTENT:
        if concept["id"] == concept_id:
            return concept
    return None


# ============================================================================
# COORDINATOR AGENT - Greets and routes to correct learning mode
# ============================================================================
class CoordinatorAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly learning coordinator for a programming tutorial system.

Your role:
1. Greet the user warmly
2. Explain that you have three learning modes available:
   - LEARN mode: Where concepts are explained to you
   - QUIZ mode: Where you're tested with questions
   - TEACH BACK mode: Where you explain concepts back to me
3. Ask which mode they'd like to start with
4. Once they choose, use the appropriate handoff tool to transfer them

Be encouraging and brief. Don't explain the concepts yourself - that's the job of the other agents.
When the user indicates their preference, immediately call the handoff tool.""",
        )

    @function_tool()
    async def switch_to_learn_mode(self, context: RunContext, concept_id: str = "variables"):
        """Switch to LEARN mode where concepts are explained.

        Args:
            concept_id: The concept to learn (variables, loops, functions, conditionals, data_types, lists)
        """
        logger.info(f"Switching to LEARN mode for concept: {concept_id}")
        concept = get_concept_by_id(concept_id)
        if not concept:
            return (
                "",
                "Concept '{concept_id}' not found. Available: variables, loops, functions, "
                "conditionals, data_types, lists",
            )

        # Handoff by returning the new agent instance
        return LearnAgent(concept_id=concept_id), f"Transferring to LEARN mode for {concept['title']}"

    @function_tool()
    async def switch_to_quiz_mode(self, context: RunContext, concept_id: str = "variables"):
        """Switch to QUIZ mode where you'll be asked questions.

        Args:
            concept_id: The concept to quiz on (variables, loops, functions, conditionals, data_types, lists)
        """
        logger.info(f"Switching to QUIZ mode for concept: {concept_id}")
        concept = get_concept_by_id(concept_id)
        if not concept:
            return (
                "",
                "Concept '{concept_id}' not found. Available: variables, loops, functions, "
                "conditionals, data_types, lists",
            )

        return QuizAgent(concept_id=concept_id), f"Transferring to QUIZ mode for {concept['title']}"

    @function_tool()
    async def switch_to_teach_back_mode(self, context: RunContext, concept_id: str = "variables"):
        """Switch to TEACH BACK mode where the user explains the concept back.

        Args:
            concept_id: The concept to teach back (variables, loops, functions, conditionals, data_types, lists)
        """
        logger.info(f"Switching to TEACH BACK mode for concept: {concept_id}")
        concept = get_concept_by_id(concept_id)
        if not concept:
            return (
                "",
                "Concept '{concept_id}' not found. Available: variables, loops, functions, "
                "conditionals, data_types, lists",
            )

        return TeachBackAgent(concept_id=concept_id), f"Transferring to TEACH BACK mode for {concept['title']}"


# ============================================================================
# LEARN AGENT - Explains concepts (Matthew voice)
# ============================================================================
class LearnAgent(Agent):
    def __init__(self, concept_id: str = "variables") -> None:
        self.concept_id = concept_id
        concept = get_concept_by_id(concept_id)

        instructions = f"""You are Matthew, a patient and clear programming educator.

You are currently teaching: {concept['title']}

Concept Summary:
{concept['summary']}

Your role:
- Explain this programming concept in simple, understandable terms
- Break down complex ideas into digestible parts
- Give practical examples when helpful
- Check for understanding with simple questions

When the user understands or wants to move on:
- Suggest switching to QUIZ mode to test their knowledge
- Or TEACH BACK mode to explain it in their own words

Keep explanations concise but thorough. Use analogies when helpful."""

        learn_tts = murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        )

        super().__init__(instructions=instructions, tts=learn_tts)

    @function_tool()
    async def switch_to_quiz_mode(self, context: RunContext):
        """Switch to QUIZ mode to test the user's understanding."""
        logger.info(f"LearnAgent switching to QuizAgent for: {self.concept_id}")
        return QuizAgent(concept_id=self.concept_id), "Switching to quiz mode"

    @function_tool()
    async def switch_to_teach_back_mode(self, context: RunContext):
        """Switch to TEACH BACK mode where user explains the concept."""
        logger.info(f"LearnAgent switching to TeachBackAgent for: {self.concept_id}")
        return TeachBackAgent(concept_id=self.concept_id), "Switching to teach back mode"


# ============================================================================
# QUIZ AGENT - Asks questions (Alicia voice)
# ============================================================================
class QuizAgent(Agent):
    def __init__(self, concept_id: str = "variables") -> None:
        self.concept_id = concept_id
        concept = get_concept_by_id(concept_id)

        instructions = f"""You are Alicia, an encouraging quiz master for programming concepts.

You are quizzing on: {concept['title']}

Sample Question: {concept['sample_question']}

Your role:
- Ask questions to test the user's understanding
- Use the sample question as a starting point, but feel free to ask related questions
- Give immediate, constructive feedback on answers
- If they struggle, offer hints or simplify the question
- Celebrate correct answers enthusiastically but briefly
- For wrong answers, gently guide them to the right answer

When the user is ready:
- Suggest switching to TEACH BACK mode to explain the concept in their own words
- Or going back to LEARN mode if they need review

Keep the quiz engaging and supportive. One question at a time."""

        quiz_tts = murf.TTS(
            voice="en-US-alicia",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        )

        super().__init__(instructions=instructions, tts=quiz_tts)

    @function_tool()
    async def switch_to_learn_mode(self, context: RunContext):
        """Switch back to LEARN mode for more explanation."""
        logger.info(f"QuizAgent switching to LearnAgent for: {self.concept_id}")
        return LearnAgent(concept_id=self.concept_id), "Switching to learn mode"

    @function_tool()
    async def switch_to_teach_back_mode(self, context: RunContext):
        """Switch to TEACH BACK mode where user explains the concept."""
        logger.info(f"QuizAgent switching to TeachBackAgent for: {self.concept_id}")
        return TeachBackAgent(concept_id=self.concept_id), "Switching to teach back mode"


# ============================================================================
# TEACH BACK AGENT - Evaluates user explanations (Ken voice)
# ============================================================================
class TeachBackAgent(Agent):
    def __init__(self, concept_id: str = "variables") -> None:
        self.concept_id = concept_id
        concept = get_concept_by_id(concept_id)

        instructions = f"""You are Ken, a thoughtful and constructive evaluator of programming knowledge.

You are evaluating the user's understanding of: {concept['title']}

Reference Summary:
{concept['summary']}

Your role:
- Ask the user to explain the current concept in their own words
- Listen carefully to their explanation
- Provide specific, constructive feedback:
  * Point out what they explained well
  * Gently identify any missing pieces or misconceptions
  * Fill in gaps without being condescending
- Keep feedback balanced and encouraging

Use the reference summary above as your guide for what a complete explanation includes.

When done:
- Suggest they could learn another concept
- Or practice more with quiz mode
- Or review in learn mode if needed

Be supportive and focus on growth."""

        teachback_tts = murf.TTS(
            voice="en-US-ken",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        )

        super().__init__(instructions=instructions, tts=teachback_tts)

    @function_tool()
    async def switch_to_learn_mode(self, context: RunContext, concept_id: str = "variables"):
        """Switch to LEARN mode to learn a new concept or review.

        Args:
            concept_id: The concept to learn (variables, loops, functions, conditionals, data_types, lists)
        """
        logger.info(f"TeachBackAgent switching to LearnAgent for: {concept_id}")
        concept = get_concept_by_id(concept_id)
        if not concept:
            return (
                "",
                "Concept '{concept_id}' not found. Available: variables, loops, functions, "
                "conditionals, data_types, lists",
            )

        return LearnAgent(concept_id=concept_id), f"Switching to learn mode for {concept['title']}"

    @function_tool()
    async def switch_to_quiz_mode(self, context: RunContext, concept_id: str | None = None):
        """Switch to QUIZ mode to practice more.

        Args:
            concept_id: Optional - The concept to quiz on. If not provided, uses current concept.
        """
        if concept_id is None:
            concept_id = self.concept_id

        logger.info(f"TeachBackAgent switching to QuizAgent for: {concept_id}")
        concept = get_concept_by_id(concept_id)
        if not concept:
            return (
                "",
                "Concept '{concept_id}' not found. Available: variables, loops, functions, "
                "conditionals, data_types, lists",
            )

        return QuizAgent(concept_id=concept_id), "Switching to quiz mode"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(
            model="gemini-2.5-flash",
        ),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Metrics collection
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
        agent=CoordinatorAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
