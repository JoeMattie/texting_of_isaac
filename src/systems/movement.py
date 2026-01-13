"""Movement system for applying velocity to positions."""
import esper
from src.components.core import Position, Velocity


class MovementSystem(esper.Processor):
    """Applies velocity to position based on delta time."""

    def __init__(self):
        """Initialize the movement system."""
        super().__init__()
        self.dt = 0.0

    def process(self):
        """Update positions based on velocities."""
        for ent, (pos, vel) in esper.get_components(Position, Velocity):
            pos.x += vel.dx * self.dt
            pos.y += vel.dy * self.dt
