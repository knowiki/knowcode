"""File discovery and language detection.

Recursively walks the repository starting from ``repo_root``, discovers
source files in supported languages, and filters out ignored directories.

This module is stateless and side-effect free.  It performs no writes,
no persistence, and no Brain-awareness.

Ignored Directories
-------------------
::

    .git, .knowcode, node_modules, dist, build, target, venv,
    .venv, __pycache__, .mypy_cache, .pytest_cache, .tox,
    .eggs, .idea, .vscode, .vs

Supported Extensions
--------------------
::

    .py   → PYTHON
    .ts   → TYPESCRIPT
    .tsx  → TYPESCRIPT
    .js   → JAVASCRIPT
"""

from __future__ import annotations

from pathlib import Path
import pathspec

from structural_engine.parser.models import (
    EXTENSION_LANGUAGE_MAP,
    FileInfo,
    Language,
)

# Directories to skip during recursive walk.
# This set is intentionally broad to avoid traversing large vendored
# or generated trees that have no structural relevance.
IGNORED_DIRECTORIES: frozenset[str] = frozenset(
    {
        ".git",
        ".knowcode",
        ".agent",
        "node_modules",
        "dist",
        "build",
        "target",
        "venv",
        ".venv",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".tox",
        ".eggs",
        ".idea",
        ".vscode",
        ".vs",
        ".next",
        ".nuxt",
        ".svelte-kit",
        "out",
        "coverage",
        ".cache",
        "tmp",
        "temp",
        ".yarn",
        "vendor",
        ".serverless",
    }
)


def discover_files(repo_root: Path) -> list[FileInfo]:
    """Walk the repository and discover all supported source files.

    Parameters
    ----------
    repo_root : Path
        Absolute path to the repository root.

    Returns
    -------
    list[FileInfo]
        Discovered files sorted by ``relative_path`` for determinism.
        Files in ignored directories are excluded.
        Files with unsupported extensions are excluded.
    """
    discovered: list[FileInfo] = []

    for item in _walk_filtered(repo_root):
        if not item.is_file():
            continue

        language = detect_language(item)
        if language is None:
            continue

        # Relative path always uses forward slashes for cross-platform
        # determinism (entity IDs depend on this).
        relative = item.relative_to(repo_root).as_posix()

        discovered.append(
            FileInfo(
                absolute_path=item,
                relative_path=relative,
                language=language,
            )
        )

    # Sort for deterministic output — entity ID generation depends on
    # a stable file ordering.
    discovered.sort(key=lambda f: f.relative_path)
    return discovered


def detect_language(file_path: Path) -> Language | None:
    """Detect the programming language of a file by extension.

    Parameters
    ----------
    file_path : Path
        Path to the source file.

    Returns
    -------
    Language | None
        The detected language, or *None* if the extension is not
        supported.
    """
    return EXTENSION_LANGUAGE_MAP.get(file_path.suffix.lower())


def _walk_filtered(root: Path) -> list[Path]:
    """Recursively collect all file paths, skipping ignored directories.

    Uses ``Path.iterdir()`` + manual recursion instead of ``os.walk()``
    to have fine-grained control over directory filtering before descent.

    Parameters
    ----------
    root : Path
        Directory to walk.

    Returns
    -------
    list[Path]
        All non-ignored file paths under *root*.
    """
    results: list[Path] = []
    
    # Compile .gitignore if it exists
    gitignore_path = root / ".gitignore"
    spec = None
    if gitignore_path.is_file():
        try:
            with gitignore_path.open("r", encoding="utf-8") as f:
                spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
        except Exception:
            pass
            
    _walk_recursive(root, results, root, spec)
    return results


def _walk_recursive(directory: Path, accumulator: list[Path], repo_root: Path, spec: pathspec.PathSpec | None) -> None:
    """Internal recursive walker.

    Parameters
    ----------
    directory : Path
        Current directory being walked.
    accumulator : list[Path]
        Mutable list collecting discovered file paths.
    repo_root : Path
        The root of the repository for calculating relative paths.
    spec : pathspec.PathSpec | None
        Compiled gitignore spec.
    """
    try:
        entries = sorted(directory.iterdir(), key=lambda p: p.name)
    except PermissionError:
        # Skip directories we can't read.
        return

    for entry in entries:
        # Compute posix relative path for gitignore matching
        relative_path = entry.relative_to(repo_root).as_posix()
        
        if entry.is_dir():
            # Match directories with a trailing slash for proper gitignore semantics
            if spec and spec.match_file(relative_path + "/"):
                continue
                
            if entry.name not in IGNORED_DIRECTORIES:
                _walk_recursive(entry, accumulator, repo_root, spec)
        elif entry.is_file():
            if spec and spec.match_file(relative_path):
                continue
            
            # Skip minified and bundled files
            name = entry.name.lower()
            if name.endswith(".min.js") or name.endswith(".min.ts") or name.endswith(".bundle.js"):
                continue
                
            accumulator.append(entry)
