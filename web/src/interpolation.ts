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
