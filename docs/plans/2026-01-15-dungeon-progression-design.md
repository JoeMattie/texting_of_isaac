# Phase 2: Multi-Room Dungeon Progression - Design Document

**Date:** 2026-01-15
**Phase:** 2 - Progression
**Status:** Design Complete - Ready for Implementation

## Executive Summary

Transform the single-room arena into a procedurally generated dungeon with 12-18 interconnected rooms. Players explore a grid-based layout, clearing locked combat rooms to progress along a main path to the boss, with optional branches containing treasure rooms, shops, secret rooms, and a mini-boss. Adds currency system (coins, bombs), room-clear rewards, mini-map navigation, and bombable secret rooms.

## Goals

- **Primary:** Enable multi-room dungeon exploration with procedural generation
- **Secondary:** Add currency system for shops and bombs
- **Tertiary:** Implement mini-map for navigation and secret room discovery

## Architecture Overview

### Core Concept

Grid-based dungeon (like Binding of Isaac) where rooms connect north/south/east/west. Generation uses "main path first" algorithm to guarantee beatable dungeons, then adds optional branches with special rooms. Doors lock during combat and unlock when rooms are cleared, with instant transitions between rooms.

### New Systems

1. **DungeonGenerator** - Procedural dungeon layout generation
2. **RoomManager** - Current room state and transitions
3. **CurrencySystem** - Tracks coins and bombs
4. **BombSystem** - Bomb placement, fuse, explosion, wall destruction
5. **MiniMapSystem** - Simple navigation overlay
6. **RewardSystem** - Room-clear reward spawning

### Modified Systems

- **CollisionSystem** - Add door collision detection for transitions
- **RenderSystem** - Add mini-map overlay rendering
- **InputSystem** - Add bomb key (B) input

## Data Structures

### New Components

```python
class Currency:
    """Tracks player resources."""
    coins: int = 0
    bombs: int = 3
    keys: int = 0  # Future: locked doors

class RoomPosition:
    """Current position in dungeon grid."""
    x: int
    y: int

class Door:
    """Door entity component."""
    direction: str  # "north", "south", "east", "west"
    locked: bool = True
    leads_to: tuple[int, int]  # (x, y) coordinates
    position: Position  # Inherited from core

class Bomb:
    """Bomb entity component."""
    fuse_time: float = 1.5  # Seconds until explosion
    blast_radius: float = 2.0  # Tiles affected
    owner: int  # Player entity ID

class MiniBoss:
    """Mini-boss component."""
    boss_type: str  # "glutton", "hoarder", "sentinel"
    phase: int = 1
    guaranteed_drop: str  # Item type to drop on death

class MiniMap:
    """Mini-map state."""
    visible_rooms: set[tuple[int, int]]  # Rooms player has visited
    current_position: tuple[int, int]

class StatusEffect:
    """Status effect component."""
    effect_type: str  # "spelunker_sense", "speed_up", etc.
    duration: float  # Seconds remaining
    timer: float  # Elapsed time
```

### Dungeon Data Structures

```python
from enum import Enum
from dataclasses import dataclass

class RoomType(Enum):
    START = "start"
    COMBAT = "combat"
    TREASURE = "treasure"
    SHOP = "shop"
    BOSS = "boss"
    MINIBOSS = "miniboss"
    SECRET = "secret"

class RoomState(Enum):
    UNVISITED = "unvisited"  # Never entered
    ENTERING = "entering"    # Player just arrived
    COMBAT = "combat"        # Enemies alive, doors locked
    CLEARED = "cleared"      # Enemies dead, doors unlocked
    PEACEFUL = "peaceful"    # No enemies (treasure/shop/start)

@dataclass
class DungeonRoom:
    """Represents one room in the dungeon."""
    position: tuple[int, int]  # Grid coordinates
    room_type: RoomType
    doors: dict[str, tuple[int, int]]  # direction -> neighbor coords
    visited: bool = False
    cleared: bool = False
    state: RoomState = RoomState.UNVISITED
    enemies: list[dict] = None  # Enemy spawn configs
    secret_walls: list[str] = None  # Directions with bombable walls

@dataclass
class Dungeon:
    """Complete dungeon layout."""
    rooms: dict[tuple[int, int], DungeonRoom]  # (x,y) -> room
    start_position: tuple[int, int]
    boss_position: tuple[int, int]
    miniboss_position: tuple[int, int]
    main_path: list[tuple[int, int]]  # Guaranteed route to boss
    treasure_rooms: list[tuple[int, int]]
    shop_rooms: list[tuple[int, int]]
    secret_rooms: list[tuple[int, int]]
```

### Room Types

| Type | Description | Enemies | Doors | Reward |
|------|-------------|---------|-------|--------|
| **Start** | Spawn point | None | All unlocked | None |
| **Combat** | Regular fight | 2-5 enemies | Lock on entry | Room-clear reward |
| **Treasure** | Item room | None | Unlocked | Item pedestal |
| **Shop** | Purchase items | Shopkeeper NPC | Unlocked | 3-4 items for sale |
| **Boss** | Final fight | Boss enemy | Lock on entry | Victory |
| **Mini-boss** | Mid-run challenge | 1 tough enemy | Lock on entry | Guaranteed item |
| **Secret** | Hidden room | None | Revealed by bomb | Extra rewards |

## Dungeon Generation Algorithm

### Main Path First Approach

