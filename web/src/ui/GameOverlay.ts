// web/src/ui/GameOverlay.ts
/**
 * Full-screen overlay for game end states (victory/death).
 */

export type GameEndState = 'victory' | 'game_over' | null;

export interface GameOverlayCallbacks {
    onRestart?: () => void;
    onMainMenu?: () => void;
}

export class GameOverlay {
    private container: HTMLElement;
    private element: HTMLElement;
    private titleEl: HTMLElement;
    private subtitleEl: HTMLElement;
    private statsEl: HTMLElement;
    private callbacks: GameOverlayCallbacks;
    private currentState: GameEndState = null;

    constructor(container: HTMLElement, callbacks: GameOverlayCallbacks = {}) {
        this.container = container;
        this.callbacks = callbacks;

        this.element = document.createElement('div');
        this.element.className = 'game-overlay';
        this.element.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.85);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 200;
        `;

        // Title (YOU DIED / VICTORY)
        this.titleEl = document.createElement('div');
        this.titleEl.className = 'game-overlay-title pixel-text';
        this.titleEl.style.cssText = `
            font-size: 48px;
            margin-bottom: 16px;
            text-shadow: 0 0 20px currentColor;
        `;
        this.element.appendChild(this.titleEl);

        // Subtitle
        this.subtitleEl = document.createElement('div');
        this.subtitleEl.className = 'game-overlay-subtitle pixel-text';
        this.subtitleEl.style.cssText = `
            font-size: 14px;
            color: #888;
            margin-bottom: 32px;
        `;
        this.element.appendChild(this.subtitleEl);

        // Stats container
        this.statsEl = document.createElement('div');
        this.statsEl.className = 'game-overlay-stats pixel-text';
        this.statsEl.style.cssText = `
            font-size: 12px;
            color: #aaa;
            text-align: center;
            margin-bottom: 48px;
            line-height: 1.8;
        `;
        this.element.appendChild(this.statsEl);

        // Button container
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = `
            display: flex;
            gap: 16px;
        `;

        // Restart button
        const restartBtn = this.createButton('PLAY AGAIN', () => {
            this.callbacks.onRestart?.();
        });
        buttonContainer.appendChild(restartBtn);

        // Main menu button
        const menuBtn = this.createButton('MAIN MENU', () => {
            this.callbacks.onMainMenu?.();
        });
        menuBtn.style.background = '#333';
        buttonContainer.appendChild(menuBtn);

        this.element.appendChild(buttonContainer);
        this.container.appendChild(this.element);
    }

    private createButton(text: string, onClick: () => void): HTMLElement {
        const btn = document.createElement('button');
        btn.className = 'pixel-text pixel-border';
        btn.textContent = text;
        btn.style.cssText = `
            background: #444;
            color: #fff;
            border: none;
            padding: 12px 24px;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.1s;
        `;
        btn.onmouseenter = () => { btn.style.background = '#666'; };
        btn.onmouseleave = () => { btn.style.background = '#444'; };
        btn.onclick = onClick;
        return btn;
    }

    /**
     * Show the overlay for a specific end state.
     */
    show(state: 'victory' | 'game_over', stats?: { floor?: number; items?: string[] }): void {
        this.currentState = state;

        if (state === 'victory') {
            this.titleEl.textContent = 'VICTORY';
            this.titleEl.style.color = '#ffcc00';
            this.subtitleEl.textContent = 'You have conquered the basement!';
        } else {
            this.titleEl.textContent = 'YOU DIED';
            this.titleEl.style.color = '#ff0000';
            this.subtitleEl.textContent = 'Your journey ends here...';
        }

        // Show stats if provided
        if (stats) {
            const lines: string[] = [];
            if (stats.floor !== undefined) {
                lines.push(`Floor Reached: ${stats.floor}`);
            }
            if (stats.items && stats.items.length > 0) {
                lines.push(`Items Collected: ${stats.items.length}`);
            }
            this.statsEl.innerHTML = lines.join('<br>');
        } else {
            this.statsEl.innerHTML = '';
        }

        this.element.style.display = 'flex';
    }

    /**
     * Hide the overlay.
     */
    hide(): void {
        this.element.style.display = 'none';
        this.currentState = null;
    }

    /**
     * Check if overlay is currently visible.
     */
    isVisible(): boolean {
        return this.element.style.display === 'flex';
    }

    /**
     * Get current overlay state.
     */
    getState(): GameEndState {
        return this.currentState;
    }

    /**
     * Clean up the overlay element.
     */
    destroy(): void {
        this.element.remove();
    }
}
