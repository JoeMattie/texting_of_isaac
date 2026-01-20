"""Integration tests for boss fights and floor progression system.

These tests verify that all systems work together correctly:
- Boss AI, phase transitions, and projectile spawning
- Floor transitions via trapdoor collection
- Victory and game over detection
- Health bar display integration
- Floor scaling and room management
"""
import pytest
import esper
from src.entities.player import create_player
from src.entities.bosses import create_boss
from src.entities.trapdoor import create_trapdoor
from src.entities.enemies import create_enemy
from src.systems.boss_ai import BossAISystem
from src.systems.floor_transition import FloorTransitionSystem
from src.systems.game_state import GameStateSystem
from src.systems.boss_health_bar import BossHealthBarSystem
from src.systems.room_manager import RoomManager
from src.components.core import Position, Health
from src.components.combat import Projectile
from src.components.boss import Boss, BossAI, Trapdoor
from src.components.game import Player, Enemy
from src.game.state import GameState
from src.game.dungeon import generate_dungeon
from src.config import Config


@pytest.fixture
def world():
    """Create isolated test world."""
    world_name = "test_integration"
    esper.switch_world(world_name)
    esper.clear_database()
    yield world_name
    esper.clear_database()


def test_boss_fight_pattern_execution(world):
    """Test boss executes attack patterns and spawns projectiles."""
    # Setup: spawn player and boss
    player = create_player(world, 30, 15)
    boss = create_boss(world, "boss_a", 30, 10)

    # Create boss AI system
    boss_ai_system = BossAISystem()
    boss_ai_system.dt = 1.0  # 1 second per update

    # Get initial pattern timer
    esper.switch_world(world)
    boss_ai = esper.component_for_entity(boss, BossAI)
    initial_timer = boss_ai.pattern_timer

    # Process multiple frames to trigger pattern execution
    # Pattern cooldown is 3.0 seconds, so after 3-4 frames pattern should execute
    for i in range(4):
        boss_ai_system.process()

    # Verify: projectiles spawned
    esper.switch_world(world)
    projectiles = list(esper.get_components(Projectile))
    assert len(projectiles) > 0, "Boss should spawn projectiles after pattern timer expires"


def test_boss_phase_transition_at_50_percent(world):
    """Test boss transitions to phase 2 at 50% HP and changes patterns."""
    # Setup: spawn boss
    boss = create_boss(world, "boss_a", 30, 10)

    esper.switch_world(world)

    # Get boss components
    boss_comp = esper.component_for_entity(boss, Boss)
    boss_ai = esper.component_for_entity(boss, BossAI)
    health = esper.component_for_entity(boss, Health)

    # Verify initial state (phase 1)
    assert boss_comp.current_phase == 1
    assert not boss_comp.has_transitioned
    initial_pattern = boss_ai.pattern_name
    assert initial_pattern in ["spiral", "wave"]  # Phase 1 patterns for boss_a

    # Damage boss to exactly 50% HP
    health.current = health.max * 0.5

    # Process boss AI system to trigger phase transition check
    boss_ai_system = BossAISystem()
    boss_ai_system.dt = 0.1
    boss_ai_system.process()

    # Verify phase transition occurred
    assert boss_comp.current_phase == 2
    assert boss_comp.has_transitioned

    # Verify pattern changed to phase 2 pattern
    assert boss_ai.pattern_name in ["double_spiral", "fast_wave"]
    assert boss_ai.pattern_name != initial_pattern


def test_boss_phase_transition_below_50_percent(world):
    """Test boss transitions to phase 2 when HP drops below 50%."""
    # Setup: spawn boss
    boss = create_boss(world, "boss_b", 30, 10)

    esper.switch_world(world)

    boss_comp = esper.component_for_entity(boss, Boss)
    health = esper.component_for_entity(boss, Health)

    # Damage boss to 40% HP (below threshold)
    health.current = health.max * 0.4

    # Process boss AI
    boss_ai_system = BossAISystem()
    boss_ai_system.dt = 0.1
    boss_ai_system.process()

    # Verify transition
    assert boss_comp.current_phase == 2
    assert boss_comp.has_transitioned


