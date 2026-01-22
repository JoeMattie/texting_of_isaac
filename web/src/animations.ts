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
