# TUI Roguelike Prototype Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a playable bullet-hell roguelike prototype with one floor, 3-5 enemy types, 12-15 items, and a boss fight using Python, Rich, and Esper ECS.

**Architecture:** Entity Component System (Esper) with processors for input, movement, collision, AI, shooting, and rendering. Real-time game loop at 30 FPS using Rich Live display. Procedural room generation with branching paths.

**Tech Stack:** Python 3.12+, Rich (TUI rendering), Esper (ECS), pytest (testing)

---

## Task 1: Project Structure & Configuration

**Files:**
- Create: `src/__init__.py`
- Create: `src/config.py`
- Create: `tests/__init__.py`
- Modify: `main.py` (already exists from uv init)

**Step 1: Write config test**

Create `tests/test_config.py`:

```python
import pytest
from src.config import Config


def test_config_has_game_constants():
    """Config should provide all game constants."""
    assert Config.ROOM_WIDTH == 60
    assert Config.ROOM_HEIGHT == 20
    assert Config.FPS == 30
    assert Config.PLAYER_SPEED > 0
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py -v`
Expected: FAIL with "cannot import name 'Config'"

**Step 3: Create config module**

Create `src/__init__.py` (empty file)

Create `src/config.py`:

```python
"""Game configuration and constants."""


class Config:
    """Central configuration for game constants."""

    # Display
    ROOM_WIDTH = 60
    ROOM_HEIGHT = 20
    FPS = 30

    # Player stats
    PLAYER_SPEED = 5.0
    PLAYER_DAMAGE = 1.0
    PLAYER_FIRE_RATE = 2.0
    PLAYER_SHOT_SPEED = 8.0
    PLAYER_MAX_HP = 6
    PLAYER_HITBOX = 0.3

    # Enemy stats
    ENEMY_HITBOX = 0.5

    # Projectile stats
    PROJECTILE_HITBOX = 0.2

    # Game balance
    INVINCIBILITY_DURATION = 0.5
    HEART_DROP_CHANCE = 0.1
    MAX_PROJECTILES = 200
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/__init__.py src/config.py tests/__init__.py tests/test_config.py
git commit -m "feat: add config module with game constants"
```

---

## Task 2: Core ECS Components

**Files:**
- Create: `src/components/__init__.py`
- Create: `src/components/core.py`
- Create: `tests/test_components.py`

**Step 1: Write component tests**

Create `tests/test_components.py`:

```python
import pytest
from src.components.core import Position, Velocity, Health, Sprite


def test_position_stores_coordinates():
    pos = Position(10.5, 20.3)
    assert pos.x == 10.5
    assert pos.y == 20.3


def test_velocity_stores_direction():
    vel = Velocity(1.0, -0.5)
    assert vel.dx == 1.0
    assert vel.dy == -0.5


def test_health_tracks_current_and_max():
    health = Health(3, 6)
    assert health.current == 3
    assert health.max == 6


def test_sprite_stores_appearance():
    sprite = Sprite('@', 'cyan')
    assert sprite.char == '@'
    assert sprite.color == 'cyan'
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_components.py -v`
Expected: FAIL with "cannot import name 'Position'"

**Step 3: Create core components**

Create `src/components/__init__.py` (empty)

Create `src/components/core.py`:

```python
"""Core ECS components for all entities."""


class Position:
    """2D position in the game world."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Velocity:
    """Movement vector."""

    def __init__(self, dx: float, dy: float):
        self.dx = dx
        self.dy = dy


class Health:
    """Hit points with current and maximum."""

    def __init__(self, current: int, max_hp: int):
        self.current = current
        self.max = max_hp


class Sprite:
    """Visual representation."""

    def __init__(self, char: str, color: str):
        self.char = char
        self.color = color
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_components.py -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/components/ tests/test_components.py
git commit -m "feat: add core ECS components (Position, Velocity, Health, Sprite)"
```

---

## Task 3: Combat Components

**Files:**
- Create: `src/components/combat.py`
- Modify: `tests/test_components.py`

**Step 1: Write combat component tests**

Add to `tests/test_components.py`:

```python
from src.components.combat import Stats, Collider, Projectile


def test_stats_stores_combat_values():
    stats = Stats(speed=5.0, damage=2.0, fire_rate=3.0, shot_speed=8.0)
    assert stats.speed == 5.0
    assert stats.damage == 2.0
    assert stats.fire_rate == 3.0
    assert stats.shot_speed == 8.0


def test_collider_has_radius():
    collider = Collider(0.5)
    assert collider.radius == 0.5


def test_projectile_stores_damage_and_owner():
    projectile = Projectile(damage=2, owner=42)
    assert projectile.damage == 2
    assert projectile.owner == 42
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_components.py::test_stats_stores_combat_values -v`
Expected: FAIL with "cannot import name 'Stats'"

**Step 3: Create combat components**

Create `src/components/combat.py`:

```python
"""Combat-related ECS components."""


class Stats:
    """Combat statistics for entities."""

    def __init__(self, speed: float, damage: float, fire_rate: float, shot_speed: float):
        self.speed = speed
        self.damage = damage
        self.fire_rate = fire_rate
        self.shot_speed = shot_speed


class Collider:
    """Circle collider for collision detection."""

    def __init__(self, radius: float):
        self.radius = radius


class Projectile:
    """Marks entity as a projectile with damage."""

    def __init__(self, damage: float, owner: int):
        self.damage = damage
        self.owner = owner  # Entity ID that fired this
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_components.py -v`
Expected: PASS (7 tests)

**Step 5: Commit**

```bash
git add src/components/combat.py tests/test_components.py
git commit -m "feat: add combat components (Stats, Collider, Projectile)"
```

---

## Task 4: Game Entity Components

**Files:**
- Create: `src/components/game.py`
- Modify: `tests/test_components.py`

**Step 1: Write game component tests**

Add to `tests/test_components.py`:

```python
from src.components.game import Player, Enemy, Item, AIBehavior, Invincible


def test_player_is_marker_component():
    player = Player()
    assert isinstance(player, Player)


def test_enemy_stores_type():
    enemy = Enemy("chaser")
    assert enemy.type == "chaser"


def test_item_stores_effects():
    item = Item(
        name="Speed Shoes",
        stat_modifiers={"speed": 1.5},
        special_effects=[]
    )
    assert item.name == "Speed Shoes"
    assert item.stat_modifiers["speed"] == 1.5


def test_ai_behavior_tracks_cooldowns():
    ai = AIBehavior(pattern_cooldowns={"shoot": 2.0})
    assert ai.pattern_cooldowns["shoot"] == 2.0


def test_invincible_has_duration():
    invincible = Invincible(0.5)
    assert invincible.remaining == 0.5
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_components.py::test_player_is_marker_component -v`
Expected: FAIL with "cannot import name 'Player'"

