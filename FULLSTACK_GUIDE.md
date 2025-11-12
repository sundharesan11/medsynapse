# Full Stack Setup Guide

Complete guide to run the entire Doctor's Intelligent Assistant system.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  React Frontend (Port 3000)              │
│  - Patient intake form                                   │
│  - SOAP report viewer                                    │
│  - Search interface                                      │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                 │
│  - LangGraph multi-agent orchestration                  │
│  - Groq LLM integration                                  │
│  - REST API endpoints                                    │
└───────┬──────────────────────────┬──────────────────────┘
        │                          │
        ▼                          ▼
┌──────────────┐          ┌───────────────────┐
│   Qdrant     │          │   Groq API        │
│  (Port 6333) │          │   LangSmith       │
└──────────────┘          └───────────────────┘
```

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- API Keys (Groq, LangSmith)

---

## Step-by-Step Setup

### 1. Clone & Navigate

```bash
cd /Users/sundharesan/Ideation/medsynapse
```

### 2. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys:
# - GROQ_API_KEY
# - LANGCHAIN_API_KEY
```

### 3. Start Qdrant Database

```bash
docker-compose up -d qdrant

# Wait for it to start
sleep 10

# Verify it's running
curl http://localhost:6333/
```

### 4. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Frontend is ready (don't start yet)
cd ..
```

---

## Running the Full Stack

You'll need **3 terminals**:

### Terminal 1: Qdrant (if not already running)

```bash
docker-compose up -d qdrant
```

### Terminal 2: Backend

```bash
# Activate venv
source venv/bin/activate

# Start FastAPI
cd backend
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 3: Frontend

```bash
# From project root
cd frontend
npm run dev
```

You should see:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:3000/
```

---

## Access the Application

Open your browser:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

---

## Testing the System

### Test 1: Patient Intake

1. Go to http://localhost:3000
2. Fill in the form:
   - Patient ID: `TEST001`
   - Patient Information:
     ```
     58-year-old male with chest pain for 2 hours.
     Pain is sharp, radiating to left arm.
     History of hypertension.
     Taking Lisinopril 10mg daily.
     BP: 160/95, HR: 98
     ```
3. Click "Process Patient Intake"
4. Wait ~10-15 seconds
5. SOAP report appears!

### Test 2: View in Qdrant

1. Go to http://localhost:6333/dashboard
2. Click "Collections"
3. Click "patient_cases"
4. See your case stored as a vector!

### Test 3: LangSmith Traces

1. Go to https://smith.langchain.com
2. Select project: `medsynapse-dev`
3. See detailed traces of all agent calls

---

## Troubleshooting

### Frontend can't connect to backend

**Error**: "Network Error" or "Failed to fetch"

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/

# If not, start backend:
cd backend
uvicorn main:app --reload --port 8000
```

### Backend can't connect to Qdrant

**Error**: "Qdrant is not running"

**Solution**:
```bash
# Check Qdrant status
docker ps | grep qdrant

# If not running:
docker-compose up -d qdrant
sleep 10
```

### Port already in use

**Error**: "Address already in use"

**Solution**:
```bash
# Find what's using the port
lsof -i :3000  # or :8000 or :6333

# Kill the process or change port in config
```

### API Keys not working

**Error**: "GROQ_API_KEY not found"

**Solution**:
```bash
# Check .env file exists
cat .env

# Make sure keys are set (no quotes needed)
GROQ_API_KEY=gsk_your_key_here
LANGCHAIN_API_KEY=ls__your_key_here
```

---

## Development Workflow

### Making Backend Changes

```bash
# Backend has hot reload enabled
# Just edit files in backend/
# Server automatically restarts
```

### Making Frontend Changes

```bash
# Frontend has hot reload via Vite
# Just edit files in frontend/src/
# Browser automatically refreshes
```

### Adding New Features

1. **New Agent**: Add to `backend/agents/`
2. **New API Endpoint**: Add to `backend/main.py`
3. **New UI Component**: Add to `frontend/src/components/`
4. **New Page**: Add to `frontend/src/pages/` and route in `App.jsx`

---

## Stopping the System

```bash
# Stop frontend: Ctrl+C in Terminal 3
# Stop backend: Ctrl+C in Terminal 2
# Stop Qdrant:
docker-compose down
```

---

## Production Deployment

### Build Frontend

```bash
cd frontend
npm run build

# Output in: frontend/dist/
```

### Serve Frontend with Backend

Update `backend/main.py` to serve static files:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="frontend")
```

### Run in Production

```bash
# Use gunicorn or uvicorn workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Environment Variables

### Backend (.env in project root)

```env
GROQ_API_KEY=gsk_xxx
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__xxx
LANGCHAIN_PROJECT=medsynapse-prod
QDRANT_URL=http://localhost:6333
```

### Frontend (.env in frontend/)

```env
VITE_API_URL=http://localhost:8000
```

---

## Performance Tips

1. **Groq Rate Limits**: Free tier = 30 req/min
2. **First Request Slow**: Model loading takes ~2-3 seconds
3. **Qdrant Startup**: Takes 5-10 seconds to be ready
4. **Frontend Build**: Production build is much faster

---

## Next Steps

- ✅ Phase 1: Backend working
- ✅ Phase 2: Qdrant integration
- ✅ Phase 3: React frontend
- ⬜ Phase 4: Enhanced orchestration
- ⬜ Phase 5: Docker deployment

---

## Support

- Backend Issues: Check `backend/main.py`
- Frontend Issues: Check browser console (F12)
- Database Issues: Check `docker logs medsynapse-qdrant`
- API Issues: Check `http://localhost:8000/docs`

---

**You're all set! Enjoy your multi-agent healthcare system!**
