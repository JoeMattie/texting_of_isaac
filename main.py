"""Main game loop for Texting of Isaac."""
import time
from rich.console import Console
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

    # Game loop
    frame_time = 1.0 / Config.FPS
    last_time = time.time()

    console.clear()
    console.print("[cyan]Starting Texting of Isaac...[/cyan]")
    time.sleep(0.5)

    try:
        while engine.running:
            # Calculate delta time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Update game
            engine.update(dt)

            # Render
            console.clear()
            layout = create_game_display(engine)
            console.print(layout)

            # Sleep to maintain FPS
            elapsed = time.time() - current_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)

    except KeyboardInterrupt:
        console.clear()
        console.print("[yellow]Game stopped by user[/yellow]")

    finally:
        console.print("[green]Thanks for playing![/green]")


if __name__ == "__main__":
    main()
