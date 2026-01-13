# TUI Roguelike Design - "Texting of Isaac"

**Date:** 2026-01-13
**Status:** Prototype Specification
**Goal:** Solid playable prototype with one floor, basic combat, and item variety

## Overview

A real-time bullet-hell roguelike in ASCII/TUI inspired by The Binding of Isaac, built with Python using an Entity Component System architecture. The prototype focuses on proving the core gameplay loop: procedurally generated rooms, real-time bullet-hell combat, and meaningful item pickups.

## Technology Stack

- **Language:** Python
- **TUI Library:** Rich (custom rendering loop for game updates)
- **ECS Library:** Esper (lightweight component-entity-system)
- **Target FPS:** 30 FPS

## High-Level Architecture

### Game Loop Structure

Main loop runs at ~30 FPS using Rich's `Live` display:
1. Handle input (WASD movement, arrow keys shooting)
2. Update all ECS systems (movement, collision, shooting, AI)
3. Render current room to Rich panel
4. Check room clear/game state transitions

### ECS Architecture

**Core Components:**
- `Position(x, y)` - spatial location
- `Velocity(dx, dy)` - movement vector
- `Health(current, max)` - hitpoints
- `Player()` - marker for player entity
- `Enemy(type)` - marker + enemy variant
- `Projectile(damage, pattern, owner)` - bullets/tears
- `Collider(radius)` - collision detection
- `Sprite(char, color)` - rendering info
- `Stats(speed, damage, fire_rate, shot_speed)` - combat stats
- `Item(effects)` - item data
- `AIBehavior(state, cooldowns)` - enemy patterns

**System Processors:**
- `InputSystem` - captures player input, updates velocity/shooting
- `MovementSystem` - applies velocity to positions
- `CollisionSystem` - detects overlaps, triggers damage
- `AISystem` - enemy behavior and pattern execution
- `ShootingSystem` - spawns projectiles based on fire rate
- `RenderSystem` - draws everything to Rich console

## Room Structure & Procedural Generation

### Room Representation

Each room is a 60x20 character grid containing:
- Walls around perimeter
- Procedurally placed obstacles (rocks, pits) for cover
- 2-4 doors (top/bottom/left/right) that lock when enemies spawn
- Spawn points for enemies and items

### Generation Algorithm

For each room:

1. **Base layout:** Empty rectangular room with doors based on connections
2. **Obstacle placement:**
   - Place 3-8 obstacle "seeds" randomly
   - Grow each seed into 2-4 tile clusters
   - Ensure obstacles don't block doors or center spawn area
3. **Enemy composition:** Select 2-5 enemies based on difficulty
   - Early rooms: 2-3 weak enemies
   - Mid rooms: 3-4 mixed enemies
   - Pre-boss: 4-5 harder enemies
4. **Spawn positions:** Place enemies away from entrance, spread out

### Dungeon Flow

A run consists of 8-12 rooms in a branching tree:
- 1 start room (no enemies)
- 5-8 combat rooms (random enemy compositions)
- 1-2 treasure rooms (item pickup, no enemies)
- 1 boss room (final encounter)

Generation creates paths with occasional branches, ensuring boss is reachable and treasure rooms are on side paths.

## Combat System

### Player Combat

- **Movement:** WASD keys, continuous 8-directional movement at `stats.speed` tiles/second
- **Shooting:** Arrow keys fire tears independently (twin-stick style)
- **Fire rate:** Tears spawn every `1.0 / fire_rate` seconds
- **Tear behavior:** Travel at `shot_speed`, deal `damage` on collision, disappear after hitting

### Enemy Types (3-5 for prototype)

1. **Chaser** (melee): Moves toward player. Patterns: dash attack when close
2. **Shooter** (basic ranged): Stationary/slow. Patterns: single aimed shot, 3-way spread
3. **Orbiter** (mobile ranged): Circles player at medium range. Patterns: aimed shot, ring of 8 bullets
4. **Turret** (stationary): Doesn't move. Patterns: rotating spray, cross-pattern (4 directions)
5. **Tank** (tough melee): Slow, high HP. Patterns: radial shockwave, charge attack

### Attack Pattern System

Patterns stored as `Pattern(name, cooldown, bullet_config)`:
- `bullet_config` defines: count, spread_angle, speed, offset_angle
- Example spread: `count=3, spread_angle=30°, speed=5`
- Example ring: `count=8, spread_angle=45°, speed=3`

`AISystem` tracks cooldowns, triggers patterns, spawns projectile entities with appropriate velocities.

## Item System

### Item Structure

Items contain:
- Name and description
- `stat_modifiers` - dict of stat changes
- `special_effects` - list of behavior modifications

### 12-15 Item Examples

