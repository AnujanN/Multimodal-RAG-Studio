"""
Advanced chunking techniques (8):
  1. TableAwareChunker     — detects and preserves markdown tables
  2. TopicBasedChunker     — keyword frequency shift detection
  3. ContentAwareChunker   — identifies content types (lists, code, prose)
  4. StructuredChunker     — HTML tags, JSON keys, log entries
  5. EntityBasedChunker    — chunks around named entity groups
  6. HeadingBasedChunker   — splits on markdown/HTML headings
  7. DelimiterBasedChunker — custom user-defined delimiter
  8. ListAwareChunker      — detects and preserves bullet/numbered lists
"""
import re
import json
from html.parser import HTMLParser
from typing import Any

from .base import BaseChunker


class TableAwareChunker(BaseChunker):
    """Detects and preserves markdown table structures as single chunks."""

    name = "table_aware_chunker"
    description = (
        "Identifies markdown tables and keeps them intact as single chunks. "
        "Non-table content is split by paragraphs. Preserves data relationships."
    )
    category = "advanced"
    use_cases = [
        "Financial reports with tables",
        "Spreadsheet content",
        "Data-heavy technical documentation",
        "CSV-structured documents",
    ]
    parameters = []

    def chunk(self, text: str, **kwargs) -> list[str]:
        chunks = []
        current_lines: list[str] = []
        in_table = False

        for line in text.split("\n"):
            is_table_line = bool(re.match(r"^\s*\|", line)) or bool(re.match(r"^\s*[-|]+\s*$", line))

            if is_table_line:
                if not in_table:
                    # Flush accumulated non-table content
                    if current_lines:
                        content = "\n".join(current_lines).strip()
                        if content:
                            chunks.append(content)
                        current_lines = []
                    in_table = True
                current_lines.append(line)
            else:
                if in_table:
                    # Flush the table as one chunk
                    table_content = "\n".join(current_lines).strip()
                    if table_content:
                        chunks.append(table_content)
                    current_lines = []
                    in_table = False
                current_lines.append(line)

        # Flush remaining
        if current_lines:
            content = "\n".join(current_lines).strip()
            if content:
                chunks.append(content)

        return [c for c in chunks if c.strip()]


class TopicBasedChunker(BaseChunker):
    """Detects topic shifts using TF-IDF keyword frequency analysis."""

    name = "topic_based_chunker"
    description = (
        "Splits text when topic shifts are detected by comparing keyword "
        "frequency vectors between consecutive sentence windows."
    )
    category = "advanced"
    use_cases = [
        "Long documents covering multiple topics",
        "Research papers",
        "Multi-subject reports",
        "News articles with topic transitions",
    ]
    parameters = [
        {
            "name": "window_size",
            "type": "int",
            "default": 3,
            "min": 1,
            "max": 10,
            "description": "Number of sentences per sliding window",
        },
        {
            "name": "threshold",
            "type": "float",
            "default": 0.3,
            "min": 0.0,
            "max": 1.0,
            "description": "Similarity threshold — lower = more chunks",
        },
    ]

    def chunk(self, text: str, window_size: int = 3, threshold: float = 0.3, **kwargs) -> list[str]:
        import re
        from collections import Counter
        import math

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        if len(sentences) <= window_size:
            return [text.strip()] if text.strip() else []

        def get_word_freq(sents: list[str]) -> Counter:
            words = " ".join(sents).lower()
            words = re.sub(r"[^\w\s]", "", words)
            return Counter(words.split())

        def cosine_sim(c1: Counter, c2: Counter) -> float:
            vocab = set(c1) | set(c2)
            dot = sum(c1.get(w, 0) * c2.get(w, 0) for w in vocab)
            norm1 = math.sqrt(sum(v ** 2 for v in c1.values()))
            norm2 = math.sqrt(sum(v ** 2 for v in c2.values()))
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)

        chunks = []
        current_chunk: list[str] = []
        window_size = max(1, int(window_size))

        for i, sentence in enumerate(sentences):
            current_chunk.append(sentence)
            if i + 1 < len(sentences) and len(current_chunk) >= window_size:
                window_a = sentences[max(0, i - window_size + 1) : i + 1]
                window_b = sentences[i + 1 : i + 1 + window_size]
                sim = cosine_sim(get_word_freq(window_a), get_word_freq(window_b))
                if sim < threshold:
                    chunks.append(" ".join(current_chunk).strip())
                    current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk).strip())

        return [c for c in chunks if c.strip()]


