"""Semantic Sync service.

Handles the Runtime orchestration for the 'brain sync-semantic' command.
"""

from __future__ import annotations

import structlog
from pathlib import Path
from pydantic import BaseModel

from runtime.repository.discovery import discover_repository
from runtime.repository.paths import build_paths
from structural_engine.state.manager import StateManager

logger = structlog.get_logger(__name__)


class SemanticSyncResult(BaseModel):
    """Result of a semantic synchronization."""
    message: str
    semantic_revision: str


def run_semantic_sync(cwd: Path) -> SemanticSyncResult:
    """Execute the semantic synchronization workflow.

    1. Discover repository
    2. Increment the semantic_revision in state.yaml
    3. Delete the previous_context.md file, flushing the queue

    Parameters
    ----------
    cwd : Path
        Current working directory to start discovery.

    Returns
    -------
    SemanticSyncResult
        The result of the sync.
    """
    repo = discover_repository(cwd)
    paths = build_paths(repo)
    
    state_manager = StateManager()
    new_rev = state_manager.increment_semantic_revision(paths)
    
    if paths.previous_context_file.exists():
        paths.previous_context_file.unlink()
        logger.info("semantic_sync.memory_flushed", file=str(paths.previous_context_file))
        
    return SemanticSyncResult(
        message="Semantic Knowledge Synchronized.",
        semantic_revision=new_rev
    )
