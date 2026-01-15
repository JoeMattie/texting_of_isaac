import pytest
import esper
from src.systems.shooting import ShootingSystem
from src.systems.input import InputSystem
from src.components.core import Position, Velocity
from src.components.combat import Stats, Projectile, Collider
from src.components.game import Player


def test_shooting_system_creates_projectile():
    world = "test_shooting_creates"
    esper.switch_world(world)
    esper.clear_database()

    shooting = ShootingSystem()
    esper.add_processor(shooting)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(30.0, 10.0))
    esper.add_component(player, Stats(speed=5.0, damage=2.0, fire_rate=2.0, shot_speed=8.0))

    # Trigger shot
    shooting.shoot_x = 1
    shooting.shoot_y = 0
    shooting.dt = 1.0
    esper.process()

    # Check projectile created
    projectiles = [e for e, (proj,) in esper.get_components(Projectile)]
    assert len(projectiles) > 0


def test_shooting_system_respects_fire_rate():
    world = "test_shooting_fire_rate"
    esper.switch_world(world)
    esper.clear_database()

    shooting = ShootingSystem()
    esper.add_processor(shooting)

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(30.0, 10.0))
    esper.add_component(player, Stats(speed=5.0, damage=2.0, fire_rate=2.0, shot_speed=8.0))

    # Fire rate 2.0 = shoot every 0.5 seconds
    shooting.shoot_x = 1
    shooting.shoot_y = 0
    shooting.dt = 0.1

    # Process multiple times
    for _ in range(3):
        esper.process()

    # Should only create 1 projectile (not enough time passed)
    projectiles = [e for e, (proj,) in esper.get_components(Projectile)]
    assert len(projectiles) == 1


def test_multi_shot_fires_three_projectiles():
    """Test multi_shot effect creates 3 projectiles in spread pattern."""
    import math
    from src.components.game import CollectedItems, Item

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    shooting = ShootingSystem()
    esper.add_processor(shooting)

    # Create player with multi_shot effect
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(30.0, 20.0))
    stats = Stats(speed=5.0, damage=2.0, fire_rate=2.0, shot_speed=8.0)
    esper.add_component(player, stats)

    # Add multi_shot item
    collected = CollectedItems()
    multi_shot_item = Item("triple_shot", {}, ["multi_shot"])
    collected.items.append(multi_shot_item)
    esper.add_component(player, collected)

    # Set firing input
    shooting.shoot_x = 1.0
    shooting.shoot_y = 0.0
    shooting.dt = 1.0  # Enough time to reset cooldown
    esper.process()

    # Count projectiles
    projectiles = list(esper.get_components(Projectile, Velocity))
    assert len(projectiles) == 3

    # Check spread pattern
    velocities = [vel for _, (proj, vel) in projectiles]

    # Center shot should be (1, 0) direction
    # Left should be rotated -15 degrees
    # Right should be rotated +15 degrees
    angles = [math.atan2(vel.dy, vel.dx) for vel in velocities]
    angles.sort()

    # Verify spread (angles should be approximately -15°, 0°, +15° in radians)
    assert abs(angles[0] - math.radians(-15)) < 0.01
    assert abs(angles[1]) < 0.01  # Center
    assert abs(angles[2] - math.radians(15)) < 0.01


def test_multi_shot_each_projectile_full_damage():
    """Test each projectile in multi-shot has full damage."""
    from src.components.game import CollectedItems, Item

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    shooting = ShootingSystem()
    esper.add_processor(shooting)

    # Create player with multi_shot
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(30.0, 20.0))
    stats = Stats(speed=5.0, damage=2.0, fire_rate=2.0, shot_speed=8.0)
    esper.add_component(player, stats)

    collected = CollectedItems()
    collected.items.append(Item("triple_shot", {}, ["multi_shot"]))
    esper.add_component(player, collected)

    # Set firing input
    shooting.shoot_x = 1.0
    shooting.shoot_y = 0.0
    shooting.dt = 1.0
    esper.process()

    # Check all projectiles have full damage
    for _, (proj,) in esper.get_components(Projectile):
        assert proj.damage == stats.damage


def test_normal_shot_without_multi_shot():
    """Test normal firing creates single projectile without multi_shot."""
    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    shooting = ShootingSystem()
    esper.add_processor(shooting)

    # Create player without multi_shot
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(30.0, 20.0))
    esper.add_component(player, Stats(speed=5.0, damage=2.0, fire_rate=2.0, shot_speed=8.0))

    # Set firing input
    shooting.shoot_x = 1.0
    shooting.shoot_y = 0.0
    shooting.dt = 1.0
    esper.process()

    # Should only create 1 projectile
    projectiles = list(esper.get_components(Projectile))
    assert len(projectiles) == 1
