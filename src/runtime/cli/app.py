"""KnowCode CLI.

The top-level Typer application providing the ``know`` command.
"""

from __future__ import annotations

import sys
from pathlib import Path

import structlog
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from runtime.exceptions.errors import KnowcodeError
from runtime.services.init_service import run_init
from runtime.services.status_service import run_status
from runtime.services.sync_service import run_sync
from runtime.cli.animation import BackgroundAnimator
from runtime.cli.auth import ensure_authenticated
from runtime.cli.telemetry import send_telemetry_async
import shutil

app = typer.Typer(
    name="knowcode",
    help="KnowCode Structural Cognition Engine",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()
animator = BackgroundAnimator()


def _capture_console_lines(renderable) -> list[str]:
    """Capture rich console output and split it into clean string lines constrained to right column."""
    if sys.stdout.isatty():
        cols, lines = shutil.get_terminal_size()
        if cols >= 80 and lines >= 14:
            right_width = max(20, cols - 35 - 4)
        else:
            right_width = max(20, cols - 4)
        from rich.console import Console as RichConsole

        temp_console = RichConsole(width=right_width, color_system=console.color_system)
    else:
        temp_console = console

    with temp_console.capture() as capture:
        temp_console.print(renderable)
    return capture.get().rstrip().split("\n")


def _update_animator(logger, method_name, event_dict):
    if animator and animator.running:
        animator.status = str(event_dict.get("event", "Processing..."))
    return event_dict


def _setup_logging() -> None:
    """Configure minimal JSON logging for the entire ecosystem."""
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(
            file=open("knowcode.log", "a", encoding="utf-8")
        ),
    )


_setup_logging()


def _handle_error(e: Exception) -> None:
    """Print an error nicely and exit."""
    if isinstance(e, KnowcodeError):
        console.print(f"[red]Error:[/red] {e}")
    else:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
    sys.exit(1)


@app.command(".")
def init_command() -> None:
    """Initialize a new KnowCode instance in the current repository."""
    try:
        ensure_authenticated()
    except Exception as e:
        _handle_error(e)

    animator.start()
    try:
        cwd = Path.cwd()
        result = run_init(cwd)
        panel = Panel.fit(
            f"[bold green]{result.message}[/bold green]\n"
            f"Structural Revision: [cyan]{result.structural_revision}[/cyan]\n"
            f"Initial Snapshot: [cyan]{result.snapshot_file}[/cyan]",
            title="KnowCode Initialization",
            border_style="green",
        )
        results_lines = _capture_console_lines(panel)
        animator.stop(final_status="Initialization complete.", results=results_lines)
        send_telemetry_async("init", "success")
    except Exception as e:
        animator.stop(final_status="Initialization failed.")
        send_telemetry_async("init", "failed")
        _handle_error(e)


@app.command("init")
def init_alias_command() -> None:
    """Initialize a new KnowCode instance in the current repository."""
    init_command()


@app.command("sync")
def sync_command() -> None:
    """Synchronize the KnowCode artifact with the current repository state."""
    try:
        ensure_authenticated()
    except Exception as e:
        _handle_error(e)

    animator.start()
    try:
        cwd = Path.cwd()
        result = run_sync(cwd)

        if not result.changes_detected:
            results_lines = _capture_console_lines(f"[green]✓[/green] {result.message}")
            animator.stop(final_status="Sync complete.", results=results_lines)
            send_telemetry_async("sync", "success")
            return

        table = Table(title="Sync Results", show_header=False)
        table.add_column("Key", style="dim")
        table.add_column("Value", style="cyan")

        table.add_row("Revision", result.structural_revision)
        table.add_row("Snapshot", result.snapshot_file)
        table.add_row("Report", result.report_file)
        table.add_row(
            "Components",
            ", ".join(result.affected_components)
            if result.affected_components
            else "None",
        )

        panel = Panel.fit(
            table, title="[bold green]Sync Complete[/bold green]", border_style="green"
        )
        results_lines = _capture_console_lines(panel)
        animator.stop(final_status="Sync complete.", results=results_lines)
        send_telemetry_async("sync", "success")

    except Exception as e:
        animator.stop(final_status="Sync failed.")
        send_telemetry_async("sync", "failed")
        _handle_error(e)


