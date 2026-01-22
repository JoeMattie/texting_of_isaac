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

/** Current shake state */
export type ShakeState = {
    active: boolean;
    intensity: number;  // Current shake intensity (decays over time)
    timeRemaining: number;  // Seconds remaining
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

    private shakeState: ShakeState = {
        active: false,
        intensity: 0,
        timeRemaining: 0
    };

    /** Duration of each phase in seconds */
    private readonly phaseDuration = 0.15;

    /** Default shake duration in seconds */
    private readonly shakeDuration = 0.3;

    /** Maximum shake offset in pixels */
    private readonly maxShakeOffset = 8;

    /** Room dimensions in pixels */
    private readonly roomWidth: number;
    private readonly roomHeight: number;

    constructor(roomWidth: number = 1920, roomHeight: number = 640) {
        this.roomWidth = roomWidth;
        this.roomHeight = roomHeight;
    }

    /**
     * Start a screen shake effect.
     * @param intensity - Shake intensity from 0 to 1 (default 1)
     * @param duration - Duration in seconds (default 0.3)
     */
    startShake(intensity: number = 1, duration?: number): void {
        this.shakeState = {
            active: true,
            intensity: Math.max(0, Math.min(1, intensity)),
            timeRemaining: duration ?? this.shakeDuration
        };
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
     * Update transition animation and shake effect.
     * @param dt - Delta time in seconds
     */
    update(dt: number): void {
        // Update room transition
        if (this.state.active) {
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

        // Update shake effect
        if (this.shakeState.active) {
            this.shakeState.timeRemaining -= dt;
            if (this.shakeState.timeRemaining <= 0) {
                this.shakeState = {
                    active: false,
                    intensity: 0,
                    timeRemaining: 0
                };
            }
        }
    }

    /**
     * Get current offset to apply to game container.
     * Combines room transition offset with screen shake.
     * @returns Pixel offset { x, y } to apply
     */
    getOffset(): { x: number; y: number } {
        let offsetX = 0;
        let offsetY = 0;

        // Add room transition offset
        if (this.state.active) {
            const { phase, progress, direction } = this.state;

            // Ease function for smoother animation
            const eased = this.easeInOutQuad(progress);

            if (phase === 'slide-out') {
                // Slide from center to off-screen in direction
                offsetX = -direction.x * this.roomWidth * eased;
                offsetY = -direction.y * this.roomHeight * eased;
            } else {
                // slide-in: Slide from opposite side to center
                offsetX = direction.x * this.roomWidth * (1 - eased);
                offsetY = direction.y * this.roomHeight * (1 - eased);
            }
        }

        // Add shake offset
        if (this.shakeState.active) {
            const shake = this.getShakeOffset();
            offsetX += shake.x;
            offsetY += shake.y;
        }

        return { x: offsetX, y: offsetY };
    }

    /**
     * Calculate current shake offset with decay.
     */
    private getShakeOffset(): { x: number; y: number } {
        if (!this.shakeState.active) {
            return { x: 0, y: 0 };
        }

        // Calculate decay factor (1 at start, 0 at end)
        const decay = this.shakeState.timeRemaining / this.shakeDuration;

        // Random offset scaled by intensity and decay
        const magnitude = this.maxShakeOffset * this.shakeState.intensity * decay;

        // Use sine waves for more organic shake (based on time)
        const time = Date.now() / 1000;
        const x = Math.sin(time * 50) * magnitude;
        const y = Math.cos(time * 47) * magnitude;  // Different frequency for y

        return { x, y };
    }

    /**
     * Check if currently transitioning.
     */
    isTransitioning(): boolean {
        return this.state.active;
    }

    /**
     * Check if currently shaking.
     */
    isShaking(): boolean {
        return this.shakeState.active;
    }

    /**
     * Get current transition state (for debugging/UI).
     */
    getState(): TransitionState {
        return { ...this.state };
    }

    /**
     * Get current shake state (for debugging/UI).
     */
    getShakeState(): ShakeState {
        return { ...this.shakeState };
    }

    /**
     * Quadratic ease-in-out for smooth animation.
     */
    private easeInOutQuad(t: number): number {
        return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    }
}
