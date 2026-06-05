"""CI build/start check — verifies the app imports and core endpoints respond."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app
from src.guardrails import RAGResponse


def main() -> None:
    client = app.test_client()

    health = client.get("/health")
    assert health.status_code == 200, health.get_data(as_text=True)
    assert health.get_json()["status"] == "ok"
    print("OK  GET /health")

    index = client.get("/")
    assert index.status_code == 200, index.get_data(as_text=True)
    print("OK  GET / (web UI)")

    mock_result = RAGResponse(answer="Build check answer.", refused=False)
    with patch("app.get_pipeline") as mock_get_pipeline:
        mock_get_pipeline.return_value.query.return_value = mock_result
        chat = client.post("/chat", json={"message": "build check"})
        assert chat.status_code == 200, chat.get_data(as_text=True)
        body = chat.get_json()
        assert "answer" in body
        assert "snippets" in body
        assert "citations" in body
    print("OK  POST /chat")

    print("Build check passed.")


if __name__ == "__main__":
    main()
