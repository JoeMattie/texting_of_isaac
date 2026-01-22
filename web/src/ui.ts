// web/src/ui.ts
import { HUD, HUDData } from './ui/HUD';
import { LandingPage, SessionListItem } from './ui/LandingPage';
import { SpectatorOverlay, SpectatorData } from './ui/SpectatorOverlay';
import { SessionInfo } from './network';

export interface UICallbacks {
    onPlay: () => void;
    onSpectate: () => void;
    onJoinSession: (sessionId: string) => void;
}

export class UIManager {
    private hud: HUD;
    private landingPage: LandingPage;
    private spectatorOverlay: SpectatorOverlay | null = null;
    private container: HTMLElement;
    private isSpectator: boolean = false;

    constructor(container: HTMLElement, callbacks: UICallbacks) {
        this.container = container;

        // Create components
        this.hud = new HUD(container);
        this.hud.hide();

        this.landingPage = new LandingPage(container, {
            onPlay: callbacks.onPlay,
            onSpectate: callbacks.onSpectate,
            onJoinSession: callbacks.onJoinSession
        });
    }

    showLandingPage(): void {
        this.landingPage.show();
        this.hud.hide();
        this.spectatorOverlay?.hide();
    }

    showGame(isSpectator: boolean = false): void {
        this.isSpectator = isSpectator;
        this.landingPage.hide();
        this.hud.show();

        if (isSpectator) {
            if (!this.spectatorOverlay) {
                this.spectatorOverlay = new SpectatorOverlay(this.container);
            }
            this.spectatorOverlay.show();
        } else {
            this.spectatorOverlay?.hide();
        }
    }

    updateHUD(data: HUDData): void {
        this.hud.update(data);
    }

    updateSpectatorOverlay(data: SpectatorData): void {
        this.spectatorOverlay?.update(data);
    }

    showSessionList(sessions: SessionListItem[]): void {
        this.landingPage.showSessionList(sessions);
    }

    updateSessionInfo(info: SessionInfo): void {
        // Could display session info somewhere if needed
        console.log('Session info:', info);
    }

    showDisconnected(): void {
        // Could show a disconnected message
        console.log('Disconnected');
    }

    showError(error: string): void {
        console.error('UI Error:', error);
    }

    destroy(): void {
        this.hud.destroy();
        this.landingPage.destroy();
        this.spectatorOverlay?.destroy();
    }
}

// Re-export types for convenience
export { HUDData } from './ui/HUD';
export { SessionListItem } from './ui/LandingPage';
export { SpectatorData } from './ui/SpectatorOverlay';
