"""
Hybrid BM25 Keyword + Dense Vector Search Retriever using Reciprocal Rank Fusion (RRF).

Combines dense vector similarity matching with keyword matching to maximize recall.
"""
import logging
import re
from typing import Any

from .base import BaseRetriever
from ..embeddings import embedder

logger = logging.getLogger(__name__)


def _compute_bm25_score(query: str, text: str) -> float:
    """Lightweight in-memory keyword frequency score for RRF hybrid fusion."""
    query_words = set(re.findall(r"\w+", query.lower()))
    if not query_words:
        return 0.0
    text_words = re.findall(r"\w+", text.lower())
    if not text_words:
        return 0.0

    score = 0.0
    for qw in query_words:
        freq = text_words.count(qw)
        if freq > 0:
            score += 1.0 + (freq / len(text_words))
    return score


class HybridRetriever(BaseRetriever):
    name = "hybrid"
    label = "Hybrid Search (BM25 + Dense RRF)"
    description = "Fuses dense vector similarity with sparse BM25 keyword matching via Reciprocal Rank Fusion (RRF)."

    async def retrieve(
        self,
        query: str,
        limit: int = 5,
        session_id: str | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        logger.info("Running Hybrid BM25+Dense Search for query: '%s'", query[:50])

        # 1. Get candidates via Dense Vector Search
        query_vector = embedder.embed_text(query)
        candidates = self.qs.search_dense(
            query_vector=query_vector,
            limit=limit * 3,  # Candidate pool for RRF
            session_id=session_id,
            user_id=self.user_id,
        )

        if not candidates:
            return []

        # 2. Rank candidates by Dense score
        dense_ranked = sorted(candidates, key=lambda x: x.get("_score", 0.0), reverse=True)

        # 3. Rank candidates by BM25 keyword score
        bm25_ranked = sorted(
            candidates,
            key=lambda x: _compute_bm25_score(query, x.get("text", "")),
            reverse=True,
        )

        # 4. Perform Reciprocal Rank Fusion (RRF)
        rrf_k = 60
        rrf_scores = {}

        for rank, item in enumerate(dense_ranked):
            item_id = item.get("_id")
            rrf_scores[item_id] = rrf_scores.get(item_id, 0.0) + (1.0 / (rrf_k + rank + 1))

        for rank, item in enumerate(bm25_ranked):
            item_id = item.get("_id")
            rrf_scores[item_id] = rrf_scores.get(item_id, 0.0) + (1.0 / (rrf_k + rank + 1))

        # 5. Sort by RRF score
        candidates_by_id = {c["_id"]: c for c in candidates}
        fused = []
        for item_id, r_score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:limit]:
            item = candidates_by_id[item_id]
            fused.append({
                "text": item.get("text", ""),
                "source_type": item.get("source_type", "text"),
                "source_name": item.get("source_name", "document"),
                "score": round(r_score, 4),
                "metadata": item.get("metadata", {}),
            })

        logger.info("Hybrid retriever returned %d fused matches.", len(fused))
        return fused