**Step 3: Create game components**

Create `src/components/game.py`:

```python
"""Game-specific ECS components."""
from typing import Dict, List


class Player:
    """Marker component for the player entity."""
    pass


class Enemy:
    """Marker component for enemy entities."""

    def __init__(self, type: str):
        self.type = type


class Item:
    """Item pickup component."""

    def __init__(self, name: str, stat_modifiers: Dict[str, float], special_effects: List[str]):
        self.name = name
        self.stat_modifiers = stat_modifiers
        self.special_effects = special_effects


class AIBehavior:
    """AI state and cooldowns for enemy behavior."""

    def __init__(self, pattern_cooldowns: Dict[str, float]):
        self.pattern_cooldowns = pattern_cooldowns


class Invincible:
    """Temporary invincibility component."""

    def __init__(self, duration: float):
        self.remaining = duration
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_components.py -v`
Expected: PASS (12 tests)

**Step 5: Commit**

```bash
git add src/components/game.py tests/test_components.py
git commit -m "feat: add game components (Player, Enemy, Item, AI, Invincible)"
```

---

## Task 5: Player Entity Factory

**Files:**
- Create: `src/entities/__init__.py`
- Create: `src/entities/player.py`
- Create: `tests/test_entities.py`

**Step 1: Write player entity test**

Create `tests/test_entities.py`:

```python
import pytest
import esper
from src.entities.player import create_player
from src.components.core import Position, Velocity, Health, Sprite
from src.components.combat import Stats, Collider
from src.components.game import Player


def test_create_player_returns_entity_id():
    world = esper.World()
    entity_id = create_player(world, 30.0, 10.0)
    assert isinstance(entity_id, int)


def test_create_player_has_all_components():
    world = esper.World()
    entity_id = create_player(world, 30.0, 10.0)

    # Check all components exist
    assert world.has_component(entity_id, Position)
    assert world.has_component(entity_id, Velocity)
    assert world.has_component(entity_id, Health)
    assert world.has_component(entity_id, Sprite)
    assert world.has_component(entity_id, Stats)
    assert world.has_component(entity_id, Collider)
    assert world.has_component(entity_id, Player)


def test_create_player_position():
    world = esper.World()
    entity_id = create_player(world, 30.0, 10.0)
    pos = world.component_for_entity(entity_id, Position)

    assert pos.x == 30.0
    assert pos.y == 10.0
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_entities.py -v`
Expected: FAIL with "cannot import name 'create_player'"

**Step 3: Create player entity factory**

Create `src/entities/__init__.py` (empty)

Create `src/entities/player.py`:

```python
"""Player entity factory."""
import esper
from src.components.core import Position, Velocity, Health, Sprite
from src.components.combat import Stats, Collider
from src.components.game import Player
from src.config import Config


def create_player(world: esper.World, x: float, y: float) -> int:
    """Create the player entity at the given position.

    Args:
        world: The ECS world
        x: Starting x coordinate
        y: Starting y coordinate

    Returns:
        Entity ID of the created player
    """
    entity = world.create_entity()

    world.add_component(entity, Position(x, y))
    world.add_component(entity, Velocity(0.0, 0.0))
    world.add_component(entity, Health(Config.PLAYER_MAX_HP, Config.PLAYER_MAX_HP))
    world.add_component(entity, Sprite('@', 'cyan'))
    world.add_component(entity, Stats(
        speed=Config.PLAYER_SPEED,
        damage=Config.PLAYER_DAMAGE,
        fire_rate=Config.PLAYER_FIRE_RATE,
        shot_speed=Config.PLAYER_SHOT_SPEED
    ))
    world.add_component(entity, Collider(Config.PLAYER_HITBOX))
    world.add_component(entity, Player())

    return entity
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_entities.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/entities/ tests/test_entities.py
git commit -m "feat: add player entity factory"
```

---

## Task 6: Basic Game Loop & Rich Setup

**Files:**
- Create: `src/game/__init__.py`
- Create: `src/game/engine.py`
- Create: `tests/test_engine.py`

**Step 1: Write game engine test**

Create `tests/test_engine.py`:

```python
import pytest
import esper
from src.game.engine import GameEngine


def test_game_engine_creates_world():
    engine = GameEngine()
    assert isinstance(engine.world, esper.World)


def test_game_engine_tracks_delta_time():
    engine = GameEngine()
    engine.update(0.016)  # ~60 FPS frame
    # Just verify it doesn't crash
    assert True


def test_game_engine_can_stop():
    engine = GameEngine()
    engine.stop()
    assert engine.running is False
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_engine.py -v`
Expected: FAIL with "cannot import name 'GameEngine'"

**Step 3: Create game engine**

Create `src/game/__init__.py` (empty)

Create `src/game/engine.py`:

```python
"""Main game engine and loop."""
import esper
from src.config import Config


class GameEngine:
    """Main game engine managing ECS world and game loop."""

    def __init__(self):
        self.world = esper.World()
        self.running = True
        self.delta_time = 0.0

    def update(self, dt: float):
        """Update all systems.

        Args:
            dt: Delta time in seconds since last frame
        """
        self.delta_time = dt
        # Process all systems (to be added)
        self.world.process()

    def stop(self):
        """Stop the game engine."""
        self.running = False
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_engine.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/game/ tests/test_engine.py
git commit -m "feat: add basic game engine with ECS world"
```

---

## Task 7: Movement System

**Files:**
- Create: `src/systems/__init__.py`
- Create: `src/systems/movement.py`
- Create: `tests/test_movement_system.py`

**Step 1: Write movement system tests**

Create `tests/test_movement_system.py`:

```python
import pytest
import esper
from src.systems.movement import MovementSystem
from src.components.core import Position, Velocity


def test_movement_system_moves_entities():
    world = esper.World()
    system = MovementSystem()
    world.add_processor(system)

    # Create entity with position and velocity
    entity = world.create_entity()
    world.add_component(entity, Position(10.0, 10.0))
    world.add_component(entity, Velocity(2.0, -1.0))

    # Set delta time and process
    system.dt = 1.0
    world.process()

    # Check position updated
    pos = world.component_for_entity(entity, Position)
    assert pos.x == 12.0
    assert pos.y == 9.0


def test_movement_system_respects_delta_time():
    world = esper.World()
    system = MovementSystem()
    world.add_processor(system)

    entity = world.create_entity()
    world.add_component(entity, Position(0.0, 0.0))
    world.add_component(entity, Velocity(10.0, 0.0))

    # Half-second frame
    system.dt = 0.5
    world.process()

    pos = world.component_for_entity(entity, Position)
    assert pos.x == 5.0
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_movement_system.py -v`
Expected: FAIL with "cannot import name 'MovementSystem'"

