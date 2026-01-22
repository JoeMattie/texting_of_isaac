"""Tests for session listing functionality."""
import pytest
from src.web.session_manager import SessionManager, GameSession
from src.web.protocol import parse_message, serialize_message, ListSessionsMessage, SessionListMessage


class TestSessionList:
    def test_parse_list_sessions_message(self):
        msg = parse_message('{"type": "list_sessions"}')
        assert isinstance(msg, ListSessionsMessage)

    def test_serialize_session_list_message(self):
        msg = SessionListMessage(sessions=[
            {'sessionId': 'abc', 'playerHealth': 3, 'floor': 1, 'spectatorCount': 0}
        ])
        result = serialize_message(msg)
        assert '"type": "session_list"' in result
        assert '"sessions"' in result

    def test_session_manager_get_session_list_empty(self):
        manager = SessionManager()
        result = manager.get_session_list()
        assert result == []

    def test_game_session_get_session_info(self):
        session = GameSession('test-session')
        info = session.get_session_info()
        assert info['sessionId'] == 'test-session'
        assert 'playerHealth' in info
        assert 'floor' in info
        assert 'spectatorCount' in info

    def test_session_manager_get_session_list_with_running_sessions(self):
        """Test that only running sessions are included in the list."""
        manager = SessionManager()
        session1 = manager.create_session()
        session2 = manager.create_session()

        # Both sessions are running by default
        result = manager.get_session_list()
        assert len(result) == 2

        # Stop one session
        session1.running = False
        result = manager.get_session_list()
        assert len(result) == 1
        assert result[0]['sessionId'] == session2.session_id

    def test_session_info_spectator_count(self):
        """Test that spectator count is correctly reported."""
        session = GameSession('test-session')
        assert session.get_session_info()['spectatorCount'] == 0

        # Add mock spectators
        session.spectator_clients.add('spectator1')
        session.spectator_clients.add('spectator2')
        assert session.get_session_info()['spectatorCount'] == 2
