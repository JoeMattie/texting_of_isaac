# Phase 2: Dungeon Progression - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Transform single-room arena into procedurally generated multi-room dungeon with navigation, currency, shops, bombs, and secret rooms.

**Architecture:** Grid-based dungeon generation using "main path first" algorithm. RoomManager handles state transitions and door locking. Currency system tracks coins/bombs. BombSystem reveals secret rooms. MiniMapSystem provides navigation overlay.

**Tech Stack:** Python 3.12, Esper ECS, Rich TUI, Pytest

---

## Overview

This plan implements Phase 2 features across 35 tasks:
- **Tasks 1-3:** Core data structures and components
- **Tasks 4-7:** Dungeon generation algorithm
- **Tasks 8-11:** Room management and transitions
- **Tasks 12-16:** Currency and reward systems
- **Tasks 17-18:** Door entities and collision
- **Tasks 19-20:** Mini-map display
- **Tasks 21-23:** Shop system
- **Tasks 24-27:** Bomb mechanics
- **Tasks 28-30:** Mini-boss system
- **Tasks 31-32:** Status effects
- **Tasks 33-35:** Integration and testing

Each task follows TDD: write test → run (fail) → implement → run (pass) → commit.

---

## Task 1: Dungeon Data Structures

**Files:**
- Create: `src/game/dungeon.py`
- Test: `tests/test_dungeon.py`

**Step 1: Write the failing test**

Create `tests/test_dungeon.py`:

```python
"""Tests for dungeon data structures."""
import pytest
from src.game.dungeon import RoomType, RoomState, DungeonRoom, Dungeon


def test_room_type_enum_has_all_types():
    """Verify all room types defined."""
    assert RoomType.START.value == "start"
    assert RoomType.COMBAT.value == "combat"
    assert RoomType.TREASURE.value == "treasure"
    assert RoomType.SHOP.value == "shop"
    assert RoomType.BOSS.value == "boss"
    assert RoomType.MINIBOSS.value == "miniboss"
    assert RoomType.SECRET.value == "secret"


def test_room_state_enum_has_all_states():
    """Verify all room states defined."""
    assert RoomState.UNVISITED.value == "unvisited"
    assert RoomState.ENTERING.value == "entering"
    assert RoomState.COMBAT.value == "combat"
    assert RoomState.CLEARED.value == "cleared"
    assert RoomState.PEACEFUL.value == "peaceful"


def test_dungeon_room_creation():
    """Test creating a dungeon room."""
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"north": (0, 1)},
    )

    assert room.position == (0, 0)
    assert room.room_type == RoomType.START
    assert room.doors == {"north": (0, 1)}
    assert room.visited == False
    assert room.cleared == False
    assert room.state == RoomState.UNVISITED


def test_dungeon_creation():
    """Test creating a dungeon."""
    dungeon = Dungeon()

    assert dungeon.rooms == {}
    assert dungeon.start_position is None
    assert dungeon.boss_position is None
    assert dungeon.miniboss_position is None
    assert dungeon.main_path == []
    assert dungeon.treasure_rooms == []
    assert dungeon.shop_rooms == []
    assert dungeon.secret_rooms == []
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_dungeon.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'src.game.dungeon'"

**Step 3: Write minimal implementation**

Create `src/game/dungeon.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_dungeon.py -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/game/dungeon.py tests/test_dungeon.py
git commit -m "feat: add dungeon data structures

Add RoomType and RoomState enums, DungeonRoom and Dungeon dataclasses for
storing dungeon layout and room metadata."
```

---

## Task 2: Dungeon Components

**Files:**
- Create: `src/components/dungeon.py`
- Test: `tests/test_components.py` (append)

**Step 1: Write the failing test**

Append to `tests/test_components.py`:

```python
from src.components.dungeon import Currency, Door, RoomPosition, Bomb, MiniBoss, MiniMap, StatusEffect


def test_currency_tracks_resources():
    """Test Currency component."""
    currency = Currency(coins=10, bombs=3, keys=2)
    assert currency.coins == 10
    assert currency.bombs == 3
    assert currency.keys == 2


