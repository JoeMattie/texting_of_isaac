"""Bomb placement and explosion system."""
import esper
from src.components.core import Position, Sprite
from src.components.game import Player
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

        Note:
            For now, this is a stub that just removes the bomb.
            Explosion damage logic will be added in Task 4.
        """
        # For now, just remove the bomb (explosion logic in Task 4)
        esper.delete_entity(bomb_ent, immediate=True)
