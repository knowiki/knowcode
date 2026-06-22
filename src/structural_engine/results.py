"""Structural Engine result contracts.

These models form the strict return boundary between the Engine and the Runtime.
The Runtime only imports these results and the ``StructuralEngine`` facade.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class InitializationResult:
    """Result of a successful KnowCode initialization."""

    success: bool
    structural_revision: str
    snapshot_file: str
    message: str


@dataclass(frozen=True)
class SyncResult:
    """Result of a sync operation.

    If ``changes_detected`` is False, the other fields reflect the existing
    unchanged state.
    """

    success: bool
    changes_detected: bool
    structural_revision: str
    snapshot_file: str
    report_file: str
    message: str
    affected_components: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class StructuralStatusResult:
    """Current status of the structural state.

    Provides a comprehensive view of the engine's internal state
    plus unowned passthrough fields (like semantic_revision).
    """

    initialized: bool
    structural_revision: str
    semantic_revision: str
    current_snapshot: str
    latest_report: str
    last_sync: datetime | None
    repository_root: str
