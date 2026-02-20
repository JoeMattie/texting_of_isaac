// web/src/renderer.ts

import * as PIXI from 'pixi.js';
import { SpriteManager, EntityType } from './sprites';
import { LevelSpriteManager, LevelSpriteKey } from './levelSprites';
import { GameState } from './network';

/**
 * Configurable screen shake presets.
 * Intensity is 0–1; decay is how fast intensity falls off per second.
 */
export const SHAKE_CONFIG = {
    /** Medium shake – used on player taking damage. */
    medium: { intensity: 0.6, duration: 0.3 },
    /** Heavy shake – used on boss hit or major explosion. */
    heavy: { intensity: 1.0, duration: 0.5 },
    /** Light shake – minor impacts. */
    light: { intensity: 0.25, duration: 0.15 },
} as const;

export type ShakePreset = keyof typeof SHAKE_CONFIG;

// ---------------------------------------------------------------------------
// Room layout constants
// ---------------------------------------------------------------------------
const ROOM_COLS = 60;   // matches Config.ROOM_WIDTH
const ROOM_ROWS = 20;   // matches Config.ROOM_HEIGHT

/** Door directions from the server's room.doors array. */
type DoorDir = 'north' | 'south' | 'east' | 'west';

/** Which column/row each door occupies (approximate center of the wall). */
const DOOR_POSITIONS: Record<DoorDir, { col: number; row: number }> = {
    north: { col: ROOM_COLS / 2, row: 0 },
    south: { col: ROOM_COLS / 2, row: ROOM_ROWS - 1 },
    east:  { col: ROOM_COLS - 1, row: ROOM_ROWS / 2 },
    west:  { col: 0,             row: ROOM_ROWS / 2 },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Determine if a cell is a wall border, returning direction or null. */
function wallDir(col: number, row: number): DoorDir | 'corner' | 'wall' | null {
    const top    = row === 0;
    const bottom = row === ROOM_ROWS - 1;
    const left   = col === 0;
    const right  = col === ROOM_COLS - 1;

    if (top    && left)  return 'corner';
    if (top    && right) return 'corner';
    if (bottom && left)  return 'corner';
    if (bottom && right) return 'corner';
    if (top)    return 'north';
    if (bottom) return 'south';
    if (left)   return 'west';
    if (right)  return 'east';
    return null;
}

/** Resolve which wall tile to use for a border cell. */
function wallTileKey(col: number, row: number): LevelSpriteKey {
    const top    = row === 0;
    const bottom = row === ROOM_ROWS - 1;
    const left   = col === 0;
    const right  = col === ROOM_COLS - 1;

    if (top    && left)  return 'wall_corner_tl';
    if (top    && right) return 'wall_corner_tr';
    if (bottom && left)  return 'wall_corner_bl';
    if (bottom && right) return 'wall_corner_br';
    if (top)    return 'wall_top';
    if (bottom) return 'wall_bottom';
    if (left)   return 'wall_left';
    if (right)  return 'wall_right';
    return 'wall_top';
}

/** Pick a floor variant by position (deterministic pseudo-random). */
function floorTileKey(col: number, row: number): LevelSpriteKey {
    const hash = (col * 7 + row * 13) % 32;
    if (hash < 22) return 'floor_plain';
    if (hash < 26) return 'floor_cracked';
    if (hash < 29) return 'floor_mossy';
    if (hash < 31) return 'floor_decorated';
    return 'floor_shadow';
}

/** Return the door key for an open or locked door tile. */
function doorTileKey(dir: DoorDir, locked: boolean): LevelSpriteKey {
    const base = locked ? `door_${dir}_locked` : `door_${dir}_open`;
    return base as LevelSpriteKey;
}

/** Obstacle entity types → level sprite keys. */
const OBSTACLE_KEYS: Partial<Record<string, LevelSpriteKey>> = {
    obstacle:       'obstacle_rock',
    obstacle_rock:  'obstacle_rock',
    barrel:         'obstacle_barrel',
    skull:          'obstacle_skull',
    pillar:         'obstacle_pillar',
};

// ---------------------------------------------------------------------------
// GameRenderer
// ---------------------------------------------------------------------------

export class GameRenderer {
    private app: PIXI.Application;
    private container: PIXI.Container;
    private spriteManager: SpriteManager;
    private levelSprites: LevelSpriteManager;
    private entitySprites: Map<number, PIXI.Sprite> = new Map();
    private tileSize: number = 32;

    /** Background layer drawn once per room change. */
    private bgContainer: PIXI.Container;
    /** Tracks what room state the background was last drawn for. */
    private lastRoomKey: string = '';

    constructor(
        app: PIXI.Application,
        spriteManager: SpriteManager,
        levelSprites: LevelSpriteManager,
        container?: PIXI.Container,
    ) {
        this.app = app;
        this.container = container ?? app.stage;
        this.spriteManager = spriteManager;
        this.levelSprites = levelSprites;

        // Background sits behind entities
        this.bgContainer = new PIXI.Container();
        this.container.addChildAt(this.bgContainer, 0);
    }

    render(gameState: GameState): void {
        if (!this.spriteManager.isLoaded()) {
            console.warn('Sprites not loaded yet');
            return;
        }

        // Rebuild background only when room changes
        if (this.levelSprites.isLoaded()) {
            this._renderBackground(gameState);
        }

        // Track which entities are still alive
        const activeEntityIds = new Set<number>();

        // Update or create sprites for each entity
        for (const entity of gameState.entities) {
            activeEntityIds.add(entity.id);

            // Use level sprite for obstacle-type entities
            const isObstacle = OBSTACLE_KEYS[entity.type] !== undefined;
            const sprite = isObstacle
                ? this._getOrCreateLevelSprite(entity.id, OBSTACLE_KEYS[entity.type]!)
                : this._getOrCreateEntitySprite(entity.id, entity.type as EntityType);

            if (sprite && entity.components.position) {
                const x = entity.components.position.x;
                const y = entity.components.position.y;

                if (isFinite(x) && isFinite(y)) {
                    sprite.x = x * this.tileSize;
                    sprite.y = y * this.tileSize;
                } else {
                    console.warn(`Invalid position for entity ${entity.id}: (${x}, ${y})`);
                }
            }
        }

        // Remove sprites for dead entities
        for (const [entityId, sprite] of this.entitySprites) {
            if (!activeEntityIds.has(entityId)) {
                this.container.removeChild(sprite);
                sprite.destroy();
                this.entitySprites.delete(entityId);
            }
        }
    }

    // -------------------------------------------------------------------------
    // Background rendering
    // -------------------------------------------------------------------------

    private _renderBackground(gameState: GameState): void {
        // Build a cache key that covers room position + door states
        const doors = gameState.room?.doors ?? [];
        const doorSig = doors
            .map(d => `${d.type}:${d.components?.locked ? '1' : '0'}`)
            .sort()
            .join(',');
        const roomPos = gameState.room?.position ?? [0, 0];
        const key = `${roomPos[0]},${roomPos[1]}|${doorSig}`;

        if (key === this.lastRoomKey) return;
        this.lastRoomKey = key;

        // Clear previous background
        this.bgContainer.removeChildren().forEach(c => (c as PIXI.Sprite).destroy());

        // Build a set of door cells: map from "col,row" → door direction + locked state
        const doorCells = new Map<string, { dir: DoorDir; locked: boolean }>();
        for (const door of doors) {
            const type  = door.type as string;
            const locked = !!door.components?.locked;

            // Type is "door_north", "door_south", etc.
            const dirMatch = type.match(/door_(north|south|east|west)/);
            if (!dirMatch) continue;
            const dir = dirMatch[1] as DoorDir;
            const { col, row } = DOOR_POSITIONS[dir];

            // Mark ~4 cells around the door position as door cells
            for (let dc = -2; dc <= 2; dc++) {
                for (let dr = -2; dr <= 2; dr++) {
                    const c = Math.max(0, Math.min(ROOM_COLS - 1, col + dc));
                    const r = Math.max(0, Math.min(ROOM_ROWS - 1, row + dr));
                    doorCells.set(`${c},${r}`, { dir, locked });
                }
            }
        }

        // Render floor + walls
        for (let row = 0; row < ROOM_ROWS; row++) {
            for (let col = 0; col < ROOM_COLS; col++) {
                const cellKey = `${col},${row}`;
                const wDir = wallDir(col, row);
                let tileKey: LevelSpriteKey;

                if (wDir !== null) {
                    // Check if this wall cell is a door
                    const door = doorCells.get(cellKey);
                    if (door) {
                        tileKey = doorTileKey(door.dir, door.locked);
                    } else {
                        tileKey = wallTileKey(col, row);
                    }
                } else {
                    // Interior floor
                    tileKey = floorTileKey(col, row);
                }

                const tex = this.levelSprites.getTexture(tileKey);
                if (!tex) continue;

                const sprite = new PIXI.Sprite(tex);
                sprite.anchor.set(0);
                sprite.x = col * this.tileSize;
                sprite.y = row * this.tileSize;
                this.bgContainer.addChild(sprite);
            }
        }
    }

    // -------------------------------------------------------------------------
    // Entity sprite helpers
    // -------------------------------------------------------------------------

    private _getOrCreateEntitySprite(entityId: number, entityType: EntityType): PIXI.Sprite | null {
        if (this.entitySprites.has(entityId)) {
            return this.entitySprites.get(entityId)!;
        }
        const texture = this.spriteManager.getTexture(entityType);
        if (!texture) {
            console.warn(`No texture for entity type: ${entityType}`);
            return null;
        }
        const sprite = new PIXI.Sprite(texture);
        sprite.anchor.set(0.5);
        this.container.addChild(sprite);
        this.entitySprites.set(entityId, sprite);
        return sprite;
    }

    private _getOrCreateLevelSprite(entityId: number, key: LevelSpriteKey): PIXI.Sprite | null {
        if (this.entitySprites.has(entityId)) {
            return this.entitySprites.get(entityId)!;
        }
        const texture = this.levelSprites.getTexture(key);
        if (!texture) {
            console.warn(`No level texture for key: ${key}`);
            return null;
        }
        const sprite = new PIXI.Sprite(texture);
        sprite.anchor.set(0.5);
        this.container.addChild(sprite);
        this.entitySprites.set(entityId, sprite);
        return sprite;
    }

    // -------------------------------------------------------------------------
    // Public API (unchanged from original)
    // -------------------------------------------------------------------------

    clear(): void {
        for (const [, sprite] of this.entitySprites) {
            this.container.removeChild(sprite);
            sprite.destroy();
        }
        this.entitySprites.clear();
        this.bgContainer.removeChildren().forEach(c => (c as PIXI.Sprite).destroy());
        this.lastRoomKey = '';
    }

    getEntitySprites(): Map<number, PIXI.Sprite> {
        return this.entitySprites;
    }

    getEntityType(entityId: number, gameState: GameState): string {
        const entity = gameState.entities.find(e => e.id === entityId);
        return entity?.type || 'unknown';
    }
}
