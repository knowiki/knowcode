# Global Runtime Implementation Plan — Part I

## Architecture, Components, Initialization and Cooperation with the Structural Engine

---

# 1. Purpose

The Global Runtime is the entrypoint into the Knowiki ecosystem. Its purpose is orchestration rather than computation. As described in the Runtime specification, the Runtime owns commands, repository discovery, initialization, and delegation, while structural computation belongs entirely to the Structural Engine. 

The Runtime should remain intentionally thin.

It should answer only one question:

> Which subsystem should perform this operation?

The Runtime never:

* parses repositories,
* computes structure,
* generates reports,
* creates understanding,
* modifies semantic knowledge.

Those responsibilities belong elsewhere.

---

# 2. Architectural Philosophy

The Runtime behaves similarly to a shell.

```text
User

↓

CLI

↓

Commands

↓

Services

↓

Repository

↓

Artifact Builder

↓

Structural Engine

↓

Brain Artifact
```

The Runtime owns orchestration.

The Structural Engine owns deterministic computation.

The Brain Artifact owns state.

No layer should violate these ownership boundaries.

---

# 3. Runtime Directory Structure

```text
runtime/

├── cli/
│
├── commands/
│
├── services/
│
├── repository/
│
├── artifact/
│
├── config/
│
├── templates/
│
├── skills/
│
├── output/
│
└── exceptions/
```

Each component owns exactly one responsibility.

---

# 4. Technical Stack

## CLI

Typer

```python
Typer
```

---

## Console Rendering

Rich

```python
rich
```

---

## Configuration

ruamel.yaml

```python
ruamel.yaml
```

---

## Validation

Pydantic

```python
pydantic
```

---

## Templates

Jinja2

```python
jinja2
```

---

## Filesystem

pathlib

```python
Path
```

---

## Logging

structlog

---

## Packaging

uv

---

# 5. Internal Runtime Structure

```text
runtime/

cli/
    app.py

commands/
    init.py
    sync.py
    status.py

services/
    init_service.py
    sync_service.py
    status_service.py

repository/
    discovery.py
    paths.py
    validator.py
    models.py

artifact/
    builder.py

config/
    loader.py
    models.py

templates/

skills/

output/
    console.py

exceptions/
    errors.py
```

---

# 6. CLI Layer

Location:

```text
runtime/cli/app.py
```

Purpose:

Expose the public interface.

Commands:

```bash
brain .

brain sync

brain status
```

Flow:

```text
brain sync

↓

Typer

↓

sync_command()

↓

sync_service.sync()
```

The CLI owns:

* arguments
* options
* help
* aliases

The CLI owns no business logic.

---

# 7. Command Layer

Location:

```text
runtime/commands/
```

Files:

```text
init.py

sync.py

status.py
```

Purpose:

Translate user commands into service calls.

Example:

```text
brain .

↓

init_command()

↓

init_service.initialize()
```

Commands should remain extremely small.

Responsibilities:

### Input parsing

```bash
brain . --skills react python
```

### Flag validation

### Delegation

Commands never:

* access the Structural Engine
* parse repositories
* manipulate files

---

# 8. Service Layer

Location:

```text
runtime/services/
```

Purpose:

Runtime orchestration.

Services coordinate subsystems.

They do not perform structural computation.

Files:

```text
init_service.py

sync_service.py

status_service.py
```

---

# init_service.py

Responsible for:

```text
Repository discovery

↓

Validation

↓

ArtifactBuilder

↓

StructuralEngine.initialize()

↓

Return result
```

---

# sync_service.py

Responsible for:

```text
Repository discovery

↓

Validation

↓

StructuralEngine.sync()

↓

Return SyncResult
```

---

# status_service.py

Responsible for:

Reading:

```text
.brain/state.yaml
```

Producing:

```text
Structural Revision : S-014

Semantic Revision : S-013

Latest Report : R-014

Status:
Pending Semantic Update
```

---

# 9. Repository Subsystem

Location:

```text
runtime/repository/
```

The Repository subsystem creates a common language shared by Runtime and Structural Engine.

Components:

```text
discovery.py

paths.py

validator.py

models.py
```

---

# Repository Model

models.py

```python
class Repository:

    root: Path

    git_dir: Path

    brain_dir: Path
```

---

# RepositoryPaths

The most important object in the Runtime.

```python
class RepositoryPaths:

    repo_root

    brain_root

    structure_dir

    snapshots_dir

    reports_dir

    logs_dir

    knowledge_dir

    state_file

    brain_file
```