**Stat Modifiers:**
1. **Speed Shoes** - +1.5 speed
2. **Steroids** - +2 damage, -0.2 speed
3. **Rapid Fire** - +1 fire rate
4. **Big Tears** - +3 damage, -0.5 shot speed

**Special Effects:**
5. **Homing Tears** - projectiles curve toward nearest enemy
6. **Piercing Shot** - tears pass through first enemy
7. **Shotgun** - fire 3 tears in spread pattern
8. **Poison Tears** - enemies take damage over time after hit
9. **Shield** - gain 1 orbital that blocks projectiles
10. **Ghost Tears** - projectiles pass through walls

**Health/Utility:**
11. **Heart Container** - +1 max HP, full heal
12. **Speed Boost** - +1 speed, +0.5 shot speed
13. **Glass Cannon** - +4 damage, -1 max HP
14. **Boomerang Tears** - tears return after max distance
15. **Explosive Tears** - area damage on impact

### Item Application

On pickup:
1. Apply stat modifiers to `player.stats`
2. Add special effect tags to player entity
3. Relevant systems check tags and modify behavior
4. Item sprite disappears, play pickup effect

## Collision Detection & Physics

### Collision System

Circle-based collision (each entity has `Collider(radius)`):
- Player: radius ~0.3 tiles (small hitbox for fairness)
- Enemies: radius 0.4-0.8 tiles (varies by type)
- Projectiles: radius 0.2 tiles
- Obstacles: radius 0.5 tiles

### Collision Checks (per frame)

1. **Projectile vs Enemy:** Deal damage, remove projectile (unless piercing)
2. **Projectile vs Player:** Deal damage, remove projectile, brief invincibility (0.5s)
3. **Player vs Enemy:** Contact damage to player, knockback both
4. **Entity vs Wall/Obstacle:** Stop movement, prevent overlap
5. **Enemy vs Enemy:** Slight repulsion to prevent stacking

### Collision Response

- **Damage:** Modify `Health.current`, flash sprite, check for death
- **Knockback:** Apply temporary velocity away from collision
- **Invincibility:** Add `Invincible(duration)` component, ignore damage
- **Death:** Remove entity, spawn effects, 10% chance drop heart

### Performance

Simple O(n²) checks acceptable for prototype (small rooms, ~50 entities max).

## Rendering & UI

### Rendering Architecture

Use Rich `Live` context for 30 FPS updates:
1. Create `Table` layout with game area and HUD sidebar
2. Render game world to `Panel` (60x20 grid)
3. Render UI stats to sidebar `Panel`
4. Update `Live` display

### Game World Rendering

Build 2D character grid from ECS entities:
- Floor tiles (`.` or ` `)
- Walls (`#`) and obstacles (`█` or `○`)
- Doors (`+` locked, ` ` open)
- Entities in draw order:
  - Projectiles (`.` tears, `*` enemy bullets)
  - Enemies (`e`, `E`, `T`, `O` by type)
  - Player (`@`)
  - Items (`?` or specific icons)

**Colors (Rich):**
- Player: bright cyan
- Enemies: red/magenta
- Player tears: white
- Enemy bullets: yellow
- Hearts: red `♥`
- Items: green/yellow

### HUD Sidebar

Display:
- Current HP: `♥♥♥` (filled) `♡` (empty)
- Room count: `Room 3/10`
- Stats: `DMG: 3 | SPD: 5.0 | RATE: 2.5`
- Items collected: mini icons
- Controls reminder

## Boss Fight

### Boss Design

Special enemy entity with:
- **High HP:** 50-80 health (vs 3-10 for regular enemies)
- **Multiple phases:** Health thresholds trigger behavior changes
  - Phase 1 (100-66%): Slow, single attack
  - Phase 2 (66-33%): Faster, second pattern introduced
  - Phase 3 (33-0%): Aggressive, alternating patterns
- **Larger sprite:** 3x3 characters vs 1x1
- **Arena:** Larger room, minimal obstacles

### Example Boss - "The Bloated One"

- Phase 1: Ring of 8 bullets every 2 seconds
- Phase 2: Adds charging dash toward player
- Phase 3: Ring every 1 second + spawns 2 small chasers

## Game State Management

### State Machine

States:
1. **MENU:** Title screen, start run
2. **ROOM_ENTER:** Door animation, spawn enemies
3. **ROOM_COMBAT:** Active gameplay, doors locked
4. **ROOM_CLEAR:** Enemies dead, doors unlock, spawn rewards
5. **ROOM_TRANSITION:** Moving between rooms
6. **BOSS_INTRO:** Boss entrance animation
7. **BOSS_FIGHT:** Boss combat
8. **VICTORY:** Boss defeated, win screen
9. **GAME_OVER:** Player died, show stats

### Transitions

