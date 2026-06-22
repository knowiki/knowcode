"""Parser — public interface.

The Parser is the observation subsystem of the Structural Engine.
It answers one question:

    *What does the repository look like right now?*

Contract
--------
::

    parse(paths: RepositoryPaths) -> StructuralSnapshot

Invariants
----------
- **Deterministic:** Identical repository states always produce identical
  snapshots, regardless of machine, user, or OS.
- **Stateless:** Never reads ``state.yaml``, previous snapshots, reports,
  logs, or knowledge.  Current repository state is the only authority.
- **Side-effect free:** Performs no writes, no filesystem mutations,
  no revision generation, no persistence.
- **No Brain awareness:** Accepts ``RepositoryPaths`` but only consumes
  ``paths.repo_root``.  All other fields are ignored.

Pipeline (Phase 2A stub — discovery only)
-----------------------------------------
::

    RepositoryPaths
        ↓
    repo_root
        ↓
    File Discovery
        ↓
    Language Detection
        ↓
    [Tree-sitter Parse]       ← Phase 2B
        ↓
    [Entity Extraction]       ← Phase 2B
        ↓
    [Relationship Extraction] ← Phase 2B
        ↓
    [Call Resolution]         ← Phase 2B
        ↓
    StructuralSnapshot
"""

from __future__ import annotations

import structlog

from runtime.repository.models import RepositoryPaths
from structural_engine.parser.discovery import discover_files
from structural_engine.parser.models import StructuralSnapshot, Entity, Relationship, RawCall, Language

logger = structlog.get_logger(__name__)


def parse(paths: RepositoryPaths) -> StructuralSnapshot:
    """Parse a repository and produce its structural snapshot.

    This is the sole public entry point of the Parser subsystem.
    Called by ``StructuralEngine.initialize()`` and
    ``StructuralEngine.sync()``.

    Parameters
    ----------
    paths : RepositoryPaths
        Canonical 9-field path contract.  Only ``paths.repo_root`` is
        consumed by the parser.

    Returns
    -------
    StructuralSnapshot
        Complete structural truth of the repository.
        Entities sorted by ``id``, relationships sorted by composite key.

    Notes
    -----
    **Phase 2A stub:** Currently performs file discovery and language
    detection only.  Tree-sitter extraction, entity/relationship
    building, and call resolution will be added in Phase 2B.
    """
    repo_root = paths.repo_root

    logger.info("parser.started", repo_root=str(repo_root))

    # ── Stage 1: File Discovery + Language Detection ──────────────
    files = discover_files(repo_root)
    logger.info(
        "parser.discovery_complete",
        files_found=len(files),
        languages={
            lang.name: sum(1 for f in files if f.language == lang)
            for lang in set(f.language for f in files)
        },
    )

    # ── Stages 2–7: Tree-sitter parsing, extraction, resolution ──
    all_entities: list[Entity] = []
    all_relationships: list[Relationship] = []
    all_raw_calls: list[RawCall] = []

    for file_info in files:
        # 1. Get the language parser
        try:
            from structural_engine.parser.tree_sitter.registry import get_parser
            ts_parser = get_parser(file_info.language)
        except ValueError:
            logger.warning("parser.unsupported_language", file=file_info.relative_path, language=file_info.language.name)
            continue

        # 2. Parse the source code
        try:
            source_bytes = file_info.absolute_path.read_bytes()
            tree = ts_parser.parse(source_bytes)
        except Exception as e:
            logger.error("parser.parse_failed", file=file_info.relative_path, error=str(e))
            continue

        # 3. Extract structural facts
        adapter = None
        if file_info.language == Language.PYTHON:
            from structural_engine.parser.languages.python.adapter import PythonAdapter
            adapter = PythonAdapter()
        elif file_info.language == Language.JAVASCRIPT:
            from structural_engine.parser.languages.javascript.adapter import JavaScriptAdapter
            adapter = JavaScriptAdapter()
        elif file_info.language == Language.TYPESCRIPT:
            from structural_engine.parser.languages.typescript.adapter import TypeScriptAdapter
            adapter = TypeScriptAdapter()

        if adapter:
            result = adapter.extract(file_info, tree, source_bytes)
            all_entities.extend(result.entities)
            all_relationships.extend(result.relationships)
            all_raw_calls.extend(result.raw_calls)

    # 4. Resolve calls
    from structural_engine.parser.resolvers.calls import resolve_calls
    resolved_calls = resolve_calls(all_entities, all_relationships, all_raw_calls)
    all_relationships.extend(resolved_calls)

    # 5. Sort for deterministic output
    all_entities.sort(key=lambda e: e.id)
    all_relationships.sort(key=lambda r: (r.source_id, r.target_id, r.type.name))

    snapshot = StructuralSnapshot(
        entities=tuple(all_entities),
        relationships=tuple(all_relationships)
    )

    logger.info(
        "parser.complete",
        entities=len(snapshot.entities),
        relationships=len(snapshot.relationships),
        resolved_calls=len(resolved_calls),
    )

    return snapshot
