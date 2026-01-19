# Boss Fights and Multiple Floors Design

> **Date:** 2026-01-19
> **Status:** Approved - Ready for Implementation

## Overview

Add multi-phase boss fights and multiple floor progression to create complete dungeon runs. Players fight through Floor 1 → Floor 2 → Floor 3, with each floor ending in a unique boss fight. Defeating the final boss triggers victory.

## Core Concept

**Multi-Floor Dungeon Runs:**
Each floor is a complete procedurally generated dungeon (12-18 rooms) with escalating difficulty. Boss room always at end of main path. Defeating the boss spawns a trapdoor to the next floor.

**Multi-Phase Boss Fights:**
Bosses have 2 distinct phases based on HP:
- Phase 1: 100% → 50% HP (initial patterns)
- Phase 2: < 50% HP (harder geometric patterns + faster teleports)

**Victory Condition:**
Defeat the boss on Floor 3 (final floor) to win the game.

**Loss Condition:**
Player HP reaches 0 on any floor triggers game over.

## High-Level Architecture

### Floor System

**Structure:**
- Each floor is a self-contained `Dungeon` instance
- Track `current_floor: int` in game state
- Target: 3 floors for initial implementation (expandable to 4+)
- Same dungeon generation algorithm per floor
- Boss room always at end of main path

**Difficulty Scaling:**

Floor multipliers applied to enemy base stats:

| Floor | HP Multiplier | Damage Multiplier | Enemy Count |
|-------|---------------|-------------------|-------------|
| 1     | 1.0x          | 1.0x              | 3-5         |
| 2     | 1.3x          | 1.2x              | 4-6         |
| 3     | 1.6x          | 1.5x              | 5-7         |
| 4+    | 2.0x          | 1.8x              | 6-8         |

**Floor Transition:**
1. Boss defeated → spawn trapdoor at boss position
2. Player collision with trapdoor triggers transition
3. Clear current dungeon entities
4. Increment `current_floor += 1`
5. Generate new dungeon for new floor
6. Spawn player at new floor's start room
7. Reset room states (all unvisited)

### Boss System

**Boss Entities:**
- Unique boss components (Boss, BossAI)
- 2-phase behavior based on HP threshold
- Geometric attack patterns (spirals, waves, pulses)
- Teleport movement between attacks
- Health bar displayed at top of screen

**Phase Mechanics:**
When boss HP drops below 50%:
1. Set `Boss.current_phase = 2`
2. Switch to phase 2 attack patterns
3. Reduce teleport cooldown (more frequent repositioning)
4. Brief invulnerability (0.5s) during transition to prevent instant phase-skip
5. Visual feedback: Boss flashes/changes color

**Victory Rewards:**
- Guaranteed: 5-8 coins (scaled by floor), 1-2 hearts
- 60% chance: 1 random item from pool
- Trapdoor spawns to next floor (except final floor)

**Integration:**
- Boss type selected based on current floor
- RoomManager handles boss room entry (locks doors, spawns boss)
- RoomManager handles boss victory (spawns rewards, unlocks trapdoor)
- Floor transition system manages dungeon progression

## Components & Data Structures

### New Components

```python
@dataclass
class Boss:
    """Boss entity marker and state."""
    boss_type: str  # "boss_a", "boss_b", "boss_c"
    current_phase: int = 1
    phase_2_threshold: float = 0.5  # 50% HP triggers phase 2
    has_transitioned: bool = False  # Prevent double-transition

@dataclass
class BossAI:
    """Boss-specific AI behavior."""
    pattern_name: str  # Current pattern: "spiral", "wave", "pulse", etc.
    pattern_timer: float = 0.0  # Time until next pattern execution
    pattern_cooldown: float = 2.0  # Time between patterns
    teleport_timer: float = 0.0  # Time until next teleport
    teleport_cooldown: float = 6.0  # Changes per phase

@dataclass
class Trapdoor:
    """Floor transition marker."""
    next_floor: int  # Which floor this leads to
```

### Game States

