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
    assert Config.DUNGEON_MIN_SIZE is not None
    assert Config.DUNGEON_MAX_SIZE is not None
    assert Config.DUNGEON_MAIN_PATH_LENGTH is not None
    assert Config.TREASURE_ROOM_COUNT_MIN is not None
    assert Config.TREASURE_ROOM_COUNT_MAX is not None
    assert Config.SHOP_COUNT_MIN is not None
    assert Config.SHOP_COUNT_MAX is not None
    assert Config.SECRET_COUNT_MIN is not None
    assert Config.SECRET_COUNT_MAX is not None
    assert Config.REWARD_COINS_CHANCE is not None
    assert Config.REWARD_HEART_CHANCE is not None
    assert Config.REWARD_STAT_BOOST_CHANCE is not None
    assert Config.REWARD_BOMBS_CHANCE is not None
    assert Config.STARTING_BOMBS is not None
    assert Config.STARTING_COINS is not None
    assert Config.ENEMY_COIN_DROP_CHANCE is not None
    assert Config.BOMB_FUSE_TIME is not None
    assert Config.BOMB_BLAST_RADIUS is not None
    assert Config.BOMB_DAMAGE is not None
    assert Config.MINIMAP_DISPLAY_RADIUS is not None
    assert Config.SHOP_ITEMS_MIN is not None
    assert Config.SHOP_ITEMS_MAX is not None
    assert Config.SHOP_ITEM_PRICES is not None
    assert Config.EXPLOSIVE_TEAR_DAMAGE_MULTIPLIER is not None


def test_integer_constants_are_integers():
    """Integer constants should have integer values."""
    assert isinstance(Config.ROOM_WIDTH, int)
    assert isinstance(Config.ROOM_HEIGHT, int)
    assert isinstance(Config.FPS, int)
    assert isinstance(Config.PLAYER_MAX_HP, int)
    assert isinstance(Config.MAX_PROJECTILES, int)
    assert isinstance(Config.DUNGEON_MIN_SIZE, int)
    assert isinstance(Config.DUNGEON_MAX_SIZE, int)
    assert isinstance(Config.DUNGEON_MAIN_PATH_LENGTH, int)
    assert isinstance(Config.TREASURE_ROOM_COUNT_MIN, int)
    assert isinstance(Config.TREASURE_ROOM_COUNT_MAX, int)
    assert isinstance(Config.SHOP_COUNT_MIN, int)
    assert isinstance(Config.SHOP_COUNT_MAX, int)
    assert isinstance(Config.SECRET_COUNT_MIN, int)
    assert isinstance(Config.SECRET_COUNT_MAX, int)
    assert isinstance(Config.STARTING_BOMBS, int)
    assert isinstance(Config.STARTING_COINS, int)
    assert isinstance(Config.MINIMAP_DISPLAY_RADIUS, int)
    assert isinstance(Config.SHOP_ITEMS_MIN, int)
    assert isinstance(Config.SHOP_ITEMS_MAX, int)


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
    assert isinstance(Config.REWARD_COINS_CHANCE, (int, float))
    assert isinstance(Config.REWARD_HEART_CHANCE, (int, float))
    assert isinstance(Config.REWARD_STAT_BOOST_CHANCE, (int, float))
    assert isinstance(Config.REWARD_BOMBS_CHANCE, (int, float))
    assert isinstance(Config.ENEMY_COIN_DROP_CHANCE, (int, float))
    assert isinstance(Config.BOMB_FUSE_TIME, (int, float))
    assert isinstance(Config.BOMB_BLAST_RADIUS, (int, float))
    assert isinstance(Config.BOMB_DAMAGE, (int, float))
    assert isinstance(Config.EXPLOSIVE_TEAR_DAMAGE_MULTIPLIER, (int, float))


def test_item_drop_chance_is_probability():
    """Test ITEM_DROP_CHANCE is between 0 and 1."""
    assert hasattr(Config, 'ITEM_DROP_CHANCE')
    assert 0.0 <= Config.ITEM_DROP_CHANCE <= 1.0


def test_item_pickup_radius_is_positive():
    """Test ITEM_PICKUP_RADIUS is positive."""
    assert hasattr(Config, 'ITEM_PICKUP_RADIUS')
    assert Config.ITEM_PICKUP_RADIUS > 0


def test_homing_turn_rate_is_positive():
    """Test HOMING_TURN_RATE is positive."""
    assert hasattr(Config, 'HOMING_TURN_RATE')
    assert Config.HOMING_TURN_RATE > 0


def test_notification_duration_is_positive():
    """Test NOTIFICATION_DURATION is positive."""
    assert hasattr(Config, 'NOTIFICATION_DURATION')
    assert Config.NOTIFICATION_DURATION > 0


def test_dungeon_generation_constants_exist():
    """Verify dungeon generation constants defined."""
    assert hasattr(Config, 'DUNGEON_MIN_SIZE')
    assert hasattr(Config, 'DUNGEON_MAX_SIZE')
    assert hasattr(Config, 'DUNGEON_MAIN_PATH_LENGTH')
    assert hasattr(Config, 'TREASURE_ROOM_COUNT_MIN')
    assert hasattr(Config, 'TREASURE_ROOM_COUNT_MAX')
    assert hasattr(Config, 'SHOP_COUNT_MIN')
    assert hasattr(Config, 'SHOP_COUNT_MAX')
    assert hasattr(Config, 'SECRET_COUNT_MIN')
    assert hasattr(Config, 'SECRET_COUNT_MAX')


