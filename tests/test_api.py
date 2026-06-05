"""Tests for Flask API endpoints."""

from unittest.mock import MagicMock, patch

import pytest

from app import app, reset_pipeline
from src.guardrails import Citation, RAGResponse


@pytest.fixture
def client():
    app.config["TESTING"] = True
    reset_pipeline()
    with app.test_client() as test_client:
        yield test_client
    reset_pipeline()


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "policy-rag"


def test_index_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Corporate Policy Assistant" in response.data


@patch("app.get_pipeline")
def test_chat_endpoint_returns_answer_snippets_and_citations(mock_get_pipeline, client):
    mock_pipeline = MagicMock()
    mock_pipeline.query.return_value = RAGResponse(
        answer="Employees receive 15 PTO days [pto_and_leave_policy].",
        refused=False,
        citations=[
            Citation(
                source_id="pto_and_leave_policy",
                source_title="Paid Time Off and Leave Policy",
                chunk_index=2,
                excerpt="0-2 years | 15 days (120 hours)",
            )
        ],
    )
    mock_get_pipeline.return_value = mock_pipeline

    response = client.post("/chat", json={"message": "How many PTO days?"})
    assert response.status_code == 200
    data = response.get_json()

    assert "15 PTO days" in data["answer"]
    assert data["refused"] is False
    assert len(data["snippets"]) == 1
    assert data["snippets"][0]["source_id"] == "pto_and_leave_policy"
    assert data["snippets"][0]["text"] == "0-2 years | 15 days (120 hours)"
    assert len(data["citations"]) == 1
    assert data["citations"][0]["source_title"] == "Paid Time Off and Leave Policy"


@patch("app.get_pipeline")
def test_chat_accepts_question_field(mock_get_pipeline, client):
    mock_pipeline = MagicMock()
    mock_pipeline.query.return_value = RAGResponse(
        answer="Refused.",
        refused=True,
        refusal_reason="out_of_scope_keywords",
    )
    mock_get_pipeline.return_value = mock_pipeline

    response = client.post("/chat", json={"question": "What is the capital of France?"})
    assert response.status_code == 200
    assert response.get_json()["refused"] is True


def test_chat_requires_message_or_question(client):
    response = client.post("/chat", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()
