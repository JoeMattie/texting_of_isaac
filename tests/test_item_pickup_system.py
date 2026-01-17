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


def test_pickup_applies_additive_stats():
    """Test additive stat modifiers are added correctly."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with 1.0 damage
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    stats = Stats(5.0, 1.0, 0.3, 10.0)
    esper.add_component(player, stats)

    # Create item with +1.5 damage
    item_entity = esper.create_entity()
    item_component = Item("damage_up", {"damage": 1.5}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(10.0, 10.0))
    esper.add_component(item_entity, Collider(0.4))

    # Process pickup
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Verify damage increased additively
    assert stats.damage == 2.5


def test_pickup_applies_multiplicative_stats():
    """Test multiplicative stat modifiers are multiplied correctly."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with 5.0 speed
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    stats = Stats(5.0, 1.0, 0.3, 10.0)
    esper.add_component(player, stats)

    # Create item with 1.2 speed multiplier
    item_entity = esper.create_entity()
    item_component = Item("speed_boost", {"speed": 1.2}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(10.0, 10.0))
    esper.add_component(item_entity, Collider(0.4))

    # Process pickup
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Verify speed increased multiplicatively
    assert stats.speed == 6.0


def test_pickup_applies_multiple_stat_modifiers():
    """Test item can modify multiple stats at once."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    stats = Stats(5.0, 1.0, 0.3, 10.0)
    esper.add_component(player, stats)

    # Create item with damage + speed
    item_entity = esper.create_entity()
    item_component = Item("magic_mushroom", {"damage": 1.0, "speed": 1.2}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(10.0, 10.0))
    esper.add_component(item_entity, Collider(0.4))

    # Process pickup
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Verify both stats modified
    assert stats.damage == 2.0  # 1.0 + 1.0 (additive)
    assert stats.speed == 6.0   # 5.0 * 1.2 (multiplicative)


def test_pickup_adds_to_collected_items():
    """Test picked up items are tracked in CollectedItems."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    esper.add_component(player, Stats(5.0, 1.0, 0.3, 10.0))

    # Create first item
    item1 = esper.create_entity()
    item1_component = Item("mushroom", {"damage": 1.0}, [])
    esper.add_component(item1, item1_component)
    esper.add_component(item1, Position(10.0, 10.0))
    esper.add_component(item1, Collider(0.4))

    # Process pickup
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Verify CollectedItems component added and contains item
    assert esper.has_component(player, CollectedItems)
    collected = esper.component_for_entity(player, CollectedItems)
    assert len(collected.items) == 1
    assert collected.items[0].name == "mushroom"

    # Create second item
    item2 = esper.create_entity()
    item2_component = Item("triple_shot", {}, ["multi_shot"])
    esper.add_component(item2, item2_component)
    esper.add_component(item2, Position(10.0, 10.0))
    esper.add_component(item2, Collider(0.4))

    # Process pickup again
    system.process()

    # Verify second item added
    assert len(collected.items) == 2
    assert collected.items[1].name == "triple_shot"


def test_pickup_creates_collected_items_if_missing():
    """Test CollectedItems component is created if player doesn't have it."""
    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player without CollectedItems
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    esper.add_component(player, Stats(5.0, 1.0, 0.3, 10.0))

    # Verify no CollectedItems initially
    assert not esper.has_component(player, CollectedItems)

    # Create and pick up item
    item_entity = esper.create_entity()
    item_component = Item("test_item", {}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(10.0, 10.0))
    esper.add_component(item_entity, Collider(0.4))

    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Verify CollectedItems was created
    assert esper.has_component(player, CollectedItems)
    collected = esper.component_for_entity(player, CollectedItems)
    assert len(collected.items) == 1


def test_pickup_shows_notification():
    """Test notification is set after pickup."""
    world_name = "test_world"
    esper.switch_world(world_name)
    from src.config import Config

    # Create player
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Collider(0.3))
    esper.add_component(player, Stats(5.0, 1.0, 0.3, 10.0))

    # Create item
    item_entity = esper.create_entity()
    item_component = Item("magic_mushroom", {}, [])
    esper.add_component(item_entity, item_component)
    esper.add_component(item_entity, Position(10.0, 10.0))
    esper.add_component(item_entity, Collider(0.4))

    # Process pickup
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Verify notification set
    assert system.notification == "Picked up: magic_mushroom"
    assert system.notification_timer == Config.NOTIFICATION_DURATION


