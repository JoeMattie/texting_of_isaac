# Door System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Implement complete door system for room transitions including entity creation, spawning/despawning, locking/unlocking, and player-door collision detection.

**Architecture:** Create door entities positioned at room wall centers, integrate with RoomManager for spawning/despawning based on room connections, implement door locking based on room state, and add player-door collision detection in CollisionSystem to trigger room transitions with proper player repositioning.

**Tech Stack:** Python, Esper ECS, pytest

---

## Task 1: Door Entity Creation Function

**Files:**
- Create: `src/entities/doors.py`
- Test: `tests/test_doors.py`

**Step 1: Write the failing test**

Create `tests/test_doors.py`:

```python
"""Tests for door entity creation."""
import esper
from src.entities.doors import spawn_door
from src.components.core import Position, Sprite, Collider
from src.components.dungeon import Door
from src.config import Config


def test_spawn_door_creates_entity():
    """Test spawn_door creates door entity with all components."""
    esper.clear_database()

    door_ent = spawn_door("test", "north", (1, 2), locked=True)

    assert esper.entity_exists(door_ent)
    assert esper.has_component(door_ent, Position)
    assert esper.has_component(door_ent, Sprite)
    assert esper.has_component(door_ent, Collider)
    assert esper.has_component(door_ent, Door)


def test_spawn_door_north_position():
    """Test north door positioned at top wall center."""
    esper.clear_database()

    door_ent = spawn_door("test", "north", (1, 2))
    pos = esper.component_for_entity(door_ent, Position)

    assert pos.x == Config.ROOM_WIDTH / 2
    assert pos.y == 0


def test_spawn_door_south_position():
    """Test south door positioned at bottom wall center."""
    esper.clear_database()

    door_ent = spawn_door("test", "south", (1, 2))
    pos = esper.component_for_entity(door_ent, Position)

    assert pos.x == Config.ROOM_WIDTH / 2
    assert pos.y == Config.ROOM_HEIGHT - 1


def test_spawn_door_east_position():
    """Test east door positioned at right wall center."""
    esper.clear_database()

    door_ent = spawn_door("test", "east", (1, 2))
    pos = esper.component_for_entity(door_ent, Position)

    assert pos.x == Config.ROOM_WIDTH - 1
    assert pos.y == Config.ROOM_HEIGHT / 2


def test_spawn_door_west_position():
    """Test west door positioned at left wall center."""
    esper.clear_database()

    door_ent = spawn_door("test", "west", (1, 2))
    pos = esper.component_for_entity(door_ent, Position)

    assert pos.x == 0
    assert pos.y == Config.ROOM_HEIGHT / 2


def test_spawn_door_locked_sprite():
    """Test locked door has correct sprite."""
    esper.clear_database()

    door_ent = spawn_door("test", "north", (1, 2), locked=True)
    sprite = esper.component_for_entity(door_ent, Sprite)

    assert sprite.char == "▮"
    assert sprite.color == "red"


def test_spawn_door_unlocked_sprite():
    """Test unlocked door has correct sprite."""
    esper.clear_database()

    door_ent = spawn_door("test", "north", (1, 2), locked=False)
    sprite = esper.component_for_entity(door_ent, Sprite)

    assert sprite.char == "▯"
    assert sprite.color == "cyan"


def test_spawn_door_component_values():
    """Test Door component has correct values."""
    esper.clear_database()

    door_ent = spawn_door("test", "south", (3, 4), locked=False)
    door = esper.component_for_entity(door_ent, Door)

    assert door.direction == "south"
    assert door.leads_to == (3, 4)
    assert door.locked == False


def test_spawn_door_collider_radius():
    """Test door has correct collider radius."""
    esper.clear_database()

    door_ent = spawn_door("test", "north", (1, 2))
    collider = esper.component_for_entity(door_ent, Collider)

    assert collider.radius == Config.DOOR_COLLIDER_RADIUS
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_doors.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'src.entities.doors'"

**Step 3: Add DOOR_COLLIDER_RADIUS to Config**

Modify `src/config.py`, add after ITEM_PICKUP_RADIUS:

```python
    # Door constants
    DOOR_COLLIDER_RADIUS: float = 1.0  # Door collision detection radius
