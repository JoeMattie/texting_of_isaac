# Enemy Shooting System Design

**Date:** 2026-01-13
**Status:** Design Approved
**Goal:** Enable enemies to shoot projectiles with varied attack patterns

## Overview

Add enemy shooting capability to make combat bidirectional and challenging. Enemies will have 2-3 attack patterns each that cycle sequentially, creating learnable but varied combat encounters.

## Architecture

### Component Changes

**Extend AIBehavior component:**
- Add `pattern_index: int = 0` - tracks which pattern to use next for cycling
- Keep existing `pattern_cooldowns: Dict[str, float]` - tracks time until next shot

No new components needed - existing components support this feature.

### New System: EnemyShootingSystem

**Purpose:** Execute enemy attack patterns by creating projectiles

**Location:** `src/systems/enemy_shooting.py`

**Processor that:**
1. Queries entities with `Enemy`, `Position`, `AIBehavior` components
2. Checks if any pattern cooldowns have expired (≤ 0)
3. Reads pattern data from ENEMY_DATA based on enemy type
4. Creates projectiles according to pattern config (count, spread, speed)
5. Updates cooldowns and increments pattern_index for cycling

**System Execution Order:**
1. InputSystem (player input)
2. AISystem (enemy movement + cooldown updates)
3. **EnemyShootingSystem** ← NEW (enemy projectile creation)
4. ShootingSystem (player projectile creation)
5. MovementSystem (apply velocities)
6. CollisionSystem (damage and removal)

### Data Structure Changes

**Extend ENEMY_DATA in `src/entities/enemies.py`:**

```python
ENEMY_DATA = {
    "chaser": {
        "hp": 3,
        "speed": 3.0,
        "sprite": ("e", "red"),
        "patterns": {}  # No shooting - pure melee
    },
    "shooter": {
        "hp": 4,
        "speed": 1.5,
        "sprite": ("S", "magenta"),
        "patterns": {
            "aimed": {"count": 1, "spread": 0, "speed": 5.0, "cooldown": 2.0},
            "spread": {"count": 3, "spread": 30, "speed": 4.5, "cooldown": 2.5}
        }
    },
    "orbiter": {
        "hp": 5,
        "speed": 4.0,
        "sprite": ("O", "yellow"),
        "patterns": {
            "aimed": {"count": 1, "spread": 0, "speed": 6.0, "cooldown": 1.5},
            "ring": {"count": 8, "spread": 360, "speed": 4.0, "cooldown": 3.0}
        }
    },
    "turret": {
        "hp": 6,
        "speed": 0.0,
        "sprite": ("T", "red"),
        "patterns": {
            "spray": {"count": 5, "spread": 90, "speed": 5.0, "cooldown": 2.5},
            "cross": {"count": 4, "spread": 360, "speed": 5.5, "cooldown": 3.0}
        }
    },
    "tank": {
        "hp": 10,
        "speed": 2.0,
        "sprite": ("E", "bright_red"),
        "patterns": {
            "shockwave": {"count": 6, "spread": 360, "speed": 3.5, "cooldown": 4.0}
        }
    }
}
```

**Pattern Parameters:**
- `count` (int) - number of bullets to spawn
- `spread` (float) - total angle spread in degrees
- `speed` (float) - projectile velocity
- `cooldown` (float) - seconds between uses

## Pattern Execution Logic

### Algorithm

When EnemyShootingSystem processes an enemy ready to shoot:

1. **Get pattern list** from ENEMY_DATA[enemy.type]["patterns"]
2. **Select pattern** using `pattern_index % len(patterns)` for sequential cycling
3. **Calculate base direction:**
   - Get angle from enemy position to player position
   - `base_angle = atan2(player.y - enemy.y, player.x - enemy.x)`
4. **Spawn bullets with spread:**
   ```python
   if count == 1:
       # Single bullet - shoot in base direction
       angles = [base_angle]
   else:
       # Multiple bullets - distribute across spread
       start_angle = base_angle - (spread / 2) * (π / 180)
       angle_step = spread * (π / 180) / (count - 1)
       angles = [start_angle + i * angle_step for i in range(count)]

   for angle in angles:
       dx = cos(angle) * speed
       dy = sin(angle) * speed
       create_projectile(enemy_pos, dx, dy, damage=1.0, owner=enemy_id)
   ```
