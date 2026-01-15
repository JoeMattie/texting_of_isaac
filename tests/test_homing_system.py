import pytest
import esper
import math
from src.systems.homing import HomingSystem
from src.components.core import Position, Velocity
from src.components.combat import Projectile, Stats
from src.components.game import Player, Enemy, CollectedItems, Item
from src.config import Config


def test_homing_system_rotates_toward_target():
    """Test projectile velocity rotates toward nearest enemy."""
    world = "test_homing_rotates"
    esper.switch_world(world)
    esper.clear_database()

    homing_system = HomingSystem()
    esper.add_processor(homing_system)

    # Create player with homing effect
    player = esper.create_entity()
    esper.add_component(player, Player())
    collected = CollectedItems()
    collected.items.append(Item("homing_item", {}, ["homing"]))
    esper.add_component(player, collected)

    # Create projectile firing north (dy < 0)
    proj = esper.create_entity()
    esper.add_component(proj, Projectile(owner=player, damage=1.0))
    esper.add_component(proj, Position(10.0, 10.0))
    esper.add_component(proj, Velocity(0.0, -5.0))  # Moving north

    # Create enemy to the east
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("basic"))
    esper.add_component(enemy, Position(20.0, 10.0))  # To the right

    # Process homing system
    homing_system.dt = 1.0 / 60.0  # One frame at 60fps
    esper.process()

    # Verify projectile velocity rotated eastward (dx should increase)
    vel = esper.component_for_entity(proj, Velocity)
    assert vel.dx > 0, "Projectile should turn toward enemy to the east"


def test_homing_respects_turn_rate():
    """Test projectile doesn't instantly lock on."""
    world = "test_homing_turn_rate"
    esper.switch_world(world)
    esper.clear_database()

    homing_system = HomingSystem()
    esper.add_processor(homing_system)

    # Create player with homing effect
    player = esper.create_entity()
    esper.add_component(player, Player())
    collected = CollectedItems()
    collected.items.append(Item("homing_item", {}, ["homing"]))
    esper.add_component(player, collected)

    # Create projectile firing north
    proj = esper.create_entity()
    esper.add_component(proj, Projectile(owner=player, damage=1.0))
    esper.add_component(proj, Position(10.0, 10.0))
    initial_velocity = Velocity(0.0, -5.0)  # Moving north
    esper.add_component(proj, initial_velocity)

    # Create enemy 180 degrees away (south)
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("basic"))
    esper.add_component(enemy, Position(10.0, 20.0))  # Directly south

    # Calculate initial angle
    initial_angle = math.atan2(initial_velocity.dy, initial_velocity.dx)

    # Process one frame
    homing_system.dt = 1.0 / 60.0
    esper.process()

    # Get new velocity and angle
    vel = esper.component_for_entity(proj, Velocity)
    new_angle = math.atan2(vel.dy, vel.dx)

    # Calculate actual rotation
    angle_diff = new_angle - initial_angle
    # Normalize to [-pi, pi]
    while angle_diff > math.pi:
        angle_diff -= 2 * math.pi
    while angle_diff < -math.pi:
        angle_diff += 2 * math.pi
    actual_rotation = abs(angle_diff)

    # Should rotate by at most HOMING_TURN_RATE * dt
    max_rotation = math.radians(Config.HOMING_TURN_RATE * homing_system.dt)
    assert actual_rotation <= max_rotation + 0.001, "Rotation should respect turn rate limit"
    assert actual_rotation > 0, "Should rotate toward target"


def test_homing_only_affects_player_projectiles():
    """Test enemy projectiles are not affected by homing."""
    world = "test_homing_player_only"
    esper.switch_world(world)
    esper.clear_database()

    homing_system = HomingSystem()
    esper.add_processor(homing_system)

    # Create player with homing effect
    player = esper.create_entity()
    esper.add_component(player, Player())
    collected = CollectedItems()
    collected.items.append(Item("homing_item", {}, ["homing"]))
    esper.add_component(player, collected)

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("basic"))
    esper.add_component(enemy, Position(5.0, 10.0))

    # Create enemy projectile
    enemy_proj = esper.create_entity()
    esper.add_component(enemy_proj, Projectile(owner=enemy, damage=1.0))
    esper.add_component(enemy_proj, Position(10.0, 10.0))
    initial_vel = Velocity(1.0, 0.0)
    esper.add_component(enemy_proj, initial_vel)

    # Process homing system
    homing_system.dt = 1.0 / 60.0
    esper.process()

    # Verify enemy projectile velocity unchanged
    vel = esper.component_for_entity(enemy_proj, Velocity)
    assert vel.dx == initial_vel.dx
    assert vel.dy == initial_vel.dy


def test_homing_without_effect_does_nothing():
    """Test no homing without effect."""
    world = "test_homing_no_effect"
    esper.switch_world(world)
    esper.clear_database()

    homing_system = HomingSystem()
    esper.add_processor(homing_system)

    # Create player WITHOUT homing effect
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, CollectedItems())  # Empty items

    # Create projectile
    proj = esper.create_entity()
    esper.add_component(proj, Projectile(owner=player, damage=1.0))
    esper.add_component(proj, Position(10.0, 10.0))
    initial_vel = Velocity(0.0, -5.0)
    esper.add_component(proj, initial_vel)

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("basic"))
    esper.add_component(enemy, Position(20.0, 10.0))

    # Process homing system
    homing_system.dt = 1.0 / 60.0
    esper.process()

    # Verify projectile velocity unchanged
    vel = esper.component_for_entity(proj, Velocity)
    assert vel.dx == initial_vel.dx
    assert vel.dy == initial_vel.dy


def test_homing_finds_nearest_enemy():
    """Test homing targets closest enemy."""
    world = "test_homing_nearest"
    esper.switch_world(world)
    esper.clear_database()

    homing_system = HomingSystem()
    esper.add_processor(homing_system)

    # Create player with homing effect
    player = esper.create_entity()
    esper.add_component(player, Player())
    collected = CollectedItems()
    collected.items.append(Item("homing_item", {}, ["homing"]))
    esper.add_component(player, collected)

    # Create projectile at origin facing north
    proj = esper.create_entity()
    esper.add_component(proj, Projectile(owner=player, damage=1.0))
    esper.add_component(proj, Position(10.0, 10.0))
    esper.add_component(proj, Velocity(0.0, -5.0))  # Moving north

    # Create far enemy to the west
    far_enemy = esper.create_entity()
    esper.add_component(far_enemy, Enemy("basic"))
    esper.add_component(far_enemy, Position(0.0, 10.0))  # Distance 10

    # Create near enemy to the east
    near_enemy = esper.create_entity()
    esper.add_component(near_enemy, Enemy("basic"))
    esper.add_component(near_enemy, Position(13.0, 10.0))  # Distance 3

    # Process homing system
    homing_system.dt = 1.0 / 60.0
    esper.process()

    # Verify projectile turned toward near enemy (east)
    # Should have positive dx (turning right toward east)
    vel = esper.component_for_entity(proj, Velocity)
    assert vel.dx > 0, "Projectile should turn toward nearest enemy to the east"
