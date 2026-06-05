# AI Tooling Report

**Project:** Corporate Policy RAG Assistant  
**Author:** Samar Salah  
**Date:** June 2026

---

## 1. Overview

This project was built with **Cursor IDE** as the primary development environment, using its built-in AI coding agent (Claude-based) for code generation, debugging, deployment troubleshooting, and documentation. No separate Copilot, ChatGPT, or other AI tools were used outside of Cursor.

---

## 2. Tools Used

| Tool | Role | Usage |
|------|------|-------|
| **Cursor Agent** | Primary coding assistant | Architecture, implementation, debugging, deployment fixes |
| **Cursor Tab/autocomplete** | Inline suggestions | Boilerplate, imports, repetitive edits |
| **Groq API** | Runtime LLM (not a coding tool) | Powers the deployed RAG chat endpoint |

---

## 3. How AI Tools Were Used by Phase

### Phase 1 — Setup & Data Prep

| Task | AI contribution | Human contribution |
|------|-----------------|-------------------|
| Generate 5 policy documents | Agent drafted all five initial policies (~1,200 words each) with tables, procedures, and headings | Reviewed structure, requested corpus for RAG chunking |
| `requirements.txt` | Agent selected and pinned dependencies | Approved Python 3.13 compatibility updates |
| `README.md` | Agent wrote setup instructions and project structure | Requested repo URL and checklist additions |
| Git setup | Agent ran `git init`, `.gitignore`, staging, and commits | Provided GitHub remote URL for push |

**Performance:** Excellent for generating structured Markdown policy content. Minimal edits needed to meet the 30-page corpus target.

### Phase 2 — Backend & AI Engineering

| Task | AI contribution | Human contribution |
|------|-----------------|-------------------|
| Document loader | Agent implemented MD/TXT/PDF/HTML parsing with metadata | — |
| Chunking + ChromaDB indexing | Agent built `ingest.py` and `ingest_corpus.py` | — |
| RAG pipeline | Agent implemented Top-k retrieval, prompt template, citation injection | — |
| Guardrails | Agent built scope filter, relevance threshold, word limit, citation validation | — |
| Groq LLM integration | Agent created multi-provider `llm.py` | Provided Groq API key |
| Unit tests | Agent wrote 8 tests in `test_rag.py` | — |

**Performance:** Strong. The agent correctly wired LangChain + ChromaDB + Flask on the first pass. Required one dependency fix for Python 3.13 (`pydantic-core` wheel issue).

### Phase 3 — Application & Infrastructure

| Task | AI contribution | Human contribution |
|------|-----------------|-------------------|
| Web UI (`index.html`) | Agent built clean single-page interface with fetch to `/chat` | Tested in browser, reported JSON error |
| `/chat` and `/health` endpoints | Agent implemented with snippets + citations response schema | — |
| GitHub Actions CI | Agent created `.github/workflows/ci.yml` | — |
| Render deployment | Agent created `render.yaml`, `Procfile`, start command | Created Render account, set env vars, shared deploy logs |
| Production debugging | Agent diagnosed and fixed three deploy issues (see below) | Provided Render log screenshots |

**Performance:** Good overall, but deployment required iterative debugging (see Section 4).

### Phase 4 — Evaluation & Documentation

| Task | AI contribution | Human contribution |
|------|-----------------|-------------------|
| Test question set (24 questions) | Agent created `evaluation/test_questions.json` | — |
| Evaluation script | Agent built `scripts/run_evaluation.py` with metrics | — |
| Ran benchmark | Agent executed evaluation, captured p50/p95 latency | — |
| `design-and-evaluation.md` | Agent wrote architecture justification + results | — |
| `ai-tooling.md` | Agent wrote this document | — |

**Performance:** Excellent for generating evaluation harness and documentation from real benchmark output.

---

## 4. Deployment Debugging — AI Performance Under Pressure

The most challenging part was deploying to **Render's free tier**. The AI agent resolved three production issues iteratively:

| Issue | Symptom | AI diagnosis | Fix |
|-------|---------|--------------|-----|
| 1. Gunicorn not found | `command not found` (exit 127) | Start command not on PATH | Changed to `python -m gunicorn` |
| 2. Request timeout | `Unexpected end of JSON input` / 502 | Worker timeout loading PyTorch embeddings | Increased timeout to 300s, added pipeline preload |
| 3. Out of memory | Persistent 502 on `/chat` | PyTorch + sentence-transformers exceeded 512MB | Switched to ONNX embeddings (no PyTorch) |

**Assessment:** The agent performed well at reading Render logs (from screenshots), identifying root causes, and shipping targeted fixes. Each fix required one deploy cycle to validate.

---

## 5. What AI Did Well

1. **Rapid scaffolding** — Full RAG pipeline (loader → chunker → embedder → retriever → LLM → API) in a single session
2. **Consistent code style** — Matched conventions across `src/`, tests, and scripts
3. **Policy document generation** — Produced realistic, structured HR/IT policies suitable for RAG chunking
4. **Debugging from logs** — Correctly interpreted Render deployment failures from screenshots
5. **Documentation** — README, evaluation docs, and inline code were generated with accurate technical detail
6. **Test coverage** — 13 pytest tests covering loader, guardrails, and API endpoints

---

## 6. What Required Human Input

1. **API keys** — Groq key provided by the developer (stored in `.env`, never committed)
2. **GitHub remote** — Developer provided `https://github.com/samarsalah/AI.git`
3. **Render account** — Developer created the Render service and environment variables
4. **Deploy validation** — Developer tested the live URL and shared screenshots when errors occurred
5. **Scope decisions** — e.g., "use Groq", "deploy on Render", "commit and push"

---

## 7. Limitations of AI Assistance

| Limitation | Impact |
|------------|--------|
| Cannot access external dashboards directly | Required developer to share Render logs/screenshots |
| Initial deploy config underestimated memory | First two deploy attempts failed before ONNX fix |
| GitHub CLI auth timed out | Developer pushed via standard `git push` instead |
| No autonomous production monitoring | Developer had to confirm live app worked |

---

## 8. Time Estimate (AI-assisted vs. manual)

| Phase | With AI (estimate) | Without AI (estimate) |
|-------|-------------------|----------------------|
| Phase 1 — Data + setup | ~1 hour | ~4–6 hours |
| Phase 2 — RAG pipeline | ~2 hours | ~8–12 hours |
| Phase 3 — Web + CI + deploy | ~3 hours (incl. debug) | ~6–10 hours |
| Phase 4 — Evaluation + docs | ~1 hour | ~4–6 hours |
| **Total** | **~7 hours** | **~22–34 hours** |

AI tooling reduced development time by roughly **70–75%**, with the largest savings in boilerplate code, policy writing, and documentation.

---

## 9. Conclusion

**Cursor's AI agent was the sole AI coding tool** used for this project. It was most effective for scaffolding, policy generation, and documentation. It was less effective at predicting cloud deployment constraints (memory, timeouts) without runtime feedback — but iteratively resolved all production issues once logs were provided.

For future projects, the recommended workflow is:
1. Use AI for initial architecture and scaffolding
2. Human provides API keys, cloud accounts, and deploy validation
3. Share error logs/screenshots back to AI for targeted fixes
4. Use AI to generate evaluation harnesses and documentation from real benchmark data
