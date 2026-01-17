# Explosive Tears Design

> **Date:** 2026-01-17
> **Status:** Approved - Ready for Implementation

## Overview

Add "explosive tears" special effect that triggers area-of-effect damage when projectiles hit enemies. This Phase 2 feature reuses existing bomb explosion logic to create tactical area damage opportunities.

## Core Concept

**Explosive Tears:**
Projectiles with the "explosive" special effect explode on impact with enemies, dealing reduced damage (50% of bomb damage) to all entities within the bomb's blast radius. This creates tactical depth by rewarding aim at enemy clusters.

**Key Behavior:**
- Explodes on first enemy hit
- Direct hit damage + explosion damage applied
- Same radius as bombs (Config.BOMB_BLAST_RADIUS)
- 50% of bomb damage for explosion (Config.BOMB_DAMAGE * 0.5)
- Overrides piercing behavior (always deletes projectile)
- Works with multi-shot (each projectile explodes independently)

## Architecture

### Design Decisions

1. **No new components** - Use existing special_effects system in CollectedItems
2. **Reuse bomb explosion logic** - Call BombSystem.damage_entities_in_radius() for consistency
3. **Explosion on impact** - Happens in CollisionSystem._projectile_hit_enemy()
4. **Always explodes** - Overrides piercing behavior (prevents overpowered combinations)

### Data Flow

1. Player fires projectile (has explosive effect from CollectedItems)
2. Projectile hits enemy (CollisionSystem detects collision)
3. System checks projectile owner's CollectedItems for "explosive" effect
4. Apply direct hit damage to enemy (normal projectile damage)
5. Trigger explosion at projectile position (BombSystem.damage_entities_in_radius)
6. Delete projectile (even if player has piercing)

## Implementation Details

### Files to Modify

1. **src/data/items.py** - Add "explosive_tears" item definition
2. **src/systems/collision.py** - Modify _projectile_hit_enemy() to detect and trigger explosions
3. **src/systems/bomb.py** - Add optional damage parameter to damage_entities_in_radius()
4. **src/config.py** - Add EXPLOSIVE_TEAR_DAMAGE_MULTIPLIER constant

### Explosive Effect Detection

In CollisionSystem._projectile_hit_enemy(), after applying direct damage:

```python
# Check for explosive effect
has_explosive = False
if esper.entity_exists(proj.owner) and esper.has_component(proj.owner, Player):
    if esper.has_component(proj.owner, CollectedItems):
        collected = esper.component_for_entity(proj.owner, CollectedItems)
        has_explosive = collected.has_effect("explosive")

if has_explosive:
    # Get projectile position for explosion center
    proj_pos = esper.component_for_entity(projectile, Position)

    # Calculate explosion damage (50% of bomb damage)
    explosion_damage = Config.BOMB_DAMAGE * Config.EXPLOSIVE_TEAR_DAMAGE_MULTIPLIER

    # Trigger explosion (reuse bomb system logic)
    self.bomb_system.damage_entities_in_radius(proj_pos, Config.BOMB_BLAST_RADIUS, explosion_damage)

    # Always delete projectile after explosion (overrides piercing)
    esper.delete_entity(projectile)
    return  # Skip piercing check
```

### BombSystem Modification

Update damage_entities_in_radius() signature:

```python
def damage_entities_in_radius(self, center: Position, radius: float, damage: float = None):
    """Deal damage to entities within blast radius.

    Args:
        center: Position of the explosion center
        radius: Blast radius to check for damage
        damage: Damage to apply (defaults to Config.BOMB_DAMAGE)
    """
    if damage is None:
        damage = Config.BOMB_DAMAGE

    # Rest of method unchanged, use 'damage' instead of Config.BOMB_DAMAGE
```

### Config Constants

```python
# Explosive tears
EXPLOSIVE_TEAR_DAMAGE_MULTIPLIER: float = 0.5  # 50% of bomb damage
```

### Item Definition

```python
"explosive_tears": {
    "sprite": "E",
    "color": "orange",
    "stat_modifiers": {
        "damage": 0.3  # +0.3 damage bonus
    },
    "special_effects": ["explosive"]
}
```

