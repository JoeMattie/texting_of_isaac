import { describe, it, expect } from 'vitest';
import { PARTICLE_COLORS, getParticleColor, EMITTER_CONFIGS, ParticleManager } from '../particles';

// Mock PIXI.Container for node environment
class MockContainer {
    children: unknown[] = [];
    addChild(child: unknown) { this.children.push(child); return child; }
    removeChild(child: unknown) {
        const idx = this.children.indexOf(child);
        if (idx >= 0) this.children.splice(idx, 1);
        return child;
    }
}

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

    it('has heart color as pink', () => {
        expect(PARTICLE_COLORS.heart).toBe('#ff6688');
    });

    it('has coin color as gold', () => {
        expect(PARTICLE_COLORS.coin).toBe('#ffcc00');
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

    it('has explosion config with more particles than hitSpark', () => {
        expect(EMITTER_CONFIGS.explosion).toBeDefined();
        expect(EMITTER_CONFIGS.explosion.maxParticles).toBeGreaterThanOrEqual(20);
    });

    it('has hitSpark config', () => {
        expect(EMITTER_CONFIGS.hitSpark).toBeDefined();
        expect(EMITTER_CONFIGS.hitSpark.lifetime).toBeDefined();
        expect(EMITTER_CONFIGS.hitSpark.maxParticles).toBeLessThan(EMITTER_CONFIGS.explosion.maxParticles);
    });

    it('has heartPickup config', () => {
        expect(EMITTER_CONFIGS.heartPickup).toBeDefined();
        expect(EMITTER_CONFIGS.heartPickup.lifetime).toBeDefined();
    });

    it('has coinPickup config', () => {
        expect(EMITTER_CONFIGS.coinPickup).toBeDefined();
        expect(EMITTER_CONFIGS.coinPickup.lifetime).toBeDefined();
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

describe('ParticleManager', () => {
    it('creates with container', () => {
        const container = new MockContainer();
        const manager = new ParticleManager(container as unknown as import('pixi.js').Container);
        expect(manager).toBeDefined();
    });

    it('spawnTrail does not throw', () => {
        const container = new MockContainer();
        const manager = new ParticleManager(container as unknown as import('pixi.js').Container);
        expect(() => manager.spawnTrail(100, 100, 'projectile')).not.toThrow();
    });

    it('spawnExplosion does not throw', () => {
        const container = new MockContainer();
        const manager = new ParticleManager(container as unknown as import('pixi.js').Container);
        expect(() => manager.spawnExplosion(100, 100, 'enemy_chaser')).not.toThrow();
    });

    it('spawnHitSpark does not throw', () => {
        const container = new MockContainer();
        const manager = new ParticleManager(container as unknown as import('pixi.js').Container);
        expect(() => manager.spawnHitSpark(100, 100, 'enemy_projectile')).not.toThrow();
    });

    it('spawnHeartPickup does not throw', () => {
        const container = new MockContainer();
        const manager = new ParticleManager(container as unknown as import('pixi.js').Container);
        expect(() => manager.spawnHeartPickup(100, 100)).not.toThrow();
    });

    it('spawnCoinPickup does not throw', () => {
        const container = new MockContainer();
        const manager = new ParticleManager(container as unknown as import('pixi.js').Container);
        expect(() => manager.spawnCoinPickup(100, 100)).not.toThrow();
    });

    it('spawnSparkle does not throw', () => {
        const container = new MockContainer();
        const manager = new ParticleManager(container as unknown as import('pixi.js').Container);
        expect(() => manager.spawnSparkle(100, 100)).not.toThrow();
    });

    it('spawnShimmer does not throw', () => {
        const container = new MockContainer();
        const manager = new ParticleManager(container as unknown as import('pixi.js').Container);
        expect(() => manager.spawnShimmer(100, 100)).not.toThrow();
    });

    it('update does not throw', () => {
        const container = new MockContainer();
        const manager = new ParticleManager(container as unknown as import('pixi.js').Container);
        expect(() => manager.update(0.016)).not.toThrow();
    });

    it('update handles multiple calls without throwing', () => {
        const container = new MockContainer();
        const manager = new ParticleManager(container as unknown as import('pixi.js').Container);
        manager.spawnExplosion(100, 100, 'enemy_chaser');
        manager.spawnHitSpark(50, 50, 'projectile');
        expect(() => {
            for (let i = 0; i < 10; i++) {
                manager.update(0.1);
            }
        }).not.toThrow();
    });
});
