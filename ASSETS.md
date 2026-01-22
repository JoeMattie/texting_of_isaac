# Asset Pipeline Documentation

## Overview

The Texting of Isaac web frontend uses sprite sheets for rendering game entities. Currently using placeholder colored rectangles; this doc explains how to integrate real pixel art sprites.

## Asset Requirements

### Sprite Specifications

- **Format**: PNG with transparency
- **Size**: 32x32 pixels per sprite (tile size)
- **Color depth**: 32-bit RGBA
- **Style**: Pixel art (low-res aesthetic matching terminal game)

### Required Sprites

1. **Player** - idle, walk (4 directions), shoot (4 directions)
2. **Enemies** (5 types):
   - Chaser - red enemy that pursues player
   - Shooter - stationary enemy that fires projectiles
   - Orbiter - enemy that circles around player
   - Turret - fixed position shooter
   - Tank - slow but high HP enemy
3. **Projectiles**:
   - Player projectile (small cyan bullet)
   - Enemy projectile (small magenta bullet)
4. **Environment**:
   - Door (4 orientations: top, bottom, left, right)
   - Wall tiles
   - Obstacle rocks/barriers
5. **Collectibles**:
   - Heart (health pickup)
   - Coin (currency)
   - Bomb (consumable item)
   - Items (various power-ups with unique sprites)

### Animation Frames

For animated sprites (optional for Phase 6):
- **Player walk**: 4 frames per direction
- **Enemy movement**: 2-4 frames
- **Projectile impact**: 3-4 frames
- Frame rate: 8-12 FPS (slower than game rate for pixelated look)

## Sprite Sheet Creation

### Recommended Tools

1. **Aseprite** (https://www.aseprite.org/)
   - Industry standard for pixel art
   - Built-in sprite sheet export
   - Animation timeline
   - $20 or compile from source (free)

2. **Piskel** (https://www.piskelapp.com/)
   - Free web-based tool
   - Simple interface
   - Export sprite sheets

3. **GraphicsGale** (https://graphicsgale.com/us/)
   - Free for non-commercial use
   - Good for frame-by-frame animation

### Sprite Sheet Layout

Create a single PNG file (`sprites.png`) with all sprites arranged in a grid:

```
[player] [enemy1] [enemy2] [enemy3] [enemy4] [enemy5]
[proj1]  [proj2]  [door1]  [door2]  [door3]  [door4]
[wall]   [obst]   [heart]  [coin]   [bomb]   [item1]
[item2]  [item3]  [item4]  [item5]  [...]    [unknown]
```

Dimensions: 384x128 pixels (12 columns x 4 rows of 32x32 sprites)

### Sprite Sheet Manifest (JSON)

Create `sprites.json` with sprite positions:

```json
{
  "frames": {
    "player": { "x": 0, "y": 0, "w": 32, "h": 32 },
    "enemy_chaser": { "x": 32, "y": 0, "w": 32, "h": 32 },
    "enemy_shooter": { "x": 64, "y": 0, "w": 32, "h": 32 },
    "enemy_orbiter": { "x": 96, "y": 0, "w": 32, "h": 32 },
    "enemy_turret": { "x": 128, "y": 0, "w": 32, "h": 32 },
    "enemy_tank": { "x": 160, "y": 0, "w": 32, "h": 32 },
    "projectile": { "x": 0, "y": 32, "w": 32, "h": 32 },
    "door": { "x": 64, "y": 32, "w": 32, "h": 32 },
    "wall": { "x": 0, "y": 64, "w": 32, "h": 32 },
    "obstacle": { "x": 32, "y": 64, "w": 32, "h": 32 },
    "heart": { "x": 64, "y": 64, "w": 32, "h": 32 },
    "coin": { "x": 96, "y": 64, "w": 32, "h": 32 },
    "bomb": { "x": 128, "y": 64, "w": 32, "h": 32 },
    "item": { "x": 160, "y": 64, "w": 32, "h": 32 },
    "unknown": { "x": 160, "y": 96, "w": 32, "h": 32 }
  },
  "meta": {
    "image": "sprites.png",
    "size": { "w": 384, "h": 128 },
    "scale": "1"
  }
}
```

## Integration Steps

### 1. Place Assets in Project

```bash
web/public/assets/
  ├── sprites.png
  └── sprites.json
```

### 2. Update SpriteManager (web/src/sprites.ts)

Replace the placeholder texture creation with actual sprite atlas loading:

```typescript
private async loadSprites(): Promise<void> {
    // Load sprite atlas
    const atlas = await PIXI.Assets.load('/assets/sprites.json');

    // Map entity types to textures from atlas
    this.atlas.textures = {
        player: atlas.textures['player'],
        enemy_chaser: atlas.textures['enemy_chaser'],
        enemy_shooter: atlas.textures['enemy_shooter'],
        // ... map all entity types
    };

    this.atlas.loaded = true;
}
```

### 3. Test

```bash
cd web
npm run dev
```

Open browser and verify sprites appear instead of colored rectangles.

## Asset Optimization

### PNG Optimization

Use `pngquant` to reduce file size:

```bash
# Install pngquant
brew install pngquant  # macOS
apt-get install pngquant  # Linux

# Optimize sprites
pngquant --quality=65-80 --ext .png --force web/public/assets/sprites.png
```

### Production Considerations

- Keep sprite sheet < 1 MB for fast loading
- Use PNG-8 (256 colors) if possible, fallback to PNG-24 for gradients
- Consider WebP format for modern browsers (Vite handles this automatically)
- Enable Vite's asset optimization in production build

## Commissioning Artists

When hiring pixel artists:

**Style Guide**:
- 32x32 pixels per sprite
- Low-res pixel art aesthetic
- Limited color palette (16-32 colors)
- Inspired by The Binding of Isaac / Enter the Gungeon

**Deliverables**:
- Single PNG sprite sheet with all assets
- JSON manifest with sprite positions
- Layered source files (Aseprite .ase or Photoshop .psd)

**License**: Ensure artists grant commercial use rights

## Troubleshooting

### Sprites don't load

- Check browser console for 404 errors
- Verify `sprites.png` and `sprites.json` are in `web/public/assets/`
- Check JSON manifest paths match actual sprite positions

### Sprites look blurry

- Ensure Pixi.js texture settings use nearest-neighbor scaling:
  ```typescript
  texture.baseTexture.scaleMode = PIXI.SCALE_MODES.NEAREST;
  ```

### File size too large

- Run pngquant optimization
- Reduce color palette in sprite editor
- Consider splitting into multiple smaller sprite sheets

## Next Steps

Phase 6 implementation:
1. Commission or create sprite assets
2. Update `SpriteManager.loadSprites()` to use atlas
3. Add animation support with `PIXI.AnimatedSprite`
4. Test all entity types render correctly
5. Optimize and deploy
