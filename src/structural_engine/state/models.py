"""State domain models.

Defines the Structural Engine's partial view of ``state.yaml``.
The Engine only cares about the fields it manages.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StructuralState(BaseModel):
    """The Structural Engine's typed view of state.yaml.

    This model represents the strict, 4-field stewardship boundary.
    It does not contain ``semantic_revision``, which is owned by
    humans/AI agents.
    """

    structural_revision: str
    """The latest structural revision ID (e.g. ``S-015``)."""

    current_snapshot: str
    """The filename of the current snapshot (e.g. ``S-015`` or ``S-015.json``)."""

    latest_report: str
    """The filename of the latest sync report (e.g. ``R-015.md``) or ``none``."""

    last_sync: datetime = Field(default_factory=datetime.utcnow)
    """Timestamp of the last structural synchronization."""

    class Config:
        """Pydantic config."""
        frozen = True
