"""Tests for input system."""
import pytest
import esper
from src.systems.input import InputSystem
from src.components.core import Position, Velocity
from src.components.combat import Stats
from src.components.game import Player


def test_input_system_processes_movement():
    """Test that InputSystem updates player velocity based on input."""
    world_name = "test_input_1"
    esper.switch_world(world_name)
    esper.clear_database()

    system = InputSystem()
    esper.add_processor(system)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(30.0, 10.0))
    esper.add_component(player, Velocity(0.0, 0.0))
    esper.add_component(player, Stats(speed=5.0, damage=1.0, fire_rate=2.0, shot_speed=8.0))

    # Simulate moving right
    system.set_input(move_x=1, move_y=0, shoot_x=0, shoot_y=0)
    esper.process()

    vel = esper.component_for_entity(player, Velocity)
    assert vel.dx > 0  # Moving right
    assert vel.dy == 0


def test_input_system_normalizes_diagonal_movement():
    """Test that InputSystem normalizes diagonal movement to prevent faster speed."""
    world_name = "test_input_2"
    esper.switch_world(world_name)
    esper.clear_database()

    system = InputSystem()
    esper.add_processor(system)

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(30.0, 10.0))
    esper.add_component(player, Velocity(0.0, 0.0))
    esper.add_component(player, Stats(speed=5.0, damage=1.0, fire_rate=2.0, shot_speed=8.0))

    # Move diagonally
    system.set_input(move_x=1, move_y=1, shoot_x=0, shoot_y=0)
    esper.process()

    vel = esper.component_for_entity(player, Velocity)
    # Diagonal movement should be normalized (not 1.414x faster)
    speed = (vel.dx**2 + vel.dy**2)**0.5
    assert abs(speed - 5.0) < 0.1
