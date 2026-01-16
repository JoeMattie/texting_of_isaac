"""Tests for bomb system."""
import pytest
import esper
from src.systems.bomb import BombSystem
from src.systems.input import InputSystem
from src.components.core import Position, Sprite
from src.components.game import Player
from src.components.dungeon import Currency, Bomb
from src.config import Config


def test_bomb_system_places_bomb_when_player_presses_key():
    """Test that BombSystem places a bomb when player has bombs and presses key."""
    world_name = "test_bomb_1"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create player with bombs
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(30.0, 10.0))
    esper.add_component(player, Currency(coins=0, bombs=3))

    # Press bomb key
    input_system.bomb_pressed = True
    bomb_system.dt = 0.1
    esper.process()

    # Check bomb was created
    bombs = list(esper.get_components(Bomb, Position))
    assert len(bombs) == 1

    # Check bomb is at player position
    bomb_ent, (bomb, pos) = bombs[0]
    assert pos.x == 30.0
    assert pos.y == 10.0


def test_bomb_system_decrements_bomb_count():
    """Test that placing a bomb decrements player's bomb count."""
    world_name = "test_bomb_2"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create player with 3 bombs
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(30.0, 10.0))
    currency = Currency(coins=0, bombs=3)
    esper.add_component(player, currency)

    # Place bomb
    input_system.bomb_pressed = True
    bomb_system.dt = 0.1
    esper.process()

    # Check bomb count decreased
    assert currency.bombs == 2


def test_bomb_system_resets_input_flag():
    """Test that BombSystem resets the bomb_pressed flag after placing bomb."""
    world_name = "test_bomb_3"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(30.0, 10.0))
    esper.add_component(player, Currency(coins=0, bombs=3))

    # Press bomb key
    input_system.bomb_pressed = True
    bomb_system.dt = 0.1
    esper.process()

    # Check flag was reset
    assert input_system.bomb_pressed is False


def test_bomb_system_does_not_place_bomb_without_bombs():
    """Test that BombSystem doesn't place bomb when player has no bombs."""
    world_name = "test_bomb_4"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create player with 0 bombs
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(30.0, 10.0))
    esper.add_component(player, Currency(coins=0, bombs=0))

    # Press bomb key
    input_system.bomb_pressed = True
    bomb_system.dt = 0.1
    esper.process()

    # Check no bomb was created
    bombs = list(esper.get_components(Bomb))
    assert len(bombs) == 0


def test_bomb_system_creates_bomb_with_correct_components():
    """Test that placed bomb has all required components."""
    world_name = "test_bomb_5"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(25.0, 15.0))
    esper.add_component(player, Currency(coins=0, bombs=1))

    # Place bomb
    input_system.bomb_pressed = True
    bomb_system.dt = 0.1
    esper.process()

    # Get bomb entity
    bombs = list(esper.get_components(Bomb, Position, Sprite))
    assert len(bombs) == 1

    bomb_ent, (bomb, pos, sprite) = bombs[0]

    # Check Bomb component values
    # Note: fuse_time will be reduced by dt during the same frame placement occurs
    assert bomb.fuse_time == pytest.approx(Config.BOMB_FUSE_TIME - 0.1)
    assert bomb.blast_radius == Config.BOMB_BLAST_RADIUS
    assert bomb.owner == player

    # Check Position
    assert pos.x == 25.0
    assert pos.y == 15.0

    # Check Sprite
    assert sprite.char == "●"
    assert sprite.color == "red"


def test_bomb_system_counts_down_fuse():
    """Test that BombSystem counts down bomb fuse time."""
    world_name = "test_bomb_6"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create a bomb directly
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(30.0, 10.0))
    esper.add_component(bomb_ent, Sprite("●", "red"))
    bomb = Bomb(fuse_time=1.5, blast_radius=2.0, owner=0)
    esper.add_component(bomb_ent, bomb)

    # Process with dt
    bomb_system.dt = 0.5
    esper.process()

    # Check fuse decreased
    assert bomb.fuse_time == 1.0


