# Player Damage System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable player to take damage from enemy projectiles and contact, with invincibility frames and visual feedback

**Architecture:** Add Dead marker component, create InvincibilitySystem to decrement timers, modify CollisionSystem to apply damage and grant invincibility, update RenderSystem to flash player sprite during invincibility

**Tech Stack:** Python 3.12, Esper ECS, Rich TUI, pytest

---

## Task 1: Add Dead Marker Component

**Files:**
- Modify: `src/components/game.py` (add Dead class after Invincible)
- Test: `tests/test_components.py`

**Step 1: Write failing test for Dead component**

```python
def test_dead_is_marker_component():
    """Test Dead component is a simple marker."""
    dead = Dead()
    assert repr(dead) == "Dead()"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_components.py::test_dead_is_marker_component -v`
Expected: FAIL with "NameError: name 'Dead' is not defined"

**Step 3: Implement Dead marker component**

In `src/components/game.py`, add after Invincible class:

```python
class Dead:
    """Marker component indicating entity has died."""

    def __repr__(self) -> str:
        return "Dead()"
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_components.py::test_dead_is_marker_component -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/components/game.py tests/test_components.py
git commit -m "feat: add Dead marker component

Simple marker to indicate entity death for game over detection.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Create InvincibilitySystem

**Files:**
- Create: `src/systems/invincibility.py`
- Test: `tests/test_invincibility_system.py`

**Step 1: Write failing tests for InvincibilitySystem**

Create `tests/test_invincibility_system.py`:

```python
"""Tests for invincibility system."""
import esper
import pytest
from src.systems.invincibility import InvincibilitySystem
from src.components.game import Invincible


def test_invincibility_system_decrements_timer():
    """Test InvincibilitySystem reduces remaining time."""
    esper.switch_world("test_invincibility")

    # Create entity with invincibility
    entity = esper.create_entity()
    esper.add_component(entity, Invincible(0.5))

    # Process system
    system = InvincibilitySystem()
    system.dt = 0.1
    esper.add_processor(system)
    esper.process()

    # Check timer decreased
    invincible = esper.component_for_entity(entity, Invincible)
    assert invincible.remaining == pytest.approx(0.4)


def test_invincibility_removed_when_expired():
    """Test Invincible component removed at 0."""
    esper.switch_world("test_invincibility_removal")

    entity = esper.create_entity()
    esper.add_component(entity, Invincible(0.05))

    system = InvincibilitySystem()
    system.dt = 0.1
    esper.add_processor(system)
    esper.process()

    # Component should be removed
    assert not esper.has_component(entity, Invincible)


def test_invincibility_system_handles_multiple_entities():
    """Test system handles multiple invincible entities."""
    esper.switch_world("test_invincibility_multiple")

    entity1 = esper.create_entity()
    esper.add_component(entity1, Invincible(0.5))

    entity2 = esper.create_entity()
    esper.add_component(entity2, Invincible(0.1))

    system = InvincibilitySystem()
    system.dt = 0.15
    esper.add_processor(system)
    esper.process()

    # Entity1 still invincible
    assert esper.has_component(entity1, Invincible)
    inv1 = esper.component_for_entity(entity1, Invincible)
    assert inv1.remaining == pytest.approx(0.35)

    # Entity2 no longer invincible
    assert not esper.has_component(entity2, Invincible)
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_invincibility_system.py -v`
Expected: FAIL with "No module named 'src.systems.invincibility'"

**Step 3: Implement InvincibilitySystem**

Create `src/systems/invincibility.py`:

```python
"""Invincibility system for managing invulnerability frames."""
import esper
from src.components.game import Invincible


class InvincibilitySystem(esper.Processor):
    """Decrements invincibility timers and removes expired invincibility."""

    def __init__(self):
        self.dt = 0.0

    def process(self):
        """Update all invincibility timers."""
        for ent, (invincible,) in esper.get_components(Invincible):
            invincible.remaining -= self.dt

            if invincible.remaining <= 0:
                esper.remove_component(ent, Invincible)
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_invincibility_system.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/systems/invincibility.py tests/test_invincibility_system.py
git commit -m "feat: create InvincibilitySystem

System decrements invincibility timers and removes expired invincibility.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Implement Projectile Damage to Player

**Files:**
- Modify: `src/systems/collision.py` (update _projectile_hit_player method)
- Test: `tests/test_collision_system.py`

