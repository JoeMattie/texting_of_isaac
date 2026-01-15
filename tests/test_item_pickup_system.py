"""Tests for ItemPickupSystem."""
import esper
from src.systems.item_pickup import ItemPickupSystem
from src.components.core import Position
from src.components.combat import Stats, Collider
from src.components.game import Player, Item, CollectedItems


def test_pickup_system_detects_overlap():
    """Test ItemPickupSystem detects player touching item."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    esper.add_component(player, Stats(5.0, 1.0, 0.3, 10.0))

    # Create item at same position
    item_entity = esper.create_entity()
    item_component = Item("test_item", {"damage": 1.0}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(10.0, 10.0))
    esper.add_component(item_entity, Collider(0.4))

    # Process pickup system
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Item should be removed
    assert not esper.entity_exists(item_entity)


def test_pickup_system_ignores_distant_items():
    """Test ItemPickupSystem doesn't pick up items far away."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    esper.add_component(player, Stats(5.0, 1.0, 0.3, 10.0))

    # Create item far away
    item_entity = esper.create_entity()
    item_component = Item("test_item", {"damage": 1.0}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(50.0, 50.0))
    esper.add_component(item_entity, Collider(0.4))

    # Process pickup system
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Item should still exist
    assert esper.entity_exists(item_entity)
