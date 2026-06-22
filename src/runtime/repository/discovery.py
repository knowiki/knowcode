"""Repository discovery.

Locates the repository root by walking up from a starting directory
until a ``.git`` directory is found.

Algorithm
---------
::

    cwd → parent → parent → ... → .git found → repository root

Returns a ``Repository`` identity object.
Raises ``RepositoryNotFound`` if no ``.git`` ancestor exists.
"""

from __future__ import annotations

from pathlib import Path

from runtime.exceptions.errors import RepositoryNotFound
from runtime.repository.models import Repository


def discover_repository(start: Path | None = None) -> Repository:
    """Discover the enclosing git repository.

    Parameters
    ----------
    start : Path | None
        Directory to begin the upward search from.
        Defaults to ``Path.cwd()`` when *None*.

    Returns
    -------
    Repository
        Identity object anchoring all subsequent path derivation.

    Raises
    ------
    RepositoryNotFound
        If no ancestor directory contains a ``.git`` directory.
    """
    current = (start or Path.cwd()).resolve()

    # Walk upward through the filesystem hierarchy.
    while True:
        git_dir = current / ".git"
        if git_dir.is_dir():
            return Repository(
                root=current,
                git_dir=git_dir,
                knowcode_dir=current / ".knowcode",
                agent_dir=current / ".agent",
            )

        parent = current.parent
        if parent == current:
            # Reached filesystem root without finding .git.
            break
        current = parent

    raise RepositoryNotFound(
        f"No git repository found at or above: {start or Path.cwd()}"
    )
