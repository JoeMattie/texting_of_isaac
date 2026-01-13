import pytest
import esper
from src.game.room import Room
from src.config import Config


def test_room_creates_with_dimensions():
    room = Room(width=60, height=20)
    assert room.width == 60
    assert room.height == 20


def test_room_generates_obstacles():
    room = Room(width=60, height=20)
    room.generate_obstacles(seed=42)

    # Should have some obstacles
    assert len(room.obstacles) > 0


def test_room_has_doors():
    room = Room(width=60, height=20)
    room.add_door("top")
    room.add_door("bottom")

    assert "top" in room.doors
    assert "bottom" in room.doors


def test_room_spawns_enemies():
    world = "test_room_enemies"
    esper.switch_world(world)
    esper.clear_database()

    room = Room(width=60, height=20)

    enemy_config = [
        {"type": "chaser", "count": 2},
        {"type": "shooter", "count": 1}
    ]

    spawned = room.spawn_enemies(world, enemy_config)

    # Should have spawned 3 enemies
    assert len(spawned) == 3
