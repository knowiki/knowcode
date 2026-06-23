# Architectural Patch v1

## Contradiction Resolutions and Boundary Enforcements

---

# 1. Purpose

This document serves as an architectural patch to resolve contradictions and establish strict boundaries between the Global Runtime, the Structural Engine, and the Brain Artifact.

Where contradictions exist, this document supersedes previous implementation plans.

---

# 2. state.yaml Initialization Patch

## Contradiction
The Runtime's `ArtifactBuilder` and the Engine's `StateManager` both claimed responsibility for creating `state.yaml`.

## Resolution
Initialization responsibilities are strictly divided by domain:
* **Runtime:** Owns directory creation (`mkdir()`). It has zero knowledge of the `state.yaml` schema.
* **Structural Engine:** Owns structural state creation (`state.yaml`).
* **Humans + AI:** Own semantic artifact creation.

## Verifiable Criteria
* The Runtime `templates/` directory contains no `state.yaml.j2` file.
* The `ArtifactBuilder` performs no template rendering or file writing for `state.yaml`.
* `StateManager.initialize()` performs the initial `state.yaml` file creation.

---

# 3. Shared State Ownership Patch

## Contradiction
The `StateManager` ignored `semantic_revision`, while the Runtime was forbidden from modifying semantic knowledge, leaving `semantic_revision` as an unmanaged orphan.

## Resolution
There is only one synchronization authority: `state.yaml`. Ownership within this file is divided strictly by field, rather than by creating separate state files.

* **Structural Engine Owns:**
  * `current_snapshot`
  * `structural_revision`
  * `latest_report`
  * `last_sync`
* **Humans / AI Agents Own:**
  * `semantic_revision`

The `StateManager` acts as a partial steward. It must read the whole file, update only its owned fields, and write the file back without touching or dropping unowned fields.

## Verifiable Criteria
* `StateManager` load and update methods preserve the `semantic_revision` field.
* Semantic updates to `state.yaml` are performed exclusively by humans or AI agents.

---

# 4. Canonical RepositoryPaths Patch

## Contradiction
The Runtime expected a 9-field `RepositoryPaths` object, while the Structural Engine expected a 6-field object, breaking the claim of a shared contract.

## Resolution
There is exactly one canonical `RepositoryPaths` object used across the entire ecosystem. The Structural Engine will accept the full object and simply ignore the fields it does not need.

## Verifiable Criteria
* `RepositoryPaths` contains exactly 9 fields:
  * `repo_root`
  * `brain_root`
  * `structure_dir`
  * `snapshots_dir`
  * `reports_dir`
  * `logs_dir`
  * `knowledge_dir`
  * `state_file`
  * `brain_file`
* The Structural Engine accepts this unified object without requiring an intermediate translation or mapping layer.

---

# 5. Status Authority Patch

## Contradiction
The Runtime's `status_service` read `state.yaml` directly, violating the rule that the Structural Engine manages structural state access.

## Resolution
The Runtime orchestrates; the Engine manages state. The Runtime must not bypass the Engine to read the filesystem for status. 

## Verifiable Criteria
* The `StructuralEngine` exposes exactly three public methods:
  * `initialize(paths)`
  * `sync(paths)`
  * `status(paths)`
* The `status(paths)` method returns a `StructuralStatusResult` object.
* The Runtime's `status_service.py` performs zero file I/O operations targeting `state.yaml`, instead delegating entirely to `engine.status(paths)`.

---

# 6. The Authority Hierarchy Patch

## Contradiction
The `StateManager` claimed to be the ultimate synchronization authority, conflicting with the Brain Artifact specification which dictates that `state.yaml` itself is the authority. 

## Resolution
The system operates under a strict, cascading chain of truth. The `StateManager` is merely a steward of the structural fields within the authoritative file.

## The Absolute Authority Hierarchy
1. **Repository:** The ultimate physical reality.
2. **Brain Artifact:** The reflection of that reality.
3. **`state.yaml`:** The definitive synchronization authority.
4. **`StateManager`:** The steward of structural fields within `state.yaml`.
5. **Structural Engine:** The deterministic calculator of those fields.
6. **Runtime:** The orchestrator that sets these processes in motion.