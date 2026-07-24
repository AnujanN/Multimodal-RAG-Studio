"""
AI-Powered chunking techniques (7):
  1. RecursiveChunker          — hierarchical separator splitting
  2. ContextualChunker         — prepends parent heading context to each chunk
  3. SemanticChunker           — FastEmbed embeddings + similarity threshold
  4. SimilarityBasedChunker    — sentence grouping by embedding similarity
  5. TokenBasedChunker         — tiktoken token-count splitting
  6. KeywordExtractionChunker  — TF-IDF keyword-anchored chunks
  7. HybridChunker             — combines multiple techniques
"""
import re
from typing import Any

from .base import BaseChunker


class RecursiveChunker(BaseChunker):
    """Recursively splits using a hierarchy of separators."""

    name = "recursive_chunker"
    description = (
        "Splits text using a hierarchy of separators (paragraph → sentence → word). "
        "If a chunk exceeds chunk_size, it's recursively split with the next separator. "
        "Similar to LangChain's RecursiveCharacterTextSplitter."
    )
    category = "ai_powered"
    use_cases = [
        "General-purpose RAG pipelines",
        "When chunk size must be controlled precisely",
        "Mixed content that needs smart splitting",
        "LangChain-compatible workflows",
    ]
    parameters = [
        {
            "name": "chunk_size",
            "type": "int",
            "default": 500,
            "min": 50,
            "max": 5000,
            "description": "Target maximum characters per chunk",
        },
        {
            "name": "overlap",
            "type": "int",
            "default": 50,
            "min": 0,
            "max": 500,
            "description": "Overlap characters between chunks",
        },
    ]

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", " ", ""]

    def _split_recursive(self, text: str, separators: list[str], chunk_size: int) -> list[str]:
        if not separators:
            return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

        sep = separators[0]
        remaining_seps = separators[1:]

        if sep:
            parts = text.split(sep)
        else:
            parts = list(text)

        chunks: list[str] = []
        current = ""

        for part in parts:
            test = (current + sep + part) if current else part
            if len(test) <= chunk_size:
                current = test
            else:
                if current:
                    chunks.append(current)
                if len(part) > chunk_size:
                    # Recurse with next separator
                    sub_chunks = self._split_recursive(part, remaining_seps, chunk_size)
                    chunks.extend(sub_chunks)
                    current = ""
                else:
                    current = part

        if current:
            chunks.append(current)

        return chunks

    def chunk(self, text: str, chunk_size: int = 500, overlap: int = 50, **kwargs) -> list[str]:
        chunk_size = max(1, int(chunk_size))
        overlap = max(0, int(overlap))

        raw_chunks = self._split_recursive(text, self.DEFAULT_SEPARATORS, chunk_size)

        if overlap == 0:
            return [c.strip() for c in raw_chunks if c.strip()]

        # Apply overlap
        result = []
        for i, chunk in enumerate(raw_chunks):
            if i > 0 and overlap > 0:
                prev = raw_chunks[i - 1]
                suffix = prev[-overlap:] if len(prev) >= overlap else prev
                chunk = suffix + chunk
            result.append(chunk.strip())

        return [c for c in result if c.strip()]


class ContextualChunker(BaseChunker):
    """Prepends parent heading context to each chunk for better retrieval."""

    name = "contextual_chunker"
    description = (
        "Splits on headings, then prepends the document title and parent heading "
        "to each chunk. Improves retrieval accuracy by giving each chunk full context."
    )
    category = "ai_powered"
    use_cases = [
        "RAG systems where out-of-context chunks cause poor retrieval",
        "Long documents with many sections",
        "Knowledge base indexing",
        "Multi-level documentation",
    ]
    parameters = [
        {
            "name": "max_heading_level",
            "type": "int",
            "default": 2,
            "min": 1,
            "max": 6,
            "description": "Maximum heading level to use as context boundary",
        }
    ]

    def chunk(self, text: str, max_heading_level: int = 2, **kwargs) -> list[str]:
        max_heading_level = max(1, min(6, int(max_heading_level)))
        heading_pattern = re.compile(
            r"^(#{1," + str(max_heading_level) + r"})\s+(.+)$", re.MULTILINE
        )

        matches = list(heading_pattern.finditer(text))
        if not matches:
            return [text.strip()] if text.strip() else []

        chunks = []
        breadcrumb: list[str] = []

        # Handle preamble
        if matches[0].start() > 0:
            preamble = text[: matches[0].start()].strip()
            if preamble:
                chunks.append(preamble)

        for i, match in enumerate(matches):
            level = len(match.group(1))
            heading_text = match.group(2).strip()

            # Update breadcrumb
            breadcrumb = breadcrumb[: level - 1]
            breadcrumb.append(heading_text)

            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section_body = text[match.end() : end].strip()

            context = " > ".join(breadcrumb)
            chunk = f"[Context: {context}]\n\n{section_body}" if section_body else f"[Context: {context}]"
            chunks.append(chunk)

        return [c for c in chunks if c.strip()]


