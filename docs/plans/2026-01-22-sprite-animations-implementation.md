# Sprite Animations Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add procedural animations (bob, pulse, rotate, flash) to the web frontend for all entity types.

**Architecture:** AnimationManager class applies visual transforms each frame. Continuous animations use elapsed time with sinusoidal math. Triggered animations are one-shots detected via game state changes.

**Tech Stack:** TypeScript, Pixi.js, Vitest

---

## Task 1: Set Up Vitest for Web Frontend

**Files:**
- Modify: `web/package.json`
- Create: `web/vitest.config.ts`
- Create: `web/src/__tests__/setup.ts`

**Step 1: Install Vitest and dependencies**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm install -D vitest @vitest/coverage-v8
```

**Step 2: Add test script to package.json**

Modify `web/package.json` scripts section:
```json
"scripts": {
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview",
  "test": "vitest run",
  "test:watch": "vitest"
}
```

**Step 3: Create vitest.config.ts**

Create `web/vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/__tests__/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
    },
  },
});
```

**Step 4: Create test setup file**

Create `web/src/__tests__/setup.ts`:
```typescript
// Test setup for animation tests
// Mocks for Pixi.js objects will go here as needed
```

**Step 5: Verify test setup works**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: "No test files found" (that's fine, we'll add tests next)

**Step 6: Commit**

```bash
git add web/package.json web/package-lock.json web/vitest.config.ts web/src/__tests__/setup.ts
git commit -m "chore(web): add vitest for frontend testing"
```

---

## Task 2: Create Animation Types and Constants

**Files:**
- Create: `web/src/animations.ts`
- Create: `web/src/__tests__/animations.test.ts`

**Step 1: Write failing test for animation config types**

Create `web/src/__tests__/animations.test.ts`:
```typescript
import { describe, it, expect } from 'vitest';
import { ANIMATION_CONFIGS, EntityType } from '../animations';

