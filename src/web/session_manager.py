"""Game session management for WebSocket server."""
import uuid
import esper
from typing import Optional, Set, Dict
from src.game.engine import GameEngine
from example_state_export import export_game_state


class GameSession:
    """Represents a single game session with one player and multiple spectators."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.world_name = f"web_session_{session_id}"
        self.player_client: Optional[object] = None
        self.spectator_clients: Set[object] = set()
        self.running = True
        self.engine: Optional[GameEngine] = None

    async def initialize_game(self):
        """Initialize the game engine for this session."""
        # Create engine with unique world name
        self.engine = GameEngine(world_name=self.world_name)

    async def update_game(self, delta_time: float):
        """Update the game state."""
        if self.engine:
            self.engine.update(delta_time)

    def get_game_state(self) -> dict:
        """Export current game state as JSON-serializable dict."""
        if self.engine:
            return export_game_state(self.world_name)
        return {}

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
