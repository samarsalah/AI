"""Guardrails for scope enforcement, output limits, and citation requirements."""

import re
from dataclasses import dataclass, field

from langchain_core.documents import Document

from src.config import (
    CORPUS_SCOPE_KEYWORDS,
    MAX_RESPONSE_WORDS,
    MIN_RELEVANCE_SCORE,
    REFUSAL_MESSAGE,
)


@dataclass
class Citation:
    source_id: str
    source_title: str
    chunk_index: int
    excerpt: str


@dataclass
class GuardrailResult:
    allowed: bool
    message: str = ""
    reason: str = ""


@dataclass
class RAGResponse:
    answer: str
    citations: list[Citation] = field(default_factory=list)
    refused: bool = False
    refusal_reason: str = ""


def is_likely_in_scope(question: str) -> bool:
    """Lightweight keyword check before retrieval."""
    normalized = question.lower()
    return any(keyword in normalized for keyword in CORPUS_SCOPE_KEYWORDS)


def check_retrieval_relevance(scores: list[float]) -> GuardrailResult:
    """Reject if no chunk meets the minimum relevance threshold."""
    if not scores:
        return GuardrailResult(
            allowed=False,
            message=REFUSAL_MESSAGE,
            reason="no_results",
        )

    if max(scores) < MIN_RELEVANCE_SCORE:
        return GuardrailResult(
            allowed=False,
            message=REFUSAL_MESSAGE,
            reason="low_relevance",
        )

    return GuardrailResult(allowed=True)


def build_citations(docs: list[Document]) -> list[Citation]:
    """Extract unique citations from retrieved document chunks."""
    seen: set[tuple[str, int]] = set()
    citations: list[Citation] = []

    for doc in docs:
        source_id = doc.metadata.get("source_id", "unknown")
        chunk_index = int(doc.metadata.get("chunk_index", 0))
        key = (source_id, chunk_index)
        if key in seen:
            continue
        seen.add(key)

        excerpt = doc.page_content.strip()
        if len(excerpt) > 240:
            excerpt = excerpt[:240].rstrip() + "..."

        citations.append(
            Citation(
                source_id=source_id,
                source_title=doc.metadata.get("source_title", source_id),
                chunk_index=chunk_index,
                excerpt=excerpt,
            )
        )

    return citations


def enforce_word_limit(text: str, max_words: int = MAX_RESPONSE_WORDS) -> str:
    """Truncate response to the configured word limit."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip() + "..."


def validate_citations_present(answer: str, citations: list[Citation]) -> str:
    """Ensure at least one source_id appears in the answer; append if missing."""
    if not citations:
        return answer

    cited_ids = {c.source_id for c in citations}
    found = any(
        re.search(rf"\[{re.escape(source_id)}\]", answer, re.IGNORECASE)
        or source_id.lower() in answer.lower()
        for source_id in cited_ids
    )

    if found:
        return answer

    source_list = ", ".join(
        f"[{c.source_id}] {c.source_title}" for c in citations
    )
    return f"{answer.rstrip()}\n\nSources: {source_list}"


def format_context_block(docs: list[Document]) -> str:
    """Format retrieved chunks with explicit source tags for the LLM prompt."""
    blocks: list[str] = []
    for doc in docs:
        source_id = doc.metadata.get("source_id", "unknown")
        source_title = doc.metadata.get("source_title", source_id)
        chunk_index = doc.metadata.get("chunk_index", 0)
        blocks.append(
            f"[SOURCE_ID: {source_id} | TITLE: {source_title} | CHUNK: {chunk_index}]\n"
            f"{doc.page_content.strip()}"
        )
    return "\n\n---\n\n".join(blocks)
