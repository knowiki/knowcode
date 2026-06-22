"""Smoke test for Phase 4: StateManager."""

import shutil
import tempfile
from pathlib import Path

from runtime.repository.models import Repository, RepositoryPaths
from runtime.repository.paths import build_paths
from structural_engine.state.manager import StateManager
from structural_engine.state.models import StructuralState


def test_phase4():
    td = Path(tempfile.mkdtemp(dir="."))
    try:
        git_dir = td / ".git"
        git_dir.mkdir()
        knowcode_dir = td / ".knowcode"
        knowcode_dir.mkdir()
        
        repo = Repository(root=td.resolve(), git_dir=git_dir.resolve(), knowcode_dir=knowcode_dir.resolve(), agent_dir=(td / ".agent").resolve())
        paths = build_paths(repo)
        
        manager = StateManager()
        
        # 1. Initialize
        manager.initialize(paths)
        assert paths.state_file.is_file()
        
        # 2. Add human comments and a custom semantic revision
        state_content = paths.state_file.read_text(encoding="utf-8")
        
        modified_content = state_content.replace(
            "semantic_revision: none",
            "# Added by human\nsemantic_revision: v1.0.0 # Our first release!"
        )
        paths.state_file.write_text(modified_content, encoding="utf-8")
        
        # 3. Load
        state = manager.load(paths)
        assert isinstance(state, StructuralState)
        assert state.structural_revision == "S-001"
        assert state.current_snapshot == "S-001"
        assert state.latest_report == "none"
        print("[OK] State load successfully extracts StructuralState")
        
        # 4. Update
        manager.update(
            paths=paths,
            snapshot_id="S-002",
            revision_id="S-002",
            report_id="R-002.md",
        )
        
        # 5. Verify round-trip preservation
        final_content = paths.state_file.read_text(encoding="utf-8")
        
        assert "S-002" in final_content
        assert "R-002.md" in final_content
        
        assert "# Added by human" in final_content, "Human comment was stripped!"
        assert "semantic_revision: v1.0.0" in final_content, "semantic_revision was modified/stripped!"
        assert "# Our first release!" in final_content, "Inline comment was stripped!"
        
        print("[OK] State manager correctly updates structural fields while preserving comments and semantic_revision")
        
    finally:
        shutil.rmtree(str(td))


if __name__ == "__main__":
    test_phase4()
    print("\nAll Phase 4 smoke tests passed.")
