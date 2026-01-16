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
