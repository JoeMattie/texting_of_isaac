import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { SpectatorOverlay } from '../ui/SpectatorOverlay';

describe('SpectatorOverlay', () => {
    let container: HTMLElement;

    beforeEach(() => {
        container = document.createElement('div');
        document.body.appendChild(container);
    });

    afterEach(() => {
        container.remove();
    });

    it('creates spectator overlay', () => {
        const overlay = new SpectatorOverlay(container);
        expect(container.querySelector('.spectator-overlay')).not.toBeNull();
    });

    it('shows SPECTATOR MODE badge', () => {
        const overlay = new SpectatorOverlay(container);
        expect(container.textContent).toContain('SPECTATOR MODE');
    });

    it('shows watching session ID', () => {
        const overlay = new SpectatorOverlay(container);
        overlay.update({ sessionId: 'test123', spectatorCount: 5, playerHealth: 3, floor: 2, items: [], timePlayed: 120 });
        expect(container.textContent).toContain('test123');
    });

    it('shows spectator count', () => {
        const overlay = new SpectatorOverlay(container);
        overlay.update({ sessionId: 'abc', spectatorCount: 5, playerHealth: 3, floor: 2, items: [], timePlayed: 0 });
        expect(container.textContent).toContain('5');
    });

    it('shows player health', () => {
        const overlay = new SpectatorOverlay(container);
        overlay.update({ sessionId: 'abc', spectatorCount: 1, playerHealth: 4, floor: 1, items: [], timePlayed: 0 });
        expect(container.innerHTML).toContain('♥♥♥♥');
    });

    it('shows floor number', () => {
        const overlay = new SpectatorOverlay(container);
        overlay.update({ sessionId: 'abc', spectatorCount: 1, playerHealth: 3, floor: 3, items: [], timePlayed: 0 });
        expect(container.textContent).toContain('Floor 3');
    });

    it('shows time played', () => {
        const overlay = new SpectatorOverlay(container);
        overlay.update({ sessionId: 'abc', spectatorCount: 1, playerHealth: 3, floor: 1, items: [], timePlayed: 125 });
        expect(container.textContent).toContain('2:05');
    });

    it('destroy removes overlay', () => {
        const overlay = new SpectatorOverlay(container);
        overlay.destroy();
        expect(container.querySelector('.spectator-overlay')).toBeNull();
    });
});
