"""Room manager system for handling room state and transitions."""
import esper
from src.game.dungeon import Dungeon, DungeonRoom, RoomType, RoomState


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

    def transition_to_room(self, new_position: tuple[int, int], entry_direction: str) -> None:
        """Transition player to new room.

        This method handles all the logic for moving from the current room
        to a new room, including state updates and entity management.

        Args:
            new_position: Grid coordinates of new room (x, y)
            entry_direction: Direction player came from ("north", "south", "east", "west")
        """
        # Update position tracking
        self.current_position = new_position
        self.current_room = self.dungeon.rooms[new_position]

        # Mark room as visited
        self.current_room.visited = True

        # Determine and set room state based on room type and cleared status
        if self.current_room.room_type in [RoomType.START, RoomType.TREASURE, RoomType.SHOP, RoomType.SECRET]:
            # Peaceful rooms (no combat)
            self.current_room.state = RoomState.PEACEFUL
        elif self.current_room.cleared:
            # Revisiting a previously cleared combat room
            self.current_room.state = RoomState.CLEARED
        else:
            # Entering uncleared combat room
            self.current_room.state = RoomState.COMBAT

    def process(self):
        """Process room manager (currently no per-frame logic)."""
        pass
