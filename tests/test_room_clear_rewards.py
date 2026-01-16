"""Tests for room-clear reward system."""
import pytest
import esper
import random
from src.systems.room_manager import RoomManager
from src.entities.rewards import spawn_room_clear_reward
from src.game.dungeon import Dungeon, DungeonRoom, RoomType, RoomState
from src.components.core import Position
from src.components.currency import Coin, BombPickup, HeartPickup
from src.components.game import Item
from src.config import Config


def test_spawn_room_clear_reward_coins():
    """Test spawning coins as room-clear reward (60% chance)."""
    esper.clear_database()

    # Force random to roll coins (< 0.60)
    random.seed(10)  # Seed that produces roll < 0.60

    spawn_room_clear_reward("test")

    # Should spawn 3-6 coins
    coins = [ent for ent, coin in esper.get_component(Coin)]
    assert 3 <= len(coins) <= 6

    # Coins should be near room center with scatter
    for coin_ent in coins:
        pos = esper.component_for_entity(coin_ent, Position)
        center_x = Config.ROOM_WIDTH / 2
        center_y = Config.ROOM_HEIGHT / 2

        # Within ±2 of center
        assert abs(pos.x - center_x) <= 2
        assert abs(pos.y - center_y) <= 2


def test_spawn_room_clear_reward_heart():
    """Test spawning heart as room-clear reward (25% chance)."""
    esper.clear_database()

    # Force random to roll heart (0.60 <= roll < 0.85)
    random.seed(42)  # Seed that produces roll in [0.60, 0.85)

    spawn_room_clear_reward("test")

    # Should spawn exactly 1 heart
    hearts = [ent for ent, heart in esper.get_component(HeartPickup)]
    assert len(hearts) == 1

    # Heart should be at room center
    heart_ent = hearts[0]
    pos = esper.component_for_entity(heart_ent, Position)
    assert pos.x == Config.ROOM_WIDTH / 2
    assert pos.y == Config.ROOM_HEIGHT / 2


def test_spawn_room_clear_reward_stat_boost():
    """Test spawning stat boost item as room-clear reward (10% chance)."""
    # Try multiple times to find a seed that produces stat boost
    found = False
    for seed in range(1000):
        esper.clear_database()
        random.seed(seed)

        roll = random.random()
        if 0.85 <= roll < 0.95:
            # Reset random with same seed and spawn
            random.seed(seed)
            spawn_room_clear_reward("test")

            # Should spawn exactly 1 item
            items = [ent for ent, item in esper.get_component(Item)]
            if len(items) == 1:
                # Item should be one of the stat boost types
                item_ent = items[0]
                item = esper.component_for_entity(item_ent, Item)
                assert item.name in ["mini_mushroom", "speed_boost", "fire_rate_up"]

                # Item should be at room center
                pos = esper.component_for_entity(item_ent, Position)
                assert pos.x == Config.ROOM_WIDTH / 2
                assert pos.y == Config.ROOM_HEIGHT / 2

                found = True
                break

    assert found, "Could not find a seed that produces stat boost reward"


def test_spawn_room_clear_reward_bombs():
    """Test spawning bombs as room-clear reward (5% chance)."""
    # Try multiple times to find a seed that produces bombs
    found = False
    for seed in range(1000):
        esper.clear_database()
        random.seed(seed)

        roll = random.random()
        if roll >= 0.95:
            # Reset random with same seed and spawn
            random.seed(seed)
            spawn_room_clear_reward("test")

            # Should spawn 1-2 bombs
            bombs = [ent for ent, bomb in esper.get_component(BombPickup)]
            if 1 <= len(bombs) <= 2:
                # Bombs should be near room center
                for bomb_ent in bombs:
                    pos = esper.component_for_entity(bomb_ent, Position)
                    center_x = Config.ROOM_WIDTH / 2
                    center_y = Config.ROOM_HEIGHT / 2

                    # Should be at or very near center (x offset by bomb index)
                    assert abs(pos.x - center_x) <= 2
                    assert pos.y == center_y

                found = True
                break

    assert found, "Could not find a seed that produces bombs reward"


