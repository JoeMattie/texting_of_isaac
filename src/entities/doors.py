"""Door entity factory functions."""
import esper
from src.components.core import Position, Sprite
from src.components.combat import Collider
from src.components.dungeon import Door
from src.config import Config


def spawn_door(world_name: str, direction: str, leads_to: tuple[int, int], locked: bool = True) -> int:
    """Create door entity at appropriate wall position.

    Args:
        world_name: World to spawn in
        direction: "north", "south", "east", "west"
        leads_to: Destination room coordinates (x, y)
        locked: Initial lock state (True = locked, False = unlocked)

    Returns:
        Door entity ID

    Raises:
        ValueError: If direction is invalid
    """
    # Determine door position based on direction
    if direction == "north":
        x = Config.ROOM_WIDTH / 2
        y = 0
    elif direction == "south":
        x = Config.ROOM_WIDTH / 2
        y = Config.ROOM_HEIGHT - 1
    elif direction == "east":
        x = Config.ROOM_WIDTH - 1
        y = Config.ROOM_HEIGHT / 2
    elif direction == "west":
        x = 0
        y = Config.ROOM_HEIGHT / 2
    else:
        raise ValueError(f"Invalid direction: {direction}")

    # Determine sprite based on lock state
    if locked:
        sprite_char = "▮"
        sprite_color = "red"
    else:
        sprite_char = "▯"
        sprite_color = "cyan"

    # Create door entity
    esper.switch_world(world_name)
    entity = esper.create_entity()

    esper.add_component(entity, Position(x, y))
    esper.add_component(entity, Sprite(sprite_char, sprite_color))
    esper.add_component(entity, Collider(Config.DOOR_COLLIDER_RADIUS))
    esper.add_component(entity, Door(direction, leads_to, locked))

    return entity
