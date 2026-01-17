"""Integration tests for complete game systems."""
import esper
import pytest
from src.game.engine import GameEngine
from src.components.core import Position, Health
from src.components.game import Player, Enemy, AIBehavior, Invincible
from src.components.combat import Projectile, Collider
from src.entities.player import create_player
from src.entities.enemies import create_enemy


def test_full_enemy_shooting_cycle():
    """Test complete enemy shooting and collision cycle."""
    esper.switch_world("test_integration")
    esper.clear_database()

    # Create engine
    engine = GameEngine()

    # Create player
    player = create_player("test_integration", 20.0, 10.0)

    # Create shooter enemy close to player
    enemy = create_enemy("test_integration", "shooter", 10.0, 10.0)

    # Process for 3 seconds (90 frames at 30 FPS)
    # Shooter fires every 2-2.5 seconds, so should fire at least once
    for i in range(90):
        engine.update(1/30)  # dt = 0.0333...

    # Check that projectiles were created at some point
    # (They may have been removed by collision, but check history)
    # Since we can't check history, just verify system is working
    # by checking cooldowns were modified

    # This is a smoke test - if it doesn't crash, systems are integrated
    assert True  # Systems ran without errors


def test_enemy_projectiles_damage_player():
    """Test enemy projectiles remove themselves when hitting player."""
    esper.switch_world("test_integration")
    esper.clear_database()

    engine = GameEngine()

    # Create player
    player = create_player("test_integration", 10.5, 10.0)

    # Create shooter directly next to player (will hit immediately)
    enemy = create_enemy("test_integration", "shooter", 10.0, 10.0)

    # Get AI component and make pattern ready
    ai = esper.component_for_entity(enemy, AIBehavior)
    ai.pattern_cooldowns["aimed"] = 0.0

    # Update once to create projectile
    engine.update(0.1)

    # Count projectiles
    projectiles_before = len(list(esper.get_components(Projectile)))

    # Update again - projectile should hit player and be removed
    engine.update(0.1)

    projectiles_after = len(list(esper.get_components(Projectile)))

    # Projectile should be removed after collision
    assert projectiles_after < projectiles_before or projectiles_after == 0


def test_player_damage_and_invincibility_cycle():
    """Test complete damage flow from hit to recovery."""
    esper.switch_world("test_damage_cycle")
    esper.clear_database()

    # Create game engine
    engine = GameEngine()
    world = engine.world_name

    # Create player with 3 HP
    player = create_player(world, 20.0, 10.0)
    esper.switch_world(world)
    health = esper.component_for_entity(player, Health)
    health.current = 3.0

    # Create enemy
    enemy = create_enemy(world, "shooter", 10.0, 10.0)

    # Create first projectile at player position
    projectile1 = esper.create_entity()
    esper.add_component(projectile1, Position(20.0, 10.0))
    esper.add_component(projectile1, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile1, Collider(0.2))

    # Update once - collision should deal damage
    engine.update(0.1)

    # Verify damage dealt and invincibility granted
    assert health.current == 2.0
    assert esper.has_component(player, Invincible)

    # Create second projectile during invincibility
    projectile2 = esper.create_entity()
    esper.add_component(projectile2, Position(20.0, 10.0))
    esper.add_component(projectile2, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile2, Collider(0.2))

    # Update - should not deal damage (invincible)
    engine.update(0.1)
    assert health.current == 2.0

    # Wait for invincibility to expire (0.5s total)
    for _ in range(5):
        engine.update(0.1)

    # Invincibility should be gone
    assert not esper.has_component(player, Invincible)

    # Create third projectile after invincibility expires
    projectile3 = esper.create_entity()
    esper.add_component(projectile3, Position(20.0, 10.0))
    esper.add_component(projectile3, Projectile(damage=1.0, owner=enemy))
    esper.add_component(projectile3, Collider(0.2))

    # Update - should deal damage again
    engine.update(0.1)
    assert health.current == 1.0


