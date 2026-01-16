"""Tests for room manager system."""
import pytest
import esper
from src.systems.room_manager import RoomManager
from src.game.dungeon import Dungeon, DungeonRoom, RoomType, RoomState
from src.components.dungeon import Door


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


def test_transition_to_room_updates_position():
    """Test transitioning to a new room updates position."""
    dungeon = Dungeon()
    room1 = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"east": (1, 0)},
        state=RoomState.PEACEFUL
    )
    room2 = DungeonRoom(
        position=(1, 0),
        room_type=RoomType.COMBAT,
        doors={"west": (0, 0)},
        state=RoomState.UNVISITED,
        enemies=[{"type": "chaser", "count": 1}]
    )

    dungeon.rooms[(0, 0)] = room1
    dungeon.rooms[(1, 0)] = room2
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    # Transition to room2
    manager.transition_to_room((1, 0), "east")

    assert manager.current_position == (1, 0)
    assert manager.current_room == room2


def test_transition_marks_room_as_visited():
    """Test transitioning marks the new room as visited."""
    dungeon = Dungeon()
    room1 = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"east": (1, 0)},
        state=RoomState.PEACEFUL
    )
    room2 = DungeonRoom(
        position=(1, 0),
        room_type=RoomType.COMBAT,
        doors={"west": (0, 0)},
        state=RoomState.UNVISITED,
        visited=False,
        enemies=[{"type": "chaser", "count": 1}]
    )

    dungeon.rooms[(0, 0)] = room1
    dungeon.rooms[(1, 0)] = room2
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    assert room2.visited == False

    manager.transition_to_room((1, 0), "east")

    assert room2.visited == True


def test_transition_sets_combat_state_for_uncleared_room():
    """Test transitioning to uncleared combat room sets COMBAT state."""
    dungeon = Dungeon()
    room1 = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"east": (1, 0)},
        state=RoomState.PEACEFUL
    )
    room2 = DungeonRoom(
        position=(1, 0),
        room_type=RoomType.COMBAT,
        doors={"west": (0, 0)},
        state=RoomState.UNVISITED,
        cleared=False,
        enemies=[{"type": "chaser", "count": 1}]
    )

    dungeon.rooms[(0, 0)] = room1
    dungeon.rooms[(1, 0)] = room2
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    manager.transition_to_room((1, 0), "east")

    assert room2.state == RoomState.COMBAT


def test_transition_sets_peaceful_state_for_treasure_room():
    """Test transitioning to treasure room sets PEACEFUL state."""
    dungeon = Dungeon()
    room1 = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"north": (0, 1)},
        state=RoomState.PEACEFUL
    )
    room2 = DungeonRoom(
        position=(0, 1),
        room_type=RoomType.TREASURE,
        doors={"south": (0, 0)},
        state=RoomState.UNVISITED,
        enemies=[]
    )

    dungeon.rooms[(0, 0)] = room1
    dungeon.rooms[(0, 1)] = room2
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    manager.transition_to_room((0, 1), "north")

    assert room2.state == RoomState.PEACEFUL


def test_transition_to_cleared_room_sets_cleared_state():
    """Test revisiting cleared room keeps CLEARED state."""
    dungeon = Dungeon()
    room1 = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"east": (1, 0)},
        state=RoomState.PEACEFUL
    )
    room2 = DungeonRoom(
        position=(1, 0),
        room_type=RoomType.COMBAT,
        doors={"west": (0, 0)},
        state=RoomState.UNVISITED,
        cleared=True,  # Already cleared
        enemies=[{"type": "chaser", "count": 1}]
    )

    dungeon.rooms[(0, 0)] = room1
    dungeon.rooms[(1, 0)] = room2
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    manager.transition_to_room((1, 0), "east")

    # Should be CLEARED, not COMBAT, even though enemies config exists
    assert room2.state == RoomState.CLEARED


def test_despawn_current_room_entities_method_exists():
    """Test despawn_current_room_entities method exists."""
    dungeon = Dungeon()
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={},
        state=RoomState.PEACEFUL
    )
    dungeon.rooms[(0, 0)] = room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    # Should not raise AttributeError
    manager.despawn_current_room_entities()


