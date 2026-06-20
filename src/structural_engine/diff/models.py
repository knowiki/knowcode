"""Diff domain models.

Represents the structural delta between two snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from structural_engine.parser.models import Entity, Relationship


@dataclass(frozen=True)
class StructuralDiff:
    """The delta between two structural states.

    Identifies exactly what changed structurally, ignoring pure logic
    modifications that don't shift AST bounds or signatures.
    """

    entities_added: tuple[Entity, ...] = field(default_factory=tuple)
    """Entities present in current but not in previous."""

    entities_removed: tuple[Entity, ...] = field(default_factory=tuple)
    """Entities present in previous but not in current."""

    entities_modified: tuple[Entity, ...] = field(default_factory=tuple)
    """Entities whose lines shifted or properties changed, but ID matched."""

    relationships_added: tuple[Relationship, ...] = field(default_factory=tuple)
    """Relationships present in current but not in previous."""

    relationships_removed: tuple[Relationship, ...] = field(default_factory=tuple)
    """Relationships present in previous but not in current."""

    affected_components: frozenset[str] = field(default_factory=frozenset)
    """Top-level directories (components) affected by these changes."""

    @property
    def has_changes(self) -> bool:
        """Return True if any structural change occurred."""
        return bool(
            self.entities_added
            or self.entities_removed
            or self.entities_modified
            or self.relationships_added
            or self.relationships_removed
        )
