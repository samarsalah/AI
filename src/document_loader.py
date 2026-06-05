"""Load and clean policy documents from the corpus directory."""

import re
from pathlib import Path

from langchain_community.document_loaders import BSHTMLLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document


def _extract_title(text: str, fallback: str) -> str:
    """Extract the first Markdown H1 heading as the document title."""
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def _clean_text(text: str) -> str:
    """Normalize whitespace and strip boilerplate artifacts."""
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _source_id_from_path(path: Path) -> str:
    return path.stem


def _humanize_filename(stem: str) -> str:
    return stem.replace("_", " ").title()


def load_corpus(corpus_dir: Path | str) -> list[Document]:
    """Load all supported files (.md, .txt, .pdf, .html) from the corpus directory."""
    corpus_dir = Path(corpus_dir)
    if not corpus_dir.exists():
        raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")

    documents: list[Document] = []
    patterns = ("*.md", "*.txt", "*.pdf", "*.html", "*.htm")

    for pattern in patterns:
        for path in sorted(corpus_dir.glob(pattern)):
            suffix = path.suffix.lower()
            if suffix == ".pdf":
                loader = PyPDFLoader(str(path))
                raw_docs = loader.load()
                combined = _clean_text("\n\n".join(d.page_content for d in raw_docs))
                title = _humanize_filename(path.stem)
            elif suffix in (".html", ".htm"):
                loader = BSHTMLLoader(str(path), bs_kwargs={"features": "html.parser"})
                raw_docs = loader.load()
                combined = _clean_text(raw_docs[0].page_content)
                title = _extract_title(combined, _humanize_filename(path.stem))
            else:
                loader = TextLoader(str(path), encoding="utf-8")
                raw_docs = loader.load()
                combined = _clean_text(raw_docs[0].page_content)
                title = _extract_title(combined, _humanize_filename(path.stem))

            source_id = _source_id_from_path(path)
            documents.append(
                Document(
                    page_content=combined,
                    metadata={
                        "source_id": source_id,
                        "source_title": title,
                        "source_file": path.name,
                        "source_path": str(path),
                    },
                )
            )

    if not documents:
        raise ValueError(f"No supported documents found in {corpus_dir}")

    return documents
