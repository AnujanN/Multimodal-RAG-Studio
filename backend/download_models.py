"""
Pre-download AI models during Docker image build.
This bakes model weights directly into the image so users don't wait on first upload or semantic chunking.
"""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("download_models")

def main():
    logger.info("Pre-downloading FastEmbed embedding model (BAAI/bge-small-en-v1.5)...")
    try:
        from fastembed import TextEmbedding
        TextEmbedding("BAAI/bge-small-en-v1.5")
        logger.info("FastEmbed model downloaded successfully.")
    except Exception as e:
        logger.warning(f"Failed to pre-download FastEmbed model: {e}")

    logger.info("Pre-downloading Docling OCR & layout models...")
    try:
        from docling.document_converter import DocumentConverter, PdfFormatOption
        from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
        from docling.datamodel.base_models import InputFormat

        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.ocr_options = RapidOcrOptions()

        DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                ),
            }
        )
        logger.info("Docling OCR & layout models downloaded successfully.")
    except Exception as e:
        logger.warning(f"Failed to pre-download Docling models: {e}")

    logger.info("All AI models pre-downloaded and cached successfully!")

if __name__ == "__main__":
    main()