def test_boss_no_phase_transition_above_threshold(world):
    """Test boss does NOT transition when HP is above 50%."""
    # Setup: spawn boss
    boss = create_boss(world, "boss_c", 30, 10)

    esper.switch_world(world)

    boss_comp = esper.component_for_entity(boss, Boss)
    health = esper.component_for_entity(boss, Health)

    # Damage boss to 60% HP (above threshold)
    health.current = health.max * 0.6

    # Process boss AI
    boss_ai_system = BossAISystem()
    boss_ai_system.dt = 0.1
    boss_ai_system.process()

    # Verify NO transition
    assert boss_comp.current_phase == 1
    assert not boss_comp.has_transitioned


def test_trapdoor_spawns_after_boss_defeat(world):
    """Test that trapdoor spawns when boss is defeated."""
    # Setup: create dungeon and room manager
    dungeon = generate_dungeon()
    room_manager = RoomManager(dungeon, current_floor=1)

    esper.switch_world(world)

    # Manually set current room to boss room
    for pos, room in dungeon.rooms.items():
        if room.room_type.value == "boss":
            room_manager.current_position = pos
            room_manager.current_room = room
            break

    # Verify no trapdoor exists initially
    trapdoors_before = list(esper.get_components(Trapdoor))
    assert len(trapdoors_before) == 0

    # Trigger room clear
    room_manager.on_room_cleared()

    # Verify trapdoor spawned
    trapdoors_after = list(esper.get_components(Trapdoor))
    assert len(trapdoors_after) == 1

    # Verify trapdoor points to next floor
    _, (trapdoor,) = trapdoors_after[0]
    assert trapdoor.next_floor == 2


def test_floor_progression_via_trapdoor(world):
    """Test player collecting trapdoor triggers floor transition."""
    # Setup: create player and trapdoor
    player = create_player(world, 30, 10)
    trapdoor = create_trapdoor(world, 30, 10, next_floor=2)

    # Create floor transition system
    floor_system = FloorTransitionSystem()

    esper.switch_world(world)

    # Process system (player at same position as trapdoor)
    floor_system.process()

    # Verify transition is pending
    assert floor_system.pending_floor_transition is True
    assert floor_system.target_floor == 2

    # Verify trapdoor was consumed
    assert not esper.entity_exists(trapdoor)


def test_floor_scaling_enemies_have_more_hp(world):
    """Test enemies on floor 2 have more HP than floor 1 enemies."""
    # Use "tank" enemy which has 10 base HP for cleaner scaling
    # 10 * 1.0 = 10, 10 * 1.3 = 13, 10 * 1.6 = 16
    enemy_floor_1 = create_enemy(world, "tank", 10, 10, floor=1)
    enemy_floor_2 = create_enemy(world, "tank", 20, 10, floor=2)
    enemy_floor_3 = create_enemy(world, "tank", 30, 10, floor=3)

    esper.switch_world(world)

    # Get health components
    health_f1 = esper.component_for_entity(enemy_floor_1, Health)
    health_f2 = esper.component_for_entity(enemy_floor_2, Health)
    health_f3 = esper.component_for_entity(enemy_floor_3, Health)

    # Verify scaling (floor 2 should have 1.3x, floor 3 should have 1.6x)
    assert health_f2.max > health_f1.max, "Floor 2 enemies should have more HP"
    assert health_f3.max > health_f2.max, "Floor 3 enemies should have more HP"

    # Verify specific multipliers from Config
    base_hp = 10  # Tank base HP
    assert health_f1.max == int(base_hp * Config.FLOOR_HP_MULTIPLIERS[1])
    assert health_f2.max == int(base_hp * Config.FLOOR_HP_MULTIPLIERS[2])
    assert health_f3.max == int(base_hp * Config.FLOOR_HP_MULTIPLIERS[3])


def test_victory_condition_after_final_floor(world):
    """Test victory is triggered when completing floor 3 (FINAL_FLOOR)."""
    # Setup: create player and trapdoor leading beyond final floor
    player = create_player(world, 30, 10)
    # Trapdoor from floor 3 to floor 4 (beyond FINAL_FLOOR)
    trapdoor = create_trapdoor(world, 30, 10, next_floor=Config.FINAL_FLOOR + 1)

    # Create systems
    floor_system = FloorTransitionSystem()
    game_state_system = GameStateSystem(floor_system)

    esper.switch_world(world)

    # Process floor transition
    floor_system.process()

    # Verify victory flag is set
    assert floor_system.victory is True
    assert floor_system.pending_floor_transition is False

    # Process game state system
    game_state_system.process()

    # Verify game state is VICTORY
    assert game_state_system.current_state == GameState.VICTORY


