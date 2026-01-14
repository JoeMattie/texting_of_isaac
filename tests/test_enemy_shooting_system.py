"""Tests for enemy shooting system."""
import esper
import pytest
import math
from src.systems.enemy_shooting import EnemyShootingSystem
from src.components.core import Position, Velocity
from src.components.game import Enemy, Player, AIBehavior
from src.components.combat import Projectile


def test_enemy_shooting_system_exists():
    """Test EnemyShootingSystem can be instantiated."""
    system = EnemyShootingSystem()
    assert system is not None
    assert hasattr(system, 'dt')
