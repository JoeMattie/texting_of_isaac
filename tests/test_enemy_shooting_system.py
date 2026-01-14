"""Tests for enemy shooting system."""
import esper
import pytest
import math
from src.systems.enemy_shooting import EnemyShootingSystem
from src.components.core import Position, Velocity
from src.components.game import Enemy, Player, AIBehavior
from src.components.combat import Projectile


def test_enemy_shooting_system_exists():
    """Test EnemyShootingSystem can be instantiated."""
    system = EnemyShootingSystem()
    assert system is not None
    assert hasattr(system, 'dt')


def test_creates_single_aimed_bullet():
    """Test enemy creates single bullet aimed at player."""
    esper.switch_world("test_world")
    esper.clear_database()

    # Create player at (20, 10)
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(20.0, 10.0))

    # Create shooter enemy at (10, 10) with pattern ready to fire
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, AIBehavior(
        pattern_cooldowns={"aimed": 0.0, "spread": 2.0},  # aimed ready
        pattern_index=0
    ))

    # Process shooting system
    system = EnemyShootingSystem()
    system.dt = 0.1
    esper.add_processor(system)
    esper.process()

    # Find created projectile
    projectiles = [e for e, (proj,) in esper.get_components(Projectile)]
    assert len(projectiles) == 1

    # Verify projectile properties
    proj_id = projectiles[0]
    projectile = esper.component_for_entity(proj_id, Projectile)
    pos = esper.component_for_entity(proj_id, Position)
    vel = esper.component_for_entity(proj_id, Velocity)

    from src.components.core import Sprite
    sprite = esper.component_for_entity(proj_id, Sprite)

    assert projectile.owner == enemy
    assert pos.x == pytest.approx(10.0)
    assert pos.y == pytest.approx(10.0)
    assert vel.dx > 0  # Moving right toward player
    assert vel.dy == pytest.approx(0.0)  # Same y-coordinate
    assert sprite.char == '*'
    assert sprite.color == 'yellow'
