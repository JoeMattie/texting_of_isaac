# Phase 3 Completion Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete Phase 3 by adding interpolation (smooth 60 FPS movement) and particle effects.

**Architecture:** InterpolationManager handles position smoothing; ParticleManager wraps @pixi/particle-emitter for visual effects.

**Tech Stack:** TypeScript, Pixi.js v8, @pixi/particle-emitter

---

## Interpolation System

**Architecture:** `InterpolationManager` class tracks previous positions per entity. Each render frame, sprites lerp toward target position. Snap threshold (>5 tiles) triggers immediate positioning for room transitions and spawns.

**Data flow:**
1. `onGameState` stores new positions as targets
2. `app.ticker` calls `interpolationManager.update(dt)`
3. For each entity: `currentPos = lerp(currentPos, targetPos, smoothing * dt)`
4. If distance > threshold: snap immediately
5. Renderer uses interpolated positions instead of raw state

**Config:**
- Smoothing factor: 15 (higher = snappier)
- Snap threshold: 5 tiles (160px)

**New file:** `web/src/interpolation.ts`

---

## Particle System

**Architecture:** `ParticleManager` class wraps @pixi/particle-emitter. Pre-configured emitter templates for each effect type. Colors passed at spawn time based on entity.

**Effect types:**

| Effect | Trigger | Behavior |
|--------|---------|----------|
| Projectile trail | Every frame while projectile exists | Small particles behind projectile, fade quickly |
| Death explosion | Entity removed with health <= 0 | Burst outward from death position |
| Item pickup | Item collected | Sparkle burst upward |
| Door unlock | Room cleared | Brief shimmer effect |

**Color mapping:**
- Player/player projectiles: Blue (#4444ff)
- Enemy projectiles: Red (#ff4444)
- Chaser: Green (#44ff44)
- Shooter: Orange (#ff8844)
- Orbiter: Purple (#aa44ff)
- Turret: Gray (#888888)
- Tank: Brown (#886644)
- Items: Gold (#ffdd44)
- Doors: White (#ffffff)

**New file:** `web/src/particles.ts`

---

## Integration

**Changes to main.ts:**
- Initialize `InterpolationManager` and `ParticleManager`
- On game state: update interpolation targets, detect deaths for explosions
- On ticker: update interpolation, update particles, apply to sprites
- Pass particle container to Pixi stage

**Changes to renderer.ts:**
- InterpolationManager updates sprite positions directly

**Death detection:**
- Compare previous vs current entities
- If entity gone AND had health component → death explosion
- If entity gone AND was item type → pickup sparkle

**Projectile trails:**
- Each frame, emit trail particle at projectile position
- Track projectile owner (player vs enemy) for color

**New dependencies:**
- `@pixi/particle-emitter`

---

## Testing

**Test file:** `web/src/__tests__/interpolation.test.ts`

### Interpolation tests
- lerp returns correct intermediate value
- Snap triggers when distance > threshold
- New entity starts at target position (no lerp from origin)
- Removed entity cleans up state

**Test file:** `web/src/__tests__/particles.test.ts`

### Particle tests
- ParticleManager initializes without errors
- Emitter configs are valid
- Color mapping returns correct colors
- Effect spawn doesn't throw

### Error handling
- Missing entity in interpolation: skip silently
- Invalid position values: clamp/ignore
- Particle spawn failure: log warning, don't crash
