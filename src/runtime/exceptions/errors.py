"""Runtime exception hierarchy.

All Runtime-level exceptions inherit from ``BrainError`` so that the
CLI layer can catch a single base class and render user-friendly output.

Hierarchy
---------
::

    BrainError
    ├── RepositoryError
    │   ├── NotGitRepository
    │   └── RepositoryNotFound
    ├── ArtifactError
    │   ├── BrainAlreadyInitialized
    │   ├── BrainNotInitialized
    │   └── CorruptBrainArtifact
    ├── ConfigError
    │   ├── InvalidConfig
    │   └── MissingConfig
    └── SyncError
        └── StructuralEngineFailure
"""

from __future__ import annotations


# ── Base ──────────────────────────────────────────────────────────────
class BrainError(Exception):
    """Root of the Runtime exception hierarchy."""


# ── Repository ────────────────────────────────────────────────────────
class RepositoryError(BrainError):
    """Errors related to repository discovery and validation."""


class NotGitRepository(RepositoryError):
    """The target directory is not inside a git repository."""


class RepositoryNotFound(RepositoryError):
    """No git repository could be found by walking upward from cwd."""


# ── Artifact ──────────────────────────────────────────────────────────
class ArtifactError(BrainError):
    """Errors related to the Brain artifact filesystem."""


class BrainAlreadyInitialized(ArtifactError):
    """A .brain directory already exists in this repository."""


class BrainNotInitialized(ArtifactError):
    """No .brain directory found — run ``brain .`` first."""


class CorruptBrainArtifact(ArtifactError):
    """The .brain directory exists but is structurally invalid."""


# ── Config ────────────────────────────────────────────────────────────
class ConfigError(BrainError):
    """Errors related to runtime configuration."""


class InvalidConfig(ConfigError):
    """Configuration file contains invalid values."""


class MissingConfig(ConfigError):
    """Expected configuration file was not found."""


# ── Sync ──────────────────────────────────────────────────────────────
class SyncError(BrainError):
    """Errors during structural synchronization."""


class StructuralEngineFailure(SyncError):
    """The Structural Engine raised an unrecoverable error during sync."""
