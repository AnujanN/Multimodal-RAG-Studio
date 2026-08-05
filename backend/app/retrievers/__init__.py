"""
Registry of all RAG Retrieval strategies.
"""
from typing import Type
from .base import BaseRetriever
from .dense import DenseRetriever
from .hybrid import HybridRetriever
from .multi_query import MultiQueryRetriever
from .parent_child import ParentChildRetriever

RETRIEVER_REGISTRY: dict[str, Type[BaseRetriever]] = {
    "dense": DenseRetriever,
    "hybrid": HybridRetriever,
    "multi_query": MultiQueryRetriever,
    "parent_child": ParentChildRetriever,
}


def get_retriever(
    name: str,
    qdrant_service=None,
    user_id: int | None = None,
    openrouter_api_key: str | None = None,
) -> BaseRetriever:
    """Instantiate and return retriever by strategy name, passing optional per-user credentials."""
    if name not in RETRIEVER_REGISTRY:
        raise ValueError(f"Unknown retriever technique: '{name}'. Available: {list(RETRIEVER_REGISTRY.keys())}")
    cls = RETRIEVER_REGISTRY[name]
    return cls(
        qdrant_service=qdrant_service,
        user_id=user_id,
        openrouter_api_key=openrouter_api_key,
    )
