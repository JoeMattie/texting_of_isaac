"""Room-clear reward spawning functions."""
import random
import esper
from src.config import Config
from src.entities.currency import spawn_coin, spawn_heart, spawn_bomb_pickup
from src.entities.items import create_item


def spawn_room_clear_reward(world_name: str) -> None:
    """Spawn a reward when room is cleared.

    Spawns one of the following based on weighted random:
    - 60% chance: 3-6 coins scattered around room center
    - 25% chance: half-heart at room center
    - 10% chance: stat boost item at room center
    - 5% chance: 1-2 bombs at room center

    Args:
        world_name: Name of the world to spawn in
    """
    esper.switch_world(world_name)

    roll = random.random()
    center_x = Config.ROOM_WIDTH / 2
    center_y = Config.ROOM_HEIGHT / 2

    if roll < Config.REWARD_COINS_CHANCE:
        # Spawn coins (60% chance)
        num_coins = random.randint(3, 6)
        for _ in range(num_coins):
            x = center_x + random.uniform(-2, 2)
            y = center_y + random.uniform(-2, 2)
            spawn_coin(world_name, x, y)

    elif roll < Config.REWARD_COINS_CHANCE + Config.REWARD_HEART_CHANCE:
        # Spawn heart (25% chance)
        spawn_heart(world_name, center_x, center_y)

    elif roll < Config.REWARD_COINS_CHANCE + Config.REWARD_HEART_CHANCE + Config.REWARD_STAT_BOOST_CHANCE:
        # Spawn stat boost item (10% chance)
        stat_item = random.choice(["mini_mushroom", "speed_boost", "fire_rate_up"])
        create_item(world_name, stat_item, center_x, center_y)

    else:
        # Spawn bombs (5% chance)
        num_bombs = random.randint(1, 2)
        for i in range(num_bombs):
            x = center_x + i
            spawn_bomb_pickup(world_name, x, center_y)