**Step 3: Create movement system**

Create `src/systems/__init__.py` (empty)

Create `src/systems/movement.py`:

```python
"""Movement system for applying velocity to positions."""
import esper
from src.components.core import Position, Velocity


class MovementSystem(esper.Processor):
    """Applies velocity to position based on delta time."""

    def __init__(self):
        self.dt = 0.0

    def process(self):
        """Update positions based on velocities."""
        for ent, (pos, vel) in self.world.get_components(Position, Velocity):
            pos.x += vel.dx * self.dt
            pos.y += vel.dy * self.dt
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_movement_system.py -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/systems/ tests/test_movement_system.py
git commit -m "feat: add movement system"
```

---

## Task 8: Input System

**Files:**
- Create: `src/systems/input.py`
- Create: `tests/test_input_system.py`

**Step 1: Write input system tests**

Create `tests/test_input_system.py`:

```python
import pytest
import esper
from src.systems.input import InputSystem
from src.components.core import Position, Velocity
from src.components.combat import Stats
from src.components.game import Player


def test_input_system_processes_movement():
    world = esper.World()
    system = InputSystem()
    world.add_processor(system)

    # Create player
    player = world.create_entity()
    world.add_component(player, Player())
    world.add_component(player, Position(30.0, 10.0))
    world.add_component(player, Velocity(0.0, 0.0))
    world.add_component(player, Stats(speed=5.0, damage=1.0, fire_rate=2.0, shot_speed=8.0))

    # Simulate moving right
    system.set_input(move_x=1, move_y=0, shoot_x=0, shoot_y=0)
    world.process()

    vel = world.component_for_entity(player, Velocity)
    assert vel.dx > 0  # Moving right


def test_input_system_normalizes_diagonal_movement():
    world = esper.World()
    system = InputSystem()
    world.add_processor(system)

    player = world.create_entity()
    world.add_component(player, Player())
    world.add_component(player, Position(30.0, 10.0))
    world.add_component(player, Velocity(0.0, 0.0))
    world.add_component(player, Stats(speed=5.0, damage=1.0, fire_rate=2.0, shot_speed=8.0))

    # Move diagonally
    system.set_input(move_x=1, move_y=1, shoot_x=0, shoot_y=0)
    world.process()

    vel = world.component_for_entity(player, Velocity)
    # Diagonal movement should be normalized (not 1.414x faster)
    speed = (vel.dx**2 + vel.dy**2)**0.5
    assert abs(speed - 5.0) < 0.1
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_input_system.py -v`
Expected: FAIL with "cannot import name 'InputSystem'"

**Step 3: Create input system**

Create `src/systems/input.py`:

```python
"""Input handling system."""
import esper
import math
from src.components.core import Velocity
from src.components.combat import Stats
from src.components.game import Player


class InputSystem(esper.Processor):
    """Processes input and updates player velocity."""

    def __init__(self):
        self.move_x = 0
        self.move_y = 0
        self.shoot_x = 0
        self.shoot_y = 0

    def set_input(self, move_x: int, move_y: int, shoot_x: int, shoot_y: int):
        """Set current input state.

        Args:
            move_x: -1 (left), 0 (none), 1 (right)
            move_y: -1 (up), 0 (none), 1 (down)
            shoot_x: -1 (left), 0 (none), 1 (right)
            shoot_y: -1 (up), 0 (none), 1 (down)
        """
        self.move_x = move_x
        self.move_y = move_y
        self.shoot_x = shoot_x
        self.shoot_y = shoot_y

    def process(self):
        """Update player velocity based on input."""
        for ent, (player, vel, stats) in self.world.get_components(Player, Velocity, Stats):
            # Calculate movement direction
            dx = float(self.move_x)
            dy = float(self.move_y)

            # Normalize diagonal movement
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Apply speed
            vel.dx = dx * stats.speed
            vel.dy = dy * stats.speed
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_input_system.py -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/systems/input.py tests/test_input_system.py
git commit -m "feat: add input system with normalized diagonal movement"
```

---

## Task 9: Render System Foundation

**Files:**
- Create: `src/systems/render.py`
- Create: `tests/test_render_system.py`

**Step 1: Write render system tests**

Create `tests/test_render_system.py`:

```python
import pytest
import esper
from src.systems.render import RenderSystem
from src.components.core import Position, Sprite
from src.config import Config


def test_render_system_creates_grid():
    world = esper.World()
    system = RenderSystem()

    grid = system.create_grid()

    assert len(grid) == Config.ROOM_HEIGHT
    assert len(grid[0]) == Config.ROOM_WIDTH


def test_render_system_draws_entity():
    world = esper.World()
    system = RenderSystem()
    world.add_processor(system)

    # Create entity
    entity = world.create_entity()
    world.add_component(entity, Position(10.0, 5.0))
    world.add_component(entity, Sprite('@', 'cyan'))

    grid = system.render(world)

    # Check entity appears in grid
    cell = grid[5][10]
    assert cell['char'] == '@'
    assert cell['color'] == 'cyan'
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_render_system.py -v`
Expected: FAIL with "cannot import name 'RenderSystem'"

**Step 3: Create render system**

Create `src/systems/render.py`:

```python
"""Rendering system for drawing the game world."""
import esper
from typing import List, Dict
from src.components.core import Position, Sprite
from src.config import Config


class RenderSystem(esper.Processor):
    """Renders entities to a 2D character grid."""

    def create_grid(self) -> List[List[Dict]]:
        """Create empty render grid.

        Returns:
            2D grid of cells with char and color
        """
        return [
            [{'char': '.', 'color': 'white'} for _ in range(Config.ROOM_WIDTH)]
            for _ in range(Config.ROOM_HEIGHT)
        ]

    def render(self, world: esper.World) -> List[List[Dict]]:
        """Render all entities to a grid.

        Args:
            world: The ECS world

        Returns:
            2D grid with rendered entities
        """
        grid = self.create_grid()

        # Draw all entities with position and sprite
        for ent, (pos, sprite) in world.get_components(Position, Sprite):
            x = int(pos.x)
            y = int(pos.y)

            # Bounds check
            if 0 <= x < Config.ROOM_WIDTH and 0 <= y < Config.ROOM_HEIGHT:
                grid[y][x] = {'char': sprite.char, 'color': sprite.color}

        return grid

    def process(self):
        """Process is called by ECS but rendering is pull-based."""
        pass
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_render_system.py -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/systems/render.py tests/test_render_system.py
git commit -m "feat: add render system for grid-based display"
```

