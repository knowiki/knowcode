# KnowCode

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license)

**KnowCode** is a structural cognition engine designed specifically for Agentic IDEs (like Cursor, Gemini, and Copilot). It bridges the gap between **physical repository code**, **deterministic structural snapshots**, and **semantic architectural knowledge**, allowing AI agents and human developers to seamlessly inspect, track, and maintain codebase architectures.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage: The Agentic Workflow](#usage-the-agentic-workflow)
- [Ecosystem Layout](#ecosystem-layout)
- [CLI Reference & Manual Execution](#cli-reference--manual-execution)
- [License](#license)

---

## Overview

KnowCode completely flips the traditional documentation model. Instead of forcing developers to write specs *before* they code, KnowCode uses an AI agent to track your intent during a development session. When you sync your physical code changes, the AI agent is automatically invoked to synthesize your intent against the deterministic reality of the codebase, ensuring your architectural knowledge naturally accumulates as a byproduct of development.

KnowCode partitions codebase understanding into three clean domains:
1. **Physical Reality:** The actual source files inside the repository.
2. **Structural Truth:** Deterministic representation of files, components, and code symbols parsed via abstract syntax trees (ASTs).
3. **Semantic Knowledge:** Permanent architectural rules, decisions, and constraints synthesized by your AI agent.

---

## Key Features

- **Native Agent Integration:** Built-in slash commands (`/knowcode`, `/know-sync`) that plug directly into Agentic IDEs without configuration.
- **Smart File Discovery:** Natively respects your `.gitignore` to prevent parsing build artifacts. It also features built-in fallback protection against framework cache folders (e.g., `.next`, `.nuxt`) and minified bundles (`.min.js`), ensuring your AST snapshots remain lightning-fast and bloat-free.
- **Multi-Language AST Parsing**: Built on top of `tree-sitter`, with out-of-the-box support for **Python**, **JavaScript**, and **TypeScript**.
- **Deterministic State & Revision Tracking**: Tracks codebase changes across sequential revisions (`S-001`, `S-002`, etc.).
- **Diff & Report Generation**: Automatically computes additions, deletions, line-boundary modifications, and maps changes to their top-level affected components.

---

## Installation

### Prerequisites
- [Python 3.13+](https://www.python.org/)
- [uv Package Manager](https://github.com/astral-sh/uv)

### Setup
Clone the repository and install it in editable mode:

```bash
git clone https://github.com/your-username/knowcode.git
cd knowcode
uv sync
uv pip install -e .
```

---

## Usage: The Agentic Workflow

KnowCode is designed to be driven by you and your AI agent in tandem.

### 1. Initialize the Repository
Run the initialization command in your target repository terminal:
```bash
know .
```
This scaffolds the `.agent/` and `.knowcode/` directories, computes your first AST snapshot, and drops `knowcode.md` at your root.

### 2. Activate the Agent
In your AI chat (Cursor, Copilot, Gemini), simply type:
```text
/knowcode
```
The agent will instantly read `knowcode.md`, lock into the KnowCode governance rules, and begin silently tracking your intent in `.agent/memory/active_context.md` while you code.

### 3. Sync & Synthesize
After you finish a coding session or fix a bug, instruct the agent to synchronize by typing:
```text
/know-sync
```
The agent will orchestrate the entire lifecycle:
1. Run `know sync` to compute structural AST diffs.
2. Read the generated structural report (`R-XXX.md`).
3. Reconcile the structural reality against your tracked intent.
4. Distribute the extracted knowledge into the 5 semantic buckets (`architecture`, `decisions`, etc.).
5. Run `know sync-semantic` to commit the knowledge and bump the revision.

---

## Ecosystem Layout

When KnowCode is initialized in a repository via `know .`, it generates a governed agent architecture:

```text
/
├── knowcode.md                # The Agent Ignition Switch (Read by the AI)
├── .agent/                    # The Semantic Governance & Memory Layer
│   ├── memory/
│   │   ├── active_context.md  # The AI's short-term intent tracking buffer
│   │   └── previous_context.md
│   ├── skills/
│   │   ├── track_intent.md    # Background skill for tracking architectural intent
│   │   └── synthesize_knowledge.md
│   └── workflows/
│       ├── sync_reconciliation.md # The /know-sync workflow
│       └── ingest_legacy.md       # The /know-ingest workflow
│
└── .knowcode/                 # The Deterministic Knowledge Artifact
    ├── state.yaml             # Authoritative state registry (managed by the Engine)
    ├── structure/             # Deterministic AST snapshots (e.g. S-001.json)
    ├── reports/               # Change and diff analysis reports (e.g. R-001.md)
    └── knowledge/             # Permanent semantic knowledge (AI synthesized)
        ├── architecture/
        ├── components/
        ├── constraints/
        ├── conventions/
        ├── decisions/
        └── raw/               # Inbox for legacy or unstructured documentation
```

---

## CLI Reference & Manual Execution

While the Agentic Workflow relies on slash commands to orchestrate operations, developers can bypass the AI entirely and execute any step manually using the `know` CLI. This is useful for CI/CD pipelines, programmatic integration, or direct inspection.

- `know .`: Initializes Knowcode in the current directory.
- `know status`: Displays current structural and semantic revisions.
- `know sync`: Computes AST diffs, generates a report, and rolls over the memory buffer.
- `know sync-semantic`: Bumps the semantic revision after the AI (or a human) finishes synthesis.
- `know ingest-semantic .`: Wipes the raw documentation inbox and bumps the revision.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
