import { describe, it, expect } from 'vitest';
import { lerp, InterpolatedPosition, InterpolationManager, INTERPOLATION_CONFIG } from '../interpolation';

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
        expect(pos!.currentX).toBe(100);
    });

    it('update moves current toward target', () => {
        const manager = new InterpolationManager();
        manager.setTarget(1, 0, 0);
        manager.setTarget(1, 100, 100);
        manager.update(0.016); // ~60fps frame time, small enough to not reach t=1
        const pos = manager.getPosition(1);
        expect(pos!.currentX).toBeGreaterThan(0);
        expect(pos!.currentX).toBeLessThan(100);
    });

    it('snaps when distance exceeds threshold', () => {
        const manager = new InterpolationManager();
        manager.setTarget(1, 0, 0);
        manager.setTarget(1, 1000, 1000);
        manager.update(0.016);
        const pos = manager.getPosition(1);
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
