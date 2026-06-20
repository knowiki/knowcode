"""Python structural extractor.

Walks a Python tree-sitter AST to extract entities, relationships,
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

class PythonAdapter(LanguageAdapter):
    """AST extractor for Python."""

    def extract(
        self, file_info: FileInfo, tree: tree_sitter.Tree, source_bytes: bytes
    ) -> ExtractionResult:
        result = ExtractionResult()

        file_id = file_info.relative_path
        file_entity = Entity(
            id=file_id,
            type=EntityType.FILE,
            name=file_info.absolute_path.name,
            path=file_info.relative_path,
            parent_id=str(file_info.absolute_path.parent.relative_to(file_info.absolute_path.parents[len(file_info.relative_path.split("/")) - 1])) if "/" in file_info.relative_path else "repo", # Actually let's just make the parser build the directories later or assign properly. Let's simplify and make the caller build dir entities. Or build them here if needed.
            start_line=1,
            end_line=source_bytes.count(b"\n") + 1,
        )
        result.entities.append(file_entity)
        
        # Let's fix parent_id for file. The parser.py should probably assemble Repository and Directory entities.
        # But we'll leave it as None for now and let the caller fix it, or we can just say parent_id is the directory.
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
        result.entities[-1] = file_entity

        def walk(node: tree_sitter.Node, current_parent_id: str, is_in_class: bool = False):
            # Extract Imports
            if node.type == "import_statement":
                for child in node.children:
                    if child.type == "dotted_name":
                        imported_module = child.text.decode("utf-8")
                        result.relationships.append(
                            Relationship(
                                source_id=file_id,
                                target_id=imported_module, # This will be resolved conservatively later, but for now we record it as is. Wait, IMPORTS should target the module id.
                                type=RelationshipType.IMPORTS,
                            )
                        )
            elif node.type == "import_from_statement":
                module_node = node.child_by_field_name("module_name")
                if module_node:
                    module_name = module_node.text.decode("utf-8")
                    result.relationships.append(
                        Relationship(
                            source_id=file_id,
                            target_id=module_name,
                            type=RelationshipType.IMPORTS,
                        )
                    )

            # Extract Classes
            elif node.type == "class_definition":
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = name_node.text.decode("utf-8")
                    class_id = f"{current_parent_id}::{name}"
                    
                    result.entities.append(
                        Entity(
                            id=class_id,
                            type=EntityType.CLASS,
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
                            target_id=class_id,
                            type=RelationshipType.CONTAINS,
                        )
                    )
                    
                    # Extract Base Classes (INHERITS)
                    superclasses = node.child_by_field_name("superclasses")
                    if superclasses:
                        for child in superclasses.children:
                            if child.type == "identifier" or child.type == "attribute":
                                base_name = child.text.decode("utf-8")
                                result.relationships.append(
                                    Relationship(
                                        source_id=class_id,
                                        target_id=base_name, # Raw target, we may need to resolve it, but INHERITS is usually raw or we can use the same resolver.
                                        type=RelationshipType.INHERITS,
                                    )
                                )

                    for child in node.children:
                        walk(child, class_id, is_in_class=True)
                return

            # Extract Functions/Methods
            elif node.type == "function_definition":
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = name_node.text.decode("utf-8")
                    func_id = f"{current_parent_id}::{name}"
                    func_type = EntityType.METHOD if is_in_class else EntityType.FUNCTION
                    
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
            elif node.type == "call":
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