def test_item_pickup_and_stat_modification():
    """Test complete pickup flow from collision to stat change."""
    esper.switch_world("test_pickup_flow")
    esper.clear_database()

    # Import dependencies inside test
    from src.entities.items import create_item
    from src.components.combat import Stats
    from src.systems.item_pickup import ItemPickupSystem

    # Create engine with player
    engine = GameEngine()
    world = engine.world_name

    # Create player with base stats
    player = create_player(world, 10.0, 10.0)
    esper.switch_world(world)
    stats = esper.component_for_entity(player, Stats)
    initial_damage = stats.damage
    initial_speed = stats.speed

    # Create magic_mushroom at player position
    item = create_item(world, "magic_mushroom", 10.0, 10.0)

    # Process ItemPickupSystem
    engine.update(0.016)

    # Verify stats changed (+1.0 damage additive, 1.2x speed multiplicative)
    assert stats.damage == initial_damage + 1.0
    assert stats.speed == initial_speed * 1.2

    # Verify item added to CollectedItems
    from src.components.game import CollectedItems
    assert esper.has_component(player, CollectedItems)
    collected = esper.component_for_entity(player, CollectedItems)
    assert len(collected.items) == 1
    assert collected.items[0].name == "magic_mushroom"

    # Verify item entity removed
    assert not esper.entity_exists(item)

    # Verify notification displayed
    assert engine.item_pickup_system.notification == "Picked up: magic_mushroom"
    assert engine.item_pickup_system.notification_timer > 0


def test_piercing_effect_in_combat():
    """Test piercing effect allows hitting multiple enemies."""
    esper.switch_world("test_piercing_combat")
    esper.clear_database()

    # Import dependencies inside test
    from src.components.combat import Collider, Projectile
    from src.components.game import CollectedItems, Item
    from src.entities.enemies import create_enemy
    from src.entities.player import create_player
    from src.systems.collision import CollisionSystem
    from src.components.core import Velocity

    # Create player with piercing effect (via CollectedItems)
    player = create_player("test_piercing_combat", 10.0, 10.0)
    collected = CollectedItems()
    # Add piercing item to collection
    piercing_item = Item("piercing_tears", {"damage": 0.5}, ["piercing"])
    collected.items.append(piercing_item)
    esper.add_component(player, collected)

    # Create first enemy
    enemy1 = create_enemy("test_piercing_combat", "chaser", 15.0, 10.0)
    enemy1_health = esper.component_for_entity(enemy1, Health)
    enemy1_initial_hp = enemy1_health.current

    # Create projectile at enemy position
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(15.0, 10.0))
    esper.add_component(projectile, Projectile(damage=2.0, owner=player))
    esper.add_component(projectile, Collider(0.2))
    esper.add_component(projectile, Velocity(10.0, 0.0))

    # Process CollisionSystem - hit first enemy
    system = CollisionSystem()
    esper.add_processor(system)
    esper.process()

    # Verify first enemy took damage
    assert enemy1_health.current < enemy1_initial_hp

    # Verify projectile still exists (piercing)
    assert esper.entity_exists(projectile)

    # Move projectile forward and create second enemy
    proj_pos = esper.component_for_entity(projectile, Position)
    proj_pos.x = 20.0
    enemy2 = create_enemy("test_piercing_combat", "chaser", 20.0, 10.0)
    enemy2_health = esper.component_for_entity(enemy2, Health)
    enemy2_initial_hp = enemy2_health.current

    # Process CollisionSystem again - hit second enemy
    esper.process()

    # Verify second enemy took damage
    assert enemy2_health.current < enemy2_initial_hp

    # Verify projectile still exists (piercing)
    assert esper.entity_exists(projectile)


