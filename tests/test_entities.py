import pytest
import esper
from src.entities.player import create_player
from src.entities.enemies import create_enemy
from src.components.core import Position, Velocity, Health, Sprite
from src.components.combat import Stats, Collider
from src.components.game import Player, Enemy, AIBehavior
from src.config import Config


def test_create_player_returns_entity_id():
    world = "test_player_entity_1"
    esper.switch_world(world)
    esper.clear_database()
    entity_id = create_player(world, 30.0, 10.0)
    assert isinstance(entity_id, int)


def test_create_player_has_all_components():
    world = "test_player_entity_2"
    esper.switch_world(world)
    esper.clear_database()
    entity_id = create_player(world, 30.0, 10.0)

    # Check all components exist
    assert esper.has_component(entity_id, Position)
    assert esper.has_component(entity_id, Velocity)
    assert esper.has_component(entity_id, Health)
    assert esper.has_component(entity_id, Sprite)
    assert esper.has_component(entity_id, Stats)
    assert esper.has_component(entity_id, Collider)
    assert esper.has_component(entity_id, Player)


def test_create_player_position():
    world = "test_player_entity_3"
    esper.switch_world(world)
    esper.clear_database()
    entity_id = create_player(world, 30.0, 10.0)
    pos = esper.component_for_entity(entity_id, Position)

    assert pos.x == 30.0
    assert pos.y == 10.0


def test_create_enemy_chaser():
    world = "test_enemy_chaser"
    esper.switch_world(world)
    esper.clear_database()

    enemy_id = create_enemy(world, "chaser", 20.0, 10.0)

    assert esper.has_component(enemy_id, Position)
    assert esper.has_component(enemy_id, Enemy)

    enemy = esper.component_for_entity(enemy_id, Enemy)
    assert enemy.type == "chaser"


def test_create_enemy_shooter():
    world = "test_enemy_shooter"
    esper.switch_world(world)
    esper.clear_database()

    enemy_id = create_enemy(world, "shooter", 15.0, 8.0)

    enemy = esper.component_for_entity(enemy_id, Enemy)
    assert enemy.type == "shooter"

    # Shooter should have AI behavior
    assert esper.has_component(enemy_id, AIBehavior)


def test_enemy_data_has_pattern_configs():
    """Test ENEMY_DATA contains proper pattern configurations."""
    from src.entities.enemies import ENEMY_DATA

    # Chaser has no patterns
    assert ENEMY_DATA["chaser"]["patterns"] == {}

    # Shooter has aimed and spread patterns
    shooter_patterns = ENEMY_DATA["shooter"]["patterns"]
    assert "aimed" in shooter_patterns
    assert "spread" in shooter_patterns
    assert shooter_patterns["aimed"]["count"] == 1
    assert shooter_patterns["aimed"]["spread"] == 0
    assert shooter_patterns["aimed"]["speed"] == 5.0
    assert shooter_patterns["aimed"]["cooldown"] == 2.0

    # Verify all patterns have required keys
    for enemy_type, data in ENEMY_DATA.items():
        for pattern_name, pattern in data["patterns"].items():
            assert "count" in pattern, f"{enemy_type}.{pattern_name} missing count"
            assert "spread" in pattern, f"{enemy_type}.{pattern_name} missing spread"
            assert "speed" in pattern, f"{enemy_type}.{pattern_name} missing speed"
            assert "cooldown" in pattern, f"{enemy_type}.{pattern_name} missing cooldown"


def test_create_enemy_initializes_pattern_index():
    """Test enemy with patterns gets pattern_index set to 0."""
    esper.switch_world("test_world")
    enemy_id = create_enemy("test_world", "shooter", 10.0, 5.0)
    ai = esper.component_for_entity(enemy_id, AIBehavior)
    assert ai.pattern_index == 0


def test_create_player_has_collected_items():
    """Test player is initialized with empty CollectedItems component."""
    from src.components.game import CollectedItems

    world = "test_player_collected_items"
    esper.switch_world(world)
    esper.clear_database()

    entity_id = create_player(world, 30.0, 10.0)

    # Check CollectedItems component exists
    assert esper.has_component(entity_id, CollectedItems)

    # Check it starts empty
    collected_items = esper.component_for_entity(entity_id, CollectedItems)
    assert collected_items.items == []


def test_create_player_has_currency():
    """Test player entity has Currency component."""
    from src.components.dungeon import Currency

    world = "test_player_currency"
    esper.switch_world(world)
    esper.clear_database()

    player = create_player(world, 30.0, 20.0)

    assert esper.has_component(player, Currency)

    currency = esper.component_for_entity(player, Currency)
    assert currency.coins == Config.STARTING_COINS
    assert currency.bombs == Config.STARTING_BOMBS
    assert currency.keys == 0