def test_spawn_room_contents_method_exists():
    """Test spawn_room_contents method exists."""
    dungeon = Dungeon()
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"east": (1, 0)},
        state=RoomState.PEACEFUL
    )
    dungeon.rooms[(0, 0)] = room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    # Should not raise AttributeError
    manager.spawn_room_contents()


def test_transition_calls_despawn_and_spawn():
    """Test transition_to_room despawns old room and spawns new room."""
    # This test verifies the integration, actual entity logic comes later
    dungeon = Dungeon()
    room1 = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"east": (1, 0)},
        state=RoomState.PEACEFUL
    )
    room2 = DungeonRoom(
        position=(1, 0),
        room_type=RoomType.COMBAT,
        doors={"west": (0, 0)},
        state=RoomState.UNVISITED,
        enemies=[{"type": "chaser", "count": 1}]
    )

    dungeon.rooms[(0, 0)] = room1
    dungeon.rooms[(1, 0)] = room2
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    # Transition should call despawn and spawn internally
    # For now just verify no errors
    manager.transition_to_room((1, 0), "east")

    assert manager.current_position == (1, 0)


def test_on_room_cleared_marks_room_cleared():
    """Test on_room_cleared marks room as cleared."""
    dungeon = Dungeon()
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.COMBAT,
        doors={"east": (1, 0)},
        state=RoomState.COMBAT,
        cleared=False,
        enemies=[{"type": "chaser", "count": 1}]
    )
    dungeon.rooms[(0, 0)] = room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    assert room.cleared == False
    assert room.state == RoomState.COMBAT

    manager.on_room_cleared()

    assert room.cleared == True
    assert room.state == RoomState.CLEARED


def test_lock_all_doors_method_exists():
    """Test lock_all_doors method exists."""
    dungeon = Dungeon()
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"east": (1, 0)},
        state=RoomState.PEACEFUL
    )
    dungeon.rooms[(0, 0)] = room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    # Should not raise AttributeError
    manager.lock_all_doors()


def test_unlock_all_doors_method_exists():
    """Test unlock_all_doors method exists."""
    dungeon = Dungeon()
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"east": (1, 0)},
        state=RoomState.PEACEFUL
    )
    dungeon.rooms[(0, 0)] = room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    # Should not raise AttributeError
    manager.unlock_all_doors()


def test_spawn_room_clear_reward_method_exists():
    """Test spawn_room_clear_reward method exists."""
    dungeon = Dungeon()
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"east": (1, 0)},
        state=RoomState.PEACEFUL
    )
    dungeon.rooms[(0, 0)] = room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    # Should not raise AttributeError
    manager.spawn_room_clear_reward()


def test_spawn_room_contents_spawns_doors_for_connections():
    """Test spawn_room_contents spawns doors for each connection."""
    dungeon = Dungeon()
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"north": (0, 1), "east": (1, 0)},
        state=RoomState.PEACEFUL
    )
    dungeon.rooms[(0, 0)] = room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)
    esper.switch_world("main")

    manager.spawn_room_contents()

    # Get all door components
    doors = list(esper.get_components(Door))

    # Should have spawned 2 doors
    assert len(doors) == 2

    # Extract door data
    door_data = {door_comp.direction: door_comp.leads_to for _, (door_comp,) in doors}

    # Verify doors for each connection
    assert "north" in door_data
    assert door_data["north"] == (0, 1)
    assert "east" in door_data
    assert door_data["east"] == (1, 0)


def test_spawn_room_contents_locks_doors_in_uncleared_combat_room():
    """Test spawn_room_contents locks doors in uncleared combat room."""
    dungeon = Dungeon()
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.COMBAT,
        doors={"south": (0, -1)},
        state=RoomState.COMBAT,
        cleared=False,
        enemies=[{"type": "chaser", "count": 1}]
    )
    dungeon.rooms[(0, 0)] = room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)
    esper.switch_world("main")

    manager.spawn_room_contents()

    # Get all door components
    doors = list(esper.get_components(Door))

    # Should have spawned 1 door
    assert len(doors) == 1

    # Verify door is locked
    _, (door_component,) = doors[0]
    assert door_component.locked == True