class SemanticChunker(BaseChunker):
    """Uses FastEmbed sentence embeddings to find natural topic boundaries."""

    name = "semantic_chunker"
    description = (
        "Computes sentence embeddings using FastEmbed (BAAI/bge-small-en-v1.5 ONNX model, ~67MB). "
        "Creates chunk boundaries where cosine similarity between consecutive sentences "
        "drops below the threshold. Produces semantically coherent chunks."
    )
    category = "ai_powered"
    use_cases = [
        "High-quality RAG systems",
        "Research paper indexing",
        "Complex documents with subtle topic shifts",
        "When semantic coherence is critical",
    ]
    parameters = [
        {
            "name": "similarity_threshold",
            "type": "float",
            "default": 0.5,
            "min": 0.1,
            "max": 0.99,
            "description": "Cosine similarity threshold — lower = more chunks, higher = fewer larger chunks",
        },
        {
            "name": "min_chunk_sentences",
            "type": "int",
            "default": 2,
            "min": 1,
            "max": 10,
            "description": "Minimum number of sentences per chunk",
        },
    ]

    _model = None

    @classmethod
    def _get_model(cls):
        if cls._model is None:
            from fastembed import TextEmbedding
            cls._model = TextEmbedding("BAAI/bge-small-en-v1.5")
        return cls._model

    def chunk(
        self,
        text: str,
        similarity_threshold: float = 0.5,
        min_chunk_sentences: int = 2,
        **kwargs,
    ) -> list[str]:
        import numpy as np

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) <= min_chunk_sentences:
            return [text.strip()] if text.strip() else []

        model = self._get_model()
        embeddings = list(model.embed(sentences))

        def cosine_sim(a, b):
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return float(np.dot(a, b) / (norm_a * norm_b))

        chunks = []
        current: list[str] = [sentences[0]]

        for i in range(1, len(sentences)):
            sim = cosine_sim(embeddings[i - 1], embeddings[i])
            if sim < similarity_threshold and len(current) >= min_chunk_sentences:
                chunks.append(" ".join(current))
                current = [sentences[i]]
            else:
                current.append(sentences[i])

        if current:
            chunks.append(" ".join(current))

        return [c for c in chunks if c.strip()]


