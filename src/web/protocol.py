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

    def __post_init__(self):
        self.type = "input"


@dataclass
class GameStateMessage(Message):
    """Server response with session info."""
    session_id: str
    role: str
    status: str

    def __post_init__(self):
        self.type = "session_info"


def parse_message(json_str: str) -> Union[ConnectMessage, InputMessage]:
    """Parse JSON string into message object."""
    data = json.loads(json_str)
    msg_type = data.get("type")

    if msg_type == "connect":
        return ConnectMessage(
            role=data["role"],
            session_id=data.get("sessionId")
        )
    elif msg_type == "input":
        return InputMessage(key=data["key"])
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
    raise ValueError(f"Cannot serialize {type(msg)}")
