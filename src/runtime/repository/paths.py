"""Repository path builder.

Transforms a ``Repository`` identity into the canonical 9-field
``RepositoryPaths`` contract.

This module performs pure path generation.
No validation occurs here.  No filesystem access.
"""

from __future__ import annotations

from runtime.repository.models import Repository, RepositoryPaths


def build_paths(repo: Repository) -> RepositoryPaths:
    """Derive all canonical paths from a repository identity.

    Parameters
    ----------
    repo : Repository
        The discovered repository identity.

    Returns
    -------
    RepositoryPaths
        The 9-field path contract consumed by the entire ecosystem.
    """
    brain = repo.brain_dir
    structure = brain / "structure"

    return RepositoryPaths(
        repo_root=repo.root,
        brain_root=brain,
        structure_dir=structure,
        snapshots_dir=structure / "snapshots",
        reports_dir=brain / "reports",
        logs_dir=brain / "logs",
        knowledge_dir=brain / "knowledge",
        state_file=brain / "state.yaml",
        brain_file=brain / "BRAIN.md",
    )