**Step 1: Write failing tests for projectile damage**

Add to `tests/test_collision_system.py`:

```python
def test_projectile_damages_player():
    """Test enemy projectile reduces player health."""
    esper.switch_world("test_projectile_damage_player")

    # Create player with 3 HP
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(3, 6))
    esper.add_component(player, Collider(0.5))

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))
    esper.add_component(enemy, Position(5.0, 10.0))

    # Create enemy projectile at player position
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(10.0, 10.0))
    esper.add_component(projectile, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile, Collider(0.2))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify damage dealt
    health = esper.component_for_entity(player, Health)
    assert health.current == 2.0

    # Verify invincibility granted
    assert esper.has_component(player, Invincible)
    inv = esper.component_for_entity(player, Invincible)
    assert inv.remaining == pytest.approx(0.5)

    # Verify projectile removed
    assert not esper.entity_exists(projectile)


def test_projectile_respects_invincibility():
    """Test projectile doesn't damage invincible player."""
    esper.switch_world("test_projectile_invincibility")

    # Create invincible player with 3 HP
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(3, 6))
    esper.add_component(player, Collider(0.5))
    esper.add_component(player, Invincible(0.3))

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))

    # Create enemy projectile
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(10.0, 10.0))
    esper.add_component(projectile, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile, Collider(0.2))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify no damage dealt
    health = esper.component_for_entity(player, Health)
    assert health.current == 3.0

    # Verify projectile still removed
    assert not esper.entity_exists(projectile)
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_collision_system.py::test_projectile_damages_player tests/test_collision_system.py::test_projectile_respects_invincibility -v`
Expected: FAIL (health unchanged, no invincibility added)

**Step 3: Update _projectile_hit_player() implementation**

In `src/systems/collision.py`, replace the _projectile_hit_player method:

```python
def _projectile_hit_player(self, projectile: int, player: int):
    """Handle enemy projectile hitting player."""
    from src.components.game import Invincible, Dead
    from src.config import Config

    # Check invincibility
    if esper.has_component(player, Invincible):
        esper.delete_entity(projectile)  # Remove projectile but no damage
        return

    # Get projectile damage
    proj = esper.component_for_entity(projectile, Projectile)
    health = esper.component_for_entity(player, Health)

    # Apply damage
    health.current -= proj.damage

    # Add invincibility
    esper.add_component(player, Invincible(Config.INVINCIBILITY_DURATION))

    # Remove projectile
    esper.delete_entity(projectile)

    # Check for death
    if health.current <= 0:
        esper.add_component(player, Dead())
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_collision_system.py::test_projectile_damages_player tests/test_collision_system.py::test_projectile_respects_invincibility -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/systems/collision.py tests/test_collision_system.py
git commit -m "feat: implement projectile damage to player

Apply damage, grant invincibility, respect i-frames, handle death.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Implement Contact Damage from Enemies

**Files:**
- Modify: `src/systems/collision.py` (add _enemy_contact_player method and collision checks)
- Test: `tests/test_collision_system.py`

**Step 1: Write failing tests for contact damage**

Add to `tests/test_collision_system.py`:

```python
def test_enemy_contact_damages_player():
    """Test touching enemy deals 1 damage."""
    esper.switch_world("test_enemy_contact")

    # Create player with 3 HP
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(3, 6))
    esper.add_component(player, Collider(0.5))

    # Create enemy overlapping player
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("chaser"))
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, Collider(0.5))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify damage dealt
    health = esper.component_for_entity(player, Health)
    assert health.current == 2.0

    # Verify invincibility granted
    assert esper.has_component(player, Invincible)


def test_enemy_contact_respects_invincibility():
    """Test touching enemy while invincible doesn't damage."""
    esper.switch_world("test_enemy_contact_invincible")

    # Create invincible player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(3, 6))
    esper.add_component(player, Collider(0.5))
    esper.add_component(player, Invincible(0.3))

    # Create enemy overlapping player
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("chaser"))
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, Collider(0.5))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify no damage dealt
    health = esper.component_for_entity(player, Health)
    assert health.current == 3.0
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_collision_system.py::test_enemy_contact_damages_player tests/test_collision_system.py::test_enemy_contact_respects_invincibility -v`
Expected: FAIL (no contact damage implemented)

**Step 3: Add contact damage to collision system**

In `src/systems/collision.py`, add these collision checks to the `_handle_collision()` method after the projectile checks:

```python
    # Enemy touching player (contact damage)
    if esper.has_component(e1, Enemy) and esper.has_component(e2, Player):
        self._enemy_contact_player(e1, e2)
    elif esper.has_component(e2, Enemy) and esper.has_component(e1, Player):
        self._enemy_contact_player(e2, e1)
