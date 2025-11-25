# Day 5 - Razorpay SDR Agent Implementation

## 🎯 Overview

**Zoya** - An energetic and efficient AI SDR (Sales Development Representative) for Razorpay, India's leading payment solutions company.

## ✨ Features Implemented

### Primary Goal (MVP) ✅

1. **Professional SDR Persona - "Zoya"**
   - Energetic, efficient, and quick-witted
   - Modern fintech vibe matching Razorpay's brand
   - Natural conversational flow

2. **Comprehensive FAQ System**
   - 30+ detailed FAQ entries covering:
     - Product features (Payment Gateway, Subscriptions, Invoices, RazorpayX, etc.)
     - Pricing and transparency
     - Integration details
     - Payment methods (100+ supported)
     - Security and compliance
     - Use cases across industries
     - Technical specifications

3. **Intelligent FAQ Search**
   - Keyword-based matching with scoring algorithm
   - Multi-factor relevance (keywords, question match, category bonus)
   - Natural response formatting

4. **Lead Information Collection**
   - Personal Info: name, email, company, role
   - Business Context: use_case, team_size, timeline, pain_points
   - Automatic tracking of questions asked
   - Interest level qualification

5. **End-of-Call Summary**
   - Personalized closing based on conversation
   - Timeline-aware follow-up promises
   - Automatic interest level scoring
   - Complete lead data export to JSON

## 📁 File Structure

```
backend/
├── src/
│   ├── agent.py                      # Main SDR agent with all tools
│   └── utils/
│       ├── faq_matcher.py            # FAQ search and matching logic
│       ├── llm_helpers.py            # Prompt templates for advanced features
│       └── __init__.py
├── shared-data/
│   ├── razorpay_faq.json            # Comprehensive FAQ database (30+ entries)
│   └── leads/
│       ├── leads_database.json      # All leads aggregated
│       └── [lead-uuid].json         # Individual lead reports
```

## 🛠️ Tools Available to Zoya

### 1. `search_faq(query: str)`
Search Razorpay FAQ for relevant information.
- **When to use**: User asks about products, pricing, features, integrations, etc.
- **Example**: `search_faq("What are your pricing plans?")`

### 2. `save_lead_info(field: str, value: str)`
Save collected lead information incrementally.
- **Fields**: name, email, company, role, use_case, team_size, timeline, pain_point
- **Auto-saves**: Immediately writes to JSON after each field
- **Example**: `save_lead_info("email", "founder@startup.com")`

### 3. `get_pricing_info()`
Get concise Razorpay pricing summary.
- **Returns**: Standard pricing (2% per transaction, zero setup fees)

### 4. `get_company_info()`
Get Razorpay company overview.
- **Returns**: Tagline, description, customer count, industries served

### 5. `end_conversation_summary()`
Generate personalized end-of-call summary.
- **When to use**: User says goodbye, thanks, that's all, etc.
- **Actions**:
  - Creates personalized closing message
  - Scores interest level (high/medium/low)
  - Saves final lead report
  - Provides timeline-aware follow-up promise

## 📊 Lead Data Structure

```json
{
  "lead_id": "uuid-generated",
  "timestamp": "2025-11-25T10:30:00Z",
  "personal_info": {
    "name": "Rajesh Kumar",
    "email": "rajesh@startup.com",
    "company": "FastCommerce",
    "role": "Founder"
  },
  "business_context": {
    "use_case": "E-commerce payment gateway",
    "team_size": "5-10",
    "timeline": "now",
    "pain_points": ["Low success rates", "Complex integration"]
  },
  "conversation_summary": "Thanks so much for your time, Rajesh!...",
  "questions_asked": ["pricing plans", "UPI support", "integration time"],
  "interest_level": "high",
  "status": "completed"
}
```

## 🎯 Conversation Flow

1. **Greeting** (Energetic)
   - "Hi there! This is Zoya from Razorpay. Thanks for stopping by! What brings you here today?"

2. **Discovery** (Open-ended questions)
   - "Tell me about your business - what do you do?"
   - "What challenges are you facing with payments right now?"

3. **Answering Questions** (Using FAQ tools)
   - Searches FAQ database
   - Provides accurate, concise answers
   - Connects features to their use case

4. **Lead Collection** (Natural, conversational)
   - Asks for details throughout conversation
   - Saves incrementally using `save_lead_info`
   - Never feels like a form

