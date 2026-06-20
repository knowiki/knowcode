# Structural Engine Implementation Plan

## Architecture, Components, Initialization and Cooperation with the Runtime

---

# 1. Purpose

The Structural Engine is the implementation of the Structural Layer inside Knowiki.

Its responsibility is deterministic structural computation.

It establishes structural truth, preserves structural history, and records structural evolution.

The Structural Engine answers two questions:

> What does the repository look like right now?

and

> How has the repository changed since the previous revision?

It does not answer:

* Why does the architecture exist?
* What constraints should be preserved?
* What conventions should contributors follow?

Those responsibilities belong to semantic understanding.

---

# 2. Architectural Philosophy

The Structural Engine behaves similarly to Git.

It owns structural history.

It does not own understanding.

It computes facts rather than interpretations.

The repository remains the ultimate authority.

The Structural Engine merely establishes structural reality.

Given identical repository states:

```text
repo@commit_x
```

the Structural Engine must always produce:

```text
snapshot_x
```

regardless of:

* machine
* user
* operating system
* runtime state
* previous history

Determinism is its most important property.

---

# 3. Architectural Position

```text
User

↓

Runtime

↓

Structural Engine

↓

Brain Artifact

↓

Humans + AI Agents
```

Ownership:

Runtime

↓

orchestration

Structural Engine

↓

structural computation

Brain Artifact

↓

persistent state

Humans + Agents

↓

semantic understanding

These ownership boundaries must never be violated.

---

# 4. Public Interface

The Structural Engine exposes exactly two operations.

```python
initialize(paths)

sync(paths)
```

Initialization occurs during:

```bash
brain .
```

Synchronization occurs during:

```bash
brain sync
```

No other public operations exist.

Everything else remains internal.

---

# 5. Directory Structure

```text
structural_engine/

    engine.py

    parser/

    snapshot/

        generator.py
        loader.py
        serializer.py

        models.py

    revisions/

        tracker.py
        models.py

    state/

        manager.py
        models.py

    diff/

        generator.py
        models.py

    reports/

        generator.py
        templates/

    logs/

        generator.py

    results/

        initialization.py
        sync.py

    exceptions/

        errors.py
```

Each subsystem owns exactly one responsibility.

---

# 6. Internal Architecture

```text
Structural Engine

├── Parser
├── Snapshot Generator
├── Snapshot Loader
├── Revision Tracker
├── State Manager
├── Diff Generator
├── Report Generator
├── Log Generator
└── Result Builder
```

The engine coordinates these components.

Components do not call each other directly.

All orchestration occurs through:

```python
StructuralEngine
```

---

# 7. Structural Engine Contract

Input:

```python
RepositoryPaths
```

Output:

Initialization:

```python
InitializationResult
```

Synchronization:

```python
SyncResult
```

The Runtime communicates only through these contracts.

No Runtime component should import:

```python
Parser

StateManager

DiffGenerator

ReportGenerator
```

Likewise the Structural Engine never imports:

```python
Commands

Services

CLI

Output
```

Communication occurs only through:

```python
RepositoryPaths

InitializationResult

SyncResult
```

---

# 8. Internal Models

## StructuralSnapshot

Represents complete structural truth.

```python
class StructuralSnapshot:

    entities

    relationships
```

Snapshots are immutable.

---

## StructuralDiff

Represents structural evolution.

```python
class StructuralDiff:

    entities_added

    entities_removed

    entities_modified

    relationships_added

    relationships_removed

    affected_components
```

Diffs contain facts only.

---

## StructuralState

Represents synchronization state.

```python
class StructuralState:

    current_snapshot

    structural_revision

    latest_report

    last_sync
```

---

## Revision

Represents revision identity.

```python
class Revision:

    number

    id
```

Examples:

```text
S-001

S-002

S-003
```

---

# 9. Parser

Location:

```text
parser/
```

Purpose:

Observe repository structure.

Output:

