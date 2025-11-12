# 🩺 Doctor's Intelligent Assistant (MedSynapse)

A multi-agent healthcare system using **LangGraph** to coordinate specialized AI agents for intelligent patient intake, clinical summarization, knowledge retrieval, and SOAP report generation.

---

## 🎯 **System Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    Doctor's Dashboard (React)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              LangGraph Orchestrator                    │  │
│  │                                                        │  │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐       │  │
│  │  │ Intake   │───▶│ Summary  │───▶│Knowledge │       │  │
│  │  │  Agent   │    │  Agent   │    │  Agent   │       │  │
│  │  └──────────┘    └──────────┘    └────┬─────┘       │  │
│  │                                        │             │  │
│  │                                        ▼             │  │
│  │                                  ┌──────────┐       │  │
│  │                                  │  Report  │       │  │
│  │                                  │  Agent   │       │  │
│  │                                  └──────────┘       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    ┌─────────┐          ┌──────────┐        ┌──────────┐
    │  Groq   │          │LangSmith │        │ Qdrant   │
    │   API   │          │ Tracing  │        │VectorDB  │
    └─────────┘          └──────────┘        └──────────┘
```

---

## 🧱 **Architecture**

### **Multi-Agent System**
1. **Intake Agent** - Extracts structured patient data from conversational input
2. **Summary Agent** - Generates concise clinical summaries
3. **Knowledge Agent** - Retrieves relevant medical context from vector DB
4. **Report Agent** - Produces structured SOAP format reports

### **Tech Stack**
- **LangGraph** - Multi-agent orchestration
- **Groq API** - Fast, cost-effective LLM inference
- **LangSmith** - Complete observability and tracing
- **Qdrant** - Vector database for patient context
- **FastAPI** - High-performance backend
- **React + Tailwind** - Modern frontend UI

---

## 🚀 **Quick Start**

### **1. Prerequisites**
```bash
# Python 3.11+
python --version

# Node.js 18+ (for frontend)
node --version
```

### **2. Clone & Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Configure Environment**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys:
# - GROQ_API_KEY from https://console.groq.com/keys
# - LANGCHAIN_API_KEY from https://smith.langchain.com/settings
```

### **4. Start Qdrant (Docker)**
```bash
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage:z \
  qdrant/qdrant
```

### **5. Run Backend**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### **6. Test the System**
```bash
# Run example patient intake
python backend/test_graph.py
```

---

## 📊 **Development Phases**

- [x] **Phase 1** - Minimal working prototype (LangGraph + Groq + LangSmith)
- [x] **Phase 2** - Qdrant memory integration ✨ NEW
- [ ] **Phase 3** - React dashboard UI
- [ ] **Phase 4** - Enhanced orchestration & logging
- [ ] **Phase 5** - Docker containerization

---

## 🧩 **Project Structure**

```
medsynapse/
├── backend/
│   ├── agents/              # Agent node implementations
│   │   ├── intake.py
│   │   ├── summary.py
│   │   ├── knowledge.py
│   │   └── report.py
│   ├── models/              # Pydantic models
│   │   └── schemas.py
│   ├── utils/               # Utilities
│   │   ├── groq_client.py
│   │   └── qdrant_client.py
│   ├── graph.py             # LangGraph orchestration
│   ├── main.py              # FastAPI app
│   └── test_graph.py        # Testing script
├── frontend/                # React application
│   └── src/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔍 **Observability**

All agent runs are automatically traced in **LangSmith**:
1. Go to [smith.langchain.com](https://smith.langchain.com)
2. Select project: `medsynapse-dev`
3. View detailed traces of each agent execution

---

## 📝 **Example Output**

```json
{
  "report_type": "SOAP",
  "patient_id": "P12345",
  "subjective": "Patient reports chest pain...",
  "objective": "BP: 140/90, HR: 85...",
  "assessment": "Possible angina...",
  "plan": "Schedule ECG, prescribe..."
}
```

---

## 🛠️ **Troubleshooting**

### **Issue: LangSmith not tracing**
- Ensure `LANGCHAIN_TRACING_V2=true` in `.env`
- Check API key is valid

### **Issue: Groq rate limits**
- Free tier: 30 requests/minute
- Consider implementing retry logic

---

## 📚 **Resources**

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Groq API Docs](https://console.groq.com/docs)
- [LangSmith Guide](https://docs.smith.langchain.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)

---

## 🤝 **Contributing**

This is a learning project. Experiment, break things, and learn!

---

**Built with ❤️ using LangGraph**
