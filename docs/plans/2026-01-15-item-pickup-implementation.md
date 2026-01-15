# Item Pickup & Stat Modification Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement item pickup system with permanent stat modifications and three special effects (piercing, homing, multi-shot)

**Architecture:** ECS-based system with ItemPickupSystem for collision detection and stat application, HomingSystem for bullet curving, and modified ShootingSystem/CollisionSystem for special effects. Items stored in ITEM_DEFINITIONS database, tracked per-player in CollectedItems component.

**Tech Stack:** Python 3.12, Esper ECS, pytest

---

## Task 1: CollectedItems Component

**Files:**
- Modify: `src/components/game.py:77` (add after Dead class)
- Test: `tests/test_components.py:288` (add after existing tests)

**Step 1: Write the failing test**

Add to `tests/test_components.py`:

```python
def test_collected_items_tracks_items():
    """Test CollectedItems stores Item objects."""
    from src.components.game import CollectedItems, Item

    item1 = Item("mushroom", {"damage": 1.0}, [])
    item2 = Item("triple_shot", {}, ["multi_shot"])

    collected = CollectedItems()
    collected.items.append(item1)
    collected.items.append(item2)

    assert len(collected.items) == 2
    assert collected.items[0].name == "mushroom"
    assert collected.items[1].name == "triple_shot"


def test_collected_items_has_effect():
    """Test has_effect() correctly identifies special effects."""
    from src.components.game import CollectedItems, Item

    item1 = Item("piercing_tears", {}, ["piercing"])
    item2 = Item("homing_shots", {}, ["homing"])

    collected = CollectedItems()
    collected.items.append(item1)
    collected.items.append(item2)

    assert collected.has_effect("piercing") is True
    assert collected.has_effect("homing") is True
    assert collected.has_effect("multi_shot") is False


def test_collected_items_has_effect_with_no_items():
    """Test has_effect() returns False when no items collected."""
    from src.components.game import CollectedItems

    collected = CollectedItems()
    assert collected.has_effect("piercing") is False
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_components.py::test_collected_items_tracks_items -v`

Expected: FAIL with "ImportError: cannot import name 'CollectedItems'"

**Step 3: Write minimal implementation**

Add to `src/components/game.py` after Dead class (line 77):

```python
class CollectedItems:
    """Tracks items collected by the player."""

    def __init__(self) -> None:
        self.items: List[Item] = []

    def has_effect(self, effect_name: str) -> bool:
        """Check if player has a specific special effect.

        Args:
            effect_name: Name of the effect to check for

        Returns:
            True if any collected item has this effect
        """
        return any(effect_name in item.special_effects for item in self.items)

    def __repr__(self) -> str:
        return f"CollectedItems(items={[item.name for item in self.items]})"
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_components.py::test_collected_items_tracks_items tests/test_components.py::test_collected_items_has_effect tests/test_components.py::test_collected_items_has_effect_with_no_items -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/components/game.py tests/test_components.py
git commit -m "feat: add CollectedItems component for tracking picked up items

- Stores list of Item objects
- has_effect() helper for special effect queries
- Tests verify item tracking and effect detection

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Item Database and Entity Factory

**Files:**
- Create: `src/data/__init__.py`
- Create: `src/data/items.py`
- Create: `src/entities/items.py`
- Create: `tests/test_items.py`

**Step 1: Write the failing test**

Create `tests/test_items.py`:

```python
"""Tests for item entities and database."""
import pytest
import esper
from src.components.core import Position
from src.components.combat import Collider
from src.components.game import Item


def test_item_database_has_items():
    """Test ITEM_DEFINITIONS contains expected items."""
    from src.data.items import ITEM_DEFINITIONS

    assert "magic_mushroom" in ITEM_DEFINITIONS
    assert "triple_shot" in ITEM_DEFINITIONS
    assert "piercing_tears" in ITEM_DEFINITIONS
    assert "homing_shots" in ITEM_DEFINITIONS
    assert "speed_boost" in ITEM_DEFINITIONS
    assert "damage_up" in ITEM_DEFINITIONS


def test_item_definition_structure():
    """Test item definitions have required fields."""
    from src.data.items import ITEM_DEFINITIONS

    item_data = ITEM_DEFINITIONS["magic_mushroom"]
    assert "sprite" in item_data
    assert "color" in item_data
    assert "stat_modifiers" in item_data
    assert "special_effects" in item_data


def test_create_item_entity():
    """Test create_item creates entity with correct components."""
    from src.entities.items import create_item

    world_name = "test_world"
    esper.switch_world(world_name)

    entity = create_item(world_name, "magic_mushroom", 10.0, 20.0)

    # Check entity exists
    assert esper.entity_exists(entity)

    # Check components
    assert esper.has_component(entity, Position)
    assert esper.has_component(entity, Item)
    assert esper.has_component(entity, Collider)

    # Check values
    pos = esper.component_for_entity(entity, Position)
    assert pos.x == 10.0
    assert pos.y == 20.0

    item = esper.component_for_entity(entity, Item)
    assert item.name == "magic_mushroom"
    assert "damage" in item.stat_modifiers
    assert "speed" in item.stat_modifiers


def test_create_item_invalid_name():
    """Test create_item raises error for unknown item."""
    from src.entities.items import create_item

    world_name = "test_world"
    esper.switch_world(world_name)

    with pytest.raises(ValueError, match="Unknown item"):
        create_item(world_name, "nonexistent_item", 0.0, 0.0)


def test_spawn_random_item():
    """Test spawn_random_item creates valid item."""
    from src.entities.items import spawn_random_item
    from src.data.items import ITEM_DEFINITIONS

    world_name = "test_world"
    esper.switch_world(world_name)

    entity = spawn_random_item(world_name, 15.0, 25.0)

    # Check entity exists and has Item component
    assert esper.entity_exists(entity)
    assert esper.has_component(entity, Item)

    # Check item name is valid
    item = esper.component_for_entity(entity, Item)
    assert item.name in ITEM_DEFINITIONS
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_items.py::test_item_database_has_items -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'src.data'"

**Step 3: Write minimal implementation**

Create `src/data/__init__.py`:
```python
"""Game data definitions."""
```

Create `src/data/items.py`:
```python
"""Item database definitions."""

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

Create `src/entities/items.py`:
```python
"""Item entity factory functions."""
import esper
import random
from src.components.core import Position, Sprite
from src.components.combat import Collider
from src.components.game import Item
from src.data.items import ITEM_DEFINITIONS


def create_item(world: str, item_name: str, x: float, y: float) -> int:
    """Create an item entity at the specified position.

    Args:
        world: World name to create entity in
        item_name: Name of item from ITEM_DEFINITIONS
        x: X position
        y: Y position

    Returns:
        Entity ID of created item

    Raises:
        ValueError: If item_name not in ITEM_DEFINITIONS
    """
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
    """Spawn a random item from the item pool.

    Args:
        world: World name to create entity in
        x: X position
        y: Y position

    Returns:
        Entity ID of created item
    """
    item_name = random.choice(list(ITEM_DEFINITIONS.keys()))
    return create_item(world, item_name, x, y)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_items.py -v`

Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add src/data/ src/entities/items.py tests/test_items.py
git commit -m "feat: add item database and entity factory

- ITEM_DEFINITIONS with 6 starter items
- create_item() factory for specific items
- spawn_random_item() for random drops
- Tests verify database structure and entity creation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Configuration Constants

**Files:**
- Modify: `src/config.py:76` (add after INVINCIBILITY_DURATION)
- Test: `tests/test_config.py:199` (add after existing tests)

**Step 1: Write the failing test**

Add to `tests/test_config.py`:

```python
def test_item_drop_chance_is_probability():
    """Test ITEM_DROP_CHANCE is between 0 and 1."""
    from src.config import Config

    assert hasattr(Config, 'ITEM_DROP_CHANCE')
    assert 0.0 <= Config.ITEM_DROP_CHANCE <= 1.0


def test_item_pickup_radius_is_positive():
    """Test ITEM_PICKUP_RADIUS is positive."""
    from src.config import Config

    assert hasattr(Config, 'ITEM_PICKUP_RADIUS')
    assert Config.ITEM_PICKUP_RADIUS > 0


