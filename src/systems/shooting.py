"""Shooting system for creating projectiles."""
import esper
import math
from src.components.core import Position, Velocity, Sprite
from src.components.combat import Stats, Projectile, Collider
from src.components.game import Player
from src.config import Config


class ShootingSystem(esper.Processor):
    """Handles shooting projectiles."""

    def __init__(self):
        self.shoot_x = 0
        self.shoot_y = 0
        self.dt = 0.0
        self.shoot_cooldowns = {}  # entity_id -> cooldown remaining

    def process(self):
        """Process shooting for all entities with shooting capability."""
        # Update cooldowns
        for entity_id in list(self.shoot_cooldowns.keys()):
            self.shoot_cooldowns[entity_id] -= self.dt
            if self.shoot_cooldowns[entity_id] <= 0:
                del self.shoot_cooldowns[entity_id]

        # Process player shooting
        for ent, (player, pos, stats) in esper.get_components(Player, Position, Stats):
            # Check if trying to shoot
            if self.shoot_x == 0 and self.shoot_y == 0:
                continue

            # Check cooldown
            if ent in self.shoot_cooldowns:
                continue

            # Create projectile
            self._create_projectile(
                ent, pos.x, pos.y,
                float(self.shoot_x), float(self.shoot_y),
                stats.damage, stats.shot_speed
            )

            # Set cooldown
            self.shoot_cooldowns[ent] = 1.0 / stats.fire_rate

    def _create_projectile(self, owner: int, x: float, y: float,
                          dx: float, dy: float, damage: float, speed: float):
        """Create a projectile entity.

        Args:
            owner: Entity ID that fired this
            x, y: Starting position
            dx, dy: Direction (will be normalized)
            damage: Damage dealt on hit
            speed: Projectile speed
        """
        from src.components.game import CollectedItems

        # Normalize direction
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

        # Get player position
        pos = esper.component_for_entity(owner, Position)

        # Check for multi-shot effect
        has_multi_shot = False
        if esper.has_component(owner, CollectedItems):
            collected = esper.component_for_entity(owner, CollectedItems)
            has_multi_shot = collected.has_effect("multi_shot")

        # Calculate base angle
        angle = math.atan2(dy, dx)

        if has_multi_shot:
            # Fire 3 projectiles: left (-15°), center, right (+15°)
            stats = esper.component_for_entity(owner, Stats)
            self._spawn_projectile(owner, pos, angle - math.radians(15), stats)
            self._spawn_projectile(owner, pos, angle, stats)
            self._spawn_projectile(owner, pos, angle + math.radians(15), stats)
        else:
            # Fire single projectile
            stats = esper.component_for_entity(owner, Stats)
            self._spawn_projectile(owner, pos, angle, stats)

    def _spawn_projectile(self, player_ent: int, pos: Position, angle: float, stats: Stats):
        """Spawn a single projectile at the given angle.

        Args:
            player_ent: Player entity ID (projectile owner)
            pos: Starting position
            angle: Angle in radians
            stats: Player stats for damage/speed
        """
        # Calculate velocity from angle
        vel_x = math.cos(angle) * stats.shot_speed
        vel_y = math.sin(angle) * stats.shot_speed

        # Create projectile entity
        projectile = esper.create_entity()
        esper.add_component(projectile, Position(pos.x, pos.y))
        esper.add_component(projectile, Velocity(vel_x, vel_y))
        esper.add_component(projectile, Projectile(stats.damage, player_ent))
        esper.add_component(projectile, Collider(Config.PROJECTILE_HITBOX))
        esper.add_component(projectile, Sprite('.', 'white'))
