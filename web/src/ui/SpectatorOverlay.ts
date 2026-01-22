export interface SpectatorData {
    sessionId: string;
    spectatorCount: number;
    playerHealth: number;
    floor: number;
    items: string[];
    timePlayed: number; // seconds
}

export class SpectatorOverlay {
    private container: HTMLElement;
    private element: HTMLElement;
    private watchingEl: HTMLElement;
    private healthEl: HTMLElement;
    private floorEl: HTMLElement;
    private itemsEl: HTMLElement;
    private timeEl: HTMLElement;
    private countEl: HTMLElement;

    constructor(container: HTMLElement) {
        this.container = container;

        this.element = document.createElement('div');
        this.element.className = 'spectator-overlay';

        // Badge (top-left)
        const badge = document.createElement('div');
        badge.className = 'spectator-badge pixel-text';
        badge.textContent = 'SPECTATOR MODE';
        badge.style.cssText = `
            position: fixed;
            top: 16px;
            left: 16px;
            background: #ff0000;
            color: #fff;
            padding: 8px 12px;
            font-size: 10px;
            z-index: 150;
        `;
        this.element.appendChild(badge);

        // Watching label
        this.watchingEl = document.createElement('div');
        this.watchingEl.className = 'spectator-watching pixel-text';
        this.watchingEl.style.cssText = `
            position: fixed;
            top: 48px;
            left: 16px;
            color: #888;
            font-size: 8px;
            z-index: 150;
        `;
        this.element.appendChild(this.watchingEl);

        // Sidebar (right)
        const sidebar = document.createElement('div');
        sidebar.className = 'spectator-sidebar pixel-text pixel-border';
        sidebar.style.cssText = `
            position: fixed;
            top: 16px;
            right: 16px;
            bottom: 64px;
            width: 180px;
            background: rgba(0, 0, 0, 0.85);
            padding: 12px;
            font-size: 10px;
            z-index: 150;
            display: flex;
            flex-direction: column;
            gap: 12px;
        `;

        // Player info section
        const infoSection = document.createElement('div');
        infoSection.innerHTML = '<div style="color: #888; margin-bottom: 8px;">PLAYER INFO</div>';

        this.healthEl = document.createElement('div');
        this.healthEl.style.color = '#ff0000';
        infoSection.appendChild(this.healthEl);

        this.floorEl = document.createElement('div');
        this.floorEl.style.color = '#fff';
        infoSection.appendChild(this.floorEl);

        this.timeEl = document.createElement('div');
        this.timeEl.style.color = '#888';
        infoSection.appendChild(this.timeEl);

        this.itemsEl = document.createElement('div');
        this.itemsEl.style.cssText = 'color: #ffcc00; margin-top: 8px;';
        infoSection.appendChild(this.itemsEl);

        sidebar.appendChild(infoSection);

        // Spectator count
        this.countEl = document.createElement('div');
        this.countEl.style.color = '#888';
        sidebar.appendChild(this.countEl);

        // Chat placeholder
        const chatEl = document.createElement('div');
        chatEl.className = 'pixel-border';
        chatEl.style.cssText = `
            flex: 1;
            background: rgba(0, 0, 0, 0.5);
            padding: 8px;
            color: #666;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        `;
        chatEl.textContent = 'Chat coming soon...';
        sidebar.appendChild(chatEl);

        this.element.appendChild(sidebar);
        this.container.appendChild(this.element);
    }

    update(data: SpectatorData): void {
        this.watchingEl.textContent = `Watching: ${data.sessionId}`;
        this.healthEl.innerHTML = '♥'.repeat(data.playerHealth);
        this.floorEl.textContent = `Floor ${data.floor}`;
        this.timeEl.textContent = this.formatTime(data.timePlayed);
        this.countEl.textContent = `👁 ${data.spectatorCount} watching`;

        if (data.items.length > 0) {
            this.itemsEl.textContent = `Items: ${data.items.slice(0, 3).join(', ')}`;
        } else {
            this.itemsEl.textContent = '';
        }
    }

    private formatTime(seconds: number): string {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    show(): void {
        this.element.style.display = 'block';
    }

    hide(): void {
        this.element.style.display = 'none';
    }

    destroy(): void {
        this.element.remove();
    }
}