```python
def generate_dungeon(target_size: int = 15) -> Dungeon:
    """Generate dungeon using main path first algorithm.

    Args:
        target_size: Target number of rooms (12-18)

    Returns:
        Complete dungeon with guaranteed path to boss
    """
    dungeon = Dungeon()

    # Step 1: Place start room
    start_pos = (0, 0)
    dungeon.rooms[start_pos] = DungeonRoom(
        position=start_pos,
        room_type=RoomType.START,
        doors={},
        visited=False,
        cleared=True,
        state=RoomState.PEACEFUL
    )
    dungeon.start_position = start_pos
    dungeon.main_path.append(start_pos)

    # Step 2: Generate main path (10-12 rooms)
    current_pos = start_pos
    main_path_length = random.randint(10, 12)

    for i in range(main_path_length - 1):  # -1 because start already placed
        # Random walk with bias toward continuing in same direction
        next_pos = choose_next_position(current_pos, dungeon.rooms)

        # Place mini-boss at ~40% progress (around room 4-5)
        if i == int(main_path_length * 0.4):
            room_type = RoomType.MINIBOSS
            dungeon.miniboss_position = next_pos
        # Place boss at end
        elif i == main_path_length - 2:
            room_type = RoomType.BOSS
            dungeon.boss_position = next_pos
        else:
            room_type = RoomType.COMBAT

        # Create room
        room = DungeonRoom(
            position=next_pos,
            room_type=room_type,
            doors={},
            enemies=generate_enemy_config(room_type) if room_type == RoomType.COMBAT else []
        )
        dungeon.rooms[next_pos] = room

        # Create bidirectional door connection
        direction = get_direction(current_pos, next_pos)
        opposite = get_opposite_direction(direction)
        dungeon.rooms[current_pos].doors[direction] = next_pos
        dungeon.rooms[next_pos].doors[opposite] = current_pos

        dungeon.main_path.append(next_pos)
        current_pos = next_pos

    # Step 3: Add special room branches (4-6 rooms)
    special_rooms_added = 0
    max_special = random.randint(4, 6)

    # Add 2-3 treasure rooms
    for _ in range(random.randint(2, 3)):
        if special_rooms_added >= max_special:
            break
        branch_pos = add_branch_room(dungeon, RoomType.TREASURE)
        if branch_pos:
            dungeon.treasure_rooms.append(branch_pos)
            special_rooms_added += 1

    # Add 1-2 shops
    for _ in range(random.randint(1, 2)):
        if special_rooms_added >= max_special:
            break
        branch_pos = add_branch_room(dungeon, RoomType.SHOP)
        if branch_pos:
            dungeon.shop_rooms.append(branch_pos)
            special_rooms_added += 1

    # Step 4: Add secret rooms (1-2)
    num_secrets = random.randint(1, 2)
    for _ in range(num_secrets):
        secret_pos = add_secret_room(dungeon)
        if secret_pos:
            dungeon.secret_rooms.append(secret_pos)

    # Step 5: Fill to target size with combat rooms
    while len(dungeon.rooms) < target_size:
        branch_pos = add_branch_room(dungeon, RoomType.COMBAT)
        if not branch_pos:
            break  # Can't add more rooms

    # Step 6: Validate dungeon
    if not validate_dungeon(dungeon):
        # Regenerate if validation fails
        return generate_dungeon(target_size)

    return dungeon


def choose_next_position(current: tuple[int, int], existing_rooms: dict) -> tuple[int, int]:
    """Choose next position for main path.

    Biased random walk - prefers continuing in same direction.
    """
    x, y = current
    directions = [
        (x, y + 1),  # South
        (x, y - 1),  # North
        (x + 1, y),  # East
        (x - 1, y),  # West
    ]

    # Filter out positions that already have rooms
    available = [pos for pos in directions if pos not in existing_rooms]

    if not available:
        raise Exception("No available positions - dungeon generation stuck")

    return random.choice(available)


def add_branch_room(dungeon: Dungeon, room_type: RoomType) -> tuple[int, int]:
    """Add a branch room off the main path.

    Returns:
        Position of new room, or None if couldn't place
    """
    # Select random room on main path as branch point
    branch_point = random.choice(dungeon.main_path[:-3])  # Not too close to boss

    # Find available adjacent position
    x, y = branch_point
    candidates = [
        (x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)
    ]

    available = [pos for pos in candidates if pos not in dungeon.rooms]
    if not available:
        return None

    new_pos = random.choice(available)

    # Create room
    room = DungeonRoom(
        position=new_pos,
        room_type=room_type,
        doors={},
        enemies=generate_enemy_config(room_type) if room_type == RoomType.COMBAT else []
    )
    dungeon.rooms[new_pos] = room

    # Create door connection
    direction = get_direction(branch_point, new_pos)
    opposite = get_opposite_direction(direction)
    dungeon.rooms[branch_point].doors[direction] = new_pos
    dungeon.rooms[new_pos].doors[opposite] = branch_point

    return new_pos


def add_secret_room(dungeon: Dungeon) -> tuple[int, int]:
    """Add a secret room adjacent to existing room.

    Secret rooms have no door initially - must be bombed to reveal.
    """
    # Find eligible walls (adjacent to existing rooms, not on corners)
    eligible_walls = []

    for pos, room in dungeon.rooms.items():
        x, y = pos
        candidates = [
            ((x, y + 1), "south"),
            ((x, y - 1), "north"),
            ((x + 1, y), "east"),
            ((x - 1, y), "west")
        ]

        for secret_pos, direction in candidates:
            # Must be empty and not on main path
            if secret_pos not in dungeon.rooms and pos not in dungeon.main_path[-3:]:
                eligible_walls.append((pos, secret_pos, direction))

    if not eligible_walls:
        return None

    # Select random wall
    adjacent_room_pos, secret_pos, direction = random.choice(eligible_walls)

    # Create secret room (no doors initially)
    room = DungeonRoom(
        position=secret_pos,
        room_type=RoomType.SECRET,
        doors={},  # No doors - must be bombed
        enemies=[]
    )
    dungeon.rooms[secret_pos] = room

    # Mark wall as bombable on adjacent room
    adjacent_room = dungeon.rooms[adjacent_room_pos]
    if adjacent_room.secret_walls is None:
        adjacent_room.secret_walls = []
    adjacent_room.secret_walls.append(direction)

    return secret_pos


def validate_dungeon(dungeon: Dungeon) -> bool:
    """Validate dungeon is beatable and well-formed.

    Returns:
        True if valid, False if should regenerate
    """
    # Check main path is walkable
    if not is_path_connected(dungeon.main_path, dungeon):
        return False

    # Check all special rooms are reachable
    all_positions = (
        dungeon.treasure_rooms +
        dungeon.shop_rooms +
        [dungeon.miniboss_position, dungeon.boss_position]
    )

    for pos in all_positions:
        if not is_reachable(dungeon.start_position, pos, dungeon):
            return False

    # Check dungeon fits within reasonable bounds
    min_x = min(x for x, y in dungeon.rooms.keys())
    max_x = max(x for x, y in dungeon.rooms.keys())
    min_y = min(y for x, y in dungeon.rooms.keys())
    max_y = max(y for x, y in dungeon.rooms.keys())

    if (max_x - min_x) > 16 or (max_y - min_y) > 16:
        return False  # Too spread out

    return True
```

### Helper Functions

```python
def get_direction(from_pos: tuple[int, int], to_pos: tuple[int, int]) -> str:
    """Get direction from one position to adjacent position."""
    fx, fy = from_pos
    tx, ty = to_pos

    if tx == fx and ty == fy + 1:
        return "south"
    elif tx == fx and ty == fy - 1:
        return "north"
    elif tx == fx + 1 and ty == fy:
        return "east"
    elif tx == fx - 1 and ty == fy:
        return "west"
    else:
        raise ValueError(f"Positions not adjacent: {from_pos} -> {to_pos}")


def get_opposite_direction(direction: str) -> str:
    """Get opposite direction."""
    opposites = {
        "north": "south",
        "south": "north",
        "east": "west",
        "west": "east"
    }
    return opposites[direction]


def generate_enemy_config(room_type: RoomType) -> list[dict]:
    """Generate enemy spawn configuration for room."""
    if room_type == RoomType.COMBAT:
        num_enemies = random.randint(2, 5)
        enemy_types = ["chaser", "shooter", "orbiter", "turret", "tank"]

        return [
            {"type": random.choice(enemy_types), "count": 1}
            for _ in range(num_enemies)
        ]

    elif room_type == RoomType.MINIBOSS:
        miniboss_type = random.choice(["glutton", "hoarder", "sentinel"])
        return [{"type": miniboss_type, "count": 1}]

    else:
        return []
```

## Room Management System

### Room State Machine

Each room follows this state flow:

```
UNVISITED (never entered)
    ↓ (player enters door)
ENTERING (just arrived, spawn enemies)
    ↓ (has enemies)
COMBAT (doors locked, fighting)
    ↓ (all enemies dead)
CLEARED (doors unlocked, spawn reward)

OR from ENTERING:
    ↓ (no enemies - treasure/shop/start)
PEACEFUL (doors unlocked)
```

### RoomManager Implementation

