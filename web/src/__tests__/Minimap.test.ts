// web/src/__tests__/Minimap.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { Minimap, MinimapRoom } from '../ui/Minimap';

describe('Minimap', () => {
    let container: HTMLElement;
    let minimap: Minimap;

    beforeEach(() => {
        container = document.createElement('div');
        document.body.appendChild(container);
    });

    afterEach(() => {
        minimap?.destroy();
        container.remove();
    });

    describe('initialization', () => {
        it('creates minimap element in container', () => {
            minimap = new Minimap(container);
            expect(container.querySelector('.minimap')).not.toBeNull();
        });

        it('starts hidden', () => {
            minimap = new Minimap(container);
            expect(minimap.isVisible()).toBe(false);
        });
    });

    describe('show/hide', () => {
        beforeEach(() => {
            minimap = new Minimap(container);
        });

        it('becomes visible when show called', () => {
            minimap.show();
            expect(minimap.isVisible()).toBe(true);
        });

        it('becomes hidden when hide called', () => {
            minimap.show();
            minimap.hide();
            expect(minimap.isVisible()).toBe(false);
        });
    });

    describe('update', () => {
        beforeEach(() => {
            minimap = new Minimap(container);
        });

        it('renders rooms as divs', () => {
            const rooms: MinimapRoom[] = [
                { x: 0, y: 0, type: 'start', cleared: true },
                { x: 1, y: 0, type: 'combat', cleared: false }
            ];
            minimap.update(rooms, [0, 0]);

            const roomEls = container.querySelectorAll('.minimap-room');
            expect(roomEls.length).toBe(2);
        });

        it('handles empty rooms array', () => {
            minimap.update([], null);
            const roomEls = container.querySelectorAll('.minimap-room');
            expect(roomEls.length).toBe(0);
        });


        it('uses correct color for start room', () => {
            const rooms: MinimapRoom[] = [
                { x: 0, y: 0, type: 'start', cleared: true }
            ];
            minimap.update(rooms, null);

            const roomEl = container.querySelector('.minimap-room') as HTMLElement;
            expect(roomEl.style.background).toBe('rgb(0, 255, 0)');
        });

        it('uses correct color for boss room', () => {
            const rooms: MinimapRoom[] = [
                { x: 0, y: 0, type: 'boss', cleared: false }
            ];
            minimap.update(rooms, null);

            const roomEl = container.querySelector('.minimap-room') as HTMLElement;
            expect(roomEl.style.background).toBe('rgb(255, 0, 0)');
        });

        it('uses correct color for treasure room', () => {
            const rooms: MinimapRoom[] = [
                { x: 0, y: 0, type: 'treasure', cleared: false }
            ];
            minimap.update(rooms, null);

            const roomEl = container.querySelector('.minimap-room') as HTMLElement;
            expect(roomEl.style.background).toBe('rgb(255, 204, 0)');
        });

        it('shows cleared combat room as white', () => {
            const rooms: MinimapRoom[] = [
                { x: 0, y: 0, type: 'combat', cleared: true }
            ];
            minimap.update(rooms, null);

            const roomEl = container.querySelector('.minimap-room') as HTMLElement;
            expect(roomEl.style.background).toBe('rgb(255, 255, 255)');
        });

        it('shows uncleared combat room as gray', () => {
            const rooms: MinimapRoom[] = [
                { x: 0, y: 0, type: 'combat', cleared: false }
            ];
            minimap.update(rooms, null);

            const roomEl = container.querySelector('.minimap-room') as HTMLElement;
            expect(roomEl.style.background).toBe('rgb(102, 102, 102)');
        });

        it('positions rooms correctly relative to bounds', () => {
            const rooms: MinimapRoom[] = [
                { x: 5, y: 3, type: 'start', cleared: true },
                { x: 6, y: 3, type: 'combat', cleared: false }
            ];
            minimap.update(rooms, null);

            const roomEls = container.querySelectorAll('.minimap-room');
            const firstRoom = roomEls[0] as HTMLElement;
            const secondRoom = roomEls[1] as HTMLElement;

            // First room should be at left: 0
            expect(firstRoom.style.left).toBe('0px');
            // Second room should be offset by cellSize + gap (12 + 2 = 14)
            expect(secondRoom.style.left).toBe('14px');
        });
    });

    describe('destroy', () => {
        it('removes minimap from DOM', () => {
            minimap = new Minimap(container);
            minimap.destroy();
            expect(container.querySelector('.minimap')).toBeNull();
        });
    });
});
