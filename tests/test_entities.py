import pytest
import esper
from src.entities.player import create_player
from src.components.core import Position, Velocity, Health, Sprite
from src.components.combat import Stats, Collider
from src.components.game import Player


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
