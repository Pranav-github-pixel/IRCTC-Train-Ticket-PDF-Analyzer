# IRCTC Train Ticket PDF Analyzer

Python application for analyzing Indian Railway / IRCTC train ticket PDFs.

## Features

- **PDF Parsing** — Extracts structured data from IRCTC ticket PDFs using dual-library extraction (pdfplumber + PyMuPDF fallback)
- **Excel Reports** — Multi-sheet workbook with all ticket data and per-passenger journey summaries
- **Timeline Visualization** — Professional Plotly-based chronological journey timeline
- **PDF Report** — Polished ReportLab PDF with executive summary, tables, and embedded timeline
- **Error Resilience** — Per-file error handling ensures one bad PDF never crashes the pipeline

## Architecture

```
project_root/
├── main.py                          # CLI entry point
├── requirements.txt
├── README.md
│
├── models/                          # Data models
│   ├── passenger.py                 # Passenger dataclass
│   ├── ticket.py                    # Ticket dataclass
│   └── linked_list.py              # Custom linked list + merge sort
│
├── parser/                          # PDF parsing
│   ├── regex_patterns.py            # Compiled regex patterns
│   ├── text_extractor.py            # PDF text extraction (dual-library)
│   └── pdf_parser.py               # High-level parsing orchestrator
│
├── processing/                      # Data processing
│   ├── sorter.py                    # Chronological sorting
│   └── journey_aggregator.py       # Per-passenger grouping
│
├── reporting/                       # Report generation
│   ├── excel_generator.py           # Multi-sheet Excel report
│   ├── visualization.py            # Plotly timeline
│   └── pdf_report_generator.py     # ReportLab PDF report
│
├── utils/                           # Shared utilities
│   ├── logger.py                    # Dual-handler logging setup
│   ├── helpers.py                   # Date/currency parsing, text cleaning
│   └── constants.py                # Application-wide constants
│
├── input/pdfs/                      # Place IRCTC ticket PDFs here
├── output/                          # Generated reports
└── tests/                           # Test suite
```

## Installation

```bash
# 1. Clone or navigate to the project
cd train_ticket

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

Place your IRCTC ticket PDFs in `input/pdfs/`, then run:

```bash
python main.py
```

### Custom Directories

```bash
python main.py --input ./my_tickets --output ./my_reports
```

### Selective Report Generation

```bash
python main.py --excel-only       # Excel report only
python main.py --pdf-only         # PDF report only
python main.py --timeline-only    # Timeline visualization only
```

### Verbose Mode

```bash
python main.py --verbose
```

### Full Example

```bash
python main.py --input ./input/pdfs --output ./output --verbose
```

## Output Files

| File | Description |
|------|-------------|
| `tickets_analysis.xlsx` | Multi-sheet Excel workbook with all ticket data |
| `tickets_report.pdf` | Professional PDF report with executive summary |
| `journey_timeline.png` | Chronological timeline visualization |
| `error_log.txt` | Detailed log of any parsing failures |

## Supported PDF Formats

- Standard IRCTC e-ticket PDFs
- Text-based PDFs (not scanned images)
- Single and multi-passenger tickets
- Various IRCTC formatting versions

## Error Handling

The application **never crashes** due to a bad PDF. Each file is parsed independently:

- Successful parses → included in reports
- Failed parses → logged to `error_log.txt` with full stack traces
- Processing continues regardless of individual failures

## Tech Stack

- **Python 3.10+**
- **pdfplumber** / **PyMuPDF** — PDF text extraction
- **pandas** / **openpyxl** — Excel generation
- **plotly** / **kaleido** — Timeline visualization
- **reportlab** — PDF report generation
