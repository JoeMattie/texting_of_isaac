import pytest
import esper
from src.systems.ai import AISystem
from src.entities.enemies import create_enemy
from src.entities.player import create_player
from src.components.core import Position, Velocity


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
