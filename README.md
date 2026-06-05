# AI Engineering Policy RAG Application

An LLM-powered Retrieval-Augmented Generation (RAG) application that answers user queries based on internal corporate policies and procedures.

## Overview

This project ingests corporate policy documents, chunks and embeds them into a vector store, and uses an LLM to generate accurate, context-grounded answers to employee questions about HR, operations, security, and compliance.

## Live Demo

**Web app:** https://policy-rag-tpok.onrender.com

**Health check:** https://policy-rag-tpok.onrender.com/health

**API example:**
```bash
curl -X POST https://policy-rag-tpok.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"How many PTO days do new employees get?\"}"
```

> Free-tier Render services may take 30–60 seconds to wake after idle periods.

## Project Structure

```
AI/
├── app.py                     # Flask web app + API (/chat, /health)
├── templates/
│   └── index.html             # Web UI with question input
├── .github/workflows/ci.yml   # GitHub Actions CI/CD
├── render.yaml                # Render deployment blueprint
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
├── design-and-evaluation.md
├── ai-tooling.md
├── deployed.md
├── demo-script.md
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
| Chunk text and embed (free-tier model) | ✅ ONNX `all-MiniLM-L6-v2` (local, free) |
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

## Repository

https://github.com/samarsalah/AI

## Installation

```bash
git clone https://github.com/samarsalah/AI.git
cd AI

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Embeddings are FREE and local (ONNX MiniLM) — no key needed

# LLM — pick ONE provider:
OPENAI_API_KEY=your_key_here
# LLM_PROVIDER=groq
# GROQ_API_KEY=your_key_here
# LLM_PROVIDER=openrouter
# OPENROUTER_API_KEY=your_key_here
```

## Phase 3: Application & Infrastructure

### Phase 3 Checklist

| Requirement | Status |
|-------------|--------|
| Web UI with text input | ✅ `templates/index.html` at `/` |
| `POST /chat` with answer, snippets, citations | ✅ |
| `GET /health` JSON status | ✅ |
| GitHub Actions on push/PR | ✅ `.github/workflows/ci.yml` |
| Install deps + build/start check in CI | ✅ `pytest` + `scripts/check_build.py` |
| Optional deployment config | ✅ `render.yaml` + `Procfile` |

### Web interface

```bash
python app.py
```

Open http://localhost:5000 — enter a policy question and submit.

### API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web UI |
| GET | `/health` | Health check |
| POST | `/chat` | Ask a question (returns answer, snippets, citations) |
| POST | `/query` | Alias for `/chat` |
| POST | `/ingest` | Rebuild vector index |

**`POST /chat` example:**

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"How many PTO days do new employees get?\"}"
```

**Response:**

```json
{
  "answer": "Employees with 0–2 years receive 15 PTO days [pto_and_leave_policy].",
  "refused": false,
  "refusal_reason": "",
  "snippets": [
    {
      "source_id": "pto_and_leave_policy",
      "source_title": "Paid Time Off and Leave Policy",
      "chunk_index": 2,
      "text": "..."
    }
  ],
  "citations": [
    {
      "source_id": "pto_and_leave_policy",
      "source_title": "Paid Time Off and Leave Policy",
      "chunk_index": 2
    }
  ]
}
```

### CI/CD

GitHub Actions runs on every push and pull request to `main`:

1. Installs dependencies from `requirements.txt`
2. Runs `pytest tests/ -v`
3. Runs `python scripts/check_build.py` (health, UI, and `/chat` smoke test)

### Deploy to Render (optional)

1. Push this repo to GitHub
2. Create a new **Web Service** on [Render](https://render.com) and connect the repo
3. Render will use `render.yaml` automatically, or set manually:
   - **Build:** `pip install -r requirements.txt && python scripts/ingest_corpus.py`
   - **Start:** `python -m gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1`
4. Add environment variables: `GROQ_API_KEY`, `LLM_PROVIDER=groq`
5. Deploy — live at https://policy-rag-tpok.onrender.com

## Phase 2 — Process, Index & Query

### 1. Index the corpus

```bash
python scripts/ingest_corpus.py
```

This will:
- Parse and clean all files in `corpus/`
- Chunk text (1000 chars, 200 overlap) respecting Markdown headings
- Embed chunks with **free local ONNX** `all-MiniLM-L6-v2` (no API key)
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

## Phase 4 — Evaluation & Documentation

| Requirement | Status | Location |
|-------------|--------|----------|
| Test set (15–30 questions) | ✅ 24 questions | `evaluation/test_questions.json` |
| Groundedness + citation metrics | ✅ | `evaluation/results.json` |
| Latency p50/p95 | ✅ p50=1,083ms, p95=7,793ms | `scripts/run_evaluation.py` |
| Architecture + evaluation doc | ✅ | `design-and-evaluation.md` |
| AI tooling doc | ✅ | `ai-tooling.md` |

```bash
EMBEDDING_BACKEND=onnx python scripts/run_evaluation.py
```

## Run Tests

```bash
pytest tests/ -v
```

## Deployed Application

See [deployed.md](deployed.md) for the live URL, endpoints, and Render configuration.

## Tech Stack

- **Flask** — Web API
- **LangChain** — RAG orchestration
- **ChromaDB** — Local vector store
- **ONNX MiniLM-L6-v2** — Free local embeddings (via Chroma ONNX runtime)
- **Groq** — LLM completions (`llama-3.3-70b-versatile`)
- **Gunicorn** — Production WSGI server
- **Pytest** — Testing

## License

Internal use only.
