"""
Patient Intake Agent

This agent extracts structured patient data from conversational/raw text input.
It uses the Groq LLM to parse unstructured patient information into a standardized format.
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from models.schemas import GraphState, StructuredPatientData
from utils.groq_client import get_intake_llm
from utils.routing import determine_case_priority


# The prompt template that guides the LLM's extraction
INTAKE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a medical intake specialist. Your job is to extract structured patient information from conversational text.

Extract the following information:
- Chief complaint (primary reason for visit)
- Symptoms (list all mentioned symptoms)
- Duration (how long symptoms have been present)
- Severity (mild/moderate/severe)
- Medical history (any past conditions mentioned)
- Current medications
- Known allergies
- Vital signs (if mentioned: BP, heart rate, temperature, etc.)

Return ONLY a valid JSON object with these exact fields:
{{
    "chief_complaint": "string",
    "symptoms": ["symptom1", "symptom2"],
    "duration": "string or null",
    "severity": "string or null",
    "medical_history": ["condition1"],
    "medications": ["med1"],
    "allergies": ["allergy1"],
    "vital_signs": {{"bp": "120/80", "hr": 75}} or null
}}

If information is not provided, use empty lists [] or null. Be precise and clinical."""),
    ("human", "Patient intake text:\n\n{raw_input}")
])


def intake_agent(state: GraphState) -> Dict[str, Any]:
    """
    Extract structured patient data from raw intake text.

    This is the FIRST node in the graph. It processes the raw patient input
    and creates a structured representation that downstream agents can use.

    Args:
        state: Current graph state containing patient_intake

    Returns:
        Dictionary with updated state (adds structured_data field)
    """
    print("[INTAKE AGENT] Starting patient data extraction...")

    # Get the raw input from the state
    if not state.patient_intake:
        return {
            "errors": ["No patient intake data provided"],
            "current_step": "intake_failed"
        }

    raw_input = state.patient_intake.raw_input
    patient_id = state.patient_intake.patient_id

    try:
        # Create the LangChain processing chain
        # Chain = Prompt → LLM → JSON Parser
        llm = get_intake_llm()
        parser = JsonOutputParser()

        chain = INTAKE_PROMPT | llm | parser

        # Invoke the chain
        result = chain.invoke({"raw_input": raw_input})

        # Create the structured data object
        structured_data = StructuredPatientData(
            patient_id=patient_id,
            **result
        )

        # Phase 4: Determine case priority for dynamic routing
        case_priority = determine_case_priority(structured_data)

        # Update routing path
        routing_path = state.routing_path + ["intake"]

        print(f"[INTAKE AGENT] Extracted data for patient {patient_id}")
        print(f"   Chief complaint: {structured_data.chief_complaint}")
        print(f"   Symptoms: {', '.join(structured_data.symptoms)}")
        print(f"   Case Priority: {case_priority.upper()}")

        return {
            "structured_data": structured_data,
            "current_step": "summary",
            "case_priority": case_priority,
            "routing_path": routing_path,
        }

    except Exception as e:
        error_msg = f"Intake agent error: {str(e)}"
        print(f"[INTAKE AGENT ERROR] {error_msg}")
        return {
            "errors": [error_msg],
            "current_step": "intake_failed"
        }