class SimilarityBasedChunker(BaseChunker):
    """Groups sentences by embedding similarity using configurable distance metrics."""

    name = "similarity_based_chunker"
    description = (
        "Groups consecutive sentences that are similar using FastEmbed embeddings. "
        "Supports cosine, Jaccard (on tokens), and Levenshtein (on characters) metrics."
    )
    category = "ai_powered"
    use_cases = [
        "Topic-coherent retrieval",
        "Deduplication-aware chunking",
        "When controlling similarity metric is important",
        "Comparative analysis between distance metrics",
    ]
    parameters = [
        {
            "name": "distance_metric",
            "type": "select",
            "options": ["cosine", "jaccard", "levenshtein"],
            "default": "cosine",
            "description": "Distance metric for comparing consecutive sentences",
        },
        {
            "name": "threshold",
            "type": "float",
            "default": 0.5,
            "min": 0.1,
            "max": 0.99,
            "description": "Similarity threshold to determine chunk boundaries",
        },
    ]

    _model = None

    @classmethod
    def _get_model(cls):
        if cls._model is None:
            from fastembed import TextEmbedding
            cls._model = TextEmbedding("BAAI/bge-small-en-v1.5")
        return cls._model

    def _jaccard(self, a: str, b: str) -> float:
        set_a = set(a.lower().split())
        set_b = set(b.lower().split())
        if not set_a and not set_b:
            return 1.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0

    def _levenshtein(self, a: str, b: str) -> float:
        # Normalized similarity (1 - normalized edit distance)
        if a == b:
            return 1.0
        la, lb = len(a), len(b)
        if la == 0 or lb == 0:
            return 0.0
        dp = list(range(lb + 1))
        for i in range(1, la + 1):
            prev = dp[:]
            dp[0] = i
            for j in range(1, lb + 1):
                cost = 0 if a[i - 1] == b[j - 1] else 1
                dp[j] = min(dp[j] + 1, dp[j - 1] + 1, prev[j - 1] + cost)
        return 1.0 - dp[lb] / max(la, lb)

    def chunk(
        self,
        text: str,
        distance_metric: str = "cosine",
        threshold: float = 0.5,
        **kwargs,
    ) -> list[str]:
        import numpy as np

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) <= 1:
            return [text.strip()] if text.strip() else []

        def similarity(a_idx: int, b_idx: int) -> float:
            if distance_metric == "jaccard":
                return self._jaccard(sentences[a_idx], sentences[b_idx])
            elif distance_metric == "levenshtein":
                return self._levenshtein(sentences[a_idx], sentences[b_idx])
            else:  # cosine — use FastEmbed
                embs = list(self._get_model().embed([sentences[a_idx], sentences[b_idx]]))
                a_emb, b_emb = embs[0], embs[1]
                norm_a = np.linalg.norm(a_emb)
                norm_b = np.linalg.norm(b_emb)
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return float(np.dot(a_emb, b_emb) / (norm_a * norm_b))

        # For cosine, batch embed all sentences
        if distance_metric == "cosine":
            embeddings = list(self._get_model().embed(sentences))
            def cosine_batch(a_idx, b_idx):
                a_emb, b_emb = embeddings[a_idx], embeddings[b_idx]
                norm_a = np.linalg.norm(a_emb)
                norm_b = np.linalg.norm(b_emb)
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return float(np.dot(a_emb, b_emb) / (norm_a * norm_b))
            sim_fn = cosine_batch
        else:
            sim_fn = similarity

        chunks = []
        current = [sentences[0]]

        for i in range(1, len(sentences)):
            sim = sim_fn(i - 1, i)
            if sim < threshold:
                chunks.append(" ".join(current))
                current = [sentences[i]]
            else:
                current.append(sentences[i])

        if current:
            chunks.append(" ".join(current))

        return [c for c in chunks if c.strip()]


class TokenBasedChunker(BaseChunker):
    """Splits by token count using tiktoken — LLM-token-aware chunking."""

    name = "token_based_chunker"
    description = (
        "Splits text by LLM token count using tiktoken. Ensures chunks "
        "fit within LLM context windows. Supports GPT-4, GPT-3.5, and cl100k_base encodings."
    )
    category = "ai_powered"
    use_cases = [
        "LLM-optimized RAG pipelines",
        "When precise token budget control is needed",
        "OpenAI API integration",
        "Context window management",
    ]
    parameters = [
        {
            "name": "max_tokens",
            "type": "int",
            "default": 256,
            "min": 32,
            "max": 4096,
            "description": "Maximum tokens per chunk",
        },
        {
            "name": "encoding",
            "type": "select",
            "options": ["cl100k_base", "p50k_base", "r50k_base"],
            "default": "cl100k_base",
            "description": "Tokenizer encoding (cl100k_base = GPT-4/GPT-3.5)",
        },
    ]

    def chunk(self, text: str, max_tokens: int = 256, encoding: str = "cl100k_base", **kwargs) -> list[str]:
        try:
            import tiktoken
            enc = tiktoken.get_encoding(encoding)
        except Exception:
            # Fallback: rough approximation (1 token ≈ 4 chars)
            approx_chars = max_tokens * 4
            return [text[i : i + approx_chars] for i in range(0, len(text), approx_chars)]

        tokens = enc.encode(text)
        max_tokens = max(1, int(max_tokens))
        chunks = []

        for i in range(0, len(tokens), max_tokens):
            token_slice = tokens[i : i + max_tokens]
            chunk_text = enc.decode(token_slice).strip()
            if chunk_text:
                chunks.append(chunk_text)

        return chunks


