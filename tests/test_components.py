import pytest
from src.components.core import Position, Velocity, Health, Sprite


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