```

**Step 4: Write minimal implementation**

Create `src/entities/doors.py`:

```python
"""Door entity creation functions."""
import esper
from src.components.core import Position, Sprite, Collider
from src.components.dungeon import Door
from src.config import Config


def spawn_door(world_name: str, direction: str, leads_to: tuple[int, int], locked: bool = True) -> int:
    """Create door entity at appropriate wall position.

    Args:
        world_name: World to spawn in
        direction: "north", "south", "east", "west"
        leads_to: Destination room coordinates (x, y)
        locked: Initial lock state (True = locked, False = unlocked)

    Returns:
        Door entity ID
    """
    esper.switch_world(world_name)

    # Determine position based on direction
    if direction == "north":
        x = Config.ROOM_WIDTH / 2
        y = 0
    elif direction == "south":
        x = Config.ROOM_WIDTH / 2
        y = Config.ROOM_HEIGHT - 1
    elif direction == "east":
        x = Config.ROOM_WIDTH - 1
        y = Config.ROOM_HEIGHT / 2
    elif direction == "west":
        x = 0
        y = Config.ROOM_HEIGHT / 2
    else:
        raise ValueError(f"Invalid direction: {direction}")

    # Create door entity
    door_ent = esper.create_entity()
    esper.add_component(door_ent, Position(x, y))
    esper.add_component(door_ent, Collider(Config.DOOR_COLLIDER_RADIUS))

    # Set sprite based on lock state
    if locked:
        esper.add_component(door_ent, Sprite("▮", "red"))
    else:
        esper.add_component(door_ent, Sprite("▯", "cyan"))

    esper.add_component(door_ent, Door(direction, leads_to, locked))

    return door_ent
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_doors.py -v`

Expected: PASS (9 tests)

**Step 6: Commit**

```bash
git add src/entities/doors.py tests/test_doors.py src/config.py
git commit -m "feat: add door entity creation with spawn_door function"
```

---

## Task 2: RoomManager Door Spawning

**Files:**
- Modify: `src/systems/room_manager.py`
- Modify: `tests/test_room_manager.py`

**Step 1: Write the failing test**

Add to `tests/test_room_manager.py`:

```python
from src.components.dungeon import Door
from src.components.core import Position


def test_spawn_room_contents_spawns_doors():
    """Test spawn_room_contents spawns door for each connection."""
    esper.clear_database()

    # Create dungeon with room that has 2 doors
    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"north": (0, -1), "east": (1, 0)}
    )
    dungeon.start_position = (0, 0)

    room_manager = RoomManager(dungeon)
    room_manager.spawn_room_contents()

    # Check that 2 doors were spawned
    doors = list(esper.get_components(Door))
    assert len(doors) == 2

    # Check door directions
    door_directions = {door.direction for _, (door,) in doors}
    assert door_directions == {"north", "east"}


def test_spawn_room_contents_doors_unlocked_in_start_room():
    """Test doors spawn unlocked in start room."""
    esper.clear_database()

    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"north": (0, -1)}
    )
    dungeon.start_position = (0, 0)

    room_manager = RoomManager(dungeon)
    room_manager.spawn_room_contents()

    door_ent, (door,) = list(esper.get_components(Door))[0]
    assert door.locked == False


def test_spawn_room_contents_doors_locked_in_uncleared_combat():
    """Test doors spawn locked in uncleared combat room."""
    esper.clear_database()

    dungeon = Dungeon()
    dungeon.rooms[(1, 0)] = DungeonRoom(
        position=(1, 0),
        room_type=RoomType.COMBAT,
        doors={"west": (0, 0)},
        cleared=False
    )
    dungeon.start_position = (1, 0)

    room_manager = RoomManager(dungeon)
    room_manager.spawn_room_contents()

    door_ent, (door,) = list(esper.get_components(Door))[0]
    assert door.locked == True


