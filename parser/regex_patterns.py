"""Compiled regex patterns for IRCTC ticket field extraction.

All patterns are pre-compiled for performance and grouped by category.
Each pattern is designed to be tolerant of spacing variations, optional
punctuation, and common formatting differences found in IRCTC PDFs.

Pattern design is informed by real IRCTC ERS (Electronic Reservation Slip)
PDF layouts.
"""

import re

# =====================================================================
# TRAIN INFORMATION
# =====================================================================

# PNR is a 10-digit number, usually on a line like:
# "PNR Train No./Name Class"
# "8248433572 09081/MMCT MAN SF SPL THIRD AC (3A)"
PNR_PATTERN = re.compile(
    r"(?:PNR\s*(?:No\.?|Number)?\s*:?\s*(\d{10}))"
    r"|(?:^(\d{10})\s+\d{4,5})",
    re.IGNORECASE | re.MULTILINE,
)

# Train number: 4-5 digit number.  Handles both "09081/NAME" and "12655 / NAME"
TRAIN_NUMBER_PATTERN = re.compile(
    r"(?:Train\s*(?:No\.?|Number)?\s*[:/]?\s*(\d{4,5}))"
    r"|(?:\d{10}\s+(\d{4,5})\s*/)",
    re.IGNORECASE,
)

# Train name: after train number with slash (spaces around slash tolerated),
# or on a dedicated "Train Name" line.
# Handles end-of-line case where class info is on the next line.
TRAIN_NAME_PATTERN = re.compile(
    r"(?:Train\s*Name\s*[:/]?\s*(.+?)(?:\n|$))"
    r"|(?:\d{10}\s+\d{4,5}\s*/\s*(.+?)(?:\s+(?:FIRST|SECOND|THIRD|SLEEPER|AC\s+CHAIR)\s))"
    r"|(?:\d{10}\s+\d{4,5}\s*/\s*(.+?)$)",
    re.IGNORECASE | re.MULTILINE,
)

# =====================================================================
# STATION PATTERNS
# =====================================================================

# IRCTC ERS format: "Booked from To"
# Next line: "STATION_A (CODE_A) STATION_B (CODE_B) STATION_C (CODE_C)"
FROM_STATION_PATTERN = re.compile(
    r"(?:From|Boarding\s*(?:Station|Point|At))\s*[:/]?\s*(.+?)(?:\n|$)",
    re.IGNORECASE,
)

TO_STATION_PATTERN = re.compile(
    r"(?:To|Destination\s*(?:Station)?|Reserved\s*(?:Up\s*)?To)\s*[:/]?\s*(.+?)(?:\n|$)",
    re.IGNORECASE,
)

# Pattern for the IRCTC ERS "Booked from  To" station line
# Matches: "STATION_NAME (CODE) STATION_NAME (CODE) STATION_NAME (CODE)"
STATION_LINE_PATTERN = re.compile(
    r"([A-Z][A-Z\s]+\([A-Z]{2,6}\))\s+([A-Z][A-Z\s]+\([A-Z]{2,6}\))\s+([A-Z][A-Z\s]+\([A-Z]{2,6}\))",
    re.IGNORECASE,
)

# Simpler two-station pattern
TWO_STATION_PATTERN = re.compile(
    r"([A-Z][A-Z\s]+\([A-Z]{2,6}\))\s+([A-Z][A-Z\s]+\([A-Z]{2,6}\))",
    re.IGNORECASE,
)

# =====================================================================
# DATE / TIME
# =====================================================================

_DATE_PART = r"\d{1,2}[-/]\w{3,9}[-/]\d{2,4}"
_TIME_PART = r"\d{1,2}:\d{2}(?::\d{2})?"
_DATETIME_PART = rf"{_DATE_PART}\s+{_TIME_PART}"

# IRCTC ERS format:
# "Start Date* 21-May-2026 Departure* 23:20 21-May-2026 Arrival* 07:25 22-May-2026"
IRCTC_SCHEDULE_PATTERN = re.compile(
    r"(?:Start\s*Date\*?)\s*({date})\s+"
    r"(?:Departure\*?)\s*({time})\s+({date})\s+"
    r"(?:Arrival\*?)\s*({time})\s+({date})".format(
        date=_DATE_PART, time=_TIME_PART
    ),
    re.IGNORECASE,
)

DEPARTURE_DATETIME_PATTERN = re.compile(
    rf"(?:Departure|Depart(?:ing)?|Dep\.?)\s*[:/]?\s*({_DATETIME_PART}|{_DATE_PART})",
    re.IGNORECASE,
)

ARRIVAL_DATETIME_PATTERN = re.compile(
    rf"(?:Arrival|Arriv(?:ing)?|Arr\.?)\s*[:/]?\s*({_DATETIME_PART}|{_DATE_PART})",
    re.IGNORECASE,
)

