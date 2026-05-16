"""PDF report generator using ReportLab.

Produces a professional multi-section PDF report containing:
  1. Executive Summary
  2. All Tickets Table
  3. Passenger Journey Summaries
  4. Embedded Timeline Visualization
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch, mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from models.ticket import Ticket
from processing.journey_aggregator import JourneyEntry
from utils.constants import APP_NAME, APP_VERSION, REPORT_TITLE

logger = logging.getLogger("irctc_analyzer")

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
PRIMARY = colors.HexColor("#1F4E79")
SECONDARY = colors.HexColor("#2E75B6")
LIGHT_BG = colors.HexColor("#D6E4F0")
WHITE = colors.white
DARK_TEXT = colors.HexColor("#333333")
LIGHT_GREY = colors.HexColor("#F5F5F5")


def generate_pdf_report(
    tickets: list[Ticket],
    passenger_journeys: dict[str, list[JourneyEntry]],
    timeline_path: Optional[Path],
    output_path: Path,
) -> None:
    """Generate a professional PDF report.

    Args:
        tickets: Sorted list of tickets.
        passenger_journeys: Per-passenger journey data.
        timeline_path: Path to timeline PNG (embedded if exists).
        output_path: Output PDF path.
    """
    logger.info("Generating PDF report: %s", output_path.name)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=landscape(A4),
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        title=REPORT_TITLE,
        author=APP_NAME,
    )

    styles = _build_styles()
    elements: list = []

    # Section 1: Executive Summary
    elements.extend(_build_executive_summary(tickets, styles))
    elements.append(PageBreak())

    # Section 2: All Tickets Table
    elements.extend(_build_tickets_table(tickets, styles))
    elements.append(PageBreak())

    # Section 3: Passenger Journey Summaries
    elements.extend(
        _build_passenger_summaries(passenger_journeys, styles)
    )

    # Section 4: Timeline Image
    if timeline_path and timeline_path.exists():
        elements.append(PageBreak())
        elements.extend(_build_timeline_section(timeline_path, styles))

    doc.build(elements)
    logger.info("[OK] PDF report saved: %s", output_path)


# ======================================================================
# Styles
# ======================================================================

def _build_styles() -> dict[str, ParagraphStyle]:
    """Create custom paragraph styles."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "CustomTitle",
            parent=base["Title"],
            fontSize=26,
            textColor=PRIMARY,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        ),
        "heading": ParagraphStyle(
            "CustomHeading",
            parent=base["Heading1"],
            fontSize=16,
            textColor=PRIMARY,
            spaceBefore=20,
            spaceAfter=12,
            fontName="Helvetica-Bold",
        ),
        "subheading": ParagraphStyle(
            "CustomSubheading",
            parent=base["Heading2"],
            fontSize=13,
            textColor=SECONDARY,
            spaceBefore=14,
            spaceAfter=8,
            fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "CustomBody",
            parent=base["Normal"],
            fontSize=10,
            textColor=DARK_TEXT,
            spaceAfter=6,
            leading=14,
        ),
        "stat_label": ParagraphStyle(
            "StatLabel",
            parent=base["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#666666"),
        ),
        "stat_value": ParagraphStyle(
            "StatValue",
            parent=base["Normal"],
            fontSize=18,
            textColor=PRIMARY,
            fontName="Helvetica-Bold",
        ),
    }


# ======================================================================
# Section 1: Executive Summary
# ======================================================================