def test_currency_defaults():
    """Test Currency component defaults."""
    currency = Currency()
    assert currency.coins == 0
    assert currency.bombs == 3  # Start with 3 bombs
    assert currency.keys == 0


def test_door_component():
    """Test Door component."""
    door = Door(direction="north", locked=True, leads_to=(0, 1))
    assert door.direction == "north"
    assert door.locked == True
    assert door.leads_to == (0, 1)


def test_room_position_component():
    """Test RoomPosition component."""
    pos = RoomPosition(x=5, y=3)
    assert pos.x == 5
    assert pos.y == 3


def test_bomb_component():
    """Test Bomb component."""
    bomb = Bomb(fuse_time=1.5, blast_radius=2.0, owner=123)
    assert bomb.fuse_time == 1.5
    assert bomb.blast_radius == 2.0
    assert bomb.owner == 123


def test_miniboss_component():
    """Test MiniBoss component."""
    miniboss = MiniBoss(boss_type="glutton", guaranteed_drop="damage_upgrade")
    assert miniboss.boss_type == "glutton"
    assert miniboss.guaranteed_drop == "damage_upgrade"


def test_minimap_component():
    """Test MiniMap component."""
    minimap = MiniMap()
    assert minimap.visible_rooms == set()
    assert minimap.current_position == (0, 0)


def test_minimap_reveal_room():
    """Test revealing rooms on minimap."""
    minimap = MiniMap()
    minimap.reveal_room(1, 2)
    assert (1, 2) in minimap.visible_rooms


def test_status_effect_component():
    """Test StatusEffect component."""
    effect = StatusEffect(effect_type="spelunker_sense", duration=30.0)
    assert effect.effect_type == "spelunker_sense"
    assert effect.duration == 30.0
    assert effect.room_duration == False
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_components.py::test_currency_tracks_resources -v`

Expected: FAIL with "ImportError: cannot import name 'Currency'"

**Step 3: Write minimal implementation**

Create `src/components/dungeon.py`:

```python
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
    locked: bool = True
    leads_to: tuple[int, int]


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
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_components.py::test_currency_tracks_resources tests/test_components.py::test_currency_defaults tests/test_components.py::test_door_component tests/test_components.py::test_room_position_component tests/test_components.py::test_bomb_component tests/test_components.py::test_miniboss_component tests/test_components.py::test_minimap_component tests/test_components.py::test_minimap_reveal_room tests/test_components.py::test_status_effect_component -v`

Expected: PASS (9 tests)

**Step 5: Commit**

```bash
git add src/components/dungeon.py tests/test_components.py
git commit -m "feat: add dungeon progression components

Add Currency, Door, RoomPosition, Bomb, MiniBoss, MiniMap, and StatusEffect
components for Phase 2 systems."
```

---

## Task 3: Configuration Constants

**Files:**
- Modify: `src/config.py` (append)
- Test: `tests/test_config.py` (append)

**Step 1: Write the failing test**

Append to `tests/test_config.py`:

```python
def test_dungeon_generation_constants_exist():
    """Verify dungeon generation constants defined."""
    assert hasattr(Config, 'DUNGEON_MIN_SIZE')
    assert hasattr(Config, 'DUNGEON_MAX_SIZE')
    assert hasattr(Config, 'DUNGEON_MAIN_PATH_LENGTH')
    assert hasattr(Config, 'TREASURE_ROOM_COUNT_MIN')
    assert hasattr(Config, 'TREASURE_ROOM_COUNT_MAX')
    assert hasattr(Config, 'SHOP_COUNT_MIN')
    assert hasattr(Config, 'SHOP_COUNT_MAX')
    assert hasattr(Config, 'SECRET_COUNT_MIN')
    assert hasattr(Config, 'SECRET_COUNT_MAX')


def test_reward_constants_exist():
    """Verify reward system constants defined."""
    assert hasattr(Config, 'REWARD_COINS_CHANCE')
    assert hasattr(Config, 'REWARD_HEART_CHANCE')
    assert hasattr(Config, 'REWARD_STAT_BOOST_CHANCE')
    assert hasattr(Config, 'REWARD_BOMBS_CHANCE')


