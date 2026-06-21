# KnoWiki

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license)

**KnoWiki** is a structural cognition engine for code repositories. It bridges the gap between **physical repository code**, **deterministic structural snapshots**, and **semantic architectural knowledge**, allowing AI agents and human developers to inspect, track, and maintain codebase structures deterministically.

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture & Authority Hierarchy](#-architecture--authority-hierarchy)
- [Ecosystem Layout (`.brain`)](#-ecosystem-layout-brain)
- [Installation](#-installation)
- [Usage & CLI Reference](#-usage--cli-reference)
- [License](#-license)

---

## 🔍 Overview

KnoWiki partitions codebase understanding into three clean domains:
1. **Physical Reality:** The actual source files inside the repository.
2. **Structural Truth:** Deterministic representation of files, components, and code symbols parsed via abstract syntax trees (ASTs).
3. **Semantic Knowledge:** Human-authored or AI-generated documentation, rules, and architectural guidelines that provide meaning and context.

By analyzing the structure, KnoWiki computes a deterministic state and exposes it to orchestrators through a unified CLI. 

**Retroactive Context Distillation:**
KnoWiki completely flips the traditional documentation model. Instead of forcing developers to write specs *before* they code, KnoWiki uses an AI agent to track your intent during a development session. When you sync your physical code changes, the AI agent is automatically invoked to synthesize your intent against the deterministic reality of the codebase, ensuring your architectural knowledge naturally accumulates as a byproduct of development.

---

## ✨ Key Features

- 🌲 **Multi-Language AST Parsing**: Built on top of `tree-sitter`, with out-of-the-box support for **Python**, **JavaScript**, and **TypeScript**.
- 🔄 **Deterministic State & Revision Tracking**: Tracks codebase changes across sequential revisions (`S-001`, `S-002`, etc.) written to an authoritative state registry.
- 🔀 **Diff & Report Generation**: Automatically computes additions, deletions, line-boundary modifications, and maps changes to their top-level affected components.
- 🛠️ **Zero-Bypassing State Stewardship**: The engine handles updating all structural fields within `state.yaml` while preserving semantic metadata (such as `semantic_revision`).

---

## 🏛️ Architecture & Authority Hierarchy

KnoWiki operates under a strict, cascading chain of truth. No system layer is permitted to bypass the layers above it:

```mermaid
graph TD
    A[1. Repository - Physical Reality] --> B[2. Brain Artifact - .brain/ directory]
    B --> C[3. state.yaml - Definitive Sync Authority]
    C --> D[4. StateManager - Steward of state.yaml]
    D --> E[5. Structural Engine - Deterministic Calculator]
    E --> F[6. Runtime - Orchestrator / CLI]
```

1. **Repository:** The ultimate physical source of truth.
2. **Brain Artifact:** The reflection of that reality (`.brain/` directory).
3. **`state.yaml`:** The definitive metadata and synchronization authority.
4. **`StateManager`:** The steward managing structural fields inside `state.yaml`.
5. **Structural Engine:** The deterministic calculator of ASTs and changes.
6. **Runtime:** The thin orchestration layer that exposes commands to the user.

---

## 📂 Ecosystem Layout (`.brain` & `.agent`)

When KnoWiki is initialized in a repository, it generates a dual-folder structure:

```text
.brain/                        # The Deterministic Knowledge Artifact
├── state.yaml                 # Authoritative state registry (managed by the Engine)
├── structure/
│   └── snapshots/
│       ├── S-001.json         # Deterministic structural snapshots of AST symbols
│       └── ...
├── reports/
│   ├── R-001.md               # Change and diff analysis reports
│   └── ...
├── knowledge/                 # Permanent semantic knowledge (AI synthesized)
│   ├── architecture.md
│   ├── decisions.md
│   └── ...
└── logs/                      # Subsystem logs and diagnostic information

.agent/                        # The Semantic Governance & Memory Layer
├── BRAIN.md                   # Human-readable entrypoint and subsystem overview
├── memory/
│   ├── active_context.md      # The AI's short-term intent tracking buffer
│   └── previous_context.md    # Rolled-over buffer waiting for synthesis
├── skills/
│   └── system/
│       └── context_tracker.md # The Semantic Prime Directive
└── workflows/
```

---

## 🚀 Installation

### Prerequisites
- [Python 3.13+](https://www.python.org/)
- [uv Package Manager](https://github.com/astral-sh/uv)

### Setup
Clone the repository and install it in editable mode:

```bash
# Clone the repository
git clone https://github.com/your-username/knowiki.git
cd knowiki

# Synchronize dependencies and virtual environment
uv sync

# Install KnoWiki globally/locally in editable mode
uv pip install -e .
```

---

## 🛠️ Usage & CLI Reference

All interactions are done through the `brain` command-line utility.

### 1. Initialize the Brain
To scaffold the `.brain/` directory and create the initial baseline snapshot (`S-001`) of your repository:

```bash
brain .
```

### 2. View Current Status
To view the status of the Brain instance, including the current structural/semantic revision, snapshot reference, and synchronization metadata:

```bash
brain status
```

*Example Output:*
```text
┌─────────────────────────────────────────────────────────────┐
│                 Brain Status: /path/to/repo                 │
├──────────────────────┬──────────────────────────────────────┤
│ Initialized          │ Yes                                  │
│ Structural Revision  │ S-001                                │
│ Semantic Revision    │ none                                 │
│ Current Snapshot     │ .brain/structure/snapshots/S-001.yaml│
│ Latest Report        │ .brain/reports/R-001.yaml            │
│ Last Sync            │ 2026-06-20 14:30:00 UTC              │
└──────────────────────┴──────────────────────────────────────┘
```

### 3. Synchronize Structural State
Scan the repository for structural changes. If modifications are detected, KnoWiki writes a new snapshot (`S-002`, `S-003`, etc.), documents the structural differences in a report, and automatically rolls over the `active_context.md` memory buffer:

```bash
brain sync
```

* If there are no structural changes, KnoWiki returns immediately with a `No structural changes detected` shortcut and does not write a new snapshot.

### 4. Synchronize Semantic Knowledge
After a structural sync, the Semantic Agent synthesizes the rolled-over `previous_context.md` with the structural report. Once the Agent commits the architectural updates to `.brain/knowledge/`, run this command to safely bump the semantic revision (`M-001`) and flush the memory buffer:

```bash
brain sync-semantic
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
