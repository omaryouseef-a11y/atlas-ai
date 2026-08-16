"""Shared, lazy Gemini configuration for legacy CrewAI examples."""

import os


def create_crewai_llm(model: str = "gemini/gemini-3.1-pro-preview"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "NOT_CONFIGURED: GEMINI_API_KEY is required for this optional provider"
        )
    try:
        from crewai import LLM
    except ImportError as exc:
        raise RuntimeError(
            "PROVIDER_UNAVAILABLE: install the 'ai' optional dependency group"
        ) from exc
    return LLM(model=model, api_key=api_key)


def create_langchain_llm(model: str = "gemini-1.5-pro"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "NOT_CONFIGURED: GEMINI_API_KEY is required for this optional provider"
        )
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as exc:
        raise RuntimeError(
            "PROVIDER_UNAVAILABLE: install the 'ai' optional dependency group"
        ) from exc
    return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
