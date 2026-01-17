"""Collision detection and response system."""
import esper
import math
from src.components.core import Position, Health, Velocity
from src.components.combat import Collider, Projectile
from src.components.dungeon import Door
from src.components.game import Enemy, Player


class CollisionSystem(esper.Processor):
    """Handles collision detection and damage."""

    def __init__(self, room_manager=None, bomb_system=None):
        """Initialize collision system.

        Args:
            room_manager: RoomManager instance for room transitions (optional)
            bomb_system: BombSystem instance for explosive tears (optional)
        """
        super().__init__()
        self.room_manager = room_manager
        self.bomb_system = bomb_system

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

        # Player-door collision for room transitions (only if room_manager available)
        if self.room_manager:
            transition_triggered = False
            for player_ent, (player, player_pos, player_collider) in esper.get_components(Player, Position, Collider):
                for door_ent, (door, door_pos, door_collider) in esper.get_components(Door, Position, Collider):
                    # Only unlocked doors allow transitions
                    if not door.locked and self._check_collision(player_ent, door_ent, esper.current_world):
                        # Trigger room transition via RoomManager
                        self.room_manager.transition_to_room(door.leads_to, door.direction)

                        # Reposition player at entrance of new room
                        self._reposition_player_after_transition(player_ent, player_pos, door.direction)

                        transition_triggered = True

                        # Only transition through one door per frame
                        break
                if transition_triggered:
                    break

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

        # Check for explosive effect
        has_explosive = False
        if esper.entity_exists(proj.owner) and esper.has_component(proj.owner, Player):
            if esper.has_component(proj.owner, CollectedItems):
                collected = esper.component_for_entity(proj.owner, CollectedItems)
                has_explosive = collected.has_effect("explosive")

        # If explosive, trigger explosion and delete projectile (overrides piercing)
        if has_explosive and self.bomb_system is not None:
            # Get projectile position for explosion center
            proj_pos = esper.component_for_entity(projectile, Position)

            # Calculate explosion damage (50% of bomb damage)
            explosion_damage = Config.BOMB_DAMAGE * Config.EXPLOSIVE_TEAR_DAMAGE_MULTIPLIER

            # Trigger explosion (reuse bomb system logic)
            self.bomb_system.damage_entities_in_radius(proj_pos, Config.BOMB_BLAST_RADIUS, explosion_damage)

            # Always delete projectile after explosion (overrides piercing)
            esper.delete_entity(projectile)
            return

        # Check for piercing effect (only if not explosive)
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
            pos = esper.component_for_entity(enemy, Position)

            # Roll for item drop
            if random.random() < Config.ITEM_DROP_CHANCE:
                from src.entities.items import spawn_random_item
                spawn_random_item(esper._current_world, pos.x, pos.y)

            # Roll for coin drop (independent of item drop)
            if random.random() < Config.ENEMY_COIN_DROP_CHANCE:
                # Drop 1-2 coins
                num_coins = random.randint(1, 2)
                from src.entities.currency import spawn_coin
                for _ in range(num_coins):
                    spawn_coin(esper._current_world, pos.x, pos.y)

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

    def _reposition_player_after_transition(self, player_ent: int, player_pos: Position, entry_direction: str) -> None:
        """Move player to entrance position in new room.

        When entering through a door, position player on opposite side of new room,
        slightly offset from the wall to avoid immediate re-collision.

        Args:
            player_ent: Player entity ID
            player_pos: Player's Position component
            entry_direction: Direction player came from
        """
        from src.config import Config

        if entry_direction == "north":
            # Entered from north, spawn at south
            player_pos.y = Config.ROOM_HEIGHT - 2
            player_pos.x = Config.ROOM_WIDTH / 2
        elif entry_direction == "south":
            # Entered from south, spawn at north
            player_pos.y = 1
            player_pos.x = Config.ROOM_WIDTH / 2
        elif entry_direction == "east":
            # Entered from east, spawn at west
            player_pos.x = 1
            player_pos.y = Config.ROOM_HEIGHT / 2
        elif entry_direction == "west":
            # Entered from west, spawn at east
            player_pos.x = Config.ROOM_WIDTH - 2
            player_pos.y = Config.ROOM_HEIGHT / 2
