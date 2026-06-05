"""Flask API for the policy RAG assistant."""

from flask import Flask, jsonify, request
from pydantic import BaseModel, Field

from src.ingest import build_vector_store, load_vector_store
from src.rag_pipeline import PolicyRAGPipeline

app = Flask(__name__)
_pipeline: PolicyRAGPipeline | None = None


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


def get_pipeline() -> PolicyRAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = PolicyRAGPipeline(vector_store=load_vector_store())
    return _pipeline


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "policy-rag"})


@app.route("/query", methods=["POST"])
def query():
    try:
        payload = QueryRequest.model_validate(request.get_json(force=True))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        result = get_pipeline().query(payload.question)
    except FileNotFoundError:
        return jsonify(
            {
                "error": "Vector index not found. Run: python scripts/ingest_corpus.py"
            }
        ), 503
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 503

    return jsonify(
        {
            "answer": result.answer,
            "refused": result.refused,
            "refusal_reason": result.refusal_reason,
            "citations": [
                {
                    "source_id": c.source_id,
                    "source_title": c.source_title,
                    "chunk_index": c.chunk_index,
                    "excerpt": c.excerpt,
                }
                for c in result.citations
            ],
        }
    )


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
    app.run(host="0.0.0.0", port=5000, debug=True)