class KeywordExtractionChunker(BaseChunker):
    """TF-IDF keyword-anchored chunking — groups sentences around top keywords."""

    name = "keyword_extraction_chunker"
    description = (
        "Extracts top keywords using TF-IDF (scikit-learn), then groups sentences "
        "containing the same primary keyword into chunks. Search-optimized."
    )
    category = "ai_powered"
    use_cases = [
        "Search-optimized indexing",
        "Keyword-based retrieval systems",
        "Topic extraction and clustering",
        "SEO and content analysis",
    ]
    parameters = [
        {
            "name": "num_keywords",
            "type": "int",
            "default": 5,
            "min": 2,
            "max": 20,
            "description": "Number of top keywords to extract",
        },
        {
            "name": "min_sentences_per_chunk",
            "type": "int",
            "default": 2,
            "min": 1,
            "max": 10,
            "description": "Minimum sentences per keyword group chunk",
        },
    ]

    def chunk(
        self,
        text: str,
        num_keywords: int = 5,
        min_sentences_per_chunk: int = 2,
        **kwargs,
    ) -> list[str]:
        from sklearn.feature_extraction.text import TfidfVectorizer

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return [text.strip()] if text.strip() else []

        # Extract keywords via TF-IDF
        try:
            vectorizer = TfidfVectorizer(
                max_features=int(num_keywords),
                stop_words="english",
            )
            vectorizer.fit([text])
            keywords = vectorizer.get_feature_names_out().tolist()
        except Exception:
            # Fallback to frequency-based keywords
            words = re.findall(r"\b[a-z]{4,}\b", text.lower())
            from collections import Counter
            keywords = [w for w, _ in Counter(words).most_common(num_keywords)]

        # Group sentences by dominant keyword
        keyword_groups: dict[str, list[str]] = {kw: [] for kw in keywords}
        other: list[str] = []

        for sentence in sentences:
            lower = sentence.lower()
            matched_kw = next((kw for kw in keywords if kw in lower), None)
            if matched_kw:
                keyword_groups[matched_kw].append(sentence)
            else:
                other.append(sentence)

        chunks = []
        for kw, sents in keyword_groups.items():
            if len(sents) >= min_sentences_per_chunk:
                chunks.append(f"[Keyword: {kw}]\n" + " ".join(sents))
        if other:
            chunks.append("[Other]\n" + " ".join(other))

        return [c for c in chunks if c.strip()]


class HybridChunker(BaseChunker):
    """Combines HeadingBased → RecursiveChunker for two-pass structure-aware chunking."""

    name = "hybrid_chunker"
    description = (
        "Two-pass chunking: first splits on headings to get sections, "
        "then applies recursive splitting to any section that exceeds the size limit. "
        "Best of structure-awareness and size control."
    )
    category = "ai_powered"
    use_cases = [
        "Production RAG systems",
        "Long structured documents",
        "Documents with both headings and long prose sections",
        "When you need both semantic structure and size control",
    ]
    parameters = [
        {
            "name": "max_chunk_size",
            "type": "int",
            "default": 800,
            "min": 100,
            "max": 5000,
            "description": "Maximum characters per final chunk",
        },
        {
            "name": "heading_level",
            "type": "int",
            "default": 2,
            "min": 1,
            "max": 6,
            "description": "Heading depth for initial section split",
        },
    ]

    def chunk(self, text: str, max_chunk_size: int = 800, heading_level: int = 2, **kwargs) -> list[str]:
        from .advanced import HeadingBasedChunker

        heading_chunker = HeadingBasedChunker()
        recursive_chunker = RecursiveChunker()

        sections = heading_chunker.chunk(text, max_heading_level=heading_level)

        final_chunks = []
        for section in sections:
            if len(section) <= max_chunk_size:
                final_chunks.append(section)
            else:
                sub_chunks = recursive_chunker.chunk(
                    section, chunk_size=max_chunk_size, overlap=50
                )
                final_chunks.extend(sub_chunks)

        return [c for c in final_chunks if c.strip()]
