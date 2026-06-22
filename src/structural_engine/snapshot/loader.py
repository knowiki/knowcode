"""Snapshot loader.

Deserializes JSON snapshots back into frozen model tuples.
"""

from __future__ import annotations

import json
from pathlib import Path

from runtime.repository.models import RepositoryPaths
from structural_engine.parser.models import (
    Entity,
    EntityType,
    Relationship,
    RelationshipType,
    StructuralSnapshot,
)


def load(snapshot_id: str, paths: RepositoryPaths) -> StructuralSnapshot | None:
    """Load a StructuralSnapshot from disk.

    Parameters
    ----------
    snapshot_id : str
        The filename or ID of the snapshot (e.g. ``S-014`` or ``S-014.json``).
    paths : RepositoryPaths
        Canonical paths; reads from ``paths.snapshots_dir``.

    Returns
    -------
    StructuralSnapshot | None
        The hydrated snapshot tuple, or None if the file doesn't exist.
    """
    if not snapshot_id.endswith(".json"):
        snapshot_id = f"{snapshot_id}.json"

    snapshot_path = paths.snapshots_dir / snapshot_id
    if not snapshot_path.is_file():
        return None

    with open(snapshot_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    entities = []
    for ed in data.get("entities", []):
        ed["type"] = EntityType[ed["type"]]
        entities.append(Entity(**ed))

    relationships = []
    for rd in data.get("relationships", []):
        rd["type"] = RelationshipType[rd["type"]]
        relationships.append(Relationship(**rd))

    return StructuralSnapshot(
        entities=tuple(entities),
        relationships=tuple(relationships),
    )