def test_spawn_room_contents_doors_unlocked_in_cleared_combat():
    """Test doors spawn unlocked in cleared combat room."""
    esper.clear_database()

    dungeon = Dungeon()
    dungeon.rooms[(1, 0)] = DungeonRoom(
        position=(1, 0),
        room_type=RoomType.COMBAT,
        doors={"west": (0, 0)},
        cleared=True
    )
    dungeon.start_position = (1, 0)

    room_manager = RoomManager(dungeon)
    room_manager.spawn_room_contents()

    door_ent, (door,) = list(esper.get_components(Door))[0]
    assert door.locked == False
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_room_manager.py::test_spawn_room_contents_spawns_doors -v`

Expected: FAIL with "AssertionError: assert 0 == 2" (no doors spawned)

**Step 3: Write minimal implementation**

Modify `src/systems/room_manager.py`, replace `spawn_room_contents()` method:

```python
    def spawn_room_contents(self) -> None:
        """Spawn entities for current room."""
        from src.entities.doors import spawn_door

        # Spawn doors for each connection
        for direction, leads_to in self.current_room.doors.items():
            # Determine if door should be locked
            locked = self._should_lock_doors()
            spawn_door("main", direction, leads_to, locked)

        # TODO: Spawn enemies, items, etc. (future tasks)

    def _should_lock_doors(self) -> bool:
        """Determine if doors should be locked in current room.

        Returns:
            True if doors should lock, False otherwise
        """
        # Lock doors in uncleared combat rooms
        if self.current_room.room_type == RoomType.COMBAT and not self.current_room.cleared:
            return True

        # Don't lock in peaceful rooms (start, treasure, shop)
        if self.current_room.room_type in [RoomType.START, RoomType.TREASURE, RoomType.SHOP]:
            return False

        # Don't lock if already cleared
        return False
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_room_manager.py::test_spawn_room_contents_spawns_doors -v`
Run: `uv run pytest tests/test_room_manager.py::test_spawn_room_contents_doors_unlocked_in_start_room -v`
Run: `uv run pytest tests/test_room_manager.py::test_spawn_room_contents_doors_locked_in_uncleared_combat -v`
Run: `uv run pytest tests/test_room_manager.py::test_spawn_room_contents_doors_unlocked_in_cleared_combat -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/systems/room_manager.py tests/test_room_manager.py
git commit -m "feat: implement door spawning in RoomManager"
```

---

## Task 3: RoomManager Door Despawning

**Files:**
- Modify: `src/systems/room_manager.py`
- Modify: `tests/test_room_manager.py`

**Step 1: Write the failing test**

Add to `tests/test_room_manager.py`:

```python
def test_despawn_current_room_entities_removes_doors():
    """Test despawn_current_room_entities removes all door entities."""
    esper.clear_database()

    from src.entities.doors import spawn_door

    # Spawn some doors
    spawn_door("main", "north", (0, -1))
    spawn_door("main", "south", (0, 1))

    assert len(list(esper.get_components(Door))) == 2

    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={}
    )
    dungeon.start_position = (0, 0)

    room_manager = RoomManager(dungeon)
    room_manager.despawn_current_room_entities()

    # All doors should be removed
    assert len(list(esper.get_components(Door))) == 0
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_room_manager.py::test_despawn_current_room_entities_removes_doors -v`

Expected: FAIL with "AssertionError: assert 2 == 0" (doors not removed)

**Step 3: Write minimal implementation**

Modify `src/systems/room_manager.py`, replace `despawn_current_room_entities()` method:

```python
    def despawn_current_room_entities(self) -> None:
        """Remove all entities from current room."""
        # Delete all door entities
        for door_ent, (door,) in esper.get_components(Door):
            esper.delete_entity(door_ent)

        # TODO: Despawn enemies, projectiles, items (future tasks)
        # Keep player entity
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_room_manager.py::test_despawn_current_room_entities_removes_doors -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/systems/room_manager.py tests/test_room_manager.py
git commit -m "feat: implement door despawning in RoomManager"
```

---

## Task 4: RoomManager Lock/Unlock Doors

**Files:**
- Modify: `src/systems/room_manager.py`
- Modify: `tests/test_room_manager.py`

**Step 1: Write the failing test**

Add to `tests/test_room_manager.py`:

```python
from src.components.core import Sprite


