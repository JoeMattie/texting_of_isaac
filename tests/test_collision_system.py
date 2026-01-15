import pytest
import esper
from src.systems.collision import CollisionSystem
from src.components.core import Position, Health
from src.components.combat import Collider, Projectile
from src.components.game import Player, Enemy, Dead
from src.config import Config


def test_collision_system_detects_overlap():
    world = "test_collision_overlap"
    esper.switch_world(world)
    esper.clear_database()

    system = CollisionSystem()

    # Two entities at same position
    e1 = esper.create_entity()
    esper.add_component(e1, Position(10.0, 10.0))
    esper.add_component(e1, Collider(0.5))

    e2 = esper.create_entity()
    esper.add_component(e2, Position(10.0, 10.0))
    esper.add_component(e2, Collider(0.5))

    assert system._check_collision(e1, e2, world) is True


def test_collision_system_no_overlap():
    world = "test_collision_no_overlap"
    esper.switch_world(world)
    esper.clear_database()

    system = CollisionSystem()

    # Entities far apart
    e1 = esper.create_entity()
    esper.add_component(e1, Position(10.0, 10.0))
    esper.add_component(e1, Collider(0.5))

    e2 = esper.create_entity()
    esper.add_component(e2, Position(20.0, 20.0))
    esper.add_component(e2, Collider(0.5))

    assert system._check_collision(e1, e2, world) is False


def test_projectile_damages_enemy():
    world = "test_collision_damage"
    esper.switch_world(world)
    esper.clear_database()

    system = CollisionSystem()
    esper.add_processor(system)

    # Create player projectile
    proj = esper.create_entity()
    esper.add_component(proj, Position(10.0, 10.0))
    esper.add_component(proj, Collider(0.2))
    esper.add_component(proj, Projectile(damage=2.0, owner=999))

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, Collider(0.5))
    esper.add_component(enemy, Health(5, 5))
    esper.add_component(enemy, Enemy("test"))

    esper.process()

    # Enemy should take damage
    health = esper.component_for_entity(enemy, Health)
    assert health.current == 3  # 5 - 2 damage


def test_enemy_projectile_hits_player():
    """Test enemy projectiles collide with player."""
    esper.switch_world("test_world")
    esper.clear_database()

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(3, 6))
    esper.add_component(player, Collider(0.5))

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))
    esper.add_component(enemy, Position(5.0, 10.0))

    # Create enemy projectile at player position
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(10.0, 10.0))
    esper.add_component(projectile, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile, Collider(0.2))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Projectile should be removed
    assert not esper.entity_exists(projectile)


def test_enemy_projectile_ignores_enemies():
    """Test enemy projectiles don't collide with other enemies."""
    esper.switch_world("test_world")
    esper.clear_database()

    # Create player (needed for collision system)
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(20.0, 20.0))
    esper.add_component(player, Collider(0.5))

    # Create two enemies
    enemy1 = esper.create_entity()
    esper.add_component(enemy1, Enemy("shooter"))
    esper.add_component(enemy1, Position(10.0, 10.0))
    esper.add_component(enemy1, Collider(0.4))
    esper.add_component(enemy1, Health(5, 5))

    enemy2 = esper.create_entity()
    esper.add_component(enemy2, Enemy("chaser"))
    esper.add_component(enemy2, Position(10.0, 10.0))
    esper.add_component(enemy2, Collider(0.4))
    esper.add_component(enemy2, Health(3, 3))

    # Create enemy projectile at enemy2 position
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(10.0, 10.0))
    esper.add_component(projectile, Projectile(damage=1.0, owner=enemy1))
    esper.add_component(projectile, Collider(0.2))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Projectile should still exist (no collision with enemy)
    assert esper.entity_exists(projectile)

    # Enemy health unchanged
    health = esper.component_for_entity(enemy2, Health)
    assert health.current == 3


def test_projectile_damages_player():
    """Test enemy projectile reduces player health."""
    esper.switch_world("test_projectile_damage_player")
    esper.clear_database()

    # Create player with 3 HP
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(3, 6))
    esper.add_component(player, Collider(0.5))

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))
    esper.add_component(enemy, Position(5.0, 10.0))

    # Create enemy projectile at player position
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(10.0, 10.0))
    esper.add_component(projectile, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile, Collider(0.2))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify damage dealt
    health = esper.component_for_entity(player, Health)
    assert health.current == 2.0

    # Verify invincibility granted
    from src.components.game import Invincible
    assert esper.has_component(player, Invincible)
    inv = esper.component_for_entity(player, Invincible)
    assert inv.remaining == pytest.approx(Config.INVINCIBILITY_DURATION)

    # Verify projectile removed
    assert not esper.entity_exists(projectile)


def test_projectile_respects_invincibility():
    """Test projectile doesn't damage invincible player."""
    esper.switch_world("test_projectile_invincibility")
    esper.clear_database()

    # Create invincible player with 3 HP
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(3, 6))
    esper.add_component(player, Collider(0.5))
    from src.components.game import Invincible
    esper.add_component(player, Invincible(0.3))

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))

    # Create enemy projectile
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(10.0, 10.0))
    esper.add_component(projectile, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile, Collider(0.2))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify no damage dealt
    health = esper.component_for_entity(player, Health)
    assert health.current == 3.0

    # Verify projectile still removed
    assert not esper.entity_exists(projectile)


