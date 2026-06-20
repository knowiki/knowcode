"""State Manager.

Manages the persistent ``state.yaml`` file, maintaining strict stewardship
boundaries. Uses a round-trip YAML parser to preserve human comments
and unowned fields (like ``semantic_revision``).
"""

from __future__ import annotations

from datetime import datetime, timezone

from ruamel.yaml import YAML
import structlog

from runtime.repository.models import RepositoryPaths
from structural_engine.state.models import StructuralState

logger = structlog.get_logger(__name__)


class StateManager:
    """Manages read/write operations for state.yaml."""

    def __init__(self) -> None:
        """Initialize the state manager."""
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)

    def initialize(self, paths: RepositoryPaths) -> None:
        """Create the initial state.yaml file.

        Writes the default structural fields plus the baseline
        ``semantic_revision``.

        Parameters
        ----------
        paths : RepositoryPaths
            The canonical path contract.
        """
        initial_state = {
            "structural_revision": "S-001",
            "current_snapshot": "S-001",
            "latest_report": "none",
            "last_sync": datetime.now(timezone.utc).isoformat(),
            "semantic_revision": "none",
        }

        with open(paths.state_file, "w", encoding="utf-8") as f:
            self.yaml.dump(initial_state, f)

        logger.info(
            "state_manager.initialized",
            file=str(paths.state_file),
            structural_revision="S-001",
        )

    def load(self, paths: RepositoryPaths) -> StructuralState:
        """Load the structural state from disk.

        Parameters
        ----------
        paths : RepositoryPaths
            The canonical path contract.

        Returns
        -------
        StructuralState
            The strictly typed state subset owned by the Engine.
        """
        with open(paths.state_file, "r", encoding="utf-8") as f:
            data = self.yaml.load(f)

        state = StructuralState(
            structural_revision=data["structural_revision"],
            current_snapshot=data["current_snapshot"],
            latest_report=data["latest_report"],
            last_sync=datetime.fromisoformat(data["last_sync"]),
        )

        logger.debug(
            "state_manager.loaded",
            revision=state.structural_revision,
        )
        return state

    def update(
        self,
        paths: RepositoryPaths,
        snapshot_id: str,
        revision_id: str,
        report_id: str,
    ) -> None:
        """Update the structural state fields while preserving everything else.

        Performs a safe read-modify-write cycle. The ``semantic_revision``
        field and any human comments are explicitly preserved.

        Parameters
        ----------
        paths : RepositoryPaths
            The canonical path contract.
        snapshot_id : str
            The filename of the new snapshot.
        revision_id : str
            The new structural revision ID.
        report_id : str
            The filename of the new sync report.
        """
        # 1. Read existing
        with open(paths.state_file, "r", encoding="utf-8") as f:
            data = self.yaml.load(f)

        # 2. Modify only our fields
        data["structural_revision"] = revision_id
        data["current_snapshot"] = snapshot_id
        data["latest_report"] = report_id
        data["last_sync"] = datetime.now(timezone.utc).isoformat()

        # 3. Write back
        with open(paths.state_file, "w", encoding="utf-8") as f:
            self.yaml.dump(data, f)

        logger.info(
            "state_manager.updated",
            file=str(paths.state_file),
            revision=revision_id,
        )
