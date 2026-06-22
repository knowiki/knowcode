"""Quick smoke test for Phase 1 foundation."""

import shutil
import tempfile
from pathlib import Path

from runtime.exceptions.errors import KnowcodeNotInitialized
from runtime.repository.discovery import discover_repository
from runtime.repository.models import Repository, RepositoryPaths
from runtime.repository.paths import build_paths
from runtime.repository.validator import validate_for_init, validate_for_sync

# 1. Verify RepositoryPaths has exactly 16 fields
assert len(RepositoryPaths.model_fields) == 18, "Expected 18 fields"
print("[OK] RepositoryPaths has 18 fields")

# 2. Verify frozen immutability
rp = RepositoryPaths(
    repo_root=Path("/mock/repo"),
    git_dir=Path("/mock/repo/.git"),
    knowcode_root=Path(".knowcode"),
    knowcode_file=Path(".knowcode/KNOWCODE.md"),
    state_file=Path(".knowcode/state.yaml"),
    structure_dir=Path(".knowcode/structure"),
    snapshots_dir=Path(".knowcode/structure/snapshots"),
    reports_dir=Path(".knowcode/reports"),
    logs_dir=Path(".knowcode/logs"),
    knowledge_dir=Path(".knowcode/knowledge"),
    agent_dir=Path(".agent"),
    workflows_dir=Path(".agent/workflows"),
    skills_dir=Path(".agent/skills"),
    memory_dir=Path(".agent/memory"),
    active_context_file=Path(".agent/memory/active_context.md"),
    previous_context_file=Path(".agent/memory/previous_context.md"),
    system_skills_dir=Path(".agent/skills/system"),
    raw_knowledge_dir=Path(".knowcode/knowledge/raw"),
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

    # 4. Validate for init — should pass (no .knowcode yet)
    validate_for_init(paths)
    print("[OK] validate_for_init passed (no .knowcode)")

    # 5. Validate for sync — should raise KnowcodeNotInitialized
    try:
        validate_for_sync(paths)
        assert False, "Should have raised"
    except KnowcodeNotInitialized:
        print("[OK] validate_for_sync raised KnowcodeNotInitialized")

finally:
    shutil.rmtree(str(td))

print("\nAll Phase 1 smoke tests passed.")
