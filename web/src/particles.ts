import * as PIXI from 'pixi.js';
import { Emitter, upgradeConfig } from '@pixi/particle-emitter';

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
    heart: '#ff6688',
    coin: '#ffcc00',
    bomb: '#88aa44',

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

    /** Dramatic burst on enemy death */
    explosion: {
        lifetime: { min: 0.4, max: 0.7 },
        frequency: 0.001,
        emitterLifetime: 0.08,
        maxParticles: 30,
        addAtBack: false,
        behaviors: [
            {
                type: 'alpha',
                config: { alpha: { list: [{ value: 1, time: 0 }, { value: 0.6, time: 0.5 }, { value: 0, time: 1 }] } }
            },
            {
                type: 'scale',
                config: { scale: { list: [{ value: 0.8, time: 0 }, { value: 0.3, time: 0.7 }, { value: 0.05, time: 1 }] } }
            },
            {
                type: 'moveSpeed',
                config: { speed: { list: [{ value: 300, time: 0 }, { value: 80, time: 0.5 }, { value: 10, time: 1 }] } }
            },
            {
                type: 'rotation',
                config: { minStart: 0, maxStart: 360 }
            },
        ]
    },

    /** Small sparks on projectile impact */
    hitSpark: {
        lifetime: { min: 0.1, max: 0.25 },
        frequency: 0.001,
        emitterLifetime: 0.04,
        maxParticles: 8,
        addAtBack: false,
        behaviors: [
            {
                type: 'alpha',
                config: { alpha: { list: [{ value: 1, time: 0 }, { value: 0, time: 1 }] } }
            },
            {
                type: 'scale',
                config: { scale: { list: [{ value: 0.35, time: 0 }, { value: 0.05, time: 1 }] } }
            },
            {
                type: 'moveSpeed',
                config: { speed: { list: [{ value: 180, time: 0 }, { value: 20, time: 1 }] } }
            },
            {
                type: 'rotation',
                config: { minStart: 0, maxStart: 360 }
            },
        ]
    },

    /** Upward burst for heart pickup */
    heartPickup: {
        lifetime: { min: 0.5, max: 0.8 },
        frequency: 0.005,
        emitterLifetime: 0.15,
        maxParticles: 18,
        addAtBack: false,
        behaviors: [
            {
                type: 'alpha',
                config: { alpha: { list: [{ value: 1, time: 0 }, { value: 0.8, time: 0.5 }, { value: 0, time: 1 }] } }
            },
            {
                type: 'scale',
                config: { scale: { list: [{ value: 0.5, time: 0 }, { value: 0.2, time: 0.6 }, { value: 0.05, time: 1 }] } }
            },
            {
                type: 'moveSpeed',
                config: { speed: { list: [{ value: 120, time: 0 }, { value: 30, time: 1 }] } }
            },
            {
                type: 'rotation',
                config: { minStart: 240, maxStart: 300 }
            },
        ]
    },

    /** Coin sparkle pickup effect */
    coinPickup: {
        lifetime: { min: 0.3, max: 0.5 },
        frequency: 0.005,
        emitterLifetime: 0.12,
        maxParticles: 12,
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
                config: { minStart: 0, maxStart: 360 }
            },
        ]
    },

    /** Upward burst for generic item pickup */
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

/**
 * Creates a simple circle texture for particles.
 * Returns null in non-browser environments (for testing).
 */
function createParticleTexture(): PIXI.Texture | null {
    // Check if we're in a browser environment with canvas support
    if (typeof document === 'undefined') {
        return null;
    }

    try {
        const canvas = document.createElement('canvas');
        canvas.width = 16;
        canvas.height = 16;
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            return null;
        }

        // Draw a simple white circle
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(8, 8, 6, 0, Math.PI * 2);
        ctx.fill();

        return PIXI.Texture.from(canvas);
    } catch {
        return null;
    }
}

/** A pooled emitter ready for reuse */
interface PoolEntry {
    emitter: Emitter;
    inUse: boolean;
}

type EmitterConfigKey = keyof typeof EMITTER_CONFIGS;

/**
 * Object pool for Emitter instances, keyed by config type.
 * Reuses emitter instances instead of creating new ones on every spawn.
 */
class EmitterPool {
    private pools: Map<string, PoolEntry[]> = new Map();
    private container: PIXI.Container;
    private texture: PIXI.Texture;
    private readonly poolSize: number;

    constructor(container: PIXI.Container, texture: PIXI.Texture, poolSize: number = 6) {
        this.container = container;
        this.texture = texture;
        this.poolSize = poolSize;
    }

    /**
     * Acquire an emitter of the given config type, positioned at (x, y).
     * Reuses an idle emitter from the pool, or creates one if pool is not full.
     */
    acquire(configKey: EmitterConfigKey, x: number, y: number, color: string): Emitter | null {
        const pool = this.getPool(configKey);

        // Find an idle emitter
        const entry = pool.find(e => !e.inUse);
        if (entry) {
            entry.inUse = true;
            entry.emitter.updateOwnerPos(x, y);
            entry.emitter.emit = true;
            return entry.emitter;
        }

        // Pool exhausted - create a new one only if under hard cap
        if (pool.length < this.poolSize * 2) {
            const emitter = this.createEmitter(configKey, x, y, color);
            if (emitter) {
                pool.push({ emitter, inUse: true });
                return emitter;
            }
        }

        return null;
    }

    /**
     * Release an emitter back to the pool when it finishes.
     */
    release(configKey: string, emitter: Emitter): void {
        const pool = this.pools.get(configKey);
        if (!pool) return;
        const entry = pool.find(e => e.emitter === emitter);
        if (entry) {
            entry.inUse = false;
            emitter.emit = false;
        }
    }

