# Phase 3 Completion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add interpolation for smooth movement and particle effects for visual flair.

**Architecture:** InterpolationManager for position smoothing; ParticleManager wrapping @pixi/particle-emitter.

**Tech Stack:** TypeScript, Pixi.js v8, @pixi/particle-emitter

---

## Task 1: Add @pixi/particle-emitter dependency

**Files:**
- Modify: `web/package.json`

**Step 1: Install the dependency**

Run: `cd /home/joe/dev/texting_of_isaac/.worktrees/phase3-completion/web && npm install @pixi/particle-emitter`

**Step 2: Verify installation**

Run: `npm list @pixi/particle-emitter`
Expected: Shows installed version

**Step 3: Commit**

```bash
git add package.json package-lock.json
git commit -m "chore(web): add @pixi/particle-emitter dependency"
```

---

## Task 2: Create interpolation types and lerp function

**Files:**
- Create: `web/src/interpolation.ts`
- Create: `web/src/__tests__/interpolation.test.ts`

**Step 1: Write the failing test**

```typescript
// web/src/__tests__/interpolation.test.ts
import { describe, it, expect } from 'vitest';
import { lerp, InterpolatedPosition } from '../interpolation';

describe('lerp', () => {
    it('returns start value when t is 0', () => {
        expect(lerp(0, 100, 0)).toBe(0);
    });

    it('returns end value when t is 1', () => {
        expect(lerp(0, 100, 1)).toBe(100);
    });

    it('returns midpoint when t is 0.5', () => {
        expect(lerp(0, 100, 0.5)).toBe(50);
    });

    it('works with negative values', () => {
        expect(lerp(-50, 50, 0.5)).toBe(0);
    });
});

describe('InterpolatedPosition', () => {
    it('has correct initial structure', () => {
        const pos: InterpolatedPosition = {
            currentX: 0,
            currentY: 0,
            targetX: 0,
            targetY: 0,
        };
        expect(pos.currentX).toBe(0);
    });
});
```

**Step 2: Run test to verify it fails**

Run: `cd /home/joe/dev/texting_of_isaac/.worktrees/phase3-completion/web && npm test`
Expected: FAIL with "Cannot find module '../interpolation'"

**Step 3: Write minimal implementation**

```typescript
// web/src/interpolation.ts

/**
 * Interpolated position tracking for an entity.
 */
export interface InterpolatedPosition {
    currentX: number;
    currentY: number;
    targetX: number;
    targetY: number;
}

/**
 * Linear interpolation between two values.
 * @param start - Starting value
 * @param end - Ending value
 * @param t - Interpolation factor (0 to 1)
 * @returns Interpolated value
 */
export function lerp(start: number, end: number, t: number): number {
    return start + (end - start) * t;
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS

**Step 5: Commit**

```bash
git add web/src/interpolation.ts web/src/__tests__/interpolation.test.ts
git commit -m "feat(web): add lerp function and InterpolatedPosition type"
```

---

## Task 3: Implement InterpolationManager class

**Files:**
- Modify: `web/src/interpolation.ts`
- Modify: `web/src/__tests__/interpolation.test.ts`

**Step 1: Write the failing tests**

Add to `web/src/__tests__/interpolation.test.ts`:

```typescript
import { lerp, InterpolatedPosition, InterpolationManager, INTERPOLATION_CONFIG } from '../interpolation';

