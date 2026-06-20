"""Parser domain models.

All structural data types produced by the parser pipeline.

These models are internal to the Structural Engine.  The Runtime never
imports them directly — it only sees the ``StructuralSnapshot`` indirectly
through result objects returned by the Engine's public interface.

Invariants
----------
- All models are frozen (immutable).
- ``Entity.id`` uses stable, path-based identifiers — never UUIDs.
- ``StructuralSnapshot`` contains no metadata, revisions, or timestamps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path


# ── Enums ─────────────────────────────────────────────────────────────


class EntityType(Enum):
    """Classification of structural entities discovered in a repository."""

    REPOSITORY = auto()
    DIRECTORY = auto()
    FILE = auto()
    CLASS = auto()
    INTERFACE = auto()
    FUNCTION = auto()
    METHOD = auto()


class RelationshipType(Enum):
    """Classification of structural relationships between entities."""

    CONTAINS = auto()
    IMPORTS = auto()
    INHERITS = auto()
    IMPLEMENTS = auto()
    CALLS = auto()


class Language(Enum):
    """Supported programming languages for structural parsing.

    V1 supports Python, TypeScript, and JavaScript.
    """

    PYTHON = auto()
    TYPESCRIPT = auto()
    JAVASCRIPT = auto()


# ── Extension → Language mapping ──────────────────────────────────────

EXTENSION_LANGUAGE_MAP: dict[str, Language] = {
    ".py": Language.PYTHON,
    ".ts": Language.TYPESCRIPT,
    ".tsx": Language.TYPESCRIPT,
    ".js": Language.JAVASCRIPT,
}


# ── Data models ───────────────────────────────────────────────────────


@dataclass(frozen=True)
class FileInfo:
    """A discovered source file with its resolved language.

    Produced by file discovery, consumed by the tree-sitter parsing stage.
    """

    absolute_path: Path
    """Absolute path to the source file on disk."""

    relative_path: str
    """Path relative to repository root, using forward slashes (e.g. ``src/auth.py``)."""

    language: Language
    """Detected programming language."""


@dataclass(frozen=True)
class Entity:
    """A structural entity extracted from the repository.

    Entities are identified by stable, path-based string IDs that are
    deterministic across machines and runs.

    ID Examples
    -----------
    ::

        repo
        src
        src/auth.py
        src/auth.py::verify_token
        src/auth.py::UserService
        src/auth.py::UserService::create_user
    """

    id: str
    """Stable path-based identifier.  Never a UUID."""

    type: EntityType
    """Structural classification of this entity."""

    name: str
    """Human-readable name (e.g. ``verify_token``, ``UserService``)."""

    path: str
    """Relative file path within the repository (forward slashes)."""

    parent_id: str | None
    """ID of the containing entity, or *None* for the repository root."""

    start_line: int
    """1-indexed start line in the source file.  0 for non-file entities."""

    end_line: int
    """1-indexed end line in the source file.  0 for non-file entities."""


@dataclass(frozen=True)
class Relationship:
    """A directed structural relationship between two entities.

    Relationships are matched for diffing using the composite key
    ``(source_id, target_id, type)``.
    """

    source_id: str
    """ID of the originating entity."""

    target_id: str
    """ID of the target entity."""

    type: RelationshipType
    """Classification of this relationship."""


@dataclass(frozen=True)
class RawCall:
    """An unresolved function/method call extracted from source code.

    Raw calls are an intermediate representation produced by call
    extraction and consumed by the call resolver.  They do not appear
    in the final snapshot.
    """

    caller_id: str
    """Stable ID of the entity that makes the call."""

    target_name: str
    """Unresolved name of the called function/method."""

    source_file: str
    """Relative path to the source file."""

    line: int
    """1-indexed line number of the call site."""


@dataclass(frozen=True)
class StructuralSnapshot:
    """Complete structural truth of a repository at a point in time.

    Contains all discovered entities and relationships.
    No metadata, revisions, timestamps, or reports.

    Sorting contract (guarantees deterministic output):
    - ``entities`` sorted by ``id``
    - ``relationships`` sorted by ``(source_id, target_id, type.name)``
    """

    entities: tuple[Entity, ...] = field(default_factory=tuple)
    """All structural entities, sorted by ``id``."""

    relationships: tuple[Relationship, ...] = field(default_factory=tuple)
    """All structural relationships, sorted by composite key."""
