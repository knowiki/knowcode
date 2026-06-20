"""Sync service.

Handles the Runtime orchestration for the 'brain sync' command.
"""

from __future__ import annotations

from pathlib import Path

from runtime.repository.discovery import discover_repository
from runtime.repository.paths import build_paths
from runtime.repository.validator import validate_for_sync
from structural_engine.engine import StructuralEngine
from structural_engine.results import SyncResult


def run_sync(cwd: Path) -> SyncResult:
    """Execute the synchronization workflow.

    1. Discover repository
    2. Validate preconditions
    3. Call StructuralEngine.sync()

    Parameters
    ----------
    cwd : Path
        Current working directory to start discovery.

    Returns
    -------
    SyncResult
        The result from the engine.
    """
    repo = discover_repository(cwd)
    paths = build_paths(repo)
    
    validate_for_sync(paths)
    
    engine = StructuralEngine()
    return engine.sync(paths)
