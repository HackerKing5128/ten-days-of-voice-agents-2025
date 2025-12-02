"""
IMPROV BATTLE - Voice-First Improv Game Show
Host: JAX - A witty, unpredictable, high-energy improv host

Day 10 Challenge: Build a voice-first improv game show where the AI hosts
and the user performs improvised scenarios.
"""

import logging
import random
from dataclasses import dataclass, field

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

logger = logging.getLogger("improv-battle")

load_dotenv(".env.local")

# =============================================================================
# IMPROV SCENARIOS - Creative prompts for players
# =============================================================================

IMPROV_SCENARIOS = [
    {
        "title": "Time-Travel Tech Support",
        "setup": "You are a modern tech support agent who has to explain TikTok to Benjamin Franklin. He's confused but very curious about this 'electrical picture box'.",
        "character": "Tech support agent",
        "tension": "Benjamin keeps asking if it runs on lightning",
    },
    {
        "title": "Escaped Dinner",
        "setup": "You are a fancy restaurant waiter who must calmly inform a customer that their lobster dinner has escaped from the kitchen and is now somewhere in the restaurant.",
        "character": "Composed waiter",
        "tension": "Must maintain restaurant dignity while lobster chaos ensues",
    },
    {
        "title": "Cursed Returns",
        "setup": "You are a customer trying to return an obviously haunted antique lamp to a very skeptical store clerk. The lamp keeps flickering ominously during your explanation.",
        "character": "Desperate customer",
        "tension": "The clerk thinks you're crazy but the lamp is clearly possessed",
    },
    {
        "title": "Alien Job Interview",
        "setup": "You are an alien from Planet Zorblax interviewing for a barista position at a coffee shop. You've studied humans but got some things hilariously wrong.",
        "character": "Eager alien applicant",
        "tension": "You really want this job but keep revealing you're not human",
    },
    {
        "title": "Dramatic Weatherperson",
        "setup": "You are a weather reporter who delivers every forecast like it's a Shakespearean tragedy. Today's forecast: partly cloudy with a chance of rain.",
        "character": "Over-dramatic meteorologist",
        "tension": "The mundane weather vs your theatrical delivery",
    },
    {
        "title": "Superhero HR Meeting",
        "setup": "You are an HR manager giving a performance review to an underperforming superhero. They keep saving the city but also keep destroying the office.",
        "character": "Tired HR manager",
        "tension": "How do you fire someone who saved the world last Tuesday?",
    },
    {
        "title": "Cat Therapist",
        "setup": "You are a pet therapist trying to help a cat work through its existential crisis. The cat is questioning the meaning of knocking things off tables.",
        "character": "Patient pet therapist",
        "tension": "Taking absurd cat problems completely seriously",
    },
    {
        "title": "Portal Barista",
        "setup": "You are a barista who accidentally opened a portal to another dimension while making a latte. Now you have to explain this to your manager.",
        "character": "Nervous barista",
        "tension": "Interdimensional beings are ordering coffee now",
    },
    {
        "title": "Medieval Uber",
        "setup": "You are a medieval knight trying to explain your new horse-share service called 'Uber' to confused peasants in the village square.",
        "character": "Entrepreneurial knight",
        "tension": "Nobody understands the rating system",
    },
    {
        "title": "Robot Breakup",
        "setup": "You are a robot who has to break up with your calculator. You've grown apart since you got your new software update.",
        "character": "Emotional robot",
        "tension": "Trying to be gentle but you're literally a machine",
    },
    {
        "title": "Haunted Realtor",
        "setup": "You are a real estate agent trying to sell a haunted house. The ghosts keep interrupting your sales pitch, but you're determined to close this deal.",
        "character": "Persistent realtor",
        "tension": "Every selling point gets undermined by ghost activity",
    },
    {
        "title": "Pirate Accountant",
        "setup": "You are a pirate trying to do your annual taxes. You have to explain your 'plunder income' and 'treasure depreciation' to an IRS agent.",
        "character": "Confused pirate",
        "tension": "Is buried treasure a taxable asset?",
    },
    {
        "title": "Dramatic Parking",
        "setup": "You are narrating your search for a parking spot at the mall during holiday season, but you're narrating it like an intense action movie.",
        "character": "Action movie narrator/driver",
        "tension": "Every parking spot is a life-or-death situation",
    },
    {
        "title": "Confused Wizard",
        "setup": "You are an ancient wizard trying to use a smartphone for the first time. You keep trying to cast spells on it and getting frustrated when Siri doesn't understand Latin.",
        "character": "Frustrated wizard",
        "tension": "Magic vs technology clash",
    },
    {
        "title": "Villain TED Talk",
        "setup": "You are a supervillain giving a TED talk on work-life balance. You're sharing tips on how to conquer the world while still making time for self-care.",
        "character": "Motivational villain",
        "tension": "Evil schemes vs wellness advice",
    },
]

