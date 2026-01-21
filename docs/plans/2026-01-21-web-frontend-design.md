# Web Frontend Design

**Date**: 2026-01-21
**Type**: Production-ready player experience with spectator mode
**Rendering**: Pixi.js (WebGL)
**Assets**: Custom sprite graphics and audio

## Overview

Build a production-ready web version of Texting of Isaac with:
- Full playable experience in the browser
- Real sprite graphics (custom pixel art, replacing ASCII)
- Spectator mode allowing viewers to watch live gameplay
- Python backend (game logic) + Pixi.js frontend (rendering)

## Architecture

### Three Main Components

**1. Python Game Server**
- Runs the existing game engine (ECS architecture with Esper)
- Each player session creates an isolated game world
- Game loop runs at 30 FPS
- Exports game state using existing `export_game_state()` function
- Broadcasts JSON over WebSocket to all connected clients
- One client designated as "player" (can send input)
- Others are "spectators" (read-only)

**2. WebSocket Protocol**
- Bidirectional communication channel
- Server → Clients: game state updates (JSON at 30 FPS)
- Player → Server: keyboard input events (WASD movement, arrow keys for shooting)
- Connection handshake distinguishes player vs spectator

**3. Pixi.js Frontend**
- Single-page web application
- Connects via WebSocket
- Hardware-accelerated WebGL rendering
- Loads sprite sheets and maps entity types to sprites
- Handles animation/interpolation for smooth movement
- Responsive UI for health/coins/items
- Players send keyboard input; spectators only render

**Key Decision**: Server is authoritative. All game logic runs in Python. Frontend is a "thin client" that only renders and sends input. This keeps proven Python game logic intact and makes spectator mode trivial.

## Game Server Implementation

### Session Management

`GameSessionManager` handles multiple concurrent game sessions. Each session has:
- Unique session ID
- Isolated Esper world (using `esper.switch_world()`)
- One `GameEngine` instance
- Set of connected WebSocket clients (one player, N spectators)
- Session state (running, paused, game over)

### Connection Flow

When a client connects:
1. Client sends handshake: `{"type": "connect", "role": "player" | "spectator", "sessionId": "optional"}`
2. If role is "player" and no sessionId: create new session, assign as player
3. If role is "spectator" with sessionId: join existing session as spectator
4. Server responds: `{"sessionId": "abc123", "role": "player", "status": "ready"}`

### Game Loop per Session

Each session runs asynchronously:

```python
async def run_game_session(session):
    while session.running:
        # Update game logic (30 FPS)
        session.engine.update(delta_time=1/30)

        # Export current state
        state = export_game_state(session.world_name)

        # Broadcast to all clients in this session
        await broadcast_to_session(session, state)

        await asyncio.sleep(1/30)
```

### Input Handling

- Only designated player can send input
- Player sends: `{"type": "input", "key": "w"}`
- Server validates sender is player (not spectator)
- Forwards to game engine's input system

### Server Structure

- `src/web/server.py` - Main WebSocket server
- `src/web/session_manager.py` - Manages multiple game sessions
- `src/web/protocol.py` - Message serialization/validation

## Pixi.js Frontend - Core Rendering

### Application Structure

- `web/src/index.html` - Entry point with canvas container
- `web/src/game.js` - Main Pixi.js application and game state manager
- `web/src/renderer.js` - Entity rendering system
- `web/src/sprites.js` - Sprite atlas loading and management
- `web/src/network.js` - WebSocket connection handling
- `web/src/ui.js` - UI overlay (health, coins, items)

### Pixi.js Setup

```javascript
const app = new PIXI.Application({
    width: 1920,
    height: 640,
    backgroundColor: 0x000000,
    resolution: window.devicePixelRatio || 1,
    autoDensity: true
});
```

Canvas uses coordinate system matching game's 60x20 grid, each tile 32x32 pixels.

### Sprite System

- Load sprite atlas (single PNG + JSON manifest)
- `SpriteManager` maps entity types to sprite textures:
  - `player` → player sprite
  - `enemy_chaser` → chaser enemy sprite
  - `projectile` → bullet sprite
  - etc.
- Each entity gets corresponding Pixi `Sprite` object
- Maintain map of `entityId → PIXI.Sprite` to reuse sprites across frames

### Frame Update

When receiving game state:
1. Parse JSON
2. For each entity: create sprite if new, update position if exists, remove sprite if gone
3. Update sprite positions with smooth interpolation
4. Update UI elements (health bar, coins, etc.)

