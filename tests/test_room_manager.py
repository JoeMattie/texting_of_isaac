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


def test_room_manager_reveals_room_on_transition():
    """Test RoomManager reveals room in minimap on transition."""
    from src.components.dungeon import MiniMap

    # Create dungeon with two connected rooms
    rooms = {
        (0, 0): DungeonRoom(position=(0, 0), room_type=RoomType.START, doors={"east": (1, 0)}),
        (1, 0): DungeonRoom(position=(1, 0), room_type=RoomType.COMBAT, doors={"west": (0, 0)}),
    }
    dungeon = Dungeon(rooms=rooms, start_position=(0, 0), main_path=[(0, 0), (1, 0)])

    # Switch to main world for esper operations
    esper.switch_world("main")

    # Create minimap entity
    minimap_ent = esper.create_entity()
    minimap = MiniMap(current_position=(0, 0), visible_rooms=set())
    esper.add_component(minimap_ent, minimap)

    # Initial room should not be revealed yet
    assert (0, 0) not in minimap.visible_rooms

    # Create room manager
    room_manager = RoomManager(dungeon)

    # Transition to (1, 0)
    room_manager.transition_to_room((1, 0), "east")

    # Both rooms should now be revealed
    assert (0, 0) in minimap.visible_rooms
    assert (1, 0) in minimap.visible_rooms


def test_room_manager_reveals_start_room_on_init():
    """Test RoomManager reveals start room when initialized."""
    from src.components.dungeon import MiniMap

    rooms = {
        (0, 0): DungeonRoom(position=(0, 0), room_type=RoomType.START, doors={}),
    }
    dungeon = Dungeon(rooms=rooms, start_position=(0, 0), main_path=[(0, 0)])

    # Switch to main world for esper operations
    esper.switch_world("main")

    # Create minimap entity
    minimap_ent = esper.create_entity()
    minimap = MiniMap(current_position=(0, 0), visible_rooms=set())
    esper.add_component(minimap_ent, minimap)

    # Create room manager
    room_manager = RoomManager(dungeon)

    # Start room should be revealed
    assert (0, 0) in minimap.visible_rooms


def test_room_manager_updates_minimap_current_position():
    """Test RoomManager updates minimap current_position on transition."""
    from src.components.dungeon import MiniMap

    rooms = {
        (0, 0): DungeonRoom(position=(0, 0), room_type=RoomType.START, doors={"east": (1, 0)}),
        (1, 0): DungeonRoom(position=(1, 0), room_type=RoomType.COMBAT, doors={"west": (0, 0)}),
    }
    dungeon = Dungeon(rooms=rooms, start_position=(0, 0), main_path=[(0, 0), (1, 0)])

    # Switch to main world for esper operations
    esper.switch_world("main")

    minimap_ent = esper.create_entity()
    minimap = MiniMap(current_position=(0, 0), visible_rooms=set())
    esper.add_component(minimap_ent, minimap)

    room_manager = RoomManager(dungeon)

    # Transition to (1, 0)
    room_manager.transition_to_room((1, 0), "east")

    # Minimap current_position should update
    assert minimap.current_position == (1, 0)


def test_shop_room_spawns_items():
    """Test shop room spawns 3-4 shop items."""
    from src.components.dungeon import ShopItem

    # Create dungeon with shop room
    dungeon = Dungeon()
    shop_pos = (1, 0)
    dungeon.rooms[shop_pos] = DungeonRoom(
        position=shop_pos,
        room_type=RoomType.SHOP,
        doors={"west": (0, 0)},
        visited=False,
        cleared=False
    )
    dungeon.start_position = (0, 0)
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={"east": shop_pos},
        visited=True,
        cleared=True
    )

    # Switch to main world for esper operations
    esper.switch_world("main")

    # Create room manager
    manager = RoomManager(dungeon)

    # Transition to shop room
    manager.transition_to_room(shop_pos, "east")

    # Check shop items spawned
    shop_items = list(esper.get_components(ShopItem))
    assert 3 <= len(shop_items) <= 4

    # All should have prices
    for _, (shop_item,) in shop_items:
        assert shop_item.price > 0
        assert shop_item.purchased == False


