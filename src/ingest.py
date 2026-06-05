"""Build embeddings and persist chunked documents in ChromaDB."""

import shutil
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    CORPUS_DIR,
)
from src.document_loader import load_corpus
from src.embeddings import get_embeddings


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Split documents into overlapping chunks while preserving source metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        length_function=len,
    )

    chunks: list[Document] = []
    for doc in documents:
        doc_chunks = splitter.split_documents([doc])
        for index, chunk in enumerate(doc_chunks):
            chunk.metadata = {
                **doc.metadata,
                "chunk_index": index,
            }
            chunks.append(chunk)

    return chunks


def build_vector_store(
    persist_directory: str | None = None,
    corpus_dir: str | None = None,
) -> Chroma:
    """Load corpus, chunk, embed, and index into ChromaDB."""
    persist_path = persist_directory or str(CHROMA_DIR)
    corpus_path = corpus_dir or str(CORPUS_DIR)

    documents = load_corpus(corpus_path)
    chunks = chunk_documents(documents)
    embeddings = get_embeddings()

    persist = Path(persist_path)
    if persist.exists():
        shutil.rmtree(persist)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=persist_path,
    )

    return vector_store


def load_vector_store(persist_directory: str | None = None) -> Chroma:
    """Load an existing ChromaDB index from disk."""
    persist_path = persist_directory or str(CHROMA_DIR)
    embeddings = get_embeddings()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=persist_path,
    )
