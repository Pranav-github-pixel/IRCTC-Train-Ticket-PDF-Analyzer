"""Chronological ticket sorting.

Wraps the LinkedList's merge sort to provide a clean processing-layer API.
"""

import logging

from models.linked_list import LinkedList

logger = logging.getLogger("irctc_analyzer")


def sort_tickets(tickets: LinkedList) -> LinkedList:
    """Sort tickets chronologically by departure datetime (ascending).

    Tickets with missing departure datetimes are placed at the end.

    Args:
        tickets: LinkedList of parsed Ticket objects.

    Returns:
        The same LinkedList, now sorted in-place.
    """
    if len(tickets) <= 1:
        logger.debug("Skipping sort — %d ticket(s).", len(tickets))
        return tickets

    logger.info("Sorting %d tickets by departure datetime...", len(tickets))
    tickets.sort_by_departure_datetime()
    logger.info("Sorting complete.")

    return tickets
