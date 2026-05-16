"""Passenger data model.

Represents a single passenger entry on an IRCTC train ticket.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Passenger:
    """A single passenger listed on a train ticket.

    Attributes:
        name: Full passenger name as printed on the ticket.
        age: Age of the passenger (string because some PDFs include units like 'Yrs').
        gender: Gender code (e.g., 'Male', 'Female', 'M', 'F').
        booking_status: Status at time of booking (e.g., 'CNF/B1/54/UPPER').
        current_status: Current reservation status.
        coach: Coach designation (e.g., 'B1', 'S2').
        seat_number: Seat or berth number (e.g., '54').
        berth: Berth type (e.g., 'UPPER', 'LOWER', 'MIDDLE', 'SIDE UPPER').
    """

    name: str
    age: Optional[str] = None
    gender: Optional[str] = None
    booking_status: Optional[str] = None
    current_status: Optional[str] = None
    coach: Optional[str] = None
    seat_number: Optional[str] = None
    berth: Optional[str] = None

    def __str__(self) -> str:
        parts = [self.name]
        if self.age:
            parts.append(f"Age: {self.age}")
        if self.current_status:
            parts.append(f"Status: {self.current_status}")
        return " | ".join(parts)

    @property
    def seat_display(self) -> str:
        """Human-readable seat designation (e.g., 'B1-54')."""
        parts: list[str] = []
        if self.coach:
            parts.append(self.coach)
        if self.seat_number:
            parts.append(self.seat_number)
        return "-".join(parts) if parts else ""