## Animation and Visual Effects

### Sprite Animation

Each entity type has multiple animation states:
- **Player**: idle, walk (4 directions), shoot (4 directions)
- **Enemies**: idle, move, attack, death
- **Projectiles**: travel, impact

Use `PIXI.AnimatedSprite` for frame-based animations. Sprite atlas includes all animation frames. Animation state determined by entity components (velocity for movement, health <= 0 for death).

### Interpolation

Server sends updates at 30 FPS, browser renders at 60 FPS. Use linear interpolation between received positions:

```javascript
// Smooth movement between network updates
sprite.x = lerp(lastPos.x, currentPos.x, alpha);
sprite.y = lerp(lastPos.y, currentPos.y, alpha);
```

### Particle Effects

Use `PIXI.ParticleEmitter` (from pixi-particles library) for:
- Projectile trails
- Enemy death explosions
- Item pickup sparkles
- Door opening effects

Particles are client-side only (not in game state), triggered by state changes.

### Visual Polish

- Screen shake on player damage (camera offset)
- Flash effects on hits (sprite tint)
- Health bars above enemies (PIXI.Graphics rectangles)
- Fade-in/out for room transitions

All effects driven by game state changes but rendered purely client-side.

## UI, Input, and Spectator Experience

### UI Layout

Three layers:
1. **Game Canvas** (Pixi.js) - Main game view, 1920x640px, centered
2. **HUD Overlay** (HTML/CSS) - Health, coins, bombs, items as absolutely positioned divs
3. **Side Panel** (HTML/CSS) - Session info, spectator count, connection status

### Player Input

For active player:
- Capture keyboard: WASD (movement), Arrow keys (shooting), Space (bombs), E (use item)
- Send to server: `{"type": "input", "key": "w", "action": "press"}`
- Show input indicators (visual feedback for pressed keys)
- Handle key repeat and prevent browser defaults

### Spectator View

Spectators see:
- Same game canvas as player (identical rendering)
- "SPECTATOR MODE" badge
- Player name/info in side panel
- Connection status ("Watching player123...")
- No input capture (keyboard inactive)

### Session Discovery

Frontend includes:
- Landing page with "Play" or "Watch" buttons
- "Watch" shows list of active sessions (from server API)
- Click session to join as spectator
- Show session metadata: player name, current floor, time played

### Connection States

Handle all network scenarios:
- **Connecting**: show loading spinner
- **Connected**: game renders normally
- **Disconnected**: show reconnect button, pause rendering
- **Player left** (spectator view): show "Game ended" message

## Deployment and Technical Considerations

### Development Setup

- **Python dependencies**: `websockets`, existing game dependencies via `uv`
- **Frontend build**: Vite for bundling, npm for package management
- **Frontend dependencies**: `pixi.js`, `pixi-particles`
- **Development mode**: Python server on `localhost:8765`, Vite dev server with proxy

### Production Deployment

Deploy as two services:

**Python WebSocket Server**:
- Deploy on Railway, Render, or DigitalOcean App Platform
- Uses async/await with `asyncio` and `websockets`
- Environment variables for host/port configuration
- Health check endpoint for monitoring

**Static Frontend**:
- Deploy on Netlify, Vercel, or Cloudflare Pages
- Single-page app built with Vite
- Configure WebSocket URL via environment variable

### Asset Pipeline

- Sprite sheets created with TexturePacker or Aseprite
- Store in `web/assets/sprites/` directory
- Generate atlas JSON manifest with sprite positions
- Optimize PNGs with pngquant
- Load sprites on frontend initialization with loading screen

### Performance Targets

- **Server**: Handle 10-20 concurrent game sessions (one player + spectators each)
- **Network**: ~10-30KB/s per spectator (JSON state at 30 FPS)
- **Frontend**: Solid 60 FPS rendering with 100+ entities on screen
- **Latency**: <100ms input response time for player

### Monitoring

- Server logs session creation/termination
- Track spectator count per session
- Frontend reports connection drops
- FPS counter visible for debugging

## Implementation Phases

1. **Backend**: Session manager, WebSocket server, protocol
2. **Frontend Core**: Pixi.js setup, sprite loading, basic rendering
3. **Animation**: Interpolation, sprite animations, particle effects
4. **UI**: HUD overlay, session discovery, spectator mode
5. **Polish**: Visual effects, sound integration, deployment setup
6. **Assets**: Custom sprite sheets, sound effects, music
