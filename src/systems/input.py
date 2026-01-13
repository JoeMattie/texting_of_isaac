"""Input handling system."""
import esper
import math
from src.components.core import Velocity
from src.components.combat import Stats
from src.components.game import Player


class InputSystem(esper.Processor):
    """Processes input and updates player velocity."""

    def __init__(self):
        """Initialize the input system."""
        super().__init__()
        self.move_x = 0
        self.move_y = 0
        self.shoot_x = 0
        self.shoot_y = 0

    def set_input(self, move_x: int, move_y: int, shoot_x: int, shoot_y: int):
        """Set current input state.

        Args:
            move_x: -1 (left), 0 (none), 1 (right)
            move_y: -1 (up), 0 (none), 1 (down)
            shoot_x: -1 (left), 0 (none), 1 (right)
            shoot_y: -1 (up), 0 (none), 1 (down)
        """
        self.move_x = move_x
        self.move_y = move_y
        self.shoot_x = shoot_x
        self.shoot_y = shoot_y

    def process(self):
        """Update player velocity based on input."""
        for ent, (player, vel, stats) in esper.get_components(Player, Velocity, Stats):
            # Calculate movement direction
            dx = float(self.move_x)
            dy = float(self.move_y)

            # Normalize diagonal movement
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Apply speed
            vel.dx = dx * stats.speed
            vel.dy = dy * stats.speed
