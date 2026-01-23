// web/src/ui/Minimap.ts
/**
 * Minimap component showing explored dungeon rooms.
 */

export interface MinimapRoom {
    x: number;
    y: number;
    type: string;
    cleared: boolean;
}

export class Minimap {
    private container: HTMLElement;
    private element: HTMLElement;
    private roomsContainer: HTMLElement;
    private readonly cellSize = 12;
    private readonly gap = 2;

    // Color scheme by room type
    private readonly colors: Record<string, string> = {
        start: '#00ff00',
        combat: '#666666',
        combat_cleared: '#ffffff',
        boss: '#ff0000',
        treasure: '#ffcc00',
        shop: '#0088ff',
        secret: '#aa00ff',
        miniboss: '#ff6600'
    };

    constructor(container: HTMLElement) {
        this.container = container;

        this.element = document.createElement('div');
        this.element.className = 'minimap';
        this.element.style.cssText = `
            position: fixed;
            top: 16px;
            right: 16px;
            background: rgba(0, 0, 0, 0.7);
            padding: 8px;
            z-index: 100;
            display: none;
        `;

        this.roomsContainer = document.createElement('div');
        this.roomsContainer.style.cssText = `
            position: relative;
        `;
        this.element.appendChild(this.roomsContainer);

        this.container.appendChild(this.element);
    }

    /**
     * Update minimap with current room data.
     */
    update(rooms: MinimapRoom[], currentPosition: [number, number] | null): void {
        if (rooms.length === 0) {
            this.roomsContainer.innerHTML = '';
            return;
        }

        // Calculate bounding box
        let minX = Infinity, maxX = -Infinity;
        let minY = Infinity, maxY = -Infinity;
        for (const room of rooms) {
            minX = Math.min(minX, room.x);
            maxX = Math.max(maxX, room.x);
            minY = Math.min(minY, room.y);
            maxY = Math.max(maxY, room.y);
        }

        // Calculate container size
        const width = (maxX - minX + 1) * (this.cellSize + this.gap) - this.gap;
        const height = (maxY - minY + 1) * (this.cellSize + this.gap) - this.gap;
        this.roomsContainer.style.width = `${width}px`;
        this.roomsContainer.style.height = `${height}px`;

        // Clear and rebuild rooms
        this.roomsContainer.innerHTML = '';

        for (const room of rooms) {
            const roomEl = document.createElement('div');
            roomEl.className = 'minimap-room';

            // Calculate position relative to bounds
            const left = (room.x - minX) * (this.cellSize + this.gap);
            const top = (room.y - minY) * (this.cellSize + this.gap);

            // Get color based on type and cleared status
            let color = this.colors[room.type] || '#666666';
            if (room.type === 'combat' && room.cleared) {
                color = this.colors.combat_cleared;
            }

            // Check if current room
            const isCurrent = currentPosition &&
                room.x === currentPosition[0] &&
                room.y === currentPosition[1];

            roomEl.style.cssText = `
                position: absolute;
                left: ${left}px;
                top: ${top}px;
                width: ${this.cellSize}px;
                height: ${this.cellSize}px;
                background: ${color};
                ${isCurrent ? 'border: 2px solid #ffffff; box-sizing: border-box;' : ''}
            `;

            this.roomsContainer.appendChild(roomEl);
        }
    }

    /**
     * Show the minimap.
     */
    show(): void {
        this.element.style.display = 'block';
    }

    /**
     * Hide the minimap.
     */
    hide(): void {
        this.element.style.display = 'none';
    }

    /**
     * Check if minimap is visible.
     */
    isVisible(): boolean {
        return this.element.style.display === 'block';
    }

    /**
     * Clean up the minimap element.
     */
    destroy(): void {
        this.element.remove();
    }
}
