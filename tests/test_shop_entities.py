"""Tests for shop entity creation."""
import pytest
import esper
from src.entities.shop import create_shop_item, generate_shop_items
from src.components.game import Item
from src.components.dungeon import ShopItem
from src.components.core import Position, Sprite


@pytest.fixture
def world():
    """Create and switch to test world."""
    world_name = "test_shop"
    esper.switch_world(world_name)
    esper.clear_database()
    yield world_name


def test_create_shop_item(world):
    """Test creating a shop item entity."""
    entity = create_shop_item(world, "magic_mushroom", 30.0, 10.0)

    assert esper.has_component(entity, Item)
    assert esper.has_component(entity, ShopItem)
    assert esper.has_component(entity, Position)
    assert esper.has_component(entity, Sprite)

    shop_item = esper.component_for_entity(entity, ShopItem)
    assert shop_item.item_name == "magic_mushroom"
    assert shop_item.price == 15  # From Config.SHOP_ITEM_PRICES
    assert shop_item.purchased == False

    item = esper.component_for_entity(entity, Item)
    assert item.name == "magic_mushroom"

    pos = esper.component_for_entity(entity, Position)
    assert pos.x == 30.0
    assert pos.y == 10.0


def test_generate_shop_items_count(world):
    """Test generate_shop_items returns 3-4 items."""
    items = generate_shop_items()

    assert 3 <= len(items) <= 4

    # All items should be valid
    from src.config import Config
    for item_name in items:
        assert item_name in Config.SHOP_ITEM_PRICES


def test_generate_shop_items_randomness(world):
    """Test shop items are randomized."""
    # Generate multiple times, should get different results
    results = [tuple(sorted(generate_shop_items())) for _ in range(10)]

    # At least 2 different combinations in 10 tries
    unique_results = set(results)
    assert len(unique_results) >= 2
