"""
Unified Multimodal Embedding Service.

Uses FastEmbed CLIP models (Qdrant/clip-ViT-B-32-text, Qdrant/clip-ViT-B-32-vision) to project both text passages
and images into the SAME 512-dimensional vector space for cross-modal RAG search.
"""
import io
import logging
from typing import Union

logger = logging.getLogger(__name__)

# Model identifiers for CLIP 512d unified vector space
CLIP_TEXT_MODEL = "Qdrant/clip-ViT-B-32-text"
CLIP_IMAGE_MODEL = "Qdrant/clip-ViT-B-32-vision"
VECTOR_DIMENSION = 512


class MultimodalEmbedder:
    """Singleton manager for unified CLIP text and image embeddings."""

    _text_model = None
    _image_model = None

    @classmethod
    def _get_text_model(cls):
        if cls._text_model is None:
            logger.info("Initializing FastEmbed CLIP text encoder (%s)...", CLIP_TEXT_MODEL)
            try:
                from fastembed import TextEmbedding
                cls._text_model = TextEmbedding(model_name=CLIP_TEXT_MODEL)
                logger.info("FastEmbed CLIP text encoder initialized successfully (512d).")
            except Exception as e:
                logger.error("Failed to initialize FastEmbed CLIP text encoder: %s", e, exc_info=True)
                raise RuntimeError(f"CLIP text encoder failed to load: {e}") from e
        return cls._text_model

    @classmethod
    def _get_image_model(cls):
        if cls._image_model is None:
            logger.info("Initializing FastEmbed CLIP image encoder (%s)...", CLIP_IMAGE_MODEL)
            try:
                from fastembed import ImageEmbedding
                cls._image_model = ImageEmbedding(model_name=CLIP_IMAGE_MODEL)
                logger.info("FastEmbed CLIP image encoder initialized successfully (512d).")
            except Exception as e:
                logger.error("Failed to initialize FastEmbed CLIP image encoder: %s", e, exc_info=True)
                raise RuntimeError(f"CLIP image encoder failed to load: {e}") from e
        return cls._image_model

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string into a 512d vector."""
        if not text or not text.strip():
            logger.warning("Empty string passed to embed_text — returning zero vector.")
            return [0.0] * VECTOR_DIMENSION

        model = self._get_text_model()
        try:
            generator = model.embed([text])
            vector = list(next(generator))
            return [float(v) for v in vector]
        except Exception as e:
            logger.error("Error embedding text chunk: %s", e, exc_info=True)
            raise RuntimeError(f"Text embedding failed: {e}") from e

    def embed_text_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of text strings into 512d vectors."""
        if not texts:
            return []

        clean_texts = [t if t and t.strip() else " " for t in texts]
        model = self._get_text_model()
        try:
            logger.info("Embedding batch of %d text chunks via CLIP...", len(clean_texts))
            embeddings = list(model.embed(clean_texts))
            return [[float(v) for v in emb] for emb in embeddings]
        except Exception as e:
            logger.error("Error embedding batch of %d text chunks: %s", len(texts), e, exc_info=True)
            raise RuntimeError(f"Text batch embedding failed: {e}") from e

    def embed_image_bytes(self, image_bytes: bytes) -> list[float]:
        """Embed raw image bytes into the exact same 512d vector space."""
        if not image_bytes:
            raise ValueError("Image bytes cannot be empty.")

        model = self._get_image_model()
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            # Save to temporary file in memory for FastEmbed ImageEmbedding
            temp_buffer = io.BytesIO()
            img.save(temp_buffer, format="JPEG")
            temp_buffer.seek(0)

            generator = model.embed([temp_buffer])
            vector = list(next(generator))
            logger.info("Embedded image (%d bytes) into 512d vector.", len(image_bytes))
            return [float(v) for v in vector]
        except Exception as e:
            logger.error("Error embedding image: %s", e, exc_info=True)
            raise RuntimeError(f"Image embedding failed: {e}") from e


embedder = MultimodalEmbedder()
