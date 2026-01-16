# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Texting of Isaac** is a TUI (Terminal User Interface) roguelike game inspired by The Binding of Isaac. It's a real-time bullet-hell game rendered entirely in ASCII/Unicode in the terminal using Python 3.12+ with an Entity Component System (ECS) architecture.

## Development Commands

### Package Manager: uv

**IMPORTANT**: This project uses **uv** for Python package management, NOT poetry or pip. Always use `uv` commands:

- ✅ Use: `uv run python main.py`
- ✅ Use: `uv run pytest`
- ✅ Use: `uv sync`
- ❌ Don't use: `poetry run python main.py`
- ❌ Don't use: `python main.py` (direct)
- ❌ Don't use: `pip install`

### Running the Game
```bash
uv run python main.py
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_collision_system.py

# Run specific test function
uv run pytest tests/test_collision_system.py::test_player_projectile_hits_enemy
```

### Dependencies
```bash
# Install/sync dependencies
uv sync

# Add a new dependency (modifies pyproject.toml)
uv add <package-name>

# Remove a dependency
uv remove <package-name>
```

## Architecture

### Entity Component System (ECS)

The game uses the **Esper** ECS framework. Understanding this architecture is critical:

- **Entities**: Integer IDs representing game objects (player, enemies, projectiles, items)
- **Components**: Pure data classes (Position, Velocity, Health, Stats, etc.)
- **Systems**: Logic processors that operate on entities with specific component combinations

**Important**: Esper uses module-level world management. Each `GameEngine` instance creates its own world via `esper.switch_world(world_name)`. Always ensure you're operating on the correct world context.

### System Processing Order

Systems run in priority order (lower = earlier). From `src/game/engine.py`:

1. **InputSystem** (0) - Captures player input
2. **AISystem** (1) - Enemy AI behaviors
3. **EnemyShootingSystem** (2) - Enemy projectile spawning
4. **ShootingSystem** (3) - Player projectile spawning
5. **MovementSystem** (4) - Apply velocity to positions
6. **HomingSystem** (4.5) - Homing projectile guidance
7. **CollisionSystem** (5) - Collision detection and damage
8. **InvincibilitySystem** (6) - Invincibility frame management
9. **ItemPickupSystem** (6.5) - Item collection logic
10. **RenderSystem** (7) - Grid-based rendering

This order matters. For example, collision must happen after movement, and rendering must be last.

### Core Component Structure

Components are split across multiple files:

- `src/components/core.py` - Position, Velocity, Health, Sprite
- `src/components/combat.py` - Stats, Collider, Projectile, Homing
- `src/components/game.py` - Player, Enemy, Item, AIBehavior, Invincible, CollectedItems
- `src/components/dungeon.py` - DungeonPosition, Door
- `src/components/currency.py` - Coins, Bombs

### Entity Factories

Entity creation functions in `src/entities/`:
- `player.py` - `create_player()` - Creates player with all required components
- `enemies.py` - `create_enemy(type)` - Creates 5 enemy types (chaser, shooter, orbiter, turret, tank)
- `items.py` - `create_item(item_name)` - Creates item pickups from definitions
- `rewards.py` - `create_heart()`, `create_stat_boost()` - Creates room-clear rewards
- `currency.py` - `create_coin()`, `create_bomb_pickup()` - Creates currency pickups

### Configuration System

`src/config.py` contains a `Config` class with ALL game constants:
- Display settings (ROOM_WIDTH, ROOM_HEIGHT, FPS)
- Player stats (PLAYER_SPEED, PLAYER_DAMAGE, PLAYER_FIRE_RATE, etc.)
- Enemy/projectile hitboxes
- Drop rates and probabilities
- Dungeon generation parameters
- Bomb mechanics, currency settings

**Always use Config constants rather than hardcoding values.**

### Dungeon System

Two key concepts:

1. **DungeonRoom** (`src/game/dungeon.py`): Logical dungeon structure
   - Procedural generation creates 12-18 rooms
   - Main path with branches for treasure/shop rooms
   - Secret rooms accessible via bombs
   - Each room has connections (doors) to adjacent rooms

2. **Room** (`src/game/room.py`): Physical room rendering
   - Obstacle generation and placement
   - Enemy spawning based on room type
   - 60x20 character grid

