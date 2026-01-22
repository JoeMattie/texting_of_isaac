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

/**
 * Calculate Y offset for bob animation at given time.
 * @param elapsed - Time in seconds
 * @param config - Bob configuration
 * @returns Y offset in pixels
 */
export function calculateBobOffset(elapsed: number, config: BobConfig): number {
  return config.amplitude * Math.sin(elapsed * config.frequency * 2 * Math.PI);
}

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
