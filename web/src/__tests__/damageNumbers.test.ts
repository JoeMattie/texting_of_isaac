// web/src/__tests__/damageNumbers.test.ts
import { describe, it, expect } from 'vitest';
import { DamageNumberManager, DAMAGE_COLORS, DAMAGE_NUMBER_CONFIG } from '../damageNumbers';

// Minimal PIXI.Container mock for test environment
class MockContainer {
    children: unknown[] = [];
    addChild(child: unknown) { this.children.push(child); return child; }
    removeChild(child: unknown) {
        const idx = this.children.indexOf(child);
        if (idx >= 0) this.children.splice(idx, 1);
        return child;
    }
}

describe('DAMAGE_COLORS', () => {
    it('player damage is red', () => {
        expect(DAMAGE_COLORS.player).toBe(0xff3333);
    });

    it('enemy damage is gold', () => {
        expect(DAMAGE_COLORS.enemy).toBe(0xffcc00);
    });
});

describe('DAMAGE_NUMBER_CONFIG', () => {
    it('has a positive drift speed', () => {
        expect(DAMAGE_NUMBER_CONFIG.driftSpeed).toBeGreaterThan(0);
    });

    it('has a positive duration', () => {
        expect(DAMAGE_NUMBER_CONFIG.duration).toBeGreaterThan(0);
    });

    it('has a positive font size', () => {
        expect(DAMAGE_NUMBER_CONFIG.fontSize).toBeGreaterThan(0);
    });
});

describe('DamageNumberManager', () => {
    it('creates without throwing', () => {
        const container = new MockContainer();
        expect(() => new DamageNumberManager(
            container as unknown as import('pixi.js').Container
        )).not.toThrow();
    });

    it('add does not throw for player damage', () => {
        const container = new MockContainer();
        const manager = new DamageNumberManager(
            container as unknown as import('pixi.js').Container, 5
        );
        expect(() => manager.add(100, 200, 3, 'player')).not.toThrow();
    });

    it('add does not throw for enemy damage', () => {
        const container = new MockContainer();
        const manager = new DamageNumberManager(
            container as unknown as import('pixi.js').Container, 5
        );
        expect(() => manager.add(50, 80, 7, 'enemy')).not.toThrow();
    });

    it('update does not throw when empty', () => {
        const container = new MockContainer();
        const manager = new DamageNumberManager(
            container as unknown as import('pixi.js').Container, 5
        );
        expect(() => manager.update(0.016)).not.toThrow();
    });

    it('update does not throw after adding numbers', () => {
        const container = new MockContainer();
        const manager = new DamageNumberManager(
            container as unknown as import('pixi.js').Container, 5
        );
        manager.add(100, 100, 5, 'enemy');
        manager.add(200, 150, 2, 'player');
        expect(() => manager.update(0.016)).not.toThrow();
    });

    it('update runs through full popup lifetime without throwing', () => {
        const container = new MockContainer();
        const manager = new DamageNumberManager(
            container as unknown as import('pixi.js').Container, 5
        );
        manager.add(100, 100, 10, 'enemy');
        expect(() => {
            // Simulate more than the full duration
            for (let i = 0; i < 60; i++) {
                manager.update(0.02);
            }
        }).not.toThrow();
    });

    it('handles pool exhaustion gracefully', () => {
        const container = new MockContainer();
        // Pool of 2 – add more than pool size
        const manager = new DamageNumberManager(
            container as unknown as import('pixi.js').Container, 2
        );
        expect(() => {
            for (let i = 0; i < 10; i++) {
                manager.add(i * 10, i * 10, i + 1, 'enemy');
            }
        }).not.toThrow();
    });
});
