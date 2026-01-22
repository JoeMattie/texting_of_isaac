// web/src/__tests__/GameOverlay.test.ts
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { GameOverlay } from '../ui/GameOverlay';

describe('GameOverlay', () => {
    let container: HTMLElement;
    let overlay: GameOverlay;

    beforeEach(() => {
        container = document.createElement('div');
        document.body.appendChild(container);
    });

    afterEach(() => {
        overlay?.destroy();
        container.remove();
    });

    describe('initialization', () => {
        it('creates overlay element in container', () => {
            overlay = new GameOverlay(container);
            expect(container.querySelector('.game-overlay')).not.toBeNull();
        });

        it('starts hidden', () => {
            overlay = new GameOverlay(container);
            expect(overlay.isVisible()).toBe(false);
        });

        it('has null state initially', () => {
            overlay = new GameOverlay(container);
            expect(overlay.getState()).toBeNull();
        });
    });

    describe('show', () => {
        beforeEach(() => {
            overlay = new GameOverlay(container);
        });

        it('becomes visible when shown', () => {
            overlay.show('victory');
            expect(overlay.isVisible()).toBe(true);
        });

        it('sets state to victory', () => {
            overlay.show('victory');
            expect(overlay.getState()).toBe('victory');
        });

        it('sets state to game_over', () => {
            overlay.show('game_over');
            expect(overlay.getState()).toBe('game_over');
        });

        it('displays VICTORY for victory state', () => {
            overlay.show('victory');
            const title = container.querySelector('.game-overlay-title');
            expect(title?.textContent).toBe('VICTORY');
        });

        it('displays YOU DIED for game_over state', () => {
            overlay.show('game_over');
            const title = container.querySelector('.game-overlay-title');
            expect(title?.textContent).toBe('YOU DIED');
        });

        it('shows floor stat when provided', () => {
            overlay.show('victory', { floor: 5 });
            const stats = container.querySelector('.game-overlay-stats');
            expect(stats?.innerHTML).toContain('Floor Reached: 5');
        });

        it('shows item count when provided', () => {
            overlay.show('victory', { items: ['item1', 'item2', 'item3'] });
            const stats = container.querySelector('.game-overlay-stats');
            expect(stats?.innerHTML).toContain('Items Collected: 3');
        });
    });

    describe('hide', () => {
        beforeEach(() => {
            overlay = new GameOverlay(container);
        });

        it('becomes hidden when hide called', () => {
            overlay.show('victory');
            overlay.hide();
            expect(overlay.isVisible()).toBe(false);
        });

        it('clears state when hidden', () => {
            overlay.show('victory');
            overlay.hide();
            expect(overlay.getState()).toBeNull();
        });
    });

    describe('callbacks', () => {
        it('calls onRestart when restart button clicked', () => {
            const onRestart = vi.fn();
            overlay = new GameOverlay(container, { onRestart });
            overlay.show('game_over');

            const buttons = container.querySelectorAll('button');
            const restartBtn = Array.from(buttons).find(b => b.textContent === 'PLAY AGAIN');
            restartBtn?.click();

            expect(onRestart).toHaveBeenCalled();
        });

        it('calls onMainMenu when menu button clicked', () => {
            const onMainMenu = vi.fn();
            overlay = new GameOverlay(container, { onMainMenu });
            overlay.show('game_over');

            const buttons = container.querySelectorAll('button');
            const menuBtn = Array.from(buttons).find(b => b.textContent === 'MAIN MENU');
            menuBtn?.click();

            expect(onMainMenu).toHaveBeenCalled();
        });
    });

    describe('destroy', () => {
        it('removes overlay from DOM', () => {
            overlay = new GameOverlay(container);
            overlay.destroy();
            expect(container.querySelector('.game-overlay')).toBeNull();
        });
    });
});
