"""Tests for FloorTransitionSystem."""
import esper
from src.systems.floor_transition import FloorTransitionSystem
from src.components.core import Position
from src.components.game import Player
from src.components.boss import Trapdoor
from src.config import Config


def test_detects_collision_with_trapdoor():
    """Test FloorTransitionSystem detects when player near trapdoor."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))

    # Create trapdoor at same position (within pickup radius)
    trapdoor = esper.create_entity()
    esper.add_component(trapdoor, Trapdoor(next_floor=2))
    esper.add_component(trapdoor, Position(10.0, 10.0))

    # Process system
    system = FloorTransitionSystem()
    system.process()

    # Should detect collision and set pending transition
    assert system.pending_floor_transition is True
    assert system.target_floor == 2
    # Trapdoor should be consumed
    assert not esper.entity_exists(trapdoor)


def test_increments_floor_number():
    """Test floor number is correctly stored on transition."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))

    # Create trapdoor leading to floor 3
    trapdoor = esper.create_entity()
    esper.add_component(trapdoor, Trapdoor(next_floor=3))
    esper.add_component(trapdoor, Position(10.0, 10.0))

    # Process system
    system = FloorTransitionSystem()
    system.process()

    # Verify floor 3 is the target
    assert system.target_floor == 3


def test_victory_condition():
    """Test victory is triggered when next_floor > FINAL_FLOOR."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))

    # Create trapdoor leading beyond final floor (FINAL_FLOOR is 3)
    trapdoor = esper.create_entity()
    esper.add_component(trapdoor, Trapdoor(next_floor=Config.FINAL_FLOOR + 1))
    esper.add_component(trapdoor, Position(10.0, 10.0))

    # Process system
    system = FloorTransitionSystem()
    system.process()

    # Should detect victory
    assert system.victory is True
    assert system.pending_floor_transition is False
    # Trapdoor should still be consumed
    assert not esper.entity_exists(trapdoor)


def test_no_collision_when_far():
    """Test no transition when player far from trapdoor."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))

    # Create trapdoor far away
    trapdoor = esper.create_entity()
    esper.add_component(trapdoor, Trapdoor(next_floor=2))
    esper.add_component(trapdoor, Position(50.0, 50.0))

    # Process system
    system = FloorTransitionSystem()
    system.process()

    # Should not detect collision
    assert system.pending_floor_transition is False
    assert system.target_floor is None
    # Trapdoor should still exist
    assert esper.entity_exists(trapdoor)


def test_collision_radius():
    """Test uses correct collision distance (item pickup radius)."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))

    # Create trapdoor just within pickup radius (0.4)
    # Distance = 0.39 < 0.4
    trapdoor = esper.create_entity()
    esper.add_component(trapdoor, Trapdoor(next_floor=2))
    esper.add_component(trapdoor, Position(10.39, 10.0))

    # Process system
    system = FloorTransitionSystem()
    system.process()

    # Should detect collision
    assert system.pending_floor_transition is True
    assert not esper.entity_exists(trapdoor)


def test_collision_just_outside_radius():
    """Test no collision just outside pickup radius."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))

    # Create trapdoor just outside pickup radius (0.4)
    # Distance = 0.41 > 0.4
    trapdoor = esper.create_entity()
    esper.add_component(trapdoor, Trapdoor(next_floor=2))
    esper.add_component(trapdoor, Position(10.41, 10.0))

    # Process system
    system = FloorTransitionSystem()
    system.process()

    # Should NOT detect collision
    assert system.pending_floor_transition is False
    assert esper.entity_exists(trapdoor)


def test_multiple_trapdoors():
    """Test system handles multiple trapdoors (only first one is consumed)."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))

    # Create two trapdoors at same position
    trapdoor1 = esper.create_entity()
    esper.add_component(trapdoor1, Trapdoor(next_floor=2))
    esper.add_component(trapdoor1, Position(10.0, 10.0))

    trapdoor2 = esper.create_entity()
    esper.add_component(trapdoor2, Trapdoor(next_floor=3))
    esper.add_component(trapdoor2, Position(10.1, 10.0))

    # Process system
    system = FloorTransitionSystem()
    system.process()

    # Should only trigger one transition (breaks after first)
    assert system.pending_floor_transition is True
    # At least one trapdoor should be consumed
    consumed = not esper.entity_exists(trapdoor1) or not esper.entity_exists(trapdoor2)
    assert consumed


def test_no_player_no_transition():
    """Test no transition when no player exists."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create trapdoor without player
    trapdoor = esper.create_entity()
    esper.add_component(trapdoor, Trapdoor(next_floor=2))
    esper.add_component(trapdoor, Position(10.0, 10.0))

    # Process system
    system = FloorTransitionSystem()
    system.process()

    # Should not trigger transition
    assert system.pending_floor_transition is False
    # Trapdoor should still exist
    assert esper.entity_exists(trapdoor)


def test_reset_transition_state():
    """Test transition state can be reset."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player and trapdoor
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))

    trapdoor = esper.create_entity()
    esper.add_component(trapdoor, Trapdoor(next_floor=2))
    esper.add_component(trapdoor, Position(10.0, 10.0))

    # Trigger transition
    system = FloorTransitionSystem()
    system.process()
    assert system.pending_floor_transition is True

    # Reset state
    system.reset_transition()
    assert system.pending_floor_transition is False
    assert system.target_floor is None


def test_victory_on_final_floor_completion():
    """Test victory when completing floor 3 (FINAL_FLOOR)."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))

    # Create trapdoor from floor 3 to floor 4
    trapdoor = esper.create_entity()
    esper.add_component(trapdoor, Trapdoor(next_floor=4))
    esper.add_component(trapdoor, Position(10.0, 10.0))

    # Process system
    system = FloorTransitionSystem()
    system.process()

    # Should trigger victory, not floor transition
    assert system.victory is True
    assert system.pending_floor_transition is False
