"""LLM Helper Functions and Prompt Templates for SDR Agent"""

from typing import Dict, Any, List


def generate_call_summary_prompt(lead_data: Dict[str, Any], conversation_excerpt: str) -> str:
    """Generate prompt for creating end-of-call summary.
    
    Args:
        lead_data: Collected lead information
        conversation_excerpt: Key parts of the conversation
        
    Returns:
        Prompt for LLM to generate summary
    """
    return f"""Based on this sales conversation, create a brief verbal summary to share with the prospect.

Lead Information Collected:
- Name: {lead_data.get('personal_info', {}).get('name', 'Not provided')}
- Company: {lead_data.get('personal_info', {}).get('company', 'Not provided')}
- Role: {lead_data.get('personal_info', {}).get('role', 'Not provided')}
- Use Case: {lead_data.get('business_context', {}).get('use_case', 'Not provided')}
- Team Size: {lead_data.get('business_context', {}).get('team_size', 'Not provided')}
- Timeline: {lead_data.get('business_context', {}).get('timeline', 'Not provided')}

Conversation Highlights:
{conversation_excerpt}

Create a warm, professional 2-3 sentence summary that:
1. Thanks them for their time
2. Briefly recaps their key need/use case
3. Mentions the next step or timeline they mentioned

Keep it natural and conversational. Do not use any formatting, emojis, or special characters."""


def generate_qualification_notes_prompt(transcript: str, lead_data: Dict[str, Any]) -> str:
    """Generate prompt for creating CRM-style qualification notes.
    
    Args:
        transcript: Full or partial conversation transcript
        lead_data: Collected lead information
        
    Returns:
        Prompt for generating structured notes
    """
    return f"""Analyze this sales conversation and create structured qualification notes for our CRM.

Conversation Transcript:
{transcript}

Lead Data:
{lead_data}

Generate a JSON response with the following structure:
{{
    "key_pain_points": ["list of main challenges they mentioned"],
    "budget_mentioned": true/false,
    "decision_maker_status": "decision_maker" | "influencer" | "unknown",
    "urgency_level": "high" | "medium" | "low",
    "timeline": "now" | "soon" | "exploring",
    "fit_score": 0-100 (based on urgency, budget signals, authority, and need clarity),
    "crm_notes": "2-3 sentence summary suitable for CRM entry",
    "recommended_next_steps": ["list of suggested follow-up actions"]
}}

Base your assessment on:
- Budget signals: Did they ask about pricing? Express concern about costs? Mention budget?
- Authority: Do they seem to make decisions or influence them? Are they a founder/manager?
- Need: How clear and urgent is their problem?
- Timeline: When do they need a solution?

Be objective and specific in your analysis."""


def generate_followup_email_prompt(lead_data: Dict[str, Any], conversation_summary: str) -> str:
    """Generate prompt for creating follow-up email draft.
    
    Args:
        lead_data: Collected lead information
        conversation_summary: Summary of the conversation
        
    Returns:
        Prompt for generating email draft
    """
    name = lead_data.get('personal_info', {}).get('name', 'there')
    company = lead_data.get('personal_info', {}).get('company', 'your company')
    use_case = lead_data.get('business_context', {}).get('use_case', 'your needs')
    
    return f"""Create a professional but friendly follow-up email for this sales conversation.

Context:
- Prospect Name: {name}
- Company: {company}
- Use Case: {use_case}
- Conversation Summary: {conversation_summary}

Generate a JSON response with:
{{
    "subject": "Email subject line (professional, personalized, not salesy)",
    "body": "Email body (3-4 paragraphs: greeting, recap key points, value proposition, clear call-to-action)",
    "signature": "Best regards,\\nZoya\\nSales Development Representative\\nRazorpay"
}}

Email Guidelines:
- Reference specific points from our conversation
- Keep it concise (under 200 words)
- Personalize to their use case
- Include a clear next step
- Professional but warm tone
- No jargon or buzzwords"""


def extract_lead_fields_prompt(conversation_text: str) -> str:
    """Generate prompt to extract lead information from conversation.
    
    Args:
        conversation_text: Portion of conversation to analyze
        
    Returns:
        Prompt for extracting structured lead data
    """
    return f"""Extract lead information from this conversation excerpt.

Conversation:
{conversation_text}

Extract and return JSON with these fields (use null if not mentioned):
{{
    "name": "Full name",
    "email": "Email address",
    "company": "Company name",
    "role": "Job title/role",
    "use_case": "What they want to use Razorpay for",
    "team_size": "Size of their team/company",
    "timeline": "now" | "soon" | "later" | null,
    "pain_points": ["specific challenges mentioned"],
    "questions_asked": ["topics they asked about"]
}}

Only include information explicitly mentioned. Don't infer or guess."""


def persona_detection_prompt(conversation_context: str) -> str:
    """Generate prompt to detect user persona for tailored pitching.
    
    Args:
        conversation_context: Recent conversation context
        
    Returns:
        Prompt for persona detection
    """
    return f"""Based on this conversation, identify the person's likely professional persona.

Conversation:
{conversation_context}

Personas to choose from:
- developer: Technical person, cares about APIs, documentation, integration ease
- founder: Business owner, cares about speed to market, cost, reliability
- product_manager: Product-focused, cares about features, analytics, user experience
- finance: Financial decision-maker, cares about compliance, security, cost structure
- marketer: Marketing-focused, cares about conversion rates, customer experience
- operations: Operations-focused, cares about automation, reconciliation, efficiency

Return JSON:
{{
    "persona": "most likely persona",
    "confidence": "high" | "medium" | "low",
    "reasoning": "brief explanation of why this persona fits"
}}"""


# Persona-specific pitch angles
PERSONA_PITCHES = {
    "developer": """For developers, Razorpay offers clean, well-documented APIs with SDKs in all major languages. Most teams integrate in under 2 hours. We have extensive docs, sample code, and a sandbox environment. Our webhook system is robust, and our API uptime is 99.9%.""",
    
    "founder": """For founders, Razorpay means you can start accepting payments in under a day with zero setup costs. We handle all the complexity - PCI compliance, fraud prevention, reconciliation - so you can focus on building your product. Over 10 million businesses trust us, from startups to unicorns.""",
    
    "product_manager": """For product teams, Razorpay provides detailed analytics on payment success rates, drop-offs, and customer behavior. Our checkout is highly customizable and mobile-optimized. We support A/B testing and have features that directly impact conversion like one-click checkout and smart retry logic.""",
    
    "finance": """For finance teams, Razorpay is PCI-DSS Level 1 certified with complete compliance coverage. We provide detailed transaction reports, GST-compliant invoicing, automated reconciliation, and integration with accounting software like Tally and Zoho. Settlement tracking is transparent and reliable.""",
    
    "marketer": """For marketing teams, Razorpay helps improve conversion with features like one-click checkout, multiple payment options, and mobile-optimized flows. We provide detailed analytics on payment performance and drop-off points. Our payment links make it easy to run campaigns without developer dependency.""",
    
    "operations": """For operations teams, Razorpay automates payment reconciliation, vendor payouts, and subscription billing. We eliminate manual work with auto-matching payments, bulk payout capabilities, and real-time webhooks. Our dashboard provides full visibility into all transactions."""
}


def get_persona_pitch(persona: str) -> str:
    """Get tailored pitch for detected persona.
    
    Args:
        persona: Detected persona type
        
    Returns:
        Persona-specific pitch
    """
    return PERSONA_PITCHES.get(persona, PERSONA_PITCHES["founder"])
