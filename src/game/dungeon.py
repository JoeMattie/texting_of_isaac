"""Dungeon generation and data structures."""
import random
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


def generate_dungeon(target_size: int = 15) -> Dungeon:
    """Generate dungeon using main path first algorithm.

    Args:
        target_size: Target number of rooms (12-18)

    Returns:
        Complete dungeon with guaranteed path to boss
    """
    dungeon = Dungeon()

    # Step 1: Place start room at (0, 0)
    start_pos = (0, 0)
    start_room = DungeonRoom(
        position=start_pos,
        room_type=RoomType.START,
        doors={},
        visited=False,
        cleared=True,
        state=RoomState.PEACEFUL
    )
    dungeon.rooms[start_pos] = start_room
    dungeon.start_position = start_pos
    dungeon.main_path.append(start_pos)

    # Step 2: Generate main path (10-12 rooms including start)
    current_pos = start_pos
    main_path_length = random.randint(10, 12)

    for i in range(main_path_length - 1):  # -1 because start already placed
        # Choose next position (random walk)
        next_pos = _choose_next_position(current_pos, dungeon.rooms)

        # Determine room type
        if i == int((main_path_length - 1) * 0.4):
            room_type = RoomType.MINIBOSS
            dungeon.miniboss_position = next_pos
        elif i == main_path_length - 2:
            room_type = RoomType.BOSS
            dungeon.boss_position = next_pos
        else:
            room_type = RoomType.COMBAT

        # Create room
        room = DungeonRoom(
            position=next_pos,
            room_type=room_type,
            doors={},
            enemies=_generate_enemy_config(room_type) if room_type in [RoomType.COMBAT, RoomType.MINIBOSS] else []
        )
        dungeon.rooms[next_pos] = room

        # Create bidirectional door connection
        direction = get_direction(current_pos, next_pos)
        opposite = get_opposite_direction(direction)
        dungeon.rooms[current_pos].doors[direction] = next_pos
        dungeon.rooms[next_pos].doors[opposite] = current_pos

        dungeon.main_path.append(next_pos)
        current_pos = next_pos

    return dungeon


def _choose_next_position(current: tuple[int, int], existing_rooms: dict[tuple[int, int], DungeonRoom]) -> tuple[int, int]:
    """Choose next position for main path.

    Args:
        current: Current position
        existing_rooms: Already placed rooms

    Returns:
        Next position for path

    Raises:
        RuntimeError: If no available positions
    """
    x, y = current
    directions = [
        (x, y + 1),  # South
        (x, y - 1),  # North
        (x + 1, y),  # East
        (x - 1, y),  # West
    ]

    # Filter out positions that already have rooms
    available = [pos for pos in directions if pos not in existing_rooms]

    if not available:
        raise RuntimeError("No available positions - dungeon generation stuck")

    return random.choice(available)


def _generate_enemy_config(room_type: RoomType) -> list[dict]:
    """Generate enemy spawn configuration for room.

    Args:
        room_type: Type of room

    Returns:
        List of enemy spawn configs
    """
    if room_type == RoomType.COMBAT:
        num_enemies = random.randint(2, 5)
        enemy_types = ["chaser", "shooter", "orbiter", "turret", "tank"]

        return [
            {"type": random.choice(enemy_types), "count": 1}
            for _ in range(num_enemies)
        ]
    elif room_type == RoomType.MINIBOSS:
        miniboss_type = random.choice(["glutton", "hoarder", "sentinel"])
        return [{"type": miniboss_type, "count": 1}]
    else:
        return []
