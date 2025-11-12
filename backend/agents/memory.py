"""
Patient Memory Agent

This agent retrieves a patient's historical SOAP reports and summaries from Qdrant.
It runs after the intake agent to provide context about the patient's medical history.

Phase 5: New agent for patient memory retrieval
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from models.schemas import GraphState
from utils.qdrant_client import get_qdrant_client


def memory_agent(state: GraphState) -> Dict[str, Any]:
    """
    Retrieve patient's historical medical records from Qdrant.

    This agent runs after the intake agent to fetch the patient's prior
    SOAP reports and provide historical context for the current visit.

    Args:
        state: Current graph state containing patient_intake with patient_id

    Returns:
        Dictionary with updated state (adds patient_history field to knowledge_context)
    """
    print("[MEMORY AGENT] Retrieving patient history...")

    if not state.patient_intake or not state.patient_intake.patient_id:
        print("   WARNING: No patient ID provided, skipping history retrieval")
        return {
            "current_step": "summary",
            "routing_path": state.routing_path + ["memory"]
        }

    patient_id = state.patient_intake.patient_id

    try:
        qdrant = get_qdrant_client()

        # Retrieve patient's historical cases
        history = qdrant.get_patient_history(
            patient_id=patient_id,
            limit=10  # Get last 10 visits
        )

        if not history:
            print(f"   No previous history found for patient {patient_id}")
            print("   -> This appears to be the patient's first visit")
        else:
            print(f"   Retrieved {len(history)} previous visits for patient {patient_id}")
            # Show most recent visit
            if history:
                recent = history[0]
                print(f"   -> Most recent: {recent.get('timestamp', 'Unknown date')}")
                print(f"   -> Chief complaint: {recent.get('chief_complaint', 'N/A')}")

        # Store history in state for downstream agents to use
        # We'll add this to the GraphState schema
        return {
            "patient_history": history,  # List of previous visits
            "current_step": "summary",
            "routing_path": state.routing_path + ["memory"]
        }

    except Exception as e:
        error_msg = f"Memory agent error: {str(e)}"
        print(f"ERROR: [MEMORY AGENT] {error_msg}")
        # Don't fail the pipeline if history retrieval fails
        # Just log the error and continue
        print("   -> Continuing without patient history")
        return {
            "patient_history": [],
            "current_step": "summary",
            "routing_path": state.routing_path + ["memory"],
            "errors": state.errors + [error_msg]
        }


def get_patient_history_summary(history: List[Dict[str, Any]]) -> str:
    """
    Create a human-readable summary of patient's medical history.

    This is useful for including in prompts to downstream agents.

    Args:
        history: List of previous visits from Qdrant

    Returns:
        Formatted string summary of patient history
    """
    if not history:
        return "No previous visit history available for this patient."

    summary_parts = []
    summary_parts.append(f"Patient has {len(history)} previous visit(s):\n")

    for i, visit in enumerate(history[:5], 1):  # Show last 5 visits
        timestamp = visit.get("timestamp", "Unknown date")
        # Parse ISO timestamp to readable format
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_str = dt.strftime("%B %d, %Y")
        except:
            date_str = timestamp

        chief_complaint = visit.get("chief_complaint", "N/A")
        assessment = visit.get("assessment", "N/A")

        # Truncate long assessments
        if len(assessment) > 150:
            assessment = assessment[:150] + "..."

        summary_parts.append(f"\n{i}. {date_str}")
        summary_parts.append(f"   Chief Complaint: {chief_complaint}")
        summary_parts.append(f"   Assessment: {assessment}")

    if len(history) > 5:
        summary_parts.append(f"\n... and {len(history) - 5} more visit(s)")

    return "\n".join(summary_parts)


async def get_patient_history_standalone(patient_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Standalone function to retrieve patient history (for API endpoints).

    This can be called directly from API endpoints without going through
    the LangGraph workflow.

    Args:
        patient_id: Patient identifier
        limit: Maximum number of visits to retrieve

    Returns:
        List of previous visits with timestamps, complaints, and assessments
    """
    try:
        qdrant = get_qdrant_client()
        history = qdrant.get_patient_history(patient_id=patient_id, limit=limit)
        return history
    except Exception as e:
        print(f"Error retrieving patient history: {e}")
        return []
