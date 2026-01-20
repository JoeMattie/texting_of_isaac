"""Tests for trapdoor entity factory."""
import pytest
import esper


@pytest.fixture
def world():
    """Create isolated test world."""
    world_name = "test_trapdoor_entities"
    esper.switch_world(world_name)
    esper.clear_database()
    yield world_name
    esper.clear_database()


def test_create_trapdoor(world):
    """Test creating trapdoor entity."""
    from src.entities.trapdoor import create_trapdoor
    from src.components.core import Position, Sprite
    from src.components.combat import Collider
    from src.components.boss import Trapdoor

    trapdoor = create_trapdoor(world, 30.0, 10.0, 2)

    # Verify entity exists
    assert esper.entity_exists(trapdoor)

    # Verify components
    assert esper.has_component(trapdoor, Position)
    assert esper.has_component(trapdoor, Sprite)
    assert esper.has_component(trapdoor, Collider)
    assert esper.has_component(trapdoor, Trapdoor)

    # Verify Position
    pos = esper.component_for_entity(trapdoor, Position)
    assert pos.x == 30.0
    assert pos.y == 10.0

    # Verify Sprite
    sprite = esper.component_for_entity(trapdoor, Sprite)
    assert sprite.char == "▼"
    assert sprite.color == "white"

    # Verify Collider (pickup radius)
    collider = esper.component_for_entity(trapdoor, Collider)
    assert collider.radius == 0.5

    # Verify Trapdoor component
    trapdoor_comp = esper.component_for_entity(trapdoor, Trapdoor)
    assert trapdoor_comp.next_floor == 2