def _build_executive_summary(
    tickets: list[Ticket], styles: dict
) -> list:
    """Build the executive summary section."""
    elements: list = []

    elements.append(Paragraph(REPORT_TITLE, styles["title"]))
    elements.append(
        Paragraph(
            f"Generated on {datetime.now().strftime('%d %B %Y at %H:%M')}",
            styles["body"],
        )
    )
    elements.append(Spacer(1, 20))
    elements.append(
        Paragraph("Section 1: Executive Summary", styles["heading"])
    )

    # Compute stats
    total_tickets = len(tickets)
    all_passengers: set[str] = set()
    total_journeys = 0
    earliest: Optional[datetime] = None
    latest: Optional[datetime] = None

    for t in tickets:
        for p in t.passengers:
            all_passengers.add(p.name)
            total_journeys += 1
        if t.departure_datetime:
            if earliest is None or t.departure_datetime < earliest:
                earliest = t.departure_datetime
            if latest is None or t.departure_datetime > latest:
                latest = t.departure_datetime

    if not all_passengers:
        total_journeys = total_tickets

    stats = [
        ("Total Tickets", str(total_tickets)),
        ("Total Journeys", str(total_journeys)),
        ("Unique Passengers", str(len(all_passengers) or "N/A")),
        (
            "Earliest Trip",
            earliest.strftime("%d %b %Y") if earliest else "N/A",
        ),
        (
            "Latest Trip",
            latest.strftime("%d %b %Y") if latest else "N/A",
        ),
    ]

    # Build stats table
    stat_data = []
    for label, value in stats:
        stat_data.append([
            Paragraph(value, styles["stat_value"]),
            Paragraph(label, styles["stat_label"]),
        ])

    stat_table = Table(stat_data, colWidths=[4 * cm, 6 * cm])
    stat_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#E0E0E0")),
        ])
    )
    elements.append(stat_table)
    return elements


# ======================================================================
# Section 2: All Tickets Table
# ======================================================================

def _build_tickets_table(
    tickets: list[Ticket], styles: dict
) -> list:
    """Build paginated ticket data table."""
    elements: list = []
    elements.append(
        Paragraph("Section 2: All Ticket Details", styles["heading"])
    )

    if not tickets:
        elements.append(Paragraph("No tickets parsed.", styles["body"]))
        return elements

    headers = [
        "PNR", "Train", "Passengers", "From", "To",
        "Departure", "Class", "Fare",
    ]

    data = [headers]
    for t in tickets:
        train = f"{t.train_number or ''}\n{t.train_name or ''}"
        data.append([
            t.pnr or "N/A",
            train,
            t.passenger_names or "N/A",
            t.from_station or "N/A",
            t.to_station or "N/A",
            t.departure_display or "N/A",
            t.travel_class or "N/A",
            f"₹{t.total_fare:.2f}" if t.total_fare else "N/A",
        ])

    col_widths = [2.5*cm, 3.5*cm, 4*cm, 3.5*cm, 3.5*cm, 3*cm, 1.8*cm, 2*cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        # Data
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]

    # Alternating row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(
                ("BACKGROUND", (0, i), (-1, i), LIGHT_BG)
            )

    table.setStyle(TableStyle(style_cmds))
    elements.append(table)
    return elements


# ======================================================================
# Section 3: Passenger Journey Summaries
# ======================================================================

def _build_passenger_summaries(
    passenger_journeys: dict[str, list[JourneyEntry]],
    styles: dict,
) -> list:
    """Build per-passenger journey summary sections."""
    elements: list = []
    elements.append(
        Paragraph(
            "Section 3: Passenger Journey Summaries", styles["heading"]
        )
    )

    if not passenger_journeys:
        elements.append(Paragraph("No passenger data.", styles["body"]))
        return elements

    for name, journeys in passenger_journeys.items():
        elements.append(Paragraph(f"▸ {name}", styles["subheading"]))

        headers = ["Train", "PNR", "Departure", "From", "To", "Seat"]
        data = [headers]

        for j in journeys:
            train = f"{j.train_number or ''} {j.train_name or ''}".strip()
            data.append([
                train or "N/A",
                j.pnr or "N/A",
                j.departure_display or "N/A",
                j.from_station or "N/A",
                j.to_station or "N/A",
                j.seat_info or "N/A",
            ])

        col_widths = [4*cm, 2.8*cm, 3*cm, 4*cm, 4*cm, 3*cm]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        elements.append(table)
        elements.append(Spacer(1, 10))

    return elements


# ======================================================================
# Section 4: Timeline
# ======================================================================

def _build_timeline_section(
    timeline_path: Path, styles: dict
) -> list:
    """Embed the timeline visualization image."""
    elements: list = []
    elements.append(
        Paragraph("Section 4: Journey Timeline", styles["heading"])
    )

    try:
        # Scale image to fit landscape A4
        page_width = landscape(A4)[0] - 3 * cm
        img = Image(str(timeline_path), width=page_width, height=12 * cm)
        img.hAlign = "CENTER"
        elements.append(img)
    except Exception as exc:
        logger.warning("Could not embed timeline image: %s", exc)
        elements.append(
            Paragraph(
                f"Timeline image could not be embedded: {exc}",
                styles["body"],
            )
        )

    return elements
