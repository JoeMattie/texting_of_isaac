// web/src/renderer.ts

import * as PIXI from 'pixi.js';
import { SpriteManager, EntityType } from './sprites';
import { GameState } from './network';

export class GameRenderer {
    private app: PIXI.Application;
    private container: PIXI.Container;
    private spriteManager: SpriteManager;
    private entitySprites: Map<number, PIXI.Sprite> = new Map();
    private tileSize: number = 32;

    constructor(app: PIXI.Application, spriteManager: SpriteManager, container?: PIXI.Container) {
        this.app = app;
        this.container = container ?? app.stage;
        this.spriteManager = spriteManager;
    }

    render(gameState: GameState): void {
        if (!this.spriteManager.isLoaded()) {
            console.warn('Sprites not loaded yet');
            return;
        }

        // Track which entities are still alive
        const activeEntityIds = new Set<number>();

        // Update or create sprites for each entity
        for (const entity of gameState.entities) {
            activeEntityIds.add(entity.id);

            const sprite = this.getOrCreateSprite(entity.id, entity.type as EntityType);
            if (sprite && entity.components.position) {
                const x = entity.components.position.x;
                const y = entity.components.position.y;

                // Validate position values to prevent rendering issues
                if (isFinite(x) && isFinite(y)) {
                    // Convert grid position to pixel position
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

    private getOrCreateSprite(entityId: number, entityType: EntityType): PIXI.Sprite | null {
        // Return existing sprite if it exists
        if (this.entitySprites.has(entityId)) {
            return this.entitySprites.get(entityId)!;
        }

        // Create new sprite
        const texture = this.spriteManager.getTexture(entityType);
        if (!texture) {
            console.warn(`No texture for entity type: ${entityType}`);
            return null;
        }

        const sprite = new PIXI.Sprite(texture);
        sprite.anchor.set(0.5); // Center the sprite on its position
        this.container.addChild(sprite);
        this.entitySprites.set(entityId, sprite);
        return sprite;
    }

    clear(): void {
        // Remove all entity sprites
        for (const [entityId, sprite] of this.entitySprites) {
            this.container.removeChild(sprite);
            sprite.destroy();
        }
        this.entitySprites.clear();
    }

    /**
     * Get all entity sprites for animation.
     * @returns Map of entity ID to sprite
     */
    getEntitySprites(): Map<number, PIXI.Sprite> {
        return this.entitySprites;
    }

    /**
     * Get entity type for a given entity ID.
     * @param entityId - Entity ID
     * @param gameState - Current game state
     * @returns Entity type or 'unknown'
     */
    getEntityType(entityId: number, gameState: GameState): string {
        const entity = gameState.entities.find(e => e.id === entityId);
        return entity?.type || 'unknown';
    }
}