```python
StructuralSnapshot
```

The parser owns:

* file discovery
* language detection
* tree-sitter parsing
* entity extraction
* relationship extraction
* call resolution

Parser internals are documented separately.

See:

```text
Parser_Implementation.md
```

Parser performs:

```text
Observation only
```

Parser performs no:

* persistence
* reports
* revisions
* state updates
* logs

Its responsibility ends after returning:

```python
StructuralSnapshot
```

---

# 10. Snapshot Generator

Location:

```text
snapshot/generator.py
```

Purpose:

Persist structural snapshots.

Input:

```python
snapshot

revision
```

Output:

```text
.brain/structure/snapshots/S-014.json
```

Responsibilities:

* serialization
* persistence
* deterministic ordering

Never:

* compare snapshots
* update state
* generate reports

Snapshots are immutable.

Existing snapshots are never modified.

---

# 11. Snapshot Loader

Location:

```text
snapshot/loader.py
```

Purpose:

Load historical structural truth.

Input:

```python
current_snapshot
```

Output:

```python
StructuralSnapshot
```

Example:

```text
state.yaml

↓

current_snapshot=S-013

↓

load()

↓

S-013.json

↓

StructuralSnapshot
```

Initialization never uses Snapshot Loader.

Synchronization always uses it.

---

# 12. Revision Tracker

Location:

```text
revisions/tracker.py
```

Purpose:

Manage structural chronology.

Responsibilities:

Determine:

```python
current()

next()

previous()
```

Examples:

```text
S-001

S-002

S-003
```

Revision Tracker owns numbering.

It does not own state.

It does not own persistence.

---

# 13. State Manager

Location:

```text
state/manager.py
```

Authority:

```text
.brain/state.yaml
```

Responsible for:

Loading:

```yaml
current_snapshot

structural_revision

latest_report

last_sync
```

Updating:

```yaml
current_snapshot

structural_revision

latest_report

last_sync
```

It ignores:

```yaml
semantic_revision
```

because semantic ownership belongs to humans and AI agents.

State Manager is the synchronization authority of the Structural Engine.

---

# 14. Report Generator

Location:

```text
reports/generator.py
```

Purpose:

Transform structural evolution into report artifacts.

Input:

```python
StructuralDiff
```

Output:

```text
R-014.md
```

Reports contain:

* entities added
* entities removed
* dependencies changed
* relationships changed
* affected regions

Reports contain facts only.

They perform no interpretation.

---

# 15. Log Generator

Location:

```text
logs/generator.py
```

Purpose:

Record synchronization history.

Output:

```text
logs/sync.md
```

Records:

```text
revision

timestamp

report

status
```

Logs provide observability.

They never affect structural computation.

---

# 16. Result Objects

Initialization returns:

```python
class InitializationResult:

    revision

    snapshot

    success
```

Synchronization returns:

```python
class SyncResult:

    revision

    report

    timestamp

    success
```

These objects are consumed by the Runtime.

Never strings.

Never console output.

---

# 17. Cooperation with Runtime

The Runtime sees:

```python
initialize(paths)

sync(paths)
```

and nothing else.

The Structural Engine sees:

```python
RepositoryPaths
```

containing:

```python
repo_root

brain_root

snapshots_dir

reports_dir

logs_dir

state_file
```

The Structural Engine does not know:

* CLI
* Commands
* Services
* Output

The Runtime does not know:

* Parser
* StateManager
* DiffGenerator
* ReportGenerator

This separation is critical.

---

# 18. Initialization Philosophy

Initialization establishes truth.

It does not establish evolution.

Since no previous truth exists:

There are:

```text
No reports

No diffs

No logs
```

Initialization exists solely to establish:

```text
S-001
```

---

# 19. Initialization Flow