The entire Runtime and Structural Engine communicate using this object.

No component should hardcode:

```python
".brain/structure"
```

Everything comes from RepositoryPaths.

---

# discovery.py

Purpose:

Locate repository root.

Algorithm:

```text
cwd

↓

parent

↓

parent

↓

.git

↓

repository root
```

Returns:

```python
Repository
```

---

# paths.py

Purpose:

Build path objects.

Input:

```python
Repository
```

Output:

```python
RepositoryPaths
```

No validation occurs here.

Pure path generation.

---

# validator.py

Purpose:

Verify repository integrity.

Checks:

### Git repository exists

```text
.git exists?
```

### .brain initialized?

```text
.brain exists?
```

### state.yaml exists?

### structure folder exists?

Raises:

```python
NotGitRepository

BrainNotInitialized

CorruptBrainArtifact
```

---

# 10. Artifact Builder

Location:

```text
runtime/artifact/builder.py
```

Purpose:

Construct the Brain Artifact filesystem.

This component is responsible only for filesystem creation.

It performs no structural analysis.

---

## Responsibilities

Create:

```text
.brain/

structure/

reports/

logs/

knowledge/

knowledge/architecture/

knowledge/decisions/

knowledge/constraints/

knowledge/conventions/

knowledge/components/
```

Render templates.

Install skills.

Initialize files.

---

## Artifact Creation Flow

```text
ArtifactBuilder

↓

mkdir()

↓

render templates

↓

copy skills

↓

complete
```

---

## Generated Files

```text
BRAIN.md

knowledge-maintenance.md

state.yaml
```

These files come from:

```text
runtime/templates/
```

---

# 11. Template System

Location:

```text
runtime/templates/
```

Files:

```text
BRAIN.md.j2

state.yaml.j2

knowledge-maintenance.md.j2
```

Purpose:

Generate initial Brain artifacts.

Uses:

```python
jinja2
```

Flow:

```text
Template

↓

render()

↓

write()

↓

file
```

---

# 12. Skills System

Location:

```text
runtime/skills/
```

Built-in skills:

```text
knowledge-maintenance.md

architecture-maintenance.md

constraints.md

decisions.md
```

Future structure:

```text
~/.knowiki/

skills/

    builtins/

    custom/
```

Allow:

```bash
brain . --skills react backend
```

to install:

```text
.brain/skills/

react.md

backend.md
```

Skills are never interpreted by the Runtime.

Runtime only copies them.

---

# 13. Configuration System

Location:

```text
runtime/config/
```

Files:

```text
loader.py

models.py
```

---

## models.py

Defines schemas.

```python
class RuntimeConfig(BaseModel):

    ignored_dirs:list[str]

    supported_languages:list[str]

    custom_skill_paths:list[str]
```

No file reading occurs here.

---

## loader.py

Reads:

```text
~/.knowiki/config/config.yaml
```

Produces:

```python
RuntimeConfig
```

Flow:

```text
config.yaml

↓

loader.py

↓

RuntimeConfig

↓

Runtime
```

---

# 14. Cooperation with Structural Engine

The Runtime never calls:

```python
Parser()

SnapshotGenerator()

DiffGenerator()
```

Instead it only sees:

```python
StructuralEngine.initialize()

StructuralEngine.sync()
```

This separation is critical.

Runtime does not know how structure is computed.

Structural Engine does not know Runtime exists.

---

# Initialization Data Flow

```text
brain .

↓

CLI

↓

init_command()

↓

init_service.initialize()

↓

RepositoryDiscovery

↓

RepositoryPaths

↓

Validator

↓

ArtifactBuilder

↓

StructuralEngine.initialize(paths)

══════════════════════

Parser

↓

SnapshotModel

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

Runtime Output

↓

Complete
```

---

# Runtime → Structural Engine Contract

Runtime only provides:

```python
paths
```

and requests:

```python
initialize(paths)

sync(paths)
```

The Structural Engine receives:

```python
RepositoryPaths
```

which gives access to:

```python
repo_root

brain_root

snapshots_dir

reports_dir

logs_dir

state_file
```

allowing the parser to ignore:

```text
.brain/

.git/

node_modules/
```

and allowing generators to know where artifacts should be persisted.

---

# Initialization Call Graph

```text
User

↓

brain .

↓

Typer

↓

init_command()

↓

init_service.initialize()

↓

RepositoryDiscovery

↓

RepositoryPaths

↓

Validator

↓

ArtifactBuilder

↓

StructuralEngine.initialize()

↓

InitializationResult

↓

console.render()

↓

Done
```

