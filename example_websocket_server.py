"""Example WebSocket server for streaming game state to web frontend.

This shows how to integrate the game state export with a web frontend
using WebSockets for real-time updates.

Installation:
    pip install websockets

Usage:
    python example_websocket_server.py

    Then open example_web_frontend.html in a browser.
"""
import asyncio
import json
import websockets
from example_state_export import export_game_state


class GameServer:
    """WebSocket server that streams game state to web clients."""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.game_running = False

    async def register_client(self, websocket):
        """Register a new client connection."""
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")

    async def unregister_client(self, websocket):
        """Remove a disconnected client."""
        self.clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.clients)}")

    async def broadcast_game_state(self, state_json: str):
        """Send game state to all connected clients."""
        if self.clients:
            # Send to all clients concurrently
            await asyncio.gather(
                *[client.send(state_json) for client in self.clients],
                return_exceptions=True
            )

    async def handle_client(self, websocket, path):
        """Handle a client connection."""
        await self.register_client(websocket)
        try:
            # Keep connection alive and handle messages
            async for message in websocket:
                # Handle client messages (e.g., input commands)
                data = json.loads(message)
                if data.get('type') == 'input':
                    # Forward input to game
                    print(f"Received input: {data.get('key')}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)

    async def game_loop(self):
        """Main game loop that exports state every frame."""
        # This would integrate with your actual game engine
        # For demo purposes, we'll simulate it

        frame_time = 1.0 / 60  # 60 FPS

        while True:
            try:
                # Export current game state
                # In a real implementation, this would be:
                # state = export_game_state("main")

                # For demo, create a mock state
                state = self._create_demo_state()
                state_json = json.dumps(state)

                # Broadcast to all clients
                await self.broadcast_game_state(state_json)

                # Wait for next frame
                await asyncio.sleep(frame_time)

            except Exception as e:
                print(f"Error in game loop: {e}")
                await asyncio.sleep(1)

    def _create_demo_state(self):
        """Create demo state for testing without full game."""
        import random
        import math
        import time

        # Animate player position in a circle
        t = time.time()
        player_x = 30 + math.cos(t) * 10
        player_y = 10 + math.sin(t) * 5

        return {
            "frame": {"width": 60, "height": 20},
            "entities": [
                {
                    "id": 1,
                    "type": "player",
                    "components": {
                        "position": {"x": player_x, "y": player_y},
                        "sprite": {"char": "@", "color": "#00ff00"},
                        "health": {"current": 3, "max": 3}
                    }
                },
                {
                    "id": 2,
                    "type": "enemy_chaser",
                    "components": {
                        "position": {"x": 45, "y": 8},
                        "sprite": {"char": "C", "color": "#ff0000"},
                        "health": {"current": 2, "max": 3}
                    }
                },
                {
                    "id": 3,
                    "type": "door",
                    "components": {
                        "position": {"x": 30, "y": 0},
                        "sprite": {"char": "▯", "color": "#00ffff"}
                    }
                }
            ],
            "ui": {
                "currency": {"coins": random.randint(0, 99), "bombs": 3},
                "health": {"current": 3, "max": 3},
                "items": ["piercing", "multi_shot"]
            },
            "room": {"position": [0, 0], "doors": []}
        }

    async def start(self):
        """Start the WebSocket server and game loop."""
        print(f"Starting WebSocket server on {self.host}:{self.port}")

        # Start server
        async with websockets.serve(self.handle_client, self.host, self.port):
            print("Server started!")
            print(f"Open example_web_frontend.html in a browser")
            print(f"Make sure to uncomment the WebSocket connection line")

            # Run game loop
            await self.game_loop()


# Integration with actual game engine
class RealGameIntegration:
    """Shows how to integrate with the actual game engine."""

    @staticmethod
    async def run_game_with_websocket():
        """Run the actual game while streaming state over WebSocket."""
        from src.engine.game import GameEngine

        # Create game server
        server = GameServer()

        # Start WebSocket server in background
        server_task = asyncio.create_task(server.start())

        # Your game loop would look like:
        engine = GameEngine()

        while engine.running:
            # Normal game update
            engine.update(delta_time=1/60)

            # Export state and broadcast
            state = export_game_state("main")
            state_json = json.dumps(state)
            await server.broadcast_game_state(state_json)

            await asyncio.sleep(1/60)  # 60 FPS


if __name__ == "__main__":
    # Run demo server
    server = GameServer()
    asyncio.run(server.start())
