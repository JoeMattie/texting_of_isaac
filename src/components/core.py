"""Core ECS components for all entities."""


class Position:
    """2D position in the game world."""

    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y

    def __repr__(self) -> str:
        return f"Position(x={self.x}, y={self.y})"


class Velocity:
    """Movement vector."""

    def __init__(self, dx: float, dy: float) -> None:
        self.dx: float = dx
        self.dy: float = dy

    def __repr__(self) -> str:
        return f"Velocity(dx={self.dx}, dy={self.dy})"


class Health:
    """Hit points with current and maximum."""

    def __init__(self, current: int, max_hp: int) -> None:
        if current < 0:
            raise ValueError("current health cannot be negative")
        if max_hp < 0:
            raise ValueError("max health cannot be negative")
        if current > max_hp:
            raise ValueError("current health cannot exceed max health")
        self.current: int = current
        self.max: int = max_hp

    def __repr__(self) -> str:
        return f"Health(current={self.current}, max_hp={self.max})"


class Sprite:
    """Visual representation."""

    def __init__(self, char: str, color: str) -> None:
        if len(char) != 1:
            raise ValueError("char must be a single character")
        self.char: str = char
        self.color: str = color

    def __repr__(self) -> str:
        return f"Sprite(char={self.char!r}, color={self.color!r})"