---

# Global Runtime Implementation Plan — Part II

## Synchronization, Contracts, Status, Error Handling, Testing and Integration

Part I established the Runtime architecture, repository subsystem, artifact builder, templates, skills, and initialization flow. This part focuses on the operational lifecycle after initialization and defines how the Runtime interacts with the Structural Engine while preserving strict ownership boundaries.

---

# 15. Synchronization Philosophy

Synchronization is not a Runtime operation.

Synchronization is a Structural Engine operation coordinated by the Runtime.

The Runtime does not:

* load snapshots,
* compare snapshots,
* compute structural differences,
* generate reports,
* update structural state.

Those responsibilities belong entirely to the Structural Engine. The Runtime merely prepares context and delegates execution, consistent with the Runtime architecture and the Structural Engine ownership model.  

---

# 16. Synchronization Data Flow

```text
brain sync

↓

CLI

↓

sync_command()

↓

sync_service.sync()

↓

RepositoryDiscovery

↓

RepositoryPaths

↓

Validator

↓

StructuralEngine.sync(paths)

═══════════════════════

StateManager.load()

↓

SnapshotLoader.load()

↓

Parser.parse()

↓

RevisionTracker.next()

↓

SnapshotGenerator.persist()

↓

DiffGenerator.generate()

↓

ReportGenerator.create()

↓

LogGenerator.create()

↓

StateManager.update()

═══════════════════════

SyncResult

↓

Output.render()

↓

Done
```

The Runtime never sees internal Structural Engine components.

---

# 17. Synchronization Call Graph

```text
brain sync

↓

Typer

↓

sync_command()

↓

sync_service.sync()

↓

discover()

↓

build_paths()

↓

validate()

↓

StructuralEngine.sync(paths)

↓

SyncResult

↓

console.render()
```

The Runtime knows only:

```python
engine.sync(paths)
```

Nothing else.

---

# 18. Internal Synchronization Flow

Inside the Structural Engine:

```text
sync()

↓

Load state.yaml

↓

Load previous snapshot

↓

Parse repository

↓

Current snapshot

↓

New revision

↓

Persist snapshot

↓

Generate diff

↓

Generate report

↓

Generate logs

↓

Update state

↓

Return SyncResult
```

The Runtime is unaware of every step above.

---

# 19. Status Flow

Status is entirely a Runtime concern.

No Structural Engine invocation occurs.

---

## Flow

```text
brain status

↓

status_command()

↓

status_service.status()

↓

Read state.yaml

↓

Create StatusResult

↓

Output.render()
```

No synchronization occurs.

No parsing occurs.

No structural computation occurs.

---

## Display

Example:

```text
Structural Revision : S-014

Semantic Revision : S-013

Latest Report : R-014

Last Sync : 2026-06-18 12:00

Status :

Pending Semantic Update
```

---

# 20. Output Layer

Location:

```text
runtime/output/
```

Files:

```text
console.py

formatter.py
```

Uses:

```python
rich
```

Purpose:

Presentation.

Never computation.

---

# Output Flow

```text
Service

↓

Result object

↓

Formatter

↓

Rich Console

↓

User
```

---

# Result Objects

Services return structured objects.

Never strings.

---

## InitializationResult

```python
class InitializationResult:

    revision: str

    snapshot: str

    success: bool
```

---

## SyncResult

```python
class SyncResult:

    revision: str

    report: str

    timestamp: datetime

    success: bool
```

---

## StatusResult

```python
class StatusResult:

    structural_revision: str

    semantic_revision: str

    latest_report: str

    status: str
```

The Output layer renders these objects.

---

# 21. Exception System

Location:

```text
runtime/exceptions/
```

Purpose:

Provide typed failures.

---

# Hierarchy

```text
BrainError

├── RepositoryError
│
│   ├── NotGitRepository
│   ├── RepositoryNotFound
│
├── ArtifactError
│
│   ├── BrainAlreadyInitialized
│   ├── BrainNotInitialized
│   ├── CorruptBrainArtifact
│
├── ConfigError
│
│   ├── InvalidConfig
│   ├── MissingConfig
│
├── SyncError
│
│   ├── StructuralEngineFailure
│
└── RuntimeError
```

---

# Exception Flow

```text
Service

↓

Exception

↓

Output

↓

Friendly message
```

Example:

```python
try:

    engine.sync()

except BrainNotInitialized:

    console.error(
        "Repository is not initialized."
    )
```

