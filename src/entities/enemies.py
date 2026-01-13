"""Enemy entity factories."""
import esper
from src.components.core import Position, Velocity, Health, Sprite
from src.components.combat import Stats, Collider
from src.components.game import Enemy, AIBehavior
from src.config import Config


ENEMY_DATA = {
    "chaser": {
        "hp": 3,
        "speed": 3.0,
        "sprite": ("e", "red"),
        "patterns": {}
    },
    "shooter": {
        "hp": 4,
        "speed": 1.5,
        "sprite": ("S", "magenta"),
        "patterns": {"shoot": 2.0}  # Cooldown in seconds
    },
    "orbiter": {
        "hp": 5,
        "speed": 4.0,
        "sprite": ("O", "yellow"),
        "patterns": {"shoot": 1.5, "ring": 3.0}
    },
    "turret": {
        "hp": 6,
        "speed": 0.0,
        "sprite": ("T", "red"),
        "patterns": {"spray": 2.5}
    },
    "tank": {
        "hp": 10,
        "speed": 2.0,
        "sprite": ("E", "bright_red"),
        "patterns": {"charge": 4.0}
    }
}


def create_enemy(world_name: str, enemy_type: str, x: float, y: float) -> int:
    """Create an enemy entity.

    Args:
        world_name: ECS world name
        enemy_type: Type of enemy ("chaser", "shooter", etc.)
        x, y: Starting position

    Returns:
        Entity ID of created enemy
    """
    if enemy_type not in ENEMY_DATA:
        raise ValueError(f"Unknown enemy type: {enemy_type}")

    esper.switch_world(world_name)
    data = ENEMY_DATA[enemy_type]
    entity = esper.create_entity()

    esper.add_component(entity, Position(x, y))
    esper.add_component(entity, Velocity(0.0, 0.0))
    esper.add_component(entity, Health(data["hp"], data["hp"]))
    esper.add_component(entity, Sprite(data["sprite"][0], data["sprite"][1]))
    esper.add_component(entity, Collider(Config.ENEMY_HITBOX))
    esper.add_component(entity, Enemy(enemy_type))

    # Add AI if enemy has patterns
    if data["patterns"]:
        esper.add_component(entity, AIBehavior(data["patterns"].copy()))

    return entity
