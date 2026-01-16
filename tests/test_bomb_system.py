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
