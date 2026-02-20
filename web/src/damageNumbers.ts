// web/src/damageNumbers.ts
/**
 * Floating damage number popups that drift upward and fade out.
 * Red for player damage received, yellow for enemy damage received.
 */

import * as PIXI from 'pixi.js';

/** Who took the damage: determines color */
export type DamageTarget = 'player' | 'enemy';

/** Colors for damage popups */
export const DAMAGE_COLORS: Record<DamageTarget, number> = {
    player: 0xff3333,  // Red   – player took damage
    enemy:  0xffcc00,  // Gold  – enemy took damage
};

/** Configuration for damage number display */
export const DAMAGE_NUMBER_CONFIG = {
    /** Pixels per second the number drifts upward */
    driftSpeed: 60,
    /** Total display duration in seconds */
    duration: 0.9,
    /** Font size in pixels */
    fontSize: 14,
    /** How much the number spreads horizontally (±pixels) */
    horizontalSpread: 12,
} as const;

/** Active damage popup instance */
interface DamagePopup {
    text: PIXI.Text;
    startX: number;
    startY: number;
    elapsed: number;
    duration: number;
    inUse: boolean;
}

/**
 * Manages floating damage number popups using an object pool.
 */
export class DamageNumberManager {
    private container: PIXI.Container;
    private pool: DamagePopup[] = [];
    private readonly poolSize: number;

    constructor(container: PIXI.Container, poolSize: number = 20) {
        this.container = container;
        this.poolSize = poolSize;
        this.prewarm();
    }

    /**
     * Show a damage number at the given position.
     * @param x - World pixel X coordinate
     * @param y - World pixel Y coordinate
     * @param damage - Amount of damage (will be displayed as integer)
     * @param target - Who took the damage ('player' = red, 'enemy' = yellow)
     */
    add(x: number, y: number, damage: number, target: DamageTarget): void {
        if (typeof document === 'undefined') return; // no-op in test env without PIXI

        const popup = this.acquire(target);
        if (!popup) return;

        // Spread horizontally slightly so multiple hits don't overlap
        const spreadX = (Math.random() - 0.5) * 2 * DAMAGE_NUMBER_CONFIG.horizontalSpread;

        popup.text.text = String(Math.round(damage));
        popup.text.alpha = 1;
        popup.text.visible = true;
        popup.startX = x + spreadX;
        popup.startY = y;
        popup.text.x = popup.startX;
        popup.text.y = popup.startY;
        popup.elapsed = 0;
        popup.duration = DAMAGE_NUMBER_CONFIG.duration;
        popup.inUse = true;
    }

    /**
     * Update all active popups.
     * @param dt - Delta time in seconds
     */
    update(dt: number): void {
        for (const popup of this.pool) {
            if (!popup.inUse) continue;

            popup.elapsed += dt;
            const progress = popup.elapsed / popup.duration;

            if (progress >= 1) {
                this.release(popup);
                continue;
            }

            // Drift upward
            popup.text.y = popup.startY - popup.elapsed * DAMAGE_NUMBER_CONFIG.driftSpeed;

            // Fade out in the second half
            if (progress > 0.5) {
                popup.text.alpha = 1 - (progress - 0.5) * 2;
            }

            // Pop scale: briefly enlarge then shrink back
            const scalePeak = 1.4;
            const scaleProgress = Math.min(progress * 4, 1); // peaks at 25% of duration
            const scale = 1 + (scalePeak - 1) * Math.sin(scaleProgress * Math.PI);
            popup.text.scale.set(scale);
        }
    }

    private prewarm(): void {
        for (let i = 0; i < this.poolSize; i++) {
            this.pool.push(this.createPopup(0xff3333));
        }
    }

    private createPopup(color: number): DamagePopup {
        let text: PIXI.Text;
        try {
            text = new PIXI.Text({
                text: '',
                style: {
                    fontFamily: "'Press Start 2P', monospace",
                    fontSize: DAMAGE_NUMBER_CONFIG.fontSize,
                    fill: color,
                    stroke: { color: 0x000000, width: 2 },
                    dropShadow: {
                        color: 0x000000,
                        blur: 2,
                        distance: 1,
                        alpha: 0.8,
                        angle: Math.PI / 4,
                    },
                },
            });
            text.anchor.set(0.5, 0.5);
            text.visible = false;
            this.container.addChild(text);
        } catch {
            // Fallback for environments without full PIXI support
            text = { text: '', alpha: 1, visible: false, x: 0, y: 0, scale: { set: () => {} }, anchor: { set: () => {} } } as unknown as PIXI.Text;
        }

        return {
            text,
            startX: 0,
            startY: 0,
            elapsed: 0,
            duration: DAMAGE_NUMBER_CONFIG.duration,
            inUse: false,
        };
    }

    private acquire(target: DamageTarget): DamagePopup | null {
        const color = DAMAGE_COLORS[target];

        // Find an idle popup
        const idle = this.pool.find(p => !p.inUse);
        if (idle) {
            // Re-tint for the target type
            try {
                (idle.text.style as any).fill = color;
            } catch { /* ignore */ }
            return idle;
        }

        // Pool exhausted – create an extra one if not too many
        if (this.pool.length < this.poolSize * 2) {
            const popup = this.createPopup(color);
            this.pool.push(popup);
            return popup;
        }

        return null;
    }

    private release(popup: DamagePopup): void {
        popup.inUse = false;
        popup.text.visible = false;
        popup.text.alpha = 1;
        popup.text.scale.set(1);
    }
}