def test_bomb_system_explodes_bomb_when_fuse_expires():
    """Test that bomb is removed when fuse time reaches 0."""
    world_name = "test_bomb_7"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create a bomb with short fuse
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(30.0, 10.0))
    esper.add_component(bomb_ent, Sprite("●", "red"))
    bomb = Bomb(fuse_time=0.1, blast_radius=2.0, owner=0)
    esper.add_component(bomb_ent, bomb)

    # Process with enough dt to expire fuse
    bomb_system.dt = 0.2
    esper.process()

    # Check bomb was removed
    bombs = list(esper.get_components(Bomb))
    assert len(bombs) == 0


def test_bomb_system_multiple_bombs_countdown():
    """Test that multiple bombs count down independently."""
    world_name = "test_bomb_8"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create multiple bombs with different fuse times
    bomb1 = esper.create_entity()
    esper.add_component(bomb1, Position(20.0, 10.0))
    esper.add_component(bomb1, Sprite("●", "red"))
    bomb1_comp = Bomb(fuse_time=1.5, blast_radius=2.0, owner=0)
    esper.add_component(bomb1, bomb1_comp)

    bomb2 = esper.create_entity()
    esper.add_component(bomb2, Position(30.0, 10.0))
    esper.add_component(bomb2, Sprite("●", "red"))
    bomb2_comp = Bomb(fuse_time=0.5, blast_radius=2.0, owner=0)
    esper.add_component(bomb2, bomb2_comp)

    # Process
    bomb_system.dt = 0.3
    esper.process()

    # Check both bombs decreased
    assert bomb1_comp.fuse_time == pytest.approx(1.2)
    assert bomb2_comp.fuse_time == pytest.approx(0.2)


def test_bomb_system_only_first_bomb_explodes():
    """Test that only expired bombs are removed."""
    world_name = "test_bomb_9"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create two bombs - one expires, one doesn't
    bomb1 = esper.create_entity()
    esper.add_component(bomb1, Position(20.0, 10.0))
    esper.add_component(bomb1, Sprite("●", "red"))
    esper.add_component(bomb1, Bomb(fuse_time=0.1, blast_radius=2.0, owner=0))

    bomb2 = esper.create_entity()
    esper.add_component(bomb2, Position(30.0, 10.0))
    esper.add_component(bomb2, Sprite("●", "red"))
    esper.add_component(bomb2, Bomb(fuse_time=1.5, blast_radius=2.0, owner=0))

    # Process - only bomb1 should expire
    bomb_system.dt = 0.2
    esper.process()

    # Check only one bomb remains
    bombs = list(esper.get_components(Bomb))
    assert len(bombs) == 1


def test_bomb_system_does_not_consume_bomb_if_none_pressed():
    """Test that bombs aren't consumed when key isn't pressed."""
    world_name = "test_bomb_10"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(30.0, 10.0))
    currency = Currency(coins=0, bombs=3)
    esper.add_component(player, currency)

    # Don't press bomb key
    input_system.bomb_pressed = False
    bomb_system.dt = 0.1
    esper.process()

    # Check bomb count unchanged
    assert currency.bombs == 3

    # Check no bomb created
    bombs = list(esper.get_components(Bomb))
    assert len(bombs) == 0


def test_bomb_system_multiple_players_place_bombs():
    """Test that each player can place their own bombs."""
    world_name = "test_bomb_11"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create two players (unlikely in real game, but tests the logic)
    player1 = esper.create_entity()
    esper.add_component(player1, Player())
    esper.add_component(player1, Position(20.0, 10.0))
    currency1 = Currency(coins=0, bombs=2)
    esper.add_component(player1, currency1)

    player2 = esper.create_entity()
    esper.add_component(player2, Player())
    esper.add_component(player2, Position(40.0, 10.0))
    currency2 = Currency(coins=0, bombs=1)
    esper.add_component(player2, currency2)

    # Press bomb key
    input_system.bomb_pressed = True
    bomb_system.dt = 0.1
    esper.process()

    # Check both players placed bombs
    bombs = list(esper.get_components(Bomb, Position))
    assert len(bombs) == 2

    # Check both currency counts decreased
    assert currency1.bombs == 1
    assert currency2.bombs == 0


