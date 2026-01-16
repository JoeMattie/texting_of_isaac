"""Currency entity creation functions."""
import esper
from src.components.core import Position, Sprite
from src.components.currency import Coin


def spawn_coin(world_name: str, x: float, y: float, value: int = 1) -> int:
    """Spawn a coin pickup entity.

    Args:
        world_name: Name of the world to spawn in
        x: X position
        y: Y position
        value: Coin value (default 1 for penny, 5 for nickel, etc.)

    Returns:
        Entity ID of created coin
    """
    coin_ent = esper.create_entity()
    esper.add_component(coin_ent, Position(x, y))
    esper.add_component(coin_ent, Sprite("$", "yellow"))
    esper.add_component(coin_ent, Coin(value=value))

    return coin_ent
