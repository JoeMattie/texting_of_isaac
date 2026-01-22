// web/src/ui.ts

import { SessionInfo } from './network';

export interface UIData {
    currency: { coins: number; bombs: number };
    health: { current: number; max: number };
    items: string[];
}

export class UIManager {
    private sessionElement: HTMLElement | null = null;
    private healthElement: HTMLElement | null = null;
    private currencyElement: HTMLElement | null = null;
    private itemsElement: HTMLElement | null = null;
    private statusElement: HTMLElement | null = null;

    constructor() {
        this.createUI();
    }

    private createUI(): void {
        // Create UI container
        const uiContainer = document.createElement('div');
        uiContainer.id = 'ui-container';
        uiContainer.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 20px;
            font-family: monospace;
            font-size: 14px;
            border: 2px solid #00ff00;
            min-width: 200px;
        `;

        // Session info
        this.sessionElement = document.createElement('div');
        this.sessionElement.id = 'session-info';
        uiContainer.appendChild(this.sessionElement);

        // Health display
        this.healthElement = document.createElement('div');
        this.healthElement.id = 'health-display';
        this.healthElement.style.marginTop = '10px';
        uiContainer.appendChild(this.healthElement);

        // Currency display
        this.currencyElement = document.createElement('div');
        this.currencyElement.id = 'currency-display';
        this.currencyElement.style.marginTop = '10px';
        uiContainer.appendChild(this.currencyElement);

        // Items display
        this.itemsElement = document.createElement('div');
        this.itemsElement.id = 'items-display';
        this.itemsElement.style.marginTop = '10px';
        uiContainer.appendChild(this.itemsElement);

        // Status display
        this.statusElement = document.createElement('div');
        this.statusElement.id = 'status-display';
        this.statusElement.style.marginTop = '10px';
        this.statusElement.style.color = '#ffff00';
        uiContainer.appendChild(this.statusElement);

        document.body.appendChild(uiContainer);
    }

    updateSessionInfo(info: SessionInfo): void {
        if (this.sessionElement) {
            this.sessionElement.innerHTML = `
                <strong>Session:</strong> ${info.sessionId}<br>
                <strong>Role:</strong> ${info.role}
            `;
        }
    }

    updateUI(uiData: UIData): void {
        // Update health
        if (this.healthElement) {
            const hearts = '♥'.repeat(uiData.health.current) +
                          '♡'.repeat(uiData.health.max - uiData.health.current);
            this.healthElement.innerHTML = `<strong>Health:</strong> ${hearts}`;
        }

        // Update currency
        if (this.currencyElement) {
            this.currencyElement.innerHTML = `
                <strong>Coins:</strong> ${uiData.currency.coins}<br>
                <strong>Bombs:</strong> ${uiData.currency.bombs}
            `;
        }

        // Update items
        if (this.itemsElement && uiData.items.length > 0) {
            const itemsList = uiData.items.map(item => `• ${item}`).join('<br>');
            this.itemsElement.innerHTML = `<strong>Items:</strong><br>${itemsList}`;
        }
    }

    showDisconnected(): void {
        if (this.statusElement) {
            this.statusElement.textContent = '⚠ Disconnected';
        }
    }

    showError(error: string): void {
        if (this.statusElement) {
            this.statusElement.textContent = `⚠ Error: ${error}`;
        }
    }

    clear(): void {
        if (this.statusElement) {
            this.statusElement.textContent = '';
        }
    }
}