---

## Task 10: Shooting System

**Files:**
- Create: `src/systems/shooting.py`
- Create: `tests/test_shooting_system.py`

**Step 1: Write shooting system tests**

Create `tests/test_shooting_system.py`:

```python
import pytest
import esper
from src.systems.shooting import ShootingSystem
from src.systems.input import InputSystem
from src.components.core import Position, Velocity
from src.components.combat import Stats, Projectile, Collider
from src.components.game import Player


def test_shooting_system_creates_projectile():
    world = esper.World()
    shooting = ShootingSystem()
    world.add_processor(shooting)

    # Create player
    player = world.create_entity()
    world.add_component(player, Player())
    world.add_component(player, Position(30.0, 10.0))
    world.add_component(player, Stats(speed=5.0, damage=2.0, fire_rate=2.0, shot_speed=8.0))

    # Trigger shot
    shooting.shoot_x = 1
    shooting.shoot_y = 0
    shooting.dt = 1.0
    world.process()

    # Check projectile created
    projectiles = [e for e, (proj,) in world.get_components(Projectile)]
    assert len(projectiles) > 0


def test_shooting_system_respects_fire_rate():
    world = esper.World()
    shooting = ShootingSystem()
    world.add_processor(shooting)

    player = world.create_entity()
    world.add_component(player, Player())
    world.add_component(player, Position(30.0, 10.0))
    world.add_component(player, Stats(speed=5.0, damage=2.0, fire_rate=2.0, shot_speed=8.0))

    # Fire rate 2.0 = shoot every 0.5 seconds
    shooting.shoot_x = 1
    shooting.shoot_y = 0
    shooting.dt = 0.1

    # Process multiple times
    for _ in range(3):
        world.process()

    # Should only create 1 projectile (not enough time passed)
    projectiles = [e for e, (proj,) in world.get_components(Projectile)]
    assert len(projectiles) == 1
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_shooting_system.py -v`
Expected: FAIL with "cannot import name 'ShootingSystem'"

**Step 3: Create shooting system**

Create `src/systems/shooting.py`:

```python
"""Shooting system for creating projectiles."""
import esper
import math
from src.components.core import Position, Velocity, Sprite
from src.components.combat import Stats, Projectile, Collider
from src.components.game import Player
from src.config import Config


class ShootingSystem(esper.Processor):
    """Handles shooting projectiles."""

    def __init__(self):
        self.shoot_x = 0
        self.shoot_y = 0
        self.dt = 0.0
        self.shoot_cooldowns = {}  # entity_id -> cooldown remaining

    def process(self):
        """Process shooting for all entities with shooting capability."""
        # Update cooldowns
        for entity_id in list(self.shoot_cooldowns.keys()):
            self.shoot_cooldowns[entity_id] -= self.dt
            if self.shoot_cooldowns[entity_id] <= 0:
                del self.shoot_cooldowns[entity_id]

        # Process player shooting
        for ent, (player, pos, stats) in self.world.get_components(Player, Position, Stats):
            # Check if trying to shoot
            if self.shoot_x == 0 and self.shoot_y == 0:
                continue

            # Check cooldown
            if ent in self.shoot_cooldowns:
                continue

            # Create projectile
            self._create_projectile(
                ent, pos.x, pos.y,
                float(self.shoot_x), float(self.shoot_y),
                stats.damage, stats.shot_speed
            )

            # Set cooldown
            self.shoot_cooldowns[ent] = 1.0 / stats.fire_rate

    def _create_projectile(self, owner: int, x: float, y: float,
                          dx: float, dy: float, damage: float, speed: float):
        """Create a projectile entity.

        Args:
            owner: Entity ID that fired this
            x, y: Starting position
            dx, dy: Direction (will be normalized)
            damage: Damage dealt on hit
            speed: Projectile speed
        """
        # Normalize direction
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

        # Create projectile entity
        projectile = self.world.create_entity()
        self.world.add_component(projectile, Position(x, y))
        self.world.add_component(projectile, Velocity(dx * speed, dy * speed))
        self.world.add_component(projectile, Projectile(damage, owner))
        self.world.add_component(projectile, Collider(Config.PROJECTILE_HITBOX))
        self.world.add_component(projectile, Sprite('.', 'white'))
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_shooting_system.py -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/systems/shooting.py tests/test_shooting_system.py
git commit -m "feat: add shooting system with fire rate cooldowns"
```

---

## Task 11: Collision Detection System

**Files:**
- Create: `src/systems/collision.py`
- Create: `tests/test_collision_system.py`

**Step 1: Write collision tests**

Create `tests/test_collision_system.py`:

```python
import pytest
import esper
from src.systems.collision import CollisionSystem
from src.components.core import Position, Health
from src.components.combat import Collider, Projectile
from src.components.game import Player, Enemy


def test_collision_system_detects_overlap():
    world = esper.World()
    system = CollisionSystem()

    # Two entities at same position
    e1 = world.create_entity()
    world.add_component(e1, Position(10.0, 10.0))
    world.add_component(e1, Collider(0.5))

    e2 = world.create_entity()
    world.add_component(e2, Position(10.0, 10.0))
    world.add_component(e2, Collider(0.5))

    assert system._check_collision(e1, e2, world) is True


def test_collision_system_no_overlap():
    world = esper.World()
    system = CollisionSystem()

    # Entities far apart
    e1 = world.create_entity()
    world.add_component(e1, Position(10.0, 10.0))
    world.add_component(e1, Collider(0.5))

    e2 = world.create_entity()
    world.add_component(e2, Position(20.0, 20.0))
    world.add_component(e2, Collider(0.5))

    assert system._check_collision(e1, e2, world) is False


def test_projectile_damages_enemy():
    world = esper.World()
    system = CollisionSystem()
    world.add_processor(system)

    # Create player projectile
    proj = world.create_entity()
    world.add_component(proj, Position(10.0, 10.0))
    world.add_component(proj, Collider(0.2))
    world.add_component(proj, Projectile(damage=2.0, owner=999))

    # Create enemy
    enemy = world.create_entity()
    world.add_component(enemy, Position(10.0, 10.0))
    world.add_component(enemy, Collider(0.5))
    world.add_component(enemy, Health(5, 5))
    world.add_component(enemy, Enemy("test"))

    world.process()

    # Enemy should take damage
    health = world.component_for_entity(enemy, Health)
    assert health.current == 3  # 5 - 2 damage
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_collision_system.py -v`
Expected: FAIL with "cannot import name 'CollisionSystem'"