def test_lock_all_doors_locks_doors():
    """Test lock_all_doors locks all door entities."""
    esper.clear_database()

    from src.entities.doors import spawn_door

    # Spawn unlocked doors
    door1 = spawn_door("main", "north", (0, -1), locked=False)
    door2 = spawn_door("main", "south", (0, 1), locked=False)

    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={}
    )
    dungeon.start_position = (0, 0)

    room_manager = RoomManager(dungeon)
    room_manager.lock_all_doors()

    # Check doors are locked
    door1_comp = esper.component_for_entity(door1, Door)
    door2_comp = esper.component_for_entity(door2, Door)
    assert door1_comp.locked == True
    assert door2_comp.locked == True

    # Check sprites updated
    door1_sprite = esper.component_for_entity(door1, Sprite)
    door2_sprite = esper.component_for_entity(door2, Sprite)
    assert door1_sprite.char == "▮"
    assert door1_sprite.color == "red"
    assert door2_sprite.char == "▮"
    assert door2_sprite.color == "red"


def test_unlock_all_doors_unlocks_doors():
    """Test unlock_all_doors unlocks all door entities."""
    esper.clear_database()

    from src.entities.doors import spawn_door

    # Spawn locked doors
    door1 = spawn_door("main", "north", (0, -1), locked=True)
    door2 = spawn_door("main", "south", (0, 1), locked=True)

    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={}
    )
    dungeon.start_position = (0, 0)

    room_manager = RoomManager(dungeon)
    room_manager.unlock_all_doors()

    # Check doors are unlocked
    door1_comp = esper.component_for_entity(door1, Door)
    door2_comp = esper.component_for_entity(door2, Door)
    assert door1_comp.locked == False
    assert door2_comp.locked == False

    # Check sprites updated
    door1_sprite = esper.component_for_entity(door1, Sprite)
    door2_sprite = esper.component_for_entity(door2, Sprite)
    assert door1_sprite.char == "▯"
    assert door1_sprite.color == "cyan"
    assert door2_sprite.char == "▯"
    assert door2_sprite.color == "cyan"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_room_manager.py::test_lock_all_doors_locks_doors -v`

Expected: FAIL (doors not locked)

**Step 3: Write minimal implementation**

Modify `src/systems/room_manager.py`, replace `lock_all_doors()` and `unlock_all_doors()` methods:

```python
    def lock_all_doors(self) -> None:
        """Lock all doors in current room."""
        for door_ent, (door, sprite) in esper.get_components(Door, Sprite):
            door.locked = True
            sprite.char = "▮"
            sprite.color = "red"

    def unlock_all_doors(self) -> None:
        """Unlock all doors in current room."""
        for door_ent, (door, sprite) in esper.get_components(Door, Sprite):
            door.locked = False
            sprite.char = "▯"
            sprite.color = "cyan"
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_room_manager.py::test_lock_all_doors_locks_doors -v`
Run: `uv run pytest tests/test_room_manager.py::test_unlock_all_doors_unlocks_doors -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/systems/room_manager.py tests/test_room_manager.py
git commit -m "feat: implement door locking/unlocking in RoomManager"
```

---

## Task 5: CollisionSystem Player-Door Collision Detection

**Files:**
- Modify: `src/systems/collision.py`
- Modify: `tests/test_collision_system.py`

**Step 1: Write the failing test**

Add to `tests/test_collision_system.py`:

```python
from src.components.dungeon import Door
from src.game.dungeon import Dungeon, DungeonRoom, RoomType
from src.systems.room_manager import RoomManager
from src.entities.doors import spawn_door


def test_player_door_collision_with_unlocked_door_triggers_transition():
    """Test player colliding with unlocked door triggers room transition."""
    esper.clear_database()

    # Create dungeon with two connected rooms
    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"north": (0, -1)}
    )
    dungeon.rooms[(0, -1)] = DungeonRoom(
        position=(0, -1),
        room_type=RoomType.COMBAT,
        doors={"south": (0, 0)}
    )
    dungeon.start_position = (0, 0)

    room_manager = RoomManager(dungeon)
    collision_system = CollisionSystem(room_manager=room_manager)

    # Create player at door position
    player = create_player("main", 30, 0)  # North door position

    # Create unlocked north door
    spawn_door("main", "north", (0, -1), locked=False)

    # Process collision
    collision_system.process()

    # Verify room transitioned
    assert room_manager.current_position == (0, -1)


