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
        # Find player position
        player_pos = None
        for ent, (player, pos) in esper.get_components(Player, Position):
            player_pos = pos
            break

        if not player_pos:
            return

        # Process each enemy with AI behavior
        for ent, (enemy, pos, ai) in esper.get_components(Enemy, Position, AIBehavior):
            patterns = ENEMY_DATA[enemy.type]["patterns"]
            if not patterns:
                continue

            # Get pattern list for indexing
            pattern_names = list(patterns.keys())

            # Select current pattern based on pattern_index
            current_pattern_name = pattern_names[ai.pattern_index % len(pattern_names)]

            # Check if current pattern is ready
            if ai.pattern_cooldowns[current_pattern_name] <= 0:
                pattern = patterns[current_pattern_name]

                # Calculate base angle to player
                dx = player_pos.x - pos.x
                dy = player_pos.y - pos.y
                base_angle = math.atan2(dy, dx)

                # Create bullets
                self._create_bullets(pos, base_angle, pattern, ent)

                # Reset cooldown
                ai.pattern_cooldowns[current_pattern_name] = pattern["cooldown"]

                # Cycle to next pattern
                ai.pattern_index = (ai.pattern_index + 1) % len(pattern_names)

    def _create_bullets(self, pos: Position, base_angle: float,
                       pattern: dict, owner: int):
        """Create bullets according to pattern.

        Args:
            pos: Enemy position
            base_angle: Angle to player (radians)
            pattern: Pattern config dict
            owner: Enemy entity ID
        """
        count = pattern["count"]
        spread = pattern["spread"]
        speed = pattern["speed"]

        if count == 1:
            # Single bullet - shoot in base direction
            angles = [base_angle]
        elif spread == 360:
            # Ring pattern - distribute evenly around full circle
            angle_step = (2 * math.pi) / count
            angles = [i * angle_step for i in range(count)]
        else:
            # Multiple bullets - distribute across spread
            spread_rad = spread * (math.pi / 180)
            start_angle = base_angle - (spread_rad / 2)
            angle_step = spread_rad / (count - 1)
            angles = [start_angle + i * angle_step for i in range(count)]

        for angle in angles:
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed

            # Create projectile entity
            projectile = esper.create_entity()
            esper.add_component(projectile, Position(pos.x, pos.y))
            esper.add_component(projectile, Velocity(dx, dy))
            esper.add_component(projectile, Projectile(damage=1.0, owner=owner))
            esper.add_component(projectile, Collider(Config.PROJECTILE_HITBOX))
            esper.add_component(projectile, Sprite('*', 'yellow'))
