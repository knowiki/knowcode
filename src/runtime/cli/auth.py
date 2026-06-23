"""Authentication and configuration module for KnowCode CLI."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from platformdirs import user_config_dir
import typer
import questionary
from rich.console import Console
from runtime.exceptions.errors import KnowcodeError

CONFIG_DIR = Path(user_config_dir("knowcode"))
CONFIG_FILE = CONFIG_DIR / "config.json"


def save_access_key(key: str) -> None:
    """Save the beta tester access key to the user config file."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config_data = {}
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                pass

        config_data["access_key"] = key.strip()

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
    except Exception:
        pass


def clear_access_key() -> None:
    """Clear the stored access key from the user config file."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            if "access_key" in config_data:
                del config_data["access_key"]
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=4)
    except Exception:
        pass


def get_access_key() -> str | None:
    """Retrieve the stored access key, or None if not authenticated."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            return config_data.get("access_key")
    except Exception:
        pass
    return None


def validate_access_key(key: str) -> bool:
    """Validate the access key with the backend database."""
    if not key or not key.strip():
        return False

    try:
        from runtime.cli.telemetry import API_BASE_URL

        url = f"{API_BASE_URL}/api/auth/validate"
        data = json.dumps({"key": key.strip()}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "knowcode-cli-auth",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2.0) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data.get("valid", False)
    except urllib.error.HTTPError as e:
        try:
            res_data = json.loads(e.read().decode("utf-8"))
            return res_data.get("valid", False)
        except Exception:
            return False
    except Exception:
        # Network connection error or timeout. We treat this as valid to avoid blocking offline users.
        return True


def ensure_authenticated() -> str:
    """Ensure the user is authenticated with a valid access key.
    Prompts the user if missing or invalid.
    """
    console = Console()
    access_key = get_access_key()

    if access_key:
        if access_key == "opt-out":
            return access_key

        if validate_access_key(access_key):
            return access_key
        else:
            console.print(
                "[yellow]Stored access key is invalid. Please re-enter.[/yellow]"
            )

    while True:
        if sys.stdout.isatty():
            console.print(
                "\n[dim]Privacy Notice: We collect command usage and demographic data to improve KnowCode.\n"
                "No codebase information is ever collected. If you opt out, no usage data will be collected.[/dim]"
            )
            
            choice = questionary.select(
                "How would you like to proceed?",
                choices=[
                    "Enter Access Key",
                    "Opt-out of Telemetry"
                ]
            ).ask()
            
            if choice == "Opt-out of Telemetry":
                save_access_key("opt-out")
                console.print("[dim]Opted out of telemetry. No access code provided.[/dim]\n")
                return "opt-out"
            elif choice == "Enter Access Key":
                access_key = typer.prompt("Enter your access code")
                if validate_access_key(access_key):
                    save_access_key(access_key)
                    console.print("[green]Access code verified successfully.[/green]")
                    return access_key
                else:
                    console.print("[red]Invalid access code. Please try again.[/red]")
            else:
                raise KnowcodeError("Authentication aborted.")
        else:
            raise KnowcodeError(
                "Access code is missing or invalid, and terminal is not interactive."
            )

def manage_auth() -> None:
    """Manage authentication settings interactively (used by 'know auth')."""
    console = Console()
    access_key = get_access_key()
    
    if access_key:
        if not sys.stdout.isatty():
            console.print("Authentication preferences already set.")
            return
            
        status = "Opted out of telemetry" if access_key == "opt-out" else "Authenticated with Access Key"
        console.print(f"\n[bold cyan]Current Status:[/bold cyan] {status}")
        
        choice = questionary.select(
            "Would you like to change your preferences?",
            choices=["Yes, change preferences", "No, exit"]
        ).ask()
        
        if choice == "Yes, change preferences":
            clear_access_key()
            ensure_authenticated()
        else:
            return
    else:
        ensure_authenticated()
