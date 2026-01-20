"""Game state enumeration."""
from enum import Enum


class GameState(Enum):
    """Game state management."""
    PLAYING = "playing"
    BOSS_FIGHT = "boss_fight"
    FLOOR_TRANSITION = "floor_transition"
    VICTORY = "victory"
    GAME_OVER = "game_over"
