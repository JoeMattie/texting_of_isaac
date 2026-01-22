# Running the Web Frontend Demo

This guide walks through running the complete Texting of Isaac web frontend with the Python game server.

## Prerequisites

- Python 3.12+ with `uv` package manager
- Node.js 18+ with `npm`
- A terminal/command line

## Setup

### 1. Install Python Dependencies

```bash
# From project root
uv sync
```

### 2. Install Frontend Dependencies

```bash
cd web
npm install
```

## Running the Demo

You'll need **two terminal windows** - one for the backend server, one for the frontend.

### Terminal 1: Start Python WebSocket Server

```bash
# From project root
uv run python -m src.web.server
```

Expected output:
```
Starting WebSocket server on localhost:8765
Server ready - waiting for connections
```

### Terminal 2: Start Frontend Dev Server

```bash
# From the web/ directory
npm run dev
```

Expected output:
```
VITE vX.X.X ready in XXXms

Local:   http://localhost:3000/
```

## Testing the Application

### Test 1: Basic Connection

1. Open your browser to `http://localhost:3000`
2. **Expected**: Black canvas (1920x640) appears
3. **Expected**: UI panel in top-right shows "Session: XXXXXXXX" and "Role: player"
4. **Expected**: Browser console shows "Session established"

### Test 2: Game State Rendering

1. Wait a few seconds after connection
2. **Expected**: Colored squares appear on the canvas representing entities:
   - Green square = Player
   - Red squares = Enemies
   - Cyan = Doors
   - Yellow = Coins
   - Pink = Hearts
3. **Expected**: UI panel shows health (♥♥♥), coins, and bombs

### Test 3: Player Movement (WASD)

1. Press `W`, `A`, `S`, `D` keys
2. **Expected**: Green player square moves around the canvas
3. **Expected**: No page scrolling (keyboard defaults are prevented)
4. **Expected**: Position updates smoothly

### Test 4: Player Shooting (Arrow Keys)

1. Press arrow keys (↑ ↓ ← →)
2. **Expected**: Cyan projectile squares appear and move in the pressed direction
3. **Expected**: Projectiles travel across the screen
4. **Expected**: Projectiles disappear when off-screen or hitting enemies

### Test 5: Enemy Behavior

1. Watch the red enemy squares
2. **Expected**: Enemies move (some chase player, some orbit, etc.)
3. **Expected**: Enemies shoot magenta projectiles at the player
4. **Expected**: Enemy positions update smoothly

### Test 6: Collision Detection

1. Shoot projectiles at enemies (use arrow keys)
2. **Expected**: When cyan projectile hits red enemy, enemy disappears
3. **Expected**: When magenta projectile hits green player, health decreases (♥ → ♡)
4. **Expected**: UI panel updates health display immediately

### Test 7: Item Collection

1. Move player (WASD) to purple item squares
2. **Expected**: Item disappears when player touches it
3. **Expected**: UI panel "Items" list updates to show collected item
4. **Expected**: Player stats may change (damage, speed, fire rate)

### Test 8: Currency Collection

1. Move player to yellow coin squares
2. **Expected**: Coin disappears when player touches it
3. **Expected**: UI panel "Coins" count increases

### Test 9: Door Transitions

1. Move player to brown door squares at room edges
2. **Expected**: Screen transitions to new room layout
3. **Expected**: New enemies spawn
4. **Expected**: New obstacles appear

### Test 10: Disconnection Handling

1. Stop the Python server (Ctrl+C in Terminal 1)
2. **Expected**: Frontend UI shows "⚠ Disconnected" in status
3. **Expected**: Game stops updating
4. **Expected**: No browser errors or crashes

### Test 11: Reconnection

1. Restart Python server
2. Refresh browser page
3. **Expected**: New session connects successfully
4. **Expected**: Game resumes with new session ID

## Troubleshooting

### Frontend doesn't connect

**Symptom**: "⚠ Error: Connection error" in UI
**Solution**: Verify Python server is running on port 8765

### Sprites don't load

**Symptom**: "Failed to load game assets" error
**Solution**: Check browser console for specific errors, try hard refresh (Ctrl+Shift+R)

### Input not working

**Symptom**: Pressing WASD/arrows doesn't move player
**Solution**: Click on the canvas area first to focus it

### TypeScript compilation errors

**Symptom**: `npm run dev` shows TypeScript errors
**Solution**: Run `npm install` again to ensure all dependencies are installed

### Port already in use

**Symptom**: Backend shows "Address already in use" error
**Solution**: Kill existing process on port 8765 or change port in config

## Next Steps

Once all tests pass:
- Try multiple browser tabs as "spectators" (not yet implemented)
- Test on different browsers (Chrome, Firefox, Safari)
- Measure FPS performance with browser dev tools
- Profile network traffic to verify efficient state updates

## Development Notes

- Backend runs at 30 FPS (game updates)
- Frontend renders at 60 FPS (browser refresh rate)
- WebSocket sends JSON game state ~30 times per second
- Each entity has position, sprite type, and components

## Stopping the Demo

1. Press Ctrl+C in Terminal 1 (Python server)
2. Press Ctrl+C in Terminal 2 (Vite dev server)
3. Close browser tabs