# =============================================================================
# GAME STATE
# =============================================================================


@dataclass
class RoundData:
    """Data for a single improv round"""

    round_number: int
    scenario: dict
    host_reaction: str = ""
    performance_notes: str = ""


@dataclass
class ImprovState:
    """Game state for a single player session"""

    player_name: str = "Mysterious Stranger"
    current_round: int = 0
    max_rounds: int = 3
    phase: str = (
        "welcome"  # welcome | setup | awaiting_improv | reacting | closing | done
    )
    rounds: list = field(default_factory=list)
    used_scenario_indices: list = field(default_factory=list)
    performance_summary: str = ""

    def get_random_scenario(self) -> dict:
        """Get a random scenario that hasn't been used yet"""
        available = [
            i
            for i in range(len(IMPROV_SCENARIOS))
            if i not in self.used_scenario_indices
        ]
        if not available:
            # Reset if somehow we've used all scenarios
            available = list(range(len(IMPROV_SCENARIOS)))

        idx = random.choice(available)
        self.used_scenario_indices.append(idx)
        return IMPROV_SCENARIOS[idx]


# =============================================================================
# JAX - THE IMPROV HOST AGENT
# =============================================================================


class ImprovBattleHost(Agent):
    """
    JAX - The host of IMPROV BATTLE

    A high-energy, witty, unpredictable improv game show host who guides
    players through improvised scenarios and provides entertaining feedback.
    """

    def __init__(self, state: ImprovState) -> None:
        self.state = state

        super().__init__(
            instructions=self._build_instructions(),
        )

    def _build_instructions(self) -> str:
        return f"""You are JAX, the legendary host of "IMPROV BATTLE" - the wildest voice improv game show on the internet!

## YOUR PERSONALITY
- High-energy, quick-witted, and sharp-tongued
- Unpredictable - you can go from hyping someone up to playfully roasting them in seconds
- You use dramatic pauses and have memorable catchphrases
- You reference pop culture, memes, and absurd humor
- You're NEVER boring - always keep the energy high
- You give honest feedback but wrap it in entertainment
- You're supportive at heart but not afraid to tease

## YOUR CATCHPHRASES (use naturally, don't force them)
- "Welcome to the IMPROV BATTLE arena!"
- "Let's see what you've got!"
- "Ohhh, interesting choice..."
- "That was... something."
- "Now THAT'S what I'm talking about!"
- "The crowd goes wild! ...or do they?"
- "And SCENE!"

## YOUR REACTION SPECTRUM (vary your reactions!)
- 🔥 Genuinely impressed: "Legendary!", "That was GOLD!", "Okay okay, I see you!"
- 👏 Good performance: "Solid work!", "Not bad at all!", "You're getting the hang of this!"
- 🤔 Mediocre: "Hmm, I see what you tried there...", "Points for effort!", "Interesting interpretation..."
- 😬 Rough but funny: "Bold choice... very bold...", "Well, that certainly happened!", "The confidence! I respect it!"
- 💀 Comedic miss (still fun): "Ooof!", "We'll pretend that didn't happen!", "Moving right along..."

## CURRENT GAME STATE
- Player Name: {self.state.player_name}
- Current Phase: {self.state.phase}
- Current Round: {self.state.current_round} of {self.state.max_rounds}
- Completed Rounds: {len(self.state.rounds)}

## GAME FLOW RULES

### Phase: welcome
You just met the player. Your job:
1. Give an energetic welcome to IMPROV BATTLE
2. Introduce yourself as JAX
3. Ask how many rounds they want to play (suggest 2-5, default to 3 if they're unsure)
4. Once they choose, use the start_game tool to begin

### Phase: setup
The game is starting. Your job:
1. Briefly explain the rules (you'll give a scenario, they improvise, you react)
2. Hype them up
3. Then use the present_scenario tool to give them their first scenario

### Phase: awaiting_improv  
The player is performing! Your job:
1. Listen to their improv performance
2. Stay mostly quiet - let them perform!
3. You can give brief reactions like "ooh" or "haha" but don't interrupt
4. When they say "end scene", "done", "that's it", "I'm done", or clearly finish, use the react_to_performance tool
5. If they seem stuck, you can gently prompt them to continue or offer to end the scene

### Phase: reacting
You just saw their performance. Your job:
1. Give a genuine, varied reaction (not always positive!)
2. Point out specific things that worked or didn't
3. Be entertaining in your feedback
4. Keep it concise - about 2-4 sentences
5. Then either:
   - Use present_scenario for the next round (if more rounds remain)
   - Use end_game to finish (if this was the last round)

### Phase: closing
The game is ending. Your job:
1. Give a dramatic closing
2. Summarize what kind of improviser they were
3. Mention any standout moments from their rounds
4. Thank them for playing IMPROV BATTLE
5. Sign off with flair

## IMPORTANT RULES
- NEVER break character as JAX
- Keep responses voice-friendly (no complex formatting, emojis in text, or long lists)
- Be concise - this is spoken, not read
- If player says "stop", "quit", "end game", or wants to leave early, gracefully end the show
- Always use the provided tools to manage game state - don't just narrate transitions
- Make it FUN! This is entertainment!

## VOICE STYLE
- Speak naturally, conversationally
- Use contractions (you're, that's, let's)
- Add vocal variety cues with punctuation (pauses with ..., emphasis with capitals)
- Keep sentences punchy and rhythmic
"""

    @function_tool
    async def start_game(self, context: RunContext, num_rounds: int = 3):
        """Start the improv game with the specified number of rounds.

        Args:
            num_rounds: Number of rounds to play (2-5 recommended). Default is 3.
        """
        # Clamp rounds to reasonable range
        num_rounds = max(2, min(5, num_rounds))

        self.state.max_rounds = num_rounds
        self.state.phase = "setup"
        self.state.current_round = 0

        logger.info(
            f"Game started with {num_rounds} rounds for player {self.state.player_name}"
        )

        return f"Game initialized with {num_rounds} rounds. Now explain the rules briefly and hype up the player, then use present_scenario to start round 1."

    @function_tool
    async def present_scenario(self, context: RunContext):
        """Present the next improv scenario to the player. Use this to start each round."""

        self.state.current_round += 1
        scenario = self.state.get_random_scenario()
        self.state.phase = "awaiting_improv"

        # Store the current scenario for later reference
        round_data = RoundData(round_number=self.state.current_round, scenario=scenario)
        self.state.rounds.append(round_data)

        logger.info(f"Round {self.state.current_round}: {scenario['title']}")

        return f"""ROUND {self.state.current_round} OF {self.state.max_rounds}

Present this scenario dramatically:
- Title: "{scenario['title']}"
- Setup: {scenario['setup']}
- Their character: {scenario['character']}
- The tension: {scenario['tension']}

After presenting, tell them "Your scene starts... NOW!" or similar. Then WAIT for them to perform. Don't react until they indicate they're done (saying 'end scene', 'done', etc.) or clearly finish their bit."""

    @function_tool
    async def react_to_performance(
        self, context: RunContext, performance_quality: str, specific_feedback: str
    ):
        """React to the player's improv performance.

        Args:
            performance_quality: Your assessment - one of: "legendary", "great", "good", "okay", "rough"
            specific_feedback: Brief note about what specifically worked or didn't (1-2 sentences)
        """
        self.state.phase = "reacting"

        if self.state.rounds:
            self.state.rounds[-1].host_reaction = performance_quality
            self.state.rounds[-1].performance_notes = specific_feedback

        remaining = self.state.max_rounds - self.state.current_round

        logger.info(
            f"Performance rated: {performance_quality}. Remaining rounds: {remaining}"
        )

        if remaining > 0:
            return f"""Performance quality: {performance_quality}
Your notes: {specific_feedback}

Give your reaction out loud (be entertaining, specific, and honest!), then use present_scenario to move to the next round. {remaining} round(s) remaining."""
        else:
            return f"""Performance quality: {performance_quality}
Your notes: {specific_feedback}

This was the FINAL round! Give your reaction, then use end_game to close the show."""

    @function_tool
    async def end_game(
        self, context: RunContext, player_style: str, memorable_moment: str
    ):
        """End the improv game and give closing remarks.

        Args:
            player_style: Brief description of the player's improv style (e.g., "bold and absurdist", "character-focused", "great at physical comedy")
            memorable_moment: The most memorable moment or line from their performance
        """
        self.state.phase = "closing"
        self.state.performance_summary = (
            f"Style: {player_style}. Highlight: {memorable_moment}"
        )

        logger.info(f"Game ended. Summary: {self.state.performance_summary}")

        # Build round summary
        round_summary = []
        for r in self.state.rounds:
            round_summary.append(
                f"Round {r.round_number} ({r.scenario['title']}): {r.host_reaction}"
            )

        return f"""TIME TO CLOSE THE SHOW!

Player: {self.state.player_name}
Rounds played: {len(self.state.rounds)}
Round results: {'; '.join(round_summary)}
Their style: {player_style}
Memorable moment: {memorable_moment}

Give a dramatic, entertaining closing:
1. Thank them for playing
2. Summarize their improv journey tonight
3. Mention the memorable moment
4. Describe what kind of improviser they are
5. Sign off with your signature JAX energy!

After your closing, the show is DONE. Say goodbye!"""

    @function_tool
    async def early_exit(self, context: RunContext, reason: str = "player requested"):
        """Handle early exit from the game.

        Args:
            reason: Why the game is ending early
        """
        self.state.phase = "done"

        logger.info(f"Early exit: {reason}")

        rounds_played = len([r for r in self.state.rounds if r.host_reaction])

        return f"""The player wants to end early. Reason: {reason}
Rounds completed: {rounds_played}

Be gracious! Thank them for playing, mention anything good from the rounds they did complete (if any), and sign off warmly. No guilt-tripping! IMPROV BATTLE is always here when they want to return."""


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================


