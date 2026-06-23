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
COLORS = [
    "\033[1;91m",
    "\033[1;93m",
    "\033[1;92m",
    "\033[1;96m",
    "\033[1;94m",
    "\033[1;95m",
]

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

try:
    from importlib.metadata import version as get_version
    VERSION = f"v{get_version('knowcode')}"
except Exception:
    VERSION = "v0.1.8"


def move_up(n: int) -> None:
    if n > 0:
        sys.stdout.write(f"\033[{n}A")


def write(s: str) -> None:
    sys.stdout.write(s)
    sys.stdout.flush()


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

        # Precompute logo grid to speed up rendering
        self._precomputed_logo = []
        for y, line in enumerate(LOGO_LINES):
            row_data = []
            for x, char in enumerate(line):
                if char == " ":
                    row_data.append((" ", 0.0, " ", " "))
                else:
                    dx = (x - LXN / 2) * 0.6
                    dy = y - LYN / 2
                    d = math.sqrt(dx * dx + dy * dy)
                    theta = math.atan2(dy, dx)
                    hue_idx = int(((theta + math.pi) / (2 * math.pi)) * 6) % 6
                    ring_str = f"{COLORS[hue_idx]}{char}{RESET}"
                    inner_str = f"{BOLD}{WHITE}{char}{RESET}"
                    row_data.append((char, d, ring_str, inner_str))
            self._precomputed_logo.append(row_data)

    def start(self) -> None:
        """Start the animation in a background thread if running in an interactive terminal."""
        if not self.is_tty:
            return

        write(HIDE_CURSOR)

        cols, lines = shutil.get_terminal_size()

        # Reserve screen lines initially depending on terminal size
        if lines < 15 or cols < 70:
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

            # Enforce a minimum animation duration so the reveal is visible
            while self.phase < 35 and self._thread and self._thread.is_alive():
                time.sleep(0.03)

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

    def _run(self) -> None:
        self.phase = 0
        R_max = 10.5
        cycle = 76

        try:
            cols, lines = shutil.get_terminal_size()
            while self.running:
                # Query terminal size periodically to reduce overhead
                if self.phase % 10 == 0:
                    cols, lines = shutil.get_terminal_size()

                # Determine display mode based on terminal size
                if lines < 15 or cols < 70:
                    mode = "single"
                    current_height = 0
                else:
                    mode = "full"
                    current_height = LOGO_HEIGHT + 1

                frame_buffer = []

                # Move cursor back to the top of the previous frame
                if self.last_height and self.last_height > 0:
                    frame_buffer.append(f"\033[{self.last_height}A")
                    if current_height < self.last_height:
                        frame_buffer.append("\033[J")

                if mode == "single":
                    max_width = max(10, cols - 6)
                    status_text = self.status
                    if len(status_text) > max_width:
                        status_text = status_text[: max_width - 3] + "..."
                    frame_buffer.append(f"\r  ● {status_text:<{max_width}}\033[K")
                else:
                    s = self.phase % cycle
                    # Linear triangle wave for constant speed and zero peak/trough lag
                    half_cycle = cycle / 2
                    if s < half_cycle:
                        R = R_max * (s / half_cycle)
                    else:
                        R = R_max * (2.0 - s / half_cycle)

                    left_lines = []
                    for row in self._precomputed_logo:
                        animated_line_chars = []
                        for item in row:
                            d = item[1]
                            if d > R:
                                animated_line_chars.append(" ")
                            elif R - 2.0 < d <= R:
                                animated_line_chars.append(item[2])
                            else:
                                animated_line_chars.append(item[3])
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

                    frame_buffer.append("\n")
                    max_len = max(len(left_lines), len(right_lines))
                    for i in range(max_len):
                        if i < len(left_lines):
                            left = left_lines[i] + "    "
                        else:
                            left = " " * LEFT_BLOCK_WIDTH
                        right = right_lines[i] if i < len(right_lines) else ""
                        frame_buffer.append(f"{left}{right}\033[K\n")

                write("".join(frame_buffer))
                self.last_height = current_height
                self.phase += 1
                time.sleep(0.025)
        except Exception as e:
            # Safely log exception and stop the thread if writing fails
            with open("animation_error.log", "a", encoding="utf-8") as f:
                f.write(f"Animation thread crashed: {e}\n")
            self.running = False

    def _print_final(self, results: list[str] | None = None) -> None:
        cols, lines = shutil.get_terminal_size()

        if lines < 15 or cols < 70:
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
                if i < len(left_lines):
                    left = left_lines[i] + "    "
                else:
                    left = " " * LEFT_BLOCK_WIDTH
                right = right_lines[i] if i < len(right_lines) else ""
                buffer.append(f"{left}{right}\n")

            write("".join(buffer))
