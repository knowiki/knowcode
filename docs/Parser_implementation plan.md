# Knowiki Parser v1 — Detailed Implementation Plan

# Purpose

The Parser is an internal subsystem of the Structural Engine.

Its purpose is to establish the current structural truth of a repository.

It answers one question:

> What does the repository look like right now?

The parser performs observation only.

It never:

* persists artifacts
* computes revisions
* generates reports
* updates state
* performs semantic reasoning
* modifies knowledge

Its output is a StructuralSnapshot.

---

# Architectural Position

```text
Runtime

↓

Structural Engine

↓

Parser

↓

Structural Snapshot

↓

Snapshot Generator

↓

Diff Generator

↓

Report Generator

↓

State Manager
```

Parser participates only in the highlighted stage.

---

# Parser Contract

Input:

```python
RepositoryPaths
```

Output:

```python
StructuralSnapshot
```

```python
parse(
    paths: RepositoryPaths
) -> StructuralSnapshot
```

---

# Parser Invariants

## Deterministic

Given identical repository states:

```text
repo@commit_x
```

Parser must always produce:

```text
snapshot_x
```

regardless of:

* user
* machine
* runtime state
* operating system

---

## Stateless

Parser never reads:

```text
state.yaml
previous snapshots
reports
logs
knowledge
```

Current repository state is the only authority.

---

## Side-Effect Free

Parser performs no writes.

No filesystem mutations.

No revision generation.

No persistence.

---

## No Brain Awareness

Parser receives:

```python
RepositoryPaths
```

but only consumes:

```python
paths.repo_root
```

It ignores:

```python
paths.snapshots_dir
paths.reports_dir
paths.logs_dir
paths.state_file
```

---

# Directory Structure

```text
structural_engine/

    parser/

        parser.py

        models/

            entity.py
            relationship.py
            snapshot.py
            references.py

        discovery/

            file_discovery.py
            language_detection.py

        tree_sitter/

            registry.py
            parser_factory.py

        extractors/

            entities.py
            relationships.py
            calls.py

        languages/

            base.py

            python/
                adapter.py

            typescript/
                adapter.py

            javascript/
                adapter.py

        resolvers/

            imports.py
            calls.py
```

---

# Parsing Pipeline

```text
RepositoryPaths

↓

repo_root

↓

File Discovery

↓

Language Detection

↓

Tree-sitter Parse

↓

Entity Extraction

↓

Relationship Extraction

↓

Raw Call Extraction

↓

Reference Resolution

↓

Structural Snapshot
```

---

# Stage 1 — File Discovery

Input:

```python
paths.repo_root
```

Responsibilities:

* recursively walk repository
* identify supported files
* filter ignored directories

Ignored:

```text
.git
.brain
node_modules
dist
build
target
venv
```

Output:

```python
list[FileInfo]
```

---

# Stage 2 — Language Detection

V1 Languages:

```text
Python
TypeScript
JavaScript
```

Future:

```text
Go
Rust
Java
C#
```

Mapping:

```python
{
    ".py": PYTHON,
    ".ts": TYPESCRIPT,
    ".tsx": TYPESCRIPT,
    ".js": JAVASCRIPT
}
```

Output:

```python
Language
```

---

# Stage 3 — Tree-sitter Parse

Input:

```python
FileInfo
```

Output:

```python
Tree
```

Responsibilities:

* load grammar
* parse source
* produce AST

No extraction occurs here.

---

# Stage 4 — Entity Extraction

Input:

```python
Tree
```

Output:

```python
Entity[]
```

---

## Entity Types

```text
Repository
Directory
File
Class
Interface
Function
Method
```

---

## Entity Model

```python
@dataclass
class Entity:

    id: str

    type: EntityType

    name: str

    path: str

    parent_id: str | None

    start_line: int

    end_line: int
```

---

## Stable IDs

Examples:

