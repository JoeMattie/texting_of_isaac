"""Bomb placement and explosion system."""
import esper
import math
from src.components.core import Position, Sprite, Health
from src.components.game import Player, Invincible
from src.components.dungeon import Currency, Bomb
from src.config import Config
from src.systems.input import InputSystem


class BombSystem(esper.Processor):
    """Handles bomb placement and explosions."""

    def __init__(self, input_system: InputSystem):
        """Initialize the bomb system.

        Args:
            input_system: Reference to InputSystem to check bomb input
        """
        super().__init__()
        self.input_system = input_system
        self.dt = 0.0

    def process(self):
        """Process bomb placement and fuse countdown."""
        dt = self.dt

        # Check for bomb placement input
        if self.input_system.bomb_pressed:
            for player_ent, (player, pos, currency) in esper.get_components(Player, Position, Currency):
                if currency.bombs > 0:
                    # Place bomb at player position
                    self.place_bomb(pos.x, pos.y, player_ent)
                    currency.bombs -= 1

            # Reset input flag after processing all players
            self.input_system.bomb_pressed = False

        # Update all active bombs and collect expired ones
        bombs_to_explode = []
        for bomb_ent, (bomb, pos) in esper.get_components(Bomb, Position):
            bomb.fuse_time -= dt

            if bomb.fuse_time <= 0:
                bombs_to_explode.append((bomb_ent, pos, bomb))

        # Explode all expired bombs
        for bomb_ent, pos, bomb in bombs_to_explode:
            self.explode_bomb(bomb_ent, pos, bomb)

    def place_bomb(self, x: float, y: float, owner: int):
        """Create bomb entity at position.

        Args:
            x: X coordinate to place bomb
            y: Y coordinate to place bomb
            owner: Entity ID of the player who placed the bomb
        """
        bomb_ent = esper.create_entity()
        esper.add_component(bomb_ent, Position(x, y))
        esper.add_component(bomb_ent, Sprite("●", "red"))
        esper.add_component(bomb_ent, Bomb(
            fuse_time=Config.BOMB_FUSE_TIME,
            blast_radius=Config.BOMB_BLAST_RADIUS,
            owner=owner
        ))

    def explode_bomb(self, bomb_ent: int, pos: Position, bomb: Bomb):
        """Handle bomb explosion.

        Args:
            bomb_ent: Entity ID of the bomb
            pos: Position of the bomb
            bomb: Bomb component
        """
        # Show explosion effect (placeholder for future visual effects)
        # self.spawn_explosion_effect(pos.x, pos.y)

        # Damage entities in blast radius
        self.damage_entities_in_radius(pos, bomb.blast_radius)

        # Remove bomb
        esper.delete_entity(bomb_ent, immediate=True)

    def damage_entities_in_radius(self, center: Position, radius: float):
        """Deal damage to entities within blast radius.

        Args:
            center: Position of the explosion center
            radius: Blast radius to check for damage
        """
        for ent, (pos, health) in esper.get_components(Position, Health):
            # Skip entities that are already dead
            if health.current <= 0:
                continue

            # Skip players with invincibility frames
            if esper.has_component(ent, Player) and esper.has_component(ent, Invincible):
                continue

            # Calculate Euclidean distance from explosion center
            distance = math.sqrt((center.x - pos.x) ** 2 + (center.y - pos.y) ** 2)

            # Apply damage if within blast radius
            if distance <= radius:
                health.current -= Config.BOMB_DAMAGE
