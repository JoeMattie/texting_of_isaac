# tests/test_session_manager.py
import pytest
import esper
from src.web.session_manager import GameSession, SessionManager
from src.game.engine import GameEngine


def test_create_new_session():
    """Test creating a new game session."""
    manager = SessionManager()

    session = manager.create_session()

    assert session.session_id is not None
    assert len(session.session_id) > 0
    assert session.player_client is None
    assert len(session.spectator_clients) == 0
    assert session.running is True


def test_get_session_by_id():
    """Test retrieving session by ID."""
    manager = SessionManager()
    session = manager.create_session()

    retrieved = manager.get_session(session.session_id)

    assert retrieved == session


def test_get_nonexistent_session_returns_none():
    """Test getting nonexistent session returns None."""
    manager = SessionManager()

    result = manager.get_session("nonexistent")

    assert result is None


def test_add_player_to_session():
    """Test adding player client to session."""
    manager = SessionManager()
    session = manager.create_session()

    mock_websocket = object()
    session.set_player(mock_websocket)

    assert session.player_client == mock_websocket


def test_add_spectator_to_session():
    """Test adding spectator client to session."""
    manager = SessionManager()
    session = manager.create_session()

    mock_websocket = object()
    session.add_spectator(mock_websocket)

    assert mock_websocket in session.spectator_clients


def test_remove_spectator_from_session():
    """Test removing spectator client."""
    manager = SessionManager()
    session = manager.create_session()
    mock_websocket = object()
    session.add_spectator(mock_websocket)

    session.remove_spectator(mock_websocket)

    assert mock_websocket not in session.spectator_clients


def test_session_cleanup():
    """Test session cleanup removes from manager."""
    manager = SessionManager()
    session = manager.create_session()
    session_id = session.session_id

    manager.remove_session(session_id)

    assert manager.get_session(session_id) is None