### Shop Integration

Add to Config.SHOP_ITEM_PRICES:

```python
"explosive_tears": 15,  # Expensive tier (same as magic_mushroom)
```

## Priority Handling

**Explosive takes precedence over piercing:**

1. Check for explosive effect first
2. If explosive, trigger explosion and delete projectile
3. Return early (skip piercing check)
4. If not explosive, then check for piercing

This ensures predictable behavior and prevents overpowered combinations.

## Testing Strategy

### Unit Tests Required

1. **test_explosive_projectile_triggers_explosion** - Explosive projectile damages enemies in radius
2. **test_explosive_direct_hit_and_explosion_damage** - Enemy takes both direct + explosion damage
3. **test_explosive_overrides_piercing** - Player with both: projectile explodes, doesn't pierce
4. **test_explosive_with_multi_shot** - Each of 3 projectiles creates separate explosion
5. **test_explosive_respects_invincibility** - Explosion doesn't damage player during i-frames
6. **test_explosive_radius_accuracy** - Entities within radius damaged, outside not damaged
7. **test_explosive_without_owner** - Projectile still explodes if owner doesn't exist

### Integration Test

**test_explosive_tears_combat_scenario:**
- Player with explosive tears
- Multiple enemies clustered together
- Fire into cluster
- Verify all enemies take explosion damage
- Verify player can take self-damage from explosion

## Edge Cases

1. **Projectile owner doesn't exist** - Should still explode (check for explosive before checking owner)
2. **Enemy already dead from direct hit** - Explosion still triggers (can damage other nearby enemies)
3. **Player in explosion radius** - Should take damage (no friendly fire protection)
4. **Multiple explosive projectiles** - Each creates independent explosion (multi-shot compatibility)

## Future Enhancements

**Visual Feedback (Not in Scope):**
- Explosion sprite/animation at impact point
- Reuse bomb explosion effect when implemented
- Current implementation works without visuals (damage feedback is sufficient)

**Balance Tuning (After Implementation):**
- Adjust EXPLOSIVE_TEAR_DAMAGE_MULTIPLIER if too strong/weak
- Consider separate EXPLOSIVE_TEAR_RADIUS if bomb radius too large
- Monitor player feedback on self-damage mechanic

## Success Criteria

- ✅ Explosive tears explode on first enemy hit
- ✅ Explosion uses same radius as bombs
- ✅ Explosion deals 50% of bomb damage
- ✅ Direct hit damage + explosion damage both applied
- ✅ Explosive overrides piercing behavior
- ✅ Works with multi-shot (3 independent explosions)
- ✅ Explosion respects invincibility frames
- ✅ Player can take self-damage from explosions
- ✅ All tests passing (no regressions)
- ✅ Item available in shops at appropriate price

## Dependencies

**Existing Systems:**
- BombSystem.damage_entities_in_radius() - Reused for explosion logic
- CollectedItems.has_effect() - Used to detect explosive effect
- CollisionSystem._projectile_hit_enemy() - Where explosion triggers

**No New Dependencies Required**

## Risks & Mitigations

**Risk:** Explosive + multi-shot too powerful (9 enemies hit = 27 total with 3 explosions)
**Mitigation:** 50% damage reduction keeps it balanced, requires good aim

**Risk:** Self-damage frustrating for players
**Mitigation:** Same radius as bombs (players already understand bomb safety), respects invincibility frames

**Risk:** Code duplication between bomb and projectile explosions
**Mitigation:** Reuse BombSystem.damage_entities_in_radius() with optional damage parameter

## Timeline Estimate

- **Design:** Complete ✅
- **Implementation:** 1-2 hours (simple, reuses existing code)
- **Testing:** 30-45 minutes (7 unit tests + 1 integration test)
- **Total:** ~2-3 hours

## Next Steps

1. Create worktree for isolated development
2. Write detailed implementation plan with TDD steps
3. Implement explosive tears feature
4. Run full test suite to verify no regressions
5. Merge to main

---

**Ready for Implementation** - Use superpowers:using-git-worktrees and superpowers:writing-plans to begin.
