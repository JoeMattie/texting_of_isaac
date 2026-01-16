"""Room manager system for handling room state and transitions."""
import esper
from src.game.dungeon import Dungeon, DungeonRoom


class RoomManager(esper.Processor):
    """Manages current room state and transitions.

    Responsibilities:
    - Track current room position
    - Handle room state transitions
    - Spawn/despawn room contents
    - Lock/unlock doors based on room state
    """

    def __init__(self, dungeon: Dungeon):
        """Initialize room manager with dungeon.

        Args:
            dungeon: Complete dungeon layout
        """
        super().__init__()
        self.dungeon = dungeon
        self.current_position = dungeon.start_position
        self.current_room = dungeon.rooms[self.current_position]

    def process(self):
        """Process room manager (currently no per-frame logic)."""
        pass