def test_enemy_contact_damages_player():
    """Test touching enemy deals 1 damage."""
    esper.switch_world("test_enemy_contact")
    esper.clear_database()

    # Create player with 3 HP
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(3, 6))
    esper.add_component(player, Collider(0.5))

    # Create enemy overlapping player
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("chaser"))
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, Collider(0.5))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify damage dealt
    health = esper.component_for_entity(player, Health)
    assert health.current == 2.0

    # Verify invincibility granted
    from src.components.game import Invincible
    assert esper.has_component(player, Invincible)


def test_enemy_contact_respects_invincibility():
    """Test touching enemy while invincible doesn't damage."""
    esper.switch_world("test_enemy_contact_invincible")
    esper.clear_database()

    # Create invincible player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(3, 6))
    esper.add_component(player, Collider(0.5))
    from src.components.game import Invincible
    esper.add_component(player, Invincible(0.3))

    # Create enemy overlapping player
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("chaser"))
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, Collider(0.5))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify no damage dealt
    health = esper.component_for_entity(player, Health)
    assert health.current == 3.0


def test_enemy_contact_kills_player():
    """Test contact damage adds Dead component when health reaches 0."""
    esper.switch_world("test_enemy_contact_death")
    esper.clear_database()

    # Create player with 1 HP
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(1, 6))
    esper.add_component(player, Collider(0.5))

    # Create enemy overlapping player
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("chaser"))
    esper.add_component(enemy, Position(10.0, 10.0))
    esper.add_component(enemy, Collider(0.5))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify death
    health = esper.component_for_entity(player, Health)
    assert health.current <= 0
    assert esper.has_component(player, Dead)


def test_player_death_on_zero_health():
    """Test Dead component added when health reaches 0."""
    esper.switch_world("test_player_death_zero")
    esper.clear_database()

    # Create player with 1 HP
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(1, 6))
    esper.add_component(player, Collider(0.5))

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))

    # Create fatal projectile
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(10.0, 10.0))
    esper.add_component(projectile, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile, Collider(0.2))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify death
    health = esper.component_for_entity(player, Health)
    assert health.current <= 0
    assert esper.has_component(player, Dead)


def test_player_death_on_negative_health():
    """Test Dead component added even if damage exceeds remaining HP."""
    esper.switch_world("test_player_death_negative")
    esper.clear_database()

    # Create player with 1 HP
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Health(1, 6))
    esper.add_component(player, Collider(0.5))

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("shooter"))

    # Create overkill projectile
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(10.0, 10.0))
    esper.add_component(projectile, Projectile(damage=5.0, owner=enemy))
    esper.add_component(projectile, Collider(0.2))

    # Process collision
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify death
    health = esper.component_for_entity(player, Health)
    assert health.current < 0
    assert esper.has_component(player, Dead)


def test_piercing_projectile_doesnt_get_destroyed():
    """Test piercing projectiles continue after hitting enemy."""
    from src.components.game import CollectedItems, Item
    from src.entities.player import create_player

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    # Create player with piercing effect
    player = create_player(world_name, 10.0, 10.0)
    collected = CollectedItems()
    collected.items.append(Item("piercing_tears", {}, ["piercing"]))
    esper.add_component(player, collected)

    # Create enemy
    from src.entities.enemies import create_enemy
    enemy = create_enemy(world_name, "chaser", 15.0, 10.0)
    enemy_health = esper.component_for_entity(enemy, Health)

    # Create projectile from player
    proj_entity = esper.create_entity()
    esper.add_component(proj_entity, Position(15.0, 10.0))
    from src.components.core import Velocity
    esper.add_component(proj_entity, Velocity(10.0, 0.0))
    esper.add_component(proj_entity, Collider(0.1))
    esper.add_component(proj_entity, Projectile(1.0, player))

    # Process collision
    collision_system = CollisionSystem()
    esper.add_processor(collision_system)
    esper.process()

    # Enemy should take damage
    assert enemy_health.current < enemy_health.max

    # Projectile should still exist (piercing)
    assert esper.entity_exists(proj_entity)


def test_normal_projectile_gets_destroyed():
    """Test normal projectiles are destroyed after hitting enemy."""
    from src.entities.player import create_player

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    # Create player without piercing
    player = create_player(world_name, 10.0, 10.0)

    # Create enemy
    from src.entities.enemies import create_enemy
    enemy = create_enemy(world_name, "chaser", 15.0, 10.0)

    # Create projectile from player
    proj_entity = esper.create_entity()
    esper.add_component(proj_entity, Position(15.0, 10.0))
    from src.components.core import Velocity
    esper.add_component(proj_entity, Velocity(10.0, 0.0))
    esper.add_component(proj_entity, Collider(0.1))
    esper.add_component(proj_entity, Projectile(1.0, player))

    # Process collision
    collision_system = CollisionSystem()
    esper.add_processor(collision_system)
    esper.process()

    # Projectile should be destroyed (normal shot)
    assert not esper.entity_exists(proj_entity)


