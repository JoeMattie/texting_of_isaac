# src/web/server.py
"""WebSocket server for game state streaming."""
import asyncio
import json
import websockets
from typing import Optional
from src.web.session_manager import SessionManager, GameSession
from src.web.protocol import parse_message, ConnectMessage, InputMessage, serialize_message, GameStateMessage


class GameServer:
    """WebSocket server that manages game sessions."""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.session_manager = SessionManager()
        self.running = False

    async def handle_client(self, websocket):
        """Handle a client connection."""
        session: Optional[GameSession] = None
        role = None

        try:
            # Wait for connection message
            message_str = await websocket.recv()
            message = parse_message(message_str)

            if isinstance(message, ConnectMessage):
                if message.role == "player":
                    # Create new session for player
                    session = self.session_manager.create_session()
                    session.set_player(websocket)
                    role = "player"
                elif message.role == "spectator" and message.session_id:
                    # Join existing session as spectator
                    session = self.session_manager.get_session(message.session_id)
                    if session:
                        session.add_spectator(websocket)
                        role = "spectator"

                if session:
                    # Send session info
                    response = GameStateMessage(
                        session_id=session.session_id,
                        role=role,
                        status="ready"
                    )
                    await websocket.send(serialize_message(response))

                    # Keep connection alive
                    async for msg_str in websocket:
                        msg = parse_message(msg_str)
                        # Handle input messages here later
                        pass

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Cleanup on disconnect
            if session and role == "spectator":
                session.remove_spectator(websocket)

    async def start(self):
        """Start the WebSocket server."""
        self.running = True
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"WebSocket server running on ws://{self.host}:{self.port}")
            # Keep server running
            while self.running:
                await asyncio.sleep(0.1)
