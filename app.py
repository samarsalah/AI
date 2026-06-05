"""Flask web app and API for the policy RAG assistant."""

import logging
import os

from flask import Flask, jsonify, render_template, request
from pydantic import BaseModel, Field, model_validator

from src.api_responses import format_chat_response
from src.ingest import build_vector_store, load_vector_store
from src.rag_pipeline import PolicyRAGPipeline

app = Flask(__name__)
logger = logging.getLogger(__name__)
_pipeline: PolicyRAGPipeline | None = None


class ChatRequest(BaseModel):
    message: str | None = Field(default=None, max_length=1000)
    question: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def require_message_or_question(self):
        if not (self.message or self.question):
            raise ValueError("Provide 'message' or 'question' in the request body.")
        return self

    @property
    def text(self) -> str:
        return (self.message or self.question or "").strip()


def get_pipeline() -> PolicyRAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = PolicyRAGPipeline(vector_store=load_vector_store())
    return _pipeline


def reset_pipeline() -> None:
    """Clear cached pipeline (used in tests)."""
    global _pipeline
    _pipeline = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "policy-rag"})


@app.route("/chat", methods=["POST"])
def chat():
    try:
        payload = ChatRequest.model_validate(request.get_json(force=True))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        result = get_pipeline().query(payload.text)
    except FileNotFoundError:
        return jsonify(
            {
                "error": "Vector index not found. Run: python scripts/ingest_corpus.py"
            }
        ), 503
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception as exc:
        logger.exception("Chat request failed")
        return jsonify({"error": f"Server error: {exc}"}), 500

    return jsonify(format_chat_response(result))


def preload_pipeline() -> None:
    """Warm up the RAG pipeline on startup to avoid first-request timeouts."""
    if os.getenv("PRELOAD_PIPELINE", "true").lower() != "true":
        return
    if not os.getenv("RENDER"):
        return
    try:
        get_pipeline()
        logger.info("RAG pipeline preloaded successfully")
    except Exception as exc:
        logger.warning("Pipeline preload failed: %s", exc)


preload_pipeline()


@app.route("/query", methods=["POST"])
def query():
    """Backward-compatible alias for /chat."""
    return chat()


@app.route("/ingest", methods=["POST"])
def ingest():
    """Rebuild the vector index from the corpus (admin/dev endpoint)."""
    try:
        vector_store = build_vector_store()
        global _pipeline
        _pipeline = PolicyRAGPipeline(vector_store=vector_store)
        count = vector_store._collection.count()
        return jsonify({"status": "indexed", "chunk_count": count})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
