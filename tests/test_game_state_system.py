"""Tests for the GameStateSystem."""
import pytest
import esper
from src.systems.game_state import GameStateSystem
from src.systems.floor_transition import FloorTransitionSystem
from src.components.core import Position, Health
from src.components.game import Player
from src.game.state import GameState


@pytest.fixture
def game_world():
    """Create a test world."""
    world_name = "test_game_state_world"
    esper.switch_world(world_name)
    yield world_name
    # Cleanup handled by conftest.py autouse fixture


@pytest.fixture
def floor_transition_system(game_world):
    """Create a FloorTransitionSystem for testing."""
    esper.switch_world(game_world)
    return FloorTransitionSystem()


@pytest.fixture
def game_state_system(game_world, floor_transition_system):
    """Create a GameStateSystem for testing."""
    esper.switch_world(game_world)
    return GameStateSystem(floor_transition_system)


def test_initial_state(game_state_system):
    """Test that system starts in PLAYING state."""
    assert game_state_system.current_state == GameState.PLAYING


def test_player_death_triggers_game_over(game_world, game_state_system):
    """Test that player death (HP <= 0) transitions to GAME_OVER state."""
    esper.switch_world(game_world)

    # Create player with low health
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(current=0, max_hp=6))

    # Process the system
    game_state_system.process()

    # Should transition to GAME_OVER
    assert game_state_system.current_state == GameState.GAME_OVER


def test_player_with_health_remains_playing(game_world, game_state_system):
    """Test that player with HP > 0 stays in PLAYING state."""
    esper.switch_world(game_world)

    # Create player with health
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(current=3, max_hp=6))

    # Process the system
    game_state_system.process()

    # Should remain in PLAYING
    assert game_state_system.current_state == GameState.PLAYING


def test_victory_flag_triggers_victory_state(game_world, game_state_system, floor_transition_system):
    """Test that victory flag set in FloorTransitionSystem triggers VICTORY state."""
    esper.switch_world(game_world)

    # Set victory flag
    floor_transition_system.victory = True

    # Process the system
    game_state_system.process()

    # Should transition to VICTORY
    assert game_state_system.current_state == GameState.VICTORY


def test_state_persistence_game_over(game_world, game_state_system):
    """Test that GAME_OVER state persists and doesn't process further."""
    esper.switch_world(game_world)

    # Create dead player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(current=0, max_hp=6))

    # First process - should go to GAME_OVER
    game_state_system.process()
    assert game_state_system.current_state == GameState.GAME_OVER

    # Heal player (shouldn't matter, state is terminal)
    health = esper.component_for_entity(player, Health)
    health.current = 6

    # Second process - should stay in GAME_OVER
    game_state_system.process()
    assert game_state_system.current_state == GameState.GAME_OVER


def test_state_persistence_victory(game_world, game_state_system, floor_transition_system):
    """Test that VICTORY state persists and doesn't process further."""
    esper.switch_world(game_world)

    # Set victory flag
    floor_transition_system.victory = True

    # First process - should go to VICTORY
    game_state_system.process()
    assert game_state_system.current_state == GameState.VICTORY

    # Clear victory flag (shouldn't matter, state is terminal)
    floor_transition_system.victory = False

    # Second process - should stay in VICTORY
    game_state_system.process()
    assert game_state_system.current_state == GameState.VICTORY


def test_victory_screen_text(game_state_system):
    """Test that VICTORY state returns correct screen text."""
    # Set state to VICTORY
    game_state_system.current_state = GameState.VICTORY

    text = game_state_system.get_state_screen_text()

    # Should contain victory message
    assert "VICTORY" in text
    assert "You defeated the final boss!" in text
    assert "Floors completed: 3" in text
    assert "Press R to restart" in text
    assert "Press Q to quit" in text


def test_game_over_screen_text(game_state_system):
    """Test that GAME_OVER state returns correct screen text."""
    # Set state to GAME_OVER
    game_state_system.current_state = GameState.GAME_OVER

    text = game_state_system.get_state_screen_text()

    # Should contain game over message
    assert "GAME OVER" in text
    assert "You died!" in text
    assert "Press R to restart" in text
    assert "Press Q to quit" in text


def test_playing_screen_text(game_state_system):
    """Test that PLAYING state returns empty string."""
    # State is PLAYING by default
    assert game_state_system.current_state == GameState.PLAYING

    text = game_state_system.get_state_screen_text()

    # Should be empty
    assert text == ""


def test_no_player_no_game_over(game_world, game_state_system):
    """Test that missing player doesn't cause game over."""
    esper.switch_world(game_world)

    # No player entity created

    # Process the system
    game_state_system.process()

    # Should remain in PLAYING (no player means no death)
    assert game_state_system.current_state == GameState.PLAYING


def test_victory_takes_precedence_over_death(game_world, game_state_system, floor_transition_system):
    """Test that victory is checked before death condition."""
    esper.switch_world(game_world)

    # Create dead player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(current=0, max_hp=6))

    # Set victory flag
    floor_transition_system.victory = True

    # Process the system
    game_state_system.process()

    # Should transition to VICTORY (not GAME_OVER)
    assert game_state_system.current_state == GameState.VICTORY
