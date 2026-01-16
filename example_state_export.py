"""Example: Exporting full game state as JSON for web frontend.

This demonstrates how to export the complete game state every frame,
which can be sent to a web frontend for rendering with sprites.
"""
import json
import esper
from src.components.core import Position, Sprite, Health, Velocity
from src.components.game import Player, Enemy, Currency, CollectedItems
from src.components.dungeon import Door
from src.components.combat import Collider
from src.config import Config


def export_game_state(world_name: str = "main") -> dict:
    """Export complete game state as structured data.

    Returns a dictionary that can be JSON-serialized and sent to
    a web frontend for rendering with sprites instead of ASCII.

    Args:
        world_name: ECS world to export

    Returns:
        Dictionary containing all game state
    """
    esper.switch_world(world_name)

    state = {
        "frame": {
            "width": Config.ROOM_WIDTH,
            "height": Config.ROOM_HEIGHT,
        },
        "entities": [],
        "player": None,
        "ui": {
            "currency": {"coins": 0, "bombs": 0},
            "health": {"current": 0, "max": 0},
            "items": [],
        },
        "room": {
            "position": None,  # Would come from RoomManager
            "doors": [],
        }
    }

    # Export all entities with their components
    for ent in esper._entities:
        entity_data = {
            "id": ent,
            "type": _get_entity_type(ent),
            "components": {}
        }

        # Position
        if esper.has_component(ent, Position):
            pos = esper.component_for_entity(ent, Position)
            entity_data["components"]["position"] = {
                "x": pos.x,
                "y": pos.y
            }

        # Sprite (visual representation)
        if esper.has_component(ent, Sprite):
            sprite = esper.component_for_entity(ent, Sprite)
            entity_data["components"]["sprite"] = {
                "char": sprite.char,
                "color": sprite.color
            }

        # Health
        if esper.has_component(ent, Health):
            health = esper.component_for_entity(ent, Health)
            entity_data["components"]["health"] = {
                "current": health.current,
                "max": health.max
            }

        # Velocity
        if esper.has_component(ent, Velocity):
            vel = esper.component_for_entity(ent, Velocity)
            entity_data["components"]["velocity"] = {
                "dx": vel.dx,
                "dy": vel.dy
            }

        # Collider
        if esper.has_component(ent, Collider):
            collider = esper.component_for_entity(ent, Collider)
            entity_data["components"]["collider"] = {
                "radius": collider.radius
            }

        # Door-specific data
        if esper.has_component(ent, Door):
            door = esper.component_for_entity(ent, Door)
            entity_data["components"]["door"] = {
                "direction": door.direction,
                "locked": door.locked,
                "leads_to": door.leads_to
            }
            state["room"]["doors"].append(entity_data)

        # Player-specific data
        if esper.has_component(ent, Player):
            state["player"] = entity_data

            # Extract UI data from player
            if esper.has_component(ent, Currency):
                currency = esper.component_for_entity(ent, Currency)
                state["ui"]["currency"] = {
                    "coins": currency.coins,
                    "bombs": currency.bombs
                }

            if esper.has_component(ent, Health):
                health = esper.component_for_entity(ent, Health)
                state["ui"]["health"] = {
                    "current": health.current,
                    "max": health.max
                }

            if esper.has_component(ent, CollectedItems):
                items = esper.component_for_entity(ent, CollectedItems)
                state["ui"]["items"] = items.items.copy()

        state["entities"].append(entity_data)

    return state


def _get_entity_type(entity_id: int) -> str:
    """Determine entity type from its components."""
    if esper.has_component(entity_id, Player):
        return "player"
    elif esper.has_component(entity_id, Enemy):
        enemy = esper.component_for_entity(entity_id, Enemy)
        return f"enemy_{enemy.enemy_type}"
    elif esper.has_component(entity_id, Door):
        return "door"
    else:
        # Check sprite for item/projectile detection
        if esper.has_component(entity_id, Sprite):
            sprite = esper.component_for_entity(entity_id, Sprite)
            if sprite.char == '$':
                return "coin"
            elif sprite.char == '♥':
                return "heart"
            elif sprite.char == 'B':
                return "bomb"
            elif sprite.char in ['•', '○', '●']:
                return "projectile"
        return "unknown"


def export_to_json(world_name: str = "main") -> str:
    """Export game state as JSON string.

    This can be sent over a WebSocket connection to a web frontend.

    Example usage:
        # In your game loop
        state_json = export_to_json()
        websocket.send(state_json)
    """
    state = export_game_state(world_name)
    return json.dumps(state, indent=2)


# Example usage
if __name__ == "__main__":
    # This would be called every frame in your game loop
    state = export_game_state()
    print(json.dumps(state, indent=2))
