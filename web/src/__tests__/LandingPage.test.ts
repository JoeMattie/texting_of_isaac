import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { LandingPage } from '../ui/LandingPage';

describe('LandingPage', () => {
    let container: HTMLElement;

    beforeEach(() => {
        container = document.createElement('div');
        document.body.appendChild(container);
    });

    afterEach(() => {
        container.remove();
    });

    it('creates landing page element', () => {
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate: () => {} });
        expect(container.querySelector('.landing-page')).not.toBeNull();
    });

    it('shows title', () => {
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate: () => {} });
        expect(container.textContent).toContain('TEXTING OF ISAAC');
    });

    it('shows NEW GAME option', () => {
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate: () => {} });
        expect(container.textContent).toContain('NEW GAME');
    });

    it('shows SPECTATE option', () => {
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate: () => {} });
        expect(container.textContent).toContain('SPECTATE');
    });

    it('calls onPlay when NEW GAME clicked', () => {
        const onPlay = vi.fn();
        const page = new LandingPage(container, { onPlay, onSpectate: () => {} });
        const newGameBtn = container.querySelector('.menu-new-game') as HTMLElement;
        newGameBtn?.click();
        expect(onPlay).toHaveBeenCalled();
    });

    it('calls onSpectate when SPECTATE clicked', () => {
        const onSpectate = vi.fn();
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate });
        const spectateBtn = container.querySelector('.menu-spectate') as HTMLElement;
        spectateBtn?.click();
        expect(onSpectate).toHaveBeenCalled();
    });

    it('shows session list', () => {
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate: () => {} });
        page.showSessionList([
            { sessionId: 'abc', playerHealth: 3, floor: 1, spectatorCount: 2 }
        ]);
        expect(container.textContent).toContain('abc');
    });

    it('destroy removes landing page', () => {
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate: () => {} });
        page.destroy();
        expect(container.querySelector('.landing-page')).toBeNull();
    });
});
