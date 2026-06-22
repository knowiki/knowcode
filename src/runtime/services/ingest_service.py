"""Ingest service.

Handles the Runtime orchestration for the 'knowcode ingest-semantic' command.
"""

from __future__ import annotations

import structlog
from pathlib import Path
from pydantic import BaseModel

from runtime.exceptions.errors import KnowcodeError
from runtime.repository.discovery import discover_repository
from runtime.repository.paths import build_paths
from structural_engine.state.manager import StateManager

logger = structlog.get_logger(__name__)


class IngestSemanticResult(BaseModel):
    """Result of a semantic ingestion."""
    message: str
    semantic_revision: str
    deleted_files: list[str]


def run_ingest(cwd: Path, target_file: str) -> IngestSemanticResult:
    """Execute the semantic ingestion workflow.

    1. Discover repository
    2. Validate that the target_file is within the raw/ inbox
    3. Delete the target file(s)
    4. Increment the semantic_revision in state.yaml

    Parameters
    ----------
    cwd : Path
        Current working directory to start discovery.
    target_file : str
        The specific file to delete, or "." to empty the inbox.

    Returns
    -------
    IngestSemanticResult
        The result of the ingestion.
        
    Raises
    ------
    KnowcodeError
        If the target_file resolves outside the raw directory sandbox.
    """
    repo = discover_repository(cwd)
    paths = build_paths(repo)
    
    deleted_files = []
    
    if target_file == ".":
        # Bulk deletion: safely iterate over raw directory
        if paths.raw_knowledge_dir.exists():
            for child in paths.raw_knowledge_dir.iterdir():
                if child.is_file() and child.name != "README.md":
                    child.unlink()
                    deleted_files.append(child.name)
        
        if not deleted_files:
            return IngestSemanticResult(
                message="Inbox is already empty.",
                semantic_revision="No change",
                deleted_files=[]
            )
    else:
        # Single file deletion: resolve and validate security boundary
        # target_file could be an absolute path or relative to cwd.
        target_path = Path(target_file).resolve()
        raw_path = paths.raw_knowledge_dir.resolve()
        
        # Security validation: MUST be inside raw directory
        if not target_path.is_relative_to(raw_path):
            raise KnowcodeError(
                f"Security Violation: Target '{target_file}' is not inside the raw inbox directory.\n"
                f"Resolved target: {target_path}\n"
                f"Allowed sandbox: {raw_path}"
            )
            
        if not target_path.exists():
            raise KnowcodeError(f"Target file does not exist: {target_path}")
            
        if target_path.name == "README.md":
            raise KnowcodeError("Cannot delete the inbox README.md placeholder.")

            
        target_path.unlink()
        deleted_files.append(target_path.name)
        
    # Commit the state update
    state_manager = StateManager()
    new_rev = state_manager.increment_semantic_revision(paths)
    
    logger.info("semantic_sync.ingest_flushed", deleted_count=len(deleted_files))
    
    return IngestSemanticResult(
        message=f"Ingested {len(deleted_files)} file(s).",
        semantic_revision=new_rev,
        deleted_files=deleted_files
    )
