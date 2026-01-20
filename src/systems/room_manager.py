"""Room manager system for handling room state and transitions."""
import esper
from src.game.dungeon import Dungeon, DungeonRoom, RoomType, RoomState, generate_dungeon
from src.entities.rewards import spawn_room_clear_reward as _spawn_room_clear_reward
from src.entities.doors import spawn_door
from src.entities.shop import create_shop_item, generate_shop_items
from src.entities.enemies import create_enemy
from src.entities.bosses import create_boss
from src.entities.trapdoor import create_trapdoor
from src.components.dungeon import Door
from src.components.core import Sprite, Position
from src.components.game import Enemy, Player
from src.components.combat import Collider
from src.components.boss import Boss, Trapdoor
from src.config import Config


class RoomManager(esper.Processor):
    """Manages current room state and transitions.

    Responsibilities:
    - Track current room position and floor number
    - Handle room state transitions
    - Spawn/despawn room contents (enemies, bosses, trapdoors)
    - Lock/unlock doors based on room state
    - Handle floor transitions
    """

    def __init__(self, dungeon: Dungeon, current_floor: int = 1):
        """Initialize room manager with dungeon.

        Args:
            dungeon: Complete dungeon layout
            current_floor: Current floor number (default: 1)
        """
        super().__init__()
        self.dungeon = dungeon
        self.current_position = dungeon.start_position
        self.current_room = dungeon.rooms[self.current_position]
        self.current_floor = current_floor

        # Reveal start room in minimap
        self._reveal_current_room()

    def despawn_current_room_entities(self) -> None:
        """Remove all entities from current room.

        This method will despawn enemies, projectiles, doors, and other
        room-specific entities when transitioning to a new room.
        """
        # Delete all door entities
        for entity, (door,) in esper.get_components(Door):
            esper.delete_entity(entity, immediate=True)

        # TODO: Implement additional entity despawning in integration tasks
        # - Delete all enemies (esper.get_components(Enemy))
        # - Delete all projectiles (esper.get_components(Projectile))
        # - Keep player entity

    def spawn_room_contents(self) -> None:
        """Spawn entities for current room.

        This method spawns all entities that should exist in the current
        room based on room type, cleared status, and door connections.
        """
        # Determine if doors should be locked
        should_lock = self._should_lock_doors()

        # Spawn doors for each connection
        for direction, leads_to in self.current_room.doors.items():
            spawn_door("main", direction, leads_to, locked=should_lock)

        # Spawn shop items if shop room
        if self.current_room.room_type == RoomType.SHOP:
            self._spawn_shop_items()

        # Spawn boss in boss room
        if self.current_room.room_type == RoomType.BOSS and not self.current_room.cleared:
            self._spawn_boss()

        # Spawn enemies in combat rooms (if not cleared and not boss room)
        elif self.current_room.room_type == RoomType.COMBAT and not self.current_room.cleared:
            self._spawn_enemies()

        # TODO: Implement additional entity spawning in integration tasks
        # - Spawn treasure pedestal if treasure room

    def _should_lock_doors(self) -> bool:
        """Determine if doors should be locked based on room state.

        Returns:
            True if doors should be locked, False otherwise
        """
        # Lock doors in uncleared combat rooms
        if self.current_room.room_type == RoomType.COMBAT and not self.current_room.cleared:
            return True

        # Unlock doors in all other cases (peaceful rooms, cleared rooms)
        return False

    def transition_to_room(self, new_position: tuple[int, int], entry_direction: str) -> None:
        """Transition player to new room.

        This method handles all the logic for moving from the current room
        to a new room, including state updates and entity management.

        Args:
            new_position: Grid coordinates of new room (x, y)
            entry_direction: Direction player came from ("north", "south", "east", "west")
        """
        # Clean up old room
        self.despawn_current_room_entities()

        # Update position tracking
        self.current_position = new_position
        self.current_room = self.dungeon.rooms[new_position]

        # Mark room as visited
        self.current_room.visited = True

        # Spawn new room contents
        self.spawn_room_contents()

        # Determine and set room state based on room type and cleared status
        if self.current_room.room_type in [RoomType.START, RoomType.TREASURE, RoomType.SHOP, RoomType.SECRET]:
            # Peaceful rooms (no combat)
            self.current_room.state = RoomState.PEACEFUL
        elif self.current_room.cleared:
            # Revisiting a previously cleared combat room
            self.current_room.state = RoomState.CLEARED
        else:
            # Entering uncleared combat room
            self.current_room.state = RoomState.COMBAT

        # Reveal room in minimap
        self._reveal_current_room()

    def on_room_cleared(self) -> None:
        """Called when last enemy in room dies.

        This method handles the room clear event by marking the room as
        cleared, updating state, unlocking doors, and spawning rewards.
        """
        # Mark room as cleared
        self.current_room.cleared = True
        self.current_room.state = RoomState.CLEARED

        # Unlock all doors
        self.unlock_all_doors()

        # Spawn trapdoor if boss room
        if self.current_room.room_type == RoomType.BOSS:
            self._spawn_trapdoor()

        # Spawn room-clear reward (implementation in integration tasks)
        self.spawn_room_clear_reward()

    def lock_all_doors(self) -> None:
        """Lock all doors in current room."""
        for door_ent, (door, sprite) in esper.get_components(Door, Sprite):
            door.locked = True
            sprite.char = "▮"
            sprite.color = "red"

    def unlock_all_doors(self) -> None:
        """Unlock all doors in current room."""
        for door_ent, (door, sprite) in esper.get_components(Door, Sprite):
            door.locked = False
            sprite.char = "▯"
            sprite.color = "cyan"

    def spawn_room_clear_reward(self) -> None:
        """Spawn reward when room is cleared.

        Spawns one reward based on weighted random selection:
        - 60% coins, 25% heart, 10% stat boost, 5% bombs
        """
        # Call the standalone reward spawning function
        # Note: We need to determine which world to spawn in
        # For now, use "main" world as default
        _spawn_room_clear_reward("main")

    def _reveal_current_room(self) -> None:
        """Reveal current room in minimap."""
        from src.components.dungeon import MiniMap

        # Find minimap entity
        minimap_entities = esper.get_component(MiniMap)
        if minimap_entities:
            minimap_ent, minimap = minimap_entities[0]

            # Reveal current room
            minimap.reveal_room(self.current_position[0], self.current_position[1])

            # Update current position
            minimap.current_position = self.current_position

    def _spawn_shop_items(self) -> None:
        """Spawn shop items in current room."""
        # Generate 3-4 random items
        item_names = generate_shop_items()

        # Position items in row at top of room
        # Spacing: divide room width by (num_items + 1)
        num_items = len(item_names)
        spacing = Config.ROOM_WIDTH / (num_items + 1)
        y_pos = 8.0  # Top third of room

        for i, item_name in enumerate(item_names):
            x_pos = spacing * (i + 1)
            create_shop_item("main", item_name, x_pos, y_pos)

    def _spawn_enemies(self) -> None:
        """Spawn enemies in current room with floor scaling."""
        import random

        # Spawn enemies based on room config
        for enemy_config in self.current_room.enemies:
            enemy_type = enemy_config["type"]
            count = enemy_config["count"]

            for _ in range(count):
                # Random spawn position (avoid edges and center)
                x = random.uniform(10, Config.ROOM_WIDTH - 10)
                y = random.uniform(5, Config.ROOM_HEIGHT - 5)

                # Avoid center spawn area
                if abs(x - Config.ROOM_WIDTH // 2) < 10:
                    x += 15

                # Create enemy with floor scaling
                create_enemy("main", enemy_type, x, y, floor=self.current_floor)

    def _spawn_boss(self) -> None:
        """Spawn boss in current room based on current floor."""
        # Map floor to boss type
        boss_types = {
            1: "boss_a",
            2: "boss_b",
            3: "boss_c"
        }

        boss_type = boss_types.get(self.current_floor, "boss_a")

        # Spawn boss at center of room
        center_x = Config.ROOM_WIDTH / 2
        center_y = Config.ROOM_HEIGHT / 2

        create_boss("main", boss_type, center_x, center_y)

    def _spawn_trapdoor(self) -> None:
        """Spawn trapdoor after boss defeat."""
        # Spawn at center of room
        center_x = Config.ROOM_WIDTH / 2
        center_y = Config.ROOM_HEIGHT / 2

        # Next floor is current + 1
        next_floor = self.current_floor + 1

        create_trapdoor("main", center_x, center_y, next_floor)

    def advance_to_next_floor(self, target_floor: int) -> None:
        """Advance to the next floor.

        This method handles transitioning to a new floor by:
        - Incrementing current_floor
        - Generating a new dungeon
        - Clearing all entities except player
        - Resetting player position

        Args:
            target_floor: The floor number to advance to
        """
        # Update floor number
        self.current_floor = target_floor

        # Generate new dungeon
        self.dungeon = generate_dungeon()
        self.current_position = self.dungeon.start_position
        self.current_room = self.dungeon.rooms[self.current_position]

        # Clear all entities except player
        self._clear_all_entities_except_player()

        # Reset player position to center of start room
        self._reset_player_position()

        # Spawn new room contents
        self.spawn_room_contents()

        # Reveal start room
        self._reveal_current_room()

    def _clear_all_entities_except_player(self) -> None:
        """Clear all entities except the player."""
        # Delete all enemies
        for entity, (enemy,) in esper.get_components(Enemy):
            esper.delete_entity(entity, immediate=True)

        # Delete all doors
        for entity, (door,) in esper.get_components(Door):
            esper.delete_entity(entity, immediate=True)

        # Delete all bosses
        for entity, (boss,) in esper.get_components(Boss):
            esper.delete_entity(entity, immediate=True)

        # Delete all trapdoors
        for entity, (trapdoor,) in esper.get_components(Trapdoor):
            esper.delete_entity(entity, immediate=True)

        # Delete all projectiles (if any)
        from src.components.combat import Projectile
        for entity, (projectile,) in esper.get_components(Projectile):
            esper.delete_entity(entity, immediate=True)

        # TODO: Clear other entities like items, rewards, etc.

    def _reset_player_position(self) -> None:
        """Reset player to center of start room."""
        # Find player entity
        player_entities = list(esper.get_components(Player, Position))

        if player_entities:
            player_ent, (player, pos) = player_entities[0]

            # Reset to center
            pos.x = Config.ROOM_WIDTH / 2
            pos.y = Config.ROOM_HEIGHT / 2

    def process(self):
        """Process room manager (currently no per-frame logic)."""
        pass