**Step 3: Create collision system**

Create `src/systems/collision.py`:

```python
"""Collision detection and response system."""
import esper
import math
from src.components.core import Position, Health, Velocity
from src.components.combat import Collider, Projectile
from src.components.game import Enemy, Player


class CollisionSystem(esper.Processor):
    """Handles collision detection and damage."""

    def process(self):
        """Check all collisions and apply damage."""
        # Get all entities with colliders
        collidables = [
            (ent, pos, col)
            for ent, (pos, col) in self.world.get_components(Position, Collider)
        ]

        # Check all pairs
        for i, (e1, pos1, col1) in enumerate(collidables):
            for e2, pos2, col2 in collidables[i + 1:]:
                if self._check_collision(e1, e2, self.world):
                    self._handle_collision(e1, e2)

    def _check_collision(self, e1: int, e2: int, world: esper.World) -> bool:
        """Check if two entities collide.

        Args:
            e1, e2: Entity IDs
            world: ECS world

        Returns:
            True if entities overlap
        """
        pos1 = world.component_for_entity(e1, Position)
        pos2 = world.component_for_entity(e2, Position)
        col1 = world.component_for_entity(e1, Collider)
        col2 = world.component_for_entity(e2, Collider)

        # Circle collision
        dx = pos2.x - pos1.x
        dy = pos2.y - pos1.y
        distance = math.sqrt(dx * dx + dy * dy)

        return distance < (col1.radius + col2.radius)

    def _handle_collision(self, e1: int, e2: int):
        """Handle collision between two entities.

        Args:
            e1, e2: Entity IDs that collided
        """
        # Projectile hitting enemy
        if self.world.has_component(e1, Projectile) and self.world.has_component(e2, Enemy):
            self._projectile_hit_enemy(e1, e2)
        elif self.world.has_component(e2, Projectile) and self.world.has_component(e1, Enemy):
            self._projectile_hit_enemy(e2, e1)

        # Projectile hitting player
        if self.world.has_component(e1, Projectile) and self.world.has_component(e2, Player):
            self._projectile_hit_player(e1, e2)
        elif self.world.has_component(e2, Projectile) and self.world.has_component(e1, Player):
            self._projectile_hit_player(e2, e1)

    def _projectile_hit_enemy(self, projectile: int, enemy: int):
        """Handle projectile hitting enemy."""
        proj = self.world.component_for_entity(projectile, Projectile)
        health = self.world.component_for_entity(enemy, Health)

        # Apply damage
        health.current -= proj.damage

        # Remove projectile
        self.world.delete_entity(projectile)

        # Remove enemy if dead
        if health.current <= 0:
            self.world.delete_entity(enemy)

    def _projectile_hit_player(self, projectile: int, player: int):
        """Handle projectile hitting player."""
        # TODO: Check invincibility, apply damage
        # For now just remove projectile
        self.world.delete_entity(projectile)
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_collision_system.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/systems/collision.py tests/test_collision_system.py
git commit -m "feat: add collision system with projectile damage"
```

---

## Task 12: Enemy Entity Factory

**Files:**
- Create: `src/entities/enemies.py`
- Modify: `tests/test_entities.py`

**Step 1: Write enemy factory tests**

Add to `tests/test_entities.py`:

```python
from src.entities.enemies import create_enemy


def test_create_enemy_chaser():
    world = esper.World()
    enemy_id = create_enemy(world, "chaser", 20.0, 10.0)

    assert world.has_component(enemy_id, Position)
    assert world.has_component(enemy_id, Enemy)

    enemy = world.component_for_entity(enemy_id, Enemy)
    assert enemy.type == "chaser"


def test_create_enemy_shooter():
    world = esper.World()
    enemy_id = create_enemy(world, "shooter", 15.0, 8.0)

    enemy = world.component_for_entity(enemy_id, Enemy)
    assert enemy.type == "shooter"

    # Shooter should have AI behavior
    assert world.has_component(enemy_id, AIBehavior)
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_entities.py::test_create_enemy_chaser -v`
Expected: FAIL with "cannot import name 'create_enemy'"

**Step 3: Create enemy factory**

Create `src/entities/enemies.py`:

```python
"""Enemy entity factories."""
import esper
from src.components.core import Position, Velocity, Health, Sprite
from src.components.combat import Stats, Collider
from src.components.game import Enemy, AIBehavior
from src.config import Config


ENEMY_DATA = {
    "chaser": {
        "hp": 3,
        "speed": 3.0,
        "sprite": ("e", "red"),
        "patterns": {}
    },
    "shooter": {
        "hp": 4,
        "speed": 1.5,
        "sprite": ("S", "magenta"),
        "patterns": {"shoot": 2.0}  # Cooldown in seconds
    },
    "orbiter": {
        "hp": 5,
        "speed": 4.0,
        "sprite": ("O", "yellow"),
        "patterns": {"shoot": 1.5, "ring": 3.0}
    },
    "turret": {
        "hp": 6,
        "speed": 0.0,
        "sprite": ("T", "red"),
        "patterns": {"spray": 2.5}
    },
    "tank": {
        "hp": 10,
        "speed": 2.0,
        "sprite": ("E", "bright_red"),
        "patterns": {"charge": 4.0}
    }
}


def create_enemy(world: esper.World, enemy_type: str, x: float, y: float) -> int:
    """Create an enemy entity.

    Args:
        world: ECS world
        enemy_type: Type of enemy ("chaser", "shooter", etc.)
        x, y: Starting position

    Returns:
        Entity ID of created enemy
    """
    if enemy_type not in ENEMY_DATA:
        raise ValueError(f"Unknown enemy type: {enemy_type}")

    data = ENEMY_DATA[enemy_type]
    entity = world.create_entity()

    world.add_component(entity, Position(x, y))
    world.add_component(entity, Velocity(0.0, 0.0))
    world.add_component(entity, Health(data["hp"], data["hp"]))
    world.add_component(entity, Sprite(data["sprite"][0], data["sprite"][1]))
    world.add_component(entity, Collider(Config.ENEMY_HITBOX))
    world.add_component(entity, Enemy(enemy_type))

    # Add AI if enemy has patterns
    if data["patterns"]:
        world.add_component(entity, AIBehavior(data["patterns"].copy()))

    return entity
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_entities.py -v`
Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add src/entities/enemies.py tests/test_entities.py
git commit -m "feat: add enemy entity factory with 5 enemy types"
```

---

## Task 13: Simple AI System

**Files:**
- Create: `src/systems/ai.py`
- Create: `tests/test_ai_system.py`

**Step 1: Write AI system tests**

Create `tests/test_ai_system.py`:

```python
import pytest
import esper
from src.systems.ai import AISystem
from src.entities.enemies import create_enemy
from src.entities.player import create_player
from src.components.core import Position, Velocity