def test_bomb_system_negative_fuse_triggers_explosion():
    """Test that bomb explodes even if fuse goes negative."""
    world_name = "test_bomb_12"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create bomb with tiny fuse
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(30.0, 10.0))
    esper.add_component(bomb_ent, Sprite("●", "red"))
    esper.add_component(bomb_ent, Bomb(fuse_time=0.05, blast_radius=2.0, owner=0))

    # Process with large dt that overshoots
    bomb_system.dt = 1.0
    esper.process()

    # Check bomb was removed
    bombs = list(esper.get_components(Bomb))
    assert len(bombs) == 0


# ===== Task 4: Explosion Damage Tests =====

def test_bomb_explosion_damages_enemy_in_range():
    """Test that bomb explosion damages enemy within blast radius."""
    from src.components.core import Health
    from src.components.game import Enemy

    world_name = "test_bomb_explosion_1"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create enemy near bomb location
    enemy = esper.create_entity()
    esper.add_component(enemy, Position(30.0, 10.0))
    esper.add_component(enemy, Health(current=3, max_hp=3))
    esper.add_component(enemy, Enemy(type="chaser"))

    # Create bomb that will explode at same position
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(30.0, 10.0))
    esper.add_component(bomb_ent, Sprite("●", "red"))
    esper.add_component(bomb_ent, Bomb(fuse_time=0.1, blast_radius=2.0, owner=0))

    # Get enemy health reference
    enemy_health = esper.component_for_entity(enemy, Health)

    # Process - bomb should explode and damage enemy
    bomb_system.dt = 0.2
    esper.process()

    # Check enemy took damage (1.0 damage = 1 heart)
    assert enemy_health.current == 2


def test_bomb_explosion_damages_player_in_range():
    """Test that bomb explosion can damage the player (self-damage)."""
    from src.components.core import Health

    world_name = "test_bomb_explosion_2"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create player near bomb location
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(31.0, 10.0))
    esper.add_component(player, Health(current=6, max_hp=6))
    esper.add_component(player, Currency(coins=0, bombs=1))

    # Create bomb that will explode close to player
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(30.0, 10.0))
    esper.add_component(bomb_ent, Sprite("●", "red"))
    esper.add_component(bomb_ent, Bomb(fuse_time=0.1, blast_radius=2.0, owner=player))

    # Get player health reference
    player_health = esper.component_for_entity(player, Health)

    # Process - bomb should explode and damage player
    bomb_system.dt = 0.2
    esper.process()

    # Check player took damage
    assert player_health.current == 5


def test_bomb_explosion_does_not_damage_entities_out_of_range():
    """Test that entities outside blast radius are not damaged."""
    from src.components.core import Health
    from src.components.game import Enemy

    world_name = "test_bomb_explosion_3"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create enemy far from bomb (outside blast radius of 2.0)
    enemy = esper.create_entity()
    esper.add_component(enemy, Position(35.0, 10.0))  # 5 units away
    esper.add_component(enemy, Health(current=3, max_hp=3))
    esper.add_component(enemy, Enemy(type="chaser"))

    # Create bomb
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(30.0, 10.0))
    esper.add_component(bomb_ent, Sprite("●", "red"))
    esper.add_component(bomb_ent, Bomb(fuse_time=0.1, blast_radius=2.0, owner=0))

    # Get enemy health reference
    enemy_health = esper.component_for_entity(enemy, Health)

    # Process - bomb should explode but not damage enemy
    bomb_system.dt = 0.2
    esper.process()

    # Check enemy did NOT take damage
    assert enemy_health.current == 3


