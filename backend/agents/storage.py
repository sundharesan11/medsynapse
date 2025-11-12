"""
Storage Agent

This agent stores the completed case in Qdrant vector database
for future retrieval and similarity search.
"""

from typing import Dict, Any
from models.schemas import GraphState
from utils.qdrant_client import get_qdrant_client


def storage_agent(state: GraphState) -> Dict[str, Any]:
    """
    Store the completed case in Qdrant.

    This is the FINAL node in the graph (after report generation).
    It stores the case with embeddings for future semantic search.

    Args:
        state: Current graph state with complete case data

    Returns:
        Dictionary with updated state
    """
    print("[STORAGE AGENT] Storing case in Qdrant...")

    # Validate all required data is present
    if not state.structured_data or not state.soap_report:
        print("   WARNING: Incomplete case data, skipping storage")
        return {
            "current_step": "completed"
        }

    try:
        qdrant = get_qdrant_client()

        # Prepare case data for storage
        case_data = {
            "chief_complaint": state.structured_data.chief_complaint,
            "symptoms": state.structured_data.symptoms,
            "medical_history": state.structured_data.medical_history,
            "assessment": state.soap_report.assessment,
        }

        # Store in Qdrant
        point_id = qdrant.store_patient_case(
            patient_id=state.structured_data.patient_id,
            case_data=case_data,
            session_id=state.patient_intake.session_id if state.patient_intake else None
        )

        # Phase 4: Update routing path
        routing_path = state.routing_path + ["storage"]

        print(f"SUCCESS: [STORAGE AGENT] Case stored successfully")
        print(f"   Point ID: {point_id}")

        return {
            "current_step": "completed",
            "routing_path": routing_path,
        }

    except Exception as e:
        # Don't fail the entire pipeline if storage fails
        error_msg = f"Storage agent warning: {str(e)}"
        print(f"WARNING: [STORAGE AGENT] {error_msg}")
        print("   Case not stored, but pipeline completed")

        return {
            "current_step": "completed",
            "errors": state.errors + [error_msg]
        }
