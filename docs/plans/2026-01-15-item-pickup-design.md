# Item Pickup & Stat Modification System Design

**Date:** 2026-01-15
**Status:** Design Approved
**Goal:** Implement item pickups that permanently modify player stats and provide special combat effects

## Overview

Add item pickup system with permanent stat modifications and special effects. Items spawn both as pre-placed pickups in rooms and as random drops from defeated enemies. Picked up items immediately modify player stats using a hybrid system (additive for damage/fire_rate, multiplicative for speed/shot_speed) and grant special effects like piercing shots, homing bullets, and multi-shot.

## Architecture

### New Components

**CollectedItems**

Location: `src/components/game.py`

```python
class CollectedItems:
    """Tracks items collected by the player."""

    def __init__(self) -> None:
        self.items: List[Item] = []  # Full Item objects for reference

    def has_effect(self, effect_name: str) -> bool:
        """Check if player has a specific special effect."""
        return any(effect_name in item.special_effects for item in self.items)

    def __repr__(self) -> str:
        return f"CollectedItems(items={[item.name for item in self.items]})"
```

Stores complete Item objects so we can reference names, effects, and modifiers. The `has_effect()` helper makes special effect queries simple.

### Existing Components (No Changes)

**Item** (already exists in `src/components/game.py`)
- `name: str` - Item display name
- `stat_modifiers: Dict[str, float]` - Stat changes to apply
- `special_effects: List[str]` - Effect names (e.g., "piercing", "homing")

**Stats** (already exists in `src/components/combat.py`)
- `speed: float` - Movement speed
- `damage: float` - Projectile damage
- `fire_rate: float` - Time between shots
- `shot_speed: float` - Projectile velocity

### New Systems

**ItemPickupSystem**

**Purpose:** Detect Player + Item collisions, apply stat modifications, track collected items, show notifications

**Location:** `src/systems/item_pickup.py`

```python
from typing import Optional
import esper
from src.components.core import Position
from src.components.combat import Stats, Collider
from src.components.game import Player, Item, CollectedItems


class ItemPickupSystem(esper.Processor):
    """Handles item pickup detection and stat application."""

    def __init__(self):
        super().__init__()
        self.notification: Optional[str] = None
        self.notification_timer: float = 0.0
        self.dt: float = 0.0

    def process(self):
        """Check for item pickups and apply effects."""
        # Decrement notification timer
        if self.notification_timer > 0:
            self.notification_timer -= self.dt
            if self.notification_timer <= 0:
                self.notification = None

        # Check for Player + Item collisions
        for player_ent, (player, player_pos, player_col) in esper.get_components(Player, Position, Collider):
            for item_ent, (item, item_pos, item_col) in esper.get_components(Item, Position, Collider):
                if self._check_overlap(player_pos, player_col, item_pos, item_col):
                    self._pickup_item(player_ent, item_ent, item)

    def _check_overlap(self, pos1: Position, col1: Collider, pos2: Position, col2: Collider) -> bool:
        """Check if two circles overlap."""
        import math
        dx = pos2.x - pos1.x
        dy = pos2.y - pos1.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (col1.radius + col2.radius)

    def _pickup_item(self, player_ent: int, item_ent: int, item: Item):
        """Apply item effects and remove item entity."""
        # Apply stat modifiers
        stats = esper.component_for_entity(player_ent, Stats)
        for stat_name, value in item.stat_modifiers.items():
            if stat_name in ["damage", "fire_rate"]:
                # Additive stats
                setattr(stats, stat_name, getattr(stats, stat_name) + value)
            elif stat_name in ["speed", "shot_speed"]:
                # Multiplicative stats
                setattr(stats, stat_name, getattr(stats, stat_name) * value)

        # Add to collected items
        if not esper.has_component(player_ent, CollectedItems):
            esper.add_component(player_ent, CollectedItems())
        collected = esper.component_for_entity(player_ent, CollectedItems)
        collected.items.append(item)

        # Show notification
        self.notification = f"Picked up: {item.name}"
        self.notification_timer = 2.0  # Show for 2 seconds

        # Remove item entity
        esper.delete_entity(item_ent)
```