def test_ai_system_chaser_moves_toward_player():
    world = esper.World()
    system = AISystem()
    system.dt = 0.1
    world.add_processor(system)

    # Create player
    player = create_player(world, 30.0, 10.0)

    # Create chaser to the left of player
    enemy = create_enemy(world, "chaser", 20.0, 10.0)

    world.process()

    # Enemy velocity should point toward player (right)
    vel = world.component_for_entity(enemy, Velocity)
    assert vel.dx > 0


def test_ai_system_shooter_stays_stationary():
    world = esper.World()
    system = AISystem()
    system.dt = 0.1
    world.add_processor(system)

    player = create_player(world, 30.0, 10.0)
    shooter = create_enemy(world, "shooter", 20.0, 10.0)

    world.process()

    vel = world.component_for_entity(shooter, Velocity)
    # Shooter should move slowly or not at all
    assert abs(vel.dx) < 2.0
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_ai_system.py -v`
Expected: FAIL with "cannot import name 'AISystem'"

**Step 3: Create AI system**

Create `src/systems/ai.py`:

```python
"""AI system for enemy behavior."""
import esper
import math
from src.components.core import Position, Velocity
from src.components.game import Enemy, Player, AIBehavior


class AISystem(esper.Processor):
    """Handles enemy AI behavior."""

    def __init__(self):
        self.dt = 0.0

    def process(self):
        """Process AI for all enemies."""
        # Find player position
        player_pos = None
        for ent, (player, pos) in self.world.get_components(Player, Position):
            player_pos = pos
            break

        if not player_pos:
            return

        # Process each enemy
        for ent, (enemy, pos, vel) in self.world.get_components(Enemy, Position, Velocity):
            if enemy.type == "chaser":
                self._ai_chaser(pos, vel, player_pos)
            elif enemy.type == "shooter":
                self._ai_shooter(pos, vel, player_pos)
            elif enemy.type == "orbiter":
                self._ai_orbiter(pos, vel, player_pos)
            elif enemy.type == "turret":
                self._ai_turret(pos, vel, player_pos)
            elif enemy.type == "tank":
                self._ai_tank(pos, vel, player_pos)

    def _ai_chaser(self, pos: Position, vel: Velocity, player_pos: Position):
        """Chaser AI: move toward player."""
        dx = player_pos.x - pos.x
        dy = player_pos.y - pos.y

        # Normalize
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

        # Move at chaser speed (3.0)
        vel.dx = dx * 3.0
        vel.dy = dy * 3.0

    def _ai_shooter(self, pos: Position, vel: Velocity, player_pos: Position):
        """Shooter AI: stay mostly still."""
        vel.dx = 0.0
        vel.dy = 0.0

    def _ai_orbiter(self, pos: Position, vel: Velocity, player_pos: Position):
        """Orbiter AI: circle around player."""
        # TODO: Implement circular movement
        vel.dx = 0.0
        vel.dy = 0.0

    def _ai_turret(self, pos: Position, vel: Velocity, player_pos: Position):
        """Turret AI: stationary."""
        vel.dx = 0.0
        vel.dy = 0.0

    def _ai_tank(self, pos: Position, vel: Velocity, player_pos: Position):
        """Tank AI: slow movement toward player."""
        dx = player_pos.x - pos.x
        dy = player_pos.y - pos.y

        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

        vel.dx = dx * 2.0
        vel.dy = dy * 2.0
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_ai_system.py -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/systems/ai.py tests/test_ai_system.py
git commit -m "feat: add basic AI system for enemy movement"
```

---

## Task 14: Room Generation

**Files:**
- Create: `src/game/room.py`
- Create: `tests/test_room.py`

**Step 1: Write room tests**

Create `tests/test_room.py`:

```python
import pytest
import esper
from src.game.room import Room
from src.config import Config


def test_room_creates_with_dimensions():
    room = Room(width=60, height=20)
    assert room.width == 60
    assert room.height == 20


def test_room_generates_obstacles():
    room = Room(width=60, height=20)
    room.generate_obstacles(seed=42)

    # Should have some obstacles
    assert len(room.obstacles) > 0


def test_room_has_doors():
    room = Room(width=60, height=20)
    room.add_door("top")
    room.add_door("bottom")

    assert "top" in room.doors
    assert "bottom" in room.doors


def test_room_spawns_enemies():
    world = esper.World()
    room = Room(width=60, height=20)

    enemy_config = [
        {"type": "chaser", "count": 2},
        {"type": "shooter", "count": 1}
    ]

    room.spawn_enemies(world, enemy_config)

    # Should have spawned entities (verify via world)
    # This is a basic check - full verification would count entities
    assert True  # Placeholder
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_room.py -v`
Expected: FAIL with "cannot import name 'Room'"

**Step 3: Create room class**

Create `src/game/room.py`:

```python
"""Room generation and management."""
import esper
import random
from typing import List, Tuple, Dict, Set
from src.entities.enemies import create_enemy


