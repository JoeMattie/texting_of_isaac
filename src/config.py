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
    ITEM_DROP_CHANCE = 0.15  # 15% chance for enemy to drop item
    ITEM_PICKUP_RADIUS = 0.4  # Collision radius for item pickups

    # Homing effect
    HOMING_TURN_RATE = 120.0  # Degrees per second (2 degrees per frame at 60fps)

    # Notification display
    NOTIFICATION_DURATION = 2.0  # Seconds to display pickup notification