```

Then add this new method at the end of the class:

```python
def _enemy_contact_player(self, enemy: int, player: int):
    """Handle enemy touching player (contact damage)."""
    from src.components.game import Invincible, Dead
    from src.config import Config

    # Check invincibility
    if esper.has_component(player, Invincible):
        return  # No damage while invincible

    health = esper.component_for_entity(player, Health)
    health.current -= 1.0  # Contact damage = 1 heart

    # Add invincibility frames
    esper.add_component(player, Invincible(Config.INVINCIBILITY_DURATION))

    # Check for death
    if health.current <= 0:
        esper.add_component(player, Dead())
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_collision_system.py::test_enemy_contact_damages_player tests/test_collision_system.py::test_enemy_contact_respects_invincibility -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/systems/collision.py tests/test_collision_system.py
git commit -m "feat: implement contact damage from enemies

Touching enemies deals 1 damage and grants invincibility.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Test Player Death Handling

**Files:**
- Test: `tests/test_collision_system.py`

**Step 1: Write tests for death handling**

Add to `tests/test_collision_system.py`:

```python
def test_player_death_on_zero_health():
    """Test Dead component added when health reaches 0."""
    esper.switch_world("test_player_death_zero")

    # Create player with 1 HP
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(1, 6))
    esper.add_component(player, Collider(0.5))

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))

    # Create fatal projectile
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(10.0, 10.0))
    esper.add_component(projectile, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile, Collider(0.2))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify death
    health = esper.component_for_entity(player, Health)
    assert health.current <= 0
    assert esper.has_component(player, Dead)


def test_player_death_on_negative_health():
    """Test Dead component added even if damage exceeds remaining HP."""
    esper.switch_world("test_player_death_negative")

    # Create player with 1 HP
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(1, 6))
    esper.add_component(player, Collider(0.5))

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))

    # Create overkill projectile
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(10.0, 10.0))
    esper.add_component(projectile, Projectile(damage=5.0, owner=enemy))
    esper.add_component(projectile, Collider(0.2))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify death
    health = esper.component_for_entity(player, Health)
    assert health.current < 0
    assert esper.has_component(player, Dead)
```

**Step 2: Run tests to verify they pass**

Run: `uv run pytest tests/test_collision_system.py::test_player_death_on_zero_health tests/test_collision_system.py::test_player_death_on_negative_health -v`
Expected: PASS (2 tests) - death handling already implemented in previous tasks

**Step 3: Commit**

```bash
git add tests/test_collision_system.py
git commit -m "test: add player death tests

Verify Dead component added on fatal damage.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Implement Sprite Flashing in RenderSystem

**Files:**
- Modify: `src/systems/render.py`
- Test: `tests/test_render_system.py`

**Step 1: Write failing tests for sprite flashing**

Add to `tests/test_render_system.py`:

```python
def test_sprite_flashes_during_invincibility():
    """Test player sprite flashes white during invincibility."""
    esper.switch_world("test_flash_invincible")

    # Create invincible player with elapsed time 0.05s (should show white)
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(5.0, 5.0))
    esper.add_component(player, Sprite('@', 'cyan'))
    esper.add_component(player, Invincible(0.45))  # 0.5 - 0.05 elapsed

    # Render
    system = RenderSystem(10, 10)
    esper.add_processor(system)
    esper.process()

    grid = system.get_grid()
    # Player at (5, 5) should be white (flashing)
    assert grid[5][5]['char'] == '@'
    assert grid[5][5]['color'] == 'white'


def test_sprite_normal_color_without_invincibility():
    """Test player uses normal color when not invincible."""
    esper.switch_world("test_no_flash")

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(5.0, 5.0))
    esper.add_component(player, Sprite('@', 'cyan'))

    system = RenderSystem(10, 10)
    esper.add_processor(system)
    esper.process()

    grid = system.get_grid()
    # Player should be cyan (normal)
    assert grid[5][5]['char'] == '@'
    assert grid[5][5]['color'] == 'cyan'


