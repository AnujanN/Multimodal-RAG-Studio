"""
Document parser using Docling + RapidOCR for structured Markdown output.

Supported formats:
  - .pdf          → Docling (text + scanned via RapidOCR)
  - .png/.jpg/.jpeg/.tiff → Docling + RapidOCR
  - .docx         → python-docx
  - .txt/.md      → plain UTF-8
  - .csv          → csv module
  - .json         → json module
  - .html         → html.parser
"""
import csv
import io
import json
import logging
import re
import tempfile
import os
from html.parser import HTMLParser
from pathlib import Path

logger = logging.getLogger(__name__)


class FileParser:
    SUPPORTED_EXTENSIONS = {
        ".pdf", ".png", ".jpg", ".jpeg", ".tiff",
        ".docx",
        ".txt", ".md", ".csv", ".json", ".html",
    }
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

    def __init__(self):
        self._docling_converter = None

    def _get_docling_converter(self):
        """Lazy-initialize Docling converter with RapidOCR backend."""
        if self._docling_converter is None:
            try:
                from docling.document_converter import DocumentConverter, PdfFormatOption
                from docling.datamodel.pipeline_options import (
                    PdfPipelineOptions,
                    RapidOcrOptions,
                )
                from docling.datamodel.base_models import InputFormat

                pipeline_options = PdfPipelineOptions()
                pipeline_options.do_ocr = True
                pipeline_options.ocr_options = RapidOcrOptions()

                self._docling_converter = DocumentConverter(
                    format_options={
                        InputFormat.PDF: PdfFormatOption(
                            pipeline_options=pipeline_options
                        ),
                    }
                )
                logger.info("Docling converter initialized with RapidOCR backend")
            except ImportError as e:
                logger.warning(f"Docling not available: {e}. PDF parsing will be limited.")
                self._docling_converter = None
        return self._docling_converter

    async def parse(self, filename: str, content: bytes, file_size: int) -> dict:
        """
        Parse file content and return extracted text with metadata.

        Returns:
            {
                "text": str,
                "filename": str,
                "extension": str,
                "character_count": int,
                "parser_used": str,
            }
        """
        if file_size > self.MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"File too large: {file_size / 1024 / 1024:.1f}MB. Maximum is 10MB."
            )

        ext = Path(filename).suffix.lower()

        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: '{ext}'. "
                f"Supported: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

        if ext in {".pdf", ".png", ".jpg", ".jpeg", ".tiff"}:
            text, parser_used = await self._parse_with_docling(content, ext)
        elif ext == ".docx":
            text, parser_used = self._parse_docx(content)
        elif ext == ".csv":
            text, parser_used = self._parse_csv(content)
        elif ext == ".json":
            text, parser_used = self._parse_json(content)
        elif ext == ".html":
            text, parser_used = self._parse_html(content)
        else:  # .txt, .md
            text, parser_used = self._parse_text(content)

        return {
            "filename": filename,
            "extension": ext,
            "text": text,
            "character_count": len(text),
            "parser_used": parser_used,
        }

    async def _parse_with_docling(self, content: bytes, ext: str) -> tuple[str, str]:
        """Use Docling to convert PDF/image → structured Markdown with RapidOCR."""
        converter = self._get_docling_converter()

        if converter is None:
            # Fallback for PDFs if docling not installed
            if ext == ".pdf":
                return self._parse_pdf_fallback(content)
            return "", "error: docling not available"

        # Write to temp file (Docling needs a file path)
        suffix = ext if ext != ".jpeg" else ".jpg"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            result = converter.convert(tmp_path)
            markdown_text = result.document.export_to_markdown()
            return markdown_text, "docling+rapidocr"
        except Exception as e:
            logger.error(f"Docling conversion failed: {e}")
            if ext == ".pdf":
                return self._parse_pdf_fallback(content)
            return f"[Error parsing file: {e}]", "error"
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def _parse_pdf_fallback(self, content: bytes) -> tuple[str, str]:
        """Fallback PDF text extraction using pypdf if docling fails."""
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n\n".join(pages), "pypdf-fallback"
        except ImportError:
            return "[PDF parsing unavailable. Install docling or pypdf.]", "error"
        except Exception as e:
            return f"[Error reading PDF: {e}]", "error"

    def _parse_docx(self, content: bytes) -> tuple[str, str]:
        """Extract text from DOCX using python-docx."""
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    # Detect headings and format as markdown
                    if para.style.name.startswith("Heading"):
                        level = para.style.name.replace("Heading ", "")
                        try:
                            level_num = int(level)
                            parts.append("#" * level_num + " " + para.text.strip())
                        except ValueError:
                            parts.append(para.text.strip())
                    else:
                        parts.append(para.text.strip())

            # Extract tables
            for table in doc.tables:
                rows = []
                for i, row in enumerate(table.rows):
                    cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                    rows.append("| " + " | ".join(cells) + " |")
                    if i == 0:
                        rows.append("|" + " --- |" * len(cells))
                parts.append("\n".join(rows))

            return "\n\n".join(parts), "python-docx"
        except ImportError:
            return "[DOCX parsing unavailable. Install python-docx.]", "error"
        except Exception as e:
            return f"[Error reading DOCX: {e}]", "error"

    def _parse_csv(self, content: bytes) -> tuple[str, str]:
        """Convert CSV to readable text format."""
        try:
            text = content.decode("utf-8", errors="replace")
            reader = csv.reader(io.StringIO(text))
            rows = list(reader)

            if not rows:
                return "", "csv-builtin"

            # Format as markdown table
            lines = []
            for i, row in enumerate(rows):
                lines.append("| " + " | ".join(cell.strip() for cell in row) + " |")
                if i == 0:
                    lines.append("|" + " --- |" * len(row))

            return "\n".join(lines), "csv-builtin"
        except Exception as e:
            return f"[Error reading CSV: {e}]", "error"

    def _parse_json(self, content: bytes) -> tuple[str, str]:
        """Pretty-print JSON content."""
        try:
            text = content.decode("utf-8", errors="replace")
            data = json.loads(text)
            return json.dumps(data, indent=2, ensure_ascii=False), "json-builtin"
        except json.JSONDecodeError:
            # Not valid JSON, return as text
            return content.decode("utf-8", errors="replace"), "text-fallback"
        except Exception as e:
            return f"[Error reading JSON: {e}]", "error"

    def _parse_html(self, content: bytes) -> tuple[str, str]:
        """Strip HTML tags and extract text."""
        class _TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.chunks: list[str] = []
                self._skip_tags = {"script", "style", "meta", "link", "head"}
                self._block_tags = {
                    "p", "div", "section", "article", "li", "blockquote",
                    "h1", "h2", "h3", "h4", "h5", "h6",
                }
                self._current_tag = ""
                self._skip = False

            def handle_starttag(self, tag, attrs):
                self._current_tag = tag
                if tag in self._skip_tags:
                    self._skip = True

            def handle_endtag(self, tag):
                if tag in self._skip_tags:
                    self._skip = False

            def handle_data(self, data):
                if not self._skip:
                    data = data.strip()
                    if data:
                        self.chunks.append(data)

        try:
            text = content.decode("utf-8", errors="replace")
            extractor = _TextExtractor()
            extractor.feed(text)
            return "\n\n".join(extractor.chunks), "html-builtin"
        except Exception as e:
            return f"[Error reading HTML: {e}]", "error"

    def _parse_text(self, content: bytes) -> tuple[str, str]:
        """Decode plain text / markdown files."""
        try:
            return content.decode("utf-8", errors="replace"), "text-builtin"
        except Exception as e:
            return f"[Error reading file: {e}]", "error"