**HomingSystem**

**Purpose:** Apply homing behavior to projectiles when player has homing effect

**Location:** `src/systems/homing.py`

```python
import esper
import math
from src.components.core import Position, Velocity
from src.components.combat import Projectile
from src.components.game import Player, Enemy, CollectedItems


class HomingSystem(esper.Processor):
    """Applies homing behavior to projectiles."""

    def __init__(self):
        super().__init__()
        self.dt: float = 0.0

    def process(self):
        """Update homing projectiles to turn toward nearest enemy."""
        from src.config import Config

        # Check if player has homing effect
        player_has_homing = False
        for player_ent, (player, collected) in esper.get_components(Player, CollectedItems):
            if collected.has_effect("homing"):
                player_has_homing = True
                break

        if not player_has_homing:
            return

        # Apply homing to player's projectiles
        for proj_ent, (proj, proj_pos, proj_vel) in esper.get_components(Projectile, Position, Velocity):
            # Only home player projectiles
            if not esper.entity_exists(proj.owner):
                continue
            if not esper.has_component(proj.owner, Player):
                continue

            # Find nearest enemy
            nearest_enemy = None
            nearest_distance = float('inf')

            for enemy_ent, (enemy, enemy_pos) in esper.get_components(Enemy, Position):
                dx = enemy_pos.x - proj_pos.x
                dy = enemy_pos.y - proj_pos.y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_enemy = enemy_pos

            if nearest_enemy is None:
                continue

            # Gradually rotate velocity toward target
            target_dx = nearest_enemy.x - proj_pos.x
            target_dy = nearest_enemy.y - proj_pos.y
            target_angle = math.atan2(target_dy, target_dx)

            current_angle = math.atan2(proj_vel.dy, proj_vel.dx)
            current_speed = math.sqrt(proj_vel.dx * proj_vel.dx + proj_vel.dy * proj_vel.dy)

            # Rotate toward target by turn rate
            turn_rate = Config.HOMING_TURN_RATE  # degrees per second
            max_turn = math.radians(turn_rate) * self.dt

            angle_diff = target_angle - current_angle
            # Normalize to [-pi, pi]
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi

            # Clamp turn amount
            turn_amount = max(-max_turn, min(max_turn, angle_diff))
            new_angle = current_angle + turn_amount

            # Apply new velocity
            proj_vel.dx = math.cos(new_angle) * current_speed
            proj_vel.dy = math.sin(new_angle) * current_speed
```

**System Execution Order (updated):**
1. InputSystem (priority 0)
2. AISystem (priority 1)
3. EnemyShootingSystem (priority 2)
4. ShootingSystem (priority 3)
5. MovementSystem (priority 4)
6. **HomingSystem (priority 4.5)** ← NEW (after shooting, before movement completes)
7. CollisionSystem (priority 5)
8. InvincibilitySystem (priority 6)
9. **ItemPickupSystem (priority 6.5)** ← NEW (after combat, before rendering)
10. RenderSystem (priority 7)

### Modified Systems

**ShootingSystem** (existing in `src/systems/shooting.py`)

Add multi-shot effect checking:

```python
def _create_projectile(self, player_ent: int, stats: Stats):
    """Create projectile(s) from player."""
    # ... existing code to get position, calculate direction ...

    # Check for multi-shot effect
    has_multi_shot = False
    if esper.has_component(player_ent, CollectedItems):
        collected = esper.component_for_entity(player_ent, CollectedItems)
        has_multi_shot = collected.has_effect("multi_shot")

    # Calculate base angle
    angle = math.atan2(direction_y, direction_x)

    if has_multi_shot:
        # Fire 3 projectiles: center, left, right
        self._spawn_projectile(player_ent, pos, angle - math.radians(15), stats)
        self._spawn_projectile(player_ent, pos, angle, stats)
        self._spawn_projectile(player_ent, pos, angle + math.radians(15), stats)
    else:
        # Fire single projectile
        self._spawn_projectile(player_ent, pos, angle, stats)
```

**CollisionSystem** (existing in `src/systems/collision.py`)

