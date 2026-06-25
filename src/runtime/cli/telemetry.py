"""Telemetry logging module for KnowCode CLI."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from runtime.cli.auth import get_access_key

# Default local API URL, overrideable via env var
API_BASE_URL = os.environ.get("KNOWIKI_API_URL", "https://api.knowiki.in")
TELEMETRY_ENDPOINT = f"{API_BASE_URL}/api/telemetry"


def _send_telemetry_sync(
    command: str, status: str, project_id: str, access_key: str
) -> None:
    """Send the POST request synchronously. Runs inside the background process."""
    import urllib.request

    try:
        payload = {
            "access_key": access_key,
            "command": command,
            "status": status,
            "project_id": project_id,
        }
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            TELEMETRY_ENDPOINT,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "knowcode-cli-telemetry",
            },
            method="POST",
        )

        # We can use a longer timeout here because it runs detached
        with urllib.request.urlopen(req, timeout=5.0) as response:
            pass
    except Exception:
        pass


def send_telemetry_async(command: str, status: str) -> None:
    """Dispatches command execution metrics to the backend in a detached background process."""
    if (
        "PYTEST_CURRENT_TEST" in os.environ
        or os.environ.get("KNOWCODE_TESTING") == "true"
    ):
        return

    try:
        access_key = get_access_key()
        if not access_key or access_key == "opt-out":
            return  # Skip telemetry if the user is not authenticated or opted out

        # Compute an anonymous hash of the current repository root to identify unique projects safely
        try:
            cwd_str = str(Path.cwd().resolve())
            project_id = hashlib.sha256(cwd_str.encode("utf-8")).hexdigest()[:16]
        except Exception:
            project_id = "unknown"

        # Dispatch the network request in a separate process so the CLI exits instantly.
        # We use CREATE_NO_WINDOW on Windows to ensure it runs completely independent
        # of the parent process and keeps running after the parent exits, without showing console windows.
        # (Note: Windows ignores CREATE_NO_WINDOW if combined with DETACHED_PROCESS, causing window flashes)
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        startupinfo = None
        if sys.platform == "win32":
            creation_flags |= 0x01000000  # CREATE_BREAKAWAY_FROM_JOB
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = getattr(subprocess, "SW_HIDE", 0)

        if getattr(sys, "frozen", False):
            # Standalone binary runner: invoke the built-in hidden command
            args = [
                sys.executable,
                "telemetry-worker",
                command,
                status,
                project_id,
                access_key,
            ]
        else:
            # Standard Python environment: execute python on telemetry.py script
            args = [sys.executable, __file__, command, status, project_id, access_key]



        child_env = os.environ.copy()
        # Remove PyInstaller specific environment variables from the child process.
        # This prevents the child from conflicting with the parent's temporary folder
        # environment and forces it to initialize its own execution context cleanly.
        for key in list(child_env.keys()):
            if key.startswith("_PYI_"):
                child_env.pop(key, None)

        try:
            subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=creation_flags,
                close_fds=False,
                env=child_env,
                startupinfo=startupinfo,
            )
        except Exception as e:
            # If CREATE_BREAKAWAY_FROM_JOB failed (e.g. WinError 5 Access is denied due to environment constraints),
            # fall back to spawning without it.
            if sys.platform == "win32" and (creation_flags & 0x01000000):
                creation_flags &= ~0x01000000
                subprocess.Popen(
                    args,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    creationflags=creation_flags,
                    close_fds=False,
                    env=child_env,
                    startupinfo=startupinfo,
                )
            else:
                raise e
        
        # Give the operating system a brief moment (200ms) to initialize the child process
        # before the parent exits, preventing premature termination.
        import time
        time.sleep(0.2)
    except Exception:
        pass


if __name__ == "__main__":
    if len(sys.argv) == 5:
        _, cmd, stat, proj, key = sys.argv
        _send_telemetry_sync(cmd, stat, proj, key)
