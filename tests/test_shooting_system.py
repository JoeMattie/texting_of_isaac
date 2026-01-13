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
