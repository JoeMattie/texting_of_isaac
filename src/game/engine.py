"""Main game engine and loop."""
import esper
from src.config import Config
from src.systems.input import InputSystem
from src.systems.movement import MovementSystem
from src.systems.shooting import ShootingSystem
from src.systems.bomb import BombSystem
from src.systems.ai import AISystem
from src.systems.enemy_shooting import EnemyShootingSystem
from src.systems.homing import HomingSystem
from src.systems.collision import CollisionSystem
from src.systems.invincibility import InvincibilitySystem
from src.systems.item_pickup import ItemPickupSystem
from src.systems.render import RenderSystem
from src.systems.minimap_system import MiniMapSystem


class GameEngine:
    """Main game engine managing ECS world and game loop."""

    def __init__(self, dungeon=None):
        """Initialize the game engine.

        Args:
            dungeon: Optional Dungeon instance for minimap rendering
        """
        # Esper uses module-level world management
        # Each engine gets its own world by name
        self.world_name = f"game_world_{id(self)}"
        esper.switch_world(self.world_name)
        self.world = esper  # Expose esper module as world interface
        self.running = True
        self.delta_time = 0.0
        self.dungeon = dungeon

        # Create and register all systems with priority order
        self.input_system = InputSystem()
        self.world.add_processor(self.input_system, priority=0)

        self.ai_system = AISystem()
        self.world.add_processor(self.ai_system, priority=1)

        self.enemy_shooting_system = EnemyShootingSystem()
        self.world.add_processor(self.enemy_shooting_system, priority=2)

        self.shooting_system = ShootingSystem()
        self.world.add_processor(self.shooting_system, priority=3)

        self.bomb_system = BombSystem(self.input_system)
        self.world.add_processor(self.bomb_system, priority=4.7)

        self.movement_system = MovementSystem()
        self.world.add_processor(self.movement_system, priority=4)

        self.homing_system = HomingSystem()
        self.world.add_processor(self.homing_system, priority=4.5)

        self.collision_system = CollisionSystem(bomb_system=self.bomb_system)
        self.world.add_processor(self.collision_system, priority=5)

        self.invincibility_system = InvincibilitySystem()
        self.world.add_processor(self.invincibility_system, priority=6)

        self.item_pickup_system = ItemPickupSystem()
        self.world.add_processor(self.item_pickup_system, priority=6.5)

        # Create minimap system
        minimap_system = MiniMapSystem()

        # Create render system with dependencies
        self.render_system = RenderSystem(
            item_pickup_system=self.item_pickup_system,
            minimap_system=minimap_system,
            dungeon=dungeon
        )
        self.world.add_processor(self.render_system, priority=7)

    def update(self, dt: float):
        """Update all systems.

        Args:
            dt: Delta time in seconds since last frame
        """
        self.delta_time = dt

        # Set delta time on systems that need it
        self.movement_system.dt = dt
        self.shooting_system.dt = dt
        self.bomb_system.dt = dt
        self.ai_system.dt = dt
        self.enemy_shooting_system.dt = dt
        self.homing_system.dt = dt
        self.invincibility_system.dt = dt
        self.item_pickup_system.dt = dt

        # Process all systems
        esper.switch_world(self.world_name)
        esper.process()

    def stop(self):
        """Stop the game engine."""
        self.running = False