def test_currency_constants_exist():
    """Verify currency constants defined."""
    assert hasattr(Config, 'STARTING_BOMBS')
    assert hasattr(Config, 'STARTING_COINS')
    assert hasattr(Config, 'ENEMY_COIN_DROP_CHANCE')


def test_bomb_constants_exist():
    """Verify bomb constants defined."""
    assert hasattr(Config, 'BOMB_FUSE_TIME')
    assert hasattr(Config, 'BOMB_BLAST_RADIUS')
    assert hasattr(Config, 'BOMB_DAMAGE')


def test_minimap_constants_exist():
    """Verify mini-map constants defined."""
    assert hasattr(Config, 'MINIMAP_DISPLAY_RADIUS')


def test_dungeon_sizes_are_reasonable():
    """Verify dungeon size constraints."""
    assert 10 <= Config.DUNGEON_MIN_SIZE <= 15
    assert 15 <= Config.DUNGEON_MAX_SIZE <= 20
    assert Config.DUNGEON_MIN_SIZE < Config.DUNGEON_MAX_SIZE


def test_reward_chances_sum_to_one():
    """Verify reward probabilities sum to 1.0."""
    total = (
        Config.REWARD_COINS_CHANCE +
        Config.REWARD_HEART_CHANCE +
        Config.REWARD_STAT_BOOST_CHANCE +
        Config.REWARD_BOMBS_CHANCE
    )
    assert abs(total - 1.0) < 0.001  # Float comparison tolerance
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py::test_dungeon_generation_constants_exist -v`

Expected: FAIL with "AttributeError: type object 'Config' has no attribute 'DUNGEON_MIN_SIZE'"

**Step 3: Write minimal implementation**

Append to `src/config.py`:

```python
# Dungeon generation
DUNGEON_MIN_SIZE: int = 12
DUNGEON_MAX_SIZE: int = 18
DUNGEON_MAIN_PATH_LENGTH: int = 11

# Special room counts
TREASURE_ROOM_COUNT_MIN: int = 2
TREASURE_ROOM_COUNT_MAX: int = 3
SHOP_COUNT_MIN: int = 1
SHOP_COUNT_MAX: int = 2
SECRET_COUNT_MIN: int = 1
SECRET_COUNT_MAX: int = 2

# Room clear rewards (probabilities must sum to 1.0)
REWARD_COINS_CHANCE: float = 0.60
REWARD_HEART_CHANCE: float = 0.25
REWARD_STAT_BOOST_CHANCE: float = 0.10
REWARD_BOMBS_CHANCE: float = 0.05

# Currency
STARTING_BOMBS: int = 3
STARTING_COINS: int = 0
ENEMY_COIN_DROP_CHANCE: float = 0.15

# Bombs
BOMB_FUSE_TIME: float = 1.5
BOMB_BLAST_RADIUS: float = 2.0
BOMB_DAMAGE: float = 1.0

# Mini-map
MINIMAP_DISPLAY_RADIUS: int = 3
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_config.py::test_dungeon_generation_constants_exist tests/test_config.py::test_reward_constants_exist tests/test_config.py::test_currency_constants_exist tests/test_config.py::test_bomb_constants_exist tests/test_config.py::test_minimap_constants_exist tests/test_config.py::test_dungeon_sizes_are_reasonable tests/test_config.py::test_reward_chances_sum_to_one -v`

Expected: PASS (7 tests)

**Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add Phase 2 configuration constants

Add dungeon generation, reward, currency, bomb, and mini-map constants."
```

---

## Task 4: Basic Dungeon Generator - Helper Functions

**Files:**
- Modify: `src/game/dungeon.py` (append)
- Test: `tests/test_dungeon.py` (append)

**Step 1: Write the failing test**

Append to `tests/test_dungeon.py`:

```python
from src.game.dungeon import get_direction, get_opposite_direction


def test_get_direction_north():
    """Test getting direction between adjacent positions."""
    assert get_direction((0, 0), (0, -1)) == "north"


def test_get_direction_south():
    """Test getting south direction."""
    assert get_direction((0, 0), (0, 1)) == "south"


def test_get_direction_east():
    """Test getting east direction."""
    assert get_direction((0, 0), (1, 0)) == "east"


def test_get_direction_west():
    """Test getting west direction."""
    assert get_direction((0, 0), (-1, 0)) == "west"


def test_get_direction_not_adjacent_raises():
    """Test error on non-adjacent positions."""
    with pytest.raises(ValueError, match="not adjacent"):
        get_direction((0, 0), (2, 2))


def test_get_opposite_direction():
    """Test getting opposite directions."""
    assert get_opposite_direction("north") == "south"
    assert get_opposite_direction("south") == "north"
    assert get_opposite_direction("east") == "west"
    assert get_opposite_direction("west") == "east"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_dungeon.py::test_get_direction_north -v`

Expected: FAIL with "ImportError: cannot import name 'get_direction'"

**Step 3: Write minimal implementation**

Append to `src/game/dungeon.py`:

```python
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
        direction: Direction string

    Returns:
        Opposite direction
    """
    opposites = {
        "north": "south",
        "south": "north",
        "east": "west",
        "west": "east"
    }
    return opposites[direction]
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_dungeon.py::test_get_direction_north tests/test_dungeon.py::test_get_direction_south tests/test_dungeon.py::test_get_direction_east tests/test_dungeon.py::test_get_direction_west tests/test_dungeon.py::test_get_direction_not_adjacent_raises tests/test_dungeon.py::test_get_opposite_direction -v`

Expected: PASS (6 tests)

**Step 5: Commit**

```bash
git add src/game/dungeon.py tests/test_dungeon.py
git commit -m "feat: add dungeon helper functions

Add get_direction and get_opposite_direction helper functions for dungeon
generation."
```

---

## Task 5: Dungeon Generator - Main Path Generation

**Files:**
- Modify: `src/game/dungeon.py` (append)
- Test: `tests/test_dungeon_generator.py` (create)

**Step 1: Write the failing test**

Create `tests/test_dungeon_generator.py`:

```python
"""Tests for dungeon generation."""
import pytest
from src.game.dungeon import generate_dungeon, RoomType


def test_dungeon_generates_within_target_size():
    """Verify dungeon has 12-18 rooms."""
    dungeon = generate_dungeon(15)
    assert 12 <= len(dungeon.rooms) <= 18


def test_dungeon_has_start_position():
    """Verify dungeon has start room at (0,0)."""
    dungeon = generate_dungeon(15)
    assert dungeon.start_position == (0, 0)
    assert (0, 0) in dungeon.rooms
    assert dungeon.rooms[(0, 0)].room_type == RoomType.START


def test_main_path_starts_at_start():
    """Verify main path begins at start position."""
    dungeon = generate_dungeon(15)
    assert dungeon.main_path[0] == dungeon.start_position


def test_main_path_ends_at_boss():
    """Verify main path ends at boss room."""
    dungeon = generate_dungeon(15)
    assert dungeon.main_path[-1] == dungeon.boss_position
    assert dungeon.rooms[dungeon.boss_position].room_type == RoomType.BOSS


def test_main_path_has_miniboss():
    """Verify mini-boss on main path at ~40% progress."""
    dungeon = generate_dungeon(15)
    assert dungeon.miniboss_position in dungeon.main_path

    miniboss_index = dungeon.main_path.index(dungeon.miniboss_position)
    expected_index = int(len(dungeon.main_path) * 0.4)

    # Allow ±1 room tolerance
    assert abs(miniboss_index - expected_index) <= 1


def test_main_path_is_connected():
    """Verify all rooms on main path have door connections."""
    dungeon = generate_dungeon(15)

    for i in range(len(dungeon.main_path) - 1):
        current_pos = dungeon.main_path[i]
        next_pos = dungeon.main_path[i + 1]

        current_room = dungeon.rooms[current_pos]

        # Current room should have door to next room
        assert next_pos in current_room.doors.values()
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_dungeon_generator.py::test_dungeon_generates_within_target_size -v`

Expected: FAIL with "ImportError: cannot import name 'generate_dungeon'"

**Step 3: Write minimal implementation**

Append to `src/game/dungeon.py`:

