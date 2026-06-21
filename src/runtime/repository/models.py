"""Repository domain models.

Defines the two foundational data contracts that form the common language
between the Runtime and the Structural Engine:

- Repository: lightweight identity object for a discovered git repository.
- RepositoryPaths: the canonical 9-field path contract passed to every
  subsystem. No component should hardcode paths like ".brain/structure".
  Everything comes from RepositoryPaths.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict


class Repository(BaseModel):
    """Lightweight identity of a discovered git repository.

    Produced by ``discover_repository()``, consumed by ``build_paths()``.
    Contains only the three root-level anchors needed to derive all other
    paths.
    """

    model_config = ConfigDict(frozen=True)

    root: Path
    """Absolute path to the repository root (the directory containing .git)."""

    git_dir: Path
    """Absolute path to the .git directory."""

    brain_dir: Path
    """Absolute path to the .brain directory (may or may not exist yet)."""

    agent_dir: Path
    """Absolute path to the .agent directory (may or may not exist yet)."""


class RepositoryPaths(BaseModel):
    """The canonical 12-field path contract.

    This is the single most important object in the ecosystem.
    The entire Runtime and Structural Engine communicate using this object.

    The Structural Engine accepts the full object and simply ignores the
    fields it does not need. No intermediate translation or mapping layer
    exists.
    """

    model_config = ConfigDict(frozen=True)

    repo_root: Path
    """Repository root directory."""
    
    brain_root: Path
    """``.brain/`` directory."""
    
    agent_root: Path
    """``.agent/`` directory."""
    
    structure_dir: Path
    """``.brain/structure/`` - parent of snapshots."""
    
    snapshots_dir: Path
    """``.brain/structure/snapshots/`` - snapshot JSON files."""
    
    reports_dir: Path
    """``.brain/reports/`` - structural evolution reports."""
    
    logs_dir: Path
    """``.brain/logs/`` - synchronization history."""
    
    knowledge_dir: Path
    """``.brain/knowledge/`` - semantic knowledge (human/AI owned)."""
    
    state_file: Path
    """``.brain/state.yaml`` - the definitive synchronization authority."""
    
    brain_file: Path
    """``.agent/BRAIN.md`` - the master governance and human-facing orientation document."""
    
    skills_dir: Path
    """``.agent/skills/`` - agent capabilities."""
    
    workflows_dir: Path
    """``.agent/workflows/`` - agent orchestrations."""
    
    memory_dir: Path
    """``.agent/memory/`` - agent's short-term scratchpad."""
    
    active_context_file: Path
    """``.agent/memory/active_context.md`` - the active session intent log."""
    
    previous_context_file: Path
    """``.agent/memory/previous_context.md`` - the rolled-over intent log waiting for synthesis."""
    
    system_skills_dir: Path
    """``.agent/skills/system/`` - prime directives and system-level skills."""
