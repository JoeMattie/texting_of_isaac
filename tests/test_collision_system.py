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


def test_enemy_drops_coins_on_death():
    """Test enemies drop coins 15% of the time when killed."""
    import random
    from src.entities.player import create_player
    from src.components.currency import Coin

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    # Seed random for predictable test
    random.seed(123)

    # Create player
    player = create_player(world_name, 10.0, 10.0)

    # Create many enemies to ensure at least some coin drops
    # With 15% drop rate, 30 enemies should give ~4-5 coin drops
    from src.entities.enemies import create_enemy
    enemies = []
    for i in range(30):
        enemy = create_enemy(world_name, "chaser", 20.0 + i * 2.0, 10.0)
        enemies.append(enemy)

    # Create collision system once
    collision_system = CollisionSystem()
    esper.add_processor(collision_system)

    # Kill all enemies with projectiles
    for i, enemy in enumerate(enemies):
        proj = esper.create_entity()
        esper.add_component(proj, Position(20.0 + i * 2.0, 10.0))
        from src.components.core import Velocity
        esper.add_component(proj, Velocity(10.0, 0.0))
        esper.add_component(proj, Collider(0.5))
        esper.add_component(proj, Projectile(100.0, player))  # High damage to kill
        esper.process()

    # Count dropped coins
    coin_count = len(list(esper.get_components(Coin)))

    # Should have at least 1 coin drop from 30 enemies
    assert coin_count > 0


def test_coin_drops_at_enemy_position():
    """Test dropped coins spawn at enemy death position."""
    import random
    from src.entities.player import create_player
    from src.components.currency import Coin

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    # Force a coin drop by manipulating random
    original_random = random.random
    random.random = lambda: 0.0  # Always drop coins

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

        # Find dropped coins
        coins_found = 0
        for _, (coin, pos) in esper.get_components(Coin, Position):
            # Coins should be at enemy's death position
            assert abs(pos.x - 25.0) < 0.1
            assert abs(pos.y - 30.0) < 0.1
            coins_found += 1

        # Should have dropped at least 1 coin
        assert coins_found >= 1

    finally:
        random.random = original_random


def test_coin_drops_1_to_2_coins():
    """Test enemies drop 1-2 coins when coin drop occurs."""
    import random
    from src.entities.player import create_player
    from src.components.currency import Coin

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    # Force coin drop and control randint
    original_random = random.random
    original_randint = random.randint
    random.random = lambda: 0.0  # Always drop coins
    random.randint = lambda a, b: 2  # Always drop 2 coins

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

        # Should have 2 coins
        coin_count = len(list(esper.get_components(Coin)))
        assert coin_count == 2

    finally:
        random.random = original_random
        random.randint = original_randint


def test_no_coin_drop_without_luck():
    """Test enemies don't always drop coins (respects 15% chance)."""
    import random
    from src.entities.player import create_player
    from src.components.currency import Coin

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    # Force no coin drops
    original_random = random.random
    random.random = lambda: 0.99  # Never drop coins (>15%)

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

        # Should be no coins
        coin_count = len(list(esper.get_components(Coin)))
        assert coin_count == 0

    finally:
        random.random = original_random


def test_coin_and_item_drops_independent():
    """Test coin drops are independent from item drops (both can happen)."""
    import random
    from src.entities.player import create_player
    from src.components.currency import Coin
    from src.components.game import Item

    world_name = "test_world"
    esper.switch_world(world_name)
    esper.clear_database()

    # Force both coin and item drops
    original_random = random.random
    original_randint = random.randint
    random.random = lambda: 0.0  # Always drop both
    random.randint = lambda a, b: 1  # Drop 1 coin

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

        # Should have both coins and items
        coin_count = len(list(esper.get_components(Coin)))
        item_count = len(list(esper.get_components(Item)))

        assert coin_count >= 1, "Should have coin drops"
        assert item_count >= 1, "Should have item drops"

    finally:
        random.random = original_random
        random.randint = original_randint


