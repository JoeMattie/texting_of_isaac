"""Game configuration and constants."""


class Config:
    """Central configuration for game constants."""

    # Display
    ROOM_WIDTH: int = 60
    ROOM_HEIGHT: int = 20
    FPS: int = 30

    # Player stats
    PLAYER_SPEED: float = 5.0
    PLAYER_DAMAGE: float = 1.0
    PLAYER_FIRE_RATE: float = 2.0
    PLAYER_SHOT_SPEED: float = 8.0
    PLAYER_MAX_HP: int = 6
    PLAYER_HITBOX: float = 0.3

    # Enemy stats
    ENEMY_HITBOX: float = 0.5

    # Projectile stats
    PROJECTILE_HITBOX: float = 0.2

    # Game balance
    INVINCIBILITY_DURATION: float = 0.5
    HEART_DROP_CHANCE: float = 0.1
    MAX_PROJECTILES: int = 200

    # Item system
    ITEM_DROP_CHANCE: float = 0.15  # 15% chance for enemy to drop item
    ITEM_PICKUP_RADIUS: float = 0.4  # Collision radius for item pickups
    DOOR_COLLIDER_RADIUS: float = 1.0  # Door collision detection radius

    # Homing effect
    HOMING_TURN_RATE: float = 120.0  # Degrees per second (2 degrees per frame at 60fps)

    # Notification display
    NOTIFICATION_DURATION: float = 2.0  # Seconds to display pickup notification

    # Dungeon generation
    DUNGEON_MIN_SIZE: int = 12
    DUNGEON_MAX_SIZE: int = 18
    DUNGEON_MAIN_PATH_LENGTH: int = 11

    # Special room counts
    TREASURE_ROOM_COUNT_MIN: int = 2
    TREASURE_ROOM_COUNT_MAX: int = 3
    SHOP_COUNT_MIN: int = 1
    SHOP_COUNT_MAX: int = 2
    SECRET_COUNT_MIN: int = 1
    SECRET_COUNT_MAX: int = 2

    # Room clear rewards (probabilities must sum to 1.0)
    REWARD_COINS_CHANCE: float = 0.60
    REWARD_HEART_CHANCE: float = 0.25
    REWARD_STAT_BOOST_CHANCE: float = 0.10
    REWARD_BOMBS_CHANCE: float = 0.05

    # Currency
    STARTING_BOMBS: int = 3
    STARTING_COINS: int = 0
    ENEMY_COIN_DROP_CHANCE: float = 0.15

    # Bombs
    BOMB_FUSE_TIME: float = 1.5
    BOMB_BLAST_RADIUS: float = 2.0
    BOMB_DAMAGE: float = 1.0

    # Mini-map
    MINIMAP_DISPLAY_RADIUS: int = 3

    # Shop system
    SHOP_ITEMS_MIN: int = 3
    SHOP_ITEMS_MAX: int = 4

    # Shop item prices (in coins)
    SHOP_ITEM_PRICES: dict[str, int] = {
        # Cheap items (5-7 coins)
        "speed_boost": 5,
        "mini_mushroom": 6,
        "fire_rate_up": 7,

        # Medium items (8-12 coins)
        "triple_shot": 10,
        "homing_shots": 10,
        "piercing_tears": 12,

        # Expensive items (13-15 coins)
        "magic_mushroom": 15,
        "brimstone": 15,

        # Consumables
        "bomb_x3": 5,
        "treasure_map": 8,
        "heart": 3,
    }
