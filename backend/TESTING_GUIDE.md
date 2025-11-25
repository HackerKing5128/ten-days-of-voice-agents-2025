# Day 5 - Testing Guide for Zoya SDR Agent

## 🧪 Pre-Test Checklist

### 1. Environment Setup
```powershell
cd backend

# Verify dependencies are installed
uv sync

# Check .env.local has required keys
# LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
# MURF_API_KEY, GOOGLE_API_KEY, DEEPGRAM_API_KEY
```

### 2. Verify File Structure
```
backend/
├── src/
│   ├── agent.py ✅
│   └── utils/
│       ├── __init__.py ✅
│       ├── faq_matcher.py ✅
│       └── llm_helpers.py ✅
├── shared-data/
│   ├── razorpay_faq.json ✅
│   └── leads/
│       ├── leads_database.json ✅
│       └── .gitkeep ✅
```

## 🚀 Running the Agent

### Start Backend
```powershell
cd backend
uv run python src/agent.py dev
```

Expected output:
```
INFO: Loading Razorpay FAQ data...
INFO: FAQ data loaded successfully
INFO: Agent started on port 8080
```

### Start Frontend
```powershell
cd frontend
pnpm dev
```

Open browser to http://localhost:3000

## 🎯 Test Scenarios

### Test 1: FAQ Answering (Basic)
**Goal**: Verify FAQ search tool works

**User**: "What does Razorpay do?"

**Expected**:
- Zoya should use `search_faq` tool
- Provide accurate answer from FAQ
- Response should be natural and concise

**Check**: Look for log: `INFO: FAQ search for 'what does razorpay do': 1 results`

---

### Test 2: Pricing Questions
**Goal**: Test pricing-specific queries

**User**: "How much does it cost?"

**Expected**:
- Should use `get_pricing_info` or `search_faq`
- Answer: "2% per transaction, zero setup fees"
- Should mention UPI zero platform fee

---

### Test 3: Lead Collection (Full Flow)
**Goal**: Complete lead capture

**Conversation**:
```
User: "Hi, I'm looking for a payment gateway"
Zoya: [Greeting + discovery question]

User: "I run an e-commerce store selling electronics"
Zoya: [Should use save_lead_info for use_case]

User: "I'm facing low payment success rates"
Zoya: [Should save as pain_point]

Zoya: "By the way, what's your name?"
User: "Amit"
Zoya: [save_lead_info field=name value=Amit]

Zoya: "What email works best?"
User: "amit@electrostore.com"
Zoya: [save_lead_info field=email value=amit@electrostore.com]

Zoya: "What's your company called?"
User: "ElectroStore India"
Zoya: [save_lead_info field=company]

Zoya: "How soon are you looking to switch?"
User: "Within the next week"
Zoya: [save_lead_info field=timeline value=now]

User: "That's all, thank you!"
Zoya: [Use end_conversation_summary]
```

**Expected**:
- Check `backend/shared-data/leads/` for new UUID.json file
- Verify all fields captured:
  ```json
  {
    "personal_info": {
      "name": "Amit",
      "email": "amit@electrostore.com",
      "company": "ElectroStore India"
    },
    "business_context": {
      "use_case": "e-commerce payment gateway",
      "timeline": "now",
      "pain_points": ["low payment success rates"]
    },
    "interest_level": "high"
  }
  ```

---

### Test 4: Multiple FAQ Questions
**Goal**: Verify question tracking

**User**: 
1. "Do you support UPI?"
2. "How easy is integration?"
3. "What about international payments?"

**Expected**:
- Each question triggers `search_faq`
- All questions saved to `questions_asked` array
- Natural responses for each

**Check lead JSON**: 
```json
"questions_asked": [
  "do you support upi",
  "how easy is integration",
  "what about international payments"
]
```

---

### Test 5: Interest Level Scoring
**Goal**: Test automatic qualification

**Scenario A - High Interest**:
- Timeline: "now"
- Questions asked: 3+
- Expected: `"interest_level": "high"`

**Scenario B - Medium Interest**:
- Timeline: "soon"
- Questions asked: 2
- Expected: `"interest_level": "medium"`

**Scenario C - Low Interest**:
- Timeline: "later" or null
- Questions asked: 1
- Expected: `"interest_level": "low"`

---

### Test 6: End-of-Call Summary
**Goal**: Verify personalized closing

**User**: "Thanks, that's all I needed!"

**Expected Zoya Response Pattern**:
```
"Thanks so much for your time, [NAME]! 
It's great to hear about your [USE_CASE] use case. 
Since you're looking to get started [TIMELINE], 
I'll make sure our team reaches out to you within 24 hours. 
We'll send over some resources to [EMAIL]."
```

**Check**:
- Summary is personalized with actual data
- Timeline-appropriate follow-up promise
- Lead JSON has `"status": "completed"`

---

## 📊 Validation Checklist

After running all tests, verify:

- [ ] FAQ tool answers 10+ different questions correctly
- [ ] All 7 lead fields can be captured (name, email, company, role, use_case, team_size, timeline)
- [ ] Pain points are collected in array
- [ ] Questions asked are tracked
- [ ] Interest level scoring works (high/medium/low)
- [ ] Lead JSON files are created in `shared-data/leads/`
- [ ] `leads_database.json` is updated with each lead
- [ ] End-of-call summary is personalized
- [ ] No crashes or errors in logs
- [ ] Conversation feels natural, not robotic

## 🎬 Recording Demo Video

### Setup
1. Clean up test leads: Delete old JSON files in `shared-data/leads/`
2. Restart backend to get fresh session
3. Open browser in full screen
4. Start screen recording

### Demo Script
```
1. Show connection to agent (0:00-0:05)
2. Greeting from Zoya (0:05-0:10)
3. Ask: "What does Razorpay do?" (0:10-0:20)
4. Share your business context (0:20-0:40)
5. Ask 2-3 pricing/feature questions (0:40-1:10)
6. Provide lead details naturally (1:10-1:40)
7. End conversation: "That's all, thanks!" (1:40-1:55)
8. Show generated lead JSON file (1:55-2:10)
9. Highlight key fields and interest score (2:10-2:20)
```

### What to Highlight
- ✨ Natural conversation flow
- 🤖 FAQ answering accuracy
- 📝 Automatic lead capture
- 🎯 Interest qualification
- 💾 Generated JSON output
- ⚡ Murf Falcon TTS speed

## 🐛 Troubleshooting

### Issue: "Unable to import utils"
**Fix**: Make sure you're running from backend directory with `uv run`

### Issue: "FAQ data not found"
**Fix**: Verify `shared-data/razorpay_faq.json` exists

### Issue: "Agent not responding"
**Fix**: Check all API keys in `.env.local`

### Issue: "Lead data not saving"
**Fix**: Check `shared-data/leads/` directory has write permissions

### Issue: "Tools not being called"
**Fix**: Gemini Flash should auto-detect tool usage. Check LLM logs.

## 📈 Success Criteria

✅ **MVP Complete When**:
1. Zoya greets professionally and energetically
2. FAQ questions get accurate answers
3. All lead fields are captured naturally
4. End-of-call summary is personalized
5. Lead JSON files are generated correctly
6. Interest level is auto-scored
7. Conversation feels like talking to a real SDR

---

**Ready to Test?** Start with Test 1 and work through each scenario! 🚀