5. **Create projectile entities:**
   - Position: enemy's current position
   - Velocity: calculated from angle and speed
   - Projectile component: `Projectile(damage=1.0, owner=enemy_id)`
   - Sprite: `Sprite('*', 'yellow')` for visual distinction
   - Collider: standard projectile hitbox (0.2 radius)
6. **Update state:**
   - Reset cooldown: `pattern_cooldowns[pattern_name] = cooldown`
   - Increment: `pattern_index = (pattern_index + 1) % len(patterns)`

### Special Cases

**Ring Pattern (360° spread):**
- Bullets distribute evenly around full circle
- Ignores player position (radiates outward)
- Example: 8 bullets = 45° apart

**Cross Pattern (Turret):**
- 4 bullets at 0°, 90°, 180°, 270° (cardinal directions)
- Ignores player position (fixed directions)
- Creates predictable but dangerous coverage

## Enemy Pattern Specifications

### Chaser
- **Role:** Pure melee enemy
- **Patterns:** None (empty dict)
- **Behavior:** Only chases, no shooting

### Shooter
- **Role:** Basic ranged enemy
- **Pattern 1 - "aimed":** Single bullet at player
  - Count: 1, Spread: 0°, Speed: 5.0, Cooldown: 2.0s
- **Pattern 2 - "spread":** Three-way cone
  - Count: 3, Spread: 30°, Speed: 4.5, Cooldown: 2.5s
- **Cycle:** aimed → spread → aimed → spread...

### Orbiter
- **Role:** Mobile sniper with area denial
- **Pattern 1 - "aimed":** Fast single bullet
  - Count: 1, Spread: 0°, Speed: 6.0, Cooldown: 1.5s
- **Pattern 2 - "ring":** Eight-way radial burst
  - Count: 8, Spread: 360°, Speed: 4.0, Cooldown: 3.0s
- **Cycle:** aimed → ring → aimed → ring...

### Turret
- **Role:** Stationary coverage enemy
- **Pattern 1 - "spray":** Wide arc of bullets
  - Count: 5, Spread: 90°, Speed: 5.0, Cooldown: 2.5s
- **Pattern 2 - "cross":** Cardinal direction burst
  - Count: 4, Spread: 360°, Speed: 5.5, Cooldown: 3.0s
  - Special: Fixed directions (N, S, E, W), ignores player
- **Cycle:** spray → cross → spray → cross...

### Tank
- **Role:** Slow, high-threat area denial
- **Pattern 1 - "shockwave":** Radial burst
  - Count: 6, Spread: 360°, Speed: 3.5, Cooldown: 4.0s
- **Cycle:** Only one pattern, repeats

## Collision & Visual Differentiation

### Enemy Projectile Appearance
- **Character:** `*` (asterisk) vs player `.` (period)
- **Color:** `yellow` for visibility
- **Hitbox:** Same as player projectiles (0.2 radius)

### Collision System Updates

**Current behavior (keep):**
- Player projectiles damage enemies ✓
- Remove projectile on enemy hit ✓
- Remove enemy when health ≤ 0 ✓

**New behavior (add):**
- Enemy projectiles damage player
- Remove enemy projectile on player hit
- Determine projectile owner by checking `Projectile.owner`:
  ```python
  if world.has_component(projectile.owner, Player):
      # Player's bullet → can hit enemies
  elif world.has_component(projectile.owner, Enemy):
      # Enemy's bullet → can hit player
  ```

**Player Damage Implementation:**
- For now: Just remove projectile when hitting player (prevents pass-through)
- Future: Integrate with player health system (next feature)
- No friendly fire: Enemy projectiles don't damage enemies

### Collision Cases

| Projectile Owner | Target | Action |
|-----------------|--------|--------|
| Player | Enemy | Deal damage, remove projectile, check enemy death |
| Enemy | Player | Remove projectile (damage placeholder) |
| Player | Player | No collision |
| Enemy | Enemy | No collision |

