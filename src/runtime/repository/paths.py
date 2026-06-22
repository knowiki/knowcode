"""Repository path builder.

Transforms a ``Repository`` identity into the canonical 9-field
``RepositoryPaths`` contract.

This module performs pure path generation.
No validation occurs here.  No filesystem access.
"""

from __future__ import annotations

from runtime.repository.models import Repository, RepositoryPaths


def build_paths(repo: Repository) -> RepositoryPaths:
    """Build the full path contract from a discovered repository identity.

    Parameters
    ----------
    repo : Repository
        The base identity object containing the root anchors.

    Returns
    -------
    RepositoryPaths
        The canonical, immutable path contract for the ecosystem.
    """
    knowcode = repo.knowcode_dir
    agent = repo.agent_dir

    return RepositoryPaths(
        repo_root=repo.root,
        git_dir=repo.git_dir,
        knowcode_root=knowcode,
        knowcode_file=knowcode / "KNOWCODE.md",
        state_file=knowcode / "state.yaml",
        structure_dir=knowcode / "structure",
        snapshots_dir=knowcode / "structure" / "snapshots",
        reports_dir=knowcode / "reports",
        logs_dir=knowcode / "logs",
        knowledge_dir=knowcode / "knowledge",
        agent_dir=agent,
        workflows_dir=agent / "workflows",
        skills_dir=agent / "skills",
        memory_dir=agent / "memory",
        active_context_file=agent / "memory" / "active_context.md",
        previous_context_file=agent / "memory" / "previous_context.md",
        system_skills_dir=agent / "skills" / "system",
        raw_knowledge_dir=knowcode / "knowledge" / "raw",
    )
