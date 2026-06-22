"""Init service.

Handles the Runtime orchestration for the 'know .' command.
"""

from __future__ import annotations

from pathlib import Path

from runtime.artifact.builder import ArtifactBuilder
from runtime.repository.discovery import discover_repository
from runtime.repository.paths import build_paths
from runtime.repository.validator import validate_for_init
from structural_engine.engine import StructuralEngine
from structural_engine.results import InitializationResult


def run_init(cwd: Path) -> InitializationResult:
    """Execute the initialization workflow.

    1. Discover repository
    2. Validate preconditions
    3. Build artifact directories and templates
    4. Call StructuralEngine.initialize()

    Parameters
    ----------
    cwd : Path
        Current working directory to start discovery.

    Returns
    -------
    InitializationResult
        The result from the engine.
    """
    repo = discover_repository(cwd)
    paths = build_paths(repo)
    
    validate_for_init(paths)
    
    builder = ArtifactBuilder(paths)
    builder.build()
    
    engine = StructuralEngine()
    return engine.initialize(paths)