def test_bomb_explosion_damages_multiple_entities():
    """Test that bomb damages all entities within blast radius."""
    from src.components.core import Health
    from src.components.game import Enemy

    world_name = "test_bomb_explosion_4"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create multiple enemies at different distances
    enemy1 = esper.create_entity()
    esper.add_component(enemy1, Position(30.0, 10.0))  # At bomb location
    esper.add_component(enemy1, Health(current=4, max_hp=4))
    esper.add_component(enemy1, Enemy(type="chaser"))

    enemy2 = esper.create_entity()
    esper.add_component(enemy2, Position(31.5, 10.0))  # 1.5 units away
    esper.add_component(enemy2, Health(current=5, max_hp=5))
    esper.add_component(enemy2, Enemy(type="shooter"))

    enemy3 = esper.create_entity()
    esper.add_component(enemy3, Position(28.5, 12.0))  # ~2.5 units away (outside range)
    esper.add_component(enemy3, Health(current=3, max_hp=3))
    esper.add_component(enemy3, Enemy(type="orbiter"))

    # Create bomb
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(30.0, 10.0))
    esper.add_component(bomb_ent, Sprite("●", "red"))
    esper.add_component(bomb_ent, Bomb(fuse_time=0.1, blast_radius=2.0, owner=0))

    # Get health references
    health1 = esper.component_for_entity(enemy1, Health)
    health2 = esper.component_for_entity(enemy2, Health)
    health3 = esper.component_for_entity(enemy3, Health)

    # Process - bomb should explode
    bomb_system.dt = 0.2
    esper.process()

    # Check enemy1 and enemy2 took damage, enemy3 didn't
    assert health1.current == 3  # Was 4, now 3
    assert health2.current == 4  # Was 5, now 4
    assert health3.current == 3  # Was 3, still 3 (out of range)


def test_bomb_explosion_does_not_damage_dead_entities():
    """Test that entities with health <= 0 don't take damage."""
    from src.components.core import Health
    from src.components.game import Enemy

    world_name = "test_bomb_explosion_5"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create enemy that's already dead
    enemy = esper.create_entity()
    esper.add_component(enemy, Position(30.0, 10.0))
    esper.add_component(enemy, Health(current=0, max_hp=3))  # Dead
    esper.add_component(enemy, Enemy(type="chaser"))

    # Create bomb at same position
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(30.0, 10.0))
    esper.add_component(bomb_ent, Sprite("●", "red"))
    esper.add_component(bomb_ent, Bomb(fuse_time=0.1, blast_radius=2.0, owner=0))

    # Get enemy health reference
    enemy_health = esper.component_for_entity(enemy, Health)

    # Process - bomb should explode but not damage dead enemy
    bomb_system.dt = 0.2
    esper.process()

    # Check enemy health didn't go negative
    assert enemy_health.current == 0


def test_bomb_explosion_at_edge_of_radius():
    """Test that bomb damages entity exactly at the edge of blast radius."""
    from src.components.core import Health
    from src.components.game import Enemy

    world_name = "test_bomb_explosion_6"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create enemy exactly at blast radius distance (2.0)
    enemy = esper.create_entity()
    esper.add_component(enemy, Position(32.0, 10.0))  # Exactly 2.0 units away
    esper.add_component(enemy, Health(current=3, max_hp=3))
    esper.add_component(enemy, Enemy(type="chaser"))

    # Create bomb
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(30.0, 10.0))
    esper.add_component(bomb_ent, Sprite("●", "red"))
    esper.add_component(bomb_ent, Bomb(fuse_time=0.1, blast_radius=2.0, owner=0))

    # Get enemy health reference
    enemy_health = esper.component_for_entity(enemy, Health)

    # Process - bomb should explode and damage enemy (distance <= radius)
    bomb_system.dt = 0.2
    esper.process()

    # Check enemy took damage
    assert enemy_health.current == 2