def test_player_door_collision_triggers_transition():
    """Test player colliding with unlocked door triggers room transition."""
    from src.components.dungeon import Door
    from src.components.core import Position
    from src.components.combat import Collider
    from src.components.core import Sprite
    from src.components.game import Player
    from src.game.dungeon import Dungeon, DungeonRoom, RoomType
    from src.systems.room_manager import RoomManager
    from unittest.mock import Mock

    esper.switch_world("test_world")
    esper.clear_database()

    # Create dungeon with two connected rooms
    dungeon = Dungeon()
    room1_pos = (0, 0)
    room2_pos = (0, -1)

    dungeon.rooms[room1_pos] = DungeonRoom(
        position=room1_pos,
        room_type=RoomType.START,
        doors={"north": room2_pos},
        cleared=True
    )
    dungeon.rooms[room2_pos] = DungeonRoom(
        position=room2_pos,
        room_type=RoomType.COMBAT,
        doors={"south": room1_pos},
        cleared=False
    )
    dungeon.start_position = room1_pos

    # Create room manager with mock transition method
    room_manager = RoomManager(dungeon)
    room_manager.transition_to_room = Mock()

    # Create collision system with room manager
    collision_system = CollisionSystem(room_manager)
    esper.add_processor(collision_system)

    # Create player at position (10, 5)
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10, 5))
    esper.add_component(player, Collider(0.5))

    # Create unlocked door at position (10, 5) - overlapping with player
    door = esper.create_entity()
    esper.add_component(door, Door("north", room2_pos, locked=False))
    esper.add_component(door, Position(10, 5))
    esper.add_component(door, Collider(1.0))
    esper.add_component(door, Sprite("▯", "cyan"))

    # Process collisions
    collision_system.process()

    # Verify transition was triggered
    room_manager.transition_to_room.assert_called_once_with(room2_pos, "north")


def test_player_door_collision_locked_door_no_transition():
    """Test player colliding with locked door does not trigger transition."""
    from src.components.dungeon import Door
    from src.components.core import Position
    from src.components.combat import Collider
    from src.components.core import Sprite
    from src.components.game import Player
    from src.game.dungeon import Dungeon, DungeonRoom, RoomType
    from src.systems.room_manager import RoomManager
    from unittest.mock import Mock

    esper.switch_world("test_world")
    esper.clear_database()

    # Create dungeon
    dungeon = Dungeon()
    room1_pos = (0, 0)
    room2_pos = (0, -1)

    dungeon.rooms[room1_pos] = DungeonRoom(
        position=room1_pos,
        room_type=RoomType.START,
        doors={"north": room2_pos},
        cleared=True
    )
    dungeon.rooms[room2_pos] = DungeonRoom(
        position=room2_pos,
        room_type=RoomType.COMBAT,
        doors={"south": room1_pos},
        cleared=False
    )
    dungeon.start_position = room1_pos

    # Create room manager with mock
    room_manager = RoomManager(dungeon)
    room_manager.transition_to_room = Mock()

    # Create collision system
    collision_system = CollisionSystem(room_manager)
    esper.add_processor(collision_system)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10, 5))
    esper.add_component(player, Collider(0.5))

    # Create LOCKED door at same position
    door = esper.create_entity()
    esper.add_component(door, Door("north", room2_pos, locked=True))
    esper.add_component(door, Position(10, 5))
    esper.add_component(door, Collider(1.0))
    esper.add_component(door, Sprite("▮", "red"))

    # Process collisions
    collision_system.process()

    # Verify NO transition was triggered
    room_manager.transition_to_room.assert_not_called()


def test_collision_system_without_room_manager():
    """Test CollisionSystem works without room_manager (no door transitions)."""
    from src.components.dungeon import Door
    from src.components.core import Position
    from src.components.combat import Collider
    from src.components.core import Sprite
    from src.components.game import Player

    esper.switch_world("test_world")
    esper.clear_database()

    # Create collision system without room manager
    collision_system = CollisionSystem(room_manager=None)
    esper.add_processor(collision_system)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10, 5))
    esper.add_component(player, Collider(0.5))

    # Create unlocked door
    door = esper.create_entity()
    esper.add_component(door, Door("north", (0, -1), locked=False))
    esper.add_component(door, Position(10, 5))
    esper.add_component(door, Collider(1.0))
    esper.add_component(door, Sprite("▯", "cyan"))

    # Should not crash when processing without room_manager
    collision_system.process()
    # If we get here without exception, test passes