```python
class GameState(Enum):
    PLAYING = "playing"
    BOSS_FIGHT = "boss_fight"
    FLOOR_TRANSITION = "floor_transition"
    VICTORY = "victory"
    GAME_OVER = "game_over"
```

### Configuration Constants

```python
# Boss configuration
BOSS_FIGHT_MUSIC: bool = False  # Future: boss music toggle
BOSS_HEALTH_BAR_WIDTH: int = 40
BOSS_PHASE_2_THRESHOLD: float = 0.5
BOSS_PHASE_TRANSITION_INVULN: float = 0.5  # seconds

# Floor scaling
FLOOR_HP_MULTIPLIERS: dict[int, float] = {
    1: 1.0, 2: 1.3, 3: 1.6, 4: 2.0
}
FLOOR_DAMAGE_MULTIPLIERS: dict[int, float] = {
    1: 1.0, 2: 1.2, 3: 1.5, 4: 1.8
}
FLOOR_ENEMY_COUNT_RANGES: dict[int, tuple[int, int]] = {
    1: (3, 5), 2: (4, 6), 3: (5, 7), 4: (6, 8)
}

# Win condition
FINAL_FLOOR: int = 3  # Can adjust to 4 later

# Boss teleport safe zones
BOSS_TELEPORT_POSITIONS: list[tuple[float, float]] = [
    (10.0, 5.0), (50.0, 5.0), (30.0, 5.0),
    (10.0, 15.0), (50.0, 15.0), (30.0, 15.0),
    (20.0, 10.0), (40.0, 10.0)
]
BOSS_TELEPORT_MIN_PLAYER_DISTANCE: float = 5.0
```

## Systems Architecture

### New Systems

**1. BossAISystem (priority 1.5)**
- Processes after AISystem, before EnemyShootingSystem
- Queries entities with `Boss + BossAI + Position + Health`
- Handles phase transition logic (checks HP threshold)
- Updates pattern timers and executes geometric attack patterns
- Manages teleport logic (timer countdown, position selection)
- Switches patterns/cooldowns when entering phase 2

**2. BossHealthBarSystem (priority 7.5)**
- Processes before RenderSystem
- Queries for `Boss + Health` components
- Only renders if boss exists in current room
- Calculates health percentage and bar fill
- Renders boss health bar above main game grid
- Highlights phase transition threshold (50% mark)

**3. FloorTransitionSystem (priority 6.5)**
- Processes after ItemPickupSystem, before InvincibilitySystem
- Queries for player + `Trapdoor` entities
- Detects collision between player and trapdoor
- Triggers floor transition when player touches trapdoor
- Clears current dungeon, increments floor number
- Generates new dungeon for next floor

**4. GameStateSystem (priority 0)**
- Runs first, before InputSystem
- Manages game state transitions
- Checks win condition (boss dead on final floor)
- Checks loss condition (player HP ≤ 0)
- Handles input in VICTORY/GAME_OVER states (R to restart, Q to quit)
- Pauses other systems during non-PLAYING states

### Modified Systems

**RoomManager:**
- Detect boss room entry → spawn boss entity
- Lock doors during boss fight
- Unlock doors + spawn trapdoor when boss dies
- Track current floor number
- Pass floor number to dungeon generator for scaling

**CollisionSystem:**
- Handle trapdoor collision (player walks over → floor transition)
- Handle boss invulnerability during phase transition

## Boss Attack Patterns

### Pattern Implementation

Each pattern is a function that generates projectile data (positions, velocities). BossAISystem calls the appropriate pattern function based on current phase and boss type.

### Phase 1 Patterns (Easier)

**Spiral Pattern:**
- Spawn 8 projectiles in a circle around boss
- Rotate spawn angle by 15 degrees each execution
- Creates expanding spiral effect over time
- Speed: 4.0 units/sec
- Cooldown: 3.0 seconds

**Wave Pattern:**
- Fire 5 projectiles in 60-degree arc
- Arc sweeps from left to right over pattern duration
- Each volley shifts arc by 10 degrees
- Speed: 5.0 units/sec
- Cooldown: 2.5 seconds

