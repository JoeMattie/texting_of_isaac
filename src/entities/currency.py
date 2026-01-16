"""Currency entity creation functions."""
import esper
from src.components.core import Position, Sprite
from src.components.currency import Coin, BombPickup


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


def spawn_bomb_pickup(world_name: str, x: float, y: float, quantity: int = 1) -> int:
    """Spawn a bomb pickup entity.

    Args:
        world_name: Name of the world to spawn in
        x: X position
        y: Y position
        quantity: Number of bombs (default 1)

    Returns:
        Entity ID of created bomb pickup
    """
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(x, y))
    esper.add_component(bomb_ent, Sprite("B", "cyan"))
    esper.add_component(bomb_ent, BombPickup(quantity=quantity))

    return bomb_ent