def test_homing_turn_rate_is_positive():
    """Test HOMING_TURN_RATE is positive."""
    from src.config import Config

    assert hasattr(Config, 'HOMING_TURN_RATE')
    assert Config.HOMING_TURN_RATE > 0


def test_notification_duration_is_positive():
    """Test NOTIFICATION_DURATION is positive."""
    from src.config import Config

    assert hasattr(Config, 'NOTIFICATION_DURATION')
    assert Config.NOTIFICATION_DURATION > 0
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py::test_item_drop_chance_is_probability -v`

Expected: FAIL with "AttributeError: type object 'Config' has no attribute 'ITEM_DROP_CHANCE'"

**Step 3: Write minimal implementation**

Add to `src/config.py` after INVINCIBILITY_DURATION (around line 76):

```python
    # Item system
    ITEM_DROP_CHANCE = 0.15  # 15% chance for enemy to drop item
    ITEM_PICKUP_RADIUS = 0.4  # Collision radius for item pickups

    # Homing effect
    HOMING_TURN_RATE = 120.0  # Degrees per second (2 degrees per frame at 60fps)

    # Notification display
    NOTIFICATION_DURATION = 2.0  # Seconds to display pickup notification
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_config.py::test_item_drop_chance_is_probability tests/test_config.py::test_item_pickup_radius_is_positive tests/test_config.py::test_homing_turn_rate_is_positive tests/test_config.py::test_notification_duration_is_positive -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add item system configuration constants

- ITEM_DROP_CHANCE for enemy drops
- ITEM_PICKUP_RADIUS for collision detection
- HOMING_TURN_RATE for bullet curving speed
- NOTIFICATION_DURATION for pickup messages
- Tests verify all constants are valid

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: ItemPickupSystem - Collision Detection

**Files:**
- Create: `src/systems/item_pickup.py`
- Create: `tests/test_item_pickup_system.py`

**Step 1: Write the failing test**

Create `tests/test_item_pickup_system.py`:

```python
"""Tests for ItemPickupSystem."""
import esper
from src.systems.item_pickup import ItemPickupSystem
from src.components.core import Position
from src.components.combat import Stats, Collider
from src.components.game import Player, Item, CollectedItems


def test_pickup_system_detects_overlap():
    """Test ItemPickupSystem detects player touching item."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    esper.add_component(player, Stats(5.0, 1.0, 0.3, 10.0))

    # Create item at same position
    item_entity = esper.create_entity()
    item_component = Item("test_item", {"damage": 1.0}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(10.0, 10.0))
    esper.add_component(item_entity, Collider(0.4))

    # Process pickup system
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Item should be removed
    assert not esper.entity_exists(item_entity)


def test_pickup_system_ignores_distant_items():
    """Test ItemPickupSystem doesn't pick up items far away."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    esper.add_component(player, Stats(5.0, 1.0, 0.3, 10.0))

    # Create item far away
    item_entity = esper.create_entity()
    item_component = Item("test_item", {"damage": 1.0}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(50.0, 50.0))
    esper.add_component(item_entity, Collider(0.4))

    # Process pickup system
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Item should still exist
    assert esper.entity_exists(item_entity)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_item_pickup_system.py::test_pickup_system_detects_overlap -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'src.systems.item_pickup'"

**Step 3: Write minimal implementation**

Create `src/systems/item_pickup.py`:

```python
"""Item pickup and stat modification system."""
from typing import Optional
import esper
import math
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
        """Check if two circles overlap.

        Args:
            pos1: First position
            col1: First collider
            pos2: Second position
            col2: Second collider

        Returns:
            True if circles overlap
        """
        dx = pos2.x - pos1.x
        dy = pos2.y - pos1.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (col1.radius + col2.radius)

    def _pickup_item(self, player_ent: int, item_ent: int, item: Item):
        """Apply item effects and remove item entity.

        Args:
            player_ent: Player entity ID
            item_ent: Item entity ID
            item: Item component
        """
        # Remove item entity (stat application in next task)
        esper.delete_entity(item_ent)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_item_pickup_system.py::test_pickup_system_detects_overlap tests/test_item_pickup_system.py::test_pickup_system_ignores_distant_items -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/systems/item_pickup.py tests/test_item_pickup_system.py
git commit -m "feat: add ItemPickupSystem collision detection

- Detects Player + Item overlaps using circle collision
- Removes item entity on pickup
- Tests verify detection and distance checking
- Stat application to be added in next step

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: ItemPickupSystem - Stat Application

**Files:**
- Modify: `src/systems/item_pickup.py:49` (_pickup_item method)
- Test: `tests/test_item_pickup_system.py:51` (add after existing tests)

**Step 1: Write the failing test**

Add to `tests/test_item_pickup_system.py`:

```python
def test_pickup_applies_additive_stats():
    """Test additive stat modifiers are added correctly."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with 1.0 damage
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    stats = Stats(5.0, 1.0, 0.3, 10.0)
    esper.add_component(player, stats)

    # Create item with +1.5 damage
    item_entity = esper.create_entity()
    item_component = Item("damage_up", {"damage": 1.5}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(10.0, 10.0))
    esper.add_component(item_entity, Collider(0.4))

    # Process pickup
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Verify damage increased additively
    assert stats.damage == 2.5


def test_pickup_applies_multiplicative_stats():
    """Test multiplicative stat modifiers are multiplied correctly."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with 5.0 speed
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    stats = Stats(5.0, 1.0, 0.3, 10.0)
    esper.add_component(player, stats)

    # Create item with 1.2 speed multiplier
    item_entity = esper.create_entity()
    item_component = Item("speed_boost", {"speed": 1.2}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(10.0, 10.0))
    esper.add_component(item_entity, Collider(0.4))

    # Process pickup
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Verify speed increased multiplicatively
    assert stats.speed == 6.0


def test_pickup_applies_multiple_stat_modifiers():
    """Test item can modify multiple stats at once."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    stats = Stats(5.0, 1.0, 0.3, 10.0)
    esper.add_component(player, stats)

    # Create item with damage + speed
    item_entity = esper.create_entity()
    item_component = Item("magic_mushroom", {"damage": 1.0, "speed": 1.2}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(10.0, 10.0))
    esper.add_component(item_entity, Collider(0.4))

    # Process pickup
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Verify both stats modified
    assert stats.damage == 2.0  # 1.0 + 1.0 (additive)
    assert stats.speed == 6.0   # 5.0 * 1.2 (multiplicative)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_item_pickup_system.py::test_pickup_applies_additive_stats -v`

Expected: FAIL with "assert 1.0 == 2.5" (stat not modified)

**Step 3: Write minimal implementation**

Modify `_pickup_item` method in `src/systems/item_pickup.py`:

```python
    def _pickup_item(self, player_ent: int, item_ent: int, item: Item):
        """Apply item effects and remove item entity.

        Args:
            player_ent: Player entity ID
            item_ent: Item entity ID
            item: Item component
        """
        # Apply stat modifiers
        stats = esper.component_for_entity(player_ent, Stats)
        for stat_name, value in item.stat_modifiers.items():
            if stat_name in ["damage", "fire_rate"]:
                # Additive stats
                setattr(stats, stat_name, getattr(stats, stat_name) + value)
            elif stat_name in ["speed", "shot_speed"]:
                # Multiplicative stats
                setattr(stats, stat_name, getattr(stats, stat_name) * value)

        # Remove item entity
        esper.delete_entity(item_ent)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_item_pickup_system.py::test_pickup_applies_additive_stats tests/test_item_pickup_system.py::test_pickup_applies_multiplicative_stats tests/test_item_pickup_system.py::test_pickup_applies_multiple_stat_modifiers -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/systems/item_pickup.py tests/test_item_pickup_system.py
git commit -m "feat: add stat modification to ItemPickupSystem

- Apply additive modifiers for damage and fire_rate
- Apply multiplicative modifiers for speed and shot_speed
- Supports multiple stat modifiers per item
- Tests verify hybrid stat system works correctly

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: ItemPickupSystem - CollectedItems Tracking

**Files:**
- Modify: `src/systems/item_pickup.py:55` (after stat application in _pickup_item)
- Test: `tests/test_item_pickup_system.py:120` (add after existing tests)

**Step 1: Write the failing test**

Add to `tests/test_item_pickup_system.py`:

```python
def test_pickup_adds_to_collected_items():
    """Test picked up items are tracked in CollectedItems."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    esper.add_component(player, Stats(5.0, 1.0, 0.3, 10.0))

    # Create first item
    item1 = esper.create_entity()
    item1_component = Item("mushroom", {"damage": 1.0}, [])
    esper.add_component(item1, item1_component)
    esper.add_component(item1, Position(10.0, 10.0))
    esper.add_component(item1, Collider(0.4))

    # Process pickup
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Verify CollectedItems component added and contains item
    assert esper.has_component(player, CollectedItems)
    collected = esper.component_for_entity(player, CollectedItems)
    assert len(collected.items) == 1
    assert collected.items[0].name == "mushroom"

    # Create second item
    item2 = esper.create_entity()
    item2_component = Item("triple_shot", {}, ["multi_shot"])
    esper.add_component(item2, item2_component)
    esper.add_component(item2, Position(10.0, 10.0))
    esper.add_component(item2, Collider(0.4))

    # Process pickup again
    system.process()

    # Verify second item added
    assert len(collected.items) == 2
    assert collected.items[1].name == "triple_shot"


def test_pickup_creates_collected_items_if_missing():
    """Test CollectedItems component is created if player doesn't have it."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player without CollectedItems
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    esper.add_component(player, Stats(5.0, 1.0, 0.3, 10.0))

    # Verify no CollectedItems initially
    assert not esper.has_component(player, CollectedItems)

    # Create and pick up item
    item_entity = esper.create_entity()
    item_component = Item("test_item", {}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(10.0, 10.0))
    esper.add_component(item_entity, Collider(0.4))

    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Verify CollectedItems was created
    assert esper.has_component(player, CollectedItems)
    collected = esper.component_for_entity(player, CollectedItems)
    assert len(collected.items) == 1
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_item_pickup_system.py::test_pickup_adds_to_collected_items -v`

Expected: FAIL with "AssertionError: assert False" (CollectedItems not added)

**Step 3: Write minimal implementation**

Modify `_pickup_item` method in `src/systems/item_pickup.py` (add after stat modification):

```python
    def _pickup_item(self, player_ent: int, item_ent: int, item: Item):
        """Apply item effects and remove item entity.

        Args:
            player_ent: Player entity ID
            item_ent: Item entity ID
            item: Item component
        """
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

        # Remove item entity
        esper.delete_entity(item_ent)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_item_pickup_system.py::test_pickup_adds_to_collected_items tests/test_item_pickup_system.py::test_pickup_creates_collected_items_if_missing -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/systems/item_pickup.py tests/test_item_pickup_system.py
git commit -m "feat: add CollectedItems tracking to ItemPickupSystem

- Creates CollectedItems component if missing
- Appends picked up items to collection
- Tests verify items are tracked correctly

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: ItemPickupSystem - Notifications

**Files:**
- Modify: `src/systems/item_pickup.py:68` (after CollectedItems tracking in _pickup_item)
- Test: `tests/test_item_pickup_system.py:175` (add after existing tests)

**Step 1: Write the failing test**

Add to `tests/test_item_pickup_system.py`:

```python
def test_pickup_shows_notification():
    """Test notification is set after pickup."""
    world_name = "test_world"
    esper.switch_world(world_name)
    from src.config import Config

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    esper.add_component(player, Stats(5.0, 1.0, 0.3, 10.0))

    # Create item
    item_entity = esper.create_entity()
    item_component = Item("magic_mushroom", {}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(10.0, 10.0))
    esper.add_component(item_entity, Collider(0.4))

    # Process pickup
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Verify notification set
    assert system.notification == "Picked up: magic_mushroom"
    assert system.notification_timer == Config.NOTIFICATION_DURATION


def test_notification_clears_after_timer():
    """Test notification disappears after timer expires."""
    from src.config import Config

    system = ItemPickupSystem()
    system.notification = "Test message"
    system.notification_timer = Config.NOTIFICATION_DURATION

    # Advance time by 2.1 seconds
    for _ in range(131):  # 131 frames * 0.016 = 2.096 seconds
        system.dt = 0.016
        system.process()

    # Verify notification cleared
    assert system.notification is None
    assert system.notification_timer <= 0


def test_notification_doesnt_clear_prematurely():
    """Test notification remains visible during timer."""
    from src.config import Config

    system = ItemPickupSystem()
    system.notification = "Test message"
    system.notification_timer = Config.NOTIFICATION_DURATION

    # Advance time by 1 second
    for _ in range(62):  # 62 frames * 0.016 = 0.992 seconds
        system.dt = 0.016
        system.process()

    # Verify notification still visible
    assert system.notification == "Test message"
    assert system.notification_timer > 0
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_item_pickup_system.py::test_pickup_shows_notification -v`

Expected: FAIL with "AssertionError: assert None == 'Picked up: magic_mushroom'"

**Step 3: Write minimal implementation**

Modify `_pickup_item` method in `src/systems/item_pickup.py` (add after CollectedItems tracking):

```python
    def _pickup_item(self, player_ent: int, item_ent: int, item: Item):
        """Apply item effects and remove item entity.

        Args:
            player_ent: Player entity ID
            item_ent: Item entity ID
            item: Item component
        """
        from src.config import Config

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
        self.notification_timer = Config.NOTIFICATION_DURATION

        # Remove item entity
        esper.delete_entity(item_ent)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_item_pickup_system.py::test_pickup_shows_notification tests/test_item_pickup_system.py::test_notification_clears_after_timer tests/test_item_pickup_system.py::test_notification_doesnt_clear_prematurely -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/systems/item_pickup.py tests/test_item_pickup_system.py
git commit -m "feat: add pickup notifications to ItemPickupSystem

- Set notification message and timer on pickup
- Notification timer decrements each frame
- Notification clears when timer expires
- Tests verify notification lifecycle

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Multi-shot Effect in ShootingSystem

**Files:**
- Modify: `src/systems/shooting.py:60` (in _create_projectile method)
- Test: `tests/test_shooting_system.py:71` (add after existing tests)

**Step 1: Write the failing test**

Add to `tests/test_shooting_system.py`:

```python
def test_multi_shot_fires_three_projectiles():
    """Test multi_shot effect creates 3 projectiles in spread pattern."""
    import math
    from src.systems.shooting import ShootingSystem
    from src.systems.input import InputSystem
    from src.components.game import CollectedItems, Item

    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with multi_shot effect
    player = create_player(world_name, 30.0, 20.0)
    stats = esper.component_for_entity(player, Stats)

    # Add multi_shot item
    collected = CollectedItems()
    multi_shot_item = Item("triple_shot", {}, ["multi_shot"])
    collected.items.append(multi_shot_item)
    esper.add_component(player, collected)

    # Set firing input
    input_system = InputSystem()
    input_system.shooting_direction = (1.0, 0.0)  # Fire right

    # Fire weapon
    shooting_system = ShootingSystem()
    shooting_system.dt = 1.0  # Enough time to reset cooldown
    shooting_system.process()

    # Count projectiles
    projectiles = list(esper.get_components(Projectile, Velocity))
    assert len(projectiles) == 3

    # Check spread pattern
    velocities = [vel for _, (proj, vel) in projectiles]

    # Center shot should be (1, 0) direction
    # Left should be rotated -15 degrees
    # Right should be rotated +15 degrees
    angles = [math.atan2(vel.dy, vel.dx) for vel in velocities]
    angles.sort()

    # Verify spread (angles should be approximately -15°, 0°, +15° in radians)
    assert abs(angles[0] - math.radians(-15)) < 0.01
    assert abs(angles[1]) < 0.01  # Center
    assert abs(angles[2] - math.radians(15)) < 0.01


