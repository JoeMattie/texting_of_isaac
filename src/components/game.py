"""Game-specific ECS components."""
from typing import Dict, List


class Player:
    """Marker component for the player entity."""

    def __repr__(self) -> str:
        return "Player()"


class Enemy:
    """Marker component for enemy entities."""

    def __init__(self, type: str) -> None:
        self.type: str = type

    def __repr__(self) -> str:
        return f"Enemy(type={self.type!r})"


class Item:
    """Item pickup component."""

    def __init__(self, name: str, stat_modifiers: Dict[str, float], special_effects: List[str]) -> None:
        self.name: str = name
        self.stat_modifiers: Dict[str, float] = stat_modifiers
        self.special_effects: List[str] = special_effects

    def __repr__(self) -> str:
        return f"Item(name={self.name!r}, stat_modifiers={self.stat_modifiers!r}, special_effects={self.special_effects!r})"


class AIBehavior:
    """AI state and cooldowns for enemy behavior."""

    def __init__(self, pattern_cooldowns: Dict[str, float]) -> None:
        self.pattern_cooldowns: Dict[str, float] = pattern_cooldowns

    def __repr__(self) -> str:
        return f"AIBehavior(pattern_cooldowns={self.pattern_cooldowns!r})"


class Invincible:
    """Temporary invincibility component."""

    def __init__(self, duration: float) -> None:
        if duration < 0:
            raise ValueError("duration must be positive")
        self.remaining: float = duration

    def __repr__(self) -> str:
        return f"Invincible(duration={self.remaining})"
