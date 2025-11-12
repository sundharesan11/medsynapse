"""
Clinical Summary Agent

This agent generates a concise clinical summary from structured patient data.
It identifies key findings, risk factors, and areas requiring medical attention.
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from models.schemas import GraphState, ClinicalSummary
from utils.groq_client import get_summary_llm


SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert clinical summarizer. Create a concise, accurate clinical summary from structured patient data.

Your summary should:
1. Be clear and professional
2. Highlight the most important clinical information
3. Identify potential risk factors
4. Suggest areas that need clinical focus

Return ONLY a valid JSON object:
{{
    "concise_summary": "2-3 sentence clinical summary",
    "key_findings": ["finding1", "finding2"],
    "risk_factors": ["risk1", "risk2"],
    "suggested_focus_areas": ["area1", "area2"]
}}

Be objective and evidence-based. Only include information provided in the patient data."""),
    ("human", """Patient Data:
- Chief Complaint: {chief_complaint}
- Symptoms: {symptoms}
- Duration: {duration}
- Severity: {severity}
- Medical History: {medical_history}
- Medications: {medications}
- Allergies: {allergies}
- Vital Signs: {vital_signs}

Generate clinical summary:""")
])


def summary_agent(state: GraphState) -> Dict[str, Any]:
    """
    Generate a clinical summary from structured patient data.

    This is the SECOND node in the graph. It takes the structured data
    from the intake agent and produces a concise clinical summary.

    Args:
        state: Current graph state containing structured_data

    Returns:
        Dictionary with updated state (adds clinical_summary field)
    """
    print("📋 [SUMMARY AGENT] Generating clinical summary...")

    if not state.structured_data:
        return {
            "errors": ["No structured data available for summarization"],
            "current_step": "summary_failed"
        }

    data = state.structured_data

    try:
        llm = get_summary_llm()
        parser = JsonOutputParser()
        chain = SUMMARY_PROMPT | llm | parser

        # Prepare input data
        input_data = {
            "chief_complaint": data.chief_complaint,
            "symptoms": ", ".join(data.symptoms) if data.symptoms else "None reported",
            "duration": data.duration or "Not specified",
            "severity": data.severity or "Not specified",
            "medical_history": ", ".join(data.medical_history) if data.medical_history else "None reported",
            "medications": ", ".join(data.medications) if data.medications else "None",
            "allergies": ", ".join(data.allergies) if data.allergies else "None known",
            "vital_signs": str(data.vital_signs) if data.vital_signs else "Not recorded"
        }

        result = chain.invoke(input_data)
        clinical_summary = ClinicalSummary(**result)

        print(f"✅ [SUMMARY AGENT] Summary generated")
        print(f"   Key findings: {len(clinical_summary.key_findings)}")
        print(f"   Risk factors: {len(clinical_summary.risk_factors)}")

        return {
            "clinical_summary": clinical_summary,
            "current_step": "knowledge"
        }

    except Exception as e:
        error_msg = f"Summary agent error: {str(e)}"
        print(f"❌ [SUMMARY AGENT] {error_msg}")
        return {
            "errors": state.errors + [error_msg],
            "current_step": "summary_failed"
        }
