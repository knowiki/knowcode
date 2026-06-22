"""Structural Engine Facade.

The single public entry point for all structural operations.
Orchestrates parsers, state, diffs, and generators safely behind
a strict facade.
"""

from __future__ import annotations

import structlog
from ruamel.yaml import YAML

from runtime.exceptions.errors import StructuralEngineFailure
from runtime.repository.models import RepositoryPaths
from structural_engine.diff.generator import generate as generate_diff
from structural_engine.logs.generator import append as append_log
from structural_engine.parser.parser import parse
from structural_engine.reports.generator import generate as generate_report
from structural_engine.results import InitializationResult, StructuralStatusResult, SyncResult
from structural_engine.revisions.tracker import get_next_revision
from structural_engine.snapshot.generator import persist as persist_snapshot
from structural_engine.snapshot.loader import load as load_snapshot
from structural_engine.state.manager import StateManager

logger = structlog.get_logger(__name__)


class StructuralEngine:
    """Facade for the Structural Engine."""

    def __init__(self) -> None:
        self.state_manager = StateManager()

    def initialize(self, paths: RepositoryPaths) -> InitializationResult:
        """Initialize the structural state of the repository.

        Must only be called after the Runtime has scaffolded the
        .knowcode directory via ArtifactBuilder.

        Parameters
        ----------
        paths : RepositoryPaths
            Canonical paths.

        Returns
        -------
        InitializationResult
            Success and initial S-001 markers.
        """
        try:
            logger.info("engine.initialize.started")
            
            # 1. Parse current state
            snapshot = parse(paths)
            
            # 2. Persist initial snapshot
            revision_id = "S-001"
            snapshot_file = persist_snapshot(snapshot, revision_id, paths)
            
            # 3. Initialize state.yaml
            self.state_manager.initialize(paths)
            
            logger.info("engine.initialize.complete", revision=revision_id)
            return InitializationResult(
                success=True,
                structural_revision=revision_id,
                snapshot_file=snapshot_file,
                message="Structural Engine initialized successfully.",
            )
        except Exception as e:
            logger.exception("engine.initialize.failed")
            raise StructuralEngineFailure(f"Failed to initialize Engine: {e}") from e

    def status(self, paths: RepositoryPaths) -> StructuralStatusResult:
        """Get the current status of the engine.

        Parameters
        ----------
        paths : RepositoryPaths
            Canonical paths.

        Returns
        -------
        StructuralStatusResult
            Combined structural state and unowned passthrough fields.
        """
        try:
            state = self.state_manager.load(paths)
            
            # Read semantic_revision manually for the passthrough
            yaml = YAML()
            with open(paths.state_file, "r", encoding="utf-8") as f:
                raw_data = yaml.load(f)
            semantic_rev = raw_data.get("semantic_revision", "none")
            
            return StructuralStatusResult(
                initialized=True,
                structural_revision=state.structural_revision,
                semantic_revision=semantic_rev,
                current_snapshot=state.current_snapshot,
                latest_report=state.latest_report,
                last_sync=state.last_sync,
                repository_root=str(paths.repo_root),
            )
        except Exception as e:
            logger.exception("engine.status.failed")
            raise StructuralEngineFailure(f"Failed to read engine status: {e}") from e

    def sync(self, paths: RepositoryPaths) -> SyncResult:
        """Synchronize the engine with the current repository filesystem.

        Follows strict persistence ordering:
        Parse -> Diff -> Persist Snapshot -> Persist Report -> Persist Log -> Update State.

        Parameters
        ----------
        paths : RepositoryPaths
            Canonical paths.

        Returns
        -------
        SyncResult
            Outcome of the sync operation.
        """
        try:
            logger.info("engine.sync.started")
            
            # 1. Load previous state
            state = self.state_manager.load(paths)
            prev_snapshot = load_snapshot(state.current_snapshot, paths)
            if prev_snapshot is None:
                raise StructuralEngineFailure(f"Missing snapshot: {state.current_snapshot}")
                
            # 2. Parse current state
            curr_snapshot = parse(paths)
            
            # 3. Compute Diff
            diff = generate_diff(prev_snapshot, curr_snapshot)
            
            # 4. No-Change Shortcut
            if not diff.has_changes:
                logger.info("engine.sync.no_changes")
                return SyncResult(
                    success=True,
                    changes_detected=False,
                    structural_revision=state.structural_revision,
                    snapshot_file=state.current_snapshot,
                    report_file=state.latest_report,
                    affected_components=frozenset(),
                    message="No structural changes detected.",
                )
                
            # 5. Changes detected — execute strict persistence order
            next_rev = get_next_revision(state.structural_revision)
            
            # 5a. Persist Snapshot
            snapshot_file = persist_snapshot(curr_snapshot, next_rev, paths)
            
            # 5b. Persist Report
            report_file = generate_report(diff, next_rev, paths)
            
            # 5c. Persist Log
            append_log(next_rev, report_file, "SUCCESS", paths)
            
            # 5d. Update State (MUST BE LAST)
            self.state_manager.update(
                paths=paths,
                snapshot_id=snapshot_file,
                revision_id=next_rev,
                report_id=report_file,
            )
            
            logger.info("engine.sync.complete", next_revision=next_rev)
            return SyncResult(
                success=True,
                changes_detected=True,
                structural_revision=next_rev,
                snapshot_file=snapshot_file,
                report_file=report_file,
                affected_components=diff.affected_components,
                message=f"Sync complete: {next_rev}",
            )
            
        except Exception as e:
            logger.exception("engine.sync.failed")
            # Attempt to log failure if possible, but safely
            try:
                state = self.state_manager.load(paths)
                append_log(state.structural_revision, "none", f"FAILED: {e}", paths)
            except Exception:
                pass
            raise StructuralEngineFailure(f"Sync failed: {e}") from e
