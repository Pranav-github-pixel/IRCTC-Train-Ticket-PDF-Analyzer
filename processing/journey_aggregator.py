"""Journey aggregation by passenger.

Groups ticket data by individual passenger names to produce per-passenger
journey summaries for the Excel report and PDF report.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from models.ticket import Ticket

logger = logging.getLogger("irctc_analyzer")


@dataclass
class JourneyEntry:
    """A single journey from the perspective of one passenger.

    Attributes:
        passenger_name: Name of the passenger.
        train_number: Train number.
        train_name: Train name.
        pnr: PNR number.
        departure_datetime: Scheduled departure.
        from_station: Boarding station.
        to_station: Destination station.
        seat_info: Combined seat and status (e.g., "B1-54 (CNF)").
    """

    passenger_name: str
    train_number: Optional[str] = None
    train_name: Optional[str] = None
    pnr: Optional[str] = None
    departure_datetime: Optional[datetime] = None
    from_station: Optional[str] = None
    to_station: Optional[str] = None
    seat_info: Optional[str] = None

    @property
    def departure_display(self) -> str:
        """Formatted departure for display."""
        if self.departure_datetime:
            return self.departure_datetime.strftime("%d-%b-%Y %H:%M")
        return ""


def aggregate_by_passenger(
    tickets: list[Ticket],
) -> dict[str, list[JourneyEntry]]:
    """Group all journeys by passenger name.

    Each ticket may have multiple passengers; each passenger gets their
    own list of journeys across all tickets.  Journeys within each
    passenger are sorted chronologically.

    Args:
        tickets: Chronologically sorted list of Ticket objects.

    Returns:
        Mapping of passenger_name → list of JourneyEntry, sorted by
        departure datetime within each passenger.
    """
    journeys: dict[str, list[JourneyEntry]] = defaultdict(list)

    for ticket in tickets:
        if not ticket.passengers:
            # If no passenger data, create an "Unknown" entry
            entry = JourneyEntry(
                passenger_name="Unknown",
                train_number=ticket.train_number,
                train_name=ticket.train_name,
                pnr=ticket.pnr,
                departure_datetime=ticket.departure_datetime,
                from_station=ticket.from_station,
                to_station=ticket.to_station,
                seat_info="N/A",
            )
            journeys["Unknown"].append(entry)
            continue

        for passenger in ticket.passengers:
            # Build seat info string
            seat_parts: list[str] = []
            if passenger.seat_display:
                seat_parts.append(passenger.seat_display)
            if passenger.current_status:
                # Extract just the status prefix (CNF, RAC, etc.)
                status_prefix = passenger.current_status.split("/")[0]
                seat_parts.append(f"({status_prefix})")
            seat_info = " ".join(seat_parts) if seat_parts else None

            entry = JourneyEntry(
                passenger_name=passenger.name,
                train_number=ticket.train_number,
                train_name=ticket.train_name,
                pnr=ticket.pnr,
                departure_datetime=ticket.departure_datetime,
                from_station=ticket.from_station,
                to_station=ticket.to_station,
                seat_info=seat_info,
            )
            journeys[passenger.name].append(entry)

    # Sort each passenger's journeys chronologically
    for name in journeys:
        journeys[name].sort(
            key=lambda j: j.departure_datetime or datetime.max
        )

    total_entries = sum(len(v) for v in journeys.values())
    logger.info(
        "Aggregated %d journey entries across %d unique passenger(s).",
        total_entries,
        len(journeys),
    )

    return dict(journeys)
