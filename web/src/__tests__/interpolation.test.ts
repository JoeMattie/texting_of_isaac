import { describe, it, expect } from 'vitest';
import { lerp, InterpolatedPosition } from '../interpolation';

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
