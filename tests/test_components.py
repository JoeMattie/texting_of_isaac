import pytest
from src.components.core import Position, Velocity, Health, Sprite
from src.components.combat import Stats, Collider, Projectile
from src.components.game import Player, Enemy, Item, AIBehavior, Invincible, Dead


def test_position_stores_coordinates():
    pos = Position(10.5, 20.3)
    assert pos.x == 10.5
    assert pos.y == 20.3


def test_velocity_stores_direction():
    vel = Velocity(1.0, -0.5)
    assert vel.dx == 1.0
    assert vel.dy == -0.5


def test_health_tracks_current_and_max():
    health = Health(3, 6)
    assert health.current == 3
    assert health.max == 6


def test_sprite_stores_appearance():
    sprite = Sprite('@', 'cyan')
    assert sprite.char == '@'
    assert sprite.color == 'cyan'


def test_health_validates_bounds():
    # Test negative current health
    with pytest.raises(ValueError, match="current health cannot be negative"):
        Health(-1, 10)

    # Test negative max health
    with pytest.raises(ValueError, match="max health cannot be negative"):
        Health(5, -1)

    # Test current > max
    with pytest.raises(ValueError, match="current health cannot exceed max health"):
        Health(10, 5)

    # Valid edge cases should work
    health = Health(0, 0)
    assert health.current == 0
    assert health.max == 0

    health = Health(10, 10)
    assert health.current == 10
    assert health.max == 10


def test_sprite_validates_char_length():
    # Test empty string
    with pytest.raises(ValueError, match="char must be a single character"):
        Sprite('', 'red')

    # Test multiple characters
    with pytest.raises(ValueError, match="char must be a single character"):
        Sprite('abc', 'blue')

    # Single character should work
    sprite = Sprite('X', 'green')
    assert sprite.char == 'X'


# Combat component tests


def test_stats_stores_combat_values():
    stats = Stats(speed=5.0, damage=2.0, fire_rate=3.0, shot_speed=8.0)
    assert stats.speed == 5.0
    assert stats.damage == 2.0
    assert stats.fire_rate == 3.0
    assert stats.shot_speed == 8.0


def test_collider_has_radius():
    collider = Collider(0.5)
    assert collider.radius == 0.5


def test_projectile_stores_damage_and_owner():
    projectile = Projectile(damage=2, owner=42)
    assert projectile.damage == 2
    assert projectile.owner == 42


def test_stats_validates_positive_values():
    # Test negative speed
    with pytest.raises(ValueError, match="speed must be positive"):
        Stats(speed=-1.0, damage=2.0, fire_rate=3.0, shot_speed=8.0)

    # Test negative damage
    with pytest.raises(ValueError, match="damage must be positive"):
        Stats(speed=5.0, damage=-1.0, fire_rate=3.0, shot_speed=8.0)

    # Test negative fire_rate
    with pytest.raises(ValueError, match="fire_rate must be positive"):
        Stats(speed=5.0, damage=2.0, fire_rate=-1.0, shot_speed=8.0)

    # Test negative shot_speed
    with pytest.raises(ValueError, match="shot_speed must be positive"):
        Stats(speed=5.0, damage=2.0, fire_rate=3.0, shot_speed=-1.0)

    # Zero values should be valid edge case
    stats = Stats(speed=0.0, damage=0.0, fire_rate=0.0, shot_speed=0.0)
    assert stats.speed == 0.0


def test_collider_validates_positive_radius():
    # Test negative radius
    with pytest.raises(ValueError, match="radius must be positive"):
        Collider(-1.0)

    # Test zero radius (edge case - should be valid)
    collider = Collider(0.0)
    assert collider.radius == 0.0


def test_projectile_validates_positive_damage():
    # Test negative damage
    with pytest.raises(ValueError, match="damage must be positive"):
        Projectile(damage=-1.0, owner=42)

    # Zero damage should be valid edge case
    projectile = Projectile(damage=0.0, owner=0)
    assert projectile.damage == 0.0


# Game component tests


def test_player_is_marker_component():
    player = Player()
    assert isinstance(player, Player)


def test_enemy_stores_type():
    enemy = Enemy("chaser")
    assert enemy.type == "chaser"


def test_item_stores_effects():
    item = Item(
        name="Speed Shoes",
        stat_modifiers={"speed": 1.5},
        special_effects=[]
    )
    assert item.name == "Speed Shoes"
    assert item.stat_modifiers["speed"] == 1.5


def test_ai_behavior_tracks_cooldowns():
    ai = AIBehavior(pattern_cooldowns={"shoot": 2.0})
    assert ai.pattern_cooldowns["shoot"] == 2.0


def test_invincible_has_duration():
    invincible = Invincible(0.5)
    assert invincible.remaining == 0.5


def test_invincible_validates_positive_duration():
    # Test negative duration
    with pytest.raises(ValueError, match="duration must be positive"):
        Invincible(-1.0)

    # Zero duration should be valid edge case
    invincible = Invincible(0.0)
    assert invincible.remaining == 0.0


def test_ai_behavior_with_pattern_index():
    """Test AIBehavior component with pattern_index."""
    cooldowns = {"aimed": 2.0, "spread": 3.0}
    ai = AIBehavior(pattern_cooldowns=cooldowns, pattern_index=0)
    assert ai.pattern_cooldowns == cooldowns
    assert ai.pattern_index == 0


def test_ai_behavior_pattern_index_defaults_to_zero():
    """Test AIBehavior pattern_index defaults to 0."""
    ai = AIBehavior(pattern_cooldowns={})
    assert ai.pattern_index == 0


def test_ai_behavior_pattern_index_validation():
    """Test AIBehavior validates pattern_index is non-negative."""
    with pytest.raises(ValueError, match="pattern_index must be non-negative"):
        AIBehavior(pattern_cooldowns={}, pattern_index=-1)


def test_dead_is_marker_component():
    """Test Dead component is a simple marker."""
    dead = Dead()
    assert repr(dead) == "Dead()"


def test_collected_items_tracks_items():
    """Test CollectedItems stores Item objects."""
    from src.components.game import CollectedItems, Item

    item1 = Item("mushroom", {"damage": 1.0}, [])
    item2 = Item("triple_shot", {}, ["multi_shot"])

    collected = CollectedItems()
    collected.items.append(item1)
    collected.items.append(item2)

    assert len(collected.items) == 2
    assert collected.items[0].name == "mushroom"
    assert collected.items[1].name == "triple_shot"


def test_collected_items_has_effect():
    """Test has_effect() correctly identifies special effects."""
    from src.components.game import CollectedItems, Item

    item1 = Item("piercing_tears", {}, ["piercing"])
    item2 = Item("homing_shots", {}, ["homing"])

    collected = CollectedItems()
    collected.items.append(item1)
    collected.items.append(item2)

    assert collected.has_effect("piercing") is True
    assert collected.has_effect("homing") is True
    assert collected.has_effect("multi_shot") is False


def test_collected_items_has_effect_with_no_items():
    """Test has_effect() returns False when no items collected."""
    from src.components.game import CollectedItems

    collected = CollectedItems()
    assert collected.has_effect("piercing") is False