def test_player_door_collision_with_locked_door_no_transition():
    """Test player colliding with locked door does not trigger transition."""
    esper.clear_database()

    # Create dungeon
    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.COMBAT,
        doors={"north": (0, -1)},
        cleared=False
    )
    dungeon.rooms[(0, -1)] = DungeonRoom(
        position=(0, -1),
        room_type=RoomType.COMBAT,
        doors={"south": (0, 0)}
    )
    dungeon.start_position = (0, 0)

    room_manager = RoomManager(dungeon)
    collision_system = CollisionSystem(room_manager=room_manager)

    # Create player at door position
    player = create_player("main", 30, 0)

    # Create locked north door
    spawn_door("main", "north", (0, -1), locked=True)

    # Process collision
    collision_system.process()

    # Verify no transition (still in original room)
    assert room_manager.current_position == (0, 0)


def test_collision_system_without_room_manager_skips_door_collision():
    """Test CollisionSystem without RoomManager doesn't crash on door collision."""
    esper.clear_database()

    collision_system = CollisionSystem()  # No room_manager

    # Create player and door
    player = create_player("main", 30, 0)
    spawn_door("main", "north", (0, -1), locked=False)

    # Should not crash
    collision_system.process()
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_collision_system.py::test_player_door_collision_with_unlocked_door_triggers_transition -v`

Expected: FAIL with "TypeError: __init__() got an unexpected keyword argument 'room_manager'"

**Step 3: Write minimal implementation**

Modify `src/systems/collision.py`:

Add to `__init__` method:

```python
class CollisionSystem(esper.Processor):
    """Handles collision detection and damage."""

    def __init__(self, room_manager=None):
        """Initialize collision system.

        Args:
            room_manager: RoomManager instance for room transitions (optional)
        """
        super().__init__()
        self.room_manager = room_manager
```

Add to end of `process()` method, after all existing collision checks:

```python
        # Player-door collision for room transitions
        if self.room_manager:
            from src.components.dungeon import Door

            for player_ent, (player, player_pos, player_collider) in esper.get_components(Player, Position, Collider):
                for door_ent, (door, door_pos, door_collider) in esper.get_components(Door, Position, Collider):
                    # Only unlocked doors allow transitions
                    if not door.locked and self._check_overlap(player_pos, player_collider, door_pos, door_collider):
                        # Trigger room transition via RoomManager
                        self.room_manager.transition_to_room(door.leads_to, door.direction)

                        # Reposition player at entrance of new room
                        self._reposition_player_after_transition(player_ent, player_pos, door.direction)

                        # Only transition through one door per frame
                        break
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_collision_system.py::test_player_door_collision_with_unlocked_door_triggers_transition -v`
Run: `uv run pytest tests/test_collision_system.py::test_player_door_collision_with_locked_door_no_transition -v`
Run: `uv run pytest tests/test_collision_system.py::test_collision_system_without_room_manager_skips_door_collision -v`

Expected: FAIL with "AttributeError: 'CollisionSystem' object has no attribute '_reposition_player_after_transition'"

Note: We'll implement _reposition_player_after_transition in next task

**Step 5: Commit**

Commit after Task 6 when both collision detection and repositioning are complete.

---

## Task 6: CollisionSystem Player Repositioning

**Files:**
- Modify: `src/systems/collision.py`
- Modify: `tests/test_collision_system.py`

**Step 1: Write the failing test**

Add to `tests/test_collision_system.py`:

```python
def test_reposition_player_after_north_transition():
    """Test player repositioned at south when entering from north."""
    esper.clear_database()

    collision_system = CollisionSystem()
    player = create_player("main", 30, 0)
    player_pos = esper.component_for_entity(player, Position)

    collision_system._reposition_player_after_transition(player, player_pos, "north")

    assert player_pos.x == Config.ROOM_WIDTH / 2
    assert player_pos.y == Config.ROOM_HEIGHT - 2


