"""Singly-linked list with merge sort for chronological ticket ordering.

This module provides a generic linked list tailored for storing Ticket
objects and sorting them by departure datetime using an efficient O(n log n)
merge sort algorithm.
"""

from __future__ import annotations

from datetime import datetime
from typing import Generator, Optional

from models.ticket import Ticket


class Node:
    """A single node in the linked list.

    Attributes:
        data: The Ticket stored in this node.
        next: Reference to the next node, or None if tail.
    """

    __slots__ = ("data", "next")

    def __init__(self, data: Ticket) -> None:
        self.data: Ticket = data
        self.next: Optional[Node] = None

    def __repr__(self) -> str:
        return f"Node({self.data})"


class LinkedList:
    """Singly-linked list of Ticket objects with merge-sort capability.

    Supports O(1) tail-append, index-based insertion, iteration, and
    chronological sorting by departure_datetime using merge sort.
    """

    def __init__(self) -> None:
        self._head: Optional[Node] = None
        self._tail: Optional[Node] = None
        self._size: int = 0

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def append(self, ticket: Ticket) -> None:
        """Append *ticket* to the end of the list in O(1).

        Args:
            ticket: Ticket to add.
        """
        new_node = Node(ticket)
        if self._tail is None:
            self._head = new_node
            self._tail = new_node
        else:
            self._tail.next = new_node
            self._tail = new_node
        self._size += 1

    def insert(self, index: int, ticket: Ticket) -> None:
        """Insert *ticket* at *index* (0-based).

        Args:
            index: Position to insert at. Clamped to [0, len].
            ticket: Ticket to insert.

        Raises:
            IndexError: If index is negative.
        """
        if index < 0:
            raise IndexError(f"Negative index not supported: {index}")

        if index == 0:
            new_node = Node(ticket)
            new_node.next = self._head
            self._head = new_node
            if self._tail is None:
                self._tail = new_node
            self._size += 1
            return

        if index >= self._size:
            self.append(ticket)
            return

        new_node = Node(ticket)
        current = self._head
        for _ in range(index - 1):
            assert current is not None
            current = current.next

        assert current is not None
        new_node.next = current.next
        current.next = new_node
        self._size += 1

    # ------------------------------------------------------------------
    # Traversal
    # ------------------------------------------------------------------

    def traverse(self) -> Generator[Ticket, None, None]:
        """Yield each ticket in order from head to tail."""
        current = self._head
        while current is not None:
            yield current.data
            current = current.next

    def to_list(self) -> list[Ticket]:
        """Return a plain Python list of all tickets."""
        return list(self.traverse())

    # ------------------------------------------------------------------
    # Sorting (merge sort on linked list)
    # ------------------------------------------------------------------

    def sort_by_departure_datetime(self) -> None:
        """Sort the list chronologically by departure_datetime.

        Uses an iterative-safe recursive merge sort (O(n log n) time,
        O(log n) stack space).  Tickets with ``None`` departure are
        placed at the end.
        """
        self._head = self._merge_sort(self._head)
        # Recompute tail pointer
        self._tail = None
        current = self._head
        while current is not None:
            if current.next is None:
                self._tail = current
            current = current.next

    @staticmethod
    def _get_sort_key(node: Node) -> datetime:
        """Return a sortable datetime, using datetime.max for None values."""
        dt = node.data.departure_datetime
        return dt if dt is not None else datetime.max

    def _merge_sort(self, head: Optional[Node]) -> Optional[Node]:
        """Recursively sort the sub-list starting at *head*.

        Args:
            head: First node of the sub-list to sort.

        Returns:
            Head of the sorted sub-list.
        """
        # Base case: 0 or 1 node
        if head is None or head.next is None:
            return head

        # Split into two halves using slow/fast pointers
        left, right = self._split(head)

        # Recursively sort each half
        left = self._merge_sort(left)
        right = self._merge_sort(right)

        # Merge sorted halves
        return self._merge(left, right)

    @staticmethod
    def _split(head: Node) -> tuple[Node, Optional[Node]]:
        """Split the list at the midpoint using the slow/fast pointer technique.

        Args:
            head: First node of the list to split.

        Returns:
            Tuple of (first_half_head, second_half_head).
        """
        slow: Node = head
        fast: Optional[Node] = head.next

        while fast is not None and fast.next is not None:
            slow = slow.next  # type: ignore[assignment]
            fast = fast.next.next

        mid = slow.next
        slow.next = None  # Cut the list
        return head, mid

    def _merge(
        self, left: Optional[Node], right: Optional[Node]
    ) -> Optional[Node]:
        """Merge two sorted sub-lists into one sorted list.

        Args:
            left: Head of the first sorted sub-list.
            right: Head of the second sorted sub-list.

        Returns:
            Head of the merged sorted list.
        """
        # Dummy head simplifies edge-case handling
        dummy = Node.__new__(Node)
        dummy.next = None
        tail = dummy

        while left is not None and right is not None:
            if self._get_sort_key(left) <= self._get_sort_key(right):
                tail.next = left
                left = left.next
            else:
                tail.next = right
                right = right.next
            tail = tail.next

        # Attach remaining nodes
        tail.next = left if left is not None else right

        return dummy.next

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Generator[Ticket, None, None]:
        return self.traverse()

    def __bool__(self) -> bool:
        return self._size > 0

    def __repr__(self) -> str:
        return f"LinkedList(size={self._size})"