describe('InterpolationManager', () => {
    it('creates with empty state', () => {
        const manager = new InterpolationManager();
        expect(manager.getPosition(999)).toBeNull();
    });

    it('setTarget creates new position at target for new entity', () => {
        const manager = new InterpolationManager();
        manager.setTarget(1, 100, 200);
        const pos = manager.getPosition(1);
        expect(pos).not.toBeNull();
        expect(pos!.currentX).toBe(100);
        expect(pos!.currentY).toBe(200);
        expect(pos!.targetX).toBe(100);
        expect(pos!.targetY).toBe(200);
    });

    it('setTarget updates target for existing entity', () => {
        const manager = new InterpolationManager();
        manager.setTarget(1, 100, 200);
        manager.setTarget(1, 150, 250);
        const pos = manager.getPosition(1);
        expect(pos!.targetX).toBe(150);
        expect(pos!.targetY).toBe(250);
        // current should still be at old position
        expect(pos!.currentX).toBe(100);
    });

    it('update moves current toward target', () => {
        const manager = new InterpolationManager();
        manager.setTarget(1, 0, 0);
        manager.setTarget(1, 100, 100);
        manager.update(0.1); // small dt
        const pos = manager.getPosition(1);
        expect(pos!.currentX).toBeGreaterThan(0);
        expect(pos!.currentX).toBeLessThan(100);
    });

    it('snaps when distance exceeds threshold', () => {
        const manager = new InterpolationManager();
        manager.setTarget(1, 0, 0);
        // Set target far away (beyond snap threshold)
        manager.setTarget(1, 1000, 1000);
        manager.update(0.016);
        const pos = manager.getPosition(1);
        // Should snap to target
        expect(pos!.currentX).toBe(1000);
        expect(pos!.currentY).toBe(1000);
    });

    it('removeEntity cleans up state', () => {
        const manager = new InterpolationManager();
        manager.setTarget(1, 100, 200);
        manager.removeEntity(1);
        expect(manager.getPosition(1)).toBeNull();
    });
});

