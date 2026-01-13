"""Rendering system for drawing the game world."""
import esper
from typing import List, Dict
from src.components.core import Position, Sprite
from src.config import Config


class RenderSystem(esper.Processor):
    """Renders entities to a 2D character grid."""

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
                grid[y][x] = {'char': sprite.char, 'color': sprite.color}

        return grid

    def process(self):
        """Process is called by ECS but rendering is pull-based."""
        pass
