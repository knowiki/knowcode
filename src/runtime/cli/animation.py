"""Logo animation module for KnoWiki CLI."""

from __future__ import annotations

import math
import shutil
import sys
import threading
import time

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
WHITE = "\033[97m"
GRAY = "\033[90m"

LOGO_LINES = [
    "███████████████████████████████",
    "██                           ██",
    "██    ███████████████████    ██",
    "██    ███████▀   ▀███████    ██",
    "██    ███████▄   ▄███████    ██",
    "██    █████████ █████████    ██",
    "██    █████████ █████████    ██",
    "██    ███████▀   ▀███████    ██",
    "██    ███████▄   ▄███████    ██",
    "██    ███████████████████    ██",
    "██                           ██",
    "███████████████████████████████",
]

LXN = len(LOGO_LINES[0]) - 1
LYN = len(LOGO_LINES) - 1
TAGLINE = "KnoWiki"
VERSION = "v0.1.0"


def move_up(n: int) -> None:
    if n > 0:
        sys.stdout.write(f"\033[{n}A")


def write(s: str) -> None:
    sys.stdout.write(s)
    sys.stdout.flush()


class BackgroundAnimator:
    """Animate the KnoWiki logo in the background while tasks execute."""
    
    def __init__(self):
        self.status = "Starting..."
        self.running = False
        self._thread = None
        self.tagline_visible_chars = 0
        self.connector_visible_chars = 0
        self.last_height = None
        self.is_tty = sys.stdout.isatty()

    def start(self) -> None:
        """Start the animation in a background thread if running in an interactive terminal."""
        if not self.is_tty:
            return
            
        write(HIDE_CURSOR)
        
        cols, lines = shutil.get_terminal_size()
        
        # Reserve screen lines initially depending on terminal height
        if lines < 14 or cols < 50:
            self.last_height = 0
        elif 14 <= lines < 20:
            write("\n" * 14)
            self.last_height = 14
        else:
            write("\n" * 18)
            self.last_height = 18
            
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self, final_status: str = "Ready") -> None:
        """Stop the animation and print the final static state."""
        if not self.is_tty:
            return
            
        if self.running:
            self.status = final_status
            self.running = False
            if self._thread:
                self._thread.join()
            
            # Reposition to the top of our last frame before printing final state
            if self.last_height and self.last_height > 0:
                move_up(self.last_height)
            
            # Print final clean state
            self._print_final()
            
        write(SHOW_CURSOR)

    def _get_colored_char(self, char: str, x: int, y: int, R: float) -> str:
        if char == " ":
            return " "

        dx = (x - LXN / 2) * 0.6
        dy = y - LYN / 2
        d = math.sqrt(dx * dx + dy * dy)

        if d > R:
            return " "
        elif R - 1.5 < d <= R:
            theta = math.atan2(dy, dx)
            hue_idx = int(((theta + math.pi) / (2 * math.pi)) * 6) % 6
            colors = [
                "\033[1;91m",
                "\033[1;93m",
                "\033[1;92m",
                "\033[1;96m",
                "\033[1;94m",
                "\033[1;95m",
            ]
            return f"{colors[hue_idx]}{char}{RESET}"
        else:
            return f"{BOLD}{WHITE}{char}{RESET}"

    def _run(self) -> None:
        phase = 0
        R_max = 12.5
        cycle = 80

        while self.running:
            cols, lines = shutil.get_terminal_size()
            
            # Determine display mode based on terminal size
            if lines < 14 or cols < 50:
                mode = "single"
                current_height = 0
            elif 14 <= lines < 20:
                mode = "compact"
                current_height = 14
            else:
                mode = "full"
                current_height = 18

            # Move cursor back to the top of the previous frame
            if self.last_height and self.last_height > 0:
                move_up(self.last_height)

            if mode == "single":
                max_width = max(10, cols - 6)
                status_text = self.status
                if len(status_text) > max_width:
                    status_text = status_text[:max_width - 3] + "..."
                write(f"\r  ● {status_text:<{max_width}}")
            else:
                s = phase % cycle
                R = R_max * (1 - math.cos(s * math.pi / 40)) / 2

                buffer = []

                # Draw logo
                for y, line in enumerate(LOGO_LINES):
                    animated_line_chars = []
                    for x, char in enumerate(line):
                        animated_line_chars.append(self._get_colored_char(char, x, y, R))
                    buffer.append(f"  {''.join(animated_line_chars)}\n")

                # Type out tagline and version
                tagline_text = TAGLINE
                if self.tagline_visible_chars < len(tagline_text) and phase % 2 == 0:
                    self.tagline_visible_chars += 1
                visible_tagline = tagline_text[: self.tagline_visible_chars]

                version_text = ""
                if self.tagline_visible_chars == len(tagline_text):
                    version_text = f"    {DIM}{GRAY}{VERSION}{RESET}"

                if mode == "full":
                    buffer.append("\n")
                    buffer.append(f"  {GRAY}{visible_tagline}{RESET}{version_text}\n")
                    buffer.append("\n")

                    # Draw animated line connector
                    connector_text = "─" * 31
                    if self.tagline_visible_chars == len(tagline_text):
                        if self.connector_visible_chars < len(connector_text):
                            self.connector_visible_chars += 2
                            if self.connector_visible_chars > len(connector_text):
                                self.connector_visible_chars = len(connector_text)
                    visible_connector = connector_text[: self.connector_visible_chars]
                    buffer.append(f"  {GRAY}{visible_connector}{RESET}\n")
                    buffer.append("\n")
                else: # compact
                    buffer.append(f"  {GRAY}{visible_tagline}{RESET}{version_text}\n")

                # Print status line
                buffer.append(f"\r  {WHITE}● {self.status:<40}{RESET}\n")
                write("".join(buffer))

            self.last_height = current_height
            phase += 1
            time.sleep(0.035)

    def _print_final(self) -> None:
        cols, lines = shutil.get_terminal_size()
        
        if lines < 14 or cols < 50:
            max_width = max(10, cols - 6)
            status_text = self.status
            if len(status_text) > max_width:
                status_text = status_text[:max_width - 3] + "..."
            write(f"\r  {WHITE}✔ {status_text:<{max_width}}{RESET}\n")
        elif 14 <= lines < 20: # compact
            buffer = []
            for line in LOGO_LINES:
                buffer.append(f"  {BOLD}{WHITE}{line}{RESET}\n")
            buffer.append(f"  {GRAY}{TAGLINE}{RESET}    {DIM}{GRAY}{VERSION}{RESET}\n")
            buffer.append(f"\r  {WHITE}✔ {self.status:<40}{RESET}\n")
            write("".join(buffer))
        else: # full
            buffer = []
            for line in LOGO_LINES:
                buffer.append(f"  {BOLD}{WHITE}{line}{RESET}\n")
            buffer.append("\n")
            buffer.append(f"  {GRAY}{TAGLINE}{RESET}    {DIM}{GRAY}{VERSION}{RESET}\n")
            buffer.append("\n")
            buffer.append(f"  {GRAY}{'─' * 31}{RESET}\n")
            buffer.append("\n")
            buffer.append(f"\r  {WHITE}✔ {self.status:<40}{RESET}\n")
            write("".join(buffer))
