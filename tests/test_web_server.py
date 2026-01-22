# tests/test_web_server.py
import pytest
import asyncio
import json
import websockets
from src.web.server import GameServer


@pytest.mark.asyncio
async def test_server_starts():
    """Test server can start and stop."""
    server = GameServer(host="localhost", port=8766)

    # Start server in background
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.1)  # Let server start

    # Verify server is running
    assert server.running is True

    # Stop server
    server.running = False
    server_task.cancel()

    try:
        await server_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_client_can_connect():
    """Test client can connect to server."""
    server = GameServer(host="localhost", port=8767)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.1)

    try:
        # Connect as client
        async with websockets.connect("ws://localhost:8767") as ws:
            # Send connect message
            await ws.send('{"type": "connect", "role": "player", "sessionId": null}')

            # Receive session info
            response = await asyncio.wait_for(ws.recv(), timeout=1.0)
            assert "sessionId" in response
            assert "player" in response

    finally:
        server.running = False
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_spectator_invalid_session():
    """Test spectator with invalid session ID gets error."""
    server = GameServer(host="localhost", port=8768)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.1)

    try:
        async with websockets.connect("ws://localhost:8768") as ws:
            # Send connect with invalid session
            await ws.send('{"type": "connect", "role": "spectator", "sessionId": "invalid"}')

            # Receive error response
            response = await asyncio.wait_for(ws.recv(), timeout=1.0)
            response_data = json.loads(response)
            assert response_data["type"] == "error"
            assert "not found" in response_data["message"].lower()

    finally:
        server.running = False
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_spectator_joins_existing_session():
    """Test that a spectator can join an existing player's session."""
    server = GameServer(host="localhost", port=8769)

    # Start server
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.1)

    try:
        # Player connects first
        async with websockets.connect("ws://localhost:8769") as player_ws:
            player_connect = {"type": "connect", "role": "player"}
            await player_ws.send(json.dumps(player_connect))

            # Get session ID
            response = await player_ws.recv()
            session_data = json.loads(response)
            session_id = session_data["sessionId"]

            # Spectator joins that session
            async with websockets.connect("ws://localhost:8769") as spectator_ws:
                spectator_connect = {
                    "type": "connect",
                    "role": "spectator",
                    "sessionId": session_id
                }
                await spectator_ws.send(json.dumps(spectator_connect))

                # Verify spectator gets session confirmation
                spec_response = await spectator_ws.recv()
                spec_data = json.loads(spec_response)

                assert spec_data["type"] == "session_info"
                assert spec_data["role"] == "spectator"
                assert spec_data["sessionId"] == session_id
    finally:
        server.running = False
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
