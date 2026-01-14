# Player Damage System Design

**Date:** 2026-01-14
**Status:** Design Approved
**Goal:** Implement player damage from enemy projectiles and contact, with invincibility frames and visual feedback

## Overview

Add bidirectional damage to make combat challenging and strategic. Player takes damage from enemy projectiles and contact, gains brief invincibility frames after being hit, and has visual feedback during invincibility. Death is tracked with a marker component for future game over implementation.

## Architecture

### New Components

**Dead (marker component)**

Location: `src/components/game.py`

```python
class Dead:
    """Marker component indicating entity has died."""

    def __repr__(self) -> str:
        return "Dead()"
```

Simple presence indicates death. Future game over system queries for `Player + Dead`.

### New System: InvincibilitySystem

**Purpose:** Decrement invincibility timers and remove expired invincibility

**Location:** `src/systems/invincibility.py`

```python
class InvincibilitySystem(esper.Processor):
    """Decrements invincibility timers."""

    def __init__(self):
        self.dt = 0.0

    def process(self):
        """Update all invincibility timers."""
        for ent, (invincible,) in esper.get_components(Invincible):
            invincible.remaining -= self.dt

            if invincible.remaining <= 0:
                esper.remove_component(ent, Invincible)
```

**System Execution Order (updated):**
1. InputSystem (priority 0)
2. AISystem (priority 1)
3. EnemyShootingSystem (priority 2)
4. ShootingSystem (priority 3)
5. MovementSystem (priority 4)
6. CollisionSystem (priority 5)
7. **InvincibilitySystem (priority 6)** ← NEW
8. RenderSystem (priority 7)

### Modified System: CollisionSystem

**Updates to `_projectile_hit_player()`:**

```python
def _projectile_hit_player(self, projectile: int, player: int):
    """Handle enemy projectile hitting player."""
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

**New method `_enemy_contact_player()` for contact damage:**

Add collision cases to `_handle_collision()`:
```python
# Enemy touching player (contact damage)
if esper.has_component(e1, Enemy) and esper.has_component(e2, Player):
    self._enemy_contact_player(e1, e2)
elif esper.has_component(e2, Enemy) and esper.has_component(e1, Player):
    self._enemy_contact_player(e2, e1)
```

Implementation:
```python
def _enemy_contact_player(self, enemy: int, player: int):
    """Handle enemy touching player (contact damage)."""
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

### Modified System: RenderSystem

**Sprite Flashing During Invincibility:**

In `_render_entity()`, check for invincibility and flash sprite:

```python
def _render_entity(self, entity, grid):
    pos = esper.component_for_entity(entity, Position)
    sprite = esper.component_for_entity(entity, Sprite)

    # Handle invincibility flashing for player
    color = sprite.color
    if esper.has_component(entity, Player) and esper.has_component(entity, Invincible):
        # Flash every 0.1 seconds (10 FPS flash rate)
        invincible = esper.component_for_entity(entity, Invincible)
        # Use elapsed time: (duration - remaining)
        elapsed = Config.INVINCIBILITY_DURATION - invincible.remaining
        if (elapsed % 0.2) < 0.1:
            color = 'white'  # Flash to white
        # else: keep original 'cyan'

    # Render at position with flashed color
    # ...existing rendering logic with modified color...
```

**Flash Pattern:**
- Toggle between cyan and white every 0.1 seconds
- Based on elapsed time since invincibility started
- 0.0-0.1s: white, 0.1-0.2s: cyan, 0.2-0.3s: white, etc.

## Damage Rules

### Projectile Damage

**Enemy projectile hits player:**
- Check invincibility → If invincible, remove projectile only
- Apply damage from `Projectile.damage` (typically 1.0)
- Grant invincibility for `Config.INVINCIBILITY_DURATION` (0.5s)
- Remove projectile
- Check if health ≤ 0, add Dead component

### Contact Damage

