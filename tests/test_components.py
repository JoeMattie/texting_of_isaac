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


def test_collected_items_has_effect_validates_input():
    """Test has_effect() validates effect_name parameter."""
    import pytest
    from src.components.game import CollectedItems

    collected = CollectedItems()

    with pytest.raises(TypeError, match="effect_name must be a string"):
        collected.has_effect(None)

    with pytest.raises(ValueError, match="effect_name cannot be empty"):
        collected.has_effect("")


from src.components.dungeon import Currency, Door, RoomPosition, Bomb, MiniBoss, MiniMap, StatusEffect


def test_currency_tracks_resources():
    """Test Currency component."""
    currency = Currency(coins=10, bombs=3, keys=2)
    assert currency.coins == 10
    assert currency.bombs == 3
    assert currency.keys == 2


def test_currency_defaults():
    """Test Currency component defaults."""
    currency = Currency()
    assert currency.coins == 0
    assert currency.bombs == 3  # Start with 3 bombs
    assert currency.keys == 0


def test_door_component():
    """Test Door component."""
    door = Door(direction="north", locked=True, leads_to=(0, 1))
    assert door.direction == "north"
    assert door.locked == True
    assert door.leads_to == (0, 1)


def test_room_position_component():
    """Test RoomPosition component."""
    pos = RoomPosition(x=5, y=3)
    assert pos.x == 5
    assert pos.y == 3


def test_bomb_component():
    """Test Bomb component."""
    bomb = Bomb(fuse_time=1.5, blast_radius=2.0, owner=123)
    assert bomb.fuse_time == 1.5
    assert bomb.blast_radius == 2.0
    assert bomb.owner == 123


def test_miniboss_component():
    """Test MiniBoss component."""
    miniboss = MiniBoss(boss_type="glutton", guaranteed_drop="damage_upgrade")
    assert miniboss.boss_type == "glutton"
    assert miniboss.guaranteed_drop == "damage_upgrade"


def test_minimap_component():
    """Test MiniMap component."""
    minimap = MiniMap()
    assert minimap.visible_rooms == set()
    assert minimap.current_position == (0, 0)


def test_minimap_reveal_room():
    """Test revealing rooms on minimap."""
    minimap = MiniMap()
    minimap.reveal_room(1, 2)
    assert (1, 2) in minimap.visible_rooms


def test_status_effect_component():
    """Test StatusEffect component."""
    effect = StatusEffect(effect_type="spelunker_sense", duration=30.0)
    assert effect.effect_type == "spelunker_sense"
    assert effect.duration == 30.0
    assert effect.room_duration == False


def test_currency_validates_positive_values():
    """Test Currency validates non-negative values."""
    # Test negative coins
    with pytest.raises(ValueError, match="coins must be non-negative"):
        Currency(coins=-1, bombs=3, keys=0)

    # Test negative bombs
    with pytest.raises(ValueError, match="bombs must be non-negative"):
        Currency(coins=0, bombs=-1, keys=0)

    # Test negative keys
    with pytest.raises(ValueError, match="keys must be non-negative"):
        Currency(coins=0, bombs=3, keys=-1)

    # Zero values should be valid
    currency = Currency(coins=0, bombs=0, keys=0)
    assert currency.coins == 0
    assert currency.bombs == 0
    assert currency.keys == 0


def test_door_validates_direction():
    """Test Door validates direction."""
    # Test invalid direction
    with pytest.raises(ValueError, match="direction must be one of: north, south, east, west"):
        Door(direction="northwest", leads_to=(0, 1))

    with pytest.raises(ValueError, match="direction must be one of: north, south, east, west"):
        Door(direction="invalid", leads_to=(0, 1))

    # Valid directions should work
    door_north = Door(direction="north", leads_to=(0, 1))
    assert door_north.direction == "north"

    door_south = Door(direction="south", leads_to=(0, -1))
    assert door_south.direction == "south"

    door_east = Door(direction="east", leads_to=(1, 0))
    assert door_east.direction == "east"

    door_west = Door(direction="west", leads_to=(-1, 0))
    assert door_west.direction == "west"


