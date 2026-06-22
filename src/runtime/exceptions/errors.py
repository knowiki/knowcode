"""Runtime exceptions.

All Runtime-level exceptions inherit from ``KnowcodeError`` so that the
CLI can catch them uniformly and format them as user-friendly messages
without stack traces.

Hierarchy
---------
::

    KnowcodeError
    ├── RepositoryError
    │   ├── NotGitRepository
    │   └── RepositoryNotFound
    ├── ArtifactError
    │   ├── KnowcodeAlreadyInitialized
    │   ├── KnowcodeNotInitialized
    │   ├── CorruptKnowcodeArtifact
    │   ├── ScaffoldingFailed
    │   └── TemplateRenderFailed
    ├── ConfigError
    │   ├── ConfigNotFound
    │   └── InvalidConfig
    └── SyncError
        ├── StructuralEngineFailure
        └── SemanticSyncFailure
"""

from __future__ import annotations


class KnowcodeError(Exception):
    """Base exception for all domain-level KnowCode errors.

    Caught by the CLI layer to present a clean, un-traced error message.
    """


class RepositoryError(KnowcodeError):
    """Base exception for repository discovery and path issues."""


class NotGitRepository(RepositoryError):
    """The target directory is not inside a git repository."""


class RepositoryNotFound(RepositoryError):
    """Raised when no `.git` directory can be found by walking upward.

    This indicates KnowCode was invoked outside a valid git repository.
    """


class ArtifactError(KnowcodeError):
    """Base exception for KnowCode artifact filesystem failures."""


class KnowcodeAlreadyInitialized(ArtifactError):
    """A .knowcode directory already exists in this repository."""


class KnowcodeNotInitialized(ArtifactError):
    """No .knowcode directory found — run ``knowcode .`` first."""


class CorruptKnowcodeArtifact(ArtifactError):
    """The .knowcode directory exists but is structurally invalid."""


class ScaffoldingFailed(ArtifactError):
    """Raised when directory creation fails (e.g., permission denied)."""


class TemplateRenderFailed(ArtifactError):
    """Raised when a static markdown template fails to render."""


class ConfigError(KnowcodeError):
    """Base exception for configuration loading or parsing failures."""


class ConfigNotFound(ConfigError):
    """Raised when `config.yaml` is missing and is strictly required."""


class InvalidConfig(ConfigError):
    """Raised when `config.yaml` contains malformed or invalid YAML."""


class SyncError(KnowcodeError):
    """Base exception for synchronization workflow failures."""


class StructuralEngineFailure(SyncError):
    """The Structural Engine raised an unrecoverable error during sync."""


class SemanticSyncFailure(SyncError):
    """Raised when the semantic reconciliation workflow fails."""
