"""Tests for game engine."""
import pytest
import esper
from src.game.engine import GameEngine
from src.entities.player import create_player


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


def test_game_engine_has_all_systems():
    """Test that GameEngine registers all systems."""
    engine = GameEngine()
    # Check systems are registered
    assert len(engine.world._processors) > 0


def test_game_engine_runs_game_loop():
    """Test that GameEngine can run game loop without crashing."""
    engine = GameEngine()
    # Create player
    player = create_player(engine.world_name, 30.0, 10.0)
    # Run a few frames
    for _ in range(10):
        engine.update(0.016)
    # Should not crash
    assert True


def test_engine_has_enemy_shooting_system():
    """Test game engine registers EnemyShootingSystem."""
    from src.systems.enemy_shooting import EnemyShootingSystem

    engine = GameEngine()

    # Check system is registered
    processors = engine.world._processors
    enemy_shooting_systems = [p for p in processors if isinstance(p, EnemyShootingSystem)]
    assert len(enemy_shooting_systems) == 1


def test_engine_has_invincibility_system():
    """Test game engine registers InvincibilitySystem."""
    from src.systems.invincibility import InvincibilitySystem

    engine = GameEngine()

    # Check system is registered
    processors = engine.world._processors
    invincibility_systems = [p for p in processors if isinstance(p, InvincibilitySystem)]
    assert len(invincibility_systems) == 1


def test_engine_has_homing_system():
    """Test game engine registers HomingSystem."""
    from src.systems.homing import HomingSystem

    engine = GameEngine()

    # Check system is registered
    processors = engine.world._processors
    homing_systems = [p for p in processors if isinstance(p, HomingSystem)]
    assert len(homing_systems) == 1


def test_engine_has_item_pickup_system():
    """Test game engine registers ItemPickupSystem."""
    from src.systems.item_pickup import ItemPickupSystem

    engine = GameEngine()

    # Check system is registered
    processors = engine.world._processors
    item_pickup_systems = [p for p in processors if isinstance(p, ItemPickupSystem)]
    assert len(item_pickup_systems) == 1


def test_engine_connects_render_to_item_pickup():
    """Test that GameEngine connects RenderSystem to ItemPickupSystem."""
    engine = GameEngine()

    # Check RenderSystem has reference to ItemPickupSystem
    assert hasattr(engine.render_system, 'item_pickup_system')
    assert engine.render_system.item_pickup_system is engine.item_pickup_system