**Enemy touches player:**
- Check invincibility → If invincible, no damage
- Apply 1.0 damage (1 heart)
- Grant invincibility for 0.5s
- Check if health ≤ 0, add Dead component

### Invincibility Behavior

**Complete immunity:**
- Player cannot take damage from any source while Invincible component exists
- Projectiles still removed on contact (visual feedback)
- Enemy contact detected but no damage dealt
- Invincibility does not stack or refresh - first hit starts timer

**Timer expiration:**
- InvincibilitySystem decrements `Invincible.remaining` by dt
- When remaining ≤ 0, component is removed
- Player can be damaged again

## Visual Feedback

**Sprite Flashing:**
- Player sprite alternates between 'cyan' (normal) and 'white' (flash)
- Flash rate: 10 Hz (every 0.1 seconds)
- Pattern continues for entire invincibility duration (0.5s total)
- Uses elapsed time calculation: `(INVINCIBILITY_DURATION - remaining)`
- Flash determination: `if (elapsed % 0.2) < 0.1: white else: cyan`

**No other visual changes:**
- Position unchanged
- Character '@' unchanged
- Only color alternates

## Death Handling

**When health reaches 0:**
- Add `Dead` marker component to player entity
- Player entity remains in world (not deleted)
- Game continues running (movement, rendering still work)
- Future game over system will detect `Player + Dead` and handle:
  - Freeze game state
  - Show death screen
  - Respawn or game over menu

**Current implementation:**
- Just adds Dead component
- No game state changes
- Allows incremental implementation of game over flow

## Configuration

**Existing constants used:**
- `Config.INVINCIBILITY_DURATION = 0.5` (seconds)
- `Config.PLAYER_MAX_HP = 6` (hearts)

**No new constants needed.**

## Testing Strategy

### Unit Tests

**Projectile Damage (`test_collision_system.py`):**
```python
def test_projectile_damages_player():
    """Test enemy projectile reduces player health."""
    # Player with 3 HP
    # Enemy projectile with 1.0 damage hits
    # Verify health = 2.0
    # Verify Invincible component added
    # Verify projectile removed

def test_projectile_respects_invincibility():
    """Test projectile doesn't damage invincible player."""
    # Player with 3 HP and Invincible component
    # Enemy projectile hits
    # Verify health still 3.0
    # Verify projectile removed
```

**Contact Damage (`test_collision_system.py`):**
```python
def test_enemy_contact_damages_player():
    """Test touching enemy deals 1 damage."""
    # Player with 3 HP
    # Enemy overlaps player position
    # Verify health = 2.0
    # Verify Invincible component added

def test_enemy_contact_respects_invincibility():
    """Test touching enemy while invincible doesn't damage."""
    # Player with 3 HP and Invincible component
    # Enemy overlaps player
    # Verify health still 3.0
```

**Death Handling (`test_collision_system.py`):**
```python
def test_player_death_on_zero_health():
    """Test Dead component added when health reaches 0."""
    # Player with 1 HP
    # Enemy projectile deals 1 damage
    # Verify health = 0.0
    # Verify Dead component added

def test_player_death_on_negative_health():
    """Test Dead component added even if damage exceeds remaining HP."""
    # Player with 1 HP
    # Enemy projectile deals 2 damage
    # Verify health < 0
    # Verify Dead component added
```

**Invincibility System (`test_invincibility_system.py`):**
```python
def test_invincibility_system_decrements_timer():
    """Test InvincibilitySystem reduces remaining time."""
    # Player with Invincible(remaining=0.5)
    # Process system with dt=0.1
    # Verify remaining = 0.4

def test_invincibility_removed_when_expired():
    """Test Invincible component removed at 0."""
    # Player with Invincible(remaining=0.05)
    # Process system with dt=0.1
    # Verify Invincible component removed

def test_invincibility_system_handles_multiple_entities():
    """Test system handles multiple invincible entities."""
    # Player1 with Invincible(0.5)
    # Player2 with Invincible(0.1)
    # Process with dt=0.15
    # Verify Player1 still has Invincible(0.35)
    # Verify Player2 has no Invincible component
```

