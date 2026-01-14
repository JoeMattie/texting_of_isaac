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


def test_creates_spread_bullets():
    """Test enemy creates spread of 3 bullets."""
    esper.switch_world("test_world")
    esper.clear_database()

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(20.0, 10.0))

    # Create enemy with spread pattern as current (index 1)
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, AIBehavior(
        pattern_cooldowns={"aimed": 1.0, "spread": 0.0},  # spread ready
        pattern_index=1  # Points to "spread" pattern
    ))

    # Process shooting
    system = EnemyShootingSystem()
    system.dt = 0.1
    esper.add_processor(system)
    esper.process()

    # Should create 3 projectiles
    projectiles = [e for e, (proj,) in esper.get_components(Projectile)]
    assert len(projectiles) == 3

    # Verify angles are spread out
    velocities = [esper.component_for_entity(p, Velocity) for p in projectiles]
    angles = [math.atan2(v.dy, v.dx) for v in velocities]

    # Angles should be different
    assert angles[0] != angles[1]
    assert angles[1] != angles[2]

    # Should be spread around base direction
    assert min(angles) < 0
    assert max(angles) > 0


def test_creates_ring_bullets():
    """Test enemy creates ring of 8 bullets radiating outward."""
    esper.switch_world("test_world")
    esper.clear_database()

    # Create player (position doesn't matter for ring)
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(20.0, 10.0))

    # Create orbiter with ring pattern ready (index 1)
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("orbiter"))
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, AIBehavior(
        pattern_cooldowns={"aimed": 1.5, "ring": 0.0},
        pattern_index=1  # Ring pattern
    ))

    # Process shooting
    system = EnemyShootingSystem()
    system.dt = 0.1
    esper.add_processor(system)
    esper.process()

    # Should create 8 projectiles
    projectiles = [e for e, (proj,) in esper.get_components(Projectile)]
    assert len(projectiles) == 8

    # Verify bullets are evenly distributed (45° apart)
    velocities = [esper.component_for_entity(p, Velocity) for p in projectiles]
    angles = sorted([math.atan2(v.dy, v.dx) for v in velocities])

    # Check approximate 45° spacing (π/4 radians)
    for i in range(1, len(angles)):
        angle_diff = angles[i] - angles[i-1]
        assert angle_diff == pytest.approx(math.pi / 4, abs=0.1)


def test_pattern_cycles_through_list():
    """Test enemy cycles through patterns sequentially."""
    esper.switch_world("test_world")
    esper.clear_database()

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(20.0, 10.0))

    # Shooter has 2 patterns: aimed, spread
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, AIBehavior(
        pattern_cooldowns={"aimed": 0.0, "spread": 0.0},
        pattern_index=0
    ))

    system = EnemyShootingSystem()
    system.dt = 0.1
    esper.add_processor(system)

    # First shot: pattern_index = 0 (aimed), should shoot 1 bullet
    esper.process()
    ai = esper.component_for_entity(enemy, AIBehavior)
    assert ai.pattern_index == 1  # Cycled to next

    # Clear projectiles
    for proj_id, (proj,) in list(esper.get_components(Projectile)):
        esper.delete_entity(proj_id)

    # Wait for cooldown and shoot again
    ai.pattern_cooldowns["spread"] = 0.0
    esper.process()

    # Should cycle back to 0
    assert ai.pattern_index == 0


def test_single_pattern_stays_at_zero():
    """Test enemy with one pattern keeps pattern_index at 0."""
    esper.switch_world("test_world")
    esper.clear_database()

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(20.0, 10.0))

    # Tank has 1 pattern
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("tank"))
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, AIBehavior(
        pattern_cooldowns={"shockwave": 0.0},
        pattern_index=0
    ))

    system = EnemyShootingSystem()
    system.dt = 0.1
    esper.add_processor(system)
    esper.process()

    ai = esper.component_for_entity(enemy, AIBehavior)
    # Should cycle: (0 + 1) % 1 = 0
    assert ai.pattern_index == 0


def test_respects_cooldown_timer():
    """Test enemy doesn't shoot until cooldown expires."""
    esper.switch_world("test_world")
    esper.clear_database()

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(20.0, 10.0))

    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, AIBehavior(
        pattern_cooldowns={"aimed": 2.0, "spread": 3.0},  # Not ready
        pattern_index=0
    ))

    system = EnemyShootingSystem()
    system.dt = 0.5
    esper.add_processor(system)

    # Process 3 times (1.5 seconds) - cooldown still > 0
    for _ in range(3):
        esper.process()

    # No projectiles should be created (cooldown still > 0)
    projectiles = list(esper.get_components(Projectile))
    assert len(projectiles) == 0
