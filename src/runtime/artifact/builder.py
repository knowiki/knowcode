"""Artifact Builder.

Scaffolds the initial ``.brain/`` directory structure and renders
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
    """Scaffolds the Brain artifact directory structure."""

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
        logger.info("artifact_builder.started", brain_root=str(self.paths.brain_root))

        self._create_directories()
        self._render_templates()

        logger.info("artifact_builder.complete")

    def _create_directories(self) -> None:
        """Create the directory tree."""
        # Define all required subdirectories
        dirs_to_create = [
            self.paths.brain_root,
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
            self.paths.agent_root,
            self.paths.skills_dir,
            self.paths.workflows_dir,
            self.paths.memory_dir,
            self.paths.system_skills_dir,
        ]

        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug("artifact_builder.mkdir", path=str(directory))

    def _render_templates(self) -> None:
        """Render and write static markdown templates."""
        # 1. Render BRAIN.md
        brain_template = self.jinja_env.get_template("BRAIN.md.j2")
        # Use the name of the repository root directory as the project name
        project_name = self.paths.repo_root.name
        
        brain_content = brain_template.render(project_name=project_name)
        self.paths.brain_file.write_text(brain_content, encoding="utf-8")
        logger.debug("artifact_builder.render", file=str(self.paths.brain_file))

        # 2. Render knowledge-maintenance.md
        km_template = self.jinja_env.get_template("knowledge-maintenance.md.j2")
        km_content = km_template.render()
        
        km_file = self.paths.knowledge_dir / "knowledge-maintenance.md"
        km_file.write_text(km_content, encoding="utf-8")
        logger.debug("artifact_builder.render", file=str(km_file))

        # 3. Render example-skill.md
        skill_template = self.jinja_env.get_template("example-skill.md.j2")
        skill_content = skill_template.render()
        skill_file = self.paths.skills_dir / "example-skill.md"
        skill_file.write_text(skill_content, encoding="utf-8")
        logger.debug("artifact_builder.render", file=str(skill_file))

        # 4. Render example-workflow.md
        workflow_template = self.jinja_env.get_template("example-workflow.md.j2")
        workflow_content = workflow_template.render()
        workflow_file = self.paths.workflows_dir / "example-workflow.md"
        workflow_file.write_text(workflow_content, encoding="utf-8")
        logger.debug("artifact_builder.render", file=str(workflow_file))

        # 5. Render placeholder README.md files for knowledge subdirectories
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

        # 6. Render active_context.md
        ac_template = self.jinja_env.get_template("active_context.md.j2")
        ac_content = ac_template.render()
        self.paths.active_context_file.write_text(ac_content, encoding="utf-8")
        logger.debug("artifact_builder.render", file=str(self.paths.active_context_file))

        # 7. Render context_tracker.md
        ct_template = self.jinja_env.get_template("context_tracker.md.j2")
        ct_content = ct_template.render()
        ct_file = self.paths.system_skills_dir / "context_tracker.md"
        ct_file.write_text(ct_content, encoding="utf-8")
        logger.debug("artifact_builder.render", file=str(ct_file))