**Visual Feedback (`test_render_system.py`):**
```python
def test_sprite_flashes_during_invincibility():
    """Test RenderSystem alternates player color during invincibility."""
    # Player with Invincible(remaining=0.45) [elapsed=0.05]
    # Render entity
    # Verify color = 'white' (elapsed 0.05 < 0.1)

    # Update to Invincible(remaining=0.35) [elapsed=0.15]
    # Render entity
    # Verify color = 'cyan' (0.1 <= elapsed 0.15 < 0.2)

def test_sprite_normal_color_without_invincibility():
    """Test player uses normal color when not invincible."""
    # Player without Invincible component
    # Render entity
    # Verify color = 'cyan'
```

### Integration Tests

**Full Damage Cycle (`test_integration.py`):**
```python
def test_player_damage_and_invincibility_cycle():
    """Test complete damage flow from hit to recovery."""
    # Create player with 3 HP
    # Create enemy projectile
    # Step 1: Collision deals damage
    # Verify health = 2.0, Invincible added, projectile removed

    # Step 2: During invincibility (0.3s elapsed)
    # Create another projectile
    # Verify collision but no damage, health still 2.0

    # Step 3: After invincibility expires (0.6s total)
    # Create another projectile
    # Verify damage dealt, health = 1.0

def test_contact_damage_flow():
    """Test enemy contact damage and recovery."""
    # Player with 2 HP
    # Enemy at player position
    # Verify contact damage dealt (health = 1.0)
    # Verify invincibility prevents immediate second hit
    # Advance time past invincibility
    # Verify can be damaged again
```

### Manual Testing

1. Run game with `uv run python main.py`
2. Let enemy projectile hit you → Verify health decreases, sprite flashes
3. During flash, get hit again → Verify no damage
4. Wait for flash to stop → Get hit again → Verify damage dealt
5. Touch an enemy → Verify contact damage, sprite flashes
6. Take enough damage to reach 0 HP → Verify Dead component (check logs or tests)

## Implementation Notes

### Component Availability

**Already exists:**
- `Health` component (tracks current/max HP)
- `Invincible` component (has `remaining` float field)
- `Player` marker component
- `Enemy` marker component

**Need to add:**
- `Dead` marker component

### System Registration

Add to `src/game/engine.py` after CollisionSystem:

```python
self.invincibility_system = InvincibilitySystem()
self.world.add_processor(self.invincibility_system, priority=6)
```

Update RenderSystem priority to 7.

### Collision System Notes

- Current `_handle_collision()` checks projectile-enemy and projectile-player
- Need to add enemy-player contact checks
- Use same invincibility checking pattern for both damage types
- Death check is identical in both cases (health ≤ 0 → add Dead)

### RenderSystem Notes

- Current rendering loops through entities with Position + Sprite
- Modify `_render_entity()` helper (or inline in loop)
- Use `esper.has_component()` checks for Player and Invincible
- Calculate elapsed time, determine flash color
- Pass modified color to rendering logic

## Success Criteria

✓ Player takes damage from enemy projectiles
✓ Player takes contact damage from touching enemies
✓ Invincibility prevents damage for 0.5 seconds after hit
✓ Sprite flashes white/cyan during invincibility
✓ Dead component added when health reaches 0
✓ InvincibilitySystem decrements and removes expired invincibility
✓ All unit tests pass
✓ Manual testing confirms damage, invincibility, and visual feedback

## Future Enhancements (Not in Scope)

- Game over screen and state management
- Respawn mechanics
- Multiple lives system
- Knockback on damage
- Sound effects for damage
- Screen shake on damage
- Health UI display
- Heart pickup items
