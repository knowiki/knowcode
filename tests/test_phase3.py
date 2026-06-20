"""Smoke test for Phase 3: ArtifactBuilder."""

import shutil
import tempfile
from pathlib import Path

from runtime.repository.models import Repository, RepositoryPaths
from runtime.repository.paths import build_paths
from runtime.artifact.builder import ArtifactBuilder

def test_phase3():
    td = Path(tempfile.mkdtemp(dir="."))
    try:
        # Mock repository roots
        git_dir = td / ".git"
        git_dir.mkdir()
        
        repo = Repository(root=td.resolve(), git_dir=git_dir.resolve(), brain_dir=(td / ".brain").resolve())
        paths = build_paths(repo)
        
        # Run builder
        builder = ArtifactBuilder(paths)
        builder.build()
        
        # Verify Directories
        assert paths.brain_root.is_dir()
        assert paths.structure_dir.is_dir()
        assert paths.snapshots_dir.is_dir()
        assert paths.reports_dir.is_dir()
        assert paths.logs_dir.is_dir()
        assert paths.knowledge_dir.is_dir()
        
        # Verify specific knowledge subdirectories
        assert (paths.knowledge_dir / "architecture").is_dir()
        assert (paths.knowledge_dir / "decisions").is_dir()
        assert (paths.knowledge_dir / "constraints").is_dir()
        assert (paths.knowledge_dir / "conventions").is_dir()
        assert (paths.knowledge_dir / "components").is_dir()
        
        print("[OK] Directory structure correctly scaffolded")
        
        # Verify Templates
        assert paths.brain_file.is_file()
        brain_text = paths.brain_file.read_text(encoding="utf-8")
        assert td.resolve().name in brain_text, "Project name not templated into BRAIN.md"
        assert "Runtime:" in brain_text
        assert "Structural Engine:" in brain_text
        
        km_file = paths.knowledge_dir / "knowledge-maintenance.md"
        assert km_file.is_file()
        km_text = km_file.read_text(encoding="utf-8")
        assert "Knowledge Maintenance Protocol" in km_text
        
        print("[OK] Templates correctly rendered with variables")
        
        # Verify State Management boundary
        assert not paths.state_file.exists(), "ArtifactBuilder MUST NOT create state.yaml"
        
        print("[OK] ZERO state awareness boundary verified")
        
    finally:
        shutil.rmtree(str(td))

if __name__ == "__main__":
    test_phase3()
    print("\nAll Phase 3 smoke tests passed.")
