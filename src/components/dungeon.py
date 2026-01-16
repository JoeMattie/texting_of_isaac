"""Components for dungeon progression systems."""
from dataclasses import dataclass, field


@dataclass
class Currency:
    """Tracks player resources."""
    coins: int = 0
    bombs: int = 3
    keys: int = 0

    def __post_init__(self):
        if self.coins < 0:
            raise ValueError("coins must be non-negative")
        if self.bombs < 0:
            raise ValueError("bombs must be non-negative")
        if self.keys < 0:
            raise ValueError("keys must be non-negative")


@dataclass
class Door:
    """Door entity component."""
    direction: str  # "north", "south", "east", "west"
    leads_to: tuple[int, int]
    locked: bool = True

    def __post_init__(self):
        valid_directions = {"north", "south", "east", "west"}
        if self.direction not in valid_directions:
            raise ValueError("direction must be one of: north, south, east, west")


@dataclass
class RoomPosition:
    """Current position in dungeon grid."""
    x: int = 0
    y: int = 0


@dataclass
class Bomb:
    """Bomb entity component."""
    fuse_time: float = 1.5
    blast_radius: float = 2.0
    owner: int = 0  # Player entity ID

    def __post_init__(self):
        if self.fuse_time <= 0:
            raise ValueError("fuse_time must be positive")
        if self.blast_radius <= 0:
            raise ValueError("blast_radius must be positive")


@dataclass
class MiniBoss:
    """Mini-boss component."""
    boss_type: str
    guaranteed_drop: str
    teleport_timer: float = 5.0  # For sentinel type

    def __post_init__(self):
        valid_boss_types = {"glutton", "hoarder", "sentinel"}
        if not self.boss_type:
            raise ValueError("boss_type cannot be empty")
        if self.boss_type not in valid_boss_types:
            raise ValueError("boss_type must be one of: glutton, hoarder, sentinel")
        if not self.guaranteed_drop:
            raise ValueError("guaranteed_drop cannot be empty")
        if self.teleport_timer <= 0:
            raise ValueError("teleport_timer must be positive")


@dataclass
class MiniMap:
    """Mini-map state."""
    visible_rooms: set[tuple[int, int]] = field(default_factory=set)
    current_position: tuple[int, int] = (0, 0)

    def reveal_room(self, x: int, y: int) -> None:
        """Mark room as visited."""
        self.visible_rooms.add((x, y))

    def get_display_bounds(self) -> tuple[int, int, int, int]:
        """Get min/max coordinates for display (±3 from current).

        Returns:
            (min_x, min_y, max_x, max_y) - Display boundary coordinates
        """
        from src.config import Config

        cx, cy = self.current_position
        radius = Config.MINIMAP_DISPLAY_RADIUS
        return (cx - radius, cy - radius, cx + radius, cy + radius)

    def should_show_room(self, position: tuple[int, int], dungeon) -> bool:
        """Check if unvisited room should be shown (adjacent to visited via door).

        Args:
            position: Room coordinates to check
            dungeon: Dungeon instance with room connections

        Returns:
            True if room should be shown as adjacent unvisited (□ symbol)
        """
        # Don't show if already visited (will use ■ symbol)
        if position in self.visible_rooms:
            return False

        # Don't show if room doesn't exist
        if position not in dungeon.rooms:
            return False

        # Show if any visited room has a door to this room
        for visited_pos in self.visible_rooms:
            if visited_pos in dungeon.rooms:
                visited_room = dungeon.rooms[visited_pos]
                # Check if this visited room has a door leading to target position
                if position in visited_room.doors.values():
                    return True

        return False


@dataclass
class StatusEffect:
    """Status effect component."""
    effect_type: str
    duration: float
    room_duration: bool = False
    timer: float = 0.0

    def __post_init__(self):
        if not self.effect_type:
            raise ValueError("effect_type cannot be empty")
        if self.duration < 0:
            raise ValueError("duration must be non-negative")
