"""
Qdrant Cloud Vector Database Service.

Manages collection initialization, batch vector upserts, and cosine similarity
vector search in a single unified 512d CLIP vector space.
"""
import logging
import uuid
from typing import Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from .config import settings
from .embeddings import VECTOR_DIMENSION

logger = logging.getLogger(__name__)


class QdrantService:
    """
    Qdrant Cloud database operations.
    Can be instantiated with per-user credentials (multi-tenant)
    or falls back to global .env settings (admin).
    """

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        collection_name: str | None = None,
    ):
        self._url = (url or settings.qdrant_url or "").strip()
        self._api_key = (api_key or settings.qdrant_api_key or "").strip()
        self._collection_name = collection_name or settings.qdrant_collection_name
        self._client: QdrantClient | None = None

    def get_client(self) -> QdrantClient:
        """Return QdrantClient instance, creating it if needed."""
        if self._client is None:
            if self._url and self._api_key:
                logger.info("Connecting to Qdrant Cloud at %s...", self._url[:30] + "...")
                self._client = QdrantClient(url=self._url, api_key=self._api_key)
            elif self._url:
                logger.info("Connecting to Qdrant at %s (no API key)...", self._url)
                self._client = QdrantClient(url=self._url)
            else:
                logger.info("No Qdrant URL configured — initializing in-memory Qdrant client for local dev.")
                self._client = QdrantClient(":memory:")
        return self._client

    def ensure_collection_exists(self, collection_name: str | None = None) -> str:
        """Create the Qdrant 512d Cosine collection if it doesn't exist yet."""
        target_collection = collection_name or self._collection_name
        client = self.get_client()

        try:
            collections = client.get_collections().collections
            existing_names = [c.name for c in collections]

            if target_collection not in existing_names:
                logger.info("Creating Qdrant collection '%s' (512d Cosine)...", target_collection)
                client.create_collection(
                    collection_name=target_collection,
                    vectors_config=qmodels.VectorParams(
                        size=VECTOR_DIMENSION,
                        distance=qmodels.Distance.COSINE,
                    ),
                )
                logger.info("Created collection '%s' successfully.", target_collection)
            else:
                logger.debug("Collection '%s' already exists in Qdrant.", target_collection)
            return target_collection
        except Exception as e:
            logger.error("Error ensuring Qdrant collection '%s': %s", target_collection, e, exc_info=True)
            raise RuntimeError(f"Qdrant collection setup failed: {e}") from e

    def upsert_points(
        self,
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
        collection_name: str | None = None,
    ) -> int:
        """Upsert a list of 512d vectors with associated metadata payloads."""
        # Allow caller to override collection_name, else use instance default
        if not vectors or not payloads or len(vectors) != len(payloads):
            raise ValueError("Vectors and payloads must be non-empty and equal in length.")

        target_collection = self.ensure_collection_exists(collection_name)
        client = self.get_client()

        points = [
            qmodels.PointStruct(
                id=str(uuid.uuid4()),
                vector=vec,
                payload=payload,
            )
            for vec, payload in zip(vectors, payloads)
        ]

        try:
            logger.info("Upserting %d points into Qdrant collection '%s'...", len(points), target_collection)
            client.upsert(collection_name=target_collection, points=points)
            logger.info("Upserted %d points successfully.", len(points))
            return len(points)
        except Exception as e:
            logger.error("Failed to upsert points to Qdrant: %s", e, exc_info=True)
            raise RuntimeError(f"Qdrant vector upsert failed: {e}") from e

    def search_dense(
        self,
        query_vector: list[float],
        limit: int = 5,
        session_id: str | None = None,
        collection_name: str | None = None,
        user_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Perform dense cosine similarity search in Qdrant with optional user_id isolation."""
        target_collection = self.ensure_collection_exists(collection_name)
        client = self.get_client()

        must_conditions: list = []
        if user_id is not None:
            must_conditions.append(
                qmodels.FieldCondition(key="user_id", match=qmodels.MatchValue(value=user_id))
            )
        if session_id:
            must_conditions.append(
                qmodels.FieldCondition(key="session_id", match=qmodels.MatchValue(value=session_id))
            )

        query_filter = qmodels.Filter(must=must_conditions) if must_conditions else None

        try:
            logger.info("Searching Qdrant dense vector index (limit=%d)...", limit)
            search_result = client.search(
                collection_name=target_collection,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
            )

            results = []
            for res in search_result:
                payload = res.payload or {}
                payload["_id"] = str(res.id)
                payload["_score"] = float(res.score)
                results.append(payload)

            logger.info("Qdrant dense search returned %d matches.", len(results))
            return results
        except Exception as e:
            logger.error("Qdrant dense search error: %s", e, exc_info=True)
            raise RuntimeError(f"Qdrant search failed: {e}") from e


# Default global admin instance (uses .env credentials)
qdrant_service = QdrantService()
