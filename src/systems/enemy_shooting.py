"""Enemy shooting system for creating enemy projectiles."""
import esper
import math
from src.components.core import Position, Velocity, Sprite
from src.components.combat import Projectile, Collider
from src.components.game import Enemy, Player, AIBehavior
from src.entities.enemies import ENEMY_DATA
from src.config import Config


class EnemyShootingSystem(esper.Processor):
    """Handles enemy shooting patterns."""

    def __init__(self):
        self.dt = 0.0

    def process(self):
        """Process shooting for all enemies with patterns."""
        pass  # Implementation in next tasks
