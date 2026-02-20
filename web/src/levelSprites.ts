// web/src/levelSprites.ts
// Level/environment sprite manager — loads level-sprites.json atlas.

import * as PIXI from 'pixi.js';

// ---------------------------------------------------------------------------
// All sprite key names from the level-sprites atlas
// ---------------------------------------------------------------------------
export type LevelSpriteKey =
    // Floor variants
    | 'floor_plain'
    | 'floor_cracked'
    | 'floor_bloodstain'
    | 'floor_grate'
    | 'floor_dirt'
    | 'floor_mossy'
    | 'floor_decorated'
    | 'floor_shadow'
    // Directional walls
    | 'wall_top'
    | 'wall_bottom'
    | 'wall_left'
    | 'wall_right'
    | 'wall_corner_tl'
    | 'wall_corner_tr'
    | 'wall_corner_bl'
    | 'wall_corner_br'
    // Inner corners
    | 'wall_inner_tl'
    | 'wall_inner_tr'
    | 'wall_inner_bl'
    | 'wall_inner_br'
    // Open doors
    | 'door_north_open'
    | 'door_south_open'
    | 'door_east_open'
    | 'door_west_open'
    // Locked doors
    | 'door_north_locked'
    | 'door_south_locked'
    | 'door_east_locked'
    | 'door_west_locked'
    // Obstacles
    | 'obstacle_rock'
    | 'obstacle_barrel'
    | 'obstacle_skull'
    | 'obstacle_pillar'
    // Decorations
    | 'deco_torch'
    | 'deco_cobweb_corner'
    | 'deco_bones'
    | 'deco_pot'
    | 'deco_chain'
    | 'deco_altar'
    | 'deco_pentagram'
    | 'deco_shopkeeper'
    // Special tiles
    | 'room_boss_marker'
    | 'room_treasure_marker'
    | 'room_shop_marker'
    | 'room_secret_marker'
    | 'pit'
    | 'pit_edge_top'
    | 'pit_edge_side'
    | 'trapdoor_open'
    // Background fills + minimap
    | 'bg_room_fill'
    | 'bg_void'
    | 'bg_wall_fill'
    | 'shadow_east'
    | 'shadow_south'
    | 'shadow_corner'
    | 'minimap_room'
    | 'minimap_current';

// ---------------------------------------------------------------------------
// Fallback colors when the atlas fails to load
// ---------------------------------------------------------------------------
const FALLBACK_COLORS: Record<LevelSpriteKey, string> = {
    floor_plain:          '#2a2830',
    floor_cracked:        '#282630',
    floor_bloodstain:     '#3a1020',
    floor_grate:          '#3a3850',
    floor_dirt:           '#3c2e20',
    floor_mossy:          '#1e3420',
    floor_decorated:      '#2c2a38',
    floor_shadow:         '#181620',
    wall_top:             '#484560',
    wall_bottom:          '#404060',
    wall_left:            '#424060',
    wall_right:           '#424060',
    wall_corner_tl:       '#3e3c58',
    wall_corner_tr:       '#3e3c58',
    wall_corner_bl:       '#3e3c58',
    wall_corner_br:       '#3e3c58',
    wall_inner_tl:        '#404060',
    wall_inner_tr:        '#404060',
    wall_inner_bl:        '#404060',
    wall_inner_br:        '#404060',
    door_north_open:      '#1a181e',
    door_south_open:      '#1a181e',
    door_east_open:       '#1a181e',
    door_west_open:       '#1a181e',
    door_north_locked:    '#601212',
    door_south_locked:    '#601212',
    door_east_locked:     '#601212',
    door_west_locked:     '#601212',
    obstacle_rock:        '#505060',
    obstacle_barrel:      '#6a3c18',
    obstacle_skull:       '#b8b0a0',
    obstacle_pillar:      '#5a5870',
    deco_torch:           '#ff8c00',
    deco_cobweb_corner:   '#9090a0',
    deco_bones:           '#c0b8a8',
    deco_pot:             '#904838',
    deco_chain:           '#585868',
    deco_altar:           '#c0b8a8',
    deco_pentagram:       '#8c0080',
    deco_shopkeeper:      '#009090',
    room_boss_marker:     '#8c0000',
    room_treasure_marker: '#c0a000',
    room_shop_marker:     '#008888',
    room_secret_marker:   '#303040',
    pit:                  '#080408',
    pit_edge_top:         '#181418',
    pit_edge_side:        '#181418',
    trapdoor_open:        '#4a3010',
    bg_room_fill:         '#302e38',
    bg_void:              '#100e14',
    bg_wall_fill:         '#484568',
    shadow_east:          '#1e1c28',
    shadow_south:         '#1e1c28',
    shadow_corner:        '#181620',
    minimap_room:         '#483c54',
    minimap_current:      '#8ac3fc',
};

// ---------------------------------------------------------------------------
// LevelSpriteManager
// ---------------------------------------------------------------------------
export class LevelSpriteManager {
    private textures: Partial<Record<LevelSpriteKey, PIXI.Texture>> = {};
    private loaded = false;
    private loadingPromise: Promise<void> | null = null;

    async load(): Promise<void> {
        if (this.loadingPromise) return this.loadingPromise;
        this.loadingPromise = this._load();
        return this.loadingPromise;
    }

    private async _load(): Promise<void> {
        try {
            await this._loadAtlas();
        } catch (err) {
            console.warn('LevelSpriteManager: atlas load failed, using fallback colors.', err);
            this._loadFallback();
        }
    }

    private async _loadAtlas(): Promise<void> {
        const atlas = await PIXI.Assets.load('/assets/level-sprites.json') as PIXI.Spritesheet;

        for (const key of Object.keys(FALLBACK_COLORS) as LevelSpriteKey[]) {
            const tex = atlas.textures?.[key];
            if (tex) {
                tex.baseTexture.scaleMode = PIXI.SCALE_MODES.NEAREST;
                this.textures[key] = tex;
            }
        }

        this.loaded = true;
        console.info(`LevelSpriteManager: atlas loaded (${Object.keys(this.textures).length} textures)`);
    }

    private _loadFallback(): void {
        const make = (color: string): PIXI.Texture => {
            const canvas = document.createElement('canvas');
            canvas.width = 32;
            canvas.height = 32;
            const ctx = canvas.getContext('2d')!;
            ctx.fillStyle = color;
            ctx.fillRect(0, 0, 32, 32);
            return PIXI.Texture.from(canvas);
        };

        for (const [key, color] of Object.entries(FALLBACK_COLORS) as [LevelSpriteKey, string][]) {
            this.textures[key] = make(color);
        }

        this.loaded = true;
    }

    getTexture(key: LevelSpriteKey): PIXI.Texture | null {
        if (!this.loaded) return null;
        return this.textures[key] ?? null;
    }

    isLoaded(): boolean {
        return this.loaded;
    }
}
