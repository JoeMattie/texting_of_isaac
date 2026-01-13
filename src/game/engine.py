"""Main game engine and loop."""
import esper
from src.config import Config
from src.systems.input import InputSystem
from src.systems.movement import MovementSystem
from src.systems.shooting import ShootingSystem
from src.systems.ai import AISystem
from src.systems.collision import CollisionSystem
from src.systems.render import RenderSystem


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

        # Create and register all systems
        self.input_system = InputSystem()
        self.movement_system = MovementSystem()
        self.shooting_system = ShootingSystem()
        self.ai_system = AISystem()
        self.collision_system = CollisionSystem()
        self.render_system = RenderSystem()

        # Add systems as processors
        esper.add_processor(self.input_system)
        esper.add_processor(self.movement_system)
        esper.add_processor(self.shooting_system)
        esper.add_processor(self.ai_system)
        esper.add_processor(self.collision_system)
        esper.add_processor(self.render_system)

    def update(self, dt: float):
        """Update all systems.

        Args:
            dt: Delta time in seconds since last frame
        """
        self.delta_time = dt

        # Set delta time on systems that need it
        self.movement_system.dt = dt
        self.shooting_system.dt = dt
        self.ai_system.dt = dt

        # Process all systems
        esper.switch_world(self.world_name)
        esper.process()

    def stop(self):
        """Stop the game engine."""
        self.running = False
