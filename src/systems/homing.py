"""HomingSystem - applies homing behavior to projectiles."""
import esper
import math
from src.components.core import Position, Velocity
from src.components.combat import Projectile
from src.components.game import Player, Enemy, CollectedItems


class HomingSystem(esper.Processor):
    """Applies homing behavior to projectiles."""

    def __init__(self):
        super().__init__()
        self.dt: float = 0.0

    def process(self):
        """Update homing projectiles to turn toward nearest enemy."""
        from src.config import Config

        # Check if player has homing effect
        player_has_homing = False
        for player_ent, (player, collected) in esper.get_components(Player, CollectedItems):
            if collected.has_effect("homing"):
                player_has_homing = True
                break

        if not player_has_homing:
            return

        # Apply homing to player's projectiles
        for proj_ent, (proj, proj_pos, proj_vel) in esper.get_components(Projectile, Position, Velocity):
            # Only home player projectiles
            if not esper.entity_exists(proj.owner):
                continue
            if not esper.has_component(proj.owner, Player):
                continue

            # Find nearest enemy
            nearest_enemy = None
            nearest_distance = float('inf')

            for enemy_ent, (enemy, enemy_pos) in esper.get_components(Enemy, Position):
                dx = enemy_pos.x - proj_pos.x
                dy = enemy_pos.y - proj_pos.y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_enemy = enemy_pos

            if nearest_enemy is None:
                continue

            # Gradually rotate velocity toward target
            target_dx = nearest_enemy.x - proj_pos.x
            target_dy = nearest_enemy.y - proj_pos.y
            target_angle = math.atan2(target_dy, target_dx)

            current_angle = math.atan2(proj_vel.dy, proj_vel.dx)
            current_speed = math.sqrt(proj_vel.dx * proj_vel.dx + proj_vel.dy * proj_vel.dy)

            # Rotate toward target by turn rate
            turn_rate = Config.HOMING_TURN_RATE  # degrees per second
            max_turn = math.radians(turn_rate) * self.dt

            angle_diff = target_angle - current_angle
            # Normalize to [-pi, pi]
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi

            # Clamp turn amount
            turn_amount = max(-max_turn, min(max_turn, angle_diff))
            new_angle = current_angle + turn_amount

            # Apply new velocity
            proj_vel.dx = math.cos(new_angle) * current_speed
            proj_vel.dy = math.sin(new_angle) * current_speed
