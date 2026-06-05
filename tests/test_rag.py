"""Tests for document loading, guardrails, and chunking."""

from pathlib import Path

import pytest

from src.config import REFUSAL_MESSAGE
from src.document_loader import load_corpus
from src.guardrails import (
    build_citations,
    check_retrieval_relevance,
    enforce_word_limit,
    is_likely_in_scope,
    validate_citations_present,
)
from src.ingest import chunk_documents

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"


def test_load_corpus_finds_required_documents():
    docs = load_corpus(CORPUS_DIR)
    assert len(docs) >= 5
    ids = {d.metadata["source_id"] for d in docs}
    assert "pto_and_leave_policy" in ids
    assert "code_of_conduct" in ids
    assert "acceptable_use_policy" in ids


def test_chunks_preserve_source_metadata():
    docs = load_corpus(CORPUS_DIR)
    chunks = chunk_documents(docs)
    assert len(chunks) > 5
    for chunk in chunks:
        assert "source_id" in chunk.metadata
        assert "source_title" in chunk.metadata
        assert "chunk_index" in chunk.metadata


def test_in_scope_question():
    assert is_likely_in_scope("How many PTO days do I get?") is True
    assert is_likely_in_scope("What is the remote work stipend?") is True


def test_out_of_scope_question():
    assert is_likely_in_scope("What is the capital of France?") is False
    assert is_likely_in_scope("Write me a Python sorting algorithm") is False


def test_relevance_guardrail_rejects_low_scores():
    result = check_retrieval_relevance([0.1, 0.05])
    assert result.allowed is False
    assert result.message == REFUSAL_MESSAGE


def test_relevance_guardrail_accepts_good_scores():
    result = check_retrieval_relevance([0.8, 0.5])
    assert result.allowed is True


def test_enforce_word_limit():
    text = " ".join(["word"] * 400)
    limited = enforce_word_limit(text, max_words=50)
    assert len(limited.split()) == 50
    assert limited.endswith("...")


def test_validate_citations_appends_sources_when_missing():
    from langchain_core.documents import Document

    docs = [
        Document(
            page_content="Sample policy text.",
            metadata={
                "source_id": "pto_and_leave_policy",
                "source_title": "Paid Time Off and Leave Policy",
                "chunk_index": 0,
            },
        )
    ]
    citations = build_citations(docs)
    answer = "You receive 15 PTO days after probation."
    updated = validate_citations_present(answer, citations)
    assert "pto_and_leave_policy" in updated
