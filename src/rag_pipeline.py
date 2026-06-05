"""Top-k RAG pipeline with citation injection and guardrails."""

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import MAX_OUTPUT_TOKENS, MAX_RESPONSE_WORDS, REFUSAL_MESSAGE, TOP_K
from src.guardrails import (
    RAGResponse,
    build_citations,
    check_retrieval_relevance,
    enforce_word_limit,
    format_context_block,
    is_likely_in_scope,
    validate_citations_present,
)
from src.ingest import load_vector_store
from src.llm import get_llm

SYSTEM_PROMPT = """You are a corporate policy assistant for an internal HR and Operations knowledge base.

STRICT RULES:
1. Answer ONLY using the provided policy context. Do not use outside knowledge.
2. If the context does not contain enough information, say: "I cannot answer that based on the available policies."
3. ALWAYS cite sources inline using [source_id] after each factual claim. Example: "Employees receive 15 PTO days [pto_and_leave_policy]."
4. Keep your answer concise — no more than {max_words} words.
5. REFUSE questions unrelated to the policy corpus (PTO/leave, remote work, expenses, information security, code of conduct). Say you can only help with covered corporate policies.
6. Never invent policy details, numbers, or procedures not present in the context.

Available source IDs in this context: {source_ids}
"""


class PolicyRAGPipeline:
    """Retrieve top-k chunks and generate grounded, cited answers."""

    def __init__(self, vector_store=None, top_k: int = TOP_K):
        self.vector_store = vector_store or load_vector_store()
        self.top_k = top_k
        self.llm = get_llm()

    def retrieve(self, question: str) -> tuple[list[Document], list[float]]:
        """Top-k similarity search with relevance scores."""
        results = self.vector_store.similarity_search_with_relevance_scores(
            question, k=self.top_k
        )
        docs = [doc for doc, _score in results]
        scores = [score for _doc, score in results]
        return docs, scores

    def query(self, question: str) -> RAGResponse:
        question = question.strip()
        if not question:
            return RAGResponse(
                answer="Please provide a question about company policies.",
                refused=True,
                refusal_reason="empty_question",
            )

        if not is_likely_in_scope(question):
            return RAGResponse(
                answer=REFUSAL_MESSAGE,
                refused=True,
                refusal_reason="out_of_scope_keywords",
            )

        docs, scores = self.retrieve(question)
        relevance = check_retrieval_relevance(scores)
        if not relevance.allowed:
            return RAGResponse(
                answer=relevance.message,
                refused=True,
                refusal_reason=relevance.reason,
            )

        citations = build_citations(docs)
        context = format_context_block(docs)
        source_ids = ", ".join({c.source_id for c in citations})

        messages = [
            SystemMessage(
                content=SYSTEM_PROMPT.format(
                    max_words=MAX_RESPONSE_WORDS,
                    source_ids=source_ids,
                )
            ),
            HumanMessage(
                content=(
                    f"POLICY CONTEXT:\n{context}\n\n"
                    f"EMPLOYEE QUESTION:\n{question}\n\n"
                    "Provide a grounded answer with [source_id] citations."
                )
            ),
        ]

        response = self.llm.invoke(messages, max_tokens=MAX_OUTPUT_TOKENS)
        answer = enforce_word_limit(response.content.strip())
        answer = validate_citations_present(answer, citations)

        return RAGResponse(
            answer=answer,
            citations=citations,
            refused=False,
        )
