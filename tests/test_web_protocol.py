# tests/test_web_protocol.py
import pytest
from src.web.protocol import (
    Message,
    ConnectMessage,
    InputMessage,
    GameStateMessage,
    parse_message,
    serialize_message
)


def test_parse_connect_message():
    """Test parsing connect message from JSON."""
    json_str = '{"type": "connect", "role": "player", "sessionId": null}'
    msg = parse_message(json_str)

    assert isinstance(msg, ConnectMessage)
    assert msg.role == "player"
    assert msg.session_id is None


def test_parse_connect_spectator_message():
    """Test parsing spectator connect with session ID."""
    json_str = '{"type": "connect", "role": "spectator", "sessionId": "abc123"}'
    msg = parse_message(json_str)

    assert isinstance(msg, ConnectMessage)
    assert msg.role == "spectator"
    assert msg.session_id == "abc123"


def test_parse_input_message():
    """Test parsing player input message."""
    json_str = '{"type": "input", "key": "w"}'
    msg = parse_message(json_str)

    assert isinstance(msg, InputMessage)
    assert msg.key == "w"


def test_serialize_game_state_message():
    """Test serializing game state response."""
    msg = GameStateMessage(
        session_id="abc123",
        role="player",
        status="ready"
    )
    json_str = serialize_message(msg)

    assert '"sessionId": "abc123"' in json_str
    assert '"role": "player"' in json_str
    assert '"status": "ready"' in json_str


def test_parse_invalid_message():
    """Test parsing invalid JSON raises error."""
    with pytest.raises(ValueError):
        parse_message('{"type": "unknown"}')