def test_reward_constants_exist():
    """Verify reward system constants defined."""
    assert hasattr(Config, 'REWARD_COINS_CHANCE')
    assert hasattr(Config, 'REWARD_HEART_CHANCE')
    assert hasattr(Config, 'REWARD_STAT_BOOST_CHANCE')
    assert hasattr(Config, 'REWARD_BOMBS_CHANCE')


def test_currency_constants_exist():
    """Verify currency constants defined."""
    assert hasattr(Config, 'STARTING_BOMBS')
    assert hasattr(Config, 'STARTING_COINS')
    assert hasattr(Config, 'ENEMY_COIN_DROP_CHANCE')


def test_bomb_constants_exist():
    """Verify bomb constants defined."""
    assert hasattr(Config, 'BOMB_FUSE_TIME')
    assert hasattr(Config, 'BOMB_BLAST_RADIUS')
    assert hasattr(Config, 'BOMB_DAMAGE')


def test_minimap_constants_exist():
    """Verify mini-map constants defined."""
    assert hasattr(Config, 'MINIMAP_DISPLAY_RADIUS')


def test_dungeon_sizes_are_reasonable():
    """Verify dungeon size constraints."""
    assert 10 <= Config.DUNGEON_MIN_SIZE <= 15
    assert 15 <= Config.DUNGEON_MAX_SIZE <= 20
    assert Config.DUNGEON_MIN_SIZE < Config.DUNGEON_MAX_SIZE


def test_reward_chances_sum_to_one():
    """Verify reward probabilities sum to 1.0."""
    total = (
        Config.REWARD_COINS_CHANCE +
        Config.REWARD_HEART_CHANCE +
        Config.REWARD_STAT_BOOST_CHANCE +
        Config.REWARD_BOMBS_CHANCE
    )
    assert abs(total - 1.0) < 0.001  # Float comparison tolerance


def test_room_count_min_max_constraints():
    """Verify room count min < max for all room types."""
    assert Config.TREASURE_ROOM_COUNT_MIN < Config.TREASURE_ROOM_COUNT_MAX
    assert Config.SHOP_COUNT_MIN < Config.SHOP_COUNT_MAX
    assert Config.SECRET_COUNT_MIN < Config.SECRET_COUNT_MAX


def test_reward_probabilities_are_valid():
    """Verify all reward probabilities are between 0 and 1."""
    assert 0 <= Config.REWARD_COINS_CHANCE <= 1
    assert 0 <= Config.REWARD_HEART_CHANCE <= 1
    assert 0 <= Config.REWARD_STAT_BOOST_CHANCE <= 1
    assert 0 <= Config.REWARD_BOMBS_CHANCE <= 1


def test_currency_constants_are_non_negative():
    """Verify currency starting values are non-negative."""
    assert Config.STARTING_BOMBS >= 0
    assert Config.STARTING_COINS >= 0
    assert 0 <= Config.ENEMY_COIN_DROP_CHANCE <= 1


def test_bomb_constants_are_positive():
    """Verify bomb constants are positive values."""
    assert Config.BOMB_FUSE_TIME > 0
    assert Config.BOMB_BLAST_RADIUS > 0
    assert Config.BOMB_DAMAGE > 0


def test_minimap_radius_is_positive():
    """Verify minimap radius is positive."""
    assert Config.MINIMAP_DISPLAY_RADIUS > 0


def test_minimap_display_radius_matches_implementation():
    """Test MINIMAP_DISPLAY_RADIUS is 3 (7x7 grid = ±3 rooms)."""
    from src.config import Config
    assert Config.MINIMAP_DISPLAY_RADIUS == 3


def test_shop_item_prices_exist():
    """Verify shop item prices defined."""
    assert hasattr(Config, 'SHOP_ITEM_PRICES')
    assert isinstance(Config.SHOP_ITEM_PRICES, dict)

    # Check some expected items
    assert "speed_boost" in Config.SHOP_ITEM_PRICES
    assert "magic_mushroom" in Config.SHOP_ITEM_PRICES
    assert "bomb_x3" in Config.SHOP_ITEM_PRICES


def test_shop_prices_are_positive():
    """Verify all shop prices are positive integers."""
    for item_name, price in Config.SHOP_ITEM_PRICES.items():
        assert isinstance(price, int)
        assert price > 0


def test_shop_generation_constants_exist():
    """Verify shop generation constants defined."""
    assert hasattr(Config, 'SHOP_ITEMS_MIN')
    assert hasattr(Config, 'SHOP_ITEMS_MAX')
    assert Config.SHOP_ITEMS_MIN <= Config.SHOP_ITEMS_MAX


def test_explosive_tear_damage_multiplier_exists():
    """Verify explosive tear damage multiplier constant exists."""
    assert hasattr(Config, 'EXPLOSIVE_TEAR_DAMAGE_MULTIPLIER')
    assert isinstance(Config.EXPLOSIVE_TEAR_DAMAGE_MULTIPLIER, float)
    assert 0 < Config.EXPLOSIVE_TEAR_DAMAGE_MULTIPLIER <= 1.0
