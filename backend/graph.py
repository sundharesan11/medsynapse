"""
LangGraph Orchestration for Doctor's Intelligent Assistant

This file defines the multi-agent state machine that coordinates:
1. Intake Agent → Extract structured data
2. Memory Agent → Retrieve patient history (Phase 5)
3. Summary Agent → Generate clinical summary
4. Knowledge Agent → Retrieve relevant medical knowledge
5. Report Agent → Generate SOAP report
6. Storage Agent → Store case in Qdrant

Phase 4: Enhanced with dynamic routing and conditional orchestration
Phase 5: Added memory agent for patient history retrieval
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
import time

from models.schemas import GraphState
from agents.intake import intake_agent
from agents.memory import memory_agent  # Phase 5: New memory agent
from agents.summary import summary_agent
from agents.knowledge import knowledge_agent
from agents.report import report_agent
from agents.storage import storage_agent
from utils.routing import route_after_knowledge


def create_medical_graph() -> CompiledStateGraph:
    """
    Create and compile the medical assistant LangGraph.

    Graph structure (Phase 5 with memory agent):
        START → intake → memory → summary → knowledge → [conditional] → report → storage → END

    Phase 2: Includes storage node to save cases in Qdrant
    Phase 4: Dynamic routing based on case characteristics and confidence
    Phase 5: Memory agent retrieves patient history after intake

    The conditional routing after knowledge can:
    - Route to report (standard path)
    - Flag cases for enhanced analysis (future: route to enhanced_analysis node)

    Returns:
        Compiled state graph ready for execution
    """

    # Create the state graph with our GraphState schema
    workflow = StateGraph(GraphState)

    # Add nodes (each node is an agent)
    workflow.add_node("intake", intake_agent)
    workflow.add_node("memory", memory_agent)  # Phase 5: New node
    workflow.add_node("summary", summary_agent)
    workflow.add_node("knowledge", knowledge_agent)
    workflow.add_node("report", report_agent)
    workflow.add_node("storage", storage_agent)

    # Define edges (how agents connect)
    # START → intake
    workflow.set_entry_point("intake")

    # intake → memory (Phase 5: Retrieve patient history after intake)
    workflow.add_edge("intake", "memory")

    # memory → summary (fixed edge)
    workflow.add_edge("memory", "summary")

    # summary → knowledge (fixed edge)
    workflow.add_edge("summary", "knowledge")

    # Phase 4: Conditional routing after knowledge
    # For now, this always routes to "report", but the logic is in place
    # to support more complex routing in the future
    workflow.add_conditional_edges(
        "knowledge",
        route_after_knowledge,
        {
            "report": "report",
            # "enhanced_analysis" route here
        }
    )

    # report → storage (fixed edge)
    workflow.add_edge("report", "storage")

    # storage → END
    workflow.add_edge("storage", END)

    # Compile the graph
    # This creates an executable state machine
    app = workflow.compile()

    print("SUCCESS: Medical assistant graph compiled successfully (Phase 5)")
    print("Graph structure: START -> intake -> memory -> summary -> knowledge -> [conditional] -> report -> storage -> END")
    print("Features: Dynamic routing, patient history retrieval, enhanced analysis flagging")

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
    2. Runs the graph (all agents execute based on routing logic)
    3. Returns the final state with SOAP report and routing metadata

    Phase 4: Now tracks processing time and routing path

    Args:
        patient_id: Unique patient identifier
        raw_input: Raw conversational patient intake text
        session_id: Optional session ID for multi-turn conversations

    Returns:
        Final GraphState containing SOAP report, routing info, and all intermediate outputs

    Example:
        >>> result = await process_patient_intake(
        ...     patient_id="P12345",
        ...     raw_input="Patient complains of chest pain for 2 days..."
        ... )
        >>> print(result.soap_report.subjective)
        >>> print(f"Priority: {result.case_priority}")
        >>> print(f"Path: {' → '.join(result.routing_path)}")
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
    print(f"Starting medical intake pipeline for patient {patient_id}")
    print(f"{'='*60}\n")

    # Track processing time
    start_time = time.time()

    # Run the graph
    # LangGraph will execute nodes based on conditional routing logic
    # and manage state updates
    final_state = await medical_graph.ainvoke(initial_state)

    # Calculate processing time
    processing_time_ms = (time.time() - start_time) * 1000

    # Update final state with processing time
    final_state["processing_time_ms"] = processing_time_ms

    print(f"\n{'='*60}")
    print(f"SUCCESS: Pipeline completed for patient {patient_id}")
    print(f"Processing time: {processing_time_ms:.2f}ms")
    print(f"Priority: {final_state.get('case_priority', 'routine').upper()}")
    print(f"Path: {' -> '.join(final_state.get('routing_path', []))}")
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

    Phase 4: Now tracks processing time and routing path
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
    print(f"Starting medical intake pipeline for patient {patient_id}")
    print(f"{'='*60}\n")

    # Track processing time
    start_time = time.time()

    # Synchronous invoke
    final_state = medical_graph.invoke(initial_state)

    # Calculate processing time
    processing_time_ms = (time.time() - start_time) * 1000
    final_state["processing_time_ms"] = processing_time_ms

    print(f"\n{'='*60}")
    print(f"SUCCESS: Pipeline completed for patient {patient_id}")
    print(f"Processing time: {processing_time_ms:.2f}ms")
    print(f"Priority: {final_state.get('case_priority', 'routine').upper()}")
    print(f"Path: {' -> '.join(final_state.get('routing_path', []))}")
    print(f"{'='*60}\n")

    return GraphState(**final_state)
