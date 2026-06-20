"""Revision tracking logic.

Calculates the next structural revision ID based on the current ID.
"""

from __future__ import annotations


def get_next_revision(current_id: str) -> str:
    """Calculate the next sequential revision ID.

    Parameters
    ----------
    current_id : str
        The current structural revision ID (e.g. ``S-014``).

    Returns
    -------
    str
        The next sequential ID (e.g. ``S-015``).
        If the current_id format is invalid, returns ``S-001``.
    """
    if not current_id.startswith("S-") or len(current_id) != 5:
        # Fallback for corrupted state or unparseable initial state
        return "S-001"

    try:
        current_num = int(current_id[2:])
        next_num = current_num + 1
        return f"S-{next_num:03d}"
    except ValueError:
        return "S-001"
