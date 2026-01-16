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


def test_input_system_tracks_bomb_input():
    """Test that InputSystem tracks bomb_pressed flag."""
    world_name = "test_input_3"
    esper.switch_world(world_name)
    esper.clear_database()

    system = InputSystem()
    esper.add_processor(system)

    # Bomb not pressed initially
    assert system.bomb_pressed is False

    # Set bomb input to True
    system.set_input(move_x=0, move_y=0, shoot_x=0, shoot_y=0, bomb_pressed=True)
    assert system.bomb_pressed is True

    # Set bomb input to False
    system.set_input(move_x=0, move_y=0, shoot_x=0, shoot_y=0, bomb_pressed=False)
    assert system.bomb_pressed is False


def test_input_system_bomb_input_defaults_to_false():
    """Test that bomb_pressed defaults to False when not provided."""
    world_name = "test_input_4"
    esper.switch_world(world_name)
    esper.clear_database()

    system = InputSystem()

    # Check initial state
    assert system.bomb_pressed is False


def test_input_system_set_input_with_all_parameters():
    """Test that set_input accepts all parameters including bomb_pressed."""
    world_name = "test_input_5"
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

    # Set all inputs including bomb
    system.set_input(move_x=1, move_y=0, shoot_x=0, shoot_y=-1, bomb_pressed=True)

    # Verify all inputs are stored correctly
    assert system.move_x == 1
    assert system.move_y == 0
    assert system.shoot_x == 0
    assert system.shoot_y == -1
    assert system.bomb_pressed is True
