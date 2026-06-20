"""Smoke test for Phase 2B: Tree-sitter extraction and call resolution."""

import shutil
import tempfile
from pathlib import Path

from runtime.repository.discovery import discover_repository
from runtime.repository.paths import build_paths
from structural_engine.parser.models import EntityType, RelationshipType
from structural_engine.parser.parser import parse

def create_mock_repo(base_dir: Path):
    """Creates a small mock repository with python, ts, and js files."""
    (base_dir / ".git").mkdir()
    
    src = base_dir / "src"
    src.mkdir()
    
    # Python file: classes, inheritance, imports, and calls
    py_code = """
import os
from sys import path

class BaseNode:
    pass

class ASTNode(BaseNode):
    def visit(self):
        print(self)
        self.traverse()

def process_tree():
    node = ASTNode()
    node.visit()
"""
    (src / "tree.py").write_text(py_code, encoding="utf-8")
    
    # TypeScript file: interfaces, classes, imports
    ts_code = """
import { resolve } from "path";

interface Logger {
    log(msg: string): void;
}

class ConsoleLogger implements Logger {
    log(msg: string) {
        console.log(msg);
    }
}

function init() {
    let logger = new ConsoleLogger();
    logger.log("init");
}
"""
    (src / "logger.ts").write_text(ts_code, encoding="utf-8")

    # JavaScript file
    js_code = """
import { init } from "./logger";

function main() {
    init();
}
"""
    (src / "main.js").write_text(js_code, encoding="utf-8")

def test_phase2b():
    td = Path(tempfile.mkdtemp(dir="."))
    try:
        create_mock_repo(td)
        repo = discover_repository(td)
        paths = build_paths(repo)
        
        # Run full parser pipeline
        snapshot = parse(paths)
        
        # 1. Check Sorting Contract
        # Entities sorted by ID
        entity_ids = [e.id for e in snapshot.entities]
        assert entity_ids == sorted(entity_ids), "Entities are not sorted by ID"
        
        # Relationships sorted by (source, target, type)
        rel_keys = [(r.source_id, r.target_id, r.type.name) for r in snapshot.relationships]
        assert rel_keys == sorted(rel_keys), "Relationships are not sorted properly"

        print("[OK] Deterministic sorting verified")

        # 2. Check Entities
        # We should have files, classes, interfaces, functions, and methods
        types_found = {e.type for e in snapshot.entities}
        assert EntityType.FILE in types_found
        assert EntityType.CLASS in types_found
        assert EntityType.INTERFACE in types_found
        assert EntityType.FUNCTION in types_found
        assert EntityType.METHOD in types_found
        
        # Specific check for Python extraction
        ast_node = next((e for e in snapshot.entities if e.name == "ASTNode"), None)
        assert ast_node is not None
        assert ast_node.type == EntityType.CLASS
        
        visit_method = next((e for e in snapshot.entities if e.name == "visit"), None)
        assert visit_method is not None
        assert visit_method.type == EntityType.METHOD
        
        print("[OK] Entity extraction verified for multiple languages")
        
        # 3. Check Relationships
        rel_types = {r.type for r in snapshot.relationships}
        assert RelationshipType.CONTAINS in rel_types
        assert RelationshipType.IMPORTS in rel_types
        assert RelationshipType.INHERITS in rel_types
        assert RelationshipType.IMPLEMENTS in rel_types
        assert RelationshipType.CALLS in rel_types
        
        # Specific relationship checks
        # ASTNode INHERITS BaseNode
        inherits_rel = next((r for r in snapshot.relationships if r.type == RelationshipType.INHERITS and "ASTNode" in r.source_id and "BaseNode" in r.target_id), None)
        assert inherits_rel is not None
        
        # ConsoleLogger IMPLEMENTS Logger
        impl_rel = next((r for r in snapshot.relationships if r.type == RelationshipType.IMPLEMENTS and "ConsoleLogger" in r.source_id and "Logger" in r.target_id), None)
        assert impl_rel is not None
        
        print("[OK] Relationship extraction verified (CONTAINS, IMPORTS, INHERITS, IMPLEMENTS)")
        
        # 4. Check Call Resolution
        # process_tree calls visit
        calls_visit = next((r for r in snapshot.relationships if r.type == RelationshipType.CALLS and "process_tree" in r.source_id and "visit" in r.target_id), None)
        assert calls_visit is not None
        
        # init calls log
        calls_log = next((r for r in snapshot.relationships if r.type == RelationshipType.CALLS and "init" in r.source_id and "log" in r.target_id), None)
        assert calls_log is not None
        
        print("[OK] Conservative call resolution verified (CALLS)")
        
    finally:
        shutil.rmtree(str(td))

if __name__ == "__main__":
    test_phase2b()
    print("\nAll Phase 2B smoke tests passed.")
