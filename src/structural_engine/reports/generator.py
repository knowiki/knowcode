"""Report generator.

Creates human-readable Markdown summaries of structural diffs.
"""

from __future__ import annotations

from runtime.repository.models import RepositoryPaths
from structural_engine.diff.models import StructuralDiff


def generate(diff: StructuralDiff, revision_id: str, paths: RepositoryPaths) -> str:
    """Generate and write a human-readable report of the diff.

    Parameters
    ----------
    diff : StructuralDiff
        The computed structural changes.
    revision_id : str
        The ID of the new structural revision (e.g. ``S-014``).
    paths : RepositoryPaths
        Canonical paths; writes to ``paths.reports_dir``.

    Returns
    -------
    str
        The filename of the created report (e.g. ``R-014.md``), or
        ``none`` if no report was generated (e.g., no changes).
    """
    if not diff.has_changes:
        return "none"

    report_filename = f"R-{revision_id[2:]}.md"
    report_path = paths.reports_dir / report_filename

    lines = [
        f"# Structural Sync Report: {revision_id}",
        "",
        "## Affected Components",
    ]

    for comp in sorted(diff.affected_components):
        lines.append(f"- `{comp}/`")
    lines.append("")

    if diff.entities_added:
        lines.append("## Entities Added")
        for e in sorted(diff.entities_added, key=lambda x: x.id):
            lines.append(f"- **{e.type.name}**: `{e.id}`")
        lines.append("")

    if diff.entities_removed:
        lines.append("## Entities Removed")
        for e in sorted(diff.entities_removed, key=lambda x: x.id):
            lines.append(f"- **{e.type.name}**: `{e.id}`")
        lines.append("")

    if diff.entities_modified:
        lines.append("## Entities Modified (Line Shifts / Signature Changes)")
        for e in sorted(diff.entities_modified, key=lambda x: x.id):
            lines.append(f"- **{e.type.name}**: `{e.id}` (Lines {e.start_line}-{e.end_line})")
        lines.append("")

    if diff.relationships_added:
        lines.append("## Relationships Added")
        for r in sorted(diff.relationships_added, key=lambda x: (x.source_id, x.target_id)):
            lines.append(f"- `{r.source_id}` **{r.type.name}** `{r.target_id}`")
        lines.append("")

    if diff.relationships_removed:
        lines.append("## Relationships Removed")
        for r in sorted(diff.relationships_removed, key=lambda x: (x.source_id, x.target_id)):
            lines.append(f"- `{r.source_id}` **{r.type.name}** `{r.target_id}`")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_filename
