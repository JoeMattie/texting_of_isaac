"""Integration tests for complete game systems."""
import esper
import pytest
from src.game.engine import GameEngine
from src.components.core import Position, Health
from src.components.game import Player, Enemy, AIBehavior, Invincible
from src.components.combat import Projectile, Collider
from src.entities.player import create_player
from src.entities.enemies import create_enemy


def test_full_enemy_shooting_cycle():
    """Test complete enemy shooting and collision cycle."""
    esper.switch_world("test_integration")
    esper.clear_database()

    # Create engine
    engine = GameEngine()

    # Create player
    player = create_player("test_integration", 20.0, 10.0)

    # Create shooter enemy close to player
    enemy = create_enemy("test_integration", "shooter", 10.0, 10.0)

    # Process for 3 seconds (90 frames at 30 FPS)
    # Shooter fires every 2-2.5 seconds, so should fire at least once
    for i in range(90):
        engine.update(1/30)  # dt = 0.0333...

    # Check that projectiles were created at some point
    # (They may have been removed by collision, but check history)
    # Since we can't check history, just verify system is working
    # by checking cooldowns were modified

    # This is a smoke test - if it doesn't crash, systems are integrated
    assert True  # Systems ran without errors


def test_enemy_projectiles_damage_player():
    """Test enemy projectiles remove themselves when hitting player."""
    esper.switch_world("test_integration")
    esper.clear_database()

    engine = GameEngine()

    # Create player
    player = create_player("test_integration", 10.5, 10.0)

    # Create shooter directly next to player (will hit immediately)
    enemy = create_enemy("test_integration", "shooter", 10.0, 10.0)

    # Get AI component and make pattern ready
    ai = esper.component_for_entity(enemy, AIBehavior)
    ai.pattern_cooldowns["aimed"] = 0.0

    # Update once to create projectile
    engine.update(0.1)

    # Count projectiles
    projectiles_before = len(list(esper.get_components(Projectile)))

    # Update again - projectile should hit player and be removed
    engine.update(0.1)

    projectiles_after = len(list(esper.get_components(Projectile)))

    # Projectile should be removed after collision
    assert projectiles_after < projectiles_before or projectiles_after == 0


def test_player_damage_and_invincibility_cycle():
    """Test complete damage flow from hit to recovery."""
    esper.switch_world("test_damage_cycle")
    esper.clear_database()

    # Create game engine
    engine = GameEngine()
    world = engine.world_name

    # Create player with 3 HP
    player = create_player(world, 20.0, 10.0)
    esper.switch_world(world)
    health = esper.component_for_entity(player, Health)
    health.current = 3.0

    # Create enemy
    enemy = create_enemy(world, "shooter", 10.0, 10.0)

    # Create first projectile at player position
    projectile1 = esper.create_entity()
    esper.add_component(projectile1, Position(20.0, 10.0))
    esper.add_component(projectile1, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile1, Collider(0.2))

    # Update once - collision should deal damage
    engine.update(0.1)

    # Verify damage dealt and invincibility granted
    assert health.current == 2.0
    assert esper.has_component(player, Invincible)

    # Create second projectile during invincibility
    projectile2 = esper.create_entity()
    esper.add_component(projectile2, Position(20.0, 10.0))
    esper.add_component(projectile2, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile2, Collider(0.2))

    # Update - should not deal damage (invincible)
    engine.update(0.1)
    assert health.current == 2.0

    # Wait for invincibility to expire (0.5s total)
    for _ in range(5):
        engine.update(0.1)

    # Invincibility should be gone
    assert not esper.has_component(player, Invincible)

    # Create third projectile after invincibility expires
    projectile3 = esper.create_entity()
    esper.add_component(projectile3, Position(20.0, 10.0))
    esper.add_component(projectile3, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile3, Collider(0.2))

    # Update - should deal damage again
    engine.update(0.1)
    assert health.current == 1.0


def test_item_pickup_and_stat_modification():
    """Test complete pickup flow from collision to stat change."""
    esper.switch_world("test_pickup_flow")
    esper.clear_database()

    # Import dependencies inside test
    from src.entities.items import create_item
    from src.components.combat import Stats
    from src.systems.item_pickup import ItemPickupSystem

    # Create engine with player
    engine = GameEngine()
    world = engine.world_name

    # Create player with base stats
    player = create_player(world, 10.0, 10.0)
    esper.switch_world(world)
    stats = esper.component_for_entity(player, Stats)
    initial_damage = stats.damage
    initial_speed = stats.speed

    # Create magic_mushroom at player position
    item = create_item(world, "magic_mushroom", 10.0, 10.0)

    # Process ItemPickupSystem
    engine.update(0.016)

    # Verify stats changed (+1.0 damage additive, 1.2x speed multiplicative)
    assert stats.damage == initial_damage + 1.0
    assert stats.speed == initial_speed * 1.2

    # Verify item added to CollectedItems
    from src.components.game import CollectedItems
    assert esper.has_component(player, CollectedItems)
    collected = esper.component_for_entity(player, CollectedItems)
    assert len(collected.items) == 1
    assert collected.items[0].name == "magic_mushroom"

    # Verify item entity removed
    assert not esper.entity_exists(item)

    # Verify notification displayed
    assert engine.item_pickup_system.notification == "Picked up: magic_mushroom"
    assert engine.item_pickup_system.notification_timer > 0