---

# 22. Runtime ↔ Structural Engine Contract

This is the most important boundary.

Runtime sees:

```python
engine.initialize(paths)

engine.sync(paths)
```

and nothing more.

---

# Inputs

Runtime provides:

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

---

# Outputs

Initialization:

```python
InitializationResult
```

Synchronization:

```python
SyncResult
```

---

# Forbidden Coupling

Runtime must never import:

```python
Parser

SnapshotGenerator

DiffGenerator

ReportGenerator

StateManager
```

Structural Engine must never import:

```python
Commands

Services

Output

CLI
```

Communication occurs only through:

```python
RepositoryPaths

InitializationResult

SyncResult
```

---

# 23. RepositoryPaths as Shared Language

RepositoryPaths becomes the central contract.

Everything speaks through it.

```python
class RepositoryPaths:

    repo_root

    brain_root

    structure_dir

    snapshots_dir

    reports_dir

    logs_dir

    knowledge_dir

    state_file

    brain_file
```

The parser receives it.

Generators receive it.

Runtime receives it.

No hardcoded strings exist.

---

# 24. Mock Engine

Runtime development should begin before the Structural Engine exists.

Temporary implementation:

```python
class MockStructuralEngine:

    def initialize(paths):

        return InitializationResult(
            revision="S-001"
        )

    def sync(paths):

        return SyncResult(
            revision="S-002",
            report="R-002"
        )
```

Allows independent Runtime development.

---

# 25. Unit Testing Strategy

Every Runtime subsystem should be tested independently.

---

## CLI

Verify:

```bash
brain .
brain sync
brain status
```

invoke correct commands.

---

## Commands

Verify:

```python
sync_command()
```

calls:

```python
sync_service.sync()
```

---

## Repository

Verify:

* discovery
* path generation
* validation

---

## Artifact Builder

Verify:

`.brain/`

is created correctly.

---

## Templates

Verify:

Jinja rendering.

---

## Skills

Verify:

skill installation.

---

## Output

Verify:

result rendering.

---

## Exceptions

Verify:

proper error messages.

---

# 26. Integration Testing

Replace:

```python
MockStructuralEngine
```

with:

```python
StructuralEngine
```

No Runtime changes should be required.

This validates architecture.

---

# 27. End-to-End Flow

## Initialization

```text
brain .

↓

Runtime

↓

Artifact Builder

↓

Structural Engine

↓

Brain Artifact

↓

Done
```

---

## Synchronization

```text
brain sync

↓

Runtime

↓

Structural Engine

↓

Brain Artifact

↓

SyncResult

↓

Output

↓

Done
```

---

## Status

```text
brain status

↓

Runtime

↓

state.yaml

↓

Output

↓

Done
```

---

# 28. Full Runtime Sequence Diagram

### Initialization

```text
User

↓

CLI

↓

Command

↓

Service

↓

Repository Discovery

↓

RepositoryPaths

↓

Validator

↓

Artifact Builder

↓

StructuralEngine.initialize()

↓

InitializationResult

↓

Output

↓

User
```

---

### Synchronization

```text
User

↓

CLI

↓

Command

↓

Service

↓

Repository Discovery

↓

RepositoryPaths

↓

Validator

↓

StructuralEngine.sync()

↓

SyncResult

↓

Output

↓

User
```

---

### Status

```text
User

↓

CLI

↓

Command

↓

Status Service

↓

state.yaml

↓

StatusResult

↓

Output

↓

User
```

---

# 29. Future Extensibility

The Runtime should support future additions without modifying its architecture.

Possible additions:

### Plugin System

```text
~/.knowiki/plugins/
```

---

### Custom Templates

```text
~/.knowiki/templates/
```

---

### Custom Skills

```text
~/.knowiki/skills/custom/
```

---

### Migrations

```bash
brain migrate
```

---

### Doctor

```bash
brain doctor
```

---

### Upgrade

```bash
brain upgrade
```

---

### Semantic Status

```bash
brain semantic-status
```

---

# Runtime Architectural Invariants

The Runtime owns:

* commands
* repository discovery
* artifact creation
* validation
* configuration
* output
* exception handling
* delegation

The Runtime never owns:

* parsing
* snapshots
* reports
* logs
* revisions
* state management
* semantic knowledge

Its purpose is orchestration.

Everything interesting happens below it.

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

This separation is the most important property of the entire architecture because it allows Runtime and Structural Engine to evolve independently while maintaining a stable contract between them.
