# Project Context & Implementation Guidelines

You are tasked with implementing the Global Runtime and Structural Engine for the knowcode ecosystem.

To guide your implementation, you are provided with four foundational documents. Read them completely and internalize the architectural boundaries before taking any action.

### Provided Documents

1. **Structural_engine_implementation.md**: Details the architecture, subsystems, and deterministic state computation of the Structural Engine.
2. **Parser_implementation plan.md**: Details the stateless parser subsystem that extracts structural truth from the repository.
3. **Runtime_Implementation.md**: Details the Global Runtime orchestration, CLI, and artifact building responsibilities.
4. **Architectural Patch v1.md**: **CRITICAL.** This document resolves architectural contradictions found in the first three files. It establishes strict boundary enforcements, shared contracts (`RepositoryPaths`, `state.yaml`), and the absolute authority hierarchy. Where conflicts exist, this patch strictly supersedes the other three documents.

### Your Immediate Task

Before writing any code, scaffolding the project, or executing commands, you must complete the following verifiable step:

* **Acknowledge and Clarify:** Review all four documents. Identify any remaining ambiguities, logical frictions, unhandled edge cases, or missing technical constraints. Surface these issues and ask clear, specific questions to resolve them.

Do not generate any implementation code or filesystem structures until we have resolved your questions and I have explicitly authorized you to begin development. Your only goal right now is to ingest the architecture and confirm your understanding of the boundaries.