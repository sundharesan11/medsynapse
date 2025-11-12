"""
Groq LLM client utility.

Provides a configured ChatGroq instance for all agents to use.
Groq offers extremely fast inference with models like Llama 3 and Mixtral.
"""

import os
from typing import Optional
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()


def get_groq_llm(
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.1,
    max_tokens: Optional[int] = None,
) -> ChatGroq:
    """
    Get a configured Groq LLM instance.

    Args:
        model: Groq model name. Options:
            - "llama-3.3-70b-versatile" (default, best for complex reasoning)
            - "llama-3.1-8b-instant" (faster, good for simple tasks)
            - "mixtral-8x7b-32768" (large context window)
            - "gemma2-9b-it" (efficient, good balance)
        temperature: Randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response (None = model default)

    Returns:
        Configured ChatGroq instance ready for agent use
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment. "
            "Get your key from https://console.groq.com/keys"
        )

    return ChatGroq(
        groq_api_key=api_key,
        model_name=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


# Specialized LLM instances for different agent needs
def get_intake_llm() -> ChatGroq:
    """Get LLM optimized for patient intake (precise extraction)."""
    return get_groq_llm(
        model="llama-3.3-70b-versatile",
        temperature=0.0,  # Deterministic for data extraction
    )


def get_summary_llm() -> ChatGroq:
    """Get LLM optimized for clinical summarization."""
    return get_groq_llm(
        model="llama-3.3-70b-versatile",
        temperature=0.2,  # Slightly creative for natural summaries
    )


def get_knowledge_llm() -> ChatGroq:
    """Get LLM optimized for knowledge retrieval."""
    return get_groq_llm(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
    )


def get_report_llm() -> ChatGroq:
    """Get LLM optimized for SOAP report generation."""
    return get_groq_llm(
        model="llama-3.3-70b-versatile",
        temperature=0.0,  # Deterministic for structured reports
        max_tokens=2000,  # Reports can be long
    )
