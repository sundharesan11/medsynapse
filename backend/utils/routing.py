"""
Dynamic Routing Logic for Phase 4

This module contains routing functions that enable conditional orchestration
based on case characteristics, confidence scores, and clinical complexity.
"""

from typing import Literal
from models.schemas import GraphState, StructuredPatientData, KnowledgeContext


# Emergency keywords that trigger high-priority routing
EMERGENCY_KEYWORDS = [
    "chest pain",
    "difficulty breathing",
    "severe bleeding",
    "loss of consciousness",
    "severe head injury",
    "stroke",
    "heart attack",
    "anaphylaxis",
    "severe allergic reaction",
    "difficulty swallowing",
    "sudden vision loss",
    "severe abdominal pain",
]

# Urgent keywords that trigger medium-priority routing
URGENT_KEYWORDS = [
    "moderate pain",
    "persistent vomiting",
    "high fever",
    "confusion",
    "severe headache",
    "shortness of breath",
    "rapid heartbeat",
]


def determine_case_priority(structured_data: StructuredPatientData) -> Literal["routine", "urgent", "emergency"]:
    """
    Determine case priority based on symptoms, severity, and chief complaint.

    This function analyzes the patient data to route cases appropriately:
    - Emergency: Life-threatening symptoms requiring immediate attention
    - Urgent: Serious symptoms needing prompt evaluation
    - Routine: Standard cases that can follow normal processing

    Args:
        structured_data: Structured patient data from intake agent

    Returns:
        Priority level: "routine", "urgent", or "emergency"
    """
    chief_complaint = structured_data.chief_complaint.lower()
    symptoms = [s.lower() for s in structured_data.symptoms]
    severity = structured_data.severity.lower() if structured_data.severity else ""

    # Check for emergency keywords
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in chief_complaint or any(keyword in symptom for symptom in symptoms):
            return "emergency"

    # Check explicit severity markers
    if severity == "severe":
        return "urgent"

    # Check for urgent keywords
    for keyword in URGENT_KEYWORDS:
        if keyword in chief_complaint or any(keyword in symptom for symptom in symptoms):
            return "urgent"

    # Check vital signs for concerning values
    if structured_data.vital_signs:
        vitals = structured_data.vital_signs

        # Blood pressure (systolic > 180 or < 90, diastolic > 120 or < 60)
        if "bp" in vitals or "blood_pressure" in vitals:
            bp_str = vitals.get("bp") or vitals.get("blood_pressure", "")
            if isinstance(bp_str, str) and "/" in bp_str:
                try:
                    systolic, diastolic = map(int, bp_str.split("/"))
                    if systolic > 180 or systolic < 90 or diastolic > 120 or diastolic < 60:
                        return "urgent"
                except (ValueError, AttributeError):
                    pass

        # Heart rate (>120 or <50)
        hr = vitals.get("hr") or vitals.get("heart_rate")
        if hr:
            try:
                hr_int = int(hr)
                if hr_int > 120 or hr_int < 50:
                    return "urgent"
            except (ValueError, TypeError):
                pass

        # Temperature (>103°F or <95°F)
        temp = vitals.get("temp") or vitals.get("temperature")
        if temp:
            try:
                temp_float = float(str(temp).replace("°F", "").replace("F", "").strip())
                if temp_float > 103 or temp_float < 95:
                    return "urgent"
            except (ValueError, TypeError):
                pass

    # Default to routine
    return "routine"


def should_use_enhanced_analysis(state: GraphState) -> bool:
    """
    Determine if case requires enhanced analysis after knowledge retrieval.

    Enhanced analysis is recommended when:
    - Low confidence in knowledge retrieval (<0.5)
    - Complex case with multiple risk factors (>3)
    - No similar historical cases found
    - Conflicting information in the data

    Args:
        state: Current graph state after knowledge agent

    Returns:
        True if enhanced analysis is recommended, False otherwise
    """
    if not state.knowledge_context or not state.clinical_summary:
        return False

    knowledge = state.knowledge_context
    summary = state.clinical_summary

    # Low confidence suggests uncertainty - may need enhanced analysis
    if knowledge.confidence_score < 0.5:
        return True

    # Complex case with many risk factors
    if len(summary.risk_factors) > 3:
        return True

    # No similar cases and low confidence combination
    if not knowledge.similar_cases and knowledge.confidence_score < 0.7:
        return True

    return False


def route_after_knowledge(state: GraphState) -> str:
    """
    Conditional routing function for after knowledge retrieval.

    This is a LangGraph conditional edge function that decides the next node.

    Routes:
    - "report" (default): Proceed to SOAP report generation
    - "enhanced_analysis": Cases needing deeper investigation (future feature)

    Args:
        state: Current graph state

    Returns:
        Next node name
    """
    # For Phase 4 initial release, we'll just flag for enhanced analysis
    # but still route to report. In future phases, we can add actual
    # enhanced_analysis node

    if should_use_enhanced_analysis(state):
        # Set flag but continue to report
        # In a future update, we could route to an enhanced_analysis node
        pass

    return "report"


def get_routing_summary(state: GraphState) -> dict:
    """
    Generate a summary of the routing decisions made for this case.

    Useful for debugging, logging, and displaying to users.

    Args:
        state: Final graph state

    Returns:
        Dictionary with routing information
    """
    return {
        "case_priority": state.case_priority,
        "routing_path": state.routing_path,
        "enhanced_analysis_recommended": state.requires_enhanced_analysis,
        "total_processing_time_ms": state.processing_time_ms,
        "nodes_executed": len(state.routing_path),
    }
