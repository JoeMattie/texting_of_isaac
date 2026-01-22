"""WebSocket protocol message types and serialization."""
import json
from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class Message:
    """Base message class."""
    type: str = field(init=False)


@dataclass
class ConnectMessage(Message):
    """Client connection request."""
    role: str  # "player" or "spectator"
    session_id: Optional[str] = None

    def __post_init__(self):
        self.type = "connect"


@dataclass
class InputMessage(Message):
    """Player input event."""
    key: str
    action: str = "press"  # "press" or "release"

    def __post_init__(self):
        self.type = "input"


@dataclass
class GameStateMessage(Message):
    """Server response with session info.

    Note: This message type is "session_info" on the wire (not "game_state").
    This is the initial handshake response sent to clients after connection,
    not used for ongoing game state updates during gameplay.
    """
    session_id: str
    role: str
    status: str

    def __post_init__(self):
        self.type = "session_info"


def parse_message(json_str: str) -> Union[ConnectMessage, InputMessage]:
    """Parse JSON string into message object.

    Raises:
        ValueError: If JSON is invalid or message type is unknown.
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    msg_type = data.get("type")

    if msg_type == "connect":
        if "role" not in data:
            raise ValueError("ConnectMessage missing required field 'role'")
        return ConnectMessage(
            role=data["role"],
            session_id=data.get("sessionId")
        )
    elif msg_type == "input":
        if "key" not in data:
            raise ValueError("InputMessage missing required field 'key'")
        return InputMessage(
            key=data["key"],
            action=data.get("action", "press")
        )
    else:
        raise ValueError(f"Unknown message type: {msg_type}")


def serialize_message(msg: Message) -> str:
    """Serialize message object to JSON string."""
    if isinstance(msg, GameStateMessage):
        return json.dumps({
            "type": msg.type,
            "sessionId": msg.session_id,
            "role": msg.role,
            "status": msg.status
        })
    elif isinstance(msg, ConnectMessage):
        return json.dumps({
            "type": msg.type,
            "role": msg.role,
            "sessionId": msg.session_id
        })
    elif isinstance(msg, InputMessage):
        return json.dumps({
            "type": msg.type,
            "key": msg.key,
            "action": msg.action
        })
    raise ValueError(f"Cannot serialize {type(msg)}")
