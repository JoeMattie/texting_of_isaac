"""Tests for boss entity factories."""
import pytest
import esper


@pytest.fixture
def world():
    """Create isolated test world."""
    world_name = "test_boss_entities"
    esper.switch_world(world_name)
    esper.clear_database()
    yield world_name
    esper.clear_database()


def test_create_boss_a(world):
    """Test creating Boss A entity."""
    from src.entities.bosses import create_boss
    from src.components.core import Position, Health, Sprite, Velocity
    from src.components.combat import Collider
    from src.components.boss import Boss, BossAI

    boss = create_boss(world, "boss_a", 30.0, 10.0)

    # Verify entity exists
    assert esper.entity_exists(boss)

    # Verify components
    assert esper.has_component(boss, Position)
    assert esper.has_component(boss, Velocity)
    assert esper.has_component(boss, Health)
    assert esper.has_component(boss, Sprite)
    assert esper.has_component(boss, Collider)
    assert esper.has_component(boss, Boss)
    assert esper.has_component(boss, BossAI)

    # Verify Boss component
    boss_comp = esper.component_for_entity(boss, Boss)
    assert boss_comp.boss_type == "boss_a"
    assert boss_comp.current_phase == 1

    # Verify Health
    health = esper.component_for_entity(boss, Health)
    assert health.max == 50
    assert health.current == 50

    # Verify Sprite
    sprite = esper.component_for_entity(boss, Sprite)
    assert sprite.char == "◉"
    assert sprite.color == "cyan"


def test_create_boss_b(world):
    """Test creating Boss B entity."""
    from src.entities.bosses import create_boss
    from src.components.core import Health, Sprite
    from src.components.boss import Boss

    boss = create_boss(world, "boss_b", 30.0, 10.0)

    # Verify Boss type
    boss_comp = esper.component_for_entity(boss, Boss)
    assert boss_comp.boss_type == "boss_b"

    # Verify Health
    health = esper.component_for_entity(boss, Health)
    assert health.max == 75

    # Verify Sprite
    sprite = esper.component_for_entity(boss, Sprite)
    assert sprite.char == "✦"
    assert sprite.color == "yellow"


def test_create_boss_c(world):
    """Test creating Boss C entity."""
    from src.entities.bosses import create_boss
    from src.components.core import Health, Sprite
    from src.components.boss import Boss

    boss = create_boss(world, "boss_c", 30.0, 10.0)

    # Verify Boss type
    boss_comp = esper.component_for_entity(boss, Boss)
    assert boss_comp.boss_type == "boss_c"

    # Verify Health
    health = esper.component_for_entity(boss, Health)
    assert health.max == 100

    # Verify Sprite
    sprite = esper.component_for_entity(boss, Sprite)
    assert sprite.char == "◈"
    assert sprite.color == "bright_red"


def test_create_invalid_boss(world):
    """Test creating invalid boss type raises error."""
    from src.entities.bosses import create_boss

    with pytest.raises(ValueError, match="Unknown boss type"):
        create_boss(world, "invalid_boss", 30.0, 10.0)
