# Deployed Application

**Live URL:** https://policy-rag-tpok.onrender.com

**Health check:** https://policy-rag-tpok.onrender.com/health

**GitHub repository:** https://github.com/samarsalah/AI

## Endpoints

| Endpoint | URL |
|----------|-----|
| Web UI | https://policy-rag-tpok.onrender.com/ |
| Health | https://policy-rag-tpok.onrender.com/health |
| Chat API | `POST https://policy-rag-tpok.onrender.com/chat` |

## Example request

```bash
curl -X POST https://policy-rag-tpok.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"How many PTO days do new employees get?\"}"
```

## Hosting

- **Provider:** Render (free tier)
- **Runtime:** Python 3.12
- **Start command:** `python -m gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --preload`
- **Build command:** `pip install -r requirements.txt && python scripts/ingest_corpus.py`

## Environment variables (set in Render dashboard)

| Variable | Value |
|----------|-------|
| `LLM_PROVIDER` | `groq` |
| `GROQ_API_KEY` | *(secret — set in Render)* |
| `EMBEDDING_BACKEND` | `onnx` |
| `PRELOAD_PIPELINE` | `true` |

## Notes

- Free-tier Render services may sleep after ~15 minutes of inactivity. The first request after idle can take 30–60 seconds.
- The vector index is built during deploy (`ingest_corpus.py`); `chroma_db/` is not committed to git.
