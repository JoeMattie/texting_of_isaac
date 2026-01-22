/**
 * Interpolated position tracking for an entity.
 */
export interface InterpolatedPosition {
    currentX: number;
    currentY: number;
    targetX: number;
    targetY: number;
}

/**
 * Linear interpolation between two values.
 * @param start - Starting value
 * @param end - Ending value
 * @param t - Interpolation factor (0 to 1)
 * @returns Interpolated value
 */
export function lerp(start: number, end: number, t: number): number {
    return start + (end - start) * t;
}

/**
 * Configuration for interpolation behavior.
 */
export const INTERPOLATION_CONFIG = {
    /** Higher = snappier movement */
    smoothing: 15,
    /** Distance in pixels above which we snap instead of lerp */
    snapThreshold: 160,
};

/**
 * Manages interpolated positions for smooth rendering.
 */
export class InterpolationManager {
    private positions: Map<number, InterpolatedPosition> = new Map();

    /**
     * Set target position for an entity.
     * New entities start at target position (no lerp from origin).
     */
    setTarget(entityId: number, x: number, y: number): void {
        const existing = this.positions.get(entityId);
        if (existing) {
            existing.targetX = x;
            existing.targetY = y;
        } else {
            this.positions.set(entityId, {
                currentX: x,
                currentY: y,
                targetX: x,
                targetY: y,
            });
        }
    }

    /**
     * Update all interpolated positions.
     * @param dt - Delta time in seconds
     */
    update(dt: number): void {
        const t = Math.min(1, INTERPOLATION_CONFIG.smoothing * dt);

        for (const [entityId, pos] of this.positions) {
            const dx = pos.targetX - pos.currentX;
            const dy = pos.targetY - pos.currentY;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance > INTERPOLATION_CONFIG.snapThreshold) {
                pos.currentX = pos.targetX;
                pos.currentY = pos.targetY;
            } else {
                pos.currentX = lerp(pos.currentX, pos.targetX, t);
                pos.currentY = lerp(pos.currentY, pos.targetY, t);
            }
        }
    }

    /**
     * Get interpolated position for an entity.
     */
    getPosition(entityId: number): InterpolatedPosition | null {
        return this.positions.get(entityId) || null;
    }

    /**
     * Remove entity from tracking.
     */
    removeEntity(entityId: number): void {
        this.positions.delete(entityId);
    }
}
