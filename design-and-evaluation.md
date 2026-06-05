# Design and Evaluation

**Project:** Corporate Policy RAG Assistant  
**Author:** Samar Salah  
**Date:** June 2026  
**Live demo:** https://policy-rag-tpok.onrender.com

---

## 1. Architecture Overview

This application is a **Retrieval-Augmented Generation (RAG)** system that answers employee questions using a fixed corpus of nine corporate policy documents. The pipeline has four stages:

1. **Ingestion** — load, clean, chunk, embed, and index policy text
2. **Retrieval** — Top-k similarity search against ChromaDB
3. **Generation** — LLM produces an answer grounded in retrieved chunks
4. **Guardrails** — scope checks, relevance thresholds, length limits, and citation enforcement

```
User → Flask Web UI / API → RAG Pipeline → ChromaDB (vectors)
                              ↓
                         Groq LLM (Llama 3.3)
```

---

## 2. Architecture Decisions and Justification

### 2.1 Corpus Format and Size

| Decision | Choice | Justification |
|----------|--------|---------------|
| Document count | 9 files (MD + HTML) | Meets the 5–20 document requirement; covers HR, IT, finance, and compliance |
| Page volume | ~8,750 words (~30–35 pages) | Within the 30–120 page target; large enough for realistic retrieval |
| Synthetic policies | Yes | Ensures legal right to use, consistent structure, and reproducible evaluation |

Documents use Markdown headings (`#`, `##`, `###`), tables, and bullet lists to improve chunk boundaries during splitting.

### 2.2 Chunking Strategy

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Chunk size | 1,000 characters | Balances context richness with embedding precision |
| Overlap | 200 characters | Prevents sentence/table splits from losing meaning at boundaries |
| Splitter | `RecursiveCharacterTextSplitter` | Respects heading boundaries (`\n## `, `\n### `) before falling back to paragraphs |

### 2.3 Embedding Model

| Decision | Choice | Justification |
|----------|--------|---------------|
| Model | `all-MiniLM-L6-v2` via ONNX | Free, local, no API cost; widely used for semantic search |
| Backend | Chroma `ONNXMiniLM_L6_V2` | Avoids PyTorch on Render's 512MB free tier (prevents OOM crashes) |
| Alternative considered | `sentence-transformers` + PyTorch | Higher quality parity but exceeded Render memory limits in production |

### 2.4 Vector Database

| Decision | Choice | Justification |
|----------|--------|---------------|
| Store | ChromaDB (local persistence) | Simple setup, no cloud cost, integrates with LangChain |
| Index size | 92 chunks | Appropriate for a small policy corpus |
| Alternative considered | Pinecone | Better at scale, but unnecessary for a demo corpus under 100 chunks |

### 2.5 Retrieval

| Decision | Choice | Justification |
|----------|--------|---------------|
| Method | Top-k similarity search | Standard, interpretable RAG baseline |
| k | 4 | Enough context for multi-part answers without overflowing the prompt |
| Relevance filter | Minimum score 0.25 | Blocks low-confidence retrievals from reaching the LLM |

### 2.6 LLM Provider

| Decision | Choice | Justification |
|----------|--------|---------------|
| Provider | Groq (free tier) | Fast inference, OpenAI-compatible API, low cost for coursework |
| Model | `llama-3.3-70b-versatile` | Strong instruction-following for citation formatting |
| Temperature | 0.1 | Reduces hallucination; favors deterministic policy answers |

### 2.7 Guardrails

| Guardrail | Implementation | Justification |
|-----------|----------------|---------------|
| Scope filter | Keyword allow-list | Fast pre-filter for obviously out-of-scope queries |
| Relevance threshold | Max similarity score ≥ 0.25 | Prevents answers when retrieval confidence is low |
| Output length | 300 words / 512 tokens | Keeps responses concise for HR lookups |
| Citation enforcement | Prompt + post-processing | Ensures every answer references `source_id` and title |
| Refusal message | Standard template | Clear UX when the question is outside the corpus |

### 2.8 Web Framework and Deployment

| Decision | Choice | Justification |
|----------|--------|---------------|
| Framework | Flask | Lightweight, meets `/chat` and `/health` API requirements |
| UI | Server-rendered HTML + fetch | Simple, no frontend build step |
| Production server | Gunicorn | Standard WSGI server for Render |
| Hosting | Render free tier | Public URL for submission; `render.yaml` for reproducible deploys |
| CI/CD | GitHub Actions | Automated test + build check on every push/PR |

---

## 3. Evaluation Methodology

### 3.1 Test Set

A benchmark of **24 questions** was created in `evaluation/test_questions.json`:

