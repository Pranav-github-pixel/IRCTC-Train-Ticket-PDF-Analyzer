"""Ticket data model.

Represents all structured data extracted from a single IRCTC train ticket PDF.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from models.passenger import Passenger


@dataclass
class Ticket:
    """Complete ticket data extracted from one IRCTC PDF.

    Every field except *file_name* defaults to ``None`` or an empty list
    so that partially-parsed tickets are still usable downstream.

    Attributes:
        file_name: Source PDF file name (always set).
        pnr: 10-digit PNR number.
        train_number: Train number (4–5 digits).
        train_name: Official train name.
        from_station: Boarding station name (may include code).
        to_station: Destination station name (may include code).
        departure_datetime: Scheduled departure.
        arrival_datetime: Scheduled arrival.
        booking_datetime: When the ticket was booked.
        travel_class: Class of travel (e.g., '3A', 'SL', '2S').
        quota: Booking quota (e.g., 'GENERAL', 'TATKAL').
        distance: Journey distance in km.
        transaction_id: Payment transaction identifier.
        ticket_fare: Base ticket fare.
        convenience_fee: IRCTC convenience/service fee.
        insurance_fee: Optional travel insurance premium.
        total_fare: Grand total paid.
        invoice_number: GST invoice number.
        gstin: GSTIN of IRCTC.
        sac_code: SAC (Service Accounting Code).
        passengers: List of passengers on this ticket.
    """

    file_name: str
    pnr: Optional[str] = None
    train_number: Optional[str] = None
    train_name: Optional[str] = None
    from_station: Optional[str] = None
    to_station: Optional[str] = None
    departure_datetime: Optional[datetime] = None
    arrival_datetime: Optional[datetime] = None
    booking_datetime: Optional[datetime] = None
    travel_class: Optional[str] = None
    quota: Optional[str] = None
    distance: Optional[str] = None
    transaction_id: Optional[str] = None
    ticket_fare: Optional[float] = None
    convenience_fee: Optional[float] = None
    insurance_fee: Optional[float] = None
    total_fare: Optional[float] = None
    invoice_number: Optional[str] = None
    gstin: Optional[str] = None
    sac_code: Optional[str] = None
    passengers: list[Passenger] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def passenger_names(self) -> str:
        """Comma-separated passenger names."""
        return ", ".join(p.name for p in self.passengers if p.name)

    @property
    def seat_numbers(self) -> str:
        """Comma-separated seat designations (e.g., 'B1-54, B1-55')."""
        return ", ".join(
            p.seat_display for p in self.passengers if p.seat_display
        )

    @property
    def coaches(self) -> str:
        """Unique coach designations, comma-separated."""
        unique = dict.fromkeys(
            p.coach for p in self.passengers if p.coach
        )
        return ", ".join(unique)

    @property
    def booking_statuses(self) -> str:
        """Comma-separated booking statuses."""
        return ", ".join(
            p.booking_status for p in self.passengers if p.booking_status
        )

    @property
    def current_statuses(self) -> str:
        """Comma-separated current statuses."""
        return ", ".join(
            p.current_status for p in self.passengers if p.current_status
        )

    @property
    def departure_display(self) -> str:
        """Formatted departure for display."""
        if self.departure_datetime:
            return self.departure_datetime.strftime("%d-%b-%Y %H:%M")
        return ""

    @property
    def arrival_display(self) -> str:
        """Formatted arrival for display."""
        if self.arrival_datetime:
            return self.arrival_datetime.strftime("%d-%b-%Y %H:%M")
        return ""

    @property
    def booking_display(self) -> str:
        """Formatted booking date for display."""
        if self.booking_datetime:
            return self.booking_datetime.strftime("%d-%b-%Y %H:%M")
        return ""

    def __str__(self) -> str:
        return (
            f"Ticket(PNR={self.pnr}, "
            f"Train={self.train_number} {self.train_name}, "
            f"{self.from_station} -> {self.to_station}, "
            f"Departure={self.departure_display})"
        )