def test_notification_clears_after_timer():
    """Test notification disappears after timer expires."""
    from src.config import Config

    system = ItemPickupSystem()
    system.notification = "Test message"
    system.notification_timer = Config.NOTIFICATION_DURATION

    # Advance time by 2.1 seconds
    for _ in range(131):  # 131 frames * 0.016 = 2.096 seconds
        system.dt = 0.016
        system.process()

    # Verify notification cleared
    assert system.notification is None
    assert system.notification_timer <= 0


def test_notification_doesnt_clear_prematurely():
    """Test notification remains visible during timer."""
    from src.config import Config

    system = ItemPickupSystem()
    system.notification = "Test message"
    system.notification_timer = Config.NOTIFICATION_DURATION

    # Advance time by 1 second
    for _ in range(62):  # 62 frames * 0.016 = 0.992 seconds
        system.dt = 0.016
        system.process()

    # Verify notification still visible
    assert system.notification == "Test message"
    assert system.notification_timer > 0


def test_shop_item_purchase_success():
    """Test purchasing shop item with enough coins."""
    from src.entities.player import create_player
    from src.entities.shop import create_shop_item
    from src.components.dungeon import Currency, ShopItem

    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with coins
    player = create_player(world_name, 30, 10)
    esper.add_component(player, Currency(coins=10, bombs=3))

    # Create shop item costing 5 coins
    shop_item_ent = create_shop_item(world_name, "speed_boost", 30, 10)

    # Create and run system
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Check coins deducted
    currency = esper.component_for_entity(player, Currency)
    assert currency.coins == 5  # 10 - 5

    # Check item purchased
    shop_item = esper.component_for_entity(shop_item_ent, ShopItem)
    assert shop_item.purchased == True

    # Check item applied to player
    collected = esper.component_for_entity(player, CollectedItems)
    assert len(collected.items) == 1
    assert collected.items[0].name == "speed_boost"


def test_shop_item_insufficient_funds():
    """Test cannot purchase without enough coins."""
    from src.entities.player import create_player
    from src.entities.shop import create_shop_item
    from src.components.dungeon import Currency, ShopItem

    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with insufficient coins
    player = create_player(world_name, 30, 10)
    esper.add_component(player, Currency(coins=3, bombs=3))

    # Create shop item costing 5 coins
    shop_item_ent = create_shop_item(world_name, "speed_boost", 30, 10)

    # Create and run system
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Check coins unchanged
    currency = esper.component_for_entity(player, Currency)
    assert currency.coins == 3

    # Check item not purchased
    shop_item = esper.component_for_entity(shop_item_ent, ShopItem)
    assert shop_item.purchased == False

    # Check item not applied
    # Player may have CollectedItems from creation, check it doesn't contain speed_boost
    if esper.has_component(player, CollectedItems):
        collected = esper.component_for_entity(player, CollectedItems)
        item_names = [item.name for item in collected.items]
        assert "speed_boost" not in item_names


def test_shop_item_already_purchased():
    """Test cannot purchase item twice."""
    from src.entities.player import create_player
    from src.entities.shop import create_shop_item
    from src.components.dungeon import Currency, ShopItem

    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player with coins
    player = create_player(world_name, 30, 10)
    esper.add_component(player, Currency(coins=20, bombs=3))

    # Create shop item
    shop_item_ent = create_shop_item(world_name, "speed_boost", 30, 10)

    # Mark as already purchased
    shop_item = esper.component_for_entity(shop_item_ent, ShopItem)
    shop_item.purchased = True

    # Create and run system
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Check coins unchanged
    currency = esper.component_for_entity(player, Currency)
    assert currency.coins == 20


def test_regular_item_pickup_still_works():
    """Test regular (non-shop) items still work."""
    from src.entities.player import create_player
    from src.entities.items import create_item
    from src.components.dungeon import Currency

    world_name = "test_world"
    esper.switch_world(world_name)

    # Create player
    player = create_player(world_name, 30, 10)
    esper.add_component(player, Currency(coins=0, bombs=3))

    # Create regular item (no ShopItem component)
    item_ent = create_item(world_name, "magic_mushroom", 30, 10)

    # Create and run system
    system = ItemPickupSystem()
    system.dt = 0.016
    system.process()

    # Check item picked up for free
    collected = esper.component_for_entity(player, CollectedItems)
    item_names = [item.name for item in collected.items]
    assert "magic_mushroom" in item_names

    # Check coins unchanged
    currency = esper.component_for_entity(player, Currency)
    assert currency.coins == 0
