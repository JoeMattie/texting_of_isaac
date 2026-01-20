"""Trapdoor entity factory."""
import esper
from src.components.core import Position, Sprite
from src.components.combat import Collider
from src.components.boss import Trapdoor


def create_trapdoor(world_name: str, x: float, y: float, next_floor: int) -> int:
    """Create a trapdoor entity for floor transitions.

    Args:
        world_name: ECS world name
        x, y: Position to spawn trapdoor
        next_floor: Which floor this trapdoor leads to

    Returns:
        Entity ID of created trapdoor
    """
    esper.switch_world(world_name)
    entity = esper.create_entity()

    esper.add_component(entity, Position(x, y))
    esper.add_component(entity, Sprite("▼", "white"))
    esper.add_component(entity, Collider(0.5))  # Collision radius for player pickup
    esper.add_component(entity, Trapdoor(next_floor=next_floor))

    return entity
