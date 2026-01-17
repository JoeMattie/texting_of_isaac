"""Shop entity factories."""
import random
import esper
from src.config import Config
from src.components.core import Position, Sprite
from src.components.game import Item
from src.components.dungeon import ShopItem
from src.data.items import ITEM_DEFINITIONS


def create_shop_item(world_name: str, item_name: str, x: float, y: float) -> int:
    """Create a shop item entity at position.

    Args:
        world_name: ECS world name
        item_name: Name of item to sell
        x: X position
        y: Y position

    Returns:
        Entity ID
    """
    esper.switch_world(world_name)

    entity = esper.create_entity()

    # Get item definition
    item_def = ITEM_DEFINITIONS[item_name]

    # Add item component
    esper.add_component(entity, Item(
        name=item_name,
        stat_modifiers=item_def.get("stat_modifiers", {}),
        special_effects=item_def.get("special_effects", [])
    ))

    # Add shop component with price
    price = Config.SHOP_ITEM_PRICES.get(item_name, 10)
    esper.add_component(entity, ShopItem(
        item_name=item_name,
        price=price,
        purchased=False
    ))

    # Add position
    esper.add_component(entity, Position(x, y))

    # Add sprite (use item sprite from definition)
    sprite_char = item_def.get("sprite", "?")
    sprite_color = item_def.get("color", "yellow")
    esper.add_component(entity, Sprite(sprite_char, sprite_color))

    return entity


def generate_shop_items() -> list[str]:
    """Generate random selection of shop items.

    Returns:
        List of 3-4 item names for shop
    """
    all_items = list(Config.SHOP_ITEM_PRICES.keys())
    num_items = random.randint(Config.SHOP_ITEMS_MIN, Config.SHOP_ITEMS_MAX)

    return random.sample(all_items, num_items)
