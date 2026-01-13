"""Player entity factory."""
import esper
from src.components.core import Position, Velocity, Health, Sprite
from src.components.combat import Stats, Collider
from src.components.game import Player
from src.config import Config


def create_player(world: str, x: float, y: float) -> int:
    """Create the player entity at the given position.

    Args:
        world: The ECS world identifier
        x: Starting x coordinate
        y: Starting y coordinate

    Returns:
        Entity ID of the created player
    """
    esper.switch_world(world)
    entity = esper.create_entity()

    esper.add_component(entity, Position(x, y))
    esper.add_component(entity, Velocity(0.0, 0.0))
    esper.add_component(entity, Health(Config.PLAYER_MAX_HP, Config.PLAYER_MAX_HP))
    esper.add_component(entity, Sprite('@', 'cyan'))
    esper.add_component(entity, Stats(
        speed=Config.PLAYER_SPEED,
        damage=Config.PLAYER_DAMAGE,
        fire_rate=Config.PLAYER_FIRE_RATE,
        shot_speed=Config.PLAYER_SHOT_SPEED
    ))
    esper.add_component(entity, Collider(Config.PLAYER_HITBOX))
    esper.add_component(entity, Player())

    return entity
