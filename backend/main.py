"""
FastAPI Backend for Doctor's Intelligent Assistant

This exposes the LangGraph multi-agent system as REST APIs.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from graph import process_patient_intake
from models.schemas import PatientIntakeInput, APIResponse

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI app.

    Runs on startup and shutdown to initialize/cleanup resources.
    """
    # Startup
    print("🚀 Starting Doctor's Intelligent Assistant API")
    print(f"📊 LangSmith Tracing: {os.getenv('LANGCHAIN_TRACING_V2', 'false')}")
    print(f"🤖 Groq API configured: {bool(os.getenv('GROQ_API_KEY'))}")

    # Verify required environment variables
    required_vars = ["GROQ_API_KEY", "LANGCHAIN_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print(f"⚠️  WARNING: Missing environment variables: {', '.join(missing)}")
        print("   Some features may not work correctly")

    yield

    # Shutdown
    print("👋 Shutting down Doctor's Intelligent Assistant API")


# Create FastAPI app
app = FastAPI(
    title="Doctor's Intelligent Assistant",
    description="Multi-agent healthcare system using LangGraph",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class IntakeRequest(BaseModel):
    """Request model for patient intake endpoint."""
    patient_id: str
    raw_input: str
    session_id: str | None = None


class IntakeResponse(BaseModel):
    """Response model for patient intake endpoint."""
    success: bool
    message: str
    patient_id: str
    soap_report: dict | None = None
    errors: list[str] = []


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Doctor's Intelligent Assistant",
        "version": "1.0.0",
        "graph": "multi-agent LangGraph orchestration"
    }


@app.get("/health")
async def health_check():
    """Detailed health check with service status."""
    return {
        "status": "healthy",
        "services": {
            "groq_api": bool(os.getenv("GROQ_API_KEY")),
            "langsmith": os.getenv("LANGCHAIN_TRACING_V2") == "true",
            "qdrant": bool(os.getenv("QDRANT_URL"))
        }
    }


@app.post("/intake", response_model=IntakeResponse)
async def patient_intake(request: IntakeRequest):
    """
    Process patient intake through the multi-agent pipeline.

    This endpoint:
    1. Accepts raw patient intake text
    2. Processes through all agents (intake → summary → knowledge → report)
    3. Returns structured SOAP report

    Args:
        request: Patient intake data

    Returns:
        IntakeResponse with SOAP report or errors

    Example:
        ```bash
        curl -X POST "http://localhost:8000/intake" \\
             -H "Content-Type: application/json" \\
             -d '{
                   "patient_id": "P12345",
                   "raw_input": "Patient reports chest pain..."
                 }'
        ```
    """
    try:
        # Process through the graph
        result = await process_patient_intake(
            patient_id=request.patient_id,
            raw_input=request.raw_input,
            session_id=request.session_id
        )

        # Check for errors
        if result.errors:
            return IntakeResponse(
                success=False,
                message="Pipeline completed with errors",
                patient_id=request.patient_id,
                errors=result.errors
            )

        # Check if SOAP report was generated
        if not result.soap_report:
            return IntakeResponse(
                success=False,
                message="SOAP report generation failed",
                patient_id=request.patient_id,
                errors=["No SOAP report generated"]
            )

        # Success - return the SOAP report
        return IntakeResponse(
            success=True,
            message="Patient intake processed successfully",
            patient_id=request.patient_id,
            soap_report=result.soap_report.model_dump()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/patient/{patient_id}/history")
async def get_patient_history(patient_id: str):
    """
    Get patient history from Qdrant vector database.
    """
    try:
        from utils.qdrant_client import get_qdrant_client

        qdrant = get_qdrant_client()
        history = qdrant.get_patient_history(patient_id=patient_id, limit=10)

        return {
            "success": True,
            "patient_id": patient_id,
            "history": history,
            "total": len(history)
        }
    except Exception as e:
        return {
            "success": False,
            "patient_id": patient_id,
            "message": str(e),
            "history": []
        }


@app.post("/search")
async def search_similar_cases(request: dict):
    """
    Search for similar cases using semantic search.

    Request body:
    {
        "query": "chest pain and breathing difficulty",
        "limit": 5,
        "score_threshold": 0.5
    }
    """
    try:
        from utils.qdrant_client import get_qdrant_client

        query = request.get("query", "")
        limit = request.get("limit", 5)
        score_threshold = request.get("score_threshold", 0.5)

        if not query:
            return {
                "success": False,
                "message": "Query is required",
                "results": []
            }

        qdrant = get_qdrant_client()
        results = qdrant.search_similar_cases(
            query_text=query,
            limit=limit,
            score_threshold=score_threshold
        )

        return {
            "success": True,
            "query": query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "results": []
        }


@app.get("/stats")
async def get_database_stats():
    """
    Get database statistics from Qdrant.
    """
    try:
        from utils.qdrant_client import get_qdrant_client

        qdrant = get_qdrant_client()
        stats = qdrant.get_collection_stats()

        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "stats": {}
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
