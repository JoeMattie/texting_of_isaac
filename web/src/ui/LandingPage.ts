export interface SessionListItem {
    sessionId: string;
    playerHealth: number;
    floor: number;
    spectatorCount: number;
}

export interface LandingPageCallbacks {
    onPlay: () => void;
    onSpectate: () => void;
    onJoinSession?: (sessionId: string) => void;
}

export class LandingPage {
    private container: HTMLElement;
    private element: HTMLElement;
    private sessionListEl: HTMLElement;
    private callbacks: LandingPageCallbacks;

    constructor(container: HTMLElement, callbacks: LandingPageCallbacks) {
        this.container = container;
        this.callbacks = callbacks;

        this.element = document.createElement('div');
        this.element.className = 'landing-page pixel-text scanlines';
        this.element.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: #000;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 200;
        `;

        // Title
        const title = document.createElement('h1');
        title.textContent = 'TEXTING OF ISAAC';
        title.style.cssText = `
            font-size: 32px;
            color: #fff;
            text-shadow: 0 0 10px #ff0000, 0 0 20px #ff0000;
            margin-bottom: 8px;
        `;
        this.element.appendChild(title);

        // Subtitle
        const subtitle = document.createElement('div');
        subtitle.textContent = 'Web Edition';
        subtitle.style.cssText = 'font-size: 12px; color: #888; margin-bottom: 48px;';
        this.element.appendChild(subtitle);

        // Menu
        const menu = document.createElement('div');
        menu.style.cssText = 'display: flex; flex-direction: column; gap: 16px;';

        const newGameBtn = this.createMenuItem('> NEW GAME', 'menu-new-game');
        newGameBtn.addEventListener('click', () => callbacks.onPlay());
        menu.appendChild(newGameBtn);

        const spectateBtn = this.createMenuItem('> SPECTATE', 'menu-spectate');
        spectateBtn.addEventListener('click', () => callbacks.onSpectate());
        menu.appendChild(spectateBtn);

        this.element.appendChild(menu);

        // Session list (hidden by default)
        this.sessionListEl = document.createElement('div');
        this.sessionListEl.className = 'session-list pixel-border';
        this.sessionListEl.style.cssText = `
            display: none;
            margin-top: 24px;
            padding: 16px;
            background: rgba(0, 0, 0, 0.8);
            max-height: 200px;
            overflow-y: auto;
            min-width: 300px;
        `;
        this.element.appendChild(this.sessionListEl);

        // Footer
        const footer = document.createElement('div');
        footer.textContent = 'WASD to move, Arrow keys to shoot';
        footer.style.cssText = `
            position: absolute;
            bottom: 32px;
            font-size: 10px;
            color: #666;
        `;
        this.element.appendChild(footer);

        this.container.appendChild(this.element);
    }

    private createMenuItem(text: string, className: string): HTMLElement {
        const item = document.createElement('div');
        item.textContent = text;
        item.className = className;
        item.style.cssText = `
            font-size: 16px;
            color: #fff;
            cursor: pointer;
            padding: 8px 16px;
        `;
        item.addEventListener('mouseenter', () => {
            item.style.color = '#ffcc00';
        });
        item.addEventListener('mouseleave', () => {
            item.style.color = '#fff';
        });
        return item;
    }

    showSessionList(sessions: SessionListItem[]): void {
        this.sessionListEl.style.display = 'block';
        this.sessionListEl.innerHTML = '';

        if (sessions.length === 0) {
            this.sessionListEl.innerHTML = '<div style="color: #888;">No active games</div>';
            return;
        }

        for (const session of sessions) {
            const item = document.createElement('div');
            item.style.cssText = `
                padding: 8px;
                cursor: pointer;
                border-bottom: 1px solid #333;
            `;
            const hearts = '\u2665'.repeat(session.playerHealth);
            item.innerHTML = `
                <span style="color: #fff;">${session.sessionId.slice(0, 8)}</span>
                <span style="color: #888;"> - F${session.floor} - </span>
                <span style="color: #ff0000;">${hearts}</span>
                <span style="color: #888;"> (${session.spectatorCount} watching)</span>
            `;
            item.addEventListener('click', () => {
                this.callbacks.onJoinSession?.(session.sessionId);
            });
            item.addEventListener('mouseenter', () => {
                item.style.background = '#222';
            });
            item.addEventListener('mouseleave', () => {
                item.style.background = 'transparent';
            });
            this.sessionListEl.appendChild(item);
        }
    }

    hideSessionList(): void {
        this.sessionListEl.style.display = 'none';
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
}
