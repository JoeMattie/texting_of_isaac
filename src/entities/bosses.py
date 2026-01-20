"""Boss entity factories."""
import esper
from src.components.core import Position, Velocity, Health, Sprite
from src.components.combat import Collider
from src.components.boss import Boss, BossAI
from src.config import Config


BOSS_DATA = {
    "boss_a": {
        "name": "The Orbiter",
        "hp": 50,
        "sprite": ("◉", "cyan"),
        "patterns": ["spiral", "wave"],
        "phase_2_patterns": ["double_spiral", "fast_wave"],
        "teleport_cooldowns": {"phase_1": 7.0, "phase_2": 4.0}
    },
    "boss_b": {
        "name": "The Crossfire",
        "hp": 75,
        "sprite": ("✦", "yellow"),
        "patterns": ["wave", "pulse"],
        "phase_2_patterns": ["fast_wave", "burst_pulse"],
        "teleport_cooldowns": {"phase_1": 6.0, "phase_2": 3.0}
    },
    "boss_c": {
        "name": "The Spiral King",
        "hp": 100,
        "sprite": ("◈", "bright_red"),
        "patterns": ["pulse", "spiral"],
        "phase_2_patterns": ["burst_pulse", "double_spiral"],
        "teleport_cooldowns": {"phase_1": 6.0, "phase_2": 3.0}
    }
}


def create_boss(world_name: str, boss_type: str, x: float, y: float) -> int:
    """Create a boss entity.

    Args:
        world_name: ECS world name
        boss_type: Type of boss ("boss_a", "boss_b", "boss_c")
        x, y: Starting position

    Returns:
        Entity ID of created boss

    Raises:
        ValueError: If boss_type is not recognized
    """
    if boss_type not in BOSS_DATA:
        raise ValueError(f"Unknown boss type: {boss_type}")

    esper.switch_world(world_name)
    data = BOSS_DATA[boss_type]
    entity = esper.create_entity()

    esper.add_component(entity, Position(x, y))
    esper.add_component(entity, Velocity(0.0, 0.0))
    esper.add_component(entity, Health(data["hp"], data["hp"]))
    esper.add_component(entity, Sprite(data["sprite"][0], data["sprite"][1]))
    esper.add_component(entity, Collider(Config.ENEMY_HITBOX))  # Same size as enemies
    esper.add_component(entity, Boss(boss_type=boss_type))

    # Add BossAI with initial phase 1 pattern
    initial_pattern = data["patterns"][0]
    esper.add_component(entity, BossAI(
        pattern_name=initial_pattern,
        pattern_cooldown=3.0,  # Default cooldown
        teleport_cooldown=data["teleport_cooldowns"]["phase_1"]
    ))

    return entity
