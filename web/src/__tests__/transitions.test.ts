// web/src/__tests__/transitions.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { TransitionManager } from '../transitions';

describe('TransitionManager', () => {
    let manager: TransitionManager;

    beforeEach(() => {
        manager = new TransitionManager(1920, 640);
    });

    describe('initial state', () => {
        it('starts inactive', () => {
            expect(manager.isTransitioning()).toBe(false);
        });

        it('returns zero offset when inactive', () => {
            const offset = manager.getOffset();
            expect(offset.x).toBe(0);
            expect(offset.y).toBe(0);
        });
    });

    describe('startTransition', () => {
        it('activates transition when moving right', () => {
            manager.startTransition([0, 0], [1, 0]);
            expect(manager.isTransitioning()).toBe(true);
        });

        it('activates transition when moving left', () => {
            manager.startTransition([1, 0], [0, 0]);
            expect(manager.isTransitioning()).toBe(true);
        });

        it('activates transition when moving down', () => {
            manager.startTransition([0, 0], [0, 1]);
            expect(manager.isTransitioning()).toBe(true);
        });

        it('activates transition when moving up', () => {
            manager.startTransition([0, 1], [0, 0]);
            expect(manager.isTransitioning()).toBe(true);
        });

        it('does not activate for same position', () => {
            manager.startTransition([0, 0], [0, 0]);
            expect(manager.isTransitioning()).toBe(false);
        });

        it('sets direction correctly for right movement', () => {
            manager.startTransition([0, 0], [1, 0]);
            const state = manager.getState();
            expect(state.direction.x).toBe(1);
            expect(state.direction.y).toBe(0);
        });

        it('sets direction correctly for up movement', () => {
            manager.startTransition([0, 1], [0, 0]);
            const state = manager.getState();
            expect(state.direction.x).toBe(0);
            expect(state.direction.y).toBe(-1);
        });
    });

    describe('update', () => {
        it('progresses through slide-out phase', () => {
            manager.startTransition([0, 0], [1, 0]);
            expect(manager.getState().phase).toBe('slide-out');

            // Partial update
            manager.update(0.075);  // Half of phase duration
            expect(manager.getState().phase).toBe('slide-out');
            expect(manager.isTransitioning()).toBe(true);
        });

        it('transitions to slide-in phase after slide-out', () => {
            manager.startTransition([0, 0], [1, 0]);

            // Complete slide-out phase (0.15s)
            manager.update(0.15);
            expect(manager.getState().phase).toBe('slide-in');
        });

        it('completes transition after both phases', () => {
            manager.startTransition([0, 0], [1, 0]);

            // Complete both phases
            manager.update(0.15);  // slide-out
            manager.update(0.15);  // slide-in

            expect(manager.isTransitioning()).toBe(false);
        });

        it('does nothing when inactive', () => {
            manager.update(1.0);
            expect(manager.isTransitioning()).toBe(false);
        });
    });

    describe('getOffset', () => {
        it('returns negative offset during slide-out (moving right)', () => {
            manager.startTransition([0, 0], [1, 0]);
            manager.update(0.15);  // Complete slide-out

            // At end of slide-out, should be at -roomWidth
            const offset = manager.getOffset();
            // Now in slide-in phase, starting from +roomWidth
            expect(offset.x).toBeGreaterThan(0);
        });

        it('returns positive offset at start of slide-in (moving right)', () => {
            manager.startTransition([0, 0], [1, 0]);
            manager.update(0.15);  // Complete slide-out, start slide-in

            const offset = manager.getOffset();
            expect(offset.x).toBe(1920);  // Full room width offset
        });

        it('returns zero offset after transition complete', () => {
            manager.startTransition([0, 0], [1, 0]);
            manager.update(0.15);  // slide-out
            manager.update(0.15);  // slide-in

            const offset = manager.getOffset();
            expect(offset.x).toBe(0);
            expect(offset.y).toBe(0);
        });

        it('applies vertical offset for up/down transitions', () => {
            manager.startTransition([0, 0], [0, 1]);  // Moving down
            manager.update(0.15);  // Complete slide-out

            const offset = manager.getOffset();
            expect(offset.y).toBe(640);  // Room height
            expect(offset.x).toBe(0);
        });
    });

    describe('diagonal transitions', () => {
        it('handles diagonal movement', () => {
            manager.startTransition([0, 0], [1, 1]);
            expect(manager.isTransitioning()).toBe(true);

            const state = manager.getState();
            expect(state.direction.x).toBe(1);
            expect(state.direction.y).toBe(1);
        });
    });

    describe('screen shake', () => {
        it('starts inactive', () => {
            expect(manager.isShaking()).toBe(false);
        });

        it('activates shake when startShake called', () => {
            manager.startShake();
            expect(manager.isShaking()).toBe(true);
        });

        it('returns non-zero offset when shaking', () => {
            manager.startShake(1.0);
            const offset = manager.getOffset();
            // Shake uses sin/cos so offset will be non-zero
            expect(offset.x !== 0 || offset.y !== 0).toBe(true);
        });

        it('deactivates after duration elapses', () => {
            manager.startShake(1.0, 0.1);  // 0.1s duration
            manager.update(0.15);  // Past duration
            expect(manager.isShaking()).toBe(false);
        });

        it('clamps intensity to valid range', () => {
            manager.startShake(2.0);  // Above max
            const state = manager.getShakeState();
            expect(state.intensity).toBeLessThanOrEqual(1);

            manager.startShake(-1);  // Below min
            const state2 = manager.getShakeState();
            expect(state2.intensity).toBeGreaterThanOrEqual(0);
        });

        it('returns zero offset after shake completes', () => {
            manager.startShake(1.0, 0.1);
            manager.update(0.2);  // Complete shake
            const offset = manager.getOffset();
            expect(offset.x).toBe(0);
            expect(offset.y).toBe(0);
        });

        it('combines shake with transition offset', () => {
            // Start both a transition and shake
            manager.startTransition([0, 0], [1, 0]);
            manager.startShake(1.0);

            const offset = manager.getOffset();
            // Should have both transition and shake contributing
            // Since we're in slide-out, x should be negative from transition
            // Shake adds random offset
            expect(Math.abs(offset.x) > 0 || Math.abs(offset.y) > 0).toBe(true);
        });

        it('uses custom duration when provided', () => {
            manager.startShake(1.0, 0.5);
            const state = manager.getShakeState();
            expect(state.timeRemaining).toBe(0.5);
        });
    });
});