def test_sprite_flash_toggles_over_time():
    """Test sprite flashing alternates between colors."""
    esper.switch_world("test_flash_toggle")

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(5.0, 5.0))
    esper.add_component(player, Sprite('@', 'cyan'))

    system = RenderSystem(10, 10)
    esper.add_processor(system)

    # Test at elapsed=0.05 (within first 0.1s) -> white
    esper.add_component(player, Invincible(0.45))
    esper.process()
    grid1 = system.get_grid()
    assert grid1[5][5]['color'] == 'white'

    # Test at elapsed=0.15 (between 0.1-0.2s) -> cyan
    inv = esper.component_for_entity(player, Invincible)
    inv.remaining = 0.35  # elapsed = 0.5 - 0.35 = 0.15
    esper.process()
    grid2 = system.get_grid()
    assert grid2[5][5]['color'] == 'cyan'
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_render_system.py::test_sprite_flashes_during_invincibility tests/test_render_system.py::test_sprite_normal_color_without_invincibility tests/test_render_system.py::test_sprite_flash_toggles_over_time -v`
Expected: FAIL (sprite flashing not implemented)

**Step 3: Implement sprite flashing**

In `src/systems/render.py`, find where the sprite color is determined and modify it to check for invincibility.

Look for the rendering loop that gets Position and Sprite components. Before using the sprite color, add:

```python
# Handle invincibility flashing for player
from src.components.game import Player, Invincible
from src.config import Config

color = sprite.color
if esper.has_component(ent, Player) and esper.has_component(ent, Invincible):
    # Flash every 0.1 seconds (10 FPS flash rate)
    invincible = esper.component_for_entity(ent, Invincible)
    # Use elapsed time: (duration - remaining)
    elapsed = Config.INVINCIBILITY_DURATION - invincible.remaining
    if (elapsed % 0.2) < 0.1:
        color = 'white'  # Flash to white
    # else: keep original color
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_render_system.py::test_sprite_flashes_during_invincibility tests/test_render_system.py::test_sprite_normal_color_without_invincibility tests/test_render_system.py::test_sprite_flash_toggles_over_time -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/systems/render.py tests/test_render_system.py
git commit -m "feat: implement sprite flashing during invincibility

Player sprite alternates cyan/white every 0.1s while invincible.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Register InvincibilitySystem in Game Engine

**Files:**
- Modify: `src/game/engine.py`
- Test: `tests/test_engine.py`

**Step 1: Write failing test for system registration**

Add to `tests/test_engine.py`:

```python
def test_engine_has_invincibility_system():
    """Test game engine registers InvincibilitySystem."""
    from src.systems.invincibility import InvincibilitySystem

    engine = GameEngine()

    # Check system is registered
    processors = engine.world._processors
    invincibility_systems = [p for p in processors if isinstance(p, InvincibilitySystem)]
    assert len(invincibility_systems) == 1
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_engine.py::test_engine_has_invincibility_system -v`
Expected: FAIL with "assert len(invincibility_systems) == 1"

**Step 3: Register InvincibilitySystem**

In `src/game/engine.py`, add import at top:

```python
from src.systems.invincibility import InvincibilitySystem
```

Then in `__init__`, after CollisionSystem and before RenderSystem, add:

```python
        self.invincibility_system = InvincibilitySystem()
        self.world.add_processor(self.invincibility_system, priority=6)
```

Update RenderSystem priority to 7:

```python
        self.render_system = RenderSystem(Config.ROOM_WIDTH, Config.ROOM_HEIGHT)
        self.world.add_processor(self.render_system, priority=7)
```

In the `update()` method, add dt assignment for invincibility system:

```python
        self.invincibility_system.dt = dt
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_engine.py::test_engine_has_invincibility_system -v`
Expected: PASS

**Step 5: Run all tests**

Run: `uv run pytest`
Expected: All tests pass (should be 81 + new tests = ~92 tests)

**Step 6: Commit**