def test_reposition_player_after_south_transition():
    """Test player repositioned at north when entering from south."""
    esper.clear_database()

    collision_system = CollisionSystem()
    player = create_player("main", 30, 19)
    player_pos = esper.component_for_entity(player, Position)

    collision_system._reposition_player_after_transition(player, player_pos, "south")

    assert player_pos.x == Config.ROOM_WIDTH / 2
    assert player_pos.y == 1


def test_reposition_player_after_east_transition():
    """Test player repositioned at west when entering from east."""
    esper.clear_database()

    collision_system = CollisionSystem()
    player = create_player("main", 59, 10)
    player_pos = esper.component_for_entity(player, Position)

    collision_system._reposition_player_after_transition(player, player_pos, "east")

    assert player_pos.x == 1
    assert player_pos.y == Config.ROOM_HEIGHT / 2


def test_reposition_player_after_west_transition():
    """Test player repositioned at east when entering from west."""
    esper.clear_database()

    collision_system = CollisionSystem()
    player = create_player("main", 0, 10)
    player_pos = esper.component_for_entity(player, Position)

    collision_system._reposition_player_after_transition(player, player_pos, "west")

    assert player_pos.x == Config.ROOM_WIDTH - 2
    assert player_pos.y == Config.ROOM_HEIGHT / 2
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_collision_system.py::test_reposition_player_after_north_transition -v`

Expected: FAIL with "AttributeError: 'CollisionSystem' object has no attribute '_reposition_player_after_transition'"

**Step 3: Write minimal implementation**

Add to `src/systems/collision.py` as a new method:

```python
    def _reposition_player_after_transition(self, player_ent: int, player_pos: Position, entry_direction: str) -> None:
        """Move player to entrance position in new room.

        When entering through a door, position player on opposite side of new room,
        slightly offset from the wall to avoid immediate re-collision.

        Args:
            player_ent: Player entity ID
            player_pos: Player's Position component
            entry_direction: Direction player came from
        """
        if entry_direction == "north":
            # Entered from north, spawn at south
            player_pos.y = Config.ROOM_HEIGHT - 2
            player_pos.x = Config.ROOM_WIDTH / 2
        elif entry_direction == "south":
            # Entered from south, spawn at north
            player_pos.y = 1
            player_pos.x = Config.ROOM_WIDTH / 2
        elif entry_direction == "east":
            # Entered from east, spawn at west
            player_pos.x = 1
            player_pos.y = Config.ROOM_HEIGHT / 2
        elif entry_direction == "west":
            # Entered from west, spawn at east
            player_pos.x = Config.ROOM_WIDTH - 2
            player_pos.y = Config.ROOM_HEIGHT / 2
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_collision_system.py::test_reposition_player_after_north_transition -v`
Run: `uv run pytest tests/test_collision_system.py::test_reposition_player_after_south_transition -v`
Run: `uv run pytest tests/test_collision_system.py::test_reposition_player_after_east_transition -v`
Run: `uv run pytest tests/test_collision_system.py::test_reposition_player_after_west_transition -v`

Expected: PASS (4 tests)

Also run Task 5 tests:

Run: `uv run pytest tests/test_collision_system.py::test_player_door_collision_with_unlocked_door_triggers_transition -v`
Run: `uv run pytest tests/test_collision_system.py::test_player_door_collision_with_locked_door_no_transition -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/systems/collision.py tests/test_collision_system.py
git commit -m "feat: add player-door collision detection and repositioning"
```

---

## Task 7: Integration Test - Full Room Transition

**Files:**
- Modify: `tests/test_integration.py`

**Step 1: Write the failing test**

Add to `tests/test_integration.py`:

```python
from src.game.dungeon import Dungeon, DungeonRoom, RoomType
from src.systems.room_manager import RoomManager
from src.entities.doors import spawn_door


