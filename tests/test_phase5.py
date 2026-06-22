"""Smoke test for Phase 5: Generators and Persisters."""

import shutil
import tempfile
from pathlib import Path

from runtime.repository.models import Repository, RepositoryPaths
from runtime.repository.paths import build_paths
from structural_engine.revisions.tracker import get_next_revision
from structural_engine.snapshot.generator import persist as persist_snapshot
from structural_engine.snapshot.loader import load as load_snapshot
from structural_engine.diff.generator import generate as generate_diff
from structural_engine.reports.generator import generate as generate_report
from structural_engine.logs.generator import append as append_log
from structural_engine.parser.models import Entity, EntityType, Relationship, RelationshipType, StructuralSnapshot


def test_phase5():
    td = Path(tempfile.mkdtemp(dir="."))
    try:
        # Mock paths
        git_dir = td / ".git"
        git_dir.mkdir()
        knowcode_dir = td / ".knowcode"
        knowcode_dir.mkdir()
        
        repo = Repository(root=td.resolve(), git_dir=git_dir.resolve(), knowcode_dir=knowcode_dir.resolve(), agent_dir=(td / ".agent").resolve())
        paths = build_paths(repo)
        
        # Ensure directories exist
        paths.snapshots_dir.mkdir(parents=True, exist_ok=True)
        paths.reports_dir.mkdir(parents=True, exist_ok=True)
        paths.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Tracker
        assert get_next_revision("S-014") == "S-015"
        assert get_next_revision("invalid") == "S-001"
        print("[OK] Revision tracker logic")
        
        # 2. Snapshot Persistence & Loading
        e1 = Entity(id="src/auth.py", type=EntityType.FILE, name="auth.py", path="src/auth.py", parent_id="src", start_line=1, end_line=10)
        r1 = Relationship(source_id="src", target_id="src/auth.py", type=RelationshipType.CONTAINS)
        
        snap1 = StructuralSnapshot(entities=(e1,), relationships=(r1,))
        filename1 = persist_snapshot(snap1, "S-014", paths)
        
        assert filename1 == "S-014.json"
        assert (paths.snapshots_dir / filename1).is_file()
        
        loaded_snap1 = load_snapshot("S-014", paths)
        assert loaded_snap1 is not None
        assert len(loaded_snap1.entities) == 1
        assert loaded_snap1.entities[0].id == "src/auth.py"
        assert loaded_snap1.entities[0].type == EntityType.FILE
        assert loaded_snap1.relationships[0].type == RelationshipType.CONTAINS
        print("[OK] Snapshot persistence (JSON serialization & Enum unwrapping/wrapping)")
        
        # 3. Diff Generator
        # Let's shift line numbers of e1, and add e2
        e1_mod = Entity(id="src/auth.py", type=EntityType.FILE, name="auth.py", path="src/auth.py", parent_id="src", start_line=1, end_line=15)
        e2 = Entity(id="tests/test_auth.py", type=EntityType.FILE, name="test_auth.py", path="tests/test_auth.py", parent_id="tests", start_line=1, end_line=5)
        r2 = Relationship(source_id="tests", target_id="tests/test_auth.py", type=RelationshipType.CONTAINS)
        
        snap2 = StructuralSnapshot(entities=(e1_mod, e2), relationships=(r1, r2))
        
        diff = generate_diff(snap1, snap2)
        assert diff.has_changes
        assert len(diff.entities_modified) == 1
        assert diff.entities_modified[0].id == "src/auth.py"
        assert len(diff.entities_added) == 1
        assert diff.entities_added[0].id == "tests/test_auth.py"
        assert len(diff.entities_removed) == 0
        assert len(diff.relationships_added) == 1
        
        # Verify affected components correctly parsed top-level dirs
        assert "src" in diff.affected_components
        assert "tests" in diff.affected_components
        print("[OK] Diff generation (ID-based comparison & affected components derivation)")
        
        # 4. Report Generator
        report_file = generate_report(diff, "S-015", paths)
        assert report_file == "R-015.md"
        assert (paths.reports_dir / report_file).is_file()
        
        report_content = (paths.reports_dir / report_file).read_text(encoding="utf-8")
        assert "S-015" in report_content
        assert "`src/`" in report_content
        assert "`tests/`" in report_content
        assert "src/auth.py" in report_content
        print("[OK] Report generation (Markdown diff summary)")
        
        # 5. Log Generator
        append_log("S-015", "R-015.md", "SUCCESS", paths)
        log_file = paths.logs_dir / "sync.md"
        assert log_file.is_file()
        log_content = log_file.read_text(encoding="utf-8")
        assert "S-015" in log_content
        assert "R-015.md" in log_content
        assert "SUCCESS" in log_content
        print("[OK] Log generation (timestamped append)")
        
    finally:
        shutil.rmtree(str(td))


if __name__ == "__main__":
    test_phase5()
    print("\nAll Phase 5 smoke tests passed.")
