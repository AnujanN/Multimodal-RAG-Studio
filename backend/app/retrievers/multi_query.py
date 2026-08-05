"""
Multi-Query Expansion Retriever.

Uses OpenRouter API to expand 1 user query into 3 complementary query variations,
runs parallel dense searches against Qdrant, and deduplicates the merged results.
"""
import logging
from typing import Any
import httpx

from .base import BaseRetriever
from ..config import settings
from ..embeddings import embedder

logger = logging.getLogger(__name__)


async def _generate_query_variations(query: str, api_key: str | None = None) -> list[str]:
    """Generate 3 alternative query variations using OpenRouter API."""
    key = (api_key or settings.openrouter_api_key or "").strip()
    if not key:
        logger.warning("No OpenRouter API key configured — using original query as fallback.")
        return [query]

    prompt = (
        f"You are an AI search query expander. Given the user question: '{query}', "
        "generate 3 different phrasing variations of this question to search a vector database. "
        "Return ONLY the 3 queries, one per line, without numbering or extra text."
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                },
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                lines = [line.strip() for line in content.split("\n") if line.strip()]
                queries = [query] + lines[:3]
                logger.info("Multi-query expansion generated %d query variations.", len(queries))
                return queries
    except Exception as e:
        logger.warning("Failed to generate query variations via OpenRouter: %s", e)

    return [query]


class MultiQueryRetriever(BaseRetriever):
    name = "multi_query"
    label = "Multi-Query Retrieval (LLM Expansion)"
    description = "Rewrites user query into 3 variations using OpenRouter LLM, searches Qdrant 3x, and merges deduplicated top matches."

    async def retrieve(
        self,
        query: str,
        limit: int = 5,
        session_id: str | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        logger.info("Running Multi-Query Retrieval for: '%s'", query[:50])

        # 1. Expand query into variations using per-user OpenRouter key
        variations = await _generate_query_variations(query, api_key=self.openrouter_api_key)

        # 2. Run dense search for each query variation
        seen_ids = set()
        merged = []

        for q in variations:
            q_vector = embedder.embed_text(q)
            results = self.qs.search_dense(
                query_vector=q_vector,
                limit=limit,
                session_id=session_id,
                user_id=self.user_id,
            )
            for r in results:
                item_id = r.get("_id")
                if item_id not in seen_ids:
                    seen_ids.add(item_id)
                    merged.append({
                        "text": r.get("text", ""),
                        "source_type": r.get("source_type", "text"),
                        "source_name": r.get("source_name", "document"),
                        "score": round(r.get("_score", 0.0), 4),
                        "metadata": r.get("metadata", {}),
                    })

        # 3. Sort by score and clamp to limit
        merged.sort(key=lambda x: x["score"], reverse=True)
        final_results = merged[:limit]

        logger.info("Multi-query retriever returned %d deduplicated matches across %d queries.", len(final_results), len(variations))
        return final_results
