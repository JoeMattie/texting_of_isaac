"""Tests for BossAISystem."""
import pytest
import esper
from src.systems.boss_ai import BossAISystem
from src.entities.bosses import create_boss, BOSS_DATA
from src.entities.player import create_player
from src.components.core import Position, Health, Velocity, Sprite
from src.components.combat import Collider, Projectile
from src.components.boss import Boss, BossAI
from src.components.game import Invincible, Player
from src.config import Config


@pytest.fixture
def world():
    """Create isolated test world."""
    world_name = "test_boss_ai"
    esper.switch_world(world_name)
    esper.clear_database()
    yield world_name
    esper.clear_database()


def test_boss_phase_transition_at_threshold(world):
    """Test boss transitions to phase 2 when HP drops to 50%."""
    # Create boss with 100 HP
    boss = create_boss(world, "boss_c", 30.0, 10.0)

    # Create player (required for pattern execution)
    player = create_player(world, 40.0, 10.0)

    # Set up system
    system = BossAISystem()
    system.dt = 0.1
    esper.add_processor(system)

    # Boss should start in phase 1
    boss_comp = esper.component_for_entity(boss, Boss)
    assert boss_comp.current_phase == 1
    assert boss_comp.has_transitioned is False

    # Damage boss to exactly 50% HP (50 out of 100)
    health = esper.component_for_entity(boss, Health)
    health.current = 50

    # Process system
    esper.process()

    # Boss should now be in phase 2
    assert boss_comp.current_phase == 2
    assert boss_comp.has_transitioned is True

    # Boss should have invincibility
    assert esper.has_component(boss, Invincible)
    invincible = esper.component_for_entity(boss, Invincible)
    assert invincible.remaining == pytest.approx(Config.BOSS_PHASE_TRANSITION_INVULN)


def test_boss_phase_transition_switches_pattern(world):
    """Test boss switches to phase 2 pattern on transition."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    player = create_player(world, 40.0, 10.0)

    system = BossAISystem()
    system.dt = 0.1
    esper.add_processor(system)

    # Get phase 1 pattern
    boss_ai = esper.component_for_entity(boss, BossAI)
    phase_1_pattern = boss_ai.pattern_name

    # Verify it's a phase 1 pattern
    assert phase_1_pattern in BOSS_DATA["boss_a"]["patterns"]

    # Trigger phase transition
    health = esper.component_for_entity(boss, Health)
    health.current = 25  # 50% of 50 HP

    esper.process()

    # Pattern should now be a phase 2 pattern
    assert boss_ai.pattern_name in BOSS_DATA["boss_a"]["phase_2_patterns"]
    assert boss_ai.pattern_name != phase_1_pattern


def test_boss_phase_transition_updates_teleport_cooldown(world):
    """Test boss teleport cooldown changes in phase 2."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    player = create_player(world, 40.0, 10.0)

    system = BossAISystem()
    system.dt = 0.1
    esper.add_processor(system)

    boss_ai = esper.component_for_entity(boss, BossAI)
    phase_1_cooldown = BOSS_DATA["boss_a"]["teleport_cooldowns"]["phase_1"]
    phase_2_cooldown = BOSS_DATA["boss_a"]["teleport_cooldowns"]["phase_2"]

    # Verify phase 1 cooldown
    assert boss_ai.teleport_cooldown == phase_1_cooldown

    # Trigger phase transition
    health = esper.component_for_entity(boss, Health)
    health.current = 25

    esper.process()

    # Verify phase 2 cooldown
    assert boss_ai.teleport_cooldown == phase_2_cooldown


def test_boss_only_transitions_once(world):
    """Test boss doesn't transition multiple times."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    player = create_player(world, 40.0, 10.0)

    system = BossAISystem()
    system.dt = 0.1
    esper.add_processor(system)

    # Trigger phase transition
    health = esper.component_for_entity(boss, Health)
    health.current = 25

    esper.process()

    boss_comp = esper.component_for_entity(boss, Boss)
    assert boss_comp.has_transitioned is True

    # Process again with HP still low
    esper.process()

    # Should still be transitioned (no double transition)
    assert boss_comp.has_transitioned is True
    assert boss_comp.current_phase == 2


def test_pattern_execution_spawns_projectiles(world):
    """Test boss spawns projectiles when pattern timer reaches 0."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    player = create_player(world, 40.0, 10.0)

    system = BossAISystem()
    system.dt = 0.1
    esper.add_processor(system)

    # Set pattern timer to 0 to trigger immediate execution
    boss_ai = esper.component_for_entity(boss, BossAI)
    boss_ai.pattern_timer = 0.0

    # Process system
    esper.process()

    # Check that projectiles were created
    projectiles = list(esper.get_components(Projectile, Position))
    assert len(projectiles) > 0

    # Verify projectiles have required components
    for ent, (proj, pos) in projectiles:
        assert esper.has_component(ent, Velocity)
        assert esper.has_component(ent, Collider)
        assert esper.has_component(ent, Sprite)


