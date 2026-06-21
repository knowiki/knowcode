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
    result = engine.sync(paths)
    
    # Rollover the active context memory if structural changes occurred
    if result.changes_detected and paths.active_context_file.exists():
        active_content = paths.active_context_file.read_text(encoding="utf-8")
        
        if paths.previous_context_file.exists():
            with open(paths.previous_context_file, "a", encoding="utf-8") as f:
                f.write("\n\n---\n\n" + active_content)
        else:
            paths.previous_context_file.write_text(active_content, encoding="utf-8")
            
        import jinja2
        env = jinja2.Environment(loader=jinja2.PackageLoader("runtime", "templates"))
        template = env.get_template("active_context.md.j2")
        paths.active_context_file.write_text(template.render(), encoding="utf-8")
        
    return result