5. **Qualification** (Timeline & fit assessment)
   - Understands urgency (now/soon/later)
   - Identifies decision-making authority
   - Tracks engagement level

6. **Closing** (Personalized summary)
   - Uses `end_conversation_summary`
   - Recaps key points
   - Promises appropriate follow-up

## 🚀 Usage

### Start the Backend

```bash
cd backend
uv run python src/agent.py dev
```

### Start the Frontend

```bash
cd frontend
pnpm dev
```

### Test the Agent

1. Open browser to frontend URL
2. Connect to the agent
3. Start conversation: "Hi, I'm looking for a payment solution"
4. Ask questions about Razorpay
5. Provide lead information naturally
6. End with "That's all, thank you!"

## 📈 Success Metrics

- ✅ **30 FAQ entries** with comprehensive coverage
- ✅ **Smart FAQ search** with relevance scoring
- ✅ **7 lead fields** captured automatically
- ✅ **Real-time saving** of lead data
- ✅ **Interest qualification** (high/medium/low)
- ✅ **Natural conversation flow** without feeling scripted

## 🎨 Persona Details

**Name**: Zoya
**Voice**: Murf Falcon "en-US-matthew" (professional, conversational)
**Tone**: Professional, intelligent, yet conversational
**Vibe**: Modern fintech - sharp, distinct, energetic
**Brand Alignment**: Matches Razorpay's blue, bold, tech-forward identity

## 📝 Example Conversation

```
Zoya: Hi there! This is Zoya from Razorpay. Thanks for stopping by! What brings you here today?

User: I'm looking for a payment gateway for my e-commerce store.

Zoya: Great! Tell me about your business - what kind of products do you sell?

User: We sell fashion accessories online.

Zoya: [uses save_lead_info to note use case]
      Perfect! E-commerce is a great fit for us. What challenges are you facing 
      with payments right now?

User: Our current gateway has low success rates and it's expensive.

Zoya: [saves pain point]
      I hear you. Success rates are crucial for e-commerce. Razorpay actually has 
      one of the highest success rates in India - typically above 90% for cards. 
      We use smart routing to automatically select the best payment gateway for 
      each transaction. By the way, what's your name?

User: I'm Rajesh.

Zoya: [saves name]
      Great to meet you, Rajesh! Quick question - what's your pricing like now?

User: We're paying 2.5% plus setup fees.

Zoya: [uses get_pricing_info]
      Our standard pricing is 2% per transaction with zero setup fees. UPI 
      transactions have zero platform fee. What email works best for you so I 
      can send over detailed pricing?

User: rajesh@mystore.com

Zoya: [saves email]
      Got it! And how soon are you looking to switch?

User: Pretty urgently, within the next week or two.

Zoya: [saves timeline as "now"]
      Perfect timing! Most businesses integrate in under 2 hours. What's your 
      company called?

User: FastFashion India.

Zoya: [saves company]
      Excellent! That's all I need for now, Rajesh. Thanks so much for your time! 
      It's great to hear about your e-commerce payment gateway use case. Since 
      you're looking to get started soon, I'll make sure our team reaches out to 
      you within 24 hours. We'll send over some resources to rajesh@mystore.com. 
      Have a great day!
```

## 🎬 Next Steps for Demo

1. **Test multiple conversation paths**
   - Pricing-focused user
   - Feature-focused user
   - Just exploring user

2. **Verify lead data quality**
   - Check `shared-data/leads/` for JSON files
   - Ensure all fields are captured
   - Verify interest scoring accuracy

3. **Record demo video**
   - Show natural conversation
   - Demonstrate FAQ answering
   - Display generated lead JSON
   - Highlight interest qualification

4. **LinkedIn post elements**
   - Show Zoya in action
   - Display lead JSON output
   - Mention Murf Falcon TTS speed
   - Use hashtags: #MurfAIVoiceAgentsChallenge #10DaysofAIVoiceAgents
   - Tag @Murf AI

## 🎯 Quality Achieved

- ✅ **Production-ready code** with proper error handling
- ✅ **Type hints** on all functions
- ✅ **Comprehensive docstrings**
- ✅ **Logging** for debugging
- ✅ **Incremental saves** (never lose data)
- ✅ **Natural persona** (Zoya feels real)
- ✅ **Rich FAQ data** (30+ realistic entries)
- ✅ **Smart qualification** (automatic interest scoring)

---

**Status**: ✅ Phase 2 Complete - Ready for Testing & Demo!
