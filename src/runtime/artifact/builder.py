"""Artifact Builder.

Scaffolds the initial ``.knowcode/`` directory structure and renders
static, human-facing knowledge templates.

Invariants
----------
- **ZERO State Awareness:** This module never touches, reads, or writes
  ``state.yaml``. State management belongs exclusively to the Structural Engine.
- **Idempotency:** Re-running the builder over an existing initialized
  directory will safely assert directories exist without destructive overwrites,
  although the Validator usually prevents this.
"""

from __future__ import annotations

import jinja2
import structlog
from importlib import resources

from runtime.repository.models import RepositoryPaths

logger = structlog.get_logger(__name__)


class ArtifactBuilder:
    """Scaffolds the KnowCode artifact directory structure."""

    def __init__(self, paths: RepositoryPaths) -> None:
        """Initialize the builder.

        Parameters
        ----------
        paths : RepositoryPaths
            The canonical path contract for the repository.
        """
        self.paths = paths
        # Setup Jinja2 environment loading templates from the runtime package
        self.jinja_env = jinja2.Environment(
            loader=jinja2.PackageLoader("runtime", "templates"),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def build(self) -> None:
        """Execute the scaffolding pipeline.

        Creates all required directories and renders static templates.
        """
        logger.info("artifact_builder.started", knowcode_root=str(self.paths.knowcode_root))

        self._create_directories()
        self._render_templates()

        logger.info("artifact_builder.complete")

    def _create_directories(self) -> None:
        """Create the directory tree."""
        # Define all required subdirectories
        dirs_to_create = [
            self.paths.knowcode_root,
            self.paths.structure_dir,
            self.paths.snapshots_dir,
            self.paths.reports_dir,
            self.paths.logs_dir,
            self.paths.knowledge_dir,
            self.paths.knowledge_dir / "architecture",
            self.paths.knowledge_dir / "decisions",
            self.paths.knowledge_dir / "constraints",
            self.paths.knowledge_dir / "conventions",
            self.paths.knowledge_dir / "components",
            self.paths.agent_dir,
            self.paths.skills_dir,
            self.paths.workflows_dir,
            self.paths.memory_dir,
            self.paths.raw_knowledge_dir,
        ]

        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug("artifact_builder.mkdir", path=str(directory))

    def _render_templates(self) -> None:
        """Render and write static markdown templates."""
        # 1. Render README_STRUCTURE.md (formerly KNOWCODE.md)
        struct_template = self.jinja_env.get_template("README_STRUCTURE.md.j2")
        project_name = self.paths.repo_root.name
        
        struct_content = struct_template.render(project_name=project_name)
        struct_file = self.paths.knowcode_root / "README_STRUCTURE.md"
        struct_file.write_text(struct_content, encoding="utf-8")
        logger.debug("artifact_builder.render", file=str(struct_file))

        # 2. Render README_KNOWLEDGE.md (formerly knowledge-maintenance.md)
        km_template = self.jinja_env.get_template("README_KNOWLEDGE.md.j2")
        km_content = km_template.render()
        
        km_file = self.paths.knowledge_dir / "README_KNOWLEDGE.md"
        km_file.write_text(km_content, encoding="utf-8")
        logger.debug("artifact_builder.render", file=str(km_file))

        # 3. Render placeholder README.md files for knowledge subdirectories
        knowledge_subdirs = {
            "architecture": "Architecture",
            "decisions": "Decisions",
            "constraints": "Constraints",
            "conventions": "Conventions",
            "components": "Components",
        }
        for dirname, title in knowledge_subdirs.items():
            readme_path = self.paths.knowledge_dir / dirname / f"{dirname}.md"
            readme_path.write_text(f"# {title}\n\n", encoding="utf-8")
            logger.debug("artifact_builder.render", file=str(readme_path))

        # 4. Render raw inbox README
        raw_template = self.jinja_env.get_template("raw_readme.md.j2")
        raw_content = raw_template.render()
        raw_file = self.paths.raw_knowledge_dir / "README.md"
        raw_file.write_text(raw_content, encoding="utf-8")
        logger.debug("artifact_builder.render", file=str(raw_file))

        # 5. Render active_context.md
        ac_template = self.jinja_env.get_template("active_context.md.j2")
        ac_content = ac_template.render()
        self.paths.active_context_file.write_text(ac_content, encoding="utf-8")
        logger.debug("artifact_builder.render", file=str(self.paths.active_context_file))

        # 6. Render knowcode.md (Agent Loader)
        loader_template = self.jinja_env.get_template("KNOWCODE_LOADER.md.j2")
        loader_content = loader_template.render()
        loader_file = self.paths.repo_root / "knowcode.md"
        loader_file.write_text(loader_content, encoding="utf-8")
        logger.debug("artifact_builder.render", file=str(loader_file))

        # 7. Render Skills
        skills = {
            "track_intent.md.j2": "track_intent.md",
            "synthesize_knowledge.md.j2": "synthesize_knowledge.md"
        }
        for template_name, file_name in skills.items():
            template = self.jinja_env.get_template(template_name)
            file_path = self.paths.skills_dir / file_name
            file_path.write_text(template.render(), encoding="utf-8")
            logger.debug("artifact_builder.render", file=str(file_path))

        # 8. Render Workflows
        workflows = {
            "sync_reconciliation.md.j2": "sync_reconciliation.md",
            "ingest_legacy.md.j2": "ingest_legacy.md"
        }
        for template_name, file_name in workflows.items():
            template = self.jinja_env.get_template(template_name)
            file_path = self.paths.workflows_dir / file_name
            file_path.write_text(template.render(), encoding="utf-8")
            logger.debug("artifact_builder.render", file=str(file_path))
