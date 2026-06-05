# Demo Video Script — Corporate Policy RAG Assistant

**Target length:** 7–9 minutes  
**Live URL:** https://policy-rag-tpok.onrender.com  
**GitHub:** https://github.com/samarsalah/AI

---

## Before You Record

### Solo presenter
- [ ] Face visible on camera (picture-in-picture or split screen)
- [ ] Government-issued photo ID ready to hold up briefly at the start
- [ ] Mic tested; quiet room
- [ ] Browser tabs pre-opened (see checklist below)
- [ ] Render app awake — visit the URL 1 minute before recording (free tier cold start)

### Group project (if applicable)
- [ ] **Every member** speaks, is on camera, and holds up government ID
- [ ] Assign sections below to each person before recording
- [ ] Use a shared screen + grid view so all faces are visible

### Tabs to open before recording
1. https://policy-rag-tpok.onrender.com (web app)
2. https://policy-rag-tpok.onrender.com/health
3. https://github.com/samarsalah/AI
4. `design-and-evaluation.md` on GitHub (or locally in editor)
5. Optional: GitHub Actions CI page

---

## Script

### [0:00 – 0:45] Introduction + ID verification

**[On camera — hold up government ID next to your face]**

> "Hi, my name is **[Your Full Name]**. I'm presenting the Corporate Policy RAG Assistant for my AI Engineering project.
>
> I'm holding my government-issued ID for verification. **[Show ID clearly for 3–5 seconds, then lower it.]**
>
> This application lets employees ask natural-language questions about company policies — things like PTO, remote work, expenses, security, and conduct — and get answers grounded in our policy documents with source citations."

**[Switch to screen share]**

---

### [0:45 – 1:30] Project overview and architecture

**[Show GitHub README — scroll to Project Structure]**

> "The project has four phases. We built a corpus of nine synthetic policy documents, ingested them into ChromaDB with free ONNX embeddings, and connected a Groq LLM through a RAG pipeline with guardrails.
>
> The stack is Flask for the web API, LangChain for orchestration, ChromaDB for vector search, and Groq's Llama 3.3 for generation. It's deployed on Render at this public URL."

**[Briefly show `src/` folder on GitHub: `rag_pipeline.py`, `guardrails.py`, `ingest.py`]**

---

### [1:30 – 2:00] Health check and deployment

**[Open https://policy-rag-tpok.onrender.com/health]**

> "First, the health endpoint — this is required for deployment monitoring. It returns a simple JSON status confirming the service is running."

**[Point to `{"status":"ok","service":"policy-rag"}`]**

---

### [2:00 – 4:30] Live demo — in-scope questions (3 examples)

**[Open https://policy-rag-tpok.onrender.com]**

> "Now the main web interface. Employees type a question and click Ask."

---

**Demo 1 — PTO policy (~45 sec)**

**[Type and submit:]**
> "How many PTO days do new employees get?"

**[While waiting — if slow:]**
> "On Render's free tier, the first request after idle may take a few seconds while the service wakes up."

**[When answer appears — point to each section:]**

> "The answer says employees with zero to two years receive fifteen PTO days, with citations to `pto_and_leave_policy`.
>
> Below that, Source Snippets show the exact policy text the system retrieved. Citations list the document ID and chunk index. This is the RAG pipeline — retrieve relevant chunks, inject them into the LLM prompt, and require inline citations."

---

**Demo 2 — Remote work (~30 sec)**

**[Type and submit:]**
> "What is the monthly remote work stipend for fully remote employees?"

> "Seventy-five dollars per month for permanently fully remote employees — cited from the remote work policy. Different question, different source document."

---

**Demo 3 — Information security (~30 sec)**

**[Type and submit:]**
> "How often must standard user passwords be rotated?"

> "Ninety days — pulled from the information security policy. The system stays grounded in the corpus instead of using general world knowledge."

---

### [4:30 – 5:30] Guardrails — out-of-scope refusal

**[Type and submit:]**
> "What is the capital of France?"

> "The system refuses — it recognizes this is outside our policy corpus and returns a standard refusal message instead of hallucinating an answer. This is the scope guardrail we implemented in Phase 2."

**[Optional second out-of-scope:]**
> "Write me a Python sorting algorithm."

> "Also refused. The assistant only answers HR and operations policy questions."

---

### [5:30 – 6:30] API endpoint and citations structure

**[Open browser dev tools → Network tab, OR use a prepared curl in terminal]**

> "The same logic is exposed via a POST `/chat` API endpoint. The response includes the answer, source snippets with text excerpts, and citation metadata — source ID, title, and chunk index."

**[If showing curl — run or display:]**
```bash
curl -X POST https://policy-rag-tpok.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"How many PTO days do new employees get?\"}"
```

> "This JSON structure is what powers the web UI."

---

### [6:30 – 7:30] Evaluation results

**[Show `design-and-evaluation.md` on GitHub]**

> "For Phase 4, we built a test set of twenty-four policy questions and ran automated evaluation.
>
> Key results: one hundred percent groundedness on answered questions, one hundred percent citation accuracy, one hundred percent refusal accuracy on out-of-scope questions, and median latency of about one point one seconds with p95 under eight seconds.
>
> We documented architecture decisions and these results in `design-and-evaluation.md`, and our AI tooling usage in `ai-tooling.md`."

---

### [7:30 – 8:15] CI/CD and repository

**[Show GitHub Actions tab — optional if CI ran]**

> "GitHub Actions runs on every push — it installs dependencies, runs thirteen pytest tests, and performs a build-start check on the Flask app."

**[Show corpus folder briefly]**

> "The corpus has nine policy files — Markdown and HTML — totaling about thirty pages. Everything is in the public repo."

---

### [8:15 – 8:45] Closing

**[Optional: return to camera picture-in-picture]**

> "To summarize: we built a full RAG pipeline with ingestion, Top-k retrieval, citation injection, guardrails, a web interface, CI/CD, and a live deployment on Render.
>
> The app is available at **policy-rag-tpok.onrender.com** and the code is on GitHub at **samarsalah/AI**.
>
> Thank you — happy to answer any questions."

---

## Timing Cheat Sheet

| Section | Duration |
|---------|----------|
| Intro + ID | 0:45 |
| Architecture overview | 0:45 |
| Health check | 0:30 |
| 3 in-scope demos | 2:30 |
| Out-of-scope guardrail | 1:00 |
| API + JSON | 1:00 |
| Evaluation results | 1:00 |
| CI/CD + corpus | 0:45 |
| Closing | 0:30 |
| **Total** | **~8:45** |

---

## Troubleshooting During Recording

| Problem | What to say / do |
|---------|------------------|
| Render slow on first click | "Free tier cold start — I'll wait a moment." Refresh once if needed. |
| 502 error | Visit `/health` first, wait 30s, retry. |
| Wrong answer | Acknowledge: "Retrieval picked a related chunk — in production we'd tune the relevance threshold." |
| Camera/mic issue | Stop, fix, re-record from last section. |

---

## Group Speaking Assignments (example for 3 people)

| Person | Sections |
|--------|----------|
| **Person A** | Intro + ID, architecture, health check |
| **Person B** | Live demos (3 in-scope + 1 out-of-scope) |
| **Person C** | API, evaluation, CI/CD, closing + ID |

Each person: ~2–3 minutes speaking, on camera, ID shown at start (and end if required).
