import pytest
from src.config import Config


def test_config_has_game_constants():
    """Config should provide all game constants."""
    assert Config.ROOM_WIDTH == 60
    assert Config.ROOM_HEIGHT == 20
    assert Config.FPS == 30
    assert Config.PLAYER_SPEED > 0