class ContentAwareChunker(BaseChunker):
    """Identifies content types (code blocks, lists, tables, prose) and chunks accordingly."""

    name = "content_aware_chunker"
    description = (
        "Detects content type transitions (prose, lists, code blocks, tables) "
        "and creates chunk boundaries when the type changes."
    )
    category = "advanced"
    use_cases = [
        "Mixed-format documents",
        "Technical documentation with code examples",
        "Business reports with lists and prose",
        "Markdown documents",
    ]
    parameters = []

    def _get_line_type(self, line: str) -> str:
        stripped = line.strip()
        if not stripped:
            return "empty"
        if stripped.startswith("```") or stripped.startswith("~~~"):
            return "code_fence"
        if re.match(r"^#{1,6}\s", stripped):
            return "heading"
        if re.match(r"^\s*[-*+]\s", stripped) or re.match(r"^\s*\d+\.\s", stripped):
            return "list"
        if re.match(r"^\s*\|", stripped):
            return "table"
        if re.match(r"^>\s", stripped):
            return "blockquote"
        return "prose"

    def chunk(self, text: str, **kwargs) -> list[str]:
        lines = text.split("\n")
        chunks: list[str] = []
        current_lines: list[str] = []
        current_type = "prose"
        in_code_block = False

        for line in lines:
            line_type = self._get_line_type(line)

            if line_type == "code_fence":
                in_code_block = not in_code_block
                current_lines.append(line)
                continue

            if in_code_block:
                current_lines.append(line)
                continue

            if line_type == "empty":
                current_lines.append(line)
                continue

            if line_type != current_type and current_type != "empty":
                content = "\n".join(current_lines).strip()
                if content:
                    chunks.append(content)
                current_lines = []

            current_type = line_type
            current_lines.append(line)

        if current_lines:
            content = "\n".join(current_lines).strip()
            if content:
                chunks.append(content)

        return [c for c in chunks if c.strip()]


class StructuredChunker(BaseChunker):
    """Splits based on document structure: HTML, JSON, or plain log entries."""

    name = "structured_chunker"
    description = (
        "Detects document format (HTML, JSON, log) and uses structure-aware "
        "splitting rules. Falls back to paragraph chunking for plain text."
    )
    category = "advanced"
    use_cases = [
        "HTML web pages",
        "JSON API responses",
        "Application log files",
        "Code documentation with structured markup",
    ]
    parameters = [
        {
            "name": "format_type",
            "type": "select",
            "options": ["auto", "html", "json", "log", "plain"],
            "default": "auto",
            "description": "Document format — 'auto' detects automatically",
        }
    ]

    def _detect_format(self, text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("<") and ">" in stripped:
            return "html"
        if stripped.startswith(("{", "[")):
            try:
                json.loads(stripped)
                return "json"
            except Exception:
                pass
        if re.search(r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}", stripped):
            return "log"
        return "plain"

    def _chunk_html(self, text: str) -> list[str]:
        class _TagExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.chunks: list[str] = []
                self._current: list[str] = []
                self._block_tags = {"p", "div", "section", "article", "h1", "h2", "h3", "li"}

            def handle_starttag(self, tag, attrs):
                if tag in self._block_tags and self._current:
                    text = " ".join(self._current).strip()
                    if text:
                        self.chunks.append(text)
                    self._current = []

            def handle_data(self, data):
                data = data.strip()
                if data:
                    self._current.append(data)

            def finalize(self):
                if self._current:
                    text = " ".join(self._current).strip()
                    if text:
                        self.chunks.append(text)

        parser = _TagExtractor()
        parser.feed(text)
        parser.finalize()
        return parser.chunks or [text]

    def _chunk_json(self, text: str) -> list[str]:
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return [json.dumps(item, indent=2) for item in data]
            elif isinstance(data, dict):
                return [f"{k}:\n{json.dumps(v, indent=2)}" for k, v in data.items()]
        except Exception:
            pass
        return [text]

    def _chunk_log(self, text: str) -> list[str]:
        log_pattern = re.compile(r"(?=\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})")
        parts = log_pattern.split(text)
        return [p.strip() for p in parts if p.strip()]

    def chunk(self, text: str, format_type: str = "auto", **kwargs) -> list[str]:
        fmt = format_type if format_type != "auto" else self._detect_format(text)

        if fmt == "html":
            return self._chunk_html(text)
        elif fmt == "json":
            return self._chunk_json(text)
        elif fmt == "log":
            return self._chunk_log(text)
        else:
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
            return paragraphs or [text]


class EntityBasedChunker(BaseChunker):
    """Groups text by detected named entity types using regex heuristics."""

    name = "entity_based_chunker"
    description = (
        "Chunks text by grouping sentences that contain specific entity types "
        "(person names, locations, organizations, products). Uses regex heuristics."
    )
    category = "advanced"
    use_cases = [
        "Knowledge bases",
        "CRM data extraction",
        "News article indexing",
        "Entity-centric search systems",
    ]
    parameters = [
        {
            "name": "entity_types",
            "type": "multiselect",
            "options": ["person", "location", "organization", "product", "date", "number"],
            "default": ["person", "organization"],
            "description": "Entity types to group chunks around",
        }
    ]

    _PATTERNS = {
        "person": r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",
        "location": r"\b(?:New York|London|Paris|Tokyo|Mumbai|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:City|State|Country|Street|Avenue|Road)))\b",
        "organization": r"\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+(?:Inc|Corp|Ltd|LLC|Company|Group|Institute|University)\b",
        "product": r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b",
        "date": r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+ \d{1,2},? \d{4})\b",
        "number": r"\b\d+(?:[.,]\d+)?(?:\s*(?:million|billion|thousand|%|USD|EUR))?\b",
    }

    def chunk(self, text: str, entity_types: list[str] | None = None, **kwargs) -> list[str]:
        if entity_types is None:
            entity_types = ["person", "organization"]

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        entity_chunks: dict[str, list[str]] = {t: [] for t in entity_types}
        other_sentences: list[str] = []

        patterns = {t: re.compile(self._PATTERNS[t]) for t in entity_types if t in self._PATTERNS}

        for sentence in sentences:
            matched = False
            for entity_type, pattern in patterns.items():
                if pattern.search(sentence):
                    entity_chunks[entity_type].append(sentence)
                    matched = True
                    break
            if not matched:
                other_sentences.append(sentence)

        chunks = []
        for entity_type, sents in entity_chunks.items():
            if sents:
                chunks.append(f"[{entity_type.upper()}]\n" + " ".join(sents))
        if other_sentences:
            chunks.append("[OTHER]\n" + " ".join(other_sentences))

        return [c for c in chunks if c.strip()]