Add piercing effect and enemy drops:

```python
def _projectile_hit_enemy(self, projectile: int, enemy: int):
    """Handle projectile hitting enemy."""
    from src.config import Config
    import random

    proj = esper.component_for_entity(projectile, Projectile)
    health = esper.component_for_entity(enemy, Health)

    # Apply damage
    health.current -= proj.damage

    # Check for piercing effect
    has_piercing = False
    if esper.entity_exists(proj.owner) and esper.has_component(proj.owner, Player):
        if esper.has_component(proj.owner, CollectedItems):
            collected = esper.component_for_entity(proj.owner, CollectedItems)
            has_piercing = collected.has_effect("piercing")

    # Remove projectile (unless piercing)
    if not has_piercing:
        esper.delete_entity(projectile)

    # Check for enemy death
    if health.current <= 0:
        # Roll for item drop
        if random.random() < Config.ITEM_DROP_CHANCE:
            pos = esper.component_for_entity(enemy, Position)
            from src.entities.items import spawn_random_item
            spawn_random_item(esper.current_world, pos.x, pos.y)

        esper.delete_entity(enemy)
```

**RenderSystem** (existing in `src/systems/render.py`)

Add notification rendering:

```python
def render(self):
    """Render all entities and UI elements."""
    # ... existing rendering code ...

    # Render item pickup notification
    if hasattr(self, 'item_pickup_system') and self.item_pickup_system.notification:
        # Render at top center of screen
        notification = self.item_pickup_system.notification
        x = (Config.ROOM_WIDTH - len(notification)) // 2
        self.console.print(x, 0, notification, fg="yellow")
```

## Stat Modification Rules

### Hybrid System

**Additive Stats** (flat additions):
- `damage`: Each item adds to total (e.g., +0.5, +1.0)
- `fire_rate`: Each item adds to total (e.g., -0.1 for faster firing)

**Multiplicative Stats** (percentage multipliers):
- `speed`: Each item multiplies current value (e.g., 1.2 = 20% increase)
- `shot_speed`: Each item multiplies current value (e.g., 1.5 = 50% increase)

**Example:**
```python
# Starting stats
speed = 5.0
damage = 1.0

# Pick up item 1: {"speed": 1.2, "damage": 0.5}
speed = 5.0 * 1.2 = 6.0
damage = 1.0 + 0.5 = 1.5

# Pick up item 2: {"speed": 1.3, "damage": 1.0}
speed = 6.0 * 1.3 = 7.8
damage = 1.5 + 1.0 = 2.5
```

**Rationale:**
- Additive: Damage and fire rate scale linearly, preventing exponential power creep
- Multiplicative: Speed scales proportionally, preventing becoming impossibly fast or too slow

## Special Effects

### Three Effects for Phase 1

**1. Piercing Shots** (`"piercing"`)

Projectiles pass through enemies without being destroyed.

**Implementation:**
- In CollisionSystem._projectile_hit_enemy(), check for piercing before deleting projectile
- Damage is still applied to each enemy hit
- Projectile continues until it hits a wall or leaves the room

**Balance:** Strong against groups, allows hitting multiple enemies per shot

**2. Homing Bullets** (`"homing"`)

Projectiles gradually turn toward the nearest enemy.

**Implementation:**
- HomingSystem (priority 4.5) runs after shooting
- Finds nearest enemy to each projectile
- Rotates velocity vector toward target by HOMING_TURN_RATE degrees/second
- Subtle turning (not instant lock-on) creates skill expression

**Balance:** Helps with accuracy, especially effective against mobile enemies

**3. Multi-shot** (`"multi_shot"`)

Fire 3 projectiles in a spread pattern instead of 1.

**Implementation:**
- ShootingSystem checks for multi_shot effect when firing
- Creates 3 projectiles: center (0°), left (-15°), right (+15°)
- Each projectile has full damage (not split)
- Slightly reduced fire rate (trade-off: more projectiles, slower firing)

**Balance:** High area coverage, excellent for crowds, weaker against single targets at range

### Effect Query Pattern

Any system can check for special effects:

```python
if esper.has_component(player_ent, CollectedItems):
    collected = esper.component_for_entity(player_ent, CollectedItems)

    if collected.has_effect("piercing"):
        # Apply piercing behavior

    if collected.has_effect("homing"):
        # Apply homing behavior

    if collected.has_effect("multi_shot"):
        # Apply multi-shot behavior
```

## Item Spawning

### Two Spawn Methods

**A. Pre-placed Items (Room Generation)**

Rooms have designated item spawn points.

**Room Data Structure:**
```python
class Room:
    def __init__(self, ...):
        # ... existing fields ...
        self.item_spawns: List[Tuple[str, float, float]] = []  # (item_name, x, y)
```

**Spawn Logic:**
```python
# When room is created:
for item_name, x, y in room.item_spawns:
    from src.entities.items import create_item
    create_item(world, item_name, x, y)
```

**B. Enemy Drops (Random on Death)**

Enemies have a chance to drop items when killed.

**Config Constant:**
```python
ITEM_DROP_CHANCE = 0.15  # 15% chance per enemy
```

**Drop Logic** (in CollisionSystem._projectile_hit_enemy()):
```python
if health.current <= 0:
    if random.random() < Config.ITEM_DROP_CHANCE:
        pos = esper.component_for_entity(enemy, Position)
        spawn_random_item(world, pos.x, pos.y)
    esper.delete_entity(enemy)
```

## Item Database

**Location:** `src/data/items.py`

```python
ITEM_DEFINITIONS = {
    "magic_mushroom": {
        "sprite": "M",
        "color": "red",
        "stat_modifiers": {
            "damage": 1.0,      # +1.0 damage
            "speed": 1.2        # 20% speed increase
        },
        "special_effects": []
    },
    "triple_shot": {
        "sprite": "3",
        "color": "yellow",
        "stat_modifiers": {
            "fire_rate": 0.1    # Slightly slower fire rate
        },
        "special_effects": ["multi_shot"]
    },
    "piercing_tears": {
        "sprite": "P",
        "color": "cyan",
        "stat_modifiers": {
            "damage": 0.5       # +0.5 damage
        },
        "special_effects": ["piercing"]
    },
    "homing_shots": {
        "sprite": "H",
        "color": "magenta",
        "stat_modifiers": {},
        "special_effects": ["homing"]
    },
    "speed_boost": {
        "sprite": "S",
        "color": "green",
        "stat_modifiers": {
            "speed": 1.3        # 30% speed increase
        },
        "special_effects": []
    },
    "damage_up": {
        "sprite": "D",
        "color": "red",
        "stat_modifiers": {
            "damage": 1.5       # +1.5 damage
        },
        "special_effects": []
    }
}
```

**Item Creation Function:**

Location: `src/entities/items.py`

```python
import esper
import random
from src.components.core import Position
from src.components.rendering import Sprite
from src.components.combat import Collider
from src.components.game import Item
from src.data.items import ITEM_DEFINITIONS


def create_item(world: str, item_name: str, x: float, y: float) -> int:
    """Create an item entity at the specified position."""
    if item_name not in ITEM_DEFINITIONS:
        raise ValueError(f"Unknown item: {item_name}")

    item_data = ITEM_DEFINITIONS[item_name]

    esper.switch_world(world)
    entity = esper.create_entity()

    esper.add_component(entity, Position(x, y))
    esper.add_component(entity, Sprite(item_data["sprite"], item_data["color"]))
    esper.add_component(entity, Collider(0.4))  # Pickup radius
    esper.add_component(entity, Item(
        name=item_name,
        stat_modifiers=item_data["stat_modifiers"].copy(),
        special_effects=item_data["special_effects"].copy()
    ))

    return entity


def spawn_random_item(world: str, x: float, y: float) -> int:
    """Spawn a random item from the item pool."""
    item_name = random.choice(list(ITEM_DEFINITIONS.keys()))
    return create_item(world, item_name, x, y)
```

## Pickup Detection & Notifications

### Collision Detection

ItemPickupSystem uses the same circle collision logic as CollisionSystem:

```python
def _check_overlap(self, pos1: Position, col1: Collider, pos2: Position, col2: Collider) -> bool:
    """Check if two circles overlap."""
    import math
    dx = pos2.x - pos1.x
    dy = pos2.y - pos1.y
    distance = math.sqrt(dx * dx + dy * dy)
    return distance < (col1.radius + col2.radius)
```

**Pickup Radius:** Item colliders have radius 0.4 (slightly larger than visual size for easier pickup)

### Notification System

**Display:**
- Text appears at top center of screen
- Yellow color for visibility
- Format: "Picked up: {item_name}"

**Duration:**
- 2 seconds display time
- Timer decrements each frame
- Clears when timer reaches 0

**Implementation:**
```python
# In ItemPickupSystem:
self.notification = f"Picked up: {item.name}"
self.notification_timer = 2.0

# In RenderSystem:
if item_pickup_system.notification:
    self.console.print(x, 0, item_pickup_system.notification, fg="yellow")
```

## Configuration

**New constants in `src/config.py`:**

```python
# Item system
ITEM_DROP_CHANCE = 0.15  # 15% chance for enemy to drop item
ITEM_PICKUP_RADIUS = 0.4  # Collision radius for item pickups

# Homing effect
HOMING_TURN_RATE = 120.0  # Degrees per second (2 degrees per frame at 60fps)

# Notification display
NOTIFICATION_DURATION = 2.0  # Seconds to display pickup notification
```

## Testing Strategy

### Unit Tests

**CollectedItems Component** (`tests/test_components.py`):
```python
def test_collected_items_tracks_items():
    """Test CollectedItems stores Item objects."""
    item1 = Item("mushroom", {"damage": 1.0}, [])
    item2 = Item("triple_shot", {}, ["multi_shot"])

    collected = CollectedItems()
    collected.items.append(item1)
    collected.items.append(item2)

    assert len(collected.items) == 2
    assert collected.items[0].name == "mushroom"

def test_collected_items_has_effect():
    """Test has_effect() correctly identifies special effects."""
    item1 = Item("piercing_tears", {}, ["piercing"])
    item2 = Item("homing_shots", {}, ["homing"])

    collected = CollectedItems()
    collected.items.append(item1)
    collected.items.append(item2)

    assert collected.has_effect("piercing") == True
    assert collected.has_effect("homing") == True
    assert collected.has_effect("multi_shot") == False
```

**ItemPickupSystem** (`tests/test_item_pickup_system.py`):
```python
def test_pickup_applies_additive_stats():
    """Test additive stat modifiers are added correctly."""
    # Player with 1.0 damage
    # Pick up item with +1.5 damage
    # Verify damage = 2.5

def test_pickup_applies_multiplicative_stats():
    """Test multiplicative stat modifiers are multiplied correctly."""
    # Player with 5.0 speed
    # Pick up item with 1.2 speed multiplier
    # Verify speed = 6.0

def test_pickup_adds_to_collected_items():
    """Test picked up items are tracked in CollectedItems."""
    # Pick up 2 items
    # Verify CollectedItems contains both

def test_pickup_shows_notification():
    """Test notification is set after pickup."""
    # Pick up item
    # Verify system.notification == "Picked up: {name}"
    # Verify system.notification_timer == 2.0

def test_notification_clears_after_timer():
    """Test notification disappears after timer expires."""
    # Set notification and timer
    # Advance time by 2.1 seconds
    # Verify notification is None

def test_pickup_removes_item_entity():
    """Test item entity is deleted after pickup."""
    # Create item entity
    # Pick up item
    # Verify entity no longer exists
```

**HomingSystem** (`tests/test_homing_system.py`):
```python
def test_homing_system_rotates_toward_target():
    """Test projectile velocity rotates toward nearest enemy."""
    # Player with homing effect
    # Fire projectile north
    # Enemy to the east
    # Process homing system
    # Verify projectile velocity rotated eastward

def test_homing_respects_turn_rate():
    """Test projectile doesn't instantly lock on."""
    # Projectile facing north, target 180° away (south)
    # Process one frame
    # Verify rotation is limited to HOMING_TURN_RATE * dt

def test_homing_only_affects_player_projectiles():
    """Test enemy projectiles are not affected by homing."""
    # Enemy projectile
    # Player has homing effect
    # Process homing system
    # Verify enemy projectile velocity unchanged
```