```text
Runtime

↓

StructuralEngine.initialize()

══════════════════════

Parser

↓

StructuralSnapshot

↓

RevisionTracker

↓

S-001

↓

SnapshotGenerator

↓

Persist Snapshot

↓

StateManager

↓

Initialize state.yaml

══════════════════════

InitializationResult

↓

Runtime

↓

Output

↓

Complete
```

---

# 20. Initialization Data Flow

```text
brain .

↓

CLI

↓

Command

↓

Service

↓

RepositoryDiscovery

↓

RepositoryPaths

↓

StructuralEngine.initialize()

══════════════════════

Parser

↓

Current Snapshot

↓

RevisionTracker.next()

↓

S-001

↓

SnapshotGenerator.persist()

↓

S-001.json

↓

StateManager.initialize()

↓

state.yaml

══════════════════════

InitializationResult

↓

Runtime

↓

Console

↓

Done
```

---

# 21. Initialization Call Graph

```python
initialize()

    parser.parse()

    tracker.next()

    snapshot_generator.persist()

    state_manager.initialize()

    result_builder.build()

    return InitializationResult
```

---

# 22. Exception Hierarchy

```text
StructuralEngineError

├── ParserFailure

├── SnapshotPersistenceError

├── SnapshotNotFound

├── CorruptSnapshot

├── InvalidState

├── ReportGenerationError

├── DiffGenerationError
```

These exceptions remain internal.

The Runtime converts them into user-facing messages.

---

# 23. Architectural Invariants

The Structural Engine owns:

* snapshots
* reports
* logs
* revisions
* structural state

The Structural Engine never owns:

* commands
* output
* semantic knowledge
* decisions
* conventions
* constraints
* understanding

Its responsibility is simple:

```text
Repository

↓

Structural Truth

↓

Structural History

↓

Structural Reports

↓

Brain Artifact
```

Everything beyond that belongs to humans and intelligent systems.

---

# 24. Synchronization Philosophy

Synchronization exists to evolve structural truth.

It follows one fundamental principle:

> Truth precedes evolution.

The Structural Engine never computes differences before establishing the current truth.

Incorrect:

```text
Previous Snapshot

↓

Diff

↓

Current Snapshot
```

Correct:

```text
Previous Snapshot

↓

Current Snapshot

↓

Persist Current Truth

↓

Diff

↓

Report
```

The current snapshot is always authoritative.

Diffs are secondary.

Reports are tertiary.

---

# 25. Synchronization Flow

Synchronization occurs during:

```bash
brain sync
```

Flow:

```text
Runtime

↓

StructuralEngine.sync()

══════════════════════

StateManager.load()

↓

SnapshotLoader.load()

↓

Parser.parse()

↓

Current Snapshot

↓

RevisionTracker.next()

↓

SnapshotGenerator.persist()

↓

DiffGenerator.generate()

↓

ReportGenerator.generate()

↓

LogGenerator.generate()

↓

StateManager.update()

══════════════════════

SyncResult

↓

Runtime

↓

Output

↓

Done
```

The Runtime remains unaware of internal operations.

---

# 26. Internal Synchronization Lifecycle

The Structural Engine performs:

```text
Load state

↓

Load previous truth

↓

Observe current truth

↓

Persist current truth

↓

Compute evolution

↓

Generate report

↓

Generate log

↓

Update state

↓

Return SyncResult
```

Every stage is deterministic.

---

# 27. Synchronization Data Flow

```text
state.yaml

↓

current_snapshot

↓

Snapshot Loader

↓

S-013.json

↓

Previous Snapshot

═══════════════════

Parser

↓

Current Snapshot

═══════════════════

RevisionTracker

↓

S-014

↓

SnapshotGenerator

↓

S-014.json

═══════════════════

DiffGenerator

↓

StructuralDiff

═══════════════════

ReportGenerator

↓

R-014.md

═══════════════════

LogGenerator

↓

sync.md

═══════════════════

StateManager.update()

↓

state.yaml

═══════════════════

SyncResult
```

---

# 28. Synchronization Call Graph

