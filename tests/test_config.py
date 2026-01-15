import pytest
from src.config import Config


def test_config_has_game_constants():
    """Config should provide all game constants."""
    assert Config.ROOM_WIDTH == 60
    assert Config.ROOM_HEIGHT == 20
    assert Config.FPS == 30
    assert Config.PLAYER_SPEED > 0


def test_all_display_constants_exist():
    """All display constants should be defined."""
    assert hasattr(Config, "ROOM_WIDTH")
    assert hasattr(Config, "ROOM_HEIGHT")
    assert hasattr(Config, "FPS")


def test_all_player_constants_exist():
    """All player stat constants should be defined."""
    assert hasattr(Config, "PLAYER_SPEED")
    assert hasattr(Config, "PLAYER_DAMAGE")
    assert hasattr(Config, "PLAYER_FIRE_RATE")
    assert hasattr(Config, "PLAYER_SHOT_SPEED")
    assert hasattr(Config, "PLAYER_MAX_HP")
    assert hasattr(Config, "PLAYER_HITBOX")


def test_all_enemy_constants_exist():
    """All enemy stat constants should be defined."""
    assert hasattr(Config, "ENEMY_HITBOX")


def test_all_projectile_constants_exist():
    """All projectile stat constants should be defined."""
    assert hasattr(Config, "PROJECTILE_HITBOX")


def test_all_game_balance_constants_exist():
    """All game balance constants should be defined."""
    assert hasattr(Config, "INVINCIBILITY_DURATION")
    assert hasattr(Config, "HEART_DROP_CHANCE")
    assert hasattr(Config, "MAX_PROJECTILES")


def test_display_constants_are_positive():
    """Display constants should be positive integers."""
    assert Config.ROOM_WIDTH > 0
    assert Config.ROOM_HEIGHT > 0
    assert Config.FPS > 0


def test_player_speed_constants_are_positive():
    """Player speed-related constants should be positive."""
    assert Config.PLAYER_SPEED > 0
    assert Config.PLAYER_SHOT_SPEED > 0
    assert Config.PLAYER_FIRE_RATE > 0


def test_player_damage_is_positive():
    """Player damage should be positive."""
    assert Config.PLAYER_DAMAGE > 0


def test_player_hp_is_positive():
    """Player max HP should be positive."""
    assert Config.PLAYER_MAX_HP > 0


def test_hitbox_constants_are_positive():
    """All hitbox constants should be positive."""
    assert Config.PLAYER_HITBOX > 0
    assert Config.ENEMY_HITBOX > 0
    assert Config.PROJECTILE_HITBOX > 0


def test_invincibility_duration_is_positive():
    """Invincibility duration should be positive."""
    assert Config.INVINCIBILITY_DURATION > 0


def test_heart_drop_chance_is_probability():
    """Heart drop chance should be a valid probability (0-1)."""
    assert 0 <= Config.HEART_DROP_CHANCE <= 1


def test_max_projectiles_is_positive():
    """Max projectiles should be positive."""
    assert Config.MAX_PROJECTILES > 0


def test_no_constants_are_none():
    """No config constants should be None."""
    assert Config.ROOM_WIDTH is not None
    assert Config.ROOM_HEIGHT is not None
    assert Config.FPS is not None
    assert Config.PLAYER_SPEED is not None
    assert Config.PLAYER_DAMAGE is not None
    assert Config.PLAYER_FIRE_RATE is not None
    assert Config.PLAYER_SHOT_SPEED is not None
    assert Config.PLAYER_MAX_HP is not None
    assert Config.PLAYER_HITBOX is not None
    assert Config.ENEMY_HITBOX is not None
    assert Config.PROJECTILE_HITBOX is not None
    assert Config.INVINCIBILITY_DURATION is not None
    assert Config.HEART_DROP_CHANCE is not None
    assert Config.MAX_PROJECTILES is not None


def test_integer_constants_are_integers():
    """Integer constants should have integer values."""
    assert isinstance(Config.ROOM_WIDTH, int)
    assert isinstance(Config.ROOM_HEIGHT, int)
    assert isinstance(Config.FPS, int)
    assert isinstance(Config.PLAYER_MAX_HP, int)
    assert isinstance(Config.MAX_PROJECTILES, int)


def test_float_constants_are_numeric():
    """Float constants should have numeric values."""
    assert isinstance(Config.PLAYER_SPEED, (int, float))
    assert isinstance(Config.PLAYER_DAMAGE, (int, float))
    assert isinstance(Config.PLAYER_FIRE_RATE, (int, float))
    assert isinstance(Config.PLAYER_SHOT_SPEED, (int, float))
    assert isinstance(Config.PLAYER_HITBOX, (int, float))
    assert isinstance(Config.ENEMY_HITBOX, (int, float))
    assert isinstance(Config.PROJECTILE_HITBOX, (int, float))
    assert isinstance(Config.INVINCIBILITY_DURATION, (int, float))
    assert isinstance(Config.HEART_DROP_CHANCE, (int, float))


def test_item_drop_chance_is_probability():
    """Test ITEM_DROP_CHANCE is between 0 and 1."""
    from src.config import Config

    assert hasattr(Config, 'ITEM_DROP_CHANCE')
    assert 0.0 <= Config.ITEM_DROP_CHANCE <= 1.0


def test_item_pickup_radius_is_positive():
    """Test ITEM_PICKUP_RADIUS is positive."""
    from src.config import Config

    assert hasattr(Config, 'ITEM_PICKUP_RADIUS')
    assert Config.ITEM_PICKUP_RADIUS > 0


def test_homing_turn_rate_is_positive():
    """Test HOMING_TURN_RATE is positive."""
    from src.config import Config

    assert hasattr(Config, 'HOMING_TURN_RATE')
    assert Config.HOMING_TURN_RATE > 0


def test_notification_duration_is_positive():
    """Test NOTIFICATION_DURATION is positive."""
    from src.config import Config

    assert hasattr(Config, 'NOTIFICATION_DURATION')
    assert Config.NOTIFICATION_DURATION > 0