```python
class RoomManager:
    """Manages current room state and transitions."""

    def __init__(self, dungeon: Dungeon):
        self.dungeon = dungeon
        self.current_position = dungeon.start_position
        self.current_room = dungeon.rooms[self.current_position]

    def transition_to_room(self, new_position: tuple[int, int], entry_direction: str):
        """Transition player to new room.

        Args:
            new_position: Grid coordinates of new room
            entry_direction: Direction player came from ("north", "south", etc.)
        """
        # Clean up old room
        self.despawn_current_room_entities()

        # Update position
        self.current_position = new_position
        self.current_room = self.dungeon.rooms[new_position]

        # Mark as visited
        self.current_room.visited = True

        # Spawn new room
        self.spawn_room_contents()

        # Position player at opposite door
        player_pos = self.get_door_position(get_opposite_direction(entry_direction))
        self.reposition_player(player_pos)

        # Set room state
        if self.current_room.room_type in [RoomType.START, RoomType.TREASURE, RoomType.SHOP, RoomType.SECRET]:
            self.current_room.state = RoomState.PEACEFUL
            self.unlock_all_doors()
        elif not self.current_room.cleared:
            self.current_room.state = RoomState.COMBAT
            self.lock_all_doors()
        else:
            # Revisiting cleared room
            self.current_room.state = RoomState.CLEARED
            self.unlock_all_doors()

    def despawn_current_room_entities(self):
        """Remove all entities except player from current room."""
        # Delete all enemies, projectiles, items, obstacles, doors
        for ent, (enemy,) in esper.get_components(Enemy):
            esper.delete_entity(ent)

        for ent, (proj,) in esper.get_components(Projectile):
            esper.delete_entity(ent)

        for ent, (door,) in esper.get_components(Door):
            esper.delete_entity(ent)

        # Clear obstacles (will respawn with room)
        # Keep player entity

    def spawn_room_contents(self):
        """Spawn entities for current room."""
        room = self.current_room

        # Spawn doors
        for direction, neighbor_pos in room.doors.items():
            door_pos = self.get_door_position(direction)
            self.create_door_entity(direction, neighbor_pos, door_pos)

        # Spawn obstacles from room data
        for ox, oy in room.obstacles:
            self.create_obstacle_entity(ox, oy)

        # Spawn enemies if not cleared
        if not room.cleared and room.enemies:
            for enemy_config in room.enemies:
                enemy_type = enemy_config["type"]
                # Random position in room
                x = random.uniform(10, Config.ROOM_WIDTH - 10)
                y = random.uniform(5, Config.ROOM_HEIGHT - 5)
                create_enemy(self.world_name, enemy_type, x, y)

        # Spawn shop items if shop room
        if room.room_type == RoomType.SHOP:
            self.spawn_shop_items()

        # Spawn treasure pedestal if treasure room and not taken
        if room.room_type == RoomType.TREASURE and not room.cleared:
            self.spawn_treasure_pedestal()

    def on_room_cleared(self):
        """Called when last enemy in room dies."""
        self.current_room.cleared = True
        self.current_room.state = RoomState.CLEARED

        # Unlock all doors
        self.unlock_all_doors()

        # Spawn room-clear reward
        self.spawn_room_clear_reward()

    def lock_all_doors(self):
        """Lock all doors in current room."""
        for ent, (door,) in esper.get_components(Door):
            door.locked = True

    def unlock_all_doors(self):
        """Unlock all doors in current room."""
        for ent, (door,) in esper.get_components(Door):
            door.locked = False

    def get_door_position(self, direction: str) -> tuple[float, float]:
        """Get position for door in given direction.

        Returns:
            (x, y) coordinates for door center
        """
        if direction == "north":
            return (Config.ROOM_WIDTH / 2, 1.0)
        elif direction == "south":
            return (Config.ROOM_WIDTH / 2, Config.ROOM_HEIGHT - 1.0)
        elif direction == "east":
            return (Config.ROOM_WIDTH - 1.0, Config.ROOM_HEIGHT / 2)
        elif direction == "west":
            return (1.0, Config.ROOM_HEIGHT / 2)
```

## Door System

### Door Component & Entities

Doors are entities with collision that trigger room transitions:

```python
class Door:
    """Door component."""
    direction: str  # "north", "south", "east", "west"
    locked: bool = True
    leads_to: tuple[int, int]  # Destination room coordinates
```

### Door Visuals

- **Unlocked door**: `▯` (white/cyan)
- **Locked door**: `▮` (red/dark gray)
- **Door positions**: Center of each wall with door connection

### Collision & Transition

Modified CollisionSystem detects player-door collision:

```python
# In CollisionSystem.process()
for player_ent, (player, pos, collider) in esper.get_components(Player, Position, Collider):
    for door_ent, (door, door_pos, door_collider) in esper.get_components(Door, Position, Collider):
        if not door.locked and check_collision(pos, collider, door_pos, door_collider):
            # Trigger room transition
            self.room_manager.transition_to_room(door.leads_to, door.direction)
            break
```

## Currency & Reward Systems

### Currency Component

```python
class Currency:
    """Player resources."""
    coins: int = 0
    bombs: int = 3
    keys: int = 0  # Future use
```

Added to player entity on creation. Persists across room transitions.

### Room Clear Rewards

When last enemy dies in a room:

```python
ROOM_CLEAR_REWARDS = {
    "coins": 0.60,      # 60% chance: spawn 3-6 coins
    "heart": 0.25,      # 25% chance: spawn half-heart
    "stat_boost": 0.10, # 10% chance: spawn small stat item
    "bomb": 0.05,       # 5% chance: spawn 1-2 bombs
}

def spawn_room_clear_reward():
    """Spawn reward at room center based on weighted random."""
    roll = random.random()

    if roll < 0.60:
        # Spawn coins
        num_coins = random.randint(3, 6)
        for _ in range(num_coins):
            x = Config.ROOM_WIDTH / 2 + random.uniform(-2, 2)
            y = Config.ROOM_HEIGHT / 2 + random.uniform(-2, 2)
            spawn_coin(world_name, x, y)

    elif roll < 0.85:  # 0.60 + 0.25
        # Spawn heart
        spawn_heart(world_name, Config.ROOM_WIDTH / 2, Config.ROOM_HEIGHT / 2)

    elif roll < 0.95:  # 0.85 + 0.10
        # Spawn small stat boost item
        stat_item = random.choice(["mini_mushroom", "speed_boost", "fire_rate_up"])
        create_item(world_name, stat_item, Config.ROOM_WIDTH / 2, Config.ROOM_HEIGHT / 2)

    else:  # 0.95 to 1.0
        # Spawn bombs
        num_bombs = random.randint(1, 2)
        for i in range(num_bombs):
            x = Config.ROOM_WIDTH / 2 + i
            create_bomb_pickup(world_name, x, Config.ROOM_HEIGHT / 2)
```

### Enemy Drops

Enemies have additional drop chances (independent of room-clear rewards):

```python
# In CollisionSystem when enemy dies:
if random.random() < 0.15:
    # 15% chance to drop 1-2 coins
    num_coins = random.randint(1, 2)
    for _ in range(num_coins):
        spawn_coin(world_name, enemy_pos.x, enemy_pos.y)

# Existing item drop logic (15% chance) remains unchanged
```

### Coin Pickup

```python
class Coin:
    """Coin pickup component."""
    value: int = 1  # Coin worth (pennies=1, nickels=5, etc.)

# In ItemPickupSystem (or new CoinPickupSystem):
for player_ent, (player, player_pos, currency) in esper.get_components(Player, Position, Currency):
    for coin_ent, (coin, coin_pos) in esper.get_components(Coin, Position):
        if distance(player_pos, coin_pos) < Config.ITEM_PICKUP_RADIUS:
            currency.coins += coin.value
            esper.delete_entity(coin_ent)
            # Play coin sound, show +1 notification
```

### Bomb Pickup

```python
class BombPickup:
    """Bomb pickup component."""
    quantity: int = 1  # Number of bombs

# In ItemPickupSystem:
for player_ent, (player, player_pos, currency) in esper.get_components(Player, Position, Currency):
    for pickup_ent, (pickup, pickup_pos) in esper.get_components(BombPickup, Position):
        if distance(player_pos, pickup_pos) < Config.ITEM_PICKUP_RADIUS:
            currency.bombs += pickup.quantity
            esper.delete_entity(pickup_ent)
            # Show +N bombs notification
```

## Bomb System

### Bomb Mechanics

