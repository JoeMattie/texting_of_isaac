"""Invincibility system for managing invulnerability frames."""
import esper
from src.components.game import Invincible


class InvincibilitySystem(esper.Processor):
    """Decrements invincibility timers and removes expired invincibility."""

    def __init__(self):
        """Initialize the invincibility system."""
        super().__init__()
        self.dt = 0.0

    def process(self):
        """Update all invincibility timers."""
        for ent, (invincible,) in esper.get_components(Invincible):
            invincible.remaining -= self.dt

            if invincible.remaining <= 0:
                esper.remove_component(ent, Invincible)