```python
sync():

    state = state_manager.load()

    previous_snapshot = snapshot_loader.load()

    current_snapshot = parser.parse()

    revision = tracker.next()

    snapshot_generator.persist()

    diff = diff_generator.generate()

    report = report_generator.generate()

    log_generator.append()

    state_manager.update()

    return SyncResult
```

The engine coordinates all subsystems.

Subsystems remain isolated.

---

# 29. Snapshot Persistence Order

Persistence order is critical.

Always:

```text
Persist Snapshot

↓

Generate Diff

↓

Persist Report

↓

Persist Log

↓

Update State
```

Never:

```text
Update State

↓

Persist Artifacts
```

State must point only to successfully created artifacts.

This prevents corruption.

---

# 30. Diff Generator

Location:

```text
diff/generator.py
```

Purpose:

Compute structural evolution.

Input:

```python
previous_snapshot

current_snapshot
```

Output:

```python
StructuralDiff
```

Diff Generator performs comparison only.

It never performs interpretation.

Its purpose is to answer:

> What changed?

Never:

> Why did it change?

---

# 31. StructuralDiff Model

```python
class StructuralDiff:

    entities_added

    entities_removed

    entities_modified

    relationships_added

    relationships_removed

    affected_components
```

Diffs contain facts.

Nothing semantic.

---

# 32. Entity Comparison

Entities are matched by:

```python
entity.id
```

Not by:

```text
name

line numbers

order
```

Examples:

```text
src/auth.py::verify_token
```

Stable IDs guarantee deterministic diffs.

---

# 33. Relationship Comparison

Relationships are matched using:

```python
(
    source_id,
    target_id,
    relationship_type
)
```

Examples:

```text
CALLS

IMPORTS

INHERITS

CONTAINS
```

Added relationships become:

```python
relationships_added
```

Removed relationships become:

```python
relationships_removed
```

---

# 34. Affected Components

Purpose:

Identify regions impacted by change.

Examples:

```text
auth

database

payments
```

Derived from changed entities.

Used by semantic evolution later.

Affected components remain structural facts.

Not interpretations.

---

# 35. Report Generator

Location:

```text
reports/generator.py
```

Input:

```python
StructuralDiff
```

Output:

```text
R-014.md
```

Responsibilities:

Transform facts into readable reports.

Reports contain:

```text
Entities Added

Entities Removed

Relationships Added

Relationships Removed

Affected Regions
```

Nothing else.

---

# 36. Report Naming

Examples:

```text
R-001.md

R-002.md

R-003.md
```

Report IDs follow structural revisions.

Example:

```text
S-014

↓

R-014
```

One report per synchronization.

---

# 37. Log Generator

Location:

```text
logs/generator.py
```

Purpose:

Maintain synchronization history.

Output:

```text
logs/sync.md
```

Records:

```text
Revision

Timestamp

Report

Snapshot

Status
```

Logs provide auditability.

They are never used for computation.

---

# 38. State Update

After all artifacts are successfully created:

```yaml
current_snapshot: S-014

structural_revision: S-014

latest_report: R-014

last_sync: timestamp
```

Only then is:

```yaml
state.yaml
```

updated.

---

# 39. Failure Recovery

Suppose:

```text
Snapshot persisted

↓

Report generation fails
```

Then:

```yaml
state.yaml
```

must remain unchanged.

Because state still points to:

```text
S-013

R-013
```

The repository remains consistent.

Failed synchronizations never partially update state.

---

# 40. Idempotency

Given identical repositories:

```text
repo@commit_x
```

Parser always produces:

```text
snapshot_x
```

Diff generation always produces:

```text
diff_x
```

Reports always produce:

```text
report_x
```

Synchronization must remain deterministic.

---

# 41. SyncResult

Synchronization returns:

```python
class SyncResult:

    revision

    report

    timestamp

    success
```

Consumed only by Runtime.

Not by internal components.

---

# 42. Runtime Cooperation

Runtime invokes:

