export interface HUDData {
    health: { current: number; max: number };
    coins: number;
    bombs: number;
    items: string[];
    floor: number;
}

export class HUD {
    private container: HTMLElement;
    private element: HTMLElement;
    private healthEl: HTMLElement;
    private coinsEl: HTMLElement;
    private bombsEl: HTMLElement;
    private itemsEl: HTMLElement;
    private floorEl: HTMLElement;

    /** Previous values to detect changes for animations */
    private prevHealth: number = -1;
    private prevCoins: number = -1;
    private prevBombs: number = -1;

    constructor(container: HTMLElement) {
        this.container = container;
        this.element = document.createElement('div');
        this.element.className = 'hud pixel-text pixel-border';
        this.element.style.cssText = `
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 48px;
            background: var(--color-bg, rgba(0,0,0,0.9));
            display: flex;
            align-items: center;
            padding: 0 16px;
            gap: 24px;
            font-size: 12px;
            z-index: 100;
        `;

        // Health
        this.healthEl = document.createElement('div');
        this.healthEl.className = 'hud-health';
        this.healthEl.style.color = 'var(--color-red, #ff0000)';
        this.element.appendChild(this.healthEl);

        // Coins
        this.coinsEl = document.createElement('div');
        this.coinsEl.className = 'hud-coins';
        this.coinsEl.style.color = 'var(--color-gold, #ffcc00)';
        this.element.appendChild(this.coinsEl);

        // Bombs
        this.bombsEl = document.createElement('div');
        this.bombsEl.className = 'hud-bombs';
        this.bombsEl.style.color = 'var(--color-white, #ffffff)';
        this.element.appendChild(this.bombsEl);

        // Items
        this.itemsEl = document.createElement('div');
        this.itemsEl.className = 'hud-items';
        this.itemsEl.style.cssText = 'flex: 1; display: flex; gap: 8px; overflow: hidden;';
        this.element.appendChild(this.itemsEl);

        // Floor
        this.floorEl = document.createElement('div');
        this.floorEl.className = 'hud-floor';
        this.floorEl.style.color = 'var(--color-white, #ffffff)';
        this.element.appendChild(this.floorEl);

        this.container.appendChild(this.element);
    }

    update(data: HUDData): void {
        // Health hearts – detect damage for shake animation
        const healthChanged = this.prevHealth !== -1 && data.health.current < this.prevHealth;
        if (healthChanged) {
            this.animateDamage();
        }
        this.prevHealth = data.health.current;

        const fullHearts = '<span style="color: #ff0000">♥</span>'.repeat(data.health.current);
        const emptyHearts = '<span style="color: #666666">♡</span>'.repeat(data.health.max - data.health.current);
        this.healthEl.innerHTML = fullHearts + emptyHearts;

        // Coins – detect pickup for bounce animation
        const coinsChanged = this.prevCoins !== -1 && data.coins > this.prevCoins;
        if (coinsChanged) {
            this.animateCoinPickup();
        }
        this.prevCoins = data.coins;
        this.coinsEl.textContent = `$ ${data.coins}`;

        // Bombs – detect pickup for bounce animation
        const bombsChanged = this.prevBombs !== -1 && data.bombs > this.prevBombs;
        if (bombsChanged) {
            this.animateBombPickup();
        }
        this.prevBombs = data.bombs;
        this.bombsEl.textContent = `B ${data.bombs}`;

        // Items (show up to 6)
        const visibleItems = data.items.slice(0, 6);
        this.itemsEl.textContent = visibleItems.join(' ');

        // Floor
        this.floorEl.textContent = `F${data.floor}`;
    }

    /**
     * Shake the health hearts display – triggered when the player takes damage.
     */
    animateDamage(): void {
        this.triggerAnimation(this.healthEl, 'hud-shake');
    }

    /**
     * Bounce the coin counter – triggered when coins are picked up.
     */
    animateCoinPickup(): void {
        this.triggerAnimation(this.coinsEl, 'hud-bounce');
    }

    /**
     * Bounce the bomb counter – triggered when bombs are picked up.
     */
    animateBombPickup(): void {
        this.triggerAnimation(this.bombsEl, 'hud-bounce');
    }

    show(): void {
        this.element.style.display = 'flex';
    }

    hide(): void {
        this.element.style.display = 'none';
    }

    destroy(): void {
        this.element.remove();
    }

    /**
     * Apply a CSS animation class to an element, resetting it first so it
     * re-triggers even if the same animation fires multiple times quickly.
     */
    private triggerAnimation(el: HTMLElement, animClass: string): void {
        // Remove class to reset animation
        el.classList.remove(animClass);
        // Force reflow so removal takes effect before re-adding
        void el.offsetWidth;
        el.classList.add(animClass);

        // Auto-remove after animation completes (300ms)
        const onEnd = () => {
            el.classList.remove(animClass);
            el.removeEventListener('animationend', onEnd);
        };
        el.addEventListener('animationend', onEnd);
    }
}