BOOKING_DATETIME_PATTERN = re.compile(
    rf"(?:Date\s*(?:of\s*)?Booking|Booking\s*Date|Booked\s*On|Transaction\s*Date)\s*[:/]?\s*({_DATETIME_PART}|{_DATE_PART})",
    re.IGNORECASE,
)

# Fallback: "Booking Date" line in IRCTC ERS
# "GENERAL (GN) 488 KM 14-May-2026 08:53:54 HRS"
BOOKING_DATE_FALLBACK = re.compile(
    rf"({_DATE_PART})\s+({_TIME_PART})\s*HRS",
    re.IGNORECASE,
)

DATE_OF_JOURNEY_PATTERN = re.compile(
    rf"Date\s*(?:of\s*)?Journey\s*[:/]?\s*({_DATE_PART})",
    re.IGNORECASE,
)

# Schedule table: "departure_datetime * arrival_datetime"
SCHEDULE_LINE_PATTERN = re.compile(
    rf"({_DATE_PART}\s+{_TIME_PART})\s+\*?\s*({_DATE_PART}\s+{_TIME_PART})",
    re.IGNORECASE,
)

# =====================================================================
# TRAVEL DETAILS
# =====================================================================

# Class patterns — handles all observed formats:
#   "THIRD AC (3A)"
#   "THIRD AC ECONOMY (3E)"
#   "SLEEPER (SL)"
#   "SECOND AC (2A)"
#   "AC CHAIR CAR (CC)"
#   "FIRST AC (1A)"
CLASS_PATTERN = re.compile(
    r"(?:FIRST|SECOND|THIRD|SLEEPER)\s*(?:AC)?\s*(?:ECONOMY|CHAIR\s*CAR)?\s*\(([A-Z0-9]{1,3})\)"
    r"|(?:AC\s*CHAIR\s*CAR\s*\(([A-Z0-9]{1,3})\))"
    r"|(?:^\(([A-Z0-9]{1,3})\)$)"
    r"|(?:Class\s*[:/]\s*([A-Z0-9]{1,3}(?:\s*[-]\s*\w+)?))",
    re.IGNORECASE | re.MULTILINE,
)

QUOTA_PATTERN = re.compile(
    r"(?:GENERAL|TATKAL|PREMIUM\s*TATKAL|LADIES|LOWER\s*BERTH|DEFENCE|DUTY\s*PASS|FOREIGN\s*TOURIST)\s*\((\w+)\)"
    r"|(?:Quota\s*[:/]\s*(\w[\w\s]*?)(?:\n|$))",
    re.IGNORECASE,
)

DISTANCE_PATTERN = re.compile(
    r"([\d,]+)\s*(?:KM|KMS|Kms|km)",
    re.IGNORECASE,
)

# =====================================================================
# FINANCIAL
# =====================================================================

TICKET_FARE_PATTERN = re.compile(
    r"(?:Ticket\s*Fare|Base\s*Fare)\s*[:/]?\s*[₹Rs.INR\s]*\s*([\d,]+\.?\d*)",
    re.IGNORECASE,
)

TOTAL_FARE_PATTERN = re.compile(
    r"(?:Total\s*(?:Fare|Amount|Collected)(?:\s*\([^)]*\))?|Grand\s*Total|Amount\s*Payable)\s*[:/]?\s*[₹Rs.INR\s]*\s*([\d,]+\.?\d*)",
    re.IGNORECASE,
)

CONVENIENCE_FEE_PATTERN = re.compile(
    r"(?:Convenience\s*(?:Fee|Charge)|Service\s*(?:Fee|Charge)|IRCTC\s*(?:Service|Convenience)\s*(?:Fee|Charge))"
    r"(?:\s*\([^)]*\))?\s*[:/]?\s*[₹Rs.INR\s]*\s*([\d,]+\.?\d*)",
    re.IGNORECASE,
)

INSURANCE_FEE_PATTERN = re.compile(
    r"(?:Travel\s*)?Insurance\s*(?:Premium|Fee|Charge)?"
    r"(?:\s*\([^)]*\))?\s*[:/]?\s*[₹Rs.INR\s]*\s*([\d,]+\.?\d*)",
    re.IGNORECASE,
)

TRANSACTION_ID_PATTERN = re.compile(
    r"(?:Transaction|Transac.?on)\s*(?:ID|Id|No\.?)\s*[:/]?\s*(\d+)",
    re.IGNORECASE,
)

# =====================================================================
# GST
# =====================================================================

INVOICE_NUMBER_PATTERN = re.compile(
    r"(?:Invoice\s*(?:No\.?|Number))\s*[:/]?\s*([\w\-/]+)",
    re.IGNORECASE,
)

