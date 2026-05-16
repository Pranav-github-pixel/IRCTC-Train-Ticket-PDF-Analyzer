# Walkthrough: IRCTC Train Ticket PDF Analyzer

## What Was Built

A complete, production-quality Python CLI application for analyzing IRCTC train ticket PDFs. The system parses PDFs, stores data in a custom linked list, sorts chronologically, and generates three report types.

## Architecture (20+ files across 6 packages)

```
train_ticket/
├── main.py                    # CLI entry point (argparse)
├── requirements.txt           # 7 dependencies
├── README.md                  # Full documentation
├── models/                    # Data models
│   ├── passenger.py           # Passenger @dataclass
│   ├── ticket.py              # Ticket @dataclass with 20+ fields
│   └── linked_list.py         # Custom linked list + merge sort
├── parser/                    # PDF parsing
│   ├── regex_patterns.py      # 25+ compiled regex patterns
│   ├── text_extractor.py      # pdfplumber + PyMuPDF fallback
│   └── pdf_parser.py          # Multi-strategy field extraction
├── processing/                # Data processing
│   ├── sorter.py              # Merge sort wrapper
│   └── journey_aggregator.py  # Per-passenger grouping
├── reporting/                 # Report generation
│   ├── excel_generator.py     # 2-sheet Excel (pandas + openpyxl)
│   ├── visualization.py       # Plotly timeline
│   └── pdf_report_generator.py # 4-section ReportLab PDF
└── utils/                     # Shared utilities
    ├── logger.py              # Dual-handler logging
    ├── helpers.py             # Date/currency parsing
    └── constants.py           # App-wide config
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **IRCTC ERS-specific regex** | Real PDF analysis revealed combined PNR/Train lines, 3-station format, and `Start Date*/Departure*/Arrival*` schedule lines unique to IRCTC |
| **Multi-strategy parsing** | Each field has 2-3 extraction strategies (IRCTC ERS format → generic regex → fallback) |
| **ASCII-only logging** | Windows cp1252 console can't encode Unicode box-drawing/checkmark characters |
| **`_extract_field` returns first non-None group** | Multi-alternative regex patterns use `\|` with different capture groups |

## Testing Results

Tested with a real IRCTC ticket PDF (`1_Mumbai Central To Maninagar 21May2026.pdf`):

| Field | Extracted Value |
|-------|----------------|
| PNR | 8248433572 |
| Train | 09081 MMCT MAN SF SPL |
| From | MUMBAI CENTRAL (MMCT) |
| To | MANINAGAR (MAN) |
| Departure | 21-May-2026 23:20 |
| Arrival | 22-May-2026 07:25 |
| Booking | 14-May-2026 08:53:54 |
| Class | 3A |
| Quota | GN |
| Distance | 488 km |
| Fare | 1,129.05 |
| Passenger | SAYALI KHADSE, B1-54, UPPER |
| GSTIN | 07AAAGM0289C1ZL |

## Generated Outputs

All 4 output files generated successfully:

| File | Size | Status |
|------|------|--------|
| `tickets_analysis.xlsx` | 6.7 KB | 2 sheets, styled |
| `tickets_report.pdf` | 66.7 KB | 4 sections |
| `journey_timeline.png` | 152 KB | Professional Plotly chart |
| `error_log.txt` | Empty (no errors) | As expected |

## Timeline Preview

![Journey Timeline](file:///c:/projects/train_ticket/output/journey_timeline.png)