### Item System

Items are defined in `src/data/items.py` with:
- `stat_modifiers`: Direct stat changes (damage, speed, fire_rate)
- `special_effects`: Named effects like "homing", "piercing", "multi_shot"

The player's `CollectedItems` component tracks all collected items. Check for special effects using `collected_items.has_effect("homing")`.

### Collision System

Uses circle-based collision with configurable radii:
- Player hitbox: 0.3 (very small - bullet hell style)
- Enemy hitbox: 0.5
- Projectile hitbox: 0.2
- Item pickup radius: 0.4

Collision system handles:
- Player projectile vs enemy
- Enemy projectile vs player
- Player/projectile vs walls/obstacles
- Player vs item pickups (handled by ItemPickupSystem)

### Rendering

The game uses a grid-based rendering system:
- 60x20 character grid rendered via Rich tables
- Each cell has a character and color
- RenderSystem queries all Position + Sprite components
- Priority: walls > entities > projectiles > floor

**Character meanings**:
- `@` = Player, `e/S/T/O/E` = Enemies, `.` = Player projectile, `*` = Enemy projectile
- `○` = Obstacle, `#` = Wall, `♥` = Heart, `$` = Coin, `B` = Bomb

## Testing Philosophy

This project has comprehensive test coverage (99 tests, ~4700 lines). When adding features:

1. **Write tests for new systems** - Each system should have a dedicated test file
2. **Test entity factories** - Verify all components are attached correctly
3. **Test edge cases in collision** - The collision system is complex and critical
4. **Use conftest.py fixtures** - Shared fixtures for world setup are in `tests/conftest.py`

**Test world management**: Tests create isolated worlds using `@pytest.fixture` and clean them up. Always switch to the correct world before assertions.

## Common Patterns

### Creating a New Component

1. Define the component class in the appropriate file under `src/components/`
2. Add validation in `__init__` or `__post_init__` (for dataclasses)
3. Add tests in `tests/test_components.py`

### Creating a New System

1. Create system class inheriting from `esper.Processor`
2. Implement `process(self)` method
3. Query entities using `self.world.get_components(ComponentA, ComponentB)`
4. Register in `GameEngine.__init__()` with appropriate priority
5. Set `dt` on system in `GameEngine.update()` if needed
6. Add comprehensive tests

### Adding a New Enemy Type

1. Add enemy config to `src/entities/enemies.py` in `ENEMY_CONFIGS` dict
2. Define stats (hp, speed, damage) and shooting patterns
3. Update enemy creation logic if needed
4. Add test cases for the new enemy type

### Adding a New Item

1. Add item definition to `src/data/items.py` in `ITEM_DEFINITIONS`
2. If adding a new special effect, implement handling in relevant systems
3. Update tests in `tests/test_items.py`

## Development Notes

### Input Handling

The game uses raw terminal input (`termios`, `tty`) for non-blocking keyboard capture. `InputHandler` in `main.py` reads WASD for movement and arrow keys for shooting. This is separate from the ECS `InputSystem`.

### Delta Time (dt)

All time-based logic uses delta time in seconds. Systems receive `dt` from the engine's update loop. Use it for:
- Velocity application: `position.x += velocity.dx * dt`
- Cooldowns: `cooldown -= dt`
- Timers: `remaining -= dt`

### World Context Management

Since Esper uses module-level state, always switch to the correct world:
```python
esper.switch_world(world_name)
# Now operations affect this world
```

This is especially important in tests where multiple worlds may exist.

### Performance Considerations

- Target is 30 FPS
- Limit projectiles via `Config.MAX_PROJECTILES` (currently 200)
- Entity cleanup happens in collision system (projectiles that hit)
- Dead enemies are removed immediately after spawning rewards

## Future Architecture Notes

Based on design docs in `docs/plans/`:

- **Multi-room progression**: RoomManager system will handle room transitions
- **Door mechanics**: Doors lock during combat, unlock when room cleared
- **Boss fights**: Planned separate boss entity types
- **Special effects**: Multi-shot, piercing, and explosive projectiles planned

When implementing these features, maintain the ECS pattern: create components for new data, create systems for new logic, update entity factories as needed.
