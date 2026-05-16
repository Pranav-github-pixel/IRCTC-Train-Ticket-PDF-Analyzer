"""PDF text extraction with dual-library fallback.

Uses pdfplumber as the primary extractor and falls back to PyMuPDF
(fitz) if pdfplumber fails or returns empty text.
"""

import logging
from pathlib import Path

logger = logging.getLogger("irctc_analyzer")


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract all text content from a PDF file.

    Strategy:
        1. Try ``pdfplumber`` first (generally best for text-layer PDFs).
        2. Fall back to ``PyMuPDF`` (``fitz``) if pdfplumber returns
           empty or raises an exception.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Concatenated text from all pages.

    Raises:
        ValueError: If both extractors fail or produce no text.
    """
    text = _extract_with_pdfplumber(pdf_path)

    if not text or not text.strip():
        logger.debug(
            "pdfplumber returned empty text for %s; trying PyMuPDF.",
            pdf_path.name,
        )
        text = _extract_with_pymupdf(pdf_path)

    if not text or not text.strip():
        raise ValueError(
            f"Both pdfplumber and PyMuPDF failed to extract text "
            f"from '{pdf_path.name}'."
        )

    return text


def _extract_with_pdfplumber(pdf_path: Path) -> str:
    """Extract text using pdfplumber.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text or empty string on failure.
    """
    try:
        import pdfplumber

        pages_text: list[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
        return "\n".join(pages_text)
    except Exception as exc:
        logger.debug(
            "pdfplumber extraction failed for %s: %s",
            pdf_path.name,
            exc,
        )
        return ""


def _extract_with_pymupdf(pdf_path: Path) -> str:
    """Extract text using PyMuPDF (fitz).

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text or empty string on failure.
    """
    try:
        import fitz  # PyMuPDF

        pages_text: list[str] = []
        with fitz.open(pdf_path) as doc:
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    pages_text.append(page_text)
        return "\n".join(pages_text)
    except Exception as exc:
        logger.debug(
            "PyMuPDF extraction failed for %s: %s",
            pdf_path.name,
            exc,
        )
        return ""