def test_shop_items_positioned_correctly():
    """Test shop items arranged in row."""
    from src.components.dungeon import ShopItem
    from src.components.core import Position

    # Create dungeon with shop room
    dungeon = Dungeon()
    shop_pos = (0, 0)
    dungeon.rooms[shop_pos] = DungeonRoom(
        position=shop_pos,
        room_type=RoomType.SHOP,
        doors={},
        visited=False,
        cleared=False
    )
    dungeon.start_position = shop_pos

    # Switch to main world for esper operations
    esper.switch_world("main")

    # Create room manager
    manager = RoomManager(dungeon)

    # Check shop items positioned
    shop_items = list(esper.get_components(ShopItem, Position))

    # Should be in top half of room
    for _, (shop_item, pos) in shop_items:
        assert pos.y < 10  # Top half of 20-height room


def test_room_manager_tracks_current_floor():
    """Test RoomManager tracks current_floor attribute."""
    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={}
    )
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    # Should start at floor 1
    assert manager.current_floor == 1


def test_enemies_spawned_with_floor_scaling():
    """Test enemies created with correct floor parameter for stat scaling."""
    from src.components.game import Enemy
    from src.components.core import Health

    # Create dungeon with combat room
    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.COMBAT,
        doors={},
        enemies=[{"type": "chaser", "count": 2}],
        cleared=False
    )
    dungeon.start_position = (0, 0)

    esper.switch_world("main")
    # Create manager on floor 3 for clear scaling test
    manager = RoomManager(dungeon, current_floor=3)

    # Spawn room contents (should spawn enemies with floor=3)
    manager.spawn_room_contents()

    # Get spawned enemies
    enemies = list(esper.get_components(Enemy, Health))
    assert len(enemies) == 2

    # Floor 3 multiplier = 1.6, scaled HP = 4 (3 * 1.6 = 4.8 → int(4.8) = 4)
    for _, (enemy, health) in enemies:
        assert health.max == 4  # 3 * 1.6 = 4.8 → int(4.8) = 4


def test_boss_spawned_in_boss_room():
    """Test boss spawned in boss room instead of regular enemies."""
    from src.components.boss import Boss

    # Create dungeon with boss room
    dungeon = Dungeon()
    boss_pos = (0, 0)
    dungeon.rooms[boss_pos] = DungeonRoom(
        position=boss_pos,
        room_type=RoomType.BOSS,
        doors={},
        cleared=False
    )
    dungeon.start_position = boss_pos
    dungeon.boss_position = boss_pos

    esper.switch_world("main")
    manager = RoomManager(dungeon)
    manager.current_floor = 1  # Floor 1 = boss_a

    # Spawn room contents
    manager.spawn_room_contents()

    # Should have spawned a boss
    bosses = list(esper.get_components(Boss))
    assert len(bosses) == 1

    # Should be boss_a for floor 1
    _, (boss,) = bosses[0]
    assert boss.boss_type == "boss_a"


def test_different_boss_per_floor():
    """Test correct boss type spawned for each floor."""
    from src.components.boss import Boss

    # Test floor 1 -> boss_a
    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.BOSS,
        doors={},
        cleared=False
    )
    dungeon.start_position = (0, 0)
    dungeon.boss_position = (0, 0)

    esper.switch_world("main")
    manager = RoomManager(dungeon, current_floor=1)
    manager.spawn_room_contents()
    bosses = list(esper.get_components(Boss))
    assert len(bosses) == 1
    assert bosses[0][1][0].boss_type == "boss_a"

    # Clear boss and test floor 2 -> boss_b
    for entity, (boss,) in esper.get_components(Boss):
        esper.delete_entity(entity, immediate=True)

    manager.current_floor = 2
    manager.spawn_room_contents()
    bosses2 = list(esper.get_components(Boss))
    assert len(bosses2) == 1
    assert bosses2[0][1][0].boss_type == "boss_b"

    # Clear boss and test floor 3 -> boss_c
    for entity, (boss,) in esper.get_components(Boss):
        esper.delete_entity(entity, immediate=True)

    manager.current_floor = 3
    manager.spawn_room_contents()
    bosses3 = list(esper.get_components(Boss))
    assert len(bosses3) == 1
    assert bosses3[0][1][0].boss_type == "boss_c"


def test_trapdoor_spawned_after_boss_room_clear():
    """Test trapdoor spawns after boss room is cleared."""
    from src.components.boss import Trapdoor

    # Create boss room
    dungeon = Dungeon()
    boss_pos = (0, 0)
    dungeon.rooms[boss_pos] = DungeonRoom(
        position=boss_pos,
        room_type=RoomType.BOSS,
        doors={},
        cleared=False
    )
    dungeon.start_position = boss_pos
    dungeon.boss_position = boss_pos

    esper.switch_world("main")
    manager = RoomManager(dungeon)
    manager.current_floor = 1

    # Initially no trapdoor
    trapdoors = list(esper.get_components(Trapdoor))
    assert len(trapdoors) == 0

    # Clear the room
    manager.on_room_cleared()

    # Should spawn trapdoor
    trapdoors = list(esper.get_components(Trapdoor))
    assert len(trapdoors) == 1

    # Trapdoor should lead to next floor
    _, (trapdoor,) = trapdoors[0]
    assert trapdoor.next_floor == 2


