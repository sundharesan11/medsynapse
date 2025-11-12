"""
SOAP Report Generation Agent

This agent generates the final SOAP (Subjective, Objective, Assessment, Plan) report.
It combines all previous agent outputs into a structured clinical report.
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from models.schemas import GraphState, SOAPReport
from utils.groq_client import get_report_llm


REPORT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert medical report writer. Generate a comprehensive SOAP format clinical report.

SOAP Format:
- **Subjective**: Patient's description of symptoms and history (in their words)
- **Objective**: Measurable clinical findings (vitals, observations)
- **Assessment**: Your clinical assessment and differential diagnosis
- **Plan**: Recommended treatment plan and next steps

Return ONLY a valid JSON object:
{{
    "subjective": "Detailed subjective section",
    "objective": "Detailed objective section",
    "assessment": "Detailed assessment section",
    "plan": "Detailed plan section",
    "confidence_level": "high|medium|low",
    "flags": ["flag1", "flag2"]
}}

Include any important alerts in the flags field (e.g., "High blood pressure", "Drug interaction risk").
Be thorough, professional, and clinically accurate."""),
    ("human", """Generate SOAP report from:

PATIENT DATA:
- Patient ID: {patient_id}
- Chief Complaint: {chief_complaint}
- Symptoms: {symptoms}
- Duration: {duration}
- Severity: {severity}
- Medical History: {medical_history}
- Medications: {medications}
- Allergies: {allergies}
- Vital Signs: {vital_signs}

CLINICAL SUMMARY:
{clinical_summary}

KNOWLEDGE CONTEXT:
- Relevant Conditions: {relevant_conditions}
- Guidelines: {clinical_guidelines}
- Confidence: {confidence}

Generate SOAP report:""")
])


def report_agent(state: GraphState) -> Dict[str, Any]:
    """
    Generate final SOAP format clinical report.

    This is the FINAL node in the graph. It combines all previous outputs
    into a comprehensive, structured clinical report.

    Args:
        state: Current graph state with all previous agent outputs

    Returns:
        Dictionary with updated state (adds soap_report field)
    """
    print("[REPORT AGENT] Generating SOAP report...")

    # Validate all required data is present
    if not state.structured_data:
        return {
            "errors": state.errors + ["Missing structured patient data"],
            "current_step": "report_failed"
        }

    if not state.clinical_summary:
        return {
            "errors": state.errors + ["Missing clinical summary"],
            "current_step": "report_failed"
        }

    if not state.knowledge_context:
        return {
            "errors": state.errors + ["Missing knowledge context"],
            "current_step": "report_failed"
        }

    data = state.structured_data
    summary = state.clinical_summary
    knowledge = state.knowledge_context

    try:
        llm = get_report_llm()
        parser = JsonOutputParser()
        chain = REPORT_PROMPT | llm | parser

        # Prepare comprehensive input
        input_data = {
            "patient_id": data.patient_id,
            "chief_complaint": data.chief_complaint,
            "symptoms": ", ".join(data.symptoms) if data.symptoms else "None",
            "duration": data.duration or "Not specified",
            "severity": data.severity or "Not specified",
            "medical_history": ", ".join(data.medical_history) if data.medical_history else "None",
            "medications": ", ".join(data.medications) if data.medications else "None",
            "allergies": ", ".join(data.allergies) if data.allergies else "NKDA (No Known Drug Allergies)",
            "vital_signs": str(data.vital_signs) if data.vital_signs else "Not recorded",
            "clinical_summary": summary.concise_summary,
            "relevant_conditions": ", ".join(knowledge.relevant_conditions),
            "clinical_guidelines": "\n- ".join(knowledge.clinical_guidelines),
            "confidence": f"{knowledge.confidence_score:.0%}"
        }

        result = chain.invoke(input_data)

        soap_report = SOAPReport(
            patient_id=data.patient_id,
            **result
        )

        # Phase 4: Update routing path
        routing_path = state.routing_path + ["report"]

        print(f"SUCCESS: [REPORT AGENT] SOAP report generated for patient {data.patient_id}")
        print(f"   Confidence: {soap_report.confidence_level}")
        print(f"   Flags: {len(soap_report.flags)}")

        return {
            "soap_report": soap_report,
            "current_step": "completed",
            "routing_path": routing_path,
        }

    except Exception as e:
        error_msg = f"Report agent error: {str(e)}"
        print(f"ERROR: [REPORT AGENT] {error_msg}")
        return {
            "errors": state.errors + [error_msg],
            "current_step": "report_failed"
        }