def test_piercing_hits_multiple_enemies():
    """Test piercing projectile damages all enemies in path."""
    from src.components.game import CollectedItems, Item
    from src.entities.player import create_player

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    # Create player with piercing
    player = create_player(world_name, 10.0, 10.0)
    collected = CollectedItems()
    collected.items.append(Item("piercing_tears", {}, ["piercing"]))
    esper.add_component(player, collected)

    # Create 2 enemies in line
    from src.entities.enemies import create_enemy
    enemy1 = create_enemy(world_name, "chaser", 15.0, 10.0)
    enemy2 = create_enemy(world_name, "chaser", 15.5, 10.0)

    enemy1_health = esper.component_for_entity(enemy1, Health)
    enemy2_health = esper.component_for_entity(enemy2, Health)

    initial_hp1 = enemy1_health.current
    initial_hp2 = enemy2_health.current

    # Create projectile
    proj_entity = esper.create_entity()
    esper.add_component(proj_entity, Position(15.0, 10.0))
    from src.components.core import Velocity
    esper.add_component(proj_entity, Velocity(10.0, 0.0))
    esper.add_component(proj_entity, Collider(0.1))
    esper.add_component(proj_entity, Projectile(1.0, player))

    # Process collision
    collision_system = CollisionSystem()
    esper.add_processor(collision_system)
    esper.process()

    # Both enemies should take damage
    assert enemy1_health.current < initial_hp1
    assert enemy2_health.current < initial_hp2


def test_enemy_drops_item_on_death():
    """Test enemies can drop items when killed."""
    import random
    from src.entities.player import create_player

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    # Seed random for predictable test
    random.seed(42)

    # Create player
    player = create_player(world_name, 10.0, 10.0)

    # Create many enemies to ensure at least one drop
    # With 15% drop rate, 20 enemies should give ~3 drops
    from src.entities.enemies import create_enemy
    enemies = []
    for i in range(20):
        enemy = create_enemy(world_name, "chaser", 15.0 + i * 0.1, 10.0)
        enemies.append(enemy)

    # Kill all enemies with projectiles
    for enemy in enemies:
        proj = esper.create_entity()
        esper.add_component(proj, Position(15.0, 10.0))
        from src.components.core import Velocity
        esper.add_component(proj, Velocity(10.0, 0.0))
        esper.add_component(proj, Collider(0.1))
        esper.add_component(proj, Projectile(100.0, player))  # High damage to kill

        collision_system = CollisionSystem()
        esper.add_processor(collision_system)
        esper.process()

    # Count dropped items
    from src.components.game import Item
    item_count = len(list(esper.get_components(Item)))

    # Should have at least 1 drop from 20 enemies
    assert item_count > 0


def test_item_drops_at_enemy_position():
    """Test dropped items spawn at enemy position."""
    import random
    from src.entities.player import create_player

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    # Force a drop by manipulating random
    original_random = random.random
    random.random = lambda: 0.0  # Always drop

    try:
        # Create player
        player = create_player(world_name, 10.0, 10.0)

        # Create enemy at specific position
        from src.entities.enemies import create_enemy
        enemy = create_enemy(world_name, "chaser", 25.0, 30.0)

        # Kill enemy
        proj = esper.create_entity()
        esper.add_component(proj, Position(25.0, 30.0))
        from src.components.core import Velocity
        esper.add_component(proj, Velocity(10.0, 0.0))
        esper.add_component(proj, Collider(0.1))
        esper.add_component(proj, Projectile(100.0, player))

        collision_system = CollisionSystem()
        esper.add_processor(collision_system)
        esper.process()

        # Find dropped item
        from src.components.game import Item
        for _, (item, pos) in esper.get_components(Item, Position):
            # Item should be at enemy's death position
            assert abs(pos.x - 25.0) < 0.1
            assert abs(pos.y - 30.0) < 0.1
            break
        else:
            assert False, "No item was dropped"

    finally:
        random.random = original_random


def test_no_drop_without_luck():
    """Test enemies don't always drop items."""
    import random
    from src.entities.player import create_player

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    # Force no drops
    original_random = random.random
    random.random = lambda: 1.0  # Never drop

    try:
        # Create player
        player = create_player(world_name, 10.0, 10.0)

        # Create and kill enemy
        from src.entities.enemies import create_enemy
        enemy = create_enemy(world_name, "chaser", 15.0, 10.0)

        proj = esper.create_entity()
        esper.add_component(proj, Position(15.0, 10.0))
        from src.components.core import Velocity
        esper.add_component(proj, Velocity(10.0, 0.0))
        esper.add_component(proj, Collider(0.1))
        esper.add_component(proj, Projectile(100.0, player))

        collision_system = CollisionSystem()
        esper.add_processor(collision_system)
        esper.process()

        # Should be no items
        from src.components.game import Item
        item_count = len(list(esper.get_components(Item)))
        assert item_count == 0

    finally:
        random.random = original_random
