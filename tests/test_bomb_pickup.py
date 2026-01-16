"""Tests for bomb pickup system."""
import pytest
import esper
from src.components.core import Position
from src.components.game import Player
from src.components.currency import BombPickup
from src.components.dungeon import Currency
from src.entities.player import create_player
from src.entities.currency import spawn_bomb_pickup
from src.systems.item_pickup import ItemPickupSystem


def test_bomb_pickup_component_has_quantity():
    """Test BombPickup component stores quantity."""
    pickup = BombPickup(quantity=1)
    assert pickup.quantity == 1

    multi = BombPickup(quantity=3)
    assert multi.quantity == 3


def test_spawn_bomb_pickup_creates_entity():
    """Test spawn_bomb_pickup creates bomb entity."""
    esper.clear_database()

    bomb_ent = spawn_bomb_pickup("test", 10.0, 5.0)

    assert esper.entity_exists(bomb_ent)
    assert esper.has_component(bomb_ent, BombPickup)
    assert esper.has_component(bomb_ent, Position)

    pos = esper.component_for_entity(bomb_ent, Position)
    assert pos.x == 10.0
    assert pos.y == 5.0


def test_bomb_pickup_increments_bombs():
    """Test picking up bomb increments player bomb count."""
    esper.clear_database()

    # Create player with currency
    player = create_player("test", 20.0, 20.0)
    currency = esper.component_for_entity(player, Currency)
    initial_bombs = currency.bombs

    # Create bomb pickup near player (within ITEM_PICKUP_RADIUS of 0.4)
    bomb = spawn_bomb_pickup("test", 20.2, 20.2)

    # Run pickup system
    pickup_system = ItemPickupSystem()
    pickup_system.process()

    # Bomb should be picked up
    assert not esper.entity_exists(bomb)
    assert currency.bombs == initial_bombs + 1


def test_bomb_pickup_respects_distance():
    """Test bomb pickup requires player to be close enough."""
    esper.clear_database()

    # Create player
    player = create_player("test", 20.0, 20.0)
    currency = esper.component_for_entity(player, Currency)
    initial_bombs = currency.bombs

    # Create bomb far from player
    bomb = spawn_bomb_pickup("test", 50.0, 50.0)

    # Run pickup system
    pickup_system = ItemPickupSystem()
    pickup_system.process()

    # Bomb should NOT be picked up
    assert esper.entity_exists(bomb)
    assert currency.bombs == initial_bombs


def test_bomb_pickup_with_custom_quantity():
    """Test bomb pickups can have different quantities."""
    esper.clear_database()

    player = create_player("test", 20.0, 20.0)
    currency = esper.component_for_entity(player, Currency)
    initial_bombs = currency.bombs

    # Create multi-bomb pickup (3 bombs)
    multi_bomb = spawn_bomb_pickup("test", 20.2, 20.2, quantity=3)

    pickup_system = ItemPickupSystem()
    pickup_system.process()

    assert not esper.entity_exists(multi_bomb)
    assert currency.bombs == initial_bombs + 3


def test_bomb_pickup_validates_positive_quantity():
    """Test BombPickup validates positive quantities."""
    with pytest.raises(ValueError, match="quantity must be positive"):
        BombPickup(quantity=0)

    with pytest.raises(ValueError, match="quantity must be positive"):
        BombPickup(quantity=-1)


def test_bomb_pickup_shows_notification():
    """Test bomb pickup shows notification message."""
    esper.clear_database()

    player = create_player("test", 20.0, 20.0)
    bomb = spawn_bomb_pickup("test", 20.2, 20.2, quantity=2)

    pickup_system = ItemPickupSystem()
    pickup_system.process()

    # Should show notification
    assert pickup_system.notification == "+2 bombs"
    assert pickup_system.notification_timer > 0
