# Door System Design

> **Date:** 2026-01-15
> **Status:** Approved
> **Tasks:** 17-18 (Door entities and collision)

## Overview

Implement a complete door system that allows players to transition between rooms in the dungeon. Doors spawn at room edges, lock/unlock based on room state, and trigger room transitions when the player collides with unlocked doors.

## Goals

- Create door entities with proper positioning at room walls
- Integrate door spawning/despawning with RoomManager
- Implement door locking/unlocking based on room state
- Add player-door collision detection for room transitions
- Reposition player correctly when entering new rooms

## Architecture

### Components (Already Exist)

The Door component already exists in `src/components/dungeon.py`:

```python
@dataclass
class Door:
    """Door entity component."""
    direction: str  # "north", "south", "east", "west"
    leads_to: tuple[int, int]
    locked: bool = True
```

### Door Entity Creation

**File:** `src/entities/doors.py` (new)

```python
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
```

**Door Positioning:**

Doors spawn at the center of their respective walls based on direction:
- **North door:** (ROOM_WIDTH / 2, 0) - top wall center
- **South door:** (ROOM_WIDTH / 2, ROOM_HEIGHT - 1) - bottom wall center
- **East door:** (ROOM_WIDTH - 1, ROOM_HEIGHT / 2) - right wall center
- **West door:** (0, ROOM_HEIGHT / 2) - left wall center

**Door Components:**

Each door entity has:
1. **Position:** Wall center coordinates
2. **Collider:** Radius 1.0 for collision detection
3. **Sprite:** Visual representation
   - Locked: `▮` (red)
   - Unlocked: `▯` (cyan)
4. **Door:** Direction, destination, lock state

### RoomManager Integration

**File:** `src/systems/room_manager.py` (modify)

#### Door Spawning

Implement `spawn_room_contents()`:

```python
def spawn_room_contents(self) -> None:
    """Spawn entities for current room."""
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

#### Door Despawning

Implement `despawn_current_room_entities()`:

```python
def despawn_current_room_entities(self) -> None:
    """Remove all entities from current room."""
    # Delete all door entities
    for door_ent, (door,) in esper.get_components(Door):
        esper.delete_entity(door_ent)

    # TODO: Despawn enemies, projectiles, items (future tasks)
    # Keep player entity
```

#### Lock/Unlock Implementation

Implement placeholder methods:

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

**Door State Transitions:**

1. **Entering uncleared combat room:** Doors spawn locked
2. **Room cleared (all enemies dead):** `on_room_cleared()` calls `unlock_all_doors()`
3. **Entering peaceful room:** Doors spawn unlocked
4. **Entering cleared room:** Doors spawn unlocked

### Collision Detection & Transitions

**File:** `src/systems/collision.py` (modify)

#### Player-Door Collision

Add to `CollisionSystem.process()`:

```python
def process(self):
    """Check all collisions and apply damage."""

    # ... existing collision checks (projectiles, enemies, items) ...

    # Player-door collision for room transitions
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

#### Player Repositioning

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

#### RoomManager Reference

CollisionSystem needs access to RoomManager:

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

When RoomManager is None, door collision is skipped (useful for tests without dungeon context).

## Data Flow

### Room Transition Sequence

1. **Player moves toward door**
2. **CollisionSystem detects player-door overlap**
3. **Check door.locked:**
   - If locked: No transition, player blocked
   - If unlocked: Continue
4. **CollisionSystem calls room_manager.transition_to_room()**
5. **RoomManager.transition_to_room():**
   - Despawn old room entities (doors, enemies)
   - Update current_position and current_room
   - Mark room as visited
   - Determine room state (combat/peaceful/cleared)
   - Spawn new room entities (doors with correct lock state)
   - Lock doors if entering uncleared combat room
6. **CollisionSystem repositions player** at opposite wall
7. **Player enters new room**

### Door Lock/Unlock Flow

**On room entry (spawn_room_contents):**
```
Is combat room AND not cleared?
  → Spawn doors locked
Otherwise:
  → Spawn doors unlocked
```

**On room clear (on_room_cleared):**
```
Last enemy dies
  → Mark room.cleared = True
  → Update room.state = CLEARED
  → Call unlock_all_doors()
  → All doors change to unlocked sprite (▯)
  → Spawn room-clear reward
```

## Configuration

Add door-specific constants to `src/config.py`:

```python
# Door constants
DOOR_COLLIDER_RADIUS: float = 1.0  # Door collision detection radius
```

(ROOM_WIDTH and ROOM_HEIGHT already exist)

## Testing Strategy

### Unit Tests

**Door Entity Creation** (`tests/test_doors.py`):
- Test spawn_door() creates entity with all components
- Test door positioning for all four directions
- Test locked/unlocked sprite differences
- Test Door component validation

**RoomManager Door Management** (`tests/test_room_manager.py`):
- Test spawn_room_contents() spawns doors for each connection
- Test despawn_current_room_entities() removes all doors
- Test lock_all_doors() locks all doors and updates sprites
- Test unlock_all_doors() unlocks all doors and updates sprites
- Test _should_lock_doors() logic for different room types

**CollisionSystem Door Transitions** (`tests/test_collision_system.py`):
- Test player-door collision with unlocked door triggers transition
- Test player-door collision with locked door does nothing
- Test _reposition_player_after_transition() for all directions
- Test CollisionSystem without RoomManager (graceful handling)

### Integration Tests

**Full Room Transition** (`tests/test_integration.py`):
- Create dungeon with connected rooms
- Spawn player and doors
- Move player through unlocked door
- Verify player enters new room
- Verify old doors despawned, new doors spawned
- Verify player position in new room

**Combat Room Lock/Unlock** (`tests/test_integration.py`):
- Enter uncleared combat room with enemy
- Verify doors spawn locked
- Kill enemy
- Verify doors unlock
- Verify player can exit through door

## Edge Cases

1. **Multiple doors collision:** Only transition through first door detected (break after transition)
2. **Player stuck in door:** Repositioning places player 1-2 units from wall, avoiding immediate re-collision
3. **CollisionSystem without RoomManager:** Check `if self.room_manager:` before door collision logic
4. **Transition to non-existent room:** RoomManager validates `leads_to` exists in dungeon.rooms (future error handling)
5. **Cleared room re-entry:** Doors spawn unlocked, no enemies spawn

## Files Modified/Created

### New Files
- `src/entities/doors.py` - Door entity creation

### Modified Files
- `src/systems/room_manager.py` - Implement door spawning/despawning, lock/unlock
- `src/systems/collision.py` - Add player-door collision, transitions, player repositioning
- `src/config.py` - Add DOOR_COLLIDER_RADIUS constant
- `tests/test_doors.py` - Door entity tests (new)
- `tests/test_room_manager.py` - Door management tests (extend existing)
- `tests/test_collision_system.py` - Door collision tests (extend existing)

## Success Criteria

- ✅ Door entities spawn at correct wall positions
- ✅ Doors have appropriate sprites (▮ locked, ▯ unlocked)
- ✅ RoomManager spawns doors for all room connections
- ✅ RoomManager despawns doors when leaving room
- ✅ Doors lock in uncleared combat rooms
- ✅ Doors unlock when room cleared
- ✅ Player can transition through unlocked doors
- ✅ Player cannot transition through locked doors
- ✅ Player repositions correctly in new room
- ✅ All tests pass with comprehensive coverage

## Future Enhancements (Not in Scope)

- Door opening/closing animations
- Sound effects for door transitions
- Boss door special sprites (different from normal doors)
- Secret room doors (hidden until revealed)
- Locked doors requiring keys
- Door transition screen fade effects
