"""Repository integrity validator.

Verifies that a discovered repository meets the preconditions required
by a given operation.  Validation is *contextual* — initialization has
different requirements than synchronization.

Checks
------
- Git repository exists (``.git``).
- Brain artifact initialized (``.brain``).
- ``state.yaml`` exists.
- ``structure/`` folder exists.

Raises typed exceptions from ``runtime.exceptions.errors``.
"""

from __future__ import annotations

from runtime.exceptions.errors import (
    BrainAlreadyInitialized,
    BrainNotInitialized,
    CorruptBrainArtifact,
    NotGitRepository,
)
from runtime.repository.models import RepositoryPaths


def validate_for_init(paths: RepositoryPaths) -> None:
    """Validate preconditions for ``brain .`` (initialization).

    Parameters
    ----------
    paths : RepositoryPaths
        Canonical paths derived from the discovered repository.

    Raises
    ------
    NotGitRepository
        If the ``.git`` directory does not exist.
    BrainAlreadyInitialized
        If a ``.brain`` directory already exists.
    """
    git_dir = paths.repo_root / ".git"
    if not git_dir.is_dir():
        raise NotGitRepository(
            f"Not a git repository: {paths.repo_root}"
        )

    if paths.brain_root.is_dir():
        raise BrainAlreadyInitialized(
            f"Brain artifact already exists: {paths.brain_root}"
        )
        
    if paths.agent_root.is_dir():
        raise BrainAlreadyInitialized(
            f"Agent artifact already exists: {paths.agent_root}"
        )


def validate_for_sync(paths: RepositoryPaths) -> None:
    """Validate preconditions for ``brain sync`` or ``brain status``.

    Parameters
    ----------
    paths : RepositoryPaths
        Canonical paths derived from the discovered repository.

    Raises
    ------
    NotGitRepository
        If the ``.git`` directory does not exist.
    BrainNotInitialized
        If the ``.brain`` directory does not exist.
    CorruptBrainArtifact
        If ``.brain`` exists but critical internal structure is missing.
    """
    git_dir = paths.repo_root / ".git"
    if not git_dir.is_dir():
        raise NotGitRepository(
            f"Not a git repository: {paths.repo_root}"
        )

    if not paths.brain_root.is_dir():
        raise BrainNotInitialized(
            f"Brain artifact not found. Run 'brain .' first: {paths.repo_root}"
        )
        
    if not paths.agent_root.is_dir():
        raise BrainNotInitialized(
            f"Agent artifact not found. Run 'brain .' first: {paths.repo_root}"
        )

    if not paths.state_file.is_file():
        raise CorruptBrainArtifact(
            f"state.yaml missing: {paths.state_file}"
        )

    if not paths.structure_dir.is_dir():
        raise CorruptBrainArtifact(
            f"structure directory missing: {paths.structure_dir}"
        )
