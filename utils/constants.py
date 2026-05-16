"""Application-wide constants and configuration values."""

from typing import Final

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------
APP_NAME: Final[str] = "IRCTC Train Ticket Analyzer"
APP_VERSION: Final[str] = "1.0.0"

# ---------------------------------------------------------------------------
# Default paths (relative to project root)
# ---------------------------------------------------------------------------
DEFAULT_INPUT_DIR: Final[str] = "input/pdfs"
DEFAULT_OUTPUT_DIR: Final[str] = "output"

# ---------------------------------------------------------------------------
# Output file names
# ---------------------------------------------------------------------------
EXCEL_FILENAME: Final[str] = "tickets_analysis.xlsx"
PDF_REPORT_FILENAME: Final[str] = "tickets_report.pdf"
TIMELINE_FILENAME: Final[str] = "journey_timeline.png"
ERROR_LOG_FILENAME: Final[str] = "error_log.txt"

# ---------------------------------------------------------------------------
# Excel sheet names
# ---------------------------------------------------------------------------
SHEET_ALL_TICKETS: Final[str] = "All Tickets"
SHEET_PASSENGER_SUMMARY: Final[str] = "Passenger Journey Summary"

# ---------------------------------------------------------------------------
# Date/time format strings (ordered by frequency in IRCTC PDFs)
# ---------------------------------------------------------------------------
DATETIME_FORMATS: Final[list[str]] = [
    "%d-%b-%Y %H:%M",      # 21-May-2026 23:20
    "%d-%b-%Y %H:%M:%S",   # 21-May-2026 23:20:00
    "%d/%m/%Y %H:%M",      # 21/05/2026 23:20
    "%d/%m/%Y %H:%M:%S",   # 21/05/2026 23:20:00
    "%d-%m-%Y %H:%M",      # 21-05-2026 23:20
    "%d-%m-%Y %H:%M:%S",   # 21-05-2026 23:20:00
    "%Y-%m-%d %H:%M",      # 2026-05-21 23:20
    "%Y-%m-%d %H:%M:%S",   # 2026-05-21 23:20:00
]

DATE_ONLY_FORMATS: Final[list[str]] = [
    "%d-%b-%Y",    # 21-May-2026
    "%d/%m/%Y",    # 21/05/2026
    "%d-%m-%Y",    # 21-05-2026
    "%Y-%m-%d",    # 2026-05-21
]

# ---------------------------------------------------------------------------
# PDF report styling
# ---------------------------------------------------------------------------
REPORT_TITLE: Final[str] = "IRCTC Train Ticket Analysis Report"
REPORT_FONT_FAMILY: Final[str] = "Helvetica"

# ---------------------------------------------------------------------------
# Timeline visualization
# ---------------------------------------------------------------------------
TIMELINE_WIDTH: Final[int] = 1400
TIMELINE_HEIGHT_PER_ENTRY: Final[int] = 60
TIMELINE_MIN_HEIGHT: Final[int] = 500
TIMELINE_DPI: Final[int] = 200

# ---------------------------------------------------------------------------
# Color palette (professional, muted tones)
# ---------------------------------------------------------------------------
COLORS: Final[list[str]] = [
    "#2E86AB",  # Steel Blue
    "#A23B72",  # Plum
    "#F18F01",  # Amber
    "#C73E1D",  # Vermilion
    "#3B1F2B",  # Dark Burgundy
    "#44BBA4",  # Teal
    "#E94F37",  # Red-Orange
    "#393E41",  # Charcoal
    "#8D6A9F",  # Amethyst
    "#1B998B",  # Persian Green
]
