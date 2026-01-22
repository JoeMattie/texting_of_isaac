// web/src/transitions.ts
/**
 * Manages room transition animations with directional slide effects.
 */

import { Config } from './config';

/** Direction of room transition */
export type TransitionDirection = {
    x: number;  // -1, 0, or 1
    y: number;  // -1, 0, or 1
};

/** Current transition state */
export type TransitionState = {
    active: boolean;
    phase: 'slide-out' | 'slide-in' | 'none';
    progress: number;  // 0 to 1
    direction: TransitionDirection;
};

/**
 * Manages smooth directional slide transitions between rooms.
 *
 * When a room transition is detected:
 * 1. Phase 1 (slide-out): Current room slides off-screen in direction of movement
 * 2. Phase 2 (slide-in): New room slides in from opposite side
 */
export class TransitionManager {
    private state: TransitionState = {
        active: false,
        phase: 'none',
        progress: 0,
        direction: { x: 0, y: 0 }
    };

    /** Duration of each phase in seconds */
    private readonly phaseDuration = 0.15;

    /** Room dimensions in pixels */
    private readonly roomWidth: number;
    private readonly roomHeight: number;

    constructor(roomWidth: number = 1920, roomHeight: number = 640) {
        this.roomWidth = roomWidth;
        this.roomHeight = roomHeight;
    }

    /**
     * Start a room transition animation.
     * @param from - Previous room position [x, y]
     * @param to - New room position [x, y]
     */
    startTransition(from: [number, number], to: [number, number]): void {
        // Calculate direction from room position delta
        const direction: TransitionDirection = {
            x: Math.sign(to[0] - from[0]),
            y: Math.sign(to[1] - from[1])
        };

        // Only start if there's actually a direction
        if (direction.x === 0 && direction.y === 0) {
            return;
        }

        this.state = {
            active: true,
            phase: 'slide-out',
            progress: 0,
            direction
        };
    }

    /**
     * Update transition animation.
     * @param dt - Delta time in seconds
     */
    update(dt: number): void {
        if (!this.state.active) {
            return;
        }

        // Advance progress
        this.state.progress += dt / this.phaseDuration;

        if (this.state.progress >= 1) {
            if (this.state.phase === 'slide-out') {
                // Switch to slide-in phase
                this.state.phase = 'slide-in';
                this.state.progress = 0;
            } else {
                // Transition complete
                this.state = {
                    active: false,
                    phase: 'none',
                    progress: 0,
                    direction: { x: 0, y: 0 }
                };
            }
        }
    }

    /**
     * Get current offset to apply to game container.
     * @returns Pixel offset { x, y } to apply
     */
    getOffset(): { x: number; y: number } {
        if (!this.state.active) {
            return { x: 0, y: 0 };
        }

        const { phase, progress, direction } = this.state;

        // Ease function for smoother animation
        const eased = this.easeInOutQuad(progress);

        if (phase === 'slide-out') {
            // Slide from center to off-screen in direction
            return {
                x: -direction.x * this.roomWidth * eased,
                y: -direction.y * this.roomHeight * eased
            };
        } else {
            // slide-in: Slide from opposite side to center
            return {
                x: direction.x * this.roomWidth * (1 - eased),
                y: direction.y * this.roomHeight * (1 - eased)
            };
        }
    }

    /**
     * Check if currently transitioning.
     */
    isTransitioning(): boolean {
        return this.state.active;
    }

    /**
     * Get current transition state (for debugging/UI).
     */
    getState(): TransitionState {
        return { ...this.state };
    }

    /**
     * Quadratic ease-in-out for smooth animation.
     */
    private easeInOutQuad(t: number): number {
        return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    }
}
