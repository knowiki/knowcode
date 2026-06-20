"""Quick smoke test for Phase 1 foundation."""

import shutil
import tempfile
from pathlib import Path

from runtime.exceptions.errors import BrainNotInitialized
from runtime.repository.discovery import discover_repository
from runtime.repository.models import Repository, RepositoryPaths
from runtime.repository.paths import build_paths
from runtime.repository.validator import validate_for_init, validate_for_sync

# 1. Verify RepositoryPaths has exactly 9 fields
assert len(RepositoryPaths.model_fields) == 9, "Expected 9 fields"
print("[OK] RepositoryPaths has 9 fields")

# 2. Verify frozen immutability
rp = RepositoryPaths(
    repo_root=Path("."),
    brain_root=Path(".brain"),
    structure_dir=Path(".brain/structure"),
    snapshots_dir=Path(".brain/structure/snapshots"),
    reports_dir=Path(".brain/reports"),
    logs_dir=Path(".brain/logs"),
    knowledge_dir=Path(".brain/knowledge"),
    state_file=Path(".brain/state.yaml"),
    brain_file=Path(".brain/BRAIN.md"),
)
try:
    rp.repo_root = Path("/other")  # type: ignore[misc]
    assert False, "Should have raised"
except Exception:
    print("[OK] RepositoryPaths is immutable (frozen)")

# 3. Test discovery + path building
td = Path(tempfile.mkdtemp(dir="."))
try:
    (td / ".git").mkdir()
    repo = discover_repository(td)
    assert repo.root == td.resolve()
    print(f"[OK] discover_repository found root: {repo.root.name}")

    paths = build_paths(repo)
    assert paths.snapshots_dir == paths.structure_dir / "snapshots"
    print("[OK] build_paths: snapshots_dir is child of structure_dir")

    # 4. Validate for init — should pass (no .brain yet)
    validate_for_init(paths)
    print("[OK] validate_for_init passed (no .brain)")

    # 5. Validate for sync — should raise BrainNotInitialized
    try:
        validate_for_sync(paths)
        assert False, "Should have raised"
    except BrainNotInitialized:
        print("[OK] validate_for_sync raised BrainNotInitialized")

finally:
    shutil.rmtree(str(td))

print("\nAll Phase 1 smoke tests passed.")