def test_game_over_on_player_death(world):
    """Test game over is triggered when player HP reaches 0."""
    # Setup: create player
    player = create_player(world, 30, 10)

    # Create systems
    floor_system = FloorTransitionSystem()
    game_state_system = GameStateSystem(floor_system)

    esper.switch_world(world)

    # Kill player
    health = esper.component_for_entity(player, Health)
    health.current = 0

    # Process game state system
    game_state_system.process()

    # Verify game state is GAME_OVER
    assert game_state_system.current_state == GameState.GAME_OVER


def test_health_bar_displays_during_boss_fight(world):
    """Test boss health bar renders correctly with boss name and HP."""
    # Setup: spawn boss
    boss = create_boss(world, "boss_a", 30, 10)

    # Create health bar system
    health_bar_system = BossHealthBarSystem(world)

    esper.switch_world(world)

    # Get health bar text
    bar_text = health_bar_system.get_health_bar_text()

    # Verify health bar contains boss name and HP
    assert "The Orbiter" in bar_text  # Boss A's name
    assert "HP:" in bar_text
    assert "50/50" in bar_text  # Full health
    assert "[" in bar_text  # Visual bar present


def test_health_bar_updates_with_damage(world):
    """Test health bar updates when boss takes damage."""
    # Setup: spawn boss
    boss = create_boss(world, "boss_b", 30, 10)

    # Create health bar system
    health_bar_system = BossHealthBarSystem(world)

    esper.switch_world(world)

    # Get initial health bar
    initial_bar = health_bar_system.get_health_bar_text()
    assert "75/75" in initial_bar  # Boss B has 75 HP

    # Damage boss
    health = esper.component_for_entity(boss, Health)
    health.current = 40

    # Get updated health bar
    updated_bar = health_bar_system.get_health_bar_text()
    assert "40/75" in updated_bar
    assert updated_bar != initial_bar


def test_health_bar_empty_when_no_boss(world):
    """Test health bar returns empty string when no boss exists."""
    # Create health bar system without spawning boss
    health_bar_system = BossHealthBarSystem(world)

    esper.switch_world(world)

    # Get health bar text
    bar_text = health_bar_system.get_health_bar_text()

    # Verify empty
    assert bar_text == ""


def test_complete_floor_progression_sequence(world):
    """Test complete sequence: Boss defeat -> Trapdoor pickup -> Floor transition trigger."""
    # This test verifies the core flow without RoomManager complexities
    floor_system = FloorTransitionSystem()

    esper.switch_world(world)

    # Create player
    player = create_player(world, 30, 10)

    # Step 1: Spawn trapdoor (simulating boss defeat)
    center_x = Config.ROOM_WIDTH / 2
    center_y = Config.ROOM_HEIGHT / 2
    trapdoor = create_trapdoor(world, center_x, center_y, next_floor=2)

    # Verify trapdoor exists
    trapdoors = list(esper.get_components(Trapdoor))
    assert len(trapdoors) == 1

    # Step 2: Position player on trapdoor
    player_pos = esper.component_for_entity(player, Position)
    player_pos.x = center_x
    player_pos.y = center_y

    # Process floor transition
    floor_system.process()

    # Step 3: Verify transition is pending and correct floor is targeted
    assert floor_system.pending_floor_transition is True
    assert floor_system.target_floor == 2

    # Step 4: Verify this wasn't a victory (floor 2 < FINAL_FLOOR + 1)
    assert floor_system.victory is False