**Pulse Pattern:**
- Fire 12 projectiles in complete circle (30-degree spacing)
- Wait 0.5 seconds, fire another ring
- 3 rings total per pattern execution
- Speed: 3.5 units/sec (slower for dodging between rings)
- Cooldown: 4.0 seconds

### Phase 2 Patterns (Harder)

**Double Spiral:**
- Two spirals, rotating opposite directions
- 16 projectiles total (8 per spiral)
- Rotation speed increased to 20 degrees/execution
- Speed: 4.5 units/sec
- Cooldown: 2.5 seconds

**Fast Wave:**
- 7 projectiles in 90-degree arc (wider coverage)
- Sweeps twice as fast
- Speed: 6.0 units/sec
- Cooldown: 2.0 seconds

**Burst Pulse:**
- 4 rapid rings with 0.3s spacing (less dodge time)
- 16 projectiles per ring (tighter spacing)
- Speed: 4.0 units/sec
- Cooldown: 3.5 seconds

### Pattern Selection Logic

- Boss alternates between its 3 assigned patterns
- Pattern timer counts down each frame (`dt`)
- When timer hits 0, execute pattern, reset timer to cooldown
- Phase transition immediately switches to phase 2 patterns

## Teleport Mechanics

### Teleport Positions

- Define 8 safe teleport spots in boss arena (60x20 grid)
- Positions in corners and cardinal directions, 5 units from walls
- Example: (10, 5), (50, 5), (30, 15), (10, 15), (50, 15), etc.
- Never teleport within 5 units of player (prevents cheap hits)

### Teleport Execution

1. Teleport timer counts down each frame (`dt`)
2. When timer reaches 0:
   - Select random safe position (not current position, not near player)
   - Update boss Position component to new location
   - Optional: Brief flash/particle effect at old and new positions
   - Reset teleport timer:
     - Phase 1: 6-8 seconds (random)
     - Phase 2: 3-4 seconds (random)

### Teleport Validation

Before confirming teleport position:
- Ensure position is within arena bounds (5 unit margin from walls)
- Check distance from player > BOSS_TELEPORT_MIN_PLAYER_DISTANCE (5.0)
- Ensure position is not current boss position
- If validation fails, retry with different random position (max 3 attempts)

## Boss Roster

### Boss A - "The Orbiter" (Floor 1)

**Stats:**
- HP: 50
- Sprite: `◉` (large circle)
- Color: cyan

**Patterns:**
- Phase 1: Spiral + Wave
- Phase 2: Double Spiral + Fast Wave

**Teleport:**
- Phase 1: Every 7 seconds
- Phase 2: Every 4 seconds

**Teaching Focus:**
- Basic pattern recognition
- Tracking teleporting enemies
- Dodging geometric patterns

### Boss B - "The Crossfire" (Floor 2)

**Stats:**
- HP: 75
- Sprite: `✦` (star/cross)
- Color: yellow

**Patterns:**
- Phase 1: Wave + Pulse
- Phase 2: Fast Wave + Burst Pulse + Cross (4 projectiles in cardinal directions)

**Teleport:**
- Phase 1: Every 6 seconds
- Phase 2: Every 3 seconds

**Teaching Focus:**
- Multi-directional threats
- Faster reaction time requirements
- Pattern combining

### Boss C - "The Spiral King" (Floor 3, Final Boss)

**Stats:**
- HP: 100
- Sprite: `◈` (diamond in circle)
- Color: bright_red

**Patterns:**
- Phase 1: Pulse + Spiral
- Phase 2: Burst Pulse + Double Spiral + Triple Spiral (3 spirals rotating)

**Teleport:**
- Phase 1: Every 6 seconds
- Phase 2: Every 3 seconds

**Teaching Focus:**
- Final challenge combining all previous mechanics
- High-density bullet patterns
- Sustained concentration and dodging skill

## Boss Health Bar Display

### Rendering

