"""High-level PDF parser that orchestrates text extraction and field parsing.

This module is the main entry point for converting IRCTC ticket PDFs into
structured ``Ticket`` objects.  It delegates to ``text_extractor`` for raw
text and ``regex_patterns`` for field extraction.
"""

import logging
import traceback
from pathlib import Path
from typing import Optional

from models.linked_list import LinkedList
from models.passenger import Passenger
from models.ticket import Ticket
from parser.regex_patterns import (
    ARRIVAL_DATETIME_PATTERN,
    BOOKING_DATE_FALLBACK,
    BOOKING_DATETIME_PATTERN,
    BOOKING_STATUS_PATTERN,
    CLASS_PATTERN,
    CONVENIENCE_FEE_PATTERN,
    CURRENT_STATUS_PATTERN,
    DATE_OF_JOURNEY_PATTERN,
    DEPARTURE_DATETIME_PATTERN,
    DISTANCE_PATTERN,
    ERS_MARKER_PATTERN,
    FROM_STATION_PATTERN,
    GSTIN_PATTERN,
    INSURANCE_FEE_PATTERN,
    INVOICE_NUMBER_PATTERN,
    IRCTC_SCHEDULE_PATTERN,
    PASSENGER_LINE_PATTERN,
    PASSENGER_NAME_PATTERN,
    PNR_PATTERN,
    PNR_TRAIN_LINE_FALLBACK,
    PNR_TRAIN_LINE_PATTERN,
    QUOTA_PATTERN,
    SAC_CODE_PATTERN,
    SCHEDULE_LINE_PATTERN,
    STATION_LINE_PATTERN,
    STATUS_DETAIL_PATTERN,
    TICKET_FARE_PATTERN,
    TO_STATION_PATTERN,
    TOTAL_FARE_PATTERN,
    TRAIN_NAME_PATTERN,
    TRAIN_NUMBER_PATTERN,
    TRANSACTION_ID_PATTERN,
    TWO_STATION_PATTERN,
)
from parser.text_extractor import extract_text_from_pdf
from utils.helpers import clean_text, safe_parse_datetime, safe_parse_float

logger = logging.getLogger("irctc_analyzer")


# ======================================================================
# Public API
# ======================================================================


def parse_all_tickets(input_dir: Path) -> LinkedList:
    """Parse every PDF in *input_dir* and return a populated linked list.

    Files that fail to parse are logged and skipped -- execution never stops.

    Args:
        input_dir: Directory containing IRCTC ticket PDFs.

    Returns:
        LinkedList of successfully parsed Ticket objects.
    """
    tickets = LinkedList()
    pdf_files = sorted(input_dir.glob("*.pdf"))

    if not pdf_files:
        logger.warning("No PDF files found in %s", input_dir)
        return tickets

    logger.info("Found %d PDF file(s) in %s", len(pdf_files), input_dir)

    for pdf_path in pdf_files:
        try:
            ticket = parse_ticket(pdf_path)
            if ticket is None:
                logger.warning(
                    "[SKIP] %s is not an IRCTC ticket PDF.",
                    pdf_path.name,
                )
                continue
            tickets.append(ticket)
            logger.info(
                "[OK] Parsed: %s -> PNR %s, %s -> %s",
                pdf_path.name,
                ticket.pnr or "N/A",
                ticket.from_station or "?",
                ticket.to_station or "?",
            )
        except Exception as exc:
            logger.error(
                "[FAIL] Failed to parse %s\n\nFILE:\n%s\n\nERROR:\n%s\n\nSTACKTRACE:\n%s",
                pdf_path.name,
                pdf_path.name,
                str(exc),
                traceback.format_exc(),
            )

    logger.info(
        "Parsing complete: %d/%d tickets parsed successfully.",
        len(tickets),
        len(pdf_files),
    )
    return tickets


def parse_ticket(pdf_path: Path) -> Optional[Ticket]:
    """Parse a single IRCTC ticket PDF into a Ticket object.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Populated Ticket dataclass, or None if the PDF is not an IRCTC ticket.

    Raises:
        ValueError: If text extraction yields nothing.
    """
    text = extract_text_from_pdf(pdf_path)

    # Check if this is actually an IRCTC ERS ticket
    if not ERS_MARKER_PATTERN.search(text):
        logger.warning(
            "%s does not appear to be an IRCTC ticket (missing ERS marker).",
            pdf_path.name,
        )
        return None

    return _parse_text_to_ticket(text, pdf_path.name)


# ======================================================================
# Internal field extraction
# ======================================================================


def _extract_field(
    pattern,  # type: ignore[type-arg]
    text: str,
    group: int = 1,
) -> Optional[str]:
    """Search *text* for *pattern* and return the first non-None captured group."""
    match = pattern.search(text)
    if match:
        # Return the first non-None group
        for i in range(1, len(match.groups()) + 1):
            if match.group(i) is not None:
                return clean_text(match.group(i))
    return None