def test_full_room_transition_through_door():
    """Test complete room transition flow through door."""
    esper.clear_database()

    # Create dungeon with two connected rooms
    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"north": (0, -1)}
    )
    dungeon.rooms[(0, -1)] = DungeonRoom(
        position=(0, -1),
        room_type=RoomType.COMBAT,
        doors={"south": (0, 0)},
        cleared=False
    )
    dungeon.start_position = (0, 0)

    # Initialize systems
    room_manager = RoomManager(dungeon)
    collision_system = CollisionSystem(room_manager=room_manager)

    # Spawn initial room doors
    room_manager.spawn_room_contents()

    # Create player near north door
    player = create_player("main", Config.ROOM_WIDTH / 2, 0.5)
    player_pos = esper.component_for_entity(player, Position)

    # Verify initial state
    assert room_manager.current_position == (0, 0)
    initial_doors = list(esper.get_components(Door))
    assert len(initial_doors) == 1  # One door in start room

    # Move player into door
    player_pos.y = 0

    # Process collision (should trigger transition)
    collision_system.process()

    # Verify transition occurred
    assert room_manager.current_position == (0, -1)
    assert room_manager.current_room.visited == True

    # Verify player repositioned
    assert player_pos.y == Config.ROOM_HEIGHT - 2
    assert player_pos.x == Config.ROOM_WIDTH / 2

    # Verify old doors despawned, new doors spawned
    new_doors = list(esper.get_components(Door))
    assert len(new_doors) == 1  # One door in new room

    # Verify new room door is locked (uncleared combat room)
    door_ent, (door,) = new_doors[0]
    assert door.direction == "south"
    assert door.locked == True


def test_combat_room_door_unlock_on_clear():
    """Test doors unlock when combat room is cleared."""
    esper.clear_database()

    from src.components.core import Health, Stats
    from src.entities.enemy import create_enemy

    # Create dungeon with combat room
    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.COMBAT,
        doors={"north": (0, -1)},
        cleared=False
    )
    dungeon.start_position = (0, 0)

    room_manager = RoomManager(dungeon)
    collision_system = CollisionSystem(room_manager=room_manager)

    # Spawn doors (should be locked)
    room_manager.spawn_room_contents()

    door_ent, (door,) = list(esper.get_components(Door))[0]
    assert door.locked == True

    # Create enemy
    enemy = create_enemy("main", "chaser", 10, 10)

    # Kill enemy by setting health to 0
    enemy_health = esper.component_for_entity(enemy, Health)
    enemy_health.current = 0

    # Process collision (should mark enemy as dead)
    collision_system.process()

    # Room should be cleared and doors unlocked
    assert room_manager.current_room.cleared == True
    assert door.locked == False
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_integration.py::test_full_room_transition_through_door -v`

Expected: PASS (should work with existing implementation)

Run: `uv run pytest tests/test_integration.py::test_combat_room_door_unlock_on_clear -v`

Expected: MAY FAIL depending on whether room clear detection exists

**Step 3: No implementation needed**

If tests pass, no changes needed. If they fail, this reveals integration issues to fix.

**Step 4: Run all tests**

Run: `uv run pytest -v`

Expected: ALL PASS (240+ tests)

**Step 5: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests for room transitions"
```

---

## Summary

**Tasks completed:**
1. Door entity creation with spawn_door()
2. RoomManager door spawning based on room connections
3. RoomManager door despawning
4. RoomManager door locking/unlocking
5. CollisionSystem player-door collision detection
6. CollisionSystem player repositioning after transition
7. Integration tests for full transition flow

**Files created:**
- src/entities/doors.py
- tests/test_doors.py

**Files modified:**
- src/config.py (added DOOR_COLLIDER_RADIUS)
- src/systems/room_manager.py (spawn/despawn/lock/unlock doors)
- src/systems/collision.py (player-door collision, repositioning)
- tests/test_room_manager.py (door management tests)
- tests/test_collision_system.py (door collision tests)
- tests/test_integration.py (full transition tests)

**Total commits:** 5-6 commits following TDD flow

**Test coverage:**
- 9 tests for door entity creation
- 4 tests for door spawning logic
- 1 test for door despawning
- 2 tests for door locking/unlocking
- 3 tests for player-door collision
- 4 tests for player repositioning
- 2 integration tests

**Total:** ~25 new tests
