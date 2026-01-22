"""Game session management for WebSocket server."""
import uuid
import esper
from typing import Optional, Set, Dict
from src.game.engine import GameEngine
from src.game.dungeon import generate_dungeon
from src.systems.room_manager import RoomManager
from src.entities.player import create_player
from src.config import Config
from example_state_export import export_game_state


class GameSession:
    """Represents a single game session with one player and multiple spectators."""

    # Key mappings for movement and shooting
    MOVE_KEYS = {'w': (0, -1), 'a': (-1, 0), 's': (0, 1), 'd': (1, 0)}
    SHOOT_KEYS = {
        'ArrowUp': (0, -1), 'ArrowDown': (0, 1),
        'ArrowLeft': (-1, 0), 'ArrowRight': (1, 0)
    }

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.world_name = f"web_session_{session_id}"
        self.player_client: Optional[object] = None
        self.spectator_clients: Set[object] = set()
        self.running = True
        self.engine: Optional[GameEngine] = None
        self.dungeon = None
        self.room_manager: Optional[RoomManager] = None
        # Track currently pressed keys
        self.pressed_keys: Set[str] = set()
        # Floor progression
        self.current_floor: int = 1

    async def initialize_game(self):
        """Initialize the game engine with dungeon for this session."""
        # Generate dungeon
        self.dungeon = generate_dungeon()

        # Create engine with dungeon
        self.engine = GameEngine(dungeon=self.dungeon, world_name=self.world_name)

        # Create RoomManager and register as processor
        self.room_manager = RoomManager(self.dungeon, current_floor=self.current_floor)
        esper.switch_world(self.world_name)
        esper.add_processor(self.room_manager, priority=4.8)

        # Wire RoomManager to CollisionSystem for door transitions
        self.engine.collision_system.room_manager = self.room_manager

        # Create player at dungeon start position
        start_room = self.dungeon.rooms[self.dungeon.start_position]
        create_player(self.world_name, Config.ROOM_WIDTH / 2, Config.ROOM_HEIGHT / 2)

        # Spawn initial room contents (doors, enemies if any)
        self.room_manager.spawn_room_contents()

    async def update_game(self, delta_time: float):
        """Update the game state."""
        if self.engine:
            # Sync input state to InputSystem before processing
            self._sync_input_state()
            self.engine.update(delta_time)

    def handle_input(self, key: str, action: str):
        """Handle a key input event.

        Args:
            key: The key that was pressed/released
            action: "press" or "release"
        """
        if action == "press":
            self.pressed_keys.add(key)
        elif action == "release":
            self.pressed_keys.discard(key)

    def _sync_input_state(self):
        """Sync pressed keys to the InputSystem."""
        if not self.engine:
            return

        # Calculate movement direction from pressed keys
        move_x, move_y = 0, 0
        for key in self.pressed_keys:
            if key in self.MOVE_KEYS:
                dx, dy = self.MOVE_KEYS[key]
                move_x += dx
                move_y += dy

        # Calculate shoot direction from pressed keys
        shoot_x, shoot_y = 0, 0
        for key in self.pressed_keys:
            if key in self.SHOOT_KEYS:
                dx, dy = self.SHOOT_KEYS[key]
                shoot_x += dx
                shoot_y += dy

        # Check for bomb key
        bomb_pressed = 'e' in self.pressed_keys or ' ' in self.pressed_keys

        # Clamp to -1, 0, 1 range
        move_x = max(-1, min(1, move_x))
        move_y = max(-1, min(1, move_y))
        shoot_x = max(-1, min(1, shoot_x))
        shoot_y = max(-1, min(1, shoot_y))

        # Set input on the InputSystem
        self.engine.input_system.set_input(move_x, move_y, shoot_x, shoot_y, bomb_pressed)

    def get_game_state(self) -> dict:
        """Export current game state as JSON-serializable dict."""
        if self.engine:
            state = export_game_state(self.world_name)
            # Get room position from room manager
            room_position = None
            if self.room_manager:
                room_position = list(self.room_manager.current_position)
                self.current_floor = self.room_manager.current_floor
            # Add session metadata
            game_state = 'playing'
            if self.engine.game_state_system:
                game_state = self.engine.game_state_system.current_state.value
            state['session'] = {
                'floor': self.current_floor,
                'roomPosition': room_position,
                'gameState': game_state,
                'spectatorCount': len(self.spectator_clients)
            }
            return state
        return {}

    def get_session_info(self) -> dict:
        """Get session info for listing."""
        state = self.get_game_state()
        player_health = 3  # default
        if state and state.get('player'):
            health = state['player'].get('components', {}).get('health', {})
            player_health = health.get('current', 3)
        return {
            'sessionId': self.session_id,
            'playerHealth': player_health,
            'floor': self.current_floor,
            'spectatorCount': len(self.spectator_clients)
        }

    def set_player(self, websocket):
        """Set the player client for this session."""
        self.player_client = websocket

    def add_spectator(self, websocket):
        """Add a spectator client to this session."""
        self.spectator_clients.add(websocket)

    def remove_spectator(self, websocket):
        """Remove a spectator client from this session."""
        self.spectator_clients.discard(websocket)

    def get_all_clients(self) -> list:
        """Get all connected clients (player + spectators)."""
        clients = list(self.spectator_clients)
        if self.player_client:
            clients.append(self.player_client)
        return clients


class SessionManager:
    """Manages multiple game sessions."""

    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}

    def create_session(self) -> GameSession:
        """Create a new game session."""
        session_id = str(uuid.uuid4())[:8]
        session = GameSession(session_id)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[GameSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def remove_session(self, session_id: str):
        """Remove a session from the manager."""
        self.sessions.pop(session_id, None)

    def list_sessions(self) -> list:
        """List all active sessions."""
        return list(self.sessions.values())

    def get_session_list(self) -> list:
        """Get list of active sessions with basic info."""
        result = []
        for session_id, session in self.sessions.items():
            if session.running:
                info = session.get_session_info()
                result.append(info)
        return result
