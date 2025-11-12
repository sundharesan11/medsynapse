"""
Doctor Query Agent (RAG-style Q&A)

This agent allows doctors to ask natural-language questions about patient history.
It uses RAG (Retrieval-Augmented Generation) with Qdrant + Groq LLM.

Phase 5: New agent for interactive patient history Q&A
"""

from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from utils.groq_client import get_groq_llm
from utils.qdrant_client import get_qdrant_client


# RAG prompt template for answering doctor queries
QUERY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a medical AI assistant helping a doctor review patient history.

You will be given:
1. A doctor's question about a patient
2. Relevant historical patient data retrieved from medical records

Your task:
- Answer the question accurately using ONLY the provided patient data
- Be concise and clinical in your language
- If the data doesn't contain the answer, say "The available records don't contain information about [topic]"
- Do NOT make up information or speculate
- Cite specific visits when relevant (e.g., "In the visit on March 15, 2024...")

Format your response professionally, as if speaking to another clinician."""),
    ("human", """Question: {question}

Retrieved Patient Data:
{context}

Please answer the doctor's question based on the available patient data:""")
])


def create_context_from_history(history: List[Dict[str, Any]]) -> str:
    """
    Format patient history data into a context string for the LLM.

    Args:
        history: List of retrieved patient visits

    Returns:
        Formatted context string
    """
    if not history:
        return "No historical patient data available."

    context_parts = []
    for i, visit in enumerate(history, 1):
        timestamp = visit.get("timestamp", "Unknown date")
        chief_complaint = visit.get("chief_complaint", "N/A")
        symptoms = visit.get("symptoms", [])
        assessment = visit.get("assessment", "N/A")

        context_parts.append(f"\n--- Visit {i} ({timestamp}) ---")
        context_parts.append(f"Chief Complaint: {chief_complaint}")
        if symptoms:
            context_parts.append(f"Symptoms: {', '.join(symptoms)}")
        context_parts.append(f"Assessment: {assessment}")

    return "\n".join(context_parts)


async def query_agent(
    patient_id: str,
    question: str,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Answer a natural-language question about a patient's medical history.

    This function implements RAG (Retrieval-Augmented Generation):
    1. Retrieves relevant patient data from Qdrant (Retrieval)
    2. Formats it as context
    3. Uses Groq LLM to generate an answer (Generation)

    Args:
        patient_id: Patient identifier (optional - for filtering)
        question: Doctor's natural-language question
        limit: Maximum number of historical visits to retrieve

    Returns:
        Dictionary with answer, sources, and metadata
    """
    print(f"[QUERY AGENT] Processing question: '{question}'")

    try:
        qdrant = get_qdrant_client()

        # Step 1: Retrieve relevant patient data
        if patient_id:
            # Get specific patient's history
            print(f"   Retrieving history for patient {patient_id}...")
            history = qdrant.get_patient_history(
                patient_id=patient_id,
                limit=limit
            )
        else:
            # Search across all patients (semantic search)
            print(f"   Searching across all patients...")
            history = qdrant.search_similar_cases(
                query_text=question,
                limit=limit,
                score_threshold=0.5
            )

        if not history:
            return {
                "success": True,
                "answer": "No relevant patient data found to answer this question.",
                "sources": [],
                "question": question,
                "patient_id": patient_id
            }

        print(f"   SUCCESS: Retrieved {len(history)} relevant record(s)")

        # Step 2: Create context from retrieved data
        context = create_context_from_history(history)

        # Step 3: Generate answer using LLM
        llm = get_groq_llm(
            model="llama-3.3-70b-versatile",
            temperature=0.1  # Low temperature for factual answers
        )

        chain = QUERY_PROMPT | llm | StrOutputParser()

        print(f"   Generating answer with Groq LLM...")
        answer = await chain.ainvoke({
            "question": question,
            "context": context
        })

        print(f"   SUCCESS: Answer generated successfully")

        # Return structured response
        return {
            "success": True,
            "answer": answer,
            "sources": [
                {
                    "timestamp": visit.get("timestamp"),
                    "chief_complaint": visit.get("chief_complaint"),
                    "score": visit.get("score", 1.0)  # Similarity score if available
                }
                for visit in history
            ],
            "question": question,
            "patient_id": patient_id,
            "num_sources": len(history)
        }

    except Exception as e:
        error_msg = f"Query agent error: {str(e)}"
        print(f"ERROR: [QUERY AGENT] {error_msg}")
        return {
            "success": False,
            "answer": f"Error processing query: {error_msg}",
            "sources": [],
            "question": question,
            "patient_id": patient_id,
            "error": error_msg
        }


def query_agent_sync(
    patient_id: str,
    question: str,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Synchronous version of query_agent for non-async contexts.

    Args:
        patient_id: Patient identifier
        question: Doctor's natural-language question
        limit: Maximum number of historical visits to retrieve

    Returns:
        Dictionary with answer, sources, and metadata
    """
    print(f"[QUERY AGENT] Processing question: '{question}'")

    try:
        qdrant = get_qdrant_client()

        # Retrieve relevant patient data
        if patient_id:
            print(f"   Retrieving history for patient {patient_id}...")
            history = qdrant.get_patient_history(
                patient_id=patient_id,
                limit=limit
            )
        else:
            print(f"   Searching across all patients...")
            history = qdrant.search_similar_cases(
                query_text=question,
                limit=limit,
                score_threshold=0.5
            )

        if not history:
            return {
                "success": True,
                "answer": "No relevant patient data found to answer this question.",
                "sources": [],
                "question": question,
                "patient_id": patient_id
            }

        print(f"   SUCCESS: Retrieved {len(history)} relevant record(s)")

        # Create context
        context = create_context_from_history(history)

        # Generate answer
        llm = get_groq_llm(
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )

        chain = QUERY_PROMPT | llm | StrOutputParser()

        print(f"   Generating answer with Groq LLM...")
        answer = chain.invoke({
            "question": question,
            "context": context
        })

        print(f"   SUCCESS: Answer generated successfully")

        return {
            "success": True,
            "answer": answer,
            "sources": [
                {
                    "timestamp": visit.get("timestamp"),
                    "chief_complaint": visit.get("chief_complaint"),
                    "score": visit.get("score", 1.0)
                }
                for visit in history
            ],
            "question": question,
            "patient_id": patient_id,
            "num_sources": len(history)
        }

    except Exception as e:
        error_msg = f"Query agent error: {str(e)}"
        print(f"ERROR: [QUERY AGENT] {error_msg}")
        return {
            "success": False,
            "answer": f"Error processing query: {error_msg}",
            "sources": [],
            "question": question,
            "patient_id": patient_id,
            "error": error_msg
        }
