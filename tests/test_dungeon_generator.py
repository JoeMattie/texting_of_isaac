"""Tests for dungeon generation."""
import pytest
from src.game.dungeon import generate_dungeon, RoomType


def test_dungeon_generates_main_path():
    """Verify dungeon has main path with 10-12 rooms."""
    dungeon = generate_dungeon(15)
    assert 10 <= len(dungeon.rooms) <= 12
    # Main path is the only thing generated in Task 5
    # Tasks 6-7 will add special rooms to reach 12-18 total


def test_dungeon_has_start_position():
    """Verify dungeon has start room at (0,0)."""
    dungeon = generate_dungeon(15)
    assert dungeon.start_position == (0, 0)
    assert (0, 0) in dungeon.rooms
    assert dungeon.rooms[(0, 0)].room_type == RoomType.START


def test_main_path_starts_at_start():
    """Verify main path begins at start position."""
    dungeon = generate_dungeon(15)
    assert dungeon.main_path[0] == dungeon.start_position


def test_main_path_ends_at_boss():
    """Verify main path ends at boss room."""
    dungeon = generate_dungeon(15)
    assert dungeon.main_path[-1] == dungeon.boss_position
    assert dungeon.rooms[dungeon.boss_position].room_type == RoomType.BOSS


def test_main_path_has_miniboss():
    """Verify mini-boss on main path at ~40% progress."""
    dungeon = generate_dungeon(15)
    assert dungeon.miniboss_position in dungeon.main_path

    miniboss_index = dungeon.main_path.index(dungeon.miniboss_position)
    expected_index = int(len(dungeon.main_path) * 0.4)

    # Allow ±1 room tolerance
    assert abs(miniboss_index - expected_index) <= 1


def test_main_path_is_connected():
    """Verify all rooms on main path have door connections."""
    dungeon = generate_dungeon(15)

    for i in range(len(dungeon.main_path) - 1):
        current_pos = dungeon.main_path[i]
        next_pos = dungeon.main_path[i + 1]

        current_room = dungeon.rooms[current_pos]

        # Current room should have door to next room
        assert next_pos in current_room.doors.values()