def test_multi_shot_each_projectile_full_damage():
    """Test each projectile in multi-shot has full damage."""
    from src.systems.shooting import ShootingSystem
    from src.systems.input import InputSystem
    from src.components.game import CollectedItems, Item

    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with multi_shot
    player = create_player(world_name, 30.0, 20.0)
    stats = esper.component_for_entity(player, Stats)

    collected = CollectedItems()
    collected.items.append(Item("triple_shot", {}, ["multi_shot"]))
    esper.add_component(player, collected)

    # Set firing input
    input_system = InputSystem()
    input_system.shooting_direction = (1.0, 0.0)

    # Fire weapon
    shooting_system = ShootingSystem()
    shooting_system.dt = 1.0
    shooting_system.process()

    # Check all projectiles have full damage
    for _, (proj,) in esper.get_components(Projectile):
        assert proj.damage == stats.damage


def test_normal_shot_without_multi_shot():
    """Test normal firing creates single projectile without multi_shot."""
    from src.systems.shooting import ShootingSystem
    from src.systems.input import InputSystem

    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player without multi_shot
    player = create_player(world_name, 30.0, 20.0)

    # Set firing input
    input_system = InputSystem()
    input_system.shooting_direction = (1.0, 0.0)

    # Fire weapon
    shooting_system = ShootingSystem()
    shooting_system.dt = 1.0
    shooting_system.process()

    # Should only create 1 projectile
    projectiles = list(esper.get_components(Projectile))
    assert len(projectiles) == 1
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_shooting_system.py::test_multi_shot_fires_three_projectiles -v`

Expected: FAIL with "AssertionError: assert 1 == 3" (only 1 projectile created)

**Step 3: Read existing ShootingSystem code**

Read: `src/systems/shooting.py` to understand structure

**Step 4: Write minimal implementation**

Modify `src/systems/shooting.py`. First, add helper method after `_create_projectile`:

```python
    def _spawn_projectile(self, player_ent: int, pos: Position, angle: float, stats: Stats):
        """Spawn a single projectile at the given angle.

        Args:
            player_ent: Player entity ID (projectile owner)
            pos: Starting position
            angle: Angle in radians
            stats: Player stats for damage/speed
        """
        import math
        from src.config import Config

        # Create projectile entity
        projectile = esper.create_entity()

        # Calculate velocity from angle
        vel_x = math.cos(angle) * stats.shot_speed
        vel_y = math.sin(angle) * stats.shot_speed

        esper.add_component(projectile, Position(pos.x, pos.y))
        esper.add_component(projectile, Velocity(vel_x, vel_y))
        esper.add_component(projectile, Sprite('.', 'yellow'))
        esper.add_component(projectile, Collider(Config.PROJECTILE_RADIUS))
        esper.add_component(projectile, Projectile(stats.damage, player_ent))
```

Then modify `_create_projectile` method to check for multi-shot:

```python
    def _create_projectile(self, player_ent: int, stats: Stats):
        """Create projectile(s) from player.

        Args:
            player_ent: Player entity ID
            stats: Player stats component
        """
        import math
        from src.components.game import CollectedItems

        # Get direction from InputSystem
        if self.input_system.shooting_direction is None:
            return

        direction_x, direction_y = self.input_system.shooting_direction

        # Normalize direction
        magnitude = math.sqrt(direction_x * direction_x + direction_y * direction_y)
        if magnitude == 0:
            return

        direction_x /= magnitude
        direction_y /= magnitude

        # Get player position
        pos = esper.component_for_entity(player_ent, Position)

        # Check for multi-shot effect
        has_multi_shot = False
        if esper.has_component(player_ent, CollectedItems):
            collected = esper.component_for_entity(player_ent, CollectedItems)
            has_multi_shot = collected.has_effect("multi_shot")

        # Calculate base angle
        angle = math.atan2(direction_y, direction_x)

        if has_multi_shot:
            # Fire 3 projectiles: left (-15°), center, right (+15°)
            self._spawn_projectile(player_ent, pos, angle - math.radians(15), stats)
            self._spawn_projectile(player_ent, pos, angle, stats)
            self._spawn_projectile(player_ent, pos, angle + math.radians(15), stats)
        else:
            # Fire single projectile
            self._spawn_projectile(player_ent, pos, angle, stats)
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_shooting_system.py::test_multi_shot_fires_three_projectiles tests/test_shooting_system.py::test_multi_shot_each_projectile_full_damage tests/test_shooting_system.py::test_normal_shot_without_multi_shot -v`

Expected: PASS (3 tests)

**Step 6: Run all shooting tests**

Run: `uv run pytest tests/test_shooting_system.py -v`

Expected: All tests pass (existing + new)

**Step 7: Commit**

```bash
git add src/systems/shooting.py tests/test_shooting_system.py
git commit -m "feat: add multi-shot effect to ShootingSystem

- Check for multi_shot effect in CollectedItems
- Fire 3 projectiles in 30° spread pattern (-15°, 0°, +15°)
- Each projectile has full damage
- Extract _spawn_projectile helper for code reuse
- Tests verify spread pattern and damage

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Piercing Effect in CollisionSystem

**Files:**
- Modify: `src/systems/collision.py` (_projectile_hit_enemy method)
- Test: `tests/test_collision_system.py:216` (add after existing tests)

**Step 1: Write the failing test**

Add to `tests/test_collision_system.py`:

```python
def test_piercing_projectile_doesnt_get_destroyed():
    """Test piercing projectiles continue after hitting enemy."""
    from src.components.game import CollectedItems, Item

    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with piercing effect
    player = create_player(world_name, 10.0, 10.0)
    collected = CollectedItems()
    collected.items.append(Item("piercing_tears", {}, ["piercing"]))
    esper.add_component(player, collected)

    # Create enemy
    from src.entities.enemies import create_enemy
    enemy = create_enemy(world_name, "chaser", 15.0, 10.0)
    enemy_health = esper.component_for_entity(enemy, Health)

    # Create projectile from player
    proj_entity = esper.create_entity()
    esper.add_component(proj_entity, Position(15.0, 10.0))
    esper.add_component(proj_entity, Velocity(10.0, 0.0))
    esper.add_component(proj_entity, Collider(0.1))
    esper.add_component(proj_entity, Projectile(1.0, player))

    # Process collision
    collision_system = CollisionSystem()
    collision_system.process()

    # Enemy should take damage
    assert enemy_health.current < enemy_health.max

    # Projectile should still exist (piercing)
    assert esper.entity_exists(proj_entity)


def test_normal_projectile_gets_destroyed():
    """Test normal projectiles are destroyed after hitting enemy."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player without piercing
    player = create_player(world_name, 10.0, 10.0)

    # Create enemy
    from src.entities.enemies import create_enemy
    enemy = create_enemy(world_name, "chaser", 15.0, 10.0)

    # Create projectile from player
    proj_entity = esper.create_entity()
    esper.add_component(proj_entity, Position(15.0, 10.0))
    esper.add_component(proj_entity, Velocity(10.0, 0.0))
    esper.add_component(proj_entity, Collider(0.1))
    esper.add_component(proj_entity, Projectile(1.0, player))

    # Process collision
    collision_system = CollisionSystem()
    collision_system.process()

    # Projectile should be destroyed (normal shot)
    assert not esper.entity_exists(proj_entity)


def test_piercing_hits_multiple_enemies():
    """Test piercing projectile damages all enemies in path."""
    from src.components.game import CollectedItems, Item

    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with piercing
    player = create_player(world_name, 10.0, 10.0)
    collected = CollectedItems()
    collected.items.append(Item("piercing_tears", {}, ["piercing"]))
    esper.add_component(player, collected)

    # Create 2 enemies in line
    from src.entities.enemies import create_enemy
    enemy1 = create_enemy(world_name, "chaser", 15.0, 10.0)
    enemy2 = create_enemy(world_name, "chaser", 15.5, 10.0)

    enemy1_health = esper.component_for_entity(enemy1, Health)
    enemy2_health = esper.component_for_entity(enemy2, Health)

    initial_hp1 = enemy1_health.current
    initial_hp2 = enemy2_health.current

    # Create projectile
    proj_entity = esper.create_entity()
    esper.add_component(proj_entity, Position(15.0, 10.0))
    esper.add_component(proj_entity, Velocity(10.0, 0.0))
    esper.add_component(proj_entity, Collider(0.1))
    esper.add_component(proj_entity, Projectile(1.0, player))

    # Process collision
    collision_system = CollisionSystem()
    collision_system.process()

    # Both enemies should take damage
    assert enemy1_health.current < initial_hp1
    assert enemy2_health.current < initial_hp2
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_collision_system.py::test_piercing_projectile_doesnt_get_destroyed -v`

