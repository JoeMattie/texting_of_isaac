"""Tests for boss components."""
import pytest


def test_boss_component_creation():
    """Test Boss component can be created."""
    from src.components.boss import Boss

    boss = Boss(boss_type="boss_a")
    assert boss.boss_type == "boss_a"
    assert boss.current_phase == 1
    assert boss.phase_2_threshold == 0.5
    assert boss.has_transitioned == False


def test_boss_ai_component_creation():
    """Test BossAI component can be created."""
    from src.components.boss import BossAI

    boss_ai = BossAI(
        pattern_name="spiral",
        pattern_cooldown=3.0,
        teleport_cooldown=6.0
    )
    assert boss_ai.pattern_name == "spiral"
    assert boss_ai.pattern_timer == 0.0
    assert boss_ai.pattern_cooldown == 3.0
    assert boss_ai.teleport_timer == 0.0
    assert boss_ai.teleport_cooldown == 6.0


def test_trapdoor_component_creation():
    """Test Trapdoor component can be created."""
    from src.components.boss import Trapdoor

    trapdoor = Trapdoor(next_floor=2)
    assert trapdoor.next_floor == 2
