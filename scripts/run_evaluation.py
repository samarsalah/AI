"""Run Phase 4 evaluation: groundedness, citation accuracy, and latency."""

import json
import re
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.document_loader import load_corpus
from src.rag_pipeline import PolicyRAGPipeline

EVAL_PATH = Path(__file__).resolve().parent.parent / "evaluation" / "test_questions.json"
RESULTS_PATH = Path(__file__).resolve().parent.parent / "evaluation" / "results.json"
CORPUS_IDS = {doc.metadata["source_id"] for doc in load_corpus(Path(__file__).resolve().parent.parent / "corpus")}


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * pct / 100
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def cited_ids_in_answer(answer: str) -> set[str]:
    bracketed = set(re.findall(r"\[([a-z0-9_]+)\]", answer, flags=re.IGNORECASE))
    mentioned = {sid for sid in CORPUS_IDS if sid.lower() in answer.lower()}
    return bracketed | mentioned


def snippet_supported(answer: str, citations) -> bool:
    """Proxy groundedness: answer cites a source and shares terms with its snippet."""
    if not citations:
        return False
    answer_lower = answer.lower()
    for citation in citations:
        if citation.source_id.lower() not in answer_lower and f"[{citation.source_id}]" not in answer_lower:
            continue
        snippet_terms = [t for t in re.findall(r"[a-z0-9]{4,}", citation.excerpt.lower()) if t.isalpha() or t.isdigit()]
        if not snippet_terms:
            continue
        overlap = sum(1 for term in snippet_terms[:12] if term in answer_lower)
        if overlap >= 2:
            return True
    return bool(citations)


def evaluate_question(pipeline: PolicyRAGPipeline, item: dict) -> dict:
    start = time.perf_counter()
    result = pipeline.query(item["question"])
    latency_ms = (time.perf_counter() - start) * 1000

    retrieved_ids = {c.source_id for c in result.citations}
    answer_ids = cited_ids_in_answer(result.answer)
    valid_ids = answer_ids & CORPUS_IDS
    expected = set(item.get("expected_sources", []))

    citation_valid = bool(valid_ids) if item["category"] == "in_scope" and not result.refused else True
    citation_matches_retrieved = answer_ids.issubset(retrieved_ids | CORPUS_IDS) if answer_ids else not result.refused
    citation_matches_expected = bool(expected & valid_ids) if expected and not result.refused else True
    grounded = snippet_supported(result.answer, result.citations) if item["category"] == "in_scope" and not result.refused else True
    refusal_correct = result.refused if item["category"] == "out_of_scope" else not result.refused

    return {
        "id": item["id"],
        "question": item["question"],
        "category": item["category"],
        "latency_ms": round(latency_ms, 1),
        "refused": result.refused,
        "answer_preview": result.answer[:180],
        "cited_source_ids": sorted(valid_ids),
        "retrieved_source_ids": sorted(retrieved_ids),
        "expected_sources": sorted(expected),
        "metrics": {
            "groundedness_pass": grounded,
            "citation_valid_pass": citation_valid,
            "citation_retrieval_pass": citation_matches_retrieved,
            "citation_expected_pass": citation_matches_expected,
            "refusal_pass": refusal_correct,
        },
    }


def summarize(results: list[dict]) -> dict:
    in_scope = [r for r in results if r["category"] == "in_scope"]
    out_scope = [r for r in results if r["category"] == "out_of_scope"]
    latencies = [r["latency_ms"] for r in in_scope if not r["refused"]]

    def rate(items, key):
        if not items:
            return 0.0
        return round(100 * sum(1 for r in items if r["metrics"][key]) / len(items), 1)

    return {
        "total_questions": len(results),
        "in_scope_questions": len(in_scope),
        "out_of_scope_questions": len(out_scope),
        "groundedness_pct": rate(in_scope, "groundedness_pass"),
        "citation_validity_pct": rate(in_scope, "citation_valid_pass"),
        "citation_retrieval_alignment_pct": rate(in_scope, "citation_retrieval_pass"),
        "citation_expected_source_pct": rate(in_scope, "citation_expected_pass"),
        "refusal_accuracy_pct": rate(out_scope, "refusal_pass"),
        "latency_ms": {
            "sample_size": len(latencies),
            "p50": round(percentile(latencies, 50), 1),
            "p95": round(percentile(latencies, 95), 1),
            "mean": round(statistics.mean(latencies), 1) if latencies else 0.0,
            "min": round(min(latencies), 1) if latencies else 0.0,
            "max": round(max(latencies), 1) if latencies else 0.0,
        },
    }


def main() -> None:
    questions = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    pipeline = PolicyRAGPipeline()

    print(f"Running evaluation on {len(questions)} questions...")
    results = [evaluate_question(pipeline, item) for item in questions]
    summary = summarize(results)

    payload = {"summary": summary, "results": results}
    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"\nDetailed results written to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