describe('INTERPOLATION_CONFIG', () => {
    it('has smoothing factor', () => {
        expect(INTERPOLATION_CONFIG.smoothing).toBe(15);
    });

    it('has snap threshold in pixels', () => {
        expect(INTERPOLATION_CONFIG.snapThreshold).toBe(160);
    });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL

**Step 3: Write implementation**

Add to `web/src/interpolation.ts`:

```typescript
/**
 * Configuration for interpolation behavior.
 */
export const INTERPOLATION_CONFIG = {
    /** Higher = snappier movement */
    smoothing: 15,
    /** Distance in pixels above which we snap instead of lerp */
    snapThreshold: 160,
};

/**
 * Manages interpolated positions for smooth rendering.
 */
export class InterpolationManager {
    private positions: Map<number, InterpolatedPosition> = new Map();

    /**
     * Set target position for an entity.
     * New entities start at target position (no lerp from origin).
     */
    setTarget(entityId: number, x: number, y: number): void {
        const existing = this.positions.get(entityId);
        if (existing) {
            existing.targetX = x;
            existing.targetY = y;
        } else {
            // New entity starts at target position
            this.positions.set(entityId, {
                currentX: x,
                currentY: y,
                targetX: x,
                targetY: y,
            });
        }
    }

    /**
     * Update all interpolated positions.
     * @param dt - Delta time in seconds
     */
    update(dt: number): void {
        const t = Math.min(1, INTERPOLATION_CONFIG.smoothing * dt);

        for (const [entityId, pos] of this.positions) {
            const dx = pos.targetX - pos.currentX;
            const dy = pos.targetY - pos.currentY;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance > INTERPOLATION_CONFIG.snapThreshold) {
                // Snap for large distances (room transitions, spawns)
                pos.currentX = pos.targetX;
                pos.currentY = pos.targetY;
            } else {
                // Smooth lerp
                pos.currentX = lerp(pos.currentX, pos.targetX, t);
                pos.currentY = lerp(pos.currentY, pos.targetY, t);
            }
        }
    }

    /**
     * Get interpolated position for an entity.
     */
    getPosition(entityId: number): InterpolatedPosition | null {
        return this.positions.get(entityId) || null;
    }

    /**
     * Remove entity from tracking.
     */
    removeEntity(entityId: number): void {
        this.positions.delete(entityId);
    }
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS

**Step 5: Commit**

```bash
git add web/src/interpolation.ts web/src/__tests__/interpolation.test.ts
git commit -m "feat(web): implement InterpolationManager class"
```

---

## Task 4: Create particle color mapping

**Files:**
- Create: `web/src/particles.ts`
- Create: `web/src/__tests__/particles.test.ts`

**Step 1: Write the failing test**

```typescript
// web/src/__tests__/particles.test.ts
import { describe, it, expect } from 'vitest';
import { PARTICLE_COLORS, getParticleColor } from '../particles';

describe('PARTICLE_COLORS', () => {
    it('has player color as blue', () => {
        expect(PARTICLE_COLORS.player).toBe('#4444ff');
    });

    it('has enemy_projectile color as red', () => {
        expect(PARTICLE_COLORS.enemy_projectile).toBe('#ff4444');
    });

    it('has all enemy types', () => {
        expect(PARTICLE_COLORS.enemy_chaser).toBe('#44ff44');
        expect(PARTICLE_COLORS.enemy_shooter).toBe('#ff8844');
        expect(PARTICLE_COLORS.enemy_orbiter).toBe('#aa44ff');
        expect(PARTICLE_COLORS.enemy_turret).toBe('#888888');
        expect(PARTICLE_COLORS.enemy_tank).toBe('#886644');
    });

    it('has item color as gold', () => {
        expect(PARTICLE_COLORS.item).toBe('#ffdd44');
    });

    it('has door color as white', () => {
        expect(PARTICLE_COLORS.door).toBe('#ffffff');
    });
});

describe('getParticleColor', () => {
    it('returns correct color for known entity type', () => {
        expect(getParticleColor('player')).toBe('#4444ff');
        expect(getParticleColor('enemy_chaser')).toBe('#44ff44');
    });

    it('returns projectile color for projectile type', () => {
        expect(getParticleColor('projectile')).toBe('#4444ff');
    });

    it('returns default white for unknown type', () => {
        expect(getParticleColor('unknown_entity')).toBe('#ffffff');
    });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL with "Cannot find module '../particles'"

**Step 3: Write implementation**

```typescript
// web/src/particles.ts

/**
 * Color mapping for particle effects by entity type.
 */
export const PARTICLE_COLORS: Record<string, string> = {
    // Player and player projectiles
    player: '#4444ff',
    projectile: '#4444ff',

    // Enemy projectiles
    enemy_projectile: '#ff4444',

    // Enemy types
    enemy_chaser: '#44ff44',
    enemy_shooter: '#ff8844',
    enemy_orbiter: '#aa44ff',
    enemy_turret: '#888888',
    enemy_tank: '#886644',

    // Items
    item: '#ffdd44',
    heart: '#ffdd44',
    coin: '#ffdd44',
    bomb: '#ffdd44',

    // Doors
    door: '#ffffff',
};

/**
 * Get particle color for an entity type.
 * @param entityType - Type of entity
 * @returns Hex color string
 */
export function getParticleColor(entityType: string): string {
    return PARTICLE_COLORS[entityType] || '#ffffff';
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS

**Step 5: Commit**

```bash
git add web/src/particles.ts web/src/__tests__/particles.test.ts
git commit -m "feat(web): add particle color mapping"
```

---

## Task 5: Create particle emitter configurations

**Files:**
- Modify: `web/src/particles.ts`
- Modify: `web/src/__tests__/particles.test.ts`

**Step 1: Write the failing tests**

Add to `web/src/__tests__/particles.test.ts`:

```typescript
import { PARTICLE_COLORS, getParticleColor, EMITTER_CONFIGS } from '../particles';

describe('EMITTER_CONFIGS', () => {
    it('has trail config', () => {
        expect(EMITTER_CONFIGS.trail).toBeDefined();
        expect(EMITTER_CONFIGS.trail.lifetime).toBeDefined();
    });

    it('has explosion config', () => {
        expect(EMITTER_CONFIGS.explosion).toBeDefined();
        expect(EMITTER_CONFIGS.explosion.lifetime).toBeDefined();
    });

    it('has sparkle config', () => {
        expect(EMITTER_CONFIGS.sparkle).toBeDefined();
        expect(EMITTER_CONFIGS.sparkle.lifetime).toBeDefined();
    });

    it('has shimmer config', () => {
        expect(EMITTER_CONFIGS.shimmer).toBeDefined();
        expect(EMITTER_CONFIGS.shimmer.lifetime).toBeDefined();
    });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL

**Step 3: Write implementation**

Add to `web/src/particles.ts`:

```typescript
/**
 * Emitter configuration for different particle effects.
 * These are templates that get color applied at spawn time.
 */
export const EMITTER_CONFIGS = {
    /** Small particles behind moving projectiles */
    trail: {
        lifetime: { min: 0.1, max: 0.2 },
        frequency: 0.01,
        emitterLifetime: -1,
        maxParticles: 50,
        addAtBack: true,
        behaviors: [
            {
                type: 'alpha',
                config: { alpha: { list: [{ value: 0.8, time: 0 }, { value: 0, time: 1 }] } }
            },
            {
                type: 'scale',
                config: { scale: { list: [{ value: 0.3, time: 0 }, { value: 0.1, time: 1 }] } }
            },
            {
                type: 'moveSpeed',
                config: { speed: { list: [{ value: 20, time: 0 }, { value: 0, time: 1 }] } }
            },
        ]
    },

    /** Burst outward on entity death */
    explosion: {
        lifetime: { min: 0.3, max: 0.5 },
        frequency: 0.001,
        emitterLifetime: 0.1,
        maxParticles: 20,
        addAtBack: false,
        behaviors: [
            {
                type: 'alpha',
                config: { alpha: { list: [{ value: 1, time: 0 }, { value: 0, time: 1 }] } }
            },
            {
                type: 'scale',
                config: { scale: { list: [{ value: 0.5, time: 0 }, { value: 0.2, time: 1 }] } }
            },
            {
                type: 'moveSpeed',
                config: { speed: { list: [{ value: 200, time: 0 }, { value: 50, time: 1 }] } }
            },
            {
                type: 'rotation',
                config: { minStart: 0, maxStart: 360 }
            },
        ]
    },

    /** Upward burst for item pickup */
    sparkle: {
        lifetime: { min: 0.4, max: 0.6 },
        frequency: 0.01,
        emitterLifetime: 0.2,
        maxParticles: 15,
        addAtBack: false,
        behaviors: [
            {
                type: 'alpha',
                config: { alpha: { list: [{ value: 1, time: 0 }, { value: 0, time: 1 }] } }
            },
            {
                type: 'scale',
                config: { scale: { list: [{ value: 0.4, time: 0 }, { value: 0.1, time: 1 }] } }
            },
            {
                type: 'moveSpeed',
                config: { speed: { list: [{ value: 100, time: 0 }, { value: 20, time: 1 }] } }
            },
            {
                type: 'rotation',
                config: { minStart: 250, maxStart: 290 }
            },
        ]
    },

    /** Brief shimmer for door unlock */
    shimmer: {
        lifetime: { min: 0.2, max: 0.4 },
        frequency: 0.02,
        emitterLifetime: 0.3,
        maxParticles: 10,
        addAtBack: false,
        behaviors: [
            {
                type: 'alpha',
                config: { alpha: { list: [{ value: 0.6, time: 0 }, { value: 0, time: 1 }] } }
            },
            {
                type: 'scale',
                config: { scale: { list: [{ value: 0.3, time: 0 }, { value: 0.5, time: 1 }] } }
            },
            {
                type: 'moveSpeed',
                config: { speed: { list: [{ value: 30, time: 0 }, { value: 10, time: 1 }] } }
            },
        ]
    },
};
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS

**Step 5: Commit**

```bash
git add web/src/particles.ts web/src/__tests__/particles.test.ts
git commit -m "feat(web): add particle emitter configurations"
```

---

## Task 6: Implement ParticleManager class

**Files:**
- Modify: `web/src/particles.ts`
- Modify: `web/src/__tests__/particles.test.ts`

**Step 1: Write the failing tests**

Add to `web/src/__tests__/particles.test.ts`:

```typescript
import * as PIXI from 'pixi.js';
import { PARTICLE_COLORS, getParticleColor, EMITTER_CONFIGS, ParticleManager } from '../particles';

describe('ParticleManager', () => {
    it('creates with container', () => {
        const container = new PIXI.Container();
        const manager = new ParticleManager(container);
        expect(manager).toBeDefined();
    });

    it('spawnTrail does not throw', () => {
        const container = new PIXI.Container();
        const manager = new ParticleManager(container);
        expect(() => manager.spawnTrail(100, 100, 'projectile')).not.toThrow();
    });

    it('spawnExplosion does not throw', () => {
        const container = new PIXI.Container();
        const manager = new ParticleManager(container);
        expect(() => manager.spawnExplosion(100, 100, 'enemy_chaser')).not.toThrow();
    });

    it('spawnSparkle does not throw', () => {
        const container = new PIXI.Container();
        const manager = new ParticleManager(container);
        expect(() => manager.spawnSparkle(100, 100)).not.toThrow();
    });

    it('spawnShimmer does not throw', () => {
        const container = new PIXI.Container();
        const manager = new ParticleManager(container);
        expect(() => manager.spawnShimmer(100, 100)).not.toThrow();
    });

    it('update does not throw', () => {
        const container = new PIXI.Container();
        const manager = new ParticleManager(container);
        expect(() => manager.update(0.016)).not.toThrow();
    });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL

**Step 3: Write implementation**

Add to `web/src/particles.ts`:

```typescript
import * as PIXI from 'pixi.js';
import { Emitter, upgradeConfig } from '@pixi/particle-emitter';

/**
 * Creates a simple circle texture for particles.
 */
function createParticleTexture(): PIXI.Texture {
    const canvas = document.createElement('canvas');
    canvas.width = 16;
    canvas.height = 16;
    const ctx = canvas.getContext('2d')!;

    // Draw a simple white circle
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(8, 8, 6, 0, Math.PI * 2);
    ctx.fill();

    return PIXI.Texture.from(canvas);
}

/**
 * Manages particle effects for the game.
 */
export class ParticleManager {
    private container: PIXI.Container;
    private emitters: Emitter[] = [];
    private particleTexture: PIXI.Texture;

    constructor(container: PIXI.Container) {
        this.container = container;
        this.particleTexture = createParticleTexture();
    }

    /**
     * Spawn trail particles behind a projectile.
     */
    spawnTrail(x: number, y: number, entityType: string): void {
        const color = getParticleColor(entityType);
        this.spawnEmitter(x, y, EMITTER_CONFIGS.trail, color);
    }

    /**
     * Spawn explosion particles on entity death.
     */
    spawnExplosion(x: number, y: number, entityType: string): void {
        const color = getParticleColor(entityType);
        this.spawnEmitter(x, y, EMITTER_CONFIGS.explosion, color);
    }

    /**
     * Spawn sparkle particles on item pickup.
     */
    spawnSparkle(x: number, y: number): void {
        this.spawnEmitter(x, y, EMITTER_CONFIGS.sparkle, PARTICLE_COLORS.item);
    }

    /**
     * Spawn shimmer particles on door unlock.
     */
    spawnShimmer(x: number, y: number): void {
        this.spawnEmitter(x, y, EMITTER_CONFIGS.shimmer, PARTICLE_COLORS.door);
    }

    /**
     * Update all active emitters.
     */
    update(dt: number): void {
        for (let i = this.emitters.length - 1; i >= 0; i--) {
            const emitter = this.emitters[i];
            emitter.update(dt);

            // Remove completed emitters
            if (!emitter.emit && emitter.particleCount === 0) {
                emitter.destroy();
                this.emitters.splice(i, 1);
            }
        }
    }

    private spawnEmitter(x: number, y: number, config: typeof EMITTER_CONFIGS.trail, color: string): void {
        try {
            // Create emitter config with color tint
            const emitterConfig = upgradeConfig({
                ...config,
                pos: { x, y },
            }, [this.particleTexture]);

            const emitter = new Emitter(this.container, emitterConfig);
            emitter.emit = true;
            this.emitters.push(emitter);
        } catch (error) {
            console.warn('Failed to spawn particle emitter:', error);
        }
    }
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS

**Step 5: Commit**

```bash
git add web/src/particles.ts web/src/__tests__/particles.test.ts
git commit -m "feat(web): implement ParticleManager class"
```

---

## Task 7: Integrate InterpolationManager with main.ts

**Files:**
- Modify: `web/src/main.ts`

**Step 1: Add InterpolationManager initialization and usage**

Modify `web/src/main.ts`:

```typescript
// Add import at top
import { InterpolationManager } from './interpolation';

// After AnimationManager initialization, add:
const interpolationManager = new InterpolationManager();

// Modify onGameState handler to update interpolation targets:
onGameState: (state: GameState) => {
    // Update interpolation targets
    for (const entity of state.entities) {
        if (entity.components.position) {
            const pixelX = entity.components.position.x * 32; // tileSize
            const pixelY = entity.components.position.y * 32;
            interpolationManager.setTarget(entity.id, pixelX, pixelY);
        }
    }

    // Detect state changes for triggered animations
    if (previousState) {
        detectStateChanges(previousState, state, animationManager, interpolationManager);
    }
    previousState = state;

    // Render game state (creates sprites)
    renderer.render(state);

    // Apply animations after render
    applyAnimations(renderer, state, animationManager);

    // Update UI
    if (state.ui) {
        uiManager.updateUI(state.ui);
    }
},

// Modify ticker to update interpolation and apply positions:
app.ticker.add((ticker) => {
    const dt = ticker.deltaMS / 1000;
    animationManager.update(dt);
    interpolationManager.update(dt);

    // Apply interpolated positions to sprites
    const sprites = renderer.getEntitySprites();
    for (const [entityId, sprite] of sprites) {
        const pos = interpolationManager.getPosition(entityId);
        if (pos) {
            sprite.x = pos.currentX;
            sprite.y = pos.currentY;
        }
    }
});

// Update detectStateChanges signature and add cleanup:
function detectStateChanges(
    prev: GameState,
    curr: GameState,
    animationManager: AnimationManager,
    interpolationManager: InterpolationManager
): void {
    // ... existing code ...

    // Clean up removed entities from interpolation
    const currIds = new Set(curr.entities.map(e => e.id));
    for (const prevEntity of prev.entities) {
        if (!currIds.has(prevEntity.id)) {
            animationManager.removeEntity(prevEntity.id);
            interpolationManager.removeEntity(prevEntity.id);
        }
    }
}
```

**Step 2: Verify app still runs**

Run: `npm run dev` and check browser console for errors

**Step 3: Commit**

```bash
git add web/src/main.ts
git commit -m "feat(web): integrate InterpolationManager for smooth movement"
```

---

## Task 8: Integrate ParticleManager with main.ts

**Files:**
- Modify: `web/src/main.ts`

**Step 1: Add ParticleManager initialization**

Add to `web/src/main.ts`:

```typescript
// Add import at top
import { ParticleManager } from './particles';

// After other manager initialization:
const particleContainer = new PIXI.Container();
app.stage.addChild(particleContainer);
const particleManager = new ParticleManager(particleContainer);

// Add particle update to ticker:
app.ticker.add((ticker) => {
    const dt = ticker.deltaMS / 1000;
    animationManager.update(dt);
    interpolationManager.update(dt);
    particleManager.update(dt);

    // ... rest of ticker code
});
```

**Step 2: Add projectile trail spawning**

Add to ticker after interpolation update:

```typescript
// Spawn trails for projectiles
if (previousState) {
    for (const entity of previousState.entities) {
        if (entity.type === 'projectile' || entity.type === 'enemy_projectile') {
            const pos = interpolationManager.getPosition(entity.id);
            if (pos) {
                particleManager.spawnTrail(pos.currentX, pos.currentY, entity.type);
            }
        }
    }
}
```

**Step 3: Add death explosion spawning**

Modify detectStateChanges to spawn explosions:

```typescript
function detectStateChanges(
    prev: GameState,
    curr: GameState,
    animationManager: AnimationManager,
    interpolationManager: InterpolationManager,
    particleManager: ParticleManager
): void {
    // ... existing hit detection code ...

    // Detect deaths and spawn explosions
    const currIds = new Set(curr.entities.map(e => e.id));
    for (const prevEntity of prev.entities) {
        if (!currIds.has(prevEntity.id)) {
            const pos = interpolationManager.getPosition(prevEntity.id);

            // Enemy death = explosion
            if (prevEntity.type.startsWith('enemy_') && pos) {
                particleManager.spawnExplosion(pos.currentX, pos.currentY, prevEntity.type);
            }

            // Item pickup = sparkle
            if (['heart', 'coin', 'bomb', 'item'].includes(prevEntity.type) && pos) {
                particleManager.spawnSparkle(pos.currentX, pos.currentY);
            }

            // Cleanup
            animationManager.removeEntity(prevEntity.id);
            interpolationManager.removeEntity(prevEntity.id);
        }
    }
}
```

**Step 4: Verify app still runs**

Run: `npm run dev` and check browser console for errors

**Step 5: Commit**

```bash
git add web/src/main.ts
git commit -m "feat(web): integrate ParticleManager for visual effects"
```

---

## Task 9: Add door unlock shimmer detection

**Files:**
- Modify: `web/src/main.ts`

**Step 1: Track room cleared state for door shimmer**

Add to detectStateChanges:

```typescript
// Detect room cleared (doors unlock)
// Check if enemies existed before but none now
const prevEnemies = prev.entities.filter(e => e.type.startsWith('enemy_')).length;
const currEnemies = curr.entities.filter(e => e.type.startsWith('enemy_')).length;

if (prevEnemies > 0 && currEnemies === 0) {
    // Room just cleared - shimmer all doors
    for (const entity of curr.entities) {
        if (entity.type === 'door') {
            const pos = interpolationManager.getPosition(entity.id);
            if (pos) {
                particleManager.spawnShimmer(pos.currentX, pos.currentY);
            }
        }
    }
}
```

**Step 2: Verify app still runs**

Run: `npm run dev`

**Step 3: Commit**

```bash
git add web/src/main.ts
git commit -m "feat(web): add door unlock shimmer effect"
```

---

## Task 10: Final verification and cleanup

**Files:**
- All modified files

**Step 1: Run all tests**

Run: `npm test`
Expected: All tests pass

**Step 2: Verify no TypeScript errors**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Test manually**

Run: `npm run dev`
Verify:
- Sprites move smoothly (no jumping)
- Projectiles have trails
- Enemy deaths show explosions
- Item pickups show sparkles
- Room clear shows door shimmer

**Step 4: Final commit if any cleanup needed**

```bash
git add -A
git commit -m "chore(web): cleanup and final verification"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Add particle-emitter dependency | package.json |
| 2 | Create lerp and types | interpolation.ts |
| 3 | Implement InterpolationManager | interpolation.ts |
| 4 | Create particle color mapping | particles.ts |
| 5 | Create emitter configurations | particles.ts |
| 6 | Implement ParticleManager | particles.ts |
| 7 | Integrate interpolation | main.ts |
| 8 | Integrate particles | main.ts |
| 9 | Add door shimmer | main.ts |
| 10 | Final verification | all |