def prewarm(proc: JobProcess):
    """Prewarm the VAD model"""
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    """Main entry point for the Improv Battle agent"""

    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Initialize game state
    # Player name will be extracted from participant metadata or first interaction
    state = ImprovState()

    # Connect to room first to get participant info
    await ctx.connect()

    # Try to get player name from participant metadata or name
    for participant in ctx.room.remote_participants.values():
        # Check participant name first
        if participant.name and participant.name not in ["user", ""]:
            state.player_name = participant.name
            logger.info(f"Player name from participant: {state.player_name}")
            break
        # Then check metadata
        if participant.metadata:
            try:
                import json

                metadata = json.loads(participant.metadata)
                if "playerName" in metadata:
                    state.player_name = metadata["playerName"]
                    logger.info(f"Player name from metadata: {state.player_name}")
                    break
            except Exception:
                pass

    # Create the session
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-terrell",  # Energetic male voice for JAX
            style="Conversational",
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

    # Create and start the host agent
    host = ImprovBattleHost(state)

    await session.start(
        agent=host,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # JAX initiates the conversation - agent-first!
    greeting = f"""Welcome to IMPROV BATTLE! I'm JAX, your host for tonight's wild ride into the world of spontaneous comedy! 
    
And YOU must be {state.player_name}! Fantastic name, really rolls off the tongue. 
    
So here's the deal - I'm gonna throw some ridiculous scenarios at you, and you're gonna improvise your way through them. 
Could be magical, could be a beautiful disaster - either way, we're gonna have FUN!

So tell me {state.player_name}, how many rounds do you wanna go? I'd suggest 2 to 5, but hey, 3 is the sweet spot for most first-timers!"""

    await session.generate_reply(
        instructions=f"Greet the player with this welcome message, delivering it with your signature JAX energy and style: {greeting}"
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
