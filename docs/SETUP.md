# Setup Guide - Doctor's Intelligent Assistant

Follow these steps to get the system running.

---

## Step 1: Get Your API Keys

### Groq API Key (Required)
1. Go to [https://console.groq.com/keys](https://console.groq.com/keys)
2. Sign up or log in
3. Click "Create API Key"
4. Copy your key (starts with `gsk_...`)

**Why Groq?**
- 10x faster than OpenAI
- Free tier: 30 requests/minute
- Great for development!

### LangSmith API Key (Recommended for debugging)
1. Go to [https://smith.langchain.com/settings](https://smith.langchain.com/settings)
2. Sign up or log in
3. Create an API key
4. Copy your key (starts with `ls__...`)

**Why LangSmith?**
- See EVERY agent call in detail
- Debug what each agent is thinking
- Track token usage
- Essential for development!

---

## Step 2: Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your keys
nano .env  # or use your favorite editor
```

Your `.env` should look like:
```env
GROQ_API_KEY=gsk_your_actual_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_actual_key_here
LANGCHAIN_PROJECT=medsynapse-dev
```

---

## Step 3: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

This installs:
- LangGraph & LangChain
- Groq LLM client
- FastAPI
- Pydantic (data validation)

---

## Step 4: Run First Test

```bash
# From the project root
cd backend
python tests/test_graph.py
```

You should see:
```
Starting medical intake pipeline for patient P12345
[INTAKE AGENT] Starting patient data extraction...
[INTAKE AGENT] Extracted data for patient P12345
[SUMMARY AGENT] Generating clinical summary...
[SUMMARY AGENT] Summary generated
[KNOWLEDGE AGENT] Retrieving medical knowledge...
[KNOWLEDGE AGENT] Knowledge retrieved
[REPORT AGENT] Generating SOAP report...
[REPORT AGENT] SOAP report generated for patient P12345
```

---

## Step 5: View LangSmith Traces

1. Go to [https://smith.langchain.com](https://smith.langchain.com)
2. Select project: `medsynapse-dev`
3. You'll see a trace for your test run!

Click into it to see:
- Each agent's LLM call
- Input/output for every step
- Token usage
- Execution time

**This is amazing for debugging!**

---

## Step 6: Start FastAPI Server (Optional)

```bash
# From backend directory
uvicorn main:app --reload --port 8000
```

Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

You'll see interactive API documentation!

Try the `/intake` endpoint:
```json
{
  "patient_id": "TEST001",
  "raw_input": "Patient has headache for 3 days, feels dizzy"
}
```

---

## Troubleshooting

### "GROQ_API_KEY not found"
- Make sure `.env` file exists in project root
- Check the key starts with `gsk_`
- Try: `echo $GROQ_API_KEY` to verify it's loaded

### "Module not found" errors
- Activate venv: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

### LangSmith not showing traces
- Check `LANGCHAIN_TRACING_V2=true` in `.env`
- Verify API key is correct
- May take 30 seconds to appear

### Groq rate limits
- Free tier: 30 requests/minute
- Wait a minute and try again
- Or upgrade Groq plan

---

## What's Next?

- Phase 1 Complete - Basic multi-agent system working!
- Phase 2 - Add Qdrant for patient history
- Phase 3 - Build React dashboard
- Phase 4 - Enhanced tracing
- Phase 5 - Docker deployment

---

## Learn More

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Groq Docs](https://console.groq.com/docs)
- [LangSmith Guide](https://docs.smith.langchain.com/)

---

**Need help? Check `docs/README.md` or review the code comments!**