- **20 in-scope** questions spanning all nine policy documents
- **4 out-of-scope** questions (geography, coding, weather, sports)

Each in-scope question includes `expected_sources` — the policy document(s) most likely to contain the answer.

### 3.2 Metrics

| Metric | Definition | How measured |
|--------|------------|--------------|
| **Groundedness** | Answer content is supported by retrieved policy text | Automated: cited source appears in answer AND answer shares ≥2 terms with the source snippet |
| **Citation validity** | Cited `source_id` values exist in the corpus | Automated: all cited IDs ∈ known corpus IDs |
| **Citation accuracy (expected source)** | Answer cites the correct policy document | Automated: cited ID intersects `expected_sources` |
| **Refusal accuracy** | Out-of-scope questions are refused | Automated: `refused=true` for all out-of-scope items |
| **Latency** | End-to-end `/chat` response time | `time.perf_counter()` around `pipeline.query()` |

### 3.3 Execution

```bash
EMBEDDING_BACKEND=onnx python scripts/run_evaluation.py
```

Results are saved to `evaluation/results.json`. Evaluation was run locally against the Groq API with the ONNX-indexed ChromaDB (June 2026).

---

## 4. Evaluation Results

### 4.1 Summary Table

| Metric | Result |
|--------|--------|
| Total test questions | 24 |
| In-scope questions | 20 |
| Out-of-scope questions | 4 |
| **In-scope answer rate** | **85%** (17/20 answered) |
| **Groundedness** (answered only) | **100%** (17/17) |
| **Citation validity** (answered only) | **100%** (17/17) |
| **Citation accuracy** (expected source) | **100%** (17/17) |
| **Refusal accuracy** (out-of-scope) | **100%** (4/4) |

### 4.2 Latency (17 answered in-scope queries)

| Statistic | Time (ms) |
|-----------|-----------|
| **p50** | **1,082.5** |
| **p95** | **7,793.1** |
| Mean | 2,693.2 |
| Min | 366.8 |
| Max | 7,849.9 |

Most queries complete in ~1 second (p50). The p95 tail reflects Groq API variability and occasional cold-start embedding loads.

### 4.3 Sample Results

**Strong performance (q01 — PTO accrual):**
- Question: *"How many PTO days do employees with 0-2 years of tenure receive?"*
- Answer cited `[pto_and_leave_policy]` with correct value (15 days)
- Latency: 1,082 ms

**Strong refusal (q21 — geography):**
- Question: *"What is the capital of France?"*
- Correctly refused with scope message
- Latency: <1 ms (no LLM call)

### 4.4 False Refusals (3/20 in-scope)

Three valid policy questions were incorrectly refused by the relevance guardrail:

| ID | Question | Likely cause |
|----|----------|--------------|
| q06 | Is VPN required when accessing internal applications from home? | Retrieval score below 0.25 threshold |
| q12 | What is the clean desk screen lock timeout? | Keyword "clean desk" not in scope list; low relevance score |
| q15 | What is the company 401k match? | "401k" not in keyword list; benefits doc retrieval scored low |

These are **guardrail tuning issues**, not LLM hallucinations. Recommended fixes:
- Expand `CORPUS_SCOPE_KEYWORDS` (e.g., `401k`, `clean desk`, `vpn`)
- Lower `MIN_RELEVANCE_SCORE` from 0.25 to 0.15 for ONNX distance scores
- Add policy-specific aliases to the scope list

---

## 5. Limitations

1. **Automated groundedness** uses term overlap, not human or LLM-as-judge review — conservative but not a perfect substitute for manual audit.
2. **ONNX relevance scores** can be negative (distance-based), making the 0.25 threshold brittle — caused the three false refusals.
3. **Single LLM provider** (Groq) — results may differ with OpenAI or OpenRouter.
4. **No concurrent load testing** — latency measured sequentially, not under parallel users.
5. **Free-tier Render** — cold starts add 30–60 seconds not captured in local latency benchmarks.

---

## 6. Conclusion

The system achieves **100% groundedness and citation accuracy on answered questions**, with **100% refusal accuracy on out-of-scope queries**. The main improvement area is the **relevance guardrail**, which caused 15% false refusal on valid in-scope questions. Median latency of **1.1 seconds** is acceptable for an internal HR policy lookup tool.

---

## 7. Reproducibility

```bash
# Re-index
EMBEDDING_BACKEND=onnx python scripts/ingest_corpus.py

# Run evaluation
EMBEDDING_BACKEND=onnx python scripts/run_evaluation.py

# View results
cat evaluation/results.json
```