def test_system_integration_boss_ai_and_floor_transition(world):
    """Test BossAISystem and FloorTransitionSystem work together."""
    # Setup: spawn player and boss
    player = create_player(world, 30, 15)
    boss = create_boss(world, "boss_a", 30, 10)

    # Create systems
    boss_ai_system = BossAISystem()
    boss_ai_system.dt = 1.0
    floor_system = FloorTransitionSystem()

    esper.switch_world(world)

    # Process boss AI (should spawn projectiles)
    for _ in range(4):
        boss_ai_system.process()

    # Verify boss is active
    assert esper.entity_exists(boss)

    # Kill boss
    health = esper.component_for_entity(boss, Health)
    health.current = 0
    esper.delete_entity(boss, immediate=True)

    # Spawn trapdoor manually (simulating room clear)
    trapdoor = create_trapdoor(world, 30, 15, next_floor=2)

    # Process floor transition (player at trapdoor position)
    floor_system.process()

    # Verify floor transition is ready
    assert floor_system.pending_floor_transition is True


def test_system_integration_game_state_and_health_bar(world):
    """Test GameStateSystem and BossHealthBarSystem integration."""
    # Setup: spawn player and boss
    player = create_player(world, 30, 15)
    boss = create_boss(world, "boss_c", 30, 10)

    # Create systems
    floor_system = FloorTransitionSystem()
    game_state_system = GameStateSystem(floor_system)
    health_bar_system = BossHealthBarSystem(world)

    esper.switch_world(world)

    # Verify initial state
    assert game_state_system.current_state == GameState.PLAYING
    health_bar = health_bar_system.get_health_bar_text()
    assert "The Spiral King" in health_bar  # Boss C name
    assert "100/100" in health_bar

    # Damage boss
    boss_health = esper.component_for_entity(boss, Health)
    boss_health.current = 30

    # Check health bar updated
    updated_bar = health_bar_system.get_health_bar_text()
    assert "30/100" in updated_bar

    # Kill player
    player_health = esper.component_for_entity(player, Health)
    player_health.current = 0

    # Process game state
    game_state_system.process()

    # Verify game over
    assert game_state_system.current_state == GameState.GAME_OVER


def test_boss_teleport_integration(world):
    """Test boss teleportation changes position."""
    # Setup: spawn player and boss
    player = create_player(world, 30, 15)
    boss = create_boss(world, "boss_a", 30, 10)

    # Create boss AI system
    boss_ai_system = BossAISystem()
    boss_ai_system.dt = 1.0

    esper.switch_world(world)

    # Get initial position
    initial_pos = esper.component_for_entity(boss, Position)
    initial_x = initial_pos.x
    initial_y = initial_pos.y

    # Get boss AI and set teleport timer to trigger immediately
    boss_ai = esper.component_for_entity(boss, BossAI)
    boss_ai.teleport_timer = 0.1  # Almost expired

    # Process multiple times to trigger teleport
    for _ in range(2):
        boss_ai_system.process()

    # Verify position changed
    new_x = initial_pos.x
    new_y = initial_pos.y
    position_changed = (new_x != initial_x) or (new_y != initial_y)
    assert position_changed, "Boss should have teleported to a new position"


def test_multiple_floor_transitions_sequence(world):
    """Test progressing through floors 1 -> 2 -> 3 -> Victory."""
    # Create systems
    floor_system = FloorTransitionSystem()
    game_state_system = GameStateSystem(floor_system)

    esper.switch_world(world)

    # Create player at position where trapdoors will spawn
    player = create_player(world, 30, 10)

    # Floor 1 -> 2
    trapdoor_1 = create_trapdoor(world, 30, 10, next_floor=2)
    floor_system.process()
    assert floor_system.target_floor == 2

    # Clean up by clearing database and recreating player
    # (This simulates what happens in actual floor transition)
    esper.clear_database()
    player = create_player(world, 30, 10)
    floor_system.reset_transition()

    # Floor 2 -> 3
    trapdoor_2 = create_trapdoor(world, 30, 10, next_floor=3)
    floor_system.process()
    assert floor_system.target_floor == 3

    # Clean up and recreate
    esper.clear_database()
    player = create_player(world, 30, 10)
    floor_system.reset_transition()

    # Floor 3 -> Victory
    trapdoor_3 = create_trapdoor(world, 30, 10, next_floor=4)
    floor_system.process()
    assert floor_system.victory is True

    # Process game state
    game_state_system.process()
    assert game_state_system.current_state == GameState.VICTORY