```python
engine.sync(paths)
```

and receives:

```python
SyncResult
```

Runtime never imports:

```python
Parser

SnapshotLoader

DiffGenerator

ReportGenerator
```

Structural Engine never imports:

```python
CLI

Commands

Services

Output
```

Communication remains through contracts.

---

# 43. Unit Testing

Every subsystem should be tested independently.

---

## Parser

Verify:

```text
Deterministic snapshots
```

Parser implementation tested separately.

---

## Snapshot Generator

Verify:

```text
Snapshot serialization

Snapshot persistence
```

---

## Snapshot Loader

Verify:

```text
Snapshot loading

Corrupt snapshot detection
```

---

## Revision Tracker

Verify:

```text
S-001

S-002

S-003
```

ordering.

---

## State Manager

Verify:

```yaml
Load

Update

Consistency
```

---

## Diff Generator

Verify:

```text
Entity additions

Entity removals

Relationship additions

Relationship removals
```

---

## Report Generator

Verify:

```text
Markdown generation
```

---

## Log Generator

Verify:

```text
Synchronization history
```

---

# 44. Integration Testing

Entire Structural Engine:

```text
Parser

↓

Snapshot Generator

↓

Diff Generator

↓

Report Generator

↓

State Manager

↓

SyncResult
```

No Runtime involved.

The Structural Engine should be independently testable.

---

# 45. Runtime + Structural Engine Integration

Replace:

```python
MockStructuralEngine
```

with:

```python
StructuralEngine
```

No Runtime modifications should be required.

This validates the architecture.

---

# 46. End-to-End Initialization

```text
brain .

↓

Runtime

↓

StructuralEngine.initialize()

↓

S-001

↓

state.yaml

↓

InitializationResult

↓

Done
```

---

# 47. End-to-End Synchronization

```text
brain sync

↓

Runtime

↓

StateManager

↓

SnapshotLoader

↓

Parser

↓

Current Snapshot

↓

RevisionTracker

↓

SnapshotGenerator

↓

DiffGenerator

↓

ReportGenerator

↓

LogGenerator

↓

StateManager.update()

↓

SyncResult

↓

Done
```

---

# 48. Full Sequence Diagram

```text
User

↓

CLI

↓

Command

↓

Service

↓

RepositoryDiscovery

↓

RepositoryPaths

↓

StructuralEngine.sync()

══════════════════════

StateManager

↓

SnapshotLoader

↓

Parser

↓

RevisionTracker

↓

SnapshotGenerator

↓

DiffGenerator

↓

ReportGenerator

↓

LogGenerator

↓

StateManager.update()

══════════════════════

SyncResult

↓

Runtime

↓

Console

↓

User
```

---

# 49. Future Extensions

Possible additions:

### Snapshot Compression

```text
gzip snapshots
```

---

### Snapshot Caching

Avoid reparsing unchanged repositories.

---

### Incremental Parsing

Parse only modified files.

---

### Graph Export

```text
graph.json

graphml

networkx
```

---

### Dependency Analysis

Advanced relationship extraction.

---

### Metrics

```text
complexity

fan-in

fan-out
```

---

### Multi-language Expansion

```text
Go

Rust

Java

C#
```

These extensions should not require architectural changes.

---

# 50. Architectural Invariants

The Structural Engine owns:

* snapshots
* reports
* logs
* revisions
* structural state
* structural history

The Structural Engine never owns:

* commands
* output
* semantic knowledge
* conventions
* constraints
* decisions
* understanding

Structural truth is established first.

Structural evolution is computed second.

Reports are generated third.

State is updated last.

Its responsibility is simple:

```text
Repository

↓

Structural Truth

↓

Structural History

↓

Structural Evolution

↓

Structural Reports

↓

Brain Artifact
```

Everything beyond that belongs to humans and intelligent systems.

The Structural Engine exists to continuously establish, preserve, and evolve the structural truth of a repository.
