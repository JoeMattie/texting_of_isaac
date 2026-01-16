"""Dungeon generation and data structures."""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class RoomType(Enum):
    """Types of rooms in the dungeon."""
    START = "start"
    COMBAT = "combat"
    TREASURE = "treasure"
    SHOP = "shop"
    BOSS = "boss"
    MINIBOSS = "miniboss"
    SECRET = "secret"


class RoomState(Enum):
    """States a room can be in."""
    UNVISITED = "unvisited"
    ENTERING = "entering"
    COMBAT = "combat"
    CLEARED = "cleared"
    PEACEFUL = "peaceful"


@dataclass
class DungeonRoom:
    """Represents one room in the dungeon."""
    position: tuple[int, int]
    room_type: RoomType
    doors: dict[str, tuple[int, int]]
    visited: bool = False
    cleared: bool = False
    state: RoomState = RoomState.UNVISITED
    enemies: list[dict] = field(default_factory=list)
    secret_walls: list[str] = field(default_factory=list)


@dataclass
class Dungeon:
    """Complete dungeon layout."""
    rooms: dict[tuple[int, int], DungeonRoom] = field(default_factory=dict)
    start_position: Optional[tuple[int, int]] = None
    boss_position: Optional[tuple[int, int]] = None
    miniboss_position: Optional[tuple[int, int]] = None
    main_path: list[tuple[int, int]] = field(default_factory=list)
    treasure_rooms: list[tuple[int, int]] = field(default_factory=list)
    shop_rooms: list[tuple[int, int]] = field(default_factory=list)
    secret_rooms: list[tuple[int, int]] = field(default_factory=list)


def get_direction(from_pos: tuple[int, int], to_pos: tuple[int, int]) -> str:
    """Get direction from one position to adjacent position.

    Args:
        from_pos: Starting position (x, y)
        to_pos: Target position (x, y)

    Returns:
        Direction string: "north", "south", "east", or "west"

    Raises:
        ValueError: If positions are not adjacent
    """
    fx, fy = from_pos
    tx, ty = to_pos

    if tx == fx and ty == fy - 1:
        return "north"
    elif tx == fx and ty == fy + 1:
        return "south"
    elif tx == fx + 1 and ty == fy:
        return "east"
    elif tx == fx - 1 and ty == fy:
        return "west"
    else:
        raise ValueError(f"Positions not adjacent: {from_pos} -> {to_pos}")


def get_opposite_direction(direction: str) -> str:
    """Get opposite direction.

    Args:
        direction: Direction string ("north", "south", "east", or "west")

    Returns:
        Opposite direction

    Raises:
        ValueError: If direction is not valid
    """
    opposites = {
        "north": "south",
        "south": "north",
        "east": "west",
        "west": "east"
    }
    if direction not in opposites:
        raise ValueError(f"Invalid direction: {direction}. Must be one of: north, south, east, west")
    return opposites[direction]