Rendered at top of screen (above the 60x20 game grid):

```
BOSS: [████████████░░░░░░░░] 65/100 HP
```

**Components:**
- Filled blocks (█) represent current HP
- Empty blocks (░) represent lost HP
- Numeric display: `current_hp/max_hp`
- Visual indicator at 50% mark (phase transition point)
- Bar turns red/flashes when boss enters phase 2

### Implementation

- `BossHealthBarSystem` renders before RenderSystem (priority 7.5)
- Only active when boss entity exists in current room
- Queries for entities with `Boss + Health` components
- Calculates fill percentage: `(current_hp / max_hp) * BOSS_HEALTH_BAR_WIDTH`
- Updates every frame as boss takes damage

## Victory and Defeat Screens

### Victory Screen (Final Boss Defeated)

```
╔════════════════════════════╗
║       VICTORY!             ║
║                            ║
║   You defeated the dungeon ║
║   Final Floor: 3           ║
║   Items Collected: 8       ║
║                            ║
║   Press R to restart       ║
║   Press Q to quit          ║
╚════════════════════════════╝
```

**Trigger:**
- Boss defeated on floor == FINAL_FLOOR
- No trapdoor spawns
- Game state → VICTORY
- Rewards still spawn (player can collect before restart)

### Game Over Screen (Player Died)

```
╔════════════════════════════╗
║       GAME OVER            ║
║                            ║
║   You died on Floor 2      ║
║   Items Collected: 5       ║
║                            ║
║   Press R to restart       ║
║   Press Q to quit          ║
╚════════════════════════════╝
```

**Trigger:**
- Player HP ≤ 0 on any floor
- Game state → GAME_OVER
- Display death floor and items collected

### Restart Logic

**Press R:**
- Reset to Floor 1
- Generate new dungeon
- Reset player to fresh state (full HP, no items)
- Game state → PLAYING
- Maintains session continuity (no relaunch needed)

**Press Q:**
- Exit game

## Edge Cases & Solutions

### 1. Boss Phase Transition Invulnerability

**Problem:** Player could burst boss through phase transition instantly

**Solution:**
- Grant 0.5s invulnerability during phase transition
- Add `Invincible` component to boss when `has_transitioned` set to true
- Remove after 0.5 seconds
- Prevents phase-skipping via explosive tears or high damage

### 2. Player Death During Floor Transition

**Problem:** Floor transition in progress when HP hits 0

**Solution:**
- GameStateSystem checks player HP before other systems process
- Prioritize GAME_OVER state over FLOOR_TRANSITION
- Cancel any in-progress transition if player dies

### 3. Teleport Into Player

**Problem:** Boss teleports on top of player (instant damage)

**Solution:**
- Always validate distance > BOSS_TELEPORT_MIN_PLAYER_DISTANCE before confirming teleport
- Retry with different position if too close
- Max 3 retry attempts, fall back to current position if all fail

### 4. Boss Stuck in Walls

**Problem:** Teleport position calculation error places boss in wall

**Solution:**
- Validate all teleport positions are within arena bounds
- Use pre-defined safe positions 5 units from walls
- Never use procedurally calculated positions

### 5. Multiple Bosses Spawned

**Problem:** Re-entering boss room spawns duplicate boss

**Solution:**
- Check `boss_room.cleared` flag before spawning boss
- Only spawn boss on first entry
- RoomManager sets `cleared = true` when boss dies

### 6. Floor Number Exceeds Final Floor

**Problem:** Player reaches floor 4+ when FINAL_FLOOR = 3

**Solution:**
- Clamp floor number to FINAL_FLOOR in FloorTransitionSystem
- OR: Allow infinite floors with cycling bosses (boss_index % 3)
- Design supports both approaches

### 7. Trapdoor Collision During Combat

**Problem:** Trapdoor spawns while enemies still alive, player could exit early

**Solution:**
- Only spawn trapdoor after boss death AND room cleared
- Lock doors until boss defeated
- Trapdoor spawns after room state → CLEARED