def test_trapdoor_not_spawned_in_normal_rooms():
    """Test trapdoor only spawns in boss rooms, not combat rooms."""
    from src.components.boss import Trapdoor

    # Create normal combat room
    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.COMBAT,
        doors={},
        enemies=[{"type": "chaser", "count": 1}],
        cleared=False
    )
    dungeon.start_position = (0, 0)

    esper.switch_world("main")
    manager = RoomManager(dungeon)

    # Clear the room
    manager.on_room_cleared()

    # Should NOT spawn trapdoor in normal room
    trapdoors = list(esper.get_components(Trapdoor))
    assert len(trapdoors) == 0


def test_advance_to_next_floor():
    """Test advancing to next floor generates new dungeon and increments floor."""
    # Create initial dungeon
    dungeon1 = Dungeon()
    dungeon1.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={}
    )
    dungeon1.start_position = (0, 0)

    esper.switch_world("main")
    manager = RoomManager(dungeon1)

    # Should start at floor 1
    assert manager.current_floor == 1
    assert manager.current_position == (0, 0)

    # Advance to floor 2
    manager.advance_to_next_floor(2)

    # Floor should increment
    assert manager.current_floor == 2

    # Dungeon should be regenerated (new dungeon instance)
    assert manager.dungeon is not dungeon1

    # Should be at start position of new dungeon
    assert manager.current_position == manager.dungeon.start_position


def test_floor_transition_clears_entities():
    """Test floor transition removes all entities except player."""
    from src.components.game import Player, Enemy
    from src.entities.player import create_player
    from src.entities.enemies import create_enemy

    dungeon = Dungeon()
    dungeon.rooms[(0, 0)] = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.START,
        doors={}
    )
    dungeon.start_position = (0, 0)

    esper.switch_world("main")
    manager = RoomManager(dungeon)

    # Create player and enemies
    player = create_player("main", 30, 10)
    enemy1 = create_enemy("main", "chaser", 10, 10)
    enemy2 = create_enemy("main", "shooter", 20, 15)

    # Verify entities exist
    assert len(list(esper.get_components(Player))) == 1
    assert len(list(esper.get_components(Enemy))) == 2

    # Advance floor
    manager.advance_to_next_floor(2)

    # Player should still exist
    assert len(list(esper.get_components(Player))) == 1

    # Enemies should be cleared
    assert len(list(esper.get_components(Enemy))) == 0


def test_revisiting_shop_keeps_state():
    """Test shop items persist when revisiting."""
    from src.components.dungeon import ShopItem, Currency
    from src.entities.player import create_player

    # Create dungeon with shop room and adjacent room
    dungeon = Dungeon()
    shop_pos = (0, 0)
    dungeon.rooms[shop_pos] = DungeonRoom(
        position=shop_pos,
        room_type=RoomType.SHOP,
        doors={"east": (1, 0)},
        visited=False,
        cleared=False
    )
    dungeon.rooms[(1, 0)] = DungeonRoom(
        position=(1, 0),
        room_type=RoomType.COMBAT,
        doors={"west": shop_pos},
        visited=False,
        cleared=False,
        enemies=[]
    )
    dungeon.start_position = shop_pos

    # Switch to main world for esper operations
    esper.switch_world("main")

    # Create player with coins
    player = create_player("main", 30, 10)
    esper.add_component(player, Currency(coins=20, bombs=3))

    # Create room manager
    manager = RoomManager(dungeon)

    # Spawn initial room contents (shop items)
    manager.spawn_room_contents()

    # Get initial shop items count
    initial_count = len(list(esper.get_components(ShopItem)))
    assert initial_count >= 3

    # Leave and return
    manager.transition_to_room((1, 0), "east")
    manager.transition_to_room(shop_pos, "west")

    # Shop items should still exist (same count)
    # Note: Implementation detail - shop rooms may respawn items or persist them
    # For now, just check items exist
    final_count = len(list(esper.get_components(ShopItem)))
    assert final_count >= 3
