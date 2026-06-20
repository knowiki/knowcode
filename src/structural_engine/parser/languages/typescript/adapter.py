"""TypeScript structural extractor.

Walks a TypeScript tree-sitter AST to extract entities, relationships,
and raw calls.
"""

from __future__ import annotations

import tree_sitter

from structural_engine.parser.extractors.base import ExtractionResult, LanguageAdapter
from structural_engine.parser.models import (
    Entity,
    EntityType,
    FileInfo,
    RawCall,
    Relationship,
    RelationshipType,
)


class TypeScriptAdapter(LanguageAdapter):
    """AST extractor for TypeScript."""

    def extract(
        self, file_info: FileInfo, tree: tree_sitter.Tree, source_bytes: bytes
    ) -> ExtractionResult:
        result = ExtractionResult()

        file_id = file_info.relative_path
        parent_dir = file_info.relative_path.rsplit("/", 1)[0] if "/" in file_info.relative_path else "repo"
        file_entity = Entity(
            id=file_id,
            type=EntityType.FILE,
            name=file_info.absolute_path.name,
            path=file_info.relative_path,
            parent_id=parent_dir,
            start_line=1,
            end_line=source_bytes.count(b"\n") + 1,
        )
        result.entities.append(file_entity)

        def walk(node: tree_sitter.Node, current_parent_id: str, is_in_class: bool = False):
            # Extract Imports
            if node.type == "import_statement":
                source_node = node.child_by_field_name("source")
                if source_node:
                    imported_module = source_node.text.decode("utf-8").strip("'\"")
                    result.relationships.append(
                        Relationship(
                            source_id=file_id,
                            target_id=imported_module,
                            type=RelationshipType.IMPORTS,
                        )
                    )

            # Extract Classes / Interfaces
            elif node.type in ("class_declaration", "interface_declaration"):
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = name_node.text.decode("utf-8")
                    entity_id = f"{current_parent_id}::{name}"
                    
                    entity_type = EntityType.INTERFACE if node.type == "interface_declaration" else EntityType.CLASS

                    result.entities.append(
                        Entity(
                            id=entity_id,
                            type=entity_type,
                            name=name,
                            path=file_info.relative_path,
                            parent_id=current_parent_id,
                            start_line=node.start_point[0] + 1,
                            end_line=node.end_point[0] + 1,
                        )
                    )
                    result.relationships.append(
                        Relationship(
                            source_id=current_parent_id,
                            target_id=entity_id,
                            type=RelationshipType.CONTAINS,
                        )
                    )

                    for child in node.children:
                        if child.type == "class_heritage":
                            for heritage_child in child.children:
                                if heritage_child.type == "extends_clause":
                                    for gchild in heritage_child.children:
                                        if gchild.type == "identifier" or gchild.type == "type_identifier":
                                            result.relationships.append(
                                                Relationship(
                                                    source_id=entity_id,
                                                    target_id=gchild.text.decode("utf-8"),
                                                    type=RelationshipType.INHERITS,
                                                )
                                            )
                                elif heritage_child.type == "implements_clause":
                                    for gchild in heritage_child.children:
                                        if gchild.type == "type_identifier" or gchild.type == "identifier":
                                            result.relationships.append(
                                                Relationship(
                                                    source_id=entity_id,
                                                    target_id=gchild.text.decode("utf-8"),
                                                    type=RelationshipType.IMPLEMENTS,
                                                )
                                            )

                    for child in node.children:
                        walk(child, entity_id, is_in_class=(entity_type == EntityType.CLASS))
                return

            # Extract Functions
            elif node.type in ("function_declaration", "method_definition", "arrow_function"):
                # Arrow functions might not have a direct 'name' field if assigned to variable,
                # but let's stick to basics for V1
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = name_node.text.decode("utf-8")
                    func_id = f"{current_parent_id}::{name}"
                    func_type = EntityType.METHOD if is_in_class or node.type == "method_definition" else EntityType.FUNCTION
                    
                    result.entities.append(
                        Entity(
                            id=func_id,
                            type=func_type,
                            name=name,
                            path=file_info.relative_path,
                            parent_id=current_parent_id,
                            start_line=node.start_point[0] + 1,
                            end_line=node.end_point[0] + 1,
                        )
                    )
                    result.relationships.append(
                        Relationship(
                            source_id=current_parent_id,
                            target_id=func_id,
                            type=RelationshipType.CONTAINS,
                        )
                    )
                    for child in node.children:
                        walk(child, func_id, is_in_class=False)
                return

            # Extract Calls
            elif node.type == "call_expression":
                func_node = node.child_by_field_name("function")
                if func_node:
                    target_name = func_node.text.decode("utf-8")
                    if "." in target_name:
                        target_name = target_name.split(".")[-1]
                    result.raw_calls.append(
                        RawCall(
                            caller_id=current_parent_id,
                            target_name=target_name,
                            source_file=file_info.relative_path,
                            line=node.start_point[0] + 1,
                        )
                    )
            
            for child in node.children:
                walk(child, current_parent_id, is_in_class)

        walk(tree.root_node, file_id)
        return result
