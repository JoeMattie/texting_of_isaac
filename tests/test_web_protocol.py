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


def test_parse_missing_role():
    """Test parsing connect message without role raises error."""
    with pytest.raises(ValueError, match="missing required field 'role'"):
        parse_message('{"type": "connect", "sessionId": null}')


def test_parse_missing_key():
    """Test parsing input message without key raises error."""
    with pytest.raises(ValueError, match="missing required field 'key'"):
        parse_message('{"type": "input"}')


def test_parse_invalid_json():
    """Test parsing invalid JSON raises ValueError."""
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_message('{"type": invalid}')


def test_serialize_connect_message():
    """Test serializing connect message."""
    msg = ConnectMessage(role="player", session_id="abc123")
    json_str = serialize_message(msg)
    assert '"type": "connect"' in json_str
    assert '"role": "player"' in json_str
    assert '"sessionId": "abc123"' in json_str


def test_serialize_input_message():
    """Test serializing input message."""
    msg = InputMessage(key="w")
    json_str = serialize_message(msg)
    assert '"type": "input"' in json_str
    assert '"key": "w"' in json_str