def test_pattern_timer_resets_after_execution(world):
    """Test pattern timer resets to cooldown after executing pattern."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    player = create_player(world, 40.0, 10.0)

    system = BossAISystem()
    system.dt = 0.1
    esper.add_processor(system)

    boss_ai = esper.component_for_entity(boss, BossAI)
    original_cooldown = boss_ai.pattern_cooldown
    boss_ai.pattern_timer = 0.0

    esper.process()

    # Timer should reset to cooldown value
    assert boss_ai.pattern_timer == pytest.approx(original_cooldown)


def test_pattern_timer_counts_down(world):
    """Test pattern timer decrements over time."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    player = create_player(world, 40.0, 10.0)

    system = BossAISystem()
    system.dt = 0.5
    esper.add_processor(system)

    boss_ai = esper.component_for_entity(boss, BossAI)
    boss_ai.pattern_timer = 2.0

    esper.process()

    # Timer should have decremented
    assert boss_ai.pattern_timer == pytest.approx(1.5)


def test_teleport_when_timer_reaches_zero(world):
    """Test boss teleports when teleport timer reaches 0."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    player = create_player(world, 5.0, 5.0)  # Far from teleport positions

    system = BossAISystem()
    system.dt = 0.1
    esper.add_processor(system)

    pos = esper.component_for_entity(boss, Position)
    original_x = pos.x
    original_y = pos.y

    # Set teleport timer to 0
    boss_ai = esper.component_for_entity(boss, BossAI)
    boss_ai.teleport_timer = 0.0

    esper.process()

    # Boss should have moved to a different position
    assert (pos.x != original_x) or (pos.y != original_y)

    # Boss should be at one of the configured teleport positions
    teleport_positions = Config.BOSS_TELEPORT_POSITIONS
    assert (pos.x, pos.y) in teleport_positions


def test_teleport_timer_resets_after_teleport(world):
    """Test teleport timer resets to cooldown after teleporting."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    player = create_player(world, 5.0, 5.0)

    system = BossAISystem()
    system.dt = 0.1
    esper.add_processor(system)

    boss_ai = esper.component_for_entity(boss, BossAI)
    original_cooldown = boss_ai.teleport_cooldown
    boss_ai.teleport_timer = 0.0

    esper.process()

    # Timer should reset to cooldown
    assert boss_ai.teleport_timer == pytest.approx(original_cooldown)


def test_teleport_timer_counts_down(world):
    """Test teleport timer decrements over time."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    player = create_player(world, 40.0, 10.0)

    system = BossAISystem()
    system.dt = 0.5
    esper.add_processor(system)

    boss_ai = esper.component_for_entity(boss, BossAI)
    boss_ai.teleport_timer = 3.0

    esper.process()

    # Timer should have decremented
    assert boss_ai.teleport_timer == pytest.approx(2.5)


def test_teleport_avoids_player_position(world):
    """Test boss doesn't teleport too close to player."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)

    # Place player at first teleport position
    first_teleport_pos = Config.BOSS_TELEPORT_POSITIONS[0]
    player = create_player(world, first_teleport_pos[0], first_teleport_pos[1])

    system = BossAISystem()
    system.dt = 0.1
    esper.add_processor(system)

    boss_ai = esper.component_for_entity(boss, BossAI)
    boss_ai.teleport_timer = 0.0

    esper.process()

    # Boss should teleport, but not to player's position
    pos = esper.component_for_entity(boss, Position)
    player_pos = esper.component_for_entity(player, Position)

    # Calculate distance
    import math
    distance = math.sqrt((pos.x - player_pos.x)**2 + (pos.y - player_pos.y)**2)

    # Should be at least minimum distance away
    assert distance >= Config.BOSS_TELEPORT_MIN_PLAYER_DISTANCE


def test_pattern_projectiles_have_correct_components(world):
    """Test spawned projectiles have all required components."""
    boss = create_boss(world, "boss_a", 30.0, 10.0)
    player = create_player(world, 40.0, 10.0)

    system = BossAISystem()
    system.dt = 0.1
    esper.add_processor(system)

    boss_ai = esper.component_for_entity(boss, BossAI)
    boss_ai.pattern_timer = 0.0

    esper.process()

    # Verify all projectiles have correct components
    for ent, (proj, pos, vel) in esper.get_components(Projectile, Position, Velocity):
        # Should have all required components
        assert esper.has_component(ent, Collider)
        assert esper.has_component(ent, Sprite)

        # Verify sprite for enemy projectile
        sprite = esper.component_for_entity(ent, Sprite)
        assert sprite.char == '*'
        assert sprite.color == 'yellow'

        # Verify velocity is non-zero (projectile should move)
        assert (vel.dx != 0.0) or (vel.dy != 0.0)


def test_no_boss_no_processing(world):
    """Test system doesn't crash when no boss exists."""
    player = create_player(world, 40.0, 10.0)

    system = BossAISystem()
    system.dt = 0.1
    esper.add_processor(system)

    # Should not crash
    esper.process()
