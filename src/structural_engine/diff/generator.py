"""Diff generator.

Calculates the delta between two snapshots.
"""

from __future__ import annotations

from structural_engine.diff.models import StructuralDiff
from structural_engine.parser.models import Entity, Relationship, StructuralSnapshot


def generate(previous: StructuralSnapshot, current: StructuralSnapshot) -> StructuralDiff:
    """Generate the structural difference between two snapshots.

    Parameters
    ----------
    previous : StructuralSnapshot
        The older state.
    current : StructuralSnapshot
        The newer state.

    Returns
    -------
    StructuralDiff
        The computed delta.
    """
    prev_entities = {e.id: e for e in previous.entities}
    curr_entities = {e.id: e for e in current.entities}

    added_entities: list[Entity] = []
    removed_entities: list[Entity] = []
    modified_entities: list[Entity] = []
    affected_components: set[str] = set()

    def _track_component(entity_id: str) -> None:
        """Extract top-level directory from an ID to mark component as affected."""
        # e.g., src/auth.py::verify_token -> src
        # or tests/test_auth.py -> tests
        path_part = entity_id.split("::")[0]
        if "/" in path_part:
            component = path_part.split("/")[0]
            affected_components.add(component)
        else:
            affected_components.add("root")

    for e_id, e_curr in curr_entities.items():
        if e_id not in prev_entities:
            added_entities.append(e_curr)
            _track_component(e_id)
        else:
            e_prev = prev_entities[e_id]
            # Simple line or property shift check
            if (
                e_curr.start_line != e_prev.start_line
                or e_curr.end_line != e_prev.end_line
                or e_curr.type != e_prev.type
                or e_curr.parent_id != e_prev.parent_id
            ):
                modified_entities.append(e_curr)
                _track_component(e_id)

    for e_id, e_prev in prev_entities.items():
        if e_id not in curr_entities:
            removed_entities.append(e_prev)
            _track_component(e_id)

    # Relationship diffs
    # Relationships are identified by the tuple (source_id, target_id, type)
    prev_rels = {(r.source_id, r.target_id, r.type.name): r for r in previous.relationships}
    curr_rels = {(r.source_id, r.target_id, r.type.name): r for r in current.relationships}

    added_rels: list[Relationship] = []
    removed_rels: list[Relationship] = []

    for key, r_curr in curr_rels.items():
        if key not in prev_rels:
            added_rels.append(r_curr)
            _track_component(r_curr.source_id)

    for key, r_prev in prev_rels.items():
        if key not in curr_rels:
            removed_rels.append(r_prev)
            _track_component(r_prev.source_id)

    return StructuralDiff(
        entities_added=tuple(added_entities),
        entities_removed=tuple(removed_entities),
        entities_modified=tuple(modified_entities),
        relationships_added=tuple(added_rels),
        relationships_removed=tuple(removed_rels),
        affected_components=frozenset(affected_components),
    )
