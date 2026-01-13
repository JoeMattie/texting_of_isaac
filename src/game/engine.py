"""Main game engine and loop."""
import esper
from src.config import Config


class GameEngine:
    """Main game engine managing ECS world and game loop."""

    def __init__(self):
        """Initialize the game engine."""
        # Esper uses module-level world management
        # Each engine gets its own world by name
        self.world_name = f"game_world_{id(self)}"
        esper.switch_world(self.world_name)
        self.world = esper  # Expose esper module as world interface
        self.running = True
        self.delta_time = 0.0

    def update(self, dt: float):
        """Update all systems.

        Args:
            dt: Delta time in seconds since last frame
        """
        self.delta_time = dt
        # Process all systems (to be added)
        esper.switch_world(self.world_name)
        esper.process()

    def stop(self):
        """Stop the game engine."""
        self.running = False
