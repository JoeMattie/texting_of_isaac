"""Tests for item entities and database."""
import pytest
import esper
from src.components.core import Position
from src.components.combat import Collider
from src.components.game import Item


def test_item_database_has_items():
    """Test ITEM_DEFINITIONS contains expected items."""
    from src.data.items import ITEM_DEFINITIONS

    assert "magic_mushroom" in ITEM_DEFINITIONS
    assert "triple_shot" in ITEM_DEFINITIONS
    assert "piercing_tears" in ITEM_DEFINITIONS
    assert "homing_shots" in ITEM_DEFINITIONS
    assert "speed_boost" in ITEM_DEFINITIONS
    assert "damage_up" in ITEM_DEFINITIONS


def test_item_definition_structure():
    """Test item definitions have required fields."""
    from src.data.items import ITEM_DEFINITIONS

    item_data = ITEM_DEFINITIONS["magic_mushroom"]
    assert "sprite" in item_data
    assert "color" in item_data
    assert "stat_modifiers" in item_data
    assert "special_effects" in item_data


def test_create_item_entity():
    """Test create_item creates entity with correct components."""
    from src.entities.items import create_item

    world_name = "test_world"
    esper.switch_world(world_name)

    entity = create_item(world_name, "magic_mushroom", 10.0, 20.0)

    # Check entity exists
    assert esper.entity_exists(entity)

    # Check components
    assert esper.has_component(entity, Position)
    assert esper.has_component(entity, Item)
    assert esper.has_component(entity, Collider)

    # Check values
    pos = esper.component_for_entity(entity, Position)
    assert pos.x == 10.0
    assert pos.y == 20.0

    item = esper.component_for_entity(entity, Item)
    assert item.name == "magic_mushroom"
    assert "damage" in item.stat_modifiers
    assert "speed" in item.stat_modifiers


def test_create_item_invalid_name():
    """Test create_item raises error for unknown item."""
    from src.entities.items import create_item

    world_name = "test_world"
    esper.switch_world(world_name)

    with pytest.raises(ValueError, match="Unknown item"):
        create_item(world_name, "nonexistent_item", 0.0, 0.0)


def test_spawn_random_item():
    """Test spawn_random_item creates valid item."""
    from src.entities.items import spawn_random_item
    from src.data.items import ITEM_DEFINITIONS

    world_name = "test_world"
    esper.switch_world(world_name)

    entity = spawn_random_item(world_name, 15.0, 25.0)

    # Check entity exists and has Item component
    assert esper.entity_exists(entity)
    assert esper.has_component(entity, Item)

    # Check item name is valid
    item = esper.component_for_entity(entity, Item)
    assert item.name in ITEM_DEFINITIONS


def test_explosive_tears_item_exists():
    """Test explosive tears item definition."""
    from src.data.items import ITEM_DEFINITIONS

    assert "explosive_tears" in ITEM_DEFINITIONS
    item = ITEM_DEFINITIONS["explosive_tears"]

    # Verify structure
    assert "sprite" in item
    assert "color" in item
    assert "stat_modifiers" in item
    assert "special_effects" in item

    # Verify explosive effect
    assert "explosive" in item["special_effects"]

    # Verify has damage boost
    assert "damage" in item["stat_modifiers"]
    assert item["stat_modifiers"]["damage"] > 0
