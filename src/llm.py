"""LLM client factory supporting OpenAI, Groq, and OpenRouter."""

from langchain_openai import ChatOpenAI

from src.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_MODEL,
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    OPENAI_API_KEY,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)


def get_llm() -> ChatOpenAI:
    """Return a ChatOpenAI-compatible client for the configured provider."""
    if LLM_PROVIDER == "groq":
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in the environment.")
        return ChatOpenAI(
            model=GROQ_MODEL,
            temperature=LLM_TEMPERATURE,
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )

    if LLM_PROVIDER == "openrouter":
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set in the environment.")
        return ChatOpenAI(
            model=OPENROUTER_MODEL,
            temperature=LLM_TEMPERATURE,
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set in the environment.")
    return ChatOpenAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        api_key=OPENAI_API_KEY,
        max_tokens=512,
    )