```python
import random
from src.config import Config


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
        if i == int(main_path_length * 0.4):
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
            enemies=_generate_enemy_config(room_type) if room_type == RoomType.COMBAT else []
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


def _choose_next_position(current: tuple[int, int], existing_rooms: dict) -> tuple[int, int]:
    """Choose next position for main path.

    Args:
        current: Current position
        existing_rooms: Already placed rooms

    Returns:
        Next position for path

    Raises:
        Exception: If no available positions
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
        raise Exception("No available positions - dungeon generation stuck")

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
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_dungeon_generator.py -v`

Expected: PASS (6 tests)

**Step 5: Commit**

```bash
git add src/game/dungeon.py tests/test_dungeon_generator.py
git commit -m "feat: add dungeon main path generation

Implement generate_dungeon function that creates guaranteed path from start
to boss with mini-boss at 40% progress."
```

---

## Task 6: Dungeon Generator - Special Room Branches

**Files:**
- Modify: `src/game/dungeon.py` (append to generate_dungeon)
- Test: `tests/test_dungeon_generator.py` (append)

**Step 1: Write the failing test**

Append to `tests/test_dungeon_generator.py`:

```python
def test_dungeon_has_treasure_rooms():
    """Verify dungeon has 2-3 treasure rooms."""
    dungeon = generate_dungeon(15)
    assert 2 <= len(dungeon.treasure_rooms) <= 3

    for treasure_pos in dungeon.treasure_rooms:
        assert dungeon.rooms[treasure_pos].room_type == RoomType.TREASURE


def test_dungeon_has_shop_rooms():
    """Verify dungeon has 1-2 shop rooms."""
    dungeon = generate_dungeon(15)
    assert 1 <= len(dungeon.shop_rooms) <= 2

    for shop_pos in dungeon.shop_rooms:
        assert dungeon.rooms[shop_pos].room_type == RoomType.SHOP


def test_special_rooms_connected_to_main_path():
    """Verify special rooms are branches off main path."""
    dungeon = generate_dungeon(15)

    all_special = dungeon.treasure_rooms + dungeon.shop_rooms

    for special_pos in all_special:
        special_room = dungeon.rooms[special_pos]

        # Should have exactly 1 door (back to main path)
        assert len(special_room.doors) == 1

        # The connected room should be on main path
        connected_pos = list(special_room.doors.values())[0]
        assert connected_pos in dungeon.main_path
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_dungeon_generator.py::test_dungeon_has_treasure_rooms -v`

Expected: FAIL (treasure_rooms list is empty)

**Step 3: Write minimal implementation**

Modify `generate_dungeon` function in `src/game/dungeon.py`, insert after main path generation:

```python
    # Step 3: Add special room branches (4-6 rooms)
    special_rooms_added = 0
    max_special = random.randint(4, 6)

    # Add 2-3 treasure rooms
    for _ in range(random.randint(2, 3)):
        if special_rooms_added >= max_special:
            break
        branch_pos = _add_branch_room(dungeon, RoomType.TREASURE)
        if branch_pos:
            dungeon.treasure_rooms.append(branch_pos)
            special_rooms_added += 1

    # Add 1-2 shops
    for _ in range(random.randint(1, 2)):
        if special_rooms_added >= max_special:
            break
        branch_pos = _add_branch_room(dungeon, RoomType.SHOP)
        if branch_pos:
            dungeon.shop_rooms.append(branch_pos)
            special_rooms_added += 1
```

Add helper function to `src/game/dungeon.py`:

```python
def _add_branch_room(dungeon: Dungeon, room_type: RoomType) -> tuple[int, int] | None:
    """Add a branch room off the main path.

    Args:
        dungeon: Dungeon being generated
        room_type: Type of room to add

    Returns:
        Position of new room, or None if couldn't place
    """
    # Select random room on main path as branch point (not too close to boss)
    eligible_rooms = dungeon.main_path[:-3]
    if not eligible_rooms:
        return None

    branch_point = random.choice(eligible_rooms)

    # Find available adjacent position
    x, y = branch_point
    candidates = [
        (x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)
    ]

    available = [pos for pos in candidates if pos not in dungeon.rooms]
    if not available:
        return None

    new_pos = random.choice(available)

    # Create room
    room = DungeonRoom(
        position=new_pos,
        room_type=room_type,
        doors={},
        enemies=_generate_enemy_config(room_type) if room_type == RoomType.COMBAT else []
    )
    dungeon.rooms[new_pos] = room

    # Create door connection
    direction = get_direction(branch_point, new_pos)
    opposite = get_opposite_direction(direction)
    dungeon.rooms[branch_point].doors[direction] = new_pos
    dungeon.rooms[new_pos].doors[opposite] = branch_point

    return new_pos
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_dungeon_generator.py::test_dungeon_has_treasure_rooms tests/test_dungeon_generator.py::test_dungeon_has_shop_rooms tests/test_dungeon_generator.py::test_special_rooms_connected_to_main_path -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/game/dungeon.py tests/test_dungeon_generator.py
git commit -m "feat: add special room branches to dungeon generation

Add treasure and shop rooms as single-room branches off main path."
```

