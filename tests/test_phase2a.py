"""Smoke test for Phase 2A: Parser models, discovery, and public interface."""

import tempfile
import shutil
from pathlib import Path

from runtime.repository.models import RepositoryPaths
from runtime.repository.paths import build_paths
from runtime.repository.models import Repository

from structural_engine.parser.models import (
    Entity,
    EntityType,
    Relationship,
    RelationshipType,
    Language,
    FileInfo,
    RawCall,
    StructuralSnapshot,
    EXTENSION_LANGUAGE_MAP,
)
from structural_engine.parser.discovery import discover_files, detect_language, IGNORED_DIRECTORIES
from structural_engine.parser.parser import parse


def test_models():
    """Verify model construction and immutability."""
    # Entity
    e = Entity(
        id="src/auth.py::verify_token",
        type=EntityType.FUNCTION,
        name="verify_token",
        path="src/auth.py",
        parent_id="src/auth.py",
        start_line=10,
        end_line=25,
    )
    assert e.id == "src/auth.py::verify_token"
    assert e.type == EntityType.FUNCTION

    # Frozen check
    try:
        e.name = "other"  # type: ignore[misc]
        assert False, "Entity should be frozen"
    except AttributeError:
        pass

    # Relationship
    r = Relationship(
        source_id="src/main.py::handle_request",
        target_id="src/auth.py::verify_token",
        type=RelationshipType.CALLS,
    )
    assert r.type == RelationshipType.CALLS

    # StructuralSnapshot
    snap = StructuralSnapshot(entities=(e,), relationships=(r,))
    assert len(snap.entities) == 1
    assert len(snap.relationships) == 1

    # Empty snapshot
    empty = StructuralSnapshot()
    assert len(empty.entities) == 0
    assert len(empty.relationships) == 0

    # RawCall
    rc = RawCall(
        caller_id="src/main.py::handle_request",
        target_name="verify_token",
        source_file="src/main.py",
        line=42,
    )
    assert rc.target_name == "verify_token"

    print("[OK] All parser models construct correctly and are frozen")


def test_language_detection():
    """Verify extension-to-language mapping."""
    assert detect_language(Path("foo.py")) == Language.PYTHON
    assert detect_language(Path("bar.ts")) == Language.TYPESCRIPT
    assert detect_language(Path("baz.tsx")) == Language.TYPESCRIPT
    assert detect_language(Path("qux.js")) == Language.JAVASCRIPT
    assert detect_language(Path("readme.md")) is None
    assert detect_language(Path("Makefile")) is None
    assert detect_language(Path("foo.PY")) == Language.PYTHON  # case-insensitive

    print("[OK] Language detection works for all supported extensions")


def test_ignored_directories():
    """Verify ignored directory set contains required entries."""
    required = {".git", ".knowcode", "node_modules", "dist", "build", "target", "venv"}
    assert required.issubset(IGNORED_DIRECTORIES)

    print("[OK] All required directories are in the ignore set")


def test_file_discovery():
    """Verify discovery walks correctly, ignores dirs, and detects languages."""
    td = Path(tempfile.mkdtemp(dir="."))
    try:
        # Build a mock repo structure
        (td / "src").mkdir()
        (td / "src" / "auth.py").write_text("# auth", encoding="utf-8")
        (td / "src" / "main.py").write_text("# main", encoding="utf-8")
        (td / "src" / "utils.ts").write_text("// utils", encoding="utf-8")
        (td / "src" / "App.tsx").write_text("// app", encoding="utf-8")
        (td / "src" / "index.js").write_text("// index", encoding="utf-8")
        (td / "src" / "readme.md").write_text("# readme", encoding="utf-8")  # unsupported

        # Ignored directories — should be skipped
        (td / "node_modules").mkdir()
        (td / "node_modules" / "lib.js").write_text("// lib", encoding="utf-8")
        (td / ".git").mkdir()
        (td / ".git" / "config").write_text("[core]", encoding="utf-8")
        (td / ".knowcode").mkdir()
        (td / ".knowcode" / "state.yaml").write_text("rev: 1", encoding="utf-8")
        (td / "venv").mkdir()
        (td / "venv" / "activate.py").write_text("# venv", encoding="utf-8")

        files = discover_files(td)

        # Should find exactly 5 supported files
        assert len(files) == 5, f"Expected 5 files, got {len(files)}: {[f.relative_path for f in files]}"

        # Verify ordering is deterministic (sorted by relative_path)
        paths = [f.relative_path for f in files]
        assert paths == sorted(paths), f"Files not sorted: {paths}"

        # Verify relative paths use forward slashes
        for f in files:
            assert "\\" not in f.relative_path, f"Backslash in path: {f.relative_path}"

        # Verify ignored dirs were actually skipped
        ignored_paths = {"node_modules/lib.js", ".git/config", ".knowcode/state.yaml", "venv/activate.py"}
        discovered_paths = {f.relative_path for f in files}
        assert ignored_paths.isdisjoint(discovered_paths), "Ignored files leaked through"

        # Verify languages
        py_files = [f for f in files if f.language == Language.PYTHON]
        ts_files = [f for f in files if f.language == Language.TYPESCRIPT]
        js_files = [f for f in files if f.language == Language.JAVASCRIPT]
        assert len(py_files) == 2
        assert len(ts_files) == 2  # .ts + .tsx
        assert len(js_files) == 1

        print("[OK] File discovery: 5 files found, ignored dirs skipped, languages correct")

    finally:
        shutil.rmtree(str(td))


def test_parse_stub():
    """Verify the public parse() function runs the pipeline and returns a snapshot."""
    td = Path(tempfile.mkdtemp(dir="."))
    try:
        (td / ".git").mkdir()
        (td / "src").mkdir()
        (td / "src" / "main.py").write_text("def main(): pass", encoding="utf-8")

        repo = Repository(root=td.resolve(), git_dir=(td / ".git").resolve(), knowcode_dir=(td / ".knowcode").resolve(), agent_dir=(td / ".agent").resolve())
        paths = build_paths(repo)

        snapshot = parse(paths)

        assert isinstance(snapshot, StructuralSnapshot)
        # Phase 2A stub has been implemented; it parses main.py and finds the file and the main function.
        assert len(snapshot.entities) == 2
        assert len(snapshot.relationships) == 1

        print("[OK] parse() returns empty StructuralSnapshot (Phase 2A stub)")

    finally:
        shutil.rmtree(str(td))


if __name__ == "__main__":
    test_models()
    test_language_detection()
    test_ignored_directories()
    test_file_discovery()
    test_parse_stub()
    print("\nAll Phase 2A smoke tests passed.")
