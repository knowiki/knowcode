"""Snapshot generator and persister.

Serializes structural snapshots to JSON for deterministic persistence.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from runtime.repository.models import RepositoryPaths
from structural_engine.parser.models import StructuralSnapshot


def persist(snapshot: StructuralSnapshot, revision_id: str, paths: RepositoryPaths) -> str:
    """Serialize and write a StructuralSnapshot to disk.

    Parameters
    ----------
    snapshot : StructuralSnapshot
        The structural truth to persist.
    revision_id : str
        The ID to use for the snapshot file (e.g. ``S-014``).
    paths : RepositoryPaths
        Canonical paths; writes to ``paths.snapshots_dir``.

    Returns
    -------
    str
        The filename of the created snapshot (e.g. ``S-014.json``).
    """
    snapshot_filename = f"{revision_id}.json"
    snapshot_path = paths.snapshots_dir / snapshot_filename

    # We manually handle the enum serialization by transforming the output of asdict.
    # A cleaner approach in a real app would be a custom JSONEncoder, but this is explicit.
    
    entities = []
    for entity in snapshot.entities:
        d = asdict(entity)
        d["type"] = d["type"].name  # Enum to string
        entities.append(d)

    relationships = []
    for rel in snapshot.relationships:
        d = asdict(rel)
        d["type"] = d["type"].name  # Enum to string
        relationships.append(d)

    data = {
        "entities": entities,
        "relationships": relationships,
    }

    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return snapshot_filename
