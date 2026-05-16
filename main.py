"""IRCTC Train Ticket PDF Analyzer — CLI Entry Point.

Usage:
    python main.py --input ./input/pdfs --output ./output
    python main.py --input ./input/pdfs --output ./output --verbose
    python main.py --input ./input/pdfs --output ./output --excel-only
"""

import argparse
import sys
import time
from pathlib import Path

# Ensure project root is on sys.path for package imports
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.linked_list import LinkedList
from parser.pdf_parser import parse_all_tickets
from processing.journey_aggregator import aggregate_by_passenger
from processing.sorter import sort_tickets
from reporting.excel_generator import generate_excel
from reporting.pdf_report_generator import generate_pdf_report
from reporting.visualization import generate_timeline
from utils.constants import (
    APP_NAME,
    APP_VERSION,
    EXCEL_FILENAME,
    PDF_REPORT_FILENAME,
    TIMELINE_FILENAME,
)
from utils.helpers import ensure_dir
from utils.logger import setup_logger


def build_cli() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="irctc-analyzer",
        description=f"{APP_NAME} v{APP_VERSION} — Analyze IRCTC train ticket PDFs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py --input ./input/pdfs --output ./output\n"
            "  python main.py --input ./input/pdfs --output ./output --verbose\n"
            "  python main.py --excel-only\n"
        ),
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "input" / "pdfs",
        help="Directory containing IRCTC ticket PDFs (default: ./input/pdfs)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "output",
        help="Output directory for reports (default: ./output)",
    )
    parser.add_argument(
        "--excel-only",
        action="store_true",
        help="Generate only the Excel report.",
    )
    parser.add_argument(
        "--pdf-only",
        action="store_true",
        help="Generate only the PDF report.",
    )
    parser.add_argument(
        "--timeline-only",
        action="store_true",
        help="Generate only the timeline visualization.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose/debug logging.",
    )

    return parser


def main() -> None:
    """Application entry point."""
    parser = build_cli()
    args = parser.parse_args()

    # Resolve paths
    input_dir: Path = args.input.resolve()
    output_dir: Path = args.output.resolve()

    # Setup
    ensure_dir(output_dir)
    logger = setup_logger(output_dir, verbose=args.verbose)

    logger.info("=" * 60)
    logger.info("  %s v%s", APP_NAME, APP_VERSION)
    logger.info("=" * 60)
    logger.info("Input directory : %s", input_dir)
    logger.info("Output directory: %s", output_dir)

    # Validate input
    if not input_dir.exists():
        logger.error("Input directory does not exist: %s", input_dir)
        sys.exit(1)

    start_time = time.time()

    # Determine which reports to generate
    generate_all = not (args.excel_only or args.pdf_only or args.timeline_only)

    # ---- Step 1: Parse all PDFs ----
    logger.info("-" * 40)
    logger.info("Step 1: Parsing PDFs...")
    tickets: LinkedList = parse_all_tickets(input_dir)

    if not tickets:
        logger.warning("No tickets were successfully parsed. Nothing to report.")
        sys.exit(0)

    # ---- Step 2: Sort chronologically ----
    logger.info("-" * 40)
    logger.info("Step 2: Sorting tickets chronologically...")
    sort_tickets(tickets)

    # Convert to list for reporting
    ticket_list = tickets.to_list()

    # ---- Step 3: Aggregate by passenger ----
    logger.info("-" * 40)
    logger.info("Step 3: Aggregating journeys by passenger...")
    passenger_journeys = aggregate_by_passenger(ticket_list)

    # ---- Step 4: Generate reports ----
    logger.info("-" * 40)
    logger.info("Step 4: Generating reports...")

    timeline_path = output_dir / TIMELINE_FILENAME

    # Timeline (generate before PDF report since it's embedded)
    if generate_all or args.timeline_only:
        try:
            generate_timeline(ticket_list, timeline_path)
        except Exception as exc:
            logger.error("Timeline generation failed: %s", exc)

    # Excel
    if generate_all or args.excel_only:
        try:
            excel_path = output_dir / EXCEL_FILENAME
            generate_excel(ticket_list, passenger_journeys, excel_path)
        except Exception as exc:
            logger.error("Excel generation failed: %s", exc)

    # PDF Report
    if generate_all or args.pdf_only:
        try:
            pdf_path = output_dir / PDF_REPORT_FILENAME
            tl_path = timeline_path if timeline_path.exists() else None
            generate_pdf_report(
                ticket_list, passenger_journeys, tl_path, pdf_path
            )
        except Exception as exc:
            logger.error("PDF report generation failed: %s", exc)

    # ---- Summary ----
    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info("  COMPLETE — %.2f seconds", elapsed)
    logger.info("  Tickets parsed : %d", len(tickets))
    logger.info("  Passengers     : %d", len(passenger_journeys))
    logger.info("  Output dir     : %s", output_dir)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
