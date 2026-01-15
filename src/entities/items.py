"""Item entity factory functions."""
import esper
import random
from src.components.core import Position, Sprite
from src.components.combat import Collider
from src.components.game import Item
from src.data.items import ITEM_DEFINITIONS


def create_item(world: str, item_name: str, x: float, y: float) -> int:
    """Create an item entity at the specified position.

    Args:
        world: World name to create entity in
        item_name: Name of item from ITEM_DEFINITIONS
        x: X position
        y: Y position

    Returns:
        Entity ID of created item

    Raises:
        ValueError: If item_name not in ITEM_DEFINITIONS
    """
    if item_name not in ITEM_DEFINITIONS:
        raise ValueError(f"Unknown item: {item_name}")

    item_data = ITEM_DEFINITIONS[item_name]

    esper.switch_world(world)
    entity = esper.create_entity()

    esper.add_component(entity, Position(x, y))
    esper.add_component(entity, Sprite(item_data["sprite"], item_data["color"]))
    esper.add_component(entity, Collider(0.4))  # Pickup radius
    esper.add_component(entity, Item(
        name=item_name,
        stat_modifiers=item_data["stat_modifiers"].copy(),
        special_effects=item_data["special_effects"].copy()
    ))

    return entity


def spawn_random_item(world: str, x: float, y: float) -> int:
    """Spawn a random item from the item pool.

    Args:
        world: World name to create entity in
        x: X position
        y: Y position

    Returns:
        Entity ID of created item
    """
    item_name = random.choice(list(ITEM_DEFINITIONS.keys()))
    return create_item(world, item_name, x, y)
