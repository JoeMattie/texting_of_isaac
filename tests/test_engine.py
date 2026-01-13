"""Tests for game engine."""
import pytest
import esper
from src.game.engine import GameEngine


def test_game_engine_creates_world():
    """Test that GameEngine initializes with an ECS world."""
    engine = GameEngine()
    # Esper module is exposed as world interface
    assert engine.world is not None
    assert hasattr(engine.world, 'process')
    assert hasattr(engine.world, 'create_entity')


def test_game_engine_tracks_delta_time():
    """Test that GameEngine can update with delta time."""
    engine = GameEngine()
    engine.update(0.016)  # ~60 FPS frame
    assert engine.delta_time == 0.016


def test_game_engine_can_stop():
    """Test that GameEngine can be stopped."""
    engine = GameEngine()
    engine.stop()
    assert engine.running is False