## Testing Strategy

### Unit Tests

**Pattern Selection & Cycling (`test_enemy_shooting_system.py`):**
```python
def test_pattern_cycles_through_list():
    # Enemy with 2 patterns
    # Verify pattern_index: 0 → 1 → 0

def test_single_pattern_stays_at_zero():
    # Tank with 1 pattern
    # Verify pattern_index stays 0
```

**Single Bullet (Aimed Shot):**
```python
def test_creates_single_aimed_bullet():
    # Enemy at (10, 10), player at (20, 10)
    # Trigger "aimed" pattern (count=1, spread=0)
    # Verify: 1 projectile, moving toward player (right)
```

**Spread Pattern:**
```python
def test_creates_spread_bullets():
    # Trigger pattern: count=3, spread=30°
    # Verify: 3 projectiles created
    # Verify: angles are -15°, 0°, +15° from base direction
```

**Ring Pattern:**
```python
def test_creates_ring_bullets():
    # Trigger pattern: count=8, spread=360°
    # Verify: 8 projectiles created
    # Verify: evenly distributed (45° apart)
```

**Cooldown Respect:**
```python
def test_respects_cooldown_timer():
    # Set cooldown to 2.0s
    # Process at dt=0.5s four times
    # Verify: no shooting until 2.0s elapsed
    # Verify: shoots once after 2.0s
```

**Projectile Ownership:**
```python
def test_enemy_projectiles_have_correct_owner():
    # Create shooter enemy
    # Trigger pattern
    # Verify: Projectile.owner == enemy_id
    # Verify: Sprite is ('*', 'yellow')
```

### Integration Tests

**Full Combat Cycle:**
```python
def test_full_enemy_shooting_cycle():
    # Spawn shooter enemy and player
    # Process systems for 3 seconds (90 frames at 30 FPS)
    # Verify: enemy projectiles spawn
    # Verify: projectiles move toward player
    # Verify: collision removes projectiles
```

**No Friendly Fire:**
```python
def test_no_friendly_fire():
    # Spawn 2 enemies close together
    # One shoots through the other
    # Verify: enemy projectile doesn't damage other enemy

def test_player_bullets_dont_hit_player():
    # Player shoots, moves into projectile path
    # Verify: no collision (shouldn't be possible but test anyway)
```

### Manual Testing

1. Run game, spawn Shooter enemy
2. Verify it alternates between single shot and 3-way spread
3. Verify bullets move toward player position when fired
4. Verify bullets are yellow asterisks (*)
5. Verify bullets disappear when hitting player
6. Spawn each enemy type, observe pattern variety

## Implementation Notes

### AIBehavior Component Update

Modify initialization in `src/entities/enemies.py`:
```python
if data["patterns"]:
    esper.add_component(entity, AIBehavior(
        pattern_cooldowns=data["patterns"].copy(),
        pattern_index=0  # Add this
    ))
```

### AISystem Cooldown Update

Extend AISystem to decrement pattern cooldowns:
```python
# In AISystem.process(), for enemies with AIBehavior:
for pattern_name in ai_behavior.pattern_cooldowns:
    ai_behavior.pattern_cooldowns[pattern_name] -= self.dt
```

### EnemyShootingSystem Registration

Add to `src/game/engine.py` after AISystem, before ShootingSystem:
```python
self.enemy_shooting_system = EnemyShootingSystem()
self.world.add_processor(self.enemy_shooting_system, priority=2)
```

## Success Criteria

✓ All 5 enemy types have distinct shooting behaviors
✓ Patterns cycle sequentially and predictably
✓ Bullets spawn with correct count, spread, and speed
✓ Enemy projectiles visually distinct from player projectiles
✓ Collision system handles enemy projectiles correctly
✓ No friendly fire (enemies don't damage each other)
✓ All unit tests pass
✓ Manual testing confirms varied and interesting combat

## Future Enhancements (Not in Scope)

- Player invincibility frames (next feature: player damage system)
- Curved bullet trajectories
- Homing projectiles
- Charge-up attacks
- Conditional pattern selection (distance-based)
- Projectile cleanup (remove off-screen bullets)
