"""
Knowledge Retrieval Agent

This agent retrieves relevant medical knowledge and context.

Phase 2: Integrates Qdrant for real vector similarity search of patient cases
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from models.schemas import GraphState, KnowledgeContext
from utils.groq_client import get_knowledge_llm
from utils.qdrant_client import get_qdrant_client
from utils.routing import should_use_enhanced_analysis


KNOWLEDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a medical knowledge expert. Based on the clinical summary, identify:

1. Relevant medical conditions that could explain the symptoms
2. Clinical guidelines that should be considered
3. Important differential diagnoses

Return ONLY a valid JSON object:
{{
    "relevant_conditions": ["condition1", "condition2"],
    "clinical_guidelines": ["guideline1", "guideline2"],
    "similar_cases": [],
    "confidence_score": 0.85
}}

Be evidence-based and consider common as well as serious conditions.
Confidence score should be 0.0-1.0 based on how specific the symptoms are."""),
    ("human", """Clinical Summary:
{summary}

Key Findings:
{key_findings}

Risk Factors:
{risk_factors}

Provide relevant medical knowledge:""")
])


def knowledge_agent(state: GraphState) -> Dict[str, Any]:
    """
    Retrieve relevant medical knowledge and context.

    This is the THIRD node in the graph. It analyzes the clinical summary
    and retrieves relevant medical knowledge to inform the final report.

    Phase 2: Now integrates Qdrant vector search for similar historical cases

    Args:
        state: Current graph state containing clinical_summary

    Returns:
        Dictionary with updated state (adds knowledge_context field)
    """
    print("[KNOWLEDGE AGENT] Retrieving medical knowledge...")

    if not state.clinical_summary:
        return {
            "errors": state.errors + ["No clinical summary available"],
            "current_step": "knowledge_failed"
        }

    summary_data = state.clinical_summary
    structured_data = state.structured_data

    try:
        # === PART 1: LLM-based medical knowledge ===
        llm = get_knowledge_llm()
        parser = JsonOutputParser()
        chain = KNOWLEDGE_PROMPT | llm | parser

        input_data = {
            "summary": summary_data.concise_summary,
            "key_findings": "\n- ".join(summary_data.key_findings),
            "risk_factors": "\n- ".join(summary_data.risk_factors) if summary_data.risk_factors else "None identified"
        }

        result = chain.invoke(input_data)

        # === PART 2: Qdrant vector search for similar cases ===
        similar_cases = []
        try:
            qdrant = get_qdrant_client()

            # Create search query from symptoms and chief complaint
            search_query = f"{structured_data.chief_complaint}. Symptoms: {', '.join(structured_data.symptoms)}"

            # Search for similar cases
            similar_cases = qdrant.search_similar_cases(
                query_text=search_query,
                limit=3,
                score_threshold=0.6  # Lower threshold to catch semantic matches
            )

            if similar_cases:
                print(f"   Found {len(similar_cases)} similar cases in history")
                for i, case in enumerate(similar_cases, 1):
                    print(f"      {i}. Score: {case['score']:.2f} | {case['chief_complaint']}")

        except Exception as qdrant_error:
            print(f"   WARNING: Qdrant search failed: {qdrant_error}")
            print("   Continuing without similar case retrieval...")

        # Add similar cases to result
        result["similar_cases"] = similar_cases

        knowledge_context = KnowledgeContext(**result)

        # Phase 4: Update routing path and check if enhanced analysis is needed
        routing_path = state.routing_path + ["knowledge"]

        # Temporarily update state to check if enhanced analysis is needed
        state_data = state.model_dump()
        state_data["knowledge_context"] = knowledge_context
        temp_state = GraphState(**state_data)
        requires_enhanced = should_use_enhanced_analysis(temp_state)

        print(f"SUCCESS: [KNOWLEDGE AGENT] Knowledge retrieved")
        print(f"   Conditions: {len(knowledge_context.relevant_conditions)}")
        print(f"   Guidelines: {len(knowledge_context.clinical_guidelines)}")
        print(f"   Similar cases: {len(knowledge_context.similar_cases)}")
        print(f"   Confidence: {knowledge_context.confidence_score:.2f}")
        if requires_enhanced:
            print(f"   WARNING: Enhanced analysis recommended")

        return {
            "knowledge_context": knowledge_context,
            "current_step": "report",
            "routing_path": routing_path,
            "requires_enhanced_analysis": requires_enhanced,
        }

    except Exception as e:
        error_msg = f"Knowledge agent error: {str(e)}"
        print(f"ERROR: [KNOWLEDGE AGENT] {error_msg}")
        return {
            "errors": state.errors + [error_msg],
            "current_step": "knowledge_failed"
        }

