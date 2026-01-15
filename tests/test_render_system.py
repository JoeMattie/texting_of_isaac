import pytest
import esper
from src.systems.render import RenderSystem
from src.components.core import Position, Sprite
from src.components.game import Player, Invincible, Enemy
from src.config import Config


def test_render_system_creates_grid():
    system = RenderSystem()

    grid = system.create_grid()

    assert len(grid) == Config.ROOM_HEIGHT
    assert len(grid[0]) == Config.ROOM_WIDTH


def test_render_system_draws_entity():
    world = "test_render_entity"
    esper.switch_world(world)
    esper.clear_database()

    system = RenderSystem()
    esper.add_processor(system)

    # Create entity
    entity = esper.create_entity()
    esper.add_component(entity, Position(10.0, 5.0))
    esper.add_component(entity, Sprite('@', 'cyan'))

    grid = system.render(world)

    # Check entity appears in grid
    cell = grid[5][10]
    assert cell['char'] == '@'
    assert cell['color'] == 'cyan'


def test_sprite_flashes_during_invincibility():
    """Test player sprite flashes white during invincibility."""
    esper.switch_world("test_flash_invincible")
    esper.clear_database()

    # Create invincible player with elapsed time 0.05s (should show white)
    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(5.0, 5.0))
    esper.add_component(player, Sprite('@', 'cyan'))
    esper.add_component(player, Invincible(0.45))  # 0.5 - 0.05 elapsed

    # Render
    system = RenderSystem()
    grid = system.render("test_flash_invincible")

    # Player at (5, 5) should be white (flashing)
    assert grid[5][5]['char'] == '@'
    assert grid[5][5]['color'] == 'white'


def test_sprite_normal_color_without_invincibility():
    """Test player uses normal color when not invincible."""
    esper.switch_world("test_no_flash")
    esper.clear_database()

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(5.0, 5.0))
    esper.add_component(player, Sprite('@', 'cyan'))

    system = RenderSystem()
    grid = system.render("test_no_flash")

    # Player should be cyan (normal)
    assert grid[5][5]['char'] == '@'
    assert grid[5][5]['color'] == 'cyan'


def test_sprite_flash_toggles_over_time():
    """Test sprite flashing alternates between colors."""
    esper.switch_world("test_flash_toggle")
    esper.clear_database()

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(5.0, 5.0))
    esper.add_component(player, Sprite('@', 'cyan'))

    system = RenderSystem()

    # Test at elapsed=0.05 (within first 0.1s) -> white
    esper.add_component(player, Invincible(0.45))
    grid1 = system.render("test_flash_toggle")
    assert grid1[5][5]['color'] == 'white'

    # Test at elapsed=0.15 (between 0.1-0.2s) -> cyan
    inv = esper.component_for_entity(player, Invincible)
    inv.remaining = 0.35  # elapsed = 0.5 - 0.35 = 0.15
    grid2 = system.render("test_flash_toggle")
    assert grid2[5][5]['color'] == 'cyan'


def test_sprite_flash_at_boundary():
    """Test sprite flashing at exact boundary times."""
    esper.switch_world("test_flash_boundary")
    esper.clear_database()

    player = esper.create_entity()
    esper.add_component(player, Player())
    esper.add_component(player, Position(5.0, 5.0))
    esper.add_component(player, Sprite('@', 'cyan'))

    system = RenderSystem()
    esper.add_processor(system)

    # At exactly 0.1s boundary (between white and cyan)
    esper.add_component(player, Invincible(0.4))  # elapsed = 0.5 - 0.4 = 0.1
    esper.process()
    grid = system.render("test_flash_boundary")
    # Due to floating point precision, 0.5 - 0.4 = 0.09999999999999998, which IS < 0.1, so shows white
    assert grid[5][5]['color'] == 'white'


def test_non_player_doesnt_flash():
    """Test that non-Player entities don't flash even when invincible."""
    esper.switch_world("test_non_player_flash")
    esper.clear_database()

    # Create enemy (non-player) with invincibility
    enemy = esper.create_entity()
    esper.add_component(enemy, Enemy("test"))
    esper.add_component(enemy, Position(5.0, 5.0))
    esper.add_component(enemy, Sprite('E', 'red'))
    esper.add_component(enemy, Invincible(0.45))

    system = RenderSystem()
    esper.add_processor(system)
    esper.process()

    grid = system.render("test_non_player_flash")
    # Enemy should keep original color (no flashing)
    assert grid[5][5]['char'] == 'E'
    assert grid[5][5]['color'] == 'red'
