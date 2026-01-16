"""Tests for door entity creation."""
import pytest
import esper
from src.entities.doors import spawn_door
from src.components.core import Position, Sprite
from src.components.combat import Collider
from src.components.dungeon import Door
from src.config import Config


@pytest.fixture(autouse=True)
def setup_world():
    """Setup and teardown esper world for each test."""
    esper.switch_world("test")
    yield
    esper.clear_database()


def test_spawn_door_creates_entity():
    """Test that spawn_door creates an entity with all required components."""
    door_ent = spawn_door("test", "north", (0, -1), locked=True)

    assert esper.entity_exists(door_ent)
    assert esper.has_component(door_ent, Position)
    assert esper.has_component(door_ent, Sprite)
    assert esper.has_component(door_ent, Collider)
    assert esper.has_component(door_ent, Door)


def test_spawn_door_north_position():
    """Test north door spawns at top wall center."""
    door_ent = spawn_door("test", "north", (0, -1))
    pos = esper.component_for_entity(door_ent, Position)

    assert pos.x == Config.ROOM_WIDTH / 2
    assert pos.y == 0


def test_spawn_door_south_position():
    """Test south door spawns at bottom wall center."""
    door_ent = spawn_door("test", "south", (0, 1))
    pos = esper.component_for_entity(door_ent, Position)

    assert pos.x == Config.ROOM_WIDTH / 2
    assert pos.y == Config.ROOM_HEIGHT - 1


def test_spawn_door_east_position():
    """Test east door spawns at right wall center."""
    door_ent = spawn_door("test", "east", (1, 0))
    pos = esper.component_for_entity(door_ent, Position)

    assert pos.x == Config.ROOM_WIDTH - 1
    assert pos.y == Config.ROOM_HEIGHT / 2


def test_spawn_door_west_position():
    """Test west door spawns at left wall center."""
    door_ent = spawn_door("test", "west", (-1, 0))
    pos = esper.component_for_entity(door_ent, Position)

    assert pos.x == 0
    assert pos.y == Config.ROOM_HEIGHT / 2


def test_spawn_door_locked_sprite():
    """Test locked door has correct sprite."""
    door_ent = spawn_door("test", "north", (0, -1), locked=True)
    sprite = esper.component_for_entity(door_ent, Sprite)

    assert sprite.char == "▮"
    assert sprite.color == "red"


def test_spawn_door_unlocked_sprite():
    """Test unlocked door has correct sprite."""
    door_ent = spawn_door("test", "north", (0, -1), locked=False)
    sprite = esper.component_for_entity(door_ent, Sprite)

    assert sprite.char == "▯"
    assert sprite.color == "cyan"


def test_spawn_door_collider_radius():
    """Test door has correct collider radius."""
    door_ent = spawn_door("test", "north", (0, -1))
    collider = esper.component_for_entity(door_ent, Collider)

    assert collider.radius == Config.DOOR_COLLIDER_RADIUS


def test_spawn_door_component_values():
    """Test Door component has correct values."""
    door_ent = spawn_door("test", "south", (5, 3), locked=False)
    door = esper.component_for_entity(door_ent, Door)

    assert door.direction == "south"
    assert door.leads_to == (5, 3)
    assert door.locked == False