describe('Animation Configs', () => {
  it('should have config for player', () => {
    expect(ANIMATION_CONFIGS.player).toBeDefined();
    expect(ANIMATION_CONFIGS.player.bob).toBeDefined();
  });

  it('should have config for all enemy types', () => {
    const enemyTypes: EntityType[] = [
      'enemy_chaser', 'enemy_shooter', 'enemy_orbiter', 'enemy_turret', 'enemy_tank'
    ];
    for (const type of enemyTypes) {
      expect(ANIMATION_CONFIGS[type]).toBeDefined();
    }
  });

  it('should have config for pickups', () => {
    const pickupTypes: EntityType[] = ['heart', 'coin', 'bomb', 'item'];
    for (const type of pickupTypes) {
      expect(ANIMATION_CONFIGS[type]).toBeDefined();
      expect(ANIMATION_CONFIGS[type].bob).toBeDefined();
    }
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: FAIL - Cannot find module '../animations'

**Step 3: Create animations.ts with types and configs**

Create `web/src/animations.ts`:
```typescript
// web/src/animations.ts
/**
 * Procedural animation system for game entities.
 * Applies visual transforms (bob, pulse, rotate, flash) based on entity type.
 */

export type EntityType =
  | 'player'
  | 'enemy_chaser'
  | 'enemy_shooter'
  | 'enemy_orbiter'
  | 'enemy_turret'
  | 'enemy_tank'
  | 'projectile'
  | 'enemy_projectile'
  | 'door'
  | 'heart'
  | 'coin'
  | 'bomb'
  | 'item'
  | 'obstacle'
  | 'wall'
  | 'unknown';

/** Configuration for bob animation (vertical oscillation) */
export interface BobConfig {
  amplitude: number;  // Pixels of movement
  frequency: number;  // Hz (cycles per second)
}

/** Configuration for pulse animation (scale oscillation) */
export interface PulseConfig {
  minScale: number;
  maxScale: number;
  frequency: number;  // Hz
}

/** Configuration for rotation animation */
export interface RotateConfig {
  speed: number;  // Degrees per second
}

/** Configuration for wobble animation (rotation oscillation) */
export interface WobbleConfig {
  angle: number;     // Max angle in degrees
  frequency: number; // Hz
}

/** Complete animation configuration for an entity type */
export interface AnimationConfig {
  bob?: BobConfig;
  pulse?: PulseConfig;
  rotate?: RotateConfig;
  wobble?: WobbleConfig;
}

/** Animation configurations per entity type */
export const ANIMATION_CONFIGS: Partial<Record<EntityType, AnimationConfig>> = {
  // Player: gentle bob
  player: {
    bob: { amplitude: 2, frequency: 2 },
  },

  // Enemies: unique per type
  enemy_chaser: {
    wobble: { angle: 15, frequency: 8 },
  },
  enemy_shooter: {
    pulse: { minScale: 1.0, maxScale: 1.1, frequency: 1 },
  },
  enemy_orbiter: {
    rotate: { speed: 90 },
  },
  enemy_turret: {
    rotate: { speed: 30 },
  },
  enemy_tank: {
    bob: { amplitude: 1, frequency: 0.5 },
  },

  // Projectiles: different for player vs enemy
  projectile: {
    rotate: { speed: 360 },
  },
  enemy_projectile: {
    pulse: { minScale: 0.8, maxScale: 1.2, frequency: 4 },
  },

  // Pickups: bob + sparkle pulse
  heart: {
    bob: { amplitude: 3, frequency: 1.5 },
    pulse: { minScale: 1.0, maxScale: 1.15, frequency: 2 },
  },
  coin: {
    bob: { amplitude: 3, frequency: 1.5 },
    pulse: { minScale: 1.0, maxScale: 1.15, frequency: 2 },
  },
  bomb: {
    bob: { amplitude: 3, frequency: 1.5 },
    pulse: { minScale: 1.0, maxScale: 1.15, frequency: 2 },
  },
  item: {
    bob: { amplitude: 3, frequency: 1.5 },
    pulse: { minScale: 1.0, maxScale: 1.15, frequency: 2 },
  },

  // Doors: static (no continuous animation)
  door: {},

  // Static elements
  obstacle: {},
  wall: {},
  unknown: {},
};
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: PASS

**Step 5: Commit**

```bash
git add web/src/animations.ts web/src/__tests__/animations.test.ts
git commit -m "feat(web): add animation types and configs for all entity types"
```

---

## Task 3: Implement Bob Animation Function

**Files:**
- Modify: `web/src/animations.ts`
- Modify: `web/src/__tests__/animations.test.ts`

**Step 1: Write failing tests for bob animation**

Add to `web/src/__tests__/animations.test.ts`:
```typescript
import { describe, it, expect } from 'vitest';
import { ANIMATION_CONFIGS, EntityType, calculateBobOffset } from '../animations';

// ... existing tests ...

describe('calculateBobOffset', () => {
  it('should return 0 at time 0', () => {
    const offset = calculateBobOffset(0, { amplitude: 2, frequency: 2 });
    expect(offset).toBeCloseTo(0, 5);
  });

  it('should return amplitude at quarter period', () => {
    // At t = 1/(4*frequency), sin(2*pi*f*t) = sin(pi/2) = 1
    const frequency = 2;
    const amplitude = 2;
    const quarterPeriod = 1 / (4 * frequency);
    const offset = calculateBobOffset(quarterPeriod, { amplitude, frequency });
    expect(offset).toBeCloseTo(amplitude, 5);
  });

  it('should return negative amplitude at 3/4 period', () => {
    const frequency = 2;
    const amplitude = 2;
    const threeQuarterPeriod = 3 / (4 * frequency);
    const offset = calculateBobOffset(threeQuarterPeriod, { amplitude, frequency });
    expect(offset).toBeCloseTo(-amplitude, 5);
  });

  it('should return 0 at full period', () => {
    const frequency = 2;
    const fullPeriod = 1 / frequency;
    const offset = calculateBobOffset(fullPeriod, { amplitude: 5, frequency });
    expect(offset).toBeCloseTo(0, 5);
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: FAIL - calculateBobOffset is not exported

**Step 3: Implement calculateBobOffset**

Add to `web/src/animations.ts` (after the configs):
```typescript
/**
 * Calculate Y offset for bob animation at given time.
 * @param elapsed - Time in seconds
 * @param config - Bob configuration
 * @returns Y offset in pixels
 */
export function calculateBobOffset(elapsed: number, config: BobConfig): number {
  return config.amplitude * Math.sin(elapsed * config.frequency * 2 * Math.PI);
}
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: PASS

**Step 5: Commit**

```bash
git add web/src/animations.ts web/src/__tests__/animations.test.ts
git commit -m "feat(web): implement calculateBobOffset for vertical oscillation"
```

---

## Task 4: Implement Pulse Animation Function

**Files:**
- Modify: `web/src/animations.ts`
- Modify: `web/src/__tests__/animations.test.ts`

**Step 1: Write failing tests for pulse animation**

Add to `web/src/__tests__/animations.test.ts`:
```typescript
import {
  ANIMATION_CONFIGS,
  EntityType,
  calculateBobOffset,
  calculatePulseScale
} from '../animations';

// ... existing tests ...

describe('calculatePulseScale', () => {
  it('should return midpoint scale at time 0', () => {
    const scale = calculatePulseScale(0, { minScale: 1.0, maxScale: 1.2, frequency: 2 });
    // sin(0) = 0, so scale = midpoint = 1.1
    expect(scale).toBeCloseTo(1.1, 5);
  });

  it('should return maxScale at quarter period', () => {
    const frequency = 2;
    const quarterPeriod = 1 / (4 * frequency);
    const scale = calculatePulseScale(quarterPeriod, { minScale: 1.0, maxScale: 1.2, frequency });
    expect(scale).toBeCloseTo(1.2, 5);
  });

  it('should return minScale at 3/4 period', () => {
    const frequency = 2;
    const threeQuarterPeriod = 3 / (4 * frequency);
    const scale = calculatePulseScale(threeQuarterPeriod, { minScale: 1.0, maxScale: 1.2, frequency });
    expect(scale).toBeCloseTo(1.0, 5);
  });

  it('should handle asymmetric min/max', () => {
    const frequency = 1;
    const quarterPeriod = 0.25;
    const scale = calculatePulseScale(quarterPeriod, { minScale: 0.8, maxScale: 1.2, frequency });
    expect(scale).toBeCloseTo(1.2, 5);
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: FAIL - calculatePulseScale is not exported

**Step 3: Implement calculatePulseScale**

Add to `web/src/animations.ts`:
```typescript
/**
 * Calculate scale for pulse animation at given time.
 * @param elapsed - Time in seconds
 * @param config - Pulse configuration
 * @returns Scale factor
 */
export function calculatePulseScale(elapsed: number, config: PulseConfig): number {
  const midpoint = (config.minScale + config.maxScale) / 2;
  const amplitude = (config.maxScale - config.minScale) / 2;
  return midpoint + amplitude * Math.sin(elapsed * config.frequency * 2 * Math.PI);
}
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: PASS

**Step 5: Commit**

```bash
git add web/src/animations.ts web/src/__tests__/animations.test.ts
git commit -m "feat(web): implement calculatePulseScale for scale oscillation"
```

---

## Task 5: Implement Rotate and Wobble Animation Functions

**Files:**
- Modify: `web/src/animations.ts`
- Modify: `web/src/__tests__/animations.test.ts`

**Step 1: Write failing tests for rotate and wobble**

Add to `web/src/__tests__/animations.test.ts`:
```typescript
import {
  ANIMATION_CONFIGS,
  EntityType,
  calculateBobOffset,
  calculatePulseScale,
  calculateRotation,
  calculateWobble
} from '../animations';

// ... existing tests ...

describe('calculateRotation', () => {
  it('should return 0 at time 0', () => {
    const rotation = calculateRotation(0, { speed: 360 });
    expect(rotation).toBeCloseTo(0, 5);
  });

  it('should return speed after 1 second', () => {
    const rotation = calculateRotation(1, { speed: 360 });
    expect(rotation).toBeCloseTo(360, 5);
  });

  it('should accumulate over time', () => {
    const rotation = calculateRotation(2.5, { speed: 90 });
    expect(rotation).toBeCloseTo(225, 5);
  });
});

describe('calculateWobble', () => {
  it('should return 0 at time 0', () => {
    const angle = calculateWobble(0, { angle: 15, frequency: 8 });
    expect(angle).toBeCloseTo(0, 5);
  });

  it('should return max angle at quarter period', () => {
    const frequency = 8;
    const quarterPeriod = 1 / (4 * frequency);
    const angle = calculateWobble(quarterPeriod, { angle: 15, frequency });
    expect(angle).toBeCloseTo(15, 5);
  });

  it('should return negative max angle at 3/4 period', () => {
    const frequency = 8;
    const threeQuarterPeriod = 3 / (4 * frequency);
    const angle = calculateWobble(threeQuarterPeriod, { angle: 15, frequency });
    expect(angle).toBeCloseTo(-15, 5);
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: FAIL - calculateRotation is not exported

**Step 3: Implement calculateRotation and calculateWobble**

Add to `web/src/animations.ts`:
```typescript
/**
 * Calculate rotation angle at given time.
 * @param elapsed - Time in seconds
 * @param config - Rotation configuration
 * @returns Rotation in degrees
 */
export function calculateRotation(elapsed: number, config: RotateConfig): number {
  return elapsed * config.speed;
}

/**
 * Calculate wobble angle at given time (oscillating rotation).
 * @param elapsed - Time in seconds
 * @param config - Wobble configuration
 * @returns Rotation offset in degrees
 */
export function calculateWobble(elapsed: number, config: WobbleConfig): number {
  return config.angle * Math.sin(elapsed * config.frequency * 2 * Math.PI);
}
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: PASS

**Step 5: Commit**

```bash
git add web/src/animations.ts web/src/__tests__/animations.test.ts
git commit -m "feat(web): implement calculateRotation and calculateWobble"
```

---

## Task 6: Implement Triggered Animation Types

**Files:**
- Modify: `web/src/animations.ts`
- Modify: `web/src/__tests__/animations.test.ts`

**Step 1: Write failing tests for triggered animations**

Add to `web/src/__tests__/animations.test.ts`:
```typescript
import {
  // ... existing imports ...
  TriggeredAnimation,
  calculateFlashAlpha,
  calculateTriggeredPulse
} from '../animations';

// ... existing tests ...

describe('calculateFlashAlpha', () => {
  it('should return minAlpha at start', () => {
    const alpha = calculateFlashAlpha(0, { minAlpha: 0.3, flashes: 3, duration: 300 });
    expect(alpha).toBeCloseTo(0.3, 2);
  });

  it('should return 1.0 at half of first flash', () => {
    // 3 flashes in 300ms = 100ms per flash, peak at 50ms
    const alpha = calculateFlashAlpha(50, { minAlpha: 0.3, flashes: 3, duration: 300 });
    expect(alpha).toBeCloseTo(1.0, 2);
  });

  it('should cycle through flashes', () => {
    // At 150ms (middle of duration), should be at peak of second flash
    const alpha = calculateFlashAlpha(150, { minAlpha: 0.3, flashes: 3, duration: 300 });
    expect(alpha).toBeCloseTo(1.0, 2);
  });
});

describe('calculateTriggeredPulse', () => {
  it('should return 1.0 at start', () => {
    const scale = calculateTriggeredPulse(0, { targetScale: 1.2, duration: 200 });
    expect(scale).toBeCloseTo(1.0, 2);
  });

  it('should return targetScale at midpoint', () => {
    const scale = calculateTriggeredPulse(100, { targetScale: 1.2, duration: 200 });
    expect(scale).toBeCloseTo(1.2, 2);
  });

  it('should return 1.0 at end', () => {
    const scale = calculateTriggeredPulse(200, { targetScale: 1.2, duration: 200 });
    expect(scale).toBeCloseTo(1.0, 2);
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: FAIL - TriggeredAnimation is not exported

**Step 3: Implement triggered animation types and functions**

Add to `web/src/animations.ts`:
```typescript
/** Configuration for flash animation (alpha flicker) */
export interface FlashConfig {
  minAlpha: number;   // Minimum alpha (0-1)
  flashes: number;    // Number of flashes
  duration: number;   // Total duration in milliseconds
}

/** Configuration for triggered pulse (one-shot scale) */
export interface TriggeredPulseConfig {
  targetScale: number;  // Max scale to reach
  duration: number;     // Total duration in milliseconds
}

/** Types of triggered animations */
export type TriggeredAnimationType = 'flash' | 'pulse';

/** Active triggered animation instance */
export interface TriggeredAnimation {
  type: TriggeredAnimationType;
  startTime: number;  // Timestamp when animation started
  duration: number;   // Duration in milliseconds
  config: FlashConfig | TriggeredPulseConfig;
}

/**
 * Calculate alpha for flash animation.
 * @param elapsedMs - Time since animation start in milliseconds
 * @param config - Flash configuration
 * @returns Alpha value (0-1)
 */
export function calculateFlashAlpha(elapsedMs: number, config: FlashConfig): number {
  const flashDuration = config.duration / config.flashes;
  const flashProgress = (elapsedMs % flashDuration) / flashDuration;
  // Use sine wave for smooth flash: 0 -> 1 -> 0 per flash
  const sineValue = Math.sin(flashProgress * Math.PI);
  return config.minAlpha + (1 - config.minAlpha) * sineValue;
}

/**
 * Calculate scale for triggered pulse animation.
 * @param elapsedMs - Time since animation start in milliseconds
 * @param config - Pulse configuration
 * @returns Scale factor
 */
export function calculateTriggeredPulse(elapsedMs: number, config: TriggeredPulseConfig): number {
  const progress = elapsedMs / config.duration;
  // Sine wave from 0 to pi: starts at 1.0, peaks at targetScale, returns to 1.0
  const sineValue = Math.sin(progress * Math.PI);
  return 1.0 + (config.targetScale - 1.0) * sineValue;
}
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: PASS

**Step 5: Commit**

```bash
git add web/src/animations.ts web/src/__tests__/animations.test.ts
git commit -m "feat(web): implement triggered animations (flash, pulse)"
```

---

## Task 7: Create AnimationManager Class

**Files:**
- Modify: `web/src/animations.ts`
- Modify: `web/src/__tests__/animations.test.ts`

**Step 1: Write failing tests for AnimationManager**

Add to `web/src/__tests__/animations.test.ts`:
```typescript
import {
  // ... existing imports ...
  AnimationManager
} from '../animations';

// ... existing tests ...

describe('AnimationManager', () => {
  it('should initialize with empty state', () => {
    const manager = new AnimationManager();
    expect(manager.getElapsed()).toBe(0);
  });

  it('should accumulate elapsed time on update', () => {
    const manager = new AnimationManager();
    manager.update(0.1);  // 100ms
    expect(manager.getElapsed()).toBeCloseTo(0.1, 5);
    manager.update(0.05); // 50ms more
    expect(manager.getElapsed()).toBeCloseTo(0.15, 5);
  });

  it('should calculate transforms for entity type', () => {
    const manager = new AnimationManager();
    manager.update(0.125); // At quarter period for 2Hz bob

    const transforms = manager.getTransforms('player');
    expect(transforms.yOffset).toBeCloseTo(2, 1); // 2px amplitude at peak
    expect(transforms.scale).toBe(1);
    expect(transforms.rotation).toBe(0);
    expect(transforms.alpha).toBe(1);
  });

  it('should return neutral transforms for unknown entity type', () => {
    const manager = new AnimationManager();
    const transforms = manager.getTransforms('unknown');
    expect(transforms.yOffset).toBe(0);
    expect(transforms.scale).toBe(1);
    expect(transforms.rotation).toBe(0);
    expect(transforms.alpha).toBe(1);
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: FAIL - AnimationManager is not exported

**Step 3: Implement AnimationManager class**

Add to `web/src/animations.ts`:
```typescript
/** Visual transforms to apply to a sprite */
export interface SpriteTransforms {
  yOffset: number;   // Pixels
  scale: number;     // Scale factor
  rotation: number;  // Degrees
  alpha: number;     // 0-1
}

/** Neutral transforms (no animation) */
const NEUTRAL_TRANSFORMS: SpriteTransforms = {
  yOffset: 0,
  scale: 1,
  rotation: 0,
  alpha: 1,
};

/**
 * Manages procedural animations for game entities.
 */
export class AnimationManager {
  private elapsed: number = 0;
  private triggeredAnimations: Map<number, TriggeredAnimation[]> = new Map();

  /**
   * Update animation time.
   * @param dt - Delta time in seconds
   */
  update(dt: number): void {
    this.elapsed += dt;
  }

  /**
   * Get current elapsed time.
   */
  getElapsed(): number {
    return this.elapsed;
  }

  /**
   * Calculate visual transforms for an entity type.
   * @param entityType - Type of entity
   * @returns Transforms to apply to the sprite
   */
  getTransforms(entityType: EntityType): SpriteTransforms {
    const config = ANIMATION_CONFIGS[entityType];
    if (!config) {
      return { ...NEUTRAL_TRANSFORMS };
    }

    const transforms: SpriteTransforms = { ...NEUTRAL_TRANSFORMS };

    // Apply bob animation
    if (config.bob) {
      transforms.yOffset = calculateBobOffset(this.elapsed, config.bob);
    }

    // Apply pulse animation
    if (config.pulse) {
      transforms.scale = calculatePulseScale(this.elapsed, config.pulse);
    }

    // Apply rotation animation
    if (config.rotate) {
      transforms.rotation = calculateRotation(this.elapsed, config.rotate);
    }

    // Apply wobble animation
    if (config.wobble) {
      transforms.rotation = calculateWobble(this.elapsed, config.wobble);
    }

    return transforms;
  }
}
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: PASS

**Step 5: Commit**

```bash
git add web/src/animations.ts web/src/__tests__/animations.test.ts
git commit -m "feat(web): implement AnimationManager class"
```

---

## Task 8: Add Triggered Animation Support to AnimationManager

**Files:**
- Modify: `web/src/animations.ts`
- Modify: `web/src/__tests__/animations.test.ts`

**Step 1: Write failing tests for triggered animation support**

Add to `web/src/__tests__/animations.test.ts`:
```typescript
describe('AnimationManager triggered animations', () => {
  it('should trigger flash animation on entity', () => {
    const manager = new AnimationManager();
    manager.triggerFlash(1); // Entity ID 1

    const transforms = manager.getTransformsForEntity(1, 'player');
    // At time 0, flash starts at minAlpha
    expect(transforms.alpha).toBeCloseTo(0.3, 1);
  });

  it('should trigger pulse animation on entity', () => {
    const manager = new AnimationManager();
    manager.triggerPulse(1); // Entity ID 1

    // Advance to middle of pulse
    manager.update(0.1); // 100ms = half of 200ms duration

    const transforms = manager.getTransformsForEntity(1, 'player');
    expect(transforms.scale).toBeCloseTo(1.2, 1);
  });

  it('should remove expired triggered animations', () => {
    const manager = new AnimationManager();
    manager.triggerFlash(1);

    // Advance past flash duration (300ms)
    manager.update(0.4);

    const transforms = manager.getTransformsForEntity(1, 'player');
    expect(transforms.alpha).toBe(1); // Back to normal
  });

  it('should stack multiple triggered animations', () => {
    const manager = new AnimationManager();
    manager.triggerFlash(1);
    manager.triggerPulse(1);

    manager.update(0.05); // 50ms in

    const transforms = manager.getTransformsForEntity(1, 'player');
    // Both should be active
    expect(transforms.alpha).toBeLessThan(1);
    expect(transforms.scale).toBeGreaterThan(1);
  });

  it('should clean up entity animations on removeEntity', () => {
    const manager = new AnimationManager();
    manager.triggerFlash(1);
    manager.removeEntity(1);

    // Should return neutral transforms after removal
    const transforms = manager.getTransformsForEntity(1, 'player');
    expect(transforms.alpha).toBe(1);
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: FAIL - triggerFlash is not a function

**Step 3: Implement triggered animation methods**

Update `AnimationManager` class in `web/src/animations.ts`:
```typescript
/** Default flash configuration for hit effects */
const DEFAULT_FLASH_CONFIG: FlashConfig = {
  minAlpha: 0.3,
  flashes: 3,
  duration: 300,
};

/** Default pulse configuration for shoot effects */
const DEFAULT_PULSE_CONFIG: TriggeredPulseConfig = {
  targetScale: 1.2,
  duration: 200,
};

/**
 * Manages procedural animations for game entities.
 */
export class AnimationManager {
  private elapsed: number = 0;
  private elapsedMs: number = 0;
  private triggeredAnimations: Map<number, TriggeredAnimation[]> = new Map();

  /**
   * Update animation time and process triggered animations.
   * @param dt - Delta time in seconds
   */
  update(dt: number): void {
    this.elapsed += dt;
    this.elapsedMs += dt * 1000;

    // Clean up expired triggered animations
    for (const [entityId, anims] of this.triggeredAnimations) {
      const active = anims.filter(anim =>
        this.elapsedMs - anim.startTime < anim.duration
      );
      if (active.length === 0) {
        this.triggeredAnimations.delete(entityId);
      } else {
        this.triggeredAnimations.set(entityId, active);
      }
    }
  }

  /**
   * Get current elapsed time in seconds.
   */
  getElapsed(): number {
    return this.elapsed;
  }

  /**
   * Trigger a flash animation on an entity (e.g., when hit).
   * @param entityId - Entity ID
   */
  triggerFlash(entityId: number): void {
    const anim: TriggeredAnimation = {
      type: 'flash',
      startTime: this.elapsedMs,
      duration: DEFAULT_FLASH_CONFIG.duration,
      config: DEFAULT_FLASH_CONFIG,
    };
    this.addTriggeredAnimation(entityId, anim);
  }

  /**
   * Trigger a pulse animation on an entity (e.g., when shooting).
   * @param entityId - Entity ID
   */
  triggerPulse(entityId: number): void {
    const anim: TriggeredAnimation = {
      type: 'pulse',
      startTime: this.elapsedMs,
      duration: DEFAULT_PULSE_CONFIG.duration,
      config: DEFAULT_PULSE_CONFIG,
    };
    this.addTriggeredAnimation(entityId, anim);
  }

  /**
   * Remove all animations for an entity.
   * @param entityId - Entity ID
   */
  removeEntity(entityId: number): void {
    this.triggeredAnimations.delete(entityId);
  }

  private addTriggeredAnimation(entityId: number, anim: TriggeredAnimation): void {
    const existing = this.triggeredAnimations.get(entityId) || [];
    existing.push(anim);
    this.triggeredAnimations.set(entityId, existing);
  }

  /**
   * Calculate visual transforms for an entity type (continuous only).
   * @param entityType - Type of entity
   * @returns Transforms to apply to the sprite
   */
  getTransforms(entityType: EntityType): SpriteTransforms {
    const config = ANIMATION_CONFIGS[entityType];
    if (!config) {
      return { ...NEUTRAL_TRANSFORMS };
    }

    const transforms: SpriteTransforms = { ...NEUTRAL_TRANSFORMS };

    if (config.bob) {
      transforms.yOffset = calculateBobOffset(this.elapsed, config.bob);
    }
    if (config.pulse) {
      transforms.scale = calculatePulseScale(this.elapsed, config.pulse);
    }
    if (config.rotate) {
      transforms.rotation = calculateRotation(this.elapsed, config.rotate);
    }
    if (config.wobble) {
      transforms.rotation = calculateWobble(this.elapsed, config.wobble);
    }

    return transforms;
  }

  /**
   * Calculate visual transforms for a specific entity (continuous + triggered).
   * @param entityId - Entity ID
   * @param entityType - Type of entity
   * @returns Transforms to apply to the sprite
   */
  getTransformsForEntity(entityId: number, entityType: EntityType): SpriteTransforms {
    // Start with continuous animations
    const transforms = this.getTransforms(entityType);

    // Apply triggered animations
    const triggered = this.triggeredAnimations.get(entityId);
    if (triggered) {
      for (const anim of triggered) {
        const elapsed = this.elapsedMs - anim.startTime;
        if (anim.type === 'flash') {
          transforms.alpha = calculateFlashAlpha(elapsed, anim.config as FlashConfig);
        } else if (anim.type === 'pulse') {
          transforms.scale *= calculateTriggeredPulse(elapsed, anim.config as TriggeredPulseConfig);
        }
      }
    }

    return transforms;
  }
}
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: PASS

**Step 5: Commit**

```bash
git add web/src/animations.ts web/src/__tests__/animations.test.ts
git commit -m "feat(web): add triggered animation support to AnimationManager"
```

---

## Task 9: Expose Sprite Data from GameRenderer

**Files:**
- Modify: `web/src/renderer.ts`

**Step 1: Read current renderer implementation**

Already read earlier. The renderer has `private entitySprites: Map<number, PIXI.Sprite>`.

**Step 2: Add getter methods for animation manager access**

Modify `web/src/renderer.ts` to add these methods after the `clear()` method:
```typescript
    /**
     * Get all entity sprites for animation.
     * @returns Map of entity ID to sprite
     */
    getEntitySprites(): Map<number, PIXI.Sprite> {
        return this.entitySprites;
    }

    /**
     * Get entity type for a given entity ID.
     * @param entityId - Entity ID
     * @param gameState - Current game state
     * @returns Entity type or 'unknown'
     */
    getEntityType(entityId: number, gameState: GameState): string {
        const entity = gameState.entities.find(e => e.id === entityId);
        return entity?.type || 'unknown';
    }
```

**Step 3: Verify renderer still works**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm run build
```

Expected: Build succeeds with no errors

**Step 4: Commit**

```bash
git add web/src/renderer.ts
git commit -m "feat(web): expose sprite data from GameRenderer for animations"
```

---

## Task 10: Integrate AnimationManager with Main

**Files:**
- Modify: `web/src/main.ts`
- Modify: `web/src/renderer.ts`

**Step 1: Read current main.ts**

Already read earlier. Need to add AnimationManager initialization and update loop.

**Step 2: Update main.ts to use AnimationManager**

Modify `web/src/main.ts`:
```typescript
// web/src/main.ts

import * as PIXI from 'pixi.js';
import { NetworkClient, GameState } from './network';
import { SpriteManager } from './sprites';
import { GameRenderer } from './renderer';
import { UIManager } from './ui';
import { AnimationManager, EntityType } from './animations';

async function main() {
    console.log('Texting of Isaac - Web Edition');
    console.log('Pixi.js version:', PIXI.VERSION);

    // Initialize Pixi.js application
    const app = new PIXI.Application();
    await app.init({
        width: 1920,
        height: 640,
        backgroundColor: 0x000000,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true
    });

    const container = document.getElementById('app');
    if (container) {
        container.appendChild(app.canvas);
    }

    // Initialize sprite manager and load sprites
    let spriteManager: SpriteManager;
    try {
        spriteManager = new SpriteManager();
        await spriteManager.load();
        console.log('Sprites loaded');
    } catch (error) {
        console.error('Failed to load sprites:', error);
        document.body.innerHTML = '<div style="color: red; padding: 20px;">Failed to load game assets. Please refresh.</div>';
        return;
    }

    // Initialize renderer
    const renderer = new GameRenderer(app, spriteManager);

    // Initialize animation manager
    const animationManager = new AnimationManager();

    // Initialize UI manager
    const uiManager = new UIManager();

    // Track previous game state for detecting changes
    let previousState: GameState | null = null;

    // Connect to game server
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8765';
    const networkClient = new NetworkClient(wsUrl, {
        onSessionInfo: (info) => {
            console.log('Session established:', info);
            uiManager.updateSessionInfo(info);
        },
        onGameState: (state: GameState) => {
            // Detect state changes for triggered animations
            if (previousState) {
                detectStateChanges(previousState, state, animationManager);
            }
            previousState = state;

            // Render game state
            renderer.render(state);

            // Apply animations to sprites
            applyAnimations(renderer, state, animationManager);

            // Update UI
            if (state.ui) {
                uiManager.updateUI(state.ui);
            }
        },
        onDisconnect: () => {
            console.log('Disconnected from server');
            uiManager.showDisconnected();
        },
        onError: (error) => {
            console.error('Network error:', error);
            uiManager.showError(error);
        }
    });

    // Animation update loop
    app.ticker.add((ticker) => {
        animationManager.update(ticker.deltaMS / 1000);
    });

    // Connect as player
    networkClient.connect('player');

    // Setup keyboard input (WASD for movement, arrows for shooting)
    const gameKeys = new Set(['w', 'a', 's', 'd', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' ', 'e']);

    window.addEventListener('keydown', (e) => {
        if (gameKeys.has(e.key)) {
            e.preventDefault();
            networkClient.sendInput(e.key, 'press');
        }
    });

    window.addEventListener('keyup', (e) => {
        if (gameKeys.has(e.key)) {
            e.preventDefault();
            networkClient.sendInput(e.key, 'release');
        }
    });
}

/**
 * Detect state changes that should trigger animations.
 */
function detectStateChanges(
    prev: GameState,
    curr: GameState,
    animationManager: AnimationManager
): void {
    // Detect player hit (health decreased)
    if (prev.player && curr.player) {
        const prevHealth = prev.player.components.health?.current;
        const currHealth = curr.player.components.health?.current;
        if (prevHealth !== undefined && currHealth !== undefined && currHealth < prevHealth) {
            animationManager.triggerFlash(curr.player.id);
        }
    }

    // Detect enemy hits
    for (const currEntity of curr.entities) {
        if (currEntity.type.startsWith('enemy_')) {
            const prevEntity = prev.entities.find(e => e.id === currEntity.id);
            if (prevEntity) {
                const prevHealth = prevEntity.components.health?.current;
                const currHealth = currEntity.components.health?.current;
                if (prevHealth !== undefined && currHealth !== undefined && currHealth < prevHealth) {
                    animationManager.triggerFlash(currEntity.id);
                }
            }
        }
    }

    // Clean up removed entities
    const currIds = new Set(curr.entities.map(e => e.id));
    for (const prevEntity of prev.entities) {
        if (!currIds.has(prevEntity.id)) {
            animationManager.removeEntity(prevEntity.id);
        }
    }
}

/**
 * Apply animations to all sprites.
 */
function applyAnimations(
    renderer: GameRenderer,
    state: GameState,
    animationManager: AnimationManager
): void {
    const sprites = renderer.getEntitySprites();

    for (const [entityId, sprite] of sprites) {
        const entityType = renderer.getEntityType(entityId, state) as EntityType;
        const transforms = animationManager.getTransformsForEntity(entityId, entityType);

        // Apply transforms (Pixi uses radians for rotation)
        sprite.pivot.y = -transforms.yOffset;
        sprite.scale.set(transforms.scale);
        sprite.rotation = transforms.rotation * (Math.PI / 180);
        sprite.alpha = transforms.alpha;
    }
}

main();
```

**Step 3: Verify build succeeds**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm run build
```

Expected: Build succeeds with no errors

**Step 4: Commit**

```bash
git add web/src/main.ts
git commit -m "feat(web): integrate AnimationManager with game loop"
```

---

## Task 11: Add Player Shoot Detection

**Files:**
- Modify: `web/src/main.ts`

**Step 1: Update detectStateChanges to detect player shooting**

Add to `detectStateChanges` function in `web/src/main.ts`:
```typescript
/**
 * Detect state changes that should trigger animations.
 */
function detectStateChanges(
    prev: GameState,
    curr: GameState,
    animationManager: AnimationManager
): void {
    // Detect player hit (health decreased)
    if (prev.player && curr.player) {
        const prevHealth = prev.player.components.health?.current;
        const currHealth = curr.player.components.health?.current;
        if (prevHealth !== undefined && currHealth !== undefined && currHealth < prevHealth) {
            animationManager.triggerFlash(curr.player.id);
        }
    }

    // Detect player shooting (new player projectiles)
    const prevPlayerProjectiles = prev.entities.filter(e => e.type === 'projectile').length;
    const currPlayerProjectiles = curr.entities.filter(e => e.type === 'projectile').length;
    if (currPlayerProjectiles > prevPlayerProjectiles && curr.player) {
        animationManager.triggerPulse(curr.player.id);
    }

    // Detect enemy hits
    for (const currEntity of curr.entities) {
        if (currEntity.type.startsWith('enemy_')) {
            const prevEntity = prev.entities.find(e => e.id === currEntity.id);
            if (prevEntity) {
                const prevHealth = prevEntity.components.health?.current;
                const currHealth = currEntity.components.health?.current;
                if (prevHealth !== undefined && currHealth !== undefined && currHealth < prevHealth) {
                    animationManager.triggerFlash(currEntity.id);
                }
            }
        }
    }

    // Clean up removed entities
    const currIds = new Set(curr.entities.map(e => e.id));
    for (const prevEntity of prev.entities) {
        if (!currIds.has(prevEntity.id)) {
            animationManager.removeEntity(prevEntity.id);
        }
    }
}
```

**Step 2: Verify build succeeds**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm run build
```

Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/main.ts
git commit -m "feat(web): add player shoot detection for pulse animation"
```

---

## Task 12: Run All Tests and Final Verification

**Files:** None (verification only)

**Step 1: Run all web tests**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm test
```

Expected: All tests pass

**Step 2: Run Python tests**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations
uv run pytest -q
```

Expected: 448 passed

**Step 3: Build production bundle**

Run:
```bash
cd /home/joe/dev/texting_of_isaac/.worktrees/sprite-animations/web
npm run build
```

Expected: Build succeeds with no errors

**Step 4: Commit any remaining changes**

If there are any uncommitted changes:
```bash
git status
git add -A
git commit -m "chore(web): final cleanup for sprite animations"
```

---

## Summary

This plan implements procedural sprite animations for the web frontend:

1. **Tasks 1**: Set up Vitest for testing
2. **Tasks 2-6**: Implement animation math functions with tests (bob, pulse, rotate, wobble, flash)
3. **Tasks 7-8**: Create AnimationManager class with triggered animation support
4. **Task 9**: Expose sprite data from renderer
5. **Tasks 10-11**: Integrate with main game loop, add state change detection
6. **Task 12**: Final verification

Total: 12 tasks with TDD approach throughout.
