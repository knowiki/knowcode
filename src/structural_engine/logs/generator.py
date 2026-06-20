"""Log generator.

Appends structured timestamps and operations to the sync log.
"""

from __future__ import annotations

from datetime import datetime, timezone

from runtime.repository.models import RepositoryPaths


def append(revision_id: str, report_id: str, status: str, paths: RepositoryPaths) -> None:
    """Append a sync operation entry to the persistent log.

    Parameters
    ----------
    revision_id : str
        The ID of the generated structural revision.
    report_id : str
        The filename of the generated report, or ``none``.
    status : str
        The outcome of the sync (e.g. ``SUCCESS``, ``NO_CHANGES``).
    paths : RepositoryPaths
        Canonical paths; appends to ``paths.logs_dir / sync.md``.
    """
    log_file = paths.logs_dir / "sync.md"
    timestamp = datetime.now(timezone.utc).isoformat()

    entry = f"- **{timestamp}** | Revision: `{revision_id}` | Report: `{report_id}` | Status: `{status}`\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)
