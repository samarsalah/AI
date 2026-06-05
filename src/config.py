"""Application configuration loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = Path(os.getenv("CORPUS_DIR", PROJECT_ROOT / "corpus"))
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", PROJECT_ROOT / "chroma_db"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "policy_corpus")

# Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Retrieval
TOP_K = int(os.getenv("TOP_K", "4"))
MIN_RELEVANCE_SCORE = float(os.getenv("MIN_RELEVANCE_SCORE", "0.25"))

# Guardrails
MAX_RESPONSE_WORDS = int(os.getenv("MAX_RESPONSE_WORDS", "300"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "512"))

# Embeddings — free local model (sentence-transformers)
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

# LLM provider
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"
)

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))

# Policy scope keywords used for lightweight guardrail checks
CORPUS_SCOPE_KEYWORDS = [
    "policy",
    "leave",
    "pto",
    "vacation",
    "sick",
    "parental",
    "remote",
    "work from home",
    "expense",
    "reimbursement",
    "travel",
    "security",
    "password",
    "mfa",
    "data",
    "privacy",
    "conduct",
    "harassment",
    "conflict of interest",
    "bereavement",
    "holiday",
    "stipend",
    "meal",
    "approval",
    "report",
    "employee",
    "manager",
    "hr",
    "benefits",
    "compensation",
    "401k",
    "performance",
    "rating",
    "promotion",
    "acceptable use",
    "byod",
    "vpn",
]

REFUSAL_MESSAGE = (
    "I can only answer questions about the corporate policies in our knowledge base "
    "(PTO & leave, remote work, expense reimbursement, information security, and code "
    "of conduct). Your question appears to be outside that scope or I could not find "
    "relevant policy content. Please rephrase or ask about a covered policy topic."
)
