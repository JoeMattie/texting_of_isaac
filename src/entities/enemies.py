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
        "patterns": {}  # No shooting - pure melee
    },
    "shooter": {
        "hp": 4,
        "speed": 1.5,
        "sprite": ("S", "magenta"),
        "patterns": {
            "aimed": {"count": 1, "spread": 0, "speed": 5.0, "cooldown": 2.0},
            "spread": {"count": 3, "spread": 30, "speed": 4.5, "cooldown": 2.5}
        }
    },
    "orbiter": {
        "hp": 5,
        "speed": 4.0,
        "sprite": ("O", "yellow"),
        "patterns": {
            "aimed": {"count": 1, "spread": 0, "speed": 6.0, "cooldown": 1.5},
            "ring": {"count": 8, "spread": 360, "speed": 4.0, "cooldown": 3.0}
        }
    },
    "turret": {
        "hp": 6,
        "speed": 0.0,
        "sprite": ("T", "red"),
        "patterns": {
            "spray": {"count": 5, "spread": 90, "speed": 5.0, "cooldown": 2.5},
            "cross": {"count": 4, "spread": 360, "speed": 5.5, "cooldown": 3.0}
        }
    },
    "tank": {
        "hp": 10,
        "speed": 2.0,
        "sprite": ("E", "bright_red"),
        "patterns": {
            "shockwave": {"count": 6, "spread": 360, "speed": 3.5, "cooldown": 4.0}
        }
    }
}


def create_enemy(world_name: str, enemy_type: str, x: float, y: float, floor: int = 1) -> int:
    """Create an enemy entity.

    Args:
        world_name: ECS world name
        enemy_type: Type of enemy ("chaser", "shooter", etc.)
        x, y: Starting position
        floor: Current floor number for stat scaling (default: 1)

    Returns:
        Entity ID of created enemy
    """
    if enemy_type not in ENEMY_DATA:
        raise ValueError(f"Unknown enemy type: {enemy_type}")

    esper.switch_world(world_name)
    data = ENEMY_DATA[enemy_type]
    entity = esper.create_entity()

    # Apply floor scaling to HP
    base_hp = data["hp"]
    hp_multiplier = Config.FLOOR_HP_MULTIPLIERS.get(floor, 1.0)
    scaled_hp = int(base_hp * hp_multiplier)

    esper.add_component(entity, Position(x, y))
    esper.add_component(entity, Velocity(0.0, 0.0))
    esper.add_component(entity, Health(scaled_hp, scaled_hp))
    esper.add_component(entity, Sprite(data["sprite"][0], data["sprite"][1]))
    esper.add_component(entity, Collider(Config.ENEMY_HITBOX))
    esper.add_component(entity, Enemy(enemy_type))

    # Add AI if enemy has patterns
    if data["patterns"]:
        # Initialize cooldowns from pattern data
        cooldowns = {name: pattern["cooldown"] for name, pattern in data["patterns"].items()}
        esper.add_component(entity, AIBehavior(
            pattern_cooldowns=cooldowns,
            pattern_index=0
        ))

    return entity