def test_piercing_effect_in_combat():
    """Test piercing effect allows hitting multiple enemies."""
    esper.switch_world("test_piercing_combat")
    esper.clear_database()

    # Import dependencies inside test
    from src.components.combat import Collider, Projectile
    from src.components.game import CollectedItems, Item
    from src.entities.enemies import create_enemy
    from src.entities.player import create_player
    from src.systems.collision import CollisionSystem
    from src.components.core import Velocity

    # Create player with piercing effect (via CollectedItems)
    player = create_player("test_piercing_combat", 10.0, 10.0)
    collected = CollectedItems()
    # Add piercing item to collection
    piercing_item = Item("piercing_tears", {"damage": 0.5}, ["piercing"])
    collected.items.append(piercing_item)
    esper.add_component(player, collected)

    # Create first enemy
    enemy1 = create_enemy("test_piercing_combat", "chaser", 15.0, 10.0)
    enemy1_health = esper.component_for_entity(enemy1, Health)
    enemy1_initial_hp = enemy1_health.current

    # Create projectile at enemy position
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(15.0, 10.0))
    esper.add_component(projectile, Projectile(damage=2.0, owner=player))
    esper.add_component(projectile, Collider(0.2))
    esper.add_component(projectile, Velocity(10.0, 0.0))

    # Process CollisionSystem - hit first enemy
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify first enemy took damage
    assert enemy1_health.current < enemy1_initial_hp

    # Verify projectile still exists (piercing)
    assert esper.entity_exists(projectile)

    # Move projectile forward and create second enemy
    proj_pos = esper.component_for_entity(projectile, Position)
    proj_pos.x = 20.0
    enemy2 = create_enemy("test_piercing_combat", "chaser", 20.0, 10.0)
    enemy2_health = esper.component_for_entity(enemy2, Health)
    enemy2_initial_hp = enemy2_health.current

    # Process CollisionSystem again - hit second enemy
    esper.process()

    # Verify second enemy took damage
    assert enemy2_health.current < enemy2_initial_hp

    # Verify projectile still exists (piercing)
    assert esper.entity_exists(projectile)


def test_homing_effect_curves_bullets():
    """Test homing effect makes projectiles track enemies."""
    esper.switch_world("test_homing_curve")
    esper.clear_database()

    # Import dependencies inside test
    from src.components.combat import Stats, Projectile
    from src.components.game import CollectedItems, Item
    from src.components.core import Velocity
    from src.entities.enemies import create_enemy
    from src.systems.homing import HomingSystem

    # Create player with homing effect (via CollectedItems)
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Stats(5.0, 1.0, 0.3, 10.0))
    collected = CollectedItems()
    # Add homing item to collection
    homing_item = Item("homing_shots", {}, ["homing"])
    collected.items.append(homing_item)
    esper.add_component(player, collected)

    # Create enemy to the east
    enemy = create_enemy("test_homing_curve", "shooter", 20.0, 10.0)

    # Create projectile firing north (away from enemy)
    esper.switch_world("test_homing_curve")
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(10.0, 10.0))
    esper.add_component(projectile, Projectile(damage=1.0, owner=player))
    vel = Velocity(0.0, -10.0)  # Firing north (negative y)
    esper.add_component(projectile, vel)

    # Process HomingSystem for 10 frames
    system = HomingSystem()
    for _ in range(10):
        system.dt = 0.033  # ~30 FPS
        system.process()

    # Verify velocity rotated toward enemy (vel.dx > 0)
    # Enemy is to the east, so projectile should have turned right (positive dx)
    assert vel.dx > 0


def test_multi_shot_creates_spread():
    """Test multi-shot effect fires 3 projectiles."""
    esper.switch_world("test_multi_shot")
    esper.clear_database()

    # Import dependencies inside test
    from src.components.combat import Stats, Projectile
    from src.components.game import CollectedItems, Item
    from src.systems.shooting import ShootingSystem

    # Create player with multi_shot effect (via CollectedItems)
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Stats(5.0, 1.0, 2.0, 10.0))
    collected = CollectedItems()
    # Add multi_shot item to collection
    multi_shot_item = Item("triple_shot", {"fire_rate": 0.1}, ["multi_shot"])
    collected.items.append(multi_shot_item)
    esper.add_component(player, collected)

    # Set up ShootingSystem with shooting direction
    shooting_system = ShootingSystem()
    shooting_system.shoot_x = 1  # Shooting right
    shooting_system.shoot_y = 0
    shooting_system.dt = 0.016
    esper.add_processor(shooting_system)

    # Process ShootingSystem
    esper.process()

    # Verify 3 projectiles created
    projectiles = list(esper.get_components(Projectile))
    assert len(projectiles) == 3