def test_bomb_validates_positive_values():
    """Test Bomb validates positive values."""
    # Test non-positive fuse_time
    with pytest.raises(ValueError, match="fuse_time must be positive"):
        Bomb(fuse_time=0.0, blast_radius=2.0)

    with pytest.raises(ValueError, match="fuse_time must be positive"):
        Bomb(fuse_time=-1.0, blast_radius=2.0)

    # Test non-positive blast_radius
    with pytest.raises(ValueError, match="blast_radius must be positive"):
        Bomb(fuse_time=1.5, blast_radius=0.0)

    with pytest.raises(ValueError, match="blast_radius must be positive"):
        Bomb(fuse_time=1.5, blast_radius=-1.0)

    # Positive values should work
    bomb = Bomb(fuse_time=1.5, blast_radius=2.0)
    assert bomb.fuse_time == 1.5
    assert bomb.blast_radius == 2.0


def test_miniboss_validates_boss_type():
    """Test MiniBoss validates boss_type."""
    # Test empty boss_type
    with pytest.raises(ValueError, match="boss_type cannot be empty"):
        MiniBoss(boss_type="", guaranteed_drop="damage_upgrade")

    # Test invalid boss_type
    with pytest.raises(ValueError, match="boss_type must be one of: glutton, hoarder, sentinel"):
        MiniBoss(boss_type="invalid_boss", guaranteed_drop="damage_upgrade")

    with pytest.raises(ValueError, match="boss_type must be one of: glutton, hoarder, sentinel"):
        MiniBoss(boss_type="boss", guaranteed_drop="damage_upgrade")

    # Valid boss types should work
    glutton = MiniBoss(boss_type="glutton", guaranteed_drop="damage_upgrade")
    assert glutton.boss_type == "glutton"

    hoarder = MiniBoss(boss_type="hoarder", guaranteed_drop="key")
    assert hoarder.boss_type == "hoarder"

    sentinel = MiniBoss(boss_type="sentinel", guaranteed_drop="bomb")
    assert sentinel.boss_type == "sentinel"


def test_miniboss_validates_guaranteed_drop():
    """Test MiniBoss validates guaranteed_drop is not empty."""
    with pytest.raises(ValueError, match="guaranteed_drop cannot be empty"):
        MiniBoss(boss_type="glutton", guaranteed_drop="")


def test_miniboss_validates_teleport_timer():
    """Test MiniBoss validates teleport_timer is positive."""
    with pytest.raises(ValueError, match="teleport_timer must be positive"):
        MiniBoss(boss_type="sentinel", guaranteed_drop="coins", teleport_timer=0)
    with pytest.raises(ValueError, match="teleport_timer must be positive"):
        MiniBoss(boss_type="sentinel", guaranteed_drop="coins", teleport_timer=-1.0)


def test_status_effect_validates():
    """Test StatusEffect validates effect_type and duration."""
    # Test empty effect_type
    with pytest.raises(ValueError, match="effect_type cannot be empty"):
        StatusEffect(effect_type="", duration=30.0)

    # Test negative duration
    with pytest.raises(ValueError, match="duration must be non-negative"):
        StatusEffect(effect_type="spelunker_sense", duration=-1.0)

    # Zero duration should be valid
    effect = StatusEffect(effect_type="temporary_boost", duration=0.0)
    assert effect.duration == 0.0

    # Valid values should work
    effect = StatusEffect(effect_type="spelunker_sense", duration=30.0)
    assert effect.effect_type == "spelunker_sense"
    assert effect.duration == 30.0


def test_minimap_get_display_bounds_returns_correct_range():
    """Test get_display_bounds returns ±3 from current position."""
    minimap = MiniMap(current_position=(5, 10), visible_rooms=set())
    min_x, min_y, max_x, max_y = minimap.get_display_bounds()

    assert min_x == 2  # 5 - 3
    assert min_y == 7  # 10 - 3
    assert max_x == 8  # 5 + 3
    assert max_y == 13  # 10 + 3