## Testing Strategy

### Unit Tests

1. **Boss phase transition** - Verify phase switches at exactly 50% HP
2. **Pattern generation** - Each pattern creates correct projectile count/angles
3. **Teleport position selection** - Never too close to walls or player
4. **Floor scaling** - Enemy stats multiply correctly by floor number
5. **Trapdoor collision** - Player collision detection works correctly
6. **Game state transitions** - WIN/LOSS states trigger appropriately
7. **Boss invulnerability** - Phase transition grants temporary invincibility

### Integration Tests

1. **Boss fight scenario** - Player vs boss, phase transition, boss defeat
2. **Floor progression** - Complete floor, use trapdoor, verify new floor generation
3. **Boss defeat rewards** - Coins, hearts, items spawn correctly at boss position
4. **Final boss victory** - No trapdoor spawns, victory screen appears
5. **Player death** - Game over state, restart functionality works
6. **Multi-floor run** - Complete Floor 1 → Floor 2 → Floor 3 with victory

### System Integration Tests

1. **BossAISystem + EnemyShootingSystem** - Pattern projectiles spawn correctly
2. **BossHealthBarSystem + RenderSystem** - Health bar renders above game grid
3. **FloorTransitionSystem + RoomManager** - Floor transition generates new dungeon
4. **GameStateSystem + All Systems** - VICTORY/GAME_OVER states pause gameplay

## Success Criteria

- ✅ 3 unique bosses implemented (Floor 1, 2, 3)
- ✅ Each boss has 2 distinct phases with different patterns
- ✅ Geometric attack patterns (spiral, wave, pulse, variants) working
- ✅ Boss teleports between attacks, frequency increases in phase 2
- ✅ Boss health bar displays above arena with phase indicator
- ✅ Floor difficulty scales correctly (enemy HP, damage, counts)
- ✅ Floor transitions work (trapdoor spawns, new dungeon generated)
- ✅ Victory condition triggers on final boss defeat
- ✅ Game over condition triggers on player death
- ✅ Restart functionality works from victory/game over screens
- ✅ All edge cases handled (phase skip, teleport validation, etc.)
- ✅ No regressions in existing gameplay
- ✅ All tests passing (50+ new tests expected)

## Dependencies

**Existing Systems:**
- RoomManager - Modified for boss spawning and floor tracking
- CollisionSystem - Handles trapdoor collision and boss invulnerability
- EnemyShootingSystem - May be reused for boss pattern projectiles
- RenderSystem - Modified to accommodate boss health bar

**New Files:**
- `src/components/boss.py` - Boss, BossAI, Trapdoor components
- `src/systems/boss_ai.py` - BossAISystem for pattern execution
- `src/systems/boss_health_bar.py` - BossHealthBarSystem for UI
- `src/systems/floor_transition.py` - FloorTransitionSystem for progression
- `src/systems/game_state.py` - GameStateSystem for win/loss management
- `src/entities/bosses.py` - Boss entity factory functions
- `src/entities/trapdoor.py` - Trapdoor entity factory
- `tests/test_boss_system.py` - Boss AI and pattern tests
- `tests/test_floor_system.py` - Floor progression tests
- `tests/test_game_state.py` - Win/loss condition tests

## Timeline Estimate

- **Design:** Complete ✅
- **Implementation:** 6-8 hours (complex multi-system feature)
  - Boss components and entities: 1 hour
  - BossAISystem and patterns: 2 hours
  - Floor progression system: 1.5 hours
  - Game state management: 1 hour
  - UI (health bar, victory/game over): 1 hour
  - Testing: 1.5-2 hours
- **Total:** ~6-8 hours for complete feature

## Next Steps

1. Create worktree for isolated development
2. Write detailed implementation plan with TDD steps
3. Implement boss fights and floor progression
4. Run full test suite to verify no regressions
5. Playtest complete 3-floor run
6. Merge to main

---

**Ready for Implementation** - Use superpowers:using-git-worktrees and superpowers:writing-plans to begin.
