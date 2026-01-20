import pytest
import esper


@pytest.fixture
def world():
    """Create a clean test world."""
    world_name = "test_enemy_floor_scaling"
    esper.switch_world(world_name)
    esper.clear_database()
    yield world_name
    esper.clear_database()


def test_enemy_floor_scaling(world):
    """Test enemies scale stats based on floor number."""
    from src.entities.enemies import create_enemy
    from src.components.core import Health
    from src.components.combat import Stats
    from src.config import Config

    # Floor 1 (base stats)
    enemy1 = create_enemy(world, "chaser", 10, 10, floor=1)
    health1 = esper.component_for_entity(enemy1, Health)
    assert health1.max == 3  # Base HP

    # Floor 2 (1.3x HP multiplier)
    enemy2 = create_enemy(world, "chaser", 15, 10, floor=2)
    health2 = esper.component_for_entity(enemy2, Health)
    expected_hp2 = int(3 * Config.FLOOR_HP_MULTIPLIERS[2])
    assert health2.max == expected_hp2

    # Floor 3 (1.6x HP multiplier)
    enemy3 = create_enemy(world, "chaser", 20, 10, floor=3)
    health3 = esper.component_for_entity(enemy3, Health)
    expected_hp3 = int(3 * Config.FLOOR_HP_MULTIPLIERS[3])
    assert health3.max == expected_hp3


def test_enemy_floor_defaults_to_1(world):
    """Test enemy creation defaults to floor 1 if not specified."""
    from src.entities.enemies import create_enemy
    from src.components.core import Health

    enemy = create_enemy(world, "chaser", 10, 10)
    health = esper.component_for_entity(enemy, Health)
    assert health.max == 3  # Floor 1 base HP
