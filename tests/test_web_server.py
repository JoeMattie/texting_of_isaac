# tests/test_web_server.py
import pytest
import asyncio
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
