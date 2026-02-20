import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { HUD } from '../ui/HUD';

describe('HUD', () => {
    let container: HTMLElement;

    beforeEach(() => {
        container = document.createElement('div');
        document.body.appendChild(container);
    });

    afterEach(() => {
        container.remove();
    });

    it('creates HUD element', () => {
        const hud = new HUD(container);
        expect(container.querySelector('.hud')).not.toBeNull();
    });

    it('renders health hearts', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 3, max: 5 }, coins: 0, bombs: 0, items: [], floor: 1 });
        const healthEl = container.querySelector('.hud-health');
        expect(healthEl?.textContent).toContain('♥♥♥');
    });

    it('renders empty hearts for missing health', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 2, max: 4 }, coins: 0, bombs: 0, items: [], floor: 1 });
        const healthEl = container.querySelector('.hud-health');
        // Check that we have 2 full hearts and 2 empty hearts
        const fullHearts = (healthEl?.innerHTML.match(/♥/g) || []).length;
        const emptyHearts = (healthEl?.innerHTML.match(/♡/g) || []).length;
        expect(fullHearts).toBe(2);
        expect(emptyHearts).toBe(2);
    });

    it('renders coins', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 3, max: 3 }, coins: 15, bombs: 0, items: [], floor: 1 });
        const coinsEl = container.querySelector('.hud-coins');
        expect(coinsEl?.textContent).toContain('15');
    });

    it('renders bombs', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 3, max: 3 }, coins: 0, bombs: 5, items: [], floor: 1 });
        const bombsEl = container.querySelector('.hud-bombs');
        expect(bombsEl?.textContent).toContain('5');
    });

    it('renders floor number', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 3, max: 3 }, coins: 0, bombs: 0, items: [], floor: 2 });
        const floorEl = container.querySelector('.hud-floor');
        expect(floorEl?.textContent).toContain('F2');
    });

    it('destroy removes HUD', () => {
        const hud = new HUD(container);
        hud.destroy();
        expect(container.querySelector('.hud')).toBeNull();
    });

    it('animateDamage adds hud-shake class to health element', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 3, max: 3 }, coins: 0, bombs: 0, items: [], floor: 1 });
        hud.animateDamage();
        const healthEl = container.querySelector('.hud-health') as HTMLElement;
        expect(healthEl?.classList.contains('hud-shake')).toBe(true);
    });

    it('animateCoinPickup adds hud-bounce class to coin element', () => {
        const hud = new HUD(container);
        hud.animateCoinPickup();
        const coinsEl = container.querySelector('.hud-coins') as HTMLElement;
        expect(coinsEl?.classList.contains('hud-bounce')).toBe(true);
    });

    it('animateBombPickup adds hud-bounce class to bomb element', () => {
        const hud = new HUD(container);
        hud.animateBombPickup();
        const bombsEl = container.querySelector('.hud-bombs') as HTMLElement;
        expect(bombsEl?.classList.contains('hud-bounce')).toBe(true);
    });

    it('automatically triggers animateDamage when health decreases', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 3, max: 3 }, coins: 0, bombs: 0, items: [], floor: 1 });
        // Take damage
        hud.update({ health: { current: 2, max: 3 }, coins: 0, bombs: 0, items: [], floor: 1 });
        const healthEl = container.querySelector('.hud-health') as HTMLElement;
        expect(healthEl?.classList.contains('hud-shake')).toBe(true);
    });

    it('automatically triggers animateCoinPickup when coins increase', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 3, max: 3 }, coins: 5, bombs: 0, items: [], floor: 1 });
        hud.update({ health: { current: 3, max: 3 }, coins: 6, bombs: 0, items: [], floor: 1 });
        const coinsEl = container.querySelector('.hud-coins') as HTMLElement;
        expect(coinsEl?.classList.contains('hud-bounce')).toBe(true);
    });

    it('automatically triggers animateBombPickup when bombs increase', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 3, max: 3 }, coins: 0, bombs: 1, items: [], floor: 1 });
        hud.update({ health: { current: 3, max: 3 }, coins: 0, bombs: 2, items: [], floor: 1 });
        const bombsEl = container.querySelector('.hud-bombs') as HTMLElement;
        expect(bombsEl?.classList.contains('hud-bounce')).toBe(true);
    });
});