def _parse_text_to_ticket(text: str, file_name: str) -> Ticket:
    """Convert extracted PDF text into a Ticket object.

    Args:
        text: Full extracted text from the PDF.
        file_name: Source file name for reference.

    Returns:
        Populated Ticket.
    """
    # ---- PNR + Train info (combined line) ----
    pnr, train_number, train_name = _parse_pnr_train_combined(text)

    # Fallback for individual fields
    if not pnr:
        pnr = _extract_field(PNR_PATTERN, text)
    if not train_number:
        train_number = _extract_field(TRAIN_NUMBER_PATTERN, text)
    if not train_name:
        train_name = _extract_field(TRAIN_NAME_PATTERN, text)

    # ---- Stations ----
    from_station, to_station = _parse_stations(text)

    # ---- Dates/times ----
    departure_dt, arrival_dt = _parse_schedule(text)
    booking_dt = _parse_booking_date(text)

    # ---- Travel details ----
    travel_class = _extract_field(CLASS_PATTERN, text)
    quota = _extract_field(QUOTA_PATTERN, text)
    distance = _extract_field(DISTANCE_PATTERN, text)

    # ---- Financial ----
    transaction_id = _extract_field(TRANSACTION_ID_PATTERN, text)
    ticket_fare = safe_parse_float(_extract_field(TICKET_FARE_PATTERN, text))
    convenience_fee = safe_parse_float(
        _extract_field(CONVENIENCE_FEE_PATTERN, text)
    )
    insurance_fee = safe_parse_float(
        _extract_field(INSURANCE_FEE_PATTERN, text)
    )
    total_fare = safe_parse_float(_extract_field(TOTAL_FARE_PATTERN, text))

    # ---- GST ----
    invoice_number = _extract_field(INVOICE_NUMBER_PATTERN, text)
    gstin = _extract_field(GSTIN_PATTERN, text)
    sac_code = _extract_field(SAC_CODE_PATTERN, text)

    # ---- Passengers ----
    passengers = _parse_passengers(text)

    return Ticket(
        file_name=file_name,
        pnr=pnr,
        train_number=train_number,
        train_name=train_name,
        from_station=from_station,
        to_station=to_station,
        departure_datetime=departure_dt,
        arrival_datetime=arrival_dt,
        booking_datetime=booking_dt,
        travel_class=travel_class,
        quota=quota,
        distance=distance,
        transaction_id=transaction_id,
        ticket_fare=ticket_fare,
        convenience_fee=convenience_fee,
        insurance_fee=insurance_fee,
        total_fare=total_fare,
        invoice_number=invoice_number,
        gstin=gstin,
        sac_code=sac_code,
        passengers=passengers,
    )


# ======================================================================
# Combined PNR + Train parsing
# ======================================================================


