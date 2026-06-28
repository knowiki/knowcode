"""Smoke test for Phase 6: Engine Facade & CLI."""

import shutil
import tempfile
import os
from pathlib import Path
from typer.testing import CliRunner

from runtime.cli.app import app

runner = CliRunner()


def test_phase6():
    td = Path(tempfile.mkdtemp(dir="."))
    old_cwd = os.getcwd()
    
    try:
        os.chdir(td)
        
        # Mock git repo
        (Path(".git")).mkdir()
        src = Path("src")
        src.mkdir()
        (src / "main.py").write_text("def main(): pass", encoding="utf-8")
        
        # 1. Test init
        result = runner.invoke(app, ["."])
        if result.exit_code != 0:
            print("INIT FAILED STDOUT:", result.stdout)
            if result.exception:
                print("INIT EXCEPTION:", result.exception)
        assert result.exit_code == 0
        assert "Structural Engine initialized successfully" in result.stdout
        assert "S-001" in result.stdout
        print("[OK] knowcode . (Init)")
        
        # 2. Test status
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "Initialized" in result.stdout
        assert "Yes" in result.stdout
        assert "S-001" in result.stdout
        assert "none" in result.stdout  # semantic_revision
        print("[OK] knowcode status")
        
        # 3. Test sync (No Changes)
        result = runner.invoke(app, ["sync"])
        assert result.exit_code == 0
        assert "No structural changes detected" in result.stdout
        print("[OK] knowcode sync (No Changes shortcut)")
        
        # 4. Modify code to trigger a sync
        (src / "main.py").write_text("def main():\n    pass\n", encoding="utf-8")
        
        # 5. Test sync (Changes detected)
        result = runner.invoke(app, ["sync"])
        assert result.exit_code == 0
        assert "Sync Complete" in result.stdout
        assert "S-002" in result.stdout
        assert "src" in result.stdout  # Affected component
        print("[OK] knowcode sync (Changes detected -> S-002)")
        
        # 6. Test status again
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "S-002" in result.stdout
        print("[OK] knowcode status (Post-sync verification)")

        # 7. Test ingest-semantic (empty inbox)
        result = runner.invoke(app, ["ingest-semantic", "."])
        assert result.exit_code == 0
        assert "Inbox is already empty." in result.stdout
        print("[OK] knowcode ingest-semantic (No files to ingest)")

        # 8. Test ingest-semantic (one file)
        raw_dir = Path(".knowcode/knowledge/raw")
        raw_dir.mkdir(parents=True, exist_ok=True)
        temp_raw_file = raw_dir / "legacy_doc.md"
        temp_raw_file.write_text("Legacy doc content", encoding="utf-8")

        result = runner.invoke(app, ["ingest-semantic", "."])
        assert result.exit_code == 0
        assert "Ingested 1 file(s)." in result.stdout
        assert not temp_raw_file.exists()
        print("[OK] knowcode ingest-semantic (Successfully ingested 1 file)")
        
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(str(td))


if __name__ == "__main__":
    test_phase6()
    print("\nAll Phase 6 smoke tests passed.")
