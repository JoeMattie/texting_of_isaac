"""Rendering system for drawing the game world."""
import esper
from typing import List, Dict
from src.components.core import Position, Sprite
from src.components.game import Player, Invincible
from src.config import Config


class RenderSystem(esper.Processor):
    """Renders entities to a 2D character grid."""

    def __init__(self, item_pickup_system=None, minimap_system=None, dungeon=None):
        """Initialize render system.

        Args:
            item_pickup_system: Optional ItemPickupSystem for notifications
            minimap_system: Optional MiniMapSystem for minimap overlay
            dungeon: Optional Dungeon for minimap rendering
        """
        super().__init__()
        self.item_pickup_system = item_pickup_system
        self.minimap_system = minimap_system
        self.dungeon = dungeon
        self.flash_state = 0.0

    def create_grid(self) -> List[List[Dict]]:
        """Create empty render grid.

        Returns:
            2D grid of cells with char and color
        """
        return [
            [{'char': '.', 'color': 'white'} for _ in range(Config.ROOM_WIDTH)]
            for _ in range(Config.ROOM_HEIGHT)
        ]

    def render(self, world_name: str) -> List[List[Dict]]:
        """Render all entities to a grid.

        Args:
            world_name: The ECS world name

        Returns:
            2D grid with rendered entities
        """
        esper.switch_world(world_name)
        grid = self.create_grid()

        # Draw all entities with position and sprite
        for ent, (pos, sprite) in esper.get_components(Position, Sprite):
            x = int(pos.x)
            y = int(pos.y)

            # Bounds check
            if 0 <= x < Config.ROOM_WIDTH and 0 <= y < Config.ROOM_HEIGHT:
                # Handle invincibility flashing for player
                color = sprite.color
                if esper.has_component(ent, Player) and esper.has_component(ent, Invincible):
                    # Flash every 0.1 seconds (10 FPS flash rate)
                    invincible = esper.component_for_entity(ent, Invincible)
                    # Use elapsed time: (duration - remaining)
                    elapsed = Config.INVINCIBILITY_DURATION - invincible.remaining
                    if (elapsed % 0.2) < 0.1:
                        color = 'white'  # Flash to white
                    # else: keep original color

                grid[y][x] = {'char': sprite.char, 'color': color}

        # Render minimap overlay if available
        if self.minimap_system and self.dungeon:
            from src.components.dungeon import MiniMap
            # Find minimap entity
            minimap_entities = esper.get_component(MiniMap)
            if minimap_entities:
                minimap_ent, minimap = minimap_entities[0]
                minimap_lines = self.minimap_system.render(minimap, self.dungeon)

                # Place minimap in top-right corner
                # Position: right edge - minimap width (9 chars) - 1 margin
                start_x = Config.ROOM_WIDTH - 10
                start_y = 0

                for i, line in enumerate(minimap_lines):
                    y = start_y + i
                    if y >= Config.ROOM_HEIGHT:
                        break

                    for j, char in enumerate(line):
                        x = start_x + j
                        if 0 <= x < Config.ROOM_WIDTH and 0 <= y < Config.ROOM_HEIGHT:
                            # Minimap overlay uses cyan for borders, white for content
                            color = 'cyan' if char in '╔═╗║╚╝' else 'white'
                            grid[y][x] = {'char': char, 'color': color}

        # Render item pickup notification
        if hasattr(self, 'item_pickup_system') and self.item_pickup_system and self.item_pickup_system.notification:
            notification = self.item_pickup_system.notification
            # Center the notification at top of screen
            x = (Config.ROOM_WIDTH - len(notification)) // 2
            if 0 <= x < Config.ROOM_WIDTH:
                for i, char in enumerate(notification):
                    if x + i < Config.ROOM_WIDTH:
                        grid[0][x + i] = {'char': char, 'color': 'yellow'}

        return grid

    def process(self):
        """Process is called by ECS but rendering is pull-based."""
        pass
