"""Call resolver.

Transforms RawCalls into CALLS relationships.
Implements the conservative two-pass resolution strategy.
"""

from __future__ import annotations

from collections import defaultdict

from structural_engine.parser.models import Entity, EntityType, RawCall, Relationship, RelationshipType


def resolve_calls(
    entities: list[Entity],
    relationships: list[Relationship],
    raw_calls: list[RawCall],
) -> list[Relationship]:
    """Resolve raw calls into structural CALLS relationships.

    Uses a conservative strategy. If a call target cannot be uniquely
    resolved, it is dropped. Missing edges are allowed; incorrect edges
    are forbidden.

    Parameters
    ----------
    entities : list[Entity]
        All extracted entities.
    relationships : list[Relationship]
        Existing extracted relationships (like IMPORTS, CONTAINS).
    raw_calls : list[RawCall]
        Unresolved call extractions.

    Returns
    -------
    list[Relationship]
        A list of new Relationship objects of type CALLS.
    """
    resolved_calls: list[Relationship] = []

    # Build a global map of function/method names to their full entity IDs.
    name_to_ids: dict[str, list[str]] = defaultdict(list)
    for entity in entities:
        if entity.type in (EntityType.FUNCTION, EntityType.METHOD):
            name_to_ids[entity.name].append(entity.id)

    # Build an import map: source_file_id -> set of target_modules
    # For Pass 1 (Import Guided) we'd use this.
    imports: dict[str, set[str]] = defaultdict(set)
    for rel in relationships:
        if rel.type == RelationshipType.IMPORTS:
            imports[rel.source_id].add(rel.target_id)

    for call in raw_calls:
        candidates = name_to_ids.get(call.target_name, [])

        # Pass 2: Global Unique Match
        # If there is exactly one function/method in the entire repository
        # with this name, we resolve it.
        if len(candidates) == 1:
            resolved_calls.append(
                Relationship(
                    source_id=call.caller_id,
                    target_id=candidates[0],
                    type=RelationshipType.CALLS,
                )
            )
            continue

        # Pass 1: Import Guided (simplified for V1)
        # If there are multiple candidates, we could check if the caller's file
        # imports the module containing the candidate.
        # This requires tracking the file containing each candidate.
        if len(candidates) > 1:
            caller_file_id = call.source_file
            caller_imports = imports.get(caller_file_id, set())
            
            valid_candidates = []
            for candidate_id in candidates:
                # candidate_id format: src/auth.py::verify_token
                candidate_file_id = candidate_id.split("::")[0]
                # If it's in the same file, it's a strong candidate
                if candidate_file_id == caller_file_id:
                    valid_candidates.append(candidate_id)
                else:
                    # Check if caller imports the candidate's module
                    # For simplicity, we check if the candidate_file_id is a substring
                    # of any import target.
                    candidate_module_base = candidate_file_id.replace(".py", "").replace(".ts", "").replace(".js", "")
                    # e.g. src/auth -> auth
                    candidate_module_name = candidate_module_base.split("/")[-1]
                    
                    if candidate_module_name in caller_imports:
                        valid_candidates.append(candidate_id)

            if len(valid_candidates) == 1:
                resolved_calls.append(
                    Relationship(
                        source_id=call.caller_id,
                        target_id=valid_candidates[0],
                        type=RelationshipType.CALLS,
                    )
                )

    return resolved_calls
