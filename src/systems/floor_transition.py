"""Floor transition system for detecting trapdoor collisions and triggering floor progression."""
import esper
import math
from src.components.core import Position
from src.components.game import Player
from src.components.boss import Trapdoor
from src.config import Config


class FloorTransitionSystem(esper.Processor):
    """Detects player collision with trapdoors and triggers floor transitions.

    Handles:
    - Collision detection between player and trapdoor entities
    - Floor transition triggering when collision detected
    - Victory detection when transitioning beyond FINAL_FLOOR
    - Trapdoor consumption after use
    """

    def __init__(self):
        """Initialize the floor transition system."""
        super().__init__()
        self.pending_floor_transition = False
        self.target_floor = None
        self.victory = False

    def process(self):
        """Check for trapdoor collisions and trigger transitions."""
        # Query for Player + Position
        player_entities = list(esper.get_components(Player, Position))

        # No player, no transitions
        if not player_entities:
            return

        # Get player position (should only be one player)
        player_ent, (player, player_pos) = player_entities[0]

        # Query for Trapdoor + Position
        trapdoor_entities = list(esper.get_components(Trapdoor, Position))

        # Check each trapdoor for collision with player
        for trapdoor_ent, (trapdoor, trapdoor_pos) in trapdoor_entities:
            # Calculate distance to player
            distance = self._calculate_distance(player_pos, trapdoor_pos)

            # Check if within pickup radius
            if distance < Config.ITEM_PICKUP_RADIUS:
                # Check for victory condition
                if trapdoor.next_floor > Config.FINAL_FLOOR:
                    # Victory! Player has completed all floors
                    self.victory = True
                    self.pending_floor_transition = False
                    # Consume trapdoor
                    esper.delete_entity(trapdoor_ent)
                    # Break after first collision
                    break
                else:
                    # Normal floor transition
                    self.pending_floor_transition = True
                    self.target_floor = trapdoor.next_floor
                    # Consume trapdoor
                    esper.delete_entity(trapdoor_ent)
                    # Break after first collision
                    break

    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """Calculate Euclidean distance between two positions.

        Args:
            pos1: First position
            pos2: Second position

        Returns:
            Distance between positions
        """
        dx = pos2.x - pos1.x
        dy = pos2.y - pos1.y
        return math.sqrt(dx * dx + dy * dy)

    def reset_transition(self):
        """Reset transition state after handling.

        This should be called by the game loop after processing a floor transition.
        """
        self.pending_floor_transition = False
        self.target_floor = None
