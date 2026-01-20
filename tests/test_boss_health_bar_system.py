"""Tests for BossHealthBarSystem."""
import pytest
import esper
from src.systems.boss_health_bar import BossHealthBarSystem
from src.entities.bosses import create_boss
from src.components.core import Health
from src.config import Config


@pytest.fixture
def world():
    """Create isolated test world."""
    world_name = "test_boss_health_bar"
    esper.switch_world(world_name)
    esper.clear_database()
    yield world_name
    esper.clear_database()


@pytest.fixture
def system(world):
    """Create BossHealthBarSystem instance."""
    return BossHealthBarSystem(world)


def test_no_boss_returns_empty_string(world, system):
    """Test that system returns empty string when no boss exists."""
    result = system.get_health_bar_text()
    assert result == ""


def test_full_hp_bar(world, system):
    """Test health bar shows full when HP = max."""
    # Create boss with full HP
    boss = create_boss(world, "boss_a", 30.0, 10.0)

    result = system.get_health_bar_text()

    # Should show "The Orbiter HP: 50/50" with full bar
    assert "The Orbiter" in result
    assert "50/50" in result

    # Bar should be completely filled (40 filled characters)
    filled_count = result.count('█')
    assert filled_count == Config.BOSS_HEALTH_BAR_WIDTH


def test_half_hp_bar(world, system):
    """Test health bar shows half when HP = 50%."""
    # Create boss and damage to 50%
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    health = esper.component_for_entity(boss, Health)
    health.current = 25  # 50% of 50

    result = system.get_health_bar_text()

    # Should show "The Orbiter HP: 25/50"
    assert "The Orbiter" in result
    assert "25/50" in result

    # Bar should be half filled (20 filled, 20 empty)
    filled_count = result.count('█')
    empty_count = result.count('░')
    assert filled_count == Config.BOSS_HEALTH_BAR_WIDTH // 2
    assert empty_count == Config.BOSS_HEALTH_BAR_WIDTH // 2


def test_low_hp_bar(world, system):
    """Test health bar shows near empty when HP low."""
    # Create boss and damage to 10%
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    health = esper.component_for_entity(boss, Health)
    health.current = 5  # 10% of 50

    result = system.get_health_bar_text()

    # Should show "The Orbiter HP: 5/50"
    assert "The Orbiter" in result
    assert "5/50" in result

    # Bar should be mostly empty (4 filled, 36 empty)
    filled_count = result.count('█')
    empty_count = result.count('░')
    assert filled_count == 4  # 10% of 40
    assert empty_count == 36


def test_boss_name_display_boss_b(world, system):
    """Test correct boss name displayed for Boss B."""
    boss = create_boss(world, "boss_b", 30.0, 10.0)

    result = system.get_health_bar_text()

    # Should show "The Crossfire" (boss_b name)
    assert "The Crossfire" in result
    assert "75/75" in result  # boss_b has 75 HP


def test_boss_name_display_boss_c(world, system):
    """Test correct boss name displayed for Boss C."""
    boss = create_boss(world, "boss_c", 30.0, 10.0)

    result = system.get_health_bar_text()

    # Should show "The Spiral King" (boss_c name)
    assert "The Spiral King" in result
    assert "100/100" in result  # boss_c has 100 HP


def test_health_bar_format(world, system):
    """Test the exact format of the health bar."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    health = esper.component_for_entity(boss, Health)
    health.current = 30  # 60% of 50

    result = system.get_health_bar_text()

    # Format should be: "Name HP: current/max [bar]"
    assert result.startswith("The Orbiter HP: 30/50 [")
    assert result.endswith("]")

    # Extract bar portion
    bar_start = result.index('[') + 1
    bar_end = result.index(']')
    bar = result[bar_start:bar_end]

    # Bar should be exactly BOSS_HEALTH_BAR_WIDTH characters
    assert len(bar) == Config.BOSS_HEALTH_BAR_WIDTH

    # 60% = 24 filled, 16 empty
    filled_count = bar.count('█')
    empty_count = bar.count('░')
    assert filled_count == 24
    assert empty_count == 16


def test_zero_hp_bar(world, system):
    """Test health bar when boss has 0 HP."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    health = esper.component_for_entity(boss, Health)
    health.current = 0

    result = system.get_health_bar_text()

    # Should show "The Orbiter HP: 0/50"
    assert "The Orbiter" in result
    assert "0/50" in result

    # Bar should be completely empty
    filled_count = result.count('█')
    empty_count = result.count('░')
    assert filled_count == 0
    assert empty_count == Config.BOSS_HEALTH_BAR_WIDTH