Players use bombs to:
1. Reveal secret rooms by destroying bombable walls
2. Damage enemies (1 heart) in blast radius
3. Damage self if too close (1 heart)

### Bomb Usage Flow

```python
# In InputSystem - add bomb key
class InputSystem(esper.Processor):
    def __init__(self):
        self.bomb_pressed = False  # New input flag

    def set_input(self, move_x, move_y, shoot_x, shoot_y, bomb_pressed):
        """Update with bomb input."""
        self.bomb_pressed = bomb_pressed

# In BombSystem:
class BombSystem(esper.Processor):
    """Handles bomb placement and explosions."""

    def process(self):
        dt = self.dt

        # Check for bomb placement input
        if self.input_system.bomb_pressed:
            for player_ent, (player, pos, currency) in esper.get_components(Player, Position, Currency):
                if currency.bombs > 0:
                    # Place bomb at player position
                    self.place_bomb(pos.x, pos.y, player_ent)
                    currency.bombs -= 1
                    # Reset input flag
                    self.input_system.bomb_pressed = False

        # Update all active bombs
        for bomb_ent, (bomb, pos) in esper.get_components(Bomb, Position):
            bomb.fuse_time -= dt

            # Visual: Flash faster as fuse runs down
            if bomb.fuse_time <= 0:
                self.explode_bomb(bomb_ent, pos, bomb)

    def place_bomb(self, x: float, y: float, owner: int):
        """Create bomb entity at position."""
        bomb_ent = esper.create_entity()
        esper.add_component(bomb_ent, Position(x, y))
        esper.add_component(bomb_ent, Sprite("●", "red"))
        esper.add_component(bomb_ent, Bomb(
            fuse_time=1.5,
            blast_radius=2.0,
            owner=owner
        ))

    def explode_bomb(self, bomb_ent: int, pos: Position, bomb: Bomb):
        """Handle bomb explosion."""
        # Show explosion effect
        self.spawn_explosion_effect(pos.x, pos.y)

        # Check for secret walls to reveal
        self.check_secret_walls(pos, bomb.blast_radius)

        # Damage entities in blast radius
        self.damage_entities_in_radius(pos, bomb.blast_radius)

        # Remove bomb
        esper.delete_entity(bomb_ent)

    def check_secret_walls(self, pos: Position, radius: float):
        """Check if explosion reveals secret room."""
        # Get current room
        room = self.room_manager.current_room

        if not room.secret_walls:
            return

        # Check each secret wall direction
        for direction in room.secret_walls:
            wall_pos = self.room_manager.get_door_position(direction)

            if distance(pos, Position(wall_pos[0], wall_pos[1])) <= radius:
                # Reveal secret room!
                self.reveal_secret_room(direction)

    def reveal_secret_room(self, direction: str):
        """Create door to secret room."""
        # Find secret room position
        current_pos = self.room_manager.current_position
        x, y = current_pos

        if direction == "north":
            secret_pos = (x, y - 1)
        elif direction == "south":
            secret_pos = (x, y + 1)
        elif direction == "east":
            secret_pos = (x + 1, y)
        elif direction == "west":
            secret_pos = (x - 1, y)

        # Add door to current room
        current_room = self.room_manager.current_room
        current_room.doors[direction] = secret_pos

        # Add door to secret room
        secret_room = self.room_manager.dungeon.rooms[secret_pos]
        opposite = get_opposite_direction(direction)
        secret_room.doors[opposite] = current_pos

        # Create door entity (unlocked)
        door_pos = self.room_manager.get_door_position(direction)
        door_ent = esper.create_entity()
        esper.add_component(door_ent, Position(door_pos[0], door_pos[1]))
        esper.add_component(door_ent, Door(
            direction=direction,
            locked=False,
            leads_to=secret_pos
        ))
        esper.add_component(door_ent, Sprite("▯", "cyan"))
        esper.add_component(door_ent, Collider(0.5))

        # Show notification
        self.notification = "Secret room revealed!"

    def damage_entities_in_radius(self, center: Position, radius: float):
        """Deal 1 heart damage to entities in blast radius."""
        for ent, (pos, health) in esper.get_components(Position, Health):
            if distance(center, pos) <= radius:
                health.current -= 1.0  # 1 heart damage
```

### Secret Wall Detection

**Normal state:** Bombable walls appear identical to regular walls (`#`)

**With "Spelunker's Sense" status effect:**
- Bombable walls show as `≈` or different color
- Status granted by "Treasure Map" item or shop purchase
- Lasts 1 room or 30 seconds
- Icon in HUD: `👁️`

```python
class StatusEffect:
    """Status effect component."""
    effect_type: str  # "spelunker_sense", etc.
    duration: float  # Seconds remaining or -1 for room-duration
    room_duration: bool = False  # If True, expires on room transition

# In RenderSystem - modify wall rendering:
def render_walls(self):
    """Render walls with secret wall hints."""
    has_spelunker = False

    # Check if player has Spelunker's Sense
    for player_ent, (player, effects) in esper.get_components(Player, StatusEffect):
        if effects.effect_type == "spelunker_sense":
            has_spelunker = True
            break

    # Render walls
    current_room = self.room_manager.current_room

    # Render secret walls differently if player has sense
    if has_spelunker and current_room.secret_walls:
        for direction in current_room.secret_walls:
            wall_pos = self.get_secret_wall_render_position(direction)
            # Render as ≈ instead of #
            grid[wall_pos[1]][wall_pos[0]] = {'char': '≈', 'color': 'yellow'}
```

## Shop System

### Shop Room Layout

```
┌──────────────────────────────┐
│                              │
│    [Item1]  [Item2]  [Item3] │
│      $10      $8       $15   │
│                              │
│          Shopkeeper          │
│              S               │
│                              │
└──────────────────────────────┘
```