def _parse_pnr_train_combined(
    text: str,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Parse the combined PNR/Train line found in IRCTC ERS PDFs.

    Example: ``"8248433572 09081/MMCT MAN SF SPL THIRD AC (3A)"``

    Returns:
        Tuple of (pnr, train_number, train_name).
    """
    match = PNR_TRAIN_LINE_PATTERN.search(text)
    if match:
        return (
            match.group(1).strip(),
            match.group(2).strip(),
            clean_text(match.group(3)),
        )

    # Fallback: class on a separate line
    match = PNR_TRAIN_LINE_FALLBACK.search(text)
    if match:
        return (
            match.group(1).strip(),
            match.group(2).strip(),
            clean_text(match.group(3)),
        )

    return None, None, None


# ======================================================================
# Station parsing
# ======================================================================


def _parse_stations(
    text: str,
) -> tuple[Optional[str], Optional[str]]:
    """Extract From and To stations with multiple strategies.

    Strategy 1: IRCTC ERS 3-station line
        "BOOKED_FROM (CODE)  FROM_STATION (CODE)  TO_STATION (CODE)"
        where first = booked from, second = boarding, third = destination

    Strategy 2: IRCTC ERS 2-station line (when booked from == boarding)

    Strategy 3: Explicit "From:" / "To:" fields

    Returns:
        Tuple of (from_station, to_station).
    """
    # Strategy 1: Three stations on one line
    match = STATION_LINE_PATTERN.search(text)
    if match:
        # In IRCTC format: booked_from, boarding_station, destination
        # The boarding station is the second one
        from_station = clean_text(match.group(2))
        to_station = clean_text(match.group(3))
        return from_station, to_station

    # Strategy 2: Two stations on one line
    match = TWO_STATION_PATTERN.search(text)
    if match:
        return clean_text(match.group(1)), clean_text(match.group(2))

    # Strategy 3: Explicit From/To fields
    from_station = _extract_field(FROM_STATION_PATTERN, text)
    to_station = _extract_field(TO_STATION_PATTERN, text)
    return from_station, to_station


# ======================================================================
# Date parsing helpers
# ======================================================================


def _parse_schedule(
    text: str,
) -> tuple[Optional[object], Optional[object]]:
    """Extract departure and arrival datetimes.

    Strategy 1: IRCTC ERS schedule line
        "Start Date* DD-Mon-YYYY Departure* HH:MM DD-Mon-YYYY Arrival* HH:MM DD-Mon-YYYY"

    Strategy 2: Explicit departure/arrival fields

    Strategy 3: Schedule table line

    Returns:
        Tuple of (departure_datetime, arrival_datetime).
    """
    # Strategy 1: IRCTC ERS combined schedule line
    match = IRCTC_SCHEDULE_PATTERN.search(text)
    if match:
        # Groups: start_date, dep_time, dep_date, arr_time, arr_date
        dep_str = f"{match.group(3)} {match.group(2)}"
        arr_str = f"{match.group(5)} {match.group(4)}"
        dep_dt = safe_parse_datetime(dep_str)
        arr_dt = safe_parse_datetime(arr_str)
        if dep_dt:
            return dep_dt, arr_dt

    # Strategy 2: Explicit fields
    dep_dt = _parse_departure_fallback(text)
    arr_dt = _parse_arrival_fallback(text)
    return dep_dt, arr_dt


def _parse_departure_fallback(text: str) -> Optional[object]:
    """Extract departure datetime with multiple fallback strategies."""
    raw = _extract_field(DEPARTURE_DATETIME_PATTERN, text)
    dt = safe_parse_datetime(raw)
    if dt:
        return dt

    match = SCHEDULE_LINE_PATTERN.search(text)
    if match:
        dt = safe_parse_datetime(match.group(1))
        if dt:
            return dt

    raw = _extract_field(DATE_OF_JOURNEY_PATTERN, text)
    return safe_parse_datetime(raw)


def _parse_arrival_fallback(text: str) -> Optional[object]:
    """Extract arrival datetime with fallback to schedule line."""
    raw = _extract_field(ARRIVAL_DATETIME_PATTERN, text)
    dt = safe_parse_datetime(raw)
    if dt:
        return dt

    match = SCHEDULE_LINE_PATTERN.search(text)
    if match:
        return safe_parse_datetime(match.group(2))

    return None


def _parse_booking_date(text: str) -> Optional[object]:
    """Extract booking date/time.

    Strategy 1: Explicit "Booking Date" field
    Strategy 2: IRCTC ERS fallback "DD-Mon-YYYY HH:MM:SS HRS"
    """
    raw = _extract_field(BOOKING_DATETIME_PATTERN, text)
    dt = safe_parse_datetime(raw)
    if dt:
        return dt

    # Fallback: "14-May-2026 08:53:54 HRS"
    match = BOOKING_DATE_FALLBACK.search(text)
    if match:
        combined = f"{match.group(1)} {match.group(2)}"
        return safe_parse_datetime(combined)

    return None


# ======================================================================
# Passenger parsing
# ======================================================================


def _parse_passengers(text: str) -> list[Passenger]:
    """Extract passenger records from the PDF text.

    Tries structured table format first (IRCTC ERS), then falls back to
    individual field extraction.

    Args:
        text: Full PDF text.

    Returns:
        List of Passenger objects (may be empty).
    """
    passengers: list[Passenger] = []

    # Strategy 1: Tabular passenger data (IRCTC ERS format)
    matches = PASSENGER_LINE_PATTERN.findall(text)
    if matches:
        for match in matches:
            _, name, age, gender, booking_status, current_status = match
            # Try current status first; fall back to booking status for
            # coach/seat details (e.g. when current status is just "CAN")
            coach, seat_number, berth = _parse_status_details(current_status)
            if coach is None:
                coach, seat_number, berth = _parse_status_details(booking_status)
            passengers.append(
                Passenger(
                    name=clean_text(name),
                    age=age.strip(),
                    gender=gender.strip(),
                    booking_status=clean_text(booking_status),
                    current_status=clean_text(current_status),
                    coach=coach,
                    seat_number=seat_number,
                    berth=berth,
                )
            )
        return passengers

    # Strategy 2: Individual field-based extraction
    name_matches = PASSENGER_NAME_PATTERN.findall(text)
    booking_matches = BOOKING_STATUS_PATTERN.findall(text)
    current_matches = CURRENT_STATUS_PATTERN.findall(text)

    if name_matches:
        for i, name in enumerate(name_matches):
            booking_status = (
                clean_text(booking_matches[i])
                if i < len(booking_matches)
                else None
            )
            current_status = (
                clean_text(current_matches[i])
                if i < len(current_matches)
                else None
            )
            status_for_details = current_status or booking_status or ""
            coach, seat_number, berth = _parse_status_details(status_for_details)

            passengers.append(
                Passenger(
                    name=clean_text(name),
                    booking_status=booking_status,
                    current_status=current_status,
                    coach=coach,
                    seat_number=seat_number,
                    berth=berth,
                )
            )

    return passengers


def _parse_status_details(
    status: str,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract coach, seat number, and berth from a status string.

    Example: ``"CNF/B1/54/UPPER"`` -> ``("B1", "54", "UPPER")``.

    Args:
        status: Raw status string.

    Returns:
        Tuple of (coach, seat_number, berth). Any may be None.
    """
    match = STATUS_DETAIL_PATTERN.search(status)
    if match:
        coach = match.group(1)
        seat = match.group(2)
        berth = match.group(3).strip() if match.group(3) else None
        return coach, seat, berth
    return None, None, None
