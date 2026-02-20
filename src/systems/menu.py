"""Menu system for main menu and pause screen."""
import select
import sys
import termios
import tty
from enum import Enum, auto

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class MenuResult(Enum):
    PLAY = auto()
    RESUME = auto()
    QUIT = auto()


TITLE_ART = r"""
 _____ ___ __  ______ _  _  ____     ___  ____
|_   _| __|\ \/ /_  _| || ||  __|   / _ \|  __|
  | | | _|  >  <  | | | || || _|   | | | | _|
  |_| |___|/_/\_\ |_| |__||_||_|   |_| |_|_|

 ___  ____  ___   __    __    ___
|_ _|/ ___||   | /  \  /  \  |  __|
 | | \___ \| | || || || || | | _|
|___||____/|___| \__/  \__/  |___|
"""

SUBTITLE = "A TUI Bullet-Hell Roguelike"


class MenuSystem:
    """Handles main menu and pause menu rendering and input."""

    def __init__(self, console: Console):
        self.console = console
        self._fd: int | None = None
        self._old_settings = None
        try:
            self._fd = sys.stdin.fileno()
            if sys.stdin.isatty():
                self._old_settings = termios.tcgetattr(self._fd)
        except Exception:
            # stdin is not a real terminal (e.g. in tests or piped input)
            pass

    def _start_raw(self):
        if self._fd is not None and self._old_settings:
            tty.setcbreak(self._fd)

    def _stop_raw(self):
        if self._fd is not None and self._old_settings:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_settings)

    _ARROW_MAP = {"A": "up", "B": "down", "C": "right", "D": "left"}

    def _read_key(self, timeout: float = 0.1) -> str | None:
        """Read a single keypress with timeout. Returns None if no input."""
        if select.select([sys.stdin], [], [], timeout)[0]:
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                if select.select([sys.stdin], [], [], 0.01)[0]:
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[' and select.select([sys.stdin], [], [], 0.01)[0]:
                        ch3 = sys.stdin.read(1)
                        direction = self._ARROW_MAP.get(ch3, "")
                        return f'arrow_{direction}'
                return 'escape'
            return ch.lower()
        return None

    def show_main_menu(self) -> MenuResult:
        """Display the main menu and wait for player input.

        Returns:
            MenuResult.PLAY if player wants to start, MenuResult.QUIT to exit.
        """
        self._start_raw()
        try:
            self.console.clear()
            self._render_main_menu()
            while True:
                key = self._read_key(timeout=0.5)
                if key is None:
                    continue
                if key == '\r' or key == '\n' or key == ' ':
                    return MenuResult.PLAY
                if key in ('q', 'escape'):
                    return MenuResult.QUIT
        finally:
            self._stop_raw()

    def show_pause_menu(self) -> MenuResult:
        """Display the pause menu and wait for player input.

        Returns:
            MenuResult.RESUME to continue playing, MenuResult.QUIT to exit.
        """
        self._start_raw()
        try:
            self.console.clear()
            self._render_pause_menu()
            while True:
                key = self._read_key(timeout=0.5)
                if key is None:
                    continue
                if key in ('p', 'r', 'escape', '\r', '\n', ' '):
                    return MenuResult.RESUME
                if key == 'q':
                    return MenuResult.QUIT
        finally:
            self._stop_raw()

    def _render_main_menu(self):
        """Render the main menu to the console."""
        title = Text(TITLE_ART, style="bold cyan", justify="center")
        subtitle = Text(SUBTITLE, style="italic yellow", justify="center")

        controls = Text(justify="center")
        controls.append("\n")
        controls.append("  [ ENTER ]", style="bold green")
        controls.append("  Start Game\n", style="white")
        controls.append("  [  Q   ]", style="bold red")
        controls.append("  Quit\n", style="white")

        content = Text(justify="center")
        content.append_text(title)
        content.append("\n")
        content.append_text(subtitle)
        content.append_text(controls)

        panel = Panel(
            Align.center(content),
            border_style="bright_cyan",
            padding=(1, 4),
        )
        self.console.print(panel)

    def _render_pause_menu(self):
        """Render the pause menu to the console."""
        header = Text("  PAUSED  ", style="bold white on dark_blue", justify="center")

        controls = Text(justify="center")
        controls.append("\n")
        controls.append("  [ P / R ]", style="bold green")
        controls.append("  Resume\n", style="white")
        controls.append("  [  Q   ]", style="bold red")
        controls.append("  Quit to Terminal\n", style="white")

        content = Text(justify="center")
        content.append_text(header)
        content.append("\n\n")
        content.append_text(controls)

        panel = Panel(
            Align.center(content),
            title="[bold yellow]Pause Menu[/bold yellow]",
            border_style="yellow",
            padding=(1, 4),
        )
        self.console.print(panel)
