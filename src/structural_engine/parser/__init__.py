# Parser subsystem — internal to the Structural Engine.
# Observes current repository structure and produces a StructuralSnapshot.
# Stateless, side-effect free, deterministic.

from structural_engine.parser.parser import parse

__all__ = ["parse"]
