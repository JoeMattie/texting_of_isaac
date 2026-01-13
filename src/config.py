"""Game configuration and constants."""


class Config:
    """Central configuration for game constants."""

    # Display
    ROOM_WIDTH = 60
    ROOM_HEIGHT = 20
    FPS = 30

    # Player stats
    PLAYER_SPEED = 5.0
    PLAYER_DAMAGE = 1.0
    PLAYER_FIRE_RATE = 2.0
    PLAYER_SHOT_SPEED = 8.0
    PLAYER_MAX_HP = 6
    PLAYER_HITBOX = 0.3

    # Enemy stats
    ENEMY_HITBOX = 0.5

    # Projectile stats
    PROJECTILE_HITBOX = 0.2

    # Game balance
    INVINCIBILITY_DURATION = 0.5
    HEART_DROP_CHANCE = 0.1
    MAX_PROJECTILES = 200
