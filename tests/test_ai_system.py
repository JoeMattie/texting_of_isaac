import pytest
import esper
from src.systems.ai import AISystem
from src.entities.enemies import create_enemy
from src.entities.player import create_player
from src.components.core import Position, Velocity
from src.components.game import Enemy, Player, AIBehavior


def test_ai_system_chaser_moves_toward_player():
    world = "test_ai_chaser"
    esper.switch_world(world)
    esper.clear_database()

    system = AISystem()
    system.dt = 0.1
    esper.add_processor(system)

    # Create player
    player = create_player(world, 30.0, 10.0)

    # Create chaser to the left of player
    enemy = create_enemy(world, "chaser", 20.0, 10.0)

    esper.process()

    # Enemy velocity should point toward player (right)
    vel = esper.component_for_entity(enemy, Velocity)
    assert vel.dx > 0


def test_ai_system_shooter_stays_stationary():
    world = "test_ai_shooter"
    esper.switch_world(world)
    esper.clear_database()

    system = AISystem()
    system.dt = 0.1
    esper.add_processor(system)

    player = create_player(world, 30.0, 10.0)
    shooter = create_enemy(world, "shooter", 20.0, 10.0)

    esper.process()

    vel = esper.component_for_entity(shooter, Velocity)
    # Shooter should move slowly or not at all
    assert abs(vel.dx) < 2.0


def test_ai_system_decrements_pattern_cooldowns():
    """Test AISystem decrements pattern cooldowns each frame."""
    esper.switch_world("test_world")
    esper.clear_database()

    # Create enemy with patterns
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, Velocity(0.0, 0.0))
    esper.add_component(enemy, AIBehavior(
        pattern_cooldowns={"aimed": 2.0, "spread": 3.0},
        pattern_index=0
    ))

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(20.0, 10.0))

    # Process AI system
    ai_system = AISystem()
    ai_system.dt = 0.5
    esper.add_processor(ai_system)
    esper.process()

    # Check cooldowns decreased
    ai = esper.component_for_entity(enemy, AIBehavior)
    assert ai.pattern_cooldowns["aimed"] == pytest.approx(1.5)
    assert ai.pattern_cooldowns["spread"] == pytest.approx(2.5)
