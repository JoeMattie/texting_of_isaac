"""Game-specific ECS components."""
from dataclasses import dataclass
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


@dataclass
class AIBehavior:
    """AI behavior component for enemies.

    Attributes:
        pattern_cooldowns: Dict mapping pattern names to cooldown times
        pattern_index: Current pattern index for sequential cycling
    """
    pattern_cooldowns: Dict[str, float]
    pattern_index: int = 0

    def __post_init__(self):
        """Validate component data."""
        if not isinstance(self.pattern_cooldowns, dict):
            raise TypeError("pattern_cooldowns must be a dictionary")
        if not all(isinstance(k, str) for k in self.pattern_cooldowns.keys()):
            raise TypeError("pattern_cooldowns keys must be strings")
        if not all(isinstance(v, (int, float)) for v in self.pattern_cooldowns.values()):
            raise TypeError("pattern_cooldowns values must be numeric")
        if not isinstance(self.pattern_index, int):
            raise TypeError("pattern_index must be an integer")
        if self.pattern_index < 0:
            raise ValueError("pattern_index must be non-negative")


class Invincible:
    """Temporary invincibility component."""

    def __init__(self, duration: float) -> None:
        if duration < 0:
            raise ValueError("duration must be positive")
        self.remaining: float = duration

    def __repr__(self) -> str:
        return f"Invincible(duration={self.remaining})"


class Dead:
    """Marker component indicating entity has died."""

    def __repr__(self) -> str:
        return "Dead()"


class CollectedItems:
    """Tracks items collected by the player."""

    def __init__(self) -> None:
        self.items: List[Item] = []

    def has_effect(self, effect_name: str) -> bool:
        """Check if player has a specific special effect.

        Args:
            effect_name: Name of the effect to check for

        Returns:
            True if any collected item has this effect
        """
        return any(effect_name in item.special_effects for item in self.items)

    def __repr__(self) -> str:
        return f"CollectedItems(items={[item.name for item in self.items]})"
