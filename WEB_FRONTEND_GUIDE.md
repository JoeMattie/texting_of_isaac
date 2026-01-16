# Web Frontend Guide

## Answer: Yes, the game state can be fully exported!

The ECS (Entity Component System) architecture makes it very easy to export the entire game state as structured data every frame. All game state lives in components attached to entities, so you can query and serialize everything.

## How It Works

### 1. Current State (ASCII Rendering)

The existing `RenderSystem` already exports structured data:

```python
grid = render_system.render("main")
# Returns: List[List[Dict]] where each cell is {'char': str, 'color': str}
```

### 2. Full State Export (for Web Frontend)

The `example_state_export.py` file shows how to export **everything**:

- **Entities**: Position, sprite, health, velocity, collider for all entities
- **Player UI**: Currency (coins/bombs), health, collected items
- **Room State**: Current room position, door states
- **Entity Types**: Player, enemies (by type), doors, items, projectiles

The exported state looks like:

```json
{
  "frame": {"width": 60, "height": 20},
  "entities": [
    {
      "id": 1,
      "type": "player",
      "components": {
        "position": {"x": 30.5, "y": 10.2},
        "sprite": {"char": "@", "color": "#00ff00"},
        "health": {"current": 3, "max": 3},
        "velocity": {"dx": 0.5, "dy": 0},
        "collider": {"radius": 0.5}
      }
    }
  ],
  "ui": {
    "currency": {"coins": 12, "bombs": 3},
    "health": {"current": 3, "max": 3},
    "items": ["piercing", "multi_shot"]
  },
  "room": {
    "position": [0, 0],
    "doors": [...]
  }
}
```

## Architecture Options

### Option 1: WebSocket Streaming (Real-time)

**Best for:** Smooth 60 FPS rendering with sprites

```
Python Game (Backend)          Web Browser (Frontend)
┌─────────────────────┐       ┌──────────────────────┐
│  Game Engine        │       │  Canvas Rendering    │
│  ↓                  │       │  ↓                   │
│  export_game_state()│──────→│  renderGameState()   │
│  ↓                  │ JSON  │  ↓                   │
│  WebSocket.send()   │ 60fps │  Draw sprites        │
└─────────────────────┘       └──────────────────────┘
```

**Pros:**
- Real-time updates (60 FPS)
- Smooth animations
- Can use actual sprite images instead of ASCII
- Interactive (send input back to server)

**Cons:**
- Requires WebSocket server
- Network latency
- More complex setup

### Option 2: Local Web View (Electron/PyWebView)

**Best for:** Desktop app with web UI

```python
import webview

# Create window showing your HTML
webview.create_window('Texting of Isaac', 'index.html')

# Expose game state to JavaScript
webview.evaluate_js(f'updateGameState({json.dumps(state)})')
```

**Pros:**
- No network latency
- Native desktop app
- Can still use web technologies (HTML/CSS/JS)

**Cons:**
- Additional dependency (pywebview or electron)
- Still two processes communicating

### Option 3: Direct Canvas Rendering (Python)

**Best for:** Quick prototyping without web frontend

Use pygame or pyglet to render sprites directly in Python:

```python
import pygame

# Load sprite images
player_sprite = pygame.image.load('sprites/player.png')

# Render based on Position components
for ent, (pos, sprite) in esper.get_components(Position, Sprite):
    if sprite.char == '@':  # Player
        screen.blit(player_sprite, (pos.x * TILE_SIZE, pos.y * TILE_SIZE))
```

## Performance Considerations

### Is JSON export every frame too slow?

**No, it's very fast:**

```python
import time

start = time.perf_counter()
state = export_game_state()  # ~266 entities in test suite
state_json = json.dumps(state)
elapsed = time.perf_counter() - start

print(f"Export time: {elapsed * 1000:.2f}ms")
# Typical result: 1-3ms on modern hardware
```

At 60 FPS, you have 16.67ms per frame. JSON serialization takes 1-3ms, leaving plenty of time for game logic.

### Optimization Tips

1. **Only export visible entities:**
   ```python
   # Only export entities in current room
   if esper.has_component(ent, RoomPosition):
       room_pos = esper.component_for_entity(ent, RoomPosition)
       if room_pos == current_room:
           # Export this entity
   ```

2. **Delta compression** (only send what changed):
   ```python
   def export_delta(previous_state, current_state):
       """Only export entities that moved/changed."""
       delta = {"changed": [], "removed": [], "added": []}
       # Compare states and build delta
       return delta
   ```

3. **Binary format** (instead of JSON):
   ```python
   import msgpack
   state_bytes = msgpack.packb(state)  # 30-50% smaller, faster
   ```

## Getting Started

### 1. Try the Demo

```bash
# Install websockets
pip install websockets

# Start the demo server
python example_websocket_server.py

# Open example_web_frontend.html in your browser
# Uncomment line 175 to connect to server
```

### 2. Integrate with Your Game

```python
from example_state_export import export_game_state
import json

# In your game loop (main.py):
while game_running:
    # Normal game update
    engine.update(delta_time)

    # Export state for web frontend
    state = export_game_state("main")

    # Send to frontend (WebSocket, file, etc.)
    websocket.send(json.dumps(state))
```

### 3. Create Your Frontend

The `example_web_frontend.html` shows:
- Canvas rendering with sprites
- UI panel (health, coins, items)
- FPS counter
- WebSocket connection

You can replace the ASCII characters with actual sprite images:

```javascript
// Load sprite atlas
const sprites = {
    player: new Image(),
    chaser: new Image(),
    // ...
};

sprites.player.src = 'assets/player.png';

// Render with sprites instead of text
function renderEntity(entity) {
    const sprite = sprites[entity.type];
    ctx.drawImage(sprite, pos.x * TILE_SIZE, pos.y * TILE_SIZE);
}
```

## Advantages of This Approach

1. **Separation of Concerns**: Game logic in Python, rendering in web
2. **Easy Sprite Swapping**: Change sprites without touching game code
3. **Web Technologies**: Use CSS animations, HTML UI, JavaScript effects
4. **Cross-platform**: Works in any browser
5. **Debugging**: Inspect game state with browser dev tools
6. **Recording**: Can record JSON stream and replay later

## Example: Full Integration

```python
# game_with_web_frontend.py
import asyncio
import json
import websockets
from src.engine.game import GameEngine
from example_state_export import export_game_state

class WebGameServer:
    def __init__(self):
        self.clients = set()
        self.engine = GameEngine()

    async def handle_client(self, websocket, path):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                # Handle input from web client
                data = json.loads(message)
                if data['type'] == 'input':
                    self.engine.handle_input(data['key'])
        finally:
            self.clients.remove(websocket)

    async def game_loop(self):
        while self.engine.running:
            # Update game
            self.engine.update(1/60)

            # Export and broadcast state
            state = export_game_state("main")
            if self.clients:
                await asyncio.gather(*[
                    client.send(json.dumps(state))
                    for client in self.clients
                ])

            await asyncio.sleep(1/60)

    async def run(self):
        async with websockets.serve(self.handle_client, "localhost", 8765):
            await self.game_loop()

if __name__ == "__main__":
    server = WebGameServer()
    asyncio.run(server.run())
```

## Next Steps

1. **Try the demo** - See it working with mock data
2. **Add sprite assets** - Replace ASCII chars with actual images
3. **Implement input** - Send keyboard/mouse input back to Python
4. **Add effects** - Use CSS/Canvas for visual effects
5. **Optimize** - Add delta compression if needed

The ECS architecture makes this trivially easy - all state is already structured and queryable!