```bash
git add src/game/engine.py tests/test_engine.py
git commit -m "feat: register InvincibilitySystem in game engine

Add invincibility system at priority 6, update render to priority 7.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Integration Test - Full Damage Cycle

**Files:**
- Test: `tests/test_integration.py`

**Step 1: Write integration test**

Add to `tests/test_integration.py`:

```python
def test_player_damage_and_invincibility_cycle():
    """Test complete damage flow from hit to recovery."""
    esper.switch_world("test_damage_cycle")

    # Create game engine
    from src.game.engine import GameEngine
    engine = GameEngine()

    # Create player with 3 HP
    from src.entities.player import create_player
    player = create_player("test_damage_cycle", 20.0, 10.0)
    health = esper.component_for_entity(player, Health)
    health.current = 3.0

    # Create enemy
    from src.entities.enemies import create_enemy
    enemy = create_enemy("test_damage_cycle", "shooter", 10.0, 10.0)

    # Create first projectile at player position
    projectile1 = esper.create_entity()
    esper.add_component(projectile1, Position(20.0, 10.0))
    esper.add_component(projectile1, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile1, Collider(0.2))

    # Update once - collision should deal damage
    engine.update(0.1)

    # Verify damage dealt and invincibility granted
    assert health.current == 2.0
    assert esper.has_component(player, Invincible)

    # Create second projectile during invincibility
    projectile2 = esper.create_entity()
    esper.add_component(projectile2, Position(20.0, 10.0))
    esper.add_component(projectile2, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile2, Collider(0.2))

    # Update - should not deal damage (invincible)
    engine.update(0.1)
    assert health.current == 2.0

    # Wait for invincibility to expire (0.5s total)
    for _ in range(4):
        engine.update(0.1)

    # Invincibility should be gone
    assert not esper.has_component(player, Invincible)

    # Create third projectile after invincibility expires
    projectile3 = esper.create_entity()
    esper.add_component(projectile3, Position(20.0, 10.0))
    esper.add_component(projectile3, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile3, Collider(0.2))

    # Update - should deal damage again
    engine.update(0.1)
    assert health.current == 1.0
```

**Step 2: Run test to verify it passes**

Run: `uv run pytest tests/test_integration.py::test_player_damage_and_invincibility_cycle -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration test for damage cycle

Verify damage, invincibility, and recovery work end-to-end.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Update README

**Files:**
- Modify: `README.md`

**Step 1: Update README features and known issues**

In `README.md`, update:

**Features section:**
```markdown
- **Player Damage System** - Take damage from projectiles and contact
- **Invincibility Frames** - Brief immunity after taking damage with visual flash
```

**Known Issues section (remove):**
```markdown
- Player is currently invincible (damage system not fully integrated)
```

**Roadmap section:**
```markdown
**Phase 1: Core Gameplay** (Current)
- [x] ECS architecture
- [x] Player movement and shooting
- [x] Enemy AI
- [x] Collision detection
- [x] Enemy shooting patterns
- [x] Player damage system
- [ ] Item pickup and stat modification system
```

Update test count badge if needed (check actual count after running all tests).

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README with player damage system

Mark player damage as complete, remove invincibility known issue.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Success Criteria

All tasks completed when:
- ✅ Dead marker component added
- ✅ InvincibilitySystem decrements timers and removes expired invincibility
- ✅ Enemy projectiles damage player
- ✅ Contact damage from enemies
- ✅ Invincibility prevents damage for 0.5 seconds
- ✅ Sprite flashes white/cyan during invincibility
- ✅ Dead component added on fatal damage
- ✅ All tests pass (~92 tests)
- ✅ README updated

Run full test suite: `uv run pytest -v`
Expected: All tests passing

---

## Notes for Implementation

**System Execution Order:**
1. InputSystem (priority 0)
2. AISystem (priority 1)
3. EnemyShootingSystem (priority 2)
4. ShootingSystem (priority 3)
5. MovementSystem (priority 4)
6. CollisionSystem (priority 5) - applies damage, grants invincibility
7. InvincibilitySystem (priority 6) - NEW - decrements timers
8. RenderSystem (priority 7) - updated priority - handles flashing

**Collision Cases:**
- Enemy projectile + Player → Apply damage, grant invincibility
- Enemy + Player (contact) → Apply damage, grant invincibility
- Both check invincibility before dealing damage

**Visual Flash Calculation:**
```python
elapsed = Config.INVINCIBILITY_DURATION - invincible.remaining
if (elapsed % 0.2) < 0.1:
    color = 'white'
else:
    color = original_color
```

**Death Detection:**
- Health ≤ 0 → Add Dead component
- Player entity remains in world
- Future game over system queries for Player + Dead
