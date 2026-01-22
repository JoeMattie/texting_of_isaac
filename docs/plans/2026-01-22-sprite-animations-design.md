# Sprite Animations Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add procedural animations to the web frontend for all entity types.

**Architecture:** AnimationManager class applies visual transforms (scale, rotation, alpha, offset) each frame. Continuous animations use elapsed time; triggered animations are one-shots detected via state changes.

**Tech Stack:** TypeScript, Pixi.js

---

## Architecture

The animation system is a new `AnimationManager` class that runs alongside the existing `GameRenderer`. Rather than modifying sprite positions directly, it applies visual transforms each frame based on elapsed time.

**Animation types:**
- **Bob**: Sinusoidal Y offset over time
- **Pulse**: Sinusoidal scale oscillation
- **Rotate**: Continuous rotation at fixed speed
- **Flash**: Temporary alpha flicker (triggered by events)
- **Stretch**: Scale in direction of movement

**Data flow:**
1. `GameRenderer` creates/updates sprites as before
2. `AnimationManager.update(dt)` runs each frame
3. For each sprite, applies animation transforms based on entity type
4. Triggered animations (flash on hit, pulse on shoot) come from game state changes

**Files to create:**
- `web/src/animations.ts` - AnimationManager class + animation configs

**Files to modify:**
- `web/src/main.ts` - Initialize AnimationManager, hook into ticker
- `web/src/renderer.ts` - Expose sprite map to AnimationManager

---

## Animation Configurations

### Player
- Bob: 2px amplitude, 2Hz frequency (gentle float)
- Shoot pulse: Scale to 1.2x over 100ms, return to 1.0 over 100ms
- Hit flash: Alpha flickers 0.3→1.0 three times over 300ms

### Enemies (unique per type)
- **Chaser**: Aggressive wobble (rotation ±15° at 8Hz) - frantic, pursuing feel
- **Shooter**: Slow pulse (scale 1.0→1.1 at 1Hz) - breathing, aiming feel
- **Orbiter**: Continuous rotation (90°/sec) - matches their circular movement
- **Turret**: Very slow rotation (30°/sec) + no bob - stationary, mechanical
- **Tank**: Subtle bob (1px at 0.5Hz) - heavy, lumbering feel

### Projectiles
- Player projectiles: Rotate at 360°/sec (fast spin)
- Enemy projectiles: Pulse scale 0.8→1.2 at 4Hz (menacing throb)

### Pickups (hearts, coins, bombs, items)
- Bob: 3px amplitude, 1.5Hz (floaty, inviting)
- Sparkle pulse: Scale 1.0→1.15 at 2Hz (attention-grabbing)

### Doors
- Idle: None (static)
- When unlocked: Single pulse to 1.2x then back (feedback that room is cleared)

---

## Implementation Details

### AnimationManager class structure
```typescript
class AnimationManager {
  private sprites: Map<number, PIXI.Sprite>  // Reference from renderer
  private entityTypes: Map<number, EntityType>  // Track what each entity is
  private triggeredAnims: Map<number, TriggeredAnim[]>  // Active one-shot anims
  private elapsed: number  // Global time for continuous anims
}
```

### Continuous animations
Bob, rotate, and pulse use global elapsed time:
- `offset = amplitude * Math.sin(elapsed * frequency * 2 * Math.PI)`
- Applied fresh each frame based on entity type config

### Triggered animations
Flash and shoot pulse are one-shots:
- Stored in `triggeredAnims` map with start time and duration
- Removed when complete
- Triggered by detecting state changes (health decreased = hit, new projectile from player = shoot)

### State change detection
- Track previous frame's entity states
- Compare health values to detect hits
- Compare projectile counts to detect shooting
- Avoids needing server-side animation events

### Performance
- Only animate visible entities (already filtered by renderer)
- Use simple math (sin/cos) - no physics
- ~200 entities max at 30fps is trivial for modern browsers

---

## Testing

**Test file:** `web/src/__tests__/animations.test.ts`

### Key test cases
- Bob animation returns correct Y offset for given time
- Pulse animation returns correct scale for given time
- Triggered animation expires after duration
- Multiple triggered animations on same entity stack correctly
- Entity removal cleans up animation state

### Error handling
- Missing sprite reference: Skip animation silently (entity may have died)
- Unknown entity type: Apply no animation (fallback to static)
- NaN/Infinity in calculations: Clamp to safe values, log warning

### Graceful degradation
- If AnimationManager fails to initialize, game still works (just no animations)
- Individual animation failures don't crash the render loop
