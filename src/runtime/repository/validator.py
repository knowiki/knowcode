"""Repository integrity validator.

Verifies that a discovered repository meets the preconditions required
by a given operation.  Validation is *contextual* — initialization has
different requirements than synchronization.

Checks
------
- Git repository exists (``.git``).
- KnowCode artifact initialized (``.knowcode``).
- ``state.yaml`` exists.
- ``structure/`` folder exists.

Raises typed exceptions from ``runtime.exceptions.errors``.
"""

from __future__ import annotations

from runtime.exceptions.errors import (
    KnowcodeAlreadyInitialized,
    KnowcodeNotInitialized,
    CorruptKnowcodeArtifact,
    NotGitRepository,
)
from runtime.repository.models import RepositoryPaths


def validate_for_init(paths: RepositoryPaths) -> None:
    """Validate preconditions for ``knowcode .`` (initialization).

    Parameters
    ----------
    paths : RepositoryPaths
        Canonical paths derived from the discovered repository.

    Raises
    ------
    NotGitRepository
        If the ``.git`` directory does not exist.
    KnowcodeAlreadyInitialized
        If a ``.knowcode`` directory already exists.
    """
    git_dir = paths.repo_root / ".git"
    if not git_dir.is_dir():
        raise NotGitRepository(
            f"Not a git repository: {paths.repo_root}"
        )

    if paths.knowcode_root.is_dir():
        raise KnowcodeAlreadyInitialized(
            f"KnowCode artifact already exists: {paths.knowcode_root}"
        )
        
    if paths.agent_dir.is_dir():
        raise KnowcodeAlreadyInitialized(
            f"Agent artifact already exists: {paths.agent_dir}"
        )

def validate_for_sync(paths: RepositoryPaths) -> None:
    """Validate preconditions for ``knowcode sync`` or ``knowcode status``.

    Parameters
    ----------
    paths : RepositoryPaths
        Canonical paths derived from the discovered repository.

    Raises
    ------
    NotGitRepository
        If the ``.git`` directory does not exist.
    KnowcodeNotInitialized
        If the ``.knowcode`` directory does not exist.
    CorruptKnowcodeArtifact
        If ``.knowcode`` exists but critical internal structure is missing.
    """
    git_dir = paths.repo_root / ".git"
    if not git_dir.is_dir():
        raise NotGitRepository(
            f"Not a git repository: {paths.repo_root}"
        )

    if not paths.knowcode_root.is_dir():
        raise KnowcodeNotInitialized(
            f"KnowCode artifact not found. Run 'know .' first: {paths.repo_root}"
        )
        
    if not paths.agent_dir.is_dir():
        raise KnowcodeNotInitialized(
            f"Agent artifact not found. Run 'know .' first: {paths.repo_root}"
        )

    if not paths.state_file.is_file():
        raise CorruptKnowcodeArtifact(
            f"state.yaml missing: {paths.state_file}"
        )

    if not paths.structure_dir.is_dir():
        raise CorruptKnowcodeArtifact(
            f"structure directory missing: {paths.structure_dir}"
        )