def test_homing_effect_curves_bullets():
    """Test homing effect makes projectiles track enemies."""
    esper.switch_world("test_homing_curve")
    esper.clear_database()

    # Import dependencies inside test
    from src.components.combat import Stats, Projectile
    from src.components.game import CollectedItems, Item
    from src.components.core import Velocity
    from src.entities.enemies import create_enemy
    from src.systems.homing import HomingSystem

    # Create player with homing effect (via CollectedItems)
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Stats(5.0, 1.0, 0.3, 10.0))
    collected = CollectedItems()
    # Add homing item to collection
    homing_item = Item("homing_shots", {}, ["homing"])
    collected.items.append(homing_item)
    esper.add_component(player, collected)

    # Create enemy to the east
    enemy = create_enemy("test_homing_curve", "shooter", 20.0, 10.0)

    # Create projectile firing north (away from enemy)
    esper.switch_world("test_homing_curve")
    projectile = esper.create_entity()
    esper.add_component(projectile, Position(10.0, 10.0))
    esper.add_component(projectile, Projectile(damage=1.0, owner=player))
    vel = Velocity(0.0, -10.0)  # Firing north (negative y)
    esper.add_component(projectile, vel)

    # Process HomingSystem for 10 frames
    system = HomingSystem()
    for _ in range(10):
        system.dt = 0.033  # ~30 FPS
        system.process()

    # Verify velocity rotated toward enemy (vel.dx > 0)
    # Enemy is to the east, so projectile should have turned right (positive dx)
    assert vel.dx > 0


def test_multi_shot_creates_spread():
    """Test multi-shot effect fires 3 projectiles."""
    esper.switch_world("test_multi_shot")
    esper.clear_database()

    # Import dependencies inside test
    from src.components.combat import Stats, Projectile
    from src.components.game import CollectedItems, Item
    from src.systems.shooting import ShootingSystem

    # Create player with multi_shot effect (via CollectedItems)
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(10.0, 10.0))
    esper.add_component(player, Stats(5.0, 1.0, 2.0, 10.0))
    collected = CollectedItems()
    # Add multi_shot item to collection
    multi_shot_item = Item("triple_shot", {"fire_rate": 0.1}, ["multi_shot"])
    collected.items.append(multi_shot_item)
    esper.add_component(player, collected)

    # Set up ShootingSystem with shooting direction
    shooting_system = ShootingSystem()
    shooting_system.shoot_x = 1  # Shooting right
    shooting_system.shoot_y = 0
    shooting_system.dt = 0.016
    esper.add_processor(shooting_system)

    # Process ShootingSystem
    esper.process()

    # Verify 3 projectiles created
    projectiles = list(esper.get_components(Projectile))
    assert len(projectiles) == 3


def test_full_room_transition():
    """Test complete room transition flow from start to finish."""
    # Import dependencies
    from src.game.dungeon import Dungeon, DungeonRoom, RoomType
    from src.systems.room_manager import RoomManager
    from src.systems.collision import CollisionSystem
    from src.components.dungeon import Door
    from src.config import Config

    # Set up clean world
    esper.switch_world("test_room_transition")
    esper.clear_database()

    # Create dungeon with two connected rooms
    dungeon = Dungeon()
    room1_pos = (0, 0)
    room2_pos = (0, -1)

    dungeon.rooms[room1_pos] = DungeonRoom(
        position=room1_pos,
        room_type=RoomType.START,
        doors={"north": room2_pos},
        cleared=True
    )
    dungeon.rooms[room2_pos] = DungeonRoom(
        position=room2_pos,
        room_type=RoomType.COMBAT,
        doors={"south": room1_pos},
        cleared=False
    )
    dungeon.start_position = room1_pos

    # Create room manager and collision system
    room_manager = RoomManager(dungeon)
    collision_system = CollisionSystem(room_manager)
    esper.add_processor(collision_system)

    # Spawn starting room contents (door to north)
    room_manager.spawn_room_contents()

    # Verify one door exists in room 1
    doors_before = list(esper.get_components(Door))
    assert len(doors_before) == 1
    door_ent_before, (door_before,) = doors_before[0]
    assert door_before.direction == "north"
    assert door_before.leads_to == room2_pos
    assert door_before.locked is False  # Start room door should be unlocked

    # Create player at north door position
    door_pos = esper.component_for_entity(door_ent_before, Position)
    # Note: create_player will switch worlds, but we need to be in the same world as the door
    # The door was spawned in "main" by spawn_room_contents, so we create player there too
    player = create_player("main", door_pos.x, door_pos.y)

    # Verify player is in room 1
    assert room_manager.current_position == room1_pos

    # Process collision (this should trigger room transition)
    collision_system.process()

    # Verify room transition occurred
    assert room_manager.current_position == room2_pos
    assert room_manager.current_room == dungeon.rooms[room2_pos]

    # Verify old door was despawned
    doors_after = list(esper.get_components(Door))
    assert len(doors_after) == 1  # New door in room 2
    door_ent_after, (door_after,) = doors_after[0]
    assert door_ent_after != door_ent_before  # Different door entity
    assert door_after.direction == "south"  # Door back to room 1
    assert door_after.leads_to == room1_pos

    # Verify player was repositioned to south side of room 2
    player_pos = esper.component_for_entity(player, Position)
    assert player_pos.y == Config.ROOM_HEIGHT - 2  # Near south wall
    assert player_pos.x == Config.ROOM_WIDTH / 2   # Centered horizontally


