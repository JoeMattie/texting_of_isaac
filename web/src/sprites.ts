// web/src/sprites.ts

import * as PIXI from 'pixi.js';

export type EntityType =
    | 'player'
    | 'enemy_chaser'
    | 'enemy_shooter'
    | 'enemy_orbiter'
    | 'enemy_turret'
    | 'enemy_tank'
    | 'projectile_player'
    | 'projectile_enemy'
    | 'door'
    | 'heart'
    | 'coin'
    | 'bomb'
    | 'obstacle'
    | 'wall';

export interface SpriteAtlas {
    textures: Record<EntityType, PIXI.Texture>;
    loaded: boolean;
}

export class SpriteManager {
    private atlas: SpriteAtlas;
    private loadingPromise: Promise<void> | null = null;

    constructor() {
        this.atlas = {
            textures: {} as Record<EntityType, PIXI.Texture>,
            loaded: false
        };
    }

    async load(): Promise<void> {
        if (this.loadingPromise) {
            return this.loadingPromise;
        }

        this.loadingPromise = this.loadSprites();
        return this.loadingPromise;
    }

    private async loadSprites(): Promise<void> {
        // For now, create placeholder colored rectangles
        // Later: replace with actual sprite atlas loading

        const canvas = document.createElement('canvas');
        canvas.width = 32;
        canvas.height = 32;
        const ctx = canvas.getContext('2d')!;

        const createTexture = (color: string): PIXI.Texture => {
            ctx.fillStyle = color;
            ctx.fillRect(0, 0, 32, 32);
            return PIXI.Texture.from(canvas);
        };

        this.atlas.textures = {
            player: createTexture('#00ff00'),
            enemy_chaser: createTexture('#ff0000'),
            enemy_shooter: createTexture('#ff4444'),
            enemy_orbiter: createTexture('#ff8800'),
            enemy_turret: createTexture('#880000'),
            enemy_tank: createTexture('#440000'),
            projectile_player: createTexture('#00ffff'),
            projectile_enemy: createTexture('#ff00ff'),
            door: createTexture('#00ffff'),
            heart: createTexture('#ff0088'),
            coin: createTexture('#ffff00'),
            bomb: createTexture('#888888'),
            obstacle: createTexture('#666666'),
            wall: createTexture('#333333')
        };

        this.atlas.loaded = true;
    }

    getTexture(entityType: EntityType): PIXI.Texture | null {
        if (!this.atlas.loaded) {
            return null;
        }
        return this.atlas.textures[entityType] || null;
    }

    isLoaded(): boolean {
        return this.atlas.loaded;
    }
}
