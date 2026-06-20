Here are the architectural determinations to resolve these ambiguities and unblock development.

---

### 1. `status` Method & Field Pass-Through

* **Decision:** `engine.status(paths)` must parse the full `state.yaml` and pass through both structural fields and the `semantic_revision` within the `StructuralStatusResult` object.
* **Reasoning:** The Runtime is responsible for presenting output to the user but is forbidden from reading `state.yaml` directly. The Engine acts as the steward of the file and must bubble up the complete state context so the Runtime can render a unified status screen.

### 2. `state.yaml` Template Elimination

* **Decision:** Omit `state.yaml.j2` from the Runtime entirely.
* **Reasoning:** The Runtime must have zero awareness of the `state.yaml` schema. `StateManager.initialize()` will programmatically construct the initial dictionary structure and commit it to disk during the `engine.initialize()` pipeline.

### 3. `ArtifactBuilder` Scope

* **Decision:** Yes, `BRAIN.md.j2` and `knowledge-maintenance.md.j2` constitute the complete initial template set for `ArtifactBuilder`.
* **Reasoning:** The primary job of `ArtifactBuilder` after the patch is to execute directory scaffolding (`mkdir()`) for the system layout and place basic human-facing documentation markdown files.

### 4. `structure_dir` vs `snapshots_dir`

* **Decision:** Yes, `snapshots_dir` is a direct child of `structure_dir`.
* **Path Definition:** * `structure_dir` = `.brain/structure/`
* `snapshots_dir` = `.brain/structure/snapshots/`



### 5. `entities_modified` Criteria

* **Decision:** An entity is classified as "modified" if its stable `id` matches an entity in the previous snapshot, but its line boundaries (`start_line` or `end_line`) differ.
* **Reasoning:** V1 keeps structural parsing factual and low-overhead. Signature changes, modifier tokens, and body contents are ignored for modification checks.

### 6. First Sync Behavior

* **Decision:** Correct. `engine.initialize()` establishes the baseline at `S-001`. The first subsequent `brain sync` reads `S-001` as the historical snapshot, parses the current directory state, computes the diff, and produces `S-002` if alterations are present.

### 7. No-Change Sync Behavior

* **Decision:** Implement **Option (b)**. If the computed current snapshot is structurally identical to the previous snapshot, the engine must shortcut the process.
* **Execution:** Return a `SyncResult` with `success=true`, but do not increment the revision ID, do not write a new snapshot file, and do not append a new log/report entry. The state remains on the current revision.

### 8. `affected_components` Derivation

* **Decision:** An affected component is derived as the name of the top-level directory within the repository root where a structural change occurred (e.g., for `src/auth.py::verify_token`, the affected component is `src`).
* **Reasoning:** Keeps derivation clean, predictable, and free of complex semantic guessing.

### 9. Tree-Sitter Dependency Strategy

* **Decision:** Use standard pip dependencies with the modern `tree-sitter` v0.22+ ecosystem bindings (e.g., `tree-sitter`, `tree-sitter-python`, `tree-sitter-typescript`, `tree-sitter-javascript`).
* **Reasoning:** Avoids bundling raw, uncompiled C/C++ source code directly inside the codebase while ensuring deterministic cross-platform tree-sitter execution.

### 10. Packaging Architecture

* **Decision:** Single workspace monorepo named `knowiki` using `uv` as the package manager. `runtime` and `structural_engine` must be implemented as distinct, isolated top-level packages/modules within the same codebase.
* **Reasoning:** This setup protects the strict import boundary restrictions without the overhead of managing and publishing multiple distinct upstream/downstream distribution artifacts during early-stage development.