Expected: FAIL with "AssertionError: assert False" (projectile was destroyed)

**Step 3: Read existing CollisionSystem code**

Read: `src/systems/collision.py` to find `_projectile_hit_enemy` method

**Step 4: Write minimal implementation**

Modify `_projectile_hit_enemy` method in `src/systems/collision.py`:

```python
    def _projectile_hit_enemy(self, projectile: int, enemy: int):
        """Handle projectile hitting enemy.

        Args:
            projectile: Projectile entity ID
            enemy: Enemy entity ID
        """
        from src.components.game import Player, CollectedItems

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
            esper.delete_entity(enemy)
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_collision_system.py::test_piercing_projectile_doesnt_get_destroyed tests/test_collision_system.py::test_normal_projectile_gets_destroyed tests/test_collision_system.py::test_piercing_hits_multiple_enemies -v`

Expected: PASS (3 tests)

**Step 6: Run all collision tests**

Run: `uv run pytest tests/test_collision_system.py -v`

Expected: All tests pass

**Step 7: Commit**

```bash
git add src/systems/collision.py tests/test_collision_system.py
git commit -m "feat: add piercing effect to CollisionSystem

- Check for piercing effect when projectile hits enemy
- Piercing projectiles continue after damage, normal ones removed
- Allows piercing shots to hit multiple enemies in path
- Tests verify piercing behavior and multi-enemy hits

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Enemy Item Drops in CollisionSystem

**Files:**
- Modify: `src/systems/collision.py` (_projectile_hit_enemy method, enemy death section)
- Test: `tests/test_collision_system.py:275` (add after piercing tests)

**Step 1: Write the failing test**

Add to `tests/test_collision_system.py`:

```python
def test_enemy_drops_item_on_death():
    """Test enemies can drop items when killed."""
    import random
    from src.config import Config

    world_name = "test_world"
    esper.switch_world(world_name)

    # Seed random for predictable test
    random.seed(42)

    # Create player
    player = create_player(world_name, 10.0, 10.0)

    # Create many enemies to ensure at least one drop
    # With 15% drop rate, 20 enemies should give ~3 drops
    from src.entities.enemies import create_enemy
    enemies = []
    for i in range(20):
        enemy = create_enemy(world_name, "chaser", 15.0 + i * 0.1, 10.0)
        enemies.append(enemy)

    # Kill all enemies with projectiles
    for enemy in enemies:
        proj = esper.create_entity()
        esper.add_component(proj, Position(15.0, 10.0))
        esper.add_component(proj, Velocity(10.0, 0.0))
        esper.add_component(proj, Collider(0.1))
        esper.add_component(proj, Projectile(100.0, player))  # High damage to kill

        collision_system = CollisionSystem()
        collision_system.process()

    # Count dropped items
    item_count = len(list(esper.get_components(Item)))

    # Should have at least 1 drop from 20 enemies
    assert item_count > 0


def test_item_drops_at_enemy_position():
    """Test dropped items spawn at enemy position."""
    import random
    from src.config import Config

    world_name = "test_world"
    esper.switch_world(world_name)

    # Force a drop by manipulating random
    original_random = random.random
    random.random = lambda: 0.0  # Always drop

    try:
        # Create player
        player = create_player(world_name, 10.0, 10.0)

        # Create enemy at specific position
        from src.entities.enemies import create_enemy
        enemy = create_enemy(world_name, "chaser", 25.0, 30.0)

        # Kill enemy
        proj = esper.create_entity()
        esper.add_component(proj, Position(25.0, 30.0))
        esper.add_component(proj, Velocity(10.0, 0.0))
        esper.add_component(proj, Collider(0.1))
        esper.add_component(proj, Projectile(100.0, player))

        collision_system = CollisionSystem()
        collision_system.process()

        # Find dropped item
        for _, (item, pos) in esper.get_components(Item, Position):
            # Item should be at enemy's death position
            assert abs(pos.x - 25.0) < 0.1
            assert abs(pos.y - 30.0) < 0.1
            break
        else:
            assert False, "No item was dropped"

    finally:
        random.random = original_random


def test_no_drop_without_luck():
    """Test enemies don't always drop items."""
    import random

    world_name = "test_world"
    esper.switch_world(world_name)

    # Force no drops
    random.random = lambda: 1.0  # Never drop

    try:
        # Create player
        player = create_player(world_name, 10.0, 10.0)

        # Create and kill enemy
        from src.entities.enemies import create_enemy
        enemy = create_enemy(world_name, "chaser", 15.0, 10.0)

        proj = esper.create_entity()
        esper.add_component(proj, Position(15.0, 10.0))
        esper.add_component(proj, Velocity(10.0, 0.0))
        esper.add_component(proj, Collider(0.1))
        esper.add_component(proj, Projectile(100.0, player))

        collision_system = CollisionSystem()
        collision_system.process()

        # Should be no items
        item_count = len(list(esper.get_components(Item)))
        assert item_count == 0

    finally:
        pass  # Cleanup handled by conftest
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_collision_system.py::test_enemy_drops_item_on_death -v`

Expected: FAIL with "AssertionError: assert 0 > 0" (no items dropped)

**Step 3: Write minimal implementation**

Modify `_projectile_hit_enemy` method in `src/systems/collision.py` (modify enemy death section):

```python
    def _projectile_hit_enemy(self, projectile: int, enemy: int):
        """Handle projectile hitting enemy.

        Args:
            projectile: Projectile entity ID
            enemy: Enemy entity ID
        """
        import random
        from src.components.game import Player, CollectedItems
        from src.config import Config

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
                spawn_random_item(esper._current_world, pos.x, pos.y)

            esper.delete_entity(enemy)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_collision_system.py::test_enemy_drops_item_on_death tests/test_collision_system.py::test_item_drops_at_enemy_position tests/test_collision_system.py::test_no_drop_without_luck -v`

Expected: PASS (3 tests)

**Step 5: Run all collision tests**

Run: `uv run pytest tests/test_collision_system.py -v`

Expected: All tests pass

**Step 6: Commit**

```bash
git add src/systems/collision.py tests/test_collision_system.py
git commit -m "feat: add enemy item drops to CollisionSystem

- 15% chance to drop item on enemy death
- Item spawns at enemy's death position using spawn_random_item
- Tests verify drop rate and positioning

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 11: HomingSystem Implementation

**Files:**
- Create: `src/systems/homing.py`
- Create: `tests/test_homing_system.py`

**Step 1: Write the failing test**

Create `tests/test_homing_system.py`:

```python
"""Tests for HomingSystem."""
import esper
import math
from src.systems.homing import HomingSystem
from src.components.core import Position, Velocity
from src.components.combat import Projectile
from src.components.game import Player, Enemy, CollectedItems, Item
from src.entities.player import create_player


def test_homing_system_rotates_toward_target():
    """Test projectile velocity rotates toward nearest enemy."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with homing effect
    player = create_player(world_name, 10.0, 10.0)
    collected = CollectedItems()
    collected.items.append(Item("homing_shots", {}, ["homing"]))
    esper.add_component(player, collected)

    # Create enemy to the east
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("chaser"))
    esper.add_component(enemy, Position(20.0, 10.0))

    # Create projectile firing north
    proj = esper.create_entity()
    esper.add_component(proj, Position(10.0, 10.0))
    esper.add_component(proj, Velocity(0.0, 10.0))  # North
    esper.add_component(proj, Projectile(1.0, player))

    # Process homing
    system = HomingSystem()
    system.dt = 0.016
    system.process()

    # Velocity should have rotated toward east (positive dx)
    vel = esper.component_for_entity(proj, Velocity)
    assert vel.dx > 0  # Rotated toward enemy


def test_homing_respects_turn_rate():
    """Test projectile doesn't instantly lock on."""
    from src.config import Config

    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with homing
    player = create_player(world_name, 10.0, 10.0)
    collected = CollectedItems()
    collected.items.append(Item("homing_shots", {}, ["homing"]))
    esper.add_component(player, collected)

    # Create enemy directly behind projectile (180° away)
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("chaser"))
    esper.add_component(enemy, Position(10.0, 0.0))  # South

    # Create projectile firing north (away from enemy)
    proj = esper.create_entity()
    esper.add_component(proj, Position(10.0, 10.0))
    esper.add_component(proj, Velocity(0.0, 10.0))  # North
    esper.add_component(proj, Projectile(1.0, player))

    initial_angle = math.atan2(10.0, 0.0)  # North

    # Process one frame
    system = HomingSystem()
    system.dt = 0.016
    system.process()

    # Check rotation amount
    vel = esper.component_for_entity(proj, Velocity)
    new_angle = math.atan2(vel.dy, vel.dx)

    rotation = abs(new_angle - initial_angle)

    # Should rotate by at most HOMING_TURN_RATE * dt
    max_rotation = math.radians(Config.HOMING_TURN_RATE * system.dt)
    assert rotation <= max_rotation + 0.01  # Small tolerance


def test_homing_only_affects_player_projectiles():
    """Test enemy projectiles are not affected by homing."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with homing
    player = create_player(world_name, 10.0, 10.0)
    collected = CollectedItems()
    collected.items.append(Item("homing_shots", {}, ["homing"]))
    esper.add_component(player, collected)

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))
    esper.add_component(enemy, Position(20.0, 10.0))

    # Create enemy projectile
    enemy_proj = esper.create_entity()
    esper.add_component(enemy_proj, Position(15.0, 10.0))
    initial_vel = Velocity(10.0, 0.0)
    esper.add_component(enemy_proj, initial_vel)
    esper.add_component(enemy_proj, Projectile(1.0, enemy))

    # Process homing
    system = HomingSystem()
    system.dt = 0.016
    system.process()

    # Enemy projectile velocity should be unchanged
    vel = esper.component_for_entity(enemy_proj, Velocity)
    assert vel.dx == 10.0
    assert vel.dy == 0.0


def test_homing_without_effect_does_nothing():
    """Test homing system does nothing when player lacks effect."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player without homing
    player = create_player(world_name, 10.0, 10.0)

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("chaser"))
    esper.add_component(enemy, Position(20.0, 10.0))

    # Create projectile
    proj = esper.create_entity()
    esper.add_component(proj, Position(10.0, 10.0))
    initial_vel = Velocity(0.0, 10.0)
    esper.add_component(proj, initial_vel)
    esper.add_component(proj, Projectile(1.0, player))

    # Process homing
    system = HomingSystem()
    system.dt = 0.016
    system.process()

    # Velocity should be unchanged
    vel = esper.component_for_entity(proj, Velocity)
    assert vel.dx == 0.0
    assert vel.dy == 10.0


def test_homing_finds_nearest_enemy():
    """Test homing targets the closest enemy."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with homing
    player = create_player(world_name, 10.0, 10.0)
    collected = CollectedItems()
    collected.items.append(Item("homing_shots", {}, ["homing"]))
    esper.add_component(player, collected)

    # Create far enemy to the north
    far_enemy = esper.create_entity()
    esper.add_component(far_enemy, Enemy("chaser"))
    esper.add_component(far_enemy, Position(10.0, 50.0))

    # Create near enemy to the east
    near_enemy = esper.create_entity()
    esper.add_component(near_enemy, Enemy("chaser"))
    esper.add_component(near_enemy, Position(15.0, 10.0))

    # Create projectile firing north
    proj = esper.create_entity()
    esper.add_component(proj, Position(10.0, 10.0))
    esper.add_component(proj, Velocity(0.0, 10.0))
    esper.add_component(proj, Projectile(1.0, player))

    # Process homing
    system = HomingSystem()
    system.dt = 0.016
    system.process()

    # Should rotate toward near enemy (east) not far enemy (north)
    vel = esper.component_for_entity(proj, Velocity)
    assert vel.dx > 0  # Turned east toward near enemy
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_homing_system.py::test_homing_system_rotates_toward_target -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'src.systems.homing'"

**Step 3: Write minimal implementation**

Create `src/systems/homing.py`:

```python
"""Homing projectile behavior system."""
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

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_homing_system.py -v`

Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add src/systems/homing.py tests/test_homing_system.py
git commit -m "feat: add HomingSystem for bullet curving

- Gradually rotates projectile velocity toward nearest enemy
- Respects HOMING_TURN_RATE to prevent instant lock-on
- Only affects player projectiles when homing effect active
- Tests verify rotation, turn rate limits, and targeting

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: System Registration in GameEngine

**Files:**
- Modify: `src/game/engine.py:10` (imports)
- Modify: `src/game/engine.py:44` (system registration)
- Modify: `src/game/engine.py:64` (dt assignment)
- Test: `tests/test_engine.py:72` (add after existing tests)

**Step 1: Write the failing test**

Add to `tests/test_engine.py`:

```python
def test_engine_has_item_pickup_system():
    """Test game engine registers ItemPickupSystem."""
    from src.systems.item_pickup import ItemPickupSystem

    engine = GameEngine()

    # Check system is registered
    processors = engine.world._processors
    item_pickup_systems = [p for p in processors if isinstance(p, ItemPickupSystem)]
    assert len(item_pickup_systems) == 1


def test_engine_has_homing_system():
    """Test game engine registers HomingSystem."""
    from src.systems.homing import HomingSystem

    engine = GameEngine()

    # Check system is registered
    processors = engine.world._processors
    homing_systems = [p for p in processors if isinstance(p, HomingSystem)]
    assert len(homing_systems) == 1


def test_new_systems_have_correct_priority():
    """Test new systems execute in correct order."""
    engine = GameEngine()

    # Get all processors with their priorities
    processors = engine.world._processors

    # Find our new systems
    homing_system = None
    item_pickup_system = None

    for proc in processors:
        if proc.__class__.__name__ == 'HomingSystem':
            homing_system = proc
        elif proc.__class__.__name__ == 'ItemPickupSystem':
            item_pickup_system = proc

    assert homing_system is not None
    assert item_pickup_system is not None

    # Verify priorities (HomingSystem at 4.5, ItemPickupSystem at 6.5)
    # Priority is stored in processor priority dict
    # We can verify by checking they come after/before certain systems
    system_order = [type(p).__name__ for p in processors]

    homing_idx = system_order.index('HomingSystem')
    item_pickup_idx = system_order.index('ItemPickupSystem')
    movement_idx = system_order.index('MovementSystem')
    invincibility_idx = system_order.index('InvincibilitySystem')

    # HomingSystem should be after MovementSystem
    assert homing_idx > movement_idx

    # ItemPickupSystem should be after InvincibilitySystem
    assert item_pickup_idx > invincibility_idx
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_engine.py::test_engine_has_item_pickup_system -v`

Expected: FAIL with "AssertionError: assert 0 == 1" (system not registered)

**Step 3: Write minimal implementation**

Modify `src/game/engine.py`:

Add imports (line 10):
```python
from src.systems.homing import HomingSystem
from src.systems.item_pickup import ItemPickupSystem
```

Add system registration after MovementSystem (around line 44):
```python
        self.movement_system = MovementSystem()
        self.world.add_processor(self.movement_system, priority=4)

        self.homing_system = HomingSystem()
        self.world.add_processor(self.homing_system, priority=4.5)

        self.collision_system = CollisionSystem()
```

Add system registration after InvincibilitySystem (around line 50):
```python
        self.invincibility_system = InvincibilitySystem()
        self.world.add_processor(self.invincibility_system, priority=6)

        self.item_pickup_system = ItemPickupSystem()
        self.world.add_processor(self.item_pickup_system, priority=6.5)

        self.render_system = RenderSystem()