    /**
     * Update all in-use emitters and release finished ones.
     */
    update(dt: number): void {
        for (const [key, pool] of this.pools) {
            for (const entry of pool) {
                if (!entry.inUse) continue;
                entry.emitter.update(dt);
                if (!entry.emitter.emit && entry.emitter.particleCount === 0) {
                    this.release(key, entry.emitter);
                }
            }
        }
    }

    private getPool(configKey: string): PoolEntry[] {
        if (!this.pools.has(configKey)) {
            this.pools.set(configKey, []);
        }
        return this.pools.get(configKey)!;
    }

    private createEmitter(configKey: EmitterConfigKey, x: number, y: number, color: string): Emitter | null {
        try {
            const baseConfig = EMITTER_CONFIGS[configKey];
            const colorBehavior = {
                type: 'color',
                config: {
                    color: {
                        list: [
                            { value: color, time: 0 },
                            { value: color, time: 1 }
                        ]
                    }
                }
            };
            const configWithColor = {
                ...baseConfig,
                behaviors: [...baseConfig.behaviors, colorBehavior],
                pos: { x, y },
            };
            const emitterConfig = upgradeConfig(configWithColor, [this.texture]);
            const emitter = new Emitter(this.container as any, emitterConfig);
            emitter.emit = true;
            return emitter;
        } catch (error) {
            console.warn('Failed to create pooled emitter:', error);
            return null;
        }
    }
}

/**
 * Manages particle effects for the game.
 * Uses an object pool to reuse emitter instances and reduce GC pressure.
 */
export class ParticleManager {
    private container: PIXI.Container;
    private particleTexture: PIXI.Texture | null;
    private pool: EmitterPool | null = null;

    // Legacy emitters for non-pooled effects (backward compat)
    private legacyEmitters: Emitter[] = [];

    constructor(container: PIXI.Container) {
        this.container = container;
        this.particleTexture = createParticleTexture();
        if (this.particleTexture) {
            this.pool = new EmitterPool(container, this.particleTexture);
        }
    }

    /**
     * Spawn trail particles behind a projectile.
     */
    spawnTrail(x: number, y: number, entityType: string): void {
        const color = getParticleColor(entityType);
        this.spawnEmitter(x, y, EMITTER_CONFIGS.trail, color);
    }

    /**
     * Spawn dramatic death burst on enemy death.
     */
    spawnExplosion(x: number, y: number, entityType: string): void {
        const color = getParticleColor(entityType);
        this.pool?.acquire('explosion', x, y, color)
            ?? this.spawnEmitter(x, y, EMITTER_CONFIGS.explosion, color);
    }

    /**
     * Spawn small impact sparks on projectile hit.
     */
    spawnHitSpark(x: number, y: number, entityType: string): void {
        const color = getParticleColor(entityType);
        this.pool?.acquire('hitSpark', x, y, color)
            ?? this.spawnEmitter(x, y, EMITTER_CONFIGS.hitSpark, color);
    }

    /**
     * Spawn heart pickup effect (pink/red upward burst).
     */
    spawnHeartPickup(x: number, y: number): void {
        this.pool?.acquire('heartPickup', x, y, PARTICLE_COLORS.heart)
            ?? this.spawnEmitter(x, y, EMITTER_CONFIGS.heartPickup, PARTICLE_COLORS.heart);
    }

    /**
     * Spawn coin pickup effect (gold sparkle).
     */
    spawnCoinPickup(x: number, y: number): void {
        this.pool?.acquire('coinPickup', x, y, PARTICLE_COLORS.coin)
            ?? this.spawnEmitter(x, y, EMITTER_CONFIGS.coinPickup, PARTICLE_COLORS.coin);
    }

    /**
     * Spawn sparkle particles on generic item pickup.
     */
    spawnSparkle(x: number, y: number): void {
        this.pool?.acquire('sparkle', x, y, PARTICLE_COLORS.item)
            ?? this.spawnEmitter(x, y, EMITTER_CONFIGS.sparkle, PARTICLE_COLORS.item);
    }

    /**
     * Spawn shimmer particles on door unlock.
     */
    spawnShimmer(x: number, y: number): void {
        this.pool?.acquire('shimmer', x, y, PARTICLE_COLORS.door)
            ?? this.spawnEmitter(x, y, EMITTER_CONFIGS.shimmer, PARTICLE_COLORS.door);
    }

    /**
     * Update all active emitters.
     */
    update(dt: number): void {
        // Update pooled emitters
        this.pool?.update(dt);

        // Update legacy emitters (trail)
        for (let i = this.legacyEmitters.length - 1; i >= 0; i--) {
            const emitter = this.legacyEmitters[i];
            emitter.update(dt);
            if (!emitter.emit && emitter.particleCount === 0) {
                emitter.destroy();
                this.legacyEmitters.splice(i, 1);
            }
        }
    }

    private spawnEmitter(x: number, y: number, config: typeof EMITTER_CONFIGS.trail, color: string): void {
        // Skip if no texture available (e.g., in test environment)
        if (!this.particleTexture) {
            return;
        }

        try {
            const colorBehavior = {
                type: 'color',
                config: {
                    color: {
                        list: [
                            { value: color, time: 0 },
                            { value: color, time: 1 }
                        ]
                    }
                }
            };

            const configWithColor = {
                ...config,
                behaviors: [...config.behaviors, colorBehavior],
                pos: { x, y },
            };

            const emitterConfig = upgradeConfig(configWithColor, [this.particleTexture]);
            const emitter = new Emitter(this.container as any, emitterConfig);
            emitter.emit = true;
            this.legacyEmitters.push(emitter);
        } catch (error) {
            console.warn('Failed to spawn particle emitter:', error);
        }
    }
}