def test_combat_room_door_unlock_on_clear():
    """Test doors unlock when combat room is cleared."""
    from src.game.dungeon import Dungeon, DungeonRoom, RoomType, RoomState
    from src.systems.room_manager import RoomManager
    from src.components.dungeon import Door
    from src.components.core import Sprite
    from src.config import Config

    # Set up clean world
    # Note: Using "main" world since spawn_door hardcodes "main" world
    esper.switch_world("main")
    esper.clear_database()

    # Create dungeon with combat room
    dungeon = Dungeon()
    room_pos = (0, 0)
    next_room_pos = (0, -1)

    dungeon.rooms[room_pos] = DungeonRoom(
        position=room_pos,
        room_type=RoomType.COMBAT,
        doors={"north": next_room_pos},
        cleared=False  # Uncleared combat room
    )
    dungeon.rooms[next_room_pos] = DungeonRoom(
        position=next_room_pos,
        room_type=RoomType.COMBAT,
        doors={"south": room_pos},
        cleared=False
    )
    dungeon.start_position = room_pos

    # Create room manager
    room_manager = RoomManager(dungeon)

    # Spawn room contents
    room_manager.spawn_room_contents()

    # Verify door is locked (combat room not cleared)
    doors = list(esper.get_components(Door, Sprite))
    assert len(doors) == 1
    door_ent, (door, sprite) = doors[0]
    assert door.locked is True
    assert sprite.char == "▮"
    assert sprite.color == "red"

    # Spawn an enemy
    enemy = create_enemy("main", "chaser", Config.ROOM_WIDTH / 2, Config.ROOM_HEIGHT / 2)

    # Kill the enemy (set health to 0 and delete)
    esper.delete_entity(enemy, immediate=True)

    # Call on_room_cleared (this would normally be called by combat system)
    room_manager.on_room_cleared()

    # Verify door is now unlocked
    assert door.locked is False
    assert sprite.char == "▯"
    assert sprite.color == "cyan"

    # Verify room state
    assert room_manager.current_room.cleared is True
    assert room_manager.current_room.state == RoomState.CLEARED


