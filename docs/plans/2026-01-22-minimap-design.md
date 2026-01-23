# Minimap Design

## Overview

Add a minimap to the top-right corner showing explored dungeon rooms. Classic roguelike style - only visited rooms are visible.

## Server: Data Export

Add `minimap` field to session metadata in `get_game_state()`:

```python
def _export_minimap(self) -> list:
    if not self.dungeon:
        return []
    rooms = []
    for pos, room in self.dungeon.rooms.items():
        if room.visited:
            rooms.append({
                'x': pos[0],
                'y': pos[1],
                'type': room.room_type.value,
                'cleared': room.cleared
            })
    return rooms
```

## Client: Minimap Component

Create `web/src/ui/Minimap.ts`:

- DOM-based component (like HUD/SpectatorOverlay)
- Fixed position: top-right corner
- Cell size: 12px per room, 2px gap
- Semi-transparent black background

**Color scheme:**
- start → green (#00ff00)
- combat → gray (#666), white (#fff) if cleared
- boss → red (#ff0000)
- treasure → yellow (#ffcc00)
- shop → blue (#0088ff)
- secret → purple (#aa00ff)

**Current room:** white border highlight

## Client: Integration

Update `network.ts` interface:
```typescript
minimap: Array<{
    x: number;
    y: number;
    type: string;
    cleared: boolean;
}>;
```

Update `main.ts`:
- Create Minimap instance
- Update in onGameState with minimap data and roomPosition
- Show/hide with game state

## Tests

- `Minimap.test.ts`: Rendering, highlighting, colors, empty state
- Python: `_export_minimap()` returns only visited rooms