def test_reposition_player_after_transition_from_north():
    """Test player repositioning when entering from north (spawn at south)."""
    from src.components.core import Position
    from src.components.game import Player
    from src.config import Config

    collision_system = CollisionSystem()

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    player_pos = Position(10, 10)
    esper.add_component(player, player_pos)

    # Reposition player after entering from north
    collision_system._reposition_player_after_transition(player, player_pos, "north")

    # Should be at south wall, slightly inward
    assert player_pos.y == Config.ROOM_HEIGHT - 2
    assert player_pos.x == Config.ROOM_WIDTH / 2


def test_reposition_player_after_transition_from_south():
    """Test player repositioning when entering from south (spawn at north)."""
    from src.components.core import Position
    from src.components.game import Player
    from src.config import Config

    collision_system = CollisionSystem()

    player = esper.create_entity()
    esper.add_component(player, Player())
    player_pos = Position(10, 10)
    esper.add_component(player, player_pos)

    # Reposition player after entering from south
    collision_system._reposition_player_after_transition(player, player_pos, "south")

    # Should be at north wall, slightly inward
    assert player_pos.y == 1
    assert player_pos.x == Config.ROOM_WIDTH / 2


def test_reposition_player_after_transition_from_east():
    """Test player repositioning when entering from east (spawn at west)."""
    from src.components.core import Position
    from src.components.game import Player
    from src.config import Config

    collision_system = CollisionSystem()

    player = esper.create_entity()
    esper.add_component(player, Player())
    player_pos = Position(10, 10)
    esper.add_component(player, player_pos)

    # Reposition player after entering from east
    collision_system._reposition_player_after_transition(player, player_pos, "east")

    # Should be at west wall, slightly inward
    assert player_pos.x == 1
    assert player_pos.y == Config.ROOM_HEIGHT / 2


def test_reposition_player_after_transition_from_west():
    """Test player repositioning when entering from west (spawn at east)."""
    from src.components.core import Position
    from src.components.game import Player
    from src.config import Config

    collision_system = CollisionSystem()

    player = esper.create_entity()
    esper.add_component(player, Player())
    player_pos = Position(10, 10)
    esper.add_component(player, player_pos)

    # Reposition player after entering from west
    collision_system._reposition_player_after_transition(player, player_pos, "west")

    # Should be at east wall, slightly inward
    assert player_pos.x == Config.ROOM_WIDTH - 2
    assert player_pos.y == Config.ROOM_HEIGHT / 2


def test_explosive_projectile_triggers_explosion():
    """Test explosive projectile creates area damage on hit."""
    from src.entities.player import create_player
    from src.entities.enemies import create_enemy
    from src.systems.collision import CollisionSystem
    from src.systems.bomb import BombSystem
    from src.systems.input import InputSystem
    from src.components.core import Position, Health
    from src.components.combat import Collider, Projectile
    from src.components.game import CollectedItems
    from src.config import Config

    world_name = "test_explosive_projectile"
    esper.switch_world(world_name)
    esper.clear_database()

    # Create player with explosive tears
    player = create_player(world_name, 30, 10)
    collected = esper.component_for_entity(player, CollectedItems)
    collected.items.append(type('Item', (), {'name': 'explosive_tears', 'stat_modifiers': {}, 'special_effects': ['explosive']})())

    # Create enemy at same position (will be hit directly)
    enemy1 = create_enemy(world_name, "chaser", 30, 10)
    enemy1_health = esper.component_for_entity(enemy1, Health)
    initial_health1 = enemy1_health.current

    # Create enemy nearby (should be hit by explosion)
    enemy2 = create_enemy(world_name, "chaser", 32, 10)  # 2 units away
    enemy2_health = esper.component_for_entity(enemy2, Health)
    initial_health2 = enemy2_health.current

    # Create explosive projectile
    proj = esper.create_entity()
    esper.add_component(proj, Position(30.0, 10.0))
    esper.add_component(proj, Collider(0.2))
    esper.add_component(proj, Projectile(damage=1.0, owner=player))

    # Create collision system with bomb system
    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    collision_system = CollisionSystem()
    collision_system.bomb_system = bomb_system

    # Process collision
    collision_system.process()

    # Verify direct hit enemy took both projectile + explosion damage
    direct_damage = 1.0  # projectile damage
    explosion_damage = Config.BOMB_DAMAGE * Config.EXPLOSIVE_TEAR_DAMAGE_MULTIPLIER
    expected_total_damage = direct_damage + explosion_damage
    assert enemy1_health.current == initial_health1 - expected_total_damage

    # Verify nearby enemy took explosion damage
    explosion_damage = Config.BOMB_DAMAGE * Config.EXPLOSIVE_TEAR_DAMAGE_MULTIPLIER
    assert enemy2_health.current == initial_health2 - explosion_damage

    # Verify projectile was deleted
    assert not esper.entity_exists(proj)


