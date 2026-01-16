"""Tests for room manager system."""
import pytest
import esper
from src.systems.room_manager import RoomManager
from src.game.dungeon import Dungeon, DungeonRoom, RoomType, RoomState


def test_room_manager_initializes_with_dungeon():
    """Test RoomManager creation with dungeon."""
    dungeon = Dungeon()
    start_room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={},
        state=RoomState.PEACEFUL
    )
    dungeon.rooms[(0, 0)] = start_room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    assert manager.dungeon == dungeon
    assert manager.current_position == (0, 0)
    assert manager.current_room == start_room


def test_current_room_tracks_position():
    """Verify current_room stays in sync with position."""
    dungeon = Dungeon()
    room1 = DungeonRoom(position=(0, 0), room_type=RoomType.START, doors={}, state=RoomState.PEACEFUL)
    room2 = DungeonRoom(position=(1, 0), room_type=RoomType.COMBAT, doors={}, state=RoomState.UNVISITED)

    dungeon.rooms[(0, 0)] = room1
    dungeon.rooms[(1, 0)] = room2
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    # Initially at start
    assert manager.current_position == (0, 0)
    assert manager.current_room == room1

    # Update position
    manager.current_position = (1, 0)
    manager.current_room = dungeon.rooms[(1, 0)]

    assert manager.current_room == room2
