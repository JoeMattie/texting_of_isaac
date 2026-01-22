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
