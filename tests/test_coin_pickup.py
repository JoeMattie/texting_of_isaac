"""Tests for coin pickup system."""
import pytest
import esper
from src.components.core import Position
from src.components.game import Player
from src.components.currency import Coin
from src.components.dungeon import Currency
from src.entities.player import create_player
from src.entities.currency import spawn_coin
from src.systems.item_pickup import ItemPickupSystem


def test_coin_component_has_value():
    """Test Coin component stores value."""
    coin = Coin(value=1)
    assert coin.value == 1

    nickel = Coin(value=5)
    assert nickel.value == 5


def test_spawn_coin_creates_entity():
    """Test spawn_coin creates coin entity."""
    esper.clear_database()

    coin_ent = spawn_coin("test", 10.0, 5.0)

    assert esper.entity_exists(coin_ent)
    assert esper.has_component(coin_ent, Coin)
    assert esper.has_component(coin_ent, Position)

    pos = esper.component_for_entity(coin_ent, Position)
    assert pos.x == 10.0
    assert pos.y == 5.0


def test_coin_pickup_increments_currency():
    """Test picking up coin increments player currency."""
    esper.clear_database()

    # Create player with currency
    player = create_player("test", 20.0, 20.0)
    currency = esper.component_for_entity(player, Currency)
    initial_coins = currency.coins

    # Create coin near player (within ITEM_PICKUP_RADIUS of 0.4)
    coin = spawn_coin("test", 20.2, 20.2)

    # Run pickup system
    pickup_system = ItemPickupSystem()
    pickup_system.process()

    # Coin should be picked up
    assert not esper.entity_exists(coin)
    assert currency.coins == initial_coins + 1


def test_coin_pickup_respects_distance():
    """Test coin pickup requires player to be close enough."""
    esper.clear_database()

    # Create player
    player = create_player("test", 20.0, 20.0)
    currency = esper.component_for_entity(player, Currency)
    initial_coins = currency.coins

    # Create coin far from player
    coin = spawn_coin("test", 50.0, 50.0)

    # Run pickup system
    pickup_system = ItemPickupSystem()
    pickup_system.process()

    # Coin should NOT be picked up
    assert esper.entity_exists(coin)
    assert currency.coins == initial_coins


def test_coin_with_custom_value():
    """Test coins can have different values."""
    esper.clear_database()

    player = create_player("test", 20.0, 20.0)
    currency = esper.component_for_entity(player, Currency)
    initial_coins = currency.coins

    # Create nickel (worth 5 coins) within pickup range
    nickel = spawn_coin("test", 20.2, 20.2, value=5)

    pickup_system = ItemPickupSystem()
    pickup_system.process()

    assert not esper.entity_exists(nickel)
    assert currency.coins == initial_coins + 5


def test_coin_validates_positive_value():
    """Test Coin validates positive values."""
    with pytest.raises(ValueError, match="value must be positive"):
        Coin(value=0)

    with pytest.raises(ValueError, match="value must be positive"):
        Coin(value=-1)


def test_coin_pickup_shows_notification():
    """Test coin pickup shows notification message."""
    esper.clear_database()

    player = create_player("test", 20.0, 20.0)
    coin = spawn_coin("test", 20.2, 20.2, value=5)

    pickup_system = ItemPickupSystem()
    pickup_system.process()

    # Should show notification
    assert pickup_system.notification == "+5 coins"
    assert pickup_system.notification_timer > 0