def test_bomb_explosion_uses_config_damage_value():
    """Test that bomb uses Config.BOMB_DAMAGE for damage amount."""
    from src.components.core import Health
    from src.components.game import Enemy

    world_name = "test_bomb_explosion_7"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create enemy
    enemy = esper.create_entity()
    esper.add_component(enemy, Position(30.0, 10.0))
    esper.add_component(enemy, Health(current=10, max_hp=10))
    esper.add_component(enemy, Enemy(type="tank"))

    # Create bomb
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(30.0, 10.0))
    esper.add_component(bomb_ent, Sprite("●", "red"))
    esper.add_component(bomb_ent, Bomb(fuse_time=0.1, blast_radius=2.0, owner=0))

    # Get enemy health reference
    enemy_health = esper.component_for_entity(enemy, Health)
    original_health = enemy_health.current

    # Process - bomb should explode
    bomb_system.dt = 0.2
    esper.process()

    # Check enemy took exactly Config.BOMB_DAMAGE (1.0) damage
    assert enemy_health.current == original_health - Config.BOMB_DAMAGE


def test_bomb_explosion_diagonal_distance():
    """Test that bomb uses Euclidean distance for damage calculation."""
    from src.components.core import Health
    from src.components.game import Enemy
    import math

    world_name = "test_bomb_explosion_8"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create enemy at diagonal position
    # Distance = sqrt(1.5^2 + 1.5^2) = sqrt(4.5) ≈ 2.12 (outside range of 2.0)
    enemy1 = esper.create_entity()
    esper.add_component(enemy1, Position(31.5, 11.5))
    esper.add_component(enemy1, Health(current=3, max_hp=3))
    esper.add_component(enemy1, Enemy(type="chaser"))

    # Create enemy closer diagonally
    # Distance = sqrt(1^2 + 1^2) = sqrt(2) ≈ 1.41 (inside range of 2.0)
    enemy2 = esper.create_entity()
    esper.add_component(enemy2, Position(31.0, 11.0))
    esper.add_component(enemy2, Health(current=4, max_hp=4))
    esper.add_component(enemy2, Enemy(type="shooter"))

    # Create bomb
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(30.0, 10.0))
    esper.add_component(bomb_ent, Sprite("●", "red"))
    esper.add_component(bomb_ent, Bomb(fuse_time=0.1, blast_radius=2.0, owner=0))

    # Get health references
    health1 = esper.component_for_entity(enemy1, Health)
    health2 = esper.component_for_entity(enemy2, Health)

    # Process - bomb should explode
    bomb_system.dt = 0.2
    esper.process()

    # Check only enemy2 took damage (enemy1 is out of range)
    assert health1.current == 3  # No damage
    assert health2.current == 3  # Took damage (was 4)


def test_bomb_explosion_respects_player_invincibility():
    """Test that bomb explosions respect player invincibility frames."""
    from src.components.core import Health
    from src.components.game import Player, Invincible

    world_name = "test_bomb_explosion_invincibility"
    esper.switch_world(world_name)
    esper.clear_database()

    input_system = InputSystem()
    bomb_system = BombSystem(input_system)
    esper.add_processor(bomb_system)

    # Create player at center with invincibility frames
    player = esper.create_entity()
    esper.add_component(player, Position(30.0, 10.0))
    esper.add_component(player, Player())
    esper.add_component(player, Health(max_hp=6, current=6))
    esper.add_component(player, Invincible(duration=1.0))

    # Create bomb next to player (within blast radius)
    bomb_ent = esper.create_entity()
    esper.add_component(bomb_ent, Position(30.5, 10.0))
    esper.add_component(bomb_ent, Sprite("●", "red"))
    esper.add_component(bomb_ent, Bomb(fuse_time=0.1, blast_radius=2.0, owner=player))

    # Get player health reference
    player_health = esper.component_for_entity(player, Health)
    original_health = player_health.current

    # Process - bomb should explode
    bomb_system.dt = 0.2
    esper.process()

    # Player should NOT take damage due to invincibility frames
    assert player_health.current == original_health
    assert player_health.current == 6  # No damage taken
