"""Tests for boss attack pattern generation."""
import pytest
import math


def test_generate_spiral_pattern():
    """Test spiral pattern generation."""
    from src.systems.boss_patterns import generate_spiral_pattern

    projectiles = generate_spiral_pattern(30.0, 10.0, rotation=0.0)

    # Should generate 8 projectiles
    assert len(projectiles) == 8

    # Verify structure
    for proj in projectiles:
        assert 'x' in proj
        assert 'y' in proj
        assert 'vx' in proj
        assert 'vy' in proj

    # Verify projectiles are in circle around boss
    for i, proj in enumerate(projectiles):
        angle = i * (360 / 8)  # 45 degrees apart
        # All projectiles should start at boss position
        assert proj['x'] == 30.0
        assert proj['y'] == 10.0


def test_generate_wave_pattern():
    """Test wave pattern generation."""
    from src.systems.boss_patterns import generate_wave_pattern

    projectiles = generate_wave_pattern(30.0, 10.0, sweep_angle=0.0)

    # Should generate 5 projectiles
    assert len(projectiles) == 5

    # All should start at boss position
    for proj in projectiles:
        assert proj['x'] == 30.0
        assert proj['y'] == 10.0


def test_generate_pulse_pattern():
    """Test pulse pattern generation."""
    from src.systems.boss_patterns import generate_pulse_pattern

    projectiles = generate_pulse_pattern(30.0, 10.0)

    # Should generate 12 projectiles (complete circle)
    assert len(projectiles) == 12

    # All should start at boss position
    for proj in projectiles:
        assert proj['x'] == 30.0
        assert proj['y'] == 10.0


def test_get_pattern_for_boss():
    """Test getting correct pattern function for boss and phase."""
    from src.systems.boss_patterns import get_pattern_for_boss

    # Boss A phase 1
    pattern_func = get_pattern_for_boss("boss_a", 1, "spiral")
    assert pattern_func is not None

    # Boss A phase 2
    pattern_func = get_pattern_for_boss("boss_a", 2, "double_spiral")
    assert pattern_func is not None

    # Invalid pattern
    pattern_func = get_pattern_for_boss("boss_a", 1, "invalid")
    assert pattern_func is None