**Special Effects** (`tests/test_collision_system.py`, `tests/test_shooting_system.py`):
```python
def test_piercing_projectile_doesnt_get_destroyed():
    """Test piercing projectiles continue after hitting enemy."""
    # Player with piercing effect
    # Projectile hits enemy
    # Verify projectile still exists
    # Verify enemy takes damage

def test_multi_shot_fires_three_projectiles():
    """Test multi_shot creates 3 projectiles in spread pattern."""
    # Player with multi_shot effect
    # Fire weapon
    # Verify 3 projectiles created
    # Verify angles: center, -15°, +15°
```

### Integration Tests

**Full Pickup Flow** (`tests/test_integration.py`):
```python
def test_item_pickup_and_stat_modification():
    """Test complete pickup flow from collision to stat change."""
    # Create player with base stats
    # Create item with stat modifiers
    # Move player to overlap item
    # Process ItemPickupSystem
    # Verify stats changed
    # Verify item added to CollectedItems
    # Verify item entity removed
    # Verify notification displayed

def test_special_effect_changes_combat():
    """Test special effects actually work in combat."""
    # Player picks up piercing item
    # Fire at 2 enemies in a line
    # Verify both enemies take damage
    # Verify projectile passes through first enemy
```

### Manual Testing

1. Run game with `uv run python main.py`
2. Spawn test item with 'I' key (debug command)
3. Walk over item → Verify pickup notification appears
4. Check stats → Verify damage/speed modified correctly
5. Pick up piercing item → Fire at enemies → Verify penetration
6. Pick up homing item → Fire near enemies → Verify bullets curve
7. Pick up multi-shot → Fire → Verify 3 projectiles spawn
8. Kill enemies → Verify some drop items (15% rate)

## Implementation Notes

### System Registration

Add to `src/game/engine.py`:

```python
from src.systems.item_pickup import ItemPickupSystem
from src.systems.homing import HomingSystem

# In __init__:
self.homing_system = HomingSystem()
self.world.add_processor(self.homing_system, priority=4.5)

self.item_pickup_system = ItemPickupSystem()
self.world.add_processor(self.item_pickup_system, priority=6.5)

# In update():
self.homing_system.dt = dt
self.item_pickup_system.dt = dt

# Store reference for RenderSystem
self.render_system.item_pickup_system = self.item_pickup_system
```

### Player Initialization

Update `src/entities/player.py`:

```python
def create_player(world: str, x: float, y: float) -> int:
    # ... existing components ...
    esper.add_component(entity, CollectedItems())  # Start with empty collection
    return entity
```

### Item Variety

Start with 6 items in the database:
- magic_mushroom (damage + speed)
- triple_shot (multi_shot effect)
- piercing_tears (piercing effect)
- homing_shots (homing effect)
- speed_boost (speed only)
- damage_up (damage only)

More items can be added easily by extending ITEM_DEFINITIONS.

## Success Criteria

✓ Player can pick up items by walking over them
✓ Stat modifiers apply correctly (additive for damage/fire_rate, multiplicative for speed/shot_speed)
✓ CollectedItems component tracks all picked up items
✓ Notification displays for 2 seconds when item is picked up
✓ Piercing effect allows projectiles to pass through enemies
✓ Homing effect makes projectiles curve toward enemies
✓ Multi-shot effect fires 3 projectiles in spread pattern
✓ Items spawn in pre-placed room locations
✓ Enemies drop items 15% of the time when killed
✓ All unit tests pass
✓ Manual testing confirms pickup, stats, and special effects work

## Future Enhancements (Not in Scope)

- Item pedestals with visual glow effect
- Item description UI when hovering
- Item reroll mechanics
- Synergy effects between items
- Negative items (curses)
- Active items (usable with button press)
- Item unlock progression
- Item tier/rarity system