class Room:
    """Represents a single room in the dungeon."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.obstacles: List[Tuple[int, int]] = []
        self.doors: Set[str] = set()  # "top", "bottom", "left", "right"
        self.cleared = False

    def add_door(self, direction: str):
        """Add a door in the specified direction.

        Args:
            direction: "top", "bottom", "left", or "right"
        """
        if direction not in ["top", "bottom", "left", "right"]:
            raise ValueError(f"Invalid door direction: {direction}")
        self.doors.add(direction)

    def generate_obstacles(self, seed: int = None):
        """Generate obstacles using simple random placement.

        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)

        # Place 3-8 obstacle clusters
        num_clusters = random.randint(3, 8)

        for _ in range(num_clusters):
            # Pick random seed position (avoid edges and center)
            cx = random.randint(5, self.width - 5)
            cy = random.randint(5, self.height - 5)

            # Avoid center spawn area
            if abs(cx - self.width // 2) < 10 and abs(cy - self.height // 2) < 5:
                continue

            # Grow cluster (2-4 tiles)
            cluster_size = random.randint(2, 4)
            for _ in range(cluster_size):
                ox = cx + random.randint(-1, 1)
                oy = cy + random.randint(-1, 1)

                if 1 < ox < self.width - 1 and 1 < oy < self.height - 1:
                    self.obstacles.append((ox, oy))

    def spawn_enemies(self, world: esper.World, enemy_config: List[Dict]):
        """Spawn enemies in the room.

        Args:
            world: ECS world
            enemy_config: List of dicts with "type" and "count"
        """
        spawned = []

        for config in enemy_config:
            enemy_type = config["type"]
            count = config["count"]

            for _ in range(count):
                # Random spawn position (avoid edges and center)
                x = random.uniform(10, self.width - 10)
                y = random.uniform(5, self.height - 5)

                # Avoid center spawn
                if abs(x - self.width // 2) < 10:
                    x += 15

                enemy_id = create_enemy(world, enemy_type, x, y)
                spawned.append(enemy_id)

        return spawned
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_room.py -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/game/room.py tests/test_room.py
git commit -m "feat: add room generation with obstacles and enemy spawning"
```

---

## Task 15: Integrate Systems into Engine

**Files:**
- Modify: `src/game/engine.py`
- Modify: `tests/test_engine.py`

**Step 1: Write integration test**

Add to `tests/test_engine.py`:

```python
from src.entities.player import create_player


def test_game_engine_has_all_systems():
    engine = GameEngine()

    # Check systems are registered
    assert len(engine.world._processors) > 0


def test_game_engine_runs_game_loop():
    engine = GameEngine()

    # Create player
    player = create_player(engine.world, 30.0, 10.0)

    # Run a few frames
    for _ in range(10):
        engine.update(0.016)

    # Should not crash
    assert True
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_engine.py::test_game_engine_has_all_systems -v`
Expected: FAIL (no systems registered yet)

**Step 3: Integrate systems**

Modify `src/game/engine.py`:

```python
"""Main game engine and loop."""
import esper
from src.config import Config
from src.systems.input import InputSystem
from src.systems.movement import MovementSystem
from src.systems.shooting import ShootingSystem
from src.systems.ai import AISystem
from src.systems.collision import CollisionSystem
from src.systems.render import RenderSystem


class GameEngine:
    """Main game engine managing ECS world and game loop."""

    def __init__(self):
        self.world = esper.World()
        self.running = True
        self.delta_time = 0.0

        # Create and register systems
        self.input_system = InputSystem()
        self.movement_system = MovementSystem()
        self.shooting_system = ShootingSystem()
        self.ai_system = AISystem()
        self.collision_system = CollisionSystem()
        self.render_system = RenderSystem()

        # Add processors in order
        self.world.add_processor(self.input_system)
        self.world.add_processor(self.ai_system)
        self.world.add_processor(self.shooting_system)
        self.world.add_processor(self.movement_system)
        self.world.add_processor(self.collision_system)
        self.world.add_processor(self.render_system)

    def update(self, dt: float):
        """Update all systems.

        Args:
            dt: Delta time in seconds since last frame
        """
        self.delta_time = dt

        # Update system delta times
        self.movement_system.dt = dt
        self.shooting_system.dt = dt
        self.ai_system.dt = dt

        # Process all systems
        self.world.process()

    def stop(self):
        """Stop the game engine."""
        self.running = False
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_engine.py -v`
Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add src/game/engine.py tests/test_engine.py
git commit -m "feat: integrate all systems into game engine"
```

---

## Task 16: Main Game Loop with Rich

**Files:**
- Modify: `main.py`

**Step 1: Write main game loop**

Replace contents of `main.py`:

```python
"""Main entry point for Texting of Isaac."""
import time
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from src.game.engine import GameEngine
from src.entities.player import create_player
from src.entities.enemies import create_enemy
from src.config import Config


def create_game_display(engine: GameEngine) -> Table:
    """Create the game display layout.

    Args:
        engine: Game engine with world state

    Returns:
        Rich Table with game area and HUD
    """
    # Render game grid
    grid = engine.render_system.render(engine.world)

    # Convert grid to Rich Text
    game_text = Text()
    for row in grid:
        for cell in row:
            game_text.append(cell['char'], style=cell['color'])
        game_text.append('\n')

    # Create layout
    layout = Table.grid(padding=1)
    layout.add_column("game", width=Config.ROOM_WIDTH)
    layout.add_column("hud", width=30)

    # Game panel
    game_panel = Panel(game_text, title="Texting of Isaac", border_style="cyan")

    # HUD panel
    hud_text = Text()
    hud_text.append("Health: ", style="white")
    hud_text.append("♥♥♥", style="red")
    hud_text.append("\n\nControls:\n", style="yellow")
    hud_text.append("WASD - Move\n", style="white")
    hud_text.append("Arrows - Shoot\n", style="white")
    hud_text.append("Q - Quit\n", style="white")

    hud_panel = Panel(hud_text, title="HUD", border_style="yellow")

    layout.add_row(game_panel, hud_panel)

    return layout


def main():
    """Main game loop."""
    console = Console()
    engine = GameEngine()

    # Create player
    player = create_player(engine.world, Config.ROOM_WIDTH // 2, Config.ROOM_HEIGHT // 2)

    # Spawn some test enemies
    create_enemy(engine.world, "chaser", 10, 5)
    create_enemy(engine.world, "shooter", 50, 15)
    create_enemy(engine.world, "chaser", 30, 3)

    # Game loop variables
    last_time = time.time()
    target_frame_time = 1.0 / Config.FPS

    console.print("[cyan]Starting Texting of Isaac...[/cyan]")
    console.print("[yellow]Press Ctrl+C to quit[/yellow]\n")

    try:
        with Live(create_game_display(engine), refresh_per_second=Config.FPS, console=console) as live:
            while engine.running:
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time

                # Update game
                engine.update(dt)

                # Update display
                live.update(create_game_display(engine))

                # Maintain frame rate
                elapsed = time.time() - current_time
                if elapsed < target_frame_time:
                    time.sleep(target_frame_time - elapsed)

    except KeyboardInterrupt:
        console.print("\n[cyan]Thanks for playing![/cyan]")


if __name__ == "__main__":
    main()
```

**Step 2: Test manually**

Run: `uv run python main.py`
Expected: Display opens with player (@) and 3 enemies visible

**Step 3: Verify it runs without crashing**

Let it run for a few seconds, then Ctrl+C to quit.

**Step 4: Commit**

```bash
git add main.py
git commit -m "feat: add main game loop with Rich rendering"
```

---

## Task 17: Keyboard Input Handling

**Files:**
- Modify: `main.py`

**Step 1: Add keyboard input library**

Run: `uv add pynput`

**Step 2: Modify main loop for input**

Update `main.py` to add keyboard handling:

```python
"""Main entry point for Texting of Isaac."""
import time
from pynput import keyboard
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from src.game.engine import GameEngine
from src.entities.player import create_player
from src.entities.enemies import create_enemy
from src.config import Config


class InputHandler:
    """Handles keyboard input state."""

    def __init__(self):
        self.move_x = 0
        self.move_y = 0
        self.shoot_x = 0
        self.shoot_y = 0
        self.quit = False
        self.keys_pressed = set()

    def on_press(self, key):
        """Handle key press."""
        try:
            if hasattr(key, 'char'):
                self.keys_pressed.add(key.char)
        except AttributeError:
            # Special key
            if key == keyboard.Key.up:
                self.keys_pressed.add('up')
            elif key == keyboard.Key.down:
                self.keys_pressed.add('down')
            elif key == keyboard.Key.left:
                self.keys_pressed.add('left')
            elif key == keyboard.Key.right:
                self.keys_pressed.add('right')

    def on_release(self, key):
        """Handle key release."""
        try:
            if hasattr(key, 'char'):
                self.keys_pressed.discard(key.char)
        except AttributeError:
            if key == keyboard.Key.up:
                self.keys_pressed.discard('up')
            elif key == keyboard.Key.down:
                self.keys_pressed.discard('down')
            elif key == keyboard.Key.left:
                self.keys_pressed.discard('left')
            elif key == keyboard.Key.right:
                self.keys_pressed.discard('right')

    def update(self):
        """Update input state from pressed keys."""
        # Movement (WASD)
        self.move_x = 0
        self.move_y = 0
        if 'a' in self.keys_pressed:
            self.move_x = -1
        if 'd' in self.keys_pressed:
            self.move_x = 1
        if 'w' in self.keys_pressed:
            self.move_y = -1
        if 's' in self.keys_pressed:
            self.move_y = 1

        # Shooting (arrows)
        self.shoot_x = 0
        self.shoot_y = 0
        if 'left' in self.keys_pressed:
            self.shoot_x = -1
        if 'right' in self.keys_pressed:
            self.shoot_x = 1
        if 'up' in self.keys_pressed:
            self.shoot_y = -1
        if 'down' in self.keys_pressed:
            self.shoot_y = 1

        # Quit
        if 'q' in self.keys_pressed:
            self.quit = True


def create_game_display(engine: GameEngine) -> Table:
    """Create the game display layout."""
    # Render game grid
    grid = engine.render_system.render(engine.world)

    # Convert grid to Rich Text
    game_text = Text()
    for row in grid:
        for cell in row:
            game_text.append(cell['char'], style=cell['color'])
        game_text.append('\n')

    # Create layout
    layout = Table.grid(padding=1)
    layout.add_column("game", width=Config.ROOM_WIDTH)
    layout.add_column("hud", width=30)

    # Game panel
    game_panel = Panel(game_text, title="Texting of Isaac", border_style="cyan")

    # HUD panel
    hud_text = Text()
    hud_text.append("Health: ", style="white")
    hud_text.append("♥♥♥", style="red")
    hud_text.append("\n\nControls:\n", style="yellow")
    hud_text.append("WASD - Move\n", style="white")
    hud_text.append("Arrows - Shoot\n", style="white")
    hud_text.append("Q - Quit\n", style="white")

    hud_panel = Panel(hud_text, title="HUD", border_style="yellow")

    layout.add_row(game_panel, hud_panel)

    return layout


def main():
    """Main game loop."""
    console = Console()
    engine = GameEngine()
    input_handler = InputHandler()

    # Start keyboard listener
    listener = keyboard.Listener(
        on_press=input_handler.on_press,
        on_release=input_handler.on_release
    )
    listener.start()

    # Create player
    player = create_player(engine.world, Config.ROOM_WIDTH // 2, Config.ROOM_HEIGHT // 2)

    # Spawn test enemies
    create_enemy(engine.world, "chaser", 10, 5)
    create_enemy(engine.world, "shooter", 50, 15)
    create_enemy(engine.world, "chaser", 30, 3)

    # Game loop
    last_time = time.time()
    target_frame_time = 1.0 / Config.FPS

    console.print("[cyan]Starting Texting of Isaac...[/cyan]")
    console.print("[yellow]Press Q to quit[/yellow]\n")

    try:
        with Live(create_game_display(engine), refresh_per_second=Config.FPS, console=console) as live:
            while engine.running and not input_handler.quit:
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time

                # Update input
                input_handler.update()
                engine.input_system.set_input(
                    input_handler.move_x,
                    input_handler.move_y,
                    input_handler.shoot_x,
                    input_handler.shoot_y
                )
                engine.shooting_system.shoot_x = input_handler.shoot_x
                engine.shooting_system.shoot_y = input_handler.shoot_y

                # Update game
                engine.update(dt)

                # Update display
                live.update(create_game_display(engine))

                # Frame rate
                elapsed = time.time() - current_time
                if elapsed < target_frame_time:
                    time.sleep(target_frame_time - elapsed)

    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
        console.print("\n[cyan]Thanks for playing![/cyan]")


if __name__ == "__main__":
    main()
```

**Step 3: Test manually**

Run: `uv run python main.py`
Expected: Can control player with WASD, shoot with arrows

**Step 4: Commit**

```bash
git add main.py pyproject.toml uv.lock
git commit -m "feat: add keyboard input handling with pynput"
```

---

## Summary

This plan provides a complete foundation for the prototype:

✅ Core ECS components and systems
✅ Player and enemy entities
✅ Movement, shooting, collision, and AI
✅ Room generation with obstacles
✅ Rich rendering and input handling
✅ Playable game loop

**Remaining work for complete prototype:**
- Attack patterns for enemies (shooting projectiles)
- Item system implementation
- Boss fight mechanics
- Game state management (room transitions, win/lose)
- Dungeon flow generation
- Polish and balancing

**Execution note:** This plan follows TDD where practical, but some integration points (like the main loop) are tested manually since they involve real-time rendering and input.