```

Add dt assignment in update() method (around line 65):
```python
        self.ai_system.dt = dt
        self.enemy_shooting_system.dt = dt
        self.invincibility_system.dt = dt
        self.homing_system.dt = dt
        self.item_pickup_system.dt = dt
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_engine.py::test_engine_has_item_pickup_system tests/test_engine.py::test_engine_has_homing_system tests/test_engine.py::test_new_systems_have_correct_priority -v`

Expected: PASS (3 tests)

**Step 5: Run all engine tests**

Run: `uv run pytest tests/test_engine.py -v`

Expected: All tests pass

**Step 6: Commit**

```bash
git add src/game/engine.py tests/test_engine.py
git commit -m "feat: register HomingSystem and ItemPickupSystem in GameEngine

- Add HomingSystem at priority 4.5 (after movement)
- Add ItemPickupSystem at priority 6.5 (after invincibility)
- Set dt on both systems in update loop
- Tests verify registration and priority ordering

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 13: Notification Rendering in RenderSystem

**Files:**
- Modify: `src/systems/render.py` (end of render method)
- Test: `tests/test_render_system.py:136` (add after existing tests)

**Step 1: Write the failing test**

Add to `tests/test_render_system.py`:

```python
def test_render_displays_pickup_notification():
    """Test RenderSystem displays item pickup notifications."""
    from src.systems.item_pickup import ItemPickupSystem
    from src.config import Config

    world_name = "test_world"
    esper.switch_world(world_name)

    # Create render system with item pickup system reference
    render_system = RenderSystem()
    item_pickup_system = ItemPickupSystem()
    render_system.item_pickup_system = item_pickup_system

    # Set notification
    item_pickup_system.notification = "Picked up: magic_mushroom"
    item_pickup_system.notification_timer = 2.0

    # Render
    grid = render_system.render()

    # Check notification appears in grid (top center)
    # Notification should be in first row
    first_row = grid[0]

    # Find the notification text in the row
    notification_found = False
    for cell in first_row:
        if "Picked up" in cell:
            notification_found = True
            break

    assert notification_found


def test_render_no_notification_when_none():
    """Test RenderSystem doesn't crash when no notification."""
    from src.systems.item_pickup import ItemPickupSystem

    world_name = "test_world"
    esper.switch_world(world_name)

    # Create render system with item pickup system
    render_system = RenderSystem()
    item_pickup_system = ItemPickupSystem()
    render_system.item_pickup_system = item_pickup_system

    # No notification
    item_pickup_system.notification = None

    # Render should not crash
    grid = render_system.render()
    assert grid is not None


def test_render_without_item_pickup_system():
    """Test RenderSystem works when item_pickup_system not set."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create render system without item pickup system reference
    render_system = RenderSystem()

    # Render should not crash
    grid = render_system.render()
    assert grid is not None
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_render_system.py::test_render_displays_pickup_notification -v`

Expected: FAIL (notification not in grid)

**Step 3: Read existing RenderSystem code**

Read: `src/systems/render.py` to understand render method structure

**Step 4: Write minimal implementation**

Modify `render()` method in `src/systems/render.py` (add at end before return):

```python
    def render(self):
        """Render all entities and UI elements to grid.

        Returns:
            2D grid of rendered characters and colors
        """
        from src.config import Config

        # ... existing rendering code ...

        # Render item pickup notification
        if hasattr(self, 'item_pickup_system') and self.item_pickup_system.notification:
            notification = self.item_pickup_system.notification
            # Center the notification at top of screen
            x = (Config.ROOM_WIDTH - len(notification)) // 2
            if 0 <= x < Config.ROOM_WIDTH:
                for i, char in enumerate(notification):
                    if x + i < Config.ROOM_WIDTH:
                        self.grid[0][x + i] = (char, 'yellow')

        return self.grid
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_render_system.py::test_render_displays_pickup_notification tests/test_render_system.py::test_render_no_notification_when_none tests/test_render_system.py::test_render_without_item_pickup_system -v`

Expected: PASS (3 tests)

**Step 6: Update GameEngine to set reference**

Modify `src/game/engine.py` in `__init__` after ItemPickupSystem registration:

```python
        self.item_pickup_system = ItemPickupSystem()
        self.world.add_processor(self.item_pickup_system, priority=6.5)

        self.render_system = RenderSystem()
        self.world.add_processor(self.render_system, priority=7)

        # Store reference for notifications
        self.render_system.item_pickup_system = self.item_pickup_system
```

**Step 7: Run all render tests**

Run: `uv run pytest tests/test_render_system.py -v`

Expected: All tests pass

**Step 8: Commit**

```bash
git add src/systems/render.py src/game/engine.py tests/test_render_system.py
git commit -m "feat: add notification rendering to RenderSystem

- Display pickup notifications at top center of screen
- Yellow text for 2 seconds (controlled by ItemPickupSystem timer)
- GameEngine sets render_system.item_pickup_system reference
- Tests verify notification display and edge cases

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 14: Initialize Player with CollectedItems

**Files:**
- Modify: `src/entities/player.py` (create_player function)
- Test: `tests/test_entities.py:53` (add after existing tests)

**Step 1: Write the failing test**

Add to `tests/test_entities.py`:

```python
def test_create_player_has_collected_items():
    """Test create_player initializes CollectedItems component."""
    from src.components.game import CollectedItems

    world_name = "test_world"
    esper.switch_world(world_name)

    player = create_player(world_name, 10.0, 20.0)

    # Should have CollectedItems component
    assert esper.has_component(player, CollectedItems)

    # Should start with empty collection
    collected = esper.component_for_entity(player, CollectedItems)
    assert len(collected.items) == 0
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_entities.py::test_create_player_has_collected_items -v`

Expected: FAIL with "AssertionError: assert False" (no CollectedItems component)

**Step 3: Write minimal implementation**

Modify `create_player` function in `src/entities/player.py` (add after Stats component):

```python
def create_player(world: str, x: float, y: float) -> int:
    """Create the player entity.

    Args:
        world: World name to create entity in
        x: Starting x position
        y: Starting y position

    Returns:
        Entity ID of created player
    """
    from src.config import Config
    from src.components.game import CollectedItems

    esper.switch_world(world)
    player = esper.create_entity()

    esper.add_component(player, Player())
    esper.add_component(player, Position(x, y))
    esper.add_component(player, Velocity(0.0, 0.0))
    esper.add_component(player, Sprite('@', 'cyan'))
    esper.add_component(player, Health(Config.PLAYER_MAX_HP, Config.PLAYER_MAX_HP))
    esper.add_component(player, Stats(
        speed=Config.PLAYER_SPEED,
        damage=Config.PLAYER_DAMAGE,
        fire_rate=Config.PLAYER_FIRE_RATE,
        shot_speed=Config.PLAYER_SHOT_SPEED
    ))
    esper.add_component(player, Collider(Config.PLAYER_HITBOX_RADIUS))
    esper.add_component(player, CollectedItems())  # Start with empty collection

    return player
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_entities.py::test_create_player_has_collected_items -v`

Expected: PASS

**Step 5: Run all entity tests**

Run: `uv run pytest tests/test_entities.py -v`

Expected: All tests pass

**Step 6: Commit**

```bash
git add src/entities/player.py tests/test_entities.py
git commit -m "feat: initialize player with CollectedItems component

- Add CollectedItems component to player on creation
- Starts with empty items list
- Test verifies component exists and is empty

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 15: Integration Test - Full Pickup Flow

**Files:**
- Test: `tests/test_integration.py:89` (add after existing integration tests)

**Step 1: Write the test**

Add to `tests/test_integration.py`:

```python
def test_item_pickup_and_stat_modification():
    """Test complete pickup flow from collision to stat change."""
    from src.entities.items import create_item
    from src.systems.item_pickup import ItemPickupSystem
    from src.components.game import CollectedItems

    # Create engine and world
    engine = GameEngine()

    # Create player with base stats
    player = create_player(engine.world_name, 30.0, 20.0)
    stats = esper.component_for_entity(player, Stats)

    initial_damage = stats.damage
    initial_speed = stats.speed

    # Create item with stat modifiers at player position
    item_entity = create_item(engine.world_name, "magic_mushroom", 30.0, 20.0)

    # Process item pickup system
    item_pickup_system = ItemPickupSystem()
    item_pickup_system.dt = 0.016
    esper.switch_world(engine.world_name)
    item_pickup_system.process()

    # Verify stats changed (magic_mushroom: +1.0 damage, 1.2 speed)
    assert stats.damage == initial_damage + 1.0  # Additive
    assert stats.speed == initial_speed * 1.2    # Multiplicative

    # Verify item added to CollectedItems
    assert esper.has_component(player, CollectedItems)
    collected = esper.component_for_entity(player, CollectedItems)
    assert len(collected.items) == 1
    assert collected.items[0].name == "magic_mushroom"

    # Verify item entity removed
    assert not esper.entity_exists(item_entity)

    # Verify notification displayed
    assert item_pickup_system.notification == "Picked up: magic_mushroom"
    assert item_pickup_system.notification_timer > 0


def test_piercing_effect_in_combat():
    """Test piercing effect allows hitting multiple enemies."""
    from src.entities.enemies import create_enemy
    from src.systems.collision import CollisionSystem
    from src.components.game import CollectedItems, Item

    # Create engine
    engine = GameEngine()

    # Create player with piercing effect
    player = create_player(engine.world_name, 10.0, 10.0)
    collected = CollectedItems()
    collected.items.append(Item("piercing_tears", {"damage": 0.5}, ["piercing"]))
    esper.add_component(player, collected)

    stats = esper.component_for_entity(player, Stats)

    # Create 2 enemies in a line
    enemy1 = create_enemy(engine.world_name, "chaser", 15.0, 10.0)
    enemy2 = create_enemy(engine.world_name, "chaser", 15.5, 10.0)

    enemy1_health = esper.component_for_entity(enemy1, Health)
    enemy2_health = esper.component_for_entity(enemy2, Health)

    initial_hp1 = enemy1_health.current
    initial_hp2 = enemy2_health.current

    # Create projectile that will hit both
    proj = esper.create_entity()
    esper.add_component(proj, Position(15.0, 10.0))
    esper.add_component(proj, Velocity(10.0, 0.0))
    esper.add_component(proj, Collider(0.1))
    esper.add_component(proj, Projectile(stats.damage, player))

    # Process collision
    collision_system = CollisionSystem()
    esper.switch_world(engine.world_name)
    collision_system.process()

    # Both enemies should take damage
    assert enemy1_health.current < initial_hp1
    assert enemy2_health.current < initial_hp2

    # Projectile should still exist (piercing)
    assert esper.entity_exists(proj)


def test_homing_effect_curves_bullets():
    """Test homing effect makes projectiles track enemies."""
    from src.entities.enemies import create_enemy
    from src.systems.homing import HomingSystem
    from src.components.game import CollectedItems, Item
    import math

    # Create engine
    engine = GameEngine()

    # Create player with homing effect
    player = create_player(engine.world_name, 10.0, 10.0)
    collected = CollectedItems()
    collected.items.append(Item("homing_shots", {}, ["homing"]))
    esper.add_component(player, collected)

    stats = esper.component_for_entity(player, Stats)

    # Create enemy to the east
    enemy = create_enemy(engine.world_name, "chaser", 20.0, 10.0)

    # Create projectile firing north (away from enemy)
    proj = esper.create_entity()
    esper.add_component(proj, Position(10.0, 10.0))
    esper.add_component(proj, Velocity(0.0, stats.shot_speed))  # North
    esper.add_component(proj, Projectile(stats.damage, player))
    esper.add_component(proj, Collider(0.1))

    # Process homing for several frames
    homing_system = HomingSystem()
    homing_system.dt = 0.016
    esper.switch_world(engine.world_name)

    for _ in range(10):
        homing_system.process()

    # Velocity should have rotated toward enemy (eastward)
    vel = esper.component_for_entity(proj, Velocity)
    assert vel.dx > 0  # Turned toward enemy


def test_multi_shot_creates_spread():
    """Test multi-shot effect fires 3 projectiles."""
    from src.systems.shooting import ShootingSystem
    from src.systems.input import InputSystem
    from src.components.game import CollectedItems, Item

    # Create engine
    engine = GameEngine()

    # Create player with multi-shot
    player = create_player(engine.world_name, 30.0, 20.0)
    collected = CollectedItems()
    collected.items.append(Item("triple_shot", {}, ["multi_shot"]))
    esper.add_component(player, collected)

    # Set up shooting
    input_system = InputSystem()
    input_system.shooting_direction = (1.0, 0.0)  # Fire right

    shooting_system = ShootingSystem()
    shooting_system.input_system = input_system
    shooting_system.dt = 1.0  # Reset cooldown

    esper.switch_world(engine.world_name)
    shooting_system.process()

    # Should have created 3 projectiles
    projectiles = list(esper.get_components(Projectile))
    assert len(projectiles) == 3
```

**Step 2: Run test to verify it passes**

Run: `uv run pytest tests/test_integration.py::test_item_pickup_and_stat_modification -v`

Expected: PASS

Run: `uv run pytest tests/test_integration.py::test_piercing_effect_in_combat -v`

Expected: PASS

Run: `uv run pytest tests/test_integration.py::test_homing_effect_curves_bullets -v`

Expected: PASS

Run: `uv run pytest tests/test_integration.py::test_multi_shot_creates_spread -v`

Expected: PASS

**Step 3: Run all integration tests**

Run: `uv run pytest tests/test_integration.py -v`

Expected: All tests pass

**Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests for item system

- Test full pickup flow (collision, stats, tracking, notification)
- Test piercing effect in combat scenario
- Test homing effect curves projectiles toward enemies
- Test multi-shot creates 3-projectile spread
- All integration tests verify end-to-end functionality

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 16: Final Verification

**Files:**
- None (just running full test suite)

**Step 1: Run full test suite**

Run: `uv run pytest -v`

Expected: All tests pass (99 baseline + new tests)

**Step 2: Check test count**

Run: `uv run pytest --collect-only | grep "test session starts" -A 1`

Expected: Should show significantly more than 99 tests

**Step 3: Verify all systems integrated**

Run: `uv run python -c "from src.game.engine import GameEngine; e = GameEngine(); print(f'Systems: {len(e.world._processors)}')"`

Expected: Should show 10 systems (was 8, now +2 new systems)

**Step 4: If all pass, commit summary**

```bash
git add .
git commit -m "feat: item pickup system complete - all tests passing

Complete implementation of item pickup and stat modification system:
- CollectedItems component tracks picked up items
- ItemPickupSystem handles collision, stat application, notifications
- HomingSystem curves bullets toward enemies
- Multi-shot effect fires 3-projectile spread
- Piercing effect allows projectiles to pass through enemies
- Enemy drops (15% chance) spawn random items
- Hybrid stat system (additive for damage/fire_rate, multiplicative for speed/shot_speed)
- Item database with 6 starter items
- All integration tests passing
- Ready for Phase 2: Progression

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Success Criteria

After completing all tasks:

✓ All tests pass (baseline 99 + new tests ~40+ = 139+ total)
✓ Player can pick up items by walking over them
✓ Stat modifiers apply correctly (hybrid additive/multiplicative system)
✓ CollectedItems tracks all picked up items
✓ Notifications display for 2 seconds after pickup
✓ Piercing effect works (projectiles pass through enemies)
✓ Homing effect works (projectiles curve toward enemies)
✓ Multi-shot effect works (3 projectiles in spread pattern)
✓ Enemies drop items 15% of the time when killed
✓ Integration tests verify end-to-end functionality
✓ All systems registered in GameEngine with correct priorities
✓ Player initialized with CollectedItems component

## Next Steps After Implementation

After this plan is complete:
- Use superpowers:finishing-a-development-branch to merge work
- Update README.md to mark "Item pickup and stat modification system" as complete
- Phase 1: Core Gameplay is DONE! 🎉
- Ready to begin Phase 2: Progression (multi-room dungeons, transitions)
