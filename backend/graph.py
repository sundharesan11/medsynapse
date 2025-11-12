"""
LangGraph Orchestration for Doctor's Intelligent Assistant

This file defines the multi-agent state machine that coordinates:
1. Intake Agent → Extract structured data
2. Summary Agent → Generate clinical summary
3. Knowledge Agent → Retrieve relevant medical knowledge
4. Report Agent → Generate SOAP report

The graph automatically manages state flow between agents.
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from models.schemas import GraphState
from agents.intake import intake_agent
from agents.summary import summary_agent
from agents.knowledge import knowledge_agent
from agents.report import report_agent
from agents.storage import storage_agent


def create_medical_graph() -> CompiledStateGraph:
    """
    Create and compile the medical assistant LangGraph.

    Graph structure:
        START → intake → summary → knowledge → report → storage → END

    Phase 2: Now includes storage node to save cases in Qdrant

    Returns:
        Compiled state graph ready for execution
    """

    # Create the state graph with our GraphState schema
    workflow = StateGraph(GraphState)

    # Add nodes (each node is an agent)
    workflow.add_node("intake", intake_agent)
    workflow.add_node("summary", summary_agent)
    workflow.add_node("knowledge", knowledge_agent)
    workflow.add_node("report", report_agent)
    workflow.add_node("storage", storage_agent)  # Phase 2: New storage node

    # Define edges (how agents connect)
    # START → intake
    workflow.set_entry_point("intake")

    # intake → summary
    workflow.add_edge("intake", "summary")

    # summary → knowledge
    workflow.add_edge("summary", "knowledge")

    # knowledge → report
    workflow.add_edge("knowledge", "report")

    # report → storage (Phase 2: Store case in Qdrant)
    workflow.add_edge("report", "storage")

    # storage → END
    workflow.add_edge("storage", END)

    # Compile the graph
    # This creates an executable state machine
    app = workflow.compile()

    print("✅ Medical assistant graph compiled successfully")
    print("📊 Graph structure: START → intake → summary → knowledge → report → storage → END")

    return app


# Create a singleton instance
medical_graph = create_medical_graph()


async def process_patient_intake(
    patient_id: str,
    raw_input: str,
    session_id: str = None
) -> GraphState:
    """
    Process a patient intake through the entire multi-agent pipeline.

    This is the main entry point for processing patient data. It:
    1. Creates the initial state with patient intake data
    2. Runs the graph (all agents execute in sequence)
    3. Returns the final state with SOAP report

    Args:
        patient_id: Unique patient identifier
        raw_input: Raw conversational patient intake text
        session_id: Optional session ID for multi-turn conversations

    Returns:
        Final GraphState containing SOAP report and all intermediate outputs

    Example:
        >>> result = await process_patient_intake(
        ...     patient_id="P12345",
        ...     raw_input="Patient complains of chest pain for 2 days..."
        ... )
        >>> print(result.soap_report.subjective)
    """
    from models.schemas import PatientIntakeInput

    # Create initial state
    initial_state = GraphState(
        patient_intake=PatientIntakeInput(
            patient_id=patient_id,
            raw_input=raw_input,
            session_id=session_id
        )
    )

    print(f"\n{'='*60}")
    print(f"🚀 Starting medical intake pipeline for patient {patient_id}")
    print(f"{'='*60}\n")

    # Run the graph
    # LangGraph will automatically execute each node in sequence
    # and manage state updates
    final_state = await medical_graph.ainvoke(initial_state)

    print(f"\n{'='*60}")
    print(f"✅ Pipeline completed for patient {patient_id}")
    print(f"{'='*60}\n")

    return GraphState(**final_state)


# Synchronous version for non-async contexts
def process_patient_intake_sync(
    patient_id: str,
    raw_input: str,
    session_id: str = None
) -> GraphState:
    """
    Synchronous version of process_patient_intake.

    Use this in non-async contexts like testing or scripts.
    """
    from models.schemas import PatientIntakeInput

    initial_state = GraphState(
        patient_intake=PatientIntakeInput(
            patient_id=patient_id,
            raw_input=raw_input,
            session_id=session_id
        )
    )

    print(f"\n{'='*60}")
    print(f"🚀 Starting medical intake pipeline for patient {patient_id}")
    print(f"{'='*60}\n")

    # Synchronous invoke
    final_state = medical_graph.invoke(initial_state)

    print(f"\n{'='*60}")
    print(f"✅ Pipeline completed for patient {patient_id}")
    print(f"{'='*60}\n")

    return GraphState(**final_state)
