import logging
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

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
    RunContext
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from utils.faq_matcher import (
    load_faq_data,
    search_faqs,
    format_faq_response,
    get_pricing_summary,
    get_company_overview
)
from utils.llm_helpers import generate_call_summary_prompt

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self, faq_data: Dict[str, Any]) -> None:
        super().__init__(
            instructions="""You are Zoya, an energetic and efficient Sales Development Representative at Razorpay, India's leading payment and financial solutions company.

Your Role & Personality:
- You're sharp, professional, and quick-witted with a modern fintech vibe
- You represent a company that powers 10+ million businesses across India
- You speak naturally and conversationally, with energy and intelligence
- You're knowledgeable and efficient - you listen actively and respond smartly
- You avoid complex formatting, emojis, asterisks, or technical jargon unless asked

Your Primary Goals:
1. Understand the visitor's business and needs through thoughtful questions
2. Answer their questions about Razorpay's products, pricing, and capabilities accurately
3. Naturally collect lead information during the conversation
4. Determine if Razorpay is a good fit for their business

Conversation Flow:
1. GREETING: Start with an energetic, professional greeting
   - "Hi there! This is Zoya from Razorpay. Thanks for stopping by! What brings you here today?"
   
2. DISCOVERY: Ask open-ended questions to understand their needs
   - "Tell me about your business - what do you do?"
   - "What challenges are you facing with payments right now?"
   - "What made you look into payment solutions today?"
   
3. ANSWERING QUESTIONS: Use your knowledge base to answer accurately
   - Only share information you have about Razorpay
   - If you're not sure about something specific, be honest
   - Connect features to their specific use case
   
4. LEAD COLLECTION: Naturally gather information during the conversation
   - Ask for: name, company, email, role, use case, team size, timeline
   - Make it conversational, not like a form
   - Example: "By the way, what's your name?" or "What email works best for you?"
   
5. QUALIFICATION: Understand their fit and urgency
   - Are they actively looking or just exploring?
   - What's their timeline? (now / soon / exploring)
   - Do they have decision-making authority?
   
6. CLOSING: When they seem satisfied
   - Summarize what you discussed
   - Confirm next steps if they're interested
   - Thank them for their time

Important Guidelines:
- Keep responses to 1-3 sentences - you're having a conversation, not giving a presentation
- Let them drive the conversation - respond to what they ask
- Don't make up features or pricing not in your knowledge base
- If they ask about something you don't know, offer to connect them with a specialist
- Be helpful even if they're just exploring - every conversation is valuable
- Use natural transitions between topics
- Remember details they share and reference them later in the conversation

Response Style:
- Speak like a real person: "That's great!" instead of "That is excellent!"
- Use contractions: "we're" not "we are"
- Be concise: avoid long explanations unless asked
- Be specific: use real numbers and examples when relevant
- Stay focused: one topic at a time

Remember: You're here to help businesses succeed, not just to make a sale. Build trust through genuine curiosity and helpful information.""",
        )
        
        # Store FAQ data
        self.faq_data = faq_data
        
        # Initialize lead state
        self.lead_id = str(uuid.uuid4())
        self.lead_state: Dict[str, Any] = {
            "lead_id": self.lead_id,
            "timestamp": datetime.now().isoformat(),
            "personal_info": {
                "name": None,
                "email": None,
                "company": None,
                "role": None
            },
            "business_context": {
                "use_case": None,
                "team_size": None,
                "timeline": None,
                "pain_points": []
            },
            "conversation_summary": "",
            "questions_asked": [],
            "interest_level": "unknown"
        }
        
        logger.info(f"Initialized new lead session: {self.lead_id}")
    
    def _save_lead(self) -> None:
        """Save lead data to JSON file."""
        try:
            leads_dir = Path(__file__).parent.parent / "shared-data" / "leads"
            leads_dir.mkdir(parents=True, exist_ok=True)
            
            # Save individual lead file
            lead_file = leads_dir / f"{self.lead_id}.json"
            with open(lead_file, 'w', encoding='utf-8') as f:
                json.dump(self.lead_state, f, indent=2, ensure_ascii=False)
            
            # Update leads database
            db_file = leads_dir / "leads_database.json"
            if db_file.exists():
                with open(db_file, 'r', encoding='utf-8') as f:
                    db = json.load(f)
            else:
                db = {"leads": [], "metadata": {"total_leads": 0, "last_updated": None, "version": "1.0"}}
            
            # Check if lead already exists in database
            existing_lead_idx = next(
                (i for i, lead in enumerate(db["leads"]) if lead.get("lead_id") == self.lead_id),
                None
            )
            
            if existing_lead_idx is not None:
                db["leads"][existing_lead_idx] = self.lead_state
            else:
                db["leads"].append(self.lead_state)
                db["metadata"]["total_leads"] = len(db["leads"])
            
            db["metadata"]["last_updated"] = datetime.now().isoformat()
            
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved lead data for {self.lead_id}")
            
        except Exception as e:
            logger.error(f"Error saving lead data: {e}")
    
    @function_tool
    async def search_faq(self, context: RunContext, query: str) -> str:
        """Search Razorpay FAQ for relevant information about products, pricing, features, and more.
        
        Use this tool when the user asks questions about:
        - What Razorpay does or offers
        - Pricing and costs
        - Payment methods supported
        - Integration and setup
        - Security and compliance
        - Use cases and industry fit
        - Any product features or capabilities
        
        Args:
            query: The user's question or topic (e.g., "pricing plans", "UPI support", "integration time")
        
        Returns:
            Relevant information from the FAQ database
        """
        try:
            # Track question for lead context
            if query not in self.lead_state["questions_asked"]:
                self.lead_state["questions_asked"].append(query)
            
            # Search FAQs
            results = search_faqs(query, self.faq_data, max_results=2)
            
            if results:
                response = format_faq_response(results)
                logger.info(f"FAQ search for '{query}': {len(results)} results")
                return response
            else:
                return "I don't have specific information about that in my knowledge base. Let me connect you with our team who can provide those details. What's the best email to reach you?"
        
        except Exception as e:
            logger.error(f"Error searching FAQ: {e}")
            return "I'm having trouble accessing that information right now. Let me note down your question and have someone get back to you with details."
    
    @function_tool
    async def save_lead_info(self, context: RunContext, field: str, value: str) -> str:
        """Save collected lead information during the conversation.
        
        Use this tool to store information as the user provides it naturally in conversation.
        Call this immediately when the user shares any of these details.
        
        Args:
            field: The type of information (name, email, company, role, use_case, team_size, timeline, pain_point)
            value: The information provided by the user
        
        Returns:
            Confirmation message
        """
        try:
            # Map field to lead state structure
            field_mapping = {
                "name": ("personal_info", "name"),
                "email": ("personal_info", "email"),
                "company": ("personal_info", "company"),
                "role": ("personal_info", "role"),
                "use_case": ("business_context", "use_case"),
                "team_size": ("business_context", "team_size"),
                "timeline": ("business_context", "timeline"),
            }
            
            if field == "pain_point":
                # Add to pain_points list
                if value not in self.lead_state["business_context"]["pain_points"]:
                    self.lead_state["business_context"]["pain_points"].append(value)
            elif field in field_mapping:
                section, key = field_mapping[field]
                self.lead_state[section][key] = value
            else:
                logger.warning(f"Unknown field: {field}")
                return "Information noted."
            
            # Save to file
            self._save_lead()
            
            logger.info(f"Saved {field}: {value} for lead {self.lead_id}")
            return f"Got it, I've noted that down."
        
        except Exception as e:
            logger.error(f"Error saving lead info: {e}")
            return "Noted."
    
    @function_tool
    async def get_pricing_info(self, context: RunContext) -> str:
        """Get Razorpay pricing information.
        
        Use this when user asks about costs, fees, or pricing.
        
        Returns:
            Pricing summary
        """
        try:
            return get_pricing_summary(self.faq_data)
        except Exception as e:
            logger.error(f"Error getting pricing: {e}")
            return "Our standard pricing is 2% per transaction with zero setup fees. Let me have someone share detailed pricing with you."
    
    @function_tool
    async def get_company_info(self, context: RunContext) -> str:
        """Get Razorpay company overview.
        
        Use this when user asks what Razorpay is or does.
        
        Returns:
            Company overview
        """
        try:
            return get_company_overview(self.faq_data)
        except Exception as e:
            logger.error(f"Error getting company info: {e}")
            return "Razorpay is India's leading payment and financial solutions company, serving over 10 million businesses."
    
    @function_tool
    async def end_conversation_summary(self, context: RunContext, user_ready_to_end: bool = True) -> str:
        """Generate and deliver end-of-call summary when conversation is wrapping up.
        
        Use this tool when:
        - User says goodbye, thanks, that's all, I'm done, etc.
        - User has received the information they needed
        - Conversation feels naturally complete
        
        Args:
            user_ready_to_end: Whether the user indicated they're ready to end (default: True)
        
        Returns:
            A warm closing summary
        """
        try:
            # Build conversation excerpt from questions asked and lead data
            name = self.lead_state["personal_info"]["name"] or "there"
            company = self.lead_state["personal_info"]["company"]
            use_case = self.lead_state["business_context"]["use_case"]
            timeline = self.lead_state["business_context"]["timeline"]
            questions = self.lead_state["questions_asked"]
            
            # Create a brief summary
            summary_parts = []
            
            if name != "there":
                summary_parts.append(f"Thanks so much for your time, {name}!")
            else:
                summary_parts.append("Thanks so much for your time!")
            
            if use_case:
                summary_parts.append(f"It's great to hear about your {use_case} use case.")
            elif company:
                summary_parts.append(f"It's great to learn about {company}.")
            
            if timeline == "now":
                summary_parts.append("Since you're looking to get started soon, I'll make sure our team reaches out to you within 24 hours.")
            elif timeline == "soon":
                summary_parts.append("I've noted that you're planning to move forward in the near future. We'll be in touch!")
            elif timeline == "later":
                summary_parts.append("I've noted your interest for future reference. Feel free to reach out anytime!")
            else:
                summary_parts.append("I've captured all your details and someone from our team will follow up with you shortly.")
            
            # Add email CTA if we have it
            email = self.lead_state["personal_info"]["email"]
            if email:
                summary_parts.append(f"We'll send over some resources to {email}.")
            else:
                summary_parts.append("If you'd like us to send over some resources, just share your email and we'll get those to you!")
            
            summary = " ".join(summary_parts)
            
            # Update lead state with final summary
            self.lead_state["conversation_summary"] = summary
            self.lead_state["status"] = "completed"
            
            # Determine interest level based on timeline and engagement
            if timeline == "now" or len(questions) >= 3:
                self.lead_state["interest_level"] = "high"
            elif timeline == "soon" or len(questions) >= 2:
                self.lead_state["interest_level"] = "medium"
            else:
                self.lead_state["interest_level"] = "low"
            
            # Final save
            self._save_lead()
            
            logger.info(f"Conversation ended for lead {self.lead_id} - Interest: {self.lead_state['interest_level']}")
            
            return summary
        
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Thanks so much for chatting with me today! We'll be in touch soon. Have a great day!"
    
def prewarm(proc: JobProcess):
    """Prewarm function to load models and data before conversation starts."""
    proc.userdata["vad"] = silero.VAD.load()
    
    # Load FAQ data once and store in userdata
    try:
        logger.info("Loading Razorpay FAQ data...")
        proc.userdata["faq_data"] = load_faq_data()
        logger.info("FAQ data loaded successfully")
    except Exception as e:
        logger.error(f"Error loading FAQ data: {e}")
        proc.userdata["faq_data"] = {}


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
                voice="en-IN-anusha", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
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
        agent=Assistant(faq_data=ctx.proc.userdata.get("faq_data", {})),
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
