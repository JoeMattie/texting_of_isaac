// web/src/sprites.ts

import * as PIXI from 'pixi.js';

export type EntityType =
    | 'player'
    | 'enemy_chaser'
    | 'enemy_shooter'
    | 'enemy_orbiter'
    | 'enemy_turret'
    | 'enemy_tank'
    | 'boss_A'
    | 'boss_B'
    | 'boss_C'
    | 'projectile'
    | 'projectile_player'
    | 'projectile_enemy'
    | 'door'
    | 'door_open'
    | 'door_locked'
    | 'trapdoor'
    | 'heart'
    | 'heart_half'
    | 'coin'
    | 'bomb'
    | 'item'
    | 'powerup'
    | 'obstacle'
    | 'wall'
    | 'floor'
    | 'unknown';

export interface SpriteAtlas {
    textures: Partial<Record<EntityType, PIXI.Texture>>;
    loaded: boolean;
}

// Fallback colors used when the atlas fails to load
const FALLBACK_COLORS: Record<EntityType, string> = {
    player:           '#00ff00',
    enemy_chaser:     '#ff0000',
    enemy_shooter:    '#ff4444',
    enemy_orbiter:    '#ff8800',
    enemy_turret:     '#880000',
    enemy_tank:       '#440000',
    boss_A:           '#cc00cc',
    boss_B:           '#aa00aa',
    boss_C:           '#880088',
    projectile:       '#00ffff',
    projectile_player:'#00ffff',
    projectile_enemy: '#ff00aa',
    door:             '#8b4513',
    door_open:        '#8b4513',
    door_locked:      '#5c2e00',
    trapdoor:         '#4a3000',
    heart:            '#ff0088',
    heart_half:       '#ff6688',
    coin:             '#ffff00',
    bomb:             '#888888',
    item:             '#9370db',
    powerup:          '#44ff88',
    obstacle:         '#666666',
    wall:             '#333333',
    floor:            '#aaaaaa',
    unknown:          '#ff00ff',
};

// Atlas frame names from sprites.json (full set available in the sheet)
const ATLAS_SPRITE_NAMES: EntityType[] = [
    'player', 'enemy_chaser', 'enemy_shooter', 'enemy_orbiter', 'enemy_turret', 'enemy_tank',
    'boss_A', 'boss_B', 'boss_C', 'projectile_player', 'projectile_enemy', 'trapdoor',
    'door_open', 'door_locked', 'wall', 'obstacle', 'floor', 'unknown',
    'heart', 'heart_half', 'coin', 'bomb', 'item', 'powerup',
];

export class SpriteManager {
    private atlas: SpriteAtlas;
    private loadingPromise: Promise<void> | null = null;

    constructor() {
        this.atlas = {
            textures: {},
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
        try {
            await this.loadAtlas();
        } catch (err) {
            console.warn('SpriteManager: atlas load failed, using fallback colors.', err);
            this.loadFallback();
        }
    }

    /** Load pixel-art sprite atlas from /assets/sprites.json */
    private async loadAtlas(): Promise<void> {
        const atlasData = await PIXI.Assets.load('/assets/sprites.json') as PIXI.Spritesheet;

        // Apply nearest-neighbour scaling on every base texture so 32-px art stays crisp
        for (const name of ATLAS_SPRITE_NAMES) {
            const tex = atlasData.textures?.[name];
            if (tex) {
                tex.baseTexture.scaleMode = PIXI.SCALE_MODES.NEAREST;
                this.atlas.textures[name] = tex;
            }
        }

        // Aliases: 'projectile' → 'projectile_player', 'door' → 'door_open'
        if (this.atlas.textures['projectile_player']) {
            this.atlas.textures['projectile'] = this.atlas.textures['projectile_player'];
        }
        if (this.atlas.textures['door_open']) {
            this.atlas.textures['door'] = this.atlas.textures['door_open'];
        }

        this.atlas.loaded = true;
        console.info(`SpriteManager: atlas loaded (${Object.keys(this.atlas.textures).length} textures)`);
    }

    /** Create simple 32×32 colored rectangles as placeholders */
    private loadFallback(): void {
        const createTexture = (color: string): PIXI.Texture => {
            const canvas = document.createElement('canvas');
            canvas.width = 32;
            canvas.height = 32;
            const ctx = canvas.getContext('2d')!;
            ctx.fillStyle = color;
            ctx.fillRect(0, 0, 32, 32);
            return PIXI.Texture.from(canvas);
        };

        for (const [name, color] of Object.entries(FALLBACK_COLORS) as [EntityType, string][]) {
            this.atlas.textures[name] = createTexture(color);
        }

        this.atlas.loaded = true;
    }

    getTexture(entityType: EntityType): PIXI.Texture | null {
        if (!this.atlas.loaded) {
            return null;
        }
        return this.atlas.textures[entityType] ?? null;
    }

    isLoaded(): boolean {
        return this.atlas.loaded;
    }
}
