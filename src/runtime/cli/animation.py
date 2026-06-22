"""Logo animation module for KnowCode CLI."""

from __future__ import annotations

import math
import re
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
    "███████████████████████████",
    "██                       ██",
    "██    ███████████████    ██",
    "██    █████▀   ▀█████    ██",
    "██    █████▄   ▄█████    ██",
    "██    ███████ ███████    ██",
    "██    █████▀   ▀█████    ██",
    "██    █████▄   ▄█████    ██",
    "██    ███████████████    ██",
    "██                       ██",
    "███████████████████████████",
]

LOGO_HEIGHT = len(LOGO_LINES)
LOGO_WIDTH = len(LOGO_LINES[0])
LEFT_BLOCK_WIDTH = LOGO_WIDTH + 6

LXN = LOGO_WIDTH - 1
LYN = LOGO_HEIGHT - 1
TAGLINE = "KnowCode"
VERSION = "v0.1.0"


def move_up(n: int) -> None:
    if n > 0:
        sys.stdout.write(f"\033[{n}A")


def write(s: str) -> None:
    sys.stdout.write(s)
    sys.stdout.flush()


ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def visible_len(s: str) -> int:
    """Calculate the printed length of a string, excluding ANSI escape sequences."""
    return len(ANSI_ESCAPE.sub("", s))


def pad_left(s: str, width: int) -> str:
    """Pad a string to a specific visible width by appending spaces."""
    v_len = visible_len(s)
    if v_len < width:
        return s + " " * (width - v_len)
    return s


class BackgroundAnimator:
    """Animate the KnowCode logo in the background while tasks execute."""

    def __init__(self):
        self.status = "Starting..."
        self.running = False
        self._thread = None
        self.tagline_visible_chars = 0
        self.connector_visible_chars = 0
        self.last_height = None
        self.is_tty = sys.stdout.isatty()
        self.phase = 0

    def start(self) -> None:
        """Start the animation in a background thread if running in an interactive terminal."""
        if not self.is_tty:
            return

        write(HIDE_CURSOR)

        cols, lines = shutil.get_terminal_size()

        # Reserve screen lines initially depending on terminal size
        if lines < LOGO_HEIGHT + 2 or cols < 74:
            self.last_height = 0
        else:
            write("\n" * (LOGO_HEIGHT + 1))
            self.last_height = LOGO_HEIGHT + 1

        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(
        self, final_status: str = "Ready", results: list[str] | None = None
    ) -> None:
        """Stop the animation and print the final static state."""
        if not self.is_tty:
            if results:
                for r_line in results:
                    write(f"{r_line}\n")
            return

        if self.running:
            self.status = final_status

            # Enforce a minimum animation duration (up to phase 40, approx 1.4s)
            # so that the circular reveal animation has time to be visible
            while self.phase < 40:
                time.sleep(0.05)

            self.running = False
            if self._thread:
                self._thread.join()

            # Reposition to the top of our last frame before printing final state
            if self.last_height and self.last_height > 0:
                move_up(self.last_height)
                write("\033[J")

            # Print final clean state
            self._print_final(results)

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
        self.phase = 0
        R_max = 12.5
        cycle = 80

        while self.running:
            cols, lines = shutil.get_terminal_size()

            # Determine display mode based on terminal size
            if lines < LOGO_HEIGHT + 2 or cols < 74:
                mode = "single"
                current_height = 0
            else:
                mode = "full"
                current_height = LOGO_HEIGHT + 1

            # Move cursor back to the top of the previous frame
            if self.last_height and self.last_height > 0:
                move_up(self.last_height)
                if current_height < self.last_height:
                    write("\033[J")

            if mode == "single":
                max_width = max(10, cols - 6)
                status_text = self.status
                if len(status_text) > max_width:
                    status_text = status_text[: max_width - 3] + "..."
                write(f"\r  ● {status_text:<{max_width}}")
            else:
                s = self.phase % cycle
                R = R_max * (1 - math.cos(s * math.pi / 40)) / 2

                left_lines = []
                for y, line in enumerate(LOGO_LINES):
                    animated_line_chars = []
                    for x, char in enumerate(line):
                        animated_line_chars.append(
                            self._get_colored_char(char, x, y, R)
                        )
                    left_lines.append(f"  {''.join(animated_line_chars)}")

                # Tagline and active status side-by-side components on the right
                right_width = cols - LEFT_BLOCK_WIDTH - 4
                status_max = max(15, right_width - 2)
                status_text = self.status
                if len(status_text) > status_max:
                    status_text = status_text[: status_max - 3] + "..."

                separator_len = min(31, right_width)
                right_lines = [
                    f"{GRAY}{TAGLINE}    {DIM}{GRAY}{VERSION}{RESET}",
                    f"{GRAY}{'─' * separator_len}{RESET}",
                    "",
                    f"{WHITE}● {status_text:<{status_max}}{RESET}",
                ]

                buffer = ["\n"]
                max_len = max(len(left_lines), len(right_lines))
                for i in range(max_len):
                    left = (
                        left_lines[i] if i < len(left_lines) else " " * LEFT_BLOCK_WIDTH
                    )
                    right = right_lines[i] if i < len(right_lines) else ""
                    buffer.append(f"{pad_left(left, LEFT_BLOCK_WIDTH)}{right}\n")

                write("".join(buffer))

            self.last_height = current_height
            self.phase += 1
            time.sleep(0.035)

    def _print_final(self, results: list[str] | None = None) -> None:
        cols, lines = shutil.get_terminal_size()

        if lines < LOGO_HEIGHT + 4 or cols < 80:
            max_width = max(10, cols - 6)
            status_text = self.status
            if len(status_text) > max_width:
                status_text = status_text[: max_width - 3] + "..."
            write(f"\r  {WHITE}✔ {status_text:<{max_width}}{RESET}\n")
            if results:
                for r_line in results:
                    write(f"{r_line}\n")
        else:
            left_lines = []
            for line in LOGO_LINES:
                left_lines.append(f"  {BOLD}{WHITE}{line}{RESET}")

            right_width = cols - LEFT_BLOCK_WIDTH - 4
            status_max = max(15, right_width - 2)
            status_text = self.status
            if len(status_text) > status_max:
                status_text = status_text[: status_max - 3] + "..."

            separator_len = min(31, right_width)
            right_lines = [
                f"{GRAY}{TAGLINE}    {DIM}{GRAY}{VERSION}{RESET}",
                f"{GRAY}{'─' * separator_len}{RESET}",
                "",
                f"{WHITE}✔ {status_text:<{status_max}}{RESET}",
                "",
            ]
            if results:
                right_lines.extend(results)

            buffer = ["\n"]
            max_len = max(len(left_lines), len(right_lines))
            for i in range(max_len):
                left = left_lines[i] if i < len(left_lines) else " " * LEFT_BLOCK_WIDTH
                right = right_lines[i] if i < len(right_lines) else ""
                buffer.append(f"{pad_left(left, LEFT_BLOCK_WIDTH)}{right}\n")

            write("".join(buffer))
