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
