"""Base extraction architecture.

Defines the interface for language-specific adapters that extract
entities, relationships, and raw calls from tree-sitter ASTs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import tree_sitter

from structural_engine.parser.models import Entity, FileInfo, RawCall, Relationship

@dataclass
class ExtractionResult:
    """Accumulates structural information extracted from a single file."""

    entities: list[Entity] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    raw_calls: list[RawCall] = field(default_factory=list)

class LanguageAdapter(Protocol):
    """Protocol for language-specific tree-sitter AST extractors."""

    def extract(self, file_info: FileInfo, tree: tree_sitter.Tree, source_bytes: bytes) -> ExtractionResult:
        """Extract structural facts from a parsed AST.

        Parameters
        ----------
        file_info : FileInfo
            Information about the source file being parsed.
        tree : tree_sitter.Tree
            The tree-sitter syntax tree.
        source_bytes : bytes
            The raw bytes of the source file.

        Returns
        -------
        ExtractionResult
            The extracted entities, relationships, and unresolved calls.
        """
        ...
