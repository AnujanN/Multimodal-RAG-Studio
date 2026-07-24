"""
Chunker registry — exports all 21 chunking techniques.
Import from here in the API layer.

Usage in a RAG pipeline:
    from app.chunkers import CHUNKER_REGISTRY
    chunker = CHUNKER_REGISTRY["semantic_chunker"]()
    chunks = chunker.chunk(text, similarity_threshold=0.5)
"""
from .basic import (
    NaiveChunker,
    FixedSizeChunker,
    SlidingWindowChunker,
    SentenceChunker,
    ParagraphChunker,
    PageChunker,
)
from .advanced import (
    TableAwareChunker,
    TopicBasedChunker,
    ContentAwareChunker,
    StructuredChunker,
    EntityBasedChunker,
    HeadingBasedChunker,
    DelimiterBasedChunker,
    ListAwareChunker,
)
from .ai_powered import (
    RecursiveChunker,
    ContextualChunker,
    SemanticChunker,
    SimilarityBasedChunker,
    TokenBasedChunker,
    KeywordExtractionChunker,
    HybridChunker,
)
from .base import BaseChunker

# Registry: technique name → class
CHUNKER_REGISTRY: dict[str, type[BaseChunker]] = {
    # Basic
    "naive_chunker": NaiveChunker,
    "fixed_size_chunker": FixedSizeChunker,
    "sliding_window_chunker": SlidingWindowChunker,
    "sentence_chunker": SentenceChunker,
    "paragraph_chunker": ParagraphChunker,
    "page_chunker": PageChunker,
    # Advanced
    "table_aware_chunker": TableAwareChunker,
    "topic_based_chunker": TopicBasedChunker,
    "content_aware_chunker": ContentAwareChunker,
    "structured_chunker": StructuredChunker,
    "entity_based_chunker": EntityBasedChunker,
    "heading_based_chunker": HeadingBasedChunker,
    "delimiter_based_chunker": DelimiterBasedChunker,
    "list_aware_chunker": ListAwareChunker,
    # AI-Powered
    "recursive_chunker": RecursiveChunker,
    "contextual_chunker": ContextualChunker,
    "semantic_chunker": SemanticChunker,
    "similarity_based_chunker": SimilarityBasedChunker,
    "token_based_chunker": TokenBasedChunker,
    "keyword_extraction_chunker": KeywordExtractionChunker,
    "hybrid_chunker": HybridChunker,
}

__all__ = [
    "CHUNKER_REGISTRY",
    "BaseChunker",
    "NaiveChunker",
    "FixedSizeChunker",
    "SlidingWindowChunker",
    "SentenceChunker",
    "ParagraphChunker",
    "PageChunker",
    "TableAwareChunker",
    "TopicBasedChunker",
    "ContentAwareChunker",
    "StructuredChunker",
    "EntityBasedChunker",
    "HeadingBasedChunker",
    "DelimiterBasedChunker",
    "ListAwareChunker",
    "RecursiveChunker",
    "ContextualChunker",
    "SemanticChunker",
    "SimilarityBasedChunker",
    "TokenBasedChunker",
    "KeywordExtractionChunker",
    "HybridChunker",
]
