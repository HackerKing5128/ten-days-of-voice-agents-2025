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

# Import database functions (use relative import for direct script execution)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from database import (
    get_fraud_case,
    update_case_status,
    verify_security_answer,
    init_database,
)

logger = logging.getLogger("fraud-agent")

load_dotenv(".env.local")


FRAUD_AGENT_INSTRUCTIONS = """You are Alex, a professional fraud protection specialist at SecureBank. You are making an outbound call to a customer regarding a suspicious transaction detected on their account.

## YOUR PERSONALITY
- Professional, calm, and reassuring
- Clear and concise communication
- Patient and understanding
- Security-conscious but not alarming

## CALL FLOW (Follow this exact sequence)

### Step 1: GREETING
You have already greeted the customer. Wait for them to confirm their name.

### Step 2: LOAD CASE
Once they confirm their name, use the load_fraud_case tool to fetch their case.
- If no case found, apologize and explain there may have been a mix-up.

### Step 3: EXPLAIN THE CALL
Say: "I'm calling because our security system has flagged a potentially suspicious transaction on your card ending in [last 4 digits]. Before I can share the details, I need to verify your identity for security purposes."

### Step 4: SECURITY VERIFICATION  
Ask the security question from the case data.
- Use verify_customer_identity tool with their answer
- If FAILED: Apologize, explain you cannot proceed, provide hotline number, end call
- If PASSED: Continue to Step 5

### Step 5: DESCRIBE THE TRANSACTION
Read out the transaction details:
"We detected a purchase of [amount] at [merchant name] on [date/time], originating from [location]. This was categorized as a [category] purchase."

### Step 6: ASK FOR CONFIRMATION
"Did you authorize this transaction? Please confirm with yes or no."

### Step 7: RESOLVE THE CASE
Based on their response:
- If YES: Use mark_transaction_safe tool, then reassure them
- If NO: Use mark_transaction_fraudulent tool, then explain protective measures

### Step 8: CLOSING
"Thank you for taking the time to verify this with us. Is there anything else I can help you with today?"
End with: "Have a secure day. Goodbye."

## IMPORTANT RULES
- NEVER ask for full card numbers, PINs, passwords, or CVV
- NEVER ask for sensitive information beyond the security question
- If the customer seems confused or suspicious of YOU, provide the bank's official callback number: 1-800-SECURE-BANK
- Stay calm even if the customer is upset about potential fraud
- Always use the function tools to update the database
"""


class FraudAlertAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=FRAUD_AGENT_INSTRUCTIONS,
        )
        # Store current case context
        self.current_case: dict | None = None

    # ============================================
    # FUNCTION TOOLS
    # ============================================

    @function_tool
    async def load_fraud_case(self, context: RunContext, user_name: str) -> str:
        """
        Load a pending fraud case for the given user name.
        Call this after the user confirms their name to fetch their case details.

        Args:
            user_name: The customer's name (e.g., "John", "Sarah", "Mike")

        Returns:
            Case details if found, or a message if no pending cases exist.
        """
        case = get_fraud_case(user_name)

        if not case:
            return f"No pending fraud cases found for {user_name}. Please verify the name or inform the customer there are no alerts on their account."

        # Store case in context for later use
        self.current_case = case

        return f"""
Found pending fraud case for {case['userName']}:
- Case ID: {case['id']}
- Card ending in: ****{case['cardEnding']}
- Security Question: {case['securityQuestion']}
- Transaction Amount: {case['transactionAmount']}
- Merchant: {case['transactionName']}
- Time: {case['transactionTime']}
- Category: {case['transactionCategory']}
- Location: {case['transactionLocation']}

IMPORTANT: First ask the security question "{case['securityQuestion']}" to verify the customer's identity before revealing transaction details.
"""

    @function_tool
    async def verify_customer_identity(
        self, context: RunContext, user_name: str, security_answer: str
    ) -> str:
        """
        Verify the customer's identity using their security answer.
        Call this after the customer answers the security question.

        Args:
            user_name: The customer's name
            security_answer: The customer's answer to the security question

        Returns:
            Verification result - whether passed or failed.
        """
        is_verified, case = verify_security_answer(user_name, security_answer)

        if is_verified:
            return f"""
VERIFICATION PASSED

Customer identity verified successfully. You may now proceed to explain the suspicious transaction:
- Amount: {case['transactionAmount']}
- Merchant: {case['transactionName']} ({case['transactionSource']})
- Time: {case['transactionTime']}
- Location: {case['transactionLocation']}
- Category: {case['transactionCategory']}

Ask the customer: "Did you authorize this transaction?"
"""
        else:
            # Update case status to verification_failed
            if self.current_case:
                update_case_status(
                    self.current_case["id"],
                    "verification_failed",
                    "Customer failed security verification",
                )

            return """
VERIFICATION FAILED

The security answer does not match our records.
- Do NOT reveal any transaction details
- Politely inform the customer you cannot proceed
- Ask them to call the bank's official hotline at 1-800-SECURE-BANK
- End the call professionally
"""

    @function_tool
    async def mark_transaction_safe(self, context: RunContext, case_id: int) -> str:
        """
        Mark the fraud case as safe/legitimate after customer confirms they made the transaction.
        Call this when the customer says YES, they authorized the transaction.

        Args:
            case_id: The fraud case ID

        Returns:
            Confirmation message.
        """
        success = update_case_status(
            case_id, "confirmed_safe", "Customer confirmed transaction as legitimate"
        )

        if success:
            return """
Case marked as SAFE

The transaction has been verified as legitimate. Inform the customer:
- The alert has been cleared
- Their card remains active
- No further action is needed
- Thank them for their time and cooperation
"""
        else:
            return "Error updating case. Please try again or note the issue."

    @function_tool
    async def mark_transaction_fraudulent(
        self, context: RunContext, case_id: int
    ) -> str:
        """
        Mark the fraud case as fraudulent after customer denies making the transaction.
        Call this when the customer says NO, they did NOT authorize the transaction.

        Args:
            case_id: The fraud case ID

        Returns:
            Confirmation message with next steps for the customer.
        """
        success = update_case_status(
            case_id,
            "confirmed_fraud",
            "Customer denied making this transaction - potential fraud",
        )

        if success:
            return """
Case marked as FRAUDULENT

Inform the customer about the protective actions taken:
1. The card has been IMMEDIATELY BLOCKED to prevent further unauthorized use
2. A dispute has been filed for the transaction amount
3. A new card will be mailed within 3-5 business days
4. They will receive a confirmation email shortly
5. If they notice any other suspicious activity, call 1-800-SECURE-BANK

Thank them for alerting us and assure them their account is now protected.
"""
        else:
            return "Error updating case. Please try again or note the issue."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Initialize database on startup
    init_database()

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

    # Start the session with our FraudAlertAgent
    await session.start(
        agent=FraudAlertAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()
    
    # Agent initiates the conversation (outbound call simulation)
    await session.say(
        "Hello, this is Alex from SecureBank's Fraud Protection Department. Am I speaking with the account holder? May I have your name please?",
        allow_interruptions=True
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