class HeadingBasedChunker(BaseChunker):
    """Splits text on markdown or HTML headings."""

    name = "heading_based_chunker"
    description = (
        "Creates chunk boundaries at heading markers (# H1, ## H2, etc. or <h1>-<h6>). "
        "Each section becomes one chunk. Ideal for structured documents."
    )
    category = "advanced"
    use_cases = [
        "Documentation and wikis",
        "Technical manuals",
        "Markdown articles",
        "Structured reports with sections",
    ]
    parameters = [
        {
            "name": "max_heading_level",
            "type": "int",
            "default": 2,
            "min": 1,
            "max": 6,
            "description": "Maximum heading depth to split on (1=H1 only, 2=H1+H2, etc.)",
        }
    ]

    def chunk(self, text: str, max_heading_level: int = 2, **kwargs) -> list[str]:
        max_heading_level = max(1, min(6, int(max_heading_level)))
        pattern = re.compile(
            r"^(#{1," + str(max_heading_level) + r"})\s.+$", re.MULTILINE
        )

        positions = [m.start() for m in pattern.finditer(text)]
        if not positions:
            return [text.strip()] if text.strip() else []

        chunks = []
        for i, pos in enumerate(positions):
            end = positions[i + 1] if i + 1 < len(positions) else len(text)
            chunk = text[pos:end].strip()
            if chunk:
                chunks.append(chunk)

        # Handle text before first heading
        if positions[0] > 0:
            preamble = text[: positions[0]].strip()
            if preamble:
                chunks.insert(0, preamble)

        return [c for c in chunks if c.strip()]


class DelimiterBasedChunker(BaseChunker):
    """Splits on any user-defined delimiter string."""

    name = "delimiter_based_chunker"
    description = (
        "Splits text on a custom delimiter string. Useful for domain-specific "
        "formats that use consistent separators between records or sections."
    )
    category = "advanced"
    use_cases = [
        "Custom log formats",
        "Domain-specific data files",
        "Structured text with consistent separators",
        "Email threads (split on '---')",
    ]
    parameters = [
        {
            "name": "delimiter",
            "type": "str",
            "default": "---",
            "description": "String to split on (e.g., '---', '###', '\\n\\n')",
        }
    ]

    def chunk(self, text: str, delimiter: str = "---", **kwargs) -> list[str]:
        # Handle escaped newlines
        delimiter = delimiter.replace("\\n", "\n").replace("\\t", "\t")
        parts = text.split(delimiter)
        return [p.strip() for p in parts if p.strip()]


class ListAwareChunker(BaseChunker):
    """Detects and preserves bullet and numbered lists as coherent chunks."""

    name = "list_aware_chunker"
    description = (
        "Identifies list blocks (bullet points, numbered lists) and keeps them "
        "intact. Prose between lists is split by paragraphs."
    )
    category = "advanced"
    use_cases = [
        "Business reports with bullet points",
        "Requirements documents",
        "Meeting notes",
        "Product feature lists",
    ]
    parameters = []

    def _is_list_line(self, line: str) -> bool:
        stripped = line.strip()
        return bool(
            re.match(r"^[-*+•]\s", stripped)
            or re.match(r"^\d+[.)]\s", stripped)
        )

    def chunk(self, text: str, **kwargs) -> list[str]:
        lines = text.split("\n")
        chunks: list[str] = []
        current_lines: list[str] = []
        in_list = False

        for line in lines:
            is_list = self._is_list_line(line)
            is_empty = not line.strip()

            if is_list:
                if not in_list and current_lines:
                    content = "\n".join(current_lines).strip()
                    if content:
                        chunks.append(content)
                    current_lines = []
                in_list = True
                current_lines.append(line)
            elif is_empty:
                if in_list:
                    # End of list
                    content = "\n".join(current_lines).strip()
                    if content:
                        chunks.append(content)
                    current_lines = []
                    in_list = False
                else:
                    current_lines.append(line)
            else:
                if in_list:
                    content = "\n".join(current_lines).strip()
                    if content:
                        chunks.append(content)
                    current_lines = []
                    in_list = False
                current_lines.append(line)

        if current_lines:
            content = "\n".join(current_lines).strip()
            if content:
                chunks.append(content)

        return [c for c in chunks if c.strip()]
