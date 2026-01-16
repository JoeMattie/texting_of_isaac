"""Components for dungeon progression systems."""
from dataclasses import dataclass, field


@dataclass
class Currency:
    """Tracks player resources."""
    coins: int = 0
    bombs: int = 3
    keys: int = 0


@dataclass
class Door:
    """Door entity component."""
    direction: str  # "north", "south", "east", "west"
    leads_to: tuple[int, int]
    locked: bool = True


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


@dataclass
class MiniBoss:
    """Mini-boss component."""
    boss_type: str
    guaranteed_drop: str
    teleport_timer: float = 5.0  # For sentinel type


@dataclass
class MiniMap:
    """Mini-map state."""
    visible_rooms: set[tuple[int, int]] = field(default_factory=set)
    current_position: tuple[int, int] = (0, 0)

    def reveal_room(self, x: int, y: int):
        """Mark room as visited."""
        self.visible_rooms.add((x, y))


@dataclass
class StatusEffect:
    """Status effect component."""
    effect_type: str
    duration: float
    room_duration: bool = False
    timer: float = 0.0