def test_explosive_overrides_piercing():
    """Test explosive effect overrides piercing."""
    from src.entities.player import create_player
    from src.entities.enemies import create_enemy
    from src.systems.collision import CollisionSystem
    from src.systems.bomb import BombSystem
    from src.systems.input import InputSystem
    from src.components.core import Position
    from src.components.combat import Collider, Projectile
    from src.components.game import CollectedItems

    world_name = "test_explosive_piercing"
    esper.switch_world(world_name)
    esper.clear_database()

    # Create player with both explosive and piercing
    player = create_player(world_name, 30, 10)
    collected = esper.component_for_entity(player, CollectedItems)
    collected.items.append(type('Item', (), {'name': 'explosive_tears', 'stat_modifiers': {}, 'special_effects': ['explosive']})())
    collected.items.append(type('Item', (), {'name': 'piercing_tears', 'stat_modifiers': {}, 'special_effects': ['piercing']})())

    # Create enemy
    enemy = create_enemy(world_name, "chaser", 30, 10)

    # Create projectile
    proj = esper.create_entity()
    esper.add_component(proj, Position(30.0, 10.0))
    esper.add_component(proj, Collider(0.2))
    esper.add_component(proj, Projectile(damage=1.0, owner=player))

    # Create collision system with bomb system
    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    collision_system = CollisionSystem()
    collision_system.bomb_system = bomb_system

    # Process collision
    collision_system.process()

    # Verify projectile was deleted (explosive overrides piercing)
    assert not esper.entity_exists(proj)


def test_explosive_respects_invincibility():
    """Test explosion respects player invincibility frames."""
    from src.entities.player import create_player
    from src.entities.enemies import create_enemy
    from src.systems.collision import CollisionSystem
    from src.systems.bomb import BombSystem
    from src.systems.input import InputSystem
    from src.components.core import Position, Health
    from src.components.combat import Collider, Projectile
    from src.components.game import CollectedItems, Invincible

    world_name = "test_explosive_invincibility"
    esper.switch_world(world_name)
    esper.clear_database()

    # Create player with explosive tears and invincibility
    player = create_player(world_name, 30, 10)
    collected = esper.component_for_entity(player, CollectedItems)
    collected.items.append(type('Item', (), {'name': 'explosive_tears', 'stat_modifiers': {}, 'special_effects': ['explosive']})())
    esper.add_component(player, Invincible(duration=1.0))

    player_health = esper.component_for_entity(player, Health)
    initial_health = player_health.current

    # Create enemy at player position
    enemy = create_enemy(world_name, "chaser", 30, 10)

    # Create explosive projectile at player position (will explode near player)
    proj = esper.create_entity()
    esper.add_component(proj, Position(30.0, 10.0))
    esper.add_component(proj, Collider(0.2))
    esper.add_component(proj, Projectile(damage=1.0, owner=player))

    # Create collision system with bomb system
    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    collision_system = CollisionSystem()
    collision_system.bomb_system = bomb_system

    # Process collision
    collision_system.process()

    # Verify player health unchanged (invincibility protected from explosion)
    assert player_health.current == initial_health
