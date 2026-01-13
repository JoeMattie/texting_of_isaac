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