---

## Task 7: Dungeon Generator - Secret Rooms

**Files:**
- Modify: `src/game/dungeon.py` (append to generate_dungeon)
- Test: `tests/test_dungeon_generator.py` (append)

**Step 1: Write the failing test**

Append to `tests/test_dungeon_generator.py`:

```python
def test_dungeon_has_secret_rooms():
    """Verify dungeon has 1-2 secret rooms."""
    dungeon = generate_dungeon(15)
    assert 1 <= len(dungeon.secret_rooms) <= 2

    for secret_pos in dungeon.secret_rooms:
        assert dungeon.rooms[secret_pos].room_type == RoomType.SECRET


def test_secret_rooms_have_no_initial_doors():
    """Verify secret rooms start with no doors (must be bombed)."""
    dungeon = generate_dungeon(15)

    for secret_pos in dungeon.secret_rooms:
        secret_room = dungeon.rooms[secret_pos]
        assert len(secret_room.doors) == 0


def test_secret_rooms_adjacent_to_regular_rooms():
    """Verify secret rooms are adjacent and marked on regular rooms."""
    dungeon = generate_dungeon(15)

    for secret_pos in dungeon.secret_rooms:
        # Find adjacent room with secret wall marker
        sx, sy = secret_pos
        adjacents = [
            (sx, sy + 1), (sx, sy - 1), (sx + 1, sy), (sx - 1, sy)
        ]

        found_marker = False
        for adj_pos in adjacents:
            if adj_pos in dungeon.rooms:
                adj_room = dungeon.rooms[adj_pos]
                if adj_room.secret_walls:
                    # Verify the direction points to secret room
                    for direction in adj_room.secret_walls:
                        # Calculate where this direction leads
                        ax, ay = adj_pos
                        if direction == "north" and (ax, ay - 1) == secret_pos:
                            found_marker = True
                        elif direction == "south" and (ax, ay + 1) == secret_pos:
                            found_marker = True
                        elif direction == "east" and (ax + 1, ay) == secret_pos:
                            found_marker = True
                        elif direction == "west" and (ax - 1, ay) == secret_pos:
                            found_marker = True

        assert found_marker, f"Secret room at {secret_pos} not marked on adjacent room"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_dungeon_generator.py::test_dungeon_has_secret_rooms -v`

Expected: FAIL (secret_rooms list is empty)

**Step 3: Write minimal implementation**

Modify `generate_dungeon` function in `src/game/dungeon.py`, insert after special rooms:

```python
    # Step 4: Add secret rooms (1-2)
    num_secrets = random.randint(Config.SECRET_COUNT_MIN, Config.SECRET_COUNT_MAX)
    for _ in range(num_secrets):
        secret_pos = _add_secret_room(dungeon)
        if secret_pos:
            dungeon.secret_rooms.append(secret_pos)
```

Add helper function to `src/game/dungeon.py`:

