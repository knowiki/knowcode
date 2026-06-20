"""Brain CLI.

The top-level Typer application providing the ``brain`` command.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from runtime.exceptions.errors import BrainError
from runtime.services.init_service import run_init
from runtime.services.status_service import run_status
from runtime.services.sync_service import run_sync

app = typer.Typer(
    name="brain",
    help="KnoWiki Structural Cognition Engine",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def _handle_error(e: Exception) -> None:
    """Print an error nicely and exit."""
    if isinstance(e, BrainError):
        console.print(f"[red]Error:[/red] {e}")
    else:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
    sys.exit(1)


@app.command(".")
def init_command() -> None:
    """Initialize a new Brain instance in the current repository."""
    try:
        cwd = Path.cwd()
        result = run_init(cwd)
        
        console.print(
            Panel.fit(
                f"[bold green]{result.message}[/bold green]\n"
                f"Structural Revision: [cyan]{result.structural_revision}[/cyan]\n"
                f"Initial Snapshot: [cyan]{result.snapshot_file}[/cyan]",
                title="Brain Initialization",
                border_style="green",
            )
        )
    except Exception as e:
        _handle_error(e)


@app.command("sync")
def sync_command() -> None:
    """Synchronize the Brain artifact with the current repository state."""
    try:
        cwd = Path.cwd()
        result = run_sync(cwd)
        
        if not result.changes_detected:
            console.print(f"[green]✓[/green] {result.message}")
            return
            
        table = Table(title="Sync Results", show_header=False)
        table.add_column("Key", style="dim")
        table.add_column("Value", style="cyan")
        
        table.add_row("Revision", result.structural_revision)
        table.add_row("Snapshot", result.snapshot_file)
        table.add_row("Report", result.report_file)
        table.add_row("Components", ", ".join(result.affected_components) if result.affected_components else "None")
        
        console.print(Panel.fit(table, title="[bold green]Sync Complete[/bold green]", border_style="green"))
        
    except Exception as e:
        _handle_error(e)


@app.command("status")
def status_command() -> None:
    """View the current status of the Brain instance."""
    try:
        cwd = Path.cwd()
        result = run_status(cwd)
        
        table = Table(title=f"Brain Status: {result.repository_root}", show_header=False)
        table.add_column("Key", style="dim")
        table.add_column("Value", style="bold")
        
        table.add_row("Initialized", "[green]Yes[/green]" if result.initialized else "[red]No[/red]")
        table.add_row("Structural Revision", f"[cyan]{result.structural_revision}[/cyan]")
        table.add_row("Semantic Revision", f"[magenta]{result.semantic_revision}[/magenta]")
        table.add_row("Current Snapshot", result.current_snapshot)
        table.add_row("Latest Report", result.latest_report)
        
        last_sync = result.last_sync.strftime("%Y-%m-%d %H:%M:%S UTC") if result.last_sync else "Never"
        table.add_row("Last Sync", last_sync)
        
        console.print(table)
        
    except Exception as e:
        _handle_error(e)


if __name__ == "__main__":
    app()
