"""Embedding backends — ONNX default for low memory (Render free tier)."""

import os

from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from langchain_core.embeddings import Embeddings

from src.config import EMBEDDING_MODEL


class OnnxEmbeddings(Embeddings):
    """Lightweight local embeddings via ONNX Runtime (no PyTorch)."""

    def __init__(self):
        self._model = ONNXMiniLM_L6_V2()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._model(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._model([text])[0]


def get_embeddings() -> Embeddings:
    """Return embedding model. Use ONNX on Render to avoid OOM."""
    backend = os.getenv("EMBEDDING_BACKEND", "onnx").lower()
    if backend == "huggingface":
        from langchain_community.embeddings import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return OnnxEmbeddings()
