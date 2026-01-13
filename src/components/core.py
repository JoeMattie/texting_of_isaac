"""Core ECS components for all entities."""


class Position:
    """2D position in the game world."""

    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y


class Velocity:
    """Movement vector."""

    def __init__(self, dx: float, dy: float) -> None:
        self.dx: float = dx
        self.dy: float = dy


class Health:
    """Hit points with current and maximum."""

    def __init__(self, current: int, max_hp: int) -> None:
        self.current: int = current
        self.max: int = max_hp


class Sprite:
    """Visual representation."""

    def __init__(self, char: str, color: str) -> None:
        self.char: str = char
        self.color: str = color
