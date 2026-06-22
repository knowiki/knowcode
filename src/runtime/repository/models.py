"""Repository domain models.

Defines the two foundational data contracts that form the common language
between the Runtime and the Structural Engine:

- Repository: lightweight identity object for a discovered git repository.
- RepositoryPaths: the canonical 9-field path contract passed to every
  subsystem. No component should hardcode paths like ".knowcode/structure".
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

    knowcode_dir: Path
    """Absolute path to the .knowcode directory (may or may not exist yet)."""

    agent_dir: Path
    """Absolute path to the .agent directory (may or may not exist yet)."""


class RepositoryPaths(BaseModel):
    """Canonical paths for the entire ecosystem.
    
    This is the single source of truth for all filesystem locations.
    All paths are absolute.
    """
    
    model_config = ConfigDict(frozen=True)
    
    repo_root: Path
    """The root of the user's physical repository containing the ``.git`` folder."""
    
    git_dir: Path
    """``.git/`` directory."""
    
    knowcode_root: Path
    """``.knowcode/`` - The top-level KnowCode Artifact directory."""
    
    knowcode_file: Path
    """``.knowcode/KNOWCODE.md`` - The human-readable entrypoint document."""
    
    state_file: Path
    """``.knowcode/state.yaml`` - The definitive synchronization state registry."""
    
    structure_dir: Path
    """``.knowcode/structure/`` - Base directory for structural artifacts."""
    
    snapshots_dir: Path
    """``.knowcode/structure/snapshots/`` - Directory containing S-XXX.json files."""
    
    reports_dir: Path
    """``.knowcode/reports/`` - Directory containing R-XXX.md differential reports."""
    
    logs_dir: Path
    """``.knowcode/logs/`` - Internal system logs."""
    
    knowledge_dir: Path
    """``.knowcode/knowledge/`` - The AI-managed semantic architecture base directory."""
    
    agent_dir: Path
    """``.agent/`` - Semantic Governance and Memory Layer root."""
    
    workflows_dir: Path
    """``.agent/workflows/`` - User-defined orchestration playbooks."""
    
    skills_dir: Path
    """``.agent/skills/`` - Custom agent capability scripts."""
    
    memory_dir: Path
    """``.agent/memory/`` - The short-term semantic working memory buffer."""
    
    active_context_file: Path
    """``.agent/memory/active_context.md`` - the live intent-tracking scratchpad."""
    
    previous_context_file: Path
    """``.agent/memory/previous_context.md`` - the rolled-over intent log waiting for synthesis."""
    
    system_skills_dir: Path
    """``.agent/skills/system/`` - prime directives and system-level skills."""
    
    raw_knowledge_dir: Path
    """``.knowcode/knowledge/raw/`` - inbox for legacy documentation to be ingested."""
