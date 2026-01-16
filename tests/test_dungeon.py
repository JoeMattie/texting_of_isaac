"""Tests for dungeon data structures."""
import pytest
from src.game.dungeon import RoomType, RoomState, DungeonRoom, Dungeon


def test_room_type_enum_has_all_types():
    """Verify all room types defined."""
    assert RoomType.START.value == "start"
    assert RoomType.COMBAT.value == "combat"
    assert RoomType.TREASURE.value == "treasure"
    assert RoomType.SHOP.value == "shop"
    assert RoomType.BOSS.value == "boss"
    assert RoomType.MINIBOSS.value == "miniboss"
    assert RoomType.SECRET.value == "secret"


def test_room_state_enum_has_all_states():
    """Verify all room states defined."""
    assert RoomState.UNVISITED.value == "unvisited"
    assert RoomState.ENTERING.value == "entering"
    assert RoomState.COMBAT.value == "combat"
    assert RoomState.CLEARED.value == "cleared"
    assert RoomState.PEACEFUL.value == "peaceful"


def test_dungeon_room_creation():
    """Test creating a dungeon room."""
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"north": (0, 1)},
    )

    assert room.position == (0, 0)
    assert room.room_type == RoomType.START
    assert room.doors == {"north": (0, 1)}
    assert room.visited == False
    assert room.cleared == False
    assert room.state == RoomState.UNVISITED


def test_dungeon_creation():
    """Test creating a dungeon."""
    dungeon = Dungeon()

    assert dungeon.rooms == {}
    assert dungeon.start_position is None
    assert dungeon.boss_position is None
    assert dungeon.miniboss_position is None
    assert dungeon.main_path == []
    assert dungeon.treasure_rooms == []
    assert dungeon.shop_rooms == []
    assert dungeon.secret_rooms == []