@app.command("status")
def status_command() -> None:
    """View the current status of the KnowCode instance."""
    try:
        ensure_authenticated()
    except Exception as e:
        _handle_error(e)

    animator.start()
    try:
        cwd = Path.cwd()
        result = run_status(cwd)

        table = Table(
            title=f"KnowCode Status: {result.repository_root}", show_header=False
        )
        table.add_column("Key", style="dim")
        table.add_column("Value", style="bold")

        table.add_row(
            "Initialized",
            "[green]Yes[/green]" if result.initialized else "[red]No[/red]",
        )
        table.add_row(
            "Structural Revision", f"[cyan]{result.structural_revision}[/cyan]"
        )
        table.add_row(
            "Semantic Revision", f"[magenta]{result.semantic_revision}[/magenta]"
        )
        table.add_row("Current Snapshot", result.current_snapshot)
        table.add_row("Latest Report", result.latest_report)

        last_sync = (
            result.last_sync.strftime("%Y-%m-%d %H:%M:%S UTC")
            if result.last_sync
            else "Never"
        )
        table.add_row("Last Sync", last_sync)

        results_lines = _capture_console_lines(table)
        animator.stop(final_status="Status retrieved.", results=results_lines)
        send_telemetry_async("status", "success")

    except Exception as e:
        animator.stop(final_status="Failed to get status.")
        send_telemetry_async("status", "failed")
        _handle_error(e)


@app.command("sync-semantic")
def sync_semantic_command() -> None:
    """Commit semantic changes and flush the active memory buffer."""
    try:
        ensure_authenticated()
    except Exception as e:
        _handle_error(e)

    animator.start()
    try:
        from runtime.services.semantic_sync_service import run_semantic_sync

        cwd = Path.cwd()
        result = run_semantic_sync(cwd)

        table = Table(title="Semantic Sync Results", show_header=False)
        table.add_column("Key", style="dim")
        table.add_column("Value", style="magenta")

        table.add_row("Revision", result.semantic_revision)
        table.add_row("Memory", "[dim]Flushed previous_context.md[/dim]")

        panel = Panel.fit(
            table,
            title=f"[bold magenta]✓ {result.message}[/bold magenta]",
            border_style="magenta",
        )
        results_lines = _capture_console_lines(panel)
        animator.stop(final_status="Semantic sync complete.", results=results_lines)
        send_telemetry_async("sync-semantic", "success")

    except Exception as e:
        animator.stop(final_status="Semantic sync failed.")
        send_telemetry_async("sync-semantic", "failed")
        _handle_error(e)


@app.command("ingest-semantic")
def ingest_semantic_command(
    target_file: str = typer.Argument(
        ..., help="Path to the raw file to ingest and remove, or '.' to process all."
    ),
) -> None:
    """Ingest a legacy document and bump the semantic revision."""
    animator.start()
    try:
        from runtime.services.ingest_service import run_ingest

        cwd = Path.cwd()
        result = run_ingest(cwd, target_file)
        animator.stop(final_status="Semantic ingest complete.")

        if result.semantic_revision == "No change":
            console.print(f"[yellow]ℹ {result.message}[/yellow]")
            return

        table = Table(title="Ingest Results", show_header=False)
        table.add_column("Key", style="dim")
        table.add_column("Value", style="magenta")

        table.add_row("Revision", result.semantic_revision)
        files_str = (
            ", ".join(result.deleted_files)
            if len(result.deleted_files) <= 3
            else f"{len(result.deleted_files)} files"
        )
        table.add_row("Memory", f"[dim]Flushed {files_str} from inbox[/dim]")

        console.print(
            Panel.fit(
                table,
                title=f"[bold magenta]✓ {result.message}[/bold magenta]",
                border_style="magenta",
            )
        )

    except Exception as e:
        animator.stop(final_status="Semantic ingest failed.")
        _handle_error(e)


@app.command("auth")
def auth_command() -> None:
    """Manage authentication and telemetry preferences."""
    from runtime.cli.auth import manage_auth
    try:
        manage_auth()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


if __name__ == "__main__":
    app()
