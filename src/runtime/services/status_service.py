"""Status service.

Handles the Runtime orchestration for the 'brain status' command.
"""

from __future__ import annotations

from pathlib import Path

from runtime.repository.discovery import discover_repository
from runtime.repository.paths import build_paths
from runtime.repository.validator import validate_for_sync
from structural_engine.engine import StructuralEngine
from structural_engine.results import StructuralStatusResult


def run_status(cwd: Path) -> StructuralStatusResult:
    """Execute the status workflow.

    1. Discover repository
    2. Validate preconditions
    3. Call StructuralEngine.status()

    Parameters
    ----------
    cwd : Path
        Current working directory to start discovery.

    Returns
    -------
    StructuralStatusResult
        The result from the engine.
    """
    repo = discover_repository(cwd)
    paths = build_paths(repo)
    
    validate_for_sync(paths)
    
    engine = StructuralEngine()
    return engine.status(paths)
