"""Tests for MiniMapSystem."""
import pytest
import esper
from src.systems.minimap_system import MiniMapSystem
from src.components.dungeon import MiniMap
from src.game.dungeon import Dungeon, DungeonRoom, RoomType


@pytest.fixture
def minimap_world():
    """Create a test world for minimap tests."""
    world_name = "minimap_test"
    esper.switch_world(world_name)
    esper.clear_database()
    yield world_name
    esper.switch_world("main")


def test_minimap_system_renders_border(minimap_world):
    """Test MiniMapSystem renders border with box drawing characters."""
    # Create dungeon
    rooms = {
        (0, 0): DungeonRoom(position=(0, 0), room_type=RoomType.START, doors={}),
    }
    dungeon = Dungeon(rooms=rooms, start_position=(0, 0), main_path=[(0, 0)])

    # Create minimap
    minimap = MiniMap(current_position=(0, 0), visible_rooms={(0, 0)})

    # Render
    system = MiniMapSystem()
    lines = system.render(minimap, dungeon)

    # Check border
    assert lines[0] == "╔═══════╗"
    assert lines[-1] == "╚═══════╝"
    assert all(line.startswith("║") and line.endswith("║") for line in lines[1:-1])


def test_minimap_system_renders_current_room(minimap_world):
    """Test MiniMapSystem renders current room with ◆ symbol."""
    rooms = {
        (0, 0): DungeonRoom(position=(0, 0), room_type=RoomType.START, doors={}),
    }
    dungeon = Dungeon(rooms=rooms, start_position=(0, 0), main_path=[(0, 0)])

    minimap = MiniMap(current_position=(0, 0), visible_rooms={(0, 0)})

    system = MiniMapSystem()
    lines = system.render(minimap, dungeon)

    # Current room at (0, 0) should be in center (row 3, col 3 in 7x7 grid)
    center_line = lines[4]  # lines[0] is top border, lines[1-7] are grid, lines[4] is center
    assert "◆" in center_line


def test_minimap_system_renders_visited_room(minimap_world):
    """Test MiniMapSystem renders visited room with ■ symbol."""
    rooms = {
        (0, 0): DungeonRoom(position=(0, 0), room_type=RoomType.START, doors={"east": (1, 0)}),
        (1, 0): DungeonRoom(position=(1, 0), room_type=RoomType.COMBAT, doors={"west": (0, 0)}),
    }
    dungeon = Dungeon(rooms=rooms, start_position=(0, 0), main_path=[(0, 0), (1, 0)])

    # Current at (1, 0), visited both rooms
    minimap = MiniMap(current_position=(1, 0), visible_rooms={(0, 0), (1, 0)})

    system = MiniMapSystem()
    lines = system.render(minimap, dungeon)

    # (0, 0) is west of current, should show ■
    center_line = lines[4]
    assert "■" in center_line


def test_minimap_system_renders_adjacent_unvisited_room(minimap_world):
    """Test MiniMapSystem renders adjacent unvisited room with □ symbol."""
    rooms = {
        (0, 0): DungeonRoom(position=(0, 0), room_type=RoomType.START, doors={"east": (1, 0)}),
        (1, 0): DungeonRoom(position=(1, 0), room_type=RoomType.COMBAT, doors={"west": (0, 0)}),
    }
    dungeon = Dungeon(rooms=rooms, start_position=(0, 0), main_path=[(0, 0), (1, 0)])

    # Current at (0, 0), only visited (0, 0)
    minimap = MiniMap(current_position=(0, 0), visible_rooms={(0, 0)})

    system = MiniMapSystem()
    lines = system.render(minimap, dungeon)

    # (1, 0) is east of current and has door, should show □
    center_line = lines[4]
    assert "□" in center_line


def test_minimap_system_renders_unknown_as_space(minimap_world):
    """Test MiniMapSystem renders unknown rooms as spaces."""
    rooms = {
        (0, 0): DungeonRoom(position=(0, 0), room_type=RoomType.START, doors={}),
    }
    dungeon = Dungeon(rooms=rooms, start_position=(0, 0), main_path=[(0, 0)])

    minimap = MiniMap(current_position=(0, 0), visible_rooms={(0, 0)})

    system = MiniMapSystem()
    lines = system.render(minimap, dungeon)

    # Most cells should be spaces (unknown)
    center_line = lines[4]
    assert " " in center_line


def test_minimap_system_renders_7x7_grid(minimap_world):
    """Test MiniMapSystem renders exactly 7x7 grid."""
    rooms = {
        (0, 0): DungeonRoom(position=(0, 0), room_type=RoomType.START, doors={}),
    }
    dungeon = Dungeon(rooms=rooms, start_position=(0, 0), main_path=[(0, 0)])

    minimap = MiniMap(current_position=(0, 0), visible_rooms={(0, 0)})

    system = MiniMapSystem()
    lines = system.render(minimap, dungeon)

    # 9 lines total: top border + 7 rows + bottom border
    assert len(lines) == 9

    # Each content line has 7 characters between borders
    for line in lines[1:-1]:
        content = line[1:-1]  # Remove border characters
        assert len(content) == 7