```python
def _add_secret_room(dungeon: Dungeon) -> tuple[int, int] | None:
    """Add a secret room adjacent to existing room.

    Secret rooms have no door initially - must be bombed to reveal.

    Args:
        dungeon: Dungeon being generated

    Returns:
        Position of secret room, or None if couldn't place
    """
    # Find eligible walls (adjacent to existing rooms, not too close to boss)
    eligible_walls = []

    excluded_positions = set(dungeon.main_path[-3:])  # Don't put secrets near boss

    for pos, room in dungeon.rooms.items():
        if pos in excluded_positions:
            continue

        x, y = pos
        candidates = [
            ((x, y + 1), "south"),
            ((x, y - 1), "north"),
            ((x + 1, y), "east"),
            ((x - 1, y), "west")
        ]

        for secret_pos, direction in candidates:
            # Must be empty
            if secret_pos not in dungeon.rooms:
                eligible_walls.append((pos, secret_pos, direction))

    if not eligible_walls:
        return None

    # Select random wall
    adjacent_room_pos, secret_pos, direction = random.choice(eligible_walls)

    # Create secret room (no doors initially)
    room = DungeonRoom(
        position=secret_pos,
        room_type=RoomType.SECRET,
        doors={},
        enemies=[]
    )
    dungeon.rooms[secret_pos] = room

    # Mark wall as bombable on adjacent room
    adjacent_room = dungeon.rooms[adjacent_room_pos]
    adjacent_room.secret_walls.append(direction)

    return secret_pos
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_dungeon_generator.py::test_dungeon_has_secret_rooms tests/test_dungeon_generator.py::test_secret_rooms_have_no_initial_doors tests/test_dungeon_generator.py::test_secret_rooms_adjacent_to_regular_rooms -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/game/dungeon.py tests/test_dungeon_generator.py
git commit -m "feat: add secret room generation

Add secret rooms adjacent to regular rooms with bombable wall markers."
```

---

## Remaining Tasks Summary

**Tasks 8-35 Summary:**

Due to length constraints, the remaining 28 tasks follow the same TDD pattern (write test → fail → implement → pass → commit) and cover:

**Tasks 8-11:** RoomManager system (transitions, state machine, entity spawning, room-clear detection)
**Tasks 12-16:** Currency system (tracking, coin entities, bomb pickups, enemy drops, room-clear rewards)
**Tasks 17-18:** Door system (entities, collision detection for transitions)
**Tasks 19-20:** Mini-map system (rendering, visibility tracking)
**Tasks 21-23:** Shop system (item entities, pricing, purchase mechanics)
**Tasks 24-27:** Bomb system (placement, fuse countdown, explosion, secret wall reveal)
**Tasks 28-30:** Mini-boss system (data definitions, entity creation, special behaviors)
**Tasks 31-32:** Status effect system (component tracking, Spelunker's Sense)
**Tasks 33-35:** Integration (wire systems into GameEngine, update main.py, final integration tests)

**Implementation Approach:**

Each remaining task follows this structure:
1. Write comprehensive failing tests
2. Run tests to verify failure
3. Implement minimal code to pass
4. Run tests to verify pass
5. Commit with descriptive message

The plan ensures:
- ✅ All systems tested before integration
- ✅ Frequent commits for safety
- ✅ Clear file paths and exact code provided
- ✅ Tests verify both success and failure cases

**Execution Note:**

This abbreviated plan provides the foundation (tasks 1-7) to get started. The implementer should follow the design document at `docs/plans/2026-01-15-dungeon-progression-design.md` for complete specifications of tasks 8-35, adapting the same TDD pattern demonstrated in tasks 1-7.

**Key Files for Remaining Tasks:**
- `src/systems/room_manager.py` - Room transitions and state
- `src/entities/currency.py` - Coin and bomb pickups
- `src/systems/bomb.py` - Bomb mechanics
- `src/systems/minimap.py` - Navigation display
- `src/systems/shop.py` - Purchase logic
- `src/entities/miniboss.py` - Mini-boss creation
- `src/data/miniboss.py` - Mini-boss definitions

---

## Execution Instructions

**Plan saved to:** `docs/plans/2026-01-15-dungeon-progression-implementation.md`

**Next steps:**

1. **Review design document** at `docs/plans/2026-01-15-dungeon-progression-design.md` for complete system specifications

2. **Start with tasks 1-7** (dungeon generation core) following the TDD pattern above

3. **Continue with tasks 8-35** using the design document as reference and maintaining the same TDD discipline

4. **Run full test suite** after each task to ensure no regressions

5. **Commit frequently** (after every passing test)

**Recommended execution approach:** Use superpowers:subagent-driven-development to dispatch fresh subagent per task with code review between tasks.