- MENU → ROOM_ENTER (start)
- ROOM_COMBAT → ROOM_CLEAR (enemies.count == 0)
- ROOM_CLEAR → ROOM_TRANSITION (player enters door)
- ROOM_TRANSITION → ROOM_ENTER/BOSS_INTRO (next room)
- BOSS_FIGHT → VICTORY (boss.health <= 0)
- Any → GAME_OVER (player.health <= 0)

### Health Progression

Health persists between rooms (Isaac-style). Enemies have 10% chance to drop hearts on death, creating resource management tension.

## Project Structure

```
texting_of_isaac/
├── main.py                    # Entry point, game loop
├── requirements.txt           # Dependencies
├── src/
│   ├── __init__.py
│   ├── components/           # ECS components
│   │   ├── __init__.py
│   │   ├── core.py          # Position, Velocity, Health
│   │   ├── combat.py        # Stats, Projectile, Collider
│   │   └── game.py          # Player, Enemy, Item, AIBehavior
│   ├── systems/             # ECS processors
│   │   ├── __init__.py
│   │   ├── input.py         # InputSystem
│   │   ├── movement.py      # MovementSystem
│   │   ├── collision.py     # CollisionSystem
│   │   ├── ai.py            # AISystem
│   │   ├── shooting.py      # ShootingSystem
│   │   └── render.py        # RenderSystem
│   ├── entities/            # Entity factories
│   │   ├── __init__.py
│   │   ├── player.py        # create_player()
│   │   ├── enemies.py       # create_enemy(type)
│   │   └── items.py         # create_item(type)
│   ├── game/
│   │   ├── __init__.py
│   │   ├── state.py         # GameState enum, state machine
│   │   ├── room.py          # Room class, generation
│   │   └── dungeon.py       # Dungeon graph generation
│   ├── patterns/            # Attack pattern definitions
│   │   ├── __init__.py
│   │   └── bullet.py        # Pattern class, presets
│   └── config.py            # Constants, tuning values
├── assets/                   # Future: room templates
└── docs/
    └── plans/               # Design documents
```

### Key Design Patterns

- **Entity Factories:** Functions encapsulate component setup
- **System Processors:** Independent, communicate via components
- **Config File:** Centralize tuning values for balancing
- **Room/Dungeon Classes:** Separate layout from flow generation

## Error Handling & Edge Cases

### Critical Edge Cases

1. **Collision:**
   - Check spawn position validity (no walls)
   - Clamp positions to room boundaries
   - Queue and apply all damage in same frame

2. **Generation:**
   - Validate graph connectivity before accepting
   - Ensure minimum clear path width (obstacles)
   - Enforce minimum distance from entrance for enemy spawns

3. **Performance:**
   - Cap active projectiles (~50 total)
   - Early exit collision checks if entities far apart
   - Cull entities outside visible area

4. **Game state:**
   - Double-check enemy count for room clear
   - Use `<=` not `==` for HP thresholds
   - Add collision buffer zones

### Error Handling Strategy

- **Graceful degradation:** Retry generation with simpler parameters
- **Logging:** Debug info for collisions, state transitions
- **Assertions:** Validate invariants (player exists, bounds, state)
- **Safe defaults:** Fallback values for missing data

### Debug Mode

`--debug` flag shows:
- Collision circles
- Entity counts
- FPS counter
- Room generation seed

## Testing Strategy

### Unit Tests (pytest)

Focus on critical systems:
1. **Collision:** Circle overlap, boundary clamping, knockback
2. **Room Generation:** Obstacle placement, connectivity, spawn distance
3. **Patterns:** Bullet angles, velocities, cooldowns
4. **ECS Logic:** Health, stat modifiers, item effects

### Manual Testing Focus

- **Game feel:** Movement responsive? Bullets dodgeable?
- **Difficulty:** Room 1 easy? Boss hard?
- **Item balance:** Any overpowered/useless items?
- **Generation quality:** Rooms fair and varied?

### Test Utilities

- Seed-based generation for reproducibility
- Debug commands: spawn items, skip rooms, god mode
- Test harnesses for specific scenarios

### Acceptance Criteria

✓ Complete full run (start → boss defeat)
✓ Combat feels responsive and fair
✓ 3+ distinct enemy behaviors
✓ Items noticeably change gameplay
✓ Rooms feel varied
✓ No major bugs/crashes

## Dependencies

```
rich>=13.0.0
esper>=3.0.0
pytest>=7.0.0  # for testing
```

## Next Steps

1. Set up project structure and dependencies
2. Implement core ECS components and basic game loop
3. Build rendering system with Rich
4. Implement player movement and shooting
5. Add collision detection
6. Create first enemy type and AI
7. Implement room generation
8. Add items and stat modifications
9. Build boss encounter
10. Polish and balance
