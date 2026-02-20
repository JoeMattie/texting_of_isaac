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


# --- Tests for expanded item pool ---

def test_total_item_count():
    """Test that there are at least 15 items in the database."""
    from src.data.items import ITEM_DEFINITIONS

    assert len(ITEM_DEFINITIONS) >= 15


def test_all_items_have_required_fields():
    """Test every item definition has the required structure."""
    from src.data.items import ITEM_DEFINITIONS

    required_fields = {"sprite", "color", "stat_modifiers", "special_effects"}
    for name, item in ITEM_DEFINITIONS.items():
        for field in required_fields:
            assert field in item, f"Item '{name}' missing field '{field}'"
        assert isinstance(item["sprite"], str) and len(item["sprite"]) == 1, \
            f"Item '{name}' sprite must be a single character"
        assert isinstance(item["stat_modifiers"], dict), \
            f"Item '{name}' stat_modifiers must be a dict"
        assert isinstance(item["special_effects"], list), \
            f"Item '{name}' special_effects must be a list"


def test_soy_milk_item():
    """Test Soy Milk: fast fire rate, reduced damage."""
    from src.data.items import ITEM_DEFINITIONS

    assert "soy_milk" in ITEM_DEFINITIONS
    item = ITEM_DEFINITIONS["soy_milk"]
    assert item["stat_modifiers"]["fire_rate"] > 0
    assert item["stat_modifiers"]["damage"] < 0


def test_polyphemus_item():
    """Test Polyphemus: huge damage, slow fire rate."""
    from src.data.items import ITEM_DEFINITIONS

    assert "polyphemus" in ITEM_DEFINITIONS
    item = ITEM_DEFINITIONS["polyphemus"]
    assert item["stat_modifiers"]["damage"] >= 3.0
    assert item["stat_modifiers"]["fire_rate"] < 0


def test_cricket_head_item():
    """Test Cricket Head: solid damage boost, no special effects."""
    from src.data.items import ITEM_DEFINITIONS

    assert "cricket_head" in ITEM_DEFINITIONS
    item = ITEM_DEFINITIONS["cricket_head"]
    assert item["stat_modifiers"].get("damage", 0) > 0
    assert item["special_effects"] == []


def test_spoon_bender_item():
    """Test Spoon Bender: grants homing effect."""
    from src.data.items import ITEM_DEFINITIONS

    assert "spoon_bender" in ITEM_DEFINITIONS
    item = ITEM_DEFINITIONS["spoon_bender"]
    assert "homing" in item["special_effects"]


def test_inner_eye_item():
    """Test Inner Eye: multi-shot effect."""
    from src.data.items import ITEM_DEFINITIONS

    assert "inner_eye" in ITEM_DEFINITIONS
    item = ITEM_DEFINITIONS["inner_eye"]
    assert "multi_shot" in item["special_effects"]


def test_dead_cat_item():
    """Test Dead Cat: massive damage, set_hp_1 effect."""
    from src.data.items import ITEM_DEFINITIONS

    assert "dead_cat" in ITEM_DEFINITIONS
    item = ITEM_DEFINITIONS["dead_cat"]
    assert item["stat_modifiers"].get("damage", 0) >= 3.0
    assert "set_hp_1" in item["special_effects"]


def test_new_items_are_spawnable():
    """Test that new items can be spawned as entities."""
    from src.entities.items import create_item
    from src.components.game import Item as ItemComponent

    new_items = [
        "soy_milk", "polyphemus", "cricket_head",
        "spoon_bender", "inner_eye", "dead_cat",
    ]

    world_name = "test_new_items_spawn"
    esper.switch_world(world_name)

    for item_name in new_items:
        entity = create_item(world_name, item_name, 5.0, 5.0)
        assert esper.entity_exists(entity), f"Entity for '{item_name}' was not created"
        assert esper.has_component(entity, ItemComponent), \
            f"Entity for '{item_name}' missing Item component"
        item_comp = esper.component_for_entity(entity, ItemComponent)
        assert item_comp.name == item_name