GSTIN_PATTERN = re.compile(
    r"(?:GSTIN|GST\s*(?:No\.?|Number|IN))\s*[:/]?\s*(\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z\d][A-Z\d])",
    re.IGNORECASE,
)

SAC_CODE_PATTERN = re.compile(
    r"(?:SAC|SAC\s*Code|Service\s*(?:Accounting\s*)?Code)\s*[:/]?\s*(\d{4,8})",
    re.IGNORECASE,
)

# =====================================================================
# PASSENGER PARSING
# =====================================================================

# IRCTC ERS passenger line format — handles all observed variations:
#
#   "1. SAYALI KHADSE 26 F CNF/B1/54/UPPER CNF/B1/54/UPPER"
#   "1. SATISH NINOORAO 55 M CNF/B2/64/SIDE UPPER CNF/B2/64/SIDE UPPER"
#   "2. PRANAV KHADSE 20 M CNF/M2/62/UPPER CAN"
#   "1. KHADSE JYOTI 50 F CNF/B1/49/LOWER CNF /B1/49/LOWER"
#
# Key variations:
#   - Berth can be two words: "SIDE UPPER", "SIDE LOWER"
#   - Current status may be just "CAN" (cancelled)
#   - Current status may have a space: "CNF /B1/49/LOWER"
PASSENGER_LINE_PATTERN = re.compile(
    r"(\d+)\.?\s+"                           # Serial number
    r"([A-Z][A-Z\s.]+?)\s+"                  # Name
    r"(\d{1,3})\s+"                          # Age
    r"(Male|Female|M|F|Transgender)\s+"      # Gender
    r"((?:CNF|RAC|WL|RLWL|GNWL|PQWL|CAN|RSWL)\s*/\S+(?:\s+(?:UPPER|LOWER|MIDDLE|SIDE\s+(?:UPPER|LOWER)))?|CAN)\s+"  # Booking status
    r"((?:CNF|RAC|WL|CAN|RLWL|GNWL|PQWL|RSWL)\s*/\S+(?:\s+(?:UPPER|LOWER|MIDDLE|SIDE\s+(?:UPPER|LOWER)))?|CAN)",    # Current status
    re.IGNORECASE,
)

# Alternative: Name on its own line
PASSENGER_NAME_PATTERN = re.compile(
    r"(?:Passenger\s*Name|Name\s*of\s*Passenger)\s*[:/]?\s*([A-Z][A-Z\s.]+)",
    re.IGNORECASE,
)

BOOKING_STATUS_PATTERN = re.compile(
    r"Booking\s*Status\s*[:/]?\s*((?:CNF|RAC|WL|CAN|RLWL|GNWL|PQWL|RSWL)\S*)",
    re.IGNORECASE,
)

CURRENT_STATUS_PATTERN = re.compile(
    r"Current\s*Status\s*[:/]?\s*((?:CNF|RAC|WL|CAN|RLWL|GNWL|PQWL|RSWL)\S*)",
    re.IGNORECASE,
)

# Parse coach/berth from status strings like:
#   "CNF/B1/54/UPPER"
#   "CNF /B1/49/LOWER"  (space after status prefix)
#   "CNF/B2/64/SIDE UPPER"
STATUS_DETAIL_PATTERN = re.compile(
    r"(?:CNF|RAC|WL|RLWL|GNWL|PQWL|RSWL|CAN)"
    r"\s*/([A-Z]\d+)"        # Coach (e.g., B1, S2, M2) — allow space before /
    r"/(\d+)"                # Seat number
    r"(?:/([A-Z]+(?:\s+[A-Z]+)?))?",  # Berth type (optional, may be multi-word)
    re.IGNORECASE,
)

# =====================================================================
# PNR + TRAIN combined line pattern
# =====================================================================
# Handles both:
#   "8248433572 09081/MMCT MAN SF SPL THIRD AC (3A)"
#   "8248239903 12655 / NAVJEEVAN EXP THIRD AC (3A)"
#   "6203690241 12860 / GITANJALI EXP THIRD AC ECONOMY (3E)"
PNR_TRAIN_LINE_PATTERN = re.compile(
    r"(\d{10})\s+(\d{4,5})\s*/\s*(.+?)(?:\s+(?:FIRST|SECOND|THIRD|SLEEPER|AC\s+CHAIR))",
    re.IGNORECASE,
)

# Fallback: PNR + train number + name without class suffix (class on separate line)
# Matches: "2355493090 20626/BGKT MAS SF EXP"
PNR_TRAIN_LINE_FALLBACK = re.compile(
    r"^(\d{10})\s+(\d{4,5})\s*/\s*(.+?)$",
    re.IGNORECASE | re.MULTILINE,
)

# =====================================================================
# IRCTC ERS detection
# =====================================================================
ERS_MARKER_PATTERN = re.compile(
    r"Electronic\s*Reserva.*?Slip",
    re.IGNORECASE,
)
