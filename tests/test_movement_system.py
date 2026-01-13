"""Tests for movement system."""
import pytest
import esper
from src.systems.movement import MovementSystem
from src.components.core import Position, Velocity


def test_movement_system_moves_entities():
    """Test that MovementSystem updates entity positions based on velocity."""
    world_name = "test_movement_1"
    esper.switch_world(world_name)
    esper.clear_database()

    system = MovementSystem()
    esper.add_processor(system)

    # Create entity with position and velocity
    entity = esper.create_entity()
    esper.add_component(entity, Position(10.0, 10.0))
    esper.add_component(entity, Velocity(2.0, -1.0))

    # Set delta time and process
    system.dt = 1.0
    esper.process()

    # Check position updated
    pos = esper.component_for_entity(entity, Position)
    assert pos.x == 12.0
    assert pos.y == 9.0


def test_movement_system_respects_delta_time():
    """Test that MovementSystem correctly scales velocity by delta time."""
    world_name = "test_movement_2"
    esper.switch_world(world_name)
    esper.clear_database()

    system = MovementSystem()
    esper.add_processor(system)

    entity = esper.create_entity()
    esper.add_component(entity, Position(0.0, 0.0))
    esper.add_component(entity, Velocity(10.0, 0.0))

    # Half-second frame
    system.dt = 0.5
    esper.process()

    pos = esper.component_for_entity(entity, Position)
    assert pos.x == 5.0