def test_spawn_room_clear_reward_probability_distribution():
    """Test reward distribution matches expected probabilities."""
    # Run many iterations to verify probability distribution
    results = {"coins": 0, "heart": 0, "stat_boost": 0, "bombs": 0}

    iterations = 1000
    for i in range(iterations):
        esper.clear_database()

        # Use different seed each iteration
        random.seed(i)
        spawn_room_clear_reward("test")

        # Check what was spawned
        if esper.get_component(Coin):
            results["coins"] += 1
        elif esper.get_component(HeartPickup):
            results["heart"] += 1
        elif esper.get_component(Item):
            results["stat_boost"] += 1
        elif esper.get_component(BombPickup):
            results["bombs"] += 1

    # Verify probabilities are roughly correct (within 5% tolerance)
    assert abs(results["coins"] / iterations - Config.REWARD_COINS_CHANCE) < 0.05
    assert abs(results["heart"] / iterations - Config.REWARD_HEART_CHANCE) < 0.05
    assert abs(results["stat_boost"] / iterations - Config.REWARD_STAT_BOOST_CHANCE) < 0.05
    assert abs(results["bombs"] / iterations - Config.REWARD_BOMBS_CHANCE) < 0.05


def test_room_manager_calls_spawn_room_clear_reward():
    """Test RoomManager.on_room_cleared spawns reward."""
    esper.clear_database()

    dungeon = Dungeon()
    room = DungeonRoom(
        position=(0, 0),
        room_type=RoomType.COMBAT,
        doors={"east": (1, 0)},
        state=RoomState.COMBAT,
        cleared=False,
        enemies=[{"type": "chaser", "count": 1}]
    )
    dungeon.rooms[(0, 0)] = room
    dungeon.start_position = (0, 0)

    manager = RoomManager(dungeon)

    # Set seed for predictable reward
    random.seed(10)

    # Call on_room_cleared
    manager.on_room_cleared()

    # Should have spawned some reward (check any reward type exists)
    has_reward = (
        len(list(esper.get_component(Coin))) > 0 or
        len(list(esper.get_component(HeartPickup))) > 0 or
        len(list(esper.get_component(Item))) > 0 or
        len(list(esper.get_component(BombPickup))) > 0
    )
    assert has_reward


def test_heart_pickup_component_has_heal_amount():
    """Test HeartPickup component stores heal amount."""
    from src.components.currency import HeartPickup

    half_heart = HeartPickup(heal_amount=1)
    assert half_heart.heal_amount == 1

    full_heart = HeartPickup(heal_amount=2)
    assert full_heart.heal_amount == 2


def test_heart_pickup_validates_positive_heal():
    """Test HeartPickup validates positive heal amounts."""
    from src.components.currency import HeartPickup

    with pytest.raises(ValueError, match="heal_amount must be positive"):
        HeartPickup(heal_amount=0)

    with pytest.raises(ValueError, match="heal_amount must be positive"):
        HeartPickup(heal_amount=-1)


def test_spawn_heart_creates_entity():
    """Test spawn_heart creates heart entity."""
    from src.entities.currency import spawn_heart

    esper.clear_database()

    heart_ent = spawn_heart("test", 15.0, 10.0)

    assert esper.entity_exists(heart_ent)
    assert esper.has_component(heart_ent, HeartPickup)
    assert esper.has_component(heart_ent, Position)

    pos = esper.component_for_entity(heart_ent, Position)
    assert pos.x == 15.0
    assert pos.y == 10.0


def test_stat_boost_items_exist_in_definitions():
    """Test that stat boost items are defined."""
    from src.data.items import ITEM_DEFINITIONS

    assert "mini_mushroom" in ITEM_DEFINITIONS
    assert "speed_boost" in ITEM_DEFINITIONS
    assert "fire_rate_up" in ITEM_DEFINITIONS