def test_spawn_room_contents_unlocks_doors_in_peaceful_room():
    """Test spawn_room_contents unlocks doors in peaceful room."""
    dungeon = Dungeon()
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.TREASURE,
        doors={"west": (-1, 0)},
        state=RoomState.PEACEFUL
    )
    dungeon.rooms[(0, 0)] = room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)
    esper.switch_world("main")

    manager.spawn_room_contents()

    # Get all door components
    doors = list(esper.get_components(Door))

    # Should have spawned 1 door
    assert len(doors) == 1

    # Verify door is unlocked
    _, (door_component,) = doors[0]
    assert door_component.locked == False


def test_spawn_room_contents_unlocks_doors_in_cleared_room():
    """Test spawn_room_contents unlocks doors in cleared room."""
    dungeon = Dungeon()
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.COMBAT,
        doors={"east": (1, 0)},
        state=RoomState.CLEARED,
        cleared=True,
        enemies=[{"type": "chaser", "count": 1}]
    )
    dungeon.rooms[(0, 0)] = room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)
    esper.switch_world("main")

    manager.spawn_room_contents()

    # Get all door components
    doors = list(esper.get_components(Door))

    # Should have spawned 1 door
    assert len(doors) == 1

    # Verify door is unlocked
    _, (door_component,) = doors[0]
    assert door_component.locked == False


def test_despawn_current_room_entities_removes_doors():
    """Test despawn_current_room_entities removes all Door entities."""
    dungeon = Dungeon()
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"north": (0, 1), "east": (1, 0), "south": (0, -1)},
        state=RoomState.PEACEFUL
    )
    dungeon.rooms[(0, 0)] = room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)
    esper.switch_world("main")

    # Spawn doors
    manager.spawn_room_contents()

    # Verify doors exist
    doors_before = list(esper.get_components(Door))
    assert len(doors_before) == 3

    # Despawn all entities
    manager.despawn_current_room_entities()

    # Verify all doors removed
    doors_after = list(esper.get_components(Door))
    assert len(doors_after) == 0


def test_lock_all_doors_locks_doors():
    """Test locking all doors."""
    from src.components.dungeon import Door
    from src.components.core import Position, Sprite

    # Create dungeon with connected rooms
    dungeon = Dungeon()
    start_pos = (0, 0)
    dungeon.rooms[start_pos] = DungeonRoom(
        position=start_pos,
        room_type=RoomType.START,
        doors={"north": (0, -1)},
        cleared=True
    )
    dungeon.start_position = start_pos

    manager = RoomManager(dungeon)

    # Spawn unlocked door
    from src.entities.doors import spawn_door
    door_ent = spawn_door("main", "north", (0, -1), locked=False)

    # Verify door starts unlocked
    door = esper.component_for_entity(door_ent, Door)
    sprite = esper.component_for_entity(door_ent, Sprite)
    assert door.locked is False
    assert sprite.char == "▯"
    assert sprite.color == "cyan"

    # Lock all doors
    manager.lock_all_doors()

    # Verify door is now locked
    assert door.locked is True
    assert sprite.char == "▮"
    assert sprite.color == "red"

def test_unlock_all_doors_unlocks_doors():
    """Test unlocking all doors."""
    from src.components.dungeon import Door
    from src.components.core import Position, Sprite

    # Create dungeon with connected rooms
    dungeon = Dungeon()
    start_pos = (0, 0)
    dungeon.rooms[start_pos] = DungeonRoom(
        position=start_pos,
        room_type=RoomType.START,
        doors={"north": (0, -1)},
        cleared=True
    )
    dungeon.start_position = start_pos

    manager = RoomManager(dungeon)

    # Spawn locked door
    from src.entities.doors import spawn_door
    door_ent = spawn_door("main", "north", (0, -1), locked=True)

    # Verify door starts locked
    door = esper.component_for_entity(door_ent, Door)
    sprite = esper.component_for_entity(door_ent, Sprite)
    assert door.locked is True
    assert sprite.char == "▮"
    assert sprite.color == "red"

    # Unlock all doors
    manager.unlock_all_doors()

    # Verify door is now unlocked
    assert door.locked is False
    assert sprite.char == "▯"
    assert sprite.color == "cyan"
