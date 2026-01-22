# tests/test_game_loop_integration.py
import pytest
import asyncio
from src.web.session_manager import GameSession
from example_state_export import export_game_state


@pytest.mark.asyncio
async def test_session_initializes_game_engine():
    """Test session creates and initializes game engine."""
    session = GameSession("test123")

    await session.initialize_game()

    assert session.engine is not None
    assert session.engine.running is True


@pytest.mark.asyncio
async def test_session_runs_game_loop():
    """Test session game loop updates state."""
    session = GameSession("test123")
    await session.initialize_game()

    # Run one update
    await session.update_game(delta_time=1/30)

    # Should be able to export state
    state = export_game_state(session.world_name)
    assert state is not None
    assert "entities" in state


@pytest.mark.asyncio
async def test_session_exports_game_state():
    """Test exporting game state from session."""
    session = GameSession("test123")
    await session.initialize_game()

    state = session.get_game_state()

    assert state is not None
    assert "frame" in state
    assert "entities" in state
    assert "ui" in state
