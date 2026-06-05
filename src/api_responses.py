"""Serialize RAG pipeline results for API responses."""

from src.guardrails import Citation, RAGResponse


def format_snippets(citations: list[Citation]) -> list[dict]:
    return [
        {
            "source_id": c.source_id,
            "source_title": c.source_title,
            "chunk_index": c.chunk_index,
            "text": c.excerpt,
        }
        for c in citations
    ]


def format_citations(citations: list[Citation]) -> list[dict]:
    return [
        {
            "source_id": c.source_id,
            "source_title": c.source_title,
            "chunk_index": c.chunk_index,
        }
        for c in citations
    ]


def format_chat_response(result: RAGResponse) -> dict:
    return {
        "answer": result.answer,
        "refused": result.refused,
        "refusal_reason": result.refusal_reason,
        "snippets": format_snippets(result.citations),
        "citations": format_citations(result.citations),
    }
