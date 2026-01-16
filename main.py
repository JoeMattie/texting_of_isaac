"""Main game loop for Texting of Isaac."""
import time
import sys
import select
import termios
import tty
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text

from src.game.engine import GameEngine
from src.entities.player import create_player
from src.entities.enemies import create_enemy
from src.config import Config


def create_game_display(engine: GameEngine) -> Layout:
    """Create a Rich display showing the game grid and HUD.

    Args:
        engine: The game engine

    Returns:
        Rich Layout with game and HUD
    """
    # Get render grid from render system
    grid = engine.render_system.render(engine.world_name)

    # Create table for game grid
    table = Table(show_header=False, show_edge=False, padding=0, box=None)
    for _ in range(Config.ROOM_WIDTH):
        table.add_column(width=1)

    # Add rows to table
    for row in grid:
        cells = []
        for cell in row:
            cells.append(Text(cell['char'], style=cell['color']))
        table.add_row(*cells)

    # Wrap in panel
    game_panel = Panel(table, title="Texting of Isaac", border_style="cyan")

    # Create HUD
    hud_text = Text()
    hud_text.append("Controls: ", style="bold")
    hud_text.append("WASD=Move  Arrows=Shoot  Q=Quit\n", style="white")
    hud_text.append("Health: ", style="bold red")
    hud_text.append("♥" * 6, style="red")  # TODO: Get actual player health

    hud_panel = Panel(hud_text, title="HUD", border_style="yellow")

    # Create layout
    layout = Layout()
    layout.split_column(
        Layout(game_panel, size=Config.ROOM_HEIGHT + 2),
        Layout(hud_panel, size=5)
    )

    return layout


class InputHandler:
    """Handle keyboard input using non-blocking terminal input."""

    def __init__(self):
        """Initialize input handler."""
        self.move_x = 0
        self.move_y = 0
        self.shoot_x = 0
        self.shoot_y = 0
        self.quit_pressed = False
        self.pressed_keys = set()

        # Save terminal settings (only if stdin is a terminal)
        self.fd = sys.stdin.fileno()
        self.old_settings = None
        if sys.stdin.isatty():
            self.old_settings = termios.tcgetattr(self.fd)

    def start(self):
        """Set up terminal for raw input."""
        if self.old_settings:
            tty.setcbreak(self.fd)

    def stop(self):
        """Restore terminal settings."""
        if self.old_settings:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def read_input(self):
        """Read available input without blocking."""
        # Check if input is available
        if select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.read(1)

            # Handle escape sequences (arrow keys)
            if ch == '\x1b':
                # Read the rest of the escape sequence
                if select.select([sys.stdin], [], [], 0.01)[0]:
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[' and select.select([sys.stdin], [], [], 0.01)[0]:
                        ch3 = sys.stdin.read(1)
                        if ch3 == 'A':  # Up arrow
                            self.pressed_keys.add('arrow_up')
                        elif ch3 == 'B':  # Down arrow
                            self.pressed_keys.add('arrow_down')
                        elif ch3 == 'C':  # Right arrow
                            self.pressed_keys.add('arrow_right')
                        elif ch3 == 'D':  # Left arrow
                            self.pressed_keys.add('arrow_left')
            else:
                self.pressed_keys.add(ch.lower())

    def update(self):
        """Update input state based on currently pressed keys."""
        # Read new input
        self.read_input()

        # Check quit
        if 'q' in self.pressed_keys:
            self.quit_pressed = True
            return

        # Reset movement
        self.move_x = 0
        self.move_y = 0
        self.shoot_x = 0
        self.shoot_y = 0

        # WASD movement
        if 'w' in self.pressed_keys:
            self.move_y = -1
        if 's' in self.pressed_keys:
            self.move_y = 1
        if 'a' in self.pressed_keys:
            self.move_x = -1
        if 'd' in self.pressed_keys:
            self.move_x = 1

        # Arrow keys for shooting
        if 'arrow_up' in self.pressed_keys:
            self.shoot_y = -1
        if 'arrow_down' in self.pressed_keys:
            self.shoot_y = 1
        if 'arrow_left' in self.pressed_keys:
            self.shoot_x = -1
        if 'arrow_right' in self.pressed_keys:
            self.shoot_x = 1

        # Clear keys for next frame
        self.pressed_keys.clear()


def main():
    """Run the main game loop."""
    console = Console()

    # Create engine and entities
    engine = GameEngine()

    # Create player at center
    player = create_player(
        engine.world_name,
        Config.ROOM_WIDTH / 2,
        Config.ROOM_HEIGHT / 2
    )

    # Spawn 3 test enemies
    create_enemy(engine.world_name, "chaser", 10.0, 5.0)
    create_enemy(engine.world_name, "shooter", 50.0, 15.0)
    create_enemy(engine.world_name, "chaser", 30.0, 3.0)

    # Create input handler
    input_handler = InputHandler()
    input_handler.start()

    # Game loop
    frame_time = 1.0 / Config.FPS
    last_time = time.time()

    console.clear()
    console.print("[cyan]Starting Texting of Isaac...[/cyan]")
    console.print("[dim]Press WASD to move, arrow keys to shoot, Q to quit[/dim]")
    time.sleep(1.0)

    try:
        # Use Live display to prevent flashing
        with Live(console=console, auto_refresh=False) as live:
            while engine.running and not input_handler.quit_pressed:
                # Calculate delta time
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time

                # Update input
                input_handler.update()

                # Set input on systems
                engine.input_system.set_input(
                    input_handler.move_x,
                    input_handler.move_y,
                    input_handler.shoot_x,
                    input_handler.shoot_y
                )
                engine.shooting_system.shoot_x = input_handler.shoot_x
                engine.shooting_system.shoot_y = input_handler.shoot_y

                # Update game
                engine.update(dt)

                # Render using Live display (no flashing)
                layout = create_game_display(engine)
                live.update(layout, refresh=True)

                # Sleep to maintain FPS
                elapsed = time.time() - current_time
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)

    except KeyboardInterrupt:
        console.clear()
        console.print("[yellow]Game stopped by user[/yellow]")

    finally:
        input_handler.stop()
        console.print("[green]Thanks for playing![/green]")


if __name__ == "__main__":
    main()