def test_boss_invulnerability_on_phase_transition(world):
    """Test boss receives invulnerability frames during phase transition."""
    # Setup: spawn boss
    boss = create_boss(world, "boss_a", 30, 10)

    esper.switch_world(world)

    # Get components
    boss_comp = esper.component_for_entity(boss, Boss)
    health = esper.component_for_entity(boss, Health)

    # Verify no invulnerability initially
    from src.components.game import Invincible
    assert not esper.has_component(boss, Invincible)

    # Damage to trigger phase transition
    health.current = health.max * 0.5

    # Process boss AI
    boss_ai_system = BossAISystem()
    boss_ai_system.dt = 0.1
    boss_ai_system.process()

    # Verify phase transitioned
    assert boss_comp.current_phase == 2

    # Verify invulnerability granted
    assert esper.has_component(boss, Invincible)
    invincible = esper.component_for_entity(boss, Invincible)
    assert invincible.remaining > 0


def test_room_manager_spawns_correct_boss_per_floor(world):
    """Test RoomManager spawns correct boss type based on current floor."""
    # Test floor 1 -> boss_a
    dungeon_1 = generate_dungeon()
    room_manager_1 = RoomManager(dungeon_1, current_floor=1)

    esper.switch_world(world)

    # Find and set boss room
    for pos, room in dungeon_1.rooms.items():
        if room.room_type.value == "boss":
            room_manager_1.current_position = pos
            room_manager_1.current_room = room
            break

    # Spawn boss
    room_manager_1._spawn_boss()

    # Verify boss_a spawned
    bosses = list(esper.get_components(Boss))
    assert len(bosses) == 1
    _, (boss_comp,) = bosses[0]
    assert boss_comp.boss_type == "boss_a"

    # Clear for next test
    esper.clear_database()

    # Test floor 2 -> boss_b
    dungeon_2 = generate_dungeon()
    room_manager_2 = RoomManager(dungeon_2, current_floor=2)

    # Find boss room
    for pos, room in dungeon_2.rooms.items():
        if room.room_type.value == "boss":
            room_manager_2.current_position = pos
            room_manager_2.current_room = room
            break

    # Spawn boss
    room_manager_2._spawn_boss()

    # Verify boss_b spawned
    bosses = list(esper.get_components(Boss))
    assert len(bosses) == 1
    _, (boss_comp,) = bosses[0]
    assert boss_comp.boss_type == "boss_b"

    # Clear for next test
    esper.clear_database()

    # Test floor 3 -> boss_c
    dungeon_3 = generate_dungeon()
    room_manager_3 = RoomManager(dungeon_3, current_floor=3)

    # Find boss room
    for pos, room in dungeon_3.rooms.items():
        if room.room_type.value == "boss":
            room_manager_3.current_position = pos
            room_manager_3.current_room = room
            break

    # Spawn boss
    room_manager_3._spawn_boss()

    # Verify boss_c spawned
    bosses = list(esper.get_components(Boss))
    assert len(bosses) == 1
    _, (boss_comp,) = bosses[0]
    assert boss_comp.boss_type == "boss_c"


def test_edge_case_boss_at_exactly_50_percent(world):
    """Test phase transition triggers at exactly 50% HP."""
    # Setup: spawn boss with 100 HP for clean math
    boss = create_boss(world, "boss_c", 30, 10)

    esper.switch_world(world)

    boss_comp = esper.component_for_entity(boss, Boss)
    health = esper.component_for_entity(boss, Health)

    # Boss C has 100 HP, so 50% is exactly 50
    assert health.max == 100
    health.current = 50

    # Process boss AI
    boss_ai_system = BossAISystem()
    boss_ai_system.dt = 0.1
    boss_ai_system.process()

    # Verify transition occurred at exactly 50%
    assert boss_comp.current_phase == 2
    assert boss_comp.has_transitioned


def test_edge_case_boss_just_above_50_percent(world):
    """Test NO phase transition at 50.01% HP."""
    # Setup: spawn boss
    boss = create_boss(world, "boss_c", 30, 10)

    esper.switch_world(world)

    boss_comp = esper.component_for_entity(boss, Boss)
    health = esper.component_for_entity(boss, Health)

    # Set HP to just above threshold (50.01%)
    health.current = health.max * 0.5001

    # Process boss AI
    boss_ai_system = BossAISystem()
    boss_ai_system.dt = 0.1
    boss_ai_system.process()

    # Verify NO transition
    assert boss_comp.current_phase == 1
    assert not boss_comp.has_transitioned