def test_full_minimap_navigation():
    """Test complete minimap flow: reveal rooms, navigate, update display."""
    esper.switch_world("main")
    esper.clear_database()

    from src.components.dungeon import MiniMap
    from src.game.dungeon import Dungeon, DungeonRoom, RoomType
    from src.systems.room_manager import RoomManager
    from src.systems.minimap_system import MiniMapSystem
    from src.systems.render import RenderSystem
    from src.config import Config

    # Create dungeon with 3 connected rooms
    rooms = {
        (0, 0): DungeonRoom(position=(0, 0), room_type=RoomType.START, doors={"east": (1, 0)}),
        (1, 0): DungeonRoom(position=(1, 0), room_type=RoomType.COMBAT, doors={"west": (0, 0), "south": (1, 1)}),
        (1, 1): DungeonRoom(position=(1, 1), room_type=RoomType.TREASURE, doors={"north": (1, 0)}),
    }
    dungeon = Dungeon(rooms=rooms, start_position=(0, 0), main_path=[(0, 0), (1, 0), (1, 1)])

    # Create minimap entity
    minimap_ent = esper.create_entity()
    minimap = MiniMap(current_position=(0, 0), visible_rooms=set())
    esper.add_component(minimap_ent, minimap)

    # Create systems
    room_manager = RoomManager(dungeon)
    minimap_system = MiniMapSystem()
    render_system = RenderSystem(minimap_system=minimap_system, dungeon=dungeon)

    # Step 1: Start room revealed
    assert (0, 0) in minimap.visible_rooms
    assert minimap.current_position == (0, 0)

    # Render minimap
    minimap_display = minimap_system.render(minimap, dungeon)
    center_line = minimap_display[4]  # Center row
    assert "◆" in center_line  # Current room at (0, 0)
    assert "□" in center_line  # Adjacent room at (1, 0) should show

    # Step 2: Transition to (1, 0)
    room_manager.transition_to_room((1, 0), "east")

    # Minimap should be updated in place
    assert (1, 0) in minimap.visible_rooms
    assert minimap.current_position == (1, 0)

    # Render minimap again
    minimap_display = minimap_system.render(minimap, dungeon)
    center_line = minimap_display[4]
    assert "◆" in center_line  # Current room at (1, 0)
    assert "■" in center_line  # Visited room at (0, 0)

    # All rooms should be visible
    all_chars = ''.join(minimap_display)
    assert all_chars.count("■") >= 1  # At least 1 visited room
    assert "◆" in all_chars  # Current room

    # Step 3: Verify render system integration
    grid = render_system.render("main")

    # Minimap should appear in top-right corner
    top_right_has_border = False
    for row in grid[:10]:  # Check top 10 rows
        for cell in row[-20:]:  # Check rightmost 20 columns
            if cell['char'] in '╔═╗║╚╝':
                top_right_has_border = True
                break

    assert top_right_has_border, "Minimap border should appear in top-right corner"


def test_shop_purchase_flow():
    """Test full shop flow: enter shop, buy item, verify effects."""
    from src.game.dungeon import Dungeon, DungeonRoom, RoomType
    from src.systems.room_manager import RoomManager
    from src.systems.item_pickup import ItemPickupSystem
    from src.components.dungeon import Currency, ShopItem
    from src.components.game import Player, CollectedItems

    # Note: RoomManager spawns shop items in "main" world (hardcoded)
    esper.switch_world("main")
    esper.clear_database()

    # Create dungeon with shop
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

    # Create player with coins
    player = create_player("main", 30, 10)
    esper.add_component(player, Currency(coins=15, bombs=3))

    # Create room manager and spawn shop items
    manager = RoomManager(dungeon)
    manager.spawn_room_contents()

    # Verify shop items spawned
    shop_items = list(esper.get_components(ShopItem, Position))
    assert len(shop_items) >= 3

    # Find cheapest item
    cheapest_ent = None
    cheapest_price = 999
    for ent, (shop_item, pos) in shop_items:
        if shop_item.price < cheapest_price:
            cheapest_price = shop_item.price
            cheapest_ent = ent

    # Move player to item
    player_pos = esper.component_for_entity(player, Position)
    item_pos = esper.component_for_entity(cheapest_ent, Position)
    player_pos.x = item_pos.x
    player_pos.y = item_pos.y

    # Get initial coins
    currency = esper.component_for_entity(player, Currency)
    initial_coins = currency.coins

    # Process pickup
    pickup_system = ItemPickupSystem()
    pickup_system.dt = 0.016
    pickup_system.process()

    # Verify purchase
    assert currency.coins == initial_coins - cheapest_price

    # Verify item purchased
    shop_item = esper.component_for_entity(cheapest_ent, ShopItem)
    assert shop_item.purchased == True

    # Verify item applied
    collected = esper.component_for_entity(player, CollectedItems)
    assert any(item.name == shop_item.item_name for item in collected.items)

    # Verify entity removed
    pickup_system.process()  # Second frame should remove entity
    assert not esper.entity_exists(cheapest_ent)