Shop rooms contain:
- 3-4 item pedestals with prices
- Shopkeeper NPC (decorative, doesn't move)
- Entry door at bottom

### Shop Item Pricing

```python
SHOP_ITEM_PRICES = {
    # Cheap items (5-7 coins)
    "speed_boost": 5,
    "mini_mushroom": 6,
    "fire_rate_up": 7,

    # Medium items (8-12 coins)
    "triple_shot": 10,
    "homing_shots": 10,
    "piercing_tears": 12,

    # Expensive items (13-15 coins)
    "magic_mushroom": 15,
    "brimstone": 15,

    # Consumables
    "bomb_x3": 5,  # 3 bombs
    "treasure_map": 8,  # Reveals secret walls
    "heart": 3,
}

def generate_shop_items() -> list[str]:
    """Select 3-4 random items for shop."""
    all_items = list(SHOP_ITEM_PRICES.keys())
    num_items = random.randint(3, 4)
    return random.sample(all_items, num_items)
```

### Shop Purchase Mechanics

```python
class ShopItem:
    """Shop item component."""
    item_name: str
    price: int
    purchased: bool = False

# In ItemPickupSystem (or ShopSystem):
def check_shop_purchases(self):
    """Check if player can buy shop items."""
    for player_ent, (player, player_pos, currency) in esper.get_components(Player, Position, Currency):
        for item_ent, (shop_item, item_pos, item) in esper.get_components(ShopItem, Position, Item):
            if shop_item.purchased:
                continue

            # Check if player touching item
            if distance(player_pos, item_pos) < Config.ITEM_PICKUP_RADIUS:
                if currency.coins >= shop_item.price:
                    # Purchase!
                    currency.coins -= shop_item.price
                    shop_item.purchased = True

                    # Apply item effects (use existing item pickup logic)
                    self.apply_item(player_ent, item)

                    # Remove from shop
                    esper.delete_entity(item_ent)

                    # Show notification
                    self.notification = f"Purchased {shop_item.item_name}!"
                else:
                    # Can't afford
                    self.notification = "Not enough coins!"
                    # Play error sound
```

## Mini-Boss System

### Mini-Boss Types

```python
class MiniBossType(Enum):
    GLUTTON = "glutton"    # Enhanced tank
    HOARDER = "hoarder"    # Enhanced shooter
    SENTINEL = "sentinel"  # Enhanced orbiter

MINIBOSS_DATA = {
    "glutton": {
        "hp": 30,
        "sprite": "G",
        "color": "red",
        "patterns": ["shockwave"],
        "pattern_cooldowns": {"shockwave": 1.5},
        "guaranteed_drop": "damage_upgrade",
        "speed": 2.0,
    },
    "hoarder": {
        "hp": 25,
        "sprite": "H",
        "color": "yellow",
        "patterns": ["spread", "ring"],
        "pattern_cooldowns": {"spread": 2.0, "ring": 2.5},
        "guaranteed_drop": "coins_and_item",  # Special: 10-15 coins + random item
        "speed": 3.0,
    },
    "sentinel": {
        "hp": 35,
        "sprite": "T",
        "color": "cyan",
        "patterns": ["radial_burst"],
        "pattern_cooldowns": {"radial_burst": 3.0},
        "guaranteed_drop": "treasure_map",  # Or bomb-related item
        "speed": 4.0,
        "special": "teleport",  # Teleports every 5 seconds
    },
}
```

### Mini-Boss Component

```python
class MiniBoss:
    """Mini-boss component."""
    boss_type: str  # "glutton", "hoarder", "sentinel"
    guaranteed_drop: str  # Item to drop on death
    teleport_timer: float = 5.0  # For sentinel
```

### Mini-Boss Behavior

Mini-bosses use existing AI and shooting systems, but with enhanced stats and guaranteed drops:

```python
def create_miniboss(world: str, boss_type: str, x: float, y: float) -> int:
    """Create mini-boss entity."""
    data = MINIBOSS_DATA[boss_type]

    entity = esper.create_entity()
    esper.add_component(entity, Position(x, y))
    esper.add_component(entity, Velocity(0.0, 0.0))
    esper.add_component(entity, Health(data["hp"], data["hp"]))
    esper.add_component(entity, Sprite(data["sprite"], data["color"]))
    esper.add_component(entity, Enemy(boss_type))
    esper.add_component(entity, Collider(0.4))
    esper.add_component(entity, Stats(
        damage=2.0,  # Higher damage than regular enemies
        speed=data["speed"],
        fire_rate=1.0,
        shot_speed=8.0
    ))

    # AI with patterns
    ai = AIBehavior(behavior_type="shooter")  # Or "chaser" for glutton
    for pattern_name in data["patterns"]:
        ai.pattern_cooldowns[pattern_name] = data["pattern_cooldowns"][pattern_name]
    esper.add_component(entity, ai)

    # Mini-boss marker
    esper.add_component(entity, MiniBoss(
        boss_type=boss_type,
        guaranteed_drop=data["guaranteed_drop"]
    ))

    return entity

# In CollisionSystem - mini-boss death:
if esper.has_component(enemy, MiniBoss):
    miniboss = esper.component_for_entity(enemy, MiniBoss)

    # Spawn guaranteed drop
    if miniboss.guaranteed_drop == "coins_and_item":
        # Special: spawn coins + item
        for _ in range(random.randint(10, 15)):
            spawn_coin(world, pos.x + random.uniform(-2, 2), pos.y + random.uniform(-2, 2))
        spawn_random_item(world, pos.x, pos.y)
    else:
        # Spawn specific item
        create_item(world, miniboss.guaranteed_drop, pos.x, pos.y)

    # Extra reward (heart + coins)
    spawn_heart(world, pos.x - 1, pos.y)
    for _ in range(5):
        spawn_coin(world, pos.x + random.uniform(-3, 3), pos.y + random.uniform(-3, 3))
```

### Sentinel Teleport Mechanic

```python
class MiniBossSystem(esper.Processor):
    """Special mini-boss behaviors."""

    def process(self):
        dt = self.dt

        for ent, (miniboss, pos, enemy) in esper.get_components(MiniBoss, Position, Enemy):
            if miniboss.boss_type == "sentinel":
                miniboss.teleport_timer -= dt

                if miniboss.teleport_timer <= 0:
                    # Teleport to random position
                    new_x = random.uniform(10, Config.ROOM_WIDTH - 10)
                    new_y = random.uniform(5, Config.ROOM_HEIGHT - 5)
                    pos.x = new_x
                    pos.y = new_y

                    # Reset timer
                    miniboss.teleport_timer = 5.0

                    # Fire radial burst immediately after teleport
                    # (Handled by enemy shooting system)
```

## Mini-Map System

### Mini-Map Display

Rendered in top-right corner of screen:

```
╔═══════╗
║ □ ■ □ ║  Legend:
║ □ ◆ ■ ║  ■ = Visited room
║   ■   ║  ◆ = Current room (you are here)
╚═══════╝  □ = Adjacent unvisited (door exists)
           (blank) = Unknown/no connection
```

### Mini-Map Data Structure

```python
class MiniMap:
    """Mini-map state."""
    visible_rooms: set[tuple[int, int]]  # Rooms player has visited
    current_position: tuple[int, int]

    def reveal_room(self, x: int, y: int):
        """Mark room as visited."""
        self.visible_rooms.add((x, y))

    def get_display_bounds(self) -> tuple[int, int, int, int]:
        """Get min/max coordinates for display (±3 from current)."""
        cx, cy = self.current_position
        return (cx - 3, cy - 3, cx + 3, cy + 3)

    def should_show_room(self, x: int, y: int) -> bool:
        """Check if room should be visible on map."""
        # Show if visited
        if (x, y) in self.visible_rooms:
            return True

        # Show if adjacent to current room and has door connection
        cx, cy = self.current_position
        if abs(x - cx) + abs(y - cy) == 1:  # Manhattan distance 1
            current_room = dungeon.rooms[(cx, cy)]
            # Check if door exists to this room
            for neighbor_pos in current_room.doors.values():
                if neighbor_pos == (x, y):
                    return True

        return False
```

### Mini-Map Rendering

```python
class MiniMapSystem(esper.Processor):
    """Renders mini-map overlay."""

    def render(self, minimap: MiniMap, dungeon: Dungeon) -> list[str]:
        """Generate mini-map display lines.

        Returns:
            List of strings to render in corner
        """
        lines = []
        lines.append("╔═══════╗")

        # Get display bounds (7x7 grid centered on current)
        min_x, min_y, max_x, max_y = minimap.get_display_bounds()

        for y in range(min_y, max_y + 1):
            row = "║"
            for x in range(min_x, max_x + 1):
                if (x, y) == minimap.current_position:
                    row += "◆"  # Current room
                elif (x, y) in minimap.visible_rooms:
                    row += "■"  # Visited room
                elif minimap.should_show_room(x, y):
                    row += "□"  # Adjacent unvisited
                else:
                    row += " "  # Unknown
            row += "║"
            lines.append(row)

        lines.append("╚═══════╝")
        return lines

# In RenderSystem - add mini-map to top-right corner:
def render(self, world_name: str) -> list[list[dict]]:
    """Render game with mini-map overlay."""
    # ... existing rendering ...

    # Get mini-map
    minimap_lines = self.minimap_system.render(self.minimap, self.dungeon)

    # Overlay in top-right corner
    start_x = Config.ROOM_WIDTH - 10
    for i, line in enumerate(minimap_lines):
        for j, char in enumerate(line):
            if start_x + j < Config.ROOM_WIDTH:
                grid[i][start_x + j] = {'char': char, 'color': 'white'}

    return grid
```

### Mini-Map Updates

```python
# In RoomManager.transition_to_room():
def transition_to_room(self, new_position: tuple[int, int], entry_direction: str):
    # ... existing transition logic ...

    # Update mini-map
    self.minimap.reveal_room(new_position[0], new_position[1])
    self.minimap.current_position = new_position
```

## Configuration Constants

Add to `src/config.py`:

```python
# Dungeon generation
DUNGEON_MIN_SIZE: int = 12
DUNGEON_MAX_SIZE: int = 18
DUNGEON_MAIN_PATH_LENGTH: int = 11  # Rooms on critical path

# Special room counts
TREASURE_ROOM_COUNT_MIN: int = 2
TREASURE_ROOM_COUNT_MAX: int = 3
SHOP_COUNT_MIN: int = 1
SHOP_COUNT_MAX: int = 2
SECRET_COUNT_MIN: int = 1
SECRET_COUNT_MAX: int = 2

# Room clear rewards (probabilities sum to 1.0)
REWARD_COINS_CHANCE: float = 0.60
REWARD_HEART_CHANCE: float = 0.25
REWARD_STAT_BOOST_CHANCE: float = 0.10
REWARD_BOMBS_CHANCE: float = 0.05

# Currency
STARTING_BOMBS: int = 3
STARTING_COINS: int = 0
ENEMY_COIN_DROP_CHANCE: float = 0.15

# Bombs
BOMB_FUSE_TIME: float = 1.5  # Seconds
BOMB_BLAST_RADIUS: float = 2.0  # Tiles
BOMB_DAMAGE: float = 1.0  # Hearts

# Mini-map
MINIMAP_DISPLAY_RADIUS: int = 3  # Rooms visible in each direction
```

## Testing Strategy

### Unit Tests

**DungeonGenerator Tests (15 tests):**
```python
def test_dungeon_generates_within_target_size():
    """Verify dungeon has 12-18 rooms."""
    dungeon = generate_dungeon(15)
    assert DUNGEON_MIN_SIZE <= len(dungeon.rooms) <= DUNGEON_MAX_SIZE

def test_main_path_connects_start_to_boss():
    """Verify walkable path exists from start to boss."""
    dungeon = generate_dungeon(15)
    assert is_path_connected(dungeon.main_path, dungeon)
    assert dungeon.main_path[0] == dungeon.start_position
    assert dungeon.main_path[-1] == dungeon.boss_position

def test_special_rooms_placed_correctly():
    """Verify correct counts of special rooms."""
    dungeon = generate_dungeon(15)
    assert 2 <= len(dungeon.treasure_rooms) <= 3
    assert 1 <= len(dungeon.shop_rooms) <= 2
    assert 1 <= len(dungeon.secret_rooms) <= 2

def test_all_rooms_connected():
    """Verify no isolated rooms."""
    dungeon = generate_dungeon(15)
    reachable = get_reachable_rooms(dungeon.start_position, dungeon)
    assert len(reachable) == len(dungeon.rooms)

def test_secret_rooms_adjacent_to_regular():
    """Verify secret rooms properly placed."""
    dungeon = generate_dungeon(15)
    for secret_pos in dungeon.secret_rooms:
        # Should have exactly one adjacent room with secret wall
        adjacent_count = 0
        for room_pos, room in dungeon.rooms.items():
            if room.secret_walls and is_adjacent(room_pos, secret_pos):
                adjacent_count += 1
        assert adjacent_count == 1

def test_dungeon_fits_within_bounds():
    """Verify dungeon doesn't spread too far."""
    dungeon = generate_dungeon(15)
    min_x = min(x for x, y in dungeon.rooms.keys())
    max_x = max(x for x, y in dungeon.rooms.keys())
    min_y = min(y for x, y in dungeon.rooms.keys())
    max_y = max(y for x, y in dungeon.rooms.keys())

    assert (max_x - min_x) <= 16
    assert (max_y - min_y) <= 16

def test_miniboss_on_main_path():
    """Verify mini-boss placed at ~40% of main path."""
    dungeon = generate_dungeon(15)
    assert dungeon.miniboss_position in dungeon.main_path
    index = dungeon.main_path.index(dungeon.miniboss_position)
    expected = int(len(dungeon.main_path) * 0.4)
    assert abs(index - expected) <= 1
```

**RoomManager Tests (12 tests):**
```python
def test_room_state_transitions():
    """Test ENTERING → COMBAT → CLEARED flow."""
    manager = RoomManager(test_dungeon)
    room = manager.current_room

    # Initially ENTERING
    assert room.state == RoomState.ENTERING

    # Spawn enemies → COMBAT
    manager.spawn_room_contents()
    assert room.state == RoomState.COMBAT

    # Kill enemies → CLEARED
    kill_all_enemies()
    manager.on_room_cleared()
    assert room.state == RoomState.CLEARED

def test_doors_lock_on_enemy_spawn():
    """Verify doors locked when enemies present."""
    manager = RoomManager(combat_dungeon)
    manager.spawn_room_contents()

    for ent, (door,) in esper.get_components(Door):
        assert door.locked == True

def test_doors_unlock_on_clear():
    """Verify doors unlock when room cleared."""
    manager = RoomManager(combat_dungeon)
    manager.spawn_room_contents()
    kill_all_enemies()
    manager.on_room_cleared()

    for ent, (door,) in esper.get_components(Door):
        assert door.locked == False

def test_room_transition_repositions_player():
    """Verify player spawns at opposite door."""
    manager = RoomManager(test_dungeon)
    player_pos = get_player_position()

    # Enter north door
    manager.transition_to_room((0, 1), "north")

    # Player should be at south door of new room
    new_pos = get_player_position()
    expected = manager.get_door_position("south")
    assert abs(new_pos.x - expected[0]) < 0.1
    assert abs(new_pos.y - expected[1]) < 0.1

def test_room_clear_spawns_reward():
    """Verify reward entity created on clear."""
    manager = RoomManager(combat_dungeon)
    manager.spawn_room_contents()

    kill_all_enemies()
    manager.on_room_cleared()

    # Should have spawned coins, heart, item, or bombs
    rewards = (
        list(esper.get_components(Coin)) +
        list(esper.get_components(Heart)) +
        list(esper.get_components(Item)) +
        list(esper.get_components(BombPickup))
    )
    assert len(rewards) > 0

def test_revisiting_cleared_room_stays_cleared():
    """Verify cleared rooms don't respawn enemies."""
    manager = RoomManager(test_dungeon)
    room_pos = (1, 0)

    # Visit and clear room
    manager.transition_to_room(room_pos, "east")
    kill_all_enemies()
    manager.on_room_cleared()

    # Leave and return
    manager.transition_to_room((0, 0), "west")
    manager.transition_to_room(room_pos, "east")

    # No enemies should spawn
    enemy_count = len(list(esper.get_components(Enemy)))
    assert enemy_count == 0
    assert manager.current_room.state == RoomState.CLEARED
```

**CurrencySystem Tests (8 tests):**
```python
def test_currency_persists_across_rooms():
    """Verify coins/bombs carry over."""
    player = create_player_with_currency(coins=10, bombs=5)
    manager = RoomManager(test_dungeon)

    manager.transition_to_room((1, 0), "east")

    currency = esper.component_for_entity(player, Currency)
    assert currency.coins == 10
    assert currency.bombs == 5

def test_coin_drops_from_enemies():
    """Verify 15% drop chance works."""
    drops = 0
    for _ in range(1000):
        enemy = create_enemy("test", "chaser", 10, 10)
        kill_enemy(enemy)
        if has_coin_at_position(10, 10):
            drops += 1

    # Should be ~150 drops (15%)
    assert 120 < drops < 180  # Allow variance

def test_bomb_consumption():
    """Verify using bomb decrements count."""
    player = create_player_with_currency(bombs=3)
    currency = esper.component_for_entity(player, Currency)

    place_bomb(player)
    assert currency.bombs == 2

def test_insufficient_funds_shop():
    """Verify can't buy without enough coins."""
    player = create_player_with_currency(coins=5)
    shop_item = create_shop_item("magic_mushroom", price=15)

    result = attempt_purchase(player, shop_item)
    assert result == False

    currency = esper.component_for_entity(player, Currency)
    assert currency.coins == 5  # Unchanged

def test_coin_pickup_adds_to_total():
    """Verify picking up coins adds to currency."""
    player = create_player_with_currency(coins=5)
    coin = spawn_coin("test", 10, 10)

    pickup_coin(player, coin)

    currency = esper.component_for_entity(player, Currency)
    assert currency.coins == 6
```

**BombSystem Tests (10 tests):**
```python
def test_bomb_placement():
    """Verify bomb entity spawns at player position."""
    player = create_player("test", 20, 10)
    bomb_system = BombSystem()

    bomb_system.place_bomb(20, 10, player)

    bombs = list(esper.get_components(Bomb, Position))
    assert len(bombs) == 1
    bomb_pos = bombs[0][1]
    assert bomb_pos.x == 20
    assert bomb_pos.y == 10

def test_fuse_countdown():
    """Verify fuse_time decrements."""
    bomb = create_bomb(20, 10)
    bomb_comp = esper.component_for_entity(bomb, Bomb)
    initial_fuse = bomb_comp.fuse_time

    bomb_system = BombSystem()
    bomb_system.dt = 0.5
    bomb_system.process()

    assert bomb_comp.fuse_time == initial_fuse - 0.5

def test_explosion_reveals_secret():
    """Verify bomb creates door if secret adjacent."""
    dungeon = create_test_dungeon_with_secret()
    manager = RoomManager(dungeon)

    # Current room has secret wall to north
    bomb = create_bomb(30, 2)  # Near north wall

    bomb_system = BombSystem()
    bomb_system.room_manager = manager
    bomb_system.explode_bomb(bomb, Position(30, 2), Bomb())

    # Should have created door
    current_room = manager.current_room
    assert "north" in current_room.doors

def test_explosion_no_secret():
    """Verify nothing happens on regular walls."""
    dungeon = create_test_dungeon_no_secrets()
    manager = RoomManager(dungeon)

    bomb = create_bomb(30, 2)
    initial_door_count = len(manager.current_room.doors)

    bomb_system = BombSystem()
    bomb_system.room_manager = manager
    bomb_system.explode_bomb(bomb, Position(30, 2), Bomb())

    # No new doors
    assert len(manager.current_room.doors) == initial_door_count

def test_explosion_damages_entities():
    """Verify blast deals 1 heart damage."""
    enemy = create_enemy("test", "chaser", 20, 10)
    enemy_health = esper.component_for_entity(enemy, Health)
    initial_hp = enemy_health.current

    bomb = create_bomb(20, 10)
    bomb_system = BombSystem()
    bomb_system.explode_bomb(bomb, Position(20, 10), Bomb())

    assert enemy_health.current == initial_hp - 1.0

def test_cant_place_bomb_without_bombs():
    """Verify can't place if bombs == 0."""
    player = create_player_with_currency(bombs=0)
    bomb_system = BombSystem()

    bomb_system.attempt_place_bomb(player)

    bombs = list(esper.get_components(Bomb))
    assert len(bombs) == 0
```

**MiniMap Tests (7 tests):**
```python
def test_minimap_shows_visited_rooms():
    """Verify visited rooms rendered as ■."""
    minimap = MiniMap()
    minimap.visible_rooms = {(0, 0), (1, 0), (0, 1)}
    minimap.current_position = (0, 0)

    lines = render_minimap(minimap, test_dungeon)

    # Should contain ■ for visited rooms
    assert "■" in "".join(lines)

def test_current_room_highlighted():
    """Verify current position marked as ◆."""
    minimap = MiniMap()
    minimap.current_position = (0, 0)
    minimap.visible_rooms = {(0, 0)}

    lines = render_minimap(minimap, test_dungeon)

    assert "◆" in "".join(lines)

def test_adjacent_rooms_shown():
    """Verify rooms with doors display as □."""
    dungeon = create_test_dungeon()
    minimap = MiniMap()
    minimap.current_position = (0, 0)
    minimap.visible_rooms = {(0, 0)}

    # Room (1, 0) has door to current room
    lines = render_minimap(minimap, dungeon)

    # Should show adjacent unvisited
    assert "□" in "".join(lines)

def test_unvisited_rooms_hidden():
    """Verify unknown rooms are blank."""
    minimap = MiniMap()
    minimap.current_position = (0, 0)
    minimap.visible_rooms = {(0, 0)}

    lines = render_minimap(minimap, test_dungeon)

    # Most of grid should be spaces (unknown)
    total_chars = sum(len(line) for line in lines)
    space_count = sum(line.count(" ") for line in lines)
    assert space_count > total_chars * 0.6  # Mostly unknown
```

**MiniBoss Tests (6 tests):**
```python
def test_miniboss_higher_hp():
    """Verify mini-bosses have enhanced HP."""
    miniboss = create_miniboss("test", "glutton", 30, 10)
    health = esper.component_for_entity(miniboss, Health)

    regular_enemy = create_enemy("test", "tank", 30, 10)
    regular_health = esper.component_for_entity(regular_enemy, Health)

    assert health.max_hp > regular_health.max_hp

def test_miniboss_guaranteed_drop():
    """Verify mini-boss drops specified item."""
    miniboss = create_miniboss("test", "hoarder", 30, 10)

    kill_enemy(miniboss)

    # Should have spawned coins and item
    coins = list(esper.get_components(Coin))
    items = list(esper.get_components(Item))
    assert len(coins) >= 10  # 10-15 coins
    assert len(items) >= 1  # Random item

def test_sentinel_teleports():
    """Verify Sentinel teleports periodically."""
    miniboss = create_miniboss("test", "sentinel", 30, 10)
    pos = esper.component_for_entity(miniboss, Position)
    initial_x = pos.x

    miniboss_system = MiniBossSystem()
    miniboss_system.dt = 5.1  # Exceed teleport timer
    miniboss_system.process()

    # Position should have changed
    assert pos.x != initial_x
```

### Integration Tests (8 tests)

```python
def test_full_dungeon_run():
    """Generate dungeon, clear multiple rooms, verify progression."""
    dungeon = generate_dungeon(15)
    manager = RoomManager(dungeon)
    player = create_player("test", 30, 10)

    # Clear starting room (should be peaceful)
    assert manager.current_room.room_type == RoomType.START

    # Move to first combat room
    first_door = list(manager.current_room.doors.keys())[0]
    next_pos = manager.current_room.doors[first_door]
    manager.transition_to_room(next_pos, first_door)

    # Should have enemies and locked doors
    enemies = list(esper.get_components(Enemy))
    assert len(enemies) > 0

    doors = list(esper.get_components(Door))
    assert all(door.locked for _, (door,) in doors)

    # Clear room
    kill_all_enemies()
    manager.on_room_cleared()

    # Doors should unlock
    assert all(not door.locked for _, (door,) in esper.get_components(Door))

def test_bomb_secret_room_flow():
    """Place bomb, reveal secret, enter and clear."""
    dungeon = create_dungeon_with_known_secret()
    manager = RoomManager(dungeon)
    player = create_player_with_currency(bombs=1)

    # Place bomb near secret wall
    secret_direction = manager.current_room.secret_walls[0]
    wall_pos = manager.get_door_position(secret_direction)
    place_bomb_near(player, wall_pos)

    # Wait for explosion
    wait_for_explosion()

    # Secret should be revealed
    assert secret_direction in manager.current_room.doors

    # Enter secret room
    manager.transition_to_room(
        manager.current_room.doors[secret_direction],
        secret_direction
    )

    # Should be in secret room
    assert manager.current_room.room_type == RoomType.SECRET

def test_shop_purchase_flow():
    """Collect coins, enter shop, buy item."""
    dungeon = create_dungeon_with_shop()
    manager = RoomManager(dungeon)
    player = create_player_with_currency(coins=15)

    # Navigate to shop
    navigate_to_room_type(manager, RoomType.SHOP)

    # Shop should have items
    shop_items = list(esper.get_components(ShopItem))
    assert len(shop_items) >= 3

    # Buy cheapest item
    cheapest = min(shop_items, key=lambda x: x[1].price)
    item_ent, shop_item = cheapest

    currency = esper.component_for_entity(player, Currency)
    initial_coins = currency.coins

    attempt_purchase(player, item_ent)

    # Coins deducted
    assert currency.coins == initial_coins - shop_item.price

    # Item removed from shop
    assert not esper.entity_exists(item_ent)

def test_mini_boss_defeat_and_reward():
    """Fight mini-boss, verify guaranteed drop."""
    dungeon = generate_dungeon(15)
    manager = RoomManager(dungeon)
    player = create_player("test", 30, 10)

    # Navigate to mini-boss room
    navigate_to_position(manager, dungeon.miniboss_position)

    # Should have mini-boss
    minibosses = list(esper.get_components(MiniBoss))
    assert len(minibosses) == 1

    miniboss_ent = minibosses[0][0]
    miniboss_comp = minibosses[0][1]

    # Defeat mini-boss
    kill_enemy(miniboss_ent)

    # Verify guaranteed drop spawned
    items = list(esper.get_components(Item))
    item_names = [item.name for _, (item,) in items]
    assert miniboss_comp.guaranteed_drop in item_names

    # Verify extra rewards
    hearts = list(esper.get_components(Heart))
    coins = list(esper.get_components(Coin))
    assert len(hearts) >= 1
    assert len(coins) >= 5
```

## UI Updates

### HUD Enhancement

Add to existing HUD display:

```
╔══════════════════════════════════════╗
║ Health: ♥♥♥♡♡♡                      ║
║ Coins: 💰 12   Bombs: 💣 5   Keys: 🔑 0║
║                                      ║
║ Controls: WASD=Move  Arrows=Shoot   ║
║           B=Bomb      Q=Quit         ║
╚══════════════════════════════════════╝
```

### Notification System Enhancement

Add notification area below HUD for:
- Item pickups: "Picked up: Magic Mushroom"
- Shop purchases: "Purchased Triple Shot"
- Secret reveals: "Secret room revealed!"
- Insufficient funds: "Not enough coins!"
- Bomb placement: "Bomb placed"

Notifications display for 2 seconds (using existing notification system).

## File Structure

New files to create:

```
src/
├── game/
│   └── dungeon.py           # DungeonGenerator, Dungeon, DungeonRoom classes
│
├── systems/
│   ├── room_manager.py      # RoomManager system
│   ├── bomb.py              # BombSystem
│   ├── minimap.py           # MiniMapSystem
│   ├── miniboss.py          # MiniBossSystem (special behaviors)
│   └── shop.py              # ShopSystem (purchase logic)
│
├── entities/
│   ├── bombs.py             # Bomb entity creation
│   ├── miniboss.py          # Mini-boss entity creation
│   └── currency.py          # Coin/bomb pickup entity creation
│
├── data/
│   └── miniboss.py          # MINIBOSS_DATA definitions
│
└── components/
    └── dungeon.py           # Currency, Door, Bomb, MiniBoss, MiniMap components

tests/
├── test_dungeon_generator.py
├── test_room_manager.py
├── test_currency_system.py
├── test_bomb_system.py
├── test_minimap.py
├── test_miniboss.py
└── test_shop_system.py
```

## Success Criteria

Phase 2 is complete when:

✅ **Dungeon Generation:**
- Generate 12-18 room dungeons procedurally
- Main path guaranteed from start to boss
- Special rooms (treasure, shop, secret, mini-boss) placed correctly
- All rooms reachable
- Dungeon fits within reasonable grid size

✅ **Room Progression:**
- Player can move between rooms via doors
- Doors lock during combat, unlock when cleared
- Room state persists (cleared rooms stay cleared)
- Player repositions correctly at opposite door
- Room-clear rewards spawn (coins, hearts, items, bombs)

✅ **Currency System:**
- Coins collected from enemies and rewards
- Bombs tracked and consumed
- Currency persists across rooms
- UI displays coins and bombs count

✅ **Shop System:**
- Shop rooms contain 3-4 items with prices
- Can purchase items with coins
- "Not enough coins" feedback works
- Items properly deducted from shop after purchase

✅ **Bomb System:**
- Place bombs with B key (deducts from count)
- Fuse countdown works (1.5 seconds)
- Explosion reveals secret rooms if adjacent
- Explosion damages entities in blast radius
- "Spelunker's Sense" status shows bombable walls

✅ **Mini-Boss:**
- Mini-boss appears once per dungeon
- Enhanced HP and attack patterns
- Guaranteed item drop on defeat
- Sentinel teleport mechanic works
- Extra rewards spawn (coins + heart)

✅ **Mini-Map:**
- Displays in corner of screen
- Shows visited rooms, current position
- Shows adjacent unvisited rooms with doors
- Updates on room transitions

✅ **All Tests Pass:**
- 73 unit tests (15 dungeon, 12 room, 8 currency, 10 bomb, 7 minimap, 6 miniboss, 15 misc)
- 8 integration tests
- All tests passing

✅ **Game Playability:**
- Can complete full dungeon run (start to boss)
- Can find and purchase from shops
- Can discover and enter secret rooms
- Can defeat mini-boss and collect reward
- Mini-map aids navigation
- No crashes or game-breaking bugs

## Implementation Priority

**Phase 2A: Core Dungeon (Week 1)**
1. DungeonGenerator - main path generation
2. RoomManager - room transitions and state
3. Door system - collision and locking
4. Basic room types (start, combat, boss)
5. Room-clear detection and door unlocking
6. Mini-map display (basic)

**Phase 2B: Currency & Rewards (Week 1)**
7. Currency component and UI
8. Coin pickups and drops
9. Room-clear reward system
10. Bomb pickups

**Phase 2C: Special Features (Week 2)**
11. Shop system - items and purchases
12. Bomb system - placement and explosion
13. Secret rooms - bombable walls and reveal
14. Treasure rooms - item pedestals
15. Mini-boss system - enhanced enemies and drops
16. Status effects - Spelunker's Sense
17. Mini-map updates - visited tracking

**Phase 2D: Polish & Testing (Week 2)**
18. Integration testing
19. Balance tuning (prices, drop rates, room counts)
20. Bug fixes and edge cases
21. UI polish and notifications

## Notes

- Keep existing item pickup system from Phase 1 unchanged
- Enemy AI and shooting patterns remain unchanged
- Player damage and invincibility systems carry forward
- Collision detection reused for doors
- Existing test suite should continue passing

## Future Considerations (Phase 3)

- Boss fights with phases
- More enemy types
- More items (targeting 12-15 total)
- Multiple floors/levels
- Keys and locked doors
- Curse rooms (risk/reward)
- Challenge rooms (waves of enemies)

---

**Design Status:** Complete and Ready for Implementation
**Next Step:** Create implementation plan with TDD task breakdown
