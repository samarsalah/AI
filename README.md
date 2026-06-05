# AI Engineering Policy RAG Application

An LLM-powered Retrieval-Augmented Generation (RAG) application that answers user queries based on internal corporate policies and procedures.

## Overview

This project ingests corporate policy documents, chunks and embeds them into a vector store, and uses an LLM to generate accurate, context-grounded answers to employee questions about HR, operations, security, and compliance.

## Project Structure

```
AI/
├── app.py                     # Flask API (/query, /ingest, /health)
├── corpus/                    # Source policy documents (Markdown)
├── scripts/
│   └── ingest_corpus.py       # CLI: parse, chunk, embed, index
├── src/
│   ├── config.py              # Environment & RAG settings
│   ├── document_loader.py     # Parse and clean .md/.txt/.pdf
│   ├── ingest.py              # Chunking + ChromaDB indexing
│   ├── rag_pipeline.py        # Top-k retrieval + prompting
│   ├── guardrails.py          # Scope, length, citation enforcement
│   └── llm.py                 # OpenAI / Groq / OpenRouter client
├── tests/
│   └── test_rag.py
├── requirements.txt
└── README.md
```

## Phase 1 & 2 Completion Checklist

### Phase 1: Setup & Data Prep

| Requirement | Status |
|-------------|--------|
| 5–20 policy documents (MD, HTML, PDF, TXT) | ✅ 9 files in `corpus/` |
| ~30–120 pages of content | ✅ 9 files, ~8,750 words (~30–35 pages) |
| Virtual environment (`venv`) | ✅ |
| `requirements.txt` with dependencies | ✅ |
| `README.md` with setup & run instructions | ✅ |

### Phase 2: Backend & AI Engineering

| Requirement | Status |
|-------------|--------|
| Parse and clean policy documents | ✅ `src/document_loader.py` |
| Chunk text and embed (free-tier model) | ✅ `all-MiniLM-L6-v2` (local, free) |
| Store vectors in ChromaDB | ✅ `chroma_db/` |
| Top-k retrieval system | ✅ `PolicyRAGPipeline.retrieve()` |
| Prompt with chunks + citations | ✅ `src/rag_pipeline.py` |
| Refuse out-of-scope questions | ✅ `src/guardrails.py` |
| Limit output length | ✅ 300 words / 512 tokens |
| Cite source IDs and titles | ✅ inline `[source_id]` + citation objects |

## Corpus

The `corpus/` directory contains nine corporate policy documents (Markdown and HTML) written for RAG ingestion.

| Document | Format | Topics |
|----------|--------|--------|
| `pto_and_leave_policy.md` | Markdown | Vacation accrual, sick leave, parental leave |
| `remote_work_policy.md` | Markdown | Core hours, stipends, security protocols |
| `expense_reimbursement.md` | Markdown | Travel tiers, meal allowances, approvals |
| `information_security.md` | Markdown | Passwords, 2FA, data handling, clean desk |
| `code_of_conduct.md` | Markdown | Anti-harassment, conflicts of interest, reporting |
| `benefits_and_compensation_policy.md` | Markdown | Health, 401(k), compensation bands |
| `performance_management_policy.md` | Markdown | Goals, ratings, PIPs, promotions |
| `data_privacy_policy.md` | Markdown | GDPR, CCPA, DSRs, data handling |
| `acceptable_use_policy.html` | HTML | IT acceptable use, email, BYOD |

## Prerequisites

- Python 3.10–3.13 (3.11 or 3.12 recommended)
- Git
- An LLM API key (OpenAI, Groq, or OpenRouter)

## Installation

```bash
git clone <your-repo-url>
cd AI

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Embeddings are FREE and local (sentence-transformers) — no key needed

# LLM — pick ONE provider:
OPENAI_API_KEY=your_key_here
# LLM_PROVIDER=groq
# GROQ_API_KEY=your_key_here
# LLM_PROVIDER=openrouter
# OPENROUTER_API_KEY=your_key_here
```

## Phase 2 — Process, Index & Query

### 1. Index the corpus

```bash
python scripts/ingest_corpus.py
```

This will:
- Parse and clean all files in `corpus/`
- Chunk text (1000 chars, 200 overlap) respecting Markdown headings
- Embed chunks with **free local** `all-MiniLM-L6-v2` (no API key)
- Store vectors in `chroma_db/`

### 2. Start the API

```bash
python app.py
```

### 3. Ask a question

```bash
curl -X POST http://localhost:5000/query ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"How many PTO days do new employees get?\"}"
```

Example response:

```json
{
  "answer": "Employees with 0–2 years of tenure receive 15 PTO days (120 hours) per year [pto_and_leave_policy].",
  "refused": false,
  "refusal_reason": "",
  "citations": [
    {
      "source_id": "pto_and_leave_policy",
      "source_title": "Paid Time Off and Leave Policy",
      "chunk_index": 2,
      "excerpt": "..."
    }
  ]
}
```

## RAG Pipeline Features

| Feature | Implementation |
|---------|----------------|
| **Top-k retrieval** | `similarity_search_with_relevance_scores`, default k=4 |
| **Citation injection** | Context blocks tagged with `[SOURCE_ID: ...]`; LLM instructed to cite inline |
| **Scope guardrail** | Keyword filter + minimum relevance score (0.25) |
| **Out-of-scope refusal** | Returns standard refusal message without calling LLM |
| **Output length limit** | Max 300 words / 512 tokens |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/query` | Ask a policy question |
| POST | `/ingest` | Rebuild vector index from corpus |

## Run Tests

```bash
pytest tests/ -v
```

## Tech Stack

- **Flask** — Web API
- **LangChain** — RAG orchestration
- **ChromaDB** — Local vector store
- **sentence-transformers** — Free local embeddings
- **OpenAI / Groq / OpenRouter** — LLM completions
- **Pytest** — Testing

## License

Internal use only.
