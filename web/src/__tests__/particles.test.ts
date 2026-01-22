import { describe, it, expect } from 'vitest';
import { PARTICLE_COLORS, getParticleColor, EMITTER_CONFIGS } from '../particles';

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
