"""Collision detection and response system."""
import esper
import math
from src.components.core import Position, Health, Velocity
from src.components.combat import Collider, Projectile
from src.components.game import Enemy, Player


class CollisionSystem(esper.Processor):
    """Handles collision detection and damage."""

    def process(self):
        """Check all collisions and apply damage."""
        # Get all entities with colliders
        collidables = [
            (ent, pos, col)
            for ent, (pos, col) in esper.get_components(Position, Collider)
        ]

        # Check all pairs
        for i, (e1, pos1, col1) in enumerate(collidables):
            for e2, pos2, col2 in collidables[i + 1:]:
                # Pass the current world name
                if self._check_collision(e1, e2, esper.current_world):
                    self._handle_collision(e1, e2)

    def _check_collision(self, e1: int, e2: int, world_name: str) -> bool:
        """Check if two entities collide.

        Args:
            e1, e2: Entity IDs
            world_name: ECS world name

        Returns:
            True if entities overlap
        """
        esper.switch_world(world_name)
        pos1 = esper.component_for_entity(e1, Position)
        pos2 = esper.component_for_entity(e2, Position)
        col1 = esper.component_for_entity(e1, Collider)
        col2 = esper.component_for_entity(e2, Collider)

        # Circle collision
        dx = pos2.x - pos1.x
        dy = pos2.y - pos1.y
        distance = math.sqrt(dx * dx + dy * dy)

        return distance < (col1.radius + col2.radius)

    def _handle_collision(self, e1: int, e2: int):
        """Handle collision between two entities.

        Args:
            e1, e2: Entity IDs that collided
        """
        # Projectile hitting enemy
        if esper.has_component(e1, Projectile) and esper.has_component(e2, Enemy):
            proj = esper.component_for_entity(e1, Projectile)
            # Only if projectile is from player (or owner doesn't exist - legacy behavior)
            if not esper.entity_exists(proj.owner) or esper.has_component(proj.owner, Player):
                self._projectile_hit_enemy(e1, e2)
        elif esper.has_component(e2, Projectile) and esper.has_component(e1, Enemy):
            proj = esper.component_for_entity(e2, Projectile)
            # Only if projectile is from player (or owner doesn't exist - legacy behavior)
            if not esper.entity_exists(proj.owner) or esper.has_component(proj.owner, Player):
                self._projectile_hit_enemy(e2, e1)

        # Projectile hitting player
        if esper.has_component(e1, Projectile) and esper.has_component(e2, Player):
            proj = esper.component_for_entity(e1, Projectile)
            # Only if projectile is from enemy
            if esper.entity_exists(proj.owner) and esper.has_component(proj.owner, Enemy):
                self._projectile_hit_player(e1, e2)
        elif esper.has_component(e2, Projectile) and esper.has_component(e1, Player):
            proj = esper.component_for_entity(e2, Projectile)
            # Only if projectile is from enemy
            if esper.entity_exists(proj.owner) and esper.has_component(proj.owner, Enemy):
                self._projectile_hit_player(e2, e1)

        # Enemy touching player (contact damage)
        if esper.has_component(e1, Enemy) and esper.has_component(e2, Player):
            self._enemy_contact_player(e1, e2)
        elif esper.has_component(e2, Enemy) and esper.has_component(e1, Player):
            self._enemy_contact_player(e2, e1)

    def _projectile_hit_enemy(self, projectile: int, enemy: int):
        """Handle projectile hitting enemy.

        Args:
            projectile: Projectile entity ID
            enemy: Enemy entity ID
        """
        import random
        from src.components.game import Player, CollectedItems
        from src.config import Config

        proj = esper.component_for_entity(projectile, Projectile)
        health = esper.component_for_entity(enemy, Health)

        # Apply damage
        health.current -= proj.damage

        # Check for piercing effect
        has_piercing = False
        if esper.entity_exists(proj.owner) and esper.has_component(proj.owner, Player):
            if esper.has_component(proj.owner, CollectedItems):
                collected = esper.component_for_entity(proj.owner, CollectedItems)
                has_piercing = collected.has_effect("piercing")

        # Remove projectile (unless piercing)
        if not has_piercing:
            esper.delete_entity(projectile)

        # Check for enemy death
        if health.current <= 0:
            # Roll for item drop
            if random.random() < Config.ITEM_DROP_CHANCE:
                pos = esper.component_for_entity(enemy, Position)
                from src.entities.items import spawn_random_item
                spawn_random_item(esper._current_world, pos.x, pos.y)

            esper.delete_entity(enemy)

    def _projectile_hit_player(self, projectile: int, player: int):
        """Handle enemy projectile hitting player."""
        from src.components.game import Invincible, Dead
        from src.config import Config

        # Check invincibility
        if esper.has_component(player, Invincible):
            esper.delete_entity(projectile)  # Remove projectile but no damage
            return

        # Get projectile damage
        proj = esper.component_for_entity(projectile, Projectile)
        health = esper.component_for_entity(player, Health)

        # Apply damage
        health.current -= proj.damage

        # Add invincibility
        esper.add_component(player, Invincible(Config.INVINCIBILITY_DURATION))

        # Remove projectile
        esper.delete_entity(projectile)

        # Check for death
        if health.current <= 0:
            esper.add_component(player, Dead())

    def _enemy_contact_player(self, enemy: int, player: int):
        """Handle enemy touching player (contact damage)."""
        from src.components.game import Invincible, Dead
        from src.config import Config

        # Check invincibility
        if esper.has_component(player, Invincible):
            return  # No damage while invincible

        health = esper.component_for_entity(player, Health)
        health.current -= 1.0  # Contact damage = 1 heart

        # Add invincibility frames
        esper.add_component(player, Invincible(Config.INVINCIBILITY_DURATION))

        # Check for death
        if health.current <= 0:
            esper.add_component(player, Dead())