```text
repo

src

src/auth.py

src/auth.py::verify_token

src/auth.py::UserService

src/auth.py::UserService::create_user
```

Never use UUIDs.

---

# Stage 5 — Relationship Extraction

Output:

```python
Relationship[]
```

---

## Relationship Types

```text
CONTAINS

IMPORTS

INHERITS

IMPLEMENTS
```

---

## Relationship Model

```python
@dataclass
class Relationship:

    source_id: str

    target_id: str

    type: RelationshipType
```

---

## CONTAINS

Generated from hierarchy stack.

```text
Repository

↓

Directory

↓

File

↓

Class

↓

Method
```

---

## INHERITS

Generated from base classes.

Example:

```python
class Admin(User)
```

↓

```text
Admin INHERITS User
```

---

## IMPLEMENTS

Generated from interfaces.

---

## IMPORTS

Generated from import statements.

Resolved conservatively.

---

# Stage 6 — Raw Call Extraction

Input:

```python
Tree
```

Output:

```python
RawCall[]
```

Model:

```python
@dataclass
class RawCall:

    caller_id: str

    target_name: str

    source_file: str

    line: int
```

Example:

```python
verify_token()
```

↓

```python
RawCall(
    caller_id="handle_request",
    target_name="verify_token"
)
```

No resolution occurs here.

---

# Stage 7 — Call Resolution

Purpose:

Transform RawCalls into CALLS relationships.

---

## Pass 1 — Import Guided

Example:

```python
from auth import verify_token

verify_token()
```

↓

```text
handle_request
CALLS
auth.verify_token
```

Only when unique.

---

## Pass 2 — Global Unique Match

Build:

```python
{
    "verify_token":
        [
            "src/auth.py::verify_token"
        ]
}
```

Exactly one candidate:

Resolve.

Multiple candidates:

Skip.

No candidates:

Skip.

---

## Resolution Philosophy

Allowed:

```text
Missing edge
```

Forbidden:

```text
Incorrect edge
```

Parser never guesses.

---

# Stage 8 — Snapshot Assembly

Combine:

```python
entities
relationships
```

into:

```python
StructuralSnapshot
```

Model:

```python
@dataclass
class StructuralSnapshot:

    entities: list[Entity]

    relationships: list[Relationship]
```

No metadata.

No revisions.

No timestamps.

No reports.

---

# Sorting

Before returning:

Entities sorted by:

```text
id
```

Relationships sorted by:

```text
source_id

target_id

relationship_type
```

Guarantees deterministic output.

---

# Return

```python
snapshot = parse(paths)
```

Returned to:

```python
StructuralEngine.initialize()

or

StructuralEngine.sync()
```

---

# Cooperation With Structural Engine

Parser never invokes:

```python
RevisionTracker()

SnapshotGenerator()

DiffGenerator()

ReportGenerator()

StateManager()
```

These components invoke the parser.

---

# Initialization Flow

```text
StructuralEngine.initialize()

↓

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

Complete
```

---

# Synchronization Flow

```text
StructuralEngine.sync()

↓

StateManager.load()

↓

SnapshotLoader.load()

↓

Parser

↓

Current Snapshot

↓

RevisionTracker

↓

New Revision

↓

SnapshotGenerator

↓

Persist Snapshot

↓

DiffGenerator

↓

StructuralDiff

↓

ReportGenerator

↓

Persist Report

↓

StateManager.update()

↓

Complete
```

---

# Parser Success Criteria

Parser successfully:

✓ Discovers repository files

✓ Parses supported languages

✓ Extracts entities

✓ Extracts relationships

✓ Resolves imports

✓ Resolves calls conservatively

✓ Produces deterministic snapshots

✓ Remains stateless

✓ Performs zero persistence

✓ Maintains strict separation from the rest of the Structural Engine

The parser's responsibility ends when it returns:

```python
StructuralSnapshot
```

Everything beyond that belongs to the Structural Engine.